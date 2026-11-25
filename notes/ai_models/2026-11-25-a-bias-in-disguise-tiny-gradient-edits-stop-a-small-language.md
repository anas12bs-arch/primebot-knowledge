---
title: "A Bias in Disguise: Tiny Gradient Edits Stop a Small Language Model's Thinking Loops and Complement a Frontier Model's Weight Edit"
source: arxiv
url: https://arxiv.org/abs/2611.33133v1
category: ai_models
relevance_score: 34
matched_keywords: [accuracy, answer, answers, astra, block, budget, close, fine-tuning, finish, front, frontier, gpt-6, gradient, language, large, largest, missing, model, qwen3, ratio, reason, reasoning, recent, report, rising, small, think, thinking, token, tuning, weigh, weight, weights, without]
fetched_at: 2026-11-25T05:21:32.361916+00:00
published: 2026-11-24T18:53:22Z
status: raw
---

# A Bias in Disguise: Tiny Gradient Edits Stop a Small Language Model's Thinking Loops and Complement a Frontier Model's Weight Edit

Qwen3.5-0.8B rarely finishes reasoning in thinking mode: at a 4,096-token budget only 1 or 2 of 500 MATH-500 answers close their think block (two seeds), and accuracy is 15.4%. A recent demonstration had GPT-6 Astra edit 131,072 of the model's weights without gradients and reported MATH-500 rising from 7.9% to 48.1% at a 32,768-token budget. We provide the missing gradient baseline, then combine the two edits. Fine-tuning only the 140 to 139,750 weights with the largest gradient, on the model's

[Fuente](https://arxiv.org/abs/2611.33133v1)
