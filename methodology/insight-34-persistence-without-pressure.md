---
type: methodology
insight_number: 34
title: Persistence without pressure — operator-unauth populations don't self-remediate
---

# Insight #30 — Persistence without pressure

_Source: code-assistants population follow-up survey, 2026-05-18. Cross-referenced
against Insight #28 (extortion-driven decay)._

## The rule

For unauthenticated AI/ML services in low-attacker-pressure ecosystems (no
extortion campaign, no published disclosure pipeline targeting the platform
class), operator persistence over a 4-day window runs **~83% — operators do
not self-remediate**. The decay function shape differs from Insight #28
(extortion-driven, ~71% wipe in 24h) by approximately two orders of magnitude.

The implication is asymmetric: **the catalogue is the work product**. Survey
findings have a useful disclosure life measured in weeks, not hours, in absence
of an attacker. The 24h re-verification gate from Insight #28 applies only
where an active extortion or wipe campaign targets the platform class.

## Empirical basis

OpenHands code-assistant population, 2026-05-14 → 2026-05-18 (4 days):

| | count | share |
|---|---|---|
| baseline (5/14 unauth) | 30 | — |
| persistent unauth (still exposed) | 25 | 83.3% |
| disappeared (rotated / went down / authed-up) | 5 | 16.7% |
| new (added in the window) | 68 | — |
| total today | 93 (unique IPs) | 3.1× growth |

No external pressure was applied to the 5/14 baseline. No disclosures were
sent to the 30. No extortion campaign targets the platform class. The 25
that remained unauth did so because no signal was received that would have
caused the operator to act.

Compare to Insight #28 (Elasticsearch under the Meow / Indexrm campaign):
3,604 of 5,037 unauth ES hosts wiped in 24h (71.6%). Same operator
demographic, vastly different decay rate. The difference *is* the attacker.

## Why operators do not self-remediate

Operators of platforms with auth-off defaults inherit the framework's
posture without checking. The shipping-default lock-in (Insight #13) means
the operator's mental model is "I deployed the supported configuration,"
which is true at deploy time. Drift happens because the operator does not
revisit the posture after deploy. Without an external wake-up (a bill from
a quota-burner, an extortion note, an inbound disclosure), the posture is
self-reinforcing.

This is the mechanism by which the auth-on-default thesis sustains itself
across time as populations. The thesis is not a static observation — it is
a **dynamic equilibrium**, maintained by the fact that the only force that
moves an operator off the default is external pressure.

## Procedural rules this insight generates

1. **Disclosure pipeline timing**: surveys of low-attacker-pressure platforms
   (Sourcegraph, Tabnine, AnythingLLM, RAGFlow, code-assistants generally)
   have a working window measured in weeks. Re-verify within 24h before
   send (Insight #28's rule) is overcautious here — re-verify within 7
   days is sufficient and amortizes the harvest cost
2. **Survey shelf-life rule** (Insight #28) re-scoped: applies to
   actively-extorted platform classes only (ES, MongoDB, Redis, Cassandra,
   exposed S3 with public-write). For everything else, the shelf-life is
   weeks
3. **Cross-survey delta as a published finding**: when surveying a platform
   that has a prior baseline, report the persistence ratio in the headline
   summary. It is methodology evidence in its own right (this insight
   exists because we measured it)
4. **Pre-disclosure verification gate**: still verify-before-send, but the
   cost-benefit calculation changes. For high-decay platforms, send within
   24h or re-verify; for low-decay platforms, batch and send weekly

## Negative form (when this rule does NOT hold)

- Platform under active extortion: Insight #28 applies (24h shelf-life)
- Platform with vendor-driven force-upgrade window (Auto-updating SaaS):
  shelf-life follows the vendor's release cadence, not the operator's
- Compliance-driven sweep (a CISA advisory targeting the class): rate
  changes once the advisory lands, watch for it

## Open question

What is the persistence rate at 30 days? 90 days? The 4-day window measured
here is short. The long-tail decay function is unknown and worth measuring on
the next OpenHands re-pass (planned 2026-06-15, 30-day mark).

## See also

- `insight-13-shipping-defaults-are-load-bearing.md` — the mechanism this rule
  is built on
- `insight-28-survey-shelf-life-exposure-to-extortion.md` — the high-decay
  comparison case
- `insight-29-overwhelming-prior-state-look-at-deltas-not-snapshots.md` — the
  methodology procedural-rule for measuring deltas
- `case-studies/commercial/code-assistants-population-survey-2026-05-18.md` —
  the source survey
