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

**Jurisdiction:** Danish GDPR (GDPR as implemented via Databeskyttelsesloven). Operator is Klinikken.ai ApS (CVR 45899071), registered in Faxe, Denmark. Danish Datatilsynet is the supervisory authority. If the vector store contains health data, Sundhedsloven and Bekendtgørelse om elektronisk datakommunikation apply.

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
- WHOIS registrant + admin: **Anders Colding-Jørgensen** — `anderscolding@gmail.com`
- WHOIS organization: **Mindhouse**, Jernbanegade 8G, 4600 Køge, Denmark
- Operating company: **Klinikken.ai ApS**, Vemmetoftevej 38, 4640 Faxe, CVR 45899071

**WHOIS organization (Mindhouse, Køge) and operating company (Klinikken.ai ApS, Faxe) are at different addresses.** Anders may be founder/director of Klinikken.ai ApS, a contractor/consultant, or a stale registrant. **Pre-send verification:** confirm via LinkedIn / `klinikken.ai/about/` / Danish CVR registry (`cvr.dk` lookup of CVR 45899071 returns current directors) that Anders is currently associated with Klinikken.ai ApS before emailing the gmail address. If verification fails, switch to contact form first and use the gmail only as a fallback for the disclosure copy.

1. **Primary (after pre-send verification):** Email `anderscolding@gmail.com`
2. **Fallback (or primary if verification fails):** Contact form at `https://klinikken.ai/contact/`
3. **Secondary fallback:** Hetzner abuse (`abuse@hetzner.com`) with host IP `37.27.185.38`
4. **If unresponsive (14 days):** Danish DPA (Datatilsynet DK, `dt@datatilsynet.dk`) if health data confirmed

**Do not:** Enumerate collections or execute searches — establish exposure, stop at health check.
