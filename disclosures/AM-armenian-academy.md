---
institution: Institute for Informatics and Automation Problems, Armenia
ip: 37.26.168.19
to: ipia@ipia.sci.am
severity: CRITICAL
status: DRAFT
date: 2026-05-01
---

**To:** ipia@ipia.sci.am
**Subject:** Unauthenticated AI inference endpoint — Institute for Informatics and Automation Problems, Armenia (37.26.168.19)

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-01

**Re:** Unauthenticated Ollama AI inference endpoint — Institute for Informatics and Automation Problems, Armenia
**IP / Host:** 37.26.168.19
**Severity:** CRITICAL

---

I'm an independent security researcher. I hold CISA disclosures CVE-2025-4364 and ICSA-25-140-11 and conduct good-faith AI infrastructure research under the NuClide Research umbrella. This is an unsolicited disclosure — no engagement exists with your organization, and I have not accessed, modified, or exfiltrated any data beyond what was necessary to confirm the exposure.

---

## Summary

The Institute for Informatics and Automation Problems of the National Academy of Sciences of Armenia (Yerevan) is running Ollama inside a Docker container with two cloud proxy subscriptions. The 401 response leaks Docker container credentials — consistent with the Docker port-binding misconfig pattern also found at Hanoi University.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 37.26.168.19 |
| rDNS | h168.019.yerphi.am |
| Org | Institute for Informatics and Automation Problems, NAS Armenia |
| Country | Armenia |
| Open ports | 11434 (Ollama — **public**) |

---

## Credential Leak

```json
{
  "error": "unauthorized",
  "signin_url": "https://ollama.com/connect?name=c2a68a9aa573&key=<base64>"
}
```

- **Username:** `c2a68a9aa573` — Docker container ID
- **SSH pubkey:** `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIBqWiNKYbTt7XQxVG0OdY/61UHxsXkuGVtuS0UShBD7V`

Both cloud proxy models return 401 with the same credentials — single Ollama Connect account inside one Docker container.

---

## Models

| Model | Size | Type |
|---|---|---|
| deepseek-v4-pro:cloud | 0 GB | ☁️ Cloud proxy |
| minimax-m2.7:cloud | 0 GB | ☁️ Cloud proxy |
| llama3.2:3b | 1 GB | Local |

---

## Findings

**F1 — Docker Credential Leak (HIGH):** Container ID in Ollama Connect username.  
**F2 — Dual Cloud Proxy on Academic Research Server (HIGH):** DeepSeek and MiniMax subscriptions exposed.  
**F3 — Model Injection (CRITICAL):** All 3 models injectable via CVE-2025-63389.

---

## Pattern

Docker container hostname as Ollama username also seen at: Hanoi University (Vietnam, `04aa6fb5e0b8`), Purdue NW (US-IN, `c0ddfaef7764`). All three expose port 11434 via `docker run -p 11434:11434` which binds to 0.0.0.0.

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
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/AM/armenian-academy.md

This research is part of a broader sweep of university AI infrastructure exposures documented at:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/OVERVIEW.md

I'm happy to answer questions or assist with verification. No response is required.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
