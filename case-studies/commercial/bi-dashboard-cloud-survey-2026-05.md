---
type: survey
---

# BI/Dashboard Platforms: Auth Posture Survey

_NuClide Research · 2026-05-09_

---

## Summary

Four BI and analytics dashboard platforms surveyed via Shodan + asyncio probe: Metabase (1,789 IPs), Grafana (2,000 IPs), Apache Superset (1,176 IPs), Redash (1,079 IPs). Total 6,044 IPs → 4,449 confirmed reachable → **1,881 unauthenticated** (42% overall open rate).

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, S7068, S7070, S7075, T5904
- **733 (AI Risk & Ethics Specialist):** K7040, K7051, S7067, T5854, T5868, T5904
- **overlap (Common AI KSATs (all 5 roles)):** K108, K1158, K1159, K22, K6311, K6900, K6935, K7003, K7048, K942

<!-- ksat-tag:auto-generated:end -->

**Metabase** is the critical headline: 1,055 of 1,076 confirmed instances (98%) expose `/api/session/properties` without authentication. By design; this endpoint reveals the instance version, setup state, and crucially: **141 instances expose a live setup-token** confirming incomplete setup, meaning any external attacker can register as the first admin user and take full ownership of the database connection credentials. **Grafana** has 403 instances with the default `admin:admin` credential unchanged, granting full admin access to Prometheus, InfluxDB, PostgreSQL, ClickHouse, Elasticsearch, and MySQL datasources. **Apache Superset** has 266 instances with the default `admin:general` credential, providing full dashboard and chart access. **Redash** enforces an API-key model more consistently. 3% open rate.

---

## Metabase

### Methodology

```
shodan download --limit 2000 metabase.json.gz 'http.title:"Metabase"'
  → 1,789 unique IPs

asyncio probe (80 concurrent):
  GET  http://{ip}:3000/           → confirm Metabase HTML
  GET  http://{ip}:{port}/api/session/properties → version, has-user-setup, setup-token
  GET  http://{ip}:{port}/api/dashboard → 200 = public dashboard access
  GET  http://{ip}:{port}/api/public/dashboard → public sharing check
```

### Results

| Metric | Value |
|---|---|
| IPs probed | 1,789 |
| Confirmed reachable | **1,076** |
| `/api/session/properties` accessible | **1,055** (98%) |
| **Setup incomplete (first-admin takeover)** | **141** |
| Public dashboards enabled | 21 |

### The `/api/session/properties` Design Decision

Metabase intentionally exposes `/api/session/properties` without authentication. It's required to render the login page (the frontend needs the instance UUID, version, SSO config, and feature flags to display correctly). This is a documented behavior, not a misconfiguration. However, the response also includes:

- `has-user-setup`: whether the initial admin setup has been completed
- `setup-token`: **only present when `has-user-setup: false`**, the token required to register the first admin account
- `version`: full version string including build date and hash

**Impact of setup-token exposure:** Metabase's `/api/setup` endpoint accepts `setup-token` to create the first superuser account. Any external party who sees `has-user-setup: false` and retrieves the `setup-token` can register themselves as the initial admin with full database credentials, query access, and administrative control. This is equivalent to an unprotected admin registration page.

### Notable Finding: v0.59.5.1 Setup-Incomplete Instance

**Host:** `130.33.81.135:80`  
**Version:** v0.59.5.1 (build date 2026-03-31)  
**Severity:** HIGH. Current-version Metabase with exposed setup-token, first-admin registration possible

```bash
curl -s "http://130.33.81.135/api/session/properties" | jq '{
  "has-user-setup": .["has-user-setup"],
  "setup-token": .["setup-token"],
  "version": .version.tag
}'
# {
#   "has-user-setup": false,
#   "setup-token": "fb6d82ef-bcc8-491a-a54b-1865a50218cb",
#   "version": "v0.59.5.1"
# }
```

This is a 2026-03-31 build. Among the most recent Metabase versions available. The setup-token enables:

