---
title: "Cool the Sampler, Not the Learner: Sampling Temperature Moves the Staleness Cliff of Importance-Corrected GRPO"
source: arxiv
url: https://arxiv.org/abs/2609.36953v1
category: ai_models
relevance_score: 23
matched_keywords: [arrives, behind, correction, every, fresh, grade, import, importance, language, learn, match, model, models, moves, product, production, sampling, steps, three, updates, weigh, weight, without]
fetched_at: 2026-09-30T01:58:41.444354+00:00
published: 2026-09-29T07:56:51Z
status: raw
---

# Cool the Sampler, Not the Learner: Sampling Temperature Moves the Staleness Cliff of Importance-Corrected GRPO

Production RL for language models lets the sampler fall behind the learner and repairs the resulting mismatch with a truncated importance weight. We ask how long the sampler can go without a refresh under that correction, and find a cliff: on Qwen2.5-Math-1.5B and GSM8K, importance-corrected GRPO refreshed every 192 updates learns well for 180 steps and then degrades severely in all three data seeds before the refresh arrives. Published remedies for staleness act on the update; we act on the sam

[Fuente](https://arxiv.org/abs/2609.36953v1)
