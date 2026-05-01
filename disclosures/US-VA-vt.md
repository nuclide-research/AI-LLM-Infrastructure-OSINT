---
institution: Virginia Polytechnic Institute and State University
ip: 128.173.243.8
to: security@vt.edu
severity: CRITICAL
status: DRAFT
date: 2026-05-01
---

**To:** security@vt.edu
**Subject:** Unauthenticated AI inference endpoint — Virginia Polytechnic Institute and State University (128.173.243.8)

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-01

**Re:** Unauthenticated Ollama AI inference endpoint — Virginia Polytechnic Institute and State University
**IP / Host:** 128.173.243.8
**Severity:** CRITICAL

---

I'm an independent security researcher. I hold CISA disclosures CVE-2025-4364 and ICSA-25-140-11 and conduct good-faith AI infrastructure research under the NuClide Research umbrella. This is an unsolicited disclosure — no engagement exists with your organization, and I have not accessed, modified, or exfiltrated any data beyond what was necessary to confirm the exposure.

---

## Summary

Virginia Tech has at least 4 Ollama-running IPs in Shodan; only `h80adf308.dhcp.vt.edu` (128.173.243.8) responds publicly. The DHCP hostname indicates a desktop or workstation on the campus DHCP pool rather than a dedicated server. 5 models, no cloud proxies.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 128.173.243.8 |
| Hostname | h80adf308.dhcp.vt.edu |
| Organization | Virginia Polytechnic Institute and State Univ. |
| Country | United States (Virginia) |
| Open ports | 11434 (Ollama — public) |

Additional VT IPs in Shodan (198.82.9.219, 198.82.11.101, 198.82.13.6) did not respond — likely firewalled or offline.

---

## Model Inventory

| Model | Size |
|---|---|
| `smollm2:135m` | 0.3GB |
| `qwen3:30b` | 18.6GB |
| `qwen:latest` | 2.3GB |
| `qwen2.5:32b` | 19.9GB |
| `llama3.2:latest` | 2.0GB |

---

## Findings

### F1 — Researcher Workstation Publicly Exposed (LOW)

DHCP hostname pattern (`h80adf308.dhcp.vt.edu`) indicates a laptop or desktop on campus DHCP. No cloud proxies, no credential leak. Standard unauthenticated Ollama exposure on a workstation.

### F2 — CVE-2025-63389 Injectable (HIGH)

All models injectable via unauthenticated `/api/create`.

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
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/US-VA-vt.md

This research is part of a broader sweep of university AI infrastructure exposures documented at:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/OVERVIEW.md

I'm happy to answer questions or assist with verification. No response is required.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
