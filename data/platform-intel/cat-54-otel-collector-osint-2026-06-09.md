# Cat-54 OpenTelemetry / Distributed Tracing — Pre-Assessment OSINT (2026-06-09)

**Slug:** `cat-54-opentelemetry-collector`
**Tier:** Observability substrate (telemetry-ingest + distributed-tracing backends)
**Researcher:** Nicholas Kloster / NuClide
**Wardrobe outfit:** `ai-infra-hunt` (13 atoms; T0028 / T0188 / K0342 / S0001 / S0051 / T0247 / K0107 / K0118)
**DCWF roles:** 672 (AI T&E) + 733 (AI Risk / Ethics)
**Thesis target:** auth-on-default thesis — substrate-monitoring tier, Insight #88 generalization (scrape-topology = operator org chart).

---

## Why this category

The substrate-monitoring tier (Cat-46c VictoriaMetrics, Cat-46d Prometheus, Cat-02 Chroma) has produced **#88 (scrape topology = operator org chart)** and **#87 (canary persistence)**. The tracing tier is the next test case: if the same auth-off-default pattern reproduces in the OTel / Jaeger / Tempo / SigNoz / Zipkin substrate, the insight generalizes from scrape-config to trace-graph.

NuClide priors on this corpus:
- OTel Collector — **auth-off across every receiver and extension** by code design. Three CVEs on the binary itself; only ~one population-scale public mention (the CVE-2024-36129 blog) and **no published Census/Shodan/Hadrian survey**. Greenfield.
- Jaeger — **zero built-in auth**; documented as a reverse-proxy concern. No CVE filed for "ships unauth" because it is intentional. **No population-scale unauth survey known.**
- Grafana Tempo — `multitenancy_enabled: false` default; multitenancy is a routing label, not auth. CVE-2026-28377 confirms `/status/config` as a credential-leak surface.
- SigNoz — **first-registrant-becomes-admin window** from t=0; `am.OpenAccess(aH.registerUser)` in source; zero published GHSAs.
- Zipkin — **zero product GHSAs** (no auth to patch); shrinking but legacy population in Spring Boot / Istio / Dapr shops; OTel deprecating Zipkin exporters Dec 2025.

Hypothesis: a measurable fraction of internet-exposed deployments in each platform ship unauth at default, and a non-trivial subpopulation will be co-deployed with their storage backend (ES 9200, ClickHouse 8123, Cassandra 9042) unauth on the same IP.

---

## 1. Auth defaults — synthesis across the five platforms

| Platform | Auth default | Documented as feature? | First-claim model |
|---|---|---|---|
| OTel Collector | none (any receiver / any extension) | yes — opt-in `auth:` extensions | n/a |
| Jaeger | none (Query UI 16686 + all collectors) | yes — "no built-in auth", OAuth-proxy doc | n/a |
| Grafana Tempo | none ("does not come with any included authentication layer", verbatim) | yes — multitenancy is NOT auth | n/a (X-Scope-OrgID is unsigned routing) |
| SigNoz | open registration window | implicit — UI lets first random claim admin | first POST to `/api/v1/register` wins until v0.112.0 root-user env opt-in |
| Zipkin | none (UI + API) | yes — "no built-in authentication in the UI" | n/a |

All five sit on the auth-off-default side of Insight #40. None of them have a built-in auth tier in the binary; all five route the operator to an external reverse proxy (HAProxy / NGINX / OAuth2-proxy / Pomerium / OpenShift OAuth proxy / Apache httpd). The population-level question is how many operators reach for that doc.

---

## 2. Ranked dorks (cross-platform, with FP risk per Insight #15)

Tier-1 (low FP, single-platform-specific):

1. `http.html:"Trace Spans" port:55679` — OTel zPages tracez (zero FP; vendor-unique string).
2. `http.html:"otelcol_receiver_accepted_spans"` — OTel Collector self-metrics prefix (zero FP; binary self-names).
3. `http.title:"Jaeger UI"` — Jaeger UI (project-unique title; verify with `/api/services` envelope).
4. `http.html:"webpackJsonpzipkin-lens"` — Zipkin Lens-era webpack bundle (zero FP).
5. `http.html:"environment" http.html:"defaultLookback" http.html:"queryLimit"` — Zipkin `/config.json` four-key conjunct (low FP).
6. `http.title:"SigNoz"` — SigNoz frontend (project-unique).
7. `http.html:"echo" port:3200 http.status:200` — Tempo `/api/echo` (medium FP; confirm with body_exact `echo`, header_absent `Server`).
8. `port:3200 http.html:"tempo_ingester" http.html:"tempo_distributor"` — Tempo self-metrics + service-list conjunct.

