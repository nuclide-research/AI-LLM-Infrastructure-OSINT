# Klinikken.ai: Unauthenticated Vector Database API (Auth Bypass via Embedding Proxy)

**Discovered:** 2026-05-09  
**Host:** `37.27.185.38:8001` (Hetzner Online, `static.38.185.27.37.clients.your-server.de`)  
**Severity:** **CRITICAL**, confirmed populated psychotherapy session-notes corpus; GDPR Article 9 special-category mental-health data; user_id partition broken (corpus reachable by guessing `user_id=1`); IDOR-class broken access control; operator's own OpenAPI schema documents `user_id` as *"Bruger ID for isolation"* yet does not authenticate the field; `/search` returns original document text in `SearchResult.text`, making the endpoint a direct corpus-extraction primitive. Severity escalated from HIGH to CRITICAL on 2026-05-09 14:11 UTC after Test A (collection-name enumeration only, no content read) confirmed corpus is populated with clinical session content.  
**Status:** Not yet disclosed

---

## Summary

Klinikken.ai's self-hosted vector database API is publicly accessible without authentication. The service is the retrieval-augmented memory layer of a Danish clinical AI platform that records and indexes **psychotherapy session notes**. Each therapy session generates one Qdrant collection of chunked text, named `notes_therapist_<therapist_id>_session_<session_uuid>`. The FastAPI embedding proxy (port 8001) wraps a Qdrant backend (port 6333), and the proxy strips Qdrant's API-key authentication, exposing the full corpus via its own endpoints to anyone with curl.

