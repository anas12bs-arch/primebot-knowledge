---
title: "GPU-CFR: 80x Faster Counterfactual Regret Minimization by Compiling the Game to Static Dataflow and CUDA Graph Replay"
source: arxiv
url: https://arxiv.org/abs/2609.11923v1
category: ai_models
relevance_score: 22
matched_keywords: [actual, billion, billions, every, faster, fixed, frame, framework, graph, interface, issue, large, launch, launches, million, millions, second, small, state, states, still, through]
fetched_at: 2026-09-11T04:27:09.094628+00:00
published: 2026-09-10T17:58:14Z
status: raw
---

# GPU-CFR: 80x Faster Counterfactual Regret Minimization by Compiling the Game to Static Dataflow and CUDA Graph Replay

Counterfactual regret minimization (CFR) is one of the few large numerical workloads that still runs faster on CPUs than on GPUs. Each iteration sweeps a game tree with up to billions of states in millions of small, interdependent gather and scatter steps issued through a generic tree interface. On a GPU every kernel finishes in microseconds, so kernel launches and framework dispatch dominate the run time, and prior GPU implementations have lost to optimized CPU code. We observe that for a fixed

[Fuente](https://arxiv.org/abs/2609.11923v1)