```bash
# Register first admin (full takeover)
curl -s -X POST "http://130.33.81.135/api/setup" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "fb6d82ef-bcc8-491a-a54b-1865a50218cb",
    "prefs": {"site-name": "TestOrg", "allow-tracking": false},
    "user": {
      "first_name": "Admin",
      "last_name": "User",
      "email": "admin@example.com",
      "password": "Password1!",
      "site_name": "TestOrg"
    }
  }'
```

141 instances at various versions are in this state. Version distribution of setup-incomplete instances:

| Version family | Count |
|---|---|
| v0.41.x | 32 |
| unknown | 19 |
| v0.46.x | 15 |
| v0.42.x | 13 |
| v0.39.x | 9 |
| v0.36.x | 6 |
| v0.34.x | 6 |

The concentration in v0.41 and earlier reflects deployments that were started, abandoned mid-setup, and left running. Often Docker containers or dev environments that were never properly decommissioned.

### Version Distribution (all confirmed)

| Version family | Count |
|---|---|
| v0.58.x | 123 |
| v0.56.x | 120 |
| v0.60.x | 104 |
| v0.59.x | 96 |
| v0.55.x | 67 |
| v0.53.x | 62 |
| v0.57.x | 55 |
| v0.50.x | 50 |
| v0.46.x | 44 |
| v0.47.x | 43 |

The distribution is heavily weighted toward recent versions (v0.56-0.60), confirming this is active production infrastructure, not legacy deployments.

### Auth Posture

Metabase uses session-based auth with an API key option (Enterprise). The `api/session/properties` endpoint exposure is by design. The 98% "unauth" rate in this survey reflects the endpoint being accessible, not the dashboard data. Dashboard queries require a valid session token. However, the **141 setup-incomplete instances** represent genuine admin takeover opportunities.

