# GraphRAG Process Safety API — Full Multi-Stack Auth-Off Exposure (Scaleway FR)

**Discovered:** 2026-05-09
**Host:** `51.159.4.28` (`51-159-4-28.rev.poneytelecom.eu`, Scaleway / Online.net dedicated server, Paris FR)
**Severity:** HIGH — five auth-off services on one VPS (orchestrator + LLM + vector DB + UI + storage), industrial process safety domain, operator path leaked
**Status:** Not yet disclosed

---

## Summary

A French operator running an industrial process safety knowledge management RAG application has deployed five separate AI/ML services on a single Scaleway dedicated server with no authentication on any layer. The exposure includes the orchestrator API (which leaks the operator's home directory path), the underlying LLM, the vector database, a web UI, and an object storage layer. The orchestrator's OpenAPI spec is public and enumerates the full webhook + reindex + chat surface.

This is structurally identical to the Klinikken.ai exposure (FastAPI proxy in front of Qdrant) but at greater scale: every component of the stack is independently reachable, and the operator's personal Google Drive content is being ingested via the orchestrator's webhook layer.

---

## Technical Detail

### Service map

| Port | Service | HTTP status | Notes |
|---|---|---:|---|
| 8000 | GraphRAG Process Safety API v3.0.0 (FastAPI) | 200 | OpenAPI public, 19 endpoints |
| 11434 | Ollama (qwen2.5:7b LLM, nomic-embed-text embedder) | 200 | embedding-capable |
| 6333 | Qdrant vector database | 200 | |
| 3000 | Web UI (likely Open WebUI) | 200 | |
| 9000 | Object storage (likely MinIO) | 307 redirect | |

### Orchestrator JSON root (`GET /` on port 8000)

```json
{
  "message": "GraphRAG Process Safety API",
  "version": "3.0.0",
  "llm_model": "qwen2.5:7b",
  "embed": "nomic-embed-text",
  "dossier_local": "/home/<redacted-username>/<redacted-folder-name>",
  "status": "running"
}
```

**Operator information leaked in JSON root:**

- Linux username: `<redacted-username>`
- Local document folder: `/home/<redacted-username>/<redacted-folder-name>`
- LLM in use: `qwen2.5:7b` (Alibaba Qwen 2.5, 7B parameter)
- Embedding model: `nomic-embed-text` (Nomic AI's open-weight 768-dim embedder)
- Application: GraphRAG (Microsoft's knowledge-graph + RAG framework)
- Domain: Process Safety (industrial — typically chemical / oil & gas / manufacturing safety)

### OpenAPI surface (19 endpoints, all auth-off)

```
POST /webhook/drive/initial-sync   Initial Google Drive root-folder ingest
POST /webhook/drive                Webhook receiver
GET  /webhook/drive/status         Sync status
POST /webhook/reprocess/local      Reprocess local corpus
POST /chat                         Chat with the corpus
GET  /history                      Chat history
GET  /chat/historique              Chat history (FR)
POST /chat/debug                   Debug-mode chat
GET  /                             Status (info disclosure above)
GET  /health                       Health
GET  /embedding/status             Embedding service status
GET  /orchestrator/status          Orchestrator status
GET  /me                           User identity
GET  /streams/status               Stream status
POST /reindex                      Trigger full reindex
POST /reindex-local                Trigger local-corpus reindex
POST /dossier/scan                 Scan dossier
GET  /dossier/status               Dossier status
POST /internal/notify              Internal notification trigger
```

The OpenAPI spec is available unauthenticated at `http://51.159.4.28:8000/openapi.json`. Endpoint descriptions are in French, confirming French operator/scope.

---

## Impact

| Impact | Mechanism |
|---|---|
| **Corpus extraction (data exposure)** | `POST /chat` with adversarial queries, `GET /history` for prior interaction logs |
| **Vector DB direct access** | Qdrant `:6333` is open — collections enumerable, vectors readable |
| **LLM compute theft** | Ollama `:11434` open — unlimited prompt-completion at operator's compute cost |
| **Drive corpus ingest abuse** | `POST /webhook/drive/initial-sync` likely re-syncs operator's Google Drive root content |
| **Reindex DoS** | `POST /reindex` triggers full corpus rebuild — repeatable DoS via expensive operation |
| **Storage bucket access** | Port 9000 redirects to MinIO/storage UI — likely document blob storage |
| **User identity leak** | `GET /me` returns user identity (auth-off, so reveals "default" user state) |

The combination of these exposures means an unauthenticated caller can:

1. Read the indexed process safety corpus (via /chat semantic search)
2. Inject documents into the corpus (via reindex/webhook layer)
3. Drain operator compute (via Ollama + reindex repeatedly)
4. Extract underlying vector embeddings (via Qdrant direct)
5. Likely access raw documents (via MinIO storage layer)

**Process Safety document context:** RAG-indexed process safety documentation in industrial settings typically covers vendor-confidential procedures, plant-specific equipment configurations, hazard analyses (HAZOP/LOPA), incident reports, MSDS/SDS sheets, and emergency response playbooks. Exposure of this corpus is operationally sensitive for the operator's clients/employer.

---

## Jurisdiction

- Scaleway Group (parent: ILIAD Group), Paris, France — host infrastructure operator
- French DPA: CNIL (Commission nationale de l'informatique et des libertés)
- GDPR applies if any PII is in the indexed corpus
- French Code du travail and confidentiality obligations may apply if the corpus contains employer-confidential industrial documentation
- ANSSI (French cyber agency) is the authority for industrial / critical-infrastructure incidents — process safety documentation potentially covered

---

## Remediation

1. **Immediate:** Bind all five services to localhost (`127.0.0.1`) instead of `0.0.0.0`. Use SSH tunneling or VPN for remote access.
2. **Add a reverse proxy with auth** (Caddy / Nginx + basic auth or OAuth2) in front of port 8000.
3. **Set Qdrant API key** (`QDRANT__SERVICE__API_KEY` env var) for port 6333.
4. **Disable Ollama public binding** — `OLLAMA_HOST=127.0.0.1:11434`.
5. **Audit the indexed corpus** for PII or employer-confidential content; assess GDPR / NDA notification obligation.
6. **Rotate any Google Drive OAuth tokens** if the webhook integration uses them — the auth-off public webhook means the integration may have been triggered by external callers.
7. **Long-term:** Move to a private VPC / firewalled deployment. The current model (raw Scaleway dedicated with public IP, all services bound to 0.0.0.0) cannot be made safe with only application-layer fixes.

---

## Discovery Context

Discovered during NuClide Research embedding-services OSINT survey (2026-05-09). Surfaced via asyncio targeted probe (`/tmp/embed-probe.py`) on 440 priority IPs derived from the 818-IP embedding-services survey pool. The `embed` field in the JSON root matched the embedding-API fingerprint. Subsequent port survey (8 candidate ports, no enumeration) confirmed the multi-service stacked exposure. Documented in `case-studies/commercial/embedding-services-cloud-survey-2026-05.md` as Finding F9.

---

## Disclosure Path

Operator email is not directly identifiable from the exposed surface (the `/me` endpoint was deliberately not queried — would have crossed the establish-vs-enumerate line). The Linux username `<redacted-username>` suggests a French/Maghrebi-name operator; combined with French OpenAPI text, this is consistent with a French researcher, consultancy, or small operator.

1. **Primary:** Scaleway abuse (`abuse@scaleway.com`) — they will pass to the customer of record for `51.159.4.28`
2. **If operator identifiable from disclosure path:** direct email
3. **Fallback (14 days unresponsive):** CNIL if PII confirmed; ANSSI cert-fr if industrial-criticality assessed
4. **Coordinated:** if process safety corpus belongs to a specific industrial client, that client should be informed via their normal vendor-security channel after the operator has had reasonable disclosure window

**Do not:** Query `/chat`, `/history`, `/me`, `/dossier/scan`, or any data-revealing endpoint. Exposure has been established via OpenAPI shape + port survey + JSON root response. Stop here.

---

## Operator Re-Identification Risk

The runtime-leaked Linux username + French scope + Process Safety + GraphRAG framework is a narrow-enough pattern that the operator may be identifiable via search engines / LinkedIn. **The username and home-folder name are redacted in this public draft** to avoid pre-disclosure operator re-identification via search engines. The unredacted version is held in `~/recon/embedding-shodan-2026-05-09/disclosures-unredacted/` and will be supplied directly to Scaleway abuse / the operator via the disclosure path. The disclosure should reach Scaleway abuse first, and the operator should be re-contacted via the operator's primary identity rather than via the exposed `/me` endpoint of the running service.
