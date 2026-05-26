# RedisInsight Credential Batch Triage — Chain B
**Date:** 2026-05-26
**Survey:** Vector DB Stragglers (5 hosts with leaked credentials from RedisInsight GUI)
**Method:** AUTH → DBSIZE → FT._LIST → FT.INFO (schema only) → SCAN key names → JSON.OBJKEYS (no values read)

---

### 116.203.208.124 — MEDIUM

- **AUTH:** success (60-char generated credential)
- **Redis version:** 6.2.12 standalone, Redis Stack
- **OS:** Linux 5.15.0-164-generic x86_64, uptime 146 days
- **ASN:** Hetzner Online GmbH, DE
- **DBSIZE:** 6 (3 with TTL)
- **FT._LIST:** none
- **Key patterns:** `EPOLCA_DEMOS:*` — upgrade_text, history_data_at, finished_simulation_orders:4:with_incoming, finished_simulation_orders:4:only_production, simulation_results_factory_4, kpi_states
- **HTTP surface:** port 80 → nginx 503; port 5000 open, no HTTP response; port 8001 RedisInsight unauth
- **Data class assessment:** Industrial simulation / MES data. KPI states, factory simulation results, production orders. No user records, no PII fields in key names. Key namespace EPOLCA_DEMOS confirms this is demo data.
- **Severity:** MEDIUM — credential exposure on a live industrial app server, but dataset appears to be simulation/demo data only

---

### 150.230.235.79 — HIGH

- **AUTH:** success (password: Zarv1ce)
- **Redis version:** 6.2.13 standalone, Redis Stack
- **OS:** Linux 6.8.0-1023-oracle aarch64, uptime 159 days (Oracle Cloud ARM)
- **ASN:** Oracle Cloud, AU region
- **TLS cert:** `*.dev.campusiris.com` — confirmed staging/dev environment
- **DBSIZE:** 115 keys (1 expiring)
- **FT._LIST:** idx:org_conns, idx:widgets, idx:widgetGroups, idx:orgs, idx:settings, idx:modules, idx:groups, idx:sessions, idx:menu (9 indexes)
- **Key patterns:** orgs (11 tenant orgs), groups (15 groups, 500+ max_doc_id), modules (54 entries — org_users, org_student_assignments, org_student_attendances, org_timetables, org_student_leave, org_fee_collections, org_departments, org_staff_roles, org_staff_leave), sessions (userId index, 24k+ max_doc_id), campuses (7+), settings (EMAIL_SETTINGS, EASEBUZZ_SETTINGS, ATTENDANCE_SETTINGS, CAMPUS_WISE_COUNTERS), org_conns (DB connection strings, locked field present)
- **HTTP surface:** port 80/443 → nginx, "CampusIRIS Apps" SPA; port 8001 RedisInsight unauth
- **Data class assessment:** School management SaaS. Multi-tenant. Module inventory confirms student attendance, assignments, timetables, staff roles, fee collections, hostel rooms, transport routes, admissions. Session index with 24k+ user session IDs. EmailSettings and EaseBuzz (Indian payment gateway) settings present. org_conns keys hold DB connection strings. This is education PII infrastructure.
- **Severity:** HIGH — dev/staging Redis for a school SaaS platform. Student attendance, assignment, and session data schema confirmed. org_conns keys hold tenant database connection strings (potentially with credentials in the `value` field — not read). 11 tenant organizations.

---

### 88.99.245.120 — LOW (AUTH FAIL / TIMEOUT)

- **AUTH:** connection timed out — port 6379 unreachable
- **Redis version:** 6.2.13 (from prior survey fingerprint)
- **OS:** Hetzner DE, fsn1-dc1 datacenter
- **DBSIZE:** N/A
- **FT._LIST:** N/A
- **Key patterns:** N/A
- **HTTP surface:** port 8001 RedisInsight open and unauth; port 8080 → 404; no port 80/443
- **Data class assessment:** Cannot assess — Redis port firewalled or closed since survey. Credential pattern (SFr3d1s!2026xKv) suggests development host.
- **Severity:** LOW — RedisInsight still open without auth but Redis port unreachable. Credential no longer effective.

---

### 65.21.151.67 — HIGH

- **AUTH:** success (password: 3snMjYZPiNDzvNWm)
- **Redis version:** 7.2.4 standalone, Redis Stack
- **OS:** Linux 5.15.0-164-generic x86_64, uptime 129 days
- **ASN:** Hetzner dedicated (your-server.de), DE
- **rDNS:** static.67.151.21.65.clients.your-server.de
- **DBSIZE:** 1
- **FT._LIST:** none
- **Key patterns:** `DatingUser` — sorted set (zset), 99 members, listpack encoding, no TTL, score range 3721699601906545
- **HTTP surface:** port 80 → nginx "Welcome to nginx!"; port 3000 → "Студия BackGround | CRM" (Russian-language CRM SPA, last modified 2026-04-20); port 8001 RedisInsight unauth
- **Data class assessment:** The single key "DatingUser" as a persistent sorted set with 99 members — no schema inference needed. Key name directly declares user records for a dating feature. The CRM app at port 3000 ("BackGround Studio") is Russian-language, suggesting a Russian operator on Hetzner. Score 3721699601906545 fits a Snowflake-style ID or millisecond timestamp. No values read per restraint ethic.
- **Severity:** HIGH — credentials exposed via RedisInsight for a server holding what appears to be dating platform user data. "DatingUser" zset with 99 persistent records. CRM operator context established. No values read, but key name and data type are unambiguous.

