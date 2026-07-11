#!/usr/bin/env python3
"""Orquestador: fetch de todas las fuentes -> filtro de relevancia -> dedupe -> escribe notas.
Sin llamadas a ningún LLM de pago. Todo heurístico y gratis.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import load_config, load_seen, save_seen, url_hash, score_item, write_note
import fetch_hackernews
import fetch_arxiv
import fetch_reddit
import fetch_rss


def main():
    config = load_config()
    max_age = config.get("max_age_hours", 36)
    categories = config["categories"]
    seen = load_seen()

    print("== Fetching sources ==")
    all_items = []

    hn = fetch_hackernews.fetch([], max_age_hours=max_age)
    print(f"hackernews: {len(hn)} items")
    all_items += hn

    # arXiv publica en tandas (no continuo como HN/RSS) -> ventana mas ancha
    arxiv = fetch_arxiv.fetch(max_age_hours=max(max_age, 72))
    print(f"arxiv: {len(arxiv)} items")
    all_items += arxiv

    reddit = fetch_reddit.fetch(config.get("subreddits", []), max_age_hours=max_age)
    print(f"reddit: {len(reddit)} items")
    all_items += reddit

    rss = fetch_rss.fetch(config.get("rss_feeds", []), max_age_hours=max_age)
    print(f"rss: {len(rss)} items")
    all_items += rss

    print(f"\n== Total fetched: {len(all_items)} ==")

    written = 0
    skipped_seen = 0
    skipped_irrelevant = 0

    for item in all_items:
        if not item.get("url") or not item.get("title"):
            continue

        h = url_hash(item["url"])
        if h in seen:
            skipped_seen += 1
            continue

        cat, score, matches = score_item(item["title"], item.get("summary", ""), categories)
        if not cat:
            skipped_irrelevant += 1
            seen[h] = {"title": item["title"], "reason": "irrelevant"}
            continue

        path = write_note(item, cat, score, matches)
        seen[h] = {"title": item["title"], "category": cat, "score": score}
        if path:
            written += 1
            print(f"  + [{cat}] ({score}) {item['title'][:70]}")

    save_seen(seen)

    print(f"\n== Resumen ==")
    print(f"Nuevas notas escritas: {written}")
    print(f"Ya vistas (skip): {skipped_seen}")
    print(f"Irrelevantes (skip): {skipped_irrelevant}")


if __name__ == "__main__":
    main()
