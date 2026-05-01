---
institution: Chulalongkorn University
ip: 161.200.94.244
to: security@chula.ac.th
severity: CRITICAL
status: DRAFT
date: 2026-05-01
---

**To:** security@chula.ac.th
**Subject:** Unauthenticated AI inference endpoint — Chulalongkorn University (161.200.94.244)

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-01

**Re:** Unauthenticated Ollama AI inference endpoint — Chulalongkorn University
**IP / Host:** 161.200.94.244
**Severity:** CRITICAL

---

I'm an independent security researcher. I hold CISA disclosures CVE-2025-4364 and ICSA-25-140-11 and conduct good-faith AI infrastructure research under the NuClide Research umbrella. This is an unsolicited disclosure — no engagement exists with your organization, and I have not accessed, modified, or exfiltrated any data beyond what was necessary to confirm the exposure.

---

## Summary

Chulalongkorn University (Thailand, ranked ~1 in Southeast Asia) server with 12 Ollama models including three cloud proxy subscriptions: DeepSeek v4 Pro, Kimi K2.6 (Moonshot AI), and Qwen3-Coder-Next. All three 401 responses leak the same Ollama Connect credentials. Raw Ollama port publicly accessible, no authentication.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 161.200.94.244 |
| Org | Chulalongkorn University |
| Country | Thailand |
| Open ports | 11434 (Ollama — **public**) |

---

## Cloud Proxies + Credential Leak

All three cloud proxy models return 401 with the same credentials:

```json
{
  "error": "unauthorized",
  "signin_url": "https://ollama.com/connect?name=llm&key=<base64>"
}
```

- **Username:** `llm` (generic service account)
- **SSH pubkey:** `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIF62M2w3KpDWb90LH8DRhehBjI8Up5i3scd349g6OUdH`

| Cloud Proxy | Provider | Status |
|-------------|----------|--------|
| deepseek-v4-pro:cloud | DeepSeek API | 401 + cred leak |
| kimi-k2.6:cloud | Moonshot AI (Kimi) | 401 + cred leak |
| qwen3-coder-next:cloud | Alibaba Qwen | 401 + cred leak |

`kimi-k2.6` is Moonshot AI's frontier model. All three subscriptions share one Ollama Connect account (`llm`).

---

## Findings

### F1 — Unauthenticated Ollama API (CRITICAL)

Port 11434 publicly accessible. 12 models enumerable and injectable without credentials.

### F2 — Credential Leak via Cloud Proxy (HIGH)

Same Ollama Connect credentials leaked on all three cloud proxy 401 responses. Any actor probing port 11434 receives the operator's SSH public key and username.

### F3 — Model Injection (CRITICAL)

CVE-2025-63389 applies. All 12 models injectable. If used for student/research workflows, injection redirects outputs under attacker-controlled system prompts.

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
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/TH-Chulalongkorn.md

This research is part of a broader sweep of university AI infrastructure exposures documented at:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/OVERVIEW.md

I'm happy to answer questions or assist with verification. No response is required.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
