---
title: "Insight #27 — Docker-image-template dominance: single-version clusters track image-tag pinning, not natural distribution"
insight_number: 27
date: 2026-05-16
tags: [methodology, docker, version-distribution, defaults, deployment-templates]
related_research:
  - case-studies/commercial/vectordb-stragglers-population-survey-2026-05-16.md
  - case-studies/commercial/clickhouse-population-survey-2026-05-16.md
  - case-studies/commercial/elasticsearch-ai-stack-population-survey-2026-05-16.md
source: 2026-05-16 10-survey batch (Solr / Elasticsearch / ClickHouse version-distribution observation)
---

# Insight #27 — Docker-image-template dominance: single-version clusters track image-tag pinning, not natural distribution

> When a population-scale unauth fleet shows one version dominating by 5–30× over the next, that is the operator-population deploying the SAME Docker image. The version distribution is a signature of which image-tag people pulled, not of natural version-rollout dynamics. The image's default auth posture becomes the population's auth posture.

## The pattern (multi-survey confirmed in one day)

Three independent surveys on 2026-05-16 surfaced the same shape:

| Survey | Platform | Total unauth | Dominant version | Count | Dominance |
|---|---|---|---|---|---|
| Vector-DB stragglers | Apache Solr | 613 | **7.6.0** (2018) | 516 | **84%** (27× over next) |
| Specialty data layers | ClickHouse | 1,832 | **22.3.20.29** (2022 LTS) | 1,013 | **55%** (24× over next) |
| Elasticsearch (AI-stack) | Elasticsearch | 5,037 | 7.17.0 (2022) | 239 | **5%** (1.3× over next) |

The Solr and ClickHouse cases are clearest: one version dominates the unauth fleet by an order of magnitude. The Elasticsearch case is fainter (7.x family dominant but spread across many sub-versions), suggesting Elasticsearch's image-rollout is more distributed than Solr's or ClickHouse's.

## Why this happens

Three causal mechanisms in tension:

1. **Operator inertia** — once a Docker image is deployed, operators rarely re-pull. If they `docker pull clickhouse:22.3` in 2022 and the container has been running since, it stays on 22.3 indefinitely. Even when the operator restarts the container, they restart the same locally-cached image.

2. **Image-tag pinning** — operators who pinned to a specific tag (`solr:7.6.0`, `clickhouse:22.3`) when they wrote their docker-compose.yml in 2018-2022 have that pin in their git history. Re-deployments re-pull the same tag.

3. **Marketplace / one-click templates** — cloud marketplaces (Digital Ocean droplets, AWS Marketplace AMIs, 1-click Solr/ClickHouse/Elasticsearch templates) often pin to a specific version at the time they're built and rarely re-published. Customers who use the marketplace template inherit the version.

The combination produces a population whose version-distribution is dominated by **whatever image-tag was popular when the deployment was created**, not by natural upgrade dynamics.

## Methodology consequence

When a population-survey shows single-version dominance, treat it as:

1. **A deployment-template phenomenon, not an operator-laziness phenomenon.** Each individual operator may have deployed responsibly using a then-current image; the population shape reflects upstream-image age, not operator skill.
2. **The image's defaults ARE the population's defaults.** If the dominant image ships auth-off (Solr 7.6.0 Docker image, ClickHouse default user no password, Elasticsearch official image with `xpack.security.enabled` undefined), the population inherits that exact posture.
3. **CVE chains at the dominant version are commodity-actionable.** Solr 7.6.0 = CVE-2019-17558 Velocity RCE etc.; ClickHouse 22.3 doesn't have a comparable unauth-RCE class but the data-disclosure is full-DB; Elasticsearch 2.9.0 / 7.x have a long unauth-RCE history. Knowing the dominant version is enough to predict the dominant exploit class.
4. **The disclosure target shifts upstream.** Rather than per-host outreach to 516 Solr operators, the right move is a coordinated note to the Solr Project + Docker Hub maintainer of `solr:7.x` image + cloud-marketplace template maintainers. One change at the image layer remediates 516 hosts in one re-pull cycle.

## Per-platform consequence

**Solr:** The 84% dominance on 7.6.0 (2018) is the strongest case. Almost certainly a single popular Docker image — the official Apache Solr container `solr:7.6.0` was widely pulled in 2019 for production. Deprecated since 2021 (Solr 7.x EOL). The 516-host cluster is a single-image deployment phenomenon.

**ClickHouse:** 55% dominance on 22.3.20.29 (2022 LTS) reflects the `clickhouse:22.3` tag pinning. ClickHouse marketed 22.3 as the LTS line; operators who built docker-compose in 2022 pinned `:22.3` (LTS) and have not updated. Fewer published unauth-RCE class CVEs on ClickHouse, but full database disclosure is the consequence.

**Elasticsearch:** Lower dominance (5% on any single sub-version) but the **7.x family dominates** across all sub-versions. Elasticsearch's official Docker image at `elasticsearch:7.x` ships with `xpack.security.enabled=false` as the open-source default. The population is broadly stuck on EOL 7.x.

## How to detect the pattern

For any population survey, the version-aggregation step should:

1. Sort versions by count
2. Compute the dominance ratio: `top1_count / top2_count`
3. If ratio > 5× and top1 represents > 30% of unauth, flag as **single-image-template** pattern
4. Identify the Docker image tag(s) that match that version
5. Verify (where possible) by checking response headers or build metadata for image-fingerprint signals

This is queued as a `visorlog-stats` enhancement: a ledger query that surfaces version-dominance clusters automatically when the underlying survey raw_data has `version` fields.

## What this Insight does NOT say

This is not a claim that all single-version clusters are Docker-image-driven. Some are:

- True version-rollout snapshots (a new release happened recently, operators are mid-upgrade)
- Hardware / OS package manager versions (yum install solr-version-X)
- License-locked enterprise binaries

But for open-source platforms with widely-pulled Docker images, the dominance ratio observed here (5× to 27×) is too sharp to be natural rollout dynamics. It's image-template propagation.

## See also

- [[insight-13-shipping-defaults-are-load-bearing]] — the meta-principle: framework defaults shape the population. Insight #27 is the *delivery vector* by which framework defaults reach operators.
- [[insight-25-falsification-confirmation-tier-c-platforms]] — Tier-A* category. Docker-image defaults often ship auth-off; the population manifests that default.
- [[insight-26-shodan-facet-fp-rate-escalates-with-token-commonality]] — different methodology trap, same daily-batch observation.
- [`vectordb-stragglers-population-survey-2026-05-16.md`](../case-studies/commercial/vectordb-stragglers-population-survey-2026-05-16.md) — Solr 7.6.0 finding
- [`clickhouse-population-survey-2026-05-16.md`](../case-studies/commercial/clickhouse-population-survey-2026-05-16.md) — ClickHouse 22.3.20.29 finding
- [`elasticsearch-ai-stack-population-survey-2026-05-16.md`](../case-studies/commercial/elasticsearch-ai-stack-population-survey-2026-05-16.md) — Elasticsearch 7.x family dominance
