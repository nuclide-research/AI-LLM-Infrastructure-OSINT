---
institution: UC Davis
ip: 128.120.246.177
to: cybersecurity@ucdavis.edu
severity: HIGH
status: DRAFT
date: 2026-05-01
---

**To:** cybersecurity@ucdavis.edu
**Subject:** Unauthenticated AI inference endpoint — UC Davis (128.120.246.177)

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-01

**Re:** Unauthenticated Ollama AI inference endpoint — UC Davis
**IP / Host:** 128.120.246.177
**Severity:** HIGH

---

I'm an independent security researcher. I hold CISA disclosures CVE-2025-4364 and ICSA-25-140-11 and conduct good-faith AI infrastructure research under the NuClide Research umbrella. This is an unsolicited disclosure — no engagement exists with your organization, and I have not accessed, modified, or exfiltrated any data beyond what was necessary to confirm the exposure.

---

## Summary

University of California, Davis has an Ollama instance with `Qwen3-Coder-Next` (48GB), `qwen3.5:122b-a10b` (75GB), and — notably — `moophlo/Qwen3.5-27B-Claude-4.6-Opus-Reasoning-Distilled-GGUF:latest`, a model distilled from Claude 4.6 Opus, all accessible without authentication.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 128.120.246.177 |
| rDNS | — |
| Org | University of California, Davis |
| Country | US — California |
| Open ports | 11434 (Ollama — **public**) |

---

## Models

| Model | Size | Notes |
|---|---|---|
| Qwen3-Coder-Next:latest | 48 GB | Large code model |
| qwen3.5:122b-a10b | 75 GB | 122B MoE reasoning |
| moophlo/Qwen3.5-27B-Claude-4.6-Opus-Reasoning-Distilled-GGUF:latest | 15 GB | **Claude 4.6 Opus knowledge distillation** |
| qwen3.5:latest | 6 GB | Local |

---

## Findings

**F1 — Claude-Distilled Model Exposed (HIGH):** `Qwen3.5-27B-Claude-4.6-Opus-Reasoning-Distilled` is a model trained on Claude 4.6 Opus outputs. Accessible to any internet caller — this represents a research artifact with embedded Anthropic model behaviors.

**F2 — 75GB MoE Model Accessible (HIGH):** `qwen3.5:122b-a10b` (75GB) is a large mixture-of-experts reasoning model. Significant compute resource exposed.

**F3 — Model Injection (HIGH):** All 4 models injectable via CVE-2025-63389.

---

**Why it matters**

An embedding model indicates an active RAG pipeline — documents loaded into your vector store are reachable via unauthenticated queries.

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
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/US-CA-ucdavis.md

This research is part of a broader sweep of university AI infrastructure exposures documented at:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/OVERVIEW.md

I'm happy to answer questions or assist with verification. No response is required.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
