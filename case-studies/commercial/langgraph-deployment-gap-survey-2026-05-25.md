---
type: survey
title: "LangGraph's Deployment Gap: Exposed AI Agent Infrastructure at Scale"
date: 2026-05-25
tags: [LangGraph, agent-framework, survey, auth-on-default, fingerprinting, Redis, Langfuse]
summary: "LangGraph's self-hosted deployment path ships with no authentication. We found sixteen internet-facing deployments. All sixteen were open. The supporting infrastructure around them — Redis Commander, Langfuse, RAGFlow — was open too."
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

The operators ran different things on top of this. A financial system in Shanghai processing personal credit reports and loan applications. A SharePoint assistant in Poland holding active Microsoft tenant credentials. Two coaching platforms where every conversation thread was readable by thread ID. A two-node production scraper built to extract contact PII from business directories.

Different operators, different use cases, same missing auth layer.

---

## How It Happens

LangGraph Cloud manages auth for you. The self-hosted path does not. That is the full explanation.

A developer runs `langgraph up` locally. It works. They push the same configuration to a cloud VM. Then they add Redis Commander to inspect session state, Langfuse to watch LLM calls, MinIO for file storage. Each tool ships with no auth by default. Each one opens another port. By the time the stack is complete, five services are internet-facing and none of them required the developer to type a password.

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

The `/health` endpoint on most instances returns `redis_connected: true`. That confirms a live session store with recoverable state. The graph metadata endpoints name the workflows: their node structure, their field labels. On a credit report system, those labels name the data.

---

## What Opens Up

**LangGraph itself.** Thread history for any thread ID. Full workflow state. Graph definitions including node names and, in some cases, field labels tied to PII categories. The API is fully functional with no credentials.

**Redis Commander.** A browser-based Redis UI. The root path loads a 30KB interface with no login prompt. Redis is where agent state lives between LLM calls: in-flight sessions, completed conversations, any data the workflow handled mid-run. Read/write, no credentials.

**Langfuse.** Open registration on a private Langfuse instance means any account you create can read every LLM trace the operator recorded: the full prompt sent, the model's full response, token counts, latency, structured metadata. For the Shanghai financial system, those traces contain the credit report data the workflow processed.

**SharePoint-connected agents.** The agent's webhook registration list is readable. Its chat endpoint is open. Even after OAuth tokens expire, the Microsoft tenant ID surfaces in the error body. One host returned tenant ID `5b72381b-179a-4941-a3f8-c22cc66c3adf` in a 401 response. That is an attribution anchor that survives credential rotation.

---

## The Two Cases

**[Chinese financial LangGraph agent, TencentCloud Shanghai.](langgraph-financial-agent-1-15-66-80-2026-05-25.md)** Named workflows: `PersonalCreditReportWorkflow`, `LoanProductExtractionWorkflow`. Environment: `"dev"`. Redis Commander on port 8081, no login prompt, full session store access. Langfuse and RAGFlow on the same host. The data processed by this system is financial identity data. The session store is open.

**[Collector Scraper API, Scaleway Paris.](collector-scraper-api-langgraph-pii-2026-05-25.md)** Two production nodes. v2.0. LangGraph extraction pipeline that takes a business listing and returns emails, phone numbers, and geographic coordinates. No auth on `/extract`. MongoDB backend. International scope via cluster-based country detection. This service was not left open by accident. There is no auth layer to have forgotten.

---

## Fixes

For operators:

1. Put LangGraph behind a reverse proxy with an auth layer. nginx and Caddy both support this in a few lines of config. The LangGraph port should not be internet-facing directly.

2. Redis Commander belongs on localhost. Remove it from any Docker Compose file that maps it to `0.0.0.0`.

3. Disable Langfuse signup: `AUTH_DISABLE_SIGNUP=true`. Set this before any external exposure.

4. Bind Docker Compose services to `127.0.0.1`, not `0.0.0.0`. Every service in the stack defaults to binding all interfaces.

For LangChain: the self-hosted deployment docs need a pre-flight checklist before the "run this command" step. Not a footnote about security considerations. A required step that lists what is open and what closes it. The current gap between "this works" and "this is ready for production" is where all sixteen of these hosts ended up.

---

_Full survey data and per-host findings: [LangGraph Server Population Survey (2026-05-25)](langgraph-server-survey-2026-05-25.md)_
