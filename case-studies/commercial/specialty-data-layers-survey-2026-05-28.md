---
title: "Cat-30: Specialty Data Layers — Population Survey"
date: 2026-05-28
category: cat-30
platforms: [ClickHouse, Apache Cassandra, ScyllaDB, Apache Pinot]
total_confirmed: 107
auth_enforced: 11
dorks_tested: 21
survey_population: ClickHouse 120, Cassandra 70, ScyllaDB 107, Pinot 31
tags: [clickhouse, cassandra, scylladb, apache-pinot, data-warehouse, olap, kyc, pii, retail, fintech, iot]
---

# Cat-30: Specialty Data Layers — Population Survey

**Date:** 2026-05-28
**Scope:** Four specialty OLAP/NoSQL platforms serving AI/ML pipelines — ClickHouse, Apache Cassandra, ScyllaDB, Apache Pinot
**Dorks tested:** 21
**IPs harvested:** 120 (ClickHouse) + 70 (Cassandra) + 107 (ScyllaDB) + 31 (Pinot) = 328 total
**Confirmed unauth:** 107 (33%)
**Single-host case studies:** [Snap-E Cabs ScyllaDB](./snapecabs-scylladb-34.131.90.52-2026-05-28.md) | [Sanio AI AgentOS](./sanio-ai-collision-agentOS-2026-05-28.md)

---

## Survey Summary

| Platform | Harvested | Confirmed Unauth | Auth-Enforced | Unauth Rate |
|---|---|---|---|---|
| ClickHouse | 120 IPs | 21 | 0 verified | 100% of probed |
| Apache Cassandra | 70 IPs | 41 | 5 | 58.6% |
| ScyllaDB | 107 IPs | 24 | 0 | 100% of REST-open |
| Apache Pinot | 31 IPs | 21 | 5+2 blocked | 67.7% |
| **Total** | **328** | **107** | **~11** | **~33%** |

**Reading note:** ClickHouse probed 21 from 120 harvested; Cassandra exhausted all 70. "Unauth rate" reflects confirmed probe success, not full harvest sweep.

---

## ClickHouse — 21 Confirmed Unauth

**Discovery method:** Shodan dork `"X-ClickHouse-Server-Display-Name"` → 270 hits → 120 unique IPs harvested. Verification: `GET /?query=SHOW+DATABASES` without credentials returns database list; `GET /ping` returns `Ok.`

**Auth default:** None. The `default` user ships with an empty password in `config.xml`. Pre-2024 Docker images leave network access open. No hardened Docker defaults on any of the 21 confirmed instances.

**Population confirmed:** 21/21 unauth (100% of probed set)

**Versions observed:** 24.3.x through 24.8.x — all 2024 releases. None current (24.12 as of survey date).

| IP | Display Name | Notable Databases |
|---|---|---|
| 109.94.170.165 | ch-cluster | events, telemetry, clickstream, audit\_log |
| 135.125.237.161 | ch-node-1 | audit (errors, logs, metrics, access\_log, audit\_log) |
| 212.147.235.10 | ch-cluster | reporting, audit |
| 216.238.107.138 | ch-cluster | warehouse, metrics |
| 139.99.135.124 | warehouse | production (access\_log, audit\_log, sessions, page\_views, **users**, responses, clicks) |
| 146.59.83.12 | warehouse | production (conversions, page\_views, audit\_log, **users**, logs, requests) |
| 64.176.60.25 | data-warehouse | reporting |
| 194.71.126.47 | ch-edge-01 | default (4-node cluster, same operator) |
| 5.78.43.223 | ch-edge-01 | default (same cluster) |
| 194.182.166.180 | ch-edge-01 | default (same cluster) |
| 34.65.46.30 | ch-edge-01 | default (same cluster) |
| 64.176.18.142 | ch-prod | reporting, clickstream, events |
| 54.38.184.2 | ch-analytics | clickstream, analytics, telemetry |
| 185.154.110.14 | (default) | user\_events (audit\_log, responses, events, page\_views, **users**) |
| 198.13.39.215 | warehouse | metrics, warehouse |

**Data classes confirmed (SHOW TABLES without auth):**

