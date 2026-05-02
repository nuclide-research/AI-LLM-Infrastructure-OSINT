---
institution: Hanoi University
ip: 103.185.232.21
to: security@hanu.edu.vn
severity: CRITICAL
status: DRAFT
date: 2026-05-01
---

**To:** security@hanu.edu.vn
**Subject:** Unauthenticated AI inference endpoint — Hanoi University (103.185.232.21)

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-01

**Re:** Unauthenticated Ollama AI inference endpoint — Hanoi University
**IP / Host:** 103.185.232.21
**Severity:** CRITICAL

---

I'm an independent security researcher. I hold CISA disclosures CVE-2025-4364 and ICSA-25-140-11 and conduct good-faith AI infrastructure research under the NuClide Research umbrella. This is an unsolicited disclosure — no engagement exists with your organization, and I have not accessed, modified, or exfiltrated any data beyond what was necessary to confirm the exposure.

---

## Summary

Hanoi University (Vietnam) running a 31-model Ollama instance with 18 active cloud proxy subscriptions. Cloud proxy 401 response leaks Ollama Connect credentials — **username `04aa6fb5e0b8` is a Docker container ID**, confirming Ollama runs inside a container with no network isolation. Raw Ollama port publicly accessible.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 103.185.232.21 |
| Org | Hanoi University |
| Country | Vietnam |
| Open ports | 11434 (Ollama — **public**) |

---

## Credential Leak

```json
{
  "error": "unauthorized",
  "signin_url": "https://ollama.com/connect?name=04aa6fb5e0b8&key=<base64>"
}
```

- **Username:** `04aa6fb5e0b8` — **Docker container ID** (the container's hostname, which Ollama uses as the account name)
- **SSH pubkey:** `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAILi5RXxQeIXNUjDJJl2W54szLU6Y5IQI4IulfxbWaK14`

The container hostname as Ollama username reveals the operator registered Ollama Connect from inside a Docker container. This means port 11434 was published from the container to the host, then left accessible externally — a common misunderstanding of Docker's default `0.0.0.0` binding behavior.

---

## Cloud Proxies (18)

Same ecosystem as POSTECH and Shiv Nadar: DeepSeek (v4-pro, v4-flash, v3.2), MiniMax (m2.7, m2.5, m2.1, m2), Kimi (k2.6, k2.5, k2-thinking), GLM (5.1, 5, 4.7, 4.6), Qwen (3.5, coder-next), Nemotron, Gemini.

---

## Findings

### F1 — 18 Cloud Proxy Subscriptions Exposed (CRITICAL)

All 18 cloud proxies accessible via unauthenticated port 11434.

### F2 — Credential Leak via Containerized Deployment (HIGH)

Docker container ID exposed as Ollama Connect username. Any actor probing port 11434 receives the container's SSH public key, confirming containerized deployment and extracting credentials.

### F3 — Docker Port Publishing Misunderstanding (HIGH)

Ollama published via Docker `-p 11434:11434` defaults to `0.0.0.0` binding. The operator likely assumed this was internal-only. All 31 models + 18 cloud proxies are exposed as a result.

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
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/VN/hanoi.md

This research is part of a broader sweep of university AI infrastructure exposures documented at:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/OVERVIEW.md

I'm happy to answer questions or assist with verification. No response is required.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
