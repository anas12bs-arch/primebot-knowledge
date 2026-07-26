#!/usr/bin/env python3
"""
Motion-design extractor: the vocabulary that lifts a mediocre script.

`extract_editorial_grammar.py` measures where the cuts land and how the picture
is graded. That is the skeleton. This module measures the part a viewer
actually experiences as production value:

  1. Transition vocabulary — what happens AT the boundary. A hard cut, a
     dissolve, a whip pan and a flash frame all join two shots, but they make
     completely different promises about the relationship between them.
  2. Graphic element behaviour — how things arrive on screen. An element that
     pops in one frame reads as cheap; the same element easing in over 8 frames
     with a settle reads as designed. This is the single largest gap between a
     channel with a real editor and one without.
  3. Audio sync — whether visual events land on the audio. Cutting on a music
     hit or landing a graphic on an impact sound is what makes an edit feel
     tight rather than approximate.

Everything here is measured from pixels and PCM, so it holds for any channel
without a human labelling anything.
"""

import logging
import subprocess
from collections import deque
from pathlib import Path
from typing import Any

import cv2
import numpy as np

log = logging.getLogger(__name__)

# Thumbnails are kept in memory for the whole run, so cap the total. 12k frames
# at 96x54 grey is ~62MB, which is safe on an 8GB laptop and on a CI runner.
MAX_ANALYSIS_FRAMES = 12000
THUMB_W, THUMB_H = 96, 54

# Transitions are a house habit, not a per-boundary decision, so a sample is
# enough. Each one costs a seek plus ~30 frame decodes; 60 keeps a 20-minute
# video at a few seconds rather than a few minutes.
MAX_BOUNDARIES_SAMPLED = 60

# A pixel has to change by more than this (0-255) to count as "something
# happened here" rather than codec noise.
CHANGE_THRESHOLD = 18


# --------------------------------------------------------------------------
# Shared sampling
# --------------------------------------------------------------------------

def sample_thumbnails(path: Path) -> tuple[np.ndarray, np.ndarray, float]:
    """One sequential decode → grey thumbnails plus their timestamps.

    Sequential reading is roughly an order of magnitude faster than seeking per
    measurement, so every pixel-level metric in this module is derived from
    this single pass.
    """
    cap = cv2.VideoCapture(str(path))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1

    # Aim for 8 fps of analysis, but stretch the step on long videos so the
    # memory ceiling holds regardless of runtime.
    step = max(1, int(round(fps / 8.0)))
    if total / step > MAX_ANALYSIS_FRAMES:
        step = int(np.ceil(total / MAX_ANALYSIS_FRAMES))

    thumbs: list[np.ndarray] = []
    times: list[float] = []
    idx = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if idx % step == 0:
            small = cv2.resize(frame, (THUMB_W, THUMB_H))
            thumbs.append(cv2.cvtColor(small, cv2.COLOR_BGR2GRAY))
            times.append(idx / fps)
        idx += 1
    cap.release()

    if not thumbs:
        return np.empty((0, THUMB_H, THUMB_W), np.uint8), np.empty(0), fps
    return np.stack(thumbs), np.array(times), fps


# --------------------------------------------------------------------------
# 1. Transition vocabulary
# --------------------------------------------------------------------------

def _window_features(cap, center_frame: int, half: int) -> list[dict] | None:
    """Decode a short window around a boundary and describe each frame.

    Reads sequentially from one seek: seeking per frame would dominate runtime.
    """
    start = max(0, center_frame - half)
    cap.set(cv2.CAP_PROP_POS_FRAMES, start)

    feats = []
    for _ in range(half * 2 + 1):
        ok, frame = cap.read()
        if not ok:
            break
        small = cv2.resize(frame, (160, 90))
        gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(small, cv2.COLOR_BGR2HSV)
        hist = cv2.calcHist([hsv], [0, 1], None, [24, 24], [0, 180, 0, 256])
        cv2.normalize(hist, hist, 0, 1, cv2.NORM_MINMAX)
        feats.append({
            "gray": gray,
            "hist": hist,
            "luma": float(gray.mean()),
            # Laplacian variance drops when the image is soft. Both a dissolve
            # (two images blended) and a whip pan (motion blur) soften the
            # frame, which is what separates them from a hard cut.
            "detail": float(cv2.Laplacian(gray, cv2.CV_32F).var()),
        })
    return feats if len(feats) >= 5 else None


