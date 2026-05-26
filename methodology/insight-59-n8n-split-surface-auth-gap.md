# Insight #59 — n8n Ungated Legacy REST Surface

**Date:** 2026-05-25
**Survey anchor:** n8n discovery, 38.102.86.8

---

## Observation

n8n exposes two API surfaces on port 5678:

- `/api/v1/` — public API, optional module, disabled by default (`"publicApi": {"enabled": false}`)
- `/rest/` — internal frontend API, always present, the direct backend path for the n8n UI

In n8n 1.120.0 at 38.102.86.8, `/api/v1/workflows` returns **404** — the public API module is disabled and the routes do not exist. `/rest/workflows` returns workflow data without credentials. This is not a split-auth gap between two live surfaces. The public API is absent. The only access path is `/rest/`, and it has no auth gate.

User management is configured (`showSetupPage: false`). The `/rest/` surface is not covered by that configuration.

Of the five n8n hosts in the Shodan corpus:
- 38.102.86.8: `/rest/` open, public API disabled (404) — UNGATED
- 206.190.237.244 (16clouds.com): both `/rest/` and `/api/v1/` return 401 — GATED
- 168.119.96.100, 46.62.162.52, 88.198.205.101 (ChattyAI cluster): both surfaces return 401 — GATED

1/5 hosts (20%) have the ungated legacy REST surface.

---

## Failure Vector

The `/rest/` path is the internal API n8n's own frontend calls. It predates the public `/api/v1/` API. When the public API module is disabled, `/api/v1/` routes simply do not exist. The `/rest/` surface remains present regardless — and in this instance carries no auth gate.

The gap is configuration-state, not version-specific: 38.102.86.8 runs 1.120.0 (current). User management is configured but the `/rest/` surface is not covered by it.

---

## Detection

```
GET /rest/settings   →  200  (always responds — confirms n8n is present)
GET /rest/workflows  →  200  with workflow data  =  UNGATED
GET /api/v1/workflows →  404 (public API disabled) or 401 (API enabled but gated)
```

Both 200 on `/rest/workflows` and 404 on `/api/v1/workflows` = public API absent, legacy surface ungated.

---

## aimap Probe Candidate

Add secondary probe to the n8n fingerprint:
```
Path: /rest/workflows
Matches:
  - status_code: 200
  - json_field: data
```
Pair with a check of `/rest/settings` for `publicApi.enabled: false` to confirm the ungated-legacy pattern vs full-open.

---

## Insight Class

Ungated legacy internal API: the operator configures user management but the legacy internal REST surface is not covered. The public API module is absent. The only access path has no auth gate.

Generalizes: tools that ship with a legacy internal API alongside an optional newer public API may leave the internal surface ungated when the newer API is disabled. Check both surfaces independently.
