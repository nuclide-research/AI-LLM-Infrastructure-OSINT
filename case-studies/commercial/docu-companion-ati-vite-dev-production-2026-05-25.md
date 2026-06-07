---
type: case-study
title: "Docu Companion / ATI — Vite Dev Server and 211 Tenant Knowledge Bases Open on a Three-Node Hetzner Cluster"
date: 2026-05-25
severity: HIGH
sector: commercial
tags: [LangGraph, Qdrant, Vite, RAG, multi-tenant, SMB, Catalan, Spain, Hetzner, source-code-exposure, agent-framework]
summary: "A Catalan-language multi-tenant AI customer support platform runs a Vite development server in production on one node, exposing full TypeScript source. All three Hetzner nodes share an unauthenticated Qdrant stack holding 211 tenant knowledge bases, 377 business documents, and 121 user conversations. Agent invocation endpoints are fully open."
---

# Docu Companion / ATI — Vite Dev Server and 211 Tenant Knowledge Bases Open on a Three-Node Hetzner Cluster

**Date:** 2026-05-25
**Targets:** 157.180.21.126 · 37.27.88.127 · 5.75.229.153
**ASN:** AS24940, Hetzner Online GmbH — Helsinki (x2) + Falkenstein, Germany
**Severity:** HIGH

---

## What Was Found

### F2 — 211 Tenant Knowledge Bases, All Enumerable (HIGH)

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7004, S7068, S7075, T5904
- **733 (AI Risk & Ethics Specialist):** K7040, K7051
- **overlap (Common AI KSATs (all 5 roles)):** K1158, K22, K7003, K942

<!-- ksat-tag:auto-generated:end -->

Qdrant on all three nodes runs unauthenticated on port 6333. The tenant namespace pattern is `knowledge_1` through `knowledge_211`. Every collection is enumerable: name, metadata, and point count.

Node 1 has 377 documents in the active `knowledge` collection and 11 in `knowledge_base`. Nodes 2 and 3 carry higher-numbered collections (166, 168, 179, 209, 210, 211), the most recently onboarded tenants. The documents are customer-uploaded business files: Spanish and Catalan delivery notes (albaranes), PDFs, and technical documentation.

```
GET http://157.180.21.126:6333/collections
→ knowledge (377 points), user_conversations (121 points),
  knowledge_base (11 points), knowledge_1 ... knowledge_211
```

### F3 — 121 User Conversations Readable Without Auth (HIGH)

The `user_conversations` collection holds 121 points. Point count is identical across all three nodes, confirming a shared backend. No authentication is required to enumerate, read, or query them.

### F4 — Agent Invocation Endpoints Fully Open (HIGH)

The LangGraph API on port 8000 carries no security definition on any endpoint. The `docu_agent`, `travel_agent`, and general query pipeline are open to any external caller against any tenant's knowledge base. The upload and transcription endpoints accept arbitrary content.

```
POST /docu_agent/invoke
POST /docu_agent/stream
POST /query
POST /upload-pdf
POST /transcribe-audio
POST /travel_agent/invoke
```

All six endpoints are unauthenticated. No transport-layer authentication exists on any node.

### F1 — Vite Dev Server Running in Production (HIGH)

Port 5000 on node 1 serves raw TypeScript source files. No build step was run. The development server went straight to production.

```
GET http://157.180.21.126:5000/src/main.tsx
GET http://157.180.21.126:5000/src/App.tsx
GET http://157.180.21.126:5000/src/i18n/locales/ca.json
GET http://157.180.21.126:5000/src/i18n/locales/es.json
```

`App.tsx` exposes every client route. The Catalan locale file (`ca.json`) contains the full navigation structure, error messages, and app branding. Source maps are embedded. Locale files for all four supported languages (Catalan, Spanish, English, French) are served without auth. Vite's HMR endpoint is open alongside them.

### F5 — Admin Diagnostics Open (MEDIUM)

`GET /admin/diagnostics` requires no authentication:

```json
{
  "pid": 1545978,
  "uptimeSec": 7815281,
  "mem": {"rssMb": 1115},
  "loadAvg": {"1m": 0.13}
}
```

7,815,281 seconds is 90 days. The platform has run in this state since approximately February 2026. `/diagnostics/runtime` returns 403, confirming partial protection was applied and stopped there.

### F6 — Health Endpoint Leaks Failed Integration (LOW)

`GET /health` exposes the internal service topology, including a broken LangSmith dependency:

```
langsmith: {"available": false, "error": "No module named 'app.services.langsmith_service'"}
```

The LangSmith module was removed or never installed. The health check broadcasts this on every request.

---

## Stack Map

| Host | Port | Service | Auth | Severity |
|---|---|---|---|---|
| 157.180.21.126 | 5000 | Vite dev server (TypeScript source) | None | HIGH |
| 157.180.21.126 | 8000 | LangGraph API v3.1.0 | None | HIGH |
| 157.180.21.126 | 6333 | Qdrant 1.14.1 | None | HIGH |
| 37.27.88.127 | 8000 | LangGraph API v3.1.0 | None | HIGH |
| 37.27.88.127 | 6333 | Qdrant 1.14.1 | None | HIGH |
| 5.75.229.153 | 8000 | LangGraph API v3.1.0 | None | HIGH |
| 5.75.229.153 | 6333 | Qdrant 1.14.1 | None | HIGH |

---

## Platform Context

The application name in Catalan is "Assistent Tècnic Intel·ligent" (ATI). The English-facing name is Docu Companion. The API root describes the platform as a multi-channel AI customer support tool for businesses: WhatsApp, email, and web chat. An albaran is a Spanish/Catalan delivery note. Businesses upload these to the knowledge base so the AI assistant can answer customer queries about orders and deliveries. The `albaran` reference in the API description confirms the core use case.

The platform targets SMBs in the Catalan-speaking region of Spain. 211 tenant namespaces at the time of survey.

---

## Cluster Pattern

All three nodes run Qdrant 1.14.1 at commit `530430fac2a3ca872504f276d2c91a5c91f43fa0`. The hash is identical across every node. A single deployment template produced all three nodes. The operator scaled horizontally and added no authentication at any layer.

Node 1 (Helsinki) is the only node with the Vite dev server on port 5000. Nodes 2 and 3 do not expose it. Node 1 carries the lower-numbered collections and the main document corpus. Nodes 2 and 3 carry collections 166 through 211.

PTR records resolve to Hetzner generic reverse DNS (`static.*.clients.your-server.de`). No operator domain is recoverable from network-layer data.

---

**See also:** [LangGraph Server Survey (2026-05-25)](../surveys/langgraph-server-survey-2026-05-25.md) · [LangGraph Deployment Gap — Systematic Pattern](../surveys/langgraph-deployment-gap-survey-2026-05-25.md)
