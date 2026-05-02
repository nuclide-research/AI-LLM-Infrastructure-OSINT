---
institution: KTH Royal Institute of Technology
ip: 130.237.67.161 (+1 nodes)
to: it-support@kth.se
cc: abuse@cert.sunet.se
severity: CRITICAL
status: DRAFT
date: 2026-05-01
---

**To:** it-support@kth.se
**Cc:** abuse@cert.sunet.se
**Subject:** Unauthenticated AI inference endpoint — KTH Royal Institute of Technology (130.237.67.161 (+1 nodes))

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-01

**Re:** Unauthenticated Ollama AI inference endpoint — KTH Royal Institute of Technology
**IP / Host:** 130.237.67.161 (+1 nodes)
**Severity:** CRITICAL

---

I'm an independent security researcher. I hold CISA disclosures CVE-2025-4364 and ICSA-25-140-11 and conduct good-faith AI infrastructure research under the NuClide Research umbrella. This is an unsolicited disclosure — no engagement exists with your organization, and I have not accessed, modified, or exfiltrated any data beyond what was necessary to confirm the exposure.

---

## Summary

KTH Royal Institute of Technology (Stockholm) has two separate servers running unauthenticated Ollama with DeepSeek v4 Pro cloud proxy subscriptions. One node hosts an "abliterated" (safety-fine-tuning-removed) Gemma model and runs Ollama as root. Both nodes injectable via CVE-2025-63389.

---

## Infrastructure

| Host | IP | Models | Cloud | Notes |
|------|-----|--------|-------|-------|
| 130.237.67.161 | KTH net | 12 | deepseek-v4-pro | — |
| 130.237.3.105 | KTH net | 8 | deepseek-v4-pro | **Abliterated model, running as root** |

---

## Node 1 — 130.237.67.161 (12 models)

Includes: qwen3.6:35b, deepseek-r1:32b, qwen3.5:35b-a3b, deepseek-v4-pro:cloud

## Node 2 — 130.237.3.105 (8 models)

Includes: qwen3.6:35b, qwen3.5:9b, deepseek-v4-pro:cloud, **`hf.co/OBLITERATUS/gemma-4-E4B-it-OBLITERATED:latest`**

Abliterated model details:
- Modelfile path: `/root/.ollama/models/...` — **Ollama running as root**
- No system prompt — safety fine-tuning removed by design
- OBLITERATUS is a well-known HuggingFace model series that removes safety RLHF from base models

---

## Findings

### F1 — Unauthenticated Ollama on Both Nodes (CRITICAL)

Both servers publicly expose port 11434. All models enumerable and injectable without credentials.

### F2 — DeepSeek Cloud Proxy on Both Nodes (HIGH)

`deepseek-v4-pro:cloud` present on both. 401 returned without credential disclosure. Model injection via CVE-2025-63389 can redirect all cloud proxy traffic.

### F3 — Abliterated Model Running as Root (HIGH)

Node 130.237.3.105 runs Ollama as `root` (`/root/.ollama/`). An abliterated model (safety fine-tuning removed) is deployed and accessible to unauthenticated callers. Any actor can inject this model's system prompt or run uncensored inference via the unauthenticated port.

---

**Why it matters**

The credential leak (username + SSH public key) exposes your service account to enumeration and credential-stuffing against other services.

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
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/SE/KTH.md

This research is part of a broader sweep of university AI infrastructure exposures documented at:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/OVERVIEW.md

I'm happy to answer questions or assist with verification. No response is required.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
