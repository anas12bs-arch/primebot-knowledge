---
title: "Cap-and-Track: Optimizing LLM Inference Request Dispatch Across Shifting Capacity"
source: arxiv
url: https://arxiv.org/abs/2611.24891v1
category: ai_models
relevance_score: 39
matched_keywords: [across, asynchronous, become, becomes, capacity, change, comes, cross, current, design, fixed, fleet, fleets, generative, inference, internal, known, length, mission, optimizing, output, outside, patch, provider, request, serving, shape, share, shared, shift, shifting, signal, stale, track, traffic, understand, understanding, unknown, video]
fetched_at: 2026-11-19T09:22:52.993533+00:00
published: 2026-11-18T18:34:10Z
status: raw
---

# Cap-and-Track: Optimizing LLM Inference Request Dispatch Across Shifting Capacity

A fixed dispatch rate for LLM inference becomes stale as serving fleets resize and request sizes change. Generative output length is unknown at admission, and shared provider pools can lose capacity. We present Cap-and-Track, a design for asynchronous inference across provider capacity and internal GPUs. Meta's traffic shaper implements Cap-and-Track for post and live-video understanding. Refusals signal the backend's current admission ceiling. Durable priority queues hold excess work outside ex

[Fuente](https://arxiv.org/abs/2611.24891v1)
