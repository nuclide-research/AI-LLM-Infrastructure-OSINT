# NuClide Research - Session State

---

## 2026-06-18 (later) — CAT-RAG CARRY-OVER CLOSE-OUT + backlog triage

### Completed this session (all 5 immediate carry-over items)

- **35.78.152.204 resolved** (cert-SAN Host header, not rDNS which is generic ec2). Cert CN `console.ran-nssmf.sorp.docomo.ne.jp` -> **NTT DoCoMo 5G RAN-NSSMF management infra**. Server `awselb/2.0`: AWS ALB returns 403 on every path. Verdict SURFACE-OPEN, access not exercised. Carrier 5G infra -> hard restraint, names ARE the finding. LEADS L-01 finalized.
- **F6 babbid.com operator attribution.** Babbid Centros de Negocios (Madrid, ES coworking SME), domain reg 2019 via IONOS, Cloudflare-fronted; origin 108.132.72.10 AWS eu-west-1 self-signed cert past the WAF. LEADS L-04 + case study F6 updated.
- **Insight #106 codified** (candidate): a 422 on a chat/inference endpoint = request format mismatch, not access denial. Request-side dual of #16. Founding case babbid (422 on `messages`, 200 on `message`). `methodology/insight-106-422-format-mismatch-not-access-denied.md`.
- **auth_mode-vs-endpoint candidate was ALREADY #104** (codified 2026-06-17). SESSION note was stale.
- **LightRAG /health X post finalized** at `data/disclosures/lightrag-health-x-post-draft.md` (2 options, em-dash-clean). READY TO POST. Nick posts (outward-facing); I did not auto-post.
- **Persisted to GitHub** (`87fef05`, pushed to origin/main). Note: the bulk RAG artifacts were already committed+pushed in `582ec07` (the "blocked on Nick's go" note was stale). This commit = the post-verify attributions + insight #106 + X-post draft, scoped (raw IP data stays gitignored per repo boundary).

### Backlog triage (older queue)

