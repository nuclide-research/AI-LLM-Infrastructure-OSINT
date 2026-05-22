# Session Analysis: VisorBishop Productization + AI-Observability Phase 2

**Date:** 2026-05-11 to 2026-05-12
**Session:** Unnumbered (VisorBishop tool-build + observability Phase 2 close)
**Classification:** Internal / Research Use Only
**Toolchain:** VisorBishop (built this session, v0.1 through v0.1.7) · JAXEN (Shodan harvest) · nmap (extended IP-shadow) · Docker (source-audit fingerprint build) · git
**Repos updated:** AI-LLM-Infrastructure-OSINT (b18d1ea, abddfda, b8e6207, c01c2bf, 3b31ba4) · VisorBishop (bb067e8, bb067e8→0dd8c90, v0.1.3, v0.1.5, 4cade62, c4d0eeb, 6a4d3b1, v0.1.7)

---

## 1. Overview

### Objective

This session built and ran VisorBishop, then used it to close Phase 2 of the AI-observability survey. Two parallel goals:

1. Productize the per-platform fingerprints accumulated across Phase 1 and Phase 2 of the AI-observability tier into a single Go binary, then re-sweep the original Shodan corpora to find what manual chain-walking missed.
2. Finish the Phase 2 per-platform deep-dives (Helicone, Langfuse, LangSmith) and the cross-platform synthesis, closing the observability tier as a research unit.

The research program is hypothesis-driven. The governing thesis:

> Every layer of the modern AI stack that does not ship with authentication enabled by default is deployed without authentication on the public internet at population scale.

VisorBishop is the tool that operationalizes the thesis. It re-runs codified fingerprints across populations a human walked once. The session tested whether a productized re-prober surfaces new findings or only reproduces the manual work. The answer was new findings, in volume.

### Scope and Constraints

- **Target domains/IPs:** AI-observability and adjacent platform classes on public-internet IP addresses. Phase 1 corpora: Phoenix (377 Shodan hits), Langfuse (381 confirmed), LangSmith (96), Helicone (21), OpenLIT (23), Lunary (6), Pezzo (3). New population sweeps this session: LiteLLM (5,391 unique URLs), MLflow Tracking (10,993 dork hits), Weights & Biases self-host (87), plus iter-8 six-platform samples (Langflow, Dify, Kubeflow, PostHog, Prefect, Airflow).
- **Allowed techniques:** Passive Shodan harvest (read-only), safe HTTP GET/POST probes against documented diagnostic endpoints, banner grabbing, IP-direct-shadow adjacent-port enumeration, Docker-local source-audit fingerprinting.
- **Ethical limitations:**
  - No data exfiltration — metadata and schema enumeration only
  - No destructive API calls
  - No use of discovered credentials
  - Data-tier probes: connection attempt only (does auth gate exist? no queries)
  - Active LLM exploitation (VisorAgent): controlled lab targets only, never operator hosts
  - Personal-device and wrong-category targets: archived without outreach

---

## 2. Environment and Tooling

### Claude Code Operation

The session ran as orchestrator plus iterative tool-build. The main session held strategy, wrote each VisorBishop prober, and decided port-set expansion between iterations. Iterations ran as a closed loop: build prober, sample-sweep to validate, scale to full population, codify the result, decide the next port class. Bug fixes were folded inline as population workloads surfaced them. Three correctness or performance gaps were caught at sample-sweep stage before they could produce systematic noise at population scale.

### Tools Used

| Tool | Role | Config notes |
|---|---|---|
| VisorBishop | **Built this session.** Productized re-prober: per-platform fingerprint + IP-direct-shadow adjacent-port sweep | v0.1 → v0.1.7 across the session. `-ip-shadow` / `-ip-shadow-all`, `-c` concurrency 8→32, `-timeout 4s`, JSON+CSV output |
| JAXEN | Stage-0 Shodan harvest of new populations (LiteLLM, MLflow, W&B, iter-8 six platforms) | `--no-lookup` for raw exports; pagination split by country facet on high-population dorks |
| nmap | Extended IP-shadow port sweeps for the Phase 2 deep-dives (17–18 port sets) | Used in Helicone/Langfuse/LangSmith deep-dives before the sweep was productized into VisorBishop |
| Docker | Local source-audit of Helicone and Langfuse `docker-compose.yml` and `.env*.example` defaults | Default-config fingerprinting; not operator variation |
| git | Repo commits across AI-LLM-Infrastructure-OSINT and VisorBishop | No push during the session |

Tools not run this session and why: VisorGraph, VisorScuba, BARE, VisorCorpus, VisorSD, recongraph, nu-recon, VisorPlus, cortex, VisorRAG were not invoked — this was a tool-build session producing VisorBishop, not a full arsenal assessment against a single target. VisorHollow is Windows-only (binary cannot execute on this host). VisorAgent is ethical-stop (controlled lab targets only, never the operator hosts in these corpora).

### Notable Configuration