- `users` tables confirmed on 3 production instances — PII-class
- `sessions` — active session data
- `audit_log` — operational security records
- `access_log` — IP + user agent analytics
- `clickstream` — behavioral tracking
- `system.environment` — accessible on all instances; would leak secrets on any instance where env vars carry API keys

**High-interest instances:**

139.99.135.124 and 146.59.83.12 both have `production` databases with `users` and `sessions` tables alongside `audit_log`. Both display-named `warehouse`. Co-hosting pattern suggests same operator, possibly a data vendor or SaaS backend. Confirm via VisorGraph cert pivot.

109.94.170.165 (ch-cluster) has MinIO also present on port 9000 — internal S3 storage backing this ClickHouse node. `clickstream` + MinIO suggests a product analytics platform.

**Dork signal analysis:**

`"X-ClickHouse-Server-Display-Name"` is the precision dork. The header is vendor-unique and present on every HTTP ClickHouse response, authenticated or not. Population baseline: `port:8123 product:"ClickHouse"` → 11,772. Dork yields 270 — the precision dork filters to HTTP-responsive instances.

---

## Apache Cassandra — 41 Open, 58.6% Unauth

**Discovery method:** `product:"Cassandra"` → 89 hits → 70 IPs. Verification via CQL binary protocol: `OPTIONS` frame → `SUPPORTED` response containing `CQL_VERSION` and `COMPRESSION` keys. Then `STARTUP` frame → `READY` (open) or `AUTHENTICATE` (gated).

**Auth default:** `AllowAllAuthenticator` in cassandra.yaml is the default. No credentials required. `AuthorizationAuthorizer: AllowAllAuthorizer` also grants full permissions.

**Population results:**

- 41/70 returned `READY` — fully open CQL (58.6%)
- 5/70 returned `AUTHENTICATE` — auth enforced (7%)
- Remaining: timeout, filtered, or connection refused

**Notable cluster topology — GCP us-central1:**

12 of the 41 open instances are in the 34.x.x.x GCP us-central1 range. Consistent CQL version responses suggest a single operator running a large unconfigured Cassandra cluster. No SCYLLA markers in any SUPPORTED frame across all 70 probes — Cassandra-native only.

**Open instances (41):**

103.29.189.30, 104.42.179.74, 114.132.75.232, 117.50.159.235, 119.8.9.77, 131.153.50.76, 155.138.254.50, 157.230.246.248, 159.203.140.14, 161.97.83.9, 183.90.170.144, 202.73.50.123, 206.1.12.224, 217.182.187.52, 34.121.136.180, 34.126.221.147, 34.126.67.57, 34.136.247.1, 34.138.247.1, 34.14.175.106, 34.173.37.204, 34.44.91.108, 34.61.224.70, 34.67.35.252, 34.68.28.25, 34.69.185.125, 34.72.45.182, 35.225.70.38, 35.232.176.39, 35.238.53.188, 43.134.124.194, 47.181.219.188, 47.181.219.192, 47.95.113.249, 50.250.206.114, 52.169.219.37, 61.138.213.171, 75.119.131.176, 80.67.224.183, 82.202.160.130, 91.203.134.249

**aimap gap:** Cassandra CQL binary protocol not covered in aimap's fingerprint set. Cassandra's discovery path requires a bespoke CQL probe — `enumCassandra` module is a gap in the current fingerprint list.

---

## ScyllaDB — 24 REST API Open, 100%

**Discovery method:** Two-dork approach. `port:9180 "seastar"` → 99 hits (Prometheus endpoint). `port:10000 "Seastar"` → 58 hits (REST API). Overlap: 107 unique IPs. Verified via `GET /storage_service/keyspaces` — returns keyspace JSON without credentials.

**Auth default:** None on REST API (port 10000) and Prometheus (port 9180). CQL port 9042 uses AllowAllAuthenticator matching Cassandra defaults.

**Three attack surfaces exposed per host:**
1. Port 9042: CQL binary — full read/write to all keyspaces
2. Port 10000: REST admin API — keyspace enumeration, server management, snapshot creation
3. Port 9180: Prometheus metrics — shard utilization, read/write latency, replication topology

**Confirmed keyspaces (24 hosts with non-system data):**

High-value instances:

| IP | Keyspaces / Notable Data | Context |
|---|---|---|
| 34.90.240.245 | payments, wallets, auth, auth\_otp, orders, users, companies, employees (nyovenn) | Fintech/logistics SaaS, unknown operator |
| 34.131.90.52 | 80+ alternator\_\* tables: snapecabs-ride-logs, mahindra-trip-payloads, fleetgpt\_subscription, adas\_linux\_device\_messages, vehicle-current-state, driver-\* | Snap-E Cabs / EC Wheels India (BSE: STML) |
| 150.241.116.202 | posts, users, messages, usernames, counters | Social/messaging platform |
| 208.69.76.x (10 nodes) | users, app\_info | 2290008 Ontario Inc |
| 89.222.120.108 + 89.187.173.217 | xtream\_iptvpro\_scylla | IPTV operator |
| 217.76.60.74 | linktree | Linktree-named keyspace — social link platform |
| 206.119.185.196 | im\_app | Instant messaging backend |
| 47.238.29.124 | social, scylla\_manager | Social platform |
| 68.183.80.97 | mb\_blob\_prod | Production blob storage |

**Single-host case study:** [snapecabs-scylladb-34.131.90.52-2026-05-28.md](./snapecabs-scylladb-34.131.90.52-2026-05-28.md) — 431,808 driver safety events, 245 live auth tokens, biometric face ROI data, GPS telemetry, live video stream management. BSE-listed company. Full findings breakdown at [snapecabs-scylladb-34.131.90.52-findings-breakdown.txt](./snapecabs-scylladb-34.131.90.52-findings-breakdown.txt).

**nyovenn operator:** See `recon/specialty-data-layers-2026-05-28/nyovenn-findings-breakdown.txt` for full detail. Operator identity unresolved — all nyovenn.\* domain variants are unregistered.

**Prometheus (port 9180) note:** All 99 Seastar-matched hosts leak shard count, read/write throughput, compaction state, and replica status without credentials. This is topology intelligence — attacker can determine which nodes are hot, when to strike for minimum detection, and how many shards to target in a parallel read sweep.

---

## Apache Pinot — 21 Confirmed Unauth

**Discovery method:** `port:9000 "Apache Pinot"` → 31 hits → 31 IPs. Verification: `GET /tables` on port 9000 (broker) returns table list without credentials. `GET /cluster/info` on port 9000 returns cluster name.

**Auth default:** None. No access control is configured on fresh Pinot deployments. CORS `Access-Control-Allow-Origin: *` header present on all 20 aimap-confirmed instances — browser-based cross-origin reads are possible.

**CVE-2024-56325 test:** Dot-path bypass probe (`GET /cluster.info`) returned 404 across all 31 IPs. Population appears to be >= 1.3.0 or bypass requires additional conditions. Not a confirmed attack vector in this survey.

**Auth breakdown:**
- 21/31 unauth (67.7%)
- 5/31 return 401 (auth enforced)
- 2/31 return 403 (ACL-restricted)
- 3/31 unreachable (timeout)

**Top findings by data class:**

**FINDING P-1: Retail giant analytics (34.34.168.173 + 34.38.84.140) — Cluster: BIN-Pinot**

Two unauth Pinot nodes exposing a production retail analytics cluster. Combined live-verified table list:

`online_sales` (368 GB, 5,972 segments), `store_sales` (123 GB), `receipt_row` (6.5 GB), `customer_counter` (444 MB), `fulfillment_details`, `rfid_device_status_current`, `store_health_score`, `omni_location_master`, `shs_subscore_ranking`, `vw_db_replenishment`, `vw_db_shipmentbox`, `vw_db_storereservation_requests`

Schema includes: `ShippingFulfilmentEntity`, `CountryCode`, `OrderId`, `OrderType`, `Products_VariantID`, `Products_Description`, `Products_OnlineURL`, `BrandID`, `IsGuest`, `order_date`, `Total`

RFID + `omni_location_master` + `store_health_score` + `shs_subscore_ranking` indicates a large omnichannel retailer with RFID-enabled stores. The cluster name "BIN-Pinot" plus omnichannel RFID infrastructure narrows to top-tier global fashion retail. 490+ GB combined across two unauth nodes.

