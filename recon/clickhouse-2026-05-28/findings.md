# ClickHouse Unauth Population Survey — 2026-05-28

**Platform:** ClickHouse (OLAP database — AI feature store / LLM log store)  
**Dork:** `http.title:"ClickHouse" port:8123`  
**Total population:** 5,243  
**Probed:** 200 (first 20 Shodan pages)  
**Auth rate:** 91.5% (183/200 auth-enforced)  
**Unauth:** 8% (16/200)  
**Version endpoint:** `GET /?query=SELECT version()` → bare version string  
**Default creds:** username `default`, password empty

---

## Population Summary

| Tier | Count | Notes |
|------|-------|-------|
| Auth-enforced | 183 | ClickHouse password configured |
| Unauth + versioned | 16 | Full SQL access, no credentials |
| Auth rate | 91.5% | Higher than Ollama (0%), lower than Argo (100%) |

**Top orgs (unauth):** Hetzner (28), DigitalOcean (11), OVH (11), Microsoft (6)  
**Top countries:** US (35), Germany (24), UK (18), Netherlands (18), France (17)

All 16 unauth hosts have `/play` open — ClickHouse's built-in browser SQL interface. No client needed to query data.

**Display name header:** All 200 hosts leak internal hostname via `X-ClickHouse-Server-Display-Name` response header regardless of auth state. This reveals cluster node names, Kubernetes pod identities, and internal DNS names.

---

## Findings

### F1 — Apptica Production Data Lake (CRITICAL)

**Host:** 65.21.27.49:8123  
**Display name:** `ch-s01-r02` (ClickHouse server 1, replica 2)  
**Version:** 26.4.2.10  
**Auth:** NONE — full SQL access with no credentials  
**Database:** `apptica_stat`

**Apptica (apptica.com)** is an app store intelligence platform providing revenue estimates, download data, advertising intelligence, and ML-based revenue predictions for mobile apps across iOS and Android.

Their production ClickHouse cluster node is exposed on the public internet with no authentication. The `/play` browser SQL interface is accessible to anyone. Active write traffic was observed in the query log during enumeration — this is a live production replica receiving INSERT operations.

**Exposed datasets:**

| Table | Rows | Size | Contents |
|-------|------|------|----------|
| revenue_hist_ml_v2 | 138.02 billion | 348 GiB | ML revenue predictions (app_id, geo_id, downloads, revenue, organic_baseline_part) |
| revenue_hist_ml_v2_final | 93.79 billion | 294 GiB | Finalized ML revenue dataset |
| revenue_hist_ml_v1 | 69.86 billion | 208 GiB | Previous ML revenue model data |
| offers_log_daily | 66.75 billion | 388 GiB | Advertising offers (advertiser/publisher app_id, ad network, user_id, key_id) |
| offers_log_daily_by_adnetwork_id | 66.54 billion | 458 GiB | Same, partitioned by ad network |
| offers_log_daily_by_creative_id | 66.53 billion | 389 GiB | Same, partitioned by creative |
| offers_log_daily_by_publisher_application_id | 66.53 billion | 451 GiB | Same, partitioned by publisher |
| offers_log_daily_by_advertiser_application_id | 57.97 billion | 361 GiB | Same, partitioned by advertiser |
| application_ratings | 30.50 billion | 498 GiB | App store ratings history |
| top_history | 9.25 billion | 69 GiB | App store chart position history |
| usage_metrics_dau | 1.05 billion | 4 GiB | Daily active user metrics (app_id, geo_id, value) |
| creative_scores | 248.54 million | 1.5 GiB | Ad creative performance scores |
| keyword_history | 1.17 billion | 2.6 GiB | App store keyword ranking history |

**Total visible dataset: >700 billion rows across all tables.**

**Schema — offers_log_daily (sensitive fields):**
- `advertiser_application_id` — the app buying advertising
- `publisher_application_id` — the app showing advertising
- `adnetwork_id` — advertising network used
- `user_id` (Nullable) — end user identifier
- `key_id` (Nullable String) — advertiser API key or campaign identifier

**Sample row — revenue_hist_ml_v2:**
```json
{"utc_date":"2021-10-28","app_id":7871245,"geo_id":12,"downloads":4035,"revenue":399,"organic_baseline_part":1}
```

**What this exposes:** Apptica's entire ML training dataset for revenue prediction — the model that powers their commercial intelligence product. A competitor could reconstruct their revenue estimation methodology, extract download/revenue estimates for any app in any geography, or query the raw advertising spend data to identify advertiser/publisher relationships across ad networks.

