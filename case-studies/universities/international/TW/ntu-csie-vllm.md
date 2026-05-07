# National Taiwan University: CSIE MVNL Lab, Llama-3.3-70B vLLM (FP8, 2-Engine)

_NuClide Research · 2026-05-03_

---

## Summary

`mvnl-nas.csie.ntu.edu.tw` (140.112.91.209) in NTU's Computer Science and Information Engineering (CSIE) department exposes vLLM on port 8080 serving **`nvidia/Llama-3.3-70B-Instruct-FP8`**, NVIDIA's FP8-quantized Llama 3.3 70B, without authentication. The server runs two parallel engines (tensor-parallel multi-GPU), has processed 237 requests and 450K prompt tokens since deployment. Context is constrained to 6,000 tokens, suggesting controlled evaluation use.

---

## Infrastructure

| Field | Value |
|-------|-------|
| IP | 140.112.91.209 |
| Hostname | mvnl-nas.csie.ntu.edu.tw |
| Organization | NTU CSIE, MVNL Lab (Machine Vision and Natural Language) |
| Network | Taiwan MOE TANet (140.112.0.0/16) |
| vLLM version | `0.18.2rc1.dev73+gdb7a17ecc` (very recent dev build) |
| Port | 8080/tcp public |
| Auth | None |

---

## Model Inventory

| Model | Engines | max_model_len | Notes |
|-------|---------|---------------|-------|
| `nvidia/Llama-3.3-70B-Instruct-FP8` | 2 (tensor parallel) | 6,000 | FP8 quantized, NVIDIA packaging |

Two engines indicate tensor-parallel deployment across multiple GPUs, likely 2× H100 or A100 for 70B FP8. Context deliberately limited to 6K tokens (base supports 128K+), suggesting experimental or benchmark configuration.

---

## Prometheus Metrics

| Metric | Engine 0 | Engine 1 | Total |
|--------|----------|----------|-------|
| `request_success_total[stop]` | 130 | 106 | **236** |
| `request_success_total[length]` | 1 | 0 | 1 |
| `prompt_tokens_total` | 248,381 | 202,223 | **450,604** |
| `generation_tokens_total` | 13,839 | 11,509 | **25,348** |
| `prefix_cache_queries_total` | 248,381 | 202,223 | 450,604 |
| `prefix_cache_hits_total` | 10,352 | 10,880 | **21,232** |
| Prefix cache hit rate |, |, | **~4.7%** |
| Avg prompt length | ~1,910 tokens | ~1,908 tokens | ~1,909 |
| Avg generation length | ~106 tokens | ~108 tokens | ~107 |

**Traffic pattern:** 237 requests at ~1,909 avg prompt tokens → ~107 avg output tokens. The low cache hit rate (4.7%) indicates diverse inputs, not repeated batch evaluation but varied query content. Prompt/generation ratio (17:1) suggests question-answering or instruction-following tasks, consistent with MVNL research workloads.

---

## Findings

### F1: Unauthenticated vLLM Inference on 70B Model (HIGH)

```bash
curl http://140.112.91.209:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"nvidia/Llama-3.3-70B-Instruct-FP8",
       "messages":[{"role":"user","content":"Hello"}],
       "max_tokens":100}'
```

Inference on a 70B FP8 model running on NTU GPU cluster, billable against NTU's GPU allocation.

### F2: Prometheus /metrics Exposed (MEDIUM)

`GET http://140.112.91.209:8080/metrics`, unauthenticated. Exposes request counts, token volumes, per-engine latency, cache statistics, and the model name `nvidia/Llama-3.3-70B-Instruct-FP8`.

The 2-engine configuration is visible in metric labels (`engine="0"`, `engine="1"`), revealing the tensor-parallel topology of the cluster hardware.

---

## Context: MVNL Lab

The hostname `mvnl-nas` suggests this machine serves as both NAS (network attached storage) and inference node for MVNL, the Machine Vision and Natural Language lab at CSIE NTU. The lab conducts research in computer vision, NLP, and multimodal AI. Llama-3.3-70B-Instruct is a strong general instruction model; its presence with FP8 quantization and constrained context (6K) is consistent with evaluation runs comparing quantization methods or context-length impact on benchmarks.

**NTU also has:** `g1pc2n108.g1.ntu.edu.tw` (140.112.233.108), separate Ollama node on NTU GPU Cluster 1, 11 vision/multimodal models. That node is documented in `ntu-gpu.md`.

---

## Remediation

```bash
# Bind to localhost and use reverse proxy with auth:
vllm serve nvidia/Llama-3.3-70B-Instruct-FP8 \
  --host 127.0.0.1 --port 8080 \
  --tensor-parallel-size 2

# Or add API key:
vllm serve nvidia/Llama-3.3-70B-Instruct-FP8 \
  --api-key <secret> \
  --tensor-parallel-size 2
```

---

## Disclosure

- **Discovered:** 2026-05-03
- **Status:** Pending outreach, CSIE NTU security contact