- **BentoML git push: ALREADY DONE.** OSINT repo nothing unpushed; aimap `f3062c2` already pushed, tree clean. Stale note. (Deferred-tools pass for BentoML is a separate re-open, not done.)
- **Orphaned methodology insights** #95, #98, #99, #100 sit untracked in `methodology/` (complete, prior-session). Not swept into this commit (out of RAG scope). Decision needed: commit as a methodology catch-up?
- **SigNoz 37 open-registration disclosure pipeline: BLOCKED on constraint.** Conflicts with `feedback_no_disclosure_recommendations` (never offer/prep/recommend disclosure). Not actioned.
- **Not started** (each = a fresh full-arsenal survey needing the live Shodan/Playwright browser singleton): 51-host Linode mcp-server 1.0.1 I/N measurement (#97 promotion); Cat-LMDeploy Lane A re-dispatch (schema-anchor fix); xamplify-mcp + open-alice per-platform arcs (metadata-only, state-changing tools = no tools/call).

---

## 2026-06-18 — CAT-RAG-FRAMEWORK-SERVERS (re-verification + LightRAG disclosure)

### What changed this session

- **Re-ran 3v verification** on all pending candidates from the prior session
- **4 unreachable LightRAG hosts** (51.142.10.48, 98.81.157.172, 159.69.89.55, 167.172.40.40): STILL-DOWN — confirmed scale-in. Final LightRAG unauth count: 9/17 original candidates live+unauth (53%)
- **L-01 AWS Tokyo LightRAG Swagger fleet**: 3/4 hosts gone (timeout). 35.78.152.204 alive but returns 400 on bare-IP probe (Host header required). Only 52.69.81.89 survives.
- **F6 NEW CONFIRMED HIGH** — 108.132.72.10:443 (app.babbid.com): LlamaIndex chat, POST /api/chat returns live LLM response with zero auth. Spanish office-finder chatbot. Named commercial operator.
- **S-04 SURFACE-OPEN LOW** — 23.239.19.219:8000: LlamaIndex Chat Linode, endpoint accessible no-auth, backend returns 500 (LLM broken).
- **LEADS.md updated** with all verdicts (F1-F6 + S-04 + refuted L-02/C-03 + negatives N-01/N-03)
- **LightRAG F5 disclosure filed** — GitHub issue #3294 at github.com/HKUDS/LightRAG/issues/3294 (filed as nuclide-research). Finding: /health whitelisted by default in WHITELIST_PATHS (config.py:641); leaks llm_binding, llm_model, working_directory on ALL instances including auth-enabled. 67/67 confirmed in population survey. Fix: strip config from /health response.
- **X post drafted** tagging @huang_chao4969 (lab director, Chao Huang, Data Intelligence Lab@HKU)
- **Advisory file** written to data/disclosures/lightrag-health-config-disclosure.md

### Novel insights from this session

- **Insight candidate (422 format-mismatch):** 422 on a chat endpoint = wrong request format, not access denied. Probe message/messages/query/data.message variants before closing as denied. babbid.com found via this path.
- **Insight candidate (auth_mode flag != endpoint-level gating):** auth_mode=disabled confirms /query open; does NOT guarantee /documents open. 2/9 unauth LightRAG hosts return 403 on /documents despite auth_mode=disabled. Different risk tiers (compute theft vs data exfiltration).

### Survey final state

| Finding | Severity | Platform | Operator | Status |
|---------|----------|----------|----------|--------|
| F1 | HIGH | Qdrant | 82.165.133.93 Hanssen Agency | 531 nextcloud docs, private PII |
| F2 | HIGH | Qdrant | 31.57.224.107 ilmverse.ai | 71k quran corpus, R/W/D |
| F3 | MED | Ollama | 54.37.225.10 OVH | 4 models, cloud-relay Gen-3 |
| F4 | HIGH | LightRAG | population | 9/17 (53%) live+unauth |
| F5 | HIGH | LightRAG | platform-wide (67 instances) | /health config disclosure — DISCLOSED #3294 |
| F6 | HIGH | LlamaIndex | 108.132.72.10 babbid.com | Live chat, zero auth |
| S-04 | LOW | LlamaIndex | 23.239.19.219 Linode | Surface open, backend broken |

Refuted: Neo4j 8 hosts (all authed), 206.189.153.160 (all 3 legs authed)
Negatives: MS GraphRAG (APIM-gated), Haystack (Shodan-dark)

### What's next

- Tag @huang_chao4969 on X with the LightRAG /health finding
- Codify 422-format-mismatch and auth_mode-vs-endpoint insights as numbered methodology insights
- Probe 35.78.152.204 with rDNS Host header (last surviving Tokyo LightRAG Swagger host)
- Operator attribution for babbid.com (F6) — cert/rDNS pivot on 108.132.72.10
- Persist Cat-RAG-Framework-Servers findings to GitHub

---

## 2026-06-10 ~03:00 CDT — CAT-LMDEPLOY (4-lane DCWF parallel dispatch — Insights #101+#102 codified, browser-singleton methodology gap)

4-lane DCWF parallel dispatch (NICE 541 / DCWF 623 / 672 / 733) against the LMDeploy InternLM inference framework (port 23333, auth_default=none confirmed at `api_server.py:1486`). Wardrobe outfit `dod-pathway` (12 atoms, 39-role cross coverage). Stage 0 Shodan harvest BLOCKED by MCP browser singleton contention across sibling lanes; Stage 0b Censys BLOCKED by feature-credit bucket drained separately from `cencli credits` display.

### Verdict — METHODOLOGY-FINDING, population estimate UNKNOWN

The 5-IP bootstrap cohort (3 from prior Cat-03 + 2 from tome registry_mentions) was **100% refuted as LMDeploy** by Lane C marker-pair verification (`/openapi.json` must contain `/distserve/engine_info` + `/v1/chat/interactive`). Every host responded as a Docker Distribution v2 unauthenticated registry that catalogs an LMDeploy image, not an LMDeploy server. This is the methodological **dual of Insight #95**: the platform-name HTML dork lands on registries cataloging the image, not platform instances.

### Convergence with Cat-Syllabus-Leads 2026-06-09

| Host | Cat-Syllabus-Leads finding | Cat-LMDeploy verdict |
|------|----------------------------|----------------------|
| 115.191.10.126 | Beijing Mingya MyBA Docker registry (HIGH) | Docker registry confirmed, NOT LMDeploy |
| 65.108.11.238 | Hetzner FI HA registry pair (medium) | Docker registry HA confirmed, NOT LMDeploy |
| 46.62.204.42 | Hetzner DE registry, aibrix CANDIDATE | Docker registry confirmed, NOT LMDeploy |
| 124.163.255.214 | China Unicom Shanxi registry | Docker registry confirmed, NOT LMDeploy |

Two surveys converge on the same 4 operators from opposite directions. Shodan banner-caches both the registry-catalog JSON and the platform-HTML signal, surfacing the same upstream Docker artifact metadata twice.

### Insights codified

- **#101 (candidate)** — Per-platform path-class taxonomy encodes restraint at code level: DOC / READ / COMPUTE / ADMIN. LMDeploy's 23 paths partition cleanly (4/3/7/9). Verify-allowlist = 7 of 23. Generalization conjecture covers vLLM, SGLang, TGI, AIBrix, Triton. Path: `methodology/insight-101-per-platform-path-class-taxonomy-encodes-restraint-at-code.md`.
- **#102 (candidate)** — Dork-stage schema anchor required for OSS-name-collision platforms (dual of #95). Strategy A (positive schema anchor at Stage 0) or Strategy B (negative anchor `-http.html:"v2/_catalog"`). Path: `methodology/insight-102-dork-stage-schema-anchor-dual-of-95.md`.

### Restraint discipline

| Lane | Probes | DO_NOT_CALL violations | Notes |
|------|--------|------------------------|-------|
| A | 30 banner | 0 | banner-only, no L7 read of any LMDeploy endpoint |
| B | 0 against survey set | 0 | aimap matcher edits + negative-control smoke-test |
| C | 60 | 0/60 | 15-entry `DO_NOT_CALL` hard-refused at code level |
| D | 0 | 0 | aimap-profile classification + Cat-Tabby reconcile-rule discipline held |

### Operational methodology gap (not insight-codified)

4-lane parallel dispatch contended on the MCP browser singleton. Both `chrome-devtools` and `playwright` MCPs hold persistent `--userDataDir` locks; any lane that uses Shodan in-page fetch starves the other 3. Next dispatch: designate Lane A as singleton-holder; Lanes B/C/D consume the produced `ips.txt`. Will amend `~/.claude/skills/nuclide-stance/lane-prompts/` to encode this.

Separate operational note: `cencli credits` display is NOT the feature-credit budget. Feature-credit bucket is tracked separately and can drain while display shows available credits. Verify via test view before planning a query plan.

### Artifacts

- Case study: `case-studies/commercial/cat-lmdeploy-survey-2026-06-10.md`
- Findings: `shodan/cat-lmdeploy-2026-06-10/findings-breakdown.txt`
- Methodology: `methodology/insight-101-...md`, `methodology/insight-102-...md`
- Analysis: `analysis/2026-06-10-cat-lmdeploy-jurisdiction-and-restraint.md`
- aimap FP: `~/ai-recon/aimap/fingerprints.go:374-398` (3-anchor /openapi.json matcher)
- agent-logging-system patch: `~/agent-logging-system/agent_logging_system/adapters/aimap_adapter.py:91-100` (null-coalesce, byproduct)

### What's next

- Re-dispatch Lane A solo (singleton freed) for real population estimate against the 6-dork set
- Apply Insight #102 schema-anchor fix to all tome platforms with name-collision risk (vLLM, SGLang, AIBrix, TGI, Triton, Langfuse): audit dork tiers, add `dork_fp_risk` + `schema_anchor` metadata fields
- Promote #101 candidate: confirm 4-class path taxonomy against vLLM / SGLang / TGI (any 3)
- Promote #102 candidate: confirm dork-FP class against 2 more OSS-name-collision platforms (vLLM, SGLang are obvious next)
- Amend `~/.claude/skills/nuclide-stance/lane-prompts/` shells with the MCP browser singleton serialization rule

---

## 2026-06-10 02:30-03:15 CDT — INSIGHT #97 PROMOTED to numbered (Cat-MCP-Cred-Fleet 2026-06-10 reproduction survey)

Insight #97 (Cert-Issuer Heterogeneity Across an Identical-Backend HTTPS Fleet is the Honeypot Operator Discriminator) promoted from CANDIDATE to NUMBERED after the 2026-06-10 follow-on survey produced two independent reproduction sub-cohorts on a second port + a clean boundary-condition observation from a falsification probe.

### Promotion evidence

| Cohort | Date | Port | N | I | I/N | Disposition |
|---|---|---|---|---|---|---|
| Founding | 2026-06-09 | 9090 | 66 | 55 | 0.833 | HONEYPOT_CONFIRMED |
| Reproduction A | 2026-06-10 | 9090 | 9 | 9 | **1.00** | HONEYPOT_CONFIRMED |
| Reproduction B | 2026-06-10 | 3001 | 13 | 13 | **1.00** | HONEYPOT_CONFIRMED |
| Merged | 2026-06-10 | both | 86 | 72 | 0.837 | HONEYPOT_CONFIRMED |
| Falsification probe (open-alice) | 2026-06-10 | 3001 | 2 | - | N/A | OUT_OF_SCOPE_HTTP-only |

Boundary condition codified: I/N requires TLS. HTTP-only cohorts fall through to Insight #30 (multi-port discriminator). The decision to serve TLS is itself operator-legitimacy signal — the deception operator must run TLS in order to stage per-host certs.

### Operator behavior change observed

- All 66 original cred-theft IPs still alive at the 24-hour mark with identical backend + identical 5-tool surface. Infrastructure stable.
- 22 net-new IPs match the same backend signature on the same or adjacent port. None overlap the original 66. Operator is expanding, churning, or both.
- 1 of the original 66 IPs also serves on port 3001 with the identical backend. Multi-port serving confirmed for at least one host — boundary between Insight #30 and Insight #97 + reinforces their complementarity.
- All 22 new IPs are AWS multi-region (3.x, 13.x, 15.x, 16.x, 18.x, 43.x, 47.x, 51.x, 54.x, 56.x).
- Total verified cred-theft cohort across both snapshots: 86 unique IPs.

### Insight #30 vs Insight #97 partition codified

The 51-host Linode `mcp-server 1.0.1` fleet (2026-05-17 mcp-server-survey) and the now-86-host AWS cred-theft fleet represent **two distinct deception operator classes** on the same canned backend:
- **Insight #30 catches**: multi-port template-honeypot operators (51-host Linode; cheap-deception, multi-port canned response)
- **Insight #97 catches**: single-port cert-staged operators (86-host AWS; expensive-deception, sectoral cert distribution)

Procedural rule 5 of Insight #97 sets the 51-host Linode I/N measurement as the next high-priority replay target.

### Side findings (surfaced + queued for separate per-platform arc)

20 legitimate-operator MCP backends on port 3001, several exposing state-changing tools unauth:
- **xamplify-mcp 1.0.0** (CRM, 48 tools, create_campaign/create_deal/create_domain_whitelist)
- **open-alice 1.0.0** (financial-trading, T=42-52 across 4 hosts, cancelOrder/closePosition/calculateIndicator)
- **google-calendar 1.3.0** (calendar CRUD, 12 tools)
- **figma-mcp-server 1.0.0** (5 tools)
- **gitea-mcp 1.0.0** (5 tools)
- **Minecraft Brain REPL 1.0.0** (REPL surface, 7 tools - arbitrary code)
- promptbook-mcp, nowcoder-mcp-server, defuzion-mcp-server, Address-Intelligence-MCP, appstore-mcp, IusBot MCP, ozon-mcp-server, mcp-chatwoot, ayni-protocol, tkt, figma-mcp, Casdoor MCP, hindsight-mcp (single-host each)

Each is a candidate disclosure case study; per-platform restraint + routing review required. **No tools/call** issued against any of these. metadata-only.

### Stage -1 codify

`~/tome/platforms/mcp-server.json` written and tome binary rebuilt — first MCP entry in the corpus. `tome dorks mcp-server --dork-tier version` now returns `"mcp-server" "1.0.1" "2025-06-18"`. Stage -1 codify-every-platform-into-tome discipline applied.

### Restraint posture (DCWF 733)

- 0 `tools/call` invocations against any cred-theft host (DO_NOT_CALL hard-refused at module load)
- 0 `tools/call` invocations against any legitimate-operator backend (metadata-only)
- 0 disclosures sent. Cred-theft operator is the customer; disclosure pipeline gated by Insight #97 `cohort_signal_override`. Legitimate-operator backends queued for separate routing review.

### Artifacts (path-rooted at AI-LLM-Infrastructure-OSINT/)

- `methodology/insight-97-cert-heterogeneity-honeypot-discriminator.md` (promoted to numbered)
- `shodan/cat-mcp-cred-fleet-2026-06-09/harvest-2026-06-10/` (full reproduction survey data + analysis + findings-breakdown.txt)
- `~/tome/platforms/mcp-server.json` (Stage -1 codify; tome's first MCP entry)
- `~/tome/` binary rebuilt at `~/go/bin/tome`

### What's next

1. 51-host Linode `mcp-server 1.0.1` cohort I/N measurement (procedural rule 5; expected I/N narrow or HTTP-only; would close the partition between Insight #30 and Insight #97 deception-operator classes).
2. Operator attribution via cert-chain validation on the 86-host cred-theft cohort (real-harvested vs fabricated CA distinguishable).
3. Censys + FOFA census expansion of the 86-host cohort (100 Censys credits available, resets 2026-07-08).
4. Per-platform survey arc for the 20 legitimate-operator MCP backends (xamplify-mcp, open-alice, google-calendar, figma-mcp-server, gitea-mcp, Minecraft Brain REPL, etc.). xamplify-mcp + open-alice are highest-impact (CRM + financial state-changing tools).
5. VisorLog ingest: ledger the 86 hosts as `honeypot/mcp_cred_theft_bait` class with cohort key `mcp-server_1.0.1_2025-06-18_5tools_aws_multi-port`.
6. Aimap enhancement: add `cohort_signal_override: honeypot_fleet` field + fold `cohort-analysis.py` into the chain runner permanently.

---

## 2026-06-10 — Cat-BentoML (model serving, auth-off-by-default confirmed)

Stage -1 was done last session. Full pipeline run today.

### Population

- Shodan primary dork: `http.title:"BentoML Prediction Service"` = 68 hits, 65 IPs
- `ssl.cert.subject.cn:"*.bentoml.ai"` = 20 IPs (BentoCloud SaaS, separate cohort, omitted)
- Yatai dork: `http.title:"Yatai" port:8080` = 1 IP (51.83.76.253)
- Total cohort: 66 IPs, 54 live (82%), 26 confirmed BentoML

### Port distribution (Shodan sidebar)
port 3000/27, 80/22, 443/5, 3001/3, 5000/2

### Verdicts (Stage 3v)

| IP | Port | Service | Auth | Severity |
|---|---|---|---|---|
| 132.220.174.201 | 3000 | NestleModel:lj4jk4akzolo3nnv | NONE | HIGH |
| 57.153.31.12 | 3000 | NestleModel:lj4jk4akzolo3nnv | NONE | HIGH (twin) |
| 112.186.25.154 | 443 | FluxBaseService:dev | NONE | HIGH |
| 34.21.42.254 | 3000 | TwilioChatBot:dev | NONE | HIGH |
| 34.145.61.91 | 3000 | semantic_cache_service | NONE | MEDIUM |
| 87.106.198.114 | 3000 | rakuten_text_service | PARTIAL (docs open) | MEDIUM |
| 167.99.61.150 | 5000 | Docker Registry (aimsb-fintech-onboarding-ui) | NONE | MEDIUM |
| 51.83.76.253 | 8080 | Yatai frontend (API not exposed) | N/A | INFO |

All 26 BentoML /docs.json confirmed 200-with-data (no auth). Auth-off confirmed for the platform class.

### Headline findings

- **NestleModel** twin Azure deployment (same version hash on 2 hosts), unauth /predict, geo-prediction ML model
- **FluxBaseService:dev** Korea, FLUX image gen, /txt2img + /img2img unauth
- **TwilioChatBot:dev** Google Cloud, /chat/start_call (Twilio voice trigger) unauth
- **semantic_cache_service** /get_cache_data (LLM query cache), possible PII in prior query cache
- BARE: CVE-2025-27520 ranked #1 for 4/6 findings
- Corporate operators identified: Nestle, Rakuten, Twilio, AIMSB Fintech

### Tools run / updated

- aimap v1.9.54: BentoML FP upgraded (medium->high, port 8080, /healthz), Yatai FP added (critical), LMDeploy FP hardened (triple-anchor conjunctive)
- BARE: 6 findings ranked, CVE-2025-27520 dominant
- VisorLog: 7 findings ingested (#1-#7)
- tome: bentoml.json CANDIDATE -> CONFIRMED
- Commits: OSINT repo (1f0086a), aimap repo (f3062c2)
- Push blocked by auto-mode (explicit authorization needed)

### What's next

- `git push` on both repos (needs Nick's go)
- VisorGraph cert-pivot on NestleModel (132.220.174.201 + 57.153.31.12) — Azure cert CNs
- aimap-profile on TwilioChatBot + NestleModel (ethics classification)
- Deferred tools: VisorPlus, jaxen favicon, agent-logging-system, VisorCAS, VisorScuba, VisorCorpus
- Check semantic_cache /get_cache_data response schema (restraint: schema-only)
- BentoML aimap enumerator: add auth_status=none marker when /docs.json 200-with-data without Bearer
- FOFA/Quake pivot for BentoML hosts Shodan-dark


## 2026-06-10 — CAT-LMDEPLOY Lane D (jurisdiction + restraint, Insight #101 codified)

3-host LMDeploy cohort (`port:23333 http.html:"LMDeploy"` tome basic dork). 100% CN distribution across 3 disjoint major-carrier ASNs: Volcano Engine (ByteDance) / China Mobile CMNET / China Unicom Shanxi. Operator-class split (pre-Lane-C-verify): 1 commercial-cloud-tenant (`registry.mingya.com`), 1 enterprise-K8s (kube-apiserver banner), 1 hobby/lab (Unicom Shanxi ADSL pool — aimap-profile auto-tagged `education`, CFAA flag fires).

### Insight #101 codified (Candidate) — path-class taxonomy

LMDeploy's 23 documented paths partition cleanly into 4 safety classes: **DOC** (4) / **READ** (3) / **COMPUTE** (7) / **ADMIN** (9). Verify-scripts ask `class(path) in {DOC, READ}?` instead of pattern-matching URLs. Restraint moves from per-platform special-cases into tome's `path_classes` block — a single allowlist enforced at code level. Founding case n=1 platform, 23 paths. Promotion to confirmed requires 3 more inference-serving platforms (vLLM / SGLang / TGI / Triton / AIBrix). Path: `methodology/insight-101-per-platform-path-class-taxonomy-encodes-restraint-at-code.md`.

### Restraint posture (Lane D, DCWF 733)

- 0 calls to COMPUTE or ADMIN routes on any survey host
- 0 disclosures drafted, routed, or recommended (per `feedback-no-disclosure-recommendations`)
- All evidence preserved: aimap-profile JSON for 3 hosts, Lane C wire-shape MITM gate output (CLEAN, 5 distinct digests)
- 0 retractions/downgrades pre-orchestrator-reconciliation (Cat-Tabby 2026-06-09 discipline)

### Lane D artifacts under `shodan/cat-lmdeploy-2026-06-10/lane-d/`

| File | Purpose |
|---|---|
| `path-class-taxonomy.json` | 4-class partition of LMDeploy's 23 paths; Lane C verify-script allowlist source |
| `jurisdiction-map.json` | RDAP / ASN / carrier / country breakdown; 100% CN concentration |
| `classification-table.json` | per-host operator + sector + ethics-flag table (pre-verify) |
| `profile-{ip}.json` | aimap-profile fast-mode passive output for each of 3 IPs |

VisorLog: findings #404 / #405 / #406 ingested at info-tier, LMDEPLOY-CANDIDATE tagged. Final sector classification BLOCKED on Lane C verify — orchestrator reconciles all 4 lanes.

Session analysis: `analysis/2026-06-10-cat-lmdeploy-jurisdiction-and-restraint.md`.

---

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

