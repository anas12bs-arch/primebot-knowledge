#!/usr/bin/env python3
"""
Find the videos worth learning from and keep a measurement queue topped up.

Deliberately not a channel list. A hand-picked list only ever teaches us what we
already watch; searching the niche surfaces whoever is actually winning it,
including channels nobody here has heard of. Videos already measured are
skipped, so every run grows the corpus instead of re-measuring the same files.

Runs on the Mac, not in the cloud, and needs no API key. Two separate findings
forced that:

  1. YouTube refuses datacenter IPs outright — "Sign in to confirm you're not a
     bot", verified on a runner — so no amount of free Actions minutes buys a
     downloaded video. Discovery in the cloud only ever produced a queue that
     nothing could drain.
  2. The Data API path needed a YOUTUBE_API_KEY that was never set, so the
     scheduled workflow failed every six hours from the day it was written.

yt-dlp reads search results without credentials, which removes the secret, the
quota and the cloud round-trip in one go.
"""

import argparse
import json
import logging
import subprocess
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

REPO = Path(__file__).resolve().parent.parent

# Flat search returns everything except the upload date, so dates are confirmed
# in a second pass over survivors only. Searching wide and confirming narrow
# keeps that pass small — most candidates die on views or duration first.
SEARCH_DEPTH = 25
DATE_PROBE_TIMEOUT = 300


def yt_dlp_bin() -> str:
    """Prefer the copy next to this interpreter — launchd's PATH is minimal."""
    candidate = Path(sys.executable).parent / "yt-dlp"
    return str(candidate) if candidate.exists() else "yt-dlp"


def already_measured(grammar_dir: Path) -> set[str]:
    return {p.name.replace("_grammar.json", "") for p in grammar_dir.rglob("*_grammar.json")}


def search(query: str, depth: int) -> list[dict]:
    """One keyless search. Flat mode: a single request for the whole page."""
    proc = subprocess.run(
        [yt_dlp_bin(), "--flat-playlist", "--dump-json", "--no-warnings",
         "--ignore-errors", f"ytsearch{depth}:{query}"],
        capture_output=True, text=True, timeout=120,
    )
    out = []
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    if not out and proc.returncode:
        log.warning("Search failed for %r: %s", query, proc.stderr.strip()[:200])
    return out


def upload_dates(video_ids: list[str]) -> dict[str, str]:
    """YYYYMMDD per id. One invocation for the whole batch, ~1.5s each."""
    if not video_ids:
        return {}
    proc = subprocess.run(
        [yt_dlp_bin(), "--skip-download", "--no-warnings", "--ignore-errors",
         "--print", "%(id)s|%(upload_date)s", *video_ids],
        capture_output=True, text=True, timeout=DATE_PROBE_TIMEOUT,
    )
    dates = {}
    for line in proc.stdout.splitlines():
        vid, _, date = line.strip().partition("|")
        if vid and date.isdigit():
            dates[vid] = date
    return dates


def discover(cfg: dict, seen: set[str], limit: int) -> list[dict]:
    candidates: dict[str, dict] = {}

    for query in cfg["queries"]:
        hits = search(query, SEARCH_DEPTH)
        kept = 0
        for v in hits:
            vid = v.get("id")
            views = v.get("view_count") or 0
            dur = v.get("duration") or 0
            if not vid or vid in seen or vid in candidates:
                continue
            if views < cfg["min_views"]:
                continue
            if not (cfg["min_duration_sec"] <= dur <= cfg["max_duration_sec"]):
                continue
            candidates[vid] = {
                "video_id": vid,
                "title": v.get("title") or "",
                "channel": v.get("channel") or v.get("uploader") or "",
                "channel_id": v.get("channel_id") or "",
                "views": int(views),
                "duration_sec": int(dur),
                "found_via": query,
            }
            kept += 1
        log.info("%-45s → %2d kept (pool %d)", query[:45], kept, len(candidates))

    if not candidates:
        return []

    # Rank before confirming dates: if the pool is large only the top slice
    # needs dating, and every probe is a network round-trip.
    ranked = sorted(candidates.values(), key=lambda v: v["views"], reverse=True)
    probe = ranked[: limit * 2]
    cutoff = cfg.get("published_after", "")[:10].replace("-", "")

    dates = upload_dates([v["video_id"] for v in probe])
    fresh = []
    for v in probe:
        date = dates.get(v["video_id"])
        if not date:
            continue                      # unreachable or removed; drop quietly
        if cutoff and date < cutoff:
            continue
        v["published_at"] = f"{date[:4]}-{date[4:6]}-{date[6:]}"
        fresh.append(v)

    log.info("%d candidates → %d inside the date window", len(probe), len(fresh))
    return fresh[:limit]


def main() -> None:
    ap = argparse.ArgumentParser(description="Discover niche videos into a measurement queue")
    ap.add_argument("--config", default=str(REPO / "config" / "editing-niche.json"))
    ap.add_argument("--grammar-dir", default=str(REPO / "analysis" / "editing-grammar"))
    ap.add_argument("--queue", default=str(REPO / "queue" / "pending.json"))
    ap.add_argument("--limit", type=int, default=60, help="Queue depth to maintain")
    args = ap.parse_args()

    cfg = json.loads(Path(args.config).read_text())
    grammar_dir = Path(args.grammar_dir)
    grammar_dir.mkdir(parents=True, exist_ok=True)

    queue_path = Path(args.queue)
    queue_path.parent.mkdir(parents=True, exist_ok=True)
    existing = json.loads(queue_path.read_text()) if queue_path.exists() else []

    # Anything already measured is dropped from the queue here rather than being
    # rediscovered forever: the measuring pass deletes nothing, it only adds.
    measured = already_measured(grammar_dir)
    existing = [v for v in existing if v["video_id"] not in measured]
    log.info("Corpus holds %d videos; %d still queued", len(measured), len(existing))

    room = args.limit - len(existing)
    if room <= 0:
        log.info("Queue already at depth %d — no discovery needed", len(existing))
        queue_path.write_text(json.dumps(existing, indent=2))
        return

    seen = measured | {v["video_id"] for v in existing}
    found = discover(cfg, seen, room)
    log.info("Discovered %d new videos", len(found))

    # Highest views first: if only half the queue gets measured tonight, it
    # should be the half that carries more evidence.
    merged = sorted(existing + found, key=lambda v: v["views"], reverse=True)
    queue_path.write_text(json.dumps(merged, indent=2))
    log.info("Queue depth now %d", len(merged))


if __name__ == "__main__":
    main()
