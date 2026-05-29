---
type: template
purpose: neutral finding write-up with explicit verification-rung labeling
---

# Finding Template (verification-rung labeled)

Use for any finding before it reaches population scale. The point is to state
exactly what was done and exactly what was not, so the claim never outruns the
evidence. Fill the Verification Status as a pair and never use language above the
rung you are on. See Insight #68.

## Verification rungs (the claim grid)

Each finding carries a status pair: an **inner rung** (depth, code vs live) and
an **outer rung** (breadth, host vs population). The axes vary independently.

### Inner rungs (depth)

| Inner | What was actually done | Language it licenses | Forbidden above this |
|---|---|---|---|
| **A, logic reproduction** | Verbatim source/config review, optionally a harness running a model of the code path | "surface open by code reading, access not exercised" | "vulnerable", "exploitable", "auth bypass" |
| **B, binary / stack reproduction** | The real released artifact run in a realistic lab stack with documented defaults, the request sent, the gated action observed | "locally exploitable in default config", "field-confirmed against the released binary" | "exploitable in the field", a population rate |

### Outer rungs (breadth)

| Outer | What was actually done | Language it licenses | Forbidden above this |
|---|---|---|---|
| **0, no live host tested** | Nothing pointed at a real deployment | "no live host tested yet" | "observed in the wild" |
| **1, in-scope host** | Behavior observed for at least one host meeting inclusion criteria | "observed on an in-scope host" | a frequency or rate |
| **2, population-level** | Fingerprint + sampling + dedup across a measurable population | "X% of fingerprinted deployments exhibited this at inner A/B" | extrapolation beyond the probed set |

A logic reproduction (running a copied model of the code) is an inner-A
cross-check, not a promotion. The line that matters for the inner axis is code
vs live: was the request exercised against the real artifact?

Axis coupling: reaching outer-1 by exercising the request demonstrates inner-B
for that host. **Inner-A / outer-1** = "fingerprinted in scope, deliberately not
exercised" (the restraint ethic). **Inner-B / outer-1** = "exercised against the
live in-scope host."

## Discovery-signal rule (pairs with the rungs)

Rank fingerprints by discriminating power, not convenience. Protocol- and
domain-specific features (OpenAPI `info.title`, semantic routes, vendor response
headers) are claim-promotable. Weak signals (a shared port, a generic banner, a
single substring) are candidate-only and never promote a claim on their own.

---

## Finding fields

- **Condition:** the precise configuration/code state that produces the issue.
- **Evidence:** verbatim code snippet and/or config default. Cite the source path.
- **Impact (at the confirmed rung):** what the confirmed evidence shows, scoped
  to the rung. State it at code level if inner-A.
- **Verification status:** the pair (inner A/B, outer 0/1/2) and the exact
  remaining steps to reach the next rung on each axis.
- **Preconditions / scope limits:** what must be true for the issue to apply, so
  the claim is not an overclaim.
- **Remediation:** the copy-pasteable fix.
