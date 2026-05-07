# 2. Vector Databases

_Section verified: April 30, 2026_

The storage layer for RAG, embeddings, and long-term LLM memory. Many of these ship without authentication enabled by default, exposed instances often disclose collection names, schema, embedding model, and the LLM provider keys used to generate vectors.

## ChromaDB

| Shodan Query | Notes |
|---|---|
| `"chroma"` | 2,311 hits, ⚠️ noisy; "chroma" collides with chroma-subsampling, color-correction UIs, Razer Chroma; use as last resort |
| `product:"Chroma"` | 1,838 hits, canonical product facet; sampled hits on 8000/8100 confirm vector DB |
| `product:"Chroma" port:8000` | 1,139 hits, traditional default port |
| `product:"Chroma" "uvicorn"` | 353 hits, highest-confidence: Chroma ASGI server + product facet |
| `"chroma" "uvicorn" port:8000` | 230 hits, same intent, no product-facet dependency |
| `http.title:"Chroma"` | 94 hits, title match, some non-DB Chroma products mixed in |
| `http.html:"chromadb"` | 76 hits, name-specific HTML body match |
| `"chromadb"` | 47 hits, name-specific banner match (46 on 2026-04-30 reverify) |
| `"server: uvicorn" "/api/v2"` | 39 hits (2026-04-30), Chroma 0.6+ ASGI fingerprint; v2 API path + uvicorn header narrows to current-era unauth-by-default deployments |
| `http.html:"/api/v1/heartbeat"` | 22 hits, heartbeat path leaked into HTML response |
| `"chroma" port:8100` | 13 hits, post-0.5 default port |
| `product:"Chroma" port:8100` | 13 hits, product facet on new default |
| `"chroma" "0.6"` | 12 hits, current version era |
| `"chromadb" port:8000` | 5 hits, narrow |
| `"chroma" "0.5"` | 2 hits, transitional auth-optional era |
| `"chroma" "0.4"` | 1 hit, pre-auth legacy era, nearly extinct |

**Fingerprint note:** Shodan does **not** index arbitrary HTTP endpoint paths (`/api/v1/heartbeat`, `/api/v1/collections`, `/openapi.json`) in the root banner, it crawls `/` and headers only. Path-based fingerprints only work when the path string appears inside HTML response bodies (see `http.html:"/api/v1/heartbeat"` above). This is a general lesson applicable across the catalogue.

**Status-code caveat:** Chroma returns 404 at `/` regardless of auth configuration (no root handler registered), so `http.status:200` and `http.status:401` both return 0 for `product:"Chroma"`. Auth-enabled vs unauth cannot be distinguished from Shodan banner data alone, probe `/api/v1/heartbeat` live to tell them apart.

```
{"nanosecond heartbeat": 1713384722842816000}
```
What a T1 Chroma heartbeat response looks like. No auth, full API reachable.

## Qdrant

| Shodan Query | Notes |
|---|---|
| `http.html:"qdrant"` | 949 hits, canonical fingerprint; HTML-body match catches what banner doesn't |
| `http.html:"qdrant" port:443` | 331 hits, TLS-fronted deployments (proxy or native) |
| `http.html:"qdrant" port:80` | 221 hits, plaintext proxy-fronted |
| `"qdrant"` | 189 hits, banner-level match, narrower subset |
| `"qdrant" "vector"` | 31 hits, banner + domain term |
| `http.html:"qdrant" port:6333` | 27 hits, **direct default-port exposure; highest-risk subset, no proxy auth layer** |
| `"qdrant" "dashboard"` | 17 hits, web dashboard accessible, full read/write |
| `http.title:"Qdrant"` | 13 hits, title match |
| `http.html:"Qdrant Web UI"` | 6 hits, dashboard UI marker |
| `http.html:"Qdrant Dashboard"` | 3 hits, specific dashboard HTML |
| `"qdrant" "collections"` | 1 hit, banner + API term |
| `http.html:"qdrant-version"` | 1 hit, response header string leaked into HTML |

**Fingerprint field lesson (generalizable):** `"qdrant"` bare returns 189 hits but `"qdrant" port:6333` returns **0**, not a bug. Bare `"<term>"` matches Shodan's banner text (headers + initial response). On port 6333, Qdrant's REST root returns JSON without the literal word "qdrant" in headers, so banner match misses. The `http.html:` field parses response bodies and does catch it. Always try both `"<term>"` and `http.html:"<term>"`.

