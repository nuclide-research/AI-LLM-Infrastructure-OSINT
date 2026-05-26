---
type: case-study
title: "ArtsyPetz CrewAI Stack: Langfuse LLM Observability Open Registration, Multi-Service Stack Exposed"
date: 2026-05-25
severity: MEDIUM
sector: commercial
tags: [CrewAI, Langfuse, ClickHouse, GlitchTip, MinIO, FastAPI, Django, nginx, DigitalOcean, indie-hacker]
summary: "A multi-service AI stack at 147.182.219.125 exposes Langfuse 3.88.1 LLM observability with open self-registration. ClickHouse 25.7.1.3997, GlitchTip, and MinIO run on the same host with auth enforced. A CrewAI social content generation service is present on ports 8001 and 9002. The operator is an indie developer running ArtsyPetz (pet portrait e-commerce) alongside a social media growth tool in development."
---

# ArtsyPetz CrewAI Stack: Langfuse LLM Observability Open Registration, Multi-Service Stack Exposed

**Date:** 2026-05-25
**Host:** 147.182.219.125
**Cloud:** DigitalOcean (AS14061), New York
**App:** Langfuse 3.88.1 + CrewAI FastAPI + ClickHouse 25.7.1.3997 + GlitchTip + MinIO
**Operator:** CJ Johanson (github.com/cjjohanson), artsypetz.com
**Severity:** MEDIUM

---

## What Was Found

### F1 — Langfuse LLM Observability: Self-Registration Open (MEDIUM)

Langfuse 3.88.1 runs on port 3001. `signUpDisabled: false`. Credentials auth only (Google, GitHub, OKTA, Azure all disabled). Any caller can create an account.

```
GET  /api/public/health → {"status":"OK","version":"3.88.1"}
GET  /api/public/traces → {"message":"No authorization header"}  — requires auth
GET  /api/public/projects → {"message":"No authorization header"} — requires auth
```

The registration endpoint is live. Langfuse is the LLM observability layer for the CrewAI services on this host. It captures traces, costs, and prompt logs from agent runs. Trace data requires auth to read. Whether newly registered accounts can access the operator's existing project traces depends on Langfuse multi-tenancy configuration. The registration surface is open.

### F2 — Service Stack Fingerprinted, Auth Enforced on Data Services (LOW)

Open ports confirmed by Shodan InternetDB: 22, 80, 3001, 8001, 8002, 8123, 9001, 9002, 9090.

| Port | Service | Version | Auth State |
|---|---|---|---|
| 80 | nginx/1.26.0 | — | Reverse proxy |
| 3001 | Langfuse | 3.88.1 | Registration open; data endpoints require auth |
| 8001 | CrewAI FastAPI | v2.0.0 | Not confirmed unauthenticated |
| 8002 | GlitchTip | Unknown | Auth enforced on org/project APIs; `/_health/` open |
| 8123 | ClickHouse | 25.7.1.3997 | `REQUIRED_PASSWORD` enforced on default user |
| 9001 | gunicorn/Django | — | Internal service, 400 on HEAD |
| 9002 | CrewAI FastAPI | v2.0.0 | Same bind as 8001 |
| 9090 | MinIO | — | `AccessDenied` on root |

ClickHouse error on any query:
```
Code: 194. DB::Exception: default: Authentication failed: password is incorrect,
or there is no user with such name. (REQUIRED_PASSWORD) (version 25.7.1.3997 official build)
```

ClickHouse version is disclosed unauthenticated via the error string. Auth is enforced.

### F3 — CrewAI Social Content Generation Service (UNRATED)

Port 8001 (uvicorn FastAPI) and 9002 expose `CrewAI Service v2.0.0` with a social media content generation API:

```
POST /api/v1/generate               — blog_post, platforms[], user_id, optional writing_profile + callback_url
POST /api/v1/analyze-onboarding-style — writing samples → writing profile (voice-matching)
```

This is the operator's second startup: an AI content repurposing tool that learns writing style then generates platform-native posts. The OpenAPI spec carries no visible security definitions on these endpoints. Auth status not confirmed — the earlier survey phase recorded this host as having an auth-enforced CrewAI surface, but the social content endpoints were not probed. UNRATED pending direct test.

### F4 — nginx/1.26.0: CVE-2025-23419 Version-Confirmed (LOW)

nginx/1.26.0 is confirmed on port 80. CVE-2025-23419 is a TLS session reuse bypass that allows authentication bypass when `ssl_verify_client optional` is configured with shared memory zones. Version is confirmed vulnerable. Exploitability depends on server configuration; not testable externally.

### F5 — No Secrets in JS Bundle (CLEAR)

`artsypetz.com` serves a Django app (not React). The single JS bundle (`/static/js/base.js`, 627 bytes) is pure UI toggle code. Facebook Pixel ID `1505711333828934` and Plausible analytics are present in the HTML. No Langfuse keys, GlitchTip DSN, ClickHouse credentials, or API keys found in any client-side asset. Backend instrumentation is server-side only.

---

## Stack

Django (gunicorn, port 9001), nginx/1.26.0 (reverse proxy, port 80), Langfuse 3.88.1 (port 3001), CrewAI FastAPI v2.0.0 (ports 8001 + 9002), GlitchTip (port 8002), ClickHouse 25.7.1.3997 (port 8123), MinIO (port 9090). DigitalOcean AS14061. Domain: artsypetz.com. MX: Zoho Mail.

---

## Failure Mode

Langfuse ships with `LANGFUSE_DISABLE_REGISTRATION=false` as a default. The operator did not set `LANGFUSE_DISABLE_REGISTRATION=true`. The registration surface is the default-on state.

The stack is a self-hosted indie developer setup running two concurrent products: ArtsyPetz (pet portrait e-commerce, Django) and a social media growth tool (CrewAI FastAPI). All data services have auth configured. The LLM observability layer does not.

---

## Operator Attribution

CJ Johanson. MS Data Science, UMass Dartmouth. Data engineer by background. Boston area. GitHub: `github.com/cjjohanson`, 15 public repos. Personal site: cjlovesdata.com. Three in-progress startups listed: ArtsyPetz, an unnamed social media growth tool (the CrewAI service on this host), and an unnamed social planner app. ArtsyPetz: pet portrait e-commerce, customer uploads photos, platform generates artwork (Renaissance-style), printed on merchandise, 10% proceeds to animal rescues. `@artsypetz` on Instagram and TikTok.
