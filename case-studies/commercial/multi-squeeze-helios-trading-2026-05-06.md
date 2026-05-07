---
title: Squeeze/Helios short-squeeze trading platform, full architecture leaked + MLflow CVE-2023-1177 actively exploited (159.203.110.202)
date: 2026-05-06
class: substrate
category: mlops-tracking
status: actively-exploited
methodology: chain-revisit + post-chain-deep-dive
---

# Squeeze / Helios: short-squeeze trading platform's entire architecture leaked

NuClide Research · 2026-05-06

## Summary

DigitalOcean droplet **`159.203.110.202`** runs a complete real-time stock-prediction pipeline whose **entire internal architecture is leaked through Prometheus** + **MLflow is actively exploited via CVE-2023-1177** + **HashiCorp Vault is exposed in dev-mode storage** on port 8200.

The operator runs a short-squeeze trading platform under two internal codenames:
- **`squeeze`**, Prometheus job/pipeline label (`squeeze_finra_regsho`, `squeeze_polygon_news`, etc.)
- **`helios`**, service/host label (`helios-api-1`, `helios-finra-regsho-scraper`, `helios-polygon-news-recorder`)

The `helios_stock_direction` MLflow experiment (id 1) is the predictive ML model that consumes the data ingested by the squeeze_* scrapers. Six months of operational history visible in Prometheus counters; latest scrape from Polygon.io news API observed at **2026-05-06 18:06:10 UTC**, the platform is actively ingesting market data in production.

## Port surface (nmap top-1000)

| Port | Service | Auth | Notes |
|---|---|---|---|
| 22 | OpenSSH 8.9p1 (Ubuntu 22.04) | key-only | Standard |
| 5000 | **MLflow 2.9.2** | NONE | CVE-2023-1177 actively exploited (8 attacker-injected experiments) |
| 8000 | Uvicorn (helios-api) | filtered from external | Internal-only based on Prometheus showing it as `helios-api-1:8000` (internal Docker network) |
| 8200 | **HashiCorp Vault 1.15.6** | API auth-required (most endpoints 403) | **Initialized + UNSEALED in `inmem` storage with `t:1, n:1` Shamir**, strong signal of dev-mode |
| 9090 | **Prometheus 2.48.0** | NONE | Full target/metric/label disclosure |

## What's exposed (Prometheus full architecture leak)

`GET http://159.203.110.202:9090/api/v1/targets` returns 8 active scrape targets, the operator's full service map:

| Job | Instance | Component |
|---|---|---|
| `helios-api` | `helios-api-1:8000` | Customer-facing API (likely the prediction service or the trading dashboard backend) |
| `prometheus` | `localhost:9090` | Self-scrape |
| `redis` | `helios-redis-master:6379` | Redis cache (currently DOWN, 1/8 services degraded) |
| `squeeze_earnings_calendar` | `helios-earnings-calendar-recorder:9104` | Earnings calendar recorder |
| `squeeze_finra_regsho` | `helios-finra-regsho-scraper:9103` | **FINRA Regulation SHO short-sale data scraper** |
| `squeeze_finra_short_interest` | `helios-finra-short-interest-scraper:9105` | **FINRA Short Interest data scraper** |
| `squeeze_google_news` | `helios-google-news-recorder:9102` | Google News recorder |
| `squeeze_polygon_news` | `helios-polygon-news-recorder:9101` | Polygon.io news API consumer |

Plus 318 distinct Prometheus metric names across the platform, 83 are operator-specific (helios_*, squeeze_*) and reveal:

- `helios_finra_regsho_files_fetched_total` (290 files fetched lifetime)
- `helios_finra_regsho_cycles_total`, `helios_finra_regsho_rows_inserted_total`, `helios_finra_regsho_rows_skipped_*`
- `helios_polygon_news_last_success_timestamp` = 2026-05-06 18:06:10 (4 hours before probe)
- `helios_earnings_calendar_symbols_succeeded_total`
- `helios_google_news_*` counters

This is the **full operator-IP architecture**, anyone with the IP can map the platform's data ingestion topology, scrape success/failure cadence, and infer the data pipeline's reliability characteristics.

### Vault posture

`GET /v1/sys/seal-status` returns:

```json
{
  "type": "shamir",
  "initialized": true,
  "sealed": false,
  "t": 1, "n": 1,
  "version": "1.15.6",
  "cluster_id": "c4ed60d8-f574-82cc-1ab0-7ae73d52db08",
  "storage_type": "inmem"
}
```

The combination `storage_type: "inmem"` + `t: 1, n: 1` Shamir + sealed=false is **Vault running in DEV MODE** (`vault server -dev`). In dev mode:

- The root token is printed to stdout once at startup (or set via `-dev-root-token-id`)
- All data is in-memory (lost on restart)
- Anyone with the root token can read all secrets
- The auth gate IS in place at the API layer (we just confirmed `/v1/sys/mounts`, `/v1/sys/auth`, `/v1/sys/policies` return 403 unauth)

The exposure here is:
- **dev-mode-in-production anti-pattern**, Vault is the operator's intended secrets store but they've configured it with the dev defaults
- **Architecture leakage via cluster_id and version**
- **Bruteforce surface**, if the root token is guessable (e.g. `root` is the default), an attacker has full access. NuClide did NOT attempt to guess or use the root token.

If the root token has been set via env var or config file rather than the `vault` CLI default, this is much less serious. Verification requires operator-side check.

