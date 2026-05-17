---
title: "Insight #29. Snapshot vs delta. Prior state dominates the headline."
insight_number: 29
date: 2026-05-17
tags: [methodology, measurement, snapshot, delta, prior-state, retraction-friendly, statistics]
related_research:
  - case-studies/commercial/22-ai-stack-attribution-2026-05-17.md
  - case-studies/commercial/meow-multi-actor-campaign-scope-2026-05-17.md
  - methodology/insight-28-survey-shelf-life-exposure-to-extortion.md
source: 2026-05-17 retraction of an earlier Insight #28 claim
---

# Insight #29. Snapshot vs delta

A single observation of a population says one thing. Two observations say another. When a campaign has been running long enough to saturate the population, the snapshot reports history. Only the delta reports today.

## What happened

We surveyed 5,037 unauthenticated Elasticsearch hosts. 71.6% had a `read_me` index. The framing wrote itself. We called it a 24-hour wipe rate, codified it as Insight #28, sent disclosure copy that used it.

We re-probed 24 hours later and computed the four-cell delta:

- 92.4% already had `read_me` at the first probe.
- 1.7% gained it between probes.
- 5.4% lost it (operators restored data).
- 6.0% stayed clean.

Net direction is toward operator recovery, not away. The 71.6% is the accumulated state of a long-running campaign, not a fresh rate.

## The general rule

A single-snapshot percentage on a population that has a large prior state describes the prior. To get a rate, observe motion. Two snapshots separated by the relevant timescale. Compute the four cells: was-X-stays-X, was-X-leaves-X, was-Y-becomes-X, was-Y-stays-Y. Quote the delta as the rate. Quote the snapshot as the prior.

## When the trap matters most

1. Mature campaigns where the active actor has had time to saturate the population. Meow against Elasticsearch is the canonical example. Same applies to MongoDB Meow, Redis cryptominer drops, Cassandra extortion, ICS-protocol exposure.
2. Static-config exposures where the underlying state changes slowly. Default credentials. Open S3 buckets. Unrotated API keys. The snapshot looks the same week-over-week and reads as a rate when it is a stock.
3. Default-on Tier-A* platforms (Insight #13). The "won't fix" cohort is large and stable. The "% still exposed" looks like a current state and is dominated by stationary inertia.

## When the trap matters less

Tier-C platforms where unauthenticated instances are small and ephemeral. Newly-launched campaigns where the prior cohort is small. High-decay platforms where compromised hosts get cleaned fast.

Rule of thumb. Known automated-extortion tooling on the platform: shelf-life under one day. Otherwise: one week before staleness creeps in.

## What we do about it now

1. Re-probe before disclosure send. Always.
2. Two-timestamp survey output. Each case study reports harvest time and re-probe time with the delta between.
3. Lifecycle status `archived` with reason `wiped-by-extortion-campaign-<date>` for confirmed-wiped hosts. The historical record stays.
4. For high-decay platforms, daily VisorBishop re-runs over the same host list.
5. Time-to-disclosure is the dominant variable. A disclosure that arrives before the actor has near-full expected value. One that arrives after has near-zero. Optimize the workflow for early arrival.

## The same mistake we made on actor attribution

Three sample wiped hosts carried identical ransom notes. Same wallet, same email, same code. We confidently extrapolated single-actor at population scale. Sent a UCloud disclosure that named the actor for the hospital host on that basis.

The 150-host campaign-scope check found three actors operating the same population in parallel. The hospital host fell under the minority actor with a different wallet, a different email, and a Tor-routed mail service. We sent a correction within an hour.

The trap is the same. A small sample's identity is the sample's identity, not the population's. Per-host claims need per-host evidence.

## Procedural rule

Every "% of population" headline number requires a follow-on delta measurement before it is framed as a rate.

Every per-host claim that depends on an actor, classifier, or category attribution must be verified on that specific host. Not inferred from population-level patterns.

The population stats describe the prior. The per-host probe is the evidence that updates the prior to a posterior for the target in front of you.

## See also

- [`insight-06-conjunctive-marker-anchored-matchers.md`](insight-06-conjunctive-marker-anchored-matchers.md)
- [`insight-15-dork-hits-are-not-platform-instances.md`](insight-15-dork-hits-are-not-platform-instances.md)
- [`insight-28-survey-shelf-life-exposure-to-extortion.md`](insight-28-survey-shelf-life-exposure-to-extortion.md)
- [`../case-studies/commercial/meow-multi-actor-campaign-scope-2026-05-17.md`](../case-studies/commercial/meow-multi-actor-campaign-scope-2026-05-17.md)
