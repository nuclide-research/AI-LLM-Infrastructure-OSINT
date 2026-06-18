# Session Analysis: RAG Framework Servers (LlamaIndex / Haystack / LightRAG / Microsoft GraphRAG)

**Date:** 2026-06-17 to 2026-06-18
**Session:** Cat-RAG-Framework-Servers
**Classification:** Internal / Research Use Only
**Toolchain:** shodan-fetch (Playwright MCP in-page fetch), scanner (Step 0c banner grab), aimap v1.9.51 -> v1.9.55, agent-logging-system, VisorGraph cert-pivot, aimap-profile, JS-bundle extract, BARE, VisorLog, VisorScuba, recongraph
**Repos updated:** AI-LLM-Infrastructure-OSINT (survey dir cat-rag-framework-servers-2026-06-17) · aimap (v1.9.55, 5 RAG fingerprints)

---

## 1. Overview

### Objective

Survey the RAG **framework** tier (the pipeline above the vector DBs: LlamaIndex, Haystack/hayhooks, LightRAG, Microsoft GraphRAG) against the auth-on-default thesis. The Stage -1 OSINT read predicted three of four platforms ship auth-off (Tier-A / Tier-A*) and one (GraphRAG) pushes auth to an APIM gateway the app itself does not enforce. The thesis question: does a new platform class confirm the auth-on-default pattern, and does the framework tier leak ingested documents, retrieval logic, and provider bindings even where the underlying vector store is locked?

The aimap fingerprint inventory had a gap on this class (LlamaIndex, Haystack, GraphRAG-accelerator all unbuilt; LightRAG keyed on port+title only and missed auth-state). Building and adversarially verifying those fingerprints was a co-equal objective with the population survey.

### Scope and Constraints

- **Target classes:** RAG framework servers on Shodan-indexable surface (LightRAG :9621, LlamaIndex :8000/:4501, hayhooks :1416/:1417, GraphRAG-accelerator :443/:8000) plus shadow-port co-deploys (Qdrant :6333, Ollama :11434, Neo4j :7474, Postgres :5432, Redis :6379).
- **Allowed techniques:** passiveV2 Shodan harvest, active TCP/TLS banner grab, safe HTTP GET on identification endpoints (`/health`, `/collections`, `/api/tags`, `/db/data/`), single confirm-probe on chat endpoints, JS-bundle static read, cert-pivot WHOIS/CT attribution.
- **Ethical limitations:**
  - No data exfiltration. `data_accessed=false` on every finding. Names and counts ARE the finding.
  - No destructive API calls (no `/api/pull`, no `/api/generate`, no `/documents/upload`, no Qdrant write/delete).
  - No use of discovered credentials.
  - Data-tier probes: connection + auth-gate check only. No record reads, no graph dumps, no document content.
  - Sensitivity on the Mobee corpus is inferred from operator class only. No document was read.
  - Disclosure routing is out of scope for this artifact.

---

## 2. Environment and Tooling

### Claude Code Operation

Orchestrator + subagent delegation throughout. Stage -1 ran four parallel OSINT lanes (one per platform). The harvest, scan, and verify stages ran orchestrator-driven with the Playwright MCP held as a browser singleton. Cert-pivot attribution and the JS-bundle read were dispatched as scoped subagent tasks against the five confirmed-finding hosts. The aimap fingerprint build ran as a focused tool-build cycle inside the main session.

### Tools Used

| Tool | Role | Config notes |
|---|---|---|
| shodan-fetch (Playwright MCP) | Stage-0 discovery: authed in-page `fetch()` harvest | 0 API credits; concurrent burst tripped 429 mid-run |
| scanner (Step 0c) | Active TCP/TLS banner on all harvested IPs | 549 candidates -> 223 live -> 175 clean (48 tarpits stripped) |
| aimap v1.9.51 -> v1.9.55 | Fingerprint + deep-enum | 5 RAG fingerprints built and adversarially verified this session |
| agent-logging-system | Post-aimap per-enumerator FP-candidate scan | error-rate gate on the new fingerprints |
| VisorGraph cert-pivot | Operator attribution from cert CN/SAN | mobee.com tied to host via Cloudflare Origin CA SAN |
| aimap-profile | Target classification + ethics flags | passive; 5 finding hosts profiled |
| JS-bundle extract | SPA secret + route-table read on app.babbid.com | caught the F6 framework mislabel |
| BARE | Semantic module ranking | findings fed via adapter |
| VisorLog | Ledger ingest -> nuclide.db | |
| VisorScuba | Compliance scoring | |
| recongraph | Seed-polymorphic recon over finding hosts | |

