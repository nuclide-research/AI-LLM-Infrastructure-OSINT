---
type: case-study
title: "Stock.ai (EMOR AI) — Partial-Auth Failure, Open Weaviate, and 62 Proprietary Analyst Reports"
date: 2026-05-25
severity: HIGH
sector: commercial
tags: [LangGraph, Weaviate, partial-auth, financial, India, Azure, Flutter, vector-db, PDF-leak, equity-research]
summary: "EMOR AI's unreleased Stock.ai product exposes a Weaviate vector database, individual API resource endpoints, and 62+ proprietary Arihant Capital equity analyst reports. The developer implemented JWT and Google OAuth but left individual resource endpoints unprotected. A reused HR/resume Azure OpenAI subscription confirms operator identity."
---

# Stock.ai (EMOR AI) — Partial-Auth Failure, Open Weaviate, and 62 Proprietary Analyst Reports

**Date:** 2026-05-25
**Target:** 20.193.252.230
**ASN:** AS8075, Microsoft Azure, Pune, Maharashtra, India
**Operator:** EMOR AI (emorai.com), Thane, Maharashtra, India
**Severity:** HIGH

---

## What Was Found

### F1 — Partial-Auth Failure on LangGraph API (HIGH)

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7004, S7068, S7070, S7075, T5904, T5919
- **733 (AI Risk & Ethics Specialist):** K7040, K7051
- **overlap (Common AI KSATs (all 5 roles)):** K1158, K22, K6311, K6935, K7003, K942

<!-- ksat-tag:auto-generated:end -->

Port 8000 runs a LangGraph FastAPI backend for Stock.ai v1.0.0. Auth is enforced at the collection layer and absent at the resource layer.

The OpenAPI spec marks GET /conversations with a lock icon. That endpoint requires a Bearer token. The resource endpoints below it do not:

| Endpoint | Auth |
|---|---|
| GET /conversations | Required |
| GET /conversations/{id} | None |
| DELETE /conversations/{id} | None |
| POST /conversations/new | None |
| GET /portfolio/{user_id} | None |
| GET /pdf/{filename} | None |

Verified against live endpoints:

```
POST /conversations/new
→ {"conversation_id":"a47769a9-1ce7-45b8-bc8c-e9ba2c97f2b5"}

GET /conversations/a47769a9-1ce7-45b8-bc8c-e9ba2c97f2b5
→ {"messages":[],"created_at":"...","updated_at":"..."}

GET /portfolio/{user_id}
→ returns portfolio data or "Portfolio not found"
```

No token required on any of these. The developer built JWT tokens, Google OAuth, password reset, and profile management. None of it covers the resource layer. UUID conversation IDs are returned on signup. User IDs are enumerable via the email oracle (F5). Any registered account reaches every other user's conversations and portfolio data.

### F2 — Weaviate 1.33.1 Fully Open (HIGH)

Port 8080 serves Weaviate 1.33.1 (git hash c87f308). No authentication on any endpoint. HEALTHY, single node, 36 modules loaded including multimodal CLIP vectorization.

Seven data collections:

| Class | Contents |
|---|---|
| TextCollections | Financial PDF text: title, content, filename, stock, quarter, year, page_number, source |
| TextEmbeddings | Same schema, alternate pipeline iteration |
| ImageCollections | PDF images: filename, stock, quarter, year, page_number, picture_id, image_base64, caption, title, content, source |
| ImageEmbeddings | Image vectors with full image_base64 |
| DocumentCollectionPyPdf2 | PyPDF2 parser iteration |
| DocumentCollectionuatnew | UAT test collection |
| ImageCaptiontest | Test collection |

GraphQL aggregate, schema, and object endpoints all respond without authentication.

The vectorizer config baked into the schema confirms the operator:

```json
"text2vec-openai": {
  "isAzure": true,
  "model": "text-embedding-3-small",
  "resourceName": "oai-hrresume-emor-dev-inc",
  "deploymentId": "text-embedding-ada-002"
}
```

