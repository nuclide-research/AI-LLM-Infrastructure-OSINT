# Fu Jen Catholic University — Medical Public Health GPU Server, 75GB + 60GB Local Models

_NuClide Research · 2026-05-01_

---

## Summary

Fu Jen Catholic University's Medical and Public Health department (`user220.medph.fju.edu.tw`) has an Ollama instance exposed on port 11434 with 8 models totalling over 200GB of local inference capacity, including a 75GB mixture-of-experts model and a 60GB `gpt-oss:120b` local model.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 140.136.192.220 |
| Hostname | user220.medph.fju.edu.tw |
| Organization | Fu Jen Catholic University — Medical Public Health |
| Network | Taiwan MOE TANet (140.136.0.0/16) |
| Country | Taiwan |
| Open ports | 11434 (Ollama — public) |

---

## Model Inventory

| Model | Size | Notes |
|---|---|---|
| `qwen3.5:122b-a10b-q4_K_M` | 75GB | MoE, **125.1B params** verified via `/api/show` (tag `122b`), 10B-active, family `qwen35moe`, Q4_K_M quant |
| `gpt-oss:120b` | 60GB | 120B local inference (not cloud proxy) |
| `gemma4:31b-it-q8_0` | 31GB | High-quality quant |
| `mistral-small3.2:24b-instruct-2506-q8_0` | 24GB | Mistral Small 3.2 Q8 |
| `qwen3.5:27b-q8_0` | 27GB | — |
| `translategemma:27b-it-q4_K_M` | 16GB | Translation-specialized model |
| `qwen3.5:9b-q8_0` | 9GB | — |
| `qwen3-embedding:8b-q4_K_M` | 4GB | RAG embedding pipeline |

**Total local storage:** ~246GB of model weights

---

## Findings

### F1 — Unauthenticated Inference on Medical University Research Server (HIGH)

All 8 models are accessible without authentication. The `qwen3-embedding:8b` model signals an active RAG pipeline — documents loaded into the vector store (potentially medical research data, public health datasets, academic materials) are accessible via unauthenticated queries.

The `translategemma:27b` model is a translation-specialized fine-tune, suggesting the department is running multilingual document processing workflows through this server.

### F2 — CVE-2025-63389 Injectable (HIGH)

All models on the instance are injectable via the unauthenticated `/api/create` endpoint. Research or coursework workflows relying on any of these models are affected.

### F3 — Large Compute Exposure (HIGH)

The presence of a 75GB MoE model and a 60GB local 120B model indicates significant GPU hardware (likely multi-GPU workstation or small server). Unauthenticated inference against these models constitutes compute theft at scale.

---

## FJU Footprint (All Nodes)

| IP | Hostname | Version | Models | Notes |
|---|---|---|---|---|
| 140.136.192.220 | user220.medph.fju.edu.tw | 0.21.2 | 8 | Medical Public Health — 75GB MoE + gpt-oss:120b |
| 140.136.178.236 | user236.phy.fju.edu.tw | 0.21.0 | 4 | Physics — llama4:scout (system prompt), gemma4:31b, gemma2:27b |
| 140.136.239.75 | net2net.net.fju.edu.tw | 0.18.2 | 5 | Network Lab — openclaw-qwen (legal AI), nomic-embed-text (RAG), glm-4.7-flash |
| 140.136.147.26 | 740-26.ee.fju.edu.tw | 0.20.2 | 1 | EE dept — single model |

**user236.phy.fju.edu.tw** (Physics dept): `llama4:scout` carries a system prompt: `"You are an expert conversationalist who responds to the best of your ability. You are companionable and confident, and able to switch casually between tonal types, including but not limited to humor..."` — a researcher-configured conversational assistant on Physics department hardware.

**net2net.net.fju.edu.tw** (Network Lab): `openclaw-qwen:latest` is a Chinese legal reasoning model (OpenClaw) running on FJU's network lab server alongside `nomic-embed-text` (RAG embedding) — indicating a legal document retrieval pipeline.

---

## Taiwan MOE TANet Context

FJU is part of the TANet `140.136.0.0/16` block with at least 4 exposed nodes across Medical Public Health, Physics, and the Network Lab. All are injectable via CVE-2025-63389.

---

## Remediation

```bash
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

---

## Disclosure

- **Discovered:** 2026-05-01
- **Status:** Pending outreach to FJU IT Security (medph.fju.edu.tw)
