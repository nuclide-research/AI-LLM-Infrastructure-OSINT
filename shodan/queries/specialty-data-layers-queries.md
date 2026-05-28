# Specialty Data Layers — Shodan Query Catalog
_Generated: 2026-05-27 from pre-survey OSINT pass (15 platforms)_
_See: data/platform-intel/specialty-data-layers-osint-2026-05-27.md for full intel_

Platforms covered: ClickHouse, Apache Cassandra, Redis Stack, MinIO, Feast, Hopsworks, Tecton, Feathr, ArangoDB, Neo4j, Apache Kafka REST Proxy, Apache Flink, Spark History Server, Trino/Presto, Delta Sharing Server.

---

## ClickHouse

**Auth default:** off (default user ships with empty password; pre-DeepSeek-incident Docker images leave the default user network-accessible with no password)
**Exposure class:** Full SQL access to all databases; system tables expose env vars, query logs, schema, LLM request/response logs stored in AI stacks. `SELECT * FROM system.environment` dumps environment variables including any secrets.

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:8123 "x-clickhouse-server-display-name"` | Vendor-unique HTTP response header; present on all ClickHouse HTTP responses | Low |
| secondary | `http.title:"ClickHouse" port:8123` | Title fingerprint on the /play web SQL console | Low |
| tertiary | `port:8123 "X-ClickHouse-Format"` | Another vendor-unique response header set on query responses | Low |
| metrics | `port:9363 "clickhouse_"` | Prometheus metrics endpoint — no auth, leaks table counts and query rates | Low |
| identity-probe | `GET /?query=SELECT+1` → `1\n` + `x-clickhouse-server-display-name` header | Confirms unauthenticated SQL execution + leaks internal hostname | — |

---

## Apache Cassandra

**Auth default:** off (`authenticator: AllowAllAuthenticator` is the yaml default; no credentials required)
**Exposure class:** Full CQL read/write to all keyspaces; JMX on 7199 gives full cluster management. AI stacks expose feature vectors, session data, time-series ML features.

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:9042 "Apache Cassandra"` | CQL handshake banner contains product string | Low |
| secondary | `port:9042 "CQL_VERSION"` | CQL OPTIONS response field; vendor-unique protocol signal | Low |
| jmx | `port:7199 "cassandra"` | JMX port — unauthenticated by default; full cluster management access | Med |
| identity-probe | CQL `OPTIONS` on port 9042 → `CQL_VERSION` + `COMPRESSION` keys in response | Confirms Cassandra native protocol; no HTTP endpoint available | — |

---

## Redis Stack / Redis with Vector Modules

**Auth default:** off (no `requirepass` by default; ~60,000 of 300,000+ internet-exposed instances have zero auth per Wiz 2025)
**Exposure class:** Full key-value read/write including all embeddings, cached API keys, LLM conversation history, feature values. CVE-2025-49844 (RediShell, CVSS 9.9) enables RCE via Lua on no-auth instances.

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:6379 "redis_version"` | INFO server response contains this field in plaintext; Shodan reads it | Low |
| secondary | `port:6379 "+OK"` | Redis protocol response to PING; broad but catches no-auth instances | Med |
| redisinsight | `http.title:"RedisInsight" port:8001` | Redis Stack web UI; if exposed, direct GUI access to all keys and data | Low |
| vector-module | `port:6379 "ReJSON" "search"` | MODULE LIST response fields for Redis Stack with RediSearch + ReJSON loaded | Low |
| identity-probe | `INFO server` on port 6379 → `redis_version`, `redis_mode`, `os:Linux` fields; `MODULE LIST` → confirms vector modules | — |

---

## MinIO

**Auth default:** default-creds (`minioadmin:minioadmin` Docker default; CVE-2023-28432 leaked root credentials via unauthenticated POST on pre-2023-03-20 releases)
**Exposure class:** Full S3 API access to all buckets — model weights, training datasets, MLflow artifacts, DVC cache, Kubeflow pipeline artifacts. CVE-2023-28432 (CISA KEV) leaks `MINIO_SECRET_KEY` and `MINIO_ROOT_PASSWORD` in plaintext.

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `http.title:"MinIO Console" port:9001` | Console web UI; vendor-unique title fingerprint | Low |
| secondary | `"x-minio-deployment-id" port:9000` | Per-deployment UUID header on S3 API port; vendor-unique | Low |
| tertiary | `"MinIO" port:9000 http.status:403` | S3 API returns 403 to unauthenticated requests but MinIO header still present | Low |
| health | `port:9000 "/minio/health/live"` | Health endpoint is unauthenticated; confirms MinIO without login | Low |
| identity-probe | `GET /minio/health/live` → 200 (no auth); `HEAD /` → `x-minio-deployment-id` UUID header; CVE-2023-28432 probe: `POST /minio/bootstrap/v1/verify` → env vars on unpatched | — |

---

## Feast

**Auth default:** off (`auth: type: no_auth` is the documented default in `feature_store.yaml`; TLS also off by default)
**Exposure class:** Full online feature store read/write — real-time feature values for any entity, RAG document embeddings via `/retrieve-online-documents`, feature metadata revealing data schema. `/push` endpoint enables data poisoning.

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:6566 "feature_names"` | JSON response field from `/get-online-features` endpoint; vendor-specific schema | Low |
| secondary | `port:6566 "feast"` | Server or response body contains "feast" identifier | Low |
| identity-probe | `POST /get-online-features` with `{"features":[],"entities":{}}` → JSON with `metadata.feature_names` and `results` fields | — |

