#!/usr/bin/env python3
"""Auto-auditoría semanal (el órgano de auto-reparación):

1. Mide el rendimiento real: notas por categoría, tasa de aceptación.
2. Aprende keywords nuevas de las notas ACEPTADAS (mineria de títulos)
   y las promueve a config/keywords-learned.yml — archivo separado del
   hecho a mano, para que el sistema nunca reescriba su propio filtro
   base en silencio (auditable via git, reversible borrando el archivo).
3. Detecta categorías muertas (0 notas) y auto-crea un gap de
   investigación para encontrar mejores fuentes/keywords.
4. Escribe un informe de salud en notes/_system/ (fluye a Obsidian).

Métrica de falsación (P14): si las notas crecen pero ninguna decisión
cambia, el sistema es un pasivo. Ese juicio lo hace Claude/Anas leyendo
estos informes — este script solo aporta los números.
"""
import os
import re
import sys
import glob
import json
from collections import Counter
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT, load_config, load_seen

LEARNED_PATH = os.path.join(ROOT, "config", "keywords-learned.yml")
GAPS_PATH = os.path.join(ROOT, "gaps", "pending.md")
SYSTEM_DIR = os.path.join(ROOT, "notes", "_system")

STOPWORDS = set("""
the and for with from that this have will your what when where which how
into over under about after before between using used more most than then
them they their there been being was were are is it its can could should
would a an of to in on at by as or if not no new best top guide why
para con las los una del que como este esta han hay mas los sus se
""".split())

MIN_OCCURRENCES = 3
MIN_WORD_LEN = 5


def tokenize(text):
    words = re.findall(r"[a-záéíóúñ][\w-]+", text.lower())
    return [w for w in words if len(w) >= MIN_WORD_LEN and w not in STOPWORDS]


def load_learned():
    import yaml
    if not os.path.exists(LEARNED_PATH):
        return {}
    with open(LEARNED_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def save_learned(learned):
    import yaml
    header = (
        "# Keywords aprendidas automáticamente por self_audit.py.\n"
        "# Minadas de títulos de notas ACEPTADAS (>= 3 apariciones en una categoría).\n"
        "# Se cargan con peso 1 además de config/keywords.yml (que nunca se toca).\n"
        "# Para revertir un aprendizaje: borrar la línea y commitear.\n"
    )
    with open(LEARNED_PATH, "w", encoding="utf-8") as f:
        f.write(header + yaml.dump(learned, allow_unicode=True, default_flow_style=False))


def mine_keywords(config, learned):
    """Devuelve dict {categoria: [nuevas_keywords]} promovidas en esta pasada."""
    existing = {}
    for cat, spec in config["categories"].items():
        existing[cat] = set(k.lower() for k in spec["keywords"])
        existing[cat] |= set(k.lower() for k in learned.get(cat, []))

    promoted = {}
    for cat_dir in glob.glob(os.path.join(ROOT, "notes", "*")):
        cat = os.path.basename(cat_dir)
        if cat.startswith("_") or cat == "deep-research" or cat not in existing:
            continue
        counter = Counter()
        for note in glob.glob(os.path.join(cat_dir, "*.md")):
            with open(note, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("title:"):
                        counter.update(tokenize(line[len("title:"):]))
                        break
        new = [w for w, c in counter.items()
               if c >= MIN_OCCURRENCES and w not in existing[cat]]
        if new:
            promoted[cat] = sorted(new)
            learned.setdefault(cat, [])
            learned[cat] = sorted(set(learned[cat]) | set(new))
    return promoted


def detect_dead_categories(config):
    dead = []
    for cat in config["categories"]:
        cat_dir = os.path.join(ROOT, "notes", cat)
        count = len(glob.glob(os.path.join(cat_dir, "*.md"))) if os.path.isdir(cat_dir) else 0
        if count == 0:
            dead.append(cat)
    return dead


def add_gap_if_missing(slug, query):
    if not os.path.exists(GAPS_PATH):
        return False
    with open(GAPS_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    if slug in content:
        return False
    line = f"- [ ] {slug} | {query}"
    content = content.replace("## Pendientes\n", f"## Pendientes\n\n{line}\n", 1)
    with open(GAPS_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    return True


def main():
    config = load_config()
    seen = load_seen()
    learned = load_learned()

    total_seen = len(seen)
    irrelevant = sum(1 for v in seen.values() if v.get("reason") == "irrelevant")
    accepted = total_seen - irrelevant
    rate = (accepted / total_seen * 100) if total_seen else 0

    per_cat = Counter(v.get("category") for v in seen.values() if v.get("category"))
    note_counts = {}
    for cat in config["categories"]:
        cat_dir = os.path.join(ROOT, "notes", cat)
        note_counts[cat] = len(glob.glob(os.path.join(cat_dir, "*.md"))) if os.path.isdir(cat_dir) else 0

    promoted = mine_keywords(config, learned)
    if promoted:
        save_learned(learned)

    dead = detect_dead_categories(config)
    auto_gaps = []
    for cat in dead:
        slug = f"improve-sources-{cat.replace('_', '-')}"
        query = f"best information sources blogs research feeds for {cat.replace('_', ' ')}"
        if add_gap_if_missing(slug, query):
            auto_gaps.append(slug)

    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    os.makedirs(SYSTEM_DIR, exist_ok=True)
    report_path = os.path.join(SYSTEM_DIR, f"health-{date_str}.md")

    lines = [
        "---",
        f"date: {date_str}",
        "type: system-health",
        "---",
        "",
        f"# Salud del motor — {date_str}",
        "",
        f"- Items procesados (histórico): {total_seen}",
        f"- Aceptados: {accepted} ({rate:.1f}%)",
        f"- Descartados por irrelevancia: {irrelevant}",
        "",
        "## Notas por categoría",
        "",
    ]
    for cat, n in sorted(note_counts.items(), key=lambda x: -x[1]):
        marker = " ⚠️ MUERTA" if n == 0 else ""
        lines.append(f"- {cat}: {n} notas{marker}")

    lines += ["", "## Keywords aprendidas esta pasada", ""]
    if promoted:
        for cat, kws in promoted.items():
            lines.append(f"- {cat}: {', '.join(kws)}")
    else:
        lines.append("- (ninguna)")

    lines += ["", "## Gaps auto-creados (categorías muertas)", ""]
    lines.append("- " + (", ".join(auto_gaps) if auto_gaps else "(ninguno)"))

    lines += [
        "",
        "## Pregunta de falsación (responder en sesión, P14)",
        "",
        "¿Alguna decisión real de Anas cambió esta semana por contenido de",
        "wiki/auto-research/? Si la respuesta es NO durante 4 informes",
        "seguidos, el motor es un pasivo: apagarlo o rediseñarlo.",
        "",
    ]

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Informe: {report_path}")
    print(f"Aceptación: {rate:.1f}% | Muertas: {dead} | Keywords nuevas: {sum(len(v) for v in promoted.values())}")


if __name__ == "__main__":
    main()
