#!/usr/bin/env python3
"""
Find the videos worth learning from, then split the work into shards.

Deliberately not a channel list. A hand-picked list only ever teaches us what we
already watch; searching the niche surfaces whoever is actually winning it,
including channels nobody here has heard of. Videos already measured in this
repo are skipped, so every scheduled run grows the corpus instead of
re-measuring the same files.
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
    ap = argparse.ArgumentParser(description="Discover niche videos and shard them")
    ap.add_argument("--config", default=str(REPO / "config" / "editing-niche.json"))
    ap.add_argument("--grammar-dir", default=str(REPO / "analysis" / "editing-grammar"))
    ap.add_argument("--out-dir", default="shards")
    ap.add_argument("--limit", type=int, default=40, help="New videos per run")
    ap.add_argument("--shards", type=int, default=8)
    args = ap.parse_args()

    api_key = os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        raise SystemExit("YOUTUBE_API_KEY not set")

    cfg = json.loads(Path(args.config).read_text())
    grammar_dir = Path(args.grammar_dir)
    grammar_dir.mkdir(parents=True, exist_ok=True)

    seen = already_measured(grammar_dir)
    log.info("Corpus already holds %d measured videos", len(seen))

    videos = discover(api_key, cfg, seen, args.limit)
    log.info("Selected %d new videos", len(videos))

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    # Round-robin rather than contiguous blocks: view count correlates with
    # runtime, so contiguous slicing would hand one runner every long video.
    shards = [[] for _ in range(args.shards)]
    for i, v in enumerate(videos):
        shards[i % args.shards].append(v)

    used = 0
    for i, shard in enumerate(shards):
        if not shard:
            continue
        (out / f"shard-{i}.json").write_text(json.dumps(shard, indent=2))
        used += 1

    matrix = [i for i, s in enumerate(shards) if s]
    print(json.dumps({"count": len(videos), "shards": matrix}))

    if gh_out := os.environ.get("GITHUB_OUTPUT"):
        with open(gh_out, "a") as f:
            f.write(f"count={len(videos)}\n")
            f.write(f"matrix={json.dumps(matrix)}\n")
    log.info("Wrote %d shard file(s)", used)


if __name__ == "__main__":
    main()
