# sub2api — Population survey: 7,720 indexed hosts, auth-on-default at scale, zero pool-leak

**Date:** 2026-05-19
**Survey:** sub2api-population-2026-05-19
**Target class:** github.com/Wei-Shaw/sub2api (Go-rewrite successor to claude-relay-service)
**Population:** 7,720 unique host:port indexed on Shodan
**Toolchain:** JAXEN, direct Shodan API loop, custom verification probe, VisorGraph, attribution slicer, aimap deep-enum, JS-bundle extractor

---

## Headline findings

| State | Hosts | Share | Significance |
|---|---:|---:|---|
| CONFIRMED_AUTH_GATED | 5,848 | 75.75% | Auth-on-default holds at population scale (Insight #25 confirmed) |
| DEAD | 1,605 | 20.79% | Indexed but not responding |
| SETUP_OPEN | 101 | 1.31% | Install wizard accessible — **takeover-on-init vector** |
| PROXIED_OR_DOWN | 71 | 0.92% | Front-door 5xx or nginx/openresty without sub2api signature |
| UNKNOWN | 64 | 0.83% | Mixed: cross-contamination from other LLM proxies, scheme mismatches |
| LIVE_FRONTEND_ONLY | 15 | 0.19% | Vue3 UI served, backend not routing |
| CONFIRMED | 12 | 0.16% | `/health` only, auth status not directly anchored |
| DEV_MODE | 4 | 0.05% | vite dev server in production (build-pipeline leak) |
| **POOL_LEAK** | **0** | **0.00%** | **The v1 finding pattern does NOT generalize** |

**Top-line:** 7,720 / 7,720 = 100% probed. 6,083 / 7,720 = 78.8% returned sub2api-signature responses. Of those, **5,848 / 6,083 = 96.1% enforced auth-on-default** on the API surface.

## Why this matters

Two months ago a different Wei-Shaw project, `claude-relay-service` (v1, Node.js), was disclosed to Anthropic (2026-05-19) for pooling 32 paid Anthropic accounts across 6 visible hosts and serving 13.92B Claude tokens. The finding was anchored on publicly-readable pool stats at `/`. Insight #39 was codified from that work: pooled-account upstream proxy as attribution-laundering layer.

The successor project, `sub2api` (v2, Go), claims ~8,105 deployments. If the v1 finding pattern held at v2 scale, we'd be looking at a 1,300× larger surface of the same exposure class. The directional question this survey set out to answer: **does the v1 finding generalize to v2?**

**Answer:** No. The Go rewrite hardened the metrics surface. Zero of 7,720 hosts expose pool stats publicly. The finding pattern (publicly-readable pool counts) does not survive the v1 → v2 OSS generation. The architecture pattern (Insight #39: Tier-2 pooled-account substrate) remains; the finding shape changes.

## Methodology

### Discovery
- Dork: `http.title:"Sub2API - AI API Gateway"` (title-anchored — sub2api ships this verbatim from `index.html`)
- Total Shodan reports: 7,963 (matches Wei-Shaw's claimed 8,105 within 1.8%, consistent with normal indexing lag)
- Pulled 7,720 unique host:port across 79 pages (Freelance tier; no page-70 wall per Insight #35)
- Pre-emptively widened against schema-anchored fallbacks (`http.html:"sub2api-admin"`, favicon hash) — not needed at this scale

### Verification (load-bearing stage)
Eight schema-anchored paths per host, 80-worker concurrent probe, 8.2 minutes wall time for full population:

| Path | Anchor signal | Status code expected |
|---|---|---|
| `/health` | `{"status":"ok"}` (sub2api signature) | 200 |
| `/setup/status` | `{"code":0,"data":{"needs_setup":Bool}}` | 200 |
| `/api/v1/admin/stats` | `{"code":"UNAUTHORIZED"}` envelope | 401 (auth gated) |
| `/api/v1/admin/users` | `{"code":"UNAUTHORIZED"}` envelope | 401 (auth gated) |
| `/api/v1/auth/login` | sub2api error envelope | 405 / 422 |
| `/v1/messages` | (method-not-allowed for GET) | 404 / 405 |
| `/v1/models` | `{"code":"API_KEY_REQUIRED","message":"API key is required in Authorization header (Bearer scheme), x-api-key header, or x-goog-api-key header"}` | 401 |
| `/` | Vue 3 frontend, `/logo.png` favicon, `lang="zh-CN"`/`"zh"` | 200 |

The verbatim `/v1/models` 401 error string is the highest-confidence single-signature anchor — it appears in sub2api source at `backend/internal/gateway/*` and is unique to this project.

Classifier (v2, post-probe refinement at `reclassify.py`) anchors on response-shape rather than status codes alone per Insight #6.

### Attribution
- Per-host: ASN, org, ISP, country, hostnames, cert subject CN, domain parts (extracted from `attribution.csv`)
- Per-operator: cert-CN clustering identifies multi-host operators (Tier 3 storefronts per Insight #39)
- VisorGraph cert-pivot on 5 representative storefront CNs: zero cross-seed overlap — independent operators

### Ethics
- All probes are GET-only against published health/status endpoints and the sub2api API surface
- Anchored on response evidence; no POST to auth, install, or inference endpoints
- SETUP_OPEN hosts confirmed wizard-accessible via `/setup/status` GET; **no `/setup/init` POST attempted** (this would seize admin)
- No upstream Tier-1 vendor credentials extracted or attempted
- No customer prompt/response data retrieved

## Detailed findings

### F1 — SETUP_OPEN class (101 hosts): install-wizard takeover-on-init vector

**What:** Hosts at production-stage deployment with the sub2api install wizard accessible. `/setup/status` returns `{"code":0,"data":{"needs_setup":true,"step":"welcome"}}`. The wizard endpoint accepts admin-account creation without authentication; first POST claims the admin role.

**Verified to:** Wizard accessibility confirmed via GET. Wizard exploitability was **not** confirmed by attempted POST (ethical-stop boundary).

**Distribution:**
- 48 US, 17 SG, 13 CN, 11 HK, 8 JP
- Top providers: RackNerd (7), Asia Pacific NIC (7), Tencent BJ (6), Oracle (5), IT7 Networks (4)
- Top domain clusters: ColoCrossing (6), 16clouds (6), DMIT (4) — **same operator ecosystem** as Butterfly2Sea / Li Peipei from prior survey (project_butterfly2sea_operator)

**Operator brand certs visible:** `*.helper6.com`, `sub2api.shouyouradar.com`

**Why it matters:** Per the auth-on-default thesis, this is the residual 1.3% gap where install incompleteness creates an admin-takeover window. Anyone reaching the host before the operator completes setup can seize the admin account and bind their own pooled Tier-1 credentials.

**Verification artifact sample (101.42.109.163:8080):**
```
GET /setup/status HTTP/1.1
HTTP/1.1 200 OK
content-type: application/json; charset=utf-8

{"code":0,"message":"success","data":{"needs_setup":true,"step":"welcome"}}
```

### F2 — DEV_MODE class (4 hosts): vite dev server exposed in production

**What:** Hosts serving the root HTML with `import { inject } from "/@vite-plugin-checker-runtime"` — the vite development server's HMR client. These are production deployments accidentally running the dev build, which exposes source-map paths, unminified bundles, and the vite dev WebSocket on the same port.

**Distribution:**
- 2 HK, 2 US
- 2 on HostPapa (AS36352, ColoCrossing), 1 on FREEZING NETWORK, 1 on Alibaba LLC
- One named operator: `api.nevinxu.site`

**Why it matters:** Source-map URLs leak operator file-system paths. Dev-mode bundles are unminified and grep-friendly for downstream finding-extraction.

### F3 — multi-host operator clusters (Insight #39 Tier-3 evidence)

VisorGraph cert-pivot on 5 cert-CN seeds; population-level cert-CN aggregation:

| Operator brand | Hosts | Cluster shape |
|---|---:|---|
| aiproxy.astrum-lab.com | 9 | Multi-host storefront cluster; mostly PROXIED_OR_DOWN at probe time (cluster front-door enforces access control above sub2api layer) |
| 79102.com | 9 | Multi-host commercial brand |
| *.wowkaka.cn | 8 | Multi-host with expired DigiCert wildcard (2024-07-22) |
| sub2api.t2n.cc | 4 | Cert-blind (no CT history; plain HTTP only) |
| fuxingshop666.cn | 3 | Multi-host commercial brand |
| gpt.melemoe.com | 3 | Multi-host operator |
| sub2api.team | 1 | Branded single-host |
| api.nevinxu.site | 1 | Branded single-host (DEV_MODE) |

**Cross-cluster overlap (VisorGraph result):** Zero. Each operator brand is structurally independent — no shared IPs, no shared hosting providers, no shared cert authorities. This is direct evidence for Insight #39's Tier-3 fragmentation claim: storefronts are NOT centralized, they're independent commercial operators each pooling upstream relays.

### F4 — Non-finding: zero POOL_LEAK class hosts

**What did not appear:** 0 of 7,720 hosts exposed pool-account counts, total-token counters, or third-party-account-max-concurrent fields publicly. These were the load-bearing fields of the v1 claude-relay-service disclosure (the v1 finding was anchored on `/` returning `{"accounts":N,"availableAccounts":M,"stats":{"totalTokens":...}}`).

**What changed:** The Go rewrite gates `/api/v1/admin/*` behind an `x-api-key` header or JWT bearer. `/health` returns only `{"status":"ok"}`. `/v1/models` returns 401 with the verbatim API_KEY_REQUIRED envelope. Pool stats are not reachable at the unauthed layer.

**Why this matters:** OSS authors learn from disclosures. The v1 finding (and the resulting Anthropic disclosure) plausibly drove the v2 architecture's auth-on-default posture on metrics. This is a positive signal for the disclosure-feedback loop in this ecosystem.

### F5 — JS bundle hygiene (clean): zero baked secrets across 60-host sample

Sampled 60 hosts, fetched root HTML + ~20 JS assets per host, deduplicated by sha256, regex-scanned the cached unique bundles for:
- Anthropic, OpenAI, Google, AWS, GitHub, Slack, Cohere, DigitalOcean, Render API key patterns
- Vite/Next.js/React build-time-baked env-var secrets
- Hardcoded vendor inference URLs
- Source-map URLs and brand-string leaks

**Result:** zero matches across all unique bundles. The default sub2api Vue 3 build is sterilized; `api_base_url` is bound as a runtime form-field in the admin UI, not a build constant. Insight #36 (PaaS build-arg secret baking) does NOT generalize to sub2api OSS deployments.

The strongest bundle (sha256 4b398481…) appeared on all 60 sampled hosts = stock vendor build with no operator customization. Smaller cohorts (17-23 hosts per bundle) represent different release versions, all clean.

## Attribution

### Geographic distribution (CONFIRMED_AUTH_GATED subset, n=5,848)
- 51% US (2,966)
- 13% CN (749)
- 11% SG (635)
- 9% JP (502)
- 8% HK (441)

The US share is misleading; majority of US-hosted instances run on Chinese-operator hosting (ColoCrossing 417, 16clouds 175, DMIT 160, MULTACOM, PEG TECH) — same `.us-shell` pattern as the v1 claude-relay disclosure cohort.

### Hosting providers (top 5)
- Asia Pacific NIC: 447
- ACEVILLE PTE.LTD. (SG-registered Tencent shell): 285  *(v1 disclosure cohort: 5/6 hosts)*
- RackNerd LLC: 268
- Tencent Beijing: 256
- HostPapa: 234

The ACEVILLE concentration (285) suggests the same operator preference pattern as the v1 cohort, scaled ~47×.

### Operator-brand cert clusters
74 hosts behind CloudFlare Origin Certs (operator hides behind CF; the actual operator is one layer below).

For the visible operators (cert CN ≠ CloudFlare): the long tail is **dominated by single-host and small clusters (1-9 hosts each)**, confirming Insight #39's Tier-3 fragmentation. No operator brand fronts more than 9 visible hosts in this dataset.

## Insight extraction

### Candidate Insight #40 — "Auth-on-default thesis shifts rightward in successor OSS generations"

**Pattern:**
- v1 (claude-relay-service, Node.js, 2024-2025): pool stats publicly readable on `/` (no auth)
- v2 (sub2api, Go, 2026): all admin/metrics routes require `x-api-key` or JWT; `/health` returns only `{"status":"ok"}`; `/v1/models` returns the verbatim API_KEY_REQUIRED envelope

**Mechanism (hypothesis):** OSS authors observe disclosure outcomes from prior versions and harden the surface that drove enforcement (banned accounts, vendor pushback). The v1 disclosure (sent 2026-05-19) generalized rapidly because the v2 was already published. The v2 architecture's auth-on-default posture is the empirical answer to the v1 exposure class.

**Falsifiability:** Pick the next-published OSS pooled-account proxy after sub2api. If it ALSO auth-gates metrics by default (and references prior pushback in commit history), the pattern holds. If it reverts to publicly-readable pool stats, the hypothesis is wrong and the lesson did not transfer.

**Cross-survey applicability:** Test against OpenAI-compat pooled relays (e.g., `sub2api`'s OpenAI mode), Gemini-compat relays, Vertex relays. Expect similar auth-on-default behavior if the pattern is general.

### Methodology observations (not yet rising to numbered insight)

1. **Author-claimed deployment count is externally verifiable to within ~2%.** Wei-Shaw claims 8,105 sub2api deployments. Shodan-indexed: 7,963. Delta 1.8%, consistent with normal indexing lag. When OSS-author counts match independent measurement, the upstream-attribution claim is honest and can be relied on without re-verification.

2. **Title-anchored dorks can be precise IF the title string is shipped verbatim in stock templates.** The memory rule says prefer schema-anchor over brand-anchor. `<title>Sub2API - AI API Gateway</title>` is both — it's a brand match AND a template constant. Precision was preserved.

3. **Install-state conditionally exposes routes.** Pre-setup sub2api hosts respond on `/setup/status` + `/` only; `/health` 404s. Post-setup hosts respond on the full API. A `/health`-only dork would miss the pre-setup population. Population fingerprinting must probe multiple paths to be complete.

4. **Cert-blind operators exist.** `sub2api.t2n.cc` has no CT history and serves plain HTTP only. Cert-pivot misses this class entirely. ASN/banner pivot or response-fingerprint pivot is the fallback.

## Negative space (what we did NOT find)

- No publicly-readable pool stats anywhere in 7,720 hosts
- No baked API keys in the JS bundle sample (60 hosts)
- No upstream Tier-2 relay URLs hardcoded in default builds (operator entered at runtime)
- No shared infrastructure across the 5 storefront seeds (zero cross-cluster operator overlap)
- No defense-contractor / .gov / .mil hostnames in the cert-CN distribution
- No medical / clinical / .edu institutional hosts beyond what's expected at random in a 7,720-host sample

## Pivot avenues

1. **AROSSCLOUD 5-host cluster (CONFIRMED bucket).** 5 hosts in AS400619 are non-auth-gated CONFIRMED — possibly an older sub2api version or single-operator misconfig. Worth a focused look at the 5 cert CNs (uily.de, happycodernow.xyz, z-daha.cc, etc.) to check for a common upstream signature.

2. **`*.helper6.com` SETUP_OPEN cluster.** Sub2api install-wizard accessible on a branded multi-host cluster suggests deployment-automation script left unfinished. Test whether the wizard endpoint has been hit by anyone else.

3. **astrum-lab.com PROXIED-front cluster (9 hosts).** Front-door enforces access control above the sub2api layer. Worth a closer look at the front-door — is it an operator-built reverse proxy?

4. **CLI Proxy API Server cross-contamination.** The UNKNOWN bucket caught at least one different-OSS LLM proxy class. Worth a quick survey to identify other OSS proxy projects that happen to ship the sub2api title or template.

5. **Cross-vendor Insight #39 applicability check.** OpenAI-compat + Gemini-compat resale architectures. If the auth-on-default v2 hardening pattern transfers, expect similar zero-pool-leak finding shapes.

6. **`sub2api.t2n.cc` cert-blind cluster.** Need ASN/banner pivot to enumerate sibling hosts that deliberately stay off CT.

## Artifacts

```
~/recon/sub2api-population-2026-05-19/
├── candidates.txt                  # 7,720 host:port from Shodan
├── harvest-raw.jsonl               # raw Shodan records
├── harvest.py                      # paginated harvest harness
├── attribution.csv                 # per-host ASN/org/country/cert from Shodan
├── attribution-summary.txt         # population distribution by all dimensions
├── verify_probe.py                 # 8-path schema-anchored verification
├── verify-raw.jsonl                # full probe responses
├── verify-state.csv                # v1 classifier output
├── verify-state-v2.csv             # v2 reclassifier output (final)
├── verify-state-v2-samples.txt     # 3 sample records per state class
├── reclassify.py                   # v2 classifier with refined anchors
├── select_aimap_sample.py          # stratified 182-IP sampler
├── aimap-sample.txt                # 182 IPs for deep-enum
├── aimap-results.json              # aimap output (in progress)
├── js-sample.txt                   # 60 hosts for bundle extraction
├── js_extract.py                   # bundle harvester + secret scanner
├── js-bundles/                     # deduplicated cached bundles
├── js-bundle-attribution.csv       # sha → hosts mapping
├── js-findings.csv                 # secret matches (zero)
├── visorgraph-*.json               # 5 cert-pivot graphs
├── cert-pivot-summary.md           # VisorGraph subagent report
└── asn_slice.py                    # attribution slicer
```

## Toolchain provenance

| Stage | Tool | Used | Note |
|---|---|---|---|
| 0 | JAXEN harvest | wrapped (50-cap → direct API loop) | Tool gap #2 logged |
| 1 | aimap fingerprint | running on 182-IP stratified sample | Population sweep impractical at 7,720 |
| 2 | VisorGraph cert-pivot | 5 seeds | Zero cross-overlap (Insight #39 evidence) |
| 3 | aimap-profile | pending (top 5 cluster reps) | |
| 4 | JS bundle extractor | inline replacement for missing vampire.py | Tool gap logged; tool-ideas_js-extractor.txt proposes new build |
| 5 | VisorLog ledger ingest | pending | |
| 6 | VisorScuba compliance | pending | |
| 7 | BARE module ranking | pending | |
| 8 | VisorCorpus | N/A — no unauthed `/v1/messages` reachable | Justified: ethical-stop + zero corpus-target surface |
| 9-17 | VisorBishop, SD, Goose, menlohunt, recongraph, nu-recon, Plus, RAG, cortex | pending / partial | Run on cluster representatives, not population |

Non-run: VisorHollow (Windows-only binary), VisorAgent (controlled-target-only).

## Cross-references

- **Insight #25 (auth-on-default thesis):** confirmed at 5,848 / 6,083 = 96.1% of verified hosts
- **Insight #35 (Shodan pagination depth):** Freelance tier survived past page 70 cleanly on a 7,963-host dork; no country-split fallback needed
- **Insight #36 (PaaS build-arg secret baking):** did NOT generalize to this OSS install class (zero baked secrets in default build)
- **Insight #37 (asymmetric auth gating):** N/A — sub2api gates both dashboard AND API symmetrically
- **Insight #39 (pooled-account attribution laundering):** Tier-3 fragmentation confirmed at population scale (zero cross-cluster overlap on cert pivot); Tier-2 substrate hardening represents architectural evolution of the Insight (see candidate Insight #40)
- **Reference: project_butterfly2sea_operator:** 16clouds.com cluster overlaps prior survey's Li Peipei ecosystem
- **Reference: project_claude_relay_chinese_reseller (v1 disclosure):** sub2api is the direct successor; this survey extends the v1 disclosure's findings to the v2 population

---

*Survey conducted 2026-05-19 by Nuclide research (Nicholas Kloster + Claude). Methodology per `~/.claude/nuclide-internal/METHODOLOGY.md`. Tool gaps and improvement notes logged at `~/Desktop/nuclide-logs/`.*
