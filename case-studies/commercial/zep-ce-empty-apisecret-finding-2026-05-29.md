---
type: finding
platform: Zep Community Edition
date: 2026-05-29
verification: inner-A / outer-0
status: surface open by code reading, access not exercised
---

# Zep CE: empty default api_secret accepts a zero-entropy credential

Code-level finding from the agent-memory pre-assessment
(`data/platform-intel/agent-memory-osint-2026-05-29.md`). Labeled per
`case-studies/_FINDING-TEMPLATE.md`. This is a platform finding, not a host
case study: no live target has been touched.

## Condition

Zep Community Edition ships `legacy/zep.yaml` with `api_secret` empty, and the
secret-key middleware validates with a direct string equality check and no
"secret must be non-empty" invariant at config load.

## Evidence

Source: `getzep/zep` `legacy/src/api/middleware/secret_key_auth_ce.go`
(confirmed verbatim), control flow:

```go
parts := strings.Split(authHeader, " ")
if len(parts) != 2 { /* 401 */ }
prefix, tokenString := parts[0], parts[1]
if prefix != apiKeyAuthorizationPrefix { /* 401, prefix == "Api-Key" */ }
if tokenString != config.ApiSecret() { /* 401 */ }
// allow
```

Config default: `legacy/zep.yaml` sets `api_secret:` empty, so
`config.ApiSecret()` returns `""`. There is no startup guard rejecting an empty
secret.

Source-level trace for `Authorization: Api-Key ` (one trailing space):

- `authHeader == "Api-Key "`
- `parts == []string{"Api-Key", ""}` (len 2, passes the format gate)
- `prefix == "Api-Key"` (passes the prefix gate)
- `tokenString == ""`, and `"" == config.ApiSecret()` is `"" == ""` -> true
- request is allowed

Precondition detail that only source reading reveals: the trailing space is
load-bearing. `strings.Split("Api-Key", " ")` yields `["Api-Key"]` (len 1, 401).
The empty second element requires the space.

## Impact (code level, inner A)

At the code level the authorization check accepts a zero-entropy token (the
empty string) when the operator never set a secret. There is no length or format
constraint on the token beyond being present as the second space-delimited part,
and no additional guard. The middleware gates `/api/v2`, which on a populated
instance serves session message history, summaries, and extracted user facts
(PII-dense conversational memory).

## Verification status: inner A / outer 0

Labeled per the verification-rung grid (Insight #68). Inner A = logic
reproduction (code-confirmed, not exercised). Outer 0 = no live host tested.
(Maps from the earlier linear draft: old "T0" = inner A / outer 0.)

- Have: verbatim source-confirmed control flow; config default; an inner-A logic
  reproduction (`/tmp/zep-auth-verify/main.go`) cross-checking the branch
  behavior and the trailing-space precondition.
- Have NOT: run a Zep CE container with default config, sent a real
  `Authorization: Api-Key ` request, or observed an authenticated action
  succeed. The logic reproduction is a model of the code, not the code.
- To reach inner B (binary / stack reproduction): start a local CE instance with
  the shipped empty `api_secret`, send the empty-token request, and observe a
  material gated action succeed (e.g. `GET /api/v2/sessions-ordered` returning
  data). This raises depth only; breadth stays at outer 0.
- To raise breadth (outer 1, in-scope host; outer 2, population): point the
  survey at real CE deployments. Held at outer 0 by choice for now (NuClide
  restraint ethic: deepen validation without expanding observation scope). No
  claim of "exploitable" until inner B, and no rate until outer 2.

## Preconditions / scope limits

Applies only when the operator never set `api_secret` (the out-of-box state).
Any non-empty secret makes the empty token fail closed. The finding is
"empty-default plus empty-token," not "auth is broken."

## Remediation (for the operator)

Set a non-empty `api_secret` in `zep.yaml` (or `ZEP_AUTH_SECRET`). For the
project: reject an empty secret at config load, or use a constant-time compare
that treats an empty configured secret as "deny all."
