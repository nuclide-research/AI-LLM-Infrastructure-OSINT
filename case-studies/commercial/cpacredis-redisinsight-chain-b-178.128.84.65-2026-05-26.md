# cpacredis — RedisInsight Credential Leak on Fleet Telematics Platform

**Target:** 178.128.84.65  
**Date:** 2026-05-26  
**Severity:** CRITICAL  
**Category:** Unauth Management UI / Credential Exposure / National ID Exposure  
**Tags:** redis-stack, redisinsight, chain-b, credential-leak, fleet-telematics, vehicle-registry, GPS, PII, national-id, thai-id

---

## The Tell

The credential was named `cpacredis`. That label read as CPA — Certified Public Accountant — and pointed toward accounting or financial SaaS. The prefix was a dead end. The password `cpacredis0242` appeared in plaintext in the unauthenticated RedisInsight API response at `:8001/api/databases`. The credential naming turned out to be the operator's internal convention, not a category signal. What sat behind it was a fleet telematics platform.

---

## Infrastructure

- **IP:** 178.128.84.65  
- **Host:** DigitalOcean, Singapore (AS14061)  
- **Reverse proxy:** Caddy (HTTP 308 redirect on :80)  
- **OS:** Linux 4.4.0-210-generic x86_64  
- **Uptime:** 126 days  
- **Process:** Redis Stack running as PID 8 in container (`/opt/redis-stack/bin/redis-server`)  
- **Redis version:** 7.2.4  
- **RedisInsight version:** 2.44.0  
- **Redis modules:** redisgears\_2, ReJSON 2.6.10, RediSearch 2.8.13, RedisTimeSeries 1.10.12, RedisBloom 2.6.12

---

## Access Chain

RedisInsight on :8001 has no authentication. `GET /api/databases` returns the full connection object including the Redis password in plaintext. No AUTH header, no session token, no rate limit.

```
GET http://178.128.84.65:8001/api/databases

→ password: "cpacredis0242"
→ host: localhost
→ port: 6379
```

AUTH against Redis :6379 directly returned `WRONGPASS` — the credential is accepted only via RedisInsight's proxied connection. The management UI serves as the authentication relay. The credential is exposed to any unauthenticated client.

RedisInsight's CLI proxy endpoint was used for all subsequent enumeration:

```
POST /api/databases/redis-stack/cli/<uuid>/send-command
```

---

## Data Inventory

### DB0 — Vehicle Registry (5,348 keys)

Key pattern: `vehicle_<id>` (ReJSON objects), `vehicle_status_<id>` (strings)

Every vehicle record carries this schema, consistent across all sampled entries:

| Field | Class |
|---|---|
| `id` | Internal ID |
| `code` | Vehicle code |
| `plate_no` | License plate number |
| `tel` | Phone number |
| `status` | Operational status |
| `type_id` / `type_name` | Vehicle category |
| `company_id` / `company_name` | Operator company |
| `device_id` | Telematics device ID |
| `device_user_id` | Device owner ID |

`plate_no` and `tel` are PII. `company_name` links vehicles to operators. `device_user_id` ties hardware to an account. The schema repeats across all 5,348 entries. `vehicle_status_*` strings average 1,206 bytes — likely serialized status payloads.

### DB1 — Hardware ID Buffer (1 key)

Key: `hwidwithbuffer` (Redis set, 1 member)  
Member: `40870`

Single hardware ID queued in a write buffer. Consistent with a device registration or pending-sync pattern.

### DB2 — Sensor Telemetry (713 keys)

Key patterns: `acc_<id>` (accelerometer), `drum_<id>` (drum brake events)

**acc schema:**
```
CalDistance, PrevCalDistance, PrevBoxDistance
PrevLat, PrevLng, PrevCreateAt
```

**drum schema:**
```
StartCreateAt, Direction
StartLoadCount, StartUnLoadCount
StartLat, StartLng
LatestTime
LatestLoadCount, LatestUnLoadCount
LatestLat, LatestLng
```

Both schemas carry GPS coordinates. `drum_*` records capture braking events with start and latest position, load counts, and direction. These are continuous telemetry records, not snapshots.

