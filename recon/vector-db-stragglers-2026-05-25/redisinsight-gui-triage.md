# RedisInsight GUI Corpus Triage — 2026-05-25

Generated: 2026-05-26 (sweep run 2026-05-26)

## Summary

- 79 IPs probed
- **27** instances responded to /api/databases
- **0** AI-adjacent database name labels (all default "My Redis Stack Database")
- **1** named production database (CMS-Prod-Redis-DB)
- **1** n8n workflow automation Redis connection (AI-adjacent by platform)
- **7** instances with plaintext Redis passwords leaked via /api/databases metadata
- **15** co-located Redis instances (port 6379 open on same host)
- **52** IPs silent at time of sweep (population churn since 2026-05-25 confirmation)

Key finding: RedisInsight /api/databases returns the `password` field in plaintext for any
configured Redis connection. Seven of 27 responsive instances leaked Redis auth credentials
directly in the GUI metadata API response -- no key reads required.

---

## Elevated Findings

### 35.210.76.182 -- CMS-Prod-Redis-DB + credential leak (HIGHEST PRIORITY)
- **Database name:** CMS-Prod-Redis-DB
- **Username:** default
- **Password:** D3v_R3dis_P4ss (plaintext in /api/databases response)
- **RedisInsight version:** 2.36.0
- **Modules:** search 2.8.9, ReJSON 2.6.7, timeseries 1.10.9, redisgears_2, bf 2.6.8
- **Redis version:** 7.2.3
- **Last connection:** 2026-05-24T06:23:31Z (active -- used within 48h of sweep)
- **Co-located Redis (6379):** yes
- **Notes:** Named "Prod" + named "CMS" (content management system). Active connection.
  The password label ("D3v_R3dis_P4ss") contains "Dev" but the database is named "Prod" --
  suggests a dev-env credential was applied to a production-labeled instance.
  RedisInsight GUI itself has no auth. The Redis password is only protection on the data layer,
  and it is now exposed to anyone who hits port 8001.

### 192.169.81.2 -- n8n workflow automation Redis
- **Database name:** n8n-redis-1:6379
- **Host (configured):** n8n-redis-1 (Docker container name)
- **Database index:** 0
- **Redis version:** 7.4.7
- **Last connection:** 2026-02-27T15:17:07Z
- **RedisInsight version:** 2.42.0
- **No password configured in GUI**
- **Co-located Redis (6379):** yes
- **Notes:** n8n is a workflow automation platform with LLM/AI integrations (OpenAI, LangChain,
  Anthropic nodes). The Docker hostname "n8n-redis-1" confirms this is the backing Redis for
  an n8n deployment. Redis appears unauth (no password in metadata). n8n uses Redis for
  queue-mode execution -- this instance likely holds job queues, workflow execution state,
  and potentially webhook payloads.

### 116.203.208.124 -- credential leak, Redis search modules
- **Password:** anKdQDSPUaK3iQpy0D5VlWwaO2ex2SPK05eSQPryGHNcBNvUWjeK2GqbAzcO (60 chars, plaintext)
- **Provider:** LOCALHOST
- **Modules:** search 2.6.9, graph 2.10.10, ReJSON 2.4.7, timeseries 1.8.10, bf 2.4.5
- **Last connection:** 2026-05-19T01:52:34Z
- **RedisInsight version:** 2.22.0
- **Notes:** Full Redis Stack with search module. 60-char password suggests generated cred;
  it is now fully exposed via the unauth GUI API.

### 150.230.235.79 -- credential leak, active (last conn day of survey)
- **Username:** default / **Password:** Zarv1ce (plaintext)
- **Modules:** graph 2.10.12, search 2.6.12, ReJSON 2.4.7, timeseries 1.8.11, bf 2.4.5
- **Redis version:** 6.2.13
- **Last connection:** 2026-05-25T12:39:30Z (active -- connected day of survey)
- **RedisInsight version:** 2.28.0
- **Co-located Redis (6379):** yes
- **Notes:** Active connection. Simple password "Zarv1ce" -- low entropy. Full Redis Stack.

### 178.128.84.65 -- credential leak, label "cpacredis"
- **Password:** cpacredis0242 (plaintext)
- **Modules:** redisgears_2, bf 2.6.12, search 2.8.13, timeseries 1.10.12, ReJSON 2.6.10
- **Redis version:** 7.2.4
- **Last connection:** 2026-05-19T13:13:08Z
- **RedisInsight version:** 2.44.0
- **Notes:** Password prefix "cpacredis" suggests CPA (accounting/financial professional) context.
  Accounting/financial data in Redis would be high-value.

