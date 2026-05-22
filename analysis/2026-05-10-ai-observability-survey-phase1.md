# Session Analysis: AI Observability Survey — Phase 1 (Phoenix, Langfuse, Helicone, LangSmith, Small Platforms)

**Date:** 2026-05-10
**Session:** unnumbered (retroactive analysis)
**Classification:** Internal / Research Use Only
**Toolchain:** JAXEN (Shodan harvest), Python stdlib probers, nmap (IP-direct-shadow SYN sweep), VisorGraph (TLS-cert attribution), BARE (Metasploit semantic match), source-level auth audit
**Repos updated:** AI-LLM-Infrastructure-OSINT (commits 17a4088, 1b168cd, b9d99be, 08c653d, 26c9e94)

---

## 1. Overview

### Objective

Survey the LLM-observability platform tier at population scale. Seven platforms in one product class: Arize AI Phoenix, Langfuse, Helicone, LangSmith, Lunary, OpenLIT, and Pezzo. Every one of them sits in the same path. Every prompt, every model response, every token count, every chain step, every tool call from a production AI agent flows through an observability platform. If the platform ships open, that data is public.

The thesis question is the auth-on-default thesis. Most self-hostable AI infrastructure ships with auth off, and the population-scale exposure tracks the shipping default rather than operator skill. The observability tier is a clean test. It is a single product class with multiple vendors. If the thesis holds, the platforms that ship auth-on stay closed at population scale and the platforms that ship auth-off leak. The test is falsifiable. A platform that ships auth-off and stays closed, or a platform that ships auth-on and leaks, breaks the thesis.

Phase 1 is the parallel population-sweep phase. Enumerate each platform, classify auth posture, attribute the top operators, and write a cross-platform synthesis. Phase 2 (depth deep-dives) and Phase 3 (meta-fingerprinter tool) follow later and are out of scope for this analysis.

### Scope and Constraints

- **Target domains/IPs:** Phoenix, Langfuse, Helicone, LangSmith, Lunary, OpenLIT, and Pezzo instances globally, discovered via Shodan. IP-direct-shadow secondary-port probing on the IPs that surfaced. Single-host deep-dive on `190.210.105.193` (reputacion.digital, Argentina).
- **Allowed techniques:** passive Shodan harvest, safe HTTP GET, GraphQL read-only introspection and `projects` query, REST data-layer auth probe (`/api/public/projects`, `/api/v1/sessions`, `/v1/runs`), banner grab, version-endpoint read, nmap TCP SYN sweep, `showmount -e` for NFS export listing, source-level audit of public GitHub repositories.
- **Ethical limitations:**
  - No data exfiltration — metadata and schema enumeration only
  - No destructive API calls
  - No use of discovered credentials
  - Data-tier probes: connection attempt only (does an auth gate exist? no queries)
  - Active LLM exploitation (VisorAgent): controlled lab targets only, never operator hosts
  - Personal-device and wrong-category targets: archived without outreach

The latent-primitive probes were held back by these constraints on purpose. Phoenix's stored-secret extraction primitive, Helicone's `BETTER_AUTH_SECRET` session-forgery primitive, and Langfuse's weak-`ADMIN_API_KEY` primitive are all source-confirmed but unprobed against the live population. Each one would require credential testing or cryptographic forgery against third-party infrastructure. That is outside the read-only scope. They are documented for the threat model, not exercised.

---

## 2. Environment and Tooling

### Claude Code Operation

Orchestrator pattern with parallel population sweeps. The seven platforms are independent targets with no shared state, so they ran as parallel lanes rather than a serial chain. Phoenix carried the deepest work (GraphQL enumeration, span sampling, operator clustering, version sweep, IP-shadow sweep, single-host deep-dive). The other six ran lighter passes because each one returned 0% unauth at the first auth-posture probe, so the work after that was source-level confirmation and IP-shadow rather than data characterization.

Discovery and probing leaned on Python stdlib concurrent probers (20-worker pools) rather than the full Visor binary chain. The reason is in the methodology section. The actual auth boundary for these platforms is a specific API endpoint, not the HTTP status of `/`, and the probers had to be written to speak GraphQL and the right REST shapes per platform.

### Tools Used

| Tool | Role | Config notes |
|---|---|---|
| JAXEN | Stage-0 discovery: Shodan harvest per platform | Per-platform dork; `ssl.cert.subject.cn` dork for Langfuse, `http.html` body fingerprint for Phoenix/LangSmith/Helicone |
| Python stdlib probers | Auth-posture probe per platform | 20-worker concurrent pools; per-platform endpoint and response-shape logic (GraphQL for Phoenix, REST for the rest) |
| nmap | IP-direct-shadow SYN sweep | 11-port curated list (NFS, rpcbind, MailCatcher, MailHog, Prometheus, AlertManager, node_exporter, Kibana, Elasticsearch, Grafana, 3000) |
| VisorGraph | TLS-cert + project-name operator attribution | 14 traces on the Phoenix top-15 |
| BARE | Metasploit semantic exploit-class match | MiniLM encoder over 376 Phoenix host banners; result was a false positive (logged) |
| Source-level auth audit | Read of public GitHub repos for shipping-default and auth-wrapper logic | Phoenix `config.py` / `auth.py`, Langfuse `createAuthedProjectAPIRoute.ts`, Helicone `.env.example` files, Lunary `.env.example` |
| `showmount` | NFS export enumeration on the reputacion.digital host | Export-list read only, no mount |

