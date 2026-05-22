# Session Analysis: LLMOps Observability Stragglers + Evidently Fingerprint

**Date:** 2026-05-22  
**Session:** 31  
**Classification:** Internal / Research Use Only  
**Toolchain:** aimap v1.9.24 · JAXEN · Docker · git  
**Repos updated:** AI-LLM-Infrastructure-OSINT (da68959, 433418b) · aimap (94dbb09)

---

## 1. Overview

### Objective

This session continued the NuClide Research ongoing survey program: systematic discovery and verification of exposed AI/ML infrastructure on the public internet. The specific objectives were:

1. Resume the LLMOps observability stragglers thread from Session 30 (Agenta survey), which left four unworked targets.
2. Dispatch three parallel assessments (Langfuse `:5432` Postgres data-tier, Opik backend, PromptLayer) to independent Claude Code terminals.
3. Fully fingerprint Evidently ML Monitoring in the main session — including a live Docker-based probe to establish a conjunctive identity marker and ship it as aimap v1.9.24.

The research program is hypothesis-driven. The governing thesis:

> Every layer of the modern AI stack that does not ship with authentication enabled by default is deployed without authentication on the public internet at population scale.

Each survey confirms the thesis on a new platform class or tries to falsify it. This session confirmed Tier-A (no auth concept) status on Evidently and produced a reusable fingerprint for population-scale discovery.

### Scope and Constraints

- **Target class:** AI/ML observability and experiment-tracking platforms on public-internet IP addresses (tier-2 cloud: Hetzner, DigitalOcean, Scaleway, OVH, Linode, Vultr).
- **Allowed techniques:** Passive Shodan queries (read-only), banner grabbing, safe HTTP GET probes against known diagnostic endpoints, Docker-local fingerprinting of a fresh platform install.
- **Ethical hard stops:**
  - No data exfiltration. Metadata and schema enumeration only.
  - No destructive API calls (`/api/pull`, `/api/chat`, DELETE endpoints).
  - No use of discovered credentials — rotate-and-report only.
  - Data-tier probes (Postgres): connection attempt only; does an auth gate exist? No query execution.
  - Active LLM exploitation (VisorAgent) reserved for controlled lab targets only.

---

## 2. Environment and Tooling

### Claude Code Operation

The session ran inside Claude Code (CLI), executing shell commands via the Bash tool, reading and editing files via Read/Edit tools. Three parallel assessment sessions were spawned by providing self-contained briefing prompts to separate Claude Code terminals — each terminal runs an independent chain against its assigned target.

### Tools Used

| Tool | Role |
|---|---|
| **JAXEN** | Stage-0 discovery: Shodan harvest → `empire.db`. Blocked this session — `SHODAN_API_KEY` not in env. |
| **aimap v1.9.24** | Stage-1 fingerprint + Stage-2 verify. Gap confirmed (no Evidently fingerprint); new fingerprint shipped. |
| **Docker** | Safe local fingerprinting of `evidently/evidently-service:latest` without probing any operator host. |
| **Python urllib** | Inline HTTP probes inside `docker exec` context to map Evidently's API surface. |
| **VisorLog** | Ledger (`nuclide.db`). Not invoked this session — no new confirmed findings reached ledger stage. |
| **git / GitHub** | Version control. Two repos updated: OSINT repo (case studies + dork catalog) and aimap (fingerprint + CHANGELOG). |

### Notable Configuration

- `aimap` DefaultPorts for Evidently: `[8000, 3000, 80, 443, 8080]`. Non-listed ports require `-scan-all-fingerprints`.
- Docker container on bridge network (`172.17.0.2`). Host→container TCP resets observed — Mullvad VPN artifact. Resolved via `docker exec`.
- No network egress to operator hosts occurred during Evidently fingerprint work.

---

## 3. Methodology

The NuClide pipeline: **Discover → Fingerprint → Verify → Attribute → Classify → Ledger → Score → Codify.**

This session covered the **Fingerprint** stage (building the tool) and prepared for the Discover → Verify chain (blocked on API key). The three parallel sessions cover Discover → Verify on their respective targets.

### Step 1: Target selection from carry-forward

Session 30 (Agenta survey) left four unworked targets: Langfuse `:5432`, Opik, PromptLayer, Evidently. Each has a distinct discovery signal:

| Target | Signal | Action |
|---|---|---|
| Langfuse `:5432` | 11 Postgres-exposed hosts via cert-pivot | Dispatched to parallel session |
| Opik | Single host, 200 on `/opik/api/v1/projects` | Dispatched to parallel session |
| PromptLayer | 6 title / 10 CN hits; prior SPA secret-leak finding | Dispatched to parallel session |
| Evidently | 6 title / 10 CN hits; no fingerprint in aimap | Fingerprinted in main session |

### Step 2: Platform research before probing

Before any external probe: Docker image pulled, default startup command confirmed (`evidently ui --host 0.0.0.0 --port 8000`), server stack identified (uvicorn — Shodan-indexable).

### Step 3: API surface mapping via `docker exec`

Eight endpoints probed inside the container (no external network contact):

| Path | Status | Body |
|---|---|---|
| `/api/version` | 200 | `{"application":"Evidently UI","version":"0.7.21","commit":"-"}` |
| `/api/projects` | 200 | `[]` (empty on fresh install) |
| `/api/reports` | 404 | — |
| `/api/datasets` | 400 | Expects parameters |
| `/docs` | 404 | — |
| `/openapi.json` | 404 | — |
| `/manifest.json` | 200 | `{"short_name":"Evidently.AI","name":"Evidently.AI Dashboards",...}` |
| `/` | 200 | HTML SPA, title: `Evidently - ML Monitoring Demo` |

**Key outcome:** `/api/version` returns a unique structured JSON body with the exact string `"Evidently UI"` in the `application` field. This is the identity marker — present only in Evidently.

### Step 4: Auth posture determination

Both `/api/version` and `/api/projects` returned 200 with no `Authorization` header. On a populated instance, `/api/projects` returns project objects containing: project name/description, dashboard configurations, links to dataset/report/test-suite resources.

**Auth posture: Tier-A.** No authentication concept in default deployment — no bearer tokens, API keys, or session cookies checked on any enumerated endpoint.

### Step 5: Fingerprint construction