def _radial_score(flow: np.ndarray) -> float:
    """+1 when flow diverges from centre (zoom in), -1 when it converges."""
    h, w = flow.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    rx, ry = xx - w / 2, yy - h / 2
    norm = np.hypot(rx, ry) + 1e-6
    radial = (flow[..., 0] * rx + flow[..., 1] * ry) / norm
    mag = np.hypot(flow[..., 0], flow[..., 1])
    if mag.sum() < 1e-6:
        return 0.0
    return float(np.average(radial / (mag + 1e-6), weights=mag))


def _classify_transition(feats: list[dict]) -> tuple[str, float]:
    """Name the transition and say how long it takes, from the frame window."""
    n = len(feats)
    lumas = np.array([f["luma"] for f in feats])
    details = np.array([f["detail"] for f in feats])

    # Frame-to-frame visual distance across the window.
    dist = np.array([
        1.0 - cv2.compareHist(feats[i]["hist"], feats[i + 1]["hist"], cv2.HISTCMP_CORREL)
        for i in range(n - 1)
    ])
    peak = int(np.argmax(dist))
    if dist[peak] <= 0:
        return "none", 0.0

    # How many frames the change is smeared over: 1 means instantaneous.
    active = dist > max(0.12, 0.35 * dist[peak])
    spread = 1
    i = peak
    while i - 1 >= 0 and active[i - 1]:
        spread += 1
        i -= 1
    i = peak
    while i + 1 < len(dist) and active[i + 1]:
        spread += 1
        i += 1

    edges = np.r_[lumas[:3], lumas[-3:]]
    baseline_luma = float(edges.mean())
    baseline_detail = float(np.r_[details[:3], details[-3:]].mean()) + 1e-6
    mid = slice(max(0, peak - 1), min(n, peak + 3))

    # Luma-driven transitions first: they are unambiguous.
    if lumas[mid].min() < 18 and baseline_luma > 40:
        return "fade_through_black", spread
    if lumas[mid].max() > 235 and baseline_luma < 200:
        return "flash_to_white", spread
    if lumas[mid].max() > baseline_luma + 55:
        return "flash_frame", spread

    if spread <= 1:
        return "hard_cut", 1.0

    # Something gradual. Motion tells us whether the frame was moved or mixed.
    g1, g2 = feats[max(0, peak - 1)]["gray"], feats[min(n - 1, peak + 1)]["gray"]
    flow = cv2.calcOpticalFlowFarneback(g1, g2, None, 0.5, 3, 15, 3, 5, 1.2, 0)
    mag = np.hypot(flow[..., 0], flow[..., 1])
    mean_mag = float(mag.mean())
    softening = float(details[mid].mean()) / baseline_detail
    radial = _radial_score(flow)

    if mean_mag > 5.0 and softening < 0.75:
        return "whip_pan", spread
    if abs(radial) > 0.55 and mean_mag > 2.0:
        return "zoom_punch_in" if radial > 0 else "zoom_punch_out", spread
    if mean_mag > 2.5:
        return "slide_push", spread
    if softening < 0.85:
        return "dissolve", spread
    return "soft_cut", spread