**Path indexing:** Qdrant's `/telemetry`, `/snapshots`, and `/points/search` endpoints don't surface in Shodan at all, even the terms "telemetry", "points", "snapshots" paired with "qdrant" return 0 on every combination tested. These endpoints require live probing, not Shodan queries.

**Deployment shift:** 922 of 949 Qdrant instances are no longer on port 6333 (80+443+proxies = ~90% of exposure). Same pattern as n8n and Flowise.

## Weaviate

| Shodan Query | Notes |
|---|---|
| `http.html:"weaviate"` | 1,647 hits, canonical fingerprint |
| `"weaviate"` | 1,326 hits, banner match, anonymous access by default |
| `http.html:"weaviate" port:8080` | **899 hits**, ~55% of instances still on default port; direct unauth access likely |
| `"weaviate" port:8080` | 564 hits, banner + default port |
| `"weaviate" port:80` | 206 hits, plaintext proxy-fronted |
| `"weaviate" port:443` | 118 hits, TLS-fronted |
| `"weaviate" "meta"` | 19 hits, meta endpoint term in banner |
| `http.title:"Weaviate"` | 10 hits, title match |
| `http.title:"Weaviate Console"` | 3 hits, console UI title |
| `http.html:"Weaviate Console"` | 3 hits, console UI HTML |
| `"weaviate" "schema"` | 1 hit, schema term in banner |

**Deployment anomaly:** Weaviate is the only vector DB verified so far that **did not** mass-migrate off its default port. 899 of 1,647 instances (~55%) remain directly exposed on 8080, vs Qdrant (3% on 6333) and Flowise (~0% on 3000). Likely explanation: Weaviate is more often run behind application backends rather than user-facing reverse proxies, the embedding service sits between an app and the data, not between a user and a UI. The practical impact: direct 8080 hits are higher-confidence "this is a real Weaviate API, no auth layer in front" signals.

**Path indexing:** All 5 original `/v1/schema`, `/v1/objects`, `/v1/meta`, `/v1/nodes`, `/v1/backups` queries returned 0. Shodan doesn't crawl these paths. Live-probing the `/v1/meta` endpoint on confirmed Weaviate hosts is required to enumerate version + module config.

**Module fingerprint gap:** `"text2vec-openai"` and `"generative-openai"` both return 0 alone and paired, module config is server-side metadata, not reflected in root banner or HTML. To detect OpenAI-key-backed Weaviate deployments, probe `/v1/meta` live on the 899 port:8080 hits.

**Auth reality check:** Weaviate ships with anonymous access enabled unless `AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=false` is explicitly set. With 899 direct-exposure hits, assume most are unauthenticated absent contrary evidence.

## Milvus

| Shodan Query | Notes |
|---|---|
| `"Attu"` | 2,071 hits, admin GUI banner, unique to Milvus |
| `"milvus"` | 1,617 hits, banner match |
| `http.html:"milvus"` | 1,571 hits, canonical HTML fingerprint |
| `http.html:"Attu"` | 1,497 hits, admin GUI HTML |
| `http.title:"Attu"` | 1,492 hits, admin GUI title |
| `product:"Milvus"` | 1,486 hits, Shodan product facet |
| `http.title:"Attu" "Milvus"` | 1,483 hits, highest-confidence admin GUI |
| `"milvus" "Attu" port:8000` | 751 hits, Attu on port 8000 with Milvus banner |
| `"milvus" port:8000` | 751 hits, Milvus banner on 8000 |
| `http.title:"Attu" port:3000` | 301 hits, Attu on its own default port 3000 |
| `"milvus" http.status:200` | 57 hits, Milvus banner with 200 response |
| `"milvus" "MinIO"` | 50 hits, Milvus + object-storage backend co-located |
| `http.title:"Milvus"` | 36 hits, Milvus in title |
| `"milvus" "etcd"` | 31 hits, Milvus + metadata store |
| `"milvus" port:9000` | 11 hits, MinIO port |
| `"milvus" "metrics"` | 8 hits, metrics term in banner |
| `"milvus" port:2379 "etcd"` | 6 hits, etcd metadata store exposed |
| `"milvus" port:9091` | 1 hit, legacy HTTP proxy port |

