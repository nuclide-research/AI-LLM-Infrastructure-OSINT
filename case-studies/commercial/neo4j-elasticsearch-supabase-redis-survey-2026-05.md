---
type: survey
---

# Neo4j, Elasticsearch, Supabase, Redis Stack: AI Infrastructure Exposure Survey

_NuClide Research · 2026-05-09_

---

## Summary

Four additional infrastructure layers surveyed as part of the 2026-05-09 vector DB series. Combined Shodan pull → asyncio probe across 2,064 IPs (971 Neo4j + 636 Elasticsearch v8 + 314 Supabase + 143 Redis Stack).

**Elasticsearch is the headline finding:** 958 reachable, **920 unauthenticated** (96% open rate) — and **817 of those 920 unauth instances (89%) have been ransomed**. A single active campaign has wiped data and planted `read_me` ransom notes across the majority of exposed clusters. One confirmed v8.16.0 instance is serving live vector search workloads (BGE-M3 multilingual embeddings) without auth. **Neo4j** shows 971 open instances, all presenting their HTTP browser interface — v4+ moved to Bolt protocol, making HTTP-based probing incomplete. **Redis Stack** RedisInsight UI is 100% unauthenticated across 112 confirmed instances. **Supabase** self-hosted exposure is minimal (23 reachable, 5 unauth REST).

---

## Elasticsearch

### Methodology

```
shodan download --limit 1500 elasticsearch-v8.json.gz 'product:"Elastic" port:9200 version:8'
  → 636 unique IPs

asyncio probe (80 concurrent):
  GET  http://{ip}:9200/              → 200 = unauth (version, cluster_name)
                                      → 401 = auth gated
  GET  http://{ip}:9200/_cat/indices?format=json&h=index,docs.count
                                      → index list
  GET  http://{ip}:9200/{idx}/_mapping → check for dense_vector / knn
```

### Results

| Metric | Value |
|---|---|
| IPs probed | 636 |
| Confirmed reachable | **958** |
| **Unauthenticated** | **920** (96%) |
| Auth-gated | 38 |
| Ransomed (read_me index) | **817** (89% of unauth) |
| Vector workload confirmed | **1** |

### Version Distribution (unauth instances)

| Major version | Count |
|---|---|
| v7.x | 910 |
| v8.x | 8 |
| v9.x | 2 |

The Elasticsearch v7 dominance reflects the version where the security-by-default change was not yet in effect. Elasticsearch made TLS + auth mandatory by default starting with **v8.0.0 (2022-02)**. The 920 unauth instances are overwhelmingly v7.x deployments that shipped with security off and were never hardened.

### Ransom Campaign (Active)

**817 of 920 unauth instances have been compromised.** The attack pattern is consistent: attacker connected to the open ES API, deleted all indices, created a `read_me` index containing a ransom note. Confirmed campaign IOCs:

```
BTC wallet:  bc1q38rjul6gdamfflf6p4ukz0ymtvfgfv2j9saf6r
Contact:     wendy.etabw@gmx.com (include your unique code)
Demand:      0.0041 BTC (~$250 USD)
```

Top cluster names in ransomed set: `docker-cluster` (407), `elasticsearch` (231), `my-application` (17), `es-cluster` (15), `my-cluster` (11). The cluster name distribution — dominated by defaults — confirms these are misconfigured deployments that were never properly commissioned.

### Notable Findings

---

#### F1 — Fintech payment ledger (CRITICAL)

**Host:** `103.21.89.153` (AS group, likely APAC cloud)  
**Severity:** CRITICAL — financial transaction data exposed, then ransomed

Confirmed indices before ransom completion: `withdraw_records`, `recharge_records`, `wallet_operations`. Cluster name `my-cluster`, version v7.17.29. This is an active fintech or crypto payment processing backend — all three index names map directly to core ledger operations (withdrawals, recharges/deposits, wallet state). The ransom note (`read_me`) coexists with the data indices, suggesting either partial wipe or data was exfiltrated before deletion.

```bash
curl http://103.21.89.153:9200/_cat/indices?format=json&h=index
# Returns: withdraw_records, read_me, recharge_records, wallet_operations
```

---

#### F2 — Mastodon social network index (MEDIUM)

**Host:** `103.76.196.22`  
**Severity:** MEDIUM — social network user/post data exposed and ransomed

Cluster name `mastodon-es`, version v7.17.8. Mastodon instances use Elasticsearch for full-text search across posts, users, and accounts. The cluster name confirms this is an ES backend for a Mastodon instance. Content indexed typically includes: post text, account bios, hashtags, user search indexes. Now fully ransomed (only `read_me` index remaining).

