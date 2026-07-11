"""Fetch de feeds RSS curados (blogs oficiales de labs de IA, tech news)."""
import feedparser
from datetime import datetime, timedelta, timezone
import time


def fetch(feed_urls, max_age_hours=36):
    cutoff = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
    items = []
    for url in feed_urls:
        try:
            feed = feedparser.parse(url)
        except Exception as e:
            print(f"[rss] error en {url}: {e}")
            continue

        source_name = feed.feed.get("title", url) if feed.get("feed") else url

        for entry in feed.entries[:20]:
            pub_dt = None
            if entry.get("published_parsed"):
                pub_dt = datetime.fromtimestamp(time.mktime(entry.published_parsed), tz=timezone.utc)
            elif entry.get("updated_parsed"):
                pub_dt = datetime.fromtimestamp(time.mktime(entry.updated_parsed), tz=timezone.utc)

            if pub_dt and pub_dt < cutoff:
                continue

            title = entry.get("title", "")
            if not title:
                continue

            summary = entry.get("summary", "") or entry.get("description", "")
            items.append({
                "title": title,
                "url": entry.get("link", url),
                "source": f"rss/{source_name}",
                "published": pub_dt.isoformat() if pub_dt else "unknown",
                "summary": summary[:500],
            })
    return items
