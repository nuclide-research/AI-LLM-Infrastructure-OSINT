# Specialty Data Layers / AI Feature Stores OSINT — Pre-Survey Intelligence
**Date:** 2026-05-27
**Purpose:** Tune dork queries, understand auth posture, identify verification probes, document data exposure classes before Shodan harvests.
**Scope:** 15 platforms — OLAP databases, feature stores, object storage, stream processing, graph databases used in AI/ML pipelines.
**Status:** Pre-survey. No active probing conducted.

---

## ClickHouse

**Category:** OLAP Database / AI LLM log store / AI feature store
**Default Ports:** 8123 (HTTP REST), 8443 (HTTP TLS), 9000 (native TCP), 9440 (native TCP TLS), 9363 (Prometheus metrics)
**Auth Default:** off — default user ships with empty password; no password authentication enforced unless explicitly configured. Recent Docker images (post-DeepSeek incident) backported a fix disabling network access for the default user, but older deployments remain open. Source `config.xml` contains `<password></password>` for the default user.
**Shodan Dork (primary):** `http.title:"ClickHouse" port:8123`
**Shodan Dork (secondary):** `"x-clickhouse-server-display-name" port:8123`
**Verification Probe:** `GET /?query=SELECT+1` → 200 + body `1\n`; also `GET /play` → ClickHouse web UI page
**Data Exposure Class:** Full SQL query access to all databases and tables on the instance. At minimum: schema metadata, query logs, system tables. In production AI stacks: LLM request/response logs, feature vectors, embedding tables, inference latency metrics, API keys stored in config or environment variables accessible via `SELECT * FROM system.environment`.
**Known CVEs:** No standalone auth-bypass CVE number assigned, but the default empty-password configuration has caused mass exposure. ClickHouse itself recommends: set password, restrict `listen_host`, use TLS ports.
**Default Credentials:** username `default`, password empty string (no password required)
**Notes:** The `X-ClickHouse-Server-Display-Name` response header leaks internal hostname (e.g., `ip-10-174-70-37.ec2.internal`). The `/play` endpoint provides a full browser-based SQL interface — no client needed to query data. Port 9000 (native protocol) is not HTTP-scannable by Shodan but port 8123 is. Prometheus endpoint at 9363 leaks table counts and query rates without auth. FP risk on 8123 is low — the header is vendor-unique.

---

## Apache Cassandra

**Category:** Wide-column NoSQL Database / AI feature store
**Default Ports:** 9042 (native CQL protocol), 9160 (Thrift, legacy), 7000/7001 (inter-node), 7199 (JMX)
**Auth Default:** off — `authenticator: AllowAllAuthenticator` is the default in `cassandra.yaml`. No credentials required by default. `authorizer: AllowAllAuthorizer` also grants all permissions to all authenticated (or unauthenticated) clients.
**Shodan Dork (primary):** `port:9042 "Apache Cassandra"`
**Shodan Dork (secondary):** `port:9042 "CQL_VERSION"`
**Verification Probe:** CQL native protocol handshake on port 9042 returns `OPTIONS` response with `CQL_VERSION` and `COMPRESSION` keys. Not HTTP-accessible.
**Data Exposure Class:** Full read/write access to all keyspaces. In AI stacks: feature vectors, user session data, ML inference logs, model metadata, time-series feature data. JMX on 7199 (unauthenticated by default) exposes full cluster management — add/remove nodes, flush memtables.
**Known CVEs:** CVE-2025-23015 — privilege escalation to superuser via MODIFY permission on ALL KEYSPACES (4.0.16 only). CVE-2025-24860 — authorization bypass in CassandraNetworkAuthorizer/CassandraCIDRAuthorizer allowing access to restricted datacenters. CVE-2024-27137 — JMX credential capture via RMI registry MITM (local attacker vector). CVE-2020-17516 — auth bypass in `CassandraLoginModule` via LDAP injection.
**Default Credentials:** none (AllowAllAuthenticator bypasses credential check entirely)
**Notes:** Port 9042 is not HTTP — Shodan banner-scans the CQL handshake. Dorks targeting this port find the CQL version string in banner. JMX on 7199 is a higher-value attack path: unauthenticated JMX grants full cluster control. Port 9042 is the top-reported open port for Cassandra on Shodan. No Shodan HTTP body dork available; rely on port + banner string.