**CVE note:** [CVE-2023-38646](https://nvd.nist.gov/vuln/detail/CVE-2023-38646). Pre-auth RCE via H2 database JDBC connection setup during initial admin setup phase (fixed in 0.46.6.1 / 1.46.6.1). Several setup-incomplete instances are running versions ≤ 0.42.x, within the affected range.

---

## Grafana

### Methodology

```
shodan download --limit 2000 grafana.json.gz 'http.title:"Grafana" port:3000'
  → 2,000 unique IPs

asyncio probe (80 concurrent):
  GET  http://{ip}:3000/login        → confirm Grafana UI
  GET  http://{ip}:3000/api/health   → version (no auth required)
  GET  http://{ip}:3000/api/org      → anon viewer enabled check (200 = anon)
  GET  http://{ip}:3000/api/datasources + BasicAuth admin:admin → default creds
  GET  http://{ip}:3000/api/search?type=dash-db&limit=100 → dashboard list
```

### Results

| Metric | Value |
|---|---|
| IPs probed | 2,000 |
| Confirmed reachable | **1,961** |
| **Default admin:admin** | **403** |
| Anonymous viewer enabled | 244 |
| Either (total unauth) | **442** |

### Datasource Types Accessible via Default Creds

The following datasource types were enumerated across all 403 default-cred instances:

| Datasource | Instances |
|---|---|
| **prometheus** | 487 |
| **influxdb** | 78 |
| yesoreyeram-infinity-datasource | 61 |
| **loki** (log aggregation) | 59 |
| **grafana-postgresql-datasource** | 21 |
| **mysql** | 17 |
| **tempo** (distributed tracing) | 15 |
| **mssql** | 14 |
| **elasticsearch** | 13 |
| alexanderzobnin-zabbix-datasource | 11 |
| simpod-json-datasource | 9 |
| **grafana-clickhouse-datasource** | 5 |

**Prometheus** as a datasource means the Grafana admin has proxy access to the underlying Prometheus HTTP API, including `/api/v1/query_range`, `/api/v1/labels`, and `/api/v1/series`. The Prometheus data itself may be behind a firewall, but Grafana's datasource proxy exposes it indirectly.

**PostgreSQL/MySQL/MSSQL/ClickHouse datasources** are the highest-impact class: Grafana's datasource proxy can execute arbitrary SQL queries against the backend database through the `/api/ds/query` endpoint when authenticated. Default admin:admin gives full query execution capability against the connected database.

### Notable Findings

---

#### F1: PAM/jump-server infrastructure monitoring (MEDIUM/HIGH)

**Host:** `51.195.4.12:3000` (OVH FR)  
**Grafana version:** v12.4.1  
**Severity:** MEDIUM/HIGH. 100 dashboards, PAM/jump-server metrics, ClickHouse × 6 + Elasticsearch × 6 datasources; default creds + anon viewer

Folder structure: `jump_pmp` and `jump_pmp_bak`. Dashboard naming: `All_Server_Connection_Count`, `All_Server_Traffic_Min`, `All_Server_Traffic_Stat`. This is network monitoring infrastructure for a PAM (Privileged Access Management) or jump server fleet. The `pmp` abbreviation likely refers to a PAM product (Zoho Vault/ManageEngine PMP or similar). ClickHouse datasources suggest high-volume time-series storage of connection telemetry.

An attacker with default-creds Grafana access can:
1. Enumerate all ClickHouse datasources via `/api/datasources`
2. Execute raw ClickHouse SQL via `/api/ds/query`
3. Extract server connection history, privileged session metadata, and potentially credential usage logs from the PAM system

---

#### F2: Air quality monitoring network (LOW)

**Host:** `129.110.46.78:3000` (US academic or public)  
**Grafana version:** `12.0.0+security-01`  
**Severity:** LOW (public interest data, no PII)  
**Default creds + anon viewer enabled**

InfluxDB datasource with `defaultBucket: SharedAirDFW`, `organization: MINTS`. MINTS is the Mini Networked Sensors project (UT Dallas). A distributed air quality sensor network in the Dallas/Fort Worth area. 100 dashboards. Public interest research data, not a security-critical exposure, but the default credentials and fully open admin interface are inconsistent with research infrastructure hygiene.

---

#### F3: Multi-source infrastructure cluster (MEDIUM)

**Host:** `181.191.91.185:3000` (South America, likely BR)  
**Grafana version:** `12.3.2+security-01`  
**Severity:** MEDIUM. 82 dashboards, MySQL × 4 + Prometheus × 2 + Zabbix × 2; default creds + anon

MySQL datasources with direct SQL proxy access. 82 dashboards across MySQL + Zabbix monitoring. Zabbix is an enterprise network monitoring platform. The datasource connection means the Grafana admin key proxies to the Zabbix API, exposing all monitored hosts, alert states, and potentially authentication tokens.

---

#### F4: 107.161.208.x cluster (52 dashboards per node)

**Hosts:** `107.161.208.58`, `.59`, `.60`, `.61` (identical, 4-node cluster)  
**Severity:** MEDIUM. Cloudflare API, Google Sheets, Strava, MQTT, InfluxDB, Prometheus datasources; 52 dashboards each; all default creds

Four identically-configured nodes, likely load-balanced or replicated. Datasources include `cloudflare-api` (live Cloudflare zone/traffic data via API token stored in Grafana), `grafana-googlesheets-datasource` (Google Sheets access), `grafana-strava-datasource` (athlete activity data), and `grafana-mqtt-datasource`. The Cloudflare API datasource is the most sensitive: it contains an API token that can query zone analytics, WAF logs, and worker activity.

---

### Grafana Default Credential History

Grafana shipped with `admin:admin` as the default credential and a **first-login password change prompt** but no enforcement. The password change was enforced via `GF_SECURITY_ADMIN_PASSWORD_MUST_CHANGE=true` from Grafana 10.0+, but this is opt-in configuration. The 403 instances with unchanged admin:admin credentials span versions from 6.7.x to 12.4.1, confirming the soft-enforcement approach has not materially improved the credential hygiene rate.

---

## Apache Superset

### Methodology

```
shodan download --limit 2000 superset.json.gz 'http.title:"Superset"'
  → 1,176 unique IPs (9,754 total Shodan hits)

asyncio probe:
  GET  http://{ip}:8088/health → confirms reachable
  POST http://{ip}:8088/api/v1/security/login
    {"username":"admin","password":"general","provider":"db"} → default creds
  GET  http://{ip}:8088/api/v1/dashboard/ + Bearer token → dashboard list
```

### Results

| Metric | Value |
|---|---|
| IPs probed | 1,176 |
| Confirmed reachable | **711** |
| **Default admin:general** | **266** |
| Unauth (any path) | **360** |

**266 Superset instances accept `admin:general`**, apache Superset's documented default credentials. The `admin:general` default is called out in the Superset quickstart docs ("for testing only") and has been a known issue since Superset's initial public release.

### Impact of Default Creds

Superset with default credentials exposes:
- Full dashboard list (`/api/v1/dashboard/`). Chart layouts and query results
- Database connections list (`/api/v1/database/`). Connection strings, possibly including plaintext credentials
- Chart query execution (`/api/v1/chart/data/`). SQL queries run against connected databases
- Dataset definitions (`/api/v1/dataset/`). Table structures and column metadata

The database connection list is the highest-impact surface. Superset stores database connection URIs in its metadata DB, and with admin credentials, the full connection string (including password) is retrievable via `/api/v1/database/{id}/connection`:

```bash
# Get all database connections
curl -s -H "Authorization: Bearer {token}" "http://{ip}:8088/api/v1/database/" | jq '.result[].connection_string'
```

---

## Redash

### Methodology

```
shodan download --limit 2000 redash.json.gz 'http.title:"Redash"'
  → 1,079 unique IPs

asyncio probe:
  GET  http://{ip}:5000/           → confirm Redash HTML
  GET  http://{ip}:5000/api/queries → 200 = public/anon query access
  GET  http://{ip}:5000/api/settings/organization → org settings accessible
```

### Results

| Metric | Value |
|---|---|
| IPs probed | 1,079 |
| Confirmed reachable | **701** |
| Unauthenticated query access | **24** |
| Default credentials | 0 |

Redash enforces an API-key model at the query and datasource level, with no universal default credential. The 24 unauth instances reflect deployments with anonymous view or public query sharing enabled. Redash's `PUBLIC_ACCESS` setting allows queries to be shared without authentication.

**Best auth posture among the four platforms surveyed**: Redash's per-query API key model means there is no universal credential to rotate, reducing the blast radius of any single misconfiguration.

---

## Comparative Auth Posture

| Platform | Reachable | Unauth | Unauth % | Primary risk |
|---|---|---|---|---|
| **Metabase** | 1,076 | 1,055 | **98%** | Setup-token = admin takeover; CVE-2023-38646 on old versions |
| **Apache Superset** | 711 | 360 | **51%** | Default `admin:general`; database connection strings exposed |
| Grafana | 1,961 | 442 | 23% | Default `admin:admin`; datasource proxy = DB query execution |
| Redash | 701 | 24 | 3% | Per-query API key model; best posture of the four |

**Pattern:** The three platforms with universal default credentials (Metabase, Grafana, Superset) all show elevated exposure rates. Redash's absence of a universal default credential is structurally superior for deployment hygiene.

---

## Discovery Context

Survey conducted 2026-05-09. Shodan queries: `http.title:"Metabase"` (9,754+ hits, 2,000 sampled → 1,789 unique), `http.title:"Grafana" port:3000` (2,000 sampled), `http.title:"Superset"` (9,754 hits, 2,000 sampled → 1,176 unique), `http.title:"Redash"` (2,000 sampled → 1,079 unique). Asyncio probe with 2s connect / 5s read / 80 concurrent.