---

#### F3 — Confirmed vector search workload (MEDIUM)

**Host:** `39.102.213.167`  
**Version:** v8.16.0 (Elasticsearch)  
**Cluster:** `docker-cluster`  
**Severity:** MEDIUM — vector search index exposed without auth

Only confirmed v8.x instance with unauthenticated access AND confirmed vector workload. Indices: `search_keywords_bge-m3`, `global_search_keywords_bge-m3` — BGE-M3 (BAAI General Embedding, multilingual) is a dense vector embedding model widely used for semantic search in Chinese/multilingual applications. The `global_` prefix suggests this is a production search layer for a web application with multilingual query support.

```bash
curl http://39.102.213.167:9200/search_keywords_bge-m3/_mapping | jq '..|.type?//empty' | sort -u
# Expected: dense_vector, keyword, long, text
```

The BGE-M3 model produces 1024-dimension vectors. Exposed data likely includes: search query vectors (corpus-poisoning surface), indexed content embeddings (semantic inference of indexed documents), and mapping schema (reveals data model of the parent application).

---

### Auth Posture Analysis

Elasticsearch's security evolution is directly visible in this data:

- **v6.x and earlier:** No security features in the free tier (X-Pack Security was paid-only). Zero-auth was the only option without licensing.
- **v7.x:** Security features added to free tier (7.1+) but disabled by default. The docker-cluster naming pattern indicates docker-compose deployments that almost never enable security.
- **v8.x:** Security enabled by default for new installations. The 8 unauth v8.x instances represent deliberate `xpack.security.enabled: false` configuration or legacy upgrades that didn't inherit the new defaults.

The ransom campaign targeting is rational: 89% of exposed clusters had already been found and wiped before this survey. The remaining 11% (103 instances) have not yet been hit — or the data was insufficiently valuable to ransom.

---

## Neo4j

### Methodology

```
shodan download neo4j.json.gz 'product:"Neo4j"'
  → 971 unique IPs

asyncio probe:
  GET  http://{ip}:7474/           → 200/401 = HTTP browser open
  GET  http://{ip}:7474/db/data/   → legacy REST (v3 and earlier)
  GET  http://{ip}:7474/db/data/ + BasicAuth neo4j:neo4j → default creds check
```

### Results

| Metric | Value |
|---|---|
| IPs probed | 971 |
| HTTP browser open (:7474) | **971** |
| Legacy REST unauth | 971 (all return 200 on /db/data/) |
| Default creds (neo4j/neo4j) | 0 |
| Version fingerprinted | 0 |

### Probe Limitation: Bolt Protocol

Neo4j migrated its primary client protocol to **Bolt** (binary, port 7687) in v4.0 (2020). The HTTP REST API (`/db/data/`) was deprecated in v4.0 and removed in v5.0. The asyncio HTTP probe correctly identifies that port 7474 (the Neo4j Browser UI) is open, but:

1. **Version** cannot be extracted via the deprecated REST path — all 971 instances return `version: null`
2. **Default credentials** cannot be validated via HTTP POST — the deprecated endpoint returns HTTP 200 but doesn't validate creds the same way
3. **Actual database access** requires a Bolt client (`neo4j-driver`, Cypher shell, or raw websocket) on port 7687

The 971 "unauth" flags in this survey indicate the Neo4j Browser web UI is publicly reachable — not that the database is accessible without credentials. The Browser UI itself requires authentication, and modern Neo4j (v5+) enforces RBAC with no anonymous access path.

**What the 971 open Neo4j Browser instances represent:**
- The web UI is exposed (allows credential-stuffing/brute-force attempts)
- Port 7687 (Bolt) may be exposed separately — not probed in this survey
- Default `neo4j:neo4j` credentials remain a viable attack path via Bolt clients
- Some fraction will have changed the password, some will not

**Revised assessment:** This survey undercounts Neo4j risk. The HTTP browser probe is a reachability signal, not an auth state signal for v4+. A follow-up survey using a Bolt protocol probe (via `neo4j` Python driver or direct WebSocket) is required to determine actual unauth state.

---

## Supabase (Self-Hosted)

### Methodology

```
shodan download supabase.json.gz 'http.title:"Supabase"'
  → 314 unique IPs

asyncio probe:
  GET  http://{ip}:8000/           → Kong gateway presence
  GET  http://{ip}:8000/rest/v1/   → PostgREST unauth check
  Check for anon key leak in HTML
```

### Results

