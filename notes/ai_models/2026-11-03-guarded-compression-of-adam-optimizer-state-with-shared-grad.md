---
title: "Guarded Compression of Adam Optimizer State with Shared-Gradient Bounds"
source: arxiv
url: https://arxiv.org/abs/2611.00589v1
category: ai_models
relevance_score: 36
matched_keywords: [bounds, change, coded, compression, construction, coordinate, divide, domain, error, every, gradient, guard, keeps, learn, learning, moment, native, optimize, parameter, reconstruction, risky, second, share, shared, small, square, state, store, study, tolerance, twice, update, weigh, weight, weights, within]
fetched_at: 2026-11-03T02:34:25.689661+00:00
published: 2026-10-31T03:34:05Z
status: raw
---

# Guarded Compression of Adam Optimizer State with Shared-Gradient Bounds

Adam keeps two FP32 moments per parameter, twice the bytes of the FP32 weights, yet compressing them is risky: the update divides by the square root of the second moment, so small reconstruction errors can change the restored computation substantially. We study guarded moment compression, in which a coordinate's decoded moments are accepted only if they reproduce the native FP32 Adam update to within a tolerance $τ$, in units of the learning rate, for every gradient in a clipped domain; all othe

[Fuente](https://arxiv.org/abs/2611.00589v1)
