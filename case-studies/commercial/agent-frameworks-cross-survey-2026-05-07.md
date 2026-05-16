---
type: survey
title: "Agent frameworks cross-survey, planning + dork catalog (2026-05-07)"
date: 2026-05-07
class: agent-framework
category: planning
status: in-progress
methodology: per-framework structural dorks + aimap conjunctive validation + per-instance escalation
---

# Agent frameworks cross-survey, planning + dorks

NuClide Research, 2026-05-07

The Langfuse cross-survey ([`langfuse-cross-survey-2026-05-06.md`](langfuse-cross-survey-2026-05-06.md)) covered the **observability layer** of the agent stack. The browser-agent cloud survey ([`browser-agent-cloud-survey-2026-05.md`](browser-agent-cloud-survey-2026-05.md)) covered the **browsing-tool layer**. This survey covers the **orchestration layer** itself — the agent framework servers that schedule LLM calls, dispatch tools, and persist agent state.

Threat-class profile: agent framework servers are increasingly exposed to the public internet by researchers and small teams who follow vendor README quickstart instructions. The default-deployment path on most of these frameworks omits authentication; their developers assume LAN-only or single-user-on-localhost contexts that don't survive the move to a cloud VM. This is the same vendor-template pattern as `vendor-template-default-no-auth-research-instruments.md`, applied to the orchestration tier.

What's at stake when an agent framework is exposed unauth:

| Capability | Impact |
|---|---|
| Agent invocation | Attacker can run agents on the operator's API quota — LLMjacking class. Equivalent to PromptLayer 34.95.65.63 webhook abuse pattern, scaled to full agent pipelines. |
| Tool execution | Many agent frameworks have a code-interpreter / shell tool wired up. Unauth invocation = RCE on the host. |
| State / memory inspection | Conversation history, system prompts, tool outputs, vector store contents — full data exfiltration. Matches Langfuse cross-survey impact. |
| Configuration tampering | Adding new agents, modifying system prompts, redirecting webhooks. Persistence beats single-session exfil. |

## Coverage map (existing vs gap)

| Layer | Already in aimap | Already surveyed | Gap |
|---|---|---|---|
| Observability | Langfuse, LangSmith Self-Hosted, Promptfoo, Inspect AI, Garak REST | Langfuse 2026-05-06 | Phoenix Arize |
| Agent UI / no-code | Flowise, Dify, OpenHands | (partial in OpenHands) | (none) |
| Memory / state | Mem0 | (none) | Letta (MemGPT), Zep |
| Browsing tools | Clawdbot | browser-agent cloud 2026-05 | Browserbase, Steel.dev |
| Guardrails | NeMo Guardrails, Lakera Guard | (none) | Guardrails AI server |
| Eval | Promptfoo, Inspect AI, Garak | (none) | DeepEval Server |
| **Orchestration core** | **(GAP)** | **(GAP)** | **AutoGen Studio, LangGraph Server, AutoGPT, SuperAGI, CrewAI Studio, Agno Playground, Open Interpreter, Haystack agents, Portkey, Helicone** |

The "orchestration core" row is the focus of this survey. These are the frameworks that own the agent-invocation primitive itself — RCE-class impact when unauth.

## Per-framework structural dorks

Each dork is constructed from the framework's distinctive HTTP fingerprint: a unique HTML title, a unique JSON path, a unique OpenAPI-spec marker, or a unique header. Substring-only matchers (Methodology Insight #6 violations) are avoided in favour of conjunctive matchers wherever possible.

### Framework 1, AutoGen Studio (Microsoft)

Default deployment: `autogenstudio ui --port 8081`. FastAPI backend with React frontend, no auth in default config.

```
http.title:"AutoGen Studio" port:8081
http.html:"autogenstudio" "/api/sessions"
http.html:"AutoGen Studio" port:8081
```

Distinctive fingerprint:
- `<title>AutoGen Studio</title>` in HTML
- `/api/sessions` endpoint returns JSON with `{"data": [{"id": ..., "name": ...}]}`
- `/static/` path serves Vite-bundled React app
- OpenAPI doc at `/docs`

