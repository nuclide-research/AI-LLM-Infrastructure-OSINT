---
type: case-study
title: "CrewAI SOP RAG Agent — Multi-Agent Standard Operating Procedure System Open Without Authentication"
date: 2026-05-25
severity: HIGH
sector: commercial
tags: [CrewAI, FastAPI, uvicorn, RAG, SOP, multi-agent, Azure, upload, write-access]
summary: "A multi-agent CrewAI system on Azure exposes its full API without authentication. All nine endpoints are open. POST /upload allows unauthenticated file ingestion into the SOP database. POST /query runs the full agent pipeline against stored documents. The agent roster and workflow configuration are enumerable without credentials."
---

# CrewAI SOP RAG Agent — Multi-Agent Standard Operating Procedure System Open Without Authentication

**Date:** 2026-05-25
**Host:** 20.185.107.134
**Cloud:** Microsoft Azure (AS8075), Reston, Virginia, US
**App:** CrewAI SOP RAG Agent API — Multi-agent AI-powered Standard Operating Procedures Retrieval and Analysis
**Severity:** HIGH

---

## What Was Found

### F1 — Full API Open Without Authentication (HIGH)

All nine endpoints respond without credentials. The OpenAPI spec carries no security definitions on any route.

```
GET  /                    → redirect to web interface
GET  /health              → {"status":"healthy","crew_system_initialized":true,"agents_count":3}
POST /query               → run CrewAI agent pipeline against SOP database
POST /query/async         → async pipeline execution
GET  /query/{session_id}  → retrieve async results
GET  /stats               → SOP database statistics
POST /upload              → ingest SOP document into the database
GET  /agents              → enumerate agent roster and capabilities
GET  /web_interface       → full browser-based interface, no login
```

### F2 — Write Access: Unauthenticated SOP Document Upload (HIGH)

`POST /upload` ingests documents into the SOP database without authentication. Any caller can add arbitrary documents to the knowledge base this agent queries. The SOP Retrieval Specialist agent performs semantic search against this store. Injected documents will surface in query results.

### F3 — Agent Roster Enumerable (MEDIUM)

```
GET /agents →
{
  "agents": [
    {"name":"SOP Database Manager","role":"Manages SOP ingestion and database maintenance",
     "tools":["sop_ingestion_tool","sop_database_stats"]},
    {"name":"SOP Retrieval Specialist","role":"Finds and retrieves relevant SOPs",
     "tools":["sop_search_tool"]},
    {"name":"SOP Technical Analyst","role":"Analyzes and formats SOPs into actionable instructions",
     "tools":["AI analysis capabilities"]}
  ],
  "workflow":"Sequential collaboration with task dependencies",
  "process_type":"Multi-agent pipeline"
}
```

Three-agent sequential pipeline. The SOP Database Manager controls ingestion. The Retrieval Specialist runs semantic search. The Technical Analyst formats and returns the final response. All tool bindings are disclosed.

### F4 — Interactive Web Interface Open (MEDIUM)

`GET /web_interface` and `GET /upload_interface` and `GET /rag_interface` serve browser-accessible UIs without authentication. Any visitor can submit queries and upload documents through the UI.

---

## Stack

FastAPI backend, uvicorn server, Azure Virginia US (Microsoft Corporation AS8075). CrewAI multi-agent framework. The system processes Standard Operating Procedures — internal process documentation. The use case is enterprise SOP retrieval and analysis.

---

## Data Classification

SOP documents loaded into the database contain internal process descriptions. Their contents are readable via `POST /query` without credentials. The nature of the documents (HR, IT, operations, safety procedures) is not confirmed from metadata alone — query access would be required to enumerate contents, which we have not exercised.

The write surface (`POST /upload`) is the primary risk: it allows an external party to inject documents that the agent pipeline will treat as authoritative SOPs and serve to internal users.

---

## Operator Attribution

No domain appears in response headers or API metadata. Server header: `uvicorn`. Host 20.185.107.134 resolves to Microsoft Azure in the Reston, Virginia region. Operator identity not confirmed from public surface.
