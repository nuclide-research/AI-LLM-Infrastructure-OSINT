---
institution: Vietnam National University Ho Chi Minh City
ip: 103.88.123.165
to: info@vnuhcm.edu.vn
severity: CRITICAL
status: DRAFT
date: 2026-05-01
---

**To:** info@vnuhcm.edu.vn
**Subject:** Unauthenticated AI inference endpoint — Vietnam National University Ho Chi Minh City (103.88.123.165)

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-01

**Re:** Unauthenticated Ollama AI inference endpoint — Vietnam National University Ho Chi Minh City
**IP / Host:** 103.88.123.165
**Severity:** CRITICAL

---

I'm an independent security researcher. I hold CISA disclosures CVE-2025-4364 and ICSA-25-140-11 and conduct good-faith AI infrastructure research under the NuClide Research umbrella. This is an unsolicited disclosure — no engagement exists with your organization, and I have not accessed, modified, or exfiltrated any data beyond what was necessary to confirm the exposure.

---

## Summary

Vietnam National University Ho Chi Minh City (Information Technology Park) has an Ollama instance with an unusually named model `final-exploit-v1:latest` and a `gpt-oss:latest` cloud proxy. The `final-exploit-v1` model is 168 bytes — the size of a cloud proxy artifact, not a local model — suggesting a custom-named cloud redirect.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 103.88.123.165 |
| rDNS | — |
| Org | Information Technology Park — Vietnam National University Ho Chi Minh City |
| Country | Vietnam |
| Open ports | 11434 (Ollama — **public**) |

---

## Models

| Model | Size | Notes |
|---|---|---|
| final-exploit-v1:latest | 0 GB (168 bytes) | **Cloud proxy artifact — custom-named** |
| gpt-oss:latest | 12 GB | ☁️ Cloud proxy |
| llama3.2:3b | 1 GB | Local |
| llama3.2:latest | 1 GB | Local |
| smollm2:135m | 0 GB | Local |
| tinyllama:latest | 0 GB | Local |

---

## Findings

**F1 — Unauthenticated Ollama API (HIGH):** All models accessible without credentials.

**F2 — `final-exploit-v1` Cloud Proxy Artifact (MEDIUM):** The model is 168 bytes — identical size pattern to standard cloud proxy models (deepseek-v4-pro:cloud = 344 bytes, minimax = 384 bytes). Modified January 2026. No system prompt returned. Inference returns empty response. Likely a student-created cloud proxy with custom naming.

**F3 — gpt-oss Cloud Proxy (HIGH):** `gpt-oss:latest` 12GB present. Status (200 OK vs 401) not confirmed on final probe.

**F4 — Model Injection (HIGH):** All models injectable via CVE-2025-63389.

---

**Why it matters**

Any internet actor can run inference against your cloud API subscription at your expense — this constitutes direct quota/billing theft. The credential leak (username + SSH public key) exposes your service account to enumeration and credential-stuffing against other services.

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
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/VN/vnu-hcmc.md

This research is part of a broader sweep of university AI infrastructure exposures documented at:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/OVERVIEW.md

I'm happy to answer questions or assist with verification. No response is required.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
