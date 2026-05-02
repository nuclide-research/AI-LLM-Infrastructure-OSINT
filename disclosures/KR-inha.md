---
institution: INHA University
ip: 165.246.39.51
to: security@inha.ac.kr
severity: HIGH
status: DRAFT
date: 2026-05-01
---

**To:** security@inha.ac.kr
**Subject:** Unauthenticated AI inference endpoint — INHA University (165.246.39.51)

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-01

**Re:** Unauthenticated Ollama AI inference endpoint — INHA University
**IP / Host:** 165.246.39.51
**Severity:** HIGH

---

I'm an independent security researcher. I hold CISA disclosures CVE-2025-4364 and ICSA-25-140-11 and conduct good-faith AI infrastructure research under the NuClide Research umbrella. This is an unsolicited disclosure — no engagement exists with your organization, and I have not accessed, modified, or exfiltrated any data beyond what was necessary to confirm the exposure.

---

## Summary

INHA University (인하대학교) in Incheon has an Ollama instance with 7 models totalling ~133GB including a local `gpt-oss:20b` (20.9B params) and two NVIDIA Nemotron-Cascade 30B models.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 165.246.39.51 |
| Organization | INHA UNIVERSITY |
| Country | South Korea |
| Open ports | 11434 (Ollama — public) |

---

## Model Inventory

| Model | Size | Notes |
|---|---|---|
| `gpt-oss:20b` | 12.1GB | Local inference, 20.9B params, `gpt-oss` family |
| `hf.co/unsloth/gpt-oss-20b-GGUF:Q8_0` | 12.1GB | Same weights, direct HF GGUF pull |
| `nemotron-cascade-2:30b` | 24.3GB | NVIDIA Nemotron Cascade 2 30B |
| `gemma4:26b-a4b-it-q8_0` | 28.1GB | Gemma 4 Q8 |
| `nemotron-3-nano:30b` | 24.3GB | NVIDIA Nemotron-3 Nano 30B |
| `qwen3.5:27b` | 22.5GB | — |
| `deepseek-r1:14b` | 9.0GB | — |

**Total local storage:** ~132GB

---

## Findings

### F1 — Local gpt-oss:20b and Dual Nemotron Stack (HIGH)

`gpt-oss:20b` is running locally (12.1GB, 20.9B params). The model family `gpt-oss` is the OpenAI open-source weights release. Both the standard Ollama-tagged version and the direct HuggingFace GGUF pull are present — suggesting the operator downloaded via `hf.co/unsloth/gpt-oss-20b-GGUF:Q8_0` first, then aliased it.

The dual `nemotron-cascade-2:30b` and `nemotron-3-nano:30b` stack (both 24.3GB) suggests NVIDIA model evaluation or research use.

### F2 — CVE-2025-63389 Injectable (HIGH)

All models injectable via unauthenticated `/api/create`. The Nemotron and gpt-oss models have no system prompts — post-injection inference is unobstructed.

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
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/KR/inha.md

This research is part of a broader sweep of university AI infrastructure exposures documented at:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/OVERVIEW.md

I'm happy to answer questions or assist with verification. No response is required.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