---

## Hopsworks

**Auth default:** default-creds (`admin@kth.se` / `admin` documented default from official installer and community forums)
**Exposure class:** Full ML platform access — feature groups, feature views, training datasets, model registry (model binaries + metadata), experiment runs. Complete ML artifact lifecycle exposed.

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `http.title:"Hopsworks" port:8080` | Web UI title fingerprint | Low |
| secondary | `"hopsworks" port:8080 http.status:200` | Body/product string on open port | Low |
| identity-probe | `GET /hopsworks/auth/login.xhtml` → 200 + Hopsworks login form; attempt `admin@kth.se`/`admin` → redirects to dashboard on default installs | — |

---

## Tecton

**Auth default:** on (managed SaaS, API-key required; no open self-hosted deployment model)
**Exposure class:** N/A — no open-auth exposure documented.

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| sweep | `"tecton.ai" http.status:200` | Broad sweep for any Tecton-branded surface | High |
| identity-probe | No unauthenticated probe available; all endpoints require API key | — |

_Note: Expected near-zero actionable hits. Any findings are likely customer portals or documentation sites, not feature store infrastructure._

---

## Feathr

**Auth default:** off for Docker sandbox (local development image; Azure AD required for production)
**Exposure class:** Feature registry read/write — feature definitions, transformation logic (Python UDFs), entity definitions. Business logic exposure even without raw data access.

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `http.title:"Feathr" port:80` | Sandbox UI title | Med |
| secondary | `"feathr" "feature_store" http.status:200` | Body discriminator for API responses | Low |
| identity-probe | `GET /features` → JSON array of feature definitions on sandbox deployments | — |

---

## ArangoDB

**Auth default:** off (`--server.authentication` defaults to `false`; Docker image warns but does not enforce auth)
**Exposure class:** Full multi-model database access — graph data (knowledge graphs, RAG entity maps), document collections, key-value store. Foxx microservice framework enables RCE if app services are deployed. `/_api/database/user` lists all databases without auth.

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:8529 "ArangoDB"` | HTTP banner on default port; product name in Server header or body | Low |
| secondary | `port:8529 "arango" http.status:200` | API or UI response with arango identifier string | Low |
| version | `port:8529 "\"server\":\"arango\""` | Exact JSON field from `/_api/version` response | Low |
| identity-probe | `GET /_api/version` → `{"server":"arango","license":"community","version":"X.Y.Z"}` with no credentials required | — |

---

## Neo4j

**Auth default:** default-creds (`neo4j`/`neo4j`, forced password change on first login); many Docker deployments set `NEO4J_AUTH=none` for development and expose it externally
**Exposure class:** Full Cypher query access — knowledge graph entities and relationships, RAG document chunk metadata, ontology definitions. In AI stacks: LLM-extracted entity graphs, concept maps, user behavior graphs for recommendation.

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:7474 "neo4j_version"` | REST API `/db/data/` response field; vendor-unique JSON key | Low |
| secondary | `http.title:"Neo4j Browser" port:7474` | Web browser UI title; confirms HTTP-accessible Neo4j | Low |
| bolt | `port:7687 "bolt"` | Bolt binary protocol fingerprint; not HTTP but Shodan captures banner | Med |
| identity-probe | `GET /db/data/` → JSON with `"neo4j_version":"X.Y.Z"` and `"neo4j_edition":"community"` — no auth required on `NEO4J_AUTH=none` instances | — |

---

## Apache Kafka REST Proxy