The resource name `oai-hrresume-emor-dev-inc` names the operator ("emor" = EMOR AI) and the subscription's original purpose ("hrresume"). The Azure deployment endpoint is `https://oai-hrresume-emor-dev-inc.openai.azure.com`. Any Azure cost monitoring, quota alerts, or key rotation on this subscription covers both the HR product and Stock.ai.

Schema creation timestamp: 2 February 2026. Frontend deployed 11 March 2026.

### F3 — 62 Arihant Capital Research Reports Served Without Authorization (HIGH)

GET /pdf/{filename} serves files by name with no authentication. The Weaviate TextCollections and ImageCollections hold filename metadata for 62+ equity analyst research reports published by Arihant Capital Markets. EMOR AI built Stock.ai's RAG corpus from these reports. No license is documented.

Sample of confirmed accessible files:

```
Bajaj Auto_Q1FY26 Result Update.pdf          (448KB confirmed download)
Birlasoft_Q1FY26 Result Update.pdf           (580KB)
HDFC Bank_Result Update_Q1FY26.pdf           (385KB)
ICICI_Bank_Q4FY25_Result_Update.pdf
Infosys Q2FY26 Result Update.pdf
Mahindra & Mahindra_Q1FY26 Result Update.pdf
Maruti_Q4FY25 Result Update.pdf
L&T Technology Q2FY26 Result Update.pdf
```

Full coverage spans Q4FY25 through Q2FY26 across 50+ Indian equities in automotive, banking, pharma, technology, and consumer sectors. Arihant Capital Markets is an Indian brokerage and investment bank. These reports carry distribution restrictions. They are indexed in full in the Weaviate vector database. A single unauthenticated HTTP request retrieves a current-quarter proprietary equity analyst report as a raw download.

### F4 — PostgreSQL Port 5432 TCP Open (SURFACE)

nmap and nc confirm port 5432 TCP open on the public interface. Credential state is unconfirmed. Default-credential probe requires manual execution: `PGPASSWORD=postgres psql -h 20.193.252.230 -p 5432 -U postgres -c "\l" --connect-timeout=8`. Severity withheld pending verification.

### F5 — Email Enumeration Oracle (MEDIUM)

POST /auth/forgot-password returns distinct responses for registered and unregistered email addresses. Registered accounts receive a password reset flow acknowledgment. Unknown addresses receive an error. User enumeration without authentication.

---

## Stack Map

| Port | Service | Auth | Severity |
|---|---|---|---|
| 80 | Flutter web app (Stock.ai v1.0.0) | None (public) | INFO |
| 5432 | PostgreSQL | TCP open, credential state unknown | SURFACE |
| 8000 | LangGraph FastAPI | Partial (see F1) | HIGH |
| 8080 | Weaviate 1.33.1 | None | HIGH |
| 8081 | Flutter web app (second instance) | None (public) | INFO |

---

## Operator Context

EMOR AI's public product is EMOR Voice, an AI receptionist for US small businesses in verticals including HVAC, dental, and gyms, priced at $149/month. Stock.ai is a separate product targeting Indian retail investors with AI-assisted equity research. It is not listed on emorai.com as of the survey date. The Weaviate schema timestamps show active development from February through March 2026. The multiple collection iterations (PyPdf2, uatnew, test) in the vector database are consistent with an early-stage build.

The HR/resume subscription name is the clearest operator signal in the stack. Stock.ai runs under billing and quota from a separate product line. Key rotation or quota exhaustion on `oai-hrresume-emor-dev-inc` affects both.

---

## Chain

The partial-auth failure opens conversation history and portfolio data for any registered user. The open Weaviate endpoint exposes the full document index, including image_base64 content and PDF metadata for all 62+ reports. The unprotected /pdf/{filename} endpoint turns indexed filenames into direct downloads. The three failures are independent access paths to overlapping data.

**See also:** [LangGraph Server Survey (2026-05-25)](../surveys/langgraph-server-survey-2026-05-25.md)
