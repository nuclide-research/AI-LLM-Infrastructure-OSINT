---
type: survey
---

# ClickHouse Population Survey (2026-05-16)

_NuClide Research · 2026-05-16 (Survey 7 of the day's 10-category batch, largest single survey)_
_Closes: category 02 / specialty data layers — ClickHouse half_

---

## Summary

Largest single-platform population survey of the day. ClickHouse is the OLAP database that powers most modern observability stacks (SigNoz, Plausible, PostHog, Helicone, Phoenix-on-OTLP) — wherever an AI/LLM service emits traces or analytics, there's often a ClickHouse behind it.

- **65,100 candidate ip:port pairs harvested** via `product:"ClickHouse"` Shodan facet (harvest capped at ~65K)
- Probed via `fast_enum_clickhouse.py` (threads=250, ~35 min)
- **1,832 confirmed unauth ClickHouse instances** (2.81% real-rate at population scale)
- 7,337 auth-gated (11.3%)
- 2,563 partial-open (`/ping` returns 200 but `SHOW DATABASES` gated)
- 35,169 dead (54%)
- 18,199 unknown (28% — many returned 200 to /ping but other endpoints hung)

**Headline:** ~10K real ClickHouse instances reachable, 18% unauth. The user-database names disclose the observability stack of the operator — **SigNoz traces/metrics/logs (21 each), PostHog (8), Plausible Analytics (11), OpenTelemetry (6)** — and via those names, the operator's entire LLM observability pipeline.

---

## What ClickHouse leaks unauth

`/?query=SHOW DATABASES FORMAT JSON` returns the full list of databases. Each database name discloses the operator's application stack. Top patterns:

```
  32  analytics                  (generic - any analytics workload)
  21  signoz_traces              \
  21  signoz_metrics             |  SigNoz observability platform (often AI-stack obs)
  21  signoz_logs                /
  11  plausible_events_db        Plausible Analytics
   8  posthog                    PostHog product analytics
   8  netflow                    network flow data (high sensitivity)
   8  _temporary_and_external_tables
   7  ftacs_qoe_ui_data          FTACS Quality-of-Experience (Huawei FTACS network ops)
   6  otel                       OpenTelemetry traces (often LLM call traces)
   6  geo                        geographic data
```

The SigNoz 21×21×21 trinity (traces/metrics/logs) is interesting — it's 21 operators all running the same observability stack, each leaking the three-database pattern unauth. SigNoz is the leading open-source observability platform with **first-class LLM-tracing support** (it ingests OTLP semantic-conventions for genai). The 21 unauth SigNoz deployments are very likely AI-stack observability backends with LLM traces visible.

---

## The 6 explicit AI-stack databases

| Host | Version | AI-stack DB name(s) | Operator inference |
|---|---|---|---|
| `108.248.232.250:8123` | v25.12.1.402 | `vllm_service` | vLLM inference observability — operator running vLLM with ClickHouse backend for trace/metric storage |
| `135.181.83.69:8123` | v25.1.5.31 | `observability` | Generic observability stack (probably OTLP or SigNoz, not labeled by db-name) |
| `178.156.183.199:8123` | (vNULL) | **`ai_hedge_fund`** | **AI-driven hedge fund operator** — DB name suggests algorithmic trading with AI |
| `187.45.178.153:8123` | v25.12.4.35 | `develop_biapp_iza_observability` | Multi-tenant BI app with observability database (IZA tenant, develop environment) |
| `85.10.194.126:8123` | v24.3.1.2672 | `scentedai_fragid_new` | **scentedai.com** — AI-driven fragrance identification — `fragid` is fragrance-ID, new schema |
| `122.51.12.54:8123` | v23.3.2.37 | `qinghai_platform` | CN Qinghai province platform — could be government workload |

**Operator-attribution highlights:**
- **`ai_hedge_fund`** — the name discloses the operator's entire business model. An AI-driven hedge fund running ClickHouse unauth with that database name reachable means anyone can query their trading data.
- **`scentedai_fragid_new`** — Scented AI (https://www.scentedai.com), a fragrance-identification AI startup, running their fragrance-ID database unauth on a Hetzner IP. Operator product disclosure via DB name.
- **`vllm_service`** — operator running vLLM (open-source LLM inference) with ClickHouse as the trace backend. Unauth = full LLM call history visible.

---

## Version distribution (the Docker-image-template phenomenon, again)

```
 1013  v22.3.20.29   ← single-version dominant cluster (55% of unauth fleet)
  110  vNULL          (version-query failed)
   42  v24.8.14.39
   28  v22.1.3.7
   24  v23.8.16.16
   22  v24.10.2.80
   19  v26.3.9.8     ← bleeding edge
   19  v24.3.18.7
   16  v24.1.8.22
   16  v22.2.2.1
```

**Same pattern as Solr 7.6.0 (516 hosts) and Elasticsearch 7.17.0 (239 hosts) from today's batch:** a single-version Docker image dominates the unauth population. 1,013 hosts on ClickHouse 22.3.20.29 is the largest single-version cluster of the day. That version is the LTS line from late 2022 — operators using `clickhouse/clickhouse-server:22.3` or `:lts` (which pinned to 22.3.x for years).

The Docker-image-template phenomenon is now multi-survey-confirmed and warrants its own Insight (queued).

---

## Methodology placement

ClickHouse is **Tier-A* (auth optional, off-by-default in Docker image)**. The official `clickhouse/clickhouse-server` Docker image ships with a default user account named `default` with NO password. Operators must:

1. Set `CLICKHOUSE_USER` + `CLICKHOUSE_PASSWORD` env vars at container start, OR
2. Modify `/etc/clickhouse-server/users.xml` to set a password for `default`

The 1,832-host unauth population shows ~18% of reachable ClickHouse operators skip both steps. Auth-gated 7,337 + partial-open 2,563 = 9,900 operators DID set up auth correctly.

Adds ClickHouse (Docker default) to the Tier-A* family alongside Elasticsearch (today), Airflow, LiveKit example-template, and DCGM-exporter. The Tier-A* family is now 5 platforms strong.

---

## Cross-survey colocation

| Pair | Overlap |
|---|---|
| ClickHouse ∩ Elasticsearch (same-day, 5,037 unauth) | TBD via visorlog ledger diff (likely some — both used as observability backends) |
| ClickHouse ∩ Vault (912 from 2026-05-15) | TBD |
| ClickHouse ∩ ComfyUI (548 from same-day) | TBD |

Operator pattern hypothesis: hosts running SigNoz (21 instances) likely have ClickHouse + Elasticsearch + a Phoenix/Helicone/Langfuse frontend on the same /24. IP-direct-shadow on the 21 SigNoz hosts is the next step for cross-platform stacking.

---

## Toolchain Provenance

```
0. shodan download (product:"ClickHouse") → 65,100 unique ip:port
1. fast_enum_clickhouse.py (threads=250, ~35 min) → 1,832 unauth + 7,337 auth-gated
2. operator-DB enumeration via SHOW DATABASES FORMAT JSON → ~10K user-DB-name samples
3. AI-stack marker filter (25-substring list) → 6 explicit AI-stack hosts
4. operator-attribution from DB names → scentedai, ai_hedge_fund, vllm_service, qinghai_platform
5. (queued) visorlog ingest → 1,832 events into nuclide.db source='clickhouse-survey-2026-05-16'
6. (queued) BARE module ranking → ClickHouse has CVE-2021-43304/05/08 (heap-buffer-overflow + integer overflow) but unauth-RCE class is small — risk class is intel-disclosure, not RCE
```

---

## Honest negative space

- **35,169 dead hosts** is consistent with the Shodan-stale pattern observed all day. ClickHouse operators rotate ports/migrate at similar rate to Vault (~54% stale here vs 64% Vault).
- **AI-stack filter is conservative.** 6 explicit AI-stack DBs is the lower bound. Many of the 32 `analytics` + 21 `signoz_*` + 8 `posthog` databases probably back AI workloads (LLM call traces, RAG performance metrics, embedding-evaluation results) without that being visible in the DB name. Real AI-stack overlap is probably 200-500 hosts.
- **No table-name enumeration.** `SHOW TABLES IN <db>` would extract operator's table names — even higher-resolution operator attribution — but at population scale that's 1,832 × N tables of additional query load. Deferred.
- **No data sampling.** Restraint: never `SELECT ... FROM <table>`. The database/table names ARE the finding.
- **22.3.20.29 dominance suggests Docker-image-template phenomenon — but I didn't verify which image** (clickhouse/clickhouse-server:22.3 vs altinity/clickhouse-server vs others). Different operators may have used different images that happened to pin to 22.3.x. Follow-up: check `Server` header on the `/ping` responses for the 1,013 hosts.

---

## Disclosure posture

- **Aggregate Tier-A* disclosure recommended** to ClickHouse Inc. (Aiven-style upstream notification about the Docker-image default auth behavior).
- **Targeted per-host disclosure** for the 6 AI-stack-tagged hosts. The `ai_hedge_fund` and `scentedai_fragid_new` hosts are operator-attribution-rich and deserve coordinated outreach.
- The 21 SigNoz-deployments are interesting collectively as a SigNoz-template-phenomenon — disclose to SigNoz upstream as a "your default Docker compose ships ClickHouse without auth" finding.

---

## See also

- [[insight-13-shipping-defaults-are-load-bearing]] — ClickHouse Docker image (no default password) drives the 18% unauth rate
- [[insight-25-falsification-confirmation-tier-c-platforms]] — ClickHouse joins the multi-platform Tier-A* set; same-day Tier-C contrast: ClearML, W&B, Argilla, Mem0
- [[insight-26-shodan-facet-fp-rate-escalates-with-token-commonality]] — `product:"ClickHouse"` 65K → 1,832 unauth ≈ 2.81% (Shodan facet not particularly noisy here — "ClickHouse" is a distinctive brand-string)
- [`elasticsearch-ai-stack-population-survey-2026-05-16.md`](elasticsearch-ai-stack-population-survey-2026-05-16.md) — same-day Tier-A* companion (Docker-default-off pattern)
- [`vectordb-stragglers-population-survey-2026-05-16.md`](vectordb-stragglers-population-survey-2026-05-16.md) — same-day Solr 7.6.0 finding (parallel Docker-image-template phenomenon)