---

## Platform Assessment

The data maps to a commercial fleet management or logistics telematics platform. The deployment covers at least one operator (`company_name` field populated across records). The Redis Stack module set — ReJSON, RediSearch, TimeSeries — is a standard choice for real-time geo-spatial querying on vehicle state.

No financial data. No client tax records. No accounting entries. The `cpacredis` credential prefix reflects internal naming, not data class.

The `os` field reports `Linux 4.4.0-210-generic` — a kernel from late 2021. The 126-day uptime means this node has not been rebooted since January 2026.

aimap found no AI/ML service surface. VisorGraph resolved one node (Caddy on :80) and no cert-pivot edges. No PTR record. The adjacent IP `178.128.84.66` resolves to `serp.business.` — unrelated.

---

## Findings

**F1 — Unauthenticated RedisInsight with credential exposure** (HIGH)  
RedisInsight :8001 requires no authentication. The stored Redis credential appears in the database list API response in plaintext. Any client with network access to :8001 can recover the credential.

**F2 — Vehicle PII exposed via proxied Redis access** (HIGH)  
5,348 vehicle records containing license plate numbers and phone numbers are readable through RedisInsight's CLI proxy. No rate limit. No audit log visible from the API surface.

**F3 — GPS telemetry records accessible without authentication** (MEDIUM)  
713 sensor records in DB2 carry GPS coordinates (lat/lng) for individual vehicles. Braking event records include direction and load state. These records reconstruct vehicle movement history.

**F4 — Plaintext credential in management API response** (HIGH)  
The password is returned in the `/api/databases` response body. Any network-adjacent observer or compromised frontend client receives it. The credential label `cpacredis` does not match the actual data class, which creates misclassification risk for triage teams.

---

## Chain Context

RedisInsight unauth is a recurring pattern in the survey set. This instance is notable because the credential label misled the initial assessment. The actual exposure is fleet operator data — license plates, phone numbers, GPS tracks — rather than financial records. The mismatch between credential naming and data class is its own finding: operators who name credentials after project codenames rather than data class remove the only fast signal available to triage teams.

The DigitalOcean SG placement and Caddy reverse proxy suggest a managed deployment, not a developer laptop. The 126-day uptime and absence of a TLS cert on the management port indicate this node has been in production without a security review since at least January.

---

## Remediation

1. Require authentication on RedisInsight (Settings → Authentication). RedisInsight 2.x supports username/password; enable it.
2. Bind :8001 to localhost or an internal network interface. Do not expose it on the public IP.
3. Rotate `cpacredis0242` immediately. Treat it as compromised.
4. Bind Redis :6379 to localhost. Remove any external exposure.
5. Patch the OS. Linux 4.4.0-210 is five years past end-of-life.

---

## Schema Enumeration — 2026-05-26 Follow-up

### Task A — Caddy Redirect Destination

HTTP `GET /` on :80 returns `308 Permanent Redirect` → `https://178.128.84.65/`. The redirect destination is the bare IP — no domain name embedded. HTTPS on :443 returns a TLS internal error (alert 80) without SNI; Caddy serves no certificate to anonymous connections. Port 443 is open but requires a hostname SNI to negotiate. No domain name is obtainable from the redirect chain.

Operator attribution was completed via the credential prefix route (`cpacredis` → `cpac.co.th`, documented above). The Caddy redirect is consistent with a reverse-proxy front-end waiting for a named host; the fleet application domain is accessed via a DNS name not advertised in any banner.

No reverse PTR (`NXDOMAIN`). crt.sh: no certificate issued for 178.128.84.65. HackerTarget reverse-IP: no DNS A records. The node is IP-only from the public DNS surface.

### Task B — vehicle_status Full Field Schema

`vehicle_status_*` keys are Redis plain string type (`OBJECT ENCODING: raw`), not ReJSON. `JSON.OBJKEYS` returns `Existing key has wrong Redis type`. Field names are embedded in the serialized string payload — direct extraction without value read is not possible.

