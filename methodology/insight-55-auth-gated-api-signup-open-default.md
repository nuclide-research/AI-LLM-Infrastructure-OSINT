# Insight #55 — Auth-gated API + Open Signup = Uncontrolled Account Creation

**Date:** 2026-05-22  
**Survey anchor:** Agenta LLMOps (14-host population)  
**Finding class:** First-party authentication configuration

---

## The Pattern

A platform can enforce authentication on every API endpoint and still be open to anyone. These two conditions coexist when:

1. The API requires a valid session (401 on all endpoints without auth)
2. Account registration is unrestricted (no operator approval, no invite gate, no `SIGNUP_DISABLED` flag)

Agenta OSS ships SuperTokens with emailpassword, passwordless, and third-party auth all enabled. The `/api/auth/signup` endpoint is live by default. The docker-compose example config contains no `SIGNUP_DISABLED` variable. Result: any anonymous party can self-register on any self-hosted Agenta deployment.

This is not "unauthenticated access" in the traditional sense. The 401 responses are real — the scanner verdict is "auth enforced." But the account layer is open. The attack surface moved up one layer: the registration endpoint, not the API.

---

## Why It Looks Secure

Standard recon probe: `GET /api/apps` → HTTP 401. The natural reading is "authentication required, platform protected." It is the correct reading for the API surface. It is the wrong reading for the total access surface.

The signup probe requires a separate step: `POST /api/auth/signup`. Most population-scale surveys don't include this. The false-negative is systematic, not random — every survey that only checks API endpoints will miss this class.

---

## Verification

Probe: `POST /api/auth/signup` with empty body.

Auth-off (signup open): HTTP 200 + `{"status":"FIELD_ERROR","formFields":[...]}`  
Auth-on (signup disabled): HTTP 404 or 403 or connection refused

The `FIELD_ERROR` response proves the endpoint is accepting registration logic — it validated the input and found it incomplete, which means it would accept valid input. This is the marker probe.

Agenta corpus: 6/6 reachable hosts returned HTTP 200 + FIELD_ERROR. 0 hosts had signup disabled.

---

## Attack Chain

```
Anonymous → POST /api/auth/signup {email, password} → HTTP 200 → account created
  → POST /api/auth/signin → session token
  → GET /api/apps → 200 + app list
  → GET /api/v1/configs/{variant_id} → prompt variant data, LLM provider config
  → GET /api/v1/evaluators → evaluation pipeline
```

Once the attacker holds a session, the blast radius depends on the operator's workspace access configuration. In the OSS default, the owner/admin model means attacker accounts are isolated until granted workspace access — but the account exists, and any mis-click invite or overly permissive workspace setting is now exploitable.

---

## Generalization

The class is: **platform enforces auth on data layer, registration is open on identity layer**.

This is distinct from:
- Unauthenticated API (no session required) — the classic finding
- Auth-disabled via env toggle (deliberate or accidental) — what we look for in Ollama, ChromaDB
- Invite-only or admin-approval registration — the secure posture

Any platform that uses a third-party auth framework (SuperTokens, Auth0, Supabase Auth, Better Auth) and does not explicitly disable self-registration is potentially in this class. The framework's default is almost always "registration open."

Scan for platforms in this class:
1. API returns 401 (looks protected)
2. `POST /auth/signup` or `/api/auth/signup` or `/auth/register` returns 200 (registration live)

The delta between "API-secured population" and "registration-open subset" is the real exposure surface.

---

## Toolchain Implication

The aimap `deep-enum` phase probes services for unauthenticated data access. It does not probe registration endpoints. Adding a `registration-open` probe to aimap would surface this class at population scale:

```
POST /api/auth/signup {}   → 200 + FIELD_ERROR → SIGNUP_OPEN
POST /auth/register {}     → 200 + validation error → SIGNUP_OPEN
POST /api/v1/auth/signup {} → 200 → SIGNUP_OPEN
```

This is the fingerprint gap that produced aimap's 0-match result on the Agenta corpus.

---

## Related Insights

- Insight #02: single-template auth-off propagates
- Insight #08: auth bypass via misconfiguration redirects
- Insight #40: auth-on-default shifts rightward in successor generations
