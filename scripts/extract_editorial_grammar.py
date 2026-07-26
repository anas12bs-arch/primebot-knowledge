#!/usr/bin/env python3
"""
Editorial grammar extractor.

NOT a pixel-stats dumper. This measures what a professional editor actually
reasons about: cut rhythm, hook anatomy, text cadence, grade characteristics
and camera language. The output feeds `distill_editing_doctrine.py`, which
turns many videos into craft doctrine for OpenMontage.

Why these metrics and not "dominant hex colors": a colorist does not think
"#ff6432 at 23%". They think "blacks lifted to 6 IRE, highlights rolled off,
shadows pushed teal, skin protected". An editor does not think "motion 12.5".
They think "ASL 2.1s in the hook, 4.8s in the body — the hook is cut twice
as fast to buy the first 30 seconds of retention".
"""

import argparse
import json
import logging
import subprocess
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Any

import cv2
import numpy as np

from extract_motion_design import extract_motion_design

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

# A cut is declared when consecutive-frame histogram correlation drops below
# this. Tuned to catch hard cuts and fast dissolves without firing on a
# whip-pan. Dissolves longer than ~0.5s read as motion, not as a cut — that is
# intentional: they belong to the transition vocabulary, measured separately.
CUT_CORRELATION_THRESHOLD = 0.72
MIN_SHOT_FRAMES = 4


@dataclass
class ShotStats:
    index: int
    start_sec: float
    duration_sec: float
    mean_flow: float
    flow_coherence: float
    camera: str


@dataclass
class GrammarReport:
    video_id: str
    duration_sec: float
    fps: float
    cut_rhythm: dict[str, Any] = field(default_factory=dict)
    hook: dict[str, Any] = field(default_factory=dict)
    text_cadence: dict[str, Any] = field(default_factory=dict)
    grade: dict[str, Any] = field(default_factory=dict)
    camera_language: dict[str, Any] = field(default_factory=dict)
    # Transition vocabulary, graphic entrances, shot movement, audio sync —
    # see extract_motion_design.py.
    transitions: dict[str, Any] = field(default_factory=dict)
    motion_graphics: dict[str, Any] = field(default_factory=dict)
    shot_movement: dict[str, Any] = field(default_factory=dict)
    audio_sync: dict[str, Any] = field(default_factory=dict)
    shots: list[dict] = field(default_factory=list)


def probe_duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True,
    )
    try:
        return float(out.stdout.strip())
    except ValueError:
        return 0.0


def detect_shots(path: Path, analysis_fps: float = 8.0) -> tuple[list[tuple[float, float]], float]:
    """Return [(start_sec, duration_sec)] per shot, plus source fps.

    Histogram-correlation cut detection at a reduced sampling rate. 8 fps is
    enough to place a cut within ~125ms, which is below the threshold where an
    editor would perceive the boundary as being in a different place.
    """
    cap = cv2.VideoCapture(str(path))
    src_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    step = max(1, int(round(src_fps / analysis_fps)))

    boundaries: list[int] = [0]
    prev_hist = None
    idx = 0

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if idx % step == 0:
            small = cv2.resize(frame, (160, 90))
            hsv = cv2.cvtColor(small, cv2.COLOR_BGR2HSV)
            hist = cv2.calcHist([hsv], [0, 1], None, [32, 32], [0, 180, 0, 256])
            cv2.normalize(hist, hist, 0, 1, cv2.NORM_MINMAX)
            if prev_hist is not None:
                corr = cv2.compareHist(prev_hist, hist, cv2.HISTCMP_CORREL)
                if corr < CUT_CORRELATION_THRESHOLD and idx - boundaries[-1] >= MIN_SHOT_FRAMES * step:
                    boundaries.append(idx)
            prev_hist = hist
        idx += 1

    cap.release()
    total = idx
    boundaries.append(total)

    shots = []
    for a, b in zip(boundaries, boundaries[1:]):
        shots.append((a / src_fps, (b - a) / src_fps))
    return shots, src_fps


