# Classical ML & Auxiliary Model Services — Stage-1 Pre-Assessment OSINT

_Category: Classical ML & Auxiliary Model Services (recommenders / ranking / fraud-anomaly). Scope: NARROW, purpose-built only (excludes generic model-servers — Seldon/KServe/BentoML/MLServer — which are the model-serving-registry survey)._

_Date: 2026-05-31 · Method: 3 parallel Stage-1 OSINT agents (Recommenders / Ranking-LTR / Anomaly-Fraud), six research lanes each, primary-source-cited. Web tools confirmed working in all three; `api.github.com` MCP was down so all GitHub claims came via WebFetch on raw source files._

---

## Thesis verdict

**Strong confirmation set.** Of the nine platforms with a fingerprintable network surface, eight ship auth OFF by default; one (Marble) ships auth ON. The lone counter-example is the tell: the discriminator is **audience**, not function. A research/RSE convenience tool (django-river-ml `DISABLE_AUTHENTICATION: True`, Gorse empty-credential-string-as-open, Metarank no-auth-code-at-all) defaults open; a commercial AML product (Marble, JWT+Firebase required at boot) defaults closed. This sharpens **Insight #40** (auth-on-default strengthens under commercial/disclosure pressure): the pressure operates across tools of equal function, not only across versions of one tool.

The strongest source-verified confirmations (primary source, not docs prose):
- **Gorse** — `master/rest.go` treats `""` credentials as "access granted" at three gates (`checkLogin`, `checkAdmin`, `AuthFilter`); config defaults all empty.
- **Metarank** — `Serve.scala` route assembly has no auth middleware anywhere; auth-absent by design.
- **Vespa self-hosted** — "By default, the container allows unauthenticated writes to, and reads from, the Vespa installation" (verbatim, securing-your-installation docs).
- **Solr** (LTR host) — `blockUnknown` defaults false → "not requiring authentication at all" (verbatim).

---

## Fingerprintable surfaces (the survey population)

| Platform | Ports | Default auth | Severity | Shodan posture | Verification primitive |
|---|---|---|---|---|---|
| **Gorse** | 8088 dash / 8087 REST / 8086 gRPC / 8089 worker | OFF (empty creds = open, source-verified) | HIGH (data) → CRITICAL surface (`/api/dump`,`/api/purge`) | **Strong passive** — `http.title:"Gorse Dashboard"` | `GET /api/dashboard/userinfo` → body `null` = unauth |
| **Vespa query-node** | 8080 (+19071 config) | OFF (verbatim) | **CRITICAL** — read+write doc store, `vespa visit` bulk export | Good JSON dork (`coverage.documents`+`degraded`) | `GET /search/?yql=...&hits=1` → `root.coverage.documents>0` |
| **Metarank** | 8080 | absent by design | HIGH — `/feedback` poison + `/train` weight read | **aimap-primary, Shodan-thin** (generic 8080) | `POST /train/{m}` → JSON w/ `features`,`iterations`,`sizeBytes` |
| **TF Serving (TFRS)** | 8501 REST / 8500 gRPC | OFF (`InsecureServerCredentials`) | MED-HIGH (unauth inference + schema leak) | Good dork (`model_version_status`; unique 404 body) | `GET /v1/models/{m}/metadata` → `model_spec`+`tensorflow/serving/predict` |
| **django-river-ml** | 8000 | OFF (`DISABLE_AUTHENTICATION: True`) | HIGH — model enum + write + SSE stream | `{"models":[` JSON on Django | `GET /api/models` → top-level `models` array |
| **Cornac serving** | 8080 / 5000 | OFF (no auth code) | MED — `/recommend` + unauth `POST /feedback` | weak passive (loopback default; active-probe-favored) | `GET /recommend?uid=1&k=1` → `recommendations`+nested `query.uid` |
| **Solr-LTR** | 8983 (+ZK 2181) | inherits Solr (OFF) | **HIGH→CRIT** — trusted-configset RCE chain (CVE-2020-13957 class) | LTR extension on existing Solr fp | `GET /solr/{c}/schema/feature-store` → `managedList` |
| **ES-LTR** | 9200 | inherits ES (OFF on OSS/older) | HIGH | `.ltrstore` / `_ltr` markers | `GET /_ltr/_featureset` → feature-set list |
| **Marble** (checkmarble) | 8080 / 3000 | **ON** (JWT+Firebase at boot) | LOW default; HIGH only if `/debug/pprof/` left enabled | favicon + `yente`+`motiva` co-deploy | `GET /debug/pprof/` 200 = profiling misconfig |

**Existing aimap coverage is not overlapped.** Vespa `/state/v1`→`config-server` and Solr `/solr/admin/info/system`→`solr-spec-version` are distinct paths/keys from the new query-node / LTR / Gorse / Cornac / TF-Serving probes. All new specs are additive; no dedup needed. The Vespa-query-node and Solr-LTR specs are deliberate extensions that catch what the existing config-server / base-Solr probes miss.

---

## Shodan-dark / library-only (the negative space — itself a finding)