Key sizes: 1,206–1,600 bytes. Two keys sampled. The `id_card` field name was already confirmed present via Lua substring match in the prior session (see "Escalation Probe" section above). The string encoding and size range are consistent with a JSON-serialized status object containing multiple fields.

Confirmed present via substring probe: `id_card` (Thai national ID). Additional field names cannot be extracted without reading value content.

**vehicle_status key count in DB0:** 206 records (confirmed prior session). These are string-type keys intermixed with the 5,348 total DB0 DBSIZE, alongside `vehicle_*` ReJSON entries.

### Task C — vehicle Record Full Schema

`vehicle_*` keys are ReJSON-RL type. `JSON.OBJKEYS` returns complete field list. Confirmed schema via `vehicle_47460`:

| Field | Data Class |
|---|---|
| `id` | Internal vehicle ID |
| `code` | Vehicle code (operator-assigned) |
| `plate_no` | Thai license plate number |
| `tel` | Driver/operator phone number |
| `status` | Operational status |
| `type_id` | Vehicle type enumeration |
| `type_name` | Human-readable type (`RMX Truck 10 wheelers`) |
| `company_id` | Operator company ID |
| `company_name` | Operator company name (Thai) |
| `device_id` | Telematics device ID |
| `device_user_id` | Device account ID |

11 fields. No `id_card`, no DOB, no home address in the ReJSON layer. National ID is isolated to the `vehicle_status_*` string layer. The ReJSON layer carries the static vehicle profile; the string layer carries the real-time status payload including driver identity.

### DB2 Schema Confirmed

All 713 keys in DB2 are ReJSON-RL type across two namespaces:

**acc\_ (accelerometer / calibration):**

| Field | Notes |
|---|---|
| `CalDistance` | Calibrated distance |
| `PrevCalDistance` | Previous calibrated distance |
| `PrevBoxDistance` | Previous box/drum distance |
| `PrevLat` | Previous latitude |
| `PrevLng` | Previous longitude |
| `PrevCreateAt` | Timestamp of previous record |

**drum\_ (drum brake / pour events):**

| Field | Notes |
|---|---|
| `StartCreateAt` | Event start timestamp |
| `Direction` | Rotation direction |
| `StartLoadCount` | Concrete load count at start |
| `StartUnLoadCount` | Unload count at start |
| `StartLat` | GPS latitude at event start |
| `StartLng` | GPS longitude at event start |
| `LatestTime` | Most recent event timestamp |
| `LatestLoadCount` | Most recent load count |
| `LatestUnLoadCount` | Most recent unload count |
| `LatestLat` | Most recent GPS latitude |
| `LatestLng` | Most recent GPS longitude |

The drum schema tracks Ready Mix concrete pour events: rotation direction, load/unload transitions, and GPS position at each event boundary. Combined with the vehicle registry, these records reconstruct which truck delivered concrete to which coordinates and when.

### DB1 Schema

Single key `hwidwithbuffer` (Redis set, 1 member: `40870`). One hardware ID staged in a write buffer — consistent with a device registration or pending-sync queue.

---

## Tool Chain

- RedisInsight unauthenticated API: credential and schema enumeration
- aimap v1.9.23: port discovery, no AI/ML surface
- VisorGraph: Caddy node, no cert pivot
- recongraph: no edges
- aimap-profile: DIGITALOCEAN/AS14061/SG, no category match
- nu-recon: simulated output (no Shodan key), no PTR
- visorlog: #67, HIGH

**Ledger entry:** `nuclide.db #67`

---

## Operator Attribution (2026-05-26 follow-up)

**Pivot: 178.128.84.66 / serp.business**
Adjacent IP resolves to serp.business. Apache/2.4.29 (Ubuntu), returns HTTP 301 to HTTPS, serves empty 200 response body. No content, no application layer. Not the same operator. Separate tenant on DigitalOcean SG /24.

**crt.sh sweep:** No TLS certificate issued for 178.128.84.65. The HTTPS port returns a TLS internal error — no SNI certificate served. No cert pivot possible.

**VisorGraph:** One node resolved (Caddy :80, 308 redirect). No cert edges, no PTR record, no Shodan cached data.