def analyse_cut_rhythm(shots: list[tuple[float, float]], duration: float) -> dict[str, Any]:
    """Average shot length plus how cut density is distributed across the video.

    ASL is the standard film-studies pacing metric. The density curve matters
    more for retention work: it shows whether the editor front-loads cuts to
    survive the first 30 seconds and then lets the middle breathe.
    """
    durations = [d for _, d in shots if d > 0]
    if not durations:
        return {}

    arr = np.array(durations)
    deciles = [0.0] * 10
    for start, dur in shots:
        bucket = min(9, int((start / duration) * 10)) if duration else 0
        deciles[bucket] += 1

    return {
        "total_cuts": len(shots) - 1,
        "average_shot_length_sec": round(float(arr.mean()), 2),
        "median_shot_length_sec": round(float(np.median(arr)), 2),
        "shortest_shot_sec": round(float(arr.min()), 2),
        "longest_shot_sec": round(float(arr.max()), 2),
        "p25_shot_sec": round(float(np.percentile(arr, 25)), 2),
        "p75_shot_sec": round(float(np.percentile(arr, 75)), 2),
        "cuts_per_minute": round(len(shots) / (duration / 60), 1) if duration else 0,
        "cut_density_by_decile": deciles,
    }


def analyse_hook(shots: list[tuple[float, float]], duration: float) -> dict[str, Any]:
    """The first 15 seconds decide whether the rest of the edit is ever seen."""
    def cuts_before(t: float) -> int:
        return sum(1 for start, _ in shots if 0 < start <= t)

    body = [d for start, d in shots if start > 15]
    hook_shots = [d for start, d in shots if start <= 15]
    hook_asl = float(np.mean(hook_shots)) if hook_shots else 0.0
    body_asl = float(np.mean(body)) if body else hook_asl

    return {
        "cuts_first_5s": cuts_before(5),
        "cuts_first_15s": cuts_before(15),
        "hook_asl_sec": round(hook_asl, 2),
        "body_asl_sec": round(body_asl, 2),
        # >1 means the hook is cut faster than the body.
        "hook_acceleration_ratio": round(body_asl / hook_asl, 2) if hook_asl > 0 else 0,
        "first_shot_duration_sec": round(shots[0][1], 2) if shots else 0,
    }


def analyse_grade(path: Path, sample_count: int = 24) -> dict[str, Any]:
    """Colorist-grade measurements: contrast, black lift, split-tone, saturation.

    Split-tone is the useful one. Comparing the mean hue of the darkest pixels
    against the brightest pixels is how you detect the teal-orange treatment
    that dominates commercial and thriller grading, and it survives across
    shots in a way a dominant-color histogram does not.
    """
    cap = cv2.VideoCapture(str(path))
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1
    indices = np.linspace(0, max(0, total - 1), sample_count, dtype=int)

    blacks, whites, sats, temps = [], [], [], []
    shadow_hues, highlight_hues = [], []

    for i in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(i))
        ok, frame = cap.read()
        if not ok:
            continue
        small = cv2.resize(frame, (320, 180))
        gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(small, cv2.COLOR_BGR2HSV)

        blacks.append(float(np.percentile(gray, 1)))
        whites.append(float(np.percentile(gray, 99)))
        sats.append(float(hsv[..., 1].mean()))

        b, g, r = small[..., 0].mean(), small[..., 1].mean(), small[..., 2].mean()
        temps.append(float(r - b))

        lum = gray.reshape(-1)
        hue = hsv[..., 0].reshape(-1)
        shadow_mask = lum <= np.percentile(lum, 25)
        highlight_mask = lum >= np.percentile(lum, 75)
        if shadow_mask.any():
            shadow_hues.append(float(np.median(hue[shadow_mask])))
        if highlight_mask.any():
            highlight_hues.append(float(np.median(hue[highlight_mask])))

    cap.release()
    if not blacks:
        return {}

    black_point = float(np.mean(blacks))
    white_point = float(np.mean(whites))
    shadow_hue = float(np.mean(shadow_hues)) if shadow_hues else 0.0
    highlight_hue = float(np.mean(highlight_hues)) if highlight_hues else 0.0

    return {
        # 0-255 scale. Above ~16 means the blacks are deliberately lifted
        # (filmic / faded look) rather than crushed to true black.
        "black_point": round(black_point, 1),
        "white_point": round(white_point, 1),
        "contrast_range": round(white_point - black_point, 1),
        "blacks_lifted": bool(black_point > 16),
        "highlights_rolled_off": bool(white_point < 240),
        "mean_saturation": round(float(np.mean(sats)), 1),
        "saturation_character": (
            "desaturated" if np.mean(sats) < 70
            else "natural" if np.mean(sats) < 120
            else "punchy"
        ),
        # OpenCV hue is 0-180. ~90-105 is teal/cyan, ~10-25 is orange.
        "shadow_hue_opencv": round(shadow_hue, 1),
        "highlight_hue_opencv": round(highlight_hue, 1),
        "split_tone": _describe_split_tone(shadow_hue, highlight_hue),
        "temperature_bias": (
            "warm" if np.mean(temps) > 8
            else "cool" if np.mean(temps) < -8
            else "neutral"
        ),
    }


