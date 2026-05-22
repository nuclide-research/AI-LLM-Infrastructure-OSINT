# Session Analysis: 6-Survey Evening Batch

**Date:** 2026-05-16
**Session:** 16
**Classification:** Internal / Research Use Only
**Toolchain:** JAXEN · aimap v1.9.6→v1.9.7 · VisorLog · BARE · fast_enum_*.py (bespoke)
**Repos updated:** Nicholas-Kloster/aimap (`27c91c0`) · Nicholas-Kloster/AI-LLM-Infrastructure-OSINT (`bc64efd`)

---

## 1. Overview

### Objective

Continue the day's survey batch from Session 15 (afternoon). Six additional categories in sequence. The primary thesis question: do ClickHouse and Elasticsearch, both widely deployed as AI-stack observability backends, reflect the same Docker-image-template-version dominance pattern seen in Solr earlier? Secondary: do the null-result categories (ROS robotics, agent-framework stragglers, experiment tracking) confirm Tier-C / Shodan-dark status?

Six categories covered:
- Cat 28 robotics leg — ROS (Robot Operating System)
- Cat 14 — GPU-compute / Run:ai / DCGM-exporter
- Cat 02 specialty data layers — ClickHouse
- Cat 06 agent-framework stragglers — CrewAI / LangGraph / SuperAGI / Goose / Letta
- Cat 25 — Elasticsearch with AI-stack focus
- Cat 04 registry half — experiment tracking (Aim / ClearML / W&B / Comet)

### Scope and Constraints

- **Target domains/IPs:** Global public IP space; Shodan as the discovery layer; platform-specific ports (9200 ES, 8123 ClickHouse, various GPU exporter ports).
- **Allowed techniques:** Passive Shodan harvest, HTTP GET to documented API endpoints, banner grab, bespoke Python probing scripts.
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

Continuation of the afternoon session; treated as a separate session for analysis purposes. Orchestrator + bespoke Python scripts. aimap v1.9.7 shipped during this session, adding ComfyUI-Manager probe fix and 11 fingerprints for agent-memory, data-labeling, and vector-DB straggler classes (closing gaps from session 15). No aimap version for ClickHouse/Elasticsearch/DCGM-exporter fingerprints this session; those are queued for v1.9.8 in the next session.

### Tools Used

| Tool | Role | Config notes |
|---|---|---|
| JAXEN | Stage-0 discovery: Shodan harvest → empire.db | product-facet dorks for each platform class |
| aimap v1.9.6→v1.9.7 | Stage-1 fingerprint + Stage-2 verify | v1.9.7 shipped mid-session; 11 new fingerprints, Manager-probe fix |
| fast_enum_clickhouse.py | ClickHouse mass-probe | threads=250, ~35 min; SHOW DATABASES via HTTP GET |
| fast_enum_es.py | Elasticsearch mass-probe | threads=120, ~12 min; /_cat/indices endpoint |
| VisorLog | Ledger ingest → nuclide.db | +6,869 high-severity events; cumulative 12,284 |
| VisorAgent | Active LLM exploitation | Ethical-stop. Not run. |
| VisorHollow | Windows process-injection benchmark | Not applicable — Windows-only binary |

*Null results: VisorScuba, BARE, and VisorGraph deferred this session. BARE queued for Elasticsearch 2.9.0 fleet (95 ancient hosts, CVE-2014-3120 class). VisorAgent and VisorHollow are permanent non-run categories on operator hosts.*

### Notable Configuration

