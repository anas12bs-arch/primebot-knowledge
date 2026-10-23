---
title: "A Fix for Softmax and Cross-Entropy"
source: arxiv
url: https://arxiv.org/abs/2610.31642v1
category: ai_models
relevance_score: 18
matched_keywords: [close, collapse, entropy, first, gradient, large, longer, other, others, round, second, simple, softmax, standard, student, target, teach, teacher]
fetched_at: 2026-10-23T05:54:12.240477+00:00
published: 2026-10-22T17:54:56Z
status: raw
---

# A Fix for Softmax and Cross-Entropy

Standard implementations of softmax, log-softmax, and cross-entropy have two numerical bugs. The first bug, Softmax Collapse, rounds the target logit's gradient to zero if that one logit is much larger than the others, resulting in gradients that no longer sum to zero. The second bug, Softmax Cancellation, occurs when student logits are close to teacher logits, and produces non-zero gradients even when the student and teacher logits are equal. We present simple implementations of log-softmax, so

[Fuente](https://arxiv.org/abs/2610.31642v1)
