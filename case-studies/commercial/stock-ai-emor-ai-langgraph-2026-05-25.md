---
type: case-study
title: "Stock.ai (EMOR AI) — Partial-Auth Failure, Open Vector Store, and Third-Party Research Leak"
date: 2026-05-25
severity: HIGH
sector: commercial
tags: [LangGraph, Weaviate, partial-auth, India, Azure, financial, PDF-serve, equity-research, agent-framework]
summary: "An Indian fintech startup's LangGraph stock analysis app authenticates the list layer but leaves individual resource endpoints wide open. 62 proprietary Arihant Capital analyst reports are accessible without auth through a co-deployed Weaviate instance."
---

# Stock.ai (EMOR AI) — Partial-Auth Failure, Open Vector Store, and Third-Party Research Leak

**Date:** 2026-05-25
**Target:** 20.193.252.230
**ASN:** AS8075 Microsoft Azure, Pune, Maharashtra, India
**Severity:** HIGH

---

## What Was Found

### F1 — Partial-Auth Failure on LangGraph API (HIGH)

Port 8000 serves a FastAPI/LangGraph backend for Stock.ai v1.0.0 with a real JWT + Google OAuth implementation. The developer added authentication correctly on list-level routes and then missed every individual resource route. The result is a selective auth bypass across the API:

| Endpoint | Auth |
|---|---|
| GET /conversations | Required — lock in OpenAPI spec |
| GET /conversations/{id} | None |
| POST /conversations/new | None |
| DELETE /conversations/{id} | None |
| GET /portfolio/{user_id} | None |
| GET /pdf/{filename} | None |

```
POST http://20.193.252.230:8000/conversations/new
→ {"conversation_id":"a47769a9-1ce7-45b8-bc8c-e9ba2c97f2b5"}

GET http://20.193.252.230:8000/conversations/a47769a9-1ce7-45b8-bc8c-e9ba2c97f2b5
→ {"messages":[],"created_at":"...","updated_at":"..."}
```

No Bearer token required on either call. User IDs are guessable (sequential integers) or derivable via the email-oracle at `/auth/forgot-password`, which returns distinct error messages for registered versus unregistered accounts.

Distinct auth failure class. The developer thought about authentication and built it. The list route is protected. The individual resource routes are not. At scale this pattern appears in apps where auth middleware is applied at the router prefix level and resource routes are registered outside that prefix.

### F2 — Weaviate Vector DB Open (HIGH)

Port 8080 serves Weaviate 1.33.1 (commit c87f308) with no auth on any endpoint. Seven document collections are enumerable and readable via GraphQL and the REST API:

| Collection | Contents |
|---|---|
| TextCollections | Financial PDF text — title, content, filename, stock, quarter, year |
| TextEmbeddings | Same schema, second pipeline iteration |
| ImageCollections | PDF images — base64-encoded, captioned |
| ImageEmbeddings | Image vectors |
| DocumentCollectionPyPdf2 | PyPDF2 parser iteration |
| DocumentCollectionuatnew | UAT test collection |
| ImageCaptiontest | Test collection |

The multiple collection iterations make the development history readable: three distinct pipeline experiments (PyPDF2, uatnew, production) all left exposed in the same instance.

Vectorizer config in the Weaviate schema reveals the operator:

```json
"text2vec-openai": {
  "isAzure": true,
  "resourceName": "oai-hrresume-emor-dev-inc",
  "deploymentId": "text-embedding-ada-002"
}
```

`oai-hrresume-emor-dev-inc`: the Azure OpenAI resource name encodes the company (`emor`), an earlier product (`hrresume`), and the Azure environment (`dev-inc`). EMOR AI, Thane, Maharashtra, markets an AI phone receptionist for US small businesses under the EMOR Voice brand. Stock.ai is an unreleased second product.

### F3 — 62 Arihant Capital Analyst Reports Accessible Without Auth (HIGH)

The `/pdf/{filename}` endpoint serves files from the document corpus by filename alone, no auth. The Weaviate schema exposes the filename list. 62 proprietary Arihant Capital Markets equity research reports covering Q4FY25 through Q2FY26 are accessible:

```
GET http://20.193.252.230:8000/pdf/Bajaj%20Auto_Q1FY26%20Result%20Update.pdf
→ 200 OK — 448KB PDF binary, full analyst report
```

Sample report range: Bajaj Auto, Birlasoft, HDFC Bank, INFY, ICICI Bank, L&T Technology, Mahindra & Mahindra, Maruti Suzuki, Persistent Systems, Piramal Enterprises. 52 filings confirmed, all production analyst reports.

These are not public documents. Arihant Capital distributes these to registered clients. EMOR AI's Stock.ai indexed them to power the RAG-backed financial query system and serves them via an unauthenticated file endpoint.

The finding involves two parties: EMOR AI (the deployment operator) and Arihant Capital (whose research is indexed and served without evident authorization). Both require independent notification.

### F4 — PostgreSQL TCP Open (SURFACE)

Port 5432 accepts connections from the public internet. Credential state not probed. Stock.ai uses PostgreSQL as the user/conversation state backend; the Weaviate schema was populated on 2 February 2026.

---

## Stack Map

| Port | Service | Version | Auth | Severity |
|---|---|---|---|---|
| 8000 | LangGraph FastAPI — Stock.ai | 1.0.0 | Partial (list routes only) | HIGH |
| 8080 | Weaviate | 1.33.1 | None | HIGH |
| 5432 | PostgreSQL | — | TCP open, credential state unknown | SURFACE |
| 80/8081 | Flutter web app | — | Public frontend | — |

---

## Attribution

EMOR AI, Thane, Maharashtra, India. Contact: inquiries@emorai.com. Azure OpenAI resource `oai-hrresume-emor-dev-inc` in Pune (AS8075). Company site: emorai.com. App deployment timestamp: schema created 2 February 2026, frontend deployed 11 March 2026.

---

## Thesis Placement

Partial-auth is a variant of the auth-on-default failure class. The developer implemented JWT correctly on some routes and missed others. Authentication intent was present; execution was incomplete. At the data layer, Weaviate's default no-auth posture (Insight #13) propagates to the deployment regardless of what the application layer does. Two independent failures on the same host.

The Arihant Capital research exposure is a third-party data-class finding: operator A indexes operator B's proprietary content without evident authorization. EMOR AI's data exposure creates a secondary leak of Arihant Capital's commercial research product.

**See also:** [LangGraph Server Survey (2026-05-25)](langgraph-server-survey-2026-05-25.md) · [LangGraph Deployment Gap](langgraph-deployment-gap-survey-2026-05-25.md)
