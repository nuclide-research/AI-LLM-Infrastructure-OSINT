# Insight #59 — n8n Split-Surface Auth Gap

**Date:** 2026-05-25
**Survey anchor:** n8n discovery, 38.102.86.8

---

## Observation

n8n exposes two API surfaces on port 5678:

- `/api/v1/` — public API, enforces auth via Bearer token or X-N8N-API-KEY header
- `/rest/` — internal frontend API, historically the direct backend path for the n8n UI

In n8n 1.120.0 at 38.102.86.8, `/api/v1/workflows` returns 401 and `/rest/workflows` returns workflow data without credentials. User management is configured (`showSetupPage: false`). The `/rest/` surface is not covered by the same middleware.

Of the five n8n hosts in the Shodan corpus:
- 38.102.86.8: `/rest/` open, `/api/v1/` gated — SPLIT GAP
- 206.190.237.244 (16clouds.com): both surfaces auth-gated
- 168.119.96.100, 46.62.162.52, 88.198.205.101 (ChattyAI cluster): both surfaces auth-gated

1/5 hosts (20%) exhibit the split-surface gap.

---

## Failure Vector

The `/rest/` path is the internal API n8n's own frontend calls. It predates the `/api/v1/` public API. When n8n added user management (around v0.100), auth was wired to both. But in some configurations — upgrade paths, environment flags, or manual auth configurations — only the public API surface is covered.

The gap is version-independent: 38.102.86.8 runs 1.120.0 (current). The split-surface gap is a configuration state, not a version-specific bug.

---

## Detection

```
GET /api/v1/workflows  → 401  = public API properly gated
GET /rest/workflows    → 200  = legacy surface open = SPLIT GAP
```

Both 200 = setup not complete (SETUP_OPEN) or auth fully disabled — different finding class.
Both 401 = fully gated.

---

## aimap Probe Candidate

Add a secondary probe to the n8n fingerprint:
```
Path: /rest/workflows
Matches:
  - status_code: 200
  - json_field: data  (array of workflow objects)
```
Conjunct with a failed /api/v1/ auth check to confirm split-surface state rather than full open.

---

## Insight Class

Split-surface auth gap: a new API path enforces auth; the legacy internal path does not. The operator configured the documented security feature but the legacy surface was not explicitly covered.

Generalizes: any tool that ships with both a legacy internal API and a newer public API may exhibit this pattern on upgrade paths. Check both surfaces independently.
