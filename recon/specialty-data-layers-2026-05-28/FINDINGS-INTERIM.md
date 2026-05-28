# Cat-30: Specialty Data Layers — Interim Findings
**Date:** 2026-05-28  
**Status:** Pinot agent pending; ClickHouse/Cassandra/ScyllaDB complete

---

## CONFIRMED FINDINGS

### ClickHouse — 21/21 UNAUTH (100%)
**Dork:** `"X-ClickHouse-Server-Display-Name"` → 270 hits → 120 IPs harvested → 21 confirmed by aimap  
**Auth probe:** `GET /ping` → `Ok.` / `GET /?query=SHOW DATABASES` returns data without credentials

| IP | Display Name | Databases | Notes |
|---|---|---|---|
| 109.94.170.165 | ch-cluster | events, telemetry, clickstream, audit_log | MinIO on 9000 (internal) |
| 135.125.237.161 | ch-node-1 | audit (errors, logs, metrics, access_log, audit_log) | |
| 212.147.235.10 | ch-cluster | reporting, audit | |
| 216.238.107.138 | ch-cluster | warehouse, metrics | |
| 139.99.135.124 | warehouse | production (access_log, audit_log, sessions, page_views, users, responses, clicks) | |
| 146.59.83.12 | warehouse | production (conversions, page_views, audit_log, users, logs, requests) | |
| 64.176.60.25 | data-warehouse | reporting | |
| 194.71.126.47 | ch-edge-01 | default only | 4-node same-operator cluster |
| 5.78.43.223 | ch-edge-01 | default only | same cluster |
| 194.182.166.180 | ch-edge-01 | default only | same cluster |
| 34.65.46.30 | ch-edge-01 | default only | same cluster |
| 64.176.18.142 | ch-prod | reporting, clickstream, events | Production instance |
| 54.38.184.2 | ch-analytics | clickstream, analytics, telemetry | OVH-hosted |
| 185.154.110.14 | (default) | user_events (audit_log, responses, events, page_views, users) | |
| 198.13.39.215 | warehouse | metrics, warehouse | |

**Data classes confirmed (SHOW TABLES):**  
- `users` tables in production databases → PII-class  
- `sessions` → active session data  
- `audit_log` → operational audit records  
- `access_log` → IP/UA analytics  
- `clickstream` → user behavior tracking  

**Versions:** 24.3.x - 24.8.x (all 2024, none current). No hardened Docker defaults in effect on these bare installs.

---

### Cassandra — 41/70 OPEN (58.6% unauth)
**Dork:** `product:"Cassandra"` → 89 hits → 70 IPs probed via CQL binary protocol  
**Probe method:** CQL OPTIONS → SUPPORTED → STARTUP → READY (open) vs AUTHENTICATE (gated)

| Cluster | IPs | Notes |
|---|---|---|
| GCP us-central1 (34.x.x.x) | 12 hosts | Possible single operator |
| Independent | 29 hosts | Mixed operators |

**Auth-required:** 5/70 (7%)  
**No-ScyllaDB:** 0 SCYLLA markers in SUPPORTED frames across 70 probes  
**aimap gap:** Cassandra fingerprint not in aimap — CQL binary not covered; needs `enumCassandra` addition

Open instances (41):  
103.29.189.30, 104.42.179.74, 114.132.75.232, 117.50.159.235, 119.8.9.77, 131.153.50.76, 155.138.254.50, 157.230.246.248, 159.203.140.14, 161.97.83.9, 183.90.170.144, 202.73.50.123, 206.1.12.224, 217.182.187.52, 34.121.136.180, 34.126.221.147, 34.126.67.57, 34.136.247.1, 34.138.247.1, 34.14.175.106, 34.173.37.204, 34.44.91.108, 34.61.224.70, 34.67.35.252, 34.68.28.25, 34.69.185.125, 34.72.45.182, 35.225.70.38, 35.232.176.39, 35.238.53.188, 43.134.124.194, 47.181.219.188, 47.181.219.192, 47.95.113.249, 50.250.206.114, 52.169.219.37, 61.138.213.171, 75.119.131.176, 80.67.224.183, 82.202.160.130, 91.203.134.249

---

### ScyllaDB — 24/24 REST API OPEN (100%)
**Dorks:** `port:9180 "seastar"` (99 hits) + `port:10000 "Seastar"` (58 hits) → 107 IPs → 24 confirmed by aimap  
**Auth probe:** `GET /storage_service/keyspaces` returns JSON without credentials

**Critical instances:**

| IP | Keyspaces | Operator | Severity |
|---|---|---|---|
| 34.90.240.245 | payments, wallets, auth, auth_otp, orders, users, companies, employees | Unknown (nyovenn) — fintech/logistics SaaS | CRITICAL (unverified) |
| 34.131.90.52 | 80+ alternator_* tables: snapecabs-ride-logs, mahindra-trip-payloads, fleetgpt_subscription, adas_linux_device_messages, vehicle-current-state, driver-* | Snap-E Cabs / EC Wheels India Pvt Ltd (BSE-listed, Kolkata) | CRITICAL (unverified) |
| 150.241.116.202 | posts, users, messages, usernames, counters | Unknown — social/messaging platform | HIGH |
| 208.69.76.x (10 nodes) | users, app_info | 2290008 Ontario Inc | HIGH |
| 89.222.120.108 / 89.187.173.217 | xtream_iptvpro_scylla | IPTV operator | MEDIUM |
| 68.183.80.97 | mb_blob_prod | Unknown — blob storage | MEDIUM |
| 47.238.29.124 | social, scylla_manager | Social platform | MEDIUM |

**Snap-E Cabs attribution:**  
- EC Wheels India Pvt Ltd, subsidiary of Steelman Telecom Ltd (BSE SME listed)  
- 600+ Tata Tigor EV fleet, Kolkata  
- Exposed: real-time vehicle GPS, driver profiles, trip history, ADAS telemetry, ML model config  
- Contact: support@snapecabs.com / Mayank Bindal (CEO) on LinkedIn  
- No bug bounty program  

**Prometheus (9180) exposure:** All 99 Seastar-matched hosts leak ScyllaDB shard metrics, CPU stats, read/write latency — topology intelligence without touching CQL.

---

## PENDING
- [ ] Pinot agent (31 IPs, CVE-2024-56325 test)
- [ ] VisorGraph cert pivots on anchor hosts
- [ ] aimap-profile classification on critical instances
- [ ] VisorLog ingest → nuclide.db
- [ ] Case studies: Snap-E Cabs, nyovenn, ClickHouse production instances
