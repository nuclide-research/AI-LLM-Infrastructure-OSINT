# Embedding-Only Stack (South America) — Working Notes

**Host:** 138.219.43.172
**Cloud:** Unknown
**Timezone:** UTC-03:00 (Brazil / Argentina)
**Status:** Initial probe complete
**Priority:** 10

---

## Confirmed Services

| Port | Service | Auth |
|---|---|---|
| 8000 | LangGraph FastAPI — "LangGraph API" v1.0.0 | NONE |
| 11434 | Ollama (embedding models only) | NONE |
| 9001 | MinIO Console | UNKNOWN (login page served — may enforce at login) |

## Root Response

```json
{
  "service": "LangGraph API",
  "version": "1.0.0"
}
```

Swagger UI at `/docs`.

## Ollama Models (embedding-only — no generative LLM loaded)

| Model | Size | Type |
|---|---|---|
| paraphrase-multilingual:latest | 277M | BERT/F16 |
| snowflake-arctic-embed2:latest | 567M | BERT/F16 |
| nomic-embed-text:latest | 137M | standard embedding |

No generative LLMs in the model list. This is a pure embedding pipeline — LangGraph uses Ollama only for semantic search/retrieval, not for generation. A separate generative model (likely a cloud API) handles the output step.

## MinIO Console

Port 9001 returned HTTP 200, serving a login page. Auth state at the console login level is unknown — the login page could be client-side gated (no backend enforcement) or backend-enforced. Not probed further.

## Pending Probes

- [ ] GET /openapi.json — what does the LangGraph API expose?
- [ ] What Qdrant or vector DB receives the embeddings? (check ports 6333, 6334)
- [ ] MinIO API probe at :9000 — AccessDenied or open?
- [ ] PTR / ASN attribution — confirm SA timezone
- [ ] What generative LLM provider is used? (check any config endpoint)
- [ ] Ollama /api/show — model details for any loaded model

## Notes

The multilingual embedding model (`paraphrase-multilingual`) suggests the service handles multiple languages. The South American timezone and multilingual capability together suggest a Latin American deployment. Use case unknown — the LangGraph API schema will clarify.
