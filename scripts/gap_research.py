#!/usr/bin/env python3
"""Deep-research worker (estilo NotebookLM): para cada gap pendiente en
gaps/pending.md, agrega evidencia de 4 fuentes gratuitas (Wikipedia,
arXiv, Semantic Scholar, HackerNews all-time) y escribe un brief citado
en notes/deep-research/.

Sin GEMINI_API_KEY: el brief queda en status "gathered" (material listo,
síntesis la hace Claude en sesión — barato porque todo está pre-recolectado).
Con GEMINI_API_KEY (free tier): añade una pasada de síntesis automática.
"""
import os
import re
import sys
import json
import requests
import feedparser
from datetime import datetime, timezone
from urllib.parse import quote_plus

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT, slugify

GAPS_PATH = os.path.join(ROOT, "gaps", "pending.md")
OUT_DIR = os.path.join(ROOT, "notes", "deep-research")
MAX_GAPS_PER_RUN = 3
HEADERS = {"User-Agent": "primebot-knowledge-research/1.0"}


def parse_gaps():
    """Lineas '- [ ] slug | query' -> [(slug, query, raw_line)]"""
    if not os.path.exists(GAPS_PATH):
        return []
    gaps = []
    with open(GAPS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            m = re.match(r"^- \[ \] ([\w-]+) \| (.+)$", line.strip())
            if m:
                gaps.append((m.group(1), m.group(2).strip(), line.rstrip("\n")))
    return gaps


def mark_done(raw_line):
    with open(GAPS_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    done_line = raw_line.replace("- [ ]", "- [x]", 1) + f"  (done {datetime.now(timezone.utc).strftime('%Y-%m-%d')})"
    content = content.replace(raw_line, done_line, 1)
    with open(GAPS_PATH, "w", encoding="utf-8") as f:
        f.write(content)


def subqueries(query, max_sub=4):
    """Wikipedia y HN fallan con queries largas: descomponer en bigramas.
    Devuelve [query_completa, bigrama1, bigrama2, ...]."""
    words = query.split()
    subs = [query]
    for i in range(0, len(words) - 1, 2):
        subs.append(" ".join(words[i:i + 2]))
    return subs[:max_sub + 1]


def fetch_wikipedia(query, limit=3):
    items, seen_titles = [], set()
    for sub in subqueries(query):
        if len(items) >= limit:
            break
        try:
            r = requests.get(
                "https://en.wikipedia.org/w/api.php",
                params={"action": "opensearch", "search": sub, "limit": 2, "format": "json"},
                headers=HEADERS, timeout=15,
            )
            for t in r.json()[1]:
                if t in seen_titles or len(items) >= limit:
                    continue
                seen_titles.add(t)
                # La API REST de Wikipedia usa underscores en titulos, no '+'
                s = requests.get(
                    f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote_plus(t.replace(' ', '_'))}",
                    headers=HEADERS, timeout=15,
                ).json()
                if s.get("extract"):
                    items.append({"title": t, "snippet": s["extract"][:600],
                                  "url": s.get("content_urls", {}).get("desktop", {}).get("page", "")})
        except Exception as e:
            print(f"  [wikipedia:{sub[:20]}] {e}")
    return items


def fetch_arxiv_search(query, limit=5):
    items = []
    try:
        url = (f"http://export.arxiv.org/api/query?search_query=all:{quote_plus(query)}"
               f"&sortBy=relevance&max_results={limit}")
        feed = feedparser.parse(requests.get(url, timeout=20).text)
        for e in feed.entries:
            items.append({"title": e.title.replace("\n", " ").strip(),
                          "snippet": e.get("summary", "").replace("\n", " ").strip()[:600],
                          "url": e.link, "meta": e.get("published", "")[:10]})
    except Exception as e:
        print(f"  [arxiv] {e}")
    return items


def fetch_semantic_scholar(query, limit=5, retries=3):
    """S2 anónimo comparte rate-limit global -> 429 frecuente. Retry con backoff."""
    import time
    for attempt in range(retries):
        try:
            r = requests.get(
                "https://api.semanticscholar.org/graph/v1/paper/search",
                params={"query": query, "limit": limit,
                        "fields": "title,abstract,url,year,citationCount"},
                headers=HEADERS, timeout=20,
            )
            if r.status_code == 429:
                wait = 15 * (attempt + 1)
                print(f"  [semanticscholar] 429, retry en {wait}s")
                time.sleep(wait)
                continue
            r.raise_for_status()
            return [{"title": p.get("title", ""),
                     "snippet": (p.get("abstract") or "")[:600],
                     "url": p.get("url", ""),
                     "meta": f"{p.get('year', '?')}, {p.get('citationCount', 0)} citas"}
                    for p in r.json().get("data", [])]
        except Exception as e:
            print(f"  [semanticscholar] {e}")
            break
    return []


def fetch_hn_alltime(query, limit=8):
    items, seen_ids = [], set()
    for sub in subqueries(query):
        if len(items) >= limit:
            break
        try:
            r = requests.get(
                "https://hn.algolia.com/api/v1/search",
                params={"query": sub, "tags": "story",
                        "numericFilters": "points>40", "hitsPerPage": limit},
                headers=HEADERS, timeout=15,
            )
            for h in r.json().get("hits", []):
                oid = h.get("objectID")
                if oid in seen_ids or len(items) >= limit:
                    continue
                seen_ids.add(oid)
                items.append({"title": h.get("title", ""),
                              "snippet": f"{h.get('points', 0)} puntos, {h.get('num_comments', 0)} comentarios",
                              "url": h.get("url") or f"https://news.ycombinator.com/item?id={oid}",
                              "meta": (h.get("created_at") or "")[:10]})
        except Exception as e:
            print(f"  [hn:{sub[:20]}] {e}")
    return items


def gemini_synthesize(query, sections_md):
    """Sintesis opcional con Gemini free tier. Devuelve None si no hay key o falla."""
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not key:
        return None
    model = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
    prompt = (
        f"Eres un investigador. Tema: {query}\n\n"
        "A partir SOLO de las fuentes de abajo (no inventes nada que no esté), escribe una síntesis de 300-500 palabras:\n"
        "1) mecanismo/hallazgos clave, 2) implicación práctica para un estudio de motion design B2B unipersonal, "
        "3) condiciones límite / qué NO se puede concluir. Cita las fuentes por título.\n\n"
        f"FUENTES:\n{sections_md[:15000]}"
    )
    try:
        r = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
            params={"key": key},
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=60,
        )
        r.raise_for_status()
        return r.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print(f"  [gemini] síntesis falló, brief queda en 'gathered': {e}")
        return None


