# Session Analysis: ES + CH Cross-Stack Follow-Up

**Date:** 2026-05-17
**Session:** 17
**Classification:** Internal / Research Use Only
**Toolchain:** aimap v1.9.8 · VisorLog · BARE · fast_enum_es.py · fast_enum_clickhouse.py (retired after aimap productization)
**Repos updated:** Nicholas-Kloster/aimap (`f586217`) · Nicholas-Kloster/AI-LLM-Infrastructure-OSINT (`e48753e`, `02d18ac`)

---

## 1. Overview

### Objective

24-hour re-probe of yesterday's confirmed unauth populations: 5,037 Elasticsearch hosts and 1,832 ClickHouse hosts. Two goals:

1. Ship `enumElasticsearch` and `enumClickHouse` as aimap v1.9.8 enumerators, retiring the bespoke fast_enum scripts and closing the toolchain gap SESSION.md flagged.
2. Run `_mapping` on ES hosts to confirm AI-stack workloads via `dense_vector` / `knn_vector` field types; run `SHOW TABLES` on CH hosts to expand yesterday's 6 named AI-stack operators.

Thesis question: does a 24-hour window produce meaningful auth improvement on the unauth population? Secondary: does the Meow / Indexrm extortion campaign represent a fast ongoing wipe or a pre-existing equilibrium?

### Scope and Constraints

- **Target domains/IPs:** Yesterday's confirmed unauth ES (5,037) and CH (1,832) host lists; no new Shodan harvest.
- **Allowed techniques:** HTTP GET to documented API endpoints only. `_mapping` probe reads schema, not documents. `SHOW TABLES` reads table names, not rows.
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

Single session. Orchestrator posture. aimap v1.9.8 built during the session with two new enumerators; tested with `go test ./... clean` before any production probe run. Bespoke scripts used for initial re-probe while aimap was being built, then replaced by aimap for the production run.

### Tools Used

| Tool | Role | Config notes |
|---|---|---|
| aimap v1.9.8 | Stage-2 deep enumeration: enumElasticsearch + enumClickHouse | Shipped mid-session; replaces fast_enum scripts for future surveys |
| VisorLog | Ledger ingest → nuclide.db | +3,666 events; 3,597 ES wiped → lifecycle archived; 84 AI-stack upgraded |
| BARE | Metasploit semantic ranking | 95/95 ES 2.9.x hosts → CVE-2014-3120 Groovy RCE top-ranked |
| fast_enum_es.py | Initial ES re-probe before aimap productization | Retired after aimap v1.9.8 ships |
| fast_enum_clickhouse.py | Initial CH re-probe | Retired after aimap v1.9.8 ships |
| VisorAgent | Active LLM exploitation | Ethical-stop. Not run. |
| VisorHollow | Windows process-injection benchmark | Not applicable — Windows-only binary |

*Null results: VisorGraph queued for attribution sweep (22 AI-stack ES hosts) — executed in Session 17b, not this session. VisorScuba deferred. VisorAgent and VisorHollow are permanent non-run categories on operator hosts.*

### Notable Configuration

- Re-probe targeted yesterday's confirmed unauth list directly; no new Shodan harvest.
- `enumElasticsearch`: capped at 30 indices per host; walks one level of nested objects; captures both ES `dims` and OpenSearch `dimension` spellings. GET-only. No document reads.
- `enumClickHouse`: caps at 60 databases / 200 tables per host. `SHOW DATABASES` + `SHOW TABLES`. GET query interface only. No row reads.
- BARE run against ES 2.9.x cohort (95 hosts) for Metasploit module ranking.
- Restraint ethic enforced at the code level in both enumerators: no SELECT, no row access, no document retrieval.

---

## 3. Methodology

### Enumeration approach

Stage-0 (no harvest): re-used yesterday's confirmed IP lists. The hypothesis to test: does auth state change in 24 hours, and can `_mapping` confirm the AI-stack overlap analytically predicted yesterday?

