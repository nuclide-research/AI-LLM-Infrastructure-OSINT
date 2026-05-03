# University of Dhaka — Coding Cluster, 3 Cloud Proxies, Embedding Pipeline

_NuClide Research · 2026-05-03_

---

## Summary

University of Dhaka (AS137359) exposes an Ollama instance focused on software development AI tooling: multiple code-specialized models, a high-quality multilingual embedding model (`bge-m3`), and three cloud proxy subscriptions. The combination of `bge-m3` (embedding) + code models + `vicuna:13b` suggests an active RAG-augmented code assistant pipeline. All models accessible without authentication.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 103.221.252.77 |
| Org | University of Dhaka |
| Country | Bangladesh |
| Ollama version | 0.20.5 |
| Open port | 11434 (public, no auth) |

---

## Models

| Model | Size | Category |
|---|---|---|
| deepseek-v4-pro:cloud | 0 GB | ☁️ Cloud proxy (pre-release) |
| kimi-k2.6:cloud | 0 GB | ☁️ Cloud proxy |
| qwen3-coder-next:cloud | 0 GB | ☁️ Cloud proxy (unreleased) |
| bge-m3:latest | 1.1 GB | Multilingual embedding (RAG) |
| vicuna:13b-q4_K_M | 7.3 GB | General assistant |
| qwen2.5-coder:7b-instruct-q5_K_M | 5.1 GB | Code (quantized) |
| qwen2.5-coder:7b | 4.4 GB | Code |
| codellama:13b | 6.9 GB | Code |
| codellama:7b | 3.6 GB | Code |
| deepseek-coder:6.7b | 3.6 GB | Code |
| mistral:7b | 4.1 GB | General |

---

## System Prompts

| Model | Prompt |
|---|---|
| vicuna:13b | "A chat between a curious user and an artificial intelligence assistant. The assistant gives helpful, detailed, and polite answers." |
| qwen2.5-coder:7b variants | "You are Qwen, created by Alibaba Cloud. You are a helpful assistant." |
| deepseek-coder:6.7b | "You are an AI programming assistant, utilizing the Deepseek Coder model, developed by Deepseek Company, and you only answer questions related to computer science. For politically sensitive questions, security and privacy issues, and other non-computer science questions, you will refuse to answer." |

---

## Findings

### F1 — Coding RAG Pipeline Exposed (HIGH)

`bge-m3` (multilingual embedding, 500M params) co-deployed with 5 code models and a general assistant indicates an active RAG pipeline for code search/generation. Injection via `/api/create` on any of the code models redirects code output in RAG responses — particularly dangerous if this pipeline is used for student code review or automated grading.

### F2 — Pre-Release Cloud Code Model (HIGH)

`qwen3-coder-next:cloud` is an unreleased/beta cloud model accessible at no cost to any internet actor via the unauthenticated endpoint.

### F3 — CVE-2025-63389 on All 11 Models (CRITICAL)

All models injectable. The `deepseek-coder:6.7b` model has a code-only restriction in its system prompt that can be trivially overridden by injecting a new modelfile.

---

## Remediation

```bash
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

---

## Disclosure

- **Discovered:** 2026-05-03
- **Status:** Pending outreach to University of Dhaka IT