def render_section(name, items):
    if not items:
        return f"## {name}\n\n(sin resultados)\n"
    out = [f"## {name}\n"]
    for it in items:
        meta = f" ({it['meta']})" if it.get("meta") else ""
        out.append(f"### {it['title']}{meta}\n{it['snippet']}\n[Fuente]({it['url']})\n")
    return "\n".join(out)


def research_gap(slug, query):
    print(f"== Gap: {slug} | {query}")
    wiki = fetch_wikipedia(query)
    arxiv = fetch_arxiv_search(query)
    s2 = fetch_semantic_scholar(query)
    hn = fetch_hn_alltime(query)
    total = len(wiki) + len(arxiv) + len(s2) + len(hn)
    print(f"  fuentes: wiki={len(wiki)} arxiv={len(arxiv)} s2={len(s2)} hn={len(hn)}")

    sections = "\n".join([
        render_section("Contexto (Wikipedia)", wiki),
        render_section("Papers (arXiv)", arxiv),
        render_section("Papers (Semantic Scholar)", s2),
        render_section("Discusión práctica (HackerNews, all-time, >40 puntos)", hn),
    ])

    synthesis = gemini_synthesize(query, sections) if total > 0 else None
    status = "synthesized" if synthesis else "gathered"
    synth_block = synthesis or (
        "PENDIENTE — Claude: sintetizar en sesión. Formato: mecanismo → "
        "implicación práctica para Anas → condición límite. Solo con las fuentes de arriba."
    )

    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, f"{date_str}-{slugify(slug)}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(
            "---\n"
            f"gap: {slug}\n"
            f"query: \"{query}\"\n"
            f"status: {status}\n"
            f"sources_count: {total}\n"
            f"generated_at: {datetime.now(timezone.utc).isoformat()}\n"
            "---\n\n"
            f"# Deep research: {query}\n\n"
            f"{sections}\n\n---\n\n## Síntesis\n\n{synth_block}\n"
        )
    print(f"  -> {path} [{status}]")
    return total > 0


def main():
    gaps = parse_gaps()
    if not gaps:
        print("Sin gaps pendientes.")
        return
    for slug, query, raw in gaps[:MAX_GAPS_PER_RUN]:
        ok = research_gap(slug, query)
        if ok:
            mark_done(raw)
        else:
            print(f"  0 fuentes para '{slug}' — se deja pendiente para reintentar")


if __name__ == "__main__":
    main()
