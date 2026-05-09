# Klinikken.ai — Unauthenticated Vector Database API (Auth Bypass via Embedding Proxy)

**Discovered:** 2026-05-09  
**Host:** `37.27.185.38:8001` (Hetzner Online, `static.38.185.27.37.clients.your-server.de`)  
**Severity:** HIGH — Medical AI platform, full CRUD on vector database without credentials  
**Status:** Not yet disclosed

---

## Summary

Klinikken.ai's self-hosted vector database API is publicly accessible without authentication. The service acts as an embedding + retrieval proxy over a Qdrant vector database. While Qdrant itself (port 6333) requires an API key for collection access, the FastAPI embedding proxy (port 8001) has no authentication and exposes the full Qdrant dataset via its own endpoints.

This constitutes an auth-bypass: callers route through the unauthenticated proxy to access data that Qdrant's own API key would otherwise protect.

---

## Technical Detail

**Exposed API:** `http://37.27.185.38:8001`  
**Service title:** Klinikken.ai Vector Database API v1.0.0

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
| **Data exposure** | `POST /search` returns semantic search results over 32 collections of medical AI content |
| **Data injection** | `POST /upload` allows unauthenticated content injection into clinical AI responses |
| **Data destruction** | `POST /delete` and `DELETE /collections/` allow unauthenticated data deletion |
| **User enumeration** | `GET /collections/{user_id}` allows enumeration of user collection names |

With 32 Qdrant collections, this is a substantial medical knowledge base. Content likely includes clinic documentation, patient FAQs, clinical protocols, or patient-interaction records used to power Klinikken.ai's responses.

**Jurisdiction:** Norwegian GDPR (GDPR as implemented via Personopplysningsloven) and Helsepersonelloven apply if any personally identifiable or health-related data is in the vector store.

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

1. **Primary:** security contact via `klinikken.ai` — check for `security.txt`, security@ alias, or contact form
2. **Fallback:** Hetzner abuse (`abuse@hetzner.com`) with host IP
3. **If unresponsive (14 days):** Norwegian DPA (Datatilsynet) if patient data confirmed

**Do not:** Enumerate collections or execute searches — establish exposure, stop at health check.
