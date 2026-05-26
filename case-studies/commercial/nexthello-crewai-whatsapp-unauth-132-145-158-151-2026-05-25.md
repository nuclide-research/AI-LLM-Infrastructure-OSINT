---
type: case-study
title: "NextHello CrewAI CRM: 59-Endpoint Operational API Open Without Authentication, Live API Keys"
date: 2026-05-25
severity: HIGH
sector: commercial
tags: [CrewAI, FastAPI, WhatsApp, Baileys, PDL, HeyGen, ElevenLabs, Supabase, Oracle, event-networking]
summary: "A CrewAI-based WhatsApp CRM platform at 132.145.158.151 exposes 59 endpoints without authentication. All operational POST endpoints accept requests without credentials. People Data Labs, HeyGen, and ElevenLabs API keys are live. A WhatsApp bridge with persisted session credentials is disconnected; reconnect enables message delivery to any phone number. The admin data layer is gated."
---

# NextHello CrewAI CRM: 59-Endpoint Operational API Open Without Authentication, Live API Keys

**Date:** 2026-05-25
**Host:** 132.145.158.151
**Cloud:** Oracle Cloud (AS31898), US
**App:** NextHello CrewAI API v1.0.0 + Baileys WhatsApp Bridge
**Operator:** askmikeai@gmail.com
**Severity:** HIGH

---

## What Was Found

### F1 — Full Operational API Open Without Authentication (HIGH)

Port 8001 runs a FastAPI (uvicorn) service: `NextHello CrewAI API v1.0.0`. `/docs` and `/redoc` return HTTP 200 — interactive Swagger UI and ReDoc are publicly browsable. All operational POST endpoints accept requests without credentials. No auth challenge, no 401, no 403.

```
GET  /                → {"name":"NextHello CrewAI API","version":"1.0.0","docs":"/docs","health":"/health"}
GET  /health          → {"status":"healthy","llm_provider":"test","whatsapp_configured":false,"redis_connected":true}
GET  /config          → full integration map, all keys (PDL/HeyGen/ElevenLabs/Supabase) configured
GET  /conversations   → {"conversations":[],"count":0}
GET  /state/{phone}/history → message history endpoint open; empty for unknown numbers
```

Note: `/health` reports `llm_provider: "test"` but `/config` reports `"openai/gpt-4o"`. The health endpoint carries a stale value; the live provider is GPT-4o.

### F2 — Live API Keys, No Credential Gate on Execution Endpoints (HIGH)

`/config` (unauthenticated GET) confirms:

```json
{
  "llm_provider": "openai/gpt-4o",
  "pdl_configured": true,
  "heygen_configured": true,
  "elevenlabs_configured": true,
  "hubspot_configured": false,
  "supabase_configured": true,
  "whatsapp_configured": false,
  "redis_configured": true
}
```

All execution endpoints accept phone numbers and contact data without credentials. Each call consumes live API quota:

| Endpoint | Trigger |
|---|---|
| `POST /research` | People Data Labs query on phone number + email + LinkedIn |
| `POST /video/generate` | HeyGen video generation |
| `POST /voice/generate` | ElevenLabs voice synthesis |
| `POST /crm/sync` | HubSpot CRM record creation |
| `POST /qualify` | Contact qualification pipeline |
| `POST /pipeline/full` | Chained: research → qualify → video → CRM sync |

`POST /send` and `POST /send/immediate` accept `phone_number` and `content`. Both would deliver WhatsApp messages when the bridge reconnects.

### F3 — WhatsApp Bridge: Session Credentials Persisted (HIGH)

Port 3000 runs a Baileys WhatsApp bridge. The bridge is disconnected (`connected: false`) but session credentials exist in both local storage and Postgres.

```
GET /health:         {"status":"ok","connected":false,"sessionId":"askmikeai-gmail.com","ownerId":"askmikeai@gmail.com","hasPostgres":true}
GET /session/status: {"hasLocal":true,"hasRemote":true,"remoteFormat":"baileys-multifile-v1","postgresConfigured":true}
GET /qr:             {"available":false,"connected":false,"qrPayload":null,"qrText":null}
```

`hasLocal: true` and `hasRemote: true` mean the WhatsApp account was previously authenticated. Session state is persisted in the Baileys multifile format. The bridge is idle, not cleared. When the phone reconnects, the session resumes. At that point, `POST /send` delivers messages to any phone number.

`POST /admin/api/whatsapp/session/reset` exists and requires admin auth — it would force a fresh QR flow.

The bridge exposes `ownerId: askmikeai@gmail.com` and `sessionId: askmikeai-gmail.com` without credentials.

### F4 — Admin Signup Open: Account Creation With No Rate Limiting (HIGH)

`POST /admin/api/auth/signup` accepts registrations without credentials.

```
POST /admin/api/auth/signup
{"email":"<any>","password":"<any>","name":"<any>"}
→ {"success":true,"status":"pending"}
```

Accounts are created in `status: pending`. The approval endpoint is `POST /admin/api/auth/approve/{user_id}`. That route is blocked by the tenant account-lookup gate — it requires a provisioned admin account. Registration is open; access to admin data requires approval from an existing owner.

All other `/admin/*` routes return `{"error":"account not found"}`. The gate is a tenant-keyed account lookup, not a session or JWT check. Admin data — contacts, messages, enrichment records, CRM sync results, PII from PDL runs, media — is not accessible without a provisioned account.

`GET /admin/api/auth/users` returns `{"error":"forbidden"}`. That route checks admin privilege separately.

No Supabase URL or anon key was found in the React SPA bundle at port 80. Supabase access is server-side only.

### F5 — OpenClaw Tailscale Integration (LOW)

`GET /admin/api/research/openclaw/health` returns `{"error":"account not found"}` — the gate blocks it. The endpoint description confirms an OpenClaw research agent instance is reachable from this host over Tailscale. OpenClaw runs on a separate private host. Tailscale-gated; not reachable from the public internet.

---

## Stack

FastAPI (uvicorn), CrewAI agent framework, GPT-4o (OpenAI), People Data Labs, HeyGen, ElevenLabs, Supabase (Postgres), Redis, OpenClaw (Tailscale-private). WhatsApp bridge: Baileys (multifile session). Port 80: React SPA (nginx/1.27.5), title "NextHello CRM + Swarm". Port 3000: WhatsApp bridge. Port 8001: main API. Oracle Cloud US (AS31898). No TLS on port 8001 or 3000.

Shodan reports only ports 22, 80, 8001 — port 3000 is not indexed. Port 5432, 6379 are container-internal, not host-exposed.

---

## Failure Mode

The application authenticates the admin layer (tenant-keyed account lookup) but not the operational layer. All execution endpoints — research, qualification, message delivery, media generation — sit in front of the auth gate. The developer separated "admin" from "operational" routes and gated only the former.

The WhatsApp bridge has no auth on its metadata endpoints. The bridge's connection state is the only gate on live message delivery, and session credentials are already persisted.

---

## Operator Attribution

Operator email: `askmikeai@gmail.com` (confirmed from WhatsApp bridge `/health` response). Product: `nexthello.ai` — "AI-powered multi-channel outreach with real-time orchestration for teams managing follow-ups at scale." GitHub: `github.com/askmikeai`, created 2026-02-08. 11 public repos including `next-hello` (PLpgSQL, 9 stars), `openclaw` (TypeScript fork), `openclaw-digitalocean`. Config fields `owner_name: "the host"` and `event_name: "the event"` are placeholders — the tool is configured per-event deployment for networking events. Solo developer.
