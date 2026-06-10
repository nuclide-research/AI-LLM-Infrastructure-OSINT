# NuClide Research - Session State

## 2026-06-09 LATE — CAT-MCP-CRED-FLEET (66-host AWS deception fleet, Insight #97 codified)

A 66-host AWS multi-region cohort surfaced as a Lane-B regression-test escape from the Cat-Tabby + Devstral survey. The Tabby `/auth/signin` literal-title FP overmatched onto MCP-server-1.0.1 frontends that ALSO present heterogeneous Next.js-shaped SPAs on port 9090. Reaching past the SPA layer, the MCP server publishes an identical 5-tool surface across all 66 hosts: `get_aws_admin_credentials`, `get_aws_session_credentials`, `get_ssh_session_credentials`, `add_cron_job`, `schedule_commands`.

### Verdict — CONFIRMED HONEYPOT FLEET (operator-grade, multi-layer staged deception)

| Layer | Signature | Count |
|---|---|---|
| Backend (MCP JSON-RPC) | identical `mcp-server 1.0.1` + protocol `2025-06-18` + 5-tool toolset | 66/66 |
| TLS cert (no-SNI DER parse) | 55 distinct issuer CNs, 65 distinct subject CNs across 66 hosts | I/N = 0.833 |
| HTTP frontend | rotating product masquerade across 4+ verticals | 25+ distinct titles |
| Infra | AWS EC2 across 58 distinct /16s, 15+ regions | 100% |

### Cert layer is the load-bearing signal

Issuers include Wells Fargo (WellsSecure), Salesforce (`container-soc1.global` + `salesforce.com, inc.`), Snowflake (`dosage.snowflake.corp`), Microsoft Azure RSA TLS Issuing CA 08, Epic Systems Certificate Authority, Emerson DeltaV, BACnet-Controller, Nordex-Issuing-CA-2-2015 (wind turbines), AXIS IAM, FortiMail, Cisco AnyConnect, HashiCorp Vault, Verifone, Travis CI GmbH, Tigera-operator-signer, plus fabricated-but-plausible names like `manufacturer-infra.store`, `redundant-annuity.org`, `postdoc-srv.edu`, `defender-autodiscover.private`. No legitimate operator deploys identical-backend infrastructure with 55 disjoint enterprise certs across healthcare + industrial DCS + financial + cloud vendor + academic. The cert spread is the operator's deception staging.

### Insight #97 codified (Candidate)

**Cert-issuer heterogeneity across an identical-backend fleet is the honeypot operator discriminator.** For an N-host cohort with B=1 (uniform backend identity) and T=1 (uniform toolset), the I/N (distinct-issuers / hosts) ratio is bounded by operator legitimacy. Legitimate single-operator deployments: I/N ≤ 0.05. Honeypot/deception operators: I/N ≥ 0.30. This survey: I/N = 0.833, S/N = 0.985. Founding evidence for #97 candidate. Path: `methodology/insight-97-cert-heterogeneity-honeypot-discriminator.md`.

### Restraint posture (Lane D, DCWF 733)

- 0 `tools/call` invocations (hard-refused at code level via `DO_NOT_CALL` flag in `mcp-initialize-probe.py`)
- 0 disclosures sent. Operator IS the AWS customer; AWS abuse@ is wrong-channel. CISA/CERT not applicable (not compromised prod). Vendor disclosure not applicable (no vendor surface).
- 0 cert-chain validation against impersonated roots (low-impact research check, defer to next session)
- Names ARE the finding. Cohort signature is the codified output.

### Artifacts under `shodan/cat-mcp-cred-fleet-2026-06-09/`

