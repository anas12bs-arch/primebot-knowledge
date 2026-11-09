---
title: "ResQAdam: Residual-Preserving Adaptive Optimization for Memory-Efficient Quantization Aware Training"
source: arxiv
url: https://arxiv.org/abs/2611.08924v1
category: ai_models
relevance_score: 43
matched_keywords: [accurate, adaptive, based, consider, dense, efficient, every, further, grade, keeps, language, large, liable, low-rank, matrix, memory, method, methods, model, models, moment, momentum, optimization, optimize, optimizer, outside, project, quant, quantization, reliable, remain, remains, residual, serve, serving, space, state, states, train, training, useful, weigh, weight]
fetched_at: 2026-11-09T02:32:26.912799+00:00
published: 2026-11-06T03:12:45Z
status: raw
---

# ResQAdam: Residual-Preserving Adaptive Optimization for Memory-Efficient Quantization Aware Training

Quantization-aware training (QAT) is the most reliable way to obtain accurate low-bit large language models (LLMs), but training with AdamW keeps two dense FP32 states for every weight matrix. We find that low-rank memory-efficient optimizers such as GaLore and LDAdam degrade substantially in QAT. A considerable part of the QAT momentum lies outside its top-r singular subspace, and projection-based methods discard this part at every step. We further observe that this residual remains useful when

[Fuente](https://arxiv.org/abs/2611.08924v1)
