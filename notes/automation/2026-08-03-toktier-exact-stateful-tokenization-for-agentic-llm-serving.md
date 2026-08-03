---
title: "TokTier: Exact Stateful Tokenization for Agentic LLM Serving"
source: arxiv
url: https://arxiv.org/abs/2607.29678v1
category: automation
relevance_score: 7
matched_keywords: [agent, agentic, agents, build, coding, still, system]
fetched_at: 2026-08-03T04:09:20.352413+00:00
published: 2026-07-31T17:56:30Z
status: raw
---

# TokTier: Exact Stateful Tokenization for Agentic LLM Serving

LLM serving systems cache prompt KV state, yet most front ends still re-tokenize the full request text on every call. The cost lands on coding agents, which resubmit a long transcript after each small tool result, and reuse is hard because even a short append can change token boundaries near the end of the previous sequence. Across 153,951 calls from two agent ecosystems, the median call appends about 1.4K characters, and only 1.0-3.6% of calls start or rebuild a session with contexts of million

[Fuente](https://arxiv.org/abs/2607.29678v1)