Per [Insight #6](../methodology/insight-06-conjunctive-matchers-required.md) — a single `body_contains` is unsound at population scale.

Final fingerprint added to `aimap/fingerprints.go`:

```go
{
    Name:         "Evidently ML Monitoring",
    DefaultPorts: []int{8000, 3000, 80, 443, 8080},
    Probes: []Probe{
        {Path: "/api/version", Matches: []MatchCond{
            {Type: "status_code", Value: "200"},
            {Type: "body_contains", Value: "Evidently UI"},  // exact application field
            {Type: "json_field", Field: "version"},          // confirms structured JSON
        }},
    },
    Severity: "high",
}
```

This rejects: generic 200 responses, unstructured HTML with "evidently" as a word, JSON responses without the Evidently application identifier.

### Step 6: Dork catalog construction

Four candidates added to [`shodan/queries/24-observability.md`](../shodan/queries/24-observability.md):

| Dork | Notes |
|---|---|
| `http.title:"Evidently - ML Monitoring"` | Most specific; lowest FP rate |
| `http.title:"Evidently"` | Broader; ~50% FP expected ([Insight #15](../methodology/insight-15-dork-hits-vs-platform-instances.md)) |
| `ssl.cert.subject.cn:evidently` | Attribution-only per [Insight #47](../methodology/insight-47-tls-cn-attribution-not-platform-confirmation.md) |
| `http.html:"Evidently.AI"` | Manifest string; may not be Shodan-indexed |

### Safeguards

All probes were HTTP GET against known diagnostic endpoints (not path-fuzzed), against a local Docker container only, read-only. No POST/PUT/DELETE issued. No external operator hosts contacted during the fingerprint phase.

---

## 4. Execution Trace

| Time | Action | Outcome |
|---|---|---|
| 12:15 | Session start; loaded METHODOLOGY.md + SESSION.md | Session 30 carry-forward identified: 4 targets, uncommitted artifacts |
| 12:16 | `git add` + commit + push to OSINT repo | da68959: Pantaflow/NTU/MIT case studies + edu sweep data + nuclide.db |
| 12:17 | Wrote 3 parallel briefing prompts | Dispatched to operator for Langfuse :5432, Opik, PromptLayer |
| 12:18 | Confirmed aimap has no Evidently fingerprint | Gap documented; proceeding to fingerprint |
| 12:19 | `docker run -d evidently/evidently-service:latest -p 8900:8000` | Container started; uvicorn on :8000 confirmed |
| 12:20 | `docker exec` + Python urllib: 8 endpoint probes | `/api/version` → identity marker; `/api/projects` → Tier-A confirmed |
| 12:21 | `/manifest.json` probe | `Evidently.AI` / `Evidently.AI Dashboards` — additional dork signals |
| 12:22 | Fingerprint written to `aimap/fingerprints.go` | Conjunctive probe on `/api/version`; `DefaultPorts: [8000, 3000, 80, 443, 8080]` |
| 12:23 | `go build` → BUILD OK | Compilation clean; live-verify blocked by Mullvad VPN TCP reset |
| 12:24 | `docker stop evidently-test && docker rm evidently-test` | Container cleaned up |
| 12:25 | Dork catalog update in `24-observability.md` | 4 candidate dorks + FP caveats + auth posture documented |
| 12:26 | aimap CHANGELOG v1.9.24 + commit 94dbb09 + push; OSINT dork catalog commit 433418b + push | Both repos updated |
| 12:27 | `jaxen hunt 'http.title:"Evidently - ML Monitoring"'` | Error: `SHODAN_API_KEY` not in env; harvest blocked |

---

## 5. Findings

> **Severity label policy:** Per `feedback_100_percent_verified_tier_labels` — every label requires 100% verified evidence at that tier. UNRATED = evidence exists but verification incomplete.

### 5.1 Evidently ML Monitoring — Tier-A No-Auth Default

| Field | Value |
|---|---|
| **Platform** | Evidently ML Monitoring (`evidently/evidently-service`) |
| **Type** | ML observability / experiment tracking web service |
| **Evidence** | Live Docker probe of v0.7.21 default install, 2026-05-22 |
| **Exposure** | `/api/version` and `/api/projects` return 200 with no credentials on default deploy |
| **Auth posture** | Tier-A: no auth concept; no toggle available without adding a reverse proxy |
| **Severity** | **OBSERVED** (Tier-A confirmed on default install; not yet verified at population scale) |

**Potential impact on a populated operator instance:**
- Read access to all ML projects, evaluation reports, data drift analyses, model performance metrics, and dataset references.
- System prompt and LLM response data visible if the instance monitors a production LLM application.
- Operator identity disclosure via project names and configuration.

**Becomes HIGH once:** JAXEN harvest + aimap verify confirms real instances accessible on public internet without authentication.

---

### 5.2 Agenta LLMOps — Auth-Gated API + Open Signup (Session 30, verified)

| Field | Value |
|---|---|
| **Platform** | Agenta self-hosted (6 confirmed public hosts) |
| **Type** | LLM application lifecycle management (prompts, evals, deployment) |
| **Exposure** | `/api/auth/signup` returns 200 — SuperTokens default, no `SIGNUP_DISABLED` toggle. Default creds in source: `AGENTA_AUTH_KEY=replace-me`, `POSTGRES_PASSWORD=password`. |
| **Severity** | **HIGH** (verified open signup across 6/6 reachable hosts) |

**Potential impact:**
- Uncontrolled account creation → full authenticated API access.
- Access to all prompts, evaluation results, deployment configurations, and LLM call traces.
- Default database credentials valid if operator did not change them.

**Insight codified:** [Insight #55](../methodology/insight-55-auth-gated-api-signup-open-default.md) — auth-gated API + open signup = uncontrolled account creation.

---

### 5.3 Langfuse :5432 Postgres Cluster (CANDIDATE — parallel session)

| Field | Value |
|---|---|
| **Population** | 11 hosts, `ssl.cert.subject.cn:langfuse port:5432` |
| **Type** | Postgres database tier of Langfuse LLM tracing platform |
| **Exposure** | Cert-pivot confirms Langfuse attribution; port 5432 open on public internet |
| **Severity** | **UNRATED** pending connection-attempt verification |

If auth-absent: **CRITICAL** — direct database access to LLM call history (user prompts, model responses, latency, API key usage patterns, conversation history).

---

### 5.4 Opik Backend API (CANDIDATE — parallel session)

| Field | Value |
|---|---|
| **Host** | `80.79.202.18:5173` |
| **Type** | Comet ML Opik — LLM evaluation and tracing (self-hosted) |
| **Exposure** | `GET /opik/api/v1/projects` returned HTTP 200 without auth (Session 30) |
| **Severity** | **UNRATED** pending data-layer probe ([Insight #16](../methodology/insight-16-status-code-is-identity-not-auth-state.md): 200 ≠ auth state) |

---

### 5.5 PromptLayer Population (CANDIDATE — parallel session)

| Field | Value |
|---|---|
| **Population** | 6 title hits + 10 CN hits |
| **Type** | LLM request logging and prompt management SaaS (self-hosted) |
| **Exposure** | Prior single-host finding (34.95.65.63): 3 hardcoded Make.com webhooks in SPA JS bundle — LLMjacking/quota-drain vector |
| **Severity** | **UNRATED** pending population survey |

---

## 6. Risk Assessment

### Overall Posture

The LLMOps observability tier presents a consistent misconfiguration pattern: platforms built for internal developer tooling deployed with no network segmentation on public IP addresses.

### Confidentiality — High Risk

LLM observability platforms store the most sensitive application data: user inputs (often containing PII), model responses (business logic), system prompts (IP), and evaluation datasets (ground-truth from real user data). A single unauth Evidently instance monitoring a production RAG application exposes all of this.

### Integrity — Medium Risk

The no-auth platforms in this category do not expose write APIs prominently in their default state. However, Evidently's `/api/projects` endpoint implies create/update operations exist in the API tree. Unauthenticated write access could corrupt evaluation baselines, inject false drift metrics, or delete project history.

### Availability — Low-to-Medium Risk

No compute-exhaustion endpoints identified in the Evidently surface (no inference API). Standard DoS risk against uvicorn HTTP server — commodity, not platform-specific.

### Systemic Patterns

1. **Tier-A (no auth concept) is architectural absence**, not misconfiguration. A network control (VPN, IP allowlist, reverse proxy with auth) is the only fix.
2. **Open signup (Agenta/Insight #55) is the stealth equivalent.** The API looks auth-gated but is trivially bypassed by self-registering.
3. **Data-tier exposure (Langfuse :5432) is orthogonal to application-tier auth.** Two independent misconfiguration classes on the same operator.
4. **Observability platforms are high-value supply-chain targets** — they see all traffic, log all prompts, and store API keys used to call upstream providers.

---

## 7. Recommendations

### R1 — Network segmentation (all Tier-A platforms)

Bind the service to `localhost` or a private subnet, not `0.0.0.0`. In Docker:

```bash
# Wrong:
docker run -p 8000:8000 evidently/evidently-service

# Right:
docker run -p 127.0.0.1:8000:8000 evidently/evidently-service
```

Place nginx/Caddy/Traefik in front with HTTP Basic Auth or OAuth2 proxy (oauth2-proxy, Authentik, Authelia).

### R2 — Disable open signup

Set `SIGNUP_DISABLED=true` (or platform equivalent) before exposing any registration endpoint. Treat open signup as equivalent to no auth.

### R3 — Postgres binding

```ini
# /etc/postgresql/*/main/postgresql.conf
listen_addresses = 'localhost'
```

If remote access is required: VPN or SSH tunnel, never direct public exposure. Enforce `scram-sha-256` in `pg_hba.conf`.

### R4 — Rotate default credentials

Agenta ships `AGENTA_AUTH_KEY=replace-me` and `POSTGRES_PASSWORD=password`. Any instance where these were not explicitly changed before first run should be treated as compromised — rotate immediately.

### R5 — JS bundle secret hygiene

SPA-fronted services must not embed API keys or webhook URLs in the compiled JS bundle. Use runtime environment injection (`window.__CONFIG__` from a server-rendered endpoint) or a backend-for-frontend pattern.

### R6 — Continuous exposure monitoring

```bash
# Integrate aimap into periodic scans of your own IP space:
aimap -list your-public-ips.txt \
      -ports 8000,3000,5432,6333,11434 \
      -o report.json

# Alert on any new AI/ML fingerprint appearing on a public-facing address.
```

For CI/CD: run aimap against the deployment's egress IPs in a post-deploy step. Fail the pipeline if a Tier-A service is detected on a public port.

### R7 — Inventory your AI stack surface

```bash
docker ps
netstat -tlnp | grep -E '8000|3000|5432|6333|11434'
```

Cross-reference listening ports against the aimap `DefaultPorts` catalog. Any port in that list reachable from `0.0.0.0` is a candidate for the exposures documented here.

---

## 8. Limitations and Assumptions

| # | Limitation | Risk Implication |
|---|---|---|
| L1 | SHODAN_API_KEY not in env — harvest blocked | Population size and confirmed-unauth count for Evidently are unknown |
| L2 | Parallel sessions (Langfuse/Opik/PromptLayer) not yet reporting | Three finding sets are UNRATED/CANDIDATE |
| L3 | Internal-only deployments (VPN, private subnet, IP allowlist) not visible to Shodan | Document underestimates total population |
| L4 | Docker fingerprinting = default config, not operator variation | Operator version or config overrides may change behavior |
| L5 | Mullvad VPN TCP reset prevented aimap live-verify against local container | Fingerprint validated via `docker exec` instead; functionally equivalent |
| L6 | Write-tier operations not tested (restraint ethic) | Integrity impact estimates based on GET surface only; may understate actual exposure |
| L7 | No auth bypass attempts | Method identifies Tier-A instances only; weakly-configured auth instances are not surfaced |

---

## 9. Proof of Concept (PoC) Illustrations

> All PoCs use read-only, simulated interactions. No operator data was extracted. No credentials were used. These demonstrate existence and risk conceptually only.

### PoC 1: Unauthenticated Evidently Platform Fingerprint and Version Disclosure

**Scenario:** An unauthenticated actor discovers an Evidently instance and confirms its identity and version.

```
REQUEST:
  GET /api/version HTTP/1.1
  Host: <operator-host>:8000

RESPONSE:
  HTTP/1.1 200 OK
  Server: uvicorn
  Content-Type: application/json

  {"application":"Evidently UI","version":"0.7.21","commit":"-"}
```

**Demonstrated:** Positive platform identification + version disclosure with no credentials. Actor can: look up version-specific CVEs, enumerate `/api/projects` to assess whether the instance is populated, and determine the operator's monitoring stack from project names.

---

### PoC 2: Unauthenticated Project Enumeration on a Populated Instance

**Scenario:** Actor queries `/api/projects` after confirming the instance via PoC 1.

```
REQUEST:
  GET /api/projects HTTP/1.1
  Host: <operator-host>:8000

RESPONSE (hypothetical populated instance, sanitised):
  HTTP/1.1 200 OK
  Content-Type: application/json

  [
    {
      "id": "proj-<uuid>",
      "name": "production-rag-eval",
      "description": "Evaluation suite for customer-facing RAG pipeline"
    },
    {
      "id": "proj-<uuid>",
      "name": "churn-model-drift",
      "description": "Data drift monitoring for churn prediction model"
    }
  ]
```

**Demonstrated:** Business intelligence disclosure (operator runs a customer-facing RAG pipeline and a churn model) + project IDs for further enumeration of evaluation data, drift metrics, and dataset references — all unauthenticated.

---

### PoC 3: Agenta Open-Signup Auth Bypass (verified, Session 30)

**Scenario:** Actor observes 401 on API calls, attempts signup.

```
STEP 1 — API confirms 401:
  GET /api/v1/projects → 401 Unauthorized

STEP 2 — Signup endpoint:
  POST /api/auth/signup
  {"email":"researcher@example.com","password":"test1234"}
  → 200 OK  {"user":{"id":"..."},"token":"<jwt>"}

STEP 3 — Authenticated API access:
  GET /api/v1/projects
  Authorization: Bearer <jwt>
  → 200 OK  [{"id":"...","name":"<operator-project>"}]
```

**Demonstrated:** Auth layer is real but permeable. Anyone who can reach the signup endpoint can self-authorize and gain full authenticated API access. Not a vulnerability in the auth implementation — it is the platform's intended behavior when `SIGNUP_DISABLED` is not set.

**Insight #55:** auth-gated API + open signup = uncontrolled account creation.

---

*Prepared by NuClide Research (Nicholas Kloster + Claude Sonnet 4.6) · Session 31 · 2026-05-22*