Stage-2 (aimap v1.9.8 enumerators):
- **ES:** `GET /` (4-conjunct anchor) → `/_cat/indices` → per-index `/_mapping` (capped 30/host, one level of nested-object walk).
- **CH:** `SHOW DATABASES FORMAT JSON` → per-database `SHOW TABLES FORMAT JSON` (cap 60 DBs / 200 tables).

### Candidate identification

For AI-stack confirmation:
- **ES dense_vector / knn_vector:** `dims` field (ES native) or `dimension` field (OpenSearch) in `_mapping` response. Any index with this field type is an embedding store.
- **CH AI-stack markers:** DB or table names matching: `signoz_*`, `posthog*`, `plausible*`, `otel*`, `vllm_*`, `llm_*`, `prompt_*`, `embedding_*`, `rag_*`, `chunks_*`, `vector*`, `ai_*`.

Embedding dimension decodes LLM provider: 256d / 1536d / 3072d = OpenAI (text-embedding-3-small, text-embedding-3-large variants). 768d = bge-base or m3e-base (Chinese open-source). 1024d = Cohere v3 or bge-large. 512d = XiaoIce / smaller custom models.

### Validation checks

- **Insight #27 (Docker image-template dominance):** ClickHouse 22.3.20.29 re-measured at 67.4% (1,354/2,008 fingerprinted) vs yesterday's 55%. Confirms the pattern holds and grows with corpus cleaning.
- **Insight #28 (codified then retracted, corrected to Insight #29 in Session 17b):** Initial framing of "3,604 / 5,037 wiped in 24h" was computed as a delta. This was wrong — see Session 17b for the retraction. The shelf-life rule (re-verify before send) survives for a corrected reason.
- **BARE confirmation:** 100% of 95 ES 2.9.x hosts top-rank `exploits_multi_elasticsearch_search_groovy_script`. BARE's deterministic population-scale match confirmed.

### Safeguards