---

## Redis Stack / Redis with Vector Modules

**Category:** In-memory key-value store / Vector database / AI feature cache
**Default Ports:** 6379 (Redis protocol), 8001 (RedisInsight web UI, Redis Stack only)
**Auth Default:** off — Redis ships with no `requirepass` set. The official container image does not require authentication. ~60,000 of ~300,000+ internet-exposed Redis instances have no authentication configured (Wiz, 2025).
**Shodan Dork (primary):** `port:6379 "redis_version"`
**Shodan Dork (secondary):** `port:6379 "+OK" "redis_version"`
**Verification Probe:** Redis `INFO server` response on port 6379 returns plaintext blob with `redis_version:X.Y.Z`, `redis_mode:standalone`, `os:Linux`. For Redis Stack: `MODULE LIST` returns loaded modules including `search` (RediSearch), `ReJSON`, `bf` (RedisBloom), `timeseries`.
**Data Exposure Class:** Full key-value read/write. In AI stacks: cached embeddings (vector index data via RediSearch), session tokens, API keys stored as Redis strings, feature values, LLM conversation history, rate-limit counters. KEYS `*` dumps all key names. `CONFIG GET *` dumps full configuration including bind address, maxmemory, module list.
**Known CVEs:** CVE-2025-49844 ("RediShell") — CVSS 9.9, use-after-free in Lua scripting engine, present in all Redis versions released in last 13 years. Exploitable by authenticated users OR unauthenticated users on no-auth instances. 8,500+ unpatched instances identified (October 2025). CVE-2025-21605 — DoS via unauthenticated output buffer exhaustion (CVSS 7.5). CVE-2024-46981 — Lua script RCE. CVE-2024-31449 — Lua stack overflow/RCE.
**Default Credentials:** none
**Notes:** Port 6379 returns plaintext Redis protocol responses — Shodan reads the `INFO` response directly. RedisInsight at 8001 is an HTTP web UI with its own auth posture (check `http.title:"RedisInsight"` separately). The `SLAVEOF` and `CONFIG SET` commands are available unauthenticated on default installs — classic RCE vector via config rewrite. FP risk very low on `redis_version` banner string.

---

## MinIO

**Category:** S3-compatible Object Storage / ML model artifact store / training data store
**Default Ports:** 9000 (S3 API), 9001 (MinIO Console web UI)
**Auth Default:** default-creds — MinIO requires `MINIO_ROOT_USER` and `MINIO_ROOT_PASSWORD` but many deployments ship with `minioadmin:minioadmin` (Docker default). A bare MinIO instance without env vars set uses these defaults. CVE-2023-28432 exposed environment variables including credentials via unauthenticated POST to `/minio/bootstrap/v1/verify`.
**Shodan Dork (primary):** `http.title:"MinIO Console" port:9001`
**Shodan Dork (secondary):** `"x-minio-deployment-id" port:9000`
**Verification Probe:** `GET /minio/health/live` → 200 (no auth required, health check endpoint). `HEAD /` on port 9000 returns `x-minio-deployment-id` header — unique per-deployment UUID. Console at port 9001 returns `http.title:"MinIO Console"`.
**Data Exposure Class:** With default creds `minioadmin:minioadmin`: full S3 API access — list all buckets, download all objects. In AI/ML stacks: trained model weights (`.pt`, `.ckpt`, `.safetensors`), training datasets, inference outputs, MLflow artifact store backing, DVC cache, Kubeflow pipeline artifacts. CVE-2023-28432 (pre-patch): `MINIO_SECRET_KEY` and `MINIO_ROOT_PASSWORD` leaked in plaintext via unauthenticated POST.
**Known CVEs:** CVE-2023-28432 (CVSS 7.5) — information disclosure via `/minio/bootstrap/v1/verify`, leaks all env vars including root credentials. Widely exploited in the wild; CISA KEV listed. CVE-2023-28434 — privilege escalation (chained with 28432 in active attacks). CVE-2025-62506 — privilege escalation in IAM system.
**Default Credentials:** `minioadmin:minioadmin` (Docker default), overridden by `MINIO_ROOT_USER`/`MINIO_ROOT_PASSWORD` env vars
**Notes:** The `x-minio-deployment-id` header is a unique Shodan signal — vendor-specific, not used by any other product. Over 50,000 MinIO instances exposed on Shodan historically. Console port 9001 is HTTP and shows a login page even when auth is enabled — the title fingerprint is reliable. Check both 9000 and 9001; many deployments expose only one. CVE-2023-28432 probe: `POST /minio/bootstrap/v1/verify` with empty body → returns env vars on unpatched instances.