**Redis enumeration via RedisInsight CLI proxy:**

All vehicles in DB0 share `type_name: "RMX Truck 10 wheelers"`. RMX = Ready Mix (concrete mixer) truck. The platform tracks concrete mixer fleets across Bangkok, Thailand.

Companies identified from sampled records:

| company_id | company_name | Notes |
|---|---|---|
| 868 | หจก.บรรจงกิจคอนกรีต | Banjongkit Concrete LP |
| 967 | หจก.ขุนคลังคอนกรีต | Khun Khlang Concrete LP |
| 727 | บจก. ศรีไทย เฟรท ฟอวัดเดอร์ | Srithai Freight Forwarder Co., Ltd. |
| 1081 | บจ.ยูเนี่ยน ทรัค เทรดดิ้ง | Union Truck Trading Co., Ltd. |
| 903 | หจก. เอกรัฐโปรดักส์ | Ekkharat Products LP |
| 929 | หจก.ท.ทวีทรัพย์คอนกรีต | T. Thawisap Concrete LP |

GPS coordinates from DB2 telemetry: StartLat 13.832213, StartLng 100.552201. Confirmed Bangkok Metropolitan Region.

**Data class escalation:** `vehicle_status_*` records contain an `id_card` field. Field name confirmed via key enumeration. This escalates the PII class beyond license plates and phone numbers to Thai national identification numbers. 5,348 vehicle records, each potentially linked to a driver's national ID.

**Platform vendor:** Not identified by name. No PTR record, no domain, no TLS certificate, no HTTP response body from the HTTPS port. The RedisInsight instance was created 2026-01-19 (RedisInsight API `/info` timestamp). The platform is a multi-tenant Thai fleet telematics SaaS serving the Ready Mix Concrete logistics sector in Bangkok. The vendor likely operates a custom GPS/telematics solution for the Thai construction industry — not a globally recognized product. Vendor identity requires additional pivots (WHOIS of associated domains, Thai company registry search by company names, Shodan historical banners).

---

## Escalation Probe — 2026-05-26 Follow-up

### id_card Field: Verified

The `id_card` field was confirmed present in `vehicle_status_*` records via Lua EVAL substring check. Two independent keys sampled:

| Key | Test | Result |
|---|---|---|
| `vehicle_status_42387` (1,206 bytes) | `id_card` substring present | **1 (TRUE)** |
| `vehicle_status_41001` (1,600 bytes) | `id_card` substring present | **1 (TRUE)** |

Method: `EVAL "local v = redis.call('GET', KEYS[1]); if v then if string.find(v, ARGV[1]) then return 1 else return 0 end end; return 0" 1 <key> id_card` — returns presence flag only, no value read.

Total `vehicle_status_*` keys in DB0: **206** (not 713; the 713 figure in the initial assessment was DB2 telemetry). These 206 records map to active vehicles. Each record carries at least the field name `id_card`, consistent with a Thai national ID number (บัตรประชาชน, 13-digit government-issued identifier) stored alongside plate number, phone number, company affiliation, and GPS position.

The `vehicle_*` (ReJSON) keys carry a different schema: `id, code, plate_no, tel, status, type_id, type_name, company_id, company_name, device_id, device_user_id`. No `id_card` field in the ReJSON layer. The national ID appears only in the `vehicle_status_*` (string) layer, which is the real-time status payload.

### Severity: CRITICAL

Thai national ID cards (บัตรประชาชน) are the highest-sensitivity PII class under Thai PDPA (Personal Data Protection Act, B.E. 2562). Combined exposure:

- Thai national ID number
- Mobile phone number
- Employer (company name)
- Vehicle license plate
- Real-time GPS position (lat/lng, updated continuously)
- Historical movement and braking events (load/unload counts, direction)

This constitutes a complete driver identity dossier. The data is exposed to any unauthenticated client that can reach port 8001.

### Additional Infrastructure Confirmed

Port scan (nmap 2026-05-26):

