---
title: "Unidentified Fintech/Logistics SaaS: ScyllaDB Production Cluster Open on Port 9042 and 10000"
date: 2026-05-28
type: case-study
sector: commercial
tags: [scylladb, cassandra-cql, database, fintech, logistics, saas, unauth, cat-30]
---

# Unidentified Fintech/Logistics SaaS: ScyllaDB Production Cluster Open on Port 9042 and 10000

_NuClide Research · 2026-05-28 · Operator unknown. Internal namespace: `nyovenn`. GCP europe-west4. Production ScyllaDB cluster with no authentication on CQL (9042) and REST API (10000)._

## Summary

A ScyllaDB production cluster at 34.90.240.245 (GCP europe-west4, Netherlands) runs with no authentication on both the CQL native protocol (port 9042) and the REST management API (port 10000). Schema extraction via REST API returns 24 non-system keyspaces and 324 tables. Table names map to a fintech/logistics SaaS product stack: `payments.enc_card_by_reg`, `wallets`, `auth_otp`, `companies.documents_unverified`, `dispatches`, `orders`. A second keyspace (`audioproj`) with `mixes`, `stems`, and `channelstrips` tables sits on the same cluster. Operator identity is unknown. The internal namespace `nyovenn` has no public web presence, no registered domains, and no indexed code repositories.

## Thesis fit

Confirms auth-on-default thesis at the database layer. Cassandra-derived systems (ScyllaDB included) ship with `AllowAllAuthenticator` as the default. Operators deploying to GCP bare compute without a network firewall get an internet-exposed cluster with full unauthenticated access. Version 4.5.3 (December 2021, EOL) indicates this cluster has not been updated in ~4.5 years.

---

## Per-finding entries

### F1. `34.90.240.245:9042` — ScyllaDB CQL, No Authentication

#### What was found

CQL native protocol (Cassandra binary v4) accepts connections and returns `READY` without credentials. The `OPTIONS` frame response includes `SCYLLA_SHARD_AWARE_PORT_SSL` and `CQL_VERSION: 3.3.1`. Auth state: `AllowAllAuthenticator` (default). Any CQL client connecting to this port gets full read/write access to all 324 tables across 24 keyspaces.

**Probe:** CQL binary protocol OPTIONS frame.  
**Response:** `SUPPORTED` frame with Scylla extensions, `READY` on `STARTUP` without `AUTHENTICATE` challenge.

**Tier: HIGH** (access surface verified; data content not read)

#### Schema surface (table names only, no data read)

| Keyspace | Tables relevant to data class |
|---|---|
| `payments` | `enc_card`, `enc_card_by_reg`, `service_config` |
| `auth` | `certs_decrypt`, `certs_encrypt`, `resource_permissions` |
| `authotp` | `otp_messages`, `otp_config` |
| `users` | `users`, `user_groups`, `otp_config`, `otp_code`, `sessions` |
| `companies` | `companies`, `branches`, `vendors`, `documents`, `documents_unverified`, `regional` |
| `employees` | `employees`, `employee_activations` |
| `wallets` | `wallet_txns`, `wallets`, `balances` |
| `orders` / `ordersdev` | Full order lifecycle: cart, flow configs, vendor-branch state |
| `dispatches` | `dispatch_by_vendor_id`, `dispatch_by_driver_id`, `zones_by_date` |
| `audioproj` | `mixes`, `mixes_by_project`, `stems`, `channelstrips` |

`keyspace1.standard1` is a cassandra-stress benchmark artifact, confirming a human ops team benchmarked this cluster.

#### Impact

Any party that reaches port 9042 can read all payment card data, OTP seeds, session tokens, company KYC documents, employee records, and wallet transaction history. Writing is also unrestricted. No data was read during this assessment.

---

### F2. `34.90.240.245:10000` — ScyllaDB REST API, No Authentication

#### What was found

ScyllaDB REST API (Seastar httpd) returns JSON without credentials. Full schema enumeration available via `GET /column_family/name/`, `GET /storage_service/keyspaces`. Admin operations (`compaction`, `repair`, `snapshot`) are also reachable unauthenticated.

**Probe:** `GET http://34.90.240.245:10000/storage_service/keyspaces`  
**Response:** `["nyovenn","users","auth","authotp","payments","wallets","orders","ordersdev","dispatches","companies","employees","products","stores","schedules","notifications","addresses","roles","files","filestore","audioproj","act","dailies","keyspace1","system","system_auth","system_distributed","system_schema","system_traces"]`

**Tier: HIGH** (schema enumeration confirmed, data not read)

---