---

## Feast

**Category:** Open-source Feature Store / ML feature serving
**Default Ports:** 6566 (feature server HTTP), 8000 (metrics/Prometheus, when enabled)
**Auth Default:** off — default configuration sets `auth: type: no_auth` in `feature_store.yaml`. No authentication required for any endpoint by default. TLS is also off by default.
**Shodan Dork (primary):** `port:6566 "feature_names"`
**Shodan Dork (secondary):** `port:6566 "feast"`
**Verification Probe:** `POST /get-online-features` with minimal JSON body → 200 + JSON with `metadata.feature_names` array and `results` array. `GET /` may return 404 but confirms port open.
**Data Exposure Class:** Full read/write access to online feature store. In AI/ML stacks: real-time feature values for any entity (user IDs, item IDs, transaction IDs), feature metadata revealing data schema and business logic, entity-feature mappings. The `/retrieve-online-documents` endpoint (RAG use case) exposes full document embeddings and text.
**Known CVEs:** No specific CVEs published for Feast core. Auth is application-layer opt-in.
**Default Credentials:** none (no auth required)
**Notes:** Feast is niche — Shodan population will be small. The `feature_names` field in the response JSON is a distinctive signal. The `/push` endpoint accepts writes, enabling data poisoning attacks on the feature store. Feast has a registry (SQLite/GCS/S3-backed) that can also be exposed. Port 6566 is not commonly used by other services — FP risk low. Feast deployments are often internal-only but Kubernetes misconfigurations expose them.

---

## Hopsworks

**Category:** ML Feature Store + Model Registry / AI Lakehouse
**Default Ports:** 8080 (Hopsworks web UI / API), 8181 (Python API / HSFS connector), 8443 (HTTPS variant)
**Auth Default:** default-creds — default admin credentials are `admin@kth.se` / `admin`. These ship in the installer and are documented in official community forums. The web interface at port 8080 requires login but the default credentials are publicly known.
**Shodan Dork (primary):** `http.title:"Hopsworks" port:8080`
**Shodan Dork (secondary):** `"hopsworks" port:8080 http.status:200`
**Verification Probe:** `GET /hopsworks/` → 200 + HTML containing "Hopsworks" in title or body. Login page at `/hopsworks/auth/login.xhtml`.
**Data Exposure Class:** With default credentials: full access to feature groups, feature views, training datasets, model registry (model binaries + metadata), experiment tracking. Hopsworks manages the full ML artifact lifecycle — a compromised instance exposes model IP and training data schemas.
**Known CVEs:** No high-profile standalone CVEs. Risk is credential-default exposure.
**Default Credentials:** `admin@kth.se` / `admin` (documented default from official installer)
**Notes:** Hopsworks is enterprise-grade and self-hosted deployments should be rare on the public internet. When found, default-creds exploitation is the primary attack path. The Python API on port 8181 uses API keys generated from the web UI — an attacker with web UI access can generate keys for programmatic access. The `admin@kth.se` default is a strong FP discriminator in login attempt analysis.

---

## Tecton

