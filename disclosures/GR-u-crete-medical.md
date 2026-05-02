---
institution: University of Crete Medical Center
ip: 147.52.71.221
to: info-ict@uoc.gr
cc: grnet-cert@grnet.gr
severity: CRITICAL
status: DRAFT
date: 2026-05-01
---

**To:** info-ict@uoc.gr
**Cc:** grnet-cert@grnet.gr
**Subject:** Unauthenticated AI inference endpoint — University of Crete Medical Center (147.52.71.221)

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-01

**Re:** Unauthenticated Ollama AI inference endpoint — University of Crete Medical Center
**IP / Host:** 147.52.71.221
**Severity:** CRITICAL

---

I'm an independent security researcher. I hold CISA disclosures CVE-2025-4364 and ICSA-25-140-11 and conduct good-faith AI infrastructure research under the NuClide Research umbrella. This is an unsolicited disclosure — no engagement exists with your organization, and I have not accessed, modified, or exfiltrated any data beyond what was necessary to confirm the exposure.

---

## Summary

The University of Crete Medical Center (`centaur.med.uoc.gr`) is running Ollama with a sophisticated dual-embedding RAG pipeline — both `mxbai-embed-large` and `nomic-embed-text` are deployed alongside large language models (Llama 3.3, Qwen3-Coder, Mistral). Dual embedding models indicate a production RAG system over medical/research content, unauthenticated and injectable.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 147.52.71.221 |
| rDNS | `centaur.med.uoc.gr` |
| Org | University of Crete |
| Facility | Medical Center (med.uoc.gr) |
| Country | Greece |
| Open ports | 11434 (Ollama — **public**) |

---

## Models

| Model | Size | Notes |
|---|---|---|
| llama3.3:latest | 39 GB | Large LLM |
| qwen3-coder:30b | 17 GB | Code model |
| qwen2.5-coder:latest | 4 GB | Code model |
| qwen2.5:latest | 4 GB | — |
| mistral:latest | 4 GB | — |
| gemma3:latest | 3 GB | — |
| **mxbai-embed-large:latest** | 0 GB | **Embedding model 1 — RAG pipeline** |
| **nomic-embed-text:latest** | 0 GB | **Embedding model 2 — RAG pipeline** |

---

## Findings

**F1 — Dual-Embedding RAG Pipeline on Medical Server (CRITICAL):** Two embedding models (mxbai-embed-large + nomic-embed-text) running simultaneously indicates a production RAG system. On a medical university server, the document corpus likely includes medical research, clinical workflows, or patient-facing content. Model injection via CVE-2025-63389 affects all documents served through the RAG pipeline.

**F2 — Unauthenticated Medical Research Server (HIGH):** `centaur` suggests an academic/mythological name for a compute node (common at Greek universities). All models accessible without credentials — researchers' document-augmented queries are injectable.

**F3 — Model Injection (HIGH):** All 8 models injectable via CVE-2025-63389.

---

## Context

This is a separate institution from the Technical University of Crete (TUC, 147.27.38.32) documented in GR-tech-crete-ntua.md. University of Crete (UoC) is a public university with a medical school; `centaur.med.uoc.gr` is a named server in the medical faculty.

---

**Why it matters**

The credential leak (username + SSH public key) exposes your service account to enumeration and credential-stuffing against other services. An embedding model indicates an active RAG pipeline — documents loaded into your vector store are reachable via unauthenticated queries. Medical AI models exposed without authentication create compliance risk (potential HIPAA/patient-data adjacent exposure depending on RAG content).

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
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/GR-u-crete-medical.md

This research is part of a broader sweep of university AI infrastructure exposures documented at:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/OVERVIEW.md

I'm happy to answer questions or assist with verification. No response is required.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
