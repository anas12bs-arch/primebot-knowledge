---
title: "SoftCache: Adaptive Step Size Caching for Diffusion Transformers"
source: arxiv
url: https://arxiv.org/abs/2610.22369v1
category: ai_models
relevance_score: 43
matched_keywords: [accelerate, accelerates, activation, adaptive, cache, caching, cheap, computing, decide, diffusion, dynamic, evaluation, evaluations, former, fresh, fusion, generate, generation, input, instead, iterative, large, method, methods, model, models, network, probe, putin, rates, ratio, signal, spend, spending, steps, through, train, training, training-free, transform, transformer, transformers, valuation]
fetched_at: 2026-10-16T06:17:39.075866+00:00
published: 2026-10-15T17:59:34Z
status: raw
---

# SoftCache: Adaptive Step Size Caching for Diffusion Transformers

Diffusion and flow models generate a sample over iterative steps, each a full pass through a large network, and that pass dominates generation cost. Training-free caching accelerates them by reusing activations from recent evaluations instead of recomputing them. Dynamic caching methods decide when to refresh by accumulating a cheap probe of the network input into a staleness signal and spending a fresh evaluation once it crosses a threshold. They perform hard caching: the signal is a binary swi

[Fuente](https://arxiv.org/abs/2610.22369v1)
