---
title: "Eviction as Estimation: A Fixed-Lag Smoothing View of Test-Time Memory, and When Measuring Beats Accumulating"
source: arxiv
url: https://arxiv.org/abs/2607.24667v1
category: automation
relevance_score: 2
matched_keywords: [model, problem]
fetched_at: 2026-07-28T03:23:30.767920+00:00
published: 2026-07-27T17:08:27Z
status: raw
---

# Eviction as Estimation: A Fixed-Lag Smoothing View of Test-Time Memory, and When Measuring Beats Accumulating

A language model with a bounded working memory must repeatedly decide which stored items to keep. Every deployed method decides the moment an item arrives, from the past (StreamingLLM, H2O) or from a guess about the future (SnapKV). We recast the choice as an estimation problem on a hidden signal, whether an item will be reused, placing existing methods on one axis, the commit lag $H$: online filters and learned predictors commit at $H=0$, while Belady's offline optimum sits where the whole futu

[Fuente](https://arxiv.org/abs/2607.24667v1)
