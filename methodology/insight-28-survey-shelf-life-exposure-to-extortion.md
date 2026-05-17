---
title: "Insight #28 — Survey shelf-life: exposure-to-extortion ≈ 24h for unauth Elasticsearch; harvest-and-send disclosure pipelines need re-verification between the two"
insight_number: 28
date: 2026-05-17
tags: [methodology, shelf-life, extortion, elasticsearch, meow, indexrm, disclosure-pipeline]
related_research:
  - case-studies/commercial/es-clickhouse-cross-stack-2026-05-17.md
  - case-studies/commercial/elasticsearch-ai-stack-population-survey-2026-05-16.md
source: 2026-05-17 24-hour re-probe of the 2026-05-16 Elasticsearch unauth population (5,037 hosts)
---

# Insight #28 — Survey shelf-life: exposure-to-extortion ≈ 24h for unauth Elasticsearch

> A survey result has a shelf life. For unauthenticated Elasticsearch, 71.6%
> of yesterday's 5,037-host population was wiped by an automated extortion
> campaign in the 24-hour window between harvest and re-probe. Disclosure
> pipelines that send "your host X is exposed" reports built from yesterday's
> harvest will, more than half the time, be wrong by the time they arrive.

## The measurement

On 2026-05-16 we confirmed 5,037 unauthenticated Elasticsearch hosts at
population scale (`elasticsearch-ai-stack-population-survey-2026-05-16.md`).
Today, 2026-05-17, we re-probed the same host list with aimap v1.9.8's
new `enumElasticsearch` deep-enum.

**24-hour delta:**

| Yesterday | Today | Δ |
|---|---|---|
| 5,037 confirmed unauth | 4,564 still unauth | −473 (offline / port closed) |
| 0 wiped | 3,604 wiped + `read_me` index left (71.6%) | +3,604 |
| 0 operators auth-added | 0 operators auth-added | 0 |
| 94 hosts on ES 2.9.0 | 90 of 94 wiped (95.7%) | — |

Wipe rate scales with version age — 95.7% on ES 2.9.0 (the ancient
unauth-RCE class), 88.4% on 7.17.0 (the largest single-version cohort).
The wipe signature is a single small index named `read_me`
(or `read_me_first` / `recover_data`) containing a single ransom
document — consistent with the Meow / Indexrm extortion family that
has been active against open Elasticsearch since 2020.

## Why this is methodology-relevant

A NuClide survey produces a static snapshot of an unauth population at a
moment in time. **For platform classes targeted by automated extortion,
that snapshot decays at population scale faster than the disclosure
workflow.** The implications:

1. **Disclosure batches built from a survey older than 24h need
   re-verification before sending.** A "your host X is exposed unauth"
   report sent to an operator whose host was wiped overnight reads
   wrong — the operator is already in extortion-recovery mode, and the
   disclosure misses the actual current state. Worse, it raises the
   credibility cost of subsequent legitimate disclosures from us. Build
   re-verify-then-send into the pipeline, not harvest-then-send.

2. **Population-rate claims have decay built in.** "5,037 unauth ES
   instances at population scale" is true *as of the harvest timestamp*.
   By the time the report is read, that number is closer to 1,433
   (5,037 − 3,604 wiped). The case study should report the harvest
   number with the timestamp, and ideally a follow-up number from a
   re-probe ≤ 24h after.

3. **The extortion campaign is the more dangerous version of yesterday's
   survey.** Yesterday's 5,037 raw exposures matter; the 3,604 that got
   wiped between yesterday and today matter more — that is the live
   harm rate. The methodology should capture both.

4. **Operators don't fix on the timescale attackers exploit.** Zero
   operators added auth between yesterday and today. The
   mean-time-to-extortion (≤ 24h) is shorter than the
   mean-time-to-remediation (≥ days). For platforms in this regime,
   the only effective disclosure is one that arrives before the attacker
   does — i.e., from a *forward-looking* harvester that finds the host
   the same day it gets deployed. This is an argument for continuous
   monitoring rather than discrete-snapshot surveys for high-decay
   platform classes.

## What does NOT have this shelf life

The 24-hour wipe wave is **Elasticsearch-specific** in the 2026-05-17
window. Yesterday's ClickHouse population (1,832 hosts) was re-probed
the same day; **zero ClickHouse hosts were wiped**. Hypothesis: the
Meow / Indexrm extortion tooling is ES-tuned (REST API + `_search` +
`_delete_by_query` semantics); ClickHouse's HTTP query interface is
less indexed by mass-scanners, the wipe semantics are less convenient
(DROP DATABASE per-tenant), and the brand-recognition for ransomware
demands is lower. The same shelf-life math does *not* apply to CH.

Other platform classes likely fall on this spectrum:
- **MongoDB** — historically the canonical Meow target, ~85%+ of
  unauth Mongo got wiped in the 2020 wave. Shelf-life ≤ 24h.
- **CouchDB / Cassandra** — also extortion-targeted historically, expect
  similar.
- **Redis** — different campaign (cryptominer drop via SLAVEOF), but
  same short shelf-life.
- **Vector DBs (Qdrant, Chroma, Weaviate, Milvus)** — no known extortion
  campaign yet; shelf-life likely longer, but the *raw exposure window*
  metric still matters.
- **MLflow / Phoenix / Langfuse** — observability-tier, no extortion
  campaign; longer shelf-life.

**Rule of thumb:** if the platform has known automated-extortion tooling,
treat survey shelf-life as < 1 day. Otherwise, ≤ 1 week is reasonable
before staleness creeps in.

## What the methodology does about it

1. **Re-verify-before-disclosure step.** Disclosure batches re-probe each
   target host immediately before send. If the target is wiped /
   auth-gated / offline, the disclosure is reformulated or dropped.

2. **Two-timestamp survey output.** Case studies for high-decay
   platforms report both harvest timestamp and a re-probe timestamp
   ≤ 24h after, with deltas.

3. **Population-decay tracking.** `nuclide.db` lifecycle status now
   includes `archived` with reason `wiped-by-extortion-campaign-<date>`
   for confirmed-wiped hosts. This preserves the historical record of
   "this host was exposed → got wiped" without conflating it with the
   "host fixed itself" case.

4. **VisorBishop re-run cadence.** For platform classes in the high-decay
   bucket, VisorBishop's re-run frequency should match the
   exposure-to-extortion window — for ES, daily re-runs over the same
   host list capture the campaign in real-time.

5. **Disclosure value compounds.** A disclosure that arrives *before* an
   automated extortion campaign hits has 1× expected outcome value;
   one that arrives after has near-zero (the operator is already in
   recovery mode, knows they were exposed, and is unlikely to act on
   our follow-up). Time-to-disclosure is the dominant variable for
   high-decay platforms.

## See also

- [`../case-studies/commercial/es-clickhouse-cross-stack-2026-05-17.md`](../case-studies/commercial/es-clickhouse-cross-stack-2026-05-17.md) — the source survey
- [`../case-studies/commercial/elasticsearch-ai-stack-population-survey-2026-05-16.md`](../case-studies/commercial/elasticsearch-ai-stack-population-survey-2026-05-16.md) — the parent (24h-stale) survey
- [`insight-13-shipping-defaults-are-load-bearing.md`](insight-13-shipping-defaults-are-load-bearing.md) — the related thesis (it's the auth-on-default deployment that gets wiped; the auth-on-default vendors do not appear in the wiped set)
