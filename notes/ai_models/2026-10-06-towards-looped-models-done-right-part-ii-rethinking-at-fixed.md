---
title: "Towards Looped Models Done Right, Part II: Rethinking at Fixed Points"
source: arxiv
url: https://arxiv.org/abs/2610.06833v1
category: ai_models
relevance_score: 44
matched_keywords: [almost, close, closer, coding, compute, current, decoding, distill, enables, every, faster, fixed, force, gradient, language, learn, learning, looped, matter, matters, model, models, point, points, recurrent, reinforcement, rethinking, right, rollout, sharing, state, states, still, student, terminal, think, thinking, through, toward, towards, train, training, updates, value]
fetched_at: 2026-10-06T09:21:34.009370+00:00
published: 2026-10-05T17:58:15Z
status: raw
---

# Towards Looped Models Done Right, Part II: Rethinking at Fixed Points

Every recurrence of a looped language model adds cost in training, decoding, prefill, and reinforcement learning (RL). The closer recurrent states get to fixed points, the less the path to them matters. This enables truncated backpropagation in training; terminal key-value (KV) sharing for decoding with almost no loss in accuracy; a distilled student that prefills up to 1.79x faster; and RL updates that compute gradients from saved rollout states, 2x faster than backpropagating through the repla

[Fuente](https://arxiv.org/abs/2610.06833v1)