**Auth default:** off (REST Proxy default config binds to port 8082 with no auth; "the REST Proxy bypasses broker ACLs when authorization is disabled")
**Exposure class:** Full topic enumeration — message stream names reveal business process topology. Consumer group access enables message replay. In AI pipelines: real-time feature events, inference requests, training data streams. Native Kafka on 9092 (no auth by default) allows producing/consuming all messages.

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:8082 "kafka" http.status:200` | REST Proxy default port with Kafka product identifier | Med |
| secondary | `port:8082 "KafkaTopicList"` | v3 API `"kind"` field value in `/v3/clusters/{id}/topics` response | Low |
| tertiary | `port:8082 "/topics"` | v1/v2 API topic list endpoint appears in banner or response | Med |
| zookeeper | `port:2181 "zookeeper"` | ZooKeeper unauthenticated — lists full Kafka cluster topology | Med |
| identity-probe | `GET /topics` → JSON array of topic names (v1/v2); `GET /v3/clusters` → `"kind":"KafkaClusterList"` (v3). Unauthenticated on default installs. | — |

---

## Apache Flink

**Auth default:** off ("the REST endpoint does not authenticate the client by default" per official Flink docs)
**Exposure class:** Running job visibility, full cluster config (may include Kafka brokers, DB connection strings, AWS credentials via `/jobmanager/config`), JAR upload enabling RCE. CVE-2020-17518/17519 (arbitrary file write/read) affect unpatched instances <= 1.11.2.

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:8081 "flink-version"` | JSON field from `/config` endpoint; vendor-unique | Low |
| secondary | `http.title:"Apache Flink Web Dashboard" port:8081` | Dashboard HTML title | Low |
| tertiary | `port:8081 "/jobs/overview"` | API endpoint path in banner or response body | Low |
| identity-probe | `GET /config` → `{"flink-version":"X.Y.Z","flink-revision":"...","features":{...}}` — no auth; `GET /jobs/overview` → running job names | — |

---

## Spark History Server

**Auth default:** off ("security features like authentication are not enabled by default in Apache Spark")
**Exposure class:** Spark job history including environment variables from all historical jobs — AWS access keys, S3 bucket names, Hive metastore passwords, Databricks PATs stored as Spark config properties. Job names reveal pipeline structure.

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:18080 "Spark History Server"` | Page title and body text on default UI | Low |
| secondary | `http.title:"History Server" port:18080` | Alternate title format used in some Spark versions | Low |
| api | `port:18080 "/api/v1/applications"` | REST API endpoint path in banner | Low |
| identity-probe | `GET /api/v1/applications` → JSON array with `id`, `name`, `attempts`; `GET /api/v1/applications/{appId}/environment` → Spark config including secrets | — |

---

## Trino / Presto

**Auth default:** off ("Trino runs with no security by default"; port 8080, no auth, no TLS in default config)
**Exposure class:** Full SQL query submission to any connected data source — S3/Delta Lake/Iceberg/Hive. Running query text and results exposed via `/v1/query` without auth. Cluster topology via `/v1/cluster`.

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:8080 "nodeVersion" "Trino"` | `/v1/info` JSON field + product name; discriminates from other port 8080 services | Low |
| secondary | `port:8080 http.title:"Trino"` | Web UI title (if enabled) | Low |
| presto | `port:8080 "presto" "nodeVersion"` | Facebook Presto fork uses same API; catches both products | Low |
| tertiary | `port:8080 "/v1/info" "starting"` | Specific field from the unauthenticated health endpoint | Low |
| identity-probe | `GET /v1/info` → `{"nodeVersion":{"version":"X.Y.Z"},"environment":"production","starting":false}` — unauthenticated health endpoint by design | — |

---

## Delta Sharing Server

**Auth default:** bearer-token (required by protocol; exposure risk is static/demo tokens with zero expiry, or tokens embedded in documentation used in production)
**Exposure class:** With valid bearer token: all shared Delta Lake tables — training datasets, feature tables, model evaluation sets. Token misconfiguration (zero expiry, demo tokens in production) is the primary risk.

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:8080 "delta-sharing"` | Protocol identifier in response body or headers | Low |
| secondary | `port:8080 "/shares" "application/json"` | REST API endpoint for listing shares | Med |
| identity-probe | `GET /shares` with `Authorization: Bearer {token}` → `{"items":[{"name":"..."}]}` listing all shares; test doc example token `faaie590-f132-4954-8571-d5b5b8` on self-hosted reference server installs | — |