**Category:** Managed Feature Store / ML Feature Platform
**Default Ports:** N/A for self-hosted (Tecton is primarily SaaS/managed). Enterprise on-premises deployments use vendor-configured ports.
**Auth Default:** on — Tecton is a managed SaaS platform. All access requires API keys and workspace authentication. No self-hosted open-auth deployment model documented.
**Shodan Dork (primary):** `http.title:"Tecton" http.status:200`
**Shodan Dork (secondary):** `"tecton.ai" http.status:200`
**Verification Probe:** N/A — no unauthenticated endpoint documented for self-hosted mode.
**Data Exposure Class:** N/A — no open-auth exposure class for standard deployment.
**Known CVEs:** None published.
**Default Credentials:** N/A (API-key based auth, managed environment)
**Notes:** Tecton does not publish a self-hosted open-source deployment path with default-open ports. Shodan hits for "Tecton" are likely customer portals or documentation sites, not exposed feature store infrastructure. Low yield for this survey. Include in catalog for completeness but expected near-zero actionable hits. If Tecton-branded HTTP surfaces appear, treat as potential customer portal misconfiguration rather than a feature store exposure.

---

## Feathr

**Category:** Open-source Feature Store (LinkedIn) / Azure-native ML platform
**Default Ports:** 80 (Feathr UI in Docker sandbox), 8888 (Jupyter), 6100 (registry API — documented in some configurations), 8000 (API server)
**Auth Default:** off for local/Docker sandbox — the Feathr sandbox Docker image exposes services without authentication by default. Azure production deployments use Azure AD / Service Principal authentication. The local sandbox is documented as development-only but can be exposed if deployed on cloud VMs without firewall rules.
**Shodan Dork (primary):** `http.title:"Feathr" port:80`
**Shodan Dork (secondary):** `"feathr" "feature_store" port:8000`
**Verification Probe:** `GET /` → 200 + HTML containing "Feathr" in title. Feature registry API: `GET /features` → JSON array of feature definitions.
**Data Exposure Class:** Full read/write access to feature registry — feature definitions, feature groups, entity definitions, transformation logic (Python UDFs embedded in registry). Business logic exposure: feature computation rules reveal data science IP.
**Known CVEs:** None published. Auth bypass risk is deployment-configuration-dependent.
**Default Credentials:** none (sandbox) / Azure AD (production)
**Notes:** Feathr was open-sourced by LinkedIn in 2022 and donated to LF AI & Data. Active development; Azure is the primary production target. The Docker sandbox is the most likely exposure vector for Shodan hits. Population will be very small. The feature registry API exposes feature schemas that reveal what data is being computed — even without raw data, this is sensitive business intelligence. GitHub repo at `feathr-ai/feathr`.

---

## ArangoDB

**Category:** Multi-model Database (graph + document + key-value) / AI knowledge graph backend
**Default Ports:** 8529 (HTTP REST API + web UI "_system" database)
**Auth Default:** off — ArangoDB ships with authentication disabled by default. The `--server.authentication` flag defaults to `false`. The Docker image warning states: "this will expose all your data" but does not enforce auth. Official docs note that `/_api/version` and other endpoints respond to unauthenticated requests.
**Shodan Dork (primary):** `port:8529 "ArangoDB"`
**Shodan Dork (secondary):** `port:8529 "arango" http.status:200`
**Verification Probe:** `GET /_api/version` → 200 + JSON `{"server":"arango","license":"community","version":"X.Y.Z"}`. No auth required on default install.
**Data Exposure Class:** Full read/write access to all databases. In AI stacks: knowledge graph data (entities + relationships for RAG), document collections, user profile graphs, recommendation engine data. ArangoDB Foxx framework (built-in app server) can run arbitrary JavaScript — code execution if Foxx microservices are deployed. `GET /_api/database/user` lists all databases.
**Known CVEs:** CVE-2023-5441 — authentication bypass via HTTP header manipulation. Historical CVEs exist around Foxx service injection. Community edition lacks enterprise security features (audit logging, encryption at rest).
**Default Credentials:** no credentials required (auth disabled by default); if auth enabled, default root password set during installation
**Notes:** The `/_api/version` endpoint is a reliable no-auth probe — it returns even with auth enabled (returns version info, auth status in response). The ArangoDB web UI ("Aardvark") is served on the same port 8529 and is fully functional without auth in default config. Strong FP discriminator: the `"arango"` string in the `/_api/version` response is vendor-unique. Population on Shodan is moderate — ArangoDB has a real user base for graph analytics and AI knowledge graphs.

---

