---
title: "Insight #29 — Snapshot vs delta: when prior state dominates the population, the snapshot is the campaign's aftermath; only the delta is fresh signal"
insight_number: 29
date: 2026-05-17
tags: [methodology, measurement, snapshot, delta, prior-state, retraction-friendly, statistics]
related_research:
  - case-studies/commercial/22-ai-stack-attribution-2026-05-17.md
  - methodology/insight-28-survey-shelf-life-exposure-to-extortion.md
source: 2026-05-17 retraction of an earlier Insight #28 claim; corrected by yesterday-vs-today delta measurement
---

# Insight #29 — Snapshot vs delta: when prior state dominates, the snapshot describes history, only the delta describes today

> A population observation says less than it appears to. When prior-state
> dominates the snapshot — 92.4% of "confirmed unauth" Elasticsearch hosts
> already in extortion-victim state at first observation — the snapshot
> records *what happened before we showed up*, not *what's happening now*.
> Treating that population-state number as a current-rate measurement is
> the canonical confident-but-wrong mistake. Re-probe within 24 hours and
> measure the **delta**: that's the fresh signal.

## The trap

We surveyed 5,037 unauthenticated Elasticsearch hosts. 71.6% had been
wiped by Meow / Indexrm extortion. The framing wrote itself: "71.6% wiped
in a 24-hour window — population is decaying fast, disclosure window is
short, codify as Insight #28 (24h shelf-life)."

The framing was wrong. We re-probed 24 hours later and ran the delta:

- 92.4% **already had** `read_me` in yesterday's snapshot. The campaign
  predates the survey.
- 1.7% got newly wiped between yesterday and today.
- 5.4% restored from backup between yesterday and today — **3× more than
  fresh wipes.**

Net population motion is *toward* operator recovery, not away. The
"71.6%-wiped" figure is the campaign's accumulated equilibrium, not its
current rate.

## The general rule

> When prior state dominates the population (any large absolute %), a
> single-snapshot measurement says **history**, not **rate**. To get a
> rate you must observe motion — at minimum two snapshots separated by
> the relevant timescale.

In statistics: the snapshot's percentage is a *survival function value*
($P(X \le t)$), not a *hazard rate* ($\lambda(t)$). The two have
different shapes and confusing them inverts inferences about timescale.

In threat-intel terms: a population that's 90% compromised tells you the
campaign **was** successful; it tells you nothing about whether the
campaign is currently active, dormant, or finished.

## When this trap is most dangerous

The class is everywhere; the worst cases:

1. **Mature, well-established campaigns** — the Meow / Indexrm wave
   against Elasticsearch (2020-present) has had enough time to reach
   steady-state. By the time anyone surveys the unauth ES population,
   the prior-victim cohort dominates. The same applies to Mongo Meow,
   Redis cryptominer drops, Cassandra-NoSQL extortion, and probably
   ICS-protocol exposures at scale.

2. **Static-config exposures** — anything where the underlying state
   changes infrequently (default credentials shipping with a Docker
   image, an open S3 bucket pattern, an unrotated API key). The
   snapshot will look the same week-over-week and feels like a rate
   when it's a stock.

3. **Default-on Tier-A* platforms** (Insight #13) — the operator
   population that *would* fix is small and slow; the operator
   population that *won't* fix is large and stable. The "% still
   exposed" looks like a current-state but is dominated by the "won't
   fix" cohort which is essentially stationary.

## When this trap is LESS dangerous

- **Tier-C platforms with auth-on-default** — the unauth population is
  small and ephemeral (someone misconfigured *just now*); a snapshot is
  closer to a rate because there's no large accumulation cohort.
- **Newly-launched campaigns** — when the survey is run shortly after a
  campaign starts, the prior-state cohort is small and the snapshot
  approximates the rate.
- **High-decay platforms** — anything where compromised hosts get cleaned
  fast (revoke + rebuild) so the population doesn't accumulate. The
  snapshot then more closely tracks the current rate.

## What we should have done

Before publishing the original Insight #28:

1. **Re-probe the same host list once.** A single 24-hour delta would
   have shown immediately that the "71.6% wiped" was equilibrium, not
   rate. Took 7 minutes of aimap wall-clock.

2. **Decompose the population.** "Wiped" hides three categories:
   pre-existing wipes, fresh wipes, recovered. Each has a different
   shape and meaning.

3. **Compare to a baseline.** What's the population-state of a *random*
   sample of unauth Elasticsearch hosts, not just the just-surveyed
   set? If 90% of *every* unauth ES population is read_me-flagged, our
   71.6% isn't even high — it's normal.

## The operationalized rule

> **Every "% of population" headline number requires a follow-on delta
> measurement before it gets framed as a rate.**
>
> Procedure: at minimum, re-probe the same host list once after a delay
> equal to the inferred timescale of the phenomenon. Compute the four
> categories (was-X-stays-X, was-X-leaves-X, was-Y-becomes-X,
> was-Y-stays-Y) and quote *only the delta*, not the static fraction, as
> a "rate."

For NuClide surveys going forward, add a **delta cell** to the case
study output table: "fresh-wipe rate (24h)", "operator-response rate
(24h)", separately from the population-state count.

## Why this got past us

The 71.6% figure was *also* novel and dramatic enough to feel like a
finding. Confidence inflation comes from how striking the number is, not
from how rigorously it was measured (Insight #6 again, applied to
ourselves). The smell-test that should have caught it: "if 71.6% wiped
in a *single 24-hour window* were really the rate, the population would
have hit 99.99% wiped within a week and there would be no unauth ES
hosts left to survey at all." The math doesn't admit it as a rate.
Snapshot-as-rate confusions usually have an absurd consequence one step
out from the claim; checking that consequence is the cheapest
verification.

## See also

- [`insight-06-conjunctive-marker-anchored-matchers.md`](insight-06-conjunctive-marker-anchored-matchers.md) — the upstream rule: anchor claims in actual measurement, never in appearance
- [`insight-15-dork-hits-are-not-platform-instances.md`](insight-15-dork-hits-are-not-platform-instances.md) — the related "% of dork hits = % of real platform" inflation pattern
- [`insight-28-survey-shelf-life-exposure-to-extortion.md`](insight-28-survey-shelf-life-exposure-to-extortion.md) — the now-corrected sibling insight
