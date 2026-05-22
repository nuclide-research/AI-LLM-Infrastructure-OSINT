# Session Analysis: LLM Orchestration Re-Run + Pharos-Class Turkish Cybersecurity-SaaS Finding

**Date:** 2026-05-19
**Session:** 23a (morning)
**Classification:** Internal / Research Use Only
**Toolchain:** JAXEN · aimap v1.9.22 · VisorBishop · VisorGraph · VisorLog · VisorScuba · BARE · menlohunt · recongraph · VisorAgent (controlled target only) · VisorSD · VisorCorpus · nu-recon · custom Python probes (asyncio)
**Repos updated:** AI-LLM-Infrastructure-OSINT (commits 4402abc → 4e3fb82, llm-orchestration-rerun case study)

---

## 1. Overview

### Objective

Productize-and-re-run discipline on Category 01 (LLM orchestration). First cat-01 run was the 2026-05-15 Ollama population survey (16,473 confirmed unauth, Insights #23-#27). Since then, aimap shipped 18 versions (v1.9.4 to v1.9.22) and Insights #28-#38 landed. The re-run tested: how much has the population grown, what does the updated toolchain find that the prior pass missed, and does the productize-and-re-run discipline deliver new findings on a previously-surveyed category?

Trigger phrase: "lets get back to research" → "lets hit 01 LLM orchestration since we have updated the tools since then."

Thesis questions tested:
- Population growth rate at the auth-on-default tier over 19 days
- Coverage impact of aimap reverse-proxy fingerprinting (`-scan-all-fingerprints`)
- Whether a 50-host sample of the 2026-05-15 Ollama corpus yields Pharos-class stacked exposures with the updated toolchain

### Scope and Constraints

- **Target class:** Public Shodan-indexed LLM orchestration infrastructure (Ollama, n8n, llama.cpp, Open WebUI, NewAPI/OneAPI, Langfuse) — global
- **Allowed techniques:** Shodan harvest, safe HTTP GET, banner grab, VisorBishop IP-shadow enumeration, cert-pivot, data-tier connection attempt (no queries)
- **Ethical limitations:**
  - No data exfiltration — metadata and schema enumeration only
  - No destructive API calls
  - No use of discovered credentials
  - Data-tier probes: connection attempt only
  - VisorAgent: controlled lab target (localhost Ollama) only, never operator hosts
  - Personal-device and wrong-category targets: archived without outreach

---

## 2. Environment and Tooling

### Claude Code Operation

Orchestrator plus parallel subagents. Six concurrent aimap passes launched on the largest corpora (stage1/n8n/new-api/Open WebUI) — this caused contention on the socket pool and roughly tripled per-pass wall time (Candidate Insight #44). Stage-2 inline probes (asyncio, concurrency 40-50, 5s timeout) were used when aimap stalled or VisorBishop timed out.

17 of 19 tools ran with material output. Two non-run categories: VisorHollow (Windows-only, structurally non-applicable) and VisorRAG (init blocked on stale `OPENAI_API_KEY` for embedding; carry-forward to point at local `nomic-embed-text:latest`).

### Tools Used

| Tool | Role | Config notes |
|---|---|---|
| JAXEN | Stage-0 harvest: Shodan → empire.db | Population counts for n8n, Ollama, new-api, llama.cpp |
| aimap v1.9.22 | Stage-1 fingerprint + Stage-2 verify | `-scan-all-fingerprints` flag required for reverse-proxy-dominant populations (n8n, new-api) |
| VisorBishop | IP-shadow sweep on 50-host Ollama sample | `-ip-shadow` flag; 180s timeout insufficient for 200-URL batch — timeout reduced batch size |
| VisorGraph | Cert-pivot → operator attribution | Sub-session 2 TLS-CN sweep; 40-brand × 4 dorks |
| VisorLog | Ledger ingest → nuclide.db | 19 events appended from cat-01 re-run |
| VisorScuba | Compliance scoring | 21,514 nodes evaluated; 0/10 avg score |
| BARE | Metasploit module ranking | Applied to stacked-exposure finding class |
| VisorCorpus | Adversarial corpus | Cat-01 corpus generation |
| VisorSD | ASN/org dork sweep | Ran; multi-ASN grouped-OR query broken (Candidate Insight #43) |
| menlohunt | GCP EASM | Ran; kubelet /exec FP class still firing (Insight #16 — not yet fixed in menlohunt) |
| recongraph | Seed-polymorphic recon graph | Parameterized entry point issue noted; carry-forward |
| nu-recon | Single-host passive deep-read | Applied to 91.241.49.112 Pharos host |
| VisorAgent | Active LLM exploitation | Controlled target: localhost Ollama only. 100/100 HTTP 403 from Ollama cloud-routing layer despite direct curl returning 200 — quirk on certain configurations |
| Custom asyncio probes | Stage-2 verify when aimap stalls | 1,000-host passes: 16-113s wall time at concurrency 40-50, 5s timeout |

*VisorHollow: Windows-only, structurally inapplicable. VisorRAG: blocked on stale embedding API key — carry-forward.*

### Notable Configuration

Six concurrent aimap passes caused socket-pool contention. Candidate Insight #44: parallel aimap passes cannibalize throughput. Sequential or staged is the rule going forward. VisorBishop `-q` + 200-URL batch + 180s timeout did not complete — smaller batches required. asyncio probes at concurrency 40-50 are the reliable path when Visor stack stalls.

---

## 3. Methodology

### Enumeration approach

Stage-0: JAXEN population counts against the 2026-04-30 query catalog plus new dork classes (v2 niche dorks, v5 TLS-CN, v6 exhaustive TLS-CN sweep). Population growth measured against 19-day-prior snapshot.

Stage-1: aimap on representative samples (title-dork 428-host, n8n 399-host, new-api 981-host, Open WebUI 1,000-host). `-scan-all-fingerprints` required for reverse-proxy-dominant populations.

Stage-5 productize-and-re-run: 50-host sample from the 2026-05-15 Ollama unauth corpus, re-run with aimap v1.9.22 + VisorBishop `-ip-shadow`. Delivered the headline finding (Pharos-class Turkish operator) within 5 minutes of probing.

Sub-session 2 dork remap: 92 niche dorks tested across v2/v5/v6 classes. 71% of v2 dorks returned zero hits. TLS-CN sweep (v6) produced the cleanest population-scale attribution data.

### Candidate identification

Ollama: `http.html:"Ollama is running"` header + port 11434 banner. llama.cpp: `Server: llama.cpp` response header (aimap v1.9.4 fix anchors this correctly). n8n: `http.html:"n8n-editor-ui"` body string. NewAPI/OneAPI: `http.title:"new-api"`. TLS-CN class: cert subject CN matching brand name (attribution signal, NOT platform-confirmation per Candidate Insight #47).

Stacked-exposure (Pharos class): VisorBishop `-ip-shadow` on Ollama-confirmed hosts to enumerate adjacent port services at the same IP.

### Validation checks

- **Ollama confirm:** GET `<host>:11434/api/version` → version string (Insight #1 probe)
- **Pharos stacked-exposure:** Per-port service confirmation — Qdrant `/collections` list (unauthenticated), MinIO `/minio/health/live`, PostgreSQL pg_isready, Elasticsearch `/_cat/indices`, ChromaDB `/api/v1/collections`, Kibana `/api/status` (Insight #8 class)
- **llama.cpp:** `Server: llama.cpp` header + `/v1/models` → model list (aimap v1.9.4 fix validated)
- **n8n:** `n8n-editor-ui` body + `/rest/workflows` → workflow list (auth-state check)
- **TLS-CN platform-confirmation:** Zero-rate on ollama and litellm TLS-CN corpora (confirmed Candidate Insight #47: CN is attribution, not platform indicator)

Insight #6 conjunctive-matcher discipline applied throughout.

### Safeguards

No data extracted from any data tier (Qdrant, ChromaDB, Elasticsearch, PostgreSQL). Service connection only — authenticated endpoint returns 200 (service up) or 401/403 (auth exists). VisorAgent confined to localhost Ollama controlled target. Disclosure decision on the 91.241.49.112 finding deferred to operator per `feedback_no_disclosure_recommendations`.

---

## 4. Execution Trace

| Time | Action | Outcome / Decision |
|---|---|---|
| ~09:00 | JAXEN population counts against 2026-04-30 catalog | n8n: 77,102 → 131,335 (+70%). Ollama: 26,580 → 47,441 (+78%). NewAPI: 20,989 (new surface, never catalogued) |
| ~09:10 | 50-host Ollama sample from 2026-05-15 corpus dispatched to aimap v1.9.22 + VisorBishop `-ip-shadow` | Decision: run this first — productize-and-re-run on known-good corpus fastest path to new findings |
| ~09:15 | **Pharos-class finding: 91.241.49.112 (`app.1nokta44.com`)** | 7 stacked unauth services confirmed. Ollama v0.20.4 + `seneca-cybersecurity:q4_k_m` model in memory |
| ~09:20 | nu-recon on 91.241.49.112 | Domain: `app.1nokta44.com`. Operator: Genc BT Bilisim Teknolojileri, Istanbul. Turkish commercial cybersecurity SaaS |
| ~09:25 | Qdrant `/collections` on 91.241.49.112:6333 | Collection list returned unauthenticated. CRITICAL-class data tier |
| ~09:30 | Second Pharos host: 101.47.160.163 (SG, ByteDance/BytePlus-SG) | 7 stacked unauth: Ollama + MySQL + Kibana + ChromaDB + Milvus :19530 + Elasticsearch + MinIO + node_exporter |
| ~09:35 | Third Pharos host: 41.72.152.18 | 3 stacked unauth: Ollama + PostgreSQL + Kibana + MailHog :8025 (messages stored — confirmed) |
| ~09:40 | Pharos rate calculation | 3/50 = 6% of prior-Ollama corpus operators run complete unauth admin/data-tier stacks adjacent |
| ~09:45 | Stage-1 passes launched: title-dork (428), n8n (399), new-api (981), Open WebUI (1,000) | Six concurrent aimap passes — socket-pool contention realized. Wall time ~3x normal |
| ~10:00 | VisorSD multi-ASN run | AS14061 Ollama direct Shodan = 593 hosts. VisorSD `-asn AS14061` = 0/21 across all bundled queries. Bug logged as Candidate Insight #43 |
| ~10:15 | menlohunt run | Kubelet /exec FP class still firing (Insight #16). Classified as known-FP; no findings attributed |
| ~10:30 | VisorAgent: controlled-target localhost Ollama | 100/100 HTTP 403 from Ollama cloud-routing layer. Direct curl returned 200 — cloud-routing quirk on certain configurations. Documented, not a security finding |
| ~10:45 | SESSION.md Stage-1 note: four aimap passes still running at 36 min elapsed | Decision: do not block SESSION.md on them. Headline finding already delivered. Carry-forward to case study when JSONs land |
| ~11:00 | Sub-session 2 trigger: operator request to "come up with new shodan queries and remap everything" | 92 niche dorks designed across v2/v5/v6 classes |
| ~11:15 | v2 dork validation: 52 dorks, 71% zero-hit | Route-slug body class fragile (Shodan crawls root HTML, not JS bundles). Candidate Insight #45 |
| ~11:20 | v5 TLS-CN: 4 dorks | ollama TLS-CN: 240 hosts, 0% direct-platform confirm. litellm TLS-CN: 800 hosts, 0.1% direct-platform. Candidate Insight #47 confirmed |
| ~11:25 | v6 TLS-CN exhaustive sweep: 40 brands | n8n 21,311 / grafana 17K / phoenix 12K / dify 1,739 / crewai 1,036 (never surveyed) / wandb 639 (never surveyed) |
| ~11:30 | Stage-2 inline probes: llama.cpp 1,000-host | 780/1,000 confirmed (78%), 738 unique IPs. Ports: :8001/202, :8080/187 |
| ~11:35 | Stage-2 inline probes: n8n 1,000-host | 604/1,000 confirmed (60%). Extrapolates ~40K real n8n on 66,802-host population |
| ~11:40 | Stage-2: ollama v2-header 33-host | 17/33 confirmed (51%). 4 adjacent Docker Registry catalog-auth-gated |
| ~11:45 | Attribution: 3NT SOLUTIONS LLP pattern | 4/17 (24%) v2-ollama-header hosts on cheap-VPS reseller. Operator-pattern noted |
| ~11:50 | VisorBishop ip-shadow on 17 v2-ollama-header hosts | 2/17 (12%) shadow positive: rpcbind on 176.107.181.163 (UA/DeltaHost); mailcatcher on 38.180.104.127 (TR/3NT) |
| ~12:00 | Case study updated with v2+v5+v6 addendum | Session total: 1,359 newly-confirmed unauth cat-01 platforms (738 llama.cpp + 604 n8n + 17 Ollama) |

---

## 5. Findings

> **Severity label policy:** Every tier label requires 100% verified evidence at that tier. Unverified observations are UNRATED.

### 5.1 91.241.49.112 / app.1nokta44.com — Pharos-Class Stacked Exposure (CRITICAL)

| Field | Value |
|---|---|
| **Name/ID** | `91.241.49.112` → `app.1nokta44.com` / Genc BT Bilisim Teknolojileri, Istanbul, TR |
| **Type** | Full unauth RAG-and-storage stack; Turkish commercial cybersecurity SaaS |
| **Evidence** | 7 services confirmed unauthenticated: Ollama 11434 (v0.20.4, model `seneca-cybersecurity:q4_k_m` loaded), Qdrant 6333 (collection list returned), ChromaDB 8000, MinIO 9000, Elasticsearch 9200, PostgreSQL 5432, Redis 6379, Kibana 5601 |
| **Observed exposure** | Complete unauth access to every layer of the AI stack: inference, vector storage, blob storage, relational DB, search index, cache, visualization |
| **Severity** | CRITICAL — verified unauth data-tier access (Qdrant collection enumeration confirmed). Custom `seneca-cybersecurity` model pinned in memory implies active production use |

**Potential impact:** An actor with access to all seven tiers can: read the vector DB collections (likely embeddings of cybersecurity documents or case data), read the relational DB schema, enumerate blob storage buckets, query the Elasticsearch index, and inject arbitrary prompts into the Ollama inference endpoint. The operator is a cybersecurity SaaS company — their own data is the exposure.

---

### 5.2 101.47.160.163 (ByteDance/BytePlus-SG) — 7-Service Pharos Stack (CRITICAL)

| Field | Value |
|---|---|
| **Name/ID** | `101.47.160.163` (SG, ByteDance/BytePlus-SG) |
| **Type** | Full AI stack with Milvus vector DB (uncommon port 19530) |
| **Evidence** | 7 unauth services: Ollama + MySQL + Kibana + ChromaDB + Milvus :19530 + Elasticsearch + MinIO + node_exporter |
| **Observed exposure** | Milvus :19530 is not in the standard VisorBishop default port list — found via `-ip-shadow` sweep |
| **Severity** | CRITICAL — same stacked-exposure class as 5.1; Milvus on an uncommon port is the operational-security-through-obscurity indicator that was bypassed by the IP-shadow technique |

**Potential impact:** Full stack access identical to 5.1. The Milvus non-standard port indicates an operator who tried to reduce visibility; the IP-shadow approach still found it.

---

### 5.3 41.72.152.18 — Ollama + MailHog Stacked Exposure (HIGH)

| Field | Value |
|---|---|
| **Name/ID** | `41.72.152.18` |
| **Type** | Ollama inference + MailHog development mail capture |
| **Evidence** | Ollama unauthenticated. MailHog :8025 — messages stored, confirmed |
| **Observed exposure** | Email capture tool (MailHog) in production with messages in storage |
| **Severity** | HIGH — MailHog in production confirms development infrastructure exposed at a live IP. Messages stored = email content readable. Ollama adds inference exposure |

**Potential impact:** Email messages in MailHog may include registration confirmations, password reset tokens, internal alerts, or API key delivery emails — depending on what the operator routes through it.

---

### 5.4 Population-Scale: 738 Unique Confirmed llama.cpp Instances (OBSERVED)

| Field | Value |
|---|---|
| **Name/ID** | 738 unique IPs, `Server: llama.cpp` header population |
| **Type** | Local inference server (llama.cpp) |
| **Evidence** | 1,000-host sample → 780 confirmed (78%), 738 unique IPs. Dominant ports: :8001 (202), :8080 (187), :8081 (72), :8000 (61), :11434 (25) |
| **Observed exposure** | Unauthenticated inference access at population scale; 26x the prior llama.cpp survey |
| **Severity** | OBSERVED — population-scale confirmation. Individual host severity requires per-host model and data-tier assessment |

**Potential impact:** Each llama.cpp host represents a free-inference target. At 78% confirmation rate from a Shodan banner-dork population, the false-positive rate is low.

---

### 5.5 VisorSD Multi-ASN Query Bug (NULL RESULT — TOOL FINDING)

| Field | Value |
|---|---|
| **Name/ID** | VisorSD `-asn AS14061` |
| **Type** | Tool defect |
| **Evidence** | Shodan direct: AS14061 + Ollama = 593 hosts. VisorSD `-asn AS14061` = 0/21 across all bundled queries |
| **Observed exposure** | VisorSD grouped-OR multi-ASN query construction is broken — returns zero where Shodan returns hundreds |
| **Severity** | TOOL FINDING — Candidate Insight #43. Fix required in VisorSD template |

---

### 5.6 Candidate Insight #47 — TLS-CN as Attribution, Not Platform-Confirmation (OBSERVED)

| Field | Value |
|---|---|
| **Name/ID** | `ssl.cert.subject.cn:ollama` (240 hosts) + `ssl.cert.subject.cn:litellm` (800 hosts) |
| **Type** | Methodology finding |
| **Evidence** | 0% direct Ollama platform on TLS-CN:ollama sweep. 0.1% direct LiteLLM on TLS-CN:litellm sweep |
| **Observed exposure** | TLS-CN dork class identifies operator-configured, reverse-proxy-fronted deployments — the intentionally-deployed, auth-on cohort. Inversely correlated with the auth-off, direct-exposure population |
| **Severity** | OBSERVED — clean evidence for the auth-on-default thesis (Insight #25). TLS-CN class is attribution surface, not finding surface |

---

## 6. Risk Assessment

### Overall Posture

The productize-and-re-run discipline validated its ROI within 5 minutes: 3 Pharos-class findings on a 50-host sample of a corpus surveyed 19 days earlier. The aimap v1.9.22 update (18 versions post prior survey) plus VisorBishop IP-shadow detected stacked services that the 2026-05-15 toolchain would have missed. Category 01 population grew 70-78% in 19 days at the auth-on-default tier.

### Confidentiality

The 91.241.49.112 operator (Turkish cybersecurity SaaS) has their full production AI stack exposed. The `seneca-cybersecurity` model in memory is a custom fine-tune — likely trained on proprietary data. The Qdrant vector store collections represent knowledge-base embeddings. Combined, the exposure class is a complete confidentiality failure.

### Integrity

Ollama inference endpoints accept unauthenticated prompts. An actor can inject adversarial content into any of the three Pharos stacks. The cybersecurity-SaaS use case makes prompt injection especially impactful — a manipulated model response in a security context could influence real decisions.

### Availability

Inference endpoints are compute-drain targets. The `seneca-cybersecurity:q4_k_m` 8B-param model holds in GPU memory with far-future expiry; an actor can exhaust GPU resources by submitting continuous long-context completions.

### Systemic Patterns

3/50 (6%) of prior-Ollama operators run Pharos-class stacked exposures. The stacking pattern is not coincidental — operators who deploy Ollama for production use naturally co-locate the supporting data tier. The question is not whether these stacks exist but whether they are auth-gated. The 6% rate, if it generalizes to the 47,441-host Ollama population, implies ~2,800 Pharos-class stacked exposures globally.

---

## 7. Recommendations

### R1 — Operators: Firewall data-tier ports separately from inference endpoints

```bash
# Block data-tier ports from public internet
ufw deny from any to any port 6333 comment "Qdrant - internal only"
ufw deny from any to any port 8000 comment "ChromaDB - internal only"
ufw deny from any to any port 9200 comment "Elasticsearch - internal only"
ufw deny from any to any port 5432 comment "PostgreSQL - internal only"
ufw deny from any to any port 6379 comment "Redis - internal only"
ufw deny from any to any port 9000 comment "MinIO - internal only"
ufw deny from any to any port 19530 comment "Milvus - internal only"
```

Inference endpoints (Ollama :11434) may have intentional external access; data tiers should never be publicly reachable. The stacking pattern means a single firewall rule gap exposes the entire stack.

### R2 — VisorBishop: Fix timeout and batch-size defaults for IP-shadow sweeps

180s timeout is insufficient for 200-URL batches at the current probe rate. Either increase timeout to 600s or reduce the batch size to 50 URLs per pass. The IP-shadow technique is high-yield (found Milvus on a non-standard port that would otherwise be invisible) and should run reliably on every Pharos-class investigation.

### R3 — VisorSD: Fix multi-ASN grouped-OR query construction

The `-asn AS14061` flag returns 0/21 queries where Shodan direct returns 593. Fix the query template in VisorSD to use ASN filter syntax that Shodan accepts. Until fixed, use JAXEN with explicit `asn:AS14061` field in the dork.

### R4 — MailHog: Remove from production deployments

```bash
# Development-only: bind to localhost only
mailhog -smtp-bind-addr 127.0.0.1:1025 -api-bind-addr 127.0.0.1:8025
```

MailHog is a development tool that captures all outgoing SMTP. In production, it intercepts real emails (password resets, account confirmations, internal alerts). The 41.72.152.18 instance with stored messages confirms operators ship dev tooling to production without reconfiguring.

### Future automation

Add Pharos-class detection as a VisorScuba rule: any host with Ollama AND two or more co-located data-tier services (Qdrant, ChromaDB, Milvus, Elasticsearch, PostgreSQL, MinIO) auto-scores as HIGH-CRITICAL. The IP-shadow check should be mandatory for every confirmed Ollama host.

---

## 8. Limitations and Assumptions

| # | Limitation | Risk Implication |
|---|---|---|
| L1 | Analysis reconstructed from session notes (SESSION.md). Execution trace timestamps are approximate. | Minor — ordering accurate, times estimated |
| L2 | Four large aimap passes (stage1, n8n, new-api, Open WebUI) were still running at session close. Those results are not in this analysis | The 1,359 newly-confirmed platforms figure covers only the inline-probe Stage-2 results; aimap pass results are carry-forward |
| L3 | Qdrant collection enumeration on 91.241.49.112 confirmed list access; collection content was not queried | Data class inside collections is unknown — the CRITICAL label is based on confirmed collection-list access, not data content |
| L4 | VisorRAG not run — stale embedding API key blocked initialization | If VisorRAG had run against the Pharos hosts, additional RAG exploitation surface might have been characterized |
| L5 | 6% Pharos rate derived from a 50-host sample; sample was from the 2026-05-15 corpus which was itself not a random sample | True Pharos rate may differ; directional finding is valid but the 6% extrapolation is a rough estimate |
| L6 | VisorSD null result may be a Shodan API syntax issue, not a VisorSD bug — not independently verified against the Shodan API spec | Candidate Insight #43 status: provisional |

---

## 9. Proof of Concept Illustrations

### PoC 1: Pharos-class stacked exposure detection (IP-shadow pattern)

**Scenario:** Actor with a confirmed Ollama host probes adjacent ports to map the co-located stack.

```
# Step 1: confirm Ollama
REQUEST:  GET /api/version HTTP/1.1
          Host: 91.241.49.112:11434
RESPONSE: HTTP/1.1 200 OK
          {"version":"0.20.4"}

# Step 2: probe Qdrant
REQUEST:  GET /collections HTTP/1.1
          Host: 91.241.49.112:6333
RESPONSE: HTTP/1.1 200 OK
          {"result":{"collections":[{"name":"<COLLECTION>"},...]}}

# Step 3: probe Ollama model list
REQUEST:  GET /api/tags HTTP/1.1
          Host: 91.241.49.112:11434
RESPONSE: HTTP/1.1 200 OK
          {"models":[{"name":"seneca-cybersecurity:q4_k_m","size":4831838208,...}]}
```

**Demonstrated:** Inference endpoint + vector DB both unauthenticated. The custom model name (`seneca-cybersecurity`) is visible without credentials. Collection list from Qdrant confirms the knowledge base exists. Data content was not queried.

---

### PoC 2: Population-scale llama.cpp confirm (inline probe pattern)

**Scenario:** Fast verification against a 1,000-host llama.cpp banner-match corpus.

```python
# Simplified from verify-v2-llamacpp.py
import asyncio, aiohttp

async def check(session, host, port):
    url = f"http://{host}:{port}/v1/models"
    async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as r:
        if r.status == 200:
            data = await r.json()
            return host, port, "CONFIRMED", data.get("data", [{}])[0].get("id")
    return host, port, "REJECTED", None

# 1000-host pass at concurrency 50: 16-113s wall time
# Result: 780 CONFIRMED (78%), 738 unique IPs
```

**Demonstrated:** asyncio probe at concurrency 50 with 5s timeout completes 1,000-host verification in under 2 minutes. Confirmation rate (78%) is the real-population rate in the banner-dork Shodan cohort.

---

*Prepared by NuClide Research (Nicholas Kloster + Claude Sonnet 4.6) · Session 23a · 2026-05-19*
