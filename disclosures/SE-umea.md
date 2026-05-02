---
institution: Umeå University
ip: 130.239.40.121
to: abuse@umu.se
severity: HIGH
status: DRAFT
date: 2026-05-01
---

**To:** abuse@umu.se
**Subject:** Unauthenticated AI inference endpoint — Umeå University (130.239.40.121)

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-01

**Re:** Unauthenticated Ollama AI inference endpoint — Umeå University
**IP / Host:** 130.239.40.121
**Severity:** HIGH

---

I'm an independent security researcher. I hold CISA disclosures CVE-2025-4364 and ICSA-25-140-11 and conduct good-faith AI infrastructure research under the NuClide Research umbrella. This is an unsolicited disclosure — no engagement exists with your organization, and I have not accessed, modified, or exfiltrated any data beyond what was necessary to confirm the exposure.

---

## Summary

Umeå University (Sweden) has a named GPU compute server (`gpuhost02.cs.umu.se`) running Ollama with a large reasoning model (qwen3.6:35b) publicly accessible without authentication. Part of the Computer Science department compute cluster.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 130.239.40.121 |
| rDNS | `gpuhost02.cs.umu.se` |
| Org | Umeå University |
| Department | Computer Science |
| Country | Sweden |
| Open ports | 11434 (Ollama — **public**) |

---

## Models

| Model | Size |
|---|---|
| qwen3.6:35b | 22 GB |
| smollm2:135m | 0 GB |
| llama3.2:3b | 1 GB |

---

## Findings

**F1 — Unauthenticated GPU Research Server (HIGH):** Named GPU host #2 in CS compute cluster. All models injectable via CVE-2025-63389.

---

**Why it matters**

Any internet actor can run uncapped inference against your GPU at your compute cost, and inject malicious system prompts into any loaded model via CVE-2025-63389.

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
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/SE/umea.md

This research is part of a broader sweep of university AI infrastructure exposures documented at:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/OVERVIEW.md

I'm happy to answer questions or assist with verification. No response is required.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
