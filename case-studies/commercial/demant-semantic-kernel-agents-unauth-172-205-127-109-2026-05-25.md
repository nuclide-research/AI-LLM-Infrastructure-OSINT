---
type: case-study
title: "Demant Semantic Kernel Agent Platform: Five Production Agents Open Without Authentication"
date: 2026-05-25
severity: HIGH
sector: commercial
tags: [SemanticKernel, Microsoft, FastAPI, agents, hearing-technology, Demant, Azure, production]
summary: "A Microsoft Semantic Kernel agent hosting platform at 172.205.127.109 exposes five production agents without authentication. Agent names, system prompts, and plugin bindings name Demant, a Danish hearing technology company. POST /agents/execute runs any agent against the knowledge base without credentials. POST /agents/create and DELETE /agents/{id} are open."
---

# Demant Semantic Kernel Agent Platform: Five Production Agents Open Without Authentication

**Date:** 2026-05-25
**Host:** 172.205.127.109:8000
**Cloud:** Microsoft Azure (MICROSOFT-MAINT), Dublin, Ireland, EU
**App:** Semantic Kernel Agents Service 1.0.0 (Microsoft Semantic Kernel Agents Hosting Platform v2.0.0)
**Severity:** HIGH

---

## What Was Found

### F1 — Full API Open Without Authentication (HIGH)

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, S7068, S7075, T5904
- **733 (AI Risk & Ethics Specialist):** K7040, K7051, T5854, T5868
- **overlap (Common AI KSATs (all 5 roles)):** K1158, K22, K6311, K6935, K7003

<!-- ksat-tag:auto-generated:end -->

All endpoints respond without credentials. The OpenAPI spec carries no security definitions.

```
GET  /              → {"message":"Semantic Kernel Agents Service is running","version":"2.0.0",...}
GET  /health        → {"status":"healthy","semantic_kernel":"initialized","agents_available":5}
GET  /agents        → full agent roster with system prompts and plugin bindings
GET  /agents/plugins → plugin catalog
POST /agents/execute → run any agent against knowledge base (no credentials)
POST /agents/create  → create new agents (no credentials)
GET  /agents/{id}    → agent detail
DELETE /agents/{id}  → remove agents (no credentials)
GET  /test-gpt      → GPT integration test endpoint
```

### F2 — Production Agent Roster Enumerable: Demant Attribution Confirmed (HIGH)

```
GET /agents →
[
  {
    "id": "research-assistant",
    "name": "Research Assistant",
    "description": "Specialized in hearing technology research and Demant knowledge",
    "system_message": "You are a research assistant specializing in hearing technology and Demant's products...",
    "plugins": ["DemantKnowledgePlugin", "ResearchPlugin"],
    "is_custom": false
  },
  {
    "id": "code-helper",
    "name": "Code Helper",
    "plugins": ["CodeAnalysisPlugin"],
    "is_custom": false
  },
  {
    "id": "data-analyst",
    "name": "Data Analyst",
    "plugins": ["DataAnalysisPlugin"],
    "is_custom": false
  },
  {
    "id": "writing-advisor",
    "name": "Writing Advisor",
    "plugins": [],
    "is_custom": false
  },
  {
    "id": "custom-20250814131910",
    "name": "Customer Support Agent",
    "description": "Specialized in helping customers with Demant products and support queries",
    "system_message": "You are a friendly and knowledgeable customer support agent for Demant...",
    "plugins": ["DemantKnowledgePlugin"],
    "is_custom": true
  }
]
```

Five agents. Two carry `DemantKnowledgePlugin`. The Research Assistant system prompt names "hearing technology and Demant's products." The Customer Support Agent, created 2025-08-14, names "Demant" and "hearing aids." Demant is the parent company of Oticon, Bernafon, Philips Hearing, and EPOS.

### F3 — Unauthenticated Agent Execution (HIGH)

`POST /agents/execute` runs any agent in the roster without credentials.

```
POST /agents/execute
Content-Type: application/json

{
  "agent_id": "research-assistant",
  "message": "<query>",
  "context": null
}
```

The request reaches the Semantic Kernel runtime. The runtime processes it against the bound plugins. `DemantKnowledgePlugin` provides access to a hearing technology knowledge base. We did not query the knowledge base. The execution surface is confirmed from the OpenAPI schema.

### F4 — Agent Creation and Deletion Open (HIGH)

`POST /agents/create` and `DELETE /agents/{agent_id}` carry no auth gate. Any caller can add or remove agents from the platform roster.

### F5 — Plugin Catalog Enumerable (MEDIUM)

```
GET /agents/plugins →
[
  {"name": "DemantKnowledgePlugin", "description": "Access to Demant's hearing technology knowledge base"},
  {"name": "ResearchPlugin",        "description": "Research and analysis capabilities"},
  {"name": "CodeAnalysisPlugin",    "description": "Code analysis and best practices"},
  {"name": "DataAnalysisPlugin",    "description": "Data analysis and visualization"}
]
```

`DemantKnowledgePlugin` is a named knowledge base. Its contents were not queried.

---

## Stack

FastAPI backend. uvicorn server. Microsoft Semantic Kernel framework. Azure Dublin EU (MICROSOFT-MAINT). Port 8000. No TLS on port 8000. OpenAPI 3.1.0.

---

## Failure Mode

Semantic Kernel is a Microsoft SDK, not a hosted platform with a default auth model. Auth is the developer's responsibility. The platform ships with an open API and no auth layer configured. Five agents are running. Two carry `DemantKnowledgePlugin`. The execution endpoint accepts requests without credentials.

The Customer Support Agent was created 2025-08-14. A named knowledge base and a custom agent are not staging artifacts.

---

## Operator Attribution

Agent names, system prompts, and plugin descriptions name "Demant" and "Demant's products." William Demant Holding A/S is headquartered in Smørum, Denmark. Its brands include Oticon, Bernafon, Philips Hearing, and EPOS. The platform is on Microsoft Azure Dublin (EU region). No domain in HTTP headers or TLS certificate. IP resolves to Microsoft Corporation AS8075.