Tier: UNRATED pending operator attribution (schema confirms production retail, data volume confirmed, data contents not read).

**FINDING P-2: KYC PII database — Hamropatro (182.93.94.236 + 182.93.94.251) — Cluster: PinotCluster**

Live-verified `{"tables":["Sherlocktranscript","account_analytics","ledger_analytics","order_analytics","user_kyc_analytics"]}` on .236.

`user_kyc_analytics` schema (verified both nodes): `appId`, `userId`, `accountId`, `firstName`, `middleName`, `lastName`, `fullName`, `kycVerified`, `tpinRegistered`, `gender`, `dateOfBirthFormat`, `dateOfBirthNepaliString`, `phoneNumber`, `email`, `phoneVerified`, `emailVerified`, `profileImage`, `kycStatus`, `authProvider`, `userType`, `fatherName`, `documentType`, `documentId`, `flagged`, `matchedUserInfo`, `flaggedDescription`, `agent`, `maxEligibleAmount`, `dateOfBirth`

`hamropatro_event_analytics` table name on .251 is a direct operator attribution signal — hamropatro.com is Nepal's largest lifestyle app (10M+ users). Nepal fintech context; likely subject to Nepal Rastra Bank (NRB) data protection requirements.

KYC data confirmed by schema: government document ID (`documentType` + `documentId`), full name, DOB, phone, email, KYC verification status, TPIN registration, flagging reason and `matchedUserInfo`. Schema is AML/compliance-class PII. Data rows not read.

Tier: HIGH (PII schema confirmed unauth, data contents not verified).

**FINDING P-3: Financial transaction ledger (4.187.254.121) — Cluster: pinot-switchdev2**

Live-verified tables: `d2_operation_audit`, `d2_operation_data`, `d2_participant_balance`, `d2_participant_daily_balance`, `d2_participant_relation`, `d2_relation`, `d2_tin_balance`, `d2_tin_daily_balance`

Schema includes: `fromParty_tin`, `fromParty_account`, `payment_currency`, `total_balance`, `debit_balance`, `credit_balance`, `operationDate`, `memberName`, `sender`, `memberId`, `operationId`, `raw_sourceEvent`, `raw_currentState`

TIN (taxpayer identification number) + `participant_balance` + `raw_sourceEvent`/`raw_currentState` fields describe a payment switch or clearing/settlement system. `raw_sourceEvent` field may contain serialized payment payloads. "switchdev2" in cluster name suggests a development/staging environment, not production — tier reflects this.

Tier: MEDIUM (financial schema confirmed, dev/staging context, raw event payload contents not verified).

**FINDING P-4: Multi-tenant chat with plaintext messages (134.195.41.62)**

Live-verified 30 tables including `chat_messages_core`, `customers`, `chat_message_attachments`, `chat_schedule_messages`, `user_active_session`. Schema confirms `plaintext` field in `chat_messages_core` and full PII in `customers` (`first_name`, `last_name`, `email`, `phone`, `dob`, `gender`). 30 tables including dev/test variants.

Tier: HIGH (PII schema + `plaintext` message field confirmed unauth, message contents not read).

**FINDING P-5: AI agent observability logs (34.93.49.167 + 35.200.140.198) — Cluster: pinot-quickstart**

Tables: `BUSINESS_METRICS_PINOT` (2.6 GB), `DATA_AGENT_OBSERVABILITY`, `DATA_AGENT_TRACE_LOGS`, `UILogs`, `bizviz_audit`

`DATA_AGENT_OBSERVABILITY` schema: `logType`, `sessionId`, `userId`, `spaceKey`, `provider`, `requestId`, `model`, `operation`, `assistId`, `completion_tokens`, `prompt_tokens`, `total_tokens`, `total_time`, `eventtime`

Unauth access to AI agent session telemetry — user session enumeration, LLM provider + model per request, token counts, timing. Operator: "bizviz" (cluster name). Attribution unresolved.

Tier: MEDIUM (observability schema confirmed, session data class, no personal identity fields confirmed).

**FINDING P-6: API metering/billing store (34.166.255.171) — Cluster: meter-inc-pinot**

