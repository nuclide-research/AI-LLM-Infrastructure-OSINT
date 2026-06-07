---
type: case-study
title: "CrewAI SOP RAG Agent: Multi-Agent Standard Operating Procedure System Open Without Authentication"
date: 2026-05-25
severity: HIGH
sector: commercial
tags: [CrewAI, FastAPI, uvicorn, RAG, SOP, multi-agent, Azure, upload, write-access]
summary: "A multi-agent CrewAI system on Azure exposes its full API without authentication. All nine endpoints are open. POST /upload allows unauthenticated file ingestion into the SOP database. POST /query runs the full agent pipeline against stored documents. The agent roster and workflow configuration are enumerable without credentials."
---

# CrewAI SOP RAG Agent: Multi-Agent Standard Operating Procedure System Open Without Authentication

**Date:** 2026-05-25
**Host:** 20.185.107.134
**Cloud:** Microsoft Azure (AS8075), Reston, Virginia, US
**App:** CrewAI SOP RAG Agent API — Multi-agent AI-powered Standard Operating Procedures Retrieval and Analysis
**Severity:** HIGH

---

## What Was Found

### F1 — Full API Open Without Authentication (HIGH)

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7004, S7068, S7075, T5904
- **733 (AI Risk & Ethics Specialist):** K7051, T5868
- **overlap (Common AI KSATs (all 5 roles)):** K1158, K22, K6311, K6935, K7003

<!-- ksat-tag:auto-generated:end -->

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

`POST /upload` writes to the SOP database. No credentials. Any caller can add documents to the SOP knowledge base. The SOP Retrieval Specialist searches that store via `sop_search_tool`.

Accepted formats: `.md`, `.txt`, `.docx`, `.pdf`, `.html`. Each file is converted to markdown and saved to the `sops/` folder. ChromaDB ingests it on the next query or manual trigger.

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

Three-agent sequential pipeline. The SOP Database Manager controls ingestion. The Retrieval Specialist runs semantic search against ChromaDB. The Technical Analyst formats the final response. All tool bindings are disclosed.

### F4 — Interactive Web Interface Open (MEDIUM)

`GET /web_interface`, `GET /upload_interface`, and `GET /rag_interface` serve browser-accessible UIs without authentication. Any visitor can submit queries and upload documents through the UI.

### F5 — Internal IP and Launch Command Disclosed (LOW)

The web interface JavaScript hardcodes the internal Azure IP as a fallback for file:// mode:

```javascript
const API_BASE_URL = window.location.protocol === 'file:'
    ? 'http://10.0.0.6:8000'  // When opening HTML file directly
    : window.location.origin;
```

The error guidance in the same interface names the exact uvicorn launch command:

```
uvicorn api:app --host 10.0.0.6 --port 8000
```

Internal Azure IP: `10.0.0.6`. Python module: `api`. ASGI app variable: `app`.

### F6 — Broken Stats Tool Reveals Agent Misconfiguration (LOW)

`GET /stats` returns:

```json
{
  "status": "error",
  "message": "Error getting database stats: 'Tool' object is not callable",
  "system_type": "CrewAI Multi-Agent RAG",
  "workflow_process": "Sequential agent collaboration"
}
```

The `sop_database_stats` tool on the SOP Database Manager agent is misconfigured. The tool object is passed where a callable is expected. The error reaches the API response unhandled. The pipeline initializes (`crew_system_initialized: true`). The stats tool does not execute.

---

## Stack

FastAPI backend, uvicorn server, Azure Virginia US (Microsoft Corporation AS8075). CrewAI multi-agent framework. ChromaDB vector store (embedded, confirmed from upload endpoint schema). Port 8000 is the only externally open port. No separate vector DB port is reachable. Files land in a `sops/` folder on the host filesystem.


---

## Data Classification

SOP documents in the database contain internal process descriptions. Their contents are readable via `POST /query` without credentials. The document type (HR, IT, operations, safety procedures) is unconfirmed from metadata alone. We did not query the contents.

`POST /upload` is open. The SOP Retrieval Specialist searches the same ChromaDB store. What gets written gets read back.

---

## Operator Attribution

No domain appears in response headers or API metadata. Server header: `uvicorn`. Host 20.185.107.134 resolves to Microsoft Azure in the Reston, Virginia region. Operator identity not confirmed from public surface.