def analyse_transitions(path: Path, shots: list[tuple[float, float]], fps: float) -> dict[str, Any]:
    """What the channel does at its shot boundaries, and how fast."""
    boundaries = [start for start, _ in shots[1:]]
    if not boundaries:
        return {}

    # Even spread rather than the first N: transition habits differ between the
    # hook and the body, and sampling only the opening would report the hook's.
    if len(boundaries) > MAX_BOUNDARIES_SAMPLED:
        pick = np.linspace(0, len(boundaries) - 1, MAX_BOUNDARIES_SAMPLED, dtype=int)
        boundaries = [boundaries[i] for i in pick]

    half = max(4, int(round(fps * 0.5)))
    cap = cv2.VideoCapture(str(path))

    counts: dict[str, int] = {}
    spreads: list[float] = []
    for t in boundaries:
        feats = _window_features(cap, int(t * fps), half)
        if not feats:
            continue
        kind, spread = _classify_transition(feats)
        if kind == "none":
            continue
        counts[kind] = counts.get(kind, 0) + 1
        if kind != "hard_cut":
            spreads.append(spread / fps)
    cap.release()

    total = sum(counts.values()) or 1
    effect_names = [k for k in counts if k not in ("hard_cut", "soft_cut")]
    effect_total = sum(counts[k] for k in effect_names)

    return {
        "sampled_boundaries": total,
        "transition_distribution": counts,
        "transition_mix_pct": {k: round(100 * v / total) for k, v in sorted(
            counts.items(), key=lambda kv: kv[1], reverse=True)},
        "hard_cut_ratio": round(counts.get("hard_cut", 0) / total, 2),
        # The headline number: how often the channel spends an effect at all.
        "effect_transition_ratio": round(effect_total / total, 2),
        "dominant_effect": max(effect_names, key=lambda k: counts[k]) if effect_names else "none",
        "mean_effect_duration_sec": round(float(np.mean(spreads)), 2) if spreads else 0.0,
    }


# --------------------------------------------------------------------------
# 2. Graphic element behaviour
# --------------------------------------------------------------------------

def _classify_entrance(areas: list[float], centroids: list[tuple[float, float]],
                       intensities: list[float], dt: float) -> tuple[str, float, int]:
    """Describe how an element arrived, and how long it took to settle."""
    a = np.array(areas)
    peak_area = a.max()
    if peak_area <= 0:
        return "unknown", 0.0, 0

    # Settle point: first sample reaching 90% of the element's final size.
    settle_idx = int(np.argmax(a >= 0.9 * peak_area))
    settle = (settle_idx + 1) * dt

    if settle_idx == 0:
        return "pop", settle, settle_idx

    cx = np.array([c[0] for c in centroids])
    cy = np.array([c[1] for c in centroids])
    travel = float(np.hypot(cx[settle_idx] - cx[0], cy[settle_idx] - cy[0]))

    if travel > 0.12:
        return "slide_in", settle, settle_idx

    growth = a[settle_idx] / (a[0] + 1e-6)
    ramp = intensities[settle_idx] / (intensities[0] + 1e-6)
    # Area growing means the shape itself scaled up; area steady while the
    # difference deepens means it was there all along and faded up.
    if growth > 1.8:
        return "scale_in", settle, settle_idx
    if ramp > 1.5:
        return "fade_in", settle, settle_idx
    return "eased_in", settle, settle_idx


def _compactness(mask: np.ndarray) -> tuple[float, float]:
    """How concentrated the changed pixels are: (bbox share of frame, fill of bbox).

    This is what tells an overlaid graphic from a moving picture. A title card
    or a lower third changes a small, densely-filled rectangle. A push or a
    dissolve changes pixels wherever there is detail — scattered across the
    whole frame, so its bounding box is nearly the full frame and mostly empty.
    """
    ys, xs = np.nonzero(mask)
    if ys.size < 8:
        return 1.0, 0.0
    h, w = mask.shape
    bh = (ys.max() - ys.min() + 1)
    bw = (xs.max() - xs.min() + 1)
    bbox_area = bh * bw
    return bbox_area / (h * w), ys.size / bbox_area


def _plateaus(areas: list[float], settle_idx: int, hold_samples: int = 3,
              tolerance: float = 0.25) -> bool:
    """True when the element reached its size and then stayed at it."""
    if settle_idx + hold_samples >= len(areas):
        return False
    peak = max(areas)
    after = areas[settle_idx:settle_idx + hold_samples + 1]
    return all(abs(v - peak) <= tolerance * peak for v in after)