Tier-2 (medium FP, requires conjunctive verification at Step 0c scanner):

9. `port:4318 http.html:"Method Not Allowed"` — OTel Collector OTLP-HTTP GET 405 (medium-high FP; Jaeger and Tempo both accept OTLP on 4318).
10. `port:16686 http.status:200` — Jaeger Query port (medium FP).
11. `port:9411 http.status:200` — Zipkin port (high FP; needs schema confirmation).

Null-result handling per `feedback-shodan-playwright-only`: Shodan harvest runs through Playwright in-page fetch only (API key dead). Every dork that returns 0 is logged in `shodan/query-log.md` with the count, and a variant is generated (Censys CT-log fallback in Step 0b for HTML-body filters that miss).

---

## 3. Verification primitives (one per platform — the load-bearing Step 3v)

Each platform has a single read-only request that proves identity + auth-state + populated-state simultaneously. Per Insight #16 (200 = identity, not auth), every primitive is conjunctively anchored on a data-layer shape.

| Platform | Primitive | Pass condition |
|---|---|---|
| OTel Collector | `POST /v1/traces` w/ body `{"resourceSpans":[]}` | HTTP 200, body `{}` or `{"partialSuccess":{}}` — OTLP spec compliant unauth ingest |
| OTel Collector (read) | `GET /debug/servicez` (zpages 55679) | HTTP 200, body contains "Trace Spans" / build info |
| Jaeger | `GET /api/services` | HTTP 200, JSON `{data:[...],total:N,limit:0,offset:0,errors:null}`, `data` array length ≥ 1 |
| Tempo | `GET /api/echo` + `GET /api/search/tags` | echo: 200 + body exact `echo` + header_absent Server; tags: 200 + JSON with `tagNames:[...]` length ≥ 1 |
| SigNoz | `GET /api/v1/version` | HTTP 200, JSON `{version, ee, setup_completed}`; `setup_completed:false` = open registration window (DO NOT POST `/register`) |
| Zipkin | `GET /api/v2/services` | HTTP 200, Content-Type application/json, bare JSON array of strings, length ≥ 1 (NOT `{data:[...]}` Jaeger envelope) |

Restraint anchor: every primitive is a metadata-only read. **Names ARE the finding.** No span body reads, no trace bulk-pull, no SigNoz registration POST. PII risk through observability tier is real (gen_ai.prompt / gen_ai.completion / db.statement / http.url with tokens) — confirmed once on the first populated host, schema-documented, never bulk-extracted.

---

## 4. Shadow-port priorities (cross-platform synthesis)

The headline shadow target depends on the front-door platform:

| Front door | Top shadow targets (in order) | Why |
|---|---|---|
| OTel Collector (any port) | 13133, 55679, 8888 (Collector itself); then 16686, 3200, 9090, 3000 | OTel cluster confirmation, then co-deployed observability stack |
| Jaeger Query 16686 | **9200 Elasticsearch** (the prize); 9300, 9042, 9092 | Raw `jaeger-span-*` index — bypass Query, full corpus |
| Grafana Tempo 3200 | **3000 Grafana**, **3100 Loki**, **9009 Mimir** (LGTM rosette); then 9000/9001 MinIO | LGTM stack co-location is an unambiguous operator attribution signature |
| SigNoz 8080 | **8123 ClickHouse HTTP** (the prize), 9000 ClickHouse native; then 4317/4318, 9093 | Raw `signoz_traces` / `signoz_logs` / `signoz_metrics` databases bypass query-service |
| Zipkin 9411 | **9200 Elasticsearch**, 5601 Kibana; then 9042 Cassandra, 3306 MySQL; then 8080 Spring Boot Actuator | Storage backend (ES dominant in 2026) holds raw spans |

The cross-platform pattern: **the storage backend is the prize on every tracing/observability platform.** Each platform's Query/UI layer exposes a curated subset; the underlying store is the full corpus. On every confirmed-unauth host, Stage 0c scanner must sweep at minimum 9200, 9300, 9042, 8123, 9000.