The exposed corpus is GDPR Article 9 special-category health data. Mental-health session content is the most sensitive sub-class of health data, and Danish Sundhedsloven §40 confidentiality applies absolutely. Verification (Test A, 2026-05-09 14:11 UTC), collection-name enumeration only, no document content read, confirmed 28 populated session-notes collections under `user_id=1` (the system's main tenant) with at least 11 distinct therapist IDs visible in the collection-name metadata, and at least ~78 vector points (= ~78 stored text chunks of session content) in that one user_id alone.

This is a two-layer failure:

1. **Auth bypass**, callers route through the unauthenticated FastAPI proxy on port 8001 to reach data that Qdrant's own API key on port 6333 would otherwise protect.
2. **Broken access control / IDOR**, the proxy's `user_id` parameter is documented as `"Bruger ID for isolation"` in the operator's own OpenAPI spec, but is treated as a caller-supplied path parameter rather than an authenticated session principal. Any caller can iterate user_id values; we found the populated tenant on the first guess (`user_id=1`).

---

## Technical Detail

**Exposed API:** `http://37.27.185.38:8001`  
**Service title:** Klinikken.ai Vector Database API v1.0.0 (OpenAPI 3.1)
**Service description (Danish, from `/openapi.json`):** *"Embeddings og semantic search service med bruger-isolation"*. "Embeddings and semantic search service with user-isolation"
**Swagger UI:** `http://37.27.185.38:8001/docs`
**Server:** uvicorn (FastAPI)

The service's own description states user-isolation as a design property, and every collection-scoped endpoint takes `user_id` as a path parameter (`/collections/{user_id}`, `DELETE /collections/{user_id}/{collection_name}`). However, **`user_id` is supplied by the caller**: there is no authentication and no session binding the caller to a specific user_id, so the user-isolation primitive is unenforced. This is the IDOR class. The system models users, but anyone can substitute any user_id and access that user's collections. The operator built the structure for per-user data partitioning (consistent with the medical-AI use case requiring per-patient or per-clinician scoping) but did not implement the access control layer that prevents user impersonation.

### Verification: corpus is populated and unauthenticated (Test A, 2026-05-09)

Reproducible by the operator with a single curl. We deliberately listed collection NAMES only and never issued a `/search` to read document content:

```bash
$ curl http://37.27.185.38:8001/collections/1
{"user_id":"1","total":28,"collections":[
   {"name":"notes_therapist_<id>_session_<uuid>","points_count":N,...},
   ... 28 entries ...
]}
```

Findings (full unredacted output supplied to operator separately; redacted here to protect therapist + session identifiers ahead of operator notification):

- 28 collections returned under `user_id=1` (no auth header sent)
- All 28 match the pattern `notes_therapist_<numeric_therapist_id>_session_<32_hex_session_uuid>`
- 11 distinct therapist IDs visible in the metadata, mostly clustered in a 7-figure auto-incremented range plus one anomalously low ID
- `points_count` per collection: 1–6 (= chunked vector points of stored session text)
- `/health` reports 32 total Qdrant collections; 28 are under `user_id=1`, 4 under user_id values we did not attempt to enumerate
- All other guessed user_ids (`default`, `test`, `demo`, `admin`, `klinikken`, `anders`, `user`, `0`, `root`, `global`, `public`, `main`, `shared`) returned `{"collections":[],"total":0}`. System accepted any user_id, returning empty for unknown values, populated for `1`

This is sufficient evidence to confirm: (a) the corpus is populated with clinical session content, (b) the user_id partition is not a security boundary, (c) `user_id=1` is the system's main tenant. We did not call `/search`, `/upload`, or `/delete`.

### Health response (no auth required):
```json
{
  "status": "healthy",
  "qdrant": {
    "connected": true,
    "host": "qdrant",
    "port": 6333,
    "collections": 32
  },
  "embedding_model": {
    "name": "paraphrase-multilingual-MiniLM-L12-v2",
    "dimension": 384
  }
}
```

### Exposed endpoints (all unauthenticated):
```
GET  /              Status (service, model, embedding dimension)
GET  /health        Backend health including Qdrant state and collection count
POST /upload        Upload document → embed → store in Qdrant
POST /search        Semantic search across all stored documents
POST /delete        Delete document from vector store
GET  /collections/{user_id}           List collections for any user ID
DELETE /collections/{user_id}/{name}  Delete collections for any user ID
```

### OpenAPI schemas (publicly available at `/openapi.json`):

The schemas confirm the user-isolation design intent and reveal that the `/search` endpoint returns original document text, not just scores. Quoted directly from the spec:

`DocumentUpload`:
```
user_id          → "Bruger ID for isolation"   ← caller-controlled, no auth
collection_name  → example: 'chatbot_knowledge'
text             → "Tekst der skal chunkes og embeddes"
metadata         → free-form object
```

`SearchQuery`:
```
user_id          → "Bruger ID for isolation"   ← caller-controlled, no auth
collection_name  → required
query            → "Søgeforespørgsel"
limit            → up to 100 per request
score_threshold  → 0–1 (set to 0 to dump regardless of similarity)
```

`SearchResult`:
```
document_id, text, score, metadata          ← text is the raw chunk, not an embedding
```

The `text` field in `SearchResult` is the original document chunk in plain text, returned directly to any unauthenticated caller. `/search` is therefore a literal corpus-extraction primitive: an attacker can iterate user_id values, enumerate `collection_name`s via `GET /collections/{user_id}`, then issue broad queries with `score_threshold=0` and `limit=100` to dump arbitrary user_id collection content.

### Qdrant backend (port 6333):
```
GET /healthz → "healthz check passed"      (no auth)
GET /collections → 401 Requires API key   (auth present)
```

The proxy strips Qdrant's auth. An attacker with access to port 8001 bypasses the Qdrant API key entirely.

---

## Impact

| Impact | Description |
|---|---|
| **IDOR / broken access control** | `GET /collections/{user_id}` and `DELETE /collections/{user_id}/{name}` accept any user_id without authentication. The operator's own description claims user-isolation; the implementation does not enforce it. Cross-user data access is achievable by simply changing the user_id path parameter. |
| **Data exposure** | `POST /search` returns semantic search results over 32 collections of medical AI content |
| **Data injection** | `POST /upload` allows unauthenticated content injection into clinical AI responses (DocumentUpload schema is publicly documented) |
| **Data destruction** | `POST /delete` and `DELETE /collections/{user_id}/{name}` allow unauthenticated deletion at document and collection scope |
| **User enumeration** | `GET /collections/{user_id}` allows iteration of user_id space to enumerate every user's collection names |
| **Schema disclosure** | `DocumentUpload`, `SearchQuery`, `SearchResult`, `DeleteDocument` schemas published at `/openapi.json` — full API contract without authentication |

With 32 Qdrant collections, this is a substantial medical knowledge base. Content likely includes clinic documentation, patient FAQs, clinical protocols, or patient-interaction records used to power Klinikken.ai's responses.

**Jurisdiction:** Danish GDPR (GDPR as implemented via Databeskyttelsesloven). Operator is Klinikken.ai ApS (CVR 45899071), registered in Faxe, Denmark. Danish Datatilsynet (`dt@datatilsynet.dk`) is the supervisory authority.

**GDPR Article 9 applies**, the corpus contains clinical psychotherapy session notes per Test A's collection-name evidence. Mental-health data is special-category. Article 32 (security of processing) requires "appropriate technical measures"; an unauthenticated, internet-exposed retrieval API does not satisfy this. Article 33 requires breach notification to the supervisory authority within 72 hours of the controller becoming aware. **The 72-hour clock starts on Klinikken.ai ApS at the moment this disclosure is delivered to them.**

**Sundhedsloven §40** (patient confidentiality) and the Danish **bekendtgørelse om informationssikkerhed for behandling af personoplysninger på sundhedsområdet** (executive order on information security in the health sector) impose additional duties beyond GDPR for clinical data. Therapist-patient confidentiality under Danish law is among the strongest legal-professional confidentiality privileges and is not waivable by the controller.

---

## Remediation

1. **Immediate:** Add authentication to the FastAPI proxy (e.g., `Authorization: Bearer <token>` header check, or API key query parameter)
2. **Preferred:** Put the embedding proxy behind a reverse proxy that enforces auth at the network boundary
3. **Verify:** Audit Qdrant collections for PII or patient data; assess GDPR notification obligation
4. **Long-term:** Ensure internal services (Qdrant, embedding proxy) are not exposed on public interfaces; bind to localhost or internal VPC only

---

## Discovery Context

Discovered during NuClide Research AI infrastructure OSINT survey (2026-05-09). Host found via Shodan query `http.html:"embedding_dimension"` and confirmed via targeted HTTP probe. Part of the broader embedding services survey documented at `case-studies/commercial/embedding-services-cloud-survey-2026-05.md`.

---

## Disclosure Path

**Operator contact candidates (WHOIS):**
- WHOIS registrant + admin: **Anders Colding-Jørgensen**. `anderscolding@gmail.com`
- WHOIS organization: **Mindhouse**, Jernbanegade 8G, 4600 Køge, Denmark
- Operating company: **Klinikken.ai ApS**, Vemmetoftevej 38, 4640 Faxe, CVR 45899071

**WHOIS organization (Mindhouse, Køge) and operating company (Klinikken.ai ApS, Faxe) are at different addresses.** Anders may be founder/director of Klinikken.ai ApS, a contractor/consultant, or a stale registrant. **Pre-send verification:** confirm via LinkedIn / `klinikken.ai/about/` / Danish CVR registry (`cvr.dk` lookup of CVR 45899071 returns current directors) that Anders is currently associated with Klinikken.ai ApS before emailing the gmail address. If verification fails, switch to contact form first and use the gmail only as a fallback for the disclosure copy.

1. **Primary (after pre-send verification):** Email `anderscolding@gmail.com`
2. **Fallback (or primary if verification fails):** Contact form at `https://klinikken.ai/contact/`
3. **Secondary fallback:** Hetzner abuse (`abuse@hetzner.com`) with host IP `37.27.185.38`
4. **If unresponsive (14 days):** Danish DPA (Datatilsynet DK, `dt@datatilsynet.dk`) if health data confirmed

**Do not:** Enumerate collections or execute searches. Establish exposure, stop at health check.
