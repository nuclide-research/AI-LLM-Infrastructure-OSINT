# Apptica — Production Data Lake Exposed via Unauthenticated ClickHouse

**Date:** 2026-05-28  
**Host:** 65.21.27.49:8123 (Hetzner, Germany)  
**Cluster node:** `ch-s01-r02.apptica.tech`  
**Operator:** Apptica (apptica.com) — in-app advertising analytics SaaS  
**Version:** ClickHouse v26.2.5.45 (uptime 70 days at time of discovery)  
**Auth state:** NONE — full SQL access via HTTP and /play browser UI  
**Severity:** CRITICAL  
**Disclosure contact:** support@apptica.com

---

## Overview

Apptica is a commercial app store intelligence platform offering revenue estimates, download data, keyword rankings, and advertising intelligence for mobile apps across iOS and Android. Their product — described as "Ad Intelligence" and "Market Intelligence" — is built on the data stored in this database.

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7004, S7068, S7070, S7075, T5904
- **733 (AI Risk & Ethics Specialist):** K7040, S7067, S7069, T5854, T5868
- **overlap (Common AI KSATs (all 5 roles)):** K1158, K1159, K22, K6311, K6900, K6935, K7003, K7024, K7045, S7065

<!-- ksat-tag:auto-generated:end -->

Their production ClickHouse cluster node `ch-s01-r02.apptica.tech` was exposed on the public internet with no authentication configured. ClickHouse's built-in `/play` browser SQL interface was accessible to anyone with a web browser. No credentials were required at any point.

The instance had been running in this state for at least 70 days.

---

## Attribution

The attribution chain is definitive:

1. **Cluster config:** `SELECT * FROM system.clusters` returns cluster name `apptica` with two nodes: `ch-s01-r01.apptica.tech` (65.21.131.173) and `ch-s01-r02.apptica.tech` (65.21.27.49)
2. **Internal DNS:** Both nodes use the `apptica.tech` domain — the company's internal infrastructure domain
3. **Database name:** `apptica_stat` — unambiguous product attribution
4. **Table names:** Internal ticket numbers (`AP_4085`, `AP_4600`, `AP_3761`) consistent with a real production codebase
5. **Developer data:** Real company names (`Checkout 51 Mobile Apps ULC`, `ZiMAD`) actively flowing through `app_transfers`

The sibling node `ch-s01-r01.apptica.tech` (65.21.131.173) has port 8123 **closed** — only r02 was exposed.

---

## Exposed Surface

### Database: `apptica_stat` — 4.36 TiB total

| Table | Rows | Size | Contents |
|-------|------|------|----------|
| revenue_hist_ml_v2 | **138.02 billion** | 348 GiB | ML revenue predictions (app_id, geo_id, downloads, revenue, organic_baseline_part) |
| revenue_hist_ml_v2_final | 93.79 billion | 294 GiB | Finalized ML revenue dataset |
| revenue_hist_ml_v1 | 69.86 billion | 208 GiB | Previous ML model version |
| offers_log_daily | 66.75 billion | 388 GiB | Advertising offers log |
| offers_log_daily_by_adnetwork_id | 66.54 billion | 458 GiB | Partitioned by ad network |
| offers_log_daily_by_creative_id | 66.53 billion | 389 GiB | Partitioned by ad creative |
| offers_log_daily_by_publisher_application_id | 66.53 billion | 451 GiB | Partitioned by publisher app |
| offers_log_daily_by_advertiser_application_id | 57.97 billion | 361 GiB | Partitioned by advertiser |
| application_ratings | 30.50 billion | 498 GiB | App store ratings history |
| top_history | 9.25 billion | 69 GiB | Chart position history |
| usage_metrics_dau | 1.05 billion | 4 GiB | Daily active user metrics |
| keyword_history | 1.17 billion | 2.6 GiB | Keyword ranking history |
| creative_scores | 248.54 million | 1.5 GiB | Ad creative performance scores |

### `offers_log_daily` key_id field — advertising SDK tokens

The `key_id` column (Nullable String) in the offers log contains structured advertising intelligence including live advertiser credentials:

**Google AdMob format:**
```
id:44924;parsed:true;type:client,key:ca-app-pub-6879849083984493;type:slotname,key:3871954029;type:format,key:interstitial_mb
```
— contains the publisher's Google AdMob account ID (`ca-app-pub-XXXXXXXXXXXXXXXX`) and slot configuration.

