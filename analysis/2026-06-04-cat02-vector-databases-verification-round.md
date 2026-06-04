# Analysis — Cat-02 Vector Databases (verification round + attribution)

**Date:** 2026-06-04
**Arc:** Cat-01 methodology applied to Cat-02 as round 3. Stage -1 intel doc (never existed) ->
resolve the load-bearing verification 06-03 deferred -> live re-verify -> attribution -> ledger.
Mid-session: the NuClide methodology was promoted to default operating logic across Claude (CLAUDE.md v2.5).

## 1. Overview
06-03 ran the full arsenal on 233 vector-DB hosts but (a) hedged its verification to "32 candidate-real,
data-read NOT exercised," (b) ran Shodan-only (no Censys), (c) did no operator attribution, (d) covered only
6 vendors. This round built the missing Stage -1 intel, RESOLVED the verification from 06-03's own captured
enum data, re-verified a live sample, and added attribution. Censys expansion was blocked on credits.

## 2. Tooling
- **OSINT Platoon** (4 Sonnet lanes) -> data/platform-intel/vector-databases-osint-2026-06-04.md
  (~22-vendor universe, auth posture, verification endpoints, SHODAN-DARK map, matcher rules, FP catalog).
- **aimap v1.9.46** live re-verify (7 standouts, threads=5, congestion-controlled for home uplink).
- **Dev-browser** (Playwright MCP) Shodan host-page attribution (0 credits).
- **aimap-to-findings.py** -> **VisorLog** ingest (602 events into data/nuclide.db).
- **VisorScuba** assess (ledger-wide score).
- **Censys** — BLOCKED (1 credit balance, search=5cr, resets 2026-06-08). Logged, not skipped.

## 3. The load-bearing finding: verification was a REPORTING gap, not a probing gap
06-03's `aimap-report.json .enum_results` already held the data-layer reads (real collection names, object
counts, schema with pii_field flags). The breakdown under-surfaced them as "candidates." Reading the enum
output fully RESOLVES the survey with zero new packets.

**Resolved tally (auth=none + non-empty real data, captured 06-03):**
- ChromaDB 24, Weaviate 14, Milvus 14, Docker Registry 5, RedisInsight 1 = **58 verified unauth data reads**
  (vs 06-03's hedged "32 candidate-real").
- Identity-only (open surface, empty/no data): Weaviate 9, Lunary 2 (mis-tag), vLLM 1, Qdrant 1, Chroma 1 = ~14.

**Live re-verify 06-04 (7 standouts, congestion-controlled):** 7/7 still auth=none, identical collections.
Cross-session claim discharged for the sample; population stable (no remediation in 24h).

## 4. Findings (evidence-gated)
- **CRITICAL — unauth data-layer read on 58 hosts.** Hard proof = the live/captured 200-with-non-empty
  collection read. Restraint held: names + counts + schema property names only; objects NOT read; PII INFERRED
  from property names, not exfiltrated.
- **Standouts:** a Chroma host (Azure) = 59,856 objects in `post_market_safety` + `ip_patents` +
  `financial_disclosure` (pharma/legal/financial); `disease_glm_collection` 49,458 (Huawei CN);
  `doc-Hypertension` (E2E India); `etsu_information` 7,097 (Oracle, likely East Tennessee State); Weaviate
  `LegalDocument`/court_name (Hetzner), `MedicaidRule`, `SupportRequest`/email; Milvus `Thalys*`,
  `resume_embeddings`, `chatbot_documents`.
- **Milvus 9091 unauth = CVE-2026-26190 surface** (credential create/list). NOT exercised (restraint).
- **Docker Registry 5 hosts** expose repo catalogs (qdrant/milvus/vllm/sglang images). Layer-secret chain NOT run.
- **ACTIVE THIRD-PARTY EXPLOITATION:** 5 Chroma hosts carry `cve202645829_test_probe` collections + wide
  `probe-base-<ts>` artifacts = other actors are already mass-probing the unauth Chroma tier for the RCE CVE.

## 5. Attribution finding (structural)
All 16 attributed standouts: **0 forward hostnames, 0 TLS certs** — bare-IP cloud VPS. `org` = cloud provider
only (Azure, Aliyun, Huawei, Tencent, Oracle, DigitalOcean, Linode, Hetzner x2, Google x2, OVH-India,
E2E-India, budget VPS). Global, hyperscaler + China-cloud + budget mix. **The operator is identifiable only by
the collection/class names they stored** — the http-no-cert tier defeats DNS/cert attribution.

## 6. Risk assessment
Auth-on-default thesis holds: the dedicated vector-DB tier (Weaviate/Milvus/Qdrant/Chroma) is auth-OFF by
default and the exposed population proves it. Posture hardens by ADDED controls (Weaviate RBAC v1.30, Milvus
bypass fixes, ES 8.0 on-by-default, OpenSearch 2.12 forced-password) but the unconfigured default stays open.
Real critical risk = the large-object Chroma stores (pharma/legal/medical) and the Milvus 9091 credential
surface. Severity tracks data sensitivity (medical/legal/financial collection names), not population size.

## 7. Limitations / negative space
- Censys expansion (Shodan-dark vendors + embedded-lib bucket angle) NOT run — credit-blocked to 06-08.
- Attribution: 16 standouts only; the http-no-cert reality caps yield at cloud-provider org (no domains).
- 44 of 58 verified hosts rest on 06-03 capture + sample-confirmed population stability (not each re-probed).
- Lunary (2) is a category mis-tag (observability), reclassify to Cat-05.

## 8. Candidate Insights
- **#72** — verification can be a REPORTING gap, not a probing gap: read your tool's deep-enum output fully
  before declaring verification deferred (06-03 had the data the whole time).
- **#73** — probe-pollution-as-signal: scanner/attacker artifacts (cve-test, probe-base collections) in an
  open store are a measurable proxy for active third-party exploitation interest. Strip from the data tally,
  COUNT as a threat-activity finding.
- **#74** — VisorCAS 404-as-unauth screen can OVER-correct (06-03 downgraded 40 on status grounds while the
  deep-enum had pulled real data). The screen must check enum_results, not just fingerprint-match status.
- **#75** — the http-no-cert vector-DB tier defeats cert/DNS attribution; operator is named by stored data.

## 9. Round-N (carry-forward)
- Censys expansion after 06-08 reset: Shodan-dark vendors (Chroma/Milvus/Typesense/pgvector) + embedded-lib
  bucket enum (LanceDB/.lance, Deep Lake/dataset_meta.json) per the intel SHODAN-DARK map.
- Fix VisorCAS screen (#74). New aimap fingerprints: Marqo (`Welcome to Marqo`), Manticore (9306 handshake),
  Vald (gRPC reflection), Meilisearch embedders block.
- Reclassify Lunary out of Cat-02.

## Toolchain provenance
OSINT Platoon (Agent x4) -> aimap enum_results (06-03, free resolution) -> aimap live re-verify (7) ->
dev-browser attribution (16) -> aimap-to-findings -> visorlog ingest (602) -> visorscuba.
Recon dir: ~/recon/02-vector-databases-2026-06-04/. Intel: data/platform-intel/vector-databases-osint-2026-06-04.md.
