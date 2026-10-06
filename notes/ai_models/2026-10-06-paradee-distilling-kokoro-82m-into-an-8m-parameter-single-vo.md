---
title: "Paradee: Distilling Kokoro-82M into an 8M-Parameter Single-Voice Text-to-Speech Model"
source: arxiv
url: https://arxiv.org/abs/2610.06817v1
category: ai_models
relevance_score: 35
matched_keywords: [again, against, architecture, compute, corpus, distill, energy, feature, features, fewer, first, frozen, gains, keeps, layer, model, needs, parameters, phone, pitch, predict, ratio, single, small, speech, still, teach, teacher, text-to-speech, these, train, trained, value, values, voice]
fetched_at: 2026-10-06T09:21:34.021624+00:00
published: 2026-10-05T17:56:07Z
status: raw
---

# Paradee: Distilling Kokoro-82M into an 8M-Parameter Single-Voice Text-to-Speech Model

We distill Kokoro-82M, a widely used open text-to-speech model with 54 voices, into Paradee, an 8.07M-parameter model that speaks one of them. Paradee keeps Kokoro's architecture with much narrower layers, and each of its two halves is trained separately against the frozen teacher. It has 10x fewer parameters and needs 15x less compute. We first synthesize a corpus with the teacher and keep its durations, pitch, energy and phoneme features. We then train a small text side to predict these values

[Fuente](https://arxiv.org/abs/2610.06817v1)
