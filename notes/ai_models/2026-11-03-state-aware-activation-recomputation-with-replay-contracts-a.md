---
title: "State-Aware Activation Recomputation with Replay Contracts and Selective Preservation"
source: arxiv
url: https://arxiv.org/abs/2611.00590v1
category: ai_models
relevance_score: 25
matched_keywords: [accelerator, activation, buffer, change, choose, contract, contracts, correct, different, during, explicit, forward, generator, joint, memory, original, playing, random, replay, selective, state, store, table, unchanged, version]
fetched_at: 2026-11-03T02:34:25.687942+00:00
published: 2026-10-31T03:35:55Z
status: raw
---

# State-Aware Activation Recomputation with Replay Contracts and Selective Preservation

Activation recomputation saves accelerator memory by replaying forward segments during the backward pass, but replay is only correct if it sees the state the original forward pass saw. Mutable buffers, aliased bytes and random-generator state can change in between, so re-executing unchanged code can differentiate a different computation. We make this state explicit. A versioned replay contract specifies what replay must restore, and a joint planner chooses, per segment, between activation retent

[Fuente](https://arxiv.org/abs/2611.00590v1)