## Neo4j

**Category:** Graph Database / AI RAG knowledge graph / LLM context graph
**Default Ports:** 7474 (HTTP REST + Browser UI), 7473 (HTTPS), 7687 (Bolt binary protocol)
**Auth Default:** default-creds — default credentials are `neo4j`/`neo4j` and the system forces a password change on first login. Docker allows disabling auth entirely via `NEO4J_AUTH=none`. Many containerized deployments use `NEO4J_AUTH=none` for development and accidentally expose this to the internet.
**Shodan Dork (primary):** `port:7474 "neo4j_version"`
**Shodan Dork (secondary):** `http.title:"Neo4j Browser" port:7474`
**Verification Probe:** `GET /db/data/` → 200 + JSON containing `"neo4j_version":"X.Y.Z"` and `"neo4j_edition":"community"`. `GET /browser/` → 200 + Neo4j Browser HTML. Both work without credentials on `NEO4J_AUTH=none` deployments.
**Data Exposure Class:** Full Cypher query access to all graph data. In AI/RAG stacks: knowledge graph nodes and relationships (entity extraction results, concept maps), document chunk metadata, embedding references, ontology definitions. The Bolt protocol on 7687 enables direct programmatic access — not HTTP-scannable but reachable with any Neo4j driver.
**Known CVEs:** CVE-2025-56406 — RCE in `mcp-neo4j` 0.3.0 via unauthenticated SSE endpoint. CVE-2021-34371 — remote code execution via JDBC URL in Neo4j ETL plugin. Historical: multiple path traversal and SSRF CVEs in neo4j-browser and plugins. CVE-2022-37423 — Neo4j EE path traversal.
**Default Credentials:** `neo4j`/`neo4j` (forced change on first login); `NEO4J_AUTH=none` disables all auth
**Notes:** The `/db/data/` endpoint is the classic REST API — deprecated in Neo4j 5.x but still present and returns version info. Neo4j 5.x moves to the HTTP API at `/db/{database}/query/v2`. The `neo4j_version` field is a reliable banner signal. Port 7687 (Bolt) is TCP binary protocol — Shodan may fingerprint it as "bolt" service. FP risk on port 7474 + `neo4j_version` is very low. Community edition lacks enterprise RBAC — all graph data accessible to any authenticated (or unauthenticated) connection.

---

## Apache Kafka (REST Proxy)

**Category:** Distributed Message Bus / AI pipeline event stream
**Default Ports:** 9092 (native Kafka binary protocol), 8082 (Confluent REST Proxy HTTP), 2181 (ZooKeeper — legacy), 9093 (TLS), 9094 (SASL)
**Auth Default:** off — Kafka ships with no authentication or authorization enabled. The REST Proxy (port 8082) has no auth by default: "the server starts bound to port 8082" and auth is explicitly opt-in. ZooKeeper on 2181 is unauthenticated by default. When REST Proxy auth is disabled, broker ACLs are bypassed entirely.
**Shodan Dork (primary):** `port:8082 "kafka" http.status:200`
**Shodan Dork (secondary):** `port:8082 "KafkaTopicList"`
**Verification Probe:** `GET /topics` → 200 + JSON array of topic names (v1/v2 API). `GET /v3/clusters` → 200 + JSON with `"kind":"KafkaClusterList"` (v3 API). Either confirms unauthenticated access.
**Data Exposure Class:** Full topic enumeration — reveals all message stream names (business process topology). `GET /topics/{topic}` lists partition count, replication factor. Consumer group access via `GET /consumers` enables message replay. In AI pipelines: real-time feature computation events, model inference requests, training data pipelines, user behavior streams. Native protocol on 9092 (unauthenticated) allows producing/consuming all messages — not HTTP-scannable but high-impact.
**Known CVEs:** CVE-2025-27817 — SSRF + arbitrary file read via untrusted SASL/OAUTHBEARER configuration in Kafka client. CVE-2018-17196 — auth bypass in Kafka (older). ZooKeeper CVEs: multiple deserialization RCEs on port 2181.
**Default Credentials:** none
**Notes:** The REST Proxy is the HTTP-scannable surface — native Kafka on 9092 is binary TCP and harder to fingerprint. `KafkaTopicList` appears in the `"kind"` field of the v3 API response — useful Shodan body dork. Port 9092 being open on Shodan with no auth means any Kafka client can produce/consume — no REST proxy needed. ZooKeeper on 2181 is a separate high-value target: unauthenticated `ls /` via Zookeeper CLI enumerates the entire Kafka cluster topology.

