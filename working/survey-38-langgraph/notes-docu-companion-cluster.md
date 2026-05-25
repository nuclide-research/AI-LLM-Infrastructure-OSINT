# Docu Companion ("Assistent Tècnic Intel·ligent") — Complete Investigation Notes

**Hosts:** 157.180.21.126 · 37.27.88.127 · 5.75.229.153
**Cloud:** Hetzner Online GmbH (AS24940) — Helsinki (x2) + Falkenstein, Germany
**App name:** Assistent Tècnic Intel·ligent (ATI) — Intelligent Technical Assistant
**Operator geography:** Catalan-speaking region — Spain/Catalonia
**Status:** FULLY MAPPED — case study ready
**Priority:** 1

---

## Confirmed Services

| Host | Port | Service | Auth |
|---|---|---|---|
| 157.180.21.126 | 5000 | **Vite dev server (full source code exposed)** | NONE |
| 157.180.21.126 | 8000 | LangGraph "Docu Companion LangGraph API" v3.1.0 | NONE |
| 157.180.21.126 | 6333 | Qdrant 1.14.1 (commit 530430f) | NONE |
| 37.27.88.127 | 8000 | LangGraph API v3.1.0 | NONE |
| 37.27.88.127 | 6333 | Qdrant 1.14.1 | NONE |
| 5.75.229.153 | 8000 | LangGraph API v3.1.0 | NONE |
| 5.75.229.153 | 6333 | Qdrant 1.14.1 | NONE |

---

## Platform Description

Multi-tenant AI customer support platform. Catalan name: "Assistent Tècnic Intel·ligent." Multi-channel: WhatsApp, email, web chat. RAG knowledge base from company documents (PDFs). The API description specifically mentions "Albaran generation" — the platform processes Spanish/Catalan delivery notes and technical documents for customer support queries.

Languages: Catalan (primary), Spanish, English, French.

Architecture: Three Hetzner nodes (two Helsinki, one Falkenstein). 211 tenant namespaces in Qdrant. Each tenant (numbered knowledge_N collection) has its own document set; all share the same unauthenticated API surface.

Service uptime: 7,815,281 seconds ≈ 90 days. Running since approximately February 2026.

---

## Confirmed Findings

### F1 — Vite Dev Server Exposes Full TypeScript Source Code (HIGH)

Port 5000 on node 1 runs a Vite development server in production. It serves all source files uncompiled:

```
GET http://157.180.21.126:5000/src/main.tsx        — full source
GET http://157.180.21.126:5000/src/App.tsx          — full source + all route paths
GET http://157.180.21.126:5000/src/i18n/locales/ca.json  — Catalan strings
GET http://157.180.21.126:5000/src/i18n/locales/es.json  — Spanish strings
```

The Catalan locale file is confirmed readable and contains app branding, error messages, and the full navigation structure. Source maps are embedded in responses.

### F2 — User Conversation History Readable Without Auth (HIGH)

Qdrant `user_conversations` collection: 121 points, no auth. Identical count on all three nodes — shared backend or replication.

```
GET http://157.180.21.126:6333/collections/user_conversations
→ {"result": {"points_count": 121}}
```

### F3 — Tenant Knowledge Bases Readable Without Auth (HIGH)

Qdrant `knowledge` collection: 377 points on node 1. These are documents uploaded by tenant businesses. All 211 numbered collections (knowledge_1 through knowledge_211) are enumerable without auth. Collection list, metadata, and point counts all open.

Collection point counts on node 1:
- knowledge: 377 points (active document corpus)
- user_conversations: 121 points
- knowledge_base: 11 points
- All numbered collections: 0 points (populated on nodes 2/3)

### F4 — Agent Invocation Endpoints Fully Open (HIGH)

All agent endpoints have no security definition. Any caller can invoke the docu_agent, travel_agent, or general query with any input:

```
POST /docu_agent/invoke
POST /docu_agent/stream
POST /query
POST /upload-pdf
POST /transcribe-audio
POST /travel_agent/invoke
```

### F5 — Admin Diagnostics Open (MEDIUM)

GET /admin/diagnostics — no auth:

```json
{
  "pid": 1545978,
  "uptimeSec": 7815281,
  "mem": {"rssMb": 1115},
  "loadAvg": {"1m": 0.13}
}
```

/diagnostics/runtime: 403 (partial protection).

### F6 — Health Endpoint Leaks Service Topology (LOW)

GET /health — no auth, full internal architecture including failed LangSmith integration:

```
langsmith: {"available": false, "error": "No module named 'app.services.langsmith_service'"}
```

---

## Endpoint Map

| Method | Path | Auth |
|---|---|---|
| GET | / | NONE |
| GET | /admin/diagnostics | NONE |
| GET | /diagnostics/runtime | 403 |
| GET | /health | NONE |
| POST | /docu_agent/invoke | NONE |
| POST | /docu_agent/stream | NONE |
| POST | /docu_agent/stream_events | NONE |
| POST | /docu_agent/stream_log | NONE |
| POST | /docu_agent/c/{config_hash}/invoke | NONE |
| POST | /docu_agent/token_feedback | NONE |
| POST | /travel_agent/invoke | NONE |
| POST | /travel_agent/stream | NONE |
| POST | /query | NONE |
| POST | /upload-pdf | NONE |
| POST | /transcribe-audio | NONE |

---

## Qdrant Infrastructure

**Node 1 (157.180.21.126, Helsinki):** 11 collections — knowledge (377), user_conversations (121), knowledge_base (11), others empty
**Node 2 (37.27.88.127, Helsinki):** 15 collections — same + higher IDs (166, 168, 179, 209, 210, 211)
**Node 3 (5.75.229.153, Falkenstein):** 15 collections (identical to node 2)

Qdrant build: version 1.14.1, commit `530430fac2a3ca872504f276d2c91a5c91f43fa0` — identical across all nodes. Same operator/deployment template.

PTR: `static.*.clients.your-server.de` — Hetzner generic reverse DNS, no operator domain.

---

## Pending

- [ ] Who is the operator? Check Qdrant points metadata for company/contact info
- [ ] Check nodes 2/3 for distinct corpus (different tenants from node 1?)
- [ ] Enumerate ES locale file for any product/company name