| Tool | Why dark |
|---|---|
| PyOD | library; ships only a stdio MCP server (non-default HTTP), no listening socket |
| River (core) | library; "wrap in Flask/FastAPI yourself" — ships no server |
| PySAD | library; import-and-loop, no API |
| Alibi-Detect (standalone) | library; reaches network only via MLServer (out of scope); AD signal = `fraud`/`anomaly`/`outlier`/`drift` string in V2 model-name metadata |
| RecBole | pure PyTorch library; package tree has no serving/api/web module |
| **Vowpal Wabbit daemon** | `:26542` raw TCP, **emits no banner on connect** — Shodan indexes "open port, no data" (matches the SYN-ACK-only pattern). Needs zgrab2/tiptoe full-handshake sending a newline-terminated VW example line. Seed-only `port:26542`. |

The anomaly/fraud sub-class is structurally Shodan-dark by construction: the detector rarely owns a socket. To survey it, pivot from "find the AD tool" to "find the carrier (model server) and read the model NAME" — the AD signal lives in operator-chosen metadata, not a vendor banner.

---

## Consolidated Shodan dork candidates (DESIGN — run via Playwright, log every result)

Ranked, small+niche, vendor-unique JSON or multi-token. No single-token title dorks. FP-risk noted.

| # | Platform | Dork | Expected signal | FP-risk |
|---|---|---|---|---|
| 1 | Gorse | `http.title:"Gorse Dashboard"` | exact dashboard `<title>` | LOW — vendor-unique |
| 2 | Gorse | `http.html:"Gorse Dashboard" http.html:"fontawesome.com/releases/v7.0.0"` | title + FA CDN pin | LOW — two-token |
| 3 | Gorse | `port:8087 http.html:"/api/health/live"` | server REST liveness | MED — needs port anchor |
| 4 | Vespa-q | `http.html:"\"coverage\"" http.html:"\"documents\"" http.html:"\"degraded\"" port:8080` | search-result coverage object | MED — `degraded` sibling tightens |
| 5 | Vespa-q | `http.html:"/document/v1/" http.html:"pathId"` | document API + pathId | LOW-MED |
| 6 | TF-Serving | `port:8501 http.html:"model_version_status"` | REST status JSON key | LOW — TF-unique |
| 7 | TF-Serving | `http.html:"Could not find any versions of model"` | distinctive 404 body | LOW — fires without knowing a model name |
| 8 | django-river-ml | `http.html:"models" port:8000 "django"` (+ body `"models":[`) | unauth River model-list on Django | MED — require array shape |
| 9 | Solr-LTR | `http.html:"schema/feature-store"` | Solr LTR managed-resource path | LOW — LTR-specific |
| 10 | Solr-LTR | `http.html:"ManagedFeatureStore"` OR `http.html:"_DEFAULT_"` port:8983 | LTR class / default store name | MED |
| 11 | ES-LTR | `http.html:".ltrstore"` | hidden LTR index name | LOW — LTR-unique |
| 12 | ES-LTR | `http.html:"_ltr" http.html:"featureset"` port:9200 | LTR endpoint + term | LOW-MED |
| 13 | Cornac | `port:8080 http.html:"remove_seen"` | Cornac-specific param | MED — crawl-dependent; active-probe-favored |
| 14 | Marble | `"yente" "motiva" port:8080` | distinctive co-deploy stack | LOW-MED — niche combo |
| 15 | VW daemon | `port:26542` | open port, empty banner | HIGH — **seed only, not a classifier** |

