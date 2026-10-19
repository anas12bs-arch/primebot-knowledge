---
title: "FuTransformer: FP8 prefill and INT4 decode for Llama-style inference on Hopper"
source: arxiv
url: https://arxiv.org/abs/2610.23796v1
category: ai_models
relevance_score: 32
matched_keywords: [across, activation, adding, approach, block, cache, delay, delayed, direct, directly, fixed, former, inference, limit, limited, matrix, nvidia, output, place, placement, reads, reuse, scaling, single, token, tokens, transform, transformer, weigh, weight, weights, writing]
fetched_at: 2026-10-19T05:11:45.798529+00:00
published: 2026-10-16T17:22:01Z
status: raw
---

# FuTransformer: FP8 prefill and INT4 decode for Llama-style inference on Hopper

Transformer prefill reuses weights across tokens and is dominated by matrix multiplication and activation data movement; single-token decode has limited reuse and is dominated by weight and KV-cache reads. We present FUTRANSFORMER, a CUDA implementation of a Llama-style Transformer block for NVIDIA Hopper GPUs. It applies CODA's GEMM-plus-epilogue approach to inference, adding direct KV-cache placement, folding the fixed RMSNorm gain into weights, writing FP8 output directly with delayed scaling

[Fuente](https://arxiv.org/abs/2610.23796v1)
