---
type: survey
---

# New Vector Storage Survey: QuestDB / Meilisearch / PocketBase / NATS JetStream
_Survey date: 2026-05-09 | Platforms: QuestDB, Meilisearch, OpenObserve, PocketBase, NATS JetStream, CouchDB, Valkey_

## Executive Summary

Seven previously-unsurveyed AI-adjacent storage and messaging platforms probed via Shodan. 293 QuestDB consoles open with unauthenticated SQL execution, 488 Meilisearch instances health-confirmed (100% no-auth by default), 924 CouchDB instances with enumerable databases, 360 OpenObserve dashboards exposed. Three high-severity individual case studies follow.

---

## Survey Results

| Platform | Shodan Hits | Confirmed Live | Auth State |
|---|---|---|---|
| Meilisearch | 7,669 | 488 | 100% unauth (no API key required at /health, /indexes) |
| QuestDB | 390 | 293 | 100% unauth web console + SQL exec |
| OpenObserve | 493 | 360 | Login page present, some open |
| CouchDB | 5,831 | 924 | 71/89 sampled expose /_all_dbs |
| NATS JetStream | 476 | 72 | 20/20 sampled fully open monitoring |
| PocketBase | 43 | 40 | 4 with open /api/admins |
| Valkey | 799 | N/A (TCP) | No-auth filter = same as total |

---

## Case Study 1: GPS Tracking System. Unauthenticated QuestDB (106.14.252.215)

**Platform:** QuestDB 9000  
**Impact:** CRITICAL

QuestDB instance with no authentication. Tables confirmed via `/exec`:
- `users`: 13 records, columns: `openid`, `nickname` (Chinese), `create_time`
- `devices`: 309 records
- `GNSSUsers`: device-to-user mapping, `deviceID` column contains real IMEI-format values (e.g., `869701077438987`)
- `cat_devices` table present

GNSS = Global Navigation Satellite System. 309 tracked devices with IMEI identifiers, fully readable and writable via unauthenticated HTTP SQL API.

**Chain:** `GET /exec?query=SELECT * FROM GNSSUsers` → real-time device location history, IMEI enumeration, user identity linkage.

---

## Case Study 2: Mobile Ad Attribution Network. Open QuestDB (103.53.125.68)

**Platform:** QuestDB 9000  
**Impact:** HIGH

81 tables, obfuscated names (`tbl_zxesqswlk`, etc.) alongside platform-named tables: `oppo_stat_log`, `vivo_stat_log`, `ks_stat_log` (Kuaishou), `jl_stat_log`. Schema for `oppo_stat_log`:

```
id, adweiid, os, os_version, model, lang
```

Device fingerprint + ad attribution data for OPPO, Vivo, Kuaishou ad networks. Full read/write via unauthenticated SQL exec.

---

## Case Study 3: Observability Stack. 1,846-Table QuestDB (1.117.61.96)

**Platform:** QuestDB 9000  
**Impact:** MEDIUM (observability data, not PII)

1,846 tables ingested from Prometheus/MySQL exporters. Full metrics corpus open. Tables include: `mysql_global_status_*`, `redis_replication_*`, `prometheus_tsdb_*`. Entire infrastructure observability layer exposed: query any metric, any time range, unauthenticated.

---

## Meilisearch Index Exposure

7 of 488 confirmed instances expose `/indexes` (requires master key by default in Meilisearch ≥1.0, these are pre-1.0 or misconfigured):

| Host | Index Names |
|---|---|
| 103.54.16.37:7700 | `countries`, `departure_cities` (travel booking platform) |
| 120.26.38.129:7700 | `poi` (points of interest) |
| 124.158.124.91:7700 | `costco_products` |

Travel booking platform exposes full countries + departure cities search index. Readable without auth.

---

## PocketBase Admin Enumeration

4 instances return `/api/admins` without authentication (requires superuser token in PocketBase ≥0.8, these are misconfigured or legacy):

| Host | Identity |
|---|---|
| 101.126.152.105:8090 | Chinese-language app |
| 147.139.197.190:8090 | SOMA exam admin panel (Indonesian) |
| 34.27.33.212:8090 | Sketchware Backend |

SOMA: exam question management system with admin panel accessible without credentials.

---

## NATS JetStream Topology Exposure

20/20 sampled instances expose full monitoring API (`/jsz`, `/varz`, `/connz`, `/subsz`) without authentication. Server IDs, connection counts, stream topology, and message counts readable. Used as agent memory and event backbone in AI pipelines.

---

## CouchDB Mass Deployment Pattern

70/89 sampled CouchDB instances share an identical database schema:
```
_replicator, _users, admin, passwords, core-configuration, core-locales, core-photos, core-tasks
```
CouchDB 1.6.1 (EOL). All respond 200 to `/_all_dbs`. `passwords` database exists on all. Document-level access requires auth in most but the schema itself leaks application structure. Single vendor/framework deployed across dozens of IPs.

---

## Remediation

- **QuestDB**: Enable HTTP authentication via `http.security.user=` and `http.security.password=` in `server.conf`. Never expose port 9000 to internet.
- **Meilisearch**: Set `MEILI_MASTER_KEY` env var. All API access requires key when master key is set.
- **PocketBase**: Ensure admin API requires superuser JWT. Default in ≥0.8, verify deployment version.
- **NATS JetStream**: Set `http_port` to localhost-only or disable monitoring endpoint. Enable TLS + credentials for JetStream clients.
- **CouchDB**: Upgrade from 1.6.1 (EOL 2017). Enable CouchDB admin party fix. Set `[admins]` in config.