Confirmation probe: `curl -s http://<ip>:8081/api/sessions` returns 200 JSON with session list when unauth.

### Framework 2, Letta (formerly MemGPT)

Default deployment: `letta server` on port 8283. FastAPI server with optional ADE frontend on a separate port.

```
http.title:"Letta" port:8283
http.html:"/v1/agents" "letta"
"letta_server"
```

Distinctive fingerprint:
- `/v1/health` returns `{"version": "<semver>", "status": "ok"}`
- `/v1/agents` lists all agents
- `/v1/sources` lists knowledge sources
- ADE frontend has `<title>Letta ADE</title>` and serves on :3000 by default in Docker compose

Confirmation probe: `curl -s http://<ip>:8283/v1/health` → JSON; `curl -s http://<ip>:8283/v1/agents` returns full agent list when unauth.

### Framework 3, LangGraph Server (langgraph-cli)

Default deployment: `langgraph dev` on port 2024 (newer) or `langgraph up` on 8123. Runs an FastAPI server hosting LangGraph applications.

```
http.title:"LangGraph" port:2024
http.html:"/assistants" "/threads"
"langgraph_runtime"
```

Distinctive fingerprint:
- `/info` returns `{"version": "<semver>", "flags": {...}}`
- `/assistants` POST creates an assistant (no auth in dev mode)
- `/threads` creates persistent agent state
- `/runs` triggers agent invocation
- `/docs` Swagger UI

Confirmation probe: `curl -s http://<ip>:2024/info` returns version JSON.

### Framework 4, AutoGPT (Forge / Server mode)

Default deployment: AutoGPT server runs on port 8000 with FastAPI backend, optional Web UI on port 3000.

```
http.title:"AutoGPT"
http.html:"AutoGPT Forge"
"/api/v1/agents" "/api/v1/tasks"
```

Distinctive fingerprint:
- `<title>AutoGPT</title>` or `<title>AutoGPT Forge</title>`
- `/api/v1/agents` lists agents
- `/api/v1/tasks` shows task queue
- `/docs` Swagger
- Newer "AutoGPT Platform" version uses :8000/api and :3000 frontend

### Framework 5, SuperAGI

Default deployment: Docker compose, FastAPI backend on :8001, Next.js frontend on :3000.

```
http.title:"SuperAGI"
http.html:"superagi" "/api/agents"
port:8001 "superagi"
```

Distinctive fingerprint:
- `<title>SuperAGI</title>`
- `/api/agents` endpoint
- `/health` returns SuperAGI version
- Frontend is Next.js with distinctive `_next/static/` paths

### Framework 6, CrewAI Studio (strnad fork — most common)

Default deployment: Streamlit on port 8501. CrewAI itself is a library; the Studio is a community UI for it.

```
http.title:"CrewAI Studio"
http.html:"CrewAI" "streamlit"
http.html:"/_stcore/" "CrewAI"
```

Distinctive fingerprint:
- `<title>CrewAI Studio</title>` or similar
- Streamlit-specific paths: `/_stcore/static/`, `/_stcore/health`
- Streamlit favicon hash matches the Streamlit-default fingerprint

Confirmation probe: `/_stcore/health` returns Streamlit health JSON.

### Framework 7, Agno Playground (formerly Phidata)

Default deployment: `agno playground` runs on :7777, FastAPI backend with optional UI.

```
http.title:"Agno Playground"
http.html:"agno" "/v1/playground/agents"
port:7777 "playground"
```

Distinctive fingerprint:
- `/v1/playground/agents` endpoint
- `/v1/playground/teams` endpoint (multi-agent teams)
- `/v1/playground/workflows`
- HTML title varies; backend OpenAPI at `/docs` is more reliable

### Framework 8, Open Interpreter --server

Default deployment: `interpreter --server` on port 8000 (FastAPI) — runs the OS-level code interpreter remotely. **Highest impact: this IS RCE when exposed unauth.**

