---
title: "Insight #28 (RETRACTED + CORRECTED) — Population-state vs. fresh-wipe rate are different measurements; the survey captures long-running campaign aftermath, not 24h activity"
insight_number: 28
date: 2026-05-17
status: corrected
tags: [methodology, shelf-life, extortion, elasticsearch, meow, indexrm, disclosure-pipeline, retraction]
related_research:
  - case-studies/commercial/es-clickhouse-cross-stack-2026-05-17.md
  - case-studies/commercial/22-ai-stack-attribution-2026-05-17.md
  - case-studies/commercial/elasticsearch-ai-stack-population-survey-2026-05-16.md
source: 2026-05-17 24-hour re-probe of the 2026-05-16 Elasticsearch unauth population (5,037 hosts), with day-after correction
---

# Insight #28 (CORRECTED) — Population-state vs fresh-wipe rate are different measurements

> **Retraction notice.** The first version of this insight (committed earlier on 2026-05-17) claimed *"71.6% of yesterday's 5,037-host population was wiped by an automated extortion campaign in the 24-hour window between harvest and re-probe."* That framing is **wrong** as a 24-hour event measurement. The corrected analysis below shows that 92.4% of yesterday's "confirmed unauth" hosts **already had the Meow extortion `read_me` index in yesterday's snapshot** — the campaign predates the 2026-05-16 survey. The real 24-hour event rate is **1.7% new wipes vs. 5.4% operator-restored** — operators are recovering ~3× faster than new wipes accrue.
>
> The corrected lesson is methodology-relevant in a different way: **a survey captures the post-campaign equilibrium state, not the live campaign rate.** Two distinct measurements live behind a single "% wiped" headline, and conflating them produces wrong claims about timescales and operator response.

## The numbers that were wrong, and the corrected numbers

Yesterday (2026-05-16) we ran `fast_enum_es.py` against 9,263 candidate Elasticsearch hosts. The script confirmed 5,037 as "unauth + data visible" by issuing `GET /_cat/indices` and counting any host that returned a JSON list. It did **not** classify hosts whose visible state was `read_me`-only as already-wiped — it only filtered for the indices-present property.

Today (2026-05-17) we re-ran with aimap v1.9.8 against the same 5,037 host list. 4,776 still respond to fingerprinting. Of those:

| Category | Count | % | What it actually means |
|---:|---:|---:|---|
| Had `read_me` in **yesterday's** snapshot | 4,411 | **92.4%** | The Meow campaign predates 2026-05-16. We captured a long-running equilibrium, not a wave |
| New `read_me` between yesterday → today | **79** | **1.7%** | The genuine 24-hour wipe rate — much lower than the population-state implies |
| `read_me` yesterday, clean today | 258 | 5.4% | Operator-restored from backup. **3× more than new wipes.** Real operator response is happening |
| Both surveys clean | 286 | 6.0% | Neither yet hit |

The first version of this insight conflated "population-state" with "fresh-wipe rate" and treated the 71.6% snapshot figure as a 24-hour event. **It is not.** The 71.6% is the equilibrium of a multi-week-or-longer campaign; the 1.7% is the actual fresh-wipe pulse over a single day. The shelf-life claim ("≤ 24h before disclosure becomes stale") doesn't hold from this measurement — the population state has been *more stable* than predicted, not less.

## Why the framing matters in practice

If you draft a disclosure framing "your host is being wiped *right now*, hours-not-days" off the population-state number, you will be wrong with operators whose hosts have been in this state for weeks. Two known cases from this batch:

- **`103.69.124.214` (Nepal MoHP HMIS / Open Concept Lab)** — yesterday's snapshot reported `read_me` only; today's deeper probe shows 8 indices including the 318k-doc `concepts` index intact alongside `read_me`. The host has been in this **`read_me` + data` co-existence state** for an unknown duration; we cannot infer how recent the attacker's establishment of control was.
- **`135.125.201.31` (NewsBlur)** — same yesterday and today; the `read_me` + `discover-stories-openai-index` co-existence has likely been stable for days or longer.

The **schema-disclosure finding remains valid** — both hosts are reachable unauth and the operator's data is exposed and labeled-as-attacker-controlled — but the timescale framing in the original disclosure draft (*"hours-not-days; mid-wipe imminent"*) is unsupported by the actual data. **Corrected disclosure framing**: "The host is reachable unauthenticated. An automated extortion actor has established control on it (`read_me` index present). Your data is still alive but at indefinite risk of wipe on the attacker's next pass."

## What does carry forward — the re-verify-before-send rule

Even though the timescale claim was wrong, the procedural recommendation **survives** for a related reason: **operators are restoring data on the timescale of the disclosure send**. Of 4,411 hosts that had `read_me` in yesterday's snapshot, **258 (5.4%) restored their data overnight** — visible only because we re-probed. A disclosure sent today claiming "your data is wiped" would be wrong for 258 of yesterday's confirmed cases.

**Operationalized rule (corrected):** disclosure-pipeline state must be ≤ 24 hours old at send time. Not because the campaign is moving fast — it isn't — but because **operators are responding, and our snapshots go stale on the timescale of their recovery**. Send a per-host re-probe immediately before each disclosure goes out.

## What's actually happening with the campaign — corrected picture

- **One actor.** Three independent sample hosts (104.197.153.228, 104.248.1.214, 101.44.26.183) carry **identical ransom notes**: same BTC wallet (`bc1q38rjul6gdamfflf6p4ukz0ymtvfgfv2j9saf6r`), same email (`wendy.etabw@gmx.com`), same per-host code `0SH7HH1Q72JL` (which is therefore not per-host — bot template lie). One actor, broad spam.
- **Five paid victims.** mempool.space wallet inspection shows 5 incoming payments + sweep transactions = ~0.018 BTC / ~$1,800 received and cashed out as of 2026-05-17. **0.11% pay rate** across yesterday's 4,411 wiped hosts.
- **Steady-state, not wave.** 1.7% daily new-wipe rate + 5.4% daily restore rate. Net population-state is gently moving *toward* operator recovery, not away. The 71.6%-wiped equilibrium has been stable.
- **China-aware.** The attacker's decrypted paste.sh follow-up explicitly addresses Chinese victims with P2P/VPN guidance for buying BTC inside China's crypto restrictions. The wiped-population skew toward Tencent / Aliyun / Huawei Cloud-hosted operators is correlated with this awareness.

## See also

- [`../case-studies/commercial/22-ai-stack-attribution-2026-05-17.md`](../case-studies/commercial/22-ai-stack-attribution-2026-05-17.md) — the attribution sweep that surfaced the contradiction
- [`../case-studies/commercial/es-clickhouse-cross-stack-2026-05-17.md`](../case-studies/commercial/es-clickhouse-cross-stack-2026-05-17.md) — the parent survey (some of its headline numbers were wrong; corrections incoming)
- [`../evidence/2026-05-17-meow-attribution/`](../evidence/2026-05-17-meow-attribution/) — ransom note, decrypted paste.sh content, wallet evidence
- [`insight-29-overwhelming-prior-state-look-at-deltas-not-snapshots.md`](insight-29-overwhelming-prior-state-look-at-deltas-not-snapshots.md) — the meta-lesson on snapshot vs delta measurement
- [`insight-06-conjunctive-marker-anchored-matchers.md`](insight-06-conjunctive-marker-anchored-matchers.md) — the parent rule: anchor every claim in actual measurement, not appearance