**Query log evidence of active use:**
```sql
INSERT INTO apptica_stat.app_transfers (id, app_id, geo_id, developer_internal_id, 
developer_name, developer_id, json, date, prev_id) FORMAT Native
```
This INSERT was observed running during enumeration — the cluster is actively receiving data.

---

### F2 — DataV Multi-Tenant Analytics Platform (MEDIUM)

**Host:** 64.227.166.14:8123  
**Display name:** `42aa3ea582d8` (Docker container ID)  
**Version:** 25.10.1.3832  
**Auth:** NONE  
**Tables:** 1,092 across 7 databases

**Databases exposed:**
- `datav_2_0` — tenant data (tables named with random UUIDs, e.g. `localhost_fc3vsgwc6pxlmg5zbezr`)
- `otel` — OpenTelemetry traces and logs from production services
- `prediction_datav_2_0` — ML predictions
- `qa_datav_2_0` — QA environment data

**Largest tables (datav_2_0):**
- `localhost_fc3vsgwc6pxlmg5zbezr`: 7.39M rows, 2.70 GiB
- `dev_ymbhyu4akrypqv34h7oy`: 5.14M rows, 1.88 GiB
- `dev_jk7ykpqriawweq9i7eqt`: 5.08M rows, 1.51 GiB

The `otel` database contains production OpenTelemetry data — request traces, error rates, latency metrics from the platform's services. The randomized table names suggest multi-tenant isolation by naming convention rather than authentication — all tenant data is in one unprotected database.

---

### F3 — Airport Facility IoT Platform (MEDIUM)

**Host:** 108.248.232.250:8123  
**Display name:** `zephyrai1`  
**Version:** 25.12.1.402  
**Auth:** NONE  
**Tables:** 503

**Databases:** `MasterDB`, `phl`, `phlDB`, `pit`, `smart_facility`, `triangle`, `pearlman`

Airport codes in database names: `phl` = Philadelphia International, `pit` = Pittsburgh, `triangle` = RDU (Research Triangle). This is a smart facility management platform monitoring multiple airports.

**Largest table:** `pit.restroom_supplies` — 2.45M rows, `triangle.restroom_supplies` — 2.02M rows, `phl.restroom_supplies` — 2.02M rows

Operational facility data (restroom supply levels, smart sensor readings) across at least 3 airports is fully accessible. The query log shows complex time-windowed queries (28-day, 1-hour windows) running in production — active operational use.

---

### F4 — Video Platform User Analytics (MEDIUM)

**Host:** 209.50.238.93:8123  
**Display name:** `f24a2e8afce1` (Docker container)  
**Version:** 25.8.20.4  
**Auth:** NONE  
**Database:** `analytics`

**Exposed:** `video_history_current` (581K rows), `blog_post_uv_daily` (429K rows), `entity_reactions` (141K rows)

User interaction data — video watch history, blog post unique visitors, user reactions. The query log shows an `analytics_user` account running video popularity queries (`v_video_popularity_7d`, `v_video_popularity_30d`) — a dedicated analytics user with internal access whose queries are logged and readable.

---

## Population-Level Finding

ClickHouse has an 8% unauth rate in the Shodan-visible population — significantly better than Ollama (≈0% auth) but worse than Argo Workflows (100% auth). The auth enforcement improvement correlates with the post-DeepSeek-incident changes to ClickHouse's default Docker images (early 2025), which disabled network access for the default user. The 8% unauth tail are older deployments that predate or ignored this change.

**All 200 hosts leak the `X-ClickHouse-Server-Display-Name` header regardless of auth state.** This is a systematic information disclosure: internal hostnames, Kubernetes pod identifiers, and cluster node naming conventions are visible to any scanner without authentication. Two hosts reveal Kubernetes ClickHouse Operator deployments: `chi-lakehouse-default-0-0-0.chi-lakehouse-default-0-0.clickhouse.svc.cluster.local` and `chi-template-service-cluster-0-0-0`.

---

## Remediation

1. Set `<password>` for the `default` user in ClickHouse `config.xml` or use environment variable `CLICKHOUSE_PASSWORD`
2. Add `<listen_host>127.0.0.1</listen_host>` to restrict to local access only
3. Use ClickHouse's named users with explicit network restrictions
4. Do not expose port 8123 to the public internet; place behind a reverse proxy or VPN

The ClickHouse documentation recommends: "If you are accessing ClickHouse from the internet, you must set a password for the `default` user."
