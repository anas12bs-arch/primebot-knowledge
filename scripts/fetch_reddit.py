"""Fetch de posts recientes en subreddits públicos via endpoint .json (sin auth)."""
import requests
from datetime import datetime, timedelta, timezone

HEADERS = {"User-Agent": "primebot-knowledge-scanner/1.0 (personal research bot)"}


def fetch(subreddits, max_age_hours=36, limit=25):
    cutoff = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
    items = []
    for sub in subreddits:
        url = f"https://www.reddit.com/r/{sub}/new.json"
        try:
            resp = requests.get(url, headers=HEADERS, params={"limit": limit}, timeout=15)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"[reddit] error en r/{sub}: {e}")
            continue

        for child in data.get("data", {}).get("children", []):
            post = child.get("data", {})
            created = post.get("created_utc")
            if created:
                pub_dt = datetime.fromtimestamp(created, tz=timezone.utc)
                if pub_dt < cutoff:
                    continue
                published = pub_dt.isoformat()
            else:
                published = "unknown"

            title = post.get("title", "")
            if not title:
                continue
            permalink = post.get("permalink", "")
            items.append({
                "title": title,
                "url": f"https://reddit.com{permalink}" if permalink else post.get("url", ""),
                "source": f"reddit/r/{sub}",
                "published": published,
                "summary": (post.get("selftext") or "")[:400],
            })
    return items
