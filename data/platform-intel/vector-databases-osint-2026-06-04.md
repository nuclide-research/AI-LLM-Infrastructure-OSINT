# Stage -1 Intel — Cat-02 Vector Databases (OSINT Platoon, 2026-06-04)

**Method:** 4-lane parallel OSINT Platoon (Sonnet), primary-source only, no live probing.
Feeds the aimap fingerprint build, the Censys zero-uplink expansion, and the live verification pass.
This is the intel doc Cat-02 never had (prior runs jumped straight to harvest on 6 inherited dorks).

## 0. Why this round exists (round-2/3 discipline)

The 2026-06-03 run was a full-arsenal pass but left the load-bearing stage undone and skipped two
Cat-01 layers:
- **32 "candidate-real" unauth were never verified** ("200 on API path; data-read NOT exercised").
- **No Censys cross-population** (Shodan-only; Chroma/Milvus/Qdrant are near-Shodan-dark).
- **No dev-browser cert-CN attribution** (VisorGraph: 7 nodes / LOW linkage from 238 seeds).
- **Vendor set was only 6** (Weaviate, Milvus/Attu, Qdrant, Chroma, Typesense, Meilisearch).

This round: expand the universe, add Censys + dev-browser, and VERIFY the candidates with a 200-with-data read.

## 1. Vendor universe + auth-on-default posture

### Tier A — core dedicated (the 06-03 six + verification truth)
| Platform | Default auth | Ports | CHANGED? (thesis) |
|---|---|---|---|
| Weaviate | **OFF** (anonymous read+write; `AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED='true'`) | 8080 REST, 50051 gRPC | RBAC added v1.30 (opt-in); default unchanged |
| Milvus (+Attu) | **OFF** (`authorizationEnabled:false`) | 19530 gRPC/REST, **9091** mgmt, Attu 3000 | bypasses closed 2.5.27/2.6.10; default unchanged |
| Qdrant | **OFF** (`service.api_key` = None) | 6333 REST(+/dashboard), 6334 gRPC | JWT/RBAC added (opt-in); default unchanged; **403** not 401 on auth-on |
| ChromaDB | **OFF** (no auth provider) | 8000 uvicorn (8100 proxy) | v1.0.0 removed v1 API; default open |
| Typesense | **ON by construction** (cannot start without bootstrap `--api-key`) | 8108 | hard-confirms thesis; risk = weak/leaked key |
| Meilisearch | **SPLIT by `MEILI_ENV`** — dev=OFF, production refuses start w/o ≥16B master key | 7700 | dev default = open |

### Tier B — search/hybrid stores
| Platform | Default auth | Ports | Vector marker |
|---|---|---|---|
| Elasticsearch | **OFF pre-8.0 / ON 8.0+** (auto TLS+elastic pw) | 9200 | `dense_vector` `dims:N` in `_mapping` |
| OpenSearch | demo `admin/admin` ≤2.11; **2.12+** forces `OPENSEARCH_INITIAL_ADMIN_PASSWORD` | 9200, dash 5601 | `knn_vector` `dimension:N` |
| Vespa | **OFF self-hosted** (mTLS opt-in) | 8080 query, **19071 config/deploy** | `tensor<float>(x[N])` schema field |
| Marqo | **OFF** (OSS, deprecated 2024; api_key="") | 8882 | every index is a vector store |
| Manticore | **OFF (no auth layer exists)** | 9308 HTTP, 9306 MySQL | `float_vector` + `knn_dims` |
| Typesense/Meili | see Tier A | | |

### Tier C — embedded-lib + host-DB-backed (the Shodan-dark layer)
| Platform | Nature | Surface | Default cred |
|---|---|---|---|
| pgvector | Postgres extension | open Postgres 5432 (`trust`/weak) | `postgres`, `trust` hba |
| Redis (RediSearch/VectorSet) | module/native (8.0 built-in) | 6379 no-AUTH (protected-mode defeated by `bind 0.0.0.0`) | none |
| MyScale | ClickHouse fork | 8123 HTTP `Ok.`, 9000 native | `default` user empty pw |
| Neo4j (vector index 5.13+) | graph DB | 7474 HTTP, 7687 Bolt | `neo4j/neo4j` forced-change |
| Vald | distributed ANN (gRPC) | **8081 gRPC** (reflection) | none (TLS+Athenz opt-in) |
| SemaDB | Go single-binary | 8081 `/v1/collections` | `X-User-Id` header = identity-as-auth |
| MyScale/Pinecone-Local | dev emulator | 5080-5090, keys ignored | none |
| **LanceDB / Deep Lake / txtai** | **EMBEDDED LIBS — no listener** | **S3/GCS bucket + host app** | bucket policy / leaked cloud keys |