Not run: VisorAgent (ethical-stop, controlled targets only), VisorHollow (Windows-only). Censys (Step 0b) blocked this run (feature-credit bucket), which left Haystack population unmeasurable past the Shodan-dark wall.

### Notable Configuration

- shodan-fetch tripped a **Shodan 429** on a concurrent page-2/page-3 burst. Page-1 totals stayed reliable; deep-pagination IP samples were undercounted until a throttled re-harvest. Logged in query-log.md as a result, not a skip.
- 48-host tarpit fleet (open >= 8 ports; 21 hosts open all 25 probed) stripped pre-aimap. aimap `-scan-honeypots` default also skips these.
- aimap fingerprint build hit a **DefaultPorts-fronting bug** (see Execution Trace) caught only by a live demo against 52.69.81.89.

---

## 3. Methodology

### Enumeration approach

Four-platform parallel OSINT first (Stage -1), producing the dork set, port set, and verification primitive per platform before any probe. Then shodan-fetch harvest by brand string and bare port, scanner banner-grab to strip dead hosts and tarpits, aimap fingerprint+enum on the clean live subset, and verify (3v) on every candidate before any label promoted.

### Candidate identification

Conjunctive fingerprints anchored on platform-unique schema, not bare ports (bare :9621 / :4501 / :1416 are FP-heavy supersets). LightRAG keys on `/health` returning `core_version` + `webui_title` + `auth_mode`. The `auth_mode` field is a machine-readable auth-state decoder: it confirms platform AND auth posture in one read with no exfiltration. The GraphRAG / LightRAG dork collision was the central FP trap (`title:"GraphRAG"` catches LightRAG, MS GraphRAG wrappers, Tencent Youtu-GraphRAG, university chatbots) and was handled with an exclusion subtraction per Insight #102.

### Validation checks