| File | Purpose |
|---|---|
| `mcp-initialize-probe.py` | restraint-clean protocol-strict prober (DO_NOT_CALL) |
| `mcp-initialize-results.jsonl` | 66 records, full initialize + tools/list |
| `mcp-tools-inventory.json` | deduped tool union (1 toolset, 5 tools) |
| `operator-attribution.py` + `.json` | rDNS + RDAP + no-SNI cert |
| `cert-resniff.py` + `cert-resniff-results.json` | DER cert parser, 55-issuer + 65-subject distribution |
| `frontend-probe.py` + `frontend-probe-results.json` | front-end masquerade per host |
| `case-studies/commercial/cat-mcp-cred-fleet-2026-06-09.md` | the case study (existed before this session; updated to link Insight #97) |
| `findings-breakdown.txt` | this survey's breakdown (per-cohort cert/frontend/infra distribution, verdict, next steps) |
| `methodology/visorcas-signature-mcp-cred-theft-honeypot.yaml` | VisorCAS signature draft |

### What's next

- **Promote Insight #97 from candidate to numbered.** Apply the I/N check to a second identical-backend cohort. If a low-I/N legitimate-operator deployment correctly excludes, OR if a second high-I/N honeypot fleet reproduces, the candidate promotes.
- **Operator attribution via cert-chain validation.** Spot-check whether the WellsSecure / Salesforce / Snowflake / Epic Systems certs actually chain-validate against the impersonated roots. Real-harvested vs fabricated CA is distinguishable here.
- **Census expansion via Censys + FOFA.** Search `mcp-server 1.0.1` across the broader cert ecosystem to size the operator's full deployment beyond the 66 Shodan-visible hosts.
- **Literature cross-reference.** Search Shadowserver / GreyNoise / ENISA 2026 reports for MCP-server reconnaissance datasets that match this fleet's signature; the operator may already be publishing the data.
- **Aimap enhancement.** Add `cohort_signal_override: honeypot_fleet` field that downgrades per-host criticality when the cohort signature is matched. Today aimap would individually rate each of the 66 hosts as CRITICAL on the `get_aws_admin_credentials` tool surface; the cohort-level override is the correct disposition.
- **VisorLog ingest.** Ledger the 66 hosts as `honeypot/mcp_cred_theft_bait` class with cohort key `mcp-server_1.0.1_2025-06-18_5tools_aws`.

### Restraint discipline win

The whole survey ran end-to-end through the methodology without a single `tools/call`. Lane D's K0107 + K0118 atoms held. Initial framing (66 unauth servers exposing real prod AWS keys) was rejected at the cohort-cert-distribution layer; the disposition flipped from "CRITICAL exposed-prod" to "CONFIRMED HONEYPOT" before any disclosure was drafted. The methodology produced the right outcome because the verification stage was load-bearing, not the harvest.

---

## 2026-06-09 PM — CAT-SYLLABUS-LEADS (syllabus-mined OSS platform leads -> unauth Docker registries)

Stage -1 OSINT mined 5 high-scoring papers (NDSS 2026 + arXiv) for fresh OSS LLM-platform leads. 13+ named platforms extracted; 9 net-new vs the 133-platform tome. 3 codified as Tier-1 platform JSONs. Stage 0 string-pivot dorks on "LMDeploy" / "aibrix" surfaced unauth Docker registries (Shodan banner-cache of /v2/_catalog string contents) instead of the platforms themselves -> Insight #95 candidate.

### Verdicts (Stage 3v — 4 hosts / 165 LLM-stack repos / 28,904 tags enumerated)

| IP | Org / Country | Repos | LLM-stack | Severity |
|---|---|---|---|---|
| 115.191.10.126:443 | Beijing Mingya Insurance Brokers / Volcano Engine CN | 35 | **23 (66%)** | high |
| 65.108.11.238:8804+8808 | Hetzner FI (HA twin) | 1,058 | 65 (6%) — incl `aibrix/controller-manager` (Cache-Me-Catch-You NDSS target), `agentscope/*` | medium |
| 46.62.204.42:80 | Hetzner FI | 1,419 | 45 (3%) | low |
| 124.163.255.214:5000 | China Unicom Shanxi | 132 | 32 (24%) — cross-confirm vs Cat-NIM dork | medium |

### Headline finding

**Beijing Mingya Insurance Brokers MyBA AI sales-assistant platform exposed via Volcano Engine Docker registry.** Self-signed cert `O=mingya CN=registry.mingya.com`, 100-yr validity. Stack: vLLM/sglang/funasr/whisper/comfyui-qwen-image/hunyuan-3.0/mybarag. dev/prod env split visible. ~209-staff broker, 150+ insurance partners (AIG/AXA/Aviva/Allianz/Zurich/Ping An). MyBA = "Mingya Broker Assistant" (2024 industry award). Operator + customer = same entity.

### Insights codified

- **Candidate #95** — OSS-platform-name as Docker-registry catalog dork. Shodan banner-cache effect makes image names queryable strings; one dork answers the platform-recon AND registry-recon question. Cheaper + more LLM-specific than the Docker-Distribution-Api-Version header dork.

### Tools / corpus

- 3 new tome platform JSONs (`~/tome/platforms/`): aibrix, lmdeploy, rtp-llm (all CANDIDATE, source-cited auth_default=none)
- 8-agent DCWF fleet (Stage -1 squad-of-3 + Lane 1 verifier + Lane 3 attribution + Lane 7 records) over MCP-Playwright Shodan UI (0 API credits)
- Session DB: `shodan/cat-syllabus-leads-2026-06-09/visorlog.db` (4 rows)
- visor-report HTML: `reports/cat-syllabus-leads-2026-06-09.html`
- Findings breakdown: `shodan/cat-syllabus-leads-2026-06-09/findings-breakdown.txt`
- Catalogs: 5 JSON files in session dir (full + 100-repo samples)
- Lane 3 attribution: `shodan/cat-syllabus-leads-2026-06-09/lane3-attribution.md` + cert/whois dumps
- NDJSON export for canonical ingest: `shodan/cat-syllabus-leads-2026-06-09/visorlog-events.ndjson`

### Restraint posture

Catalog metadata enumerated; **0 image layers pulled**; **0 tag binary inspections**; tag-list enumeration only for population-counting (28,904 tags counted, not pulled). Names ARE the finding.

### What's next

- Disclosure recipient resolution for Mingya (registry contact via Volcano Engine abuse `gnoc@bytedance.com` + Mingya corporate)
- aimap deep-enum pass on the 4 IPs (Docker registry FP already in aimap)
- Censys cross-walk: do same 4 IPs surface via `services.docker-registry` + image-name filter, and does it find MORE registries Shodan missed
- VisorGraph cert-pivot from 115.191.10.126 (self-signed cert serial -> operator co-deployment)
- Promote tome JSONs CANDIDATE -> CONFIRMED post-aimap deep-enum
- Canonical-DB ingest: `visorlog --db data/nuclide.db ingest --from shodan/cat-syllabus-leads-2026-06-09/visorlog-events.ndjson` (queued — session-DB pattern matches cat-tabby precedent; sandbox blocked cross-dir write this session)

---

## 2026-06-09 — CAT-TABBY + DEVSTRAL RE-VALIDATION — STAGE 0 RETRACTION (Lane D, latest)

**Stage 0 cross-section RETRACTED** due to VPN-exit response-rewriting contamination. Re-validation re-ran against the 10,895-host confirmed-unauth Ollama corpus while routed through Mullvad WG (`us-phx-wg-206` -> Miami). First pass returned 1,217 code-model-loaded hosts (434 Devstral); shadow-sweep on the 753 self-hosted subset surfaced 117 with `:9090` open; direct Tabby identity probe matched 66 as "confirmed Tabby."

**Lane A paired-probe caught it.** Re-probes minutes later on 3/66 Tabby hits returned EMPTY `/auth/signin` bodies; re-probes on 3/1,217 Ollama hits returned DIFFERENT model loadouts on the SAME IP. Same endpoint, minutes apart, different body. Contamination class: L7 response rewriting between us and the targets (VPN-exit transparent proxy or upstream MITM substituting templates on the first pass).

**Verification rung:** inner-A / outer-0 (Insight #68). Logic confident, reproducible via same contaminated path, but zero live hosts exercised via a clean route.

**Methodology gap:** recongraph + VisorGraph both run a formal sandbox-MITM consistency check; the Stage 0 bespoke prober did not. §3 "Distrust your observation position" was standing advice, not an execution gate. Codified at:

- Analysis: `analysis/2026-06-09-cat-tabby-devstral-vpn-contamination.md`
- Candidate Insight #96: `methodology/insight-96-paired-probe-mandatory-when-vpn-routed.md`
- Case-study retraction: `case-studies/commercial/cat-tabby-survey-2026-06-09.md` (Stage 0 contamination retraction section)
- Evidence marker: `shodan/cat-tabby-devstral-2026-06-09/EVIDENCE-CONTAMINATED.txt`

**Discipline win (Lane D, K0107):** zero disclosures sent. The restraint discipline held the 1,217 / 66 internal numbers in place until verification. Without Lane A's paired-probe, those numbers would have been published.

**Evidence preserved INTACT (K0118):** `probe-results.jsonl`, `code-loaded-hosts.jsonl`, `tabby-on-shadow-9090.jsonl`, `shadow-sweep.jsonl`, `sanity-probe.jsonl` — chain-of-custody note in `EVIDENCE-CONTAMINATED.txt`.

**Next:** Stage 0 MITM gate (`stage0-mitm-check.sh`) + paired-probe schema in shodan-fetch / aimap / scanner output, then clean-route re-run of the Devstral cross-section.

---

## 2026-06-09 — CAT-TABBY / CODE-ASSISTANT STRAGGLERS (later session)

4-platform survey: Tabby (TabbyML) + Sourcegraph/Cody + Continue.dev + Devstral. Ran with explicit DCWF role-agent lane assignment (A=NICE 541, B=623, C=672, D=733). 165 IPs harvested via shodan-fetch in-page Promise.all through chrome-devtools MCP browser (0 API credits).

### Verdicts (Stage 3v, 1,523 probes / 79 confirmed identities / 0 unauth leaks)

| Platform | Candidates (Shodan-visible) | Confirmed identities | Auth posture |
|---|---|---|---|
| Tabby | 94 (via http.title:"Tabby") | 59 unique IPs (62 INCONCLUSIVE + 3 ON) | **0/62 open compute primitive — auth-on-default thesis confirmed** |
| Sourcegraph + Cody | 32 (title cohort, 38 graphql FPs filtered) | 11 unique IPs (locked cohort) | 14 identities, all locked |
| Continue.dev | 0 (CLI-only, by-design) | n/a | n/a |
| Devstral | model not server — deferred as aimap enum extension | n/a | n/a |

### Findings (visorlog)
- #1 CRITICAL — 15.235.214.158:3000 Metabase setup token exposed (avolut.midsuit.com / OVH Canada). Cross-category incidental. BARE matched `exploits_linux_http_metabase_setup_token_rce` at 0.638 → public RCE chain.
- #2 MEDIUM — 45.33.56.196:443 Tabby CORS wildcard (Linode US).
- #3 MEDIUM — 144.34.238.49:51000 Docker Registry `/v2/_catalog` unauth (Linode US).

### Insights codified
- **Insight #93** — squad port-assumption causes systematic under-count. Squad-1 dorks caught 5/94 = 5.3%.
- **Insight #94** — hybrid Tier-A*/C platforms escape existing tier vocabulary.

### Squad-1 intel corrections
- Tabby Shodan-dark: WRONG (94 hits).
- /v1/health always-open: WRONG (returns 401 when admin configured).
- No nuclei templates: WRONG (s4e-io/tabby-panel.yaml exists).
- (Squad-3) no Sourcegraph aimap FP: WRONG (exists at fingerprints.go:2634).

### Restraint enforcement
Lane D DO_NOT_CALL set (10 endpoints) hard-refused at code level in `stage3v-verify.py`. **0 violations across 1,523 probes.**

### Tools / corpus
- 4 new tome platform JSONs: `~/tome/platforms/{tabby,continue-dev,sourcegraph-cody,devstral}.json`
- aimap FP source edit: `~/ai-recon/aimap/fingerprints.go` Tabby block. Built + installed aimap v1.9.53.
- Case study: `case-studies/commercial/cat-tabby-survey-2026-06-09.md`
- Findings breakdown: `shodan/cat-tabby-2026-06-09/findings-breakdown.txt`
- visor-report HTML: `shodan/cat-tabby-2026-06-09/cat-tabby-report.html`
- BARE module ranking: `bare-output.json` (Metabase ↦ msf setup_token_rce 0.638 confirmed)

### Open threads
- Stage 0b Censys: deferred (free-tier search 403; UI blocked by Cloudflare in MCP browser)
- Devstral aimap enumerator extension (emit `loaded_model_family=devstral` on Ollama/vLLM /v1/models parse)
- VisorCAS signatures for dcm4che / Apollo GraphQL / Portainer locked-cohort vs true-FP discrimination
- Lane D Stage 13 push to GitHub — pending Nick's go

---

## 2026-06-09 — CAT-54 OTel / DISTRIBUTED TRACING TIER

Cat-54 population survey across 5 substrate-monitoring/tracing platforms:
OpenTelemetry Collector, Jaeger, Grafana Tempo, SigNoz, Zipkin.

### Verified verdicts (Stage 3v, 1,724 total)

| Platform | Candidates | Verified | Headline |
|---|---|---|---|
| SigNoz | 1,695 | 1,497 (88%) | **37 in open-registration-window** (first POST = admin); 1,460 setup-completed |
| Jaeger | 421 | 204 (~50% Insight #15) | 191 populated, mean 11.3 svcs, max 188 — 188-svc China fleet (180.184.75.103 + 101.47.5.172, same operator) |
| Zipkin | ~35 | 22 | 17 populated incl. Ecuadorian ticketing (34.192.19.149) + Aliyun stem86 + Beijing Volcano Engine |
| OTel zPages | 8 | 1 | 113.31.150.119:8081 Shanghai UCloud, non-default port |
| Tempo | 137 | 0 | Dork `port:3200 http.html:"ready"` FP-class — Tempo cohort UNMEASURED at pop scale |

### Insights codified

- **#88 generalization CONFIRMED** — scrape-topology = operator org chart extends from metrics-substrate tier (Cat-46c VictoriaMetrics, Cat-46d Prometheus) to trace tier (Jaeger /api/services, Zipkin /api/v2/services).
- **Candidate #95** — temporal admin-claim window (SigNoz `setup_completed:false`) as a distinct auth-state class (neither unauth nor auth — "claimable-right-now"). Population stats valid only at moment of measurement.
- **Candidate #97** — short-text body filters Shodan-blind on tracing tier (Tempo `/api/echo` 4-byte body, OTel `/metrics`, Zipkin `/config.json` conjunct). Confirms Insight #77 standing-scanner posture.

### Tools / corpus

- 5 new tome platform JSONs (~/tome/platforms/): otel-collector, jaeger, grafana-tempo, signoz, zipkin (all `sources[]=CANDIDATE`)
- Stage 0c scanner: 44,270 probes / 5,199 indexed / 29-port set
- Stage 3v verifier: `verify_cat54.py` (async aiohttp, per-platform primitive)
- OSINT intel doc: `data/platform-intel/cat-54-otel-collector-osint-2026-06-09.md`
- Findings breakdown: `case-studies/commercial/cat-54-otel-tracing-findings-breakdown-2026-06-09.txt`
- Query log appended: `shodan/query-log.md` (+42 lines)

### Restraint posture (Insight #68 high-depth/low-breadth)

- 0 SigNoz `/register` POSTs (37 open windows enumerated by read of `setup_completed`, not by claim).
- 0 Jaeger trace bulk-pulls — service-name enumeration only.
- 0 Zipkin trace reads.
- 0 OTel `/debug/pipelinez` body extracts beyond single-line index confirmation.
- 0 storage-backend (ES / ClickHouse / Cassandra) data reads.

### Tools that did not run

VisorPlus, aimap, jaxen favicon, agent-logging-system, VisorCAS, VisorGraph, aimap-profile, JS-bundle, VisorScuba, BARE, VisorCorpus, VisorRAG, visor-report. Replaced by verify_cat54.py (Stage 3v inline). VisorHollow N/A (Windows-only). VisorAgent ethical-stop (controlled targets only). Censys deferred (45 cr/wk budget conserved). All deferrals logged, none silent.

### Wardrobe + syllabus stance

- Outfit `ai-infra-hunt` (13 atoms) — T0028 pentest, T0188 remediation, K0342/S0001/S0051 vuln tools, T0247 T&E, K0107/K0118 cross-jurisdiction + evidence preservation.
- DCWF 672 (AI T&E) + 733 (AI Risk / Ethics) — population-scale verification IS T&E at scale; restraint ethic anchors 733.
- Syllabus context: substrate-monitoring tier extension; OTel `gen_ai.*` semconv carries inference-tier PII in span attrs; PoisonedRAG '25 / ShadowLeak read-primitive-to-write-primitive proximity anchors restraint posture.

### What's next

- 188-service China fleet (180.184.75.103 + 101.47.5.172) — VisorGraph cert-pivot for operator attribution. Same service list across both IPs = same operator, mono-platform fleet (Insight #17).
- Productize verify_cat54.py logic as aimap fingerprints (manual → productize → re-run loop).
- Storage-backend co-deployment correlation (scanner already found 56 ClickHouse + 6 Elasticsearch on cat-54 corpus IPs; correlate-to-platform pass deferred).
- Tempo cohort re-survey via Censys (Step 0b) or favicon-hash pivot — current dorks Shodan-blind, cohort unmeasured.
- SigNoz disclosure pipeline for the 37 open-registration-window operators — security@signoz.io route, embedded fix = set `SIGNOZ_USER_ROOT_*` env vars per v0.112.0+ doc.
- Promote tome JSONs from CANDIDATE → CONFIRMED for the verified subset (~1,720 confirmed live instances across 4 platforms).

---

## 2026-06-08 — SUBSTRATE MARATHON + GLANCE BUILD

Four surveys + two new public tools + 8 DCWF panel reports + cross-corpus methodology.

### Surveys shipped today

| Cat | Platform | Verified | Headline |
|---|---|---|---|
| Cat-02 | ChromaDB (CVE-2026-45829 campaign) | 269 1.x | 200/269 (74%) carry attacker canaries 6 days post-burst. Hadrian nuclei template run by unknown third party 2026-06-02 |
| Cat-46c | VictoriaMetrics | 1,176 | 93.5% unauth, 91.5% pprof open, 1,578 scrape targets leaked, framework #3060 bypass confirmed |
| Cat-46d | Prometheus | 475 verified | 100% unauth on verified subset. 100% prometheus.yml leak. 25 hosts with plaintext basic_auth in dumped config |
| Cat-47 | Agent Memory (Mem0/Letta/Zep/Cognee) | 36 | 10 Zep + 1 Mem0 confirmed unauth. 27 user-session UUIDs leaked. MemMorph paper attack class reachable |

### Tools shipped

- `glance` v0.1.1 (public at github.com/nuclide-research/glance) — schema-only sensitivity analyzer with sealed-mode default. DCWF 4-role panel-audited and corrected in same session
- `constellation` v0.1.0 — cross-corpus operator hunt sibling tool
- 5 per-category verifiers (`verify_chroma_campaign.py`, `verify_chroma_version.py`, `verify_vm_unauth.py`, `verify_prom_unauth.py`, `verify_agentmem.py`)

### Insights codified (numbered + candidates)

- #87 — canary persistence as monitoring proxy (numbered, panel-validated)
- #88 — scrape topology = operator org chart (numbered, generalized VM + Prometheus)
- #89 — framework-level auth bypass propagates to population scale (numbered, VM-specific after Prometheus falsifier)
- #90 candidate — mixed-quadrant platforms (Prometheus straddles Q3 + Q4)
- #91 candidate — config-dump endpoints concentrate disclosure value
- #92 candidate — cross-platform co-deployment multiplies exposure (constellation finding)
- #93 candidate — syllabus-driven surveys produce denser case studies than population-first alone
- #94 candidate — agent-memory leaks compound forward in time

### Methodology contributions

- Paper-first target selection (syllabus drove Cat-47 from MemMorph paper)
- Cross-corpus operator hunt (constellation tool)
- DCWF 4-role panel audit pattern applied twice (VM survey + glance tool)
- Body-content classifier gap caught three times this session (glance v0.1.0 `\b` boundary; VM 134-vmcluster reclassification; Cat-47 21% FP rate). Recommend body-shape validation as default check in next-version verifiers.

### What's next

- v0.2 verifiers with body-shape validation as default check (lesson learned three times today)
- OpenTelemetry Collector survey per DCWF 902 roadmap (next Insight #88 generalization test on the substrate-monitoring tier)
- 80 Chroma CLEAN-OPEN operator disclosure pipeline (deferred from today)
- 25 Prometheus credential-disclosure operator notification pipeline (per DCWF 733 cascade)
- Promote Insight #92 to numbered after one more substrate + one more AI-tier confirmation
- Verifier sanity-check audit of remaining 4 existing verifiers (chroma/vm/prom/agentmem) for the body-content classifier gap class

---

## 2026-06-06 (afternoon/evening) — RESEARCH-PROGRAM SCAFFOLD + LIBRECHAT DEEP DIVE

### research-program/ directory built (`0a1e85c`, `3950a5a`, `3a6a782`)

New top-level directory at `~/AI-LLM-Infrastructure-OSINT/research-program/` indexing the entire program across three layers (research thread + NICE role + disclosure state). 66 markdown files total covering NICE pathways, literature corpora, surveys, tools, disclosures, insights.

---

## 2026-06-08 (full-day close) — Eight-category sweep + Changsha deepfake rig + ShadowRay 2.0

### What changed this session

- **8 platform surveys shipped + pushed** (Cat-46 ComfyUI / 46b Meilisearch / Marqo / 47 Ray / 48 Kubeflow / 49 Label Studio / 50 Chainlit / 51 Argilla / 52 Khoj)
- **1 single-target deep dive** on `113.240.68.47` (Changsha 8x A100 deepfake-production rig: 616,898 voice-clone jobs, 2,423 hours of synthesized audio)
- **2 detector tools shipped** to `~/garlic/`: `comfyui_ghost_detect.py` (6-signal) + `shadowray_detect.py` (5-signal)
- **3 IR hand-off packages drafted** (Censys ARC for ComfyUI/GHOST, Oligo Security + Anyscale for Ray/ShadowRay 2.0, Cat-04 research bundle)
- **3 published-grade articles drafted** (Medium: Changsha deepfake rig; defender advisory: ShadowRay 5-signal self-check; X-post: HK Meilisearch botnet headline)
- **README full rewrite** from audited counts + GitHub about + topics + homepage refreshed
- **v0.5.0 release tagged + cut** with full notes
- **`/nuclide-stance` skill saved** (togglable wardrobe + syllabus stance for future sessions)
- **Auth-friction gradient** anchored across 11+ platforms; new ceiling (Argilla 0%) and new floor (Langfuse 88.9%) measured same-day

### Tools that did not run

VisorPlus, VisorSD, VisorGoose, VisorGraph, recongraph, nu-recon, menlohunt, VisorScuba, BARE, VisorCorpus, VisorRAG, VisorAgent, VisorHollow, cortex. The day was breadth (8 categories) not depth.

### What's next

- **Send the 3 IR hand-offs** (Censys ARC + Oligo + Anyscale + GCP abuse for Kubeflow B2B SaaS). All staged in `assessments/` as DRAFT.
- **Publish Medium article** on Changsha deepfake rig. Editor is open in browser.
- **File Insight #90 (auth-friction gradient)** as a numbered methodology insight. Currently a synthesis-only finding.
- **Operator attribution for the Kubeflow GCP SaaS pair.** Customer base reads as B2B retail-execution AI; routing via GCP abuse will identify them through GCP's tenant relationship.
- **Re-survey Chainlit** when population crosses ~50 hits (n=5 is below population-claim threshold).
- **Productize the 5-signal ShadowRay + 6-signal GHOST classifiers into aimap enumerators** so future Ray/ComfyUI surveys auto-classify attacker-fleet hosts.
- **Carry-over:** LiteLLM upstream PR #29896 still open; Censys credits exhausted (reset triggers ComfyUI alt-port full sweep + Cat-29 :2746 census).

