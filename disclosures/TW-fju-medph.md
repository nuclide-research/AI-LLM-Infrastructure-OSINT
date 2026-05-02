---
institution: Fu Jen Catholic University
ip: 140.136.192.220
to: security@fju.edu.tw
severity: HIGH
status: DRAFT
date: 2026-05-01
---

**To:** security@fju.edu.tw
**Subject:** Unauthenticated AI inference endpoint — Fu Jen Catholic University (140.136.192.220)

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-01

**Re:** Unauthenticated Ollama AI inference endpoint — Fu Jen Catholic University
**IP / Host:** 140.136.192.220
**Severity:** HIGH

---

I'm an independent security researcher. I hold CISA disclosures CVE-2025-4364 and ICSA-25-140-11 and conduct good-faith AI infrastructure research under the NuClide Research umbrella. This is an unsolicited disclosure — no engagement exists with your organization, and I have not accessed, modified, or exfiltrated any data beyond what was necessary to confirm the exposure.

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

## Taiwan MOE TANet Context

This server is one of 11+ Ollama instances identified on the Taiwan Ministry of Education Academic Network (TANet) across universities including NTU, NCKU, FJU, and NCU. See `TW-ncku.md` for full TANET coverage table.

---

**Why it matters**

An embedding model indicates an active RAG pipeline — documents loaded into your vector store are reachable via unauthenticated queries. Medical AI models exposed without authentication create compliance risk (potential HIPAA/patient-data adjacent exposure depending on RAG content).

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
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/TW/fju-medph.md

This research is part of a broader sweep of university AI infrastructure exposures documented at:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/OVERVIEW.md

I'm happy to answer questions or assist with verification. No response is required.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