**gRPC blind spot (important):** Milvus's primary API runs on port 19530 over gRPC (HTTP/2 + protobuf binary framing). Shodan's banner grab cannot read the "milvus" string from a gRPC banner, it's not HTTP text. `port:19530` returns 522 baseline hits that *likely* include Milvus, but `"milvus" port:19530` returns **0**. These 522 hits cannot be confirmed as Milvus from Shodan alone; live probing via a gRPC reflection request or a `milvus.proto.milvus.MilvusService/DescribeCollection` RPC is required.

**Path indexing:** Original queries using `/api/v1/health` and `/metrics` on port 9091 all returned 0 (same Shodan crawl-path limitation documented in Chroma and Qdrant sections).

**Component visibility ranking:** In this catalogue's data, the **Attu admin UI is more exposed than the Milvus core itself** (2,071 Attu banner hits vs ~1,500 Milvus HTML hits). Attu is a React SPA with full read/write access to any Milvus it connects to, typically via a connection dropdown with no auth checks in the UI layer. A reachable Attu is a reachable database.

**Side-service exposure:** When Milvus is deployed with its full stack, the etcd metadata store (port 2379) and MinIO object backend (port 9000) often ride alongside, etcd exposes the entire schema and collection topology; MinIO holds the raw vector files. Check `"milvus" "etcd"` and `"milvus" "MinIO"` results for colocated trifectas.

## Object Storage & Artifact Stores

Vector databases are the search layer. Object storage is where the models, embeddings, raw documents, training datasets, and DB snapshots actually live on disk. Milvus, Weaviate, and most RAG pipelines back onto MinIO or S3 by default. A compromised bucket is typically a higher-impact finding than the index in front of it.

### MinIO

| Shodan Query | Notes |
|---|---|
| `"MinIO Console" port:9001` | **49,984 hits**, admin console on default port; largest exposure in this catalogue |
| `"MinIO" port:9000` | 43,775 hits, S3-compatible data port; default backing for Milvus/Weaviate/RAG |
| `"Server: MinIO" port:9000` | 42,799 hits, Server header leak, near-total overlap with above |
| `http.title:"MinIO Browser" port:9000` | 2,711 hits, legacy browser UI (pre-console split) |
| `"MinIO" ("bucket" OR "objects") port:9000` | 1,444 hits, bucket listing keywords in banner |

**MinIO reality check:** The previously-listed `"MinIO" port:9000 -"auth"` is not a useful auth filter, `-"auth"` matches ~identical counts (43,778 vs 43,775) because "auth" is not a banner token for MinIO either way. Query dropped. Distinguishing authenticated vs open buckets requires live probing `/probe-bucket-sign/` or attempting anonymous `ListBuckets`.

### Docker Registry

| Shodan Query | Notes |
|---|---|
| `product:"Docker Registry"` | 15,656 hits, Shodan product facet, canonical fingerprint |
| `"Docker Registry"` | 14,843 hits, banner-level match |
| `"Docker Registry" -"unauthorized"` | **9,161 hits**, registries NOT returning 401 at root; anonymous-readable subset |
| `"Docker Registry" "unauthorized"` | 5,683 hits, auth-enabled subset (returns 401 at root) |
| `"Docker-Distribution-Api-Version"` | 1,679 hits, HTTP response header leak (highly specific) |
| `"registry/2.0"` | 1,675 hits, `www-authenticate` realm token leak |
| `"registry/2.0" "unauthorized"` | 1,030 hits, registry realm with 401 enforced |
| `"Docker Registry" port:443` | 873 hits, TLS-fronted registries |
| `"registry/2.0" -"unauthorized"` | 646 hits, realm token + no 401 = anonymous read candidate |
| `"Docker Registry" port:51000` | 397 hits, non-default port, same exposure class |
| `"Docker Registry" port:55000` | 291 hits, non-default port, same exposure class |
| `"Docker Registry" port:5001` | 273 hits, alternate registry port |
| `"Docker Registry" "/v2/" port:5000` | 131 hits, default port + v2 API token |
| `"Docker Registry" port:80` | 100 hits, plaintext registries |
| `http.html:"_catalog"` | 32 hits, catalog path leaked into HTML body |
| `"registry/2.0" port:5000` | 29 hits, realm token + default port |
| `"_catalog"` | 20 hits, catalog token in banner |
| `http.html:"/v2/_catalog"` | 14 hits, exact catalog path in HTML |
| `"/v2/_catalog"` | 2 hits, literal path in banner (rare) |