- **LightRAG:** `GET :9621/health` -> `auth_mode:"disabled"` + reachable confirms unauth (Insight #40 auth-on-default). `/documents` checked separately: 2 hosts gate `/documents` 403 despite `auth_mode=disabled` -> **verify the endpoint, not the global flag**.
- **Qdrant:** `GET /collections` 200 no-auth + `points_count` per collection. Names and counts only.
- **Ollama:** `GET /api/tags` 200 no-auth, model list read. `/api/generate` NOT exercised (Insight #39 attribution-laundering / cost-shift).
- **Neo4j:** `GET /db/data/` checked for auth gate. All 8 returned 401 -> refuted (R1).
- **Chat endpoint:** single confirm probe. A 422 means wrong request format, not access denied (probe `message`/`messages`/`query` variants before declaring denied).

### Safeguards

No brute forcing, no privilege escalation, no data exfiltration, no write-tier operations, no credential use. F6 was confirmed with a single chat probe and stopped (no chat-history read, no `/api/files` traversal). The Mobee corpus was confirmed populated by status-bucket counts only; no document content read. The flagship stacked host was re-probed read-only and **downgraded** when its three legs proved authed, rather than published on the strength of the lead.

---

## 4. Execution Trace

| Time | Action | Outcome / Decision |
|---|---|---|
| 06-17 ~14:00 | Stage -1 four-lane OSINT | Predicted 3/4 auth-off; LightRAG corrected Tier-A -> Tier-A* (auth exists, ships off); flagged aimap FP gaps to build |
| 06-17 ~19:15 | shodan-fetch harvest by brand + port | LightRAG ~93 strong; LlamaIndex 2 strong; Haystack 0 brand (Shodan-dark); GraphRAG 0 direct (APIM-gated) |
| 06-17 ~19:18 | Concurrent page-2/3 burst | **Shodan 429.** Page-1 totals reliable; samples undercounted. Logged; throttled re-harvest queued |
| 06-17 ~19:26 | scanner Step 0c on 549 candidates | 223 live; 48-host tarpit fleet stripped; 175 clean live -> aimap input |
| 06-17 ~19:30 | aimap RAG fingerprint build (LlamaIndex/Haystack/LightRAG/GraphRAG) | 5 fingerprints drafted; LightRAG hardened to anchor on `/health` json fields + wire `auth_mode` into auth_status |
| 06-17 ~19:33 | aimap v1.9.54 live demo on 52.69.81.89 (LightRAG :80 Swagger) | **DefaultPorts-fronting bug:** host served the LightRAG Swagger title on :80, but aimap returned `services:null` / 0 findings because the fingerprint only fired on its DefaultPorts list (9621), not on the port actually open. Caught by the demo, not by unit logic |
| 06-17 ~19:40 | aimap fix -> v1.9.55 | Fingerprint matches on observed-open port regardless of DefaultPorts; re-demo confirms LightRAG identified on :80 |
| 06-17 ~19:50 | agent-logging-system on aimap-report | per-enumerator FP-candidate scan; new fingerprints inside error-rate tolerance |
| 06-17 ~20:00 | aimap deep-enum on clean live subset | LightRAG 67 confirmed (50 unique IP); 2 Qdrant; 1 Ollama; 8 Neo4j; 4 MCP |
| 06-17 ~20:06 | LightRAG /health verify batch | 18 disabled / 44 enabled / 5 unknown = ~29% unauth at population (F4, F5) |
| 06-17 ~20:15 | 3v re-probe of LightRAG unauth subset | 9/13 bare-IP candidates currently live+unauth; 2 gate /documents 403 despite disabled |
| 06-17 ~late | Neo4j L-02 verify (top-ranked lead) | **REFUTED (R1):** all 8 `/db/data/` 401. The highest-ranked lead was wrong; graph backends authed |
| 06-17 ~late | Flagship 206.189.153.160 verify (C-03 "catastrophe") | **REFUTED (R2):** all 3 legs authed (LightRAG /documents 401, Neo4j 401, Redis NOAUTH). Downgraded HIGH-CRITICAL lead -> LOW metadata-disclosure |
| 06-18 ~00:00 | JS-bundle read on app.babbid.com (F6) | **Framework correction:** aimap fingerprinted LlamaIndex, but the SPA is Laravel+Inertia+Vue3. LLM/chat is server-side; bundle leaks zero secrets. Finding stands as unauth LLM chat, framework reclassified UNCONFIRMED |
| 06-18 ~00:00 | Host-header re-do on bare-IP "down" hosts | **Recovery (F7):** mobee.com (159.69.89.55) had been undercounted as down by bare-IP probe (nginx vhost-routed). Re-probed with Host from cert-SAN -> unauth LightRAG, ~600-doc production corpus on a regulated crypto exchange origin box |
| 06-18 ~00:09 | VisorGraph cert-pivot + aimap-profile on 5 finding hosts | Operator attribution; F7 tied to Mobee via Cloudflare Origin CA SAN `*.mobee.com` |
| 06-18 ~00:10 | findings.json / attribution.json / LEADS.md finalized | 7 confirmed (F1-F7), 2 refuted (R1-R2), 2 publishable negatives |

---

## 5. Findings

> **Severity label policy (load-bearing):** Every tier label requires 100% verified evidence at that tier. `data_accessed=false` on all. Each finding states its Insight #68 verification-rung pair (Depth A logic / B binary x Breadth 0 none / 1 host / 2 population).

### 5.1 Qdrant 82.165.133.93:6333 (Hanssen Agency): unauth, private Nextcloud document vectors

| Field | Value |
|---|---|
| **Name/ID** | 82.165.133.93:6333, collection `nextcloud-docs` |
| **Type** | Vector DB (RAG data tier) |
| **Evidence** | `GET /collections` 200 no-auth; `points_count` nextcloud-docs = 531 doc embeddings (+2 test collections) |
| **Observed exposure** | Unauthenticated full collection-management surface |
| **Severity** | **HIGH** (rung A/1). Data sensitivity high-pii-phi: the collection name matches `cloud.hanssen.agency` Nextcloud front; the agency's own self-hosted document corpus (contracts/proposals/client material, likely PII) vectorized for RAG. GDPR-DE |

**Potential impact:** semantic retrieval of private agency and client documents without auth; the vector store is the actual data tier even where the file store is locked. Operator: Hanssen Agency (Bodo Hanssen), single Plesk VPS on IONOS, multi-tenant (7 hostnames on one IP -> co-tenant blast radius).

### 5.2 LightRAG mobee.com 159.69.89.55:443 (Mobee): unauth, ~600-doc production corpus on a regulated financial operator

| Field | Value |
|---|---|
| **Name/ID** | 159.69.89.55:443 (vhost `static.55.89.69.159.clients.your-server.de`, operator mobee.com) |
| **Type** | LightRAG server (RAG framework, data tier) |
| **Evidence** | `/health` `auth_mode:"disabled"`; `/documents` status buckets processed:426 / failed:425 / parsing:105 / analyzing:9 / pending:34 (~600+ docs) |
| **Observed exposure** | Unauthenticated, populated production corpus; recovered only via Host-header re-probe (bare-IP undercounted it) |
| **Severity** | **HIGH** (rung A/1). Headline finding. Operator class regulated-financial (OJK Indonesia, ISO 27001), active Anthropic/Claude customer, origin host outside the Cloudflare proxy (no WAF in front of the RAG box). Data sensitivity high-pii-phi inferred from operator class only; NOT read |

**Potential impact:** unauthenticated RAG query and document inventory against a crypto-exchange origin box. The corpus is most plausibly internal KB / KYC-AML / support material derived from or containing customer PII and financial data. Boundary held: status counts only, no document content.

### 5.3 Qdrant 31.57.224.107:6333 (ilmverse.ai): unauth, public-text corpus

| Field | Value |
|---|---|
| **Name/ID** | 31.57.224.107:6333 |
| **Type** | Vector DB (RAG data tier) |
| **Evidence** | `GET /collections` 200; total points 71,037 (Quran ayah/tafsir) |
| **Observed exposure** | Unauthenticated full collection-management surface |
| **Severity** | **HIGH surface / LOW data-sensitivity** (rung A/1). Data is public religious text. Same IP carries Postgres:5432 adjacency + Neo4j (authed). Operator ilmverse.ai (commercial AI product) |

**Potential impact:** full unauth read/write/delete on the management surface; the corpus itself is public domain, so data-confidentiality impact is low while integrity/availability (collection deletion, poisoning) is the live concern.

### 5.4 LightRAG population: ~29% unauth at population scale (auth-on-default confirmed)

| Field | Value |
|---|---|
| **Name/ID** | LightRAG :9621 population (67 confirmed, 50 unique IP) |
| **Type** | RAG framework server |
| **Evidence** | `/health` auth_mode read across population: 18 disabled / 44 enabled / 5 unknown = ~29% unauth; 12/13 bare-IP candidates re-confirmed currently unauth at 3v |
| **Observed exposure** | Auth ships off (Tier-A*); operators inherit the default. 2 hosts gate `/documents` 403 despite `auth_mode=disabled` (endpoint-gating independent of the global flag) |
| **Severity** | **HIGH** (rung A/2). Population-scale thesis confirmation |

**Potential impact:** at population scale the framework tier exposes RAG query (ingested-document exfil + system-prompt leak), corpus inventory, and Ollama-emulation LLMjacking on roughly a third of instances. The 2 endpoint-gated hosts establish that auth_mode=disabled does not equal all-endpoints-open.

### 5.5 LightRAG /health config-disclosure: PLATFORM flaw on all 67 instances (incl. auth-enabled)

| Field | Value |
|---|---|
| **Name/ID** | LightRAG `/health` (WHITELIST_PATHS default) |
| **Type** | Platform config-disclosure anti-pattern |
| **Evidence** | `/health` body leaks `configuration{llm_binding, llm_model}`, `embedding_model`, and `working_directory` paths (operator usernames + project names) on every instance, including auth-enabled ones |
| **Observed exposure** | `/health` is on the no-auth skip-list by default; the response carries provider/model bindings and filesystem paths |
| **Severity** | **HIGH** (rung A/2). Finding against the platform, not operators. One upstream fix protects the whole population |

**Potential impact:** discloses LLM provider/model (anthropic / azure_openai / aws_bedrock / openai / ollama / openrouter), embedding model, and working-directory paths that name operators and projects, regardless of whether the operator enabled auth. This is the highest-leverage finding because the fix is a single platform change.

### 5.6 LightRAG 9/17 + recovered hosts: confirmed currently-unauth subset

| Field | Value |
|---|---|
| **Name/ID** | 12/13 confirmed currently unauth after Host-header re-do (was 9/13 bare-IP) |
| **Type** | RAG framework server (subset verification) |
| **Evidence** | recovered: 51.142.10.48 (rag.neolen.com, empty), 167.172.40.40 (rag.achar7303ai.com, 4 docs), 159.69.89.55 (mobee.com, ~600); only 98.81.157.172 genuinely down |
| **Observed exposure** | vhost-routed instances reject bare-IP probes; re-probe with Host header before declaring down |
| **Severity** | **HIGH** (rung A/2). Methodology recovery |

**Potential impact:** the bare-IP probe method systematically undercounts vhosted unauth population. Establishes a probe-technique correction (see Insights).

### 5.7 app.babbid.com 108.132.72.10:443 (Babbid): unauth LLM chat inference (framework UNCONFIRMED)

| Field | Value |
|---|---|
| **Name/ID** | 108.132.72.10:443, app.babbid.com, `POST /api/chat` |
| **Type** | Server-side LLM chat endpoint |
| **Evidence** | single confirm probe: `POST /api/chat` 200, live LLM reply, stateful UUID session, zero auth gate |
| **Observed exposure** | Unauthenticated LLM inference on a named commercial operator |
| **Severity** | **HIGH** (rung B/1). Cost-abuse / LLMjacking surface. Operator Babbid Centros de Negocios (Spanish coworking SME). Data sensitivity low-public |

**Potential impact:** unauthenticated inference cost-shift to the operator's provider account. **Framework correction (JS-bundle):** aimap matched `/api/chat/config` as LlamaIndex, but the SPA is Laravel+Inertia+Vue3 and the LLM is entirely server-side. The bundle leaks zero secrets. The finding stands as unauth LLM chat; the underlying framework is UNCONFIRMED and the aimap match was a loose fingerprint here. The bundle did expose a full Ziggy 241-route table, a public `build/manifest.json`, a server-side editable system prompt + restore versioning (prompt-injection surface), and a git-SHA/branch/build-time disclosure (surface-open, no access exercised).

---

### REFUTED (would have been published falsehoods)

- **R1, Neo4j (8 hosts):** all `/db/data/` 401. Auth-on at the data plane. `:7474/` root leaks version only (info / CVE-scoping). The top-ranked lead of the survey was wrong; the graph backends are authed.
- **R2, flagship 206.189.153.160 (LightRAG + Neo4j + Redis "catastrophe"):** all three legs authed (LightRAG `/documents` 401, Neo4j 401, Redis NOAUTH). Downgraded to **LOW metadata-disclosure** (storage topology + OpenRouter model + versions via `/health` + `/auth-status`). Recon / CVE-scoping value, no unauth record read.

### NEGATIVE SPACE (publishable nulls)

- **Microsoft GraphRAG accelerator:** 0 direct exposure. `/manpage/openapi.json` and accelerator routes Shodan-dark; APIM-gated by default. Thesis-confirming (gateway-auth-default produces ~0 unauth). Cannot measure a bypass-APIM misdeploy without host evidence.
- **Haystack / hayhooks:** Shodan-dark on every brand string (JSON root, no HTML title to index). `http.html:"Hayhooks"` / `"deepset"` / `"deploy_files"` all genuine 0. Population reachable only via active 1416/1417 banner-grab or Censys (blocked this run). This is a discovery routing finding, not absence.

---

## 6. Risk Assessment

### Overall Posture

Systemic on three of four platforms. LightRAG confirms the auth-on-default thesis at population scale (~29% unauth) and adds a platform-level config-disclosure that affects all instances regardless of operator action. LlamaIndex confirmed Tier-A on at least one named commercial host. GraphRAG confirms the contrapositive: a gateway-auth-default design produces ~0 direct exposure. Haystack is a discovery-surface gap, not a posture statement.

### Confidentiality

Highest at F1 (private agency Nextcloud document vectors) and F2 (regulated crypto-exchange ~600-doc production corpus, PII inferred by operator class). F5 leaks provider bindings and filesystem paths across the whole LightRAG population. The data-tier (vector store, graph store) is the real confidentiality surface; the RAG front is the index over it.

### Integrity

F3 (ilmverse Qdrant) exposes a full read/write/delete management surface on a public-text corpus: collection deletion and corpus poisoning are reachable. LightRAG `/documents/upload` is a corpus-poisoning + path-traversal sink (CVE-2025-6773 class) on the unauth subset, present and not exercised.

### Availability

Unauth Ollama (F3 host) and the unauth LightRAG subset carry compute-exhaustion and quota-drain exposure. The Ollama instance is a cloud-passthrough to ollama.com, so open `/api/generate` would cost-shift to the paid upstream (Insight #39 attribution-laundering). Surface open, not exercised.

### Systemic Patterns

- **Platform-default propagation (Insight #13):** LightRAG ships auth off and `/health` on a no-auth skip-list. Both defaults are load-bearing; operators inherit them. F5 is the cleanest case: a single upstream change fixes the whole population.
- **Co-deploy shadow (Insight #12):** Qdrant, Postgres, Neo4j, and Redis cluster on the same IPs as the RAG fronts. The data tier is where the records live, and it was the lead the survey most wanted to be true (R1/R2 refuted it on these hosts).
- **Endpoint-gating > global flag:** `auth_mode=disabled` does not equal all-endpoints-open. Two hosts gate `/documents` 403 despite the disabled flag. Verify the endpoint, not the flag.

---

## 7. Recommendations

### R1. LightRAG: enable auth and strip config from /health

```bash
# Operator: enable the auth layer that ships off by default
export AUTH_ACCOUNTS='admin:<strong-pass>'   # or TOKEN_SECRET / JWT auth
# Verify it took:
curl -s http://localhost:9621/health | jq .auth_mode   # must NOT be "disabled"
```

```python
# Platform (upstream): remove /health from the no-auth WHITELIST_PATHS,
# or strip configuration{llm_binding,llm_model}, embedding_model,
# and working_directory from the /health response body.
```

The operator fix protects one instance. The platform fix (F5) protects every instance, including auth-enabled ones, because `/health` leaks bindings and paths regardless of auth state.

### R2. Vector / graph data tier: bind to localhost or gate with a key

```bash
# Qdrant: require an API key, do not expose :6333 to the internet
QDRANT__SERVICE__API_KEY=<strong-key>
# Neo4j stays authed at /db/data/ (R1 confirmed this works); keep :7474 off the public net
```

The vector store is the data tier. An open `/collections` with point counts is a recoverable semantic-content surface even where the file store is locked.

### R3. Server-side LLM chat: gate inference behind auth or rate-limit

```nginx
# Babbid pattern: POST /api/chat reachable unauth on a public app
location /api/chat { limit_req zone=chat burst=5; auth_request /verify; }
```

Unauthenticated inference is a cost-abuse vector even when no data leaks. Pair with provider-side spend caps.

### Future automation

```bash
# Post-deploy gate: fail the pipeline if the RAG front ships auth-off
aimap -list your-public-ips.txt -ports 9621,8000,4501,1416,6333,11434 -o report.json
jq -e '.services[] | select(.platform=="LightRAG" and .auth_status=="none")' report.json \
  && { echo "FAIL: unauth LightRAG"; exit 1; }
```

---

## 8. Limitations and Assumptions

| # | Limitation | Risk Implication |
|---|---|---|
| L1 | Censys (Step 0b) blocked (feature-credit bucket) | Haystack population unmeasurable past the Shodan-dark wall; count is a null, not a zero |
| L2 | Shodan 429 on concurrent page burst | Deep-pagination IP samples undercounted; page-1 totals reliable; throttled re-harvest required |
| L3 | Bare-IP probe undercounts vhosted services | Caught and recovered via Host-header re-do (F7 mobee.com); residual undercount likely in any host that returned 400/404/timeout and was not re-probed |
| L4 | Mobee corpus sensitivity inferred from operator class, not read | high-pii-phi is an inference, not a verified data class; restraint ethic held |
| L5 | F6 framework UNCONFIRMED | aimap `/api/chat/config` match was loose; the finding is unauth LLM chat, not confirmed LlamaIndex |
| L6 | Write-tier operations not tested | Qdrant/LightRAG write surfaces present and not exercised; integrity impact is reasoned, not demonstrated |
| L7 | GraphRAG bypass-APIM misdeploy not measurable | 0 direct exposure is honest negative space; cannot count a misconfig without host evidence |

---

## 9. Proof of Concept (PoC) Illustrations

> PoCs use minimal, read-only interactions. No operator data extracted. No credentials. No exploit payloads.

### PoC 1: LightRAG /health auth-state + config disclosure (F4 / F5)

**Scenario:** an unauthenticated reader confirms platform, auth posture, provider binding, and operator filesystem paths in one GET.

```
REQUEST:
  GET /health HTTP/1.1
  Host: <lightrag-host>:9621

RESPONSE:
  HTTP/1.1 200 OK
  Content-Type: application/json

  {
    "status": "healthy",
    "core_version": "<version>",
    "webui_title": "<title>",
    "auth_mode": "disabled",
    "configuration": { "llm_binding": "<provider>", "llm_model": "<model>" },
    "embedding_model": "<model>",
    "working_directory": "/home/<operator>/<project>/..."
  }
```

**Demonstrated:** platform identification + unauth confirmation (`auth_mode:"disabled"`) + provider/model binding + operator-naming paths, with no exfiltration. On auth-enabled instances the `auth_mode` reads otherwise but the `configuration` and `working_directory` fields still leak (that is F5: the disclosure is independent of auth state). It does NOT read documents, run a query, or touch the graph.

### PoC 2: Qdrant collection inventory (F1)

**Scenario:** an unauthenticated reader inventories the vector store and reads point counts.

```
REQUEST:
  GET /collections HTTP/1.1
  Host: <qdrant-host>:6333

RESPONSE:
  HTTP/1.1 200 OK
  { "result": { "collections": [ { "name": "nextcloud-docs" }, ... ] } }

REQUEST:
  GET /collections/nextcloud-docs HTTP/1.1

RESPONSE:
  HTTP/1.1 200 OK
  { "result": { "points_count": 531, ... } }
```

**Demonstrated:** the corpus exists, is named, and holds 531 document embeddings, all unauth. It does NOT retrieve a single vector, run a similarity search, or read document content. The name and count ARE the finding.

### PoC 3: aimap DefaultPorts-fronting bug, caught by live demo (tool-build)

**Scenario:** the new LightRAG fingerprint matched only on its DefaultPorts list, not on the port actually observed open.

```
aimap v1.9.54  target 52.69.81.89
  :80 -> 200, Server: uvicorn, body title "LightRAG Server API - Swagger UI"
  services: null
  findings: 0          <- WRONG: the LightRAG title is right there on :80

# Fix (v1.9.55): fire the fingerprint on the observed-open port regardless of
# whether it is in DefaultPorts. Re-demo identifies LightRAG on :80.
```

**Demonstrated:** unit logic passed; the live demo failed. A fingerprint pinned to a default port silently misses every instance running on a non-default port (here :80 instead of :9621). The bug was load-bearing for the survey count and was visible only because the fingerprint was demoed against a real host before being trusted.

---

*Prepared by NuClide Research (Nicholas Kloster + Claude Opus 4.8) · Cat-RAG-Framework-Servers · 2026-06-17 to 2026-06-18.*