- SHODAN_API_KEY active.
- Elasticsearch: 9,263 candidates via `port:9200 elastic` Shodan filter.
- ClickHouse: 65,100 candidates harvested (product facet; harvest capped at ~65K).
- ROS: 28 candidates total (Shodan-dark platform; low-footprint OS topic publishers don't appear in banner harvest).
- Agent-framework stragglers: 302 candidates from combined dorks.
- Mullvad VPN state: not recorded; assumed active per standard operating posture.

---

## 3. Methodology

### Enumeration approach

Stage-0: JAXEN harvest per platform. ClickHouse used `product:"ClickHouse"` facet (65K candidates). Elasticsearch used `port:9200 elastic` (9,263 candidates). ROS searched for ROS master API markers on default ports (11311, 9090). Agent-framework stragglers used keyword dorks per framework. DCGM-exporter used port + metric-name body search. Experiment-tracking platforms searched by product or title marker.

Stage-1: Bespoke fast_enum scripts at high thread counts. ClickHouse probed via HTTP GET query interface (`?query=SHOW+DATABASES+FORMAT+JSON`). Elasticsearch probed via `/_cat/indices` then `/_cat/health`. DCGM-exporter probed via `/metrics` endpoint.

### Candidate identification

- **ClickHouse:** `GET /?query=SHOW+DATABASES` returning database list; confirmed by `X-ClickHouse-Server-Display-Name` response header or `version()` function result.
- **Elasticsearch:** `GET /` returning JSON with `version` object + `cluster_name` + `cluster_uuid` + `lucene_version`.
- **DCGM-exporter:** `GET /metrics` returning Prometheus text format with `DCGM_FI_DEV_*` metric family.
- **Aim:** `GET /api/apps` returning JSON array of runs; confirmed by `Aim` in response headers or meta.
- **ROS:** Master API XML-RPC on port 11311; no confirmed real instances via Shodan harvest.

Insight #16 applied throughout: status codes not treated as auth-state signals.

### Validation checks

- **Insight #6 (conjunctive markers):** Multi-conjunct confirmation required on all positive findings.
- **Insight #27 (Docker image-template dominance, codified this session):** ClickHouse 22.3.20.29 at 55% (1,013/1,832) and Elasticsearch 7.x family dominance triggered this insight during version-aggregation analysis.
- **Insight #21 (port-first discovery for low-footprint platforms):** ROS 0/28 confirms Shodan-dark; masscan tier-2 on port 11311 recommended but not run this session.

### Safeguards

No brute forcing. No privilege escalation. No data exfiltration. ClickHouse probed with `SHOW DATABASES` and `SHOW TABLES` only — no `SELECT *` row reads. Elasticsearch probed with `/_cat/indices` and `/_cat/health` — no document reads. DCGM-exporter read Prometheus metric labels (GPU hostnames, UUIDs) — no payload writes. No credentials used.

---

## 4. Execution Trace

| Time | Action | Outcome / Decision |
|---|---|---|
| ~18:00 | ROS robotics harvest | 28 candidates. All dead or unrelated. Shodan-dark confirmed |
| ~18:15 | DCGM-exporter harvest + probe | 439 candidates; 9 confirmed DCGM-exporter unauth. GPU fleet layout disclosed |
| ~18:30 | ClickHouse harvest (65,100 candidates) | Product-facet harvest capped. fast_enum_clickhouse.py launched at threads=250 |
| ~19:05 | ClickHouse probe completes | 1,832 unauth; SHOW DATABASES results analyzed. SigNoz 21-operator trinity found. AI-stack DBs identified |
| ~19:20 | Agent-framework stragglers harvest | 302 candidates; all dead/unrelated. CrewAI / LangGraph / SuperAGI / Goose: Shodan-dark |
| ~19:30 | Elasticsearch harvest (9,263 candidates) | fast_enum_es.py at threads=120 launched |
| ~19:42 | Elasticsearch probe completes | 5,037 confirmed unauth (54% real-rate). 12 AI-stack index markers found |
| ~20:00 | Version aggregation on ES + CH populations | Single-version dominance pattern confirmed on both. Insight #27 drafted |
| ~20:15 | Experiment-tracking stragglers | 1,096 candidates; 2 Aim (demo mode) confirmed. ClearML / W&B / Comet: Tier-C holds |
| ~20:30 | VisorLog ingest | +6,869 high-severity events into nuclide.db |
| ~20:45 | aimap v1.9.7 shipped | ComfyUI-Manager probe + 11 fingerprints. 27c91c0 pushed |
| ~21:00 | Insight #27 codified | Docker-image-template version dominance — Solr / ClickHouse / Elasticsearch same-day cases |
| ~21:15 | SESSION.md updated; bc64efd commit | Session 16 entry written and pushed |

---

## 5. Findings

> **Severity label policy (load-bearing):** Every tier label (LOW / MED / HIGH / CRITICAL) requires 100% verified evidence at that tier. Unverified observations are UNRATED. Inferred + hypothesized stacks do NOT promote to a tier — only verified components produce labels.

### [16.1] Elasticsearch — 5,037 unauth instances, 12 confirmed AI-stack indices

| Field | Value |
|---|---|
| **Name/ID** | Elasticsearch population globally; 5,037 confirmed unauth on port 9200 |
| **Type** | Full-text + vector search engine; AI-stack RAG document store |
| **Evidence** | `GET /` returns version + cluster_name without auth on 5,037 hosts; `/_cat/indices` lists all indices |
| **Observed exposure** | Unauthenticated access to full index catalog; 12 hosts with explicit AI-stack naming (langchain, llama-index, vector, embedding, rag, openai-index) |
| **Severity** | HIGH (verified unauth at population scale; AI-stack overlap confirmed at lower bound) |

**Potential impact:** 5,037 operators have full Elasticsearch contents accessible without authentication. The 12 AI-stack-named indices are the confirmed lower bound; actual AI-stack overlap estimated at 100-1000x by generic naming analysis. Notably: `newsblur-local/discover-stories-openai-index`, `chipmong-kb-cluster/kb_documents_v1`, `106.75.127.240/entity_vectors + event_vectors` (multi-tenant hospital AI). At the time of this session, 95 hosts on version 2.9.0 have published unauth-RCE pedigree (CVE-2014-3120 Groovy scripting); BARE ranking confirmed for following session.

---

### [16.2] ClickHouse — 1,832 unauth instances, 6 AI-stack operators named

| Field | Value |
|---|---|
| **Name/ID** | ClickHouse population globally; 1,832 confirmed unauth on port 8123 |
| **Type** | OLAP database; primary backend for AI/LLM observability stacks (SigNoz, PostHog, Helicone) |
| **Evidence** | `GET /?query=SHOW+DATABASES` returns DB list without auth on 1,832 hosts; version from `SELECT version()` |
| **Observed exposure** | Unauthenticated SHOW DATABASES; DB names disclose operator stack and business model |
| **Severity** | HIGH (verified unauth + operator-attribution via DB names on 6 named operators) |

**Potential impact:** DB names expose: `vllm_service` (vLLM observability operator), `ai_hedge_fund` (trading operator, business model disclosed), `scentedai_fragid_new` (scented AI fragrance-ID startup), `qinghai_platform` (Chinese provincial government workload). 21 SigNoz operators at 1,832 hosts represent AI-stack LLM trace stores (SigNoz has first-class genai OTLP support). Any actor can query rows — content not read per restraint ethic but access is unrestricted.

---

### [16.3] DCGM-exporter — 9 unauth GPU fleet metrics endpoints

| Field | Value |
|---|---|
| **Name/ID** | DCGM (Data Center GPU Manager) Prometheus exporters; 9 confirmed unauth |
| **Type** | GPU monitoring metrics endpoint |
| **Evidence** | `GET /metrics` returns Prometheus text with DCGM_FI_DEV_* gauge families including CUDA_VISIBLE_DEVICES and hostname labels |
| **Observed exposure** | Unauthenticated Prometheus metrics; GPU model, UUID, host layout, and multi-continent fleet topology disclosed |
| **Severity** | LOW (information disclosure; GPU layout and hostname-level topology exposed; no data or credentials) |

**Potential impact:** Operator hostnames disclose GPU fleet topology. `vs3.com` multi-continent video-AI operator confirmed on Miami and Prague nodes running NVIDIA A16. H100 80GB HBM3, H200, and L40S confirmed on separate operators. Fleet layout is competitive intelligence and attack-surface mapping. Auth-by-network (not by app) is the intended gate on these exporters; public internet exposure is the misconfiguration.

---

### [16.4] Tier-C and Shodan-dark confirmations — 4 categories

| Field | Value |
|---|---|
| **Name/ID** | ROS robotics (28 candidates), agent-framework stragglers (302), experiment tracking ex-Aim (1,094) |
| **Type** | Various: robotics OS, LLM agent orchestrators, ML experiment trackers |
| **Evidence** | 0 confirmed real unauth instances across all three categories at the surveyed population sizes |
| **Observed exposure** | None — either Shodan-dark (ROS) or Tier-C auth-on-default (ClearML / W&B / Comet) |
| **Severity** | OBSERVED (thesis-confirming null result per Insight #25) |

**Potential impact:** None at this time. ROS on physical robotics infrastructure warrants a separate masscan tier-2 run on port 11311 given the physical-impact potential of unauthenticated ROS master API access. Deferred.

---

### [16.5] Elasticsearch 2.9.x — 95 ancient hosts, unauth-RCE pedigree

| Field | Value |
|---|---|
| **Name/ID** | Elasticsearch 2.9.0 cohort within the 5,037-host unauth population |
| **Type** | Ancient-version Elasticsearch (pre-X-Pack era) |
| **Evidence** | Version confirmed as 2.9.0 via `GET /` JSON response; 95 hosts in this cohort |
| **Observed exposure** | Unauthenticated access confirmed; version confirmed in unauth-RCE class |
| **Severity** | UNRATED (version confirmed; BARE match not yet run; exploitation not attempted; severity deferred to Session 17) |

**Potential impact:** CVE-2014-3120 (Groovy scripting RCE) applies at this version. BARE queued for session 17.

---

## 6. Risk Assessment

### Overall Posture

6,878 net-new unauth hosts from the evening batch. Combined with the afternoon's 1,447, the day total is 8,325. The two largest surveys (ES: 5,037; ClickHouse: 1,832) represent data stores that are AI-stack adjacency-confirmed via index and database naming. The day's finding is systemic: AI observability stacks inherit the auth posture of their data backends, and both Elasticsearch and ClickHouse ship auth-off by default in their official Docker images.

### Confidentiality

Elasticsearch: full index catalog readable by anyone; document content not tested but unrestricted. ClickHouse: full database and table listing readable; row data not tested but unrestricted. DCGM: GPU fleet topology and hostname layout readable. The 12 named AI-stack ES indices and 6 named AI-stack CH databases represent confirmed confidentiality failures at specific operators.

### Integrity

Elasticsearch: write-tier access not tested; however, unauthenticated ES (pre-7.x) allows index creation, document upsert, and index deletion by default. ClickHouse: INSERT statements not tested; unauth ClickHouse may allow writes depending on version and `users.xml` config.

### Availability

Elasticsearch 2.9.0 × 95 hosts: RCE-class CVE enables denial of service. ClickHouse: database deletion possible via `DROP DATABASE` on some versions without write-tier auth (not tested per restraint ethic).

### Systemic Patterns

- **Docker-image-template dominance (Insight #27):** ClickHouse 22.3.20.29 at 55% (1,013/1,832), Elasticsearch 7.x family dominant, Solr 7.6.0 at 84% from the morning. Three independent surveys on the same day confirm the pattern. The mechanism: operators deploy from Docker Hub LTS tags and never re-pull. The image's auth posture becomes the population's auth posture at the image's shipped version.
- **AI-stack observability co-location:** SigNoz (21 operators) and PostHog (8 operators) use ClickHouse as their trace and analytics backend. LLM call traces flow through SigNoz; unauth ClickHouse means unauth LLM observability data.

---

## 7. Recommendations

### R1 — Elasticsearch: Enable X-Pack security (7.x+) or network-restrict (all versions)

```bash
# elasticsearch.yml for 7.x+:
xpack.security.enabled: true
xpack.security.transport.ssl.enabled: true
# Or immediately: bind to loopback only
network.host: 127.0.0.1
# For 2.9.0: upgrade. No patch exists for Groovy RCE on 2.x.
```

Upstream fix: Elasticsearch's official Docker image should ship with `xpack.security.enabled=true` as the default for all 8.x images. This is partially addressed in 8.x but not retroactively enforced.

### R2 — ClickHouse: Set user password in users.xml or use ClickHouse Cloud auth

```xml
<!-- users.xml: Remove the empty password default -->
<users>
  <default>
    <password_sha256_hex>XXXXXXXX</password_sha256_hex>
    <networks>
      <ip>::1</ip>
      <ip>127.0.0.1</ip>
    </networks>
  </default>
</users>
```

The `clickhouse/clickhouse-server:22.3` LTS Docker image ships with `default` user having no password. The fix is a one-line `users.xml` change before deployment.

### R3 — DCGM-exporter: Add authentication proxy or network-restrict

```bash
# Bind DCGM-exporter to loopback; expose via authenticated metrics push to Prometheus
dcgm-exporter --address 127.0.0.1:9400
# Or add basic auth via nginx proxy_pass to port 9400
```

### R4 — Aggregate disclosure: upstream image maintainers

The highest leverage remediation for the 55% ClickHouse and 84% Solr dominance patterns is upstream: a single coordinated disclosure to Docker Hub maintainers of `clickhouse:22.3` and `solr:7.6.0` image tags remediates hundreds of operators per re-pull cycle.

### Future automation

```bash
# Detect CH / ES with no auth as part of post-deploy scan:
aimap -list ips.txt -ports 9200,8123 -o findings.json
# CH auth check:
curl -s "http://<host>:8123/?query=SHOW+DATABASES" | jq .
# ES auth check:
curl -s "http://<host>:9200/_cat/indices" | head -5
```

---

## 8. Limitations and Assumptions

| # | Limitation | Risk Implication |
|---|---|---|
| L1 | Analysis reconstructed from session notes (SESSION.md). Execution trace timestamps are approximate. | Exact probe timing not recoverable |
| L2 | Elasticsearch document content not read; AI-stack overlap bounded only by index naming | True AI-stack overlap in the 5,025 generically-named indices is unknown |
| L3 | ClickHouse row reads not performed; data classification relies on DB/table name semantics | `ai_hedge_fund` and `vllm_service` are operator-attributed via name but data contents not verified |
| L4 | ROS: 28 Shodan candidates; Shodan-dark means the real population is uncounted | Physical-impact risk of unauthenticated ROS master API is unquantified |
| L5 | aimap v1.9.7 does not yet have ClickHouse / Elasticsearch / DCGM-exporter fingerprints | Re-run of these surveys pending aimap v1.9.8 (next session) |
| L6 | BARE on ES 2.9.0 not run this session; CVE-2014-3120 match is analytical, not tool-confirmed | Deferred to Session 17 |
| L7 | 12 AI-stack index names is a hard lower bound; generic-name AI indices not identifiable without document sampling | The estimate of "100-1000x larger" is analytical inference, not measurement |

---

## 9. Proof of Concept (PoC) Illustrations

### PoC 1: Elasticsearch AI-stack index discovery

**Scenario:** Anonymous actor discovers a RAG knowledge base running on a publicly reachable Elasticsearch cluster.

```
REQUEST:
  GET /_cat/indices?v&h=index,docs.count,store.size HTTP/1.1
  Host: 135.125.201.31:9200

RESPONSE:
  HTTP/1.1 200 OK
  Content-Type: text/plain; charset=UTF-8

  index                          docs.count   store.size
  .geoip_databases                       41         73mb
  discover-stories-openai-index       8823         91mb
  .kibana_1                               1          5kb
```

**Demonstrated:** The actor confirms the cluster name (`newsblur-local`), identifies the RAG index (`discover-stories-openai-index`), and confirms document count and storage size without authentication. Does NOT read document content.

---

### PoC 2: ClickHouse DB listing — business model disclosure

**Scenario:** Anonymous actor enumerates databases on an unauth ClickHouse host and infers the operator's business.

```
REQUEST:
  GET /?query=SHOW+DATABASES+FORMAT+JSON HTTP/1.1
  Host: 178.156.183.199:8123

RESPONSE:
  HTTP/1.1 200 OK
  X-ClickHouse-Server-Display-Name: <hostname>

  {"data":[
    {"name":"INFORMATION_SCHEMA"},
    {"name":"ai_hedge_fund"},
    {"name":"default"},
    {"name":"system"}
  ]}
```

**Demonstrated:** The database name `ai_hedge_fund` discloses the operator's business model (AI-driven trading). The actor can proceed to `SHOW TABLES FROM ai_hedge_fund` to enumerate the full schema. Does NOT read rows.

---

### PoC 3: DCGM-exporter GPU fleet topology

**Scenario:** Anonymous actor maps a video-AI operator's multi-continent GPU fleet via an unauth Prometheus endpoint.

```
REQUEST:
  GET /metrics HTTP/1.1
  Host: <vs3.com-node>:9400

RESPONSE:
  HTTP/1.1 200 OK
  Content-Type: text/plain; version=0.0.4

  # HELP DCGM_FI_DEV_GPU_UTIL GPU utilization (in %)
  DCGM_FI_DEV_GPU_UTIL{gpu="0",UUID="GPU-<uuid>",device="nvidia0",
    modelName="NVIDIA A16",Hostname="miami-gpu-01.vs3.com"} 73
  DCGM_FI_DEV_GPU_UTIL{gpu="1",UUID="GPU-<uuid>",device="nvidia1",
    modelName="NVIDIA A16",Hostname="miami-gpu-02.vs3.com"} 61
```

**Demonstrated:** GPU model (A16), utilization, hostname geography (miami), and fleet node count disclosed without authentication. Does NOT read any user workload content.

---

*Prepared by NuClide Research (Nicholas Kloster + Claude Sonnet 4.6) · Session 16 · 2026-05-16*