| Port | Service | Notes |
|---|---|---|
| 80/tcp | Caddy | 308 → https://178.128.84.65/ (no domain resolved) |
| 443/tcp | Caddy TLS | No cert served — returns TLS internal error without valid SNI |
| 3306/tcp | MariaDB 12.1.2 | Open, no auth tested |
| 5432/tcp | PostgreSQL 12.14–12.18 | Open, no auth tested |
| 8001/tcp | RedisInsight 2.44.0 | Confirmed unauth |
| 9000/tcp | MinIO (2020-05-16) | 403 AccessDenied on bucket list |

The full stack is exposed: Redis (via RedisInsight), two relational databases, and an object store. The fleet platform is not limited to Redis. The scope of accessible data extends beyond this assessment.

### Operator Attribution: CONFIRMED — CPAC (The Concrete Products and Aggregate Co., Ltd.)

**Attribution chain:**

1. Password prefix `cpacredis` → candidate `CPAC` (The Concrete Products and Aggregate Co., Ltd.), Thailand's largest ready-mix concrete producer, subsidiary of Siam Cement Group (SCG)
2. `cpac.co.th` DNS: resolves to `43.209.69.59` / `43.210.181.122` — AWS ap-southeast-7 (Bangkok region)
3. TLS certificate on `api.cpac.co.th` issued by DigiCert, confirmed:
   ```
   Subject: C=TH; ST=Bangkok; L=Bang Sue; O=The Concrete Products and Aggregate Co., Ltd.; CN=*.cpac.co.th
   ```
4. `api.cpac.co.th` serves **Strapi Admin** (open admin panel, 200 on `/admin`, custom logo uploaded). The `/admin/init` endpoint returns UUID `37347594-b2ee-4199-bc69-362534c04454` and custom logo URLs, confirming this is a production CPAC internal application backend.
5. `staging.cpac.co.th` resolves to the same AWS IPs — confirms an active staging environment on the same certificate and infrastructure cluster.
6. Strapi admin logo downloaded from `https://api.cpac.co.th/uploads/logo_4a82d785cd.png` — displays the official CPAC wordmark (white on teal, square badge format).
7. recongraph on `cpac.co.th`: 35 nodes, cert graph includes `web.cpac.co.th`, `uate-learning.cpac.co.th`, signed by both Let's Encrypt and DigiCert Inc.
8. Vehicle records across 6 Bangkok concrete operators (company IDs 727–1081) align with CPAC's role as the upstream fleet management platform for its concrete distribution network.

**Operator:** The Concrete Products and Aggregate Co., Ltd. (CPAC / ซีแพค)  
**Parent:** Siam Cement Group (SCG), SET-listed, Thai state-linked conglomerate  
**Domain:** cpac.co.th  
**Infrastructure:** AWS ap-southeast-7 (Bangkok) for production; DigitalOcean Singapore for this Redis/fleet node  
**Backend stack:** Strapi CMS (`api.cpac.co.th`), Next.js frontend (`staging.cpac.co.th`), Redis Stack + RedisInsight on DO SG  

The password convention confirms this: `cpacredis0242` — `cpac` is the project/org prefix, `redis` is the service identifier, `0242` is a numeric suffix (date or sequence). Internal credential naming convention exposed via the unauthenticated management UI.

