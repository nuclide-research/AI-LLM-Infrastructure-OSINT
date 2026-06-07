---
type: case-study
title: "Assistent Tècnic Intel·ligent (ATI) — Vite Dev Server in Production, 211-Tenant Platform"
date: 2026-05-25
severity: HIGH
sector: commercial
tags: [LangGraph, Qdrant, Vite, dev-server, multi-tenant, Spain, Catalonia, Hetzner, agent-framework, source-disclosure]
summary: "A Catalan multi-tenant AI customer support platform runs a Vite development server in production on one of three Hetzner nodes, exposing full TypeScript source code. All three nodes share unauthenticated LangGraph agent endpoints and Qdrant databases holding 121 customer conversations and 377 tenant knowledge-base documents."
---

# Assistent Tècnic Intel·ligent (ATI) — Vite Dev Server in Production, 211-Tenant Platform

**Date:** 2026-05-25
**Targets:** 157.180.21.126 · 37.27.88.127 · 5.75.229.153
**ASN:** AS24940 Hetzner Online GmbH — Helsinki (2 nodes) + Falkenstein, Germany
**Severity:** HIGH

---

## What Was Found

### F1 — Vite Dev Server Exposes Full TypeScript Source Code (HIGH)

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, S7068, S7075, T5904
- **733 (AI Risk & Ethics Specialist):** K7040, T5868
- **overlap (Common AI KSATs (all 5 roles)):** K1158, K22, K6900, K7003, K942

<!-- ksat-tag:auto-generated:end -->

Port 5000 on node 1 (157.180.21.126) runs a Vite development server. Not a compiled build. Not a staging environment. The process serving production traffic is the same Vite dev server used during local development:

```
GET http://157.180.21.126:5000/src/main.tsx
→ 200 OK — full uncompiled TypeScript source

GET http://157.180.21.126:5000/src/App.tsx
→ 200 OK — routing tree, all API paths, component structure

GET http://157.180.21.126:5000/src/i18n/locales/ca.json
→ 200 OK — full Catalan string table
```

Source maps are embedded. The full application codebase, including business logic, API endpoint definitions, error messages, and navigation structure, is readable without authentication.

The Catalan string table (`ca.json`) confirms the operator geography: primary language is Catalan, with Spanish, English, and French secondary. The app name: "Assistent Tècnic Intel·ligent" (ATI), Intelligent Technical Assistant.

### F2 — Customer Conversation History Readable Without Auth (HIGH)

Qdrant on all three nodes holds 121 conversation points across the `user_conversations` collection, all without auth:

```
GET http://157.180.21.126:6333/collections/user_conversations
→ {"result": {"points_count": 121}}
```

Identical counts on all three nodes confirm shared state or full replication. The `user_conversations` collection holds multi-channel customer support threads (WhatsApp, email, web chat) for 211 tenant businesses. The platform is described in its own API spec as handling "Albaran generation" (Spanish/Catalan delivery notes) and technical document queries.

### F3 — Tenant Knowledge Bases Readable Without Auth (HIGH)

The `knowledge` collection holds 377 document points on node 1, representing PDFs uploaded by tenant businesses. The full collection list is enumerable:

```
GET http://157.180.21.126:6333/collections
→ 11 collections: knowledge (377), user_conversations (121), knowledge_base (11), ...
```

Nodes 2 and 3 each hold 15 collections including numbered tenant namespaces (knowledge_166, knowledge_168, knowledge_179, knowledge_209, knowledge_210, knowledge_211). Every collection schema, metadata, and point count is readable. The collection contents, uploaded company documents, are accessible via the Qdrant point read API.

211 numbered tenant namespaces indicate 211 registered client businesses, each with a private knowledge base now accessible to any external caller.

### F4 — Agent Endpoints Open, Including PDF Ingestion (HIGH)

LangGraph API v3.1.0 runs on port 8000 across all three nodes with no auth:

| Endpoint | Function |
|---|---|
| POST /docu_agent/invoke | Synchronous agent call |
| POST /docu_agent/stream | Streaming agent response |
| POST /query | Direct knowledge-base query |
| POST /upload-pdf | Upload documents to knowledge base |
| POST /transcribe-audio | Audio transcription |
| POST /travel_agent/invoke | Travel assistant |

`POST /upload-pdf` means any caller can inject documents into the knowledge bases that serve 211 tenant companies. A poisoned document in `knowledge_N` propagates to every query that tenant's customers issue against that base.

### F5 — Failed LangSmith Integration Disclosed in Health Response (LOW)

```
GET http://157.180.21.126:8000/health
→ {
    "langsmith": {"available": false, "error": "No module named 'app.services.langsmith_service'"}
  }
```

The production deployment carries a broken LangSmith tracing integration. The error is observable without auth and confirms the internal module structure.

---

## Stack Map

| Host | Port | Service | Version | Auth | Severity |
|---|---|---|---|---|---|
| 157.180.21.126 | 5000 | Vite dev server | — | None | HIGH |
| 157.180.21.126 | 8000 | LangGraph API | v3.1.0 | None | HIGH |
| 157.180.21.126 | 6333 | Qdrant | 1.14.1 | None | HIGH |
| 37.27.88.127 | 8000 | LangGraph API | v3.1.0 | None | HIGH |
| 37.27.88.127 | 6333 | Qdrant | 1.14.1 | None | HIGH |
| 5.75.229.153 | 8000 | LangGraph API | v3.1.0 | None | HIGH |
| 5.75.229.153 | 6333 | Qdrant | 1.14.1 | None | HIGH |

All three Qdrant instances: identical version (1.14.1, commit `530430fac2a3ca872504f276d2c91a5c91f43fa0`). Same operator, same deployment template.

---

## Attribution

Catalan-speaking operator, Spain/Catalonia. Platform serves businesses in the Catalan market, handling delivery note processing and technical support in Catalan, Spanish, English, and French. Three Hetzner nodes (Helsinki + Falkenstein) with generic PTR (`static.*.clients.your-server.de`). No domain attribution from passive sources. Service uptime at discovery: 7,815,281 seconds, approximately 90 days running since February 2026.

---

## The Vite Dev Server Pattern

A developer building a LangGraph app runs `npm run dev` for local iteration. The `dev` command starts Vite's development server, enabling hot module replacement, source map generation, and raw file serving from `src/`. That process gets deployed to production unchanged. The compiled `dist/` build never ran.

Recurring deployment failure class in AI startups: infrastructure (Hetzner VM + Qdrant + LangGraph) deployed correctly, application build process not. The development server works. It serves the app. Nothing breaks at first use. The source disclosure is silent.

---

## Thesis Placement

Qdrant's default no-auth posture (Insight #13) propagates to production across all three nodes without operator awareness. The multi-tenant architecture amplifies the impact: a single Qdrant deployment serves 211 businesses, each with private document knowledge bases now open to the public. The Vite dev server pattern is an adjacent failure class not covered by the auth-on-default thesis. It is a build/deploy gap, not a framework default, but the exposure profile is equivalent.

**See also:** [LangGraph Server Survey (2026-05-25)](langgraph-server-survey-2026-05-25.md) · [LangGraph Deployment Gap](langgraph-deployment-gap-survey-2026-05-25.md)
