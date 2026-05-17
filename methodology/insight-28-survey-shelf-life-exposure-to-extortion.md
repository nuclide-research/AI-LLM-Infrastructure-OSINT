---
title: "Insight #28 (RETRACTED). A population state is not a daily rate"
insight_number: 28
date: 2026-05-17
status: corrected
tags: [methodology, shelf-life, extortion, elasticsearch, meow, indexrm, disclosure-pipeline, retraction]
related_research:
  - case-studies/commercial/es-clickhouse-cross-stack-2026-05-17.md
  - case-studies/commercial/22-ai-stack-attribution-2026-05-17.md
  - case-studies/commercial/elasticsearch-ai-stack-population-survey-2026-05-16.md
source: 2026-05-17 24-hour re-probe of the 2026-05-16 Elasticsearch unauthenticated population (5,037 hosts)
---

# Insight #28 (RETRACTED). A population state is not a daily rate

## Retraction

The first version of this insight claimed 71.6% of the 5,037-host population was wiped by an automated extortion campaign in a 24-hour window. That framing is wrong as a 24-hour event rate. The corrected numbers come from re-probing the same host list 24 hours later.

| Category | Hosts | Share |
|---:|---:|---:|
| Already carried `read_me` at first observation (2026-05-16) | 4,411 | 92.4% |
| New wipes between yesterday and today | 79 | 1.7% |
| Restored from backup between yesterday and today | 258 | 5.4% |
| Both surveys clean | 286 | 6.0% |

The 71.6% figure is the accumulated state of a long-running campaign. The 1.7% number is the fresh daily wipe rate. Operators are restoring data about three times faster than new wipes accrue. The campaign predates the survey.

## What still applies

Disclosure pipelines should re-probe each host immediately before send. The reason is not "the campaign is fast." The reason is that operators are restoring data within the disclosure-batch turnaround window. A 24-hour-old "your data is wiped" message is wrong for ~5% of yesterday's wiped cohort by the time it arrives.

## What the campaign actually looks like

One dominant actor (`wendy.etabw@gmx.com`, wallet `bc1q38rjul6gdamfflf6p4ukz0ymtvfgfv2j9saf6r`) accounts for about 91% of the wiped population. Five paid victims so far, roughly $1,800 swept out. Two smaller actors carry the rest of the population and have zero income to date. Three actors total in the 150-host sample.

The dominant actor's `paste.sh` follow-up page is China-victim-aware. It includes P2P + VPN guidance for buying Bitcoin under PBOC restrictions. The wiped-population skew toward Tencent, Aliyun, and Huawei Cloud hosts matches that awareness.

## See also

- [`../case-studies/commercial/22-ai-stack-attribution-2026-05-17.md`](../case-studies/commercial/22-ai-stack-attribution-2026-05-17.md)
- [`../case-studies/commercial/meow-multi-actor-campaign-scope-2026-05-17.md`](../case-studies/commercial/meow-multi-actor-campaign-scope-2026-05-17.md)
- [`../evidence/2026-05-17-meow-attribution/`](../evidence/2026-05-17-meow-attribution/)
- [`insight-29-overwhelming-prior-state-look-at-deltas-not-snapshots.md`](insight-29-overwhelming-prior-state-look-at-deltas-not-snapshots.md)