### Harbor

| Shodan Query | Notes |
|---|---|
| `http.title:"Harbor"` | 22,555 hits, enterprise registry title |
| `"harbor" (port:80 OR port:443)` | 14,607 hits, banner match with grouped OR (unparenthesized version silently breaks) |

**Triage note:** Anonymous `/v2/_catalog` read ≠ anonymous push. But anonymous pull of internal images leaks entire codebases, build-time secrets in layer history, and the full supply chain of whatever ships from that registry. Rate severity on _read vs. push_ separately before escalating. See §12 for Docker daemon and container runtime exposure (distinct from the artifact store).

**Scale callout:** MinIO (~50k console hits + ~44k data hits) and Docker Registry (~15k) together form the single largest AI-adjacent attack surface in this catalogue, bigger than any model-serving, vector-DB, or orchestration platform measured. When a Milvus or Weaviate colocates with an exposed MinIO, the storage layer is almost always the faster path to training data, DB snapshots, and raw vectors. Prioritize accordingly.

## Elasticsearch / OpenSearch

### Elasticsearch

| Shodan Query | Notes |
|---|---|
| `product:"Elastic"` | **92,587 hits**, Shodan product facet; note Shodan uses "Elastic", not "Elasticsearch" |
| `"elasticsearch"` | 77,771 hits, banner-level match |
| `"elasticsearch" "lucene_version"` | 60,294 hits, JSON root response leak (highly specific) |
| `"elasticsearch" port:9200` | 7,075 hits, banner + default HTTP port |
| `"elasticsearch" "8."` | 3,728 hits, v8.x subset, has native dense_vector support |
| `"elasticsearch" port:9200 "cluster_name"` | 109 hits, cluster_name JSON field leaked |
| `"elasticsearch" port:9200 "You Know, for Search"` | 94 hits, official tagline leak |
| `http.html:"/_cluster/health"` | 3 hits, cluster health path in HTML (rare) |

### Kibana

| Shodan Query | Notes |
|---|---|
| `"kibana"` | 17,368 hits, banner match |
| `"kibana" port:5601` | 5,253 hits, Kibana default port |
| `http.title:"Kibana"` | 2,230 hits, UI title |
| `"kibana" "server is not ready"` | 3 hits, bootstrap state, often unauth window |

### OpenSearch

| Shodan Query | Notes |
|---|---|
| `"opensearch"` | 63,832 hits, banner match; browser-plugin pollution tested as minimal |
| `http.html:"opensearch"` | 22,846 hits, HTML body match |
| `http.title:"OpenSearch Dashboards"` | 7,843 hits, dashboards UI title (clean) |
| `"opensearch" port:9200` | 934 hits, data node default port |
| `"opensearch-dashboards"` | 269 hits, dashboards banner |
| `"opensearch-dashboards" port:5601` | 78 hits, dashboards default port |

**AI-extension blind spot (important):** The vector-search features that make Elasticsearch/OpenSearch relevant to AI (dense_vector field, knn plugin, embeddings, number_of_shards, index mappings) are **invisible to Shodan**. Every query containing `"dense_vector"`, `"knn"`, `"embeddings"`, or `"number_of_shards"` returns 0, even alone, even in html fields. These tokens live in per-index API responses (`/_mapping`, `/_cat/indices`), which Shodan does not crawl. You cannot distinguish "ES running a RAG vector store" from "ES storing web logs" via Shodan alone, requires live probing.

**Auth-state blind spot:** `"elasticsearch" -"security_exception"` matches the same 77k as unfiltered (literally 77,772 vs 77,771). X-Pack auth errors don't appear in Shodan banners either. Distinguishing open clusters from auth-gated ones requires live `/` or `/_cluster/health` probes with no auth header.

**Browser plugin pollution tested, not a concern:** `http.html:"opensearch" -"opensearchdescription"` = 22,845 hits (removes 1 from 22,846). The W3C OpenSearch browser plugin spec is not meaningfully contaminating OpenSearch DB counts.

**Scale note:** With `product:"Elastic"` at 92,587, Elasticsearch is the **single most-exposed platform in this entire catalogue**, larger than MinIO Console (49,984) and n8n (77,102). Most of these run for observability/logs, not vectors, but a non-trivial fraction of the 3,728 v8.x instances serve RAG workloads whose vector indexes cannot be separated from log indexes without live probing.