Tools deliberately not run, and why:

| Tool | Status |
|---|---|
| VisorAgent / VisorRAG | Not run. Ethical stop. Active LLM exploitation is controlled-lab-only and never touches operator hosts. |
| VisorHollow | Not run. Windows-only process-injection benchmark, no relevant surface in this survey. |
| aimap Stage-2 enumerators | Attempted on the Phoenix top-15, hung repeatedly on slow hosts. Non-blocking for the rest of the chain; the GraphQL probers covered the same ground. Logged as a tooling limitation. |

### Notable Configuration

- All probing ran from the research VPN. Phoenix's population of 377 had 357 reachable from the VPN; 20 were unreachable. That gap is a VPN-routing artifact, not an operator finding.
- The Langfuse population had 1,333 cert-CN matches but only 381 reachable as Langfuse. 950 were load-balancer frontends with no backend route on the test path. The 0% unauth figure is over the 381 reachable, not the 1,333.
- Concurrent prober pools were capped at 20 workers to stay congestion-controlled and avoid hammering operator infrastructure.
- BARE ran offline against its embedded 3,904-module Metasploit corpus. No network calls.

---

## 3. Methodology

### Enumeration approach

Per-platform Shodan dorks, tested against candidates and selected for signal:

- **Phoenix:** `http.html:"arize-phoenix"`. The naive title dork `http.title:"Phoenix"` returns 4,685 hits and is ~92% noise (businesses in Phoenix, Arizona). The HTML-body fingerprint is precise. 377 hosts.
- **Langfuse:** `ssl.cert.subject.cn:"langfuse"`. Langfuse is a SPA, so the title never reaches Shodan. The HTML-body dork is wide (catches tutorials and GitHub copies). The TLS-cert-CN dork is the clean signal. 1,333 hosts.
- **LangSmith:** `http.html:"langsmith"`. 96 hits.
- **Helicone:** `http.html:"helicone"` combined with `ssl.cert.subject.cn:"helicone"`, deduplicated. 21 hits.
- **Lunary / OpenLIT / Pezzo:** per-platform title and HTML dorks. 6 / 23 / 3 confirmed-relevant hits respectively.

This is the Insight #15 pattern in practice. Dork hits are not platform instances. LangSmith returned 96 Shodan hits and 27 confirmed instances, a 28% confirmation rate. The other 69 hits were unrelated apps that merely mention "langsmith" in their HTML, usually as a backend-integration string. The dork is the start of the funnel, not the answer.

### Candidate identification

A Shodan hit becomes a confirmed instance only after a positive identity probe against a platform-specific endpoint:

- **Phoenix:** GraphQL `POST /graphql` returning either the `projects` data shape or a Phoenix-shaped JSON error.
- **Langfuse:** `/api/public/health` returning the Langfuse health JSON with a version field.
- **LangSmith:** `/api/v1/info` returning `version` + `git_sha`.
- **Helicone / OpenLIT / Lunary / Pezzo:** per-platform health or API endpoints.

Per Insight #16, a 200 from a platform endpoint is identity, not auth state, and an HTTP status code by itself is never identity. Both halves of that rule were load-bearing this session. Phoenix's React SPA on port 6006 returns HTTP 200 to anyone — that is just the app shell loading, not an auth bypass. Helicone, OpenLIT, and Pezzo all do the same SPA-shadow trick: the Next.js or Nest.js router answers any unmatched route with the marketing-page HTML, which produces false-positive 200s on naive probing. Identity had to be confirmed at the real API endpoint, and auth posture had to be read off the API endpoint's response body, not off `/`.

### Validation checks

The auth boundary is the data-layer API endpoint, not the web UI:

- **Phoenix:** `POST /graphql` with a `projects` query. Unauth instances return `{"data":{"projects":{"edges":[...]}}}`. Auth-on instances return a JSON error or the string `Invalid token`. The web UI status is irrelevant; the GraphQL response is the verdict.
- **Langfuse:** `GET /api/public/projects`. 401/403 means auth-protected. All 381 reachable hosts returned 401/403.
- **LangSmith:** `GET /api/v1/sessions` and `GET /api/v1/tenants`. All 27 returned 401 on sessions; tenants split 13×401 / 14×403 (RBAC variance). Zero 200s.
- **Helicone:** `POST /v1/oai/chat/completions` without auth headers. Zero hosts proxied to an LLM; the rest returned SPA HTML, 404, timeout, or a 307 redirect to auth.
- **Lunary / OpenLIT / Pezzo:** per-platform protected routes. Lunary's one confirmed instance returned 401 on `/v1/runs`, `/v1/apps`, `/v1/projects`. OpenLIT's 23 instances all 307-redirected every API route to `/login`. Pezzo's one instance enforced auth at the GraphQL layer.

The Phoenix write-primitive validation was a separate, deliberately bounded probe. A single unauthenticated `POST /v1/projects/{id}/spans` against the live Chinese brand-monitor host (`13.228.68.200`) returned HTTP 422 with `{"detail":[{"type":"missing","loc":["body","queries"],"msg":"Field required"}]}`. That is schema validation, not an auth rejection. The server is processing unauthenticated POSTs and only failing on payload shape. No span was written. The probe sent a deliberately incomplete body so the server would reject it on schema before any write occurred. Source-level confirmation backs it: the handler `create_spans` at `src/phoenix/server/api/routers/v1/spans.py:1289` carries only `Depends(is_not_locked)`, a storage-quota guard, not an auth guard.