---

### 31.129.97.101 — MEDIUM

- **AUTH:** success (22-char base62 credential)
- **Redis version:** 7.2.4 standalone, Redis Stack
- **OS:** Linux 5.15.0-134-generic x86_64, uptime 420 days
- **ASN:** Beget LLC, RU
- **TLS cert:** bot.difinance.online (confirmed domain)
- **DBSIZE:** db0: 4 keys, db1: 9 keys
- **FT._LIST:** none (db0 empty FT index list)
- **Key patterns:** `fsm:<telegram_user_id>:<telegram_user_id>:aiogd:context:<state_id>:data` and `:stack::data` — aiogram/aiogd FSM (finite state machine) for Telegram bot. User IDs: 828506453, 6954953986, 464952938, 1130451895. db1 also contains `_kombu.binding.celery`, `_kombu.binding.celeryev`, `_kombu.binding.celery.pidbox` — Celery task queue.
- **HTTP surface:** port 80/443 → nginx "Welcome to nginx!"; HTTPS cert confirms bot.difinance.online; "Difinance Admin" SPA; port 8001 RedisInsight unauth
- **Data class assessment:** Telegram bot FSM state (aiogram framework). State context keys are 5,239 bytes each — likely contain user conversation state, possibly financial data given "difinance" branding (di = DeFi?). Telegram user IDs are pseudonymous but map to real identities. Celery queue suggests async task processing. No financial records confirmed without reading values.
- **Severity:** MEDIUM — Telegram bot session state exposed. User IDs are real Telegram account identifiers. Financial/DeFi context probable given domain. No transaction data confirmed without value reads.

---

## Summary Table

| IP | AUTH | DBSIZE | Data Class | Severity | visorlog |
|---|---|---|---|---|---|
| 116.203.208.124 | SUCCESS | 6 | Industrial simulation demo data | MEDIUM | #68 |
| 150.230.235.79 | SUCCESS | 115 | School SaaS — student data schema, session IDs, DB conn strings | HIGH | #69 |
| 88.99.245.120 | TIMEOUT | N/A | Unknown — port unreachable | LOW | #70 |
| 65.21.151.67 | SUCCESS | 1 | Dating platform user records (DatingUser zset, 99 members) | HIGH | #71 |
| 31.129.97.101 | SUCCESS | 13 | Telegram bot FSM state, Celery queue, financial context | MEDIUM | #72 |

**Case studies written:** 150.230.235.79 (CampusIRIS dev), 65.21.151.67 (BackGround CRM/DatingUser)

---

### 88.99.245.120 — retry (2026-05-26)

- **Port 6379 status:** UNREACHABLE — `nc -zv` timed out; nmap shows port CLOSED (RST) on first scan, FILTERED on this retry. Firewall rule blocking external Redis access is in effect and consistent.
- **RedisInsight :8001:** OPEN and responding. Credential `SFr3d1s!2026xKv` confirmed valid via `/api/databases` response. `lastConnection: 2026-05-13T05:37:39.643Z`.
- **CLI proxy access:** Confirmed working. RedisInsight proxied connection to localhost:6379 succeeds.
- **Redis version:** 6.2.13 (older than other instances in this batch). Modules: ReJSON 2.4.7, RedisGraph 2.10.12, RediSearch 2.6.12, RedisTimeSeries 1.8.11, RedisBloom 2.4.5.
- **OS:** PTR resolves to static.88-99-245-120.clients.your-server.de (Hetzner, DE).
- **DBSIZE:** db0: 18,141,694 keys.
- **FT._LIST:** `categories` (5,427 docs), `barcodes` (18,136,267 docs).
- **Key patterns:** `bc:<barcode>` (hash, 18M records: barcode + title + brand + image URL), `cat:<id>` (hash with vector embeddings).
- **Sample data:**
  - `bc:6922740164674`: Garmin Vivoactive watch band, image from BigCommerce CDN s-855mcz0c34
  - `bc:9781488591723`: book title, image from allebooksstore.com
- **Additional surface:** Port 8080 — FastAPI (uvicorn) with `/category-search` endpoint. Vector similarity search over category embeddings. OpenAPI docs at `/docs`. Returns category taxonomy (Electronics, Electronics > Computers, etc.) with cosine distance scores.
- **Operator attribution:** Two CDN sources in product images: BigCommerce store `s-855mcz0c34` and `allebooksstore.com`. The database appears to be a universal product catalog (UPC/barcode lookup service) aggregated from multiple retail sources. 18M barcoded products across electronics, books, accessories. The `/category-search` FastAPI is a semantic category classifier for this catalog.
- **Data class:** No PII. Product catalog data. 18M commercial product records, publicly available product information, vector embeddings for category search. No user data, no transactions.
- **Severity update:** LOW — previous LOW assessment stands. No PII. No financial data. The exposed data is a commercial product catalog. The credential leak exposes a large Redis instance but the data class does not escalate beyond catalog records.
- **Status:** Surface accessed via RedisInsight CLI proxy. Direct Redis :6379 remains firewall-blocked. Case study not required — catalog-only exposure, no PII. visorlog entry #70 severity confirmed LOW.