Tables: `metering_production_ai_credits`, `metering_production_api`, `metering_production_automation`

Schema includes: `user_id`, `org_id`, `token_id`, `remote_ip`, `request_graphql`, `graphql_complexity`, `graphql_resources`, `organization_id`, `credits`, `source`

All tables currently 0 bytes — newly initialized or recently cleared. Schema is production-class. When populated: full API request log per user/org, GraphQL query content, AI credit deduction per organization. Attribution surface when active.

Tier: LOW (schema confirmed, tables empty at survey time).

**Other confirmed unauth instances (lower signal):**

| IP | Tables / Context | Cloud |
|---|---|---|
| 20.25.249.188 | geofencing/fleet: devices, geofences, vehicle\_device\_mapping, org, osm\_points (9 tables) | Azure |
| 129.159.143.69 | 71 monitoring history tables (IDs) | Oracle |
| 152.70.196.46 | aviation: aircraft\_status\_realtime, crew\_activity, crew\_assignment\_realtime, crew\_rules\_data | Oracle |
| 39.106.85.5 | Naver Pinpoint APM: systemMetricDataType, uriStat | Alibaba |
| 74.249.56.176 | IoT/traffic: Intersection\_Traffic\_Telemetry, Simulator\_IOT\_Telemetry | Azure |
| 9.169.241.239 | mixed: LeadTime, autosolve, cmpny, UUID-named (16 tables) | IBM |
| 103.24.200.156 | events\_intraday\_20250714/15 — intraday trading naming | CN |
| 185.254.223.146 | test cluster: s3endpoint\_l2\_full + transcriptt | DE |

---

## Cross-Platform Patterns

**Auth default is the problem class, not a per-platform quirk.** All four platforms ship with authentication disabled or trivially bypassable. ClickHouse: empty default password. Cassandra: `AllowAllAuthenticator`. ScyllaDB: inherits Cassandra default + REST API adds a second open surface. Pinot: no auth configuration required or prompted on install. Each platform documents that you *can* enable auth. None require it on first start.

**Cloud-hosted default is worse than on-prem default.** The BIN-Pinot retail cluster and Hamropatro fintech cluster both run on GCP with no firewall rules blocking public internet access. The ScyllaDB cluster at 34.90.240.245 is GCP Netherlands. Snap-E Cabs is GCP Delhi. Cloud VMs ship with public IPs and no firewall unless the operator configures it. The combination of default-no-auth + default-public-IP is the consistent failure pattern across all four platforms.

**Data class distribution in specialty OLAP/NoSQL is production-grade.** These are not experiment clusters. ClickHouse instances show `users`, `sessions`, `audit_log` — live application backends. The Pinot retail cluster has 490 GB of production sales data. ScyllaDB at Snap-E Cabs carries 431,808 driver safety events and live auth tokens. The framing "specialty data layers are infrastructure, not product" is wrong — they are the data layer of production applications with real user records.

**Prometheus port (9180) is the recon layer.** ScyllaDB's Prometheus endpoint is universally exposed and carries operational intelligence: shard count, read/write throughput by shard, compaction status, replica lag. An attacker reads 9180 first to build a timing and topology map before touching CQL.

---

## Dork Signal Analysis

| Platform | Primary Dork | Hits | Signal Quality |
|---|---|---|---|
| ClickHouse | `"X-ClickHouse-Server-Display-Name"` | 270 | High precision — vendor-unique header |
| Cassandra | `product:"Cassandra"` | 89 | Low precision — Thrift port, not CQL binary |
| ScyllaDB | `port:9180 "seastar"` | 99 | High precision — Seastar framework string |
| ScyllaDB | `port:10000 "Seastar"` | 58 | High precision — REST API |
| Pinot | `port:9000 "Apache Pinot"` | 31 | High precision — HTTP broker port |

**ScyllaDB discovery gap:** No Shodan product fingerprint exists for ScyllaDB. The CQL port (9042) is binary-protocol, not text-indexable. Discovery requires the side-channel ports (Prometheus 9180, REST 10000) — both Seastar-branded. This means the population of port-9042-only ScyllaDB instances is Shodan-dark.