## PostgreSQL + pgvector

### PostgreSQL base platform

| Shodan Query | Notes |
|---|---|
| `"PostgreSQL"` | 603,878 hits, banner match; largest base platform in catalogue. Most auth-gated on the wire protocol, not exploitable from Shodan banner alone |
| `product:"PostgreSQL"` | 602,991 hits, Shodan product facet (near-total overlap with banner) |

### pgvector

| Shodan Query | Notes |
|---|---|
| `"pgvector"` | 125 hits, banner match; vanishingly small subset of PG instances fingerprint as vector DBs |
| `http.html:"pgvector"` | 103 hits, pgvector mentioned in HTML body (dashboards, docs, admin UIs) |

### Supabase

| Shodan Query | Notes |
|---|---|
| `http.html:"supabase"` | **45,784 hits**, Supabase ships with pgvector by default; each of these is a candidate RAG backend |
| `"supabase"` | 3,276 hits, banner-level match |
| `"Supabase" port:8000` | 56 hits, Supabase Studio/API on default port, direct-exposure subset |
| `http.title:"Supabase Studio"` | 1 hit, Studio admin UI title |

### pgAdmin

| Shodan Query | Notes |
|---|---|
| `http.html:"pgAdmin"` | 6,899 hits, HTML body match (largest admin-surface count) |
| `http.title:"pgAdmin"` | 6,704 hits, admin UI title; default creds historically common |
| `"pgAdmin" port:80` | 100 hits, plaintext-exposed admin UI |
| `"pgAdmin"` | 892 hits, banner-level match |
| `"pgAdmin" port:443` | 59 hits, TLS-fronted admin UI |

### Timescale

| Shodan Query | Notes |
|---|---|
| `"Timescale"` | 63 hits, banner-level match |
| `http.html:"timescaledb"` | 56 hits, TimescaleDB mentioned in HTML; vector support via pgvector compatibility |

### Neon

| Shodan Query | Notes |
|---|---|
| `"neon.tech"` | 139 hits, Neon hostname in banner/TLS cert |
| `http.html:"neon.tech"` | 7 hits, Neon domain in HTML body |
| `"Neon" "postgres"` | 3 hits, Neon word collision is high; filter tightly |

**Scale reality:** PostgreSQL at 603k+ is the largest base-platform count in this catalogue, but the vast majority are not AI-adjacent. The pgvector subset is 125 banner-match hits, three orders of magnitude smaller. **Supabase is the signal-to-noise winner here**: 45,784 Supabase HTML hits vs 125 raw pgvector hits, and Supabase ships pgvector by default. A reachable Supabase backend with open anon keys is a pgvector-backed RAG store with higher probability than probing a random `"PostgreSQL"` host.

**Auth-state blind spot:** PostgreSQL uses a binary protocol on 5432; Shodan captures the startup error/version banner but not auth posture. `psql -h <ip> -U postgres` or explicit `SELECT` over a captured connection string is the only way to confirm anonymous vs authenticated access. The 603,878 banner hits are a visibility count, not a vulnerability count.

**Original query failures:** All 5 originals combined narrow port (`5432`) + path-style strings (`"pgvector"`, `"vector"`) that don't coexist in the PG startup banner. `"PostgreSQL" port:5432 "pgvector"` = 0 because the startup error doesn't contain extension names. Use the replacements above.

## Redis Vector Search

| Shodan Query | Notes |
|---|---|
| `product:"Redis"` | **245,566 hits**, Shodan product facet, canonical Redis fingerprint |
| `"Redis" port:6379 -"AUTH" -"NOAUTH"` | 67,934 hits, no password set (filter narrows from 245k → 68k, meaningful) |
| `"Redis Stack"` | 754 hits, Redis Stack bundle (includes RediSearch for vectors) |
| `"Redis Stack" port:6379` | 726 hits, Redis Stack on default port |
| `http.title:"RedisInsight"` | 295 hits, Redis GUI title |
| `"RedisInsight"` | 57 hits, GUI banner match |
| `"Redis" "FT.SEARCH"` | 1 hit, vector-search command in banner (extremely rare) |

## MongoDB

