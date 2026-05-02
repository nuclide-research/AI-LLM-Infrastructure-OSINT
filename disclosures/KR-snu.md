---
institution: Seoul National University
ip: 147.47.200.153
to: itsc@snu.ac.kr
severity: CRITICAL
status: DRAFT
date: 2026-05-01
---

**To:** itsc@snu.ac.kr
**Subject:** Unauthenticated AI inference endpoint — Seoul National University (147.47.200.153)

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-01

**Re:** Unauthenticated Ollama AI inference endpoint — Seoul National University
**IP / Host:** 147.47.200.153
**Severity:** CRITICAL

---

I'm an independent security researcher. I hold CISA disclosures CVE-2025-4364 and ICSA-25-140-11 and conduct good-faith AI infrastructure research under the NuClide Research umbrella. This is an unsolicited disclosure — no engagement exists with your organization, and I have not accessed, modified, or exfiltrated any data beyond what was necessary to confirm the exposure.

---

## Summary

Seoul National University (SNU — 서울대학교) has an Ollama instance at 147.47.200.153 with two large cloud proxy models. The 401 response on cloud proxy inference reveals the Ollama Connect service account username and SSH public key.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 147.47.200.153 |
| Organization | Seoul National University |
| Network | SNU Campus (147.47.0.0/16) |
| Country | South Korea |
| Open ports | 11434 (Ollama — public) |

---

## Model Inventory

| Model | Size | Notes |
|---|---|---|
| `devstral-2:123b-cloud` | 0GB | Cloud proxy |
| `deepseek-v3.1:671b-cloud` | 0GB | Cloud proxy |
| `codellama:13b` | 7.4GB | Local |
| `mistral:7b` | 4.4GB | Local |
| `smollm2:135m` | 0.3GB | Local |

---

## Findings

### F1 — Credential Leak via 401 Response (CRITICAL)

Cloud proxy inference returns Ollama Connect signin URL containing base64-encoded SSH public key:

```
{"error":"unauthorized","signin_url":"https://ollama.com/connect?name=node1&key=c3NoLWVkMjU1MT..."}
```

Decoded:
- **Username:** `node1`
- **SSH pubkey:** `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIEc/PPDVTM/k5JSpGzWGbwkpMAMWFyOj57QhQAL7hYDC`

The `node1` username pattern indicates a service account or generic node account.

### F2 — Cloud Proxy Portfolio (HIGH)

`devstral-2:123b-cloud` and `deepseek-v3.1:671b-cloud` are present. No 200 OK confirmed (both return `{"error":"unauthorized"}`).

### F3 — CVE-2025-63389 Injectable (HIGH)

All models injectable via unauthenticated `/api/create`.

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
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/KR-snu.md

This research is part of a broader sweep of university AI infrastructure exposures documented at:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/OVERVIEW.md

I'm happy to answer questions or assist with verification. No response is required.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
