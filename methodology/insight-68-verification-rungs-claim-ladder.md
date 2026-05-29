---
title: "Insight #68: The verification-rung grid. Label every claim by a depth-and-breadth pair, and never use language above the rung its evidence reached"
date: 2026-05-29
survey: agent-memory-2026-05-29
thesis_touch: methodology (claims discipline; generalizes the verify-before-asserting rule)
extends: ["insight-16-200-is-identity-not-auth-state", "insight-15-dork-hits-are-not-platform-instances", "insight-11-source-code-is-authoritative"]
---

# Insight #68: The verification-rung grid

## The lesson

Every finding carries a verification status expressed as a **pair**: an inner
rung (depth, code vs live) and an outer rung (breadth, host vs population). The
two axes are logically orthogonal, so they must not be collapsed into one ladder.
The claim language is bound to the pair. State the pair in every finding instead
of re-explaining the discipline.

A linear four-step ladder (code, then live, then one host, then population)
quietly assumes "more validation" and "more scanning" are the same direction of
progress. They are not. "Live vs code" (depth) and "one host vs many" (breadth)
are independent. Collapsing them forces some combinations to look like they sit
"between" others when they are actually incomparable, and it erases the one state
that defines how NuClide works.

## The grid

**Inner rungs (depth, code vs live):**

| Inner | What was actually done | Language it licenses | Forbidden above |
|---|---|---|---|
| **A, logic reproduction** | Verbatim source/config review, optionally a harness running a model of the code path | "surface open by code reading, access not exercised" | "vulnerable", "exploitable" |
| **B, binary / stack reproduction** | The real released artifact run in a realistic lab stack with documented defaults, the request sent, the gated action observed | "locally exploitable in default config", "field-confirmed against the released binary" | "exploitable in the field", a rate |

**Outer rungs (breadth, host vs population):**

| Outer | What was actually done | Language it licenses | Forbidden above |
|---|---|---|---|
| **0, no live host tested** | Nothing pointed at a real deployment | "no live host tested yet" | "observed in the wild" |
| **1, in-scope host** | Behavior observed for at least one host meeting inclusion criteria | "observed on an in-scope host" | a frequency or rate |
| **2, population-level** | Fingerprint + sampling + dedup across a measurable population | "X% of fingerprinted deployments exhibited this at inner A/B" | extrapolation beyond the probed set |

## The load-bearing line and the restraint state

The inner axis crux is A to B: code vs live. A logic reproduction (running a
copied model of the code) validates the transcription and catches reasoning
errors. It does not exercise the real binary, middleware chain, or config-load
path. It is an inner-A cross-check, not a promotion. "I could docker-compose this
in principle" is not inner B; the container must exist and the request must have
run.

Axis coupling: reaching outer-1 by exercising the request inherently demonstrates
inner-B for that host. So **inner-A / outer-1** is a distinct state, "this
in-scope host is fingerprinted as running the vulnerable version, but we
deliberately did not fire the request at it." **Inner-B / outer-1** means the
request was exercised against the live in-scope host.

**Depth and breadth are independent, and that independence is a stance.** We may
increase depth without increasing breadth, confirming a condition in the binary
while declining to scan the public internet for it. This is intentional restraint,
not a gap. "NuClide mode" is high-depth, low-breadth by design (inner A or B,
outer 0): the behavior is real in the product, and we are consciously not mapping
it onto the internet. On a linear ladder that looks like an unfinished step; on
the grid it is a chosen position. This encodes the restraint ethic (enumerate, do
not exfiltrate; names are the finding) as a first-class verification state.

## The anchor case: Zep CE empty api_secret (2026-05-29)

Source-confirmed verbatim (`getzep/zep`
`legacy/src/api/middleware/secret_key_auth_ce.go`):

```go
parts := strings.Split(authHeader, " ")
if len(parts) != 2 { /* 401 */ }
prefix, tokenString := parts[0], parts[1]
if prefix != apiKeyAuthorizationPrefix { /* 401, prefix == "Api-Key" */ }
if tokenString != config.ApiSecret() { /* 401 */ }
// allow
```

`legacy/zep.yaml` ships `api_secret` empty. For `Authorization: Api-Key `
(trailing space): `parts == ["Api-Key", ""]`, prefix passes, `"" ==
config.ApiSecret()` is `"" == ""`, request allowed. A zero-entropy credential
satisfies the check, with no non-empty-secret invariant at config load.

Precondition that only source reading reveals: the trailing space is
load-bearing. `strings.Split("Api-Key", " ")` is `["Api-Key"]` (len 1, 401). A
bypass claim phrased "send Api-Key with no token" would fail in the field.

A harness (`/tmp/zep-auth-verify/main.go`, 2026-05-29) reproduced the branch
logic and the trailing-space precondition against a truth table. That is the
inner-A cross-check, not a promotion.

**Current status: inner A / outer 0.** Source and logic reproduction confirm the
condition; no live Zep CE host has been stood up or surveyed. We avoid
"exploitable" and describe a code-level condition only. To reach inner B: stand
up the `zepai/zep` CE stack with the default empty secret and observe the
empty-token request gain access. Outer rung stays 0 until the scanner is pointed
at the public CE population.

## What this means for method

- **Print the pair in every finding.** "Status: inner A / outer 0" replaces
  re-explaining the discipline. The ledger and case studies carry the pair.
- **This generalizes the existing claims rules.** Insight #16 (a 200 is identity
  not auth state) is an outer-1 guard, Insight #15 (the ~50% marker rule) is the
  outer-1-to-outer-2 gate, Insight #11 (source is authoritative) is what makes
  inner-A trustworthy.
- **Reusable template:** `case-studies/_FINDING-TEMPLATE.md`.

## Source
`data/platform-intel/agent-memory-osint-2026-05-29.md`,
`case-studies/commercial/zep-ce-empty-apisecret-finding-2026-05-29.md`,
`case-studies/_FINDING-TEMPLATE.md`.
