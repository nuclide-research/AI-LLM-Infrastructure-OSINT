---
type: insight
number: 60
title: "Redis Stack FT._LIST as Vector-Tier Enumeration Primitive"
date: 2026-05-25
survey: redis-stack-redisinsight-population-survey-2026-05-25
applies-to: [Redis Stack, RediSearch, RedisInsight]
---

# Insight #60 — Redis Stack FT._LIST as Vector-Tier Enumeration Primitive

**Date:** 2026-05-25  
**Survey anchor:** Redis Stack / RedisInsight population survey (2026-05-25)

---

## The Finding

Redis Stack does not change the auth posture of Redis. Auth-on-default is off for Redis Stack exactly as it is for plain Redis. "Redis Stack" in the Shodan banner is not evidence that authentication is configured.

78 of 78 Redis Stack hosts in the survey corpus answered `+PONG` to a RESP PING with no AUTH. Auth-on-default: 0%. This is the same rate observed in every prior Redis survey.

---

## The New Primitive

Redis Stack adds RediSearch, which introduces three new enumeration commands that plain Redis does not have:

| Command | Result |
|---|---|
| `FT._LIST` | Returns all active search index names |
| `FT.INFO <index>` | Returns schema: field names, types, vector dimensions, distance metric |
| `FT.SEARCH <index> * LIMIT 0 N` | Returns all records up to N |

`FT._LIST` is the stage-2 enumeration step after a PING confirms no auth. It reveals whether the Redis instance is a plain cache or a vector search layer with an indexed corpus. An empty FT._LIST response means no vector indexes. A non-empty response names the data — `idx:vehicle`, `account:index`, `conversation:index` — before a single record is read.

`FT.INFO <index>` returns the schema without reading data. This is the restraint-safe confirmation step: the schema confirms the data class (PII fields, conversation fields, LDAP fields) without exfiltrating records.

---

## Two Finding Classes

The survey corpus splits into two distinct classes:

**AI-adjacent:** Redis Stack as the vector search backend for an LLM application. The FT indexes contain conversation history, user accounts, or embedded documents. Example: Vietnamese AI chatbot CRM (125.212.227.37) with 17,377 conversation records across FT indexes `account:index` and `conversation:index`.

**Non-AI:** Redis Stack adopted for its search capabilities in a non-LLM workload. The FT indexes contain operational data — fleet tracking, ERP cache, session stores. Example: Simón Movilidad (190.217.28.217) with 28,323 vehicle fleet records in `idx:vehicle`, `idx:user`, `idx:company`.

Both classes are vulnerable to the same probe chain. The data class is not visible from the Shodan banner — it requires FT._LIST + FT.INFO.

---

## The RedisInsight Surface

`http.title:"RedisInsight"` is a clean dork. 70 of 79 harvested RedisInsight hosts answered HTTP 200 on port 8001 with the RedisInsight UI, no auth required. RedisInsight is the official Redis GUI: it provides a browser-based key browser, FT index inspector, query executor, and bulk export. An open RedisInsight on port 8001 is a higher-severity finding than an open Redis RESP port on 6379, because the GUI surfaces the data with zero tooling and makes bulk export trivial.

The two dorks (`"Redis Stack" port:6379` and `http.title:"RedisInsight"`) produced 0 overlapping IPs. They are independent discovery vectors.

---

## Probe Chain

```
1. Shodan: "Redis Stack" port:6379            → Redis Stack IP list
2. Shodan: http.title:"RedisInsight"          → RedisInsight GUI IP list
3. TCP RESP PING                              → auth state confirmation
4. FT._LIST                                  → index inventory (names only)
5. FT.INFO <index>                           → schema (fields, types) — no data read
6. DBSIZE                                    → record count
7. FT.SEARCH <index> * LIMIT 0 1 RETURN 0   → key count without data
```

Step 5 is the restraint stop. Schema + DBSIZE + key count establishes severity and data class. Record content is only sampled when the schema alone is insufficient to classify severity.

---

## Codified Rule

> **A Redis Stack host that answers PONG is unauthenticated.** Run FT._LIST to confirm it is a vector tier, not a plain cache. Run FT.INFO to read the schema. The schema names the data class. The data class determines severity. Do not read record content until schema alone is insufficient to establish severity.

---

## aimap Gap

Redis Stack fingerprinting is in aimap. The `enumRedis` enumerator does not yet run FT._LIST + FT.INFO as dedicated steps. Adding FT._LIST to the Redis Stack enumeration path would surface the vector-index inventory for every confirmed Redis Stack instance.

**Candidate enhancement:** `enumRedisStack` (separate from generic `enumRedis`) that runs PING → DBSIZE → FT._LIST → FT.INFO per index → returns index names and field schemas as structured output.

---

## Survey Stats

| Metric | Value |
|---|---|
| Harvest: Redis Stack | 78 IPs (673 total, account-limited) |
| Harvest: RedisInsight | 79 IPs |
| Overlap | 0 |
| Auth-on-default (Redis Stack) | 0% (78/78 unauthenticated) |
| Auth-on-default (RedisInsight) | 11% closed/filtered (70/79 open) |
| Records confirmed in top 4 hosts | 53,704 |
| Distinct data classes | 4 (fleet, CRM/AI, ERP cache, session store) |
