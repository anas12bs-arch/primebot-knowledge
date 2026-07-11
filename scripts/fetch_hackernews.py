"""Fetch reciente de Hacker News via Algolia Search API (gratis, sin key)."""
import requests
from datetime import datetime, timedelta, timezone

ALGOLIA_URL = "https://hn.algolia.com/api/v1/search_by_date"


def fetch(keywords_flat, max_age_hours=36, limit_per_query=15):
    """keywords_flat: lista plana de keywords a buscar (una query por keyword top-level).
    Para no hacer 60 requests, buscamos por un set reducido de queries generales
    y dejamos que el relevance_filter haga el trabajo fino sobre el resultado.
    """
    since = int((datetime.now(timezone.utc) - timedelta(hours=max_age_hours)).timestamp())
    queries = ["AI model", "video generation", "automation agent", "SaaS pricing", "growth marketing"]
    items = []
    for q in queries:
        try:
            resp = requests.get(
                ALGOLIA_URL,
                params={
                    "query": q,
                    "tags": "story",
                    "numericFilters": f"created_at_i>{since}",
                    "hitsPerPage": limit_per_query,
                },
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"[hackernews] error en query '{q}': {e}")
            continue

        for hit in data.get("hits", []):
            title = hit.get("title") or ""
            url = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}"
            if not title:
                continue
            items.append({
                "title": title,
                "url": url,
                "source": "hackernews",
                "published": hit.get("created_at", "unknown"),
                "summary": f"HN points: {hit.get('points', 0)}, comments: {hit.get('num_comments', 0)}",
            })
    return items
