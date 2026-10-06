---
title: "TurboPairFormer: Fast and Stable Protein Folding Model Training with an Optimized Triangle Attention Kernel"
source: arxiv
url: https://arxiv.org/abs/2610.05854v1
category: ai_models
relevance_score: 35
matched_keywords: [ability, across, alpha, attention, computing, correction, former, forward, gradient, handle, kernel, loses, model, models, molecular, open-source, output, point, putin, queries, repeated, round, score, share, shared, softmax, source, stable, storage, table, these, through, token, train, training]
fetched_at: 2026-10-06T02:28:50.888839+00:00
published: 2026-10-05T06:16:34Z
status: raw
---

# TurboPairFormer: Fast and Stable Protein Folding Model Training with an Optimized Triangle Attention Kernel

Triangular attention is a core computation in AlphaFold3-style biomolecular models, with cubic cost in token count. Its shared pair bias adds a gradient reduction across attention slices to the usual reductions over queries and keys. The open-source backends we examine handle these reductions through repeated probability recomputation, floating-point atomics, or full score-gradient storage. Separately, computing the softmax backward correction from BF16-rounded forward outputs loses numerical pr

[Fuente](https://arxiv.org/abs/2610.05854v1)
