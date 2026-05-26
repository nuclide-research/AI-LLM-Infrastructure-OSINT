---
type: insight
number: 61
title: "RedisInsight /api/databases Returns Redis Passwords in Plaintext"
date: 2026-05-26
survey: redis-stack-redisinsight-population-survey-2026-05-25
applies-to: [RedisInsight, Redis Stack]
---

# Insight #61 — RedisInsight /api/databases Returns Redis Passwords in Plaintext

**Date:** 2026-05-26  
**Survey anchor:** Redis Stack / RedisInsight population survey (2026-05-25)

---

## The Finding

RedisInsight stores Redis connection configurations in a local database. The REST API at `/api/databases` (port 8001) returns those configurations with the `password` field in plaintext. No authentication on the GET request. No credentials required to call the endpoint.

```
GET http://<ip>:8001/api/databases

[
  {
    "id": "...",
    "name": "CMS-Prod-Redis-DB",
    "host": "localhost",
    "port": 6379,
    "username": "default",
    "password": "D3v_R3dis_P4ss",
    ...
  }
]
```

7 of 27 responsive instances in the corpus (26%) returned Redis AUTH credentials via this endpoint.

---

## Severity Upgrade

The original assessment of open RedisInsight instances was: **higher severity than open Redis on 6379** because the GUI enables data browsing and bulk export with zero tooling.

This finding adds a second severity class: **open RedisInsight strips Redis ACL password protection** by exposing the credential in metadata. The finding applies even when the Redis instance itself enforces AUTH.

Two distinct exposure chains:

| Chain | Prerequisite | Result |
|---|---|---|
| Chain A | Redis port 6379 open, no auth | Direct data access via RESP |
| Chain B | RedisInsight port 8001 open, no auth | Credential exposed via /api/databases → use it against Redis |

Chain B reaches Redis instances that have AUTH configured. Chain A does not.

---

## Probe Chain Addition

```
1. Shodan: http.title:"RedisInsight"         → RedisInsight GUI IP list
2. HTTP GET :<port>/api/databases            → connection metadata + password field
3. HTTP GET :<port>/api/info                 → RedisInsight version
4. If password present: confirm Redis connection using returned credentials
5. FT._LIST → FT.INFO → DBSIZE              → data class + severity
```

Step 4 uses a returned credential — this is credential confirmation against the issuing system, not a brute-force attempt.

---

## Corpus Results (2026-05-26 sweep)

| Metric | Value |
|---|---|
| IPs probed | 79 |
| Instances responded | 27 |
| Credential leaks via /api/databases | 7 (26%) |
| Co-located Redis on 6379 | 15 |
| n8n AI-adjacent connection confirmed | 1 |
| Named production database | 1 (CMS-Prod-Redis-DB) |
| RediSearch module present | 19 of 27 |

---

## aimap Gap

The `enumRedisInsight` enumerator does not call `/api/databases`. It checks the HTTP surface but does not retrieve connection metadata or parse the password field.

**Candidate enhancement:** Add `/api/databases` to the RedisInsight enumerator. Parse the `password`, `host`, `port`, `name` fields. If a password is present, flag as credential leak. If a host is present that differs from the scanned host, add it to the adjacent-host queue.

---

## Codified Rule

> **An open RedisInsight instance is two findings, not one.** First: GUI access with bulk export. Second: `/api/databases` may expose Redis AUTH credentials in plaintext, defeating password protection on the data layer. Call both endpoints. The credential leak is the higher-severity finding when present.

---

**See also:** [Insight #60 — Redis Stack FT._LIST as Vector-Tier Enumeration Primitive](insight-60-redis-stack-ft-list-vector-tier-enumeration.md) · [Redis Stack / RedisInsight Population Survey (2026-05-25)](../case-studies/commercial/redis-stack-redisinsight-population-survey-2026-05-25.md)
