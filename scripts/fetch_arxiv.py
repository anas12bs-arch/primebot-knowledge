"""Fetch de papers recientes en arXiv (cs.AI, cs.LG, cs.CL) via API oficial, sin key."""
import requests
import feedparser
from datetime import datetime, timedelta, timezone

ARXIV_API = "http://export.arxiv.org/api/query"
CATEGORIES = ["cs.AI", "cs.LG", "cs.CL", "cs.CV"]


def fetch(max_age_hours=36, max_results=25):
    # OJO: arXiv usa "+" literal como separador booleano en su query string.
    # requests.get(params=...) URL-encodearia ese "+" a "%2B" y rompe la query,
    # asi que construimos la URL a mano en vez de pasar por params.
    cat_query = "+OR+".join(f"cat:{c}" for c in CATEGORIES)
    url = (
        f"{ARXIV_API}?search_query={cat_query}"
        f"&sortBy=submittedDate&sortOrder=descending&max_results={max_results}"
    )
    try:
        resp = requests.get(url, timeout=20)
        resp.raise_for_status()
    except Exception as e:
        print(f"[arxiv] error: {e}")
        return []

    feed = feedparser.parse(resp.text)
    cutoff = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
    items = []
    for entry in feed.entries:
        published = entry.get("published", "")
        try:
            pub_dt = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            if pub_dt < cutoff:
                continue
        except Exception:
            pass
        items.append({
            "title": entry.title.replace("\n", " ").strip(),
            "url": entry.link,
            "source": "arxiv",
            "published": published,
            "summary": entry.get("summary", "").replace("\n", " ").strip()[:500],
        })
    return items
