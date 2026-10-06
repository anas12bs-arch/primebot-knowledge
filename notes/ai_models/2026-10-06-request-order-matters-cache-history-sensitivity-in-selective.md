---
title: "Request Order Matters: Cache-History Sensitivity in Selective KV-Cache Reuse for Rolling Agents"
source: arxiv
url: https://arxiv.org/abs/2610.05833v1
category: ai_models
relevance_score: 31
matched_keywords: [agent, agents, answer, answers, break, cache, change, different, document, documents, exact, history, match, matter, matters, order, persist, persistent, prefix, process, prompt, repeated, request, requests, running, selective, story, these, updates, while, window]
fetched_at: 2026-10-06T02:28:50.904165+00:00
published: 2026-10-05T05:37:22Z
status: raw
---

# Request Order Matters: Cache-History Sensitivity in Selective KV-Cache Reuse for Rolling Agents

Long-running agents repeatedly call an LLM while retaining most of their document window, evicting old documents, and appending new ones. These rolling updates break exact prefix caching and motivate non-prefix KV-cache reuse with selective recomputation. We show that persistent KV-cache reuse with selective recomputation can be history-dependent: in our rolling-agent workload, an unchanged prompt can produce different answers depending on the requests processed before it. At a matched 5% recomp

[Fuente](https://arxiv.org/abs/2610.05833v1)
