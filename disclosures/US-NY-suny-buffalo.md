---
institution: SUNY Buffalo
ip: 136.183.56.88
to: sec-office@buffalo.edu
severity: CRITICAL
status: DRAFT
date: 2026-05-01
---

**To:** sec-office@buffalo.edu
**Subject:** Unauthenticated AI inference endpoint — SUNY Buffalo (136.183.56.88)

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-01

**Re:** Unauthenticated Ollama AI inference endpoint — SUNY Buffalo
**IP / Host:** 136.183.56.88
**Severity:** CRITICAL

---

I'm an independent security researcher. I hold CISA disclosures CVE-2025-4364 and ICSA-25-140-11 and conduct good-faith AI infrastructure research under the NuClide Research umbrella. This is an unsolicited disclosure — no engagement exists with your organization, and I have not accessed, modified, or exfiltrated any data beyond what was necessary to confirm the exposure.

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

**Why it matters**

Any internet actor can run inference against your cloud API subscription at your expense — this constitutes direct quota/billing theft. An embedding model indicates an active RAG pipeline — documents loaded into your vector store are reachable via unauthenticated queries.

**One-line fix**

```
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

This rebinds Ollama to loopback only. If running in Docker: `docker run -p 127.0.0.1:11434:11434 ollama/ollama`.

**CVE-2025-63389**

All models on this instance are injectable via the unauthenticated `/api/create` endpoint — an attacker can overwrite any model's system prompt or delete models entirely. No patch exists as of this disclosure.

**Reference**

Full technical details, parameter counts, and remediation notes are in this public research repository:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/US-NY-suny-buffalo.md

This research is part of a broader sweep of university AI infrastructure exposures documented at:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/OVERVIEW.md

I'm happy to answer questions or assist with verification. No response is required.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
