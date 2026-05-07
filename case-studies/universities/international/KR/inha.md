# INHA University: Ollama Stack + vLLM Node

_NuClide Research · 2026-05-01 (updated 2026-05-03)_

---

## Summary

INHA University (인하대학교) in Incheon has **two independent unprotected AI inference nodes**: an Ollama instance (165.246.39.51) with 7 models totalling ~133GB including `gpt-oss:20b` and dual Nemotron-Cascade 30B, and a separate vLLM 0.8.4 node (165.246.170.53) serving a containerized Qwen model with 90% prefix cache efficiency.

---

## Node Summary

| Node | IP | Service | Model | Port | Notes |
|------|-----|---------|-------|------|-------|
| Ollama | 165.246.39.51 | Ollama | gpt-oss:20b + 6 models | 11434 | CVE-2025-63389 injectable |
| vLLM | 165.246.170.53 | vLLM 0.8.4 | local-qwen (Qwen, containerized) | 8000 | 311 requests, 90% cache hit |

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 165.246.39.51 (Ollama) / 165.246.170.53 (vLLM) |
| Organization | INHA UNIVERSITY |
| Country | South Korea |
| Open ports | 11434 (Ollama, public) / 8000 (vLLM, public) |

---

## Model Inventory

| Model | Size | Notes |
|---|---|---|
| `gpt-oss:20b` | 12.1GB | Local inference, 20.9B params, `gpt-oss` family |
| `hf.co/unsloth/gpt-oss-20b-GGUF:Q8_0` | 12.1GB | Same weights, direct HF GGUF pull |
| `nemotron-cascade-2:30b` | 24.3GB | NVIDIA Nemotron Cascade 2 30B |
| `gemma4:26b-a4b-it-q8_0` | 28.1GB | Gemma 4 Q8 |
| `nemotron-3-nano:30b` | 24.3GB | NVIDIA Nemotron-3 Nano 30B |
| `qwen3.5:27b` | 22.5GB |, |
| `deepseek-r1:14b` | 9.0GB |, |

**Total local storage:** ~132GB

---

## Findings

### F1: Local gpt-oss:20b and Dual Nemotron Stack (HIGH)

`gpt-oss:20b` is running locally (12.1GB, 20.9B params). The model family `gpt-oss` is the OpenAI open-source weights release. Both the standard Ollama-tagged version and the direct HuggingFace GGUF pull are present, suggesting the operator downloaded via `hf.co/unsloth/gpt-oss-20b-GGUF:Q8_0` first, then aliased it.

The dual `nemotron-cascade-2:30b` and `nemotron-3-nano:30b` stack (both 24.3GB) suggests NVIDIA model evaluation or research use.

### F2: CVE-2025-63389 Injectable (HIGH)

All models injectable via unauthenticated `/api/create`. The Nemotron and gpt-oss models have no system prompts, post-injection inference is unobstructed.

---

## Remediation

```bash
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

---

## Node: 165.246.170.53: vLLM Containerized Qwen Node

| Field | Value |
|-------|-------|
| IP | 165.246.170.53 |
| rDNS | No rDNS (SERVFAIL) |
| vLLM version | 0.8.4 |
| Model ID | `local-qwen` |
| Model root | `/model` (container mount) |
| max_model_len | 4,096 tokens |
| Port | 8000/tcp public |

`local-qwen` is an alias, the model is mounted at `/model` inside a container, hiding the actual model family and version. Based on the naming and university context, this is likely a Qwen 2.5 or Qwen 3 variant. The containerized deployment pattern (Docker volume mount at `/model`) and the vLLM 0.8.4 version suggest an automated or scripted deployment.

### Metrics

| Metric | Value |
|--------|-------|
| `request_success_total[stop]` | 277 |
| `request_success_total[length]` | 34 |
| Total requests | **311** |
| `prompt_tokens_total` | 10,833 |
| `generation_tokens_total` | 12,900 |
| `gpu_prefix_cache_queries_total` | 532 |
| `gpu_prefix_cache_hits_total` | 481 |
| Prefix cache hit rate | **90.4%** |

The high cache hit rate (90.4%) indicates a consistent input pattern, likely a chatbot or assistant with a fixed system prompt contributing repeated prefix tokens.

---

## Disclosure

- **Discovered:** 2026-05-01 (Ollama) / 2026-05-03 (vLLM node)
- **Status:** Pending outreach to INHA IT (inha.ac.kr)
