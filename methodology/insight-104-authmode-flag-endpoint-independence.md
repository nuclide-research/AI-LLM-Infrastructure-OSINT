---
type: methodology
insight_number: 104
title: "A global auth flag is not an endpoint verdict: auth_mode=disabled does not imply every endpoint is open; verify the endpoint, not the flag (generalizes #16)"
status: candidate
codified: 2026-06-17
source_survey: Cat-RAG-Framework-Servers 2026-06-17
falsifiability_tier: high
falsified_by: a platform whose self-reported global auth flag is provably exhaustive (every documented endpoint honors it with no per-endpoint override)
related_insights: [13, 16, 37, 57, 76]
---

# Insight #104 - A global auth flag is not an endpoint verdict

## The pattern

Some platforms self-report a single global authentication flag, a machine-readable
auth-state decoder, in a metadata endpoint. LightRAG's `/health` returns
`auth_mode:"disabled"` or `auth_mode:"enabled"`. The flag is genuinely useful: it
confirms platform identity AND a population-level auth posture in one read, no
exfiltration, names ARE the finding (this is what made the LightRAG population
measurable at all).

The trap is reading the global flag as an endpoint-level guarantee.
`auth_mode:"disabled"` says the platform was configured without the global auth
gate. It does NOT say every endpoint behaves accordingly. Individual data-plane
routes can carry their own access control that fires regardless of the global
flag, returning 403 on the very documents the global flag implies are open.

The flag is necessary context, not a sufficient verdict. The endpoint is the
verdict.

## Empirical founding case - LightRAG (Cat-RAG-Framework-Servers 2026-06-17)

Of the LightRAG hosts re-confirmed `auth_mode:"disabled"` at `/health`, two
returned **403 on `/documents`** despite the disabled global flag:

```
3.142.219.65    /health auth_mode=disabled    /documents -> 403
34.172.75.32    /health auth_mode=disabled    /documents -> 403
```

A survey that trusted `auth_mode=disabled` as the finding would have logged these
two hosts as open-corpus unauthenticated, an unverified, published falsehood for
each. The remaining disabled hosts split three ways at the same endpoint:
3 served a large populated `/documents`, 3 served a single-document test corpus,
and these 2 gated `/documents` at 403. One global flag, four distinct
endpoint-level outcomes. The endpoint-level gating is independent of the global
auth flag, so the global flag cannot stand in for the per-endpoint probe.

## Why this generalizes Insight #16

Insight #16 is specifically about the HTTP **status code at one endpoint**: a 200
is identity, not auth state, so you must read the data layer behind that endpoint
before declaring it open. #104 is the same discipline lifted one level up, from a
single endpoint's status to a platform's GLOBAL self-reported flag:

| | Insight #16 | Insight #104 |
|---|-------------|--------------|
| Signal being over-trusted | HTTP 200 at endpoint E | global `auth_mode=disabled` |
| Wrong inference | "200 means E's data is open" | "flag means every endpoint is open" |
| Required correction | data-layer probe at E | per-endpoint probe at each target route |
| Failure scale | one endpoint | every endpoint the flag is assumed to cover |

#16 distrusts the status code; #104 distrusts the platform's own auth-state
self-report. #104 is the broader statement: even a machine-readable, accurate
global flag does not bind individual endpoints. The auth posture is a per-endpoint
property, and a single global decoder collapses that vector to a scalar.

## How to apply

1. Use the global flag (`auth_mode`, `anonymous_access`, equivalents) for what it
   is: identity confirmation plus a population-screening prior. It is a strong
   Stage-0/Stage-3v candidate selector, not a finding.
2. For every endpoint you intend to claim open, probe THAT endpoint. A host with
   `auth_mode=disabled` and a 403 on `/documents` is "global auth off, documents
   endpoint gated," not "open corpus."
3. Record the per-endpoint outcomes separately. A platform can be auth-off
   globally while its highest-value data route is the one endpoint someone gated.
4. The rung does not advance on the flag. `auth_mode=disabled` is rung A/1 at most
   (identification surface). A populated `/documents` 200 with a count is the rung
   that earns the unauth-corpus label, per Insight #68.
5. Restraint unchanged: enumerate the per-endpoint status and any
   platform-reported counts; do not read the records.

## Population consequence

Trusting the global flag at population scale produces a systematic over-count of
open-corpus findings, by the size of the subset that runs the flag off but gates
the data route. The error is not noise: it tracks operators who deliberately left
one endpoint protected on an otherwise-open deployment, which is precisely the
subset worth distinguishing. The fix is one probe per target endpoint, cheap, and
the same shape as the Insight #16 data-layer probe.

## Related insights

- Insight #16 - A 200 is identity, not auth state (the per-endpoint parent; #104
  lifts it from endpoint status to global flag)
- Insight #13 - Shipping defaults are load-bearing (the global flag IS the
  shipping default; #104 says the default does not bind every endpoint)
- Insight #37 - Asymmetric auth gating, dashboard vs API (the same per-surface
  independence, here within one platform's route set)
- Insight #57 - Partial auth failure class (mixed auth outcomes within one host)
- Insight #76 - App auth on, operator-debris auth off (auth state varies by
  surface within a single deployment)

## Promotion criteria

Confirmed at 1 platform (LightRAG, 2 hosts gating `/documents` despite
`auth_mode=disabled`). Promotion to numbered Insight requires a second platform
whose global auth flag is contradicted by a per-endpoint probe (a global
"open"/"disabled" flag with at least one documented endpoint returning 401/403).
