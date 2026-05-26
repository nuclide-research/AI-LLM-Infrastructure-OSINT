---
to: askmikeai@gmail.com
cc: abuse@nuclide-research.com
severity: HIGH
ip: 132.145.158.151
institution: "NextHello (nexthello.ai) — AI-powered WhatsApp CRM. All operational POST endpoints unauthenticated on port 8001. PDL, HeyGen, ElevenLabs API keys live. WhatsApp Baileys session credentials persisted. Admin signup open."
status: DRAFT
outcome: pending
date: 2026-05-25
---

**To:** askmikeai@gmail.com
**Cc:** abuse@nuclide-research.com
**Subject:** NextHello (132.145.158.151) HIGH: Full operational API open without authentication, API keys exposed, WhatsApp session credentials persisted

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-25

---

This is an unsolicited good-faith disclosure. Severity: **HIGH**.

I found your project through routine AI infrastructure research and wanted to make sure you know before anyone with bad intent does.

---

## What was found

The NextHello CrewAI API running on 132.145.158.151:8001 exposes its full operational surface without authentication. The Swagger docs are publicly browsable at http://132.145.158.151:8001/docs.

**All operational POST endpoints accept requests without credentials:**

- `POST /send` and `POST /send/immediate` — deliver WhatsApp messages to any phone number
- `POST /research` — queries People Data Labs by phone number, email, and LinkedIn URL
- `POST /qualify` — runs the qualification crew on any contact
- `POST /video/generate` — consumes HeyGen quota
- `POST /voice/generate` — consumes ElevenLabs quota
- `POST /pipeline/full` — chains research + qualify + video + CRM sync in one call

`GET /config` (also public) confirms PDL, HeyGen, and ElevenLabs are all configured and active. Any caller can chain those endpoints against your API keys with no token required.

**WhatsApp session:**
The Baileys bridge on port 3000 is disconnected but the session credentials are persisted (hasLocal: true, hasRemote: true, remoteFormat: baileys-multifile-v1). When the bridge reconnects, `POST /send` and `POST /send/immediate` will deliver messages to any phone number supplied by the caller.

**Admin signup:**
`POST /admin/api/auth/signup` accepts open registration. Accounts are created in `status: pending`, so your admin data is gated, but the signup surface should be restricted.

---

## What this doesn't affect

The admin data layer is behind a tenant account lookup — contacts, messages, enrichment records, and CRM data are not accessible without a provisioned account. The Supabase URL and anon key are not in the frontend bundle. OpenClaw is on Tailscale and not reachable.

---

## Fixes

1. Add an API key or JWT middleware to the operational POST endpoints. FastAPI dependency injection makes this straightforward.
2. Restrict `POST /admin/api/auth/signup` — either disable it or add rate limiting and email verification.
3. The Baileys bridge's `/health` and `/session/status` endpoints expose your email address as the session ID. Consider restricting those to localhost or adding a token check.

---

## About NuClide Research

NuClide Research is an independent security research organization based in Denver, Colorado. This is a good-faith notification. We found the exposure, documented it, and stopped there. We did not call any of your POST endpoints against live data. No data was extracted.

Love the project — multi-agent WhatsApp CRM is a real pain point for event networking. Hope this helps.

Nicholas Michael Kloster
nicholas@nuclide-research.com
nuclide-research.com
CISA CVE-2025-4364, ICSA-25-140-11
