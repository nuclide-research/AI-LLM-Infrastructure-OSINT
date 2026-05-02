---
institution: University of Western Ontario
ip: 129.100.226.217
to: security@uwo.ca
severity: CRITICAL
status: DRAFT
date: 2026-05-01
---

**To:** security@uwo.ca
**Subject:** Unauthenticated AI inference endpoint — University of Western Ontario (129.100.226.217)

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-01

**Re:** Unauthenticated Ollama AI inference endpoint — University of Western Ontario
**IP / Host:** 129.100.226.217
**Severity:** CRITICAL

---

I'm an independent security researcher. I hold CISA disclosures CVE-2025-4364 and ICSA-25-140-11 and conduct good-faith AI infrastructure research under the NuClide Research umbrella. This is an unsolicited disclosure — no engagement exists with your organization, and I have not accessed, modified, or exfiltrated any data beyond what was necessary to confirm the exposure.

---

## Summary

University of Western Ontario (London, Ontario) research server running 9 Ollama models including `deepseek-v4-pro:cloud`. Cloud proxy request returns 401 (subscription tier limit) without credential leak — cloud subscription authenticated but not drained on this probe. Raw Ollama port publicly accessible, no authentication.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 129.100.226.217 |
| rDNS | WE-D-ECE-0288.eng.uwo.ca |
| Org | University of Western Ontario |
| Faculty | Engineering (ECE department — hostname) |
| Country | Canada — Ontario |
| Open ports | 11434 (Ollama — **public**) |

---

## Models

| Model | Size | Notes |
|---|---|---|
| deepseek-v4-pro:cloud | 0 GB | ☁️ Cloud proxy — DeepSeek API |
| qwen3.6:35b | 22 GB | Local |
| qwen2.5vl:3b | 2 GB | Local — vision-language |
| qwen2.5vl:7b-q8_0 | 8 GB | Local — vision-language |
| gemma4:e2b | 6 GB | Local |
| gemma4:31b | 18 GB | Local |
| qwen2.5vl:latest | 5 GB | Local — vision-language |
| llava:latest | 4 GB | Local — vision-language |
| qwen3.5:35b | 22 GB | Local |

---

## Findings

### F1 — Unauthenticated Ollama API (CRITICAL)

Port 11434 publicly accessible. All models enumerable and injectable without credentials.

### F2 — Cloud Proxy Accessible (HIGH)

`deepseek-v4-pro:cloud` is accessible on the unauthenticated port. 401 returned (subscription tier limit) without credential disclosure on this probe. Inference may succeed at lower priority times or with different model variants. Model injection via `/api/create` can redirect all cloud proxy traffic.

### F3 — Vision-Language Models Exposed (MEDIUM)

Three vision-language model variants (qwen2.5vl, llava) accessible without auth. If used in document or image workflows, injection would affect all vision-assisted outputs.

---

**Why it matters**

The credential leak (username + SSH public key) exposes your service account to enumeration and credential-stuffing against other services.

**One-line fix**

```
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

This rebinds Ollama to loopback only. If running in Docker: `docker run -p 127.0.0.1:11434:11434 ollama/ollama`.

**Reference**

Full technical details, parameter counts, and remediation notes are in this public research repository:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/CA/ON-western-ontario.md

This research is part of a broader sweep of university AI infrastructure exposures documented at:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/OVERVIEW.md

I'm happy to answer questions or assist with verification. No response is required.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
