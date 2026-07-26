#!/usr/bin/env python3
"""
Find the videos worth learning from and keep a measurement queue topped up.

Deliberately not a channel list. A hand-picked list only ever teaches us what we
already watch; searching the niche surfaces whoever is actually winning it,
including channels nobody here has heard of. Videos already measured are
skipped, so every scheduled run grows the corpus instead of re-measuring the
same files.

Discovery runs in the cloud; measurement does not. YouTube refuses datacenter
IPs outright — "Sign in to confirm you're not a bot", verified on a runner — so
no amount of free Actions minutes buys us a downloaded video. What a runner can
do is talk to the Data API, which is this step. So the cloud keeps the queue
full around the clock and the Mac, on a residential connection, drains it.
"""

import argparse
import json
import logging
import os
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

REPO = Path(__file__).resolve().parent.parent
ISO_UNITS = {"H": 3600, "M": 60, "S": 1}


def parse_duration(iso: str) -> int:
    """PT1H2M3S → seconds."""
    if not iso.startswith("PT"):
        return 0
    total, num = 0, ""
    for ch in iso[2:]:
        if ch.isdigit():
            num += ch
        elif ch in ISO_UNITS and num:
            total += int(num) * ISO_UNITS[ch]
            num = ""
    return total


def already_measured(grammar_dir: Path) -> set[str]:
    return {p.name.replace("_grammar.json", "") for p in grammar_dir.rglob("*_grammar.json")}


def discover(api_key: str, cfg: dict, seen: set[str], limit: int) -> list[dict]:
    from googleapiclient.discovery import build

    yt = build("youtube", "v3", developerKey=api_key)
    candidates: dict[str, dict] = {}

    for query in cfg["queries"]:
        try:
            res = yt.search().list(
                part="snippet", q=query, type="video", maxResults=25,
                order="viewCount", videoDuration="long",
                publishedAfter=cfg.get("published_after"),
                relevanceLanguage="en",
            ).execute()
        except Exception as exc:                      # quota, transient API errors
            log.warning("Search failed for %r: %s", query, exc)
            continue

        ids = [i["id"]["videoId"] for i in res.get("items", [])
               if i["id"].get("videoId") and i["id"]["videoId"] not in seen]
        if not ids:
            continue

        details = yt.videos().list(part="statistics,snippet,contentDetails",
                                   id=",".join(ids)).execute()
        for v in details.get("items", []):
            dur = parse_duration(v["contentDetails"]["duration"])
            views = int(v["statistics"].get("viewCount", 0))
            if views < cfg["min_views"]:
                continue
            if not (cfg["min_duration_sec"] <= dur <= cfg["max_duration_sec"]):
                continue
            candidates[v["id"]] = {
                "video_id": v["id"],
                "title": v["snippet"]["title"],
                "channel": v["snippet"]["channelTitle"],
                "channel_id": v["snippet"]["channelId"],
                "views": views,
                "duration_sec": dur,
                "published_at": v["snippet"]["publishedAt"],
                "found_via": query,
            }
        log.info("%-45s → %d candidates (total %d)", query[:45], len(ids), len(candidates))

    ranked = sorted(candidates.values(), key=lambda v: v["views"], reverse=True)
    return ranked[:limit]


def main() -> None:
    ap = argparse.ArgumentParser(description="Discover niche videos into a measurement queue")
    ap.add_argument("--config", default=str(REPO / "config" / "editing-niche.json"))
    ap.add_argument("--grammar-dir", default=str(REPO / "analysis" / "editing-grammar"))
    ap.add_argument("--queue", default=str(REPO / "queue" / "pending.json"))
    ap.add_argument("--limit", type=int, default=60, help="Queue depth to maintain")
    args = ap.parse_args()

    api_key = os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        raise SystemExit("YOUTUBE_API_KEY not set")

    cfg = json.loads(Path(args.config).read_text())
    grammar_dir = Path(args.grammar_dir)
    grammar_dir.mkdir(parents=True, exist_ok=True)

    queue_path = Path(args.queue)
    queue_path.parent.mkdir(parents=True, exist_ok=True)
    existing = json.loads(queue_path.read_text()) if queue_path.exists() else []

    # Anything already measured is dropped from the queue here rather than being
    # rediscovered forever: the Mac deletes nothing, it only adds measurements.
    measured = already_measured(grammar_dir)
    existing = [v for v in existing if v["video_id"] not in measured]
    log.info("Corpus holds %d videos; %d still queued", len(measured), len(existing))

    room = args.limit - len(existing)
    if room <= 0:
        log.info("Queue already at depth %d — no discovery needed", len(existing))
        queue_path.write_text(json.dumps(existing, indent=2))
        return

    seen = measured | {v["video_id"] for v in existing}
    found = discover(api_key, cfg, seen, room)
    log.info("Discovered %d new videos", len(found))

    # Highest views first: if the Mac only gets through half the queue tonight,
    # it should have measured the half that carries more evidence.
    merged = sorted(existing + found, key=lambda v: v["views"], reverse=True)
    queue_path.write_text(json.dumps(merged, indent=2))
    log.info("Queue depth now %d", len(merged))

    if gh_out := os.environ.get("GITHUB_OUTPUT"):
        with open(gh_out, "a") as f:
            f.write(f"queued={len(merged)}\n")
            f.write(f"added={len(found)}\n")


if __name__ == "__main__":
    main()
