---
title: "UE5M3 FP4 Block Scaling for Stable Language Model Pretraining"
source: arxiv
url: https://arxiv.org/abs/2609.02846v1
category: ai_models
relevance_score: 15
matched_keywords: [because, engine, former, language, model, nvidia, point, pretraining, scale, scaling, selective, train, training, transformer, while]
fetched_at: 2026-09-03T06:23:31.397797+00:00
published: 2026-09-02T17:32:07Z
status: raw
---

# UE5M3 FP4 Block Scaling for Stable Language Model Pretraining

Stable 4-bit floating-point (FP4) pretraining is difficult because the E2M1 payload represents only a narrow range of magnitudes. NVIDIA's Transformer Engine \nv{} recipe addresses this with current-tensor scaling, a randomized Hadamard transform (RHT), and bfloat16 (BF16) final layers, adding work outside the FP4 matrix multiplications. We instead pair E2M1 payloads with unsigned E5M3 (\ue{}) block scales. Their wider range permits periodic tensor scaling, while our recipe applies selective sto

[Fuente](https://arxiv.org/abs/2609.02846v1)
