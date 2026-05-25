# Stock.ai (EMOR AI) — Complete Investigation Notes

**Host:** 20.193.252.230
**Cloud:** Microsoft Azure — Pune, Maharashtra, India (AS8075)
**Operator:** EMOR AI — emorai.com — Thane, Maharashtra, India
**Contact:** inquiries@emorai.com
**App name:** Stock.ai v1.0.0
**Status:** FULLY MAPPED — case study ready
**Priority:** 1

---

## Confirmed Services

| Port | Service | Auth |
|---|---|---|
| 22 | SSH | KEY (assumed) |
| 80 | Flutter web app — Stock.ai v1.0.0 | NONE (public frontend) |
| 5432 | PostgreSQL | TCP OPEN — credential state unconfirmed |
| 8000 | LangGraph FastAPI — "LangGraph Conversational Stock Analyzer API is running" | PARTIAL (see below) |
| 8080 | Weaviate 1.33.1 — /v1 root + all endpoints | NONE |
| 8081 | Flutter web app — second instance | NONE (public frontend) |

nmap scan: `nmap -sV -p 22,80,443,5432,6379,8000,8080,8081 20.193.252.230`

---

## Operator Attribution — CONFIRMED

Azure OpenAI resource name `oai-hrresume-emor-dev-inc` baked into Weaviate vectorizer config:

```json
"text2vec-openai": {
  "isAzure": true,
  "model": "text-embedding-3-small",
  "resourceName": "oai-hrresume-emor-dev-inc",
  "deploymentId": "text-embedding-ada-002",
  "baseURL": "https://api.openai.com"
}
```

- **"emor"** → EMOR AI (emorai.com) — Thane, Maharashtra, India
- **"hrresume"** → original purpose of this Azure subscription was HR/resume app. Developer reused the Azure OpenAI resource for Stock.ai.
- **"dev-inc"** → development / incorporated
- Azure deployment URL: `https://oai-hrresume-emor-dev-inc.openai.azure.com`
- Azure region: Pune (AS8075 Microsoft — confirmed via ASN lookup)

**EMOR AI profile:**
- Primary product: EMOR Voice — AI receptionist for US small businesses (HVAC, dental, gyms) — $149/mo starter
- Secondary product: Stock.ai — Indian financial research assistant (not yet publicly marketed)
- Backend deployment: 2 February 2026 (Weaviate schema timestamp)
- Frontend deployment: 11 March 2026 (Flutter web app)

---

## Confirmed Findings

### F1 — Partial-Auth Failure on LangGraph API (HIGH)

Developer built full JWT + Google OAuth system but left individual resource read endpoints unprotected. Pattern:

| Endpoint | Auth Required | Notes |
|---|---|---|
| GET /conversations | YES (lock in OpenAPI spec) | List requires Bearer token |
| GET /conversations/{id} | NO | Individual read — no security definition |
| DELETE /conversations/{id} | NO | Individual delete — no security definition |
| POST /conversations/new | NO | Create — open |
| GET /portfolio/{user_id} | NO | Read by user_id — no security definition |
| GET /pdf/{filename} | NO | File serve — no security definition |
| GET /api/chart/{symbol} | NO | Market data — open by design |

**Verified:**
- POST /conversations/new → `{"conversation_id":"a47769a9-1ce7-45b8-bc8c-e9ba2c97f2b5"}` — no auth required
- GET /conversations/a47769a9-1ce7-45b8-bc8c-e9ba2c97f2b5 → `{"messages":[],"created_at":"...","updated_at":"..."}` — no auth required
- GET /portfolio/{user_id} → returns portfolio data or "Portfolio not found" — no auth, user_id enumerable

This is a distinct failure class: not "no auth" across the board, but "auth added at the list layer, missed at the resource layer." Individual resource IDs (conversation UUIDs, user_ids) are guessable or obtainable via signup.

### F2 — Weaviate Vector DB — Full Open (HIGH)

Weaviate 1.33.1 (git hash c87f308), single node, HEALTHY, no auth on any endpoint.

Seven data classes:

| Class | Contents |
|---|---|
| TextCollections | Financial PDF text — title, content, filename, stock, quarter, year, page_number, source |
| TextEmbeddings | Same schema, different pipeline iteration |
| ImageCollections | PDF images — filename, stock, quarter, year, page_number, picture_id, image_base64, caption, title, content, source |
| ImageEmbeddings | Image vectors — same fields + image_base64 |
| DocumentCollectionPyPdf2 | PyPDF2 parser iteration |
| DocumentCollectionuatnew | UAT test collection |
| ImageCaptiontest | Test collection |

Graphql aggregate, schema, and object endpoints all respond without auth. Object-level data confirmed via /v1/graphql.

**36 modules loaded** — full feature set including CLIP image vectorizer (multimodal search).

### F3 — Arihant Capital Research Reports Publicly Accessible (HIGH)

62+ proprietary analyst research reports indexed in Weaviate and served via GET /pdf/{filename} without auth.

**Confirmed accessible PDFs (sample):**