def _describe_split_tone(shadow_hue: float, highlight_hue: float) -> str:
    def name(h: float) -> str:
        if h < 15 or h >= 170:
            return "red"
        if h < 25:
            return "orange"
        if h < 35:
            return "yellow"
        if h < 85:
            return "green"
        if h < 105:
            return "teal"
        if h < 135:
            return "blue"
        return "magenta"

    s, hl = name(shadow_hue), name(highlight_hue)
    if s == hl:
        return f"unified {s}"
    return f"{s} shadows / {hl} highlights"


def analyse_camera(path: Path, shots: list[tuple[float, float]], fps: float) -> tuple[list[ShotStats], dict[str, Any]]:
    """Classify each shot's camera language from optical flow.

    Magnitude alone cannot separate "camera pushes in" from "subject runs
    across a locked frame". Coherence — how aligned the flow vectors are —
    does: a camera move produces globally consistent vectors, subject motion
    produces a local pocket of disagreement.
    """
    cap = cv2.VideoCapture(str(path))
    stats: list[ShotStats] = []

    for i, (start, dur) in enumerate(shots):
        # Two frames from the middle of the shot, avoiding the boundary
        # where the incoming/outgoing frames would fake a huge flow reading.
        mid = start + dur / 2
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(mid * fps))
        ok1, f1 = cap.read()
        ok2, f2 = cap.read()
        if not (ok1 and ok2):
            continue

        g1 = cv2.cvtColor(cv2.resize(f1, (160, 90)), cv2.COLOR_BGR2GRAY)
        g2 = cv2.cvtColor(cv2.resize(f2, (160, 90)), cv2.COLOR_BGR2GRAY)
        flow = cv2.calcOpticalFlowFarneback(g1, g2, None, 0.5, 3, 15, 3, 5, 1.2, 0)

        mag, ang = cv2.cartToPolar(flow[..., 0], flow[..., 1])
        mean_mag = float(mag.mean())

        # Circular variance of flow direction, weighted by magnitude.
        weights = mag.reshape(-1)
        angles = ang.reshape(-1)
        if weights.sum() > 1e-6:
            cx = float(np.average(np.cos(angles), weights=weights))
            cy = float(np.average(np.sin(angles), weights=weights))
            coherence = float(np.hypot(cx, cy))
        else:
            coherence = 0.0

        if mean_mag < 0.35:
            camera = "locked"
        elif coherence > 0.7:
            camera = "camera_move"
        elif mean_mag > 2.0:
            camera = "dynamic_subject"
        else:
            camera = "drift"

        stats.append(ShotStats(i, round(start, 2), round(dur, 2),
                               round(mean_mag, 2), round(coherence, 2), camera))

    cap.release()

    counts: dict[str, int] = {}
    for s in stats:
        counts[s.camera] = counts.get(s.camera, 0) + 1
    total = len(stats) or 1

    return stats, {
        "shot_camera_distribution": counts,
        "locked_shot_ratio": round(counts.get("locked", 0) / total, 2),
        "camera_move_ratio": round(counts.get("camera_move", 0) / total, 2),
        "dominant_camera_language": max(counts, key=counts.get) if counts else "unknown",
    }


def _ocr_frame(frame, pytesseract) -> tuple[bool, list[str]]:
    h, w = frame.shape[:2]
    small = cv2.resize(frame, (640, int(640 * h / w)))
    gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
    data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)

    found = False
    positions: list[str] = []
    for i, conf in enumerate(data["conf"]):
        try:
            c = int(conf)
        except (ValueError, TypeError):
            continue
        if c > 60 and data["text"][i].strip():
            found = True
            y = data["top"][i] / small.shape[0]
            positions.append("upper" if y < 0.33 else "center" if y < 0.66 else "lower")
    return found, positions


