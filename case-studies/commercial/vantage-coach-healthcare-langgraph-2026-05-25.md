---
type: case-study
title: "Vantage Coach — Healthcare CRM Agent With Voice Endpoints, No Auth"
date: 2026-05-25
severity: HIGH
sector: commercial
tags: [LangGraph, healthcare, pharma, CRM, voice, Supabase, Redis, DigitalOcean, PII, agent-framework, Spanish]
summary: "A pharmaceutical sales rep AI assistant runs LangGraph on two DigitalOcean nodes with no authentication. The agent has declared access to a healthcare client database. Voice endpoints accept unauthenticated audio and return agent-processed responses. Client records including doctor names, specializations, visit history, and treatment discussion notes are accessible to any caller with a valid organization ID."
---

# Vantage Coach — Healthcare CRM Agent With Voice Endpoints, No Auth

**Date:** 2026-05-25
**Targets:** 138.68.228.98 · 167.99.26.114
**ASN:** AS14061 DigitalOcean, Santa Clara, California, US
**Severity:** HIGH

---

## What Was Found

### F1 — Healthcare Client Database Accessible Without Auth (HIGH)

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7004, S7068, S7075, T5904
- **733 (AI Risk & Ethics Specialist):** K7040, T5854, T5868
- **overlap (Common AI KSATs (all 5 roles)):** K1157, K1158, K22, K6311, K7003, K942

<!-- ksat-tag:auto-generated:end -->

Port 8000 on both nodes serves a FastAPI/LangGraph API described in its own OpenAPI spec as "Production-ready AI assistant with access to weather data and client information."

The spec example data confirms the data class:

> "Dr. John Smith is a general practitioner at City Hospital. His last visit was on January 15, 2024, where you discussed the new medication protocol."

This is a pharmaceutical CRM. The agent has tool access to a database of physician clients: names, specializations, institutional affiliations, visit history, and discussion notes from sales rep interactions.

```
POST http://138.68.228.98:8000/chat
Content-Type: application/json
→ {"user_id": "...", "organization_id": "...", "message": "..."}
```

No JWT, no session token, no credential check enforced. The `organization_id` field provides tenant isolation in the request body. Any caller who supplies a valid `organization_id` can query that organization's client database through the agent. Rate limits are applied (300 req/min per IP, 20/min per user, 5,000/min per organization) but these are not auth gates.

The response includes `total_cost_usd` per call, confirming this is a production billing-enabled deployment.

### F2 — Voice Endpoints Accept Unauthenticated Audio (MEDIUM)

Two endpoints accept audio input and return agent-processed output:

```
POST /voicebot        — audio in, PCM audio out (STT + agent + TTS pipeline)
POST /voicebot/text   — audio in, streaming text response
```

Required fields: `audio`, `thread_id`, `user_id`, `organization_id`. Default language: Spanish. No auth. Any caller can drive the voice agent against any organization's client context.

### F3 — Conversation History Open (HIGH)

```
GET http://138.68.228.98:8000/chat/history/{thread_id}
→ 404 "Conversation not found" — no auth error
```

The 404 response (not 401/403) confirms no auth gate. Thread IDs follow the pattern `user-{id}-session-{id}` from the OpenAPI spec examples, making them guessable or enumerable. Full conversation turns are in thread history, including any physician records retrieved by the agent. `DELETE /chat/history/{thread_id}` is also open.

---

## Stack Map

| Host | Port | Service | Version | Auth | Severity |
|---|---|---|---|---|---|
| 138.68.228.98 | 8000 | LangGraph FastAPI — Vantage Coach | v1.0.0 | None | HIGH |
| 138.68.228.98 | 8001 | LangGraph FastAPI — duplicate | v1.0.0 | None | HIGH |
| 138.68.228.98 | 3000 | Next.js frontend | — | Not probed | — |
| 167.99.26.114 | 8000 | LangGraph FastAPI — Vantage Coach | v1.0.0 | None | HIGH |
| 167.99.26.114 | 8001 | LangGraph FastAPI — duplicate | v1.0.0 | None | HIGH |
| 167.99.26.114 | 3000 | Next.js frontend | — | Not probed | — |

Both nodes return identical Next.js ETag `"uh3ph94ezhie9"`, confirming same compiled frontend artifact and same operator. Infrastructure: Redis (48-hour TTL), Supabase (UUID message IDs in responses). Rate limiting is enforced; auth is not.

---

## Attribution

DigitalOcean Santa Clara. Contact email and GitHub URL in the codebase use placeholder values (`yourdomain.com`, `yourorg`). The operator deployed from a template without replacing development placeholders. No domain attribution from passive sources. Spanish-language default on voice endpoints points to a Latin American or Spanish market.

---

## Data Class

Healthcare provider records: physician names, medical specializations, institutional affiliations, office locations, visit histories, and discussion notes from sales rep calls. The `/voicebot` endpoint processes voice input for a field sales assistant. The data flowing through it includes sales conversations about pharmaceutical products and treatment protocols.

Whether actual patient data flows through the system is not determined from the API surface alone. The data class is healthcare professional contacts and sales interaction records. Not patient records, but HIPAA-adjacent: the underlying business context is pharmaceutical sales and the client list consists of medical providers.

---

## Thesis Placement

Two independent deployments of the same application, both unauthenticated, on adjacent DigitalOcean nodes. FastAPI ships with no auth by default; LangGraph's agent execution model adds no auth layer. The voice endpoints extend the exposure surface beyond the web API. A caller does not need to construct HTTP requests to interact with the healthcare CRM agent.

**See also:** [LangGraph Server Survey (2026-05-25)](langgraph-server-survey-2026-05-25.md) · [LangGraph Deployment Gap](langgraph-deployment-gap-survey-2026-05-25.md)
