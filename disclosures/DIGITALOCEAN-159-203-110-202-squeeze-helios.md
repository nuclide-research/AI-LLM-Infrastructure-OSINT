---
to: abuse@digitalocean.com
cc: abuse@nuclide-research.com
severity: HIGH
ip: 159.203.110.202
institution: DigitalOcean — Squeeze/Helios short-squeeze trading platform; MLflow 2.9.2 actively exploited (CVE-2023-1177) + Vault dev-mode + Prometheus full architecture leak
status: DRAFT
date: 2026-05-06
---

**To:** abuse@digitalocean.com
**Cc:** abuse@nuclide-research.com
**Subject:** DigitalOcean droplet running short-squeeze trading platform — MLflow 2.9.2 actively exploited (CVE-2023-1177), Vault dev-mode unsealed, Prometheus full architecture leak — 159.203.110.202

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-06

**Re:** DigitalOcean customer host running an entire quant-trading stack with stacked exposures
**IP:** 159.203.110.202
**Severity:** HIGH

---

I'm an independent security researcher conducting good-faith AI infrastructure research under the NuClide Research umbrella (CISA disclosures CVE-2025-4364, ICSA-25-140-11). This is an unsolicited coordinated-disclosure notification.

---

## Summary

A DigitalOcean droplet at `159.203.110.202` runs a complete short-squeeze stock-prediction pipeline whose **entire internal architecture is publicly enumerable** via Prometheus + **MLflow is actively exploited** via CVE-2023-1177 + **HashiCorp Vault is exposed in dev-mode storage**.

Operator codenames (extracted from public Prometheus labels): `squeeze` (the platform / pipeline) and `helios` (the components). The MLflow experiment `helios_stock_direction` (id 1) is the predictive ML model for the platform.

| Port | Service | Auth | Issue |
|---|---|---|---|
| 22/tcp | OpenSSH 8.9p1 (Ubuntu 22.04) | key-only | Standard |
| 5000/tcp | **MLflow 2.9.2** | NONE | CVE-2023-1177 actively exploited — 8 attacker-injected experiments with `/etc/` and `/root/.ssh/` path-traversal artifact_locations |
| 8000/tcp | helios-api (Uvicorn) | filtered externally | Internal-only per Prometheus topology |
| 8200/tcp | **HashiCorp Vault 1.15.6** | API auth-required (most endpoints 403) | Configured with `storage_type: "inmem"` + Shamir `t:1, n:1` — dev-mode-in-production anti-pattern |
| 9090/tcp | **Prometheus 2.48.0** | NONE | Full architecture leak — 8 scrape targets, 318 metric names, all internal hostnames disclosed |

## Reproduction (non-destructive)

### Prometheus full architecture leak

```bash
$ curl -s 'http://159.203.110.202:9090/api/v1/targets' \
    | jq '.data.activeTargets[] | {job: .labels.job, instance: .labels.instance, health: .health}'
{"job":"helios-api",                 "instance":"helios-api-1:8000",                              "health":"up"}
{"job":"prometheus",                 "instance":"localhost:9090",                                  "health":"up"}
{"job":"redis",                      "instance":"helios-redis-master:6379",                        "health":"down"}
{"job":"squeeze_earnings_calendar",  "instance":"helios-earnings-calendar-recorder:9104",          "health":"up"}
{"job":"squeeze_finra_regsho",       "instance":"helios-finra-regsho-scraper:9103",                "health":"up"}
{"job":"squeeze_finra_short_interest","instance":"helios-finra-short-interest-scraper:9105",       "health":"up"}
{"job":"squeeze_google_news",        "instance":"helios-google-news-recorder:9102",                "health":"up"}
{"job":"squeeze_polygon_news",       "instance":"helios-polygon-news-recorder:9101",               "health":"up"}
```

This single endpoint discloses:
- Every internal Docker / K8s service hostname the operator has deployed
- Every external data-feed integration (FINRA Regulation SHO short-sale data, FINRA Short Interest data, Polygon.io news API, Google News)
- Service health (Redis cache currently DOWN — 1 of 8 services degraded)
- Prometheus version (2.48.0)

`GET /api/v1/label/__name__/values` returns 318 distinct metric names; 83 are operator-specific (`helios_*`, `squeeze_*`) and reveal the full data-pipeline counter set (cycle counts, file-fetch counts, last-success timestamps).

### MLflow active CVE-2023-1177 exploitation

```bash
$ curl -s 'http://159.203.110.202:5000/version'
2.9.2

$ curl -s -X POST -H 'Content-Type: application/json' \
    -d '{"max_results":1000}' \
    'http://159.203.110.202:5000/api/2.0/mlflow/experiments/search' \
    | jq '.experiments[] | select(.artifact_location | contains("../"))| {name, artifact_location}'
```

