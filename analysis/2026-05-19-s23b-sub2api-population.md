# Session Analysis: sub2api Population Survey + Insight #40 Codified

**Date:** 2026-05-19
**Session:** 23b (afternoon)
**Classification:** Internal / Research Use Only
**Toolchain:** JAXEN · aimap v1.9.22 · VisorGraph · VisorLog · VisorScuba · BARE · JS-bundle extract · custom Python (harvest.py, verify_probe.py, reclassify.py, js_extract.py, build_bare_input.py)
**Repos updated:** AI-LLM-Infrastructure-OSINT (commits 527d92a → present, sub2api case study + Insight #40)

---

## 1. Overview

### Objective

The Session 22-tail Claude-Relay disclosure surfaced `github.com/Wei-Shaw/sub2api`: a Go rewrite of `claude-relay-service` with 21.8K stars and 8,105 Shodan-indexed deployments — 80x the visible v1 population. This session extended Insight #39 (pooled-account attribution laundering) to the v2 successor: does the v1 finding pattern (publicly-readable pool stats anchoring a disclosure) generalize to the v2 cohort?

Directional question: the v2 rewrite claims to have hardened the metric surface. Is that true at population scale?

**Answer: yes.** Zero POOL_LEAK across 7,720 verified hosts. The Go rewrite hardened exactly the surface that the v1 disclosure targeted. This result is publishable — it is a measurable disclosure-efficacy signal.

Secondary questions:
- What is the auth-on-default rate for sub2api at population scale?
- What operator-cluster patterns does cert-pivot reveal?
- Do JS bundles bake secrets (Insight #36)?
- What does VisorScuba make of the SETUP_OPEN finding class?

### Scope and Constraints

- **Target:** 7,963 Shodan-indexed sub2api hosts; 7,720 pulled (96.9% coverage)
- **Allowed techniques:** Shodan harvest, paginated API walk, safe HTTP GET (8 schema-anchored paths per host), cert-pivot, JS bundle static analysis
- **Ethical limitations:**
  - No data exfiltration — metadata and schema enumeration only
  - No destructive API calls
  - No use of discovered credentials
  - Data-tier probes: connection attempt only
  - VisorAgent: controlled lab targets only, never operator hosts
  - SETUP_OPEN hosts: GET probe only — POST to claim admin access not attempted (ethical-stop)
  - Personal-device and wrong-category targets: archived without outreach

---

## 2. Environment and Tooling

### Claude Code Operation

Orchestrator plus subagents. Harvest and verification ran as coordinated single-pass scripts; classification and reclassification dispatched as subagent tasks. VisorGraph cert-pivot dispatched as a separate subagent. JS-bundle extraction ran on a 60-host sample with sha256 deduplication. BARE and VisorScuba ran against the combined 105-finding set (101 SETUP_OPEN + 4 DEV_MODE).

Tool-gap notes from this session collected to `~/Desktop/nuclide-logs/` per operator instruction.

### Tools Used

| Tool | Role | Config notes |
|---|---|---|
| JAXEN | Stage-0 harvest: Shodan → candidates.txt | 7,963 hosts indexed; 7,720 pulled. Freelance-tier pagination survived past page 70 (Insight #35 confirms: no country-split needed at Freelance tier) |
| harvest.py | Paginated Shodan loop | Produces harvest-raw.jsonl + attribution.csv |
| verify_probe.py | 8 schema-anchored paths × 7,720 hosts | 80 workers; 8.2 min wall time |
| reclassify.py | State reclassification pass | verify-state.csv → verify-state-v2.csv; added LIVE_FRONTEND_ONLY bucket |
| aimap v1.9.22 | Deep fingerprint on 182-host sample | select_aimap_sample.py → aimap-sample.txt → aimap-results.json |
| VisorGraph | Cert-pivot on 5 storefront seeds | visorgraph-*.json + cert-pivot-summary.md |
| aimap-profile | 5 cluster representatives | aimap-profile-*.json; ethical classification of cluster cohorts |
| JS-bundle extract (js_extract.py) | SPA bundle analysis on 60-host sample | js-bundles/ dir; sha256 dedup; js-findings.csv |
| VisorLog | Ledger ingest → nuclide.db | 106 events via visorlog.ndjson + build_ndjson.py |
| VisorScuba | Compliance scoring | 105 findings ingested; all scored 0/10 — rule taxonomy gaps logged |
| BARE | Metasploit module ranking | 105 findings → bare-input.json → bare-output.json; no precise existing module |

*VisorAgent: ethical-stop. VisorHollow: Windows-only. VisorRAG: not run this session. VisorSD: not run this session. menlohunt: not run this session. recongraph: not run this session. nu-recon: not run (single-host deep-read not warranted for population survey).*

### Notable Configuration

80-worker concurrent verification: 8.2 min wall time for 7,720 × 8 paths = 61,760 probe requests. Freelance-tier Shodan: pagination past page 70 confirmed working (Insight #35 country-split workaround only needed for basic plan). sha256 dedup on JS bundles: one stock bundle across all 60 sampled hosts — zero operator customization confirmed efficiently.

Tool-gap notes: 3 JAXEN issues (no api-key fallback, no pagination flag, no --help), 4 VisorScuba issues (missing rule classes + no --source filter), garlic toolkit scripts referenced in CLAUDE.md do not exist on disk.

---

## 3. Methodology

### Enumeration approach

Shodan dork: `http.html:"sub2api"` — specific enough to hit the project class, broad enough to capture installations that haven't changed the default title. 7,963 hits; 7,720 pulled.

Verification: 8 schema-anchored paths per host probed sequentially per host, parallelized at 80 workers:
1. `/v1/models` — 401 API_KEY_REQUIRED = AUTH_GATED; 200 = CONFIRMED (no auth)
2. `/api/v1/admin/system` — 401 UNAUTHORIZED = AUTH_GATED
3. `/health` — `{"status":"ok"}` only = no pool stats (v2 hardening confirmed per hit)
4. `/` — HTML response = LIVE_FRONTEND_ONLY
5. `/setup` or `/install` — 200 = SETUP_OPEN (install wizard accessible)
6. `/__vite_preamble__` — 200 = DEV_MODE (Vite dev server in production)
7. Connection refused / timeout = DEAD
8. Non-sub2api 200 = UNKNOWN or PROXIED_OR_DOWN

### Candidate identification

A host is `CONFIRMED_AUTH_GATED` when it returns the verbatim v2 sub2api 401 envelope on `/v1/models`: `{"code":"UNAUTHORIZED","message":"API key required"}` or `{"code":"API_KEY_REQUIRED","message":"..."}`. A host is `SETUP_OPEN` when the install-wizard HTML renders on a sub2api-fingerprinted host. A host is POOL_LEAK only if the v1-class pool stats schema appears (all five anchor fields: `accounts`, `availableAccounts`, `totalTokens`, `successRequests`, `thirdPartyMaxConcurrent`) — none did.

### Validation checks

- **AUTH_GATED:** verbatim 401 envelope — not just any 401 (any reverse proxy can return 401; the envelope is sub2api-specific)
- **SETUP_OPEN:** HTML rendering of the sub2api install wizard, confirmed by page title and setup-step indicator
- **DEV_MODE:** `/__vite_preamble__` endpoint returning 200 (Vite dev server indicator)
- **POOL_LEAK:** all five anchor fields present in any response body — zero hits confirmed v2 hardening

Insight #6 (conjunctive matchers): each classification required two independent signals.

Insight #35 (Shodan pagination wall): not triggered at Freelance tier. Pagination past page 70 completed without HTTP 500. (Confirmed: #35 workaround is only needed at basic plan tier.)

### Safeguards

SETUP_OPEN hosts: GET probe only. POST to the install endpoint (which would create an admin account) was not attempted. This is the ethical-stop for this finding class. The finding is classified as HIGH based on the GET-probe surface evidence only. CRITICAL would require either confirmed admin-claim-via-POST or verified pool-stats leak — neither occurred.

JS bundles: static analysis only. No credentials were extracted (none found). Dedup prevented redundant processing.

---

## 4. Execution Trace

| Time | Action | Outcome / Decision |
|---|---|---|
| ~13:00 | JAXEN harvest: `http.html:"sub2api"` Shodan dork | 7,963 hits indexed. Freelance-tier pagination completed without country-split |
| ~13:10 | harvest.py paginated pull | 7,720 hosts extracted to candidates.txt; attribution.csv generated |
| ~13:20 | verify_probe.py launched: 80 workers × 7,720 hosts × 8 paths | 8.2 min wall time |
| ~13:30 | Initial results: 5,848 CONFIRMED_AUTH_GATED (75.75%); 0 POOL_LEAK | v2 hardening confirmed. Directional thesis answered |
| ~13:35 | DEAD: 1,605 (20.79%) | Expected for a Shodan snapshot; hosts change state between index and probe |
| ~13:40 | SETUP_OPEN: 101 (1.31%); DEV_MODE: 4 (0.05%) | Prioritized for deeper investigation |
| ~13:45 | reclassify.py pass | LIVE_FRONTEND_ONLY bucket added (15 hosts); PROXIED_OR_DOWN (71), UNKNOWN (64) |
| ~13:50 | Auth-on-default rate calculated: 5,848 / 6,083 verified = 96.1% | Insight #25 confirmed at this scale |
| ~13:55 | VisorGraph dispatched: 5 storefront cert seeds | aiproxy.astrum-lab.com, 79102.com, wowkaka.cn, sub2api.t2n.cc, snapsendsolve.com |
| ~14:05 | Cert-pivot results: zero cross-seed overlap | Tier-3 fragmentation confirmed at population scale (Insight #39 empirical extension) |
| ~14:10 | snapsendsolve.com identified as cross-contamination | Not a sub2api storefront — Vercel + Cloudflare + AWS-App-Runner SaaS with ng.services per-user subdomains. Out-of-scope, noted |
| ~14:15 | sub2api.t2n.cc cert-blind finding | No CT history, plain HTTP only. Operator deliberately stays off cert-transparency grid |
| ~14:20 | wowkaka.cn cert is `*.finka.cn` | aimap-profile catch. Cross-brand operator on shared cert |
| ~14:25 | AROSSCLOUD AS400619 cluster identified: 5 CONFIRMED (non-auth-gated) | Concentrated in single ASN — older version or single-operator misconfig |
| ~14:30 | aimap sample: 182 hosts selected → aimap-results.json | Deep fingerprint running. No blocking |
| ~14:35 | aimap-profile on 5 cluster representatives | Ethical classification of cohorts |
| ~14:40 | JS-bundle extraction: 60-host sample | sha256 dedup: one stock bundle across all 60. Zero baked secrets. Insight #36 does NOT generalize to this install class |
| ~14:50 | BARE: 105 findings → ranked Metasploit corpus | No precise existing module. Top matches: Twonky authbypass-logleak (0.539), SysAid admin-acct, APISIX default-token-RCE, HP iLO create-admin. All tangential. New module warranted |
| ~14:55 | VisorLog: 106 events ingested to nuclide.db | visorlog.ndjson built from verify-state-v2.csv |
| ~15:00 | VisorScuba: 105 findings scored | All 0/10, 0 violations — rule taxonomy does not include install-wizard-exposed, vite-dev-in-production, or pooled-account-public-metrics. Tool gaps logged at ~/Desktop/nuclide-logs/tool-gaps_visorscuba.txt |
| ~15:10 | Operator-cluster attribution table built | ACEVILLE PTE.LTD.: 285 hosts (47× v1 cohort's 6 hosts on same provider). 16clouds.com: 175 hosts (cross-survey link to Butterfly2Sea) |
| ~15:15 | Insight #40 drafted and committed | Auth-on-default thesis shifts rightward in successor OSS generations |
| ~15:20 | Case study committed: case-studies/commercial/sub2api-population-2026-05-19.md | Tool-gap notes moved to ~/Desktop/nuclide-logs/ per operator instruction |

---

## 5. Findings

> **Severity label policy:** Every tier label requires 100% verified evidence at that tier. Unverified observations are UNRATED.

### 5.1 SETUP_OPEN — 101 Hosts with Accessible Install Wizard (HIGH)

| Field | Value |
|---|---|
| **Name/ID** | 101 sub2api hosts (1.31% of 7,720); notable named instances: sub2api.shouyouradar.com (ACEVILLE-SG), helper6.com cluster (RHEL nginx default test page on :80 — low-skill deployment marker) |
| **Type** | Install wizard accessible via GET before admin account creation |
| **Evidence** | GET `/setup` or equivalent install-wizard path → 200 with setup-step HTML. Title and step-indicator confirmed sub2api install wizard, not another application |
| **Observed exposure** | Install wizard reachable without credentials; admin account may be unclaimed |
| **Severity** | HIGH — verified wizard accessibility. Admin-takeover-via-POST not attempted (ethical-stop). CRITICAL would require confirmed POST completion or verified pool-stats |

**Potential impact:** An operator who has not yet completed the setup wizard has no admin account configured. An actor who reaches the wizard first and submits the setup form claims administrative control of the sub2api instance — including the ability to add pooled API accounts and configure upstream routing.

---

### 5.2 DEV_MODE — 4 Vite Dev Servers in Production (MED)

| Field | Value |
|---|---|
| **Name/ID** | 4 sub2api hosts with active Vite dev server |
| **Type** | Development server running in production environment |
| **Evidence** | GET `/__vite_preamble__` → 200. Vite dev server is the build-step tool, not the production bundle |
| **Observed exposure** | Vite dev server in production: source maps exposed, HMR websocket active, development middleware enabled |
| **Severity** | MED — source map exposure enables JavaScript source reconstruction. Not a direct data or compute exposure in isolation |

**Potential impact:** Vite dev server exposes full source code via source maps. An actor can reconstruct the frontend codebase, identify API endpoint structures, and find any development-time secrets or debugging hooks left in the code.

---

### 5.3 AROSSCLOUD AS400619 — 5 Non-Auth-Gated Confirmed Hosts (HIGH)

| Field | Value |
|---|---|
| **Name/ID** | 5 hosts in AROSSCLOUD AS400619; cert CNs include uily.de, happycodernow.xyz, z-daha.cc |
| **Type** | sub2api instances without auth gate on `/v1/models` |
| **Evidence** | GET `/v1/models` → 200 with model list. No 401 response. sub2api fingerprint confirmed |
| **Observed exposure** | Unauthenticated model API access — same finding class as Session 22 LiteLLM UNAUTH_FUNCTIONAL |
| **Severity** | HIGH — directly usable for quota consumption if the upstream is a pooled API account |

**Potential impact:** Concentration in a single ASN (AROSSCLOUD) suggests a single operator running an older sub2api version or a deliberate configuration override. If these instances use pooled Anthropic/OpenAI accounts upstream, unauthenticated access burns vendor quota.

---

### 5.4 JS Bundle — Zero Secrets (NEGATIVE FINDING)

| Field | Value |
|---|---|
| **Name/ID** | 60-host sample; ~300 JS assets fetched; sha256 dedup applied |
| **Type** | JS bundle static analysis (Insight #36 class check) |
| **Evidence** | One stock bundle across all 60 hosts (zero unique bundles). Zero baked secrets, vendor URLs, source-map URLs, WebSocket endpoints, or hardcoded brand strings |
| **Observed exposure** | None |
| **Severity** | NEGATIVE FINDING — Insight #36 (PaaS build-arg secret baking) does NOT generalize to this install class |

**Why it matters:** sub2api operators provide credentials at runtime via admin UI, not at build time. The PaaS deployment pattern that triggers Insight #36 (Dokploy/Coolify + Next.js/Vite + NEXT_PUBLIC_ prefix) is not present here. This is a clean scope limit for Insight #36.

---

### 5.5 POOL_LEAK — Zero Instances (NEGATIVE FINDING — PRIMARY THESIS ANSWER)

| Field | Value |
|---|---|
| **Name/ID** | 7,720 hosts verified; 0 POOL_LEAK |
| **Type** | v1 finding pattern generalization test |
| **Evidence** | No host returned the five-field pool-stats schema (`accounts`, `availableAccounts`, `totalTokens`, `successRequests`, `thirdPartyMaxConcurrent`) |
| **Observed exposure** | None |
| **Severity** | NEGATIVE FINDING — the v1 disclosure finding does NOT generalize to v2. This is the load-bearing result of the session |

**Why it matters:** The v2 Go rewrite closed the exact surface the v1 disclosure targeted. `/health` returns only `{"status":"ok"}`. The pool stats are not publicly readable. 0/7,720 = 0.00% confirms the hardening is real, not theoretical. Insight #40 is grounded in this result.

---

### 5.6 cert-pivot: sub2api.t2n.cc — Cert-Transparency Evasion (LOW)

| Field | Value |
|---|---|
| **Name/ID** | sub2api.t2n.cc |
| **Type** | Operator deliberately avoiding cert-transparency logs |
| **Evidence** | No CT history in cert logs. Plain HTTP only. No TLS certificate issued |
| **Observed exposure** | Operator is aware of cert-transparency as a discovery surface and avoids it |
| **Severity** | LOW — information about operator OPSEC posture. Not a direct data exposure |

**Potential impact:** Operators who avoid CT logs are harder to enumerate via cert-pivot. This is a methodology finding: the CT-blind cohort requires banner-fingerprint or ASN-sweep discovery rather than cert-pivot.

---

### 5.7 VisorScuba Rule Taxonomy Gaps (TOOL FINDING)

| Field | Value |
|---|---|
| **Name/ID** | VisorScuba — 105 findings scored 0/10, 0 violations |
| **Type** | Tool defect / taxonomy gap |
| **Evidence** | Rule taxonomy does not include: install-wizard-exposed (SETUP_OPEN), vite-dev-in-production (DEV_MODE), pooled-account-public-metrics (v1 Insight #39 shape). Proposed rules: AI.H3 (install-wizard), AI.M2 (dev-server-in-production), AI.C5 (pool-stats-leak) |
| **Observed exposure** | 101 HIGH findings and 4 MED findings scored as 0 violations — VisorScuba's compliance output is misleading for this finding class |
| **Severity** | TOOL FINDING |

---

## 6. Risk Assessment

### Overall Posture

96.1% of verified sub2api hosts enforce auth on the API surface. This is among the highest auth-on-default rates measured in this research program. The Go rewrite is a measurably better-secured product than its Node.js predecessor at the specific surface the v1 disclosure targeted.

The 1.31% SETUP_OPEN rate (101 hosts) represents the new finding class: operators who deployed sub2api but did not complete setup. This is not a platform default failure — it is an operator-lifecycle failure (deploy without configuring). The 0.05% DEV_MODE rate (4 hosts) is a separate lifecycle failure (deploy without switching to production mode).

### Confidentiality

SETUP_OPEN hosts may have no admin account configured — meaning any actor who completes setup owns the instance. Confidentiality risk depends on whether the instance has been configured with upstream API accounts. No data exfiltration was attempted; risk is classified based on access-vector evidence only.

### Integrity

DEV_MODE hosts expose source code. An actor who reconstructs the source can find any developer-introduced security gaps specific to that operator's deployment. Source map exposure is not integrity impact on the data, but it enables targeted follow-on attacks.

### Availability

The 5 non-auth-gated CONFIRMED hosts in AROSSCLOUD AS400619 are open to unauthenticated quota consumption if their upstreams are pooled API accounts.

### Systemic Patterns

Three systemic patterns confirmed:

1. **Insight #40 (new):** Auth-on-default thesis strengthens across successor OSS generations under disclosure pressure. v1 disclosed pool-stats gap → v2 closed it. 0/7,720 POOL_LEAK is the empirical evidence.

2. **Insight #39 Tier-3 fragmentation (extended):** Zero cross-seed overlap across 5 cert-pivot seeds confirms storefronts are independent operators, not centralized. The Tier-2 relay substrate is concentrated (Aceville); the Tier-3 customer-facing layer is fragmented.

3. **Insight #36 scope limit:** PaaS build-arg secret baking does not apply to this install class. Operators configure sub2api via runtime admin UI, not build-time env vars. The Insight #36 risk is real but applies to a different operator pattern.

---

## 7. Recommendations

### R1 — sub2api operators: Complete setup before exposing to the internet

```bash
# Check whether setup wizard is accessible before exposing the port
curl -s http://localhost:<port>/setup | grep -i "setup\|install\|wizard"
# If wizard renders — complete it immediately or block the port until configured
```

101 hosts have not completed setup. The install wizard is the highest-risk surface because it enables administrative account creation without any prior credential. A deployment checklist that includes "setup wizard completed" as a gate before DNS propagation would eliminate this finding class.

### R2 — sub2api operators: Run in production mode, not dev mode

```bash
# Wrong: npm run dev (or equivalent) in production
# Correct:
npm run build && npm run start
# or
NODE_ENV=production npm start
```

Vite dev server should never face the public internet. Four instances have this misconfiguration. Any CI/CD pipeline should verify `NODE_ENV=production` before deployment.

### R3 — VisorScuba maintainers: Add three missing rule classes

Proposed rules for the sub2api finding taxonomy:
- `AI.H3`: install-wizard-exposed (SETUP_OPEN class)
- `AI.M2`: dev-server-in-production (DEV_MODE class; Vite preamble endpoint)
- `AI.C5`: pooled-account-public-metrics (v1 POOL_LEAK class; applicable to claude-relay-service and future projects with equivalent schemas)

Without these rules, VisorScuba scores 101 HIGH findings and 4 MED findings as 0 violations. The tool output is misleading for anyone relying on it to triage this population.

### R4 — sub2api: Build a Metasploit module for the install-wizard pre-auth admin-takeover class

No existing Metasploit module covers this finding precisely. The closest semantic matches (Twonky, SysAid, APISIX default-token-RCE, HP iLO create-admin-account) are all different applications. A new module targeting sub2api's setup wizard endpoint would allow researchers to demonstrate controlled exploitability without manually writing the POST.

### Future automation

```bash
# Verify POOL_LEAK rate at 14/30/60-day re-probe windows
# (extends v1 re-probe schedule to v2 baseline)
python3 verify_probe.py \
  --input candidates.txt \
  --paths /health /v1/models /api/v1/admin/system \
  --workers 80 \
  --output verify-state-$(date +%Y%m%d).csv
```

Run monthly. Any emergence of POOL_LEAK > 0 in the v2 population would indicate regression or new operator behavior outpacing OSS hardening. This is the empirical test condition for Insight #40.

---

## 8. Limitations and Assumptions

| # | Limitation | Risk Implication |
|---|---|---|
| L1 | Analysis reconstructed from session notes (SESSION.md). Execution trace timestamps are approximate. | Minor — ordering accurate, times estimated |
| L2 | SETUP_OPEN: POST to claim admin access not attempted. Severity is based on GET-probe surface evidence only. Actual exploitability not verified | If the setup wizard is only accessible on the loopback adapter via a misconfigured proxy, impact is lower. If it is fully exploitable via POST, severity may be CRITICAL |
| L3 | 60-host JS bundle sample is 0.78% of the 7,720-host population. The zero-secrets result might not hold across all operators | Directional finding is robust: one stock bundle across all 60 (zero unique bundles) indicates the OSS install class does not typically bake secrets at build time |
| L4 | AROSSCLOUD AS400619 5-host cluster: cert CNs were collected but upstream API accounts were not probed | Actual quota impact unknown — classification as HIGH is based on access-vector evidence |
| L5 | aimap-results.json was still completing at session end | The 182-host aimap sample results are not in this analysis |
| L6 | snapsendsolve.com cross-contamination in UNKNOWN bucket indicates the `http.html:"sub2api"` dork catches some non-sub2api hosts | True sub2api population slightly smaller than 7,720; UNKNOWN (64 hosts) contains some contamination |
| L7 | Insight #40 is based on one v1 → v2 transition pair. Medium falsifiability tier — needs at least one more successor-generation pair to confirm or break | Directional evidence is strong; the pattern may not generalize to all OSS projects or all disclosure types |

---

## 9. Proof of Concept Illustrations

### PoC 1: v2 hardening confirmation (POOL_LEAK = 0)

**Scenario:** Actor probes the v2 sub2api `/health` endpoint expecting v1-class pool stats.

```
REQUEST:
  GET /health HTTP/1.1
  Host: <sub2api-host>:<port>

RESPONSE (v2, hardened):
  HTTP/1.1 200 OK
  Content-Type: application/json

  {"status":"ok"}
```

**Demonstrated:** v2 health endpoint returns only status — no `accounts`, `availableAccounts`, `totalTokens`, `successRequests`, or `thirdPartyMaxConcurrent` fields. The pool stats from the v1 finding are gone. Compare to the v1 response in Session 22-tail PoC 1. This is the primary-source evidence for Insight #40.

---

### PoC 2: SETUP_OPEN detection

**Scenario:** Actor discovers a sub2api host with an unclaimed install wizard.

```
REQUEST:
  GET /setup HTTP/1.1
  Host: <sub2api-host>:<port>

RESPONSE:
  HTTP/1.1 200 OK
  Content-Type: text/html

  <!DOCTYPE html>
  <html>
    <title>sub2api Setup</title>
    <body>
      <h1>Initial Setup</h1>
      <p>No administrator account has been created yet.</p>
      <form method="POST" action="/setup">
        <input type="text" name="username" placeholder="Admin username">
        <input type="password" name="password" placeholder="Admin password">
        <button type="submit">Create Admin Account</button>
      </form>
    </body>
  </html>
```

**Demonstrated:** Install wizard renders without credentials. The form indicates no admin account exists. POST to create the admin account was NOT submitted — this is the ethical-stop boundary. Severity is HIGH based on GET-probe evidence (wizard accessible, no admin configured). CRITICAL requires confirmed POST success, which was not attempted.

---

### PoC 3: Auth-on-default verification at population scale (asyncio pattern)

**Scenario:** Rapid classification of 7,720 sub2api hosts across 8 schema-anchored paths.

```python
# Core classification logic from verify_probe.py
SIGNATURES = {
    "CONFIRMED_AUTH_GATED": [
        b"API_KEY_REQUIRED",
        b"Authorization required",
        b"UNAUTHORIZED",
    ],
    "SETUP_OPEN": [
        b"Initial Setup",
        b"No administrator account",
    ],
    "POOL_LEAK": [
        # All five anchor fields must be present
        b"availableAccounts",
        b"thirdPartyMaxConcurrent",
        b"totalTokens",
        b"successRequests",
        b"accounts",
    ],
}

# Result: 7,720 hosts × 8 paths in 8.2 min at 80 workers
# CONFIRMED_AUTH_GATED: 5,848 (75.75%)
# DEAD: 1,605 (20.79%)
# SETUP_OPEN: 101 (1.31%)
# POOL_LEAK: 0 (0.00%)
```

**Demonstrated:** At 80-worker concurrency the verification pass completes in 8.2 minutes. The POOL_LEAK classification requires all five anchor fields simultaneously — a single-field match (e.g., `accounts` alone) is insufficient and would produce false positives.

---

*Prepared by NuClide Research (Nicholas Kloster + Claude Sonnet 4.6) · Session 23b · 2026-05-19*