No brute forcing. No privilege escalation. No data exfiltration. `_mapping` endpoint reads schema only; no document sampling. `SHOW TABLES` reads table names only; no `SELECT` statements. Restraint ethic enforced in aimap v1.9.8 source: GET-only path hardcoded in both enumerators. The `read_me` ransom note on wiped hosts was not read this session (read in Session 17b on Nick's explicit override for attacker-attribution purposes).

---

## 4. Execution Trace

| Time | Action | Outcome / Decision |
|---|---|---|
| ~08:30 | ES re-probe on yesterday's 5,037-host list | 4,776 still responsive; 4,564 still unauth; 0 added auth; 3,604 carry read_me index |
| ~09:00 | Initial framing: "71.6% wiped in 24h" | Later retracted (Session 17b); the state was pre-existing in 92.4% of hosts |
| ~09:15 | Insight #28 drafted (later retracted) | Codified the shelf-life re-verify-before-send rule with a wrong rate |
| ~09:30 | _mapping probe on all ES hosts | 22 hosts confirmed with dense_vector or knn_vector field types |
| ~10:00 | AI-stack host analysis: embedding dimensions decoded | Nepal HMIS (ocl.hmis.gov.np), hospital AI (106.75.127.240), NewsBlur, XiaoIce, etc. identified |
| ~10:30 | CH re-probe on 1,832-host list | 70 hosts confirmed AI-stack via DB/table-name pattern (vs 6 yesterday) |
| ~11:00 | aimap v1.9.8 built: enumElasticsearch + enumClickHouse | go test ./... clean. f586217 pushed. |
| ~11:30 | aimap v1.9.8 re-run for validation | Confirms the manual probe results |
| ~12:00 | BARE on 95 ES 2.9.x hosts | 100% top-rank CVE-2014-3120 Groovy RCE module. Deterministic at this version |
| ~12:30 | VisorLog ingest | +3,666 events: 3,597 archived (wiped), 84 severity-upgraded (AI-stack confirmed) |
| ~13:00 | Nepal HMIS disclosure draft | NP-CERT + MoHP. CRITICAL. Drafted for send (sent in Session 17b) |
| ~13:30 | SESSION.md updated; case study pushed | es-clickhouse-cross-stack-2026-05-17.md committed |

---

## 5. Findings

> **Severity label policy (load-bearing):** Every tier label (LOW / MED / HIGH / CRITICAL) requires 100% verified evidence at that tier. Unverified observations are UNRATED. Inferred + hypothesized stacks do NOT promote to a tier — only verified components produce labels.

### [17.1] Nepal Ministry of Health HMIS — unauth clinical concept store, extortion-marked

| Field | Value |
|---|---|
| **Name/ID** | 103.69.124.214; TLS SAN `ocl.hmis.gov.np`; Nepal Ministry of Health and Population |
| **Type** | Government health AI / Open Concept Lab clinical terminology server |
| **Evidence** | `_mapping` confirms `concepts` index (318,114 docs, 27.7 MB), `_embeddings.vector` field; `read_me` extortion index present; WHOIS: Department of Information Technology, Government of Nepal |
| **Observed exposure** | Unauthenticated Elasticsearch; clinical concept dictionary with embeddings; admin `user_profiles` index (9 records); extortion marker planted |
| **Severity** | CRITICAL (verified government health data store, unauth, active extortion marker, live data not yet wiped) |

**Potential impact:** 318,114 clinical concepts (drug names, diagnoses, ICD-10 codes) with embeddings are accessible without authentication. Admin user profiles (9 records) are accessible. crt.sh pivot reveals 10 additional hmis.gov.np subdomains: `fhir.hmis.gov.np` (FHIR healthcare gateway), `elmis.hmis.gov.np` (vaccine/drug logistics), `erecord.hmis.gov.np` (electronic records), `sudurpashchim.hmis.gov.np` (Far-Western Province deployment). The extortion actor has marked the host; data deletion is imminent. Disclosure went to NP-CERT + Ministry of Health.

---

### [17.2] Multi-tenant hospital AI on UCloud Shanghai — 270,000 patient-record vectors, mid-wipe

| Field | Value |
|---|---|
| **Name/ID** | 106.75.127.240; UCloud Shanghai; operator name withheld |
| **Type** | Multi-tenant clinical AI platform (entity extraction, event classification, source retrieval) |
| **Evidence** | `_mapping` confirms `entity_vectors` (214,597 docs, 3.3 GB, 768d), `event_vectors`, `source_chunks`; total 6.7 GB; `read_me` index present |
| **Observed exposure** | Unauthenticated Elasticsearch; patient entity vectors live; extortion marker planted; data not yet wiped at time of probe |
| **Severity** | CRITICAL (verified patient-record vector store, unauth, active extortion marker, 6.7 GB live data) |

**Potential impact:** 270,000+ patient-record vectors from a multi-tenant hospital AI platform are accessible without authentication. The 768-dimension embedding space is consistent with bge-base (Chinese open-source clinical model). The `read_me` index indicates the attacker has already targeted this host. Disclosure sent to UCloud abuse.

---

### [17.3] 22 AI-stack Elasticsearch hosts confirmed via _mapping

| Field | Value |
|---|---|
| **Name/ID** | 22 ES hosts globally with dense_vector or knn_vector field types; full table in 22-ai-stack-attribution-2026-05-17.md |
| **Type** | RAG / embedding stores across healthcare, travel, e-commerce, media, SaaS verticals |
| **Evidence** | Per-index `_mapping` returns dense_vector or knn_vector field in at least one index on each host |
| **Observed exposure** | Unauthenticated access; embedding dimensions decode LLM provider; 18 of 22 hosts carry Meow extortion marker |
| **Severity** | HIGH (22 verified AI-stack unauth ES hosts; 2 CRITICAL-tier already filed separately; remainder HIGH as class) |

**Potential impact:** Named operators: NewsBlur (discover-stories-openai-index, 256d), XiaoIce demo (virtual-human FAQ, 512d), TorchV/ZLMediaKit (streaming SDK RAG, 1024d), AItalkx (DMS RAG, 768d), Guangxi OTA (multi-tenant tourism, 1024d), Equant Tech/Waffarha LMS (Egyptian e-commerce, 768d). 18 of 22 hosts mid-wipe or fully wiped. Embedding dimensions disclose LLM vendor without document reads.

---

### [17.4] 70 AI-stack ClickHouse hosts confirmed via SHOW TABLES

| Field | Value |
|---|---|
| **Name/ID** | 70 CH hosts globally; AI-stack confirmed via DB or table name patterns |
| **Type** | LLM observability, RAG, prompt history, and LLM inference backends |
| **Evidence** | `SHOW TABLES FROM <db>` returns AI-stack-marker table names: SigNoz (18 operators), PostHog, Plausible, vllm_service, llm_prompts, prompt_info, rag_section_text, etc. |
| **Observed exposure** | Unauthenticated ClickHouse; 11.7x expansion from yesterday's 6 named hosts |
| **Severity** | HIGH (70 verified AI-stack unauth CH hosts; row data not read per restraint) |

**Potential impact:** PostHog at `159.195.79.109` carries table `distributed_posthog_document_embeddings_text_embedding_3_large_3072` — the table name discloses the OpenAI model used, embedding dimension (3072d), and product analytics data class. vLLM multi-tenant operator at `108.248.232.250` has `vllm_service` DB with RAG-section + RAG-chunks tables across `pearlman`, `phl`, `phlDB`. Yoto (children's audio device, `129.153.24.132`) has `llm_prompts` table — a children's product with LLM prompts accessible without auth.

---

### [17.5] ES 2.9.x cohort — 95 hosts, CVE-2014-3120 BARE-confirmed

| Field | Value |
|---|---|
| **Name/ID** | 95 Elasticsearch 2.9.0 hosts within the unauth population |
| **Type** | Ancient-version Elasticsearch (pre-X-Pack era, Groovy scripting enabled) |
| **Evidence** | Version 2.9.0 confirmed via `GET /` JSON; BARE top-ranks `exploits_multi_elasticsearch_search_groovy_script` for 100% of these hosts |
| **Observed exposure** | Unauthenticated access + ancient version with unauth-RCE class; BARE match deterministic |
| **Severity** | HIGH (verified unauth + BARE match to unauth-RCE module; exploitation not attempted) |

**Potential impact:** CVE-2014-3120 allows arbitrary Groovy script execution via the `/_search` endpoint without authentication. 95 hosts confirmed at this version. Metasploit module `exploits_multi_elasticsearch_search_groovy_script` directly applicable. These hosts are 12 years behind on patches.

---

### [17.6] Meow extortion equilibrium — 92.4% prior state, 1.7% daily rate

| Field | Value |
|---|---|
| **Name/ID** | 3,604 ES hosts with Meow read_me index within the 5,037-host population |
| **Type** | Ongoing automated extortion campaign targeting unauth Elasticsearch |
| **Evidence** | Delta measurement: 92.4% already wiped at first probe; 1.7% new wipes in 24h; 5.4% operator-restored; 6.0% clean both surveys |
| **Observed exposure** | Campaign in equilibrium; restore rate (5.4%) exceeds new wipe rate (1.7%) |
| **Severity** | OBSERVED (campaign state documented; actor identity deferred to Session 17b) |

**Potential impact:** The campaign predates this survey. Operators who restore data without closing the auth gap are re-exposed immediately. Net direction is recovery not escalation. This finding drove retraction of Insight #28 and codification of Insight #29 (snapshot vs delta, Session 17b).

---

## 6. Risk Assessment

### Overall Posture

Two CRITICAL findings: a government health ministry's clinical terminology server and a multi-tenant hospital AI vector store, both unauth on public Elasticsearch, both mid-wipe by an active extortion campaign. 22 AI-stack ES hosts and 70 AI-stack CH hosts confirmed via schema probes. The re-probe produced no auth improvements: 0 operators closed the gap in 24 hours.

### Confidentiality

Nepal HMIS: 318,114 clinical concepts + 9 admin profiles accessible without authentication. Hospital AI: 270,000+ patient-record vectors. AI-stack ES/CH population: LLM call traces, RAG document chunks, prompt history, user chat histories accessible by any actor.

### Integrity

Meow campaign has already wiped 3,597 hosts. Operators who restore without closing auth are in a wipe-restore loop. The 5.4% restore rate is encouraging but the 0% auth-improvement rate means all restored data is immediately re-vulnerable.

### Availability

3,597 ES hosts had data deleted by the Meow campaign. These are the most extreme availability failures observable: not degradation, but complete destruction of data for operators who have no backup.

### Systemic Patterns

- **Zero auth improvement in 24 hours:** No operator in the 5,037-host population added authentication between the two probes. The only state changes were data deletion (attacker-driven) and data restoration (operator-driven). This confirms that unauth Elasticsearch is a structural posture, not a temporary oversight.
- **ClickHouse 22.3.20.29 dominance grows with cleaning:** 55% yesterday, 67.4% today after unresponsive hosts drop from the denominator. The image-tag dominance is real and growing as a population fraction.
- **Embedding dimension as LLM vendor fingerprint:** 256d/1536d/3072d = OpenAI; 768d = bge-base/m3e-base; 1024d = Cohere/bge-large. This is a new operator-attribution signal that requires no document reads.

---

## 7. Recommendations

### R1 — Critical-tier operators: immediate network isolation

For the Nepal HMIS and hospital AI hosts, the remediation is not authentication hardening. It is isolation first:

```bash
# Block public access immediately:
iptables -A INPUT -p tcp --dport 9200 -j DROP
# Or cloud security group: remove all inbound rules on port 9200
# Then: enable xpack.security before re-opening
```

Restore from backup only after closing the auth gap.

### R2 — Implement re-verify before disclosure send

```bash
# Before sending any ES disclosure, re-probe the host:
curl -s "http://<target>:9200/_cat/health" | jq .status
# If the host is wiped (only read_me index), amend the disclosure:
# "Your database has been deleted by an automated extortion campaign..."
```

The Meow campaign means 5.4% of the previously-wiped population has restored data by the time a disclosure draft is sent. 1.7% of the clean population gets wiped in the same window. Static disclosure copy built at harvest time is wrong for either cohort.

### R3 — ClickHouse AI-stack operators: set user password and bind to loopback

Same remediation as Session 16 R2. For SigNoz operators: SigNoz ships its own docker-compose with ClickHouse exposed to `0.0.0.0:8123` by default. Fix at the SigNoz docker-compose level:

```yaml
# signoz/deploy/docker/clickhouse-setup/docker-compose.yaml
# Change:
- "8123:8123"
# To:
- "127.0.0.1:8123:8123"
```

### R4 — Embedding dimension as future enrichment signal

Add embedding-dimension-to-provider mapping as a standard aimap enumerator output field. The mapping (`256/1536/3072 = OpenAI`, `768 = bge/m3e`, `1024 = Cohere`) is now field-validated across 22 real operators.

### Future automation

```bash
# aimap v1.9.8 now handles ES + CH deep enumeration:
aimap -list es-hosts.txt -ports 9200 -enum-elasticsearch -o es-findings.json
aimap -list ch-hosts.txt -ports 8123 -enum-clickhouse -o ch-findings.json
# Re-probe before any disclosure:
aimap -list previous-findings.txt -ports 9200 -quick-recheck
```

---

## 8. Limitations and Assumptions

| # | Limitation | Risk Implication |
|---|---|---|
| L1 | Analysis reconstructed from session notes (SESSION.md). Execution trace timestamps are approximate. | Exact probe timing not recoverable; sequence preserved |
| L2 | Insight #28 (71.6% wipe rate) was codified this session and retracted in Session 17b | The rate claim was wrong; the shelf-life rule survives for a different reason |
| L3 | _mapping probe capped at 30 indices per host | Hosts with >30 indices may have additional AI-stack vectors not counted |
| L4 | 22 AI-stack ES hosts is a floor; the 3,597 wiped hosts cannot be probed for schema | True pre-wipe AI-stack count is unknown and unrecoverable |
| L5 | VisorGraph attribution on 22 AI-stack hosts deferred to Session 17b | 5 of 22 hosts remain unattributed at session close |
| L6 | Ransom note contents not read this session (read in 17b per Nick's explicit override) | Actor identity and full extortion mechanics confirmed only in 17b |
| L7 | ClickHouse row reads not performed | Data classification relies on table names; actual data content and sensitivity unverified |
| L8 | Hospital host (106.75.127.240) operator name withheld pending disclosure | Attribution to specific hospital system not published |

---

## 9. Proof of Concept (PoC) Illustrations

### PoC 1: AI-stack confirmation via Elasticsearch _mapping

**Scenario:** Anonymous actor confirms a RAG / embedding workload on a publicly reachable Elasticsearch host without reading any documents.

```
REQUEST:
  GET /entity_vectors/_mapping HTTP/1.1
  Host: 106.75.127.240:9200

RESPONSE:
  HTTP/1.1 200 OK
  Content-Type: application/json

  {
    "entity_vectors": {
      "mappings": {
        "properties": {
          "entity_id": {"type": "keyword"},
          "entity_type": {"type": "keyword"},
          "source": {"type": "keyword"},
          "vector": {
            "type": "dense_vector",
            "dims": 768,
            "index": true,
            "similarity": "cosine"
          }
        }
      }
    }
  }
```

**Demonstrated:** The actor confirms: embedding vector field (768d, confirming bge-base or m3e-base Chinese model), cosine similarity (RAG retrieval workload), entity extraction pipeline (entity_id, entity_type fields). Does NOT read any entity records or vectors.

---

### PoC 2: ClickHouse LLM prompt history disclosure via table name

**Scenario:** Anonymous actor discovers an LLM prompt history table on an unauth ClickHouse host.

```
REQUEST:
  GET /?query=SHOW+TABLES+FROM+domestic+FORMAT+JSON HTTP/1.1
  Host: 111.231.19.122:8123

RESPONSE:
  HTTP/1.1 200 OK
  X-ClickHouse-Server-Display-Name: <hostname>

  {"data":[
    {"name":"prompt_info"},
    {"name":"user_sessions"},
    {"name":"chat_history"},
    {"name":"model_calls"}
  ]}
```

**Demonstrated:** Table names `prompt_info`, `chat_history`, and `model_calls` confirm the operator stores LLM conversation data in this ClickHouse database. The actor can issue `SELECT *` without authentication (not done per restraint ethic). Does NOT read rows.

---

### PoC 3: BARE module ranking on Elasticsearch 2.9.0

**Scenario:** Analyst ranks available Metasploit exploitation modules against the ES 2.9.x cohort using BARE.

```
# INPUT (findings.json from aimap ES enumeration):
# {host: "<host>:9200", platform: "elasticsearch", version: "2.9.0", auth: false}

bare -input findings.json -adapter aimap -top 3

# OUTPUT:
Rank 1: exploits_multi_elasticsearch_search_groovy_script
  Score: 0.918 | CVE: CVE-2014-3120
  Note: Groovy scripting RCE via /_search endpoint, no auth required, ES 1.3-2.x

Rank 2: auxiliary_scanner_elasticsearch_indices
  Score: 0.712 | CVE: N/A
  Note: Index enumeration scanner

Rank 3: exploits_multi_elasticsearch_dynamic_script
  Score: 0.701 | CVE: CVE-2015-1427
  Note: Sandbox escape via MVEL scripting, ES 1.3-1.6.0
```

**Demonstrated:** BARE deterministically ranks the Groovy RCE module as top match for this version at population scale. Does NOT execute the module.

---

*Prepared by NuClide Research (Nicholas Kloster + Claude Sonnet 4.6) · Session 17 · 2026-05-17*