def _residual_motion(thumbs: np.ndarray, settled_idx: int, base: np.ndarray) -> float | None:
    """How much the changed region keeps moving after the entrance finished.

    Returned as a fraction of the entrance's own change magnitude, so it is
    comparable across bright graphics and subtle ones. Near 0 means the region
    froze — a landed graphic. Near 1 means it never stopped — live footage.
    """
    if settled_idx + 2 >= len(thumbs):
        return None
    settled = thumbs[settled_idx].astype(np.int16)
    entrance_delta = np.abs(settled - base)
    mask = entrance_delta > CHANGE_THRESHOLD
    if mask.sum() < 8:
        return None

    after = [
        float(np.abs(thumbs[j].astype(np.int16) - thumbs[j - 1].astype(np.int16))[mask].mean())
        for j in range(settled_idx + 1, min(settled_idx + 3, len(thumbs)))
    ]
    return float(np.mean(after)) / (float(entrance_delta[mask].mean()) + 1e-6)


def analyse_graphic_events(thumbs: np.ndarray, times: np.ndarray,
                           shots: list[tuple[float, float]]) -> dict[str, Any]:
    """Find overlaid elements and measure how they animate.

    The signal that separates a graphic from ordinary picture motion: a small
    region of the frame changes while everything around it stays still. A camera
    move changes the whole frame; a subject moving changes a region but keeps
    changing it. An element arriving changes a region and then holds.
    """
    if len(thumbs) < 8:
        return {}

    dt = float(np.median(np.diff(times))) if len(times) > 1 else 0.125
    track_len = max(6, int(round(1.5 / dt)))     # watch 1.5s of the entrance
    hold_cap = int(round(10.0 / dt))

    cut_times = {round(s, 1) for s, _ in shots}

    def near_cut(t: float) -> bool:
        return any(abs(t - c) < 0.4 for c in cut_times)

    entrances: dict[str, int] = {}
    settles: list[float] = []
    holds: list[float] = []
    event_times: list[float] = []

    prev_area = 0.0
    i = 1
    while i < len(thumbs) - 2:
        cur = thumbs[i].astype(np.int16)
        base = thumbs[i - 1].astype(np.int16)
        mask = np.abs(cur - base) > CHANGE_THRESHOLD
        area = float(mask.mean())

        # A localized change, on a frame that was previously quiet, away from a
        # cut (where every pixel changes for unrelated reasons).
        if 0.004 < area < 0.35 and prev_area < 0.004 and not near_cut(times[i]):
            areas, centroids, intensities = [], [], []
            for j in range(i, min(i + track_len, len(thumbs))):
                d = np.abs(thumbs[j].astype(np.int16) - base)
                m = d > CHANGE_THRESHOLD
                frac = float(m.mean())
                areas.append(frac)
                if m.any():
                    ys, xs = np.nonzero(m)
                    centroids.append((xs.mean() / THUMB_W, ys.mean() / THUMB_H))
                    intensities.append(float(d[m].mean()))
                else:
                    centroids.append((0.5, 0.5))
                    intensities.append(0.0)

            kind, settle, settle_idx = _classify_entrance(areas, centroids, intensities, dt)
            peak = max(areas)

            # An entrance has to finish, and then hold its size. If the changed
            # area is still growing when the window ends, nothing "arrived" —
            # that is a shot drifting (a slow push, a subject crossing frame),
            # and counting it would report the window length as the timing.
            if not _plateaus(areas, settle_idx):
                prev_area = area
                i += 1
                continue

            # Geometry gate: the landed element must occupy a compact, densely
            # filled region. Picture motion fails this — it scatters changes
            # across the frame wherever there is detail.
            landed = i + settle_idx
            if landed >= len(thumbs):
                prev_area = area
                i += 1
                continue
            settled_mask = np.abs(thumbs[landed].astype(np.int16) - base) > CHANGE_THRESHOLD
            bbox_frac, fill = _compactness(settled_mask)
            if bbox_frac > 0.5 or fill < 0.25:
                prev_area = area
                i += 1
                continue

            # The discriminator between a graphic and a moving subject: once a
            # graphic lands it stops changing, while footage keeps moving for
            # as long as it is on screen. Without this, every person walking
            # through an archival clip registers as an element entering.
            settled = _residual_motion(thumbs, i + settle_idx, base)
            if settled is None or settled > 0.35:
                prev_area = area
                i += 1
                continue

            # How long it stays before the frame returns to its pre-event state.
            hold = 0.0
            for j in range(i, min(i + hold_cap, len(thumbs))):
                d = np.abs(thumbs[j].astype(np.int16) - base) > CHANGE_THRESHOLD
                if float(d.mean()) < 0.25 * peak:
                    break
                hold += dt

            entrances[kind] = entrances.get(kind, 0) + 1
            settles.append(settle)
            holds.append(hold)
            event_times.append(float(times[i]))

            i += track_len          # don't re-trigger on the same element
            prev_area = 0.0
            continue

        prev_area = area
        i += 1

    if not settles:
        return {"graphic_event_count": 0}

    runtime_min = (times[-1] - times[0]) / 60 if len(times) > 1 else 1
    return {
        "graphic_event_count": len(settles),
        "graphic_events_per_minute": round(len(settles) / max(runtime_min, 0.1), 1),
        "entrance_distribution": entrances,
        "dominant_entrance": max(entrances, key=entrances.get),
        # The craft number. Under ~0.15s reads as a hard pop; 0.2-0.5s is the
        # band where an eased entrance feels deliberate.
        "mean_entrance_sec": round(float(np.mean(settles)), 2),
        "median_entrance_sec": round(float(np.median(settles)), 2),
        "mean_hold_sec": round(float(np.mean(holds)), 2),
        "animated_entrance_ratio": round(
            1 - entrances.get("pop", 0) / len(settles), 2),
        "event_times": [round(t, 2) for t in event_times[:400]],
    }