**Strategy notes from the agents:**
- **Shodan-primary:** Gorse, Vespa-q, TF-Serving, Solr-LTR, ES-LTR (good narrow JSON/title dorks).
- **aimap-primary / Shodan-thin:** Metarank (generic 8080, no brand body — seed from Redis-6379 co-location or aimap active probe), Cornac (richest tokens live in query-path bodies Shodan won't auto-crawl).
- **Shodan-dark:** VW daemon (seed-only port), all libraries (excluded from population set).
- **Dork-population-bias caution:** Gorse/Cornac/TF-Serving default to plain HTTP and loopback/localhost binds; the exposed tier is biased toward containerized `0.0.0.0` deployments. A `ssl:`/cert dork would BLIND us to this tier (mirror of the Cat-29 `ssl:` subpopulation insight). Favor port + body-JSON dorks, not cert dorks, for this cluster.

---

## aimap fingerprint specs (for the build phase — conjunctive, never naked body_contains)

```
Gorse-Master      ports[8088,8087,8086,8089]  /api/dashboard/userinfo {200, body=="null"}  + / {200,"Gorse Dashboard"}  HIGH
Vespa-QueryNode   ports[8080]                  /search/?yql=...&hits=0 {200, root.coverage.documents, root.coverage.degraded}  CRITICAL  (disambiguate from config-server fp)
Metarank          ports[8080]                  /health {200} + /rank/ {405 method-not-allowed}  HIGH  (verify via POST /train shape)
TensorFlow-Serving ports[8501,8500]            /v1/models/model/metadata {200, model_spec, "tensorflow/serving/predict", signature_def}  MED
django-river-ml   ports[8000]                  /api/models {200, json_field "models" array}  HIGH
Cornac-Serving    ports[8080,5000]             /recommend?uid=1&k=1 {200, "recommendations", query.uid, "remove_seen"}  MED
Elasticsearch-LTR ports[9200]                  /_ltr {200, json_field "stores"}  HIGH
Solr-LTR          ports[8983]                  /solr/{c}/schema/feature-store {200, "managedList"}  HIGH  (prereq: enum collection)
checkmarble-marble ports[8080,3000]            /metrics {200,"go_goroutines","promhttp"} (opt-in); /debug/pprof/ {200}=misconfig  LOW default
mlserver-v2-anomaly ports[8080]                /v2 {200,"name","extensions"} -> /v2/models/{n} {200,"inputs","outputs"}; escalate if name~/(fraud|anomaly|outlier|drift)/  MED
VowpalWabbit-daemon ports[26542]               RAW TCP: send " 1 |f a b c\n" -> match /^-?\d+\.\d+/  MED  (needs raw-socket probe module, not HTTP)
```

Data-tier shadow-sweep ports per platform (IP-direct shadow on every confirmed host): Gorse→MySQL 3306 / Redis 6379 / Mongo 27017 / Postgres 5432 / ClickHouse 8123,9000. Metarank→Redis 6379, Prometheus 9090. Vespa→19071/19092. Solr-LTR→ZooKeeper 2181/9983. ES-LTR→9200/9300, Kibana 5601. Marble→PostGIS 5432, Elasticsearch 9200, yente 8080.

---

## UNVERIFIED — orchestrator must re-verify before asserting (do not propagate as fact)

1. **All CVE-absence claims** (Metarank, Vespa, VW, ES-LTR, Gorse, TF-Serving, Cornac) — CVE DBs were 403/empty to the fetchers. Re-query NVD directly. **CVE-2020-13957** (Solr configset RCE, CVSS ~7.5) needs NVD confirmation; it is the load-bearing CVE for the Solr-LTR RCE chain.
2. **Gorse `admin`/`password` legacy default** — a WebSearch result claimed it; `master` source says empty strings. Do NOT propagate `admin`/`password`; source says no-auth/empty. Diff `release-0.4` vs `master` if the historical default matters.
3. **Vespa `/ApplicationStatus`** — could not be sourced; canonical container status is `/state/v1/health`. Do not fingerprint on `/ApplicationStatus`.
4. **Favicon mmh3 hashes** (Gorse, Vespa, Marble frontend) — none computed; derive from a live `/favicon.ico` before any favicon dork.
5. **Exact aimap json_field wrapper keys** (`managedList`, `stores`, `root.coverage.degraded`, river `/api/stats` fields) — from doc-described shapes; confirm against a live or documented response sample before locking the fingerprint.
6. **ES-LTR auth posture by version** — ES 8.0+ enables security on fresh install; the OSS LTR plugin targets older/OSS. ES major version + distribution is the auth-determining variable.
7. **Metarank root `/` body** — whether it emits the brand string for a passive dork (Serve.scala suggests an unbranded 404).
8. **django-river-ml exact REST paths** — docs document the Python client; `/api/models` etc. inferred from `URL_PREFIX:"api"` + client methods. Confirm against `urls.py`/`riverapi/spec`.

---

## Insight candidates for the methodology ledger

1. **Sub-class-is-library:** anomaly/fraud ML is structurally Shodan-dark — the detector rarely owns a socket. Survey by finding the carrier (model server) and reading the model NAME. The carrier brands the surface; the payload is anonymous unless named (generalizes Insight #31).
2. **Auth-on-default split within one narrow category, by audience:** django-river-ml/Gorse/Metarank (research/convenience) default open; Marble (commercial AML) defaults closed. Same function, opposite default, outcome tracks audience — sharpens Insight #40 across tools of equal function.
3. **Metadata-shape as sensitivity leak:** V2 `/v2/models/{name}` `inputs.shape` leaks fraud-model feature-vector dimensionality; TF-Serving `/metadata` leaks full I/O schema. Schema-only sensitivity (no record exfil) — fits schema-recon bag-of-fields discipline.
4. **Poison-and-read chain (Metarank):** unauth `/feedback` (write) + `/train` (read weights back) is a higher-impact framing than "open dashboard" — the attacker shapes the model and reads the result.

---

## Sources (primary, retrieved this session)

gorse-io/gorse {config.toml, docker-compose.yml, master/rest.go, server/rest.go}, gorse-io/dashboard/index.html; PreferredAI/cornac/cornac/serving/app.py; RUCAIBox/RecBole package tree; tensorflow/serving g3doc/api_rest.md; metarank/metarank {Serve.scala, HealthApi.scala} + docs.metarank.ai; vespa.ai securing-your-installation / quickstart / state-v1 reference; VW daemon wiki; solr.apache.org LTR + auth reference (SOLR-14925 / CVE-2020-13957 / SOLR-16777); vsoch/django-river-ml settings module; selimfirat/pysad; SeldonIO/{MLServer,alibi-detect}; KServe V2 spec; checkmarble/marble docker-compose.yaml + docs.checkmarble.com.
