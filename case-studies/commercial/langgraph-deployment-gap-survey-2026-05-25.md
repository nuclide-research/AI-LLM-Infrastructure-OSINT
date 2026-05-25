---
type: survey
title: "LangGraph's Deployment Gap: Exposed AI Agent Infrastructure at Scale"
date: 2026-05-25
tags: [LangGraph, agent-framework, survey, auth-on-default, fingerprinting, Redis, Langfuse]
summary: "LangGraph's self-hosted deployment path ships with no authentication. We found sixteen internet-facing deployments. All sixteen were open. A financial AI system processing credit reports in Shanghai. A two-node PII scraper running in Paris with no auth by design."
---

# LangGraph's Deployment Gap: Exposed AI Agent Infrastructure at Scale

_NuClide Research · May 2026_

---

LangGraph's self-hosted deployment path ships with no authentication. Run `langgraph up`. The server starts. Agents initialize. Every endpoint responds. Nothing in that sequence tells you the configuration is not ready for production.

We ran a Shodan sweep. We found sixteen deployments. All sixteen were unauthenticated at the LangGraph layer.

---

## What We Found

Each host followed the same layout: LangGraph agent endpoints open, supporting services open beside them.

| Service | Role | Auth |
|---|---|---|
| LangGraph Server | Agent API: workflows, threads, state | None |
| Redis Commander | Session store browser UI | None |
| Langfuse | LLM trace logging | Signup open |
| RAGFlow | Document intelligence, knowledge base | Varies |
| MinIO | Object storage | Varies |

The operators ran different things on top of this. A financial system in Shanghai processing personal credit reports and loan applications. A SharePoint assistant in Poland holding active Microsoft tenant credentials. Two coaching platforms where anyone with a thread ID could read every conversation. A two-node production scraper built to extract contact PII from business directories.

Different operators, different use cases, same missing auth layer.

---

## How It Happens

LangGraph Cloud manages auth for you. The self-hosted path does not.

A developer runs `langgraph up` locally. It works. They push the same configuration to a cloud VM. Then they add Redis Commander to inspect session state, Langfuse to watch LLM calls, MinIO for file storage. Each tool ships with no auth by default. Each one opens another port. Five services end up internet-facing. None of them asked for a password.

Django throws a warning in the terminal when `DEBUG=True` handles real traffic. Flask labels its dev server "not for production use" on every startup line. LangGraph has no equivalent signal. The development configuration and the production configuration are the same configuration.

---

## Finding It

Every LangGraph Server deployment returns a JSON object at the root path. The message field names the service. Every operator customizes the text, but "LangGraph" appears in all of it.

```
GET /
→ {"message": "LangGraph多智能体系统 - LangGraph 对话工作流服务", ...}
→ {"message": "Docu Companion LangGraph API", "version": "3.0.0"}
→ {"status": "ok", "bot": "modengy_v3", "engine": "LangGraph"}
→ {"service": "standalone-langgraph-server", "version": "1.0.0"}
```

Shodan dork:

```
server: uvicorn  http.html: "LangGraph"
```

That catches 15 of the 16 hosts we found. The `x-trace-id` response header is a secondary signal and only appears on LangChain's own infrastructure. Community deployments do not set it.

The `/health` endpoint returns `redis_connected: true`. A live session store. State recoverable. The graph metadata endpoints name the workflows: their node structure, their field labels. On a credit report system, those labels name the data.

---

## What Opens Up

**LangGraph itself.** Thread history for any thread ID. Full workflow state. Graph definitions including node names and field labels tied to PII categories. The API responds with no credentials.

**Redis Commander.** A browser-based Redis UI. The root path loads a 30KB interface with no login prompt. Redis holds everything: thread IDs, conversation state, intermediate workflow outputs. Any PII that passed through the agent between LLM calls. Read/write, no credentials.

**Langfuse.** Open registration means any account reads every trace. The full prompt. The model's response. Token counts, latency, structured metadata.

**SharePoint-connected agents.** The webhook registration list is readable. The chat endpoint is open. Even after OAuth tokens expire, the Microsoft tenant ID surfaces in the error body. One host returned tenant ID `5b72381b-179a-4941-a3f8-c22cc66c3adf` in a 401 response. That ID survives credential rotation.

---

## Shanghai: Credit Reports in a Dev Environment

`1.15.66.80` is a Tencent Cloud host in Shanghai. The LangGraph instance at port 8000 returns this at the root:

```json
{
  "message": "LangGraph多智能体系统 - LangGraph 对话工作流服务",
  "service_type": "langgraph_workflow_service",
  "version": "1.0.1",
  "environment": "dev"
}
```

Four workflows are registered: `PersonalCreditReportWorkflow`, `LoanProductExtractionWorkflow`, `ConsultantWorkflow`, `GeneralFinancialWorkflow`. The environment is `"dev"`. The host is on the public internet.

Port 8081 serves Redis Commander with no authentication. The root path loads the full UI. Redis holds every in-flight and completed agent interaction. Thread IDs. Conversation state. Intermediate workflow outputs. Any data the workflow handled between LLM calls. Read/write, no credentials.

Port 3000 serves Langfuse 3.x with open registration. Create an account. Read every trace the workflow sent to the model. The workflow is named `PersonalCreditReportWorkflow`. The traces record every prompt it sent.

Port 18080 serves RAGFlow. Port 9090 serves MinIO with authentication enforced. A second LangGraph instance runs on port 8001. Two instances, same configuration, same missing auth layer.

This system processes financial identity data. The session store is open.

---

## Paris: No Auth by Design

`51.15.237.90` and `51.158.97.152` are two Scaleway nodes in Paris. Both run the same service:

```json
{
  "message": "Collector Scraper API",
  "version": "2.0.0",
  "features": [
    "Enhanced phone extraction with regex and phonenumbers library",
    "Fast email extraction with optimized regex",
    "LangGraph-based extraction workflow",
    "Multi-strategy field extraction",
    "Geographic location detection",
    "Cluster-based country detection"
  ]
}
```

"Enhanced" in two feature descriptions marks this as a second build. v1 existed. v2.0 improved the extractors.

The `/extract` endpoint accepts a `POST` with no authentication. The input schema matches Google Maps business directory records: place name, place type, nested field blocks. The pipeline fills in what the directory record is missing: email addresses, phone numbers, geographic coordinates, a cluster-assigned country label. MongoDB stores the output. "Cluster-based country detection" puts the scope at international scale.

Two nodes, same version, same config. Operational infrastructure.

The `/extract` endpoint is open. There is no auth layer.

---

## Fixes

For operators:

1. Put LangGraph behind a reverse proxy with an auth layer. nginx and Caddy both support this in a few lines of config. The LangGraph port should not be internet-facing directly.

2. Redis Commander belongs on localhost. Remove it from any Docker Compose file that maps it to `0.0.0.0`.

3. Disable Langfuse signup: `AUTH_DISABLE_SIGNUP=true`. Set this before any external exposure.

4. Bind Docker Compose services to `127.0.0.1`, not `0.0.0.0`. Every service in the stack defaults to binding all interfaces.

For LangChain: the self-hosted deployment docs need a pre-flight checklist before the "run this command" step. Not a footnote about security considerations. A required step: what is open, what closes it. All sixteen of these hosts went live without one.

---

_Full survey data and per-host findings: [LangGraph Server Population Survey (2026-05-25)](langgraph-server-survey-2026-05-25.md)_