---

## Apache Flink

**Category:** Stream Processing Engine / AI real-time feature computation
**Default Ports:** 8081 (REST API + Web Dashboard)
**Auth Default:** off — "the REST endpoint does not authenticate the client by default, meaning the server will accept connections from any client." The dashboard and all REST API endpoints are unauthenticated out of the box. Flink docs recommend a sidecar proxy for auth.
**Shodan Dork (primary):** `port:8081 "flink-version"`
**Shodan Dork (secondary):** `http.title:"Apache Flink Web Dashboard" port:8081`
**Verification Probe:** `GET /config` → 200 + JSON containing `"flink-version":"X.Y.Z"` and `"flink-revision":"..."`. `GET /jobs/overview` → 200 + JSON with `"jobs"` array containing running job states.
**Data Exposure Class:** Full visibility into running streaming jobs — job names reveal pipeline purpose (e.g., "user-feature-computation", "model-inference-logger"). `GET /jobmanager/config` exposes full cluster configuration as key-value pairs — may include Kafka brokers, database connection strings, S3 bucket names, AWS credentials. `GET /jobmanager/environment` exposes JVM classpath, revealing installed libraries and internal paths.
**Known CVEs:** CVE-2020-17518 — path traversal via REST API file upload (arbitrary file write). CVE-2020-17519 — arbitrary file read via REST API (CVSS 7.5, widely exploited). Both affect Flink <= 1.11.2. CVE-2023-41834 — log injection / HTTP response splitting.
**Default Credentials:** none
**Notes:** CVE-2020-17519 is well-known and actively scanned — unpatched Flink instances at port 8081 are high-priority targets. The `flink-version` field in the `/config` response is a reliable banner signal. The web dashboard at port 8081 is fully functional without auth — cancel jobs, trigger savepoints, upload JARs. JAR upload endpoint (`POST /jars/upload`) enables remote code execution on unpatched instances.

---

## Spark History Server

**Category:** Apache Spark Job History / AI training pipeline visibility
**Default Ports:** 18080 (Spark History Server web UI + REST API)
**Auth Default:** off — "Security features like authentication are not enabled by default in Apache Spark." The history server web UI and REST API at port 18080 are fully accessible without credentials in the default configuration.
**Shodan Dork (primary):** `port:18080 "Spark History Server"`
**Shodan Dork (secondary):** `http.title:"History Server" port:18080`
**Verification Probe:** `GET /api/v1/applications` → 200 + JSON array of Spark application records with `id`, `name`, `attempts` fields. `GET /` → 200 + HTML containing "Spark History Server" in page body.
**Data Exposure Class:** Full Spark job history — application names reveal pipeline structure and business logic (e.g., "daily-feature-recompute", "model-training-run-2026-05-27"). Executor logs accessible via `GET /api/v1/applications/{appId}/executors` — may contain data samples in log output. Environment variables from Spark jobs available via `GET /api/v1/applications/{appId}/environment` — AWS keys, database passwords, Databricks tokens stored as Spark config properties are exposed here. Databricks-adjacent deployments using open-source Spark history servers are a high-value target.
**Known CVEs:** No direct CVEs for the History Server itself. Risk is unauthenticated config/log exposure. Databricks uses a managed variant that is not externally exposed.
**Default Credentials:** none
**Notes:** Port 18080 is somewhat distinctive — fewer other services use it. The `"Spark History Server"` string appears in the HTML page title and HTTP response body. The `/api/v1/applications/{appId}/environment` endpoint is the highest-value probe: Spark configuration includes `spark.hadoop.*` properties which often contain AWS access keys, S3 bucket names, Hive metastore passwords, and Databricks personal access tokens. FP risk: Hadoop YARN also runs services on 18080 in some configurations.

---

