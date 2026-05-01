---
institution: University of Manitoba
ip: 130.179.30.15
to: security@umanitoba.ca
severity: HIGH
status: DRAFT
date: 2026-05-01
---

**To:** security@umanitoba.ca
**Subject:** Unauthenticated AI inference endpoint — University of Manitoba (130.179.30.15)

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-01

**Re:** Unauthenticated Ollama AI inference endpoint — University of Manitoba
**IP / Host:** 130.179.30.15
**Severity:** HIGH

---

I'm an independent security researcher. I hold CISA disclosures CVE-2025-4364 and ICSA-25-140-11 and conduct good-faith AI infrastructure research under the NuClide Research umbrella. This is an unsolicited disclosure — no engagement exists with your organization, and I have not accessed, modified, or exfiltrated any data beyond what was necessary to confirm the exposure.

---

## Summary

The Computer Science department at the University of Manitoba (`quail.cs.umanitoba.ca`) is running Ollama with five large local models including DeepSeek-R1:70B, Llama 3.3, and Llama 3:70B — a deep research stack totaling ~156GB of local models, all accessible without authentication.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 130.179.30.15 |
| rDNS | `quail.cs.umanitoba.ca` |
| Org | University of Manitoba |
| Department | Computer Science |
| Country | Canada — Manitoba |
| Open ports | 11434 (Ollama — **public**) |

---

## Models

| Model | Size |
|---|---|
| llama3.3:latest | 39 GB |
| llama3:70b | 37 GB |
| deepseek-r1:70b | 39 GB |
| qwen2.5-coder:32b | 18 GB |
| smollm2:135m | 0 GB |

Total local compute: ~133 GB across 5 models.

---

## Findings

**F1 — Unauthenticated CS Research Server (HIGH):** Named GPU server in CS department. Research models (DeepSeek-R1, large Llama) and code model (Qwen2.5-Coder) exposed to the public internet.

**F2 — Model Injection (HIGH):** All 5 models injectable via CVE-2025-63389 — attacker can overwrite system prompts, affecting any research workflows using this Ollama instance.

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
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/CA-MB-u-manitoba.md

This research is part of a broader sweep of university AI infrastructure exposures documented at:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/OVERVIEW.md

I'm happy to answer questions or assist with verification. No response is required.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
