---
institution: University of Newcastle, Australia
ip: 157.85.107.12
to: dts-cybersecurity@newcastle.edu.au
severity: CRITICAL
status: DRAFT
date: 2026-05-01
---

**To:** dts-cybersecurity@newcastle.edu.au
**Subject:** Unauthenticated AI inference endpoint — University of Newcastle, Australia (157.85.107.12)

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-01

**Re:** Unauthenticated Ollama AI inference endpoint — University of Newcastle, Australia
**IP / Host:** 157.85.107.12
**Severity:** CRITICAL

---

I'm an independent security researcher. I hold CISA disclosures CVE-2025-4364 and ICSA-25-140-11 and conduct good-faith AI infrastructure research under the NuClide Research umbrella. This is an unsolicited disclosure — no engagement exists with your organization, and I have not accessed, modified, or exfiltrated any data beyond what was necessary to confirm the exposure.

---

## Summary

University of Newcastle (Australia, Callaghan campus) server with `deepseek-v4-pro:cloud` cloud proxy subscription and `mxbai-embed-large:latest` embedding model indicating an active RAG pipeline. Raw Ollama port publicly accessible, no authentication.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 157.85.107.12 |
| Org | University of Newcastle, Australia — Callaghan campus |
| Country | Australia |
| Open ports | 11434 (Ollama — **public**) |

---

## Models

| Model | Size | Notes |
|---|---|---|
| deepseek-v4-pro:cloud | 0 GB | ☁️ Cloud proxy — DeepSeek API |
| qwen3.5:35b | 22 GB | Local |
| qwen2.5:32b | 18 GB | Local |
| qwen3.5:9b | 6 GB | Local |
| mxbai-embed-large:latest | 0 GB | **Embedding — RAG pipeline** |

`mxbai-embed-large` is a high-performance text embedding model used in RAG (retrieval-augmented generation) pipelines. Its presence alongside large language models confirms this Ollama instance is backing a document retrieval system.

---

## Findings

**F1 — Unauthenticated Ollama API (CRITICAL):** Port 11434 publicly accessible.  
**F2 — DeepSeek Cloud Proxy (HIGH):** `deepseek-v4-pro:cloud` accessible, 401 returned.  
**F3 — RAG Pipeline Injection Surface (HIGH):** Embedding model present — model injection via CVE-2025-63389 affects documents served via RAG.

---

**Why it matters**

An embedding model indicates an active RAG pipeline — documents loaded into your vector store are reachable via unauthenticated queries.

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
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/AU-newcastle.md

This research is part of a broader sweep of university AI infrastructure exposures documented at:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/OVERVIEW.md

I'm happy to answer questions or assist with verification. No response is required.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
