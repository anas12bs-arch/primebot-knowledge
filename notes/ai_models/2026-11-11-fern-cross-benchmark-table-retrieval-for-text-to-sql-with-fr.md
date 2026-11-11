---
title: "FERN: Cross-Benchmark Table Retrieval for Text-to-SQL with Frozen Retrievers and Learned Ranking"
source: arxiv
url: https://arxiv.org/abs/2611.14477v1
category: ai_models
relevance_score: 44
matched_keywords: [again, against, bench, benchmark, candidate, candidates, catalog, claude, compare, cross, describe, engine, engineer, feature, features, first, frozen, gains, generative, instead, large, learn, learned, light, model, models, needs, order, orders, publish, published, question, questions, ranking, recall, retrieval, system, systems, table, tables, three, train, training, words]
fetched_at: 2026-11-11T07:40:12.784420+00:00
published: 2026-11-10T18:39:49Z
status: raw
---

# FERN: Cross-Benchmark Table Retrieval for Text-to-SQL with Frozen Retrievers and Learned Ranking

Text-to-SQL systems over large pooled catalogs must first retrieve the tables a question needs. We compare against the published table recall of RASL, which uses Claude 3.5 models to extract keywords and select tables, on pooled BIRD, Spider, and Fiben catalogs. FERN (Feature-Engineered Ranking with No generative LLM) instead fuses three frozen retrievers into 100 candidates, describes each with up to 120 features, and reorders them with LightGBM rankers fitted once on BIRD's training questions.

[Fuente](https://arxiv.org/abs/2611.14477v1)
