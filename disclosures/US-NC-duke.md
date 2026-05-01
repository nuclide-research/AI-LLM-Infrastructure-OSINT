---
institution: Duke University
ip: 152.3.41.179
to: security@duke.edu
severity: CRITICAL
status: DRAFT
date: 2026-05-01
---

**To:** security@duke.edu
**Subject:** Unauthenticated AI inference endpoint — Duke University (152.3.41.179)

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-01

**Re:** Unauthenticated Ollama AI inference endpoint — Duke University
**IP / Host:** 152.3.41.179
**Severity:** CRITICAL

---

I'm an independent security researcher. I hold CISA disclosures CVE-2025-4364 and ICSA-25-140-11 and conduct good-faith AI infrastructure research under the NuClide Research umbrella. This is an unsolicited disclosure — no engagement exists with your organization, and I have not accessed, modified, or exfiltrated any data beyond what was necessary to confirm the exposure.

---

## Summary

Duke University server running Ollama with two agent-configured variants of Qwen 3.6-27B, both with system prompts instructing file-inspection behavior and native function-calling enabled. Raw Ollama port publicly accessible. Model injection via CVE-2025-63389 would silently redirect agent behavior on next workflow invocation.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 152.3.41.179 |
| Org | Duke University |
| Country | US — North Carolina |
| OS | Linux (`/usr/share/ollama/` path) |
| Open ports | 11434 (Ollama — **public**) |

---

## Models

| Model | Size | Notes |
|---|---|---|
| qwen3.6-27b-agent:latest | 16 GB | **Agent — file inspection tools** |
| qwen3.6-27b-agent-128k:latest | 16 GB | **Agent — 128K context, file inspection tools** |
| qwen3.6:27b | 16 GB | Base model |
| hermes3:8b | 4 GB | Local |

---

## Agent Configuration

Both agent models share this system prompt:

```
You are a careful local workflow agent. Prefer using available tools to inspect
files rather than guessing.
Do not overwrite files unless explicitly asked.
```

Modelfile parameters (optimized for deterministic agentic output):
```
RENDERER qwen3.5
PARSER qwen3.5
PARAMETER num_ctx 65536        # 64K context for large file reads
PARAMETER temperature 0.2      # low temperature = consistent tool calls
PARAMETER presence_penalty 1.5
PARAMETER top_k 20
PARAMETER top_p 0.8
```

`RENDERER` and `PARSER` directives enable Ollama's native tool/function-calling. This model is built to generate structured tool-call outputs that an orchestrating framework then executes.

---

## Findings

### F1 — Unauthenticated Agent Model Injection (CRITICAL)

Any actor can overwrite the agent system prompt via CVE-2025-63389:

```bash
curl -X POST http://152.3.41.179:11434/api/create \
  -d '{
    "model": "qwen3.6-27b-agent:latest",
    "from": "qwen3.6-27b-agent:latest",
    "system": "[attacker-controlled instructions]"
  }'
```

Next time the operator's workflow invokes this model, it runs under the injected system prompt. If the workflow executes tool calls emitted by the model (file read, shell, API calls), the injected prompt controls what tools are called and with what arguments.

### F2 — 128K Context Agent as Exfiltration Vector (HIGH)

The 128K context variant is optimized for processing large files. An attacker-controlled system prompt could instruct the agent to include file contents in its responses — readable by any actor watching the orchestration layer.

---

## Chain

```
CVE-2025-63389 model injection (port 11434, no auth)
  → operator's workflow runs agent under attacker prompt
  → model emits attacker-directed tool calls
  → framework executes: file_read, shell, API → operator's filesystem/environment
```

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
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/US-NC-duke.md

This research is part of a broader sweep of university AI infrastructure exposures documented at:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/OVERVIEW.md

I'm happy to answer questions or assist with verification. No response is required.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