## 2. Verification endpoints (the load-bearing reads — 200-with-data EARNS the label)

| Platform | Identity probe (200=is-platform) | Unauth-READ matcher (200 + NON-EMPTY vendor array) |
|---|---|---|
| Weaviate | `/v1/meta` → `version`+`modules` | `/v1/objects` → non-empty `objects[]` w/ `class`+`id`; `/v1/schema` → `classes[]` |
| Milvus | `/healthz` (9091) | **`/api/v1/credential/users` (9091) lists users = strongest** (CVE-2026-26190); `/v2/vectordb/collections/list` non-empty |
| Qdrant | `/` → `"qdrant - vector search engine"` | `/collections` → `result.collections[]` non-empty |
| ChromaDB | `/api/v2/version` + `server:uvicorn` | `/api/v2/tenants/default_tenant/databases/default_database/collections` non-empty |
| Typesense | `/health` → `ok:true` | `/collections` (w/ key) non-empty = key not enforced/weak |
| Meilisearch | `/health` → `status:available` | `/indexes` non-empty, no Bearer = open |
| Elasticsearch | `/` → `lucene_version`+`cluster_name` | `/_cat/indices?format=json` rows; `/<idx>/_mapping` has `dense_vector` |
| Redis | INFO `redis_version` | `INFO`/`DBSIZE`/`FT._LIST` without `-NOAUTH` |
| ClickHouse/MyScale | `/` == `Ok.` | `/?query=SHOW DATABASES` excl. default/system |
| Neo4j | `/` (7474) `neo4j_version` | `POST /db/neo4j/tx/commit` 200 results (auth disabled) |

