# Mezbar AI — Arabic Content Generation — Working Notes

**Host:** 137.184.239.176
**Cloud:** DigitalOcean
**Status:** Initial probe complete
**Priority:** 4

---

## Confirmed Services

| Port | Service | Auth |
|---|---|---|
| 8000 | LangGraph FastAPI — "Mezbar AI - Arabic Content Generation API" v1.0.0 | NONE |

## Root Response

```json
{
  "message": "Mezbar AI - Arabic Content Generation API",
  "version": "1.0.0"
}
```

## Health Endpoint

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "api_configured": {
    "openai": true,
    "claude": false
  }
}
```

OpenAI key is configured. Claude API is not active.

## Service Details

- **Backend LLM:** OpenAI gpt-4o-mini (primary + fallback identical)
- **Agent architecture:** 6-agent LangGraph workflow
- **Processing window:** 60–900 seconds
- **Output length:** 1,000–10,000+ words per job
- **Markets:** GCC, Maghreb, Pan-Arab (regional Arabic targeting)
- **Language:** Arabic throughout

## Exposed Endpoints

- `/generate-stream` — streaming content generation
- `/generate_webhook` — webhook-triggered generation
- `/job/{job_id}` — async job status/retrieval
- `/models` — LLM configuration (returns OpenAI key presence)
- `/docs` — Swagger UI

## Pending Probes

- [ ] GET /openapi.json — full endpoint schema
- [ ] GET /models — what does it return exactly? key exposure or just key presence?
- [ ] GET /job/test — does the job endpoint return anything without a valid ID?
- [ ] PTR / ASN attribution on 137.184.239.176
- [ ] What "Mezbar" means — Arabic/Gulf linguistic attribution

## Case Study Angle

Commercial Arabic-language content service. Six-agent workflow, regional GCC/Maghreb targeting. The `/generate_webhook` endpoint and async `/job/{job_id}` pattern suggest an external automation pipeline — content is requested and polled for completion. Without auth, any caller can queue generation jobs on the operator's OpenAI account, poll job status, and retrieve output. The OpenAI key is in-use on the backend — this is an LLMjacking surface.