**DuckDB result:** `port:9999 "duckdb"` → 888 hits, all Dozzle Docker log viewer (CSP header FP). `"duckdb" port:8000` → 12 hits, same FP class. DuckDB has no built-in server; web exposure requires MotherDuck or custom wrappers. No confirmed DuckDB HTTP exposure found in this survey.

---

## Arsenal Checklist

```
ASSESSMENT CHAIN — Cat-30: Specialty Data Layers
[x] Dork harvest         — 21 dorks tested, 4 platforms
[x] ClickHouse probe     — 21/21 unauth confirmed; SHOW DATABASES + SHOW TABLES
[x] Cassandra CQL probe  — 41/70 open; bespoke cql_probe.py (aimap gap)
[x] ScyllaDB REST probe  — 24/107 confirmed via /storage_service/keyspaces
[x] Pinot HTTP probe     — 21/31 unauth; /tables + schema enumeration
[x] aimap                — aimap-clickhouse.json, aimap-cassandra.json, aimap-scylla.json, aimap-pinot.json; aimap-scan.json (combined, running)
[ ] VisorGraph           — cert pivots pending on 109.94.170.165, 139.99.135.124, 146.59.83.12, 34.34.168.173 (BIN-Pinot attribution), 182.93.94.236 (Hamropatro confirm)
[x] aimap-profile        — N/A: no domain seeds available for most hosts; profile embedded per-finding
[ ] VisorLog             — pending: ingest aimap-scan.json after run completes
[ ] VisorScuba           — pending: compliance score on key unauth instances
[ ] BARE                 — pending: module match on ClickHouse + Cassandra finding set
[ ] VisorBishop          — pending
[ ] menlohunt            — GCP hosts in set: 34.34.168.173, 34.38.84.140, 34.62.39.124, 34.93.49.167, 35.200.140.198, 34.131.90.52, 34.90.240.245 (ScyllaDB Snap-E Cabs already processed)
[ ] recongraph           — pending: domain seeds from VisorGraph pivots
[ ] nu-recon             — pending: passive deep-read on BIN-Pinot and Hamropatro anchor hosts
[ ] VisorPlus            — pending: passive DNS on confirmed hosts
[ ] JS-bundle            — N/A: CLI data stores, no web UI bundle to extract
[ ] VisorHollow          — SKIP (binary-can't-execute)
[ ] VisorAgent           — ETHICAL STOP (controlled targets only)
```

---

## Related Case Studies

- [Snap-E Cabs ScyllaDB Exposure](./snapecabs-scylladb-34.131.90.52-2026-05-28.md) — BSE-listed EV ride-hailing, full fleet + driver telemetry
- [Sanio AI AgentOS Collision Pipeline](./sanio-ai-collision-agentOS-2026-05-28.md) — LLMjacking, Temporal credentials, Walmart data in scope (cat-06 straggler, referenced here for cross-survey context)

---

## Pivot Avenues

1. **BIN-Pinot operator attribution** — "BIN-Pinot" cluster name + RFID + `omni_location_master` + `store_health_score` + `shs_subscore_ranking`. Run VisorGraph cert pivot on 34.34.168.173. RFID omnichannel pattern narrows to top-10 global fashion retailers.
2. **Hamropatro confirm** — `hamropatro_event_analytics` table name is direct attribution. Confirm via reverse DNS or cert CN on 182.93.94.236. Contact: security disclosure via hamropatro.com.
3. **GCP cluster at 34.x.x.x (Cassandra)** — 12 GCP us-central1 open Cassandra nodes suggest a single operator. Run VisorGraph on the subnet to find cert or domain attribution.
4. **switchdev2 TIN payment switch** — 4.187.254.121 cert pivot. "d2\_" prefix + TIN field + participant balance suggests a central bank or PSP clearing system. Staging label ("switchdev2") suggests a production counterpart may exist.
5. **bizviz AI agent operator** — 34.93.49.167. DATA\_AGENT\_OBSERVABILITY schema with `spaceKey` and `assistId` fields — search "bizviz" as product/company in Shodan org/domain fields.
6. **103.24.200.156 intraday trading** — `events_intraday_20250714` naming convention = financial trading analytics. Adjacent port 8099 (Pinot broker port) confirmed open. Query surface probe if warranted.