### 31.129.97.101 -- credential leak
- **Password:** Sq3QmHxJCPn5Dt4LzAaNRg (22 chars, base62-style)
- **Modules:** timeseries 1.10.12, redisgears_2, ReJSON 2.6.10, search 2.8.13, bf 2.6.12
- **Redis version:** 7.2.4
- **Last connection:** 2026-05-04T09:46:54Z
- **RedisInsight version:** 2.44.0

### 88.99.245.120 -- credential leak, active
- **Username:** default / **Password:** SFr3d1s!2026xKv (plaintext)
- **Modules:** timeseries 1.8.11, ReJSON 2.4.7, graph 2.10.12, search 2.6.12, bf 2.4.5
- **Redis version:** 6.2.13
- **Last connection:** 2026-05-13T05:37:39Z
- **RedisInsight version:** 2.28.0
- **Notes:** Password "SFr3d1s!2026xKv" follows "Redis + year" pattern -- set in 2026.

### 65.21.151.67 -- credential leak
- **Password:** 3snMjYZPiNDzvNWm (16 chars)
- **Modules:** timeseries 1.10.11, search 2.8.12, redisgears_2, ReJSON 2.6.9, bf 2.6.12
- **Redis version:** 7.2.4
- **Last connection:** 2026-04-18T00:36:07Z
- **RedisInsight version:** 2.44.0

---

## Pattern: /api/databases Leaks Redis Credentials

RedisInsight stores Redis connection credentials in its local database and returns them
in the /api/databases API response -- including the `password` field in plaintext. When
RedisInsight itself has no authentication (the default on Docker deployments), this means:

**Unauthenticated HTTP GET -> plaintext Redis password for any configured connection.**

7 of 27 responsive instances (26%) had passwords in the metadata. The other 20 either
use passwordless Redis (no auth configured) or the password was not stored in RedisInsight.

This is a credential exposure class at the GUI layer, not just a Redis misconfiguration.
The Redis ACL password is the operator's intended security control -- the unauth GUI
defeats it entirely.

---

## Module Distribution (27 responsive instances)

Most instances run full Redis Stack:
- `search` (RediSearch / vector search): 19 instances
- `ReJSON`: 19 instances
- `timeseries`: 19 instances
- `bf` (Bloom Filter): 18 instances
- `graph` (RedisGraph): 11 instances
- `redisgears_2`: 8 instances

The `search` module enables vector similarity search. Operator context (AI/ML vs. general app)
cannot be determined from connection metadata alone without key inspection.

---

## Full Results Table

| IP | Database Name | RI Version | Password Exposed | 6379 | Last Connection |
|---|---|---|---|---|---|
| 20.96.25.235 | My Redis Stack Database | 2.32.0 | no | yes | 2026-05-20 |
| 31.129.97.101 | My Redis Stack Database | 2.44.0 | YES | no | 2026-05-04 |
| 34.72.166.211 | My Redis Stack Database | 2.28.0 | no | yes | 2026-05-18 |
| 35.210.76.182 | CMS-Prod-Redis-DB | 2.36.0 | YES | yes | 2026-05-24 |
| 35.240.166.119 | My Redis Stack Database | 2.0.0 | no | no | 2026-05-18 |
| 51.8.42.171 | My Redis Stack Database | 2.44.0 | no | no | (never) |
| 63.142.240.198 | My Redis Stack Database | 2.22.0 | no | no | (never) |
| 65.21.151.67 | My Redis Stack Database | 2.44.0 | YES | yes | 2026-04-18 |
| 79.133.180.209 | My Redis Stack Database | 2.40.0 | no | no | (never) |
| 88.99.245.120 | My Redis Stack Database | 2.28.0 | YES | yes | 2026-05-13 |
| 91.239.233.126 | My Redis Stack Database | 2.44.0 | no | no | (never) |
| 95.211.86.110 | My Redis Stack Database | 2.22.0 | no | no | (never) |
| 110.42.222.188 | My Redis Stack Database | 2.20.0 | no | no | (never) |
| 116.203.208.124 | My Redis Stack Database | 2.22.0 | YES (60 char) | yes | 2026-05-19 |
| 117.72.55.156 | My Redis Stack Database | 2.44.0 | no | no | (never) |
| 120.24.222.54 | My Redis Stack Database | 2.28.0 | no | yes | 2026-05-26 |
| 129.159.241.26 | My Redis Stack Database | 2.22.0 | no | yes | 2026-04-30 |
| 134.255.232.102 | My Redis Stack Database | 2.44.0 | no | no | (never) |
| 138.201.188.81 | My Redis Stack Database | 2.0.0 | no | no | (never) |
| 139.186.223.243 | My Redis Stack Database | 2.0.0 | no | no | (never) |
| 150.230.235.79 | My Redis Stack Database | 2.28.0 | YES | yes | 2026-05-25 |
| 168.119.228.180 | My Redis Stack Database | 2.28.0 | no | no | (never) |
| 172.105.158.109 | My Redis Stack Database | 2.36.0 | no | no | (never) |
| 178.128.84.65 | My Redis Stack Database | 2.44.0 | YES (cpacredis) | yes | 2026-05-19 |
| 178.128.121.171 | (none configured) | unknown | no | yes | -- |
| 192.169.81.2 | n8n-redis-1:6379 | 2.42.0 | no | yes | 2026-02-27 |
| 194.56.188.19 | My Redis Stack Database | 2.44.0 | no | yes | 2026-05-20 |

