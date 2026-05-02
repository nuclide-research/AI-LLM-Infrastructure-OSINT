---
institution: Brno University of Technology
ip: 147.229.83.12
to: cert@vut.cz
cc: abuse@cesnet.cz
severity: HIGH
status: DRAFT
date: 2026-05-01
---

**To:** cert@vut.cz
**Cc:** abuse@cesnet.cz
**Subject:** Unauthenticated AI inference endpoint — Brno University of Technology (147.229.83.12)

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-01

**Re:** Unauthenticated Ollama AI inference endpoint — Brno University of Technology
**IP / Host:** 147.229.83.12
**Severity:** HIGH

---

I'm an independent security researcher. I hold CISA disclosures CVE-2025-4364 and ICSA-25-140-11 and conduct good-faith AI infrastructure research under the NuClide Research umbrella. This is an unsolicited disclosure — no engagement exists with your organization, and I have not accessed, modified, or exfiltrated any data beyond what was necessary to confirm the exposure.

---

## Summary

Brno University of Technology (VUT Brno), Czech Republic, is running Ollama on a Faculty of Mechanical Engineering server with an abliterated Gemma 3 model (safety fine-tuning removed), two variants of a Bulgarian-language GPT model, and an embedding model indicating an active RAG pipeline. All models are unauthenticated and injectable.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 147.229.83.12 |
| rDNS | `pelton.ofivk.fme.vutbr.cz` |
| Org | Brno University of Technology |
| Faculty | Mechanical Engineering (fme.vutbr.cz) |
| Country | Czech Republic |
| Open ports | 11434 (Ollama — **public**) |

---

## Models

| Model | Size | Notes |
|---|---|---|
| seamon67/Gemma3-Abliterated:27b-q4_K_M | 16 GB | **Abliterated — safety removed** |
| ukjin/Qwen3-30B-A3B-Thinking-2507-Deepseek-v3.1-Distill:latest | 17 GB | Distilled reasoning |
| qwen3:30b | 17 GB | Local |
| todorov/bggpt:v0.2 | 4 GB | **Bulgarian language GPT** |
| todorov/bggpt:Gemma-3-4B-IT-Q4_K_M | 2 GB | **Bulgarian language GPT (Gemma base)** |
| nomic-embed-text:latest | 0 GB | **Embedding — RAG pipeline** |
| smollm2:1.7b | 1 GB | Local |
| smollm2:135m | 0 GB | Local |

---

## Findings

**F1 — Abliterated Gemma 3 27B (HIGH):** `seamon67/Gemma3-Abliterated` has safety fine-tuning removed. Accessible to any unauthenticated internet caller on a university research server.

**F2 — RAG Pipeline Injection Surface (HIGH):** `nomic-embed-text` embedding model confirms an active RAG pipeline. CVE-2025-63389 injection affects document-augmented responses.

**F3 — Bulgarian Language Models (MEDIUM):** `todorov/bggpt` is a Bulgarian-language GPT — suggests international research collaboration or researcher with Bulgarian connections. Both variants are publicly accessible.

**F4 — Unauthenticated Ollama API (HIGH):** All 8 models injectable via CVE-2025-63389.

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
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/CZ-brno-vutbr.md

This research is part of a broader sweep of university AI infrastructure exposures documented at:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/OVERVIEW.md

I'm happy to answer questions or assist with verification. No response is required.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
