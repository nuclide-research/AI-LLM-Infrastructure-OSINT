---
title: "Vite dev server left running in production exposes full TypeScript source"
insight_number: 58
date: 2026-05-25
tags:
  - methodology
  - source-code-exposure
  - vite
  - operational-security
  - multi-tenant
---

# Insight #58: Vite Dev Server in Production

**Date codified**: 2026-05-25
**Survey anchor**: Survey-38 LangGraph — Assistent Tècnic Intel·ligent / Docu Companion (157.180.21.126)
**File**: `case-studies/commercial/docu-companion-vite-dev-server-2026-05-25.md`

---

## The Finding

A Vite development server left running alongside a production API exposes every TypeScript source file on request. Vite's dev server does not build or bundle — it serves raw source modules directly from disk. Any file under `src/` is readable via HTTP GET.

Confirmed instance:

```
GET http://157.180.21.126:5000/src/main.tsx          → full source
GET http://157.180.21.126:5000/src/App.tsx            → full route structure
GET http://157.180.21.126:5000/src/i18n/locales/ca.json → Catalan string table
```

Port 5000 (Vite dev server) ran alongside port 8000 (production LangGraph API). The production API served 211 tenant namespaces. The dev server exposed the code that managed them. Service uptime: 90 days.

---

## Why This Happens

A developer runs `vite dev` during development and either:
1. Deploys the entire working directory to production without stopping the dev process, or
2. Adds `vite dev` to the startup script without distinguishing dev/prod environments

Vite's dev server binds to `0.0.0.0` by default on port 5173 or a configured alternative. When the production host has no firewall rule blocking the dev port, the server is reachable from the internet.

The operational security failure is in the startup sequence: `vite dev` and the production API start together. Nothing in the sequence signals that one is a source-serving development tool.

---

## What Is Exposed

Vite serves:
- All `.tsx`, `.ts`, `.vue`, `.js` files under `src/`
- `index.html` (application entry point)
- Source maps embedded in every response
- Locale files, config files, anything importable from the project root

From the App.tsx alone: full page/route structure, authentication boundaries, internal API paths, feature flags, admin routes.

---

## Detection

Shodan/Censys probe: ports 5173, 5000, 5001 returning `Content-Type: application/javascript` or `application/typescript` with `src/` path in request. The Vite dev server serves a distinctive `__vite_ping` endpoint at `/__vite_ping`.

aimap probe candidate:
```
Path: "/__vite_ping"
Matches: status_code 200 + body_contains "pong"
```

Or:
```
Path: "/src/main.tsx"
Matches: status_code 200 + header_contains Content-Type: application/javascript
```

---

## Severity Class

HIGH when the exposed source code reveals:
- Internal API paths and authentication logic
- Database schemas via TypeScript type definitions
- Multi-tenant routing (tenant IDs, namespaces, access control logic)
- Third-party API keys or credentials embedded in source constants

The source code exposure is secondary to the primary data exposure (Qdrant open, agent endpoints open). But it provides a complete blueprint for enumerating the primary exposure.

---

## Relation to Other Insights

- **Insight #52** (HTTP 200 at an API path is not that API): the Vite dev server returns 200 on any valid source path — confirming the file exists does not mean the API behind it is running the same code.
- **Insight #51** (port is not identity): port 5000 is the Vite dev port here; it would be a different service on another host.