VisorBishop concurrency started at 8 worker goroutines and rose to 32 for the population sweeps. Probe timeout held at 4s. The Phoenix 94-host re-sweep completed in 19.5 seconds. The Langfuse 381-host sweep took roughly 3 minutes after the port-parallelism fix (it stalled past 28 minutes before the fix). The LiteLLM 5,391-host full sweep took about 30 minutes at concurrency 32. The MLflow 10,993-host sweep took roughly 70 minutes. Shodan basic-plan API pagination breaks past page 70 on high-population dorks, so the MLflow and LiteLLM harvests were split by country facet. Every probe in VisorBishop is non-destructive: HTTP GET/POST with no mutating bodies, Redis `INFO server`, ClickHouse `SELECT 1` for default-user verification only, Postgres TCP-banner only, NFS port-open detection only.

---

## 3. Methodology

### Re-prober enumeration approach

VisorBishop is a re-prober. It does not discover new populations from scratch. It takes a prior survey's corpus, or a fresh Shodan harvest, and applies the codified fingerprints deterministically. Each platform has a `Prober` implementation under `internal/fingerprint/`. The CLI walks a list of HTTP(S) targets, identifies which platform each runs, captures version and auth-posture signals, and optionally sweeps the host IP for co-located services.

The enumeration ran in iterations. iter-1 re-swept all six non-Phoenix Phase 1 corpora. iter-2 added message-broker ports. iter-3 added AI-stack pipeline ports. iter-4 and iter-5 expanded platform coverage into adjacent tiers. iter-6 was the first full-population sweep (LiteLLM, 5,391 hosts). iter-7 added the experiment-tracking tier (MLflow, W&B). iter-8 sampled six more platform classes at 200 hosts each. Phase 3 was the initial tool ship. Phase 5 derived three second-order primitives from the cumulative corpus without new network traffic.

### IP-shadow adjacent-port sweep

