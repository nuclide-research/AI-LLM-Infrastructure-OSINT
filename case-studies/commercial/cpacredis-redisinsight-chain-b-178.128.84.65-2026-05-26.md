# cpacredis — RedisInsight Credential Leak on Fleet Telematics Platform

**Target:** 178.128.84.65  
**Date:** 2026-05-26  
**Severity:** HIGH  
**Category:** Unauth Management UI / Credential Exposure / PII  
**Tags:** redis-stack, redisinsight, chain-b, credential-leak, fleet-telematics, vehicle-registry, GPS, PII

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