def analyse_shot_movement(thumbs: np.ndarray, times: np.ndarray,
                          shots: list[tuple[float, float]]) -> dict[str, Any]:
    """Zoom vs pan, measured over half a second rather than one frame pair.

    A slow push moves a pixel a fraction of a pixel per frame — invisible to a
    frame-to-frame flow, obvious over 0.5s. This is what detects the Ken Burns
    move applied to a still, which is the backbone of any archival-footage
    channel.
    """
    if len(thumbs) < 4:
        return {}

    dt = float(np.median(np.diff(times))) if len(times) > 1 else 0.125
    gap = max(1, int(round(0.5 / dt)))
    kinds: dict[str, int] = {}

    for start, dur in shots:
        if dur < 0.8:
            continue
        mid = start + dur / 2
        a = int(np.searchsorted(times, mid))
        b = a + gap
        if b >= len(thumbs):
            continue

        flow = cv2.calcOpticalFlowFarneback(thumbs[a], thumbs[b], None,
                                            0.5, 3, 15, 3, 5, 1.2, 0)
        mag, ang = cv2.cartToPolar(flow[..., 0], flow[..., 1])
        mean_mag = float(mag.mean())
        if mean_mag < 0.25:
            kinds["static"] = kinds.get("static", 0) + 1
            continue

        # Magnitude alone would call compression noise a pan. A frame move —
        # whether a camera or a Ken Burns on a still — pushes every pixel the
        # same way, so require the flow field to agree with itself first.
        w, a_ = mag.reshape(-1), ang.reshape(-1)
        coherence = float(np.hypot(np.average(np.cos(a_), weights=w),
                                   np.average(np.sin(a_), weights=w))) if w.sum() > 1e-6 else 0.0
        if coherence < 0.55:
            kinds["subject_motion"] = kinds.get("subject_motion", 0) + 1
            continue

        radial = _radial_score(flow)
        if abs(radial) > 0.4:
            k = "push_in" if radial > 0 else "pull_out"
        else:
            k = "pan"
        kinds[k] = kinds.get(k, 0) + 1

    total = sum(kinds.values()) or 1
    framed = kinds.get("push_in", 0) + kinds.get("pull_out", 0) + kinds.get("pan", 0)
    return {
        "shot_movement_distribution": kinds,
        # Deliberate frame movement only — subject motion inside a held frame
        # is not an editing choice about the frame.
        "frame_move_ratio": round(framed / total, 2),
        "static_frame_ratio": round(kinds.get("static", 0) / total, 2),
        "push_ratio": round(kinds.get("push_in", 0) / total, 2),
        "dominant_movement": max(kinds, key=kinds.get) if kinds else "unknown",
    }


