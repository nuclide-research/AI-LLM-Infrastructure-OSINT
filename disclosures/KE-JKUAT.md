---
institution: Jomo Kenyatta University of Agriculture and Technology
ip: 41.89.8.169
to: security@jkuat.ac.ke
severity: CRITICAL
status: DRAFT
date: 2026-05-01
---

**To:** security@jkuat.ac.ke
**Subject:** Unauthenticated AI inference endpoint — Jomo Kenyatta University of Agriculture and Technology (41.89.8.169)

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-01

**Re:** Unauthenticated Ollama AI inference endpoint — Jomo Kenyatta University of Agriculture and Technology
**IP / Host:** 41.89.8.169
**Severity:** CRITICAL

---

I'm an independent security researcher. I hold CISA disclosures CVE-2025-4364 and ICSA-25-140-11 and conduct good-faith AI infrastructure research under the NuClide Research umbrella. This is an unsolicited disclosure — no engagement exists with your organization, and I have not accessed, modified, or exfiltrated any data beyond what was necessary to confirm the exposure.

---

## Summary

Jomo Kenyatta University of Agriculture and Technology (JKUAT), Kenya, is running an Ollama instance on campus with a MiniMax cloud proxy subscription publicly accessible without authentication. One local model alongside the cloud proxy. No credential leak detected on this instance.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 41.89.8.169 |
| rDNS | — (NXDOMAIN) |
| Org | Jomo Kenyatta University of Agriculture and Technology (KENET) |
| Country | Kenya |
| Open ports | 11434 (Ollama — **public**) |

JKUAT connects to the internet via KENET (Kenya Education Network). The IP block (`41.89.8.x`) is assigned to JKUAT's main campus.

---

## Models

| Model | Size | Type |
|---|---|---|
| minimax-m2.7:cloud | 0 GB | ☁️ Cloud proxy — MiniMax API |
| llama3.2:3b | 1 GB | Local |

---

## Findings

**F1 — Unauthenticated Ollama API (HIGH):** Port 11434 publicly accessible. No authentication on `/api/tags`, `/api/show`, or `/api/create`.  
**F2 — Cloud Proxy Subscription Exposed (MEDIUM):** `minimax-m2.7:cloud` accessible to any internet caller. 401 returned without credential leak on this instance.  
**F3 — Model Injection (HIGH):** Both models injectable via CVE-2025-63389 (no patch).

---

## Notes

The cloud proxy 401 response is routed through Google Frontend (Ollama Connect) and does not expose account credentials in the response body on this instance — unlike Hanoi, Armenian Academy, and Purdue NW where Docker container IDs leaked as usernames.

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
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/KE-JKUAT.md

This research is part of a broader sweep of university AI infrastructure exposures documented at:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/OVERVIEW.md

I'm happy to answer questions or assist with verification. No response is required.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
