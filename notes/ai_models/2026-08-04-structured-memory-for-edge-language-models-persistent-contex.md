---
title: "Structured Memory for Edge Language Models: Persistent Context and Corpus Retrieval via O(1) SSM State Injection"
source: arxiv
url: https://arxiv.org/abs/2608.02560v1
category: ai_models
relevance_score: 5
matched_keywords: [generation, language, model, models, token]
fetched_at: 2026-08-04T03:26:56.387998+00:00
published: 2026-08-03T17:43:36Z
status: raw
---

# Structured Memory for Edge Language Models: Persistent Context and Corpus Retrieval via O(1) SSM State Injection

Retrieval-augmented generation (RAG) imposes a prefill cost proportional to retrieved context length, and -- with Transformer backbones -- a KV-cache that grows with each generated token. State-Space Models (SSMs) avoid the second cost by construction; we eliminate the first, collapsing prefill from $O(L_{context})$ to $O(1)$ per query. We introduce PRECOG (Pre-Computed Context Injection), a retrieval mechanism that exploits a property unique to SSMs: the fixed-size, position-agnostic recurrent

[Fuente](https://arxiv.org/abs/2608.02560v1)
