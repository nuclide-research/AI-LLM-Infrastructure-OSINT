---
type: case-study
title: "Assistent Tècnic Intel·ligent — Vite Dev Server in Production Exposes Source Code Across a 211-Tenant Platform"
date: 2026-05-25
severity: HIGH
sector: commercial
tags: [LangGraph, Qdrant, Catalonia, Spain, multi-tenant, vite, source-code, document-intelligence, conversation-history]
summary: "A Catalan AI document platform running across three Hetzner nodes exposes its full TypeScript source code via a Vite development server left running in production. All agent endpoints, 121 user conversations, and 211 tenant knowledge bases are accessible without authentication."
---

# Assistent Tècnic Intel·ligent — Vite Dev Server in Production Exposes Source Code Across a 211-Tenant Platform

**Date:** 2026-05-25
**Hosts:** 157.180.21.126 · 37.27.88.127 · 5.75.229.153
**Cloud:** Hetzner Online GmbH (AS24940), Helsinki (×2) and Falkenstein, Germany
**App:** Assistent Tècnic Intel·ligent (ATI) — Docu Companion LangGraph API v3.1.0
**Operator geography:** Catalonia, Spain
**Severity:** HIGH

---

## What Was Found

### F1 — Vite Development Server Running in Production on All Three Nodes (HIGH)

Port 5000 is open on all three cluster nodes. Node 1 (157.180.21.126) serves uncompiled TypeScript source files on direct request. Nodes 2 and 3 (37.27.88.127, 5.75.229.153) return Vite's HTML shell for path requests — confirmed by the `data-vite-theme` and `data-inject-first` attributes injected by Vite's runtime. All three nodes are running `vite dev` in production.

Node 1 source exposure confirmed:

```
GET http://157.180.21.126:5000/src/main.tsx          → full TypeScript source (Content-Type: text/javascript)
GET http://157.180.21.126:5000/src/App.tsx            → full source with all route paths
GET http://157.180.21.126:5000/src/i18n/locales/ca.json → Catalan string table
GET http://157.180.21.126:5000/src/i18n/locales/es.json → Spanish string table
```

The App.tsx file exposes the full page and route structure. Routes include: dashboard, chat, knowledge base, whitelist, queries, users, roles, branding settings, prompt templates, language settings, and menu permissions. Source maps are embedded in every response.

The Catalan locale file confirms the app name: "Assistent Tècnic Intel·ligent." Code comments are in Catalan. The app supports Catalan, Spanish, English, and French.

### F1b — PostgreSQL Exposed on Port 5432 (MEDIUM)

Port 5432 is open on node 1 (157.180.21.126) and accepts connections from the public internet. PostgreSQL responds to the startup packet with an authentication challenge (MD5, code 10). The instance is reachable — it is not firewalled. Whether the authentication can be bypassed with default credentials has not been tested.

### F2 — 121 User Conversations Readable Without Auth (HIGH)

Qdrant runs on port 6333 across all three nodes. The `user_conversations` collection holds 121 points on each node. No authentication.

```
GET http://157.180.21.126:6333/collections/user_conversations
→ {"result": {"status": "green", "points_count": 121}}
```

The count is identical on all three nodes. The conversation store is shared or replicated across the cluster.

### F3 — 211 Tenant Knowledge Bases Enumerable (HIGH)

Qdrant collections on nodes 2 and 3 (37.27.88.127, 5.75.229.153) reach collection ID 211. Each numbered collection (knowledge_1 through knowledge_211) is a tenant partition. The collection list, metadata, and point counts are open without authentication.

The `knowledge` collection on node 1 holds 377 points. This is the content tenants uploaded for their document Q&A assistant.

### F4 — All Agent Invocation Endpoints Open (HIGH)

Every invocation endpoint carries no security definition in the OpenAPI spec:

```
POST /docu_agent/invoke
POST /docu_agent/stream
POST /docu_agent/stream_events
POST /docu_agent/c/{config_hash}/invoke
POST /query
POST /upload-pdf
POST /transcribe-audio
POST /travel_agent/invoke
POST /travel_agent/stream
```

Any caller can invoke the document agent, upload files, or transcribe audio against any node.

### F5 — Admin Diagnostics Open (MEDIUM)

```
GET http://157.180.21.126:8000/admin/diagnostics
→ {"pid": 1545978, "uptimeSec": 7815281, "mem": {"rssMb": 1115}, "loadAvg": {"1m": 0.13}}
```

Uptime 7,815,281 seconds equals 90 days. The service has run since approximately February 2026.

### F6 — Health Endpoint Leaks Service Topology (LOW)

The `/health` response exposes the full internal architecture: Qdrant connection state, available collections, DocumentMemoryService status, compiled workflow graph status, and a failed LangSmith integration error:

```
"langsmith": {"available": false, "error": "No module named 'app.services.langsmith_service'"}
```

---

## Platform Description

ATI is a multi-tenant AI document assistant for Catalan and Spanish businesses. The API description names "Albaran generation" as the use case — albaranes are Spanish delivery notes and packing slips. The platform handles business documents for customer support queries across WhatsApp, email, and web chat.

Three Hetzner nodes form the cluster: two in Helsinki, one in Falkenstein. All run Qdrant 1.14.1 at identical git commit `530430fac2a3ca872504f276d2c91a5c91f43fa0`. Nodes 2 and 3 carry 15 collections each, with higher tenant IDs than node 1. Node 1 has 11 collections. The higher IDs on nodes 2 and 3 mark tenants added after node 1 was provisioned.

The agent stack includes a document agent (modern), a travel agent (legacy), and a general assistant with routing. The presence of `/transcribe-audio` shows voice input is supported.

---

## Operator Attribution

No domain appears in any response header, PTR record, or API metadata. PTR records resolve to Hetzner generic addresses. The operator is identified only by language and use case: Catalan-language comments, Catalan as a primary locale alongside Spanish, and the albaran generation use case place the operator in Catalonia or the broader Spanish-speaking market.