---

## 5. CVE coverage scope

OTel Collector lane:
- CVE-2024-36129 (7.5 H) — confighttp/configgrpc decompression bomb DoS, fixed 0.102.1
- CVE-2024-45043 (5.3 M) — awsfirehosereceiver silently ignores `access_key`, fixed 0.108.0

Jaeger:
- CVE-2022-25975 — XSS in KeyValuesTable (UI <1.31.0)
- GHSA-2w8w-qhg4-f78j — Stored XSS via tag content (2023-07-11)
- CVE-2024-24788 — Transitive Go stdlib DNS DoS
- CVE-2025-15467 — OpenSSL stack BoF in Alpine base of v2 image

Tempo:
- CVE-2026-28377 (7.5 H, PR:N) — S3 SSE-C key plaintext via `/status/config` (pre-2.10.3) — **the cleanest credential-leak in this category**

SigNoz:
- Zero published GHSAs as of 2026-06-09 (clean field — first-publisher opportunity)

Zipkin:
- Zero product-code GHSAs (auth-on-default thesis confirmed: nothing to patch when there's no auth)
- All published CVEs transitive (gson, Log4Shell, Netty, Kafka, jackson-databind)

---

## 6. Insight pre-write candidates for the survey

1. **Insight #88 generalization test** — does scrape-topology-as-org-chart hold on the trace tier? `/api/services` (Jaeger), `/status/services` (Tempo), `/api/v2/services` (Zipkin), `/api/v1/services` (SigNoz) all return service-graph topology unauth-by-default. Predicted: yes, the topology-leak pattern generalizes; the unit shifts from scrape-config to service-list, but the operator-org-chart property is the same.
2. **Cross-platform storage-backend co-deployment** — does the storage backend (ES, ClickHouse, Cassandra) ship unauth on the same IP when the front-door tracer ships unauth? Predicted: yes, at non-trivial rate, because the network-layer reasoning is identical (operator who exposes 16686 publicly is the operator who exposed 9200 publicly).
3. **OTel Collector identity-by-metric-prefix** — `otelcol_*` Prometheus prefix as a single-string identification primitive that survives every receiver/extension being off. Most economical single-string ID across the population.
4. **Open registration window as a verification state** — SigNoz's `setup_completed:false` is the first NuClide-observed example of an auth-state machine where the verification primitive reads a *temporal* state (window open NOW), not a binary unauth/auth. Distinct from `signUpDisabled:false` (Airflow) because Airflow is "anyone can register"; SigNoz is "first to register wins admin."
5. **OTel collector front-door + Tempo/Jaeger back-door inversion** — predicted overlap rate where one host runs both the ingest tier (4317/4318) and the storage tier (3200/16686) — the all-in-one quickstart pattern. If common, the finding's blast radius is the full inference-instrumented data path on that host.

---

## 7. Tome corpus state

Written this run:
- `~/tome/platforms/opentelemetry-collector.json`
- `~/tome/platforms/jaeger.json`
- `~/tome/platforms/grafana-tempo.json`
- `~/tome/platforms/signoz.json`
- `~/tome/platforms/zipkin.json`

All five marked `sources[] = CANDIDATE` until Stage 3v verification produces a 200-with-populated-data on a live host. No CONFIRMED promotion before that.

---

## 8. What's next (chain pickup)

- Stage 0: Playwright in-page fetch on the Tier-1 dorks; log every dork and count.
- Stage 0b: Censys CT-log delta for the HTML-body filters that miss Shodan.
- Stage 0c: scanner full-handshake banner on the harvest — liveness, version, dork-FP strip, shadow ports.
- Stage 0d: aimap fingerprint scaffolds from tome probe configs (5 new fingerprints).
- Stages 1a–3v: VisorPlus + aimap + favicon + agent-logging + VisorCAS + VisorGraph + dev-browser + profile + VERIFY.
- Stages 4–13: ledger, score, corpus, RAG, controlled VisorAgent, report, findings-breakdown, push.

Restraint posture is set: metadata-only reads, names ARE the finding, no SigNoz registration POSTs, no Tempo/Jaeger trace-body pulls beyond a single severity-confirmation sample per host.