---

## Non-Responsive IPs (52 of 79)

Population churn: 52 IPs confirmed open on 2026-05-25 did not respond during this sweep.
Likely causes: short-lived VPS/container deployments, dynamic IP reassignment, firewall changes.

106.14.238.211, 110.42.225.77, 113.125.8.24, 128.32.175.60, 130.61.25.186,
133.125.64.37, 133.125.64.39, 137.66.56.174, 138.197.90.230, 139.144.57.95,
139.196.141.236, 143.198.110.42, 143.244.178.122, 147.93.179.153, 152.53.32.44,
167.172.23.92, 168.119.124.37, 172.245.184.83, 178.236.17.217, 180.93.43.47,
185.35.222.213, 188.166.25.64, 206.189.193.100, 213.199.37.9, 216.167.200.86,
217.12.38.58, 23.109.158.196, 24.199.78.236, 34.133.89.189, 34.47.159.30,
39.107.70.89, 4.255.168.209, 43.200.196.147, 45.85.146.180, 47.114.127.164,
5.161.210.10, 51.250.17.142, 52.49.64.247, 54.116.78.202, 54.78.165.31,
62.171.177.173, 62.72.42.172, 66.94.125.138, 70.34.205.131, 8.140.226.10,
8.140.255.242, 84.247.141.32, 85.214.241.254, 88.99.80.38, 91.107.231.141,
95.216.37.181

---

## Case Study Candidates

### 35.210.76.182 -- CMS-Prod-Redis-DB
Named production database + plaintext credential + RedisInsight unauth + active connection
(2026-05-24). The "CMS-Prod" label, active timestamp, and exposed password make this the
clearest single-host finding in the corpus. The password "D3v_R3dis_P4ss" contains "Dev"
while the label says "Prod" -- credential/environment mismatch. Case study warranted.

### 192.169.81.2 -- n8n workflow automation
n8n-connected Redis with no password in metadata. n8n queue-mode uses Redis as the job
broker. If Redis is unauth, the queue and workflow state are directly accessible.
Pivot: check port 5678 (n8n web UI default) on same host for unauth n8n installation.

### 178.128.84.65 -- "cpacredis" label
Password prefix suggests CPA/accounting context. "cpacredis0242" -- if this Redis backs
an accounting SaaS, data class could include financial records. Credential now exposed.

---

## Pivot Avenues

1. **Port 5678 on 192.169.81.2** -- check for unauth n8n web UI on the n8n-redis host
2. **ASN/org attribution on 35.210.76.182** -- identify the CMS operator behind the prod instance
3. **Reverse cert pivot on 178.128.84.65** -- "cpacredis" label may correlate with a CPA SaaS
   brand via TLS CN sweep
4. **Re-sweep the 52 silent IPs in 24h** -- short-lived containers often return; catch the
   redeployment window
5. **Version cohort: v2.0.0 instances** -- 138.201.188.81, 139.186.223.243, 35.240.166.119
   are 2+ years behind current -- unpatched GUI surface
6. **Key-count probe (deferred)** -- all 19 instances with `search` module have vector search
   capability; data class requires keyspace scan which is out of scope for this triage pass
