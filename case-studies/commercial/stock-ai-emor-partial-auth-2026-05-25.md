---
type: case-study
title: "Stock.ai — Partial-Auth Failure Exposes 62 Arihant Capital Reports and User Data"
date: 2026-05-25
severity: HIGH
sector: commercial
tags: [LangGraph, Weaviate, PostgreSQL, financial, India, Azure, partial-auth, RAG, earnings-reports]
summary: "An Indian fintech startup's stock research assistant exposes 62 proprietary Arihant Capital analyst reports and user conversation history. The developer built JWT authentication and left the individual resource endpoints unprotected."
---

# Stock.ai — Partial-Auth Failure Exposes 62 Arihant Capital Reports and User Data

**Date:** 2026-05-25
**Target:** 20.193.252.230
**ASN:** AS8075 Microsoft, Pune, Maharashtra, India
**Operator:** EMOR AI (emorai.com), Thane, Maharashtra, India
**Severity:** HIGH

---

## What Was Found

### F1 — Partial-Auth Failure on LangGraph API (HIGH)

The developer built JWT tokens, Google OAuth, password reset, and profile management. The Swagger UI shows padlock icons on list endpoints. The auth system works on those endpoints. It stops there.

Individual resource endpoints carry no security definition in the OpenAPI spec:

```
GET  /conversations/{conversation_id}
POST /conversations/new
DELETE /conversations/{conversation_id}
GET  /portfolio/{user_id}
GET  /pdf/{filename}
```

We created a conversation and read it back without a token:

```
POST http://20.193.252.230:8000/conversations/new
→ {"conversation_id": "a47769a9-1ce7-45b8-bc8c-e9ba2c97f2b5"}

GET http://20.193.252.230:8000/conversations/a47769a9-1ce7-45b8-bc8c-e9ba2c97f2b5
→ {"messages": [], "created_at": "2026-05-25T19:44:31", "updated_at": "2026-05-25T19:44:31"}
```

No token. No rejection. The pattern: auth on the list endpoint, nothing on the individual resource. A user_id from account signup reaches the unprotected `/portfolio/{user_id}`. A conversation UUID from the creation endpoint reaches the unprotected read and delete endpoints.

This is not a no-auth deployment. The developer knew auth was required and implemented it in parts. The gap is coverage, not intent.

### F2 — 62 Arihant Capital Analyst Reports Publicly Accessible (HIGH)

Weaviate's ImageCollections class holds images extracted from PDF research reports. The image filenames map directly to the PDF names served at `/pdf/{filename}`. No auth on either endpoint.

```
GET http://20.193.252.230:8000/pdf/Bajaj%20Auto_Q1FY26%20Result%20Update.pdf
→ HTTP 200, 448,872 bytes
```

The corpus: 62 analyst research reports from Arihant Capital Markets. Coverage: Q4FY25 through Q2FY26. NSE-listed companies include Bajaj Auto, HDFC Bank, ICICI Bank, Infosys, Maruti Suzuki, Mahindra & Mahindra, and 56 others.

Arihant Capital Markets (arihantcapital.com) is a SEBI-registered broker and research firm. Their reports are distributed to registered clients. The schema and endpoint responses contain no authorization record from Arihant Capital for this use. The reports are indexed and served by a third party.

### F3 — Weaviate Vector Database Open (HIGH)

Weaviate 1.33.1 runs on port 8080 with no authentication. Seven data classes, all readable:

| Class | Contents |
|---|---|
| TextCollections | Financial PDF text, stock, quarter, year, page_number |
| TextEmbeddings | Same corpus, different pipeline iteration |
| ImageCollections | PDF images with base64 data |
| ImageEmbeddings | Image vectors |
| DocumentCollectionPyPdf2 | PyPDF2 parser iteration |
| DocumentCollectionuatnew | UAT test collection |
| ImageCaptiontest | Test collection |

Four collection iterations mark the developer's parsing history. Each full schema ingest from a different PDF parsing approach remains live.

```
GET http://20.193.252.230:8080/v1/schema
→ HTTP 200, full schema with vectorizer config
```

The vectorizer config in every collection:

```json
"text2vec-openai": {
  "isAzure": true,
  "resourceName": "oai-hrresume-emor-dev-inc",
  "deploymentId": "text-embedding-ada-002"
}
```

### F4 — PostgreSQL TCP-Open on Public Interface (SURFACE)

Port 5432 is TCP-accessible from the public internet. Credential state is unconfirmed.

### F5 — Email Enumeration Oracle (MEDIUM)

`POST /auth/forgot-password` returns distinct error messages for registered versus unregistered email addresses. Accounts are enumerable without authentication.

---

## Operator Attribution

The Azure OpenAI resource name `oai-hrresume-emor-dev-inc` is baked into every Weaviate vectorizer config. It identifies the operator.

EMOR AI (emorai.com) is based in Thane, Maharashtra. Their primary product is EMOR Voice, an AI receptionist for US small businesses at $149 per month. Stock.ai is a secondary product for Indian retail investors. The app was not publicly marketed on emorai.com as of 2026-05-25.

The resource name carries the history: the subscription started as an HR/resume application (`hrresume`) and the Azure OpenAI resource was reused for the stock project. Azure region: Pune.

Weaviate schema creation: February 2, 2026. Flutter frontend deployment: March 11, 2026. The backend ran 38 days before the frontend went live.

---

## Stack

Port 22: SSH. Ports 80/8081: Flutter web app (Stock.ai v1.0.0). Port 5432: PostgreSQL. Port 8000: LangGraph FastAPI. Port 8080: Weaviate 1.33.1, git hash c87f308, single node, 36 modules loaded.

Three persistence layers: LangGraph holds conversation state. Weaviate holds the vector index. PostgreSQL holds user accounts and portfolios. All three are surface-accessible.

The app is a stock research assistant. Users ask questions about Indian equities. The LangGraph agent retrieves content from Weaviate and returns answers. The Weaviate corpus is the 62 Arihant Capital reports.

---

## Second Notification Target

Arihant Capital Markets holds the material interest. Their reports are indexed and served by an application without a visible authorization record. The reports cover active NSE-listed securities.