**Ad SDK app_key format:**
```
id:1462225;parsed:true;type:sign,key:2e881ed49362ca64fa26bd9fc104f1a3;type:app_id,key:211453;type:unit_id,key:2625941;type:app_key,key:a5b0e9323a6f918668c931443170e124
```
— contains cryptographic app authentication keys (`app_key`) used by ad SDK integrations. These are not public identifiers — they are authentication tokens for programmatic ad SDK sessions.

### `app_transfers` — developer identity data

Schema: `id`, `app_id`, `geo_id`, `developer_internal_id`, `developer_name`, `developer_id`, `json`, `date`, `prev_id`

Sample rows (live production data, actively being written during enumeration):
```json
{"app_id":4,"developer_name":"Checkout 51 Mobile Apps ULC","developer_id":245373,"geo_id":14,"date":"2024-03-28"}
{"app_id":7,"developer_name":"ZiMAD","developer_id":7,"geo_id":56,"date":"2024-03-27"}
```

Developer company names, internal developer IDs, and app-to-developer mappings across geographies. The `json` column likely contains additional structured metadata.

---

## System Users — Two with Zero IP Restrictions

```json
{"name":"belyaev","host_ip":["::\/0"],"host_names":[]}
{"name":"petya","host_ip":["206.54.164.80","206.54.164.70","206.54.164.72","188.42.216.106","185.7.235.114","95.217.43.232","::\/1"],"host_names":["localhost"]}
{"name":"rpl","host_ip":["::\/0"],"host_names":[]}
{"name":"web","host_ip":["95.217.43.232","::\/1"],"host_names":["localhost"]}
{"name":"default","host_ip":["::\/1"],"host_names":[]}
```

- **`belyaev`** — `::\/0` (any IPv6/IPv4 address) — developer account with no network restriction
- **`rpl`** — `::\/0` (any address) — replication user, used for native protocol replication between cluster nodes

Port 9000 (ClickHouse native TCP protocol) is **open and reachable from the public internet**. `belyaev` and `rpl` can authenticate on port 9000 from any IP address. This extends the attack surface beyond the HTTP API: native protocol clients can execute all SQL, modify table engines, and issue replication commands.

The `petya` user is the active production pipeline inserter — their queries appear in the query log continuously.

---

## Proof of Concept

The `/play` browser UI requires no credentials:

**URL:** `http://65.21.27.49:8123/play?user=default`

Query executed without authentication:
```sql
SELECT database, name, formatReadableQuantity(total_rows) as rows,
formatReadableSize(total_bytes) as size
FROM system.tables
WHERE database = 'apptica_stat'
ORDER BY total_rows DESC LIMIT 10
```

Result: 10 rows in 0.01 seconds. See `evidence/poc-play-query-result.png`.

---

## Impact

**Competitive intelligence:** Apptica sells revenue estimates for mobile apps. Their ML model (`revenue_hist_ml_v2`) — the core of their commercial product — is trained on 138 billion data points that are now readable by anyone with a browser. A competitor can reconstruct the methodology, extract revenue estimates for any app in any geography, and undercut Apptica's commercial offering.

**Advertising SDK authentication tokens:** The `app_key` values in `key_id` are cryptographic tokens used by mobile app advertising SDKs for network authentication. If these tokens are reusable outside the Apptica system (dependent on the ad network's token lifecycle), they represent credential exposure.

**Developer identity:** Real developer company names, internal IDs, and app-to-developer mappings across billions of rows. Competitors or state actors could build a complete map of which developers own which apps across all geographies.

**Cluster exposure:** The `rpl` user with `::\/0` restriction and port 9000 open means an attacker with the replication password can interact with the cluster using the native protocol — including issuing DDL statements, modifying replication topology, or causing data loss.

**Exposure duration:** 70-day server uptime suggests the database has been publicly accessible for at minimum 10 weeks. No evidence of prior exploitation was examined.

---

## Remediation

1. Set `CLICKHOUSE_PASSWORD` for the `default` user immediately
2. Restrict `belyaev` and `rpl` to internal IP ranges only (`host_ip`)
3. Close port 8123 and 9000 to public internet; restrict to VPN or internal CIDR
4. Add `<listen_host>10.x.x.x</listen_host>` to `config.xml` to bind to internal interface only
5. Rotate any `app_key` values that may have been exposed via the `key_id` field

---

## Evidence

- `evidence/poc-play-ui.png` — ClickHouse /play UI, no auth required
- `evidence/poc-play-query-result.png` — live query result showing 138B-row table
- `../clickhouse-findings.csv` — full probe results (200 hosts)
- `../deep-enum.json` — raw enumeration output

**Disclosure:** support@apptica.com
