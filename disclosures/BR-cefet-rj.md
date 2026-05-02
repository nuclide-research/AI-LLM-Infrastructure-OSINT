---
institution: CEFET/RJ
ip: 200.9.149.153
to: dtinf@cefet-rj.br
severity: HIGH
status: DRAFT
date: 2026-05-01
---

**To:** dtinf@cefet-rj.br
**Subject:** Unauthenticated AI inference endpoint — CEFET/RJ (200.9.149.153)

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-01

**Re:** Unauthenticated Ollama AI inference endpoint — CEFET/RJ
**IP / Host:** 200.9.149.153
**Severity:** HIGH

---

I'm an independent security researcher. I hold CISA disclosures CVE-2025-4364 and ICSA-25-140-11 and conduct good-faith AI infrastructure research under the NuClide Research umbrella. This is an unsolicited disclosure — no engagement exists with your organization, and I have not accessed, modified, or exfiltrated any data beyond what was necessary to confirm the exposure.

---

## Summary

Brazil's CEFET/RJ (Federal Center for Technological Education Celso Suckow da Fonseca) has an Ollama instance with 17 models, including custom Brazilian Portuguese fine-tunes and a 39GB DeepSeek-R1:70B local model. No authentication. Heavy emphasis on Portuguese-language AI research/coursework.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 200.9.149.153 |
| Organization | Centro Federal de Educação Tecnológica Celso Suckow da Fonseca (CEFET/RJ) |
| Country | Brazil |
| Open ports | 11434 (Ollama — public) |

---

## Model Inventory (17 models)

| Model | Size | Notes |
|---|---|---|
| `deepseek-r1:70b` | 39GB | Local DeepSeek-R1 70B |
| `RecognaNLP/chatbode:7b` | 14GB | **Brazilian Portuguese chatbot** (RecognaNLP, USP/UFSCar lab) |
| `cnmoro/mistral_7b_portuguese:q2_K` | 2GB | Portuguese-fine-tuned Mistral |
| `lukashabtoch/plutotext-r3-emotional:latest` | 4GB | Custom: "emotional text" model |
| `lukashabtoch/moirai-agent:latest` | 1GB | Custom: agent model (likely student project) |
| `mattw/pygmalion:latest` | 3GB | Pygmalion (roleplay/chat model) |
| `mario:latest` | 1GB | Custom small model |
| `gemma:7b` | 4GB | — |
| `mistral:7b` | 4GB | — |
| `llama3.2:3b-instruct-q5_K_M` | 2GB | — |
| `llama3.1:latest` | 4GB | — |
| `llama2:latest` | 3GB | — |
| `llama3-backup:latest` | 1GB | — |
| `llama3.2:latest` | 1GB | — |
| `tinyllama:latest` | — | — |
| `smollm2:135m` | — | — |
| `deepseek-r1:latest` | 4GB | — |

---

## Findings

### F1 — Unauthenticated Inference Across 17 Models (HIGH)

All 17 models accessible without authentication. The 39GB DeepSeek-R1:70B requires significant GPU resources — free inference at CEFET/RJ's compute expense.

### F2 — Custom Brazilian Portuguese AI Models Exposed (HIGH)

Three custom-namespace models indicate either student/faculty research projects or coursework deployments:
- `lukashabtoch/moirai-agent` — likely a student's "Moirai" agent project
- `lukashabtoch/plutotext-r3-emotional` — emotional text model (R3 = release 3)
- `mario:latest` — unnamed researcher's model

CVE-2025-63389 injection on these custom models would silently affect any student/researcher relying on their outputs.

The `RecognaNLP/chatbode:7b` model is the public Brazilian Portuguese ChatBode (from USP/UFSCar's RecognaNLP group) — its system prompt confirms instructional/conversational use:

> "Você é assistente de IA chamado ChatBode... projetado para ser prestativo, honesto e inofensivo."

### F3 — Pygmalion Roleplay Model Present (MEDIUM)

`mattw/pygmalion:latest` is a roleplay/character-chat model — unusual deployment on a federal educational institution server.

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
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/BR-cefet-rj.md

This research is part of a broader sweep of university AI infrastructure exposures documented at:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/OVERVIEW.md

I'm happy to answer questions or assist with verification. No response is required.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
