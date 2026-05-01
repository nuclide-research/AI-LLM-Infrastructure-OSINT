---
institution: Thailand Ministry of Public Health
ip: 203.157.41.151
to: security@moph.go.th
severity: HIGH
status: DRAFT
date: 2026-05-01
---

**To:** security@moph.go.th
**Subject:** Unauthenticated AI inference endpoint — Thailand Ministry of Public Health (203.157.41.151)

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-01

**Re:** Unauthenticated Ollama AI inference endpoint — Thailand Ministry of Public Health
**IP / Host:** 203.157.41.151
**Severity:** HIGH

---

I'm an independent security researcher. I hold CISA disclosures CVE-2025-4364 and ICSA-25-140-11 and conduct good-faith AI infrastructure research under the NuClide Research umbrella. This is an unsolicited disclosure — no engagement exists with your organization, and I have not accessed, modified, or exfiltrated any data beyond what was necessary to confirm the exposure.

---

## Summary

Thailand's Ministry of Public Health (MoPH) has an Ollama instance at 203.157.41.151 with 5 models publicly accessible, including `granite3.2-vision:2b` (IBM's vision-language model) and `qwen3.6:35b` (22GB). No authentication, no Open WebUI fronting the API.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 203.157.41.151 |
| Organization | Ministry of Public Health, Thailand |
| Country | Thailand |
| Open ports | 11434 (Ollama — public) |

---

## Model Inventory

| Model | Size | Notes |
|---|---|---|
| `qwen3.6:35b` | 22GB | Large general LLM |
| `granite3.2-vision:2b` | 2GB | IBM Granite vision-language model |
| `gemma3:4b` | 3GB | Google Gemma3 |
| `llama3.2:3b` | 1GB | — |
| `smollm2:135m` | — | Tiny LLM |

---

## Findings

### F1 — Government Health Ministry Inference Exposed (HIGH)

All 5 models are accessible without authentication on a Thai government Ministry of Public Health IP. Any internet actor can:
- Run inference against `qwen3.6:35b` (22GB, large model) at MoPH compute cost
- Submit images to `granite3.2-vision:2b` for analysis
- Enumerate all configured models via `/api/tags`

The `granite3.2-vision:2b` model carries IBM's default system prompt (not customized), indicating likely development/testing rather than a custom healthcare application.

No Open WebUI was detected on port 3000. The Ollama API is directly exposed with no frontend authentication layer.

### F2 — CVE-2025-63389 Injectable (HIGH)

All 5 models injectable via unauthenticated `/api/create`. If any of these models are being used for internal MoPH workflows, injected prompts affect those users.

---

**Why it matters**

Medical AI models exposed without authentication create compliance risk (potential HIPAA/patient-data adjacent exposure depending on RAG content).

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
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/TH-moph.md

This research is part of a broader sweep of university AI infrastructure exposures documented at:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/OVERVIEW.md

I'm happy to answer questions or assist with verification. No response is required.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
