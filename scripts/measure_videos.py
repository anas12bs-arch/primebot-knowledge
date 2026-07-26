#!/usr/bin/env python3
"""
Download and measure one shard of videos. Cloud half of the learning engine.

Runs on a GitHub runner: measures editorial grammar and motion design, writes
JSON, and deletes the video immediately. Only the measurements are ever kept —
they are a few kB each, so the corpus can grow indefinitely inside the repo
while no copyrighted footage is ever stored or committed.

Failure here is expected and survivable. A blocked download or a codec the
runner cannot decode costs one video, never the run: the remaining shards and
the existing corpus are untouched.
"""

import argparse
import json
import logging
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

# Fewer shots than this means the decode produced nothing usable — measuring it
# would drag the corpus-wide average shot length toward the whole runtime.
MIN_SHOTS_FOR_TRUST = 4


def download(video_id: str, dest: Path) -> Path | None:
    dest.mkdir(parents=True, exist_ok=True)
    out = dest / f"{video_id}.mp4"

    # 720p: every measurement is structural (cut points, optical flow, luma
    # percentiles). Higher resolution costs bandwidth and decode time without
    # moving a single number.
    cmd = [
        "yt-dlp", "-f", "best[ext=mp4][height<=720]/best[ext=mp4]/best",
        "-o", str(out), "--no-warnings", "--quiet",
        "--no-playlist", "--socket-timeout", "30", "--retries", "3",
        f"https://www.youtube.com/watch?v={video_id}",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
    if r.returncode != 0 or not out.exists():
        log.error("Download failed %s: %s", video_id, (r.stderr or "").strip()[:160])
        return None
    return out


def measure(path: Path, video: dict, out_dir: Path) -> bool:
    from extract_editorial_grammar import extract
    from dataclasses import asdict

    report = asdict(extract(path, video["video_id"]))
    if len(report.get("shots", [])) < MIN_SHOTS_FOR_TRUST:
        log.warning("Discarding %s — only %d shots (likely decode failure)",
                    video["video_id"], len(report.get("shots", [])))
        return False

    report["metadata"] = video
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"{video['video_id']}_grammar.json").write_text(json.dumps(report, indent=2))
    return True


def main() -> None:
    ap = argparse.ArgumentParser(description="Measure a shard of videos")
    ap.add_argument("--shard", required=True, help="JSON file listing videos")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--work-dir", default="/tmp/learning-videos")
    args = ap.parse_args()

    videos = json.loads(Path(args.shard).read_text())
    work = Path(args.work_dir)
    out_dir = Path(args.out_dir)

    ok = failed = 0
    for v in videos:
        log.info("→ %s | %s (%s views)", v["channel"][:22], v["title"][:48], f"{v['views']:,}")
        path = None
        try:
            path = download(v["video_id"], work)
            if path and measure(path, v, out_dir):
                ok += 1
            else:
                failed += 1
        except Exception as exc:
            log.error("Failed %s: %s", v["video_id"], exc)
            failed += 1
        finally:
            # Delete immediately: a runner has ~14GB and a shard can exceed it.
            if path and path.exists():
                path.unlink()

    log.info("Shard complete: %d measured, %d failed", ok, failed)
    if ok == 0 and failed:
        # Surfaces a systemic problem (YouTube blocking the runner, a yt-dlp
        # break) instead of letting the run pass with an empty result.
        raise SystemExit("Every video in this shard failed")


if __name__ == "__main__":
    main()
