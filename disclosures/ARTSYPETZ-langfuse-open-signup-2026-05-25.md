---
to: cjjohanson@gmail.com
cc: abuse@nuclide-research.com
severity: MEDIUM
ip: 147.182.219.125
institution: "ArtsyPetz / CJ Johanson — Langfuse 3.88.1 LLM observability open self-registration on port 3001. ClickHouse 25.7.1.3997 version-disclosed. Multiple services publicly fingerprinted."
status: DRAFT
outcome: pending
date: 2026-05-25
note: "Contact email unconfirmed — no public email found for cjjohanson. Try contact form at artsypetz.com or cjlovesdata.com. GitHub: cjjohanson."
---

**To:** [contact via artsypetz.com / cjlovesdata.com — no public email confirmed]
**Cc:** abuse@nuclide-research.com
**Subject:** ArtsyPetz stack (147.182.219.125) MEDIUM: Langfuse LLM observability open registration, service stack version-disclosed

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-25

---

This is an unsolicited good-faith disclosure. Severity: **MEDIUM**.

---

## What was found

Your self-hosted Langfuse instance (port 3001) has `signUpDisabled: false`. Anyone can create an account on your LLM observability layer.

```
GET http://147.182.219.125:3001/api/public/health
→ {"status":"OK","version":"3.88.1"}
```

Langfuse tracks your CrewAI agent traces, costs, and prompt logs. Registered users can access Langfuse's project management UI and generate API keys. Whether a newly registered account can view your existing traces depends on your Langfuse multi-tenancy configuration, but the open registration surface means accounts can be created.

**Service stack fingerprinted (all auth-enforced on data):**
- Langfuse 3.88.1 (port 3001) — open registration
- ClickHouse 25.7.1.3997 (port 8123) — version disclosed in auth error string
- GlitchTip (port 8002) — auth enforced, /_health/ open
- MinIO (port 9090) — auth enforced
- nginx/1.26.0 — CVE-2025-23419 in the version's range (TLS bypass, depends on ssl_verify_client config)
- CrewAI FastAPI v2.0.0 (ports 8001, 9002) — auth status not confirmed from outside

Everything except Langfuse registration is properly gated. This is a narrow exposure — one default config not flipped.

---

## Fix

Set `LANGFUSE_DISABLE_REGISTRATION=true` in your Langfuse environment variables and restart. That single change closes the open registration surface.

---

## About NuClide Research

Independent security research, Denver CO. Good faith only. We confirmed the registration surface and stopped.

Nicholas Michael Kloster
nicholas@nuclide-research.com
nuclide-research.com
CISA CVE-2025-4364, ICSA-25-140-11