```
Bajaj Auto_Q1FY26 Result Update.pdf        — 448KB confirmed download
Birlasoft_Q1FY26 Result Update.pdf         — confirmed (prior probe: 580KB)
HDFC Bank_Result Update_Q1FY26.pdf         — confirmed (prior probe: 385KB)
Ashok Leyland_Result Update_Q1FY26.pdf
Bandhan Bank_Q1FY26_Result Update.pdf
CanFin Homes_Q1FY26 Result Update.pdf
Coforge_Q1FY26 Result Update.pdf
FSL_Q1FY26 Result Update.pdf
Gabriel India ltd_Q1FY26 Result Update.pdf
Gokaldas Exports-Q1FY26_Result Update.pdf
Greaves Cotton_Result Update Q1FY26.pdf
Heritage Foods_Q2FY26_Result Update.pdf
HeroMotoCorp Q4FY25_Result Update.pdf
HFCL_Ltd_Q2FY26_Result_update.pdf
Home First_Result_update Q4FY25.pdf
ICICI_Bank_Q4FY25_Result_Update.pdf
INFY_Q2FY26_Result_Update.pdf
India Glycols Ltd Q4FY25 Result update.pdf
Indian_Bank_Q2FY26 Result_Update.pdf
Indo Count_Q4FY25 Result Update.pdf
Jubilant Pharmova_Result Update_Q2FY25.pdf
Krsnaa Diagnostics Ltd_Result Update_Q1FY26.pdf
L&T_Technology_Q2FY26_Result_Update.pdf
Mahindra & Mahindra_Q1FY26 Result Update.pdf
Mahindra & Mahindra_Q4FY25 Result Update.pdf
Manappuram Finance_Q4FY25 Result Update.pdf
Maruti_Q1FY26 Result Update.pdf
Maruti_Q4FY25 Result Update.pdf
Maruti_Suzuki_Q2FY26_Result_Update.pdf
Meghmani Organics_Result Update_Q1FY26.pdf
Minda Corporation-Q1FY26 Result Update.pdf
MTAR Technologies Q1FY26 Result update.pdf
MTAR Technologies Q3FY25 Result update.pdf
Nuvoco-Q2FY25-Result Update.pdf
Orient Bell Ltd_Q1FY26_Result_Update.pdf
Orient Electric Ltd Q1FY25 Result update.pdf
Orient Electric Ltd Q1FY26 Result update.pdf
PSP Projects Ltd Q1FY26 Result update.pdf
PSP_Projects_Ltd_Q2FY26_Result_update.pdf
Parag Milk Foods Q4FY25 Result Update.pdf
Persistent_Q1FY26 Result Update.pdf
Persistent_Q4FY25 Result Update.pdf
Piramal Enterprise_Result Update_Q1FY26.pdf
Piramal Enterprise_Result Update_Q4FY25.pdf
Pitti Engineering Ltd Q1FY26 Result update.pdf
Rallis India Ltd-Q4FY25-Result Update.pdf
Ramco Cements-Q1FY26-Result Update.pdf
Ramco Cements-Q2FY25-Result Update.pdf
Raymond Lifestyle_Q1FY26 Result Update.pdf
Route Mobile Ltd-Q1FY26 result update.pdf
Route Mobile Ltd-Q4FY25 result update.pdf
```

All coverage Q4FY25–Q2FY26. These are Arihant Capital Markets analyst research reports — proprietary equity research not for public distribution.

**Second notification target:** Arihant Capital Markets (arihantcapital.com) — their research is indexed and served by a third-party application without apparent authorization.

### F4 — PostgreSQL TCP Open on Public Interface (SURFACE)

Port 5432 TCP-open confirmed (nmap + nc). Credential state unconfirmed — default-credential probe blocked by environment. Nick can run: `! PGPASSWORD=postgres psql -h 20.193.252.230 -p 5432 -U postgres -c "\l" --connect-timeout=8`

### F5 — Email Enumeration Oracle (MEDIUM)

POST /auth/forgot-password returns distinct error messages for registered vs. unregistered accounts. User enumeration without authentication.

### F6 — Open Signup Leaks 17 Onboarding Questions (LOW)

POST /auth/signup — open registration, no invite required. Signup response includes 17 pre-seeded onboarding questions that reveal the app's intended user flow and data model. No PII exposed beyond what user submits.

---

## Weaviate Infrastructure Detail

- Version: 1.33.1
- Git hash: c87f308
- Node name: node1 (single-node deployment)
- Status: HEALTHY
- Batch stats: queueLength 0, ratePerSecond 54
- Shards: null (single node, no shard distribution)
- 36 modules loaded (text2vec-openai, multi2vec-clip, generative-openai, etc.)
- Redis (6379, 6380): connection refused from external — internal only

---

## LangGraph API Endpoints — Full Map

**Conversations:**
- GET /conversations — list (auth required)
- GET /conversations/{conversation_id} — read (NO AUTH)
- POST /conversations/new — create (NO AUTH)
- DELETE /conversations/{conversation_id} — delete (NO AUTH)
- DELETE /conversations/delete — delete (auth required)

**Authentication:**
- POST /auth/signup — open registration
- POST /auth/signin — login + JWT token
- POST /auth/google — Google OAuth
- POST /auth/forgot-password — email enum oracle
- POST /auth/reset-password, /change-password
- POST /auth/profile-update, /refresh, /logout
- GET /auth/profile-image/{file_id}

**Portfolio:**
- GET /portfolio/{user_id} — read by ID (NO AUTH)

**Chart:**
- GET /api/chart/{symbol} — OHLCV market data (open by design)

**Files:**
- GET /pdf/{filename} — serve PDF by name (NO AUTH — confirmed)

---

## Development State

Active build — not a deployed product:
- Multiple Weaviate collection iterations (PyPdf2, uatnew, test) visible from pipeline iteration
- Schema auto-generated timestamp: Mon Feb 2 13:20:03 2026
- Frontend deployed 11 March 2026
- App not publicly marketed on emorai.com as of 2026-05-25

---

## Pending

- [ ] GET /portfolio/{real_user_id} — find a real user_id (try sequential integers, or via forgot-password enum)
- [ ] GET /auth/profile-image/{file_id} — confirm format, probe for enumeration
- [ ] PostgreSQL default credential probe (Nick must run manually — env blocks psql)
- [ ] GitHub authenticated search: `oai-hrresume-emor-dev-inc` (source code leak check)
