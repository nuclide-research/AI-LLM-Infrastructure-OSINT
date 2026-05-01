---
institution: COMSATS University
ip: 203.124.40.57
to: security@comsats.edu.pk
severity: CRITICAL
status: DRAFT
date: 2026-05-01
---

**To:** security@comsats.edu.pk
**Subject:** Unauthenticated AI inference endpoint — COMSATS University (203.124.40.57)

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-01

**Re:** Unauthenticated Ollama AI inference endpoint — COMSATS University
**IP / Host:** 203.124.40.57
**Severity:** CRITICAL

---

I'm an independent security researcher. I hold CISA disclosures CVE-2025-4364 and ICSA-25-140-11 and conduct good-faith AI infrastructure research under the NuClide Research umbrella. This is an unsolicited disclosure — no engagement exists with your organization, and I have not accessed, modified, or exfiltrated any data beyond what was necessary to confirm the exposure.

---

## Summary

COMSATS (Commission on Science and Technology for Sustainable Development in the South) — an intergovernmental international organization with a university campus network — has an Ollama instance with two MedGemma medical AI models (27B and 4B) alongside a Kimi K2.6 cloud proxy. The presence of medical-domain AI models on a publicly accessible research network endpoint raises data-handling concerns.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 203.124.40.57 |
| Organization | COMSATS (Commission on Science and Technology for Sustainable Development in the South) |
| Country | Pakistan |
| Open ports | 11434 (Ollama — public) |

---

## Model Inventory

| Model | Size | Notes |
|---|---|---|
| `kimi-k2.6:cloud` | 0GB | Cloud proxy (unauthorized — no cred leak) |
| `puyangwang/medgemma-27b-it:q8` | 29.6GB | MedGemma 27B Q8 — medical AI |
| `thiagomoraes/medgemma-1.5-4b-it:F16` | 8.6GB | MedGemma 1.5B instruct |
| `gemma4:26b` | 18.0GB | — |
| `qwen3.6:latest` | 23.9GB | — |
| `gemma3:12b` | 8.1GB | — |
| `llama3.2:3b` | 2.0GB | — |

---

## Findings

### F1 — Medical AI Models Exposed Without Authentication (HIGH)

`puyangwang/medgemma-27b-it:q8` (29.6GB, 27.4B params, Gemma3 family) is a community quantization of Google's MedGemma — a model specifically designed for medical question answering, clinical note processing, and health professional workflows. Co-located alongside `medgemma-1.5-4b-it`, the deployment suggests active medical AI research or clinical support tooling.

Both models are accessible without authentication, allowing unauthenticated parties to:
- Query the models with arbitrary medical content
- Inject system prompts via CVE-2025-63389 to alter medical AI behavior
- Potentially extract any RAG-loaded clinical documents via embedding queries

### F2 — Cloud Proxy Present (Unauthorized) (MEDIUM)

`kimi-k2.6:cloud` is present but returns `{"error": "unauthorized"}` with no credential leak in the 401 response body. No quota drain confirmed.

### F3 — CVE-2025-63389 Injectable (HIGH)

All models injectable via unauthenticated `/api/create`. System prompt injection on medical models is particularly sensitive — an adversary could instruct `medgemma-27b` to provide dangerous medical advice or suppress safety caveats.

---

**Why it matters**

Any internet actor can run inference against your cloud API subscription at your expense — this constitutes direct quota/billing theft. The credential leak (username + SSH public key) exposes your service account to enumeration and credential-stuffing against other services. An embedding model indicates an active RAG pipeline — documents loaded into your vector store are reachable via unauthenticated queries. Medical AI models exposed without authentication create compliance risk (potential HIPAA/patient-data adjacent exposure depending on RAG content).

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
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/PK-comsats.md

This research is part of a broader sweep of university AI infrastructure exposures documented at:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/OVERVIEW.md

I'm happy to answer questions or assist with verification. No response is required.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