| Shodan Query | Notes |
|---|---|
| `port:27017 -"unauthorized"` | **568,835 hits**, broad MongoDB-port candidates not returning 401; not all are MongoDB but the default Mongo port dominates |
| `product:"MongoDB"` | 197,308 hits, Shodan product facet |
| `"MongoDB"` | 107,071 hits, banner-level match |
| `"MongoDB" port:27017 -"auth"` | 89,942 hits, unauth-candidate subset (filter narrows ~17%) |
| `"MongoDB" port:27017 "vector"` | ⚠️ 59,996 hits, "vector" likely pollutes; Atlas Vector Search is the AI feature but this token appears in more MongoDB banners than expected, sample before trusting |
| `"mongo-express" port:8081` | 187 hits, web admin, default creds common |

## ClickHouse

| Shodan Query | Notes |
|---|---|
| `"clickhouse"` | 35,023 hits, banner |
| `product:"ClickHouse"` | 32,152 hits, Shodan product facet |
| `"clickhouse" port:8123 ("vector" OR "similarity")` | 1 hit, OLAP + vector hybrid in banner (rare, live-probe required) |

## Other Vector DBs

| Shodan Query | Notes |
|---|---|
| `"arangodb"` | 641 hits, banner match |
| `http.html:"arangodb"` | 555 hits, HTML body |
| `http.title:"ArangoDB"` | 551 hits, broader than "ArangoDB Web Interface" |
| `http.title:"ArangoDB Web Interface"` | 550 hits, specific admin UI title |
| `"surrealdb"` | 480 hits, banner |
| `"typesense"` | 341 hits, banner |
| `http.html:"lancedb"` | 334 hits, HTML body (bare `"lancedb"` banner = 0) |
| `"cassandra"` | 267 hits, banner; vector extensions in 5.x+ invisible to Shodan |
| `http.html:"vespa"` | 238 hits, Vespa HTML |
| `"Vespa"` | 232 hits, banner |
| `http.html:"typesense"` | 202 hits, HTML body |
| `"Vespa" "document"` | 67 hits, Vespa + document term (narrower) |
| `http.html:"surrealdb"` | 12 hits, HTML body |
| `"Zilliz"` | 8 hits, Milvus's hosted variant, sparse banner presence |
| `"marqo"` | 7 hits, banner |
| `"txtai"` | 3 hits, banner |

**No product facet** on Shodan (verified 0) for: SurrealDB, ArangoDB, Marqo, LanceDB, Typesense, Vespa, Zilliz, Cassandra, txtai. Use banner/HTML variants.

## Graph Databases / Memory

| Shodan Query | Notes |
|---|---|
| `product:"Neo4j"` | 9,743 hits, Shodan product facet |
| `"Neo4j"` | 6,101 hits, banner match |
| `"Neo4j" port:7474 "browser"` | 5,225 hits, Neo4j Browser UI, default creds neo4j/neo4j historically common |
| `"Dgraph"` | 185 hits, banner (case-insensitive) |
| `"Mem0"` | 140 hits, AI memory store |
| `http.title:"Ratel"` | 73 hits, Dgraph Ratel UI (cleaner than bare `"ratel"` which returns 156k of unrelated noise) |
| `"memgraph"` | 51 hits, in-memory graph DB, agent memory workloads |
| `"Memgraph Lab"` | 10 hits, Memgraph web UI |
| `"Mem0" port:8000` | 9 hits, Mem0 on default port |

**Ratel noise warning:** `"ratel"` bare returns 156,554 hits due to unrelated projects/products sharing the name. `http.title:"Ratel"` (73) is the clean version for Dgraph's UI specifically.

**Auth-state takeaways from this section:**
- Redis `-"AUTH" -"NOAUTH"` filter is **meaningful** (245k → 68k)
- MongoDB `-"auth"` filter is **meaningful** (107k → 90k)
- Contrast with ES `-"security_exception"` and MinIO `-"auth"` which are both no-ops
- Rule: always verify negative-filter behavior against the unfiltered count before relying on it as T1

**MongoDB `"vector"` anomaly ⚠️:** The `"MongoDB" port:27017 "vector"` query returns 59,996 hits, suspiciously large given MongoDB Atlas Vector Search is a 2023+ feature that runs on Atlas cloud (not typically self-hosted on open 27017). Likely contaminated by the word "vector" appearing in unrelated MongoDB banner/log content. Sample before trusting this as a RAG-backend fingerprint.