# --------------------------------------------------------------------------
# 3. Audio sync
# --------------------------------------------------------------------------

def audio_onsets(path: Path, sr: int = 8000) -> np.ndarray:
    """Times of audible impacts — music hits, stings, drops.

    Decoded to 8kHz mono PCM: enough to locate an energy onset to within a
    frame, and small enough that a 20-minute video is a few MB of samples.
    """
    proc = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(sr),
         "-f", "s16le", "-"],
        capture_output=True,
    )
    if proc.returncode != 0 or not proc.stdout:
        return np.empty(0)

    pcm = np.frombuffer(proc.stdout, np.int16).astype(np.float32) / 32768.0
    hop = sr // 100                                  # 10ms resolution
    frames = len(pcm) // hop
    if frames < 20:
        return np.empty(0)

    rms = np.sqrt((pcm[:frames * hop].reshape(frames, hop) ** 2).mean(axis=1))

    # Onset = energy rising well above the recent local level. Comparing to a
    # trailing median rather than a global threshold keeps it working through
    # both quiet narration and loud music beds.
    win = 50                                         # 500ms of history
    pad = np.pad(rms, (win, 0), mode="edge")
    local = np.array([np.median(pad[i:i + win]) for i in range(frames)])
    rising = np.diff(rms, prepend=rms[0]) > 0
    hot = (rms > local * 1.8 + 1e-4) & rising

    onsets, last = [], -1.0
    for i in np.nonzero(hot)[0]:
        t = i / 100.0
        if t - last > 0.15:                          # one onset per event
            onsets.append(t)
            last = t
    return np.array(onsets)


def analyse_audio_sync(path: Path, shots: list[tuple[float, float]],
                       graphic_times: list[float]) -> dict[str, Any]:
    """Do cuts and graphics land on the audio, or float free of it?"""
    onsets = audio_onsets(path)
    if onsets.size == 0:
        return {}

    def alignment(events: list[float], tol: float) -> tuple[float, float]:
        if not events:
            return 0.0, 0.0
        offsets = []
        for t in events:
            k = int(np.searchsorted(onsets, t))
            near = onsets[max(0, k - 1):k + 2]
            if near.size:
                offsets.append(float(np.min(np.abs(near - t))))
        if not offsets:
            return 0.0, 0.0
        arr = np.array(offsets)
        return float((arr <= tol).mean()), float(np.median(arr))

    cut_times = [s for s, _ in shots[1:]]
    # 120ms is roughly the window inside which a viewer perceives picture and
    # sound as a single event rather than two.
    cut_hit, cut_med = alignment(cut_times, 0.12)
    gfx_hit, gfx_med = alignment(graphic_times, 0.12)

    return {
        "audio_onset_count": int(onsets.size),
        "onsets_per_minute": round(onsets.size / max(shots[-1][0] / 60, 0.1), 1) if shots else 0,
        "cuts_on_audio_hit_ratio": round(cut_hit, 2),
        "median_cut_offset_sec": round(cut_med, 3),
        "graphics_on_audio_hit_ratio": round(gfx_hit, 2),
        "median_graphic_offset_sec": round(gfx_med, 3),
        "is_beat_cut": bool(cut_hit > 0.35),
    }


# --------------------------------------------------------------------------

def extract_motion_design(path: Path, shots: list[tuple[float, float]],
                          fps: float) -> dict[str, Any]:
    """Everything in this module, sharing one decode pass where possible."""
    log.info("  motion design: transitions…")
    transitions = analyse_transitions(path, shots, fps)

    log.info("  motion design: sampling frames…")
    thumbs, times, _ = sample_thumbnails(path)

    log.info("  motion design: graphic events…")
    graphics = analyse_graphic_events(thumbs, times, shots)
    movement = analyse_shot_movement(thumbs, times, shots)

    log.info("  motion design: audio sync…")
    sync = analyse_audio_sync(path, shots, graphics.get("event_times", []))

    return {
        "transitions": transitions,
        "motion_graphics": graphics,
        "shot_movement": movement,
        "audio_sync": sync,
    }