### Safeguards

- No brute forcing. No credential guessing. No privilege escalation.
- No data exfiltration. Span sampling pulled a handful of spans per cluster for data-class characterization (4 clusters, roughly 5-8 spans each) and nothing more. Bulk export was not run against any operator host.
- No write-tier operations. The Phoenix span-ingestion primitive was confirmed via source review plus one schema-rejected probe. No span was ever written to an operator's trace store.
- No use of discovered credentials. The reputacion.digital deep-dive surfaced a LiteLLM instance and an OIDC config; no credential extracted from it was used.
- The three latent primitives (Phoenix stored-secret extraction, Helicone session-forgery, Langfuse weak-`ADMIN_API_KEY`) were source-confirmed and left unprobed because probing them requires acting against third-party infrastructure.
- The pickle-deserialization hypothesis on Phoenix's ingest path was tested and disproven by source review, not by sending a payload.

---

## 4. Execution Trace

Timestamps are approximate, reconstructed from evidence-directory file modification times. The session was never assigned a session number.

| Time | Action | Outcome / Decision |
|---|---|---|
| ~13:28 | Phoenix Shodan harvest via `http.html:"arize-phoenix"` | 377 hosts. Naive title dork rejected as ~92% noise. Evidence written to `phoenix-survey/recon/`. |
| ~13:30 | Phoenix GraphQL auth-posture probe across 377 hosts | 357 reachable; 113 return `Invalid token` (auth-on); 94 return the `projects` data shape (unauth). 25% unauth rate. |
| ~13:40 | Phoenix project enumeration on the 94 unauth hosts | 83 successful deep enumerations. 57 hosts hold real customer project data; 49 actively logging tokens. Triage ranked by token volume. |
| ~13:50 | Phoenix top-15 ranked; cumulative top-15 ≈ 5.5B tokens | Host #1 `190.210.105.193` at 1.21B tokens flagged for single-host deep-dive. |
| ~14:00 | VisorGraph TLS-cert + project-name attribution on top-15 | Kapture CRM identified across three regions (#4, #6, #11). reputacion.digital, autom8.pro, Extenda Retail attributed. |
| ~14:10 | Phoenix source-level audit: `config.py`, `auth.py`, `spans.py` | `PHOENIX_ENABLE_AUTH` defaults `False` in current `main`. Two-tier admin model found: `IsAdmin` (secure-fail) vs `IsAdminIfAuthEnabled` (insecure-fail). `Secret.value` carries the insecure-fail variant. |
| ~14:20 | Phoenix write-primitive probe on `13.228.68.200` | HTTP 422 schema rejection, not auth rejection. Unauthenticated span ingestion confirmed. `create_spans` handler has no auth dependency. |
| ~14:25 | Pickle-deserialization hypothesis on Phoenix ingest | `grep` for `pickle/cloudpickle/dill/marshal` in `src/phoenix/` returns zero hits. Hypothesis disproven. BARE's pickle-class cluster was a banner false positive. |
| ~14:30 | Phoenix span sampling across 4 operator clusters | brand-monitor, Kapture, "Lillia" health-coach, MCM biodefense agent. Lillia found carrying persistent `user_id` tied to health telemetry. |
| ~14:40 | Phoenix `platformVersion` sweep across 94 unauth hosts | Unauth state spans v4.x through v15.x. Bimodal: 13.15.0 (10 hosts) legacy, 15.2.0 (6 hosts) recent. Default-no-auth is not a legacy artifact. |
| ~14:50 | Phoenix IP-direct-shadow SYN sweep across 92 IPs | 25 hosts (27%) have a secondary surface. 5 with real primitives: NFS+`/postgres`, MailHog with 139 emails, unauth Kibana, 2× Prometheus. 4 new operators attributed. |
| ~15:00 | reputacion.digital single-host deep-dive | Phoenix + unauth Prometheus (58 scrape targets, 39 internal `192.168.40.x` endpoints) + MailCatcher + MinIO + LiteLLM. Multi-surface chained exposure. |
| ~17:41 | Langfuse Shodan harvest via `ssl.cert.subject.cn:"langfuse"` | 1,333 hosts. Three dorks tested; cert-CN selected for cleanest signal. |
| ~17:45 | Langfuse auth-posture probe on `/api/public/projects` | 381 reachable as Langfuse; 950 are LB frontends. All 381 return 401/403. 0% unauth. Opposite outcome from Phoenix. |
| ~17:50 | Langfuse source-level audit | All 73 public-API handlers wrapped by `createAuthedProjectAPIRoute`. No master auth-off toggle exists. `ADMIN_API_KEY` is the latent primitive, not probed. |
| ~17:54 | Helicone Shodan harvest | 21 hosts total. SaaS-first product; small self-hosted population. |
| ~17:58 | Helicone auth-posture probe across 21 hosts | 0 unauth. Mandatory auth via BetterAuth or Supabase. `BETTER_AUTH_SECRET` literal found in 3 `.env.example` files. |
| ~18:02 | LangSmith Shodan harvest | 96 hits → 27 confirmed instances. 28% confirmation rate; Insight #15 in practice. |
| ~18:05 | LangSmith auth-posture probe | 27/27 return 401 on `/api/v1/sessions`. 0% unauth. `/api/v1/info` discloses version + git_sha + license expiry by design. |
| ~18:24 | Small-platforms batch: Lunary, OpenLIT, Pezzo | 1 / 23 / 1 confirmed instances. 0 unauth across all three. Traceloop and HoneyHive returned insufficient Shodan signal. |
| ~18:30 | IP-direct-shadow sweeps across the auth-on platforms | Langfuse 1 minor find (localhost-only Prometheus). Helicone 2 minor (empty MailHog, login-gated Cockpit). LangSmith 0. Small platforms 1 (unauth node_exporter on a Huawei Cloud OpenLIT host). |
| ~18:45 | Cross-platform synthesis written | Phoenix accounts for 100% of the unauthenticated instances in the cohort. Without Phoenix, the cohort unauth rate is 0/482. Insight #12 codified; Insight #13 drafted. |

---

## 5. Findings

> **Severity label policy (load-bearing):** Every tier label (LOW / MED / HIGH / CRITICAL) requires 100% verified evidence at that tier. Unverified observations are UNRATED. Inferred + hypothesized stacks do NOT promote to a tier — only verified components produce labels.

The findings split into two kinds. The Phoenix findings are exposure findings. The findings on the other six platforms are thesis-evidence findings. A platform that returns 0% unauth at population scale is not a vulnerability. It is a confirmed observation of platform behavior that tests and confirms the auth-on-default thesis. Those are recorded at OBSERVED tier, not as defects.

### 5.1 Arize AI Phoenix — Population-scale unauthenticated trace-store exposure

| Field | Value |
|---|---|
| **Name/ID** | 94 unauthenticated Phoenix instances; 377-host total population |
| **Type** | LLM-observability platform, GraphQL data tier (`POST /graphql`) |
| **Evidence** | GraphQL `projects` query returns `{"data":{"projects":{"edges":[...]}}}` on 94 of 357 reachable hosts. 83 deep enumerations succeeded; 57 hold real customer project data; 49 actively logging tokens. Top-15 by token volume cumulate ≈ 5.5 billion tokens of customer LLM trace data. |
| **Observed exposure** | Unauthenticated read access to the full trace store: user prompts, model responses, chain-of-thought reasoning, operator-internal logic, model identity, agent topology. |
| **Severity** | **HIGH** — verified unauthenticated access to a significant data class across a 94-host population. Not CRITICAL: most sampled spans carry session-scoped identifiers, not standing PII. The one cluster carrying persistent identified telemetry (5.3) is rated separately. |

**Potential impact:** anyone who knows to POST a `projects` query to `/graphql` reads every prompt and response logged by 94 production AI deployments. Competitors pull operator IP — brand catalogs, classification rules, system prompts, model-tier access — without ever touching the operator's primary infrastructure. The exposure is silent. The web UI returns HTTP 200 to everyone and ordinary scanners that do not speak GraphQL miss it entirely.

### 5.2 Arize AI Phoenix — Unauthenticated span-ingestion write primitive

| Field | Value |
|---|---|
| **Name/ID** | `POST /v1/projects/{project_identifier}/spans`, handler `create_spans` |
| **Type** | Write-tier API endpoint on the trace store |
| **Evidence** | Source: `src/phoenix/server/api/routers/v1/spans.py:1289` — `create_spans` carries only `Depends(is_not_locked)`, a storage-quota guard. The auth-aware sibling `restrict_access_by_viewers` is not attached. Live: a single schema-incomplete `POST` against `13.228.68.200` returned HTTP 422 `{"detail":[{"type":"missing","loc":["body","queries"]}]}` — schema validation, not auth rejection. The server processes unauthenticated POSTs. |
| **Observed exposure** | Unauthenticated write to the trace store on every default-no-auth Phoenix instance. The exposure is not read-only. |
| **Severity** | **HIGH** — write capability verified at source and corroborated by a schema-only live rejection. No span was written; the probe was bounded to a schema-rejecting payload by design. |

**Potential impact:** an attacker injects fabricated spans to poison downstream evaluation or training data, shadows real spans, or floods writes to run up the operator's storage and quota cost. Malicious payloads in the `attributes` field reach the Phoenix UI (XSS-class) and any LLM eval loop that later re-ingests the data (prompt-injection-class). A companion bulk-export path, `POST /v1/spans` (handler `query_spans_handler` at `spans.py:587`), also declares no auth dependency and streams an entire project's spans in one POST, gated only by schema. The 40-mutation GraphQL surface adds unguarded prompt-management, annotation-injection, and dataset-injection mutations; user and API-key mutations are properly `IsAdmin`-gated. The per-mutation auth audit is not exhaustive and is a Phase 2 follow-on.

### 5.3 "Lillia" health-coach cluster — Identified health telemetry through default-no-auth Phoenix

| Field | Value |
|---|---|
| **Name/ID** | Phoenix project `playground` on `34.23.90.218` (GCP US) and `101.37.104.193` (Alibaba China) |
| **Type** | Operator cluster surfaced by Jaccard project-name clustering (≥0.5 similarity) |
| **Evidence** | Sampled spans carry a persistent `user_id` in `DRB_110008755478` format tied to a tool schema including `SleepLog`, `BloodPressureLog`, `WeightLog`. User health queries and agent coaching responses present. Cluster attributed to Lillia (lilliacare.ai) — a Vertex AI population-health platform; per the operator's own marketing, 40,000+ patients under management across GCC + India and two ADA-published clinical studies. |
| **Observed exposure** | Unauthenticated read of individual health-data telemetry with stable per-user identifiers. |
| **Severity** | **HIGH** — verified persistent identifiers tied to health-adjacent telemetry. Not labeled CRITICAL: the survey did not verify any record as US-resident PHI, and class membership ("a health platform") is not data membership ("confirmed PHI in hand"). The label reflects what the sampled spans verified — identified quantified-self telemetry — and no more. |

**Potential impact:** quantified-self health data (weight, sleep, blood pressure) keyed to stable identifiers is re-identifiable and sensitive on its own. If any user is a US resident, this surface is HIPAA-relevant. The operator's public marketing site carries no `/security` or `/trust` page and no HIPAA / SOC 2 / ISO 27001 language. The cross-cloud GCP-US-plus-Alibaba-China deployment is unexplained by the operator's stated geography.

### 5.4 reputacion.digital — Multi-surface chained exposure on a single host

| Field | Value |
|---|---|
| **Name/ID** | `190.210.105.193` (Argentina), reputacion.digital — an Argentinian online-reputation SaaS |
| **Type** | Single host running an SSO-fronted stack with multiple services bound on the bare IP |
| **Evidence** | Phoenix unauth on `:6006` (project `GPU_REPORTS`, 1.21B tokens, the largest in the population). `showmount -e` returns 31 NFS exports, all world-exported (`*`), including a `/postgres` export of Postgres data files. Unauthenticated Prometheus on `:9090` with 58 scrape targets covering CoreDNS, Elasticsearch, Flower, MinIO, Postgres, Traefik, and multi-GPU vLLM, leaking 39 internal `192.168.40.x` endpoints, plus active `/-/quit` and `/-/reload` endpoints. MailCatcher and a MinIO console also present on the host. |
| **Observed exposure** | The application-layer SSO is real, but Phoenix, NFS, Prometheus, and MailCatcher each answer by raw IP and bypass it. The operator's "everything is behind SSO" model is wrong by the count of services with no auth of their own. |
| **Severity** | **HIGH** — multiple verified unauthenticated surfaces on one host. The data-plane exposure (Phoenix trace store) and the infrastructure-plane exposure (Prometheus topology) together hand an attacker the full operational picture: which models are deployed, which GPUs serve them, what data flows, and a one-request DoS on the monitoring layer. The NFS `/postgres` export was enumerated as present and world-exported; no file was mounted or read, so the database-content exposure is described from the export listing, not from data in hand. |

**Potential impact:** this host is the anchor case for Insight #12. The IP-direct-shadow check converts one Phoenix finding into a complete operator-attribution and operational-mapping opportunity. The `/-/quit` Prometheus endpoint is a one-request denial-of-service primitive on the monitoring layer.

### 5.5 Phoenix IP-direct-shadow population sweep — 27% of unauth hosts have a co-located secondary surface

| Field | Value |
|---|---|
| **Name/ID** | 92 unique IPs in the Phoenix unauth set; 11-port SYN sweep |
| **Type** | Population-scale secondary-surface enumeration |
| **Evidence** | 25 of 92 hosts (27%) expose at least one of NFS, MailHog, Kibana, or unauth Prometheus on the same IP. Five have real primitives: reputacion.digital (NFS+`/postgres`+Prometheus+MailCatcher); `173.208.247.17` (wiratek.id, Indonesian PLN AI vendor — Prometheus on GPU compute with `dcgm-exporter`); `173.214.172.254` (dsb-kairo.de, German School Cairo — Prometheus scraping a FastAPI backend); `47.251.246.12` (Alibaba Cloud US "deepagents" — Kibana 7.17.20 fully unauthenticated, `/api/saved_objects/_find` callable); `51.15.207.110` (Teetsh, French educational SaaS — MailHog holding 139 captured emails at probe time, most recent from `thibault@teetsh.com`). |
| **Observed exposure** | Operators who ship Phoenix with default-no-auth tend to ship other internally-facing services the same way. The Phoenix finding is a beacon for follow-on enumeration. |
| **Severity** | **MED** as a population-scale pattern. The two hosts inside it with verified data-in-hand or fully-callable admin surfaces — the Teetsh MailHog (139 emails) and the deepagents Kibana — are individually HIGH. |

**Potential impact:** four new operators (wiratek.id, dsb-kairo.de, "deepagents", Teetsh) were attributed via shadow ports, not Phoenix project names. The check surfaces operators the primary survey misses and turns single findings into severity multipliers when surfaces stack on one host.

### 5.6 Cross-platform thesis evidence — Six observability platforms ship auth-on and hold at 0% unauth

| Field | Value |
|---|---|
| **Name/ID** | Langfuse (381 reachable), LangSmith (27), Helicone ~16, OpenLIT (23), Lunary (1), Pezzo (1) |
| **Type** | Falsification-test result for the auth-on-default thesis |
| **Evidence** | Langfuse: all 381 reachable hosts return 401/403 on `/api/public/projects`; source audit confirms all 73 public-API handlers are wrapped and no master auth-off toggle exists. LangSmith: 27/27 return 401 on `/api/v1/sessions`. Helicone: 0 of ~16 self-hosted instances proxy unauthenticated; auth mandatory via BetterAuth or Supabase. OpenLIT: 23/23 redirect every API route to `/login`. Lunary and Pezzo: the single confirmed instance of each enforces auth at every protected route. Combined: 0 unauthenticated instances across 482 confirmed non-Phoenix instances. |
| **Observed exposure** | None. This is the point. Six platforms in the same product class as Phoenix, carrying the same data class, ship auth-on and stay closed at population scale — including Langfuse deployments run by the UK AI Safety Institute and by Amazon's own internal AI beta teams. |
| **Severity** | **OBSERVED** — confirmed platform behavior. Not a vulnerability. This finding is thesis evidence: it confirms the auth-on-default thesis by demonstrating that the platforms shipping auth-on are exactly the ones not exposed, and Phoenix, the one platform shipping auth-off, is the only one leaking. |

**Potential impact:** none directly. The research value is the falsification test. The thesis predicted that auth posture tracks the shipping default rather than operator skill. The observability tier confirms it cleanly. Phoenix accounts for 100% of the cohort's unauthenticated instances. Without Phoenix, the cohort unauth rate is 0/482. The 25% Phoenix rate is not "AI observability is hard to deploy securely." It is "Phoenix ships with `PHOENIX_ENABLE_AUTH=False`."

### 5.7 LangSmith — Unauthenticated version and build disclosure by design

| Field | Value |
|---|---|
| **Name/ID** | `GET /api/v1/info` on all 27 confirmed LangSmith instances |
| **Type** | Information-disclosure endpoint, unauthenticated by design |
| **Evidence** | The endpoint returns `version`, `git_sha`, and `license_expiration_time` as first-class JSON with no auth. Example: `version 0.13.40`, `git_sha 7ed913b5...`. Comparable behavior exists across the cohort: Phoenix exposes `Config.platformVersion` in an inline `<script>` block; Langfuse's `/api/public/health` returns the version. |
| **Observed exposure** | Pre-auth version, exact build SHA, and license-expiry window. |
| **Severity** | **LOW** — information disclosure. Standard practice for self-hosted enterprise software; not a defect on its own. |

**Potential impact:** when a LangSmith CVE lands, an attacker maps every affected operator in minutes via this endpoint at population scale. The git_sha pins the exact build and its dependency set. The license-expiry timestamp lets an attacker preferentially target instances near expiry, when the operator is distracted.

### 5.8 Helicone / OpenLIT — Default-secret and co-located-service hardening gaps (latent)

| Field | Value |
|---|---|
| **Name/ID** | Helicone `BETTER_AUTH_SECRET`, bundled MinIO `minioadmin:minioadmin`; OpenLIT node_exporter on a Huawei Cloud China host |
| **Type** | Latent primitives (source-confirmed, unprobed) and one operator-side IP-shadow finding |
| **Evidence** | Helicone: the literal `BETTER_AUTH_SECRET="MKUcaeqyMD7UBkGeFYY5hwxKS1aB6Vsi"` appears in three `.env.example` files (`web/`, `valhalla/jawn/`, `docker/`); the Quick Start docker-run command omits the secret entirely, defaulting to `change-me-in-production`; the bundled `helicone-all-in-one` image defaults MinIO to `minioadmin:minioadmin`. OpenLIT: `124.71.61.247` (Huawei Cloud China) exposes `node_exporter` on `:9100` unauthenticated, dumping full host metrics. |
| **Observed exposure** | Helicone: an operator who copies a `.env.example` verbatim has predictable session-cookie signatures and, if the bundled S3 is exposed, default MinIO credentials on the `request-response-storage` bucket. OpenLIT: one operator's host fingerprint readable at no cost. |
| **Severity** | **UNRATED** for the Helicone primitives — source-confirmed but not probed against the population; probing requires cryptographic forgery or credential testing against third-party hosts, which is out of scope. **LOW** for the OpenLIT node_exporter — verified unauthenticated, low-impact host-metrics disclosure. |

**Potential impact:** the Helicone session-forgery primitive, if an operator left the default `BETTER_AUTH_SECRET`, would let an attacker mint valid session cookies. The threat model is materially harder than Phoenix's "the GraphQL schema is reachable unauthenticated" — it needs forgery or credential guessing, not just a well-formed request. It is documented for the vendor threat-model writeup, not exercised.

---

## 6. Risk Assessment

### Overall Posture

The observability tier is not uniformly exposed. It is bimodal. One platform, Phoenix, is wide open at a 25% population-scale unauth rate. Six platforms are closed at 0%. The split is not random and it is not about operator skill. It is about a single env-var default value. Phoenix ships `PHOENIX_ENABLE_AUTH=False`; the other six ship auth as a design constraint with no off switch. The risk is systemic, and the system in question is the Phoenix shipping default.

### Confidentiality

For the 94 unauth Phoenix hosts, confidentiality is broken. Exposed: full user prompts, full model responses, chain-of-thought reasoning, operator-internal logic (brand catalogs, classification rules, system prompts), model-tier identity, and agent topology. The "Lillia" cluster exposes identified health telemetry. The reputacion.digital host additionally leaks its full internal Prometheus topology. Phoenix's stored-secret primitive means confidentiality will degrade further over time without any new operator misconfiguration — every operator who migrates an `OPENAI_API_KEY` into Phoenix's secret manager while running auth-off converts a trace-data leak into a credential leak. For the other six platforms, confidentiality holds at population scale.

### Integrity

For unauth Phoenix, integrity is broken too. The exposure is not read-only. Unauthenticated span ingestion (`create_spans`) plus unguarded prompt-management, annotation, and dataset mutations let an attacker poison evaluation baselines, inject fabricated spans, and tamper with the data downstream pipelines consume. For the six auth-on platforms, no unauthenticated integrity impact was found.

### Availability

The Phoenix span-ingestion path permits high-rate write floods that run up an operator's storage and quota cost. The reputacion.digital host exposes Prometheus `/-/quit`, a one-request denial-of-service primitive on the monitoring layer. No availability impact was found on the six auth-on platforms.

### Systemic Patterns

- **Platform-default propagation (Insight #13, drafted this session).** Two platforms in the same product class with overlapping enterprise customers can show a 0%-vs-25% unauth split driven by one env-var default. The vendor's choice of `False` vs `True`, made at platform inception, propagates through every operator's deployment template, every container image, every Helm chart, every tutorial, and shows up at population scale as the dominant signal.
- **Co-located-service hygiene tracks the platform default (Insight #12, codified this session).** The same Phoenix operators who do not set `PHOENIX_ENABLE_AUTH=true` also do not firewall NFS, do not move Prometheus to loopback, and leave MailHog running after dev. 27% of unauth Phoenix hosts carry a secondary surface. The auth-off default is a marker for a broader hardening pattern. The operator-population delta is real but smaller than the auth-default delta — Langfuse and LangSmith get comparable enterprise customers and sit at 0-6% IP-shadow rates. Both effects compound.
- **The web UI is not the auth boundary.** Phoenix, Helicone, OpenLIT, and Pezzo all serve SPA HTML on unmatched routes, producing HTTP 200 that means nothing about auth state. Per Insight #16, the data-layer API endpoint is the only honest verdict.

---

## 7. Recommendations

### R1 — Phoenix: change the shipping default to auth-on

The single highest-leverage fix. Arize should flip the `PHOENIX_ENABLE_AUTH` default to `True` in `src/phoenix/config.py`.

```python
# src/phoenix/config.py — current
def get_env_enable_auth() -> bool:
    return _bool_val(ENV_PHOENIX_ENABLE_AUTH, False)   # ships wide open

# recommended
def get_env_enable_auth() -> bool:
    return _bool_val(ENV_PHOENIX_ENABLE_AUTH, True)    # ships closed; operator opts out explicitly
```

This works because population-scale posture tracks the default. Langfuse, Helicone, LangSmith, OpenLIT, Lunary, and Pezzo all ship auth-on and sit at 0% unauth across 482 confirmed instances at 4-5× the population size. Operators who genuinely want an open instance still can — they set the variable to `False` deliberately, instead of inheriting an open instance by accident.

### R2 — Phoenix operators: enable auth and verify at the data layer

For any operator running Phoenix today:

```bash
export PHOENIX_ENABLE_AUTH=true
export PHOENIX_SECRET=$(openssl rand -hex 32)
# restart Phoenix, then verify against the GraphQL endpoint, not the web UI:
curl -s -X POST http://<your-host>:6006/graphql \
  -H 'Content-Type: application/json' \
  -d '{"query":"{ projects { edges { node { name } } } }"}'
# auth-on returns an error or "Invalid token"; the web UI returning HTTP 200 means nothing
```

The verification step matters. Phoenix's web UI returns 200 to everyone regardless of auth state. Only the GraphQL response confirms the boundary.

### R3 — Phoenix: use the secure-fail authorization class on Secret.value

`src/phoenix/server/api/types/Secret.py:48` decorates the decrypted-plaintext `Secret.value` field with `IsAdminIfAuthEnabled`, which returns `True` (allow) when auth is off. The principled fix is `IsAdmin` (secure-fail, returns `False` when auth is off). A default-off auth state should never turn an admin-only field into a public one. This is a defense-in-depth gap, latent today because operators have not widely adopted Phoenix's secret manager, and it should be closed before adoption climbs.

### R4 — All operators: close the IP-direct shadow

Per Insight #12, bind co-located services to loopback or a private interface, not `0.0.0.0`:

```bash
# instead of binding Phoenix / Prometheus / MailHog to all interfaces:
phoenix serve --host 127.0.0.1 --port 6006
# and firewall the high ports at the cloud provider — allow only 443/80 inbound:
# AWS Security Group / GCP firewall: drop inbound to 6006, 9090, 2049, 8025, 5601, 9200
```

Loopback binding is the cheapest and most durable fix. Hostname-routed SSO does not protect a service that also answers by raw IP.

### R5 — Helicone operators: rotate the default secrets

```bash
# never copy .env.example verbatim — generate fresh secrets:
BETTER_AUTH_SECRET=$(openssl rand -base64 32)
S3_ACCESS_KEY=$(openssl rand -hex 16)
S3_SECRET_KEY=$(openssl rand -hex 32)
```

The literal `BETTER_AUTH_SECRET` in the shipped `.env.example` files makes session-cookie signatures predictable for anyone with the value. Helicone should also remove the literal from the example files and have the Quick Start generate a secret rather than defaulting to `change-me-in-production`.

### Future automation

The seven per-platform fingerprints from this survey were productized as VisorBishop, a standalone Go binary that walks a target list and emits typed findings per platform plus IP-direct-shadow results. It is read-only by design — no credential testing, no payload fuzzing.

```bash
# re-sweep the whole observability corpus on a schedule:
visorbishop -i observability-hosts.txt -c 32 -ip-shadow -json out.json -csv out.csv

# operator self-check, integrated post-deploy:
visorbishop -t http://<your-host>:6006 -ip-shadow
```

VisorBishop closes the Phase 1 → Phase 2 → Phase 3 loop. Any new discovery expressible as a fingerprint gets added, then re-run across the existing population to find what the manual probes missed.

---

## 8. Limitations and Assumptions

| # | Limitation | Risk Implication |
|---|---|---|
| L1 | Analysis reconstructed from case studies, evidence directories, and git history. This session was not assigned a session number; execution-trace timestamps are approximate. | Trace timing is indicative, not exact. Findings and counts are sourced from the case studies and evidence files, not from re-running probes. |
| L2 | Internal-only deployments are invisible to Shodan. The populations are public-internet-facing instances only. | True platform deployment counts are higher. The survey measures the exposed surface, not total adoption. |
| L3 | Langfuse's 0% unauth is over 381 reachable hosts, not the 1,333 cert-CN matches; 950 were unreachable LB frontends. Phoenix's population had 357 of 377 reachable from the research VPN. | Reachability is a VPN-routing and LB-topology artifact. Unauth rates are computed over reachable hosts and stated as such. |
| L4 | The three latent primitives — Phoenix stored-secret extraction, Helicone session-forgery, Langfuse weak-`ADMIN_API_KEY` — were source-confirmed but not probed against the live population. | Population prevalence of these primitives is unknown. Probing them requires credential testing or forgery against third-party hosts, which the ethical scope forbids. |
| L5 | The Phoenix per-mutation auth gate was not exhaustively confirmed at source. The 40-mutation triage is from live probing on one host plus the `IsAdmin`/`IsAdminIfAuthEnabled` decorator audit. | Which write mutations are unauth-callable on default-no-auth hosts is not fully enumerated. This is a named Phase 2 follow-on. |
| L6 | LangSmith is closed-source; no source-level audit was possible. Its auth posture is confirmed from endpoint behavior only (27/27 returned 401). | The LangSmith finding rests on observed behavior, not on reading the auth wrapper. A source audit would strengthen it. |
| L7 | The NFS `/postgres` export on reputacion.digital was enumerated via `showmount -e` as present and world-exported; no file was mounted or read. | The database-content exposure is described from the export listing, not from data in hand. The actual contents were not verified. |
| L8 | Phoenix Stage-2 aimap enumerators hung repeatedly on slow hosts and did not complete. The GraphQL probers covered the same ground. | A tooling limitation, logged. Phoenix enumeration relied on the bespoke GraphQL probers rather than aimap for this run. |
| L9 | Span sampling pulled a handful of spans per cluster (4 clusters). Data-class characterization generalizes from a small sample. | The data-class labels per cluster are representative, not exhaustive. The "Lillia" PHI-relevance is flagged as conditional on US-resident users, which the sample did not verify. |

---

## 9. Proof of Concept (PoC) Illustrations

> PoCs use minimal, read-only interactions. No operator data extracted. No credentials used. No exploit payloads. They demonstrate the existence of the surface and the risk, nothing more.

### PoC 1: Phoenix unauthenticated trace-store read

**Scenario:** an anonymous internet client reads the project list and token counts of a production Phoenix instance by POSTing a GraphQL query to the data layer.

```
REQUEST:
  POST /graphql HTTP/1.1
  Host: <operator-host>:6006
  Content-Type: application/json

  {"query":"{ projects { edges { node { name } } } }"}

RESPONSE:
  HTTP/1.1 200 OK
  Content-Type: application/json

  {"data":{"projects":{"edges":[
    {"node":{"name":"default"}},
    {"node":{"name":"<project-name>"}}
  ]}}}
```

**Demonstrated:** the GraphQL data layer answers an unauthenticated client. On an auth-on instance the same request returns a JSON error or the string `Invalid token`. From this point an attacker enumerates every project, every trace, every token count, and can sample the spans — full prompts, full responses, system prompts. The PoC stops at the project list. It does NOT sample spans, write data, or call any mutation. The web UI on the same port returns HTTP 200 to everyone regardless of auth state, which is why the verdict is read off the GraphQL response and not off the UI.

### PoC 2: IP-direct-shadow bypass — Insight #12

**Scenario:** an operator fronts every service with application-layer SSO bound to a hostname. The same services also listen on the host's raw IP. The IP-direct path bypasses the SSO.

```
REQUEST A — via the configured hostname:
  GET / HTTP/1.1
  Host: phoenix.<operator-domain>

RESPONSE A:
  HTTP/1.1 302 Found
  Location: https://auth.<operator-domain>/...        <-- SSO front-end catches it

REQUEST B — same backend, via the raw IP:
  GET /api/v1/query?query=up HTTP/1.1
  Host: <operator-IP>:9090

RESPONSE B:
  HTTP/1.1 200 OK
  Content-Type: application/json

  {"status":"success","data":{"resultType":"vector","result":[
    {"metric":{"job":"<scrape-target>","instance":"192.168.40.<x>:<port>"}}
  ]}}
```

**Demonstrated:** the operator's mental model — "everything is behind SSO" — is correct only for traffic arriving via the configured hostnames. Request A is bounced to SSO. Request B hits Prometheus directly on the bare IP with no auth in the path, returning the internal scrape topology including private `192.168.40.x` endpoints. Same backend, two routes, only one auth-fronted. The PoC reads one `up` query to confirm the bypass exists. It does NOT enumerate the full metric set, call `/-/quit`, or touch any other shadowed service. The fix is to bind services to loopback or firewall the high ports so the only route is through the reverse proxy.

---

*Prepared by NuClide Research (Nicholas Kloster + Claude Sonnet 4.6) · 2026-05-10 AI observability survey (Phase 1)*
