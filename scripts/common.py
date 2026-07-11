"""Utilidades compartidas: carga de config, dedupe state, escritura de notas."""
import hashlib
import json
import os
import re
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(ROOT, "config", "keywords.yml")
SEEN_PATH = os.path.join(ROOT, "data", "seen.json")
NOTES_DIR = os.path.join(ROOT, "notes")


def load_config():
    import yaml
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    # Merge de keywords aprendidas (self_audit.py) con peso 1.
    # Archivo separado del hecho a mano: el filtro base nunca se auto-reescribe.
    learned_path = os.path.join(ROOT, "config", "keywords-learned.yml")
    if os.path.exists(learned_path):
        with open(learned_path, "r", encoding="utf-8") as f:
            learned = yaml.safe_load(f) or {}
        for cat, kws in learned.items():
            if cat in config.get("categories", {}):
                for kw in kws:
                    config["categories"][cat]["keywords"].setdefault(kw, 1)
    return config


def load_seen():
    if not os.path.exists(SEEN_PATH):
        return {}
    with open(SEEN_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_seen(seen):
    os.makedirs(os.path.dirname(SEEN_PATH), exist_ok=True)
    with open(SEEN_PATH, "w", encoding="utf-8") as f:
        json.dump(seen, f, indent=2)


def url_hash(url):
    return hashlib.sha256(url.strip().lower().encode("utf-8")).hexdigest()[:16]


def slugify(text, max_len=60):
    text = re.sub(r"[^\w\s-]", "", text.lower())
    text = re.sub(r"[\s_-]+", "-", text).strip("-")
    return text[:max_len] or "untitled"


def score_item(title, summary, categories):
    """Devuelve (mejor_categoria, score, matched_keywords) o (None, 0, []) si no matchea nada."""
    text = f"{title} {summary}".lower()
    best_cat, best_score, best_matches = None, 0, []
    for cat_name, cat in categories.items():
        score = 0
        matches = []
        for kw, weight in cat["keywords"].items():
            if kw.lower() in text:
                score += weight
                matches.append(kw)
        threshold = cat.get("threshold", 3)
        if score >= threshold and score > best_score:
            best_cat, best_score, best_matches = cat_name, score, matches
    return best_cat, best_score, best_matches


def write_note(item, category, score, matches):
    """item: dict con title, url, source, published (ISO str), summary"""
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    cat_dir = os.path.join(NOTES_DIR, category)
    os.makedirs(cat_dir, exist_ok=True)
    fname = f"{date_str}-{slugify(item['title'])}.md"
    path = os.path.join(cat_dir, fname)
    if os.path.exists(path):
        return None

    frontmatter = (
        "---\n"
        f"title: \"{item['title'].replace(chr(34), chr(39))}\"\n"
        f"source: {item['source']}\n"
        f"url: {item['url']}\n"
        f"category: {category}\n"
        f"relevance_score: {score}\n"
        f"matched_keywords: [{', '.join(matches)}]\n"
        f"fetched_at: {datetime.now(timezone.utc).isoformat()}\n"
        f"published: {item.get('published', 'unknown')}\n"
        "status: raw\n"
        "---\n\n"
    )
    body = f"# {item['title']}\n\n{item.get('summary', '').strip()}\n\n[Fuente]({item['url']})\n"

    with open(path, "w", encoding="utf-8") as f:
        f.write(frontmatter + body)
    return path
