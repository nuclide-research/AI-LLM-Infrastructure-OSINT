---
institution: University of Hertfordshire
ip: 147.197.191.230
to: security@herts.ac.uk
severity: CRITICAL
status: DRAFT
date: 2026-05-01
---

**To:** security@herts.ac.uk
**Subject:** Unauthenticated AI inference endpoint — University of Hertfordshire (147.197.191.230)

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-01

**Re:** Unauthenticated Ollama AI inference endpoint — University of Hertfordshire
**IP / Host:** 147.197.191.230
**Severity:** CRITICAL

---

I'm an independent security researcher. I hold CISA disclosures CVE-2025-4364 and ICSA-25-140-11 and conduct good-faith AI infrastructure research under the NuClide Research umbrella. This is an unsolicited disclosure — no engagement exists with your organization, and I have not accessed, modified, or exfiltrated any data beyond what was necessary to confirm the exposure.

---

## Summary

A development server at the University of Hertfordshire's RobotHouse facility (`robothouse-dev.herts.ac.uk`) is running Ollama with `gpt-oss:latest` cloud proxy returning **200 OK** without credentials — free-tier cloud quota consumed at operator expense by any internet caller. 103 tokens consumed during research confirmation.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 147.197.191.230 |
| rDNS | `robothouse-dev.herts.ac.uk` |
| Org | University of Hertfordshire |
| Facility | RobotHouse (robotics research lab) |
| Country | United Kingdom |
| Open ports | 11434 (Ollama — **public**) |

---

## Models

| Model | Size | Type | 200 OK? |
|---|---|---|---|
| gpt-oss:latest | 12 GB | ☁️ Cloud proxy | **YES — 34 tokens** |
| gemma4:latest | 8 GB | Local | — |

---

## Findings

### F1 — Free-Tier Cloud Proxy 200 OK (CRITICAL)

`gpt-oss:latest` returns full inference without authentication. 103 tokens total consumed (69 prompt + 34 output) during research confirmation:

```bash
curl -X POST http://147.197.191.230:11434/api/chat \
  -d '{"model":"gpt-oss:latest","messages":[{"role":"user","content":"say hi"}],"stream":false}'
# 200 OK - "Hi! 👋" — operator quota consumed
```

### F2 — Research Lab Dev Server (HIGH)

The `robothouse-dev.herts.ac.uk` hostname indicates this is a development/staging server in the RobotHouse robotics research facility. LLM API abuse or injection could affect robot-planning pipelines or research workflows connected to this Ollama instance.

### F3 — Model Injection (HIGH)

Both models injectable via CVE-2025-63389.

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
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/GB-hertfordshire.md

This research is part of a broader sweep of university AI infrastructure exposures documented at:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/OVERVIEW.md

I'm happy to answer questions or assist with verification. No response is required.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