## Trino / Presto

**Category:** Distributed SQL Engine / AI/ML data lake query layer
**Default Ports:** 8080 (HTTP REST API + Web UI), 8443 (HTTPS)
**Auth Default:** off — "Trino runs with no security by default." The coordinator listens on port 8080 without any authentication, authorization, or TLS. All query submission, metadata browsing, and result retrieval endpoints are open.
**Shodan Dork (primary):** `port:8080 "Trino" http.status:200`
**Shodan Dork (secondary):** `port:8080 "/v1/info" "nodeVersion"`
**Verification Probe:** `GET /v1/info` → 200 + JSON with `"nodeVersion":{"version":"X.Y.Z"}` and `"starting":false`. `GET /ui/` → 200 + Trino Web UI HTML.
**Data Exposure Class:** Full SQL query access to any connected data source — S3 data lakes, Hive metastore, Delta Lake, Iceberg tables, relational databases via connectors. In AI/ML stacks: training datasets, feature tables, model evaluation results, experiment tracking tables. `GET /v1/query` lists all running and recently completed queries — reveals query patterns and data schema. `GET /v1/cluster` exposes cluster topology. Query submission via `POST /v1/statement` requires no auth on default install.
**Known CVEs:** CVE-2020-15087 — Presto (pre-Trino rename) auth bypass. No high-severity standalone Trino CVEs for the HTTP interface; the primary risk is the no-auth default configuration. Dependency CVEs exist (see GitHub issue #6769).
**Default Credentials:** none
**Notes:** Port 8080 has high collision risk with other services. Use `"Trino"` body string or `"nodeVersion"` field for precision. Presto (Facebook fork) uses the same port and similar API surface — queries targeting Trino dorks will also catch Presto. The `/v1/info` endpoint is specifically designed as an unauthenticated health check endpoint. `GET /v1/query/{queryId}` exposes full query text and results for any query ID — no auth required on default installs. High FP risk on port 8080 — always use body/header discriminators.

---

## Delta Sharing Server

**Category:** Open Data Sharing Protocol / Cross-platform data lake sharing
**Default Ports:** 8080 (reference server HTTP REST)
**Auth Default:** bearer-token — the Delta Sharing Protocol requires Bearer token authentication for all API calls. However, the reference open-source server (`delta-io/delta-sharing`) can be configured with a `bearer_token_providers` list, and misconfigured deployments may use static tokens that are widely shared or embedded in client configs. Token lifetime can be set to 0 (never expire).
**Shodan Dork (primary):** `port:8080 "delta-sharing"`
**Shodan Dork (secondary):** `port:8080 "/shares" "application/json"`
**Verification Probe:** `GET /shares` with `Authorization: Bearer {token}` → 200 + JSON `{"items":[{"name":"..."}]}` listing all shares. Without token → 401. Misconfigured with empty-string token or demo token from docs: `GET /shares` with `Authorization: Bearer faaie590-f132-4954-8571-d5b5b8` (example from docs).
**Data Exposure Class:** With valid bearer token: list all shares (`GET /shares`), list schemas (`GET /shares/{share}/schemas`), list tables (`GET /shares/{share}/schemas/{schema}/tables`), query table data (`GET /shares/{share}/schemas/{schema}/tables/{table}/query`). In AI/ML context: Delta Lake training datasets, feature tables, model evaluation sets shared across organizations. Token misconfiguration is the primary risk — static tokens in config files, documentation examples used in production, or tokens with zero expiry.
**Known CVEs:** No standalone CVEs for the reference server. Protocol-level: token management and IP allowlist bypass risks documented by Databricks.
**Default Credentials:** Static bearer token set by operator; example tokens appear in documentation and may be used in production
**Notes:** Delta Sharing is Databricks-originated but the reference server is open-source at `delta-io/delta-sharing`. Production Databricks Unity Catalog uses this protocol with proper OAuth. Self-hosted reference server deployments are the exposure surface. The `delta-sharing` string in HTTP responses is a good body discriminator. Tokens with zero expiry (`tokenLifetimeDurationInMinutes: 0`) never rotate — if leaked, permanent access. Shodan population expected very small.