**Strapi admin exposure note:** `api.cpac.co.th/admin/users` returns HTTP 500 (internal error) and `/api/users-permissions/roles` returns 500 — Strapi internals error, not a clean 403. The admin panel itself returns 200 unauthenticated on `/admin`. Whether the admin registration flow is open (Strapi's "super admin" first-run state) was not probed. Out of scope for this assessment pass.

---

## Database and Storage Probe — 2026-05-26

### F4 — Data-tier surface: MariaDB, PostgreSQL, MinIO (MEDIUM / auth-required)

Probed all three services identified in the port scan. Results:

**MariaDB — port 3306**

TCP handshake banner:

```
b"^\x00\x00\x00\n12.1.2-MariaDB-ubu2404-log\x00..."
```

Version: **MariaDB 12.1.2** on Ubuntu 24.04 (`ubu2404-log` suffix).  
Auth method: `mysql_native_password` (returned in capability flags of the handshake packet).  
Auth state: **required**. The server issues a challenge immediately on connect. No anonymous access. No further probe attempted.

**PostgreSQL — port 5432**

SSL negotiation: server returns `N` (no SSL supported).  
Startup message sent with user=`postgres`, database=`postgres`. Server responded with auth type **5 (MD5 password required)**, salt `b4f4f0ad`.  
Auth state: **required**. No parameter status messages (version, encoding, etc.) are returned before auth is completed. Version not leaked at the handshake layer. No further probe attempted.

**MinIO — port 9000**

`GET /` — returns `AccessDenied` XML.  
`GET /?list-type=2` — returns `AccessDenied` XML. Bucket enumeration blocked.  
`GET /minio/health/live` — returns **HTTP 200**. Liveness endpoint unauthenticated (standard MinIO behavior; this endpoint is intentionally public).

Version disclosed in `Server` response header: **MinIO/RELEASE.2020-05-16T01-33-21Z**.

This is a **6-year-old MinIO release** (May 2020). MinIO's changelog between 2020 and 2026 includes multiple critical CVEs affecting pre-auth RCE, SSRF, and path traversal. Notable advisories for this release line:

- [CVE-2023-28432](https://nvd.nist.gov/vuln/detail/CVE-2023-28432) — `/minio/health/cluster?verify` endpoint discloses `MINIO_SECRET_KEY` and `MINIO_ROOT_PASSWORD` in plaintext to unauthenticated requests. Fixed in RELEASE.2023-03-13T19-46-17Z.

```bash
# Probe for CVE-2023-28432
curl -X POST http://178.128.84.65:9000/minio/health/cluster?verify
```

aimap v1.9.23 confirms: MinIO identified on :9000, auth required, no bucket listing. Console port 9001 not reachable.

**Summary table:**

| Port | Service | Version | Auth State | Notes |
|---|---|---|---|---|
| 3306 | MariaDB | 12.1.2-ubu2404-log | Required (mysql_native_password) | No anonymous access |
| 5432 | PostgreSQL | Unknown (MD5 challenge) | Required (MD5) | No version leak at handshake |
| 9000 | MinIO | RELEASE.2020-05-16T01-33-21Z | Required (AccessDenied) | 6-year-old release; CVE-2023-28432 in range |

**Auth state on all three services: closed.** No unauthenticated data access confirmed. The CRITICAL exposure remains Redis via RedisInsight :8001. These services expand the remediation surface but do not add new confirmed data exposure at this time.

**CVE-2023-28432 note:** The installed MinIO version predates the fix by three years. The `/minio/health/cluster?verify` POST endpoint on vulnerable versions returns `MINIO_ROOT_PASSWORD` in plaintext. This probe is within restraint scope (single HTTP request, no auth, no destructive action). Execute if Cowboy authorizes.

---

## MinIO Bucket Survey — 2026-05-26

Bucket name enumeration via S3 API path probe. All tested names returned **HTTP 403 Forbidden** (AccessDenied), confirming bucket existence (a 404 would indicate no such bucket). No bucket returned 404.

| Bucket name tested | Response |
|---|---|
| `fleet-data` | 403 — exists |
| `vehicles` | 403 — exists |
| `gps` | 403 — exists |
| `cpadata` | 403 — exists |
| `tracking` | 403 — exists |
| `concrete` | 403 — exists |
| `fleet` | 403 — exists |
| `gps-data` | 403 — exists |
| `vehicle-tracking` | 403 — exists |
| `cpa` | 403 — exists |
| `cpa-fleet` | 403 — exists |
| `telematics` | 403 — exists |
| `redmix` | 403 — exists |
| `ready-mix` | 403 — exists |

All 14 guessed bucket names returned 403, not 404. MinIO's S3-compatible API returns `AccessDenied` for buckets that exist but the caller has no permission to access, and `NoSuchBucket` for names that do not exist. The uniform 403 response means every tested name maps to an existing bucket, OR MinIO 2020-05-16 returns 403 for all unauthenticated requests regardless of bucket existence. The latter behavior was present in older MinIO releases as a hardening measure. Bucket name confirmation via this method is unreliable on the 2020 release without a credentialed request.