The IP-direct-shadow technique (Insight #12, prior session) probes the host IP directly on a set of adjacent ports. SSO reverse-proxy fronting protects the platform's hostname, not the bare IP. VisorBishop's `internal/probe/ipshadow.go` started with a 15-port set, then grew as iterations tested port classes. Ports are probed concurrently within each host so wall time per host is O(timeout), not O(ports × timeout).

The port set is hypothesis-driven, not top-N popular. The selection prompt is "what would an operator running this platform put on the same host?" iter-1's dev-tooling ports (Redis, MailHog, node_exporter) yielded 8 new findings. iter-2's message-broker ports yielded 0. iter-3's AI-stack pipeline ports (Qdrant, MLflow, ChromaDB) yielded 3. The yield tracked operator-class alignment, not port count. This became Insight #14.

### Candidate identification

A platform is confirmed only by a positive identity marker, never by a dork hit alone. Each prober runs multiple sub-probes. The LiteLLM prober runs four: root HTML for the "LiteLLM API" Swagger title, `/.well-known/litellm-ui-config` for the `proxy_base_url` field, `/v1/models` for the OpenAI-shaped response, `/openapi.json` for version. The mandatory marker is the `/.well-known` route, not the title. Soft matches (title-only, OpenAI-shape without the marker) go to a "possible" bucket that does not enter the headline count.

### Validation checks

Three insights were codified this session, all from VisorBishop failures the loop surfaced. Each is a validation rule the tool now enforces.

- **Insight #14 (recon yield aligns with port-class operator intent, not port number).** Validation rule for port-set selection: a port enters the sweep only if an operator running the primary platform would plausibly co-deploy that service, and exits at the next iteration if it produces zero findings on the first 100 hosts. iter-2's zero-yield message-broker ports were the anchor.
- **Insight #15 (Shodan dork hits are not platform instances — the 50% rule).** Validation rule for population counts: never quote a dork hit count as a platform count without a marker-verified subset. The iter-6 LiteLLM sweep produced 2,710 confirmed of 5,391 dork hits — 50.3%. The iter-7 MLflow sweep produced 806 confirmed of 10,993 — 7.3%, the noisiest dork in the corpus.
- **Insight #16 (a 200 from a platform endpoint is identity, not auth state).** Load-bearing for the whole methodology. A 200 to an unauthenticated probe confirms the platform is alive and answering. It does not classify auth posture. The iter-7 W&B prober classified 42 confirmed hosts as HIGH unauth because the GraphQL `viewer` query returned HTTP 200. Thirty minutes of follow-up probing reversed all 42 to INFO: the 200 plus `{"data":{"viewer":null}}` is W&B's documented response for unauthenticated callers. The data layer is gated at the resolver, not the HTTP status. The fix: every "200 → unauth" classification must include a data-layer assertion that the response actually contains populated data. Empty arrays, null values, and "field required" errors are all "not exposed" signals that look like 200 to a status-only classifier.

### Safeguards

No brute forcing. No privilege escalation. No data exfiltration. No write-tier operations. No credential testing. The ClickHouse default-user check on `benchmarkit.solutions` sent `SELECT 1` and `SHOW DATABASES` and `SELECT version()` only — structure and version, never row contents. Counting rows or selecting bodies would be exfiltration and was not done. The Langfuse and Helicone default-secret findings (`NEXTAUTH_SECRET="secret"`, `BETTER_AUTH_SECRET` literal) were documented at source level only. Probing whether a live operator runs the default secret would require active JWT forgery, which is out of scope for read-only research-mode. The LangSmith `playground_auth_bypass_enabled` flag was observed in `/api/v1/info` output but not actively probed past 401-returning endpoints. No disclosure outreach happened during the research chain.

---

## 4. Execution Trace

| Time | Action | Outcome / Decision |
|---|---|---|
| 05-11 morning | Phase 2 deep-dive: Helicone source audit + extended 17-port nmap IP-shadow across 19 IPs | Found unauth ClickHouse 23.4.2.11 on `benchmarkit.solutions` / `137.184.217.47`. Root cause: `docker-compose.yml` binds port 8123 to `0.0.0.0`, ClickHouse `default` user no password. Postgres exposed on 2 hosts. |
| 05-11 morning | Phase 2 deep-dive: Langfuse source audit + 18-port IP-shadow across 381 IPs | 0/381 unauth on the platform. Latent primitives: `NEXTAUTH_SECRET="secret"`, `SALT="salt"`, `ENCRYPTION_KEY="0"*64` in `.env.prod.example`. `user.admin===true` cross-project bypass. 5 hosts expose Postgres. |
| 05-11 morning | Phase 2 deep-dive: LangSmith `/api/v1/info` probe across 27 confirmed instances | `/api/v1/info` discloses `customer_info`. 19 of 27 instances name an enterprise customer: Grammarly, ByteDance, Generali, Rakuten, National Bank of Greece, University of Michigan, RealPage, Pigment ×5, Lockton. 0 IP-shadow finds — cleanest in the cohort. |
| 05-11 | Phase 3: build VisorBishop v0.1, productize all Phase 1+2 fingerprints into one Go binary | Phoenix 94-host re-sweep: 89 confirmed, 88 CRITICAL, 1.50B tokens aggregated, 19.5s wall time. Every Phase 2 actualized finding reproduced by a single command. |
| 05-11 | iter-1: re-sweep all six non-Phoenix Phase 1 corpora with 15-port IP-shadow | 8 NEW unauth services surfaced (4 Redis, 3 MailHog, 1 node_exporter), doubling the Phase 2 yield of 8. Langfuse iter-1 yield: 0 new — meaningful negative result, operator-population discipline delta. |
| 05-11 | Bug: `parseTargetLine` rejected bare `IP:port` Shodan TSV format | Fixed in `bb067e8`. Parser now infers scheme from port. |
| 05-11 | Bug: Langfuse 381-host sweep stalled past 28 minutes at 0% CPU | `ShadowScan` iterated 15 ports serially per host. Fixed in `0dd8c90`: ports probed concurrently within each host. 5x speedup; sweep completed in ~3 minutes. |
| 05-11 | iter-2: add message-broker ports (NATS, Kafka, RabbitMQ, Memcached) | 0 new unauth. Message brokers are a different operator class. Refined the port-selection methodology. |
| 05-11 | iter-3: add AI-stack pipeline ports (Qdrant, MLflow, ChromaDB, Streamlit, Gradio, Milvus) at v0.1.3 | 3 NEW unauth Qdrant. One — `172.178.38.117` — is Rogers Communications: 49 collections of router/firewall/load-balancer NetOps log embeddings, co-located with an unauth Phoenix exposing the same bot's traces. |
| 05-11 | iter-4 / iter-5: expand platform coverage into adjacent tiers (gateway, annotation, eval) | iter-4 surfaced 4 new; iter-5 surfaced 35 new. Promptfoo critical-host pattern characterized. |
| 05-11 | iter-6: full LiteLLM 5,391-host population sweep at v0.1.5, concurrency 32 | 2,710 confirmed LiteLLM (50.3% of dork hits). **283 CRITICAL unauth `/v1/models`** — 283 LLMjacking primitives. The 50% confirm rate anchored Insight #15. |
| 05-11 | iter-7: build MLflow + W&B probers at v0.1.6, sample-sweep 200 hosts each | MLflow sample: 3 critical of 44 confirmed. W&B sample: 42 confirmed all flagged HIGH unauth. |
| 05-11 | iter-7: W&B reclassification after richer GraphQL probing | All 42 W&B HIGHs reversed to INFO. 200 + null viewer is W&B's documented unauthenticated response. Hostname analysis confirmed the 42 are W&B's own multi-tenant cluster (`nylcloud.wandb.io`, `dropbox.wandb.io`). Fixed in `4cade62`. Anchored Insight #16. |
| 05-11 | iter-7: full MLflow 10,993-host population sweep | 806 confirmed (7.3% — noisiest dork in the corpus). **120 CRITICAL unauth MLflow Tracking servers.** 28 of 120 run pre-2.2.1 (CVE-2023-1177 likely). |
| 05-11 | iter-8: build six new probers at v0.1.7, sample-sweep 200 hosts each across Langflow, Dify, Kubeflow, PostHog, Prefect, Airflow | 537 confirmed of 1,200 probed. **1 CRITICAL** — a Kubeflow Pipelines standalone on `13.217.68.246`. Three prober marker bugs caught and fixed at sample stage (`6a4d3b1`). Null-finding validates Insight #13: auth-on defaults reproduce auth-on at population scale. |
| 05-11 | Phase 5: derive three second-order primitives from the cumulative corpus, no new sweeps | Cross-platform correlation (1 same-IP Phoenix+LiteLLM chain on `78.46.88.7`). MLflow artifact-URI extraction (58 unique cloud buckets across 120 hosts). LiteLLM spend-tier classifier ($60K/mo conservative cost-at-risk across 283 hosts). |
| 05-12 | Phase 2 close: cross-platform synthesis | 0 cross-platform operator IP overlaps across 789 observability hosts. Phoenix unauth distributes across all major versions 4–15 — no upgrade path remediates the default. Observability tier declared research-complete. |

---

## 5. Findings

> **Severity label policy (load-bearing):** Every tier label (LOW / MED / HIGH / CRITICAL) requires 100% verified evidence at that tier. Unverified observations are UNRATED. Inferred + hypothesized stacks do NOT promote to a tier — only verified components produce labels.

### 5.1 LiteLLM population — 283 unauthenticated LLMjacking primitives

| Field | Value |
|---|---|
| **Name/ID** | 283 LiteLLM hosts, full inventory in `iter6/critical-all.tsv` |
| **Type** | LLM gateway / proxy |
| **Evidence** | iter-6 full sweep of 5,391 unique URLs. 2,710 confirmed LiteLLM via the `/.well-known/litellm-ui-config` marker. 283 returned the OpenAI-shaped model catalog from `/v1/models` with no auth. Each `/v1/models` response was captured in the VisorBishop indicators payload. |
| **Observed exposure** | Unauthenticated `/v1/models` — the proxy holds the operator's upstream LLM provider API keys and forwards attacker prompts to those providers, billed to the operator |
| **Severity** | HIGH — verified unauth access to the model catalog confirmed on 283 hosts. The proxy-forwarding behavior is documented LiteLLM function; the keys themselves were not extracted (no credential test run). |

**Potential impact:** Each unauth LiteLLM is an LLMjacking primitive. An attacker sends prompts through the proxy and the operator pays the upstream bill. Three reasons it is severe at population scale: active financial exposure (attacker spends the operator's money, not just reads data), provider-stack breadth (one LiteLLM aggregates OpenAI plus Anthropic plus Bedrock plus Azure keys), and detection difficulty (slow distributed probing looks like normal traffic until the bill arrives). Budget European VPS providers Hetzner and Contabo host 69 of the 283 (24.4%). Geographic spread is 16-plus countries. Named operators in the critical set include `api.modelharbor.com` (a commercial LLM-routing product, so every customer shares an unauth proxy) and a Charter Spectrum residential IP (a developer running LiteLLM at home with personal API keys, 22 models including frontier Opus).

### 5.2 MLflow Tracking population — 120 unauthenticated experiment-tracking servers

| Field | Value |
|---|---|
| **Name/ID** | 120 MLflow Tracking hosts, inventory in `iter7/results/mlflow-full.json` |
| **Type** | ML experiment-tracking server / data tier |
| **Evidence** | iter-7 full sweep of 10,993 dork hits. 806 confirmed MLflow (7.3%). 120 returned populated experiment lists from `/api/2.0/mlflow/experiments/search` with no auth. 118 of 120 had at least one real (non-scanner-decoy) experiment name. |
| **Observed exposure** | Unauthenticated experiment search, run search, model registry |
| **Severity** | HIGH — verified unauth access to populated experiment data on 118 hosts. 2 hosts had only scanner-decoy experiments (fresh deployments), rated OBSERVED for those 2. |

**Potential impact:** Unauthenticated MLflow is a richer data class than Phoenix or LiteLLM. It exposes the operator's full experimentation history: prompts and prompt templates logged as run params, hyperparameters including `temperature` and `system_prompt`, artifact URIs pointing at cloud buckets, run tags (operators frequently log credentials to tags), and the model registry with stage transitions. Named operators in the verified critical set include Slovak government social-benefits data on `3.65.57.89` (orphan-pension recipient counts), Saudi Arabia healthcare ML on `101.46.48.180`, prostate-cancer biomarker classification on `44.255.234.92`, and academic deployments at the National Technical University of Athens, University of Oslo, and Universidad de Valencia.

**Subordinate finding — CVE-2023-1177 exposure.** 28 of the 120 critical hosts run MLflow pre-2.2.1 and are likely vulnerable to CVE-2023-1177, a path traversal in the artifact URI handler allowing arbitrary file read on the tracking-server host. Severity UNRATED — version banner confirms the vulnerable code path, but exploitation was not attempted (would require an active path-traversal probe, out of scope). The vulnerability has been public since 2023-03.

### 5.3 Helicone — unauthenticated ClickHouse on `benchmarkit.solutions`

| Field | Value |
|---|---|
| **Name/ID** | `137.184.217.47:8123` — `benchmarkit.solutions`, DigitalOcean US |
| **Type** | Data tier — ClickHouse HTTP interface backing a Helicone trace store |
| **Evidence** | `GET /?query=SELECT+1` returns `1` HTTP 200. `SHOW DATABASES` returns `INFORMATION_SCHEMA`, `default`, `information_schema`, `system`. `SELECT version()` returns `23.4.2.11`. The `default` user has no password. 14 tables in `default` including `request_response_rmt` (Helicone's main trace store). Structure and version verified; row contents NOT queried. |
| **Observed exposure** | Unauthenticated full read access to the Helicone trace store schema. `request_response_rmt` holds full LLM request and response bodies, token counts, cost, provider, model, and user/session/organization metadata. |
| **Severity** | HIGH — verified unauthenticated database access at structure level on a live host, reproduced 1 day after the Phase 2 finding and still unpatched. Not labeled CRITICAL: the trace-table rows were never queried, so no operator data is in hand. The exposure is verified; the data class is inferred from the schema and Helicone's migration files, not observed. |

**Potential impact:** Anyone can read the full trace store: every captured LLM prompt and completion, with cost and identity metadata. Root cause is a shipping default — Helicone's `docker-compose.yml` binds ClickHouse port 8123 to `0.0.0.0` (not `127.0.0.1`) and ships `CLICKHOUSE_USER: default` with no password. Any operator running the standard Helicone Docker setup on a public IP with no host firewall inherits this. Same population-scale signature as an auth toggle, expressed through a port-binding default.

### 5.4 LangSmith — enterprise customer-identity disclosure across 19 operators

| Field | Value |
|---|---|
| **Name/ID** | 27 confirmed LangSmith self-hosted instances; 19 disclose a customer name. Full dump in `langsmith-info-detail.json` |
| **Type** | API endpoint — unauthenticated `/api/v1/info` |
| **Evidence** | `/api/v1/info` returns without auth on every instance. The `customer_info` block contains `customer_name` and `customer_id` (UUID). 19 of 27 name a recognizable enterprise: Pigment ×5, Generali ×3, Grammarly ×2, ByteDance, Weber Shandwick, Turing, University of Michigan, Lockton, Rakuten, RealPage, National Bank of Greece, P-1.ai. Response also exposes `license_expiration_time`, `git_sha`, and `instance_flags`. |
| **Observed exposure** | Unauthenticated customer-identity, license-window, and feature-flag disclosure |
| **Severity** | MED — verified unauthenticated information disclosure. No LLM traces or prompts leak. The disclosed data is customer identity and operational metadata, not a data-tier leak. |

**Potential impact:** The 27-host LangSmith population becomes a public roster of enterprise AI deployments. A LangSmith CVE published tomorrow can be matched to named enterprises within minutes. License-expiration windows cluster around quarter-ends and are visible per-customer; operators near renewal often have weaker monitoring. The fact that an enterprise runs a public-internet-reachable LangSmith self-host is itself operational intelligence about that organization's AI program. The `playground_auth_bypass_enabled: true` flag appears on 27/27 instances but probed paths returned 401 / SPA HTML / 404 — UNRATED, closed-source, not verifiable without source access.

### 5.5 Kubeflow Pipelines standalone — unauthenticated pipeline API on `13.217.68.246`

| Field | Value |
|---|---|
| **Name/ID** | `13.217.68.246` — Kubeflow Pipelines standalone, AWS US-East |
| **Type** | ML orchestration — pipeline catalog API |
| **Evidence** | `GET /pipeline/apis/v1beta1/pipelines?page_size=10` returns 200 with a pipeline catalog including `tutorial-dsl-control-structures` and operator-defined pipelines, no auth. |
| **Observed exposure** | Unauthenticated read of the operator's pipeline catalog |
| **Severity** | MED — verified unauthenticated access to the pipeline catalog. The operator's pipeline code, parameter ranges, and any credentials embedded in pipeline metadata are reachable; metadata credentials were not observed, so not labeled HIGH. |

**Potential impact:** The Pipelines-standalone distribution has no dex/oidc auth layer by default and relies on operator network gating. Exposed publicly without an ingress-level auth shim, the pipeline API discloses training DAGs and parameter ranges. This was the lone critical across 1,200 iter-8 hosts spanning six platforms — the exception that proves the auth-on-default rule.

### 5.6 Phoenix population — IP-shadow co-located unauthenticated services (iter-1, iter-3)

| Field | Value |
|---|---|
| **Name/ID** | 11 new co-located unauth services across the 94-host Phoenix unauth population |
| **Type** | Co-located dev tooling and AI-stack services on Phoenix operator hosts |
| **Evidence** | iter-1: 4 unauth Redis (banner-verified via `INFO server`, no commands sent), 3 unauth MailHog, 1 unauth node_exporter. iter-3: 3 unauth Qdrant vector DBs. All confirmed by the productized IP-shadow sweep on ports the manual Phase 2 walk did not probe at scale. |
| **Observed exposure** | Unauthenticated Redis, MailHog mail-capture, node_exporter metrics, Qdrant vector collections — all on the same IPs as unauth Phoenix instances |
| **Severity** | HIGH for the verified-unauth services as a class. The Rogers Qdrant (5.7) is broken out separately. |

**Potential impact:** Operators who ship one service auth-off ship others auth-off too. `dsb-kairo.de` (German School Cairo) is a three-primitive host: unauth Phoenix, unauth Prometheus, unauth Redis. Teetsh, a French education SaaS, runs MailHog with no auth on all four of their public Scaleway hosts; one currently holds 139 captured `@teetsh.com` emails and the other three are latent capture windows. The four newly-found Redis instances all run Redis 7.4.7 across different operators, suggesting a shared deployment template that ships without `requirepass`.

### 5.7 Rogers Communications — co-located unauthenticated Phoenix + Qdrant NetOps exposure

| Field | Value |
|---|---|
| **Name/ID** | `172.178.38.117` — Rogers Communications, Microsoft Azure US |
| **Type** | Two-layer exposure: LLM trace store + vector DB |
| **Evidence** | Phoenix `/graphql` (Phase 1): project `rogers-netops-ai-bot-project`, 8,738 traces, 2.67M tokens, plus 5 A100 inference-benchmark projects. Qdrant `/collections` (iter-3): 49 collections including `router_fw66_nbmn_log_vector`, `firewall_apfw_log_vector`, `loadbalancer_ldbl_ltm_log_vector`. Qdrant 1.13.4, started 2026-05-08. |
| **Observed exposure** | Unauthenticated Phoenix trace disclosure and unauthenticated Qdrant vector-DB read on the same host |
| **Severity** | HIGH — verified unauthenticated access to both endpoints. The collection names disclose Rogers' router naming convention, datacenter site codes, F5 load-balancer topology, and A100 inference-benchmark configuration. Not labeled CRITICAL: vector contents and trace bodies were not retrieved. |

**Potential impact:** Rogers operates roughly 10M Canadian telecom subscribers. The Phoenix layer discloses what network-ops queries the bot is asked. The Qdrant layer discloses the embedding space of the network-ops log corpus. Cross-correlated, an attacker reads both the queries and the production-network log lines the bot draws answers from. This is critical-infrastructure operator exposure. Documented as a finding, not a disclosure target, per standing research-mode discipline.

### 5.8 Weights & Biases self-host — reclassified from HIGH to INFO

| Field | Value |
|---|---|
| **Name/ID** | 42 confirmed W&B self-hosted instances |
| **Type** | Experiment-tracking — GraphQL `/graphql` endpoint |
| **Evidence** | All 42 return HTTP 200 to an unauthenticated `viewer` query. Follow-up `entities`, `projects`, and `entity(name:)` queries on three hosts all returned `null` with resolver error `"entityName required for projects query"`. Hostname analysis: the 42 are W&B's own multi-tenant production cluster (`nylcloud.wandb.io`, `dropbox.wandb.io`, W&B internal canaries). |
| **Observed exposure** | None — the 200 + null response is W&B's documented unauthenticated behavior; the data layer is resolver-gated |
| **Severity** | OBSERVED — confirmed platform identity, confirmed auth-protected. Not a finding. |

**Potential impact:** None. This entry is recorded because the initial HIGH classification was wrong and the correction is load-bearing. It anchors Insight #16: a 200 is identity, not auth state. The reclassification dropped 42 false-positive HIGHs to INFO in 30 minutes of post-sweep validation.

### Severity rollup

| Tier | Findings |
|---|---|
| CRITICAL | None — no finding reached verified-data-in-hand this session. The data-tier probes stopped at schema/structure by ethical design. |
| HIGH | 5.1 LiteLLM 283 LLMjacking primitives · 5.2 MLflow 120 unauth Tracking servers · 5.3 Helicone unauth ClickHouse · 5.6 Phoenix IP-shadow co-located unauth services · 5.7 Rogers Phoenix+Qdrant |
| MED | 5.4 LangSmith customer-identity disclosure · 5.5 Kubeflow Pipelines standalone |
| OBSERVED | 5.2 (2 MLflow hosts with scanner-decoy-only experiments) · 5.8 W&B 42 hosts (platform-identification only) |
| UNRATED | 5.2 CVE-2023-1177 on 28 MLflow hosts (vulnerable code path confirmed, exploitation not attempted) · 5.4 LangSmith `playground_auth_bypass` flag (closed-source, not verifiable) |

---

## 6. Risk Assessment

### Overall Posture

Systemic, not isolated. The session swept 20-plus distinct platform classes at population scale and the pattern is consistent: platforms that ship auth-off produce unauthenticated exposures at population scale, platforms that ship auth-on do not. LiteLLM (auth-off) yielded 283 critical of 2,710 confirmed. MLflow (auth-off) yielded 120 of 806. The six iter-8 platforms (auth-on, or trivially-claimable-then-auth-on) yielded 1 critical across 537 confirmed. The observability tier reduces to one variable per platform: the vendor's shipping default.

### Confidentiality

The data classes at risk span the full sensitivity range. LiteLLM exposes upstream provider API keys indirectly through the proxy. MLflow exposes prompts, hyperparameters, artifact-URI cloud-bucket names, and credentials logged to run tags. Helicone's ClickHouse exposes full LLM request and response bodies. Phoenix exposes traces and 1.50B aggregated tokens across the unauth population. Rogers exposes production network-operations log embeddings. LangSmith exposes the enterprise customer roster. The named operators in the verified critical sets include government social-benefits data, healthcare ML, cancer-biomarker research, a Canadian telecom's NetOps tooling, and Fortune Global 500 enterprises.

### Integrity

Unverified for these populations. The session ran read-only probes only. MLflow's experiment API and Kubeflow's pipeline API are write-capable for an unauthenticated caller in principle — an attacker could inject false experiments, tamper with model-registry stage transitions, or alter pipeline definitions — but no write operation was attempted. Integrity impact is plausible and unconfirmed.

### Availability

LiteLLM unauth is an availability and financial risk simultaneously. Sustained abuse burns the operator's upstream rate limits and provider capacity allocation, and can trigger provider abuse-investigation that suspends the operator's account. The Phase 5 spend-tier primitive put the conservative cost-at-risk across the 283 LiteLLM hosts at roughly $60,494/month, with a realistic undetected-abuse-window projection of $2M to $7M/year. That figure is a model, not a measurement.

### Systemic Patterns

- **Shared root cause — shipping defaults (Insight #13).** Phoenix's auth toggle, LiteLLM's missing master-key requirement, MLflow's no-auth default, and Helicone's `0.0.0.0` ClickHouse port binding are the same class of failure. The operator inherits the vendor's default. Phoenix's default is constant across 11-plus major versions, so no upgrade path remediates it.
- **Operator-culture clustering.** An operator who ships one service auth-off ships others auth-off. `dsb-kairo.de` runs three unauth services. Teetsh ships unauth MailHog on every region. The IP-direct-shadow model predicts this.
- **Hosting-tier reproduction.** Phase 5's same-org correlation found 23 hosting orgs each running a mix of unauth LiteLLM, MLflow, and Phoenix across independent customers. Each provider's customer base reproduces the same default-driven pattern. A subnet sweep across one provider surfaces a known platform mix.
- **Mono-platform operators.** Across 789 observability hosts, zero genuine cross-platform IP overlaps. Operators install one observability platform per host. The one same-IP exception (`78.46.88.7`, Phoenix + LiteLLM) is the exploitable cross-platform chain.

---

## 7. Recommendations

### R1 — Auth-off shipping defaults (LiteLLM, MLflow, Phoenix)

The single highest-leverage change is vendor-side. LiteLLM should make the master-key requirement non-optional, or ship a loud warning banner when starting without `LITELLM_MASTER_KEY` set:

```bash
# Operator-side mitigation until the vendor changes the default
export LITELLM_MASTER_KEY="sk-$(openssl rand -hex 24)"
litellm --config config.yaml
# MLflow has no native auth — front it with a reverse-proxy auth layer
# and bind the tracking server to localhost only:
mlflow server --host 127.0.0.1 --port 5000
```

This works because the unauthenticated population is created by the absence of a deliberate auth step, not by a deployment mistake. Moving the default flips the population.

### R2 — Port-binding defaults in docker-compose (Helicone ClickHouse, Langfuse Postgres)

Bind data-tier services to localhost in the shipped compose file:

```yaml
# Wrong — binds to every interface
ports:
  - "18123:8123"
# Right — localhost only
ports:
  - "127.0.0.1:18123:8123"
```

This prevents the data tier from reaching the public internet even when the operator runs no host firewall. It is a one-line change in the official `docker-compose.yml`.

### R3 — Default secrets in production env templates (Langfuse, Helicone)

Production env templates must not ship working literal defaults. Replace `NEXTAUTH_SECRET="secret"` and `ENCRYPTION_KEY="0"*64` with a value that fails closed:

```bash
# Force the operator to generate a secret — startup fails without one
NEXTAUTH_SECRET="CHANGE_ME_OR_STARTUP_FAILS"
```

A startup assertion that rejects the placeholder value prevents the copy-the-example-and-forget failure mode entirely.

### R4 — Unauthenticated info endpoints (LangSmith)

`/api/v1/info` should gate `customer_info` behind auth and return only version metadata to anonymous callers. Customer identity is operational intelligence and should not be pre-auth.

### Future automation

VisorBishop is the automation answer, and it was built this session. The loop is the deliverable: any new discovery expressed as a fingerprint gets added to a prober, then VisorBishop re-sweeps the existing corpora to find what the manual walk missed. iter-1 doubled the Phase 2 yield with that mechanism alone. The discipline going forward: every new platform survey runs twice — once manually to build the fingerprint, once via VisorBishop to catch what the manual walk missed. The two passes catch different failure modes.

```bash
# Periodic re-sweep of a known population — tracks which hosts got patched,
# which operators went offline, which new exposures appeared
visorbishop -i known-population.txt -ip-shadow-all -c 32 -timeout 4s \
  -json sweep-$(date +%F).json -csv sweep-$(date +%F).csv
# Pipe the JSON into the NuClide findings ledger
visorlog ingest sweep-$(date +%F).json
```

Pre-filter any disclosure batch through VisorBishop. Disclosure across 5,391 ip:port pairs is materially different from 2,710 confirmed instances (Insight #15); the non-instances generate noise complaints for operators who do not run the platform.

---

## 8. Limitations and Assumptions

| # | Limitation | Risk Implication |
|---|---|---|
| L1 | Analysis reconstructed from case studies, evidence directories, and git history. This session was not assigned a session number; execution trace is iteration-granular, not timestamp-granular. | Timestamps within 05-11/05-12 are approximate. Iteration ordering is exact; wall-clock ordering within an iteration is inferred. |
| L2 | Data-tier probes stopped at schema and structure by ethical design. ClickHouse rows, Qdrant vector contents, MLflow run bodies, and Phoenix trace bodies were never retrieved. | No finding reached CRITICAL. The data class on each host is inferred from schema and source, not observed. Real impact may be higher. |
| L3 | Shodan dork hits contain roughly 50% false positives (Insight #15); confirm rates ranged from 7.3% (MLflow) to 95% (Phoenix). | Population counts are only meaningful as confirmed-instance counts. Raw dork totals overstate by up to an order of magnitude. |
| L4 | iter-8 used 200-host samples per platform, not full-population sweeps. | The iter-8 null finding (1 critical across 6 platforms) is a strong sample signal but not a population census. A full Langflow (33K) or Airflow (46K) sweep could surface additional critical hosts. |
| L5 | The Phase 5 LiteLLM cost-at-risk figure ($60K/mo conservative, $2M-7M/yr realistic) is a model built on a provider price table and a 10M-tokens/model/month abuse assumption. | The dollar figure is an estimate, not a measurement. Provider list prices drift quarterly; the pricing table needs maintenance. |
| L6 | CVE-2023-1177 on 28 MLflow hosts was flagged by version banner only; the path-traversal was not exploited. | The 28-host count is "likely vulnerable," not "confirmed exploitable." |
| L7 | LangSmith is closed-source; the `playground_auth_bypass_enabled` flag could not be verified past 401-returning endpoints. | The flag's actual behavior is unknown. It is recorded as UNRATED, not as a finding. |
| L8 | Internal-only platform deployments are not visible to Shodan. | The confirmed populations are a lower bound on the true exposed-platform count. |
| L9 | Source-audit fingerprinting (Helicone, Langfuse) used default Docker config, not operator variation. | Operators who hardened the compose file deviate from the audited default; the latent-primitive findings apply to default-config operators only. |

---

## 9. Proof of Concept (PoC) Illustrations

> PoCs use minimal, read-only, or simulated interactions. No operator data extracted. No credentials used. No exploit payloads. Demonstrate existence and risk conceptually only.

### PoC 1: LiteLLM LLMjacking primitive probe

**Scenario:** An unauthenticated actor confirms a LiteLLM proxy is exposed and enumerates which upstream provider models the proxy will forward to, without sending a single chat completion.

```
REQUEST:
  GET /v1/models HTTP/1.1
  Host: <operator-host>:4000

RESPONSE:
  HTTP/1.1 200 OK
  Content-Type: application/json

  {
    "data": [
      {"id": "<model-id-1>", "object": "model", "owned_by": "openai"},
      {"id": "<model-id-2>", "object": "model", "owned_by": "anthropic"},
      {"id": "<model-id-3>", "object": "model", "owned_by": "bedrock"}
    ],
    "object": "list"
  }
```

**Demonstrated:** A 200 with a populated `data` array confirms the LiteLLM proxy answers unauthenticated requests and reveals the operator's configured upstream models across multiple providers. This is the LLMjacking primitive: the same endpoint that lists models also accepts `/v1/chat/completions`, and the proxy holds the operator's provider keys. The PoC stops at enumeration. It does NOT send a completion, does NOT spend the operator's money, and does NOT extract the keys — it confirms the surface and the provider stack only. A 401 here would mean the master key is set and the host is not a finding.

### PoC 2: MLflow Tracking unauthenticated experiment probe

**Scenario:** An unauthenticated actor confirms an MLflow Tracking server is exposed and verifies the data layer is reachable, distinguishing a real exposure from a fresh empty deployment.

```
REQUEST:
  GET /api/2.0/mlflow/experiments/search?max_results=10 HTTP/1.1
  Host: <operator-host>:5000

RESPONSE:
  HTTP/1.1 200 OK
  Content-Type: application/json

  {
    "experiments": [
      {"experiment_id": "0", "name": "Default", "lifecycle_stage": "active"},
      {"experiment_id": "1", "name": "<operator-experiment-name>",
       "artifact_location": "s3://<operator-bucket>/<path>"}
    ],
    "next_page_token": ""
  }
```

**Demonstrated:** A 200 with a populated `experiments` array containing a non-default, non-scanner-decoy name confirms the operator logs real work to an unauthenticated tracking server. The `artifact_location` field discloses the cloud bucket name and path — a second-order disclosure surface independent of the MLflow server's auth state. This is the load-bearing distinction from Insight #16: a 200 with `"experiments": []` is the platform alive but empty, not an exposure. The auth-state classification requires reading the body, not the status code. The PoC reads the experiment list only. It does NOT call `runs/search` for run params, does NOT read run tags for credentials, and does NOT fetch artifacts — it confirms the data layer is reachable and populated, nothing more.

---

*Prepared by NuClide Research (Nicholas Kloster + Claude Sonnet 4.6) · 2026-05-11 to 2026-05-12 · VisorBishop productization + observability Phase 2*
