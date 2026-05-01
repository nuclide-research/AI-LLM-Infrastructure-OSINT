---
institution: SUNY Stony Brook
ip: 129.49.40.218
to: security@stonybrook.edu
severity: CRITICAL
status: DRAFT
date: 2026-05-01
---

**To:** security@stonybrook.edu
**Subject:** Unauthenticated AI inference endpoint — SUNY Stony Brook (129.49.40.218)

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-01

**Re:** Unauthenticated Ollama AI inference endpoint — SUNY Stony Brook
**IP / Host:** 129.49.40.218
**Severity:** CRITICAL

---

I'm an independent security researcher. I hold CISA disclosures CVE-2025-4364 and ICSA-25-140-11 and conduct good-faith AI infrastructure research under the NuClide Research umbrella. This is an unsolicited disclosure — no engagement exists with your organization, and I have not accessed, modified, or exfiltrated any data beyond what was necessary to confirm the exposure.

---

## Summary

SUNY Stony Brook Biology Department server (`040-218.bio.sunysb.edu`) is running Ollama with the full Allen AI OLMo-3 research stack (olmo-3, olmo-3.1-32b-think, olmo-3.1-32b-instruct) alongside `gpt-oss:latest` cloud proxy and several Gemma 4 models. Unauthenticated, publicly accessible.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 129.49.40.218 |
| rDNS | `040-218.bio.sunysb.edu` |
| Org | State University of New York at Stony Brook |
| Department | Biology |
| Country | US — New York |
| Open ports | 11434 (Ollama — **public**) |

---

## Models

| Model | Size | Notes |
|---|---|---|
| gpt-oss:latest | ? | ☁️ Cloud proxy |
| olmo-3:latest | ? | Allen AI OLMo-3 |
| olmo-3.1:32b-think | ? | Allen AI OLMo-3.1 reasoning |
| olmo-3.1:32b-instruct | ? | Allen AI OLMo-3.1 instruct |
| mistral-small3.2:latest | ? | — |
| gemma4:26b | ? | — |
| gemma4:latest | ? | — |
| lfm2:latest | ? | Liquid FM-2 |

---

## Findings

**F1 — Biology Research Server (HIGH):** OLMo models (Allen AI's open research language models) suggest active NLP/bioinformatics research. Model injection via CVE-2025-63389 affects research outputs.

**F2 — Cloud Proxy Exposure (HIGH):** `gpt-oss:latest` present. Status (200 OK vs 401) not confirmed in final probe.

**F3 — Model Injection (HIGH):** All models injectable via CVE-2025-63389.

---

**Why it matters**

Any internet actor can run inference against your cloud API subscription at your expense — this constitutes direct quota/billing theft.

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
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/US-NY-suny-stony-brook.md

This research is part of a broader sweep of university AI infrastructure exposures documented at:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/OVERVIEW.md

I'm happy to answer questions or assist with verification. No response is required.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
