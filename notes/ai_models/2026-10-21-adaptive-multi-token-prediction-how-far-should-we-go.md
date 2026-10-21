---
title: "Adaptive Multi-Token Prediction: How far should we go?"
source: arxiv
url: https://arxiv.org/abs/2610.28619v1
category: ai_models
relevance_score: 32
matched_keywords: [accelerate, adaptive, autoregressive, change, changes, coding, compute, context, decide, decoding, draft, fixes, forward, great, heads, horizon, language, language-model, longer, model, offer, predict, prediction, reject, reliable, single, speculation, stopping, target, token, tokens, verify]
fetched_at: 2026-10-21T04:26:07.357441+00:00
published: 2026-10-20T17:56:32Z
status: raw
---

# Adaptive Multi-Token Prediction: How far should we go?

Multi-token prediction (MTP) can accelerate language-model decoding by drafting several tokens and verifying them in a single target-model pass. However, the best speculation horizon changes with context: longer drafts offer greater amortization when reliable, but can waste compute on suffixes discarded after a rejection. Unlike autoregressive drafting, where a stopping rule can decide token by token, MTP must fix the horizon before drafting, as all heads fire in the same forward pass. We theref

[Fuente](https://arxiv.org/abs/2610.28619v1)