```
http.title:"Open Interpreter"
http.html:"open-interpreter" "/openai/chat/completions"
"open_interpreter" port:8000
```

Distinctive fingerprint:
- `/openai/chat/completions` OpenAI-compat endpoint
- Function-calling tool list includes `run_shell` and `execute_python`
- `/docs` Swagger lists `interpreter` namespace

Critical: this framework's design intent is single-user localhost. Public-internet exposure equals direct shell access to the host's OS.

### Framework 9, Haystack agents (Deepset)

Default deployment: Haystack 2.x has a REST API mode that runs FastAPI on :8000 with `/v1/pipelines` and `/v1/agents`.

```
http.title:"Haystack"
http.html:"haystack" "/v1/pipelines"
"haystack-api"
```

Distinctive fingerprint:
- `/v1/pipelines` endpoint
- `/v1/agents` endpoint (Haystack 2.0 introduces agent class)
- `/health` returns Haystack version

### Framework 10, Phoenix Arize (observability)

Default deployment: `phoenix.launch_app()` runs on :6006 (TensorBoard convention).

```
http.title:"Phoenix"
http.html:"arize-phoenix" "/v1/traces"
port:6006 "phoenix"
```

Distinctive fingerprint:
- `<title>Phoenix</title>`
- `/v1/traces` OTLP endpoint
- `/graphql` for project metadata
- Heavy LLM trace data leak when exposed (rivals Langfuse impact)

## Conjunctive validation requirements

Per Methodology Insight #6, single-keyword dorks have unacceptable false-positive rates. Each dork above couples at least one structural marker (path or port) with at least one content marker (title or banner string). aimap conjunctive validation per the existing pattern still required after the Shodan harvest:

```
aimap -target <ip:port> -timeout 10s -enumerate
```

The deep enumerator should be added to aimap for each framework (current gap). Until then, classify each hit manually using the confirmation probes above.

## Probe + validate workflow

When IPs come back from Shodan:

1. `jaxen import --no-lookup <ips>` — ingest into the ledger.
2. Seed `/tmp/shodan-agent-frameworks-cross-2026-05-07-hits.txt`.
3. `bash data/visor-chain-runner.sh agent-frameworks-cross-2026-05-07` — full 11-step chain.
4. Per-framework triage:
   - Auth on, version-current → no finding
   - Auth on, version-stale (CVE class) → version-currency disclosure
   - **Auth off, agents listable** → unauth exposure disclosure
   - **Auth off, code-interpreter tool present** → RCE-class disclosure (CRITICAL)
   - **Auth off, conversation data readable** → data-exfiltration disclosure (HIGH)

## Disclosure routing

Same vendor + operator parallel disclosure pattern as the Cortical Labs flow:

- Vendor security contact (security@<vendor>) — fleet-wide remediation framing
- Operator's CERT / abuse contact — per-instance notification
- For RCE-class findings: pre-empt the disclosure with a "stop the host" recommendation, then full report

## See also

- [langfuse-cross-survey-2026-05-06](langfuse-cross-survey-2026-05-06.md) — observability layer prior survey
- [browser-agent-cloud-survey-2026-05](browser-agent-cloud-survey-2026-05.md) — browsing-tool layer prior survey
- [vendor-template-default-no-auth-research-instruments](vendor-template-default-no-auth-research-instruments.md) — vendor-template threat-class study
- [Methodology Insight #6](../../methodology/insight-06-conjunctive-matchers-required.md) — conjunctive matchers required
- [Methodology Insight #10](../../methodology/insight-10-vendor-template-default-no-auth.md) — vendor-template default-no-auth pattern

## Status

This is the planning doc. No probes have been run yet. Updates expected:

- 2026-05-XX: results from Framework 1 (AutoGen Studio sweep)
- 2026-05-XX: results from Framework 8 (Open Interpreter sweep — highest-impact)
- 2026-05-XX: aimap deep-enumerator additions for any framework surfaced

When findings come in, this doc gets per-framework follow-on case studies under `case-studies/commercial/agent-framework-<name>-*.md`.
