---
title: "FVAttn: Adaptive Sparse Attention with Runtime Load Balancing for Video Generation"
source: arxiv
url: https://arxiv.org/abs/2607.16190v1
category: ai_models
relevance_score: 5
matched_keywords: [video generation, video]
fetched_at: 2026-07-20T03:52:21.140336+00:00
published: 2026-07-17T17:59:32Z
status: raw
---

# FVAttn: Adaptive Sparse Attention with Runtime Load Balancing for Video Generation

Video Diffusion Transformers process long spatio-temporal sequences, making self-attention the main bottleneck in high-resolution video generation. Training-free sparse attention reduces this cost, but adaptive Top-$p$ routing creates uneven per-head workloads under multi-GPU sequence parallelism. The resulting workload heterogeneity turns sparse attention into a rank-level straggler problem. We present \method{}, a training-free sparse-attention system that improves the distributed execution ef

[Fuente](https://arxiv.org/abs/2607.16190v1)
