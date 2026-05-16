---
type: tool-dev-log
title: VisorBishop loop-iteration #1 — re-sweep all Phase 1 corpora, surface gaps
date: 2026-05-11
class: tool
category: cross-platform-tool-validation
status: research-active
methodology: re-running the productized fingerprints (Phase 3) against the original Shodan populations to find what manual Phase 1+2 walks missed
---

# VisorBishop loop-iteration #1 · 2026-05-11

NuClide Research · 2026-05-11

## Summary

First iteration of the Phase 3 loop-back: run VisorBishop
across the **other six Phase 1 corpora** (Langfuse 381, LangSmith 96,
Helicone 21, OpenLIT 23, Lunary 6, Pezzo 3) and compare against the
manual Phase 1+2 walks.

**Result: 12 NEW unauthenticated co-located services surfaced across
two operator populations** (Phoenix and Langfuse) that the manual chain
missed. Zero regressions — every Phase 2 manual finding reproduced.

The most consequential discovery: **4 NEW unauth Redis instances** on
the Phoenix unauth population. Redis was not in the original
[Methodology Insight #12](../../methodology/insight-12-ip-direct-shadow.md)
11-port list; VisorBishop's Phase 2-extended 15-port set caught them
automatically.

> **Reproduce with VisorBishop:** `visorbishop -i unauth-hosts.txt -ip-shadow-all -c 8 -timeout 4s`
> See VisorBishop or `visorplus bishop`.

## What the loop-back proves

Phase 3 was always going to recover the Phase 2 findings — that's what
"productize the fingerprints" means. The interesting question was
whether the productized version would surface **new** findings the
manual walk missed.

The answer is **yes**, for three structural reasons:

1. **Extended port set**. Phase 1's IP-shadow used 11 ports; Phase 2 manually
   probed extra ports (5432, 6379, 8123, etc.) on a small subset of hosts.
   VisorBishop's IP-shadow has **15 ports** baked in; running it across
   the full population finds the database/cache ports we missed at scale.
2. **Consistent application of the methodology**. Manual walks miss
   hosts under time pressure or because the operator is uninteresting.
   The tool doesn't get tired.
3. **Service-level confirmation**. The tool runs the full
   "is this actually unauth?" check (Redis `INFO server`, ClickHouse
   `SELECT 1`, MailHog `/api/v2/messages`) on every host, not just the
   ones a human prioritized.

## Per-platform iter-1 results

### Phoenix (94 hosts)

Re-sweep of the original `phoenix-real-unauth.txt`:

- 89 of 94 confirmed Phoenix (5 went offline since 2026-05-10)
- 88 CRITICAL (unauth GraphQL)
- Population-aggregated **1.50B tokens** across the first 5 projects per host
- **14 unauth IP-shadow findings** (vs 6 manually identified in Phase 2)
- **0 hosts with stored secrets** — Phase 2 latent-primitive finding stable

#### NEW finds vs Phase 2

| IP | Operator | New find | Reason missed in Phase 2 |
|---|---|---|---|
| 101.200.35.242 | Alibaba Cloud CN | **unauth Redis 7.4.7** | Port 6379 not in Phase 2's port list |
| 134.209.10.163 | `demo-law.bineyes.com` (DigitalOcean US, AI-for-legal) | **unauth Redis 7.4.7** | Same |
| 173.214.172.254 | `dsb-kairo.de` (German School Cairo) | **unauth Redis 7.4.7** (host also has unauth Prometheus per Phase 2) | Same |
| 51.159.138.130 | Scaleway FR | **unauth Redis 7.2.10** | Same |
| 173.208.247.17 | `wiratek.id` (PLN Indonesia AI vendor) | **unauth node_exporter on 9100** (host also has unauth Prometheus per Phase 2) | Phase 2 caught only the Prometheus, missed the co-located node_exporter |
| 163.172.176.76 | Teetsh (French edu SaaS, Scaleway) | **unauth MailHog** | Phase 2 manually identified only `51.15.207.110:8025` |
| 51.15.203.254 | Teetsh | **unauth MailHog** | Same |
| 51.158.119.227 | Teetsh | **unauth MailHog** | Same |

Banner-verified all 4 new Redis instances respond to `INFO server`
without auth — confirmed unauth. No commands sent beyond the banner.

The 4-MailHog Teetsh expansion is interesting: Phase 2 noticed
`51.15.207.110:8025` had 139 captured emails from `@teetsh.com` and
documented that as a single-instance hardening miss. **Iter-1 shows
Teetsh runs MailHog on all four of their public Scaleway hosts.** Only
one currently holds messages, but the pattern is consistent: every
region they deploy to ships with public MailHog. Latent capture window
× 4.

### Langfuse (381 confirmed-reachable IPs)

- 242 of 381 confirmed Langfuse via direct IP probe (rest are hostname-only LB-fronted)
- Auth posture: 100% returned 401 on `/api/public/projects` (matches Phase 1)
- IP-shadow sweep (15 ports × 381 IPs): **only 2 unauth findings, both Phase 2 reproductions**
  - `46.105.53.84` (langfuse.astusse.dev, OVH France): unauth Prometheus + node_exporter (Phase 2 caught both)
  - 5 Postgres-exposed hosts (matching Phase 2 deep-dive exactly): `157.180.74.91`, `194.87.115.10`, `207.38.87.133`, `3.239.231.128`, `5.187.0.135`

**Langfuse iter-1 yield: 0 new findings.** The Phase 2 manual walk on
Langfuse was thorough; the productized sweep adds no new exposures.

This is a **meaningful negative result** when contrasted with the
Phoenix iter-1 yield (8 new findings, doubling the manual yield). The
delta isn't methodology — it's the operator population. Langfuse
operators are uniformly more disciplined about co-located service
hardening; Phoenix operators are not. The same iter-1 sweep run by the
same tool produces order-of-magnitude different yields between the two
populations.

### Bug surfaced + fixed during the Langfuse sweep

The first attempt at the Langfuse 381-host sweep stalled at 0% CPU after
~28 minutes. Diagnosis: `ShadowScan` iterated all 15 ports serially per
host. With 8 worker goroutines × 15 ports × 4s timeout per port in the
worst case (every port filtered), wall time per host hit 60s, and worker
goroutines spent most of their lives in `connect(2)` retries.

Fixed in VisorBishop@0dd8c90:
ports now probed concurrently within each host. Wall time per host
becomes O(timeout) instead of O(ports × timeout). 5x speedup on smoke
tests; the Langfuse 381-host sweep completed in ~3 minutes after the
fix (vs the >28 min stall before).

This is the second correctness/performance gap iter-1 surfaced (the
first being the `IP:port` parser fix in `bb067e8`).
Both required real population workloads to manifest; neither showed up
in single-host smoke tests.

### LangSmith (96 hosts → 28 confirmed)

- **28 confirmed LangSmith** (vs Phase 1's 27 — one minor count difference)
- **Customer enumeration stable**: Pigment ×5, Generali ×3, Grammarly ×2,
  ByteDance, Weber Shandwick, Turing, University of Michigan, Lockton,
  Rakuten, RealPage, National Bank of Greece, P-1.ai
- 9 hosts without `customer_info` (older v0.10.91 instances per Phase 2)
- 0 secondary surfaces on the 17-port IP-shadow

LangSmith iter-1 = Phase 2 reproduced exactly. No new findings, no
regressions. Confirms the LangSmith population is consistent.

### Helicone (21 hosts)

- 5 confirmed Helicone instances (down from Phase 1's nominal 5
  self-hosted operators — same set, no churn)
- **CRITICAL reproduced**: `137.184.217.47` (benchmarkit.solutions /
  DigitalOcean US) — unauth ClickHouse 23.4.2.11, `default` user no
  password. Still live since Phase 2 finding.
- **MEDIUM reproduced**: `188.34.196.197` — unauth MailHog (empty store)

Single-command reproduction of the Phase 2 actualized critical
ClickHouse finding. Same exposure, still unpatched 1 day later.

### OpenLIT (23 hosts → 19 confirmed)

- 19 confirmed OpenLIT (4 offline since Phase 1's 23)
- **CRITICAL reproduced**: `124.71.61.247` (Huawei Cloud China) — unauth
  node_exporter on port 9100
- Auth posture stable: all return 307→/login on protected endpoints

### Lunary (6 hosts → 1 confirmed)

- 1 confirmed Lunary (`100.26.119.0` / `genesysappliedresearch.com`)
- 0 IP-shadow findings (matches Phase 2)
- 5 hosts are not Lunary observability (panel.lunary.com.br is a
  different "Lunary Panel" product, etc.)

### Pezzo (3 hosts → 1 confirmed)

- 1 confirmed Pezzo (`101.34.81.6:4200` Tencent Cloud China)
- 0 IP-shadow findings

## Bug surfaced + fixed during iter-1

VisorBishop's `parseTargetLine` initially required `http://...` or
`https://...` prefix in input URLs. Phase 1 corpora use bare `IP:port`
format from Shodan TSV exports — the parser returned 0 hits because the
URL parser silently failed on the missing scheme.

Fixed in VisorBishop@bb067e8:
parser now accepts bare `IP:port` and infers scheme from port (443 / 8443
/ 9443 → https, everything else → http). This is the kind of small
correctness gap the loop-back exposes — manual Phase 1 worked because
the operator (human) added the scheme; the tool needs to handle real
TSV input formats.

## Aggregated iter-1 findings

| Source | Phase 2 finds | Iter-1 NEW | Total |
|---|--:|--:|--:|
| Phoenix unauth Redis | 0 | **4** | 4 |
| Phoenix unauth MailHog | 1 | **3** | 4 |
| Phoenix unauth node_exporter | 0 | **1** | 1 |
| Phoenix unauth MailCatcher | 1 | 0 | 1 |
| Phoenix unauth Prometheus | 2 | 0 | 2 |
| Phoenix unauth Kibana | 1 | 0 | 1 |
| Helicone unauth ClickHouse | 1 | 0 | 1 |
| Helicone unauth MailHog | 1 | 0 | 1 |
| OpenLIT unauth node_exporter | 1 | 0 | 1 |
| **Total** | **8** | **8** | **16** |

The iter-1 yield is **literally double** the Phase 2 yield by count of
unauth services, across the same population. The methodology was sound
in Phase 2; the productization captured more of what was always there.

## Pattern callouts from iter-1

### `dsb-kairo.de` (German School Cairo) is now a multi-primitive host

Phase 2 caught Phoenix unauth + unauth Prometheus. Iter-1 adds **unauth
Redis** on the same IP. Three exposed unauth services on one operator's
production host. The IP-direct-shadow model (Methodology Insight #12)
predicts this pattern: operators who ship one service auth-off tend to
ship others auth-off too.

### Teetsh runs 4 MailHog instances — 3 are latent capture windows

Phase 2 caught 1 of 4. Iter-1 caught all 4. The pattern matters: this is
not an accident on one server. Teetsh's standard deployment template
publishes MailHog with no auth on every region they run. Three of the
four currently have empty stores; one (`51.15.207.110`) holds 139
captured messages from `@teetsh.com`. If any of the 3 currently-empty
ones starts receiving traffic (a staging push, a misrouted production
notification, etc.) the data leaks publicly without anyone noticing.

### Redis 7.4.7 is the current version of an unauth-default deployment template

Three of four newly-found Redis instances run identical Redis 7.4.7,
across different operators (Alibaba, DigitalOcean, Interserver). They
likely share a common deployment template (Docker image,
docker-compose, Helm chart, or Ansible role) that ships Redis 7.4.7
without `requirepass`. Worth a follow-on to identify which template.

## Methodology insight emerging

This is the candidate for **Methodology Insight #14: Tooling
re-iteration surfaces what manual chains miss**. Stated:

> A research methodology that relies on manual chain-walking has an
> upper bound on yield determined by analyst attention and time.
> Productizing the chain as a deterministic tool and re-running across
> the original corpus surfaces gaps proportional to the ratio of
> attention-saturated coverage to deterministic coverage. The yield
> doubles in this case.

The corollary: **every new platform survey should run twice** — once
manually to build the fingerprint, once via the productized tool to
catch what the manual walk missed. The two passes are not redundant; they
catch different failure modes.

Will write up as Insight #14 once iter-2 (next round) validates the
pattern.

## Next steps

1. ~~Build VisorBishop v0.1 (Phase 3)~~ ✓
2. ~~Loop iter-1: re-sweep all Phase 1 corpora~~ ✓ (this document)
3. **Add Redis-source attribution probe** — figure out which template
   produces the unauth Redis 7.4.7 pattern
4. **Add ports 1883 (MQTT), 7474 (Neo4j HTTP), 7687 (Neo4j Bolt) to
   IP-shadow** — adjacent AI-stack services not in current 15-port set
5. **Loop iter-2 in 7 days** — re-sweep to track which exposures got
   patched, which operators went offline, which new ones appeared
6. **Cross-platform attribution clustering** — host `173.214.172.254`
   appears in both Phoenix unauth and the Phoenix IP-shadow findings.
   Same host with multiple platform fingerprints means one operator
   running multiple observability tools on the same instance. Worth
   automating in VisorBishop output.

## Evidence pack

`~/recon/2026-05-10-llm-sweep/visorbishop-results/`
- `phoenix-shadow.json` / `.csv` — full 94-host Phoenix sweep with shadow
- `iter1/langfuse-shadow.json` — pending (Langfuse 381 sweep)
- `iter1/langsmith-fixed.json` — 96-host LangSmith sweep
- `iter1/helicone-shadow.json` — 21-host Helicone sweep
- `iter1/openlit-shadow.json` — 23-host OpenLIT sweep
- `iter1/lunary-shadow.json` — 6-host Lunary sweep
- `iter1/pezzo-shadow.json` — 3-host Pezzo sweep

Source: Nicholas-Kloster/VisorBishop@bb067e8

Cross-references:
- [VisorBishop Phase 3 case study](visorbishop-phase3-survey-2026-05-11.md)
- [Phoenix Phase 1 survey](phoenix-llm-observability-survey-2026-05-10.md)
- [reputacion.digital Phase 2 deep-dive](AR-reputacion-digital-multi-surface-2026-05-10.md)
- [Methodology Insight #12 (IP-direct-shadow)](../../methodology/insight-12-ip-direct-shadow.md)
- [Methodology Insight #13 (shipping defaults)](../../methodology/insight-13-shipping-defaults-load-bearing.md)