### MLflow active exploitation

`GET /version` → `2.9.2`. `POST /api/2.0/mlflow/experiments/search` returns 11 experiments:

- 3 legitimate: `Default` (id 0), `helios_stock_direction` (id 1, 0 runs visible), `exploit_33295` (id 13, 1 run named `salty-turtle-233`, RUNNING, no user_id, likely a CTF-naming-pattern attacker probe testing CVE-2023-1177 awareness)
- **8 attacker-injected** with path-traversal `artifact_location` values

7 of the 8 attacker UUIDs SHARED with `138.197.152.103` (AIPOD finding), confirming **population-scale CVE-2023-1177 spray actor** `3BT8ncOzBWAH4GyIGz0EXsSwj7f` operating against multiple unauth MLflow hosts. The 2026-04-20 11:11 UTC burst (5 attempts targeting `/root/.ssh/`, 3 attempts targeting `/etc/`) hit BOTH hosts within the same 30-second window.

### Operator brand identification (opaque)

- No public-facing operator domain identified
- `helios.trading` / `helios.app` / `heliostrading.com` are unrelated AWS-hosted properties or for-sale domains
- **`helios` and `squeeze` appear to be internal codenames only**, the operator's customer-facing brand (if any) wasn't surfaced
- Most likely profile: solo developer or 2–3 person quant team running on a single DigitalOcean droplet, building a short-squeeze prediction platform

The Vault dev-mode + single-droplet single-instance topology + lack of publishing-facing brand strongly suggests this is **a developer's personal quant project**, not a commercial product.

## Severity

**HIGH.** Reasoning:

- MLflow CVE-2023-1177 actively exploited, same actor as AIPOD; persistence + scale confirmed
- Vault in dev mode is unusual best-practice violation; if root token is bruteforceable, escalation path exists
- Prometheus full architecture leak gives attacker the operator's complete data pipeline topology
- Active production platform, Polygon.io news ingest at 4-hour cadence; FINRA Reg-SHO scraper has fetched 290 files lifetime
- Single point of compromise affects entire trading stack

Not CRITICAL because:
- No customer / patient PII exposed (this is a market-data ingestion platform, not a customer-facing service)
- No financial primitives reachable (the trading model is in MLflow but not deployed for inference at observed external endpoints)
- Operator profile suggests personal-project scale, not commercial liability

## Disclosure routing

- **Provider:** `abuse@digitalocean.com` (rank-1 from nuclide-contact)
- **Operator-direct:** opaque, no public-facing domain identified

Disclosure draft: [`disclosures/DIGITALOCEAN-159-203-110-202-squeeze-helios.md`](../../disclosures/DIGITALOCEAN-159-203-110-202-squeeze-helios.md)

## Toolchain provenance

```
Step 0   chain runner ran on (138.197.152.103, 159.203.110.202) earlier in session
Step 1a  visorplus assess  → DigitalOcean WHOIS, nmap top-1000 (5 open ports), GreyNoise: benign
Step 1b  aimap -list       → no fingerprint match (Vault not in aimap; Prometheus is but only on port 9090 default which here it IS at)
Step DD  direct REST enum  → MLflow /api/2.0/mlflow/experiments/search; Vault /v1/sys/seal-status; Prometheus /api/v1/targets
Step 5   nuclide-contact   → abuse@digitalocean.com (operator opaque)
Step 6   visorlog          → existing event ID for 159.203.110.202 from mlflow-cloud-survey-2026-05; this case study is the post-revisit deep-dive
Step 7   visorscuba assess → AI.C1 critical violation (already in ledger from initial survey)
Step 9   visorcorpus build → 46-case adversarial corpus (kb_exfiltration + system_prompt + config_secrets) shared with AIPOD case
```

## Methodology Insight #11 candidate

**Prometheus is a more powerful operator-IP exfil endpoint than any of the dedicated AI/ML platforms.** When operators expose Prometheus unauth on port 9090, the `/api/v1/targets` and `/api/v1/label/__name__/values` endpoints reveal the *full architecture* (every service, every internal hostname, every metric name). Job + instance labels alone (`squeeze_finra_regsho`, `helios-redis-master:6379`) tell more about the operator's product than any ML metadata leak.

For future surveys, **always probe port 9090 on any confirmed Tier-A operator IP and pull the targets list**, it's the highest-information-density operator-IP exfil endpoint in the standard cloud-native stack. NuClide's existing observability survey (port 6006 Phoenix + TensorBoard) covered LLM-trace observability but not the operator-architecture observability layer.

This insight is candidate for inclusion in [SYNTHESIS-2026-05.md](SYNTHESIS-2026-05.md) Methodology Insights section.

## References

- AIPOD sister-host case study (same actor), [`multi-aipod-mlflow-cve-2026-05-06.md`](multi-aipod-mlflow-cve-2026-05-06.md)
- Original MLflow cloud survey, [`mlflow-cloud-survey-2026-05.md`](mlflow-cloud-survey-2026-05.md)
- Cross-survey synthesis, [`SYNTHESIS-2026-05.md`](SYNTHESIS-2026-05.md) (Class E, Active CVE exploitation)
- CVE-2023-1177 advisory, https://nvd.nist.gov/vuln/detail/CVE-2023-1177
- HashiCorp Vault dev mode docs, https://developer.hashicorp.com/vault/docs/concepts/dev-server
- Prometheus security model (deliberately auth-less by default), https://prometheus.io/docs/operating/security/