def analyse_text_cadence(
    path: Path,
    duration: float,
    coverage_samples: int = 120,
    dense_windows: int = 3,
    dense_window_sec: float = 40.0,
    dense_interval: float = 0.5,
) -> dict[str, Any]:
    """How long text stays on screen and where it sits.

    Two-tier sampling, because the two questions have different cost profiles.

    Coverage ("is this a text-driven edit?") only needs a wide, sparse spread —
    120 samples across the runtime answers it within a couple of percent.

    Block duration ("can a viewer actually read it?") needs dense sampling, but
    only over a few windows: text rhythm is a repeated habit, not something that
    changes across the video. Three 40s windows at 0.5s resolution measure it.

    A naive dense pass over everything would be ~2400 OCR calls on a 20-minute
    video. This is ~360, bounded regardless of runtime.
    """
    try:
        import pytesseract
    except ImportError:
        log.warning("pytesseract unavailable — skipping text cadence")
        return {}

    cap = cv2.VideoCapture(str(path))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1

    # --- Tier 1: sparse coverage across the whole runtime ---
    presence: list[bool] = []
    positions: list[str] = []
    for idx in np.linspace(0, max(0, total_frames - 1), coverage_samples, dtype=int):
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(idx))
        ok, frame = cap.read()
        if not ok:
            continue
        found, pos = _ocr_frame(frame, pytesseract)
        presence.append(found)
        positions.extend(pos)

    if not presence:
        cap.release()
        return {}

    # --- Tier 2: dense windows for block duration ---
    runs: list[float] = []
    if duration > dense_window_sec:
        starts = np.linspace(0, max(0.0, duration - dense_window_sec), dense_windows)
        for start in starts:
            window_presence: list[bool] = []
            t = start
            while t < start + dense_window_sec:
                cap.set(cv2.CAP_PROP_POS_FRAMES, int(t * fps))
                ok, frame = cap.read()
                if not ok:
                    break
                found, _ = _ocr_frame(frame, pytesseract)
                window_presence.append(found)
                t += dense_interval

            current = 0
            for p in window_presence:
                if p:
                    current += 1
                elif current:
                    runs.append(current * dense_interval)
                    current = 0
            # A run still open at the window edge is truncated by the window,
            # not by the edit — discarding it avoids biasing durations downward.

    cap.release()

    pos_counts: dict[str, int] = {}
    for p in positions:
        pos_counts[p] = pos_counts.get(p, 0) + 1

    coverage = sum(presence) / len(presence)

    return {
        "text_coverage_ratio": round(coverage, 2),
        "coverage_sample_count": len(presence),
        "text_block_count": len(runs),
        "mean_text_duration_sec": round(float(np.mean(runs)), 2) if runs else 0,
        "min_text_duration_sec": round(float(np.min(runs)), 2) if runs else 0,
        "dominant_position": max(pos_counts, key=pos_counts.get) if pos_counts else "none",
        "position_distribution": pos_counts,
        "is_text_driven": bool(coverage > 0.4),
    }


def extract(video_path: Path, video_id: str) -> GrammarReport:
    log.info("Extracting editorial grammar: %s", video_id)
    duration = probe_duration(video_path)
    shots, fps = detect_shots(video_path)
    log.info("  %d shots over %.1fs", len(shots), duration)

    shot_stats, camera = analyse_camera(video_path, shots, fps)
    motion = extract_motion_design(video_path, shots, fps)

    return GrammarReport(
        video_id=video_id,
        duration_sec=round(duration, 1),
        fps=round(fps, 2),
        cut_rhythm=analyse_cut_rhythm(shots, duration),
        hook=analyse_hook(shots, duration),
        text_cadence=analyse_text_cadence(video_path, duration),
        grade=analyse_grade(video_path),
        camera_language=camera,
        transitions=motion["transitions"],
        motion_graphics=motion["motion_graphics"],
        shot_movement=motion["shot_movement"],
        audio_sync=motion["audio_sync"],
        shots=[asdict(s) for s in shot_stats],
    )


def main() -> None:
    ap = argparse.ArgumentParser(description="Extract editorial grammar from a video")
    ap.add_argument("--video", required=True, help="Path to video file")
    ap.add_argument("--video-id", required=True)
    ap.add_argument("--metadata", help="Optional JSON file with title/views/etc")
    ap.add_argument("--output", required=True, help="Output JSON path")
    args = ap.parse_args()

    report = extract(Path(args.video), args.video_id)
    payload = asdict(report)

    if args.metadata and Path(args.metadata).exists():
        with open(args.metadata) as f:
            payload["metadata"] = json.load(f)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w") as f:
        json.dump(payload, f, indent=2)

    log.info("Wrote %s", out)


if __name__ == "__main__":
    main()