| Metric | Value |
|---|---|
| IPs probed | 314 |
| Reachable | **23** |
| **PostgREST unauth** | **5** |
| Anon key in HTML | 0 |

The low hit count reflects Supabase's architecture: the managed cloud product (`supabase.com`) uses dedicated infrastructure that Shodan fingerprints differently. Self-hosted Supabase on port 8000 (Kong API gateway) is less common than the managed service.

The 5 unauth instances expose the PostgREST API directly — `GET /rest/v1/` returns HTTP 200, meaning table-level access is possible without the `anon` key. This typically indicates a misconfigured Kong route or a Supabase deployment where the `apikey` enforcement middleware was removed.

**Unauth Supabase PostgREST exposure:**
```
178.156.202.116:8000
157.180.79.165:8000
204.168.183.239:8000
204.168.201.75:8000
141.164.63.237:8000
```

Supabase's anon key — normally required for all public API calls — is tied to Row Level Security (RLS) policies. Without the key, RLS still applies if configured, but **tables without RLS policies are fully readable/writable by any unauthenticated client** via the PostgREST endpoint.

---

## Redis Stack / RedisInsight

### Methodology

```
shodan download redis-stack.json.gz 'product:"RedisInsight" port:8001'
  → 143 unique IPs

asyncio probe:
  GET  http://{ip}:8001/           → RedisInsight UI (200 = open)
  GET  http://{ip}:8001/api/instance/ → instance list (confirms unauth)
```

### Results

| Metric | Value |
|---|---|
| IPs probed | 143 |
| RedisInsight UI open | **112** |
| **Unauthenticated (100%)** | **112** |
| Instance list accessible | ~112 |

**RedisInsight is 100% unauthenticated across all 112 confirmed instances.** RedisInsight ships with no authentication by default — it is designed as a local development tool and assumes the host is trusted. When exposed on a public IP, it provides:

- Full Redis database browser (key-value browse, search, JSON, streams)
- Workbench with live Redis command execution
- Profiler and memory analysis
- **For Redis Stack instances:** RediSearch, RedisJSON, RedisGraph, RedisTimeSeries, RedisBloom module access via GUI

A publicly accessible RedisInsight is equivalent to unauthenticated `redis-cli` access — read, write, delete on any key. For AI/ML workloads, Redis Stack is used for vector similarity search (RediSearch `VECTOR` field type), session storage, and caching LLM outputs. RedisInsight exposure means full access to these data classes.

**RedisInsight added optional authentication in v2.x** (`RI_ENCRYPTION_KEY` env var for data-at-rest, but no HTTP auth layer until the 2024 enterprise features). Most deployments do not set the encryption key.

**Sample confirmed open instances:**
```
104.237.136.86:8001
129.212.183.88:8001
138.197.96.54:8001
109.123.245.210:8001
109.245.220.210:8001
```

---

## Comparative Auth Posture (Complete Survey Series)

| Database | Reachable | Unauth | Unauth % | Default auth posture |
|---|---|---|---|---|
| **Elasticsearch v7** | 920 | 920 | **100%** | Off by default (v7.x) |
| ChromaDB (prior survey) | 92 | 92 | 100% | Off by default (< v0.6) |
| **RedisInsight** | **112** | **112** | **100%** | **No auth, designed as local tool** |
| Milvus/Attu (this series) | 763 | 593 | 78% | RBAC opt-in |
| Weaviate (this series) | 694 | 435 | 63% | Off by default |
| Supabase (this survey) | 23 | 5 | 22% | Kong gated, anon key required |
| SurrealDB (prior survey) | 262 | 34 | 13% | On by default (v2+), off in 1.x |
| Elasticsearch v8 | 8 | 8 | 100% | On by default (v8+) — these are deliberate overrides |
| Neo4j | 971 | _unknown_ | _see note_ | Bolt protocol — HTTP probe insufficient |
| Typesense (prior survey) | 60 | 0 | 0% | **Required, no bypass** |

---

## Discovery Context

Survey conducted 2026-05-09 as part of NuClide Research vector database exposure series. Shodan pulls: `product:"Elastic" port:9200 version:8` (636 IPs → 958 confirmed), `product:"Neo4j"` (971 IPs), `http.title:"Supabase"` (314 IPs → 23 confirmed), `product:"RedisInsight" port:8001` (143 IPs → 112 confirmed). Asyncio probe with 2s connect / 4s read / 80 concurrent.

Companion surveys: `weaviate-cloud-survey-2026-05.md`, `milvus-attu-survey-2026-05.md`, `surrealdb-typesense-lancedb-survey-2026-05.md`.