8 attacker-injected experiments visible. 7 of 8 attacker UUIDs are SHARED with the AIPOD finding at `138.197.152.103` — confirming **population-scale CVE-2023-1177 spray actor** `3BT8ncOzBWAH4GyIGz0EXsSwj7f` operating against multiple DigitalOcean unauth MLflow hosts. Both hosts received the same 30-second 2026-04-20 11:11 UTC injection burst targeting `/root/.ssh/` (5 attempts) and `/etc/` (3 attempts).

### HashiCorp Vault dev-mode posture

```bash
$ curl -s 'http://159.203.110.202:8200/v1/sys/seal-status' | jq '{
    initialized, sealed, t, n, version, storage_type, cluster_id }'
{
  "initialized": true,
  "sealed": false,
  "t": 1, "n": 1,
  "version": "1.15.6",
  "storage_type": "inmem",
  "cluster_id": "c4ed60d8-f574-82cc-1ab0-7ae73d52db08"
}
```

`storage_type: "inmem"` + Shamir `t: 1, n: 1` is **Vault running in dev mode** (`vault server -dev`). Dev mode auto-initializes + auto-unseals, prints the root token to stdout, and stores all data in memory. Vault's own documentation states dev mode is **not safe for production use** (https://developer.hashicorp.com/vault/docs/concepts/dev-server).

Most admin endpoints (`/v1/sys/mounts`, `/v1/sys/auth`, `/v1/sys/policies`) return 403 unauth, so the Vault auth gate IS in place at the API layer. The exposure is the dev-mode anti-pattern + the architectural disclosure (`cluster_id`, `version`, `storage_type`) — not a direct secrets read.

If the root token is the dev-mode default (`root`) or guessable, an attacker has full secrets access. NuClide DID NOT attempt to authenticate to Vault.

## Why this matters

For the Squeeze/Helios operator:

- **Real-time market data pipeline actively exposed.** `helios_polygon_news_last_success_timestamp` was 2026-05-06 18:06:10 UTC (4 hours before this disclosure) — the platform is actively ingesting Polygon.io news in production.
- **MLflow CVE-2023-1177 active exploitation.** 8 attacker-injected path-traversal experiments since 2026-03-26; same actor signature as documented on AIPOD (`138.197.152.103`).
- **Vault dev-mode-in-production.** If the Vault holds API keys for Polygon.io / Google News / FINRA scrapers (the natural design for this operator's stack), and the root token is bruteforceable, the attacker pivots from Prometheus reconnaissance to full secrets exfil.
- **Architecture leak via Prometheus** is a one-shot competitive intel dump — anyone in the operator's market segment now knows their full data-feed inventory + scraping cadence.

For DigitalOcean abuse:

- The customer needs notification. The operator profile (single droplet, dev-mode Vault, opaque branding) suggests a small team or solo developer — likely reachable through the standard customer-channel.

## Remediation (for the customer)

```bash
# 1. Patch MLflow immediately — upgrade to 2.10.0+ (CVE-2023-1177 patched in 2.3.1).
#    Bind to localhost or restrict via firewall:
ufw deny 5000/tcp
ufw allow from <admin-IP> to any port 5000

# 2. Audit MLflow access logs for GET /get-artifact?path= requests with the
#    18 attacker run UUIDs (full list in the case study). Those would confirm
#    whether the path-traversal exfil step actually executed.

# 3. Audit /root/.ssh/authorized_keys for unfamiliar entries. The 5 separate
#    /root/.ssh/ traversal attempts on 2026-04-20 represent attacker intent
#    to install persistent SSH access.

# 4. Replace Vault dev-mode with a production-mode deployment:
#    - Use file or consul storage backend (not inmem)
#    - Generate proper Shamir keys (t > 1, n > t for redundancy)
#    - Restrict to localhost or behind reverse-proxy with TLS
#    - Rotate the existing dev-mode root token immediately if it was set
#      to the default value

# 5. Restrict Prometheus:
#    - Bind to 127.0.0.1 (Prometheus expects to be reached via reverse-proxy
#      with auth in production)
#    - Or front with nginx + basic_auth

# 6. Delete the 8 attacker-injected MLflow experiments after audit.
```

Vault production-mode docs: https://developer.hashicorp.com/vault/docs/configuration
Prometheus security model: https://prometheus.io/docs/operating/security/
CVE-2023-1177 advisory: https://nvd.nist.gov/vuln/detail/CVE-2023-1177

## Reference

Full case study (with operator timeline, attacker UUID cross-correlation, methodology insights):
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/commercial/multi-squeeze-helios-trading-2026-05-06.md

Sister-host actively-exploited (same attacker signature):
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/commercial/multi-aipod-mlflow-cve-2026-05-06.md

Original mlflow cloud survey:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/commercial/mlflow-cloud-survey-2026-05.md

Happy to coordinate verification, or to extract the additional attacker UUIDs and timestamps needed for incident response.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
