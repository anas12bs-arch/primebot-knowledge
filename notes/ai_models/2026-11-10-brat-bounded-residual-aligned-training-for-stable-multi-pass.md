---
title: "BRAT: Bounded Residual-Aligned Training for Stable Multi-Pass LLM Post-Training"
source: arxiv
url: https://arxiv.org/abs/2611.10873v1
category: ai_models
relevance_score: 42
matched_keywords: [adding, aligned, avoid, bounded, collapse, different, drift, every, exist, existing, first, force, forces, generation, gradient, language, large, learn, learning, model, negative, object, objectives, passes, policy, post-training, ratio, reinforcement, residual, response, reuse, rollout, rollouts, sampling, several, stable, style, table, train, training, update, updates]
fetched_at: 2026-11-10T04:01:56.648640+00:00
published: 2026-11-07T17:51:57Z
status: raw
---

# BRAT: Bounded Residual-Aligned Training for Stable Multi-Pass LLM Post-Training

Reinforcement learning for large language model post-training often reuses each batch of sampled rollouts for several gradient passes to amortize the cost of generation. Under such multi-pass reuse, existing objectives fail in different ways: unclipped updates collapse as the policy drifts away from the sampling policy, adding a negative baseline avoids collapse but reinforces every sampled response, and PPO-style ratio clipping cuts off gradients abruptly. We first ask why reuse is fragile. Mea

[Fuente](https://arxiv.org/abs/2611.10873v1)
