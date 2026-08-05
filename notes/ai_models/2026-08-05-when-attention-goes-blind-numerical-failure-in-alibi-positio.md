---
title: "When Attention Goes Blind: Numerical Failure in ALiBi Positional Encodings"
source: arxiv
url: https://arxiv.org/abs/2608.03994v1
category: ai_models
relevance_score: 4
matched_keywords: [attention, model, models, train]
fetched_at: 2026-08-05T06:08:31.711985+00:00
published: 2026-08-04T17:54:01Z
status: raw
---

# When Attention Goes Blind: Numerical Failure in ALiBi Positional Encodings

We identify a previously overlooked failure mode of ALiBi positional encoding: its linear bias scaling underflows floating-point precision, which zeroes out a large fraction of attention weights and renders the affected attention heads partially blind. We analyze this failure mode, characterize its impact, and examine four mitigation strategies. We further demonstrate its occurrence in state-of-the-art pretrained models based on ALiBi. Comprehensive pretraining experiments with 148M-parameter de

[Fuente](https://arxiv.org/abs/2608.03994v1)