**FP guard (the 72→32 inflation class):** a `200` on health/heartbeat is **identity only** (Insight #16).
A `200` with an **empty** `[]`/`{"results":[]}` is open-but-empty, **not** a data leak. A `404/401/410/5xx`
is **never** an unauth read. The label is earned only by `200 AND non-empty vendor-unique array`.

## 3. SHODAN-DARK MAP → Censys / storage angle (drives the zero-uplink pass)

- **Tier 0 (no listener, total dark):** LanceDB, Deep Lake, txtai-library. Angle = **object-storage enum**
  (public S3/GCS): LanceDB `*.lance`+`_versions/`; Deep Lake `dataset_meta.json`+tensor dirs; txtai `documents` SQLite.
- **Tier 1 (dark to banner, surfaceable by Censys full-port/protocol):** pgvector (open Postgres 5432 then authed
  `pg_extension`), Vald (8081 gRPC reflection `vald.v1.*`), SemaDB (`/v1/collections` + `X-User-Id` err), Pinecone-Local
  (5080-5090 `/indexes` JSON), txtai-API (FastAPI `/openapi.json` route-set).
- **Tier 2 (Shodan-bright at host-DB layer):** Redis (6379 `-NOAUTH`), MyScale/ClickHouse (8123 `Ok.`), Neo4j (7474 discovery JSON).
- **Censys edge = cert layer + full-port, NOT body matching.** For dark vendors the highest-yield pivot is
  `services.tls.certificates.leaf_data.subject.common_name` / `.names` (SAN) → **operator attribution**, because the HTTP body is exactly where these are silent.

**Analytic punchline:** vector-DB exposure has migrated OFF dedicated vector ports onto host DBs and object storage.
A vector-port banner dork systematically under-counts; Censys full-port + bucket enum is the correction.

## 4. Highest-confidence Shodan dorks (small + niche)

| Vendor | Dork | Noise |
|---|---|---|
| Qdrant | `http.html:"qdrant - vector search engine"` | very low (gold) |
| Meilisearch | `http.html:"Meilisearch"` (branded root) | low (gold) |
| Milvus/Attu | `http.title:"Attu"` | low |
| Neo4j | `http.title:"Neo4j Browser"` port:7474 | low |
| Weaviate | borderline dark — `port:8080 "vectorizer"` weak; lean Censys | high |
| ChromaDB / Milvus-core / Typesense / pgvector / LanceDB | **SHODAN-DARK** → Censys/live probe | n/a |
| Elasticsearch | `port:9200 "lucene_version"` (huge, not vector-specific) | medium |
| Redis | `product:Redis "redis_version"` | medium |
| MyScale/ClickHouse | `port:8123 "Ok."` (CH-generic) | medium |

## 5. CVE leads (verify before disclosure-grade use)

- **Milvus CVE-2026-26190** (9.8) — unauth REST on 9091 (collections, data, **credential create/list**) even when 19530 auth-on. Fixed 2.5.27/2.6.10. VERIFIED advisory.
- **Milvus CVE-2025-64513** (9.3) — Proxy auth bypass via forged headers. Fixed 2.4.24/2.5.21/2.6.5.
- **ChromaDB CVE-2026-45829** — unauth pre-auth RCE (client-supplied HF model loaded pre-auth), 1.0.0-1.5.8. Fix status UNCONFIRMED (lead).
- **Qdrant CVE-2024-3829** — snapshot symlink file r/w → RCE, fixed 1.9.0. CVE-2024-2221 path traversal.
- **Redis CVE-2025-49844 "RediShell"** — Lua UAF → RCE via EVAL; on unauth-open = unauth-RCE end-to-end. VERIFY ID.
- **Weaviate CVE-2025-67818** — backup ZipSlip path traversal, fixed 1.33.4 (needs DB access).
- **ClickHouse CVE-2025-1385** — library-bridge RCE.
- **pgvector CVE-2026-3172** — parallel-HNSW buffer overflow, fixed 0.8.2 (ID needs-confirm; chains off open Postgres).
- **Neo4j CVE-2021-34371** — Bolt/Jetty Java deserialization RCE (version-gated, stale instances).
- FALSE LEADS (do not ingest): Typesense CVE-2025-26876 (WordPress plugin), Meilisearch CVE-2026-25324 (QSM WP plugin).

## 6. FP trap catalog (top 8)

1. **"chroma" lexical collision** — Razer Chroma, chroma-subsampling, CSS chroma-key. Anchor on `/api/v2`+uvicorn, never the substring.
2. **catch-all path-echo (dcm4chee class)** — proxy echoes requested path into body. Control probe: random 32-char path; if it also 200s, it's a catch-all.
3. **Elasticsearch without vector data** — require `dense_vector`/`knn_vector` in `_mapping`; plain ES is not a vector store.
4. **schema.org Product pages** — `collections`/`objects`/`vector` match e-commerce HTML. Demand JSON content-type + vendor sibling field.
5. **honeypots (AS63949-class)** — uniform certs, every port open, canned data, salt `wW0sffoqsk.EM`.
6. **404/4xx-as-unauth** — the 72→32 inflation. status 200 + non-empty array only.
7. **health/heartbeat = data** — identity tier, not auth-state (Insight #16).
8. **Meili/Typesense demo deploys** — index names `movies`/`steam-games`, vendor cert CN. Demo data ≠ exposure.

## 7. This round's plan (carry into the chain)
1. Carry forward the 06-03 233 IPs + 32 candidate-real (Weaviate=23, DockerReg=5, Lunary=2, Qdrant=1, RedisInsight=1).
2. **Censys zero-uplink** expansion on the Shodan-dark vendors (cert-pivot + full-port) + the embedded-lib bucket angle.
3. **Dev-browser cert-CN attribution** (0 credits) across prior 233 + Censys delta.
4. **VERIFY the 32 candidates** — 200-with-non-empty-array read, names/counts only (restraint, no exfil).
5. aimap new fingerprints for gap vendors (Marqo `Welcome to Marqo`, Manticore handshake, Vald reflection) — grouped/small (home-uplink).
6. VisorCAS screen → VisorLog ingest → VisorScuba score → analysis doc + commit.