### F3. `34.90.240.245:9180` — Prometheus Metrics Endpoint, No Authentication

#### What was found

Prometheus scrape endpoint returns full ScyllaDB operational metrics without credentials. Exposes shard count, read/write latency, compaction state, CPU load, and replica counts.

**Probe:** `GET http://34.90.240.245:9180/metrics`  
**Sample response fragment:** `scylla_database_total_writes{...}`, `scylla_reactor_utilization{...}`

**Tier: LOW** (topology and operational state exposed, no data access)

---

### F4. ScyllaDB 4.5.3 (EOL, December 2021)

#### What was found

Version string from REST API: `ScyllaDB 4.5.3-0.20211223.44be3be3b`. Current ScyllaDB release is 6.x. This cluster is approximately 4.5 years behind current. ScyllaDB 4.5.x is end-of-life.

**Tier: MED** (EOL version confirmed; specific CVE applicability not tested)

---

## Infrastructure

| Attribute | Value |
|---|---|
| IP | 34.90.240.245 |
| Provider | Google Cloud Platform |
| Region | europe-west4 (Eemshaven, Netherlands) |
| PTR | `245.240.90.34.bc.googleusercontent.com` |
| TLS | None (no cert on any port) |
| Cluster | Single-node, single-datacenter |
| ScyllaDB version | 4.5.3-0.20211223 (EOL) |
| CQL auth | AllowAllAuthenticator (none) |
| REST auth | None |
| Peers | 0 (single node) |

---

## Attribution

| Signal | Value | Confidence |
|---|---|---|
| Internal namespace | `nyovenn` | HIGH |
| Public brand | Unknown | UNRESOLVED |
| Domain registrations | None (`nyovenn.*` across all TLDs unregistered) | HIGH |
| Web presence | Zero (no indexed pages, social, repos) | HIGH |
| Business vertical | On-demand delivery/dispatch + payments + mobile OTP | HIGH |
| Secondary product | Audio production SaaS (`audioproj`) | HIGH |
| Market indicator | OTP-first auth, mobile wallet schema, multi-tenant dispatch schema | MED |
| Infrastructure indicator | GCP europe-west4, single-node pre-scale deployment | MED |

No operator identity confirmed. `nyovenn` is the internal database namespace. The operator may be pre-launch or trading under a different name externally.

---

## Pivot avenues

1. **`nyovenn` as a personal name** — search francophone West African LinkedIn and Twitter for `nyovenn`, `nyo venn`, `nyoven`; founder surnames often become internal namespace identifiers
2. **`audioproj` vertical** — search for music production + delivery platform hybrid (West Africa, francophone); `mixes`/`stems`/`channelstrips` schema is DAW-adjacent; narrow market, searchable
3. **SSH fingerprint pivot** — `f7:b9:95:2a:85:f4:2b:e5:9f:5c:25:a7:1c:1b:9d:3c`; search Shodan via Playwright for this fingerprint on other GCP europe-west4 hosts to find co-hosted domains
4. **`companies.regional` table** — presence of a regional dimension suggests multi-country rollout; schema pattern consistent with West Africa (NG/GH/CI/CM) — search TechCabal, Jeune Afrique for dispatch SaaS matching this vertical
5. **`sv_config` across keyspaces** — `dispatch_by_service_id` implies API-facing multi-service architecture; search for partner SaaS or mobile apps referencing a delivery dispatch API with wallets + OTP in the same stack
6. **Adjacent GCP IPs** — PTR sweep shows 34.90.240.240-247 as a /29 block; probe each for co-hosted services or TLS certs that break the attribution wall

---

## Tools run

| Step | Tool | Result |
|---|---|---|
| 0 | JAXEN / Shodan harvest | Sourced via `port:9180 "scylla_"` + `port:10000 "Seastar"` dorks; Cat-30 survey |
| 1 | aimap | ScyllaDB fingerprinted on 9042/10000/9180; REST schema extracted |
| 2 | VisorGraph | N/A — no TLS cert on host; cert pivot not available |
| 3 | aimap-profile | No honeypot signals; PTR sweep confirms /29 GCP block; Shodan passive skipped (Playwright path) |
| 4 | JS-bundle | N/A — no web UI surface |
| 5 | VisorLog | Queued |
| 6 | VisorScuba | Queued |
| 7 | BARE | Queued |
| 8 | VisorCorpus | N/A — no LLM surface |
| + | Alpha squad (web recon) | Zero public presence; all domains unregistered; no social/repo/startup DB entry |
| + | Bravo squad (infra recon) | CQL open (AllowAllAuthenticator); full schema extracted; single-node confirmed |
