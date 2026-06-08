# Session Analysis: Substrate Marathon + glance Build

**Date:** 2026-06-08
**Session:** (date-only)
**Classification:** Internal / Research Use Only
**Toolchain:** glance v0.1.1, constellation v0.1.0, verify_chroma_campaign.py, verify_chroma_version.py, verify_vm_unauth.py, verify_prom_unauth.py, verify_agentmem.py, aimap v1.9.x, visorplus, visorgraph, visorlog, visorscuba, BARE, tome, syllabus, scanner, Shodan API (Freelance tier, user-authorized this session), MCP Playwright
**Repos updated:** nuclide-research/AI-LLM-Infrastructure-OSINT (be62a07), nuclide-research/glance (7c8a1f7)

---

## 1. Overview

### Objective

Four-survey marathon across the substrate-monitoring tier and the emerging agent-memory tier. Test whether the auth-off-default thesis generalizes from established categories to substrate AND to brand-new categories. Build the schema-only sensitivity analyzer the program had been wanting. Codify cross-corpus operator detection as methodology.

### Scope and Constraints

- **Target classes:** ChromaDB (Cat-02 follow-on), VictoriaMetrics (Cat-46c, new), Prometheus (Cat-46d, new falsifier), Agent Memory Layer (Cat-47, new — Mem0/Letta/Zep/Cognee).
- **Allowed techniques:** Shodan API harvest (user-authorized), passive banner grab, safe HTTP GET, schema-only analysis on sealed corpora.
- **Ethical limitations:**
  - No data exfiltration. Metadata and schema enumeration only.
  - No destructive API calls.
  - No use of discovered credentials. 25 Prometheus hosts leaked plaintext basic_auth in `/api/v1/status/config`. Counted, never extracted, never used.
  - Data-tier probes: connection attempt only. Auth gate check only. No queries.
  - VisorAgent: not run. No controlled lab targets engaged this session.
  - Personal-device and wrong-category targets: archived without outreach (Sogei DataPower FP withdrawn; davidtcox.com letta HTML FP withdrawn).

---

## 2. Environment and Tooling

### Claude Code Operation

Orchestrator (Opus 4.7) + DCWF role subagents dispatched in parallel for two panel audits. Eight panel reports produced across four DCWF AI work roles (672 T&E, 733 Risk & Ethics, 753 AI/ML, 902 Innovation Leader). Each panel ran four agents concurrently on non-overlapping data slices.

### Tools Used

| Tool | Role | Config notes |
|---|---|---|
| Shodan API | Stage-0 discovery (Freelance tier, user-authorized this session) | shodan-fetch web UI path blocked by Cloudflare; API path approved |
| scanner | TCP/TLS banner + version + dork-FP-strip | 100 workers, 16 ports per IP |
| aimap | Stage-1b fingerprint + deep-enum | vector-db port profile on 8-host Chroma sample |
| visorplus | Stage-1a passive recon | 6-phase on representative VM host |
| visorgraph | Stage-2 cert-pivot operator attribution | 8-seed pivot on Chroma corpus |
| visorlog | Stage-6 ledger ingest | NDJSON ECS-dot-notation, 93 events ingested |
| visorscuba | Stage-7 compliance scoring | 96 nodes, 8/10 average |
| BARE | Semantic exploit module ranking | No MSF coverage for CVE-2026-45829 (top score 0.508 < 0.55 threshold) |
| tome | Platform corpus | Added chromadb.json cve_observed, victoriametrics.json (new), prometheus.json (new) |
| syllabus | Threat-literature search | Drove Cat-47 target selection via MemMorph paper |
| glance v0.1.0 → v0.1.1 | Schema-only sensitivity analyzer | NEW. Built this session. Panel-audited. v0.1.1 corrections shipped |
| constellation v0.1.0 | Cross-corpus operator hunt | NEW. Built this session |
| verify_chroma_campaign.py | Campaign canary verifier | 60-line Python, 24s wall on 307 hosts |
| verify_chroma_version.py | Multi-signal version fingerprinter | openapi.info.version + v2/auth/identity cross-check |
| verify_vm_unauth.py | VictoriaMetrics 9-endpoint verifier | 92s wall on 1,176 hosts |
| verify_prom_unauth.py | Prometheus 13-endpoint verifier | 138s wall on 1,429 hosts |
| verify_agentmem.py | Mem0/Letta/Zep/Cognee verifier | 61s wall on 269 hosts. T&E catch: status-code only, body-content gap |
| MCP Playwright | Shodan web UI session attempt | Blocked by Cloudflare; pivoted to API |
| VisorRAG | Not run | embedding API key returned 401 |
| VisorAgent | Not run | No controlled targets this session |

### Notable Configuration

- Mullvad VPN active (us-sjc-wg-508) for harvest.
- SHODAN_API_KEY pulled from `~/.config/shodan/api_key` after user authorization.
- DCWF panel pattern: 4 subagents per panel, non-overlapping mandates, written briefs not delegation prompts.
- glance sealed-mode default: `--include-samples=0`. All published rollups produced in sealed mode.

---

## 3. Methodology

### Enumeration approach

Three drivers:
1. **Carry-forward** from in-flight Chroma sweep started at session start.
2. **DCWF 902 strategic roadmap** for VictoriaMetrics and Prometheus selection (Q4 Topology Mirror generalization test).
3. **Syllabus search** for Cat-47 agent-memory selection. Search query "agent memory exfiltration LLM context store" returned MemMorph paper (arxiv 2605.26154) as top thematic match. Paper named `mem0` as target. Shodan probe confirmed population existed.

### Candidate identification

Per platform:
- Chroma: fingerprint via `/api/v1/heartbeat` `nanosecond heartbeat` body marker; campaign canaries identified via `probe-base-<nsec>` / `probe-ef-<nsec>` paired-collection pattern + `/nonexistent/cve45829<rand_text_alpha(16)>` model_name payload.
- VictoriaMetrics: body-content classification via `<h2>vmagent</h2>` / `<h2>vminsert</h2>` markers on the response of HTTP probes.
- Prometheus: `goVersion` field in `/api/v1/status/buildinfo` JSON (discriminator against VictoriaMetrics' Prometheus-API-compat shim).
- Agent memory: per-platform documented API endpoint shape (e.g., Zep `/api/v1/sessions` returning JSON array).

### Validation checks

Multi-signal per host, per platform. Insight #8 (auth probing) applied throughout: status code is necessary but not sufficient. The Cat-47 agent-memory survey caught a 21% FP rate post-publication because the verifier checked status code without body shape. Same lesson DCWF 672 audit had already caught on glance v0.1.0 earlier the same day.

### Safeguards

- Zero write-method HTTP calls (POST/PUT/DELETE/PATCH) on any endpoint across all four surveys.
- `/api/v1/import` write surface on VictoriaMetrics: known unauth-writable per docs. Not tested.
- `/api/v1/admin/tsdb/delete_series` on VictoriaMetrics and Prometheus: not tested.
- Embedded credentials in 25 Prometheus host configs: counted via regex match. Never extracted, validated, or used.
- 1,039 RFC1918 internal IPs leaked across VM and Prometheus scrape-target endpoints: counted. Never probed.
- Per-host evidence kept in private records: 307 Chroma + 1,176 VM + 1,429 Prom + 269 agentmem = 3,181 raw response bodies. Sanctioned-jurisdiction subset (436 hosts CN/RU/IR) reported aggregate-only by design.

---

## 4. Execution Trace

| Time | Action | Outcome / Decision |
|---|---|---|
| 02:51 | Session start hook fires. Wardrobe `ai-infra-hunt` loaded (13 atoms). | Posture set. |
| 02:55 | Continue in-flight Chroma sweep. 307 TIER-2 hosts available from earlier harvest. | Verifier built, 307 re-probed. |
| 03:00 | Verify pattern `probe-base-<nsec>` + `probe-ef-<nsec>` found on 201 hosts. | Hypothesis: adversary campaign. |
| 03:05 | External intel via WebSearch + WebFetch on the canary pattern. | Falsified. Hadrian's nuclei template for CVE-2026-45829 (ChromaToast) matches the pattern exactly. Withdrew adversary-campaign framing. |
| 03:15 | Push Chroma campaign case study + Insight #87 (canary persistence as monitoring proxy). | Commit eefbb5e. |
| 03:25 | DCWF 4-role panel dispatched on Chroma + on the VictoriaMetrics carry-forward target. | 8 subagents parallel. |
| 04:00 | VictoriaMetrics survey: 1,389 raw, 1,176 verified. 93.5% unauth. Insights #88 (scrape topology = org chart) + #89 (framework-level pprof bypass) drafted. | Push 571a918. |
| 04:30 | DCWF panel reports back. Catch: 134 vmcluster hosts misclassified (route paths under `/select/{accountID}/`). True unauth = 93.5% not 82.1%. | Case study corrections applied. Push 5db7d83. |
| 05:00 | glance v0.1.0 built (~600 lines Python). Schema-only sensitivity analyzer. Sealed mode default. | Public repo created. Push at 25105fb. |
| 05:30 | DCWF 4-role panel dispatched on glance. | 4 subagents parallel. |
| 06:00 | Prometheus survey kicked off as DCWF 902 falsifier test. 1,429 raw harvested. | Verifier ran 138s. |
| 06:30 | Prometheus results: 100% unauth on verified 475-host subset. 100% pprof open. 100% prometheus.yml leaked. | Push 79864ab. |
| 07:00 | Glance panel reports back. Critical bug caught (3 agents independently): `\b` regex anchor doesn't fire at underscore. `safe_runpod_dcgm_exporter` invisible to classifier. 0 AI_WORKLOAD became 830 after fix. | v0.1.1 shipped. Push d8c6817. |
| 07:30 | Constellation tool built. Cross-corpus operator hunt across 4 corpora. 9 same-IP multi-platform operators found. | Insight #92 candidate codified. Push bbb1927. |
| 08:00 | Syllabus search drives Cat-47 selection. MemMorph paper -> Mem0/Letta/Zep/Cognee. 269 hosts harvested. | Verifier built and ran. |
| 08:30 | Cat-47 results: 23 hosts claimed unauth. Sogei (Italian govt tax authority) attribution flagged. | Push ece7625. |
| 09:00 | Body-content re-verification catches 21% FP rate. Sogei is IBM DataPower gateway returning 200 with HTML 404 body. Withdrawn. | Correction push be62a07. |
| 09:30 | Session close. | This document. |

---

## 5. Findings

Grouped by severity at the end.

### F1 — ChromaDB CVE-2026-45829 (ChromaToast) Mass-Scan Campaign Attribution

| Field | Value |
|---|---|
| Name/ID | CVE-2026-45829 mass-scan canary residue |
| Type | Population-scale attack surface verification |
| Evidence | 201 of 269 (74%) verified-1.x Chroma hosts carry `probe-base-<nsec>` + `probe-ef-<nsec>` paired-canary collections from a 119-second burst on 2026-06-02. Scanner is CVE-aware: 0 of 37 unauth 0.5.x or 0.6.x hosts hit. |
| Observed exposure | 6 days post-burst, attacker collections still present. Operators have not noticed. |
| Severity | OBSERVED |

**Potential impact:** Demonstrates a framework-published nuclei template (Hadrian) being run at scale by an unknown third party. CVE itself unpatched at v1.5.9 three weeks after public disclosure.

### F2 — VictoriaMetrics Population Auth Posture + Framework Pprof Bypass

| Field | Value |
|---|---|
| Name/ID | VM Insight #88 + #89 anchor |
| Type | Population auth posture + framework-level auth bypass |
| Evidence | 1,176 verified VM-family hosts. 1,099 (93.5%) leak read access. 1,077 (91.5%) leave `/debug/pprof/` open including 10 hosts that demonstrably configured `-httpAuth` on data endpoints. 1,578 scrape-target endpoints leaked (66% RFC1918). |
| Observed exposure | Operator-config-applied auth does not gate pprof. Upstream issue #3060 (open since 2022). |
| Severity | HIGH (operator config insufficient as configured by framework defaults) |

**Potential impact:** Schema-only metadata about the operator's internal infrastructure topology is disclosed on 884 hosts. Runtime profiling, goroutine dumps, heap state on 1,077.

### F3 — Prometheus 100% Open on Verified Subset

| Field | Value |
|---|---|
| Name/ID | Prom-100-unauth-475 |
| Type | Population auth posture + config-dump endpoint disclosure |
| Evidence | 475 verified Prometheus hosts. 475/475 (100%) leak `/api/v1/status/config` returning the full `prometheus.yml`. 475/475 leave `/debug/pprof/` open. 25 hosts leak plaintext `basic_auth.password` or `bearer_token` in the dumped config. 2,031 scrape targets exposed. 661 rules. 7,604 metric names. |
| Observed exposure | Total. Operators who care deploy a reverse proxy (903 of 1,429 favicon-matched hosts behind a proxy that gates `/api/v1/*` paths). The verified 475 are the ones who didn't. |
| Severity | CRITICAL (entire configuration disclosure including credentials on 25 hosts) |

**Potential impact:** Full prometheus.yml gives remote_write URLs (pivot targets), AlertManager URLs (often internal), and on 25 hosts the basic_auth credentials used to scrape downstream targets.

### F4 — Zep Agent Memory Layer Unauth Sessions

| Field | Value |
|---|---|
| Name/ID | Zep-unauth-10 |
| Type | Application-tier auth posture on emerging category |
| Evidence | 10 of 19 verified Zep hosts return 200 JSON array on `/api/v1/sessions`. 6 of 10 leak actual session data: 27 user-session UUIDs total. Timestamps span 2024-05 through 2026-04. |
| Observed exposure | Per-user conversation session IDs disclosed. Oldest deployment exposed 2 years. |
| Severity | HIGH |

**Potential impact:** Memory poisoning per MemMorph paper attack vector is reachable on the 10 unauth hosts (POST `/api/v1/memory/{session}/messages` accepts unauth writes per Zep docs). Not tested.

### F5 — Mem0 MCP Proxy Confirmed (single host)

| Field | Value |
|---|---|
| Name/ID | mem0-mcp-proxy-1 |
| Type | Single-host MemMorph attack target confirmation |
| Evidence | 1 verified Mem0 MCP proxy on Alibaba HK returns `{"status":"ok","service":"mem0-mcp-proxy"}` on `/v1/memories/` GET. Population scout total 161 hits; verified-running subset 6; confirmed unauth after FP audit 1. |
| Observed exposure | Mem0 MCP proxy endpoint shape confirmed. Other 2 hosts originally claimed unauth were HTML-body FPs. |
| Severity | OBSERVED (single host, MCP proxy not primary Mem0 server) |

**Potential impact:** Demonstrates MemMorph paper attack class population exists. Confirms only one host; the paper's lab result generalizes empirically but at smaller scale than originally claimed.

### F6 — Cross-Platform Co-Deployment Multiplier (9 same-IP)

| Field | Value |
|---|---|
| Name/ID | constellation-2026-06-08 |
| Type | Cross-corpus operator detection finding |
| Evidence | 9 IPs run multiple unauth platforms on same host. 8 are VM + Prometheus AlertManager co-deployed. 1 is Chroma + Prometheus on the same IP (23.95.88.247, RackNerd). |
| Observed exposure | Same operator decision (ship monitoring with no auth) propagates across two platforms per IP. |
| Severity | OBSERVED |

**Potential impact:** Insight #92 candidate (cross-platform co-deployment multiplies exposure). Codified.

### Severity rollup

- **CRITICAL (1):** F3 — Prometheus prometheus.yml + credentials on 25 hosts.
- **HIGH (2):** F2 — VM framework pprof bypass; F4 — Zep unauth sessions on 10 hosts.
- **OBSERVED (3):** F1, F5, F6.
- **WITHDRAWN:** Sogei Italian government tax authority Letta attribution (HTML-body FP, not running Letta).
- **WITHDRAWN:** davidtcox.com (UK) Letta attribution (same HTML-body FP class).
- **WITHDRAWN:** A100 ROW Germany Letta, soul-bingo.com UAE Letta, Tencent China Mem0 + Cognee — all HTML-body FPs.

---

## 6. Risk Assessment

### Overall posture

Systemic. Across four substrate and emerging tiers, the auth-off-default thesis holds. VictoriaMetrics 93.5%, Prometheus 100% on the verified subset, Chroma 100% on TIER-2 verified, Zep 53% confirmed unauth post-FP-audit. The pattern is the deployment decision (operator ships defaults, walks away).

### Confidentiality

- Internal infrastructure topology disclosed across VM and Prometheus (~3,609 scrape-target endpoints across both surveys, ~66% RFC1918).
- Full prometheus.yml content on 475 hosts including 25 with embedded credentials.
- Agent session IDs on 6 Zep hosts.
- Collection name metadata on 281 Chroma hosts.

### Integrity

- VM `/api/v1/import` write surface documented unauth on 884 hosts. Not tested. If exploited per the documented behavior: forged metrics drive operator automation (autoscaling, alerting, training early-stopping, GPU thermal shutdown).
- Prometheus `/api/v1/admin/tsdb/delete_series` gated by `--web.enable-admin-api` flag (default off). 0 confirmed where flag is flipped.
- Zep memory write surface documented unauth on 10 hosts. Not tested. MemMorph paper demonstrates the attack works in lab.

### Availability

- Prometheus `/api/v1/admin/tsdb/snapshot/create` available where admin API enabled. DoS via disk fill.
- VM `/debug/pprof/profile` and `/debug/pprof/heap` produce 30-second CPU snapshots; sustained pulls can degrade service.

### Systemic patterns

- **Framework pprof bypass.** VM `-httpAuth.username/password` does not cover `/debug/pprof/`. Upstream issue #3060 open since 2022. 10 hosts demonstrate operators applied auth and pprof still leaks.
- **Reverse-proxy-or-nothing on Prometheus.** 63% of favicon-matched Prometheus hosts behind a proxy that gates `/api/v1/*`. 33% completely open. No middle ground.
- **Status-code-without-body classifier FP cascade.** Three independent verifiers this session classified status_code == 200 without body shape validation. DCWF 672 panel caught this pattern on glance v0.1.0 (`\b` regex anchor issue). DCWF 672 + 753 caught it on VM (134 vmcluster reclassification). The agentmem verifier exhibited the same bug post-publication and was corrected.

---

## 7. Recommendations

### R1 — VictoriaMetrics: deploy vmauth or restrict network

```bash
# Operator-side: deploy vmauth as the only public entrypoint
docker run -p 80:80 -v /etc/vmauth.yml:/etc/vmauth.yml \
  victoriametrics/vmauth -auth.config=/etc/vmauth.yml
# Restrict raw vmsingle/vmagent port to known clients
iptables -A INPUT -p tcp --dport 8428 ! -s 10.0.0.0/8 -j DROP
```

This addresses both Insight #88 (scrape topology disclosure) and Insight #89 (pprof bypass). `--web.config.file` with basic_auth alone is insufficient because pprof inherits a separate mux.

### R2 — Prometheus: same pattern, vmauth analog or nginx-basic-auth

```bash
# Apply --web.config.file with TLS + basic_auth + drop /debug/pprof network reach
prometheus --web.config.file=/etc/prom-web.yml --web.enable-admin-api=false
```

The 475 verified-open Prometheus hosts. The fix scales operator-by-operator. Framework-side: file upstream issue extending `--web.config.file` to cover `/debug/pprof/`.

### R3 — Zep + agent memory: set environment auth

```bash
# Zep: set ZEP_AUTH_REQUIRED=true and per-user JWT auth in config
# Mem0: configure API key gate on /v1/memories endpoints
```

10 Zep + 1 Mem0 reachable hosts. Restraint-bounded; no operator outreach yet per protocol.

### Future automation

```bash
# Integrate aimap + glance into post-deploy pipeline
aimap -list your-public-ips.txt -ports 8428,8429,8480,8481,9090,9091,9093,8000,8011,8283 -o report.json
glance scan ./evidence --source vm-verify -o sensitivity-rollup.json
# Fail CI if rollup contains PII/PHI hits or known-vulnerable signatures
```

---

## 8. Limitations and Assumptions

| # | Limitation | Risk Implication |
|---|---|---|
| L1 | Cat-47 agentmem verifier did not validate response body shape, only status code. 21% FP rate caught post-publication. | Initial Letta + Cognee findings withdrawn. T&E discipline shifted to body-content as default check in next verifier. |
| L2 | Cat-46d Prometheus favicon dork has 63% FP rate. Real Prometheus = 475 of 1,429. | Headline numbers reported on verified subset only. Behind-reverse-proxy operators counted separately as operator-side hardening signal. |
| L3 | VictoriaMetrics version detection regex missed `vm_app_version{version="..."}` text-format label. 30+ hosts under-classified as version-unknown. | DCWF 672 audit logged. v0.2 verifier patch pending. |
| L4 | VictoriaMetrics `/api/v1/import` write surface documented unauth but not tested. | Claim that "import accepts unauth writes" rests on docs only, not on probe. Demoted in case study to "documented behavior, not validated." |
| L5 | 25 Prometheus hosts leaked plaintext credentials in `/api/v1/status/config`. Counted via regex match in our verifier. Not extracted or used. | Disclosure pipeline pending. Restraint maintained. |
| L6 | 436 hosts in CN/RU/IR sanctioned jurisdictions (31% of VM harvest, similar shares elsewhere). | Aggregate-only reporting by design. Per-host disclosure not available. |
| L7 | DCWF panel audits caught one FP cascade per panel (3 of 3 panels). Pattern is consistent across glance and VM. | Recommend body-shape validation as default in every future verifier. |
| L8 | Mullvad VPN active throughout. Probe origin IP is San Jose CA. | Operator-side blocklists targeting that range may have filtered some probes. Cannot enumerate from probe data. |

---

## 9. Proof of Concept (PoC) Illustrations

> PoCs use read-only or simulated interactions. No operator data extracted. No credentials used. No exploit payloads.

### PoC 1: VictoriaMetrics /api/v1/targets scrape-topology disclosure

**Scenario:** Unauthenticated read of vmagent target list reveals internal infrastructure naming.

```
REQUEST:
  GET /api/v1/targets HTTP/1.1
  Host: <operator-host>:8429

RESPONSE:
  HTTP/1.1 200 OK
  Content-Type: application/json

  {"status":"success","data":{"activeTargets":[{"discoveredLabels":{
    "__address__":"<internal-svc-name>:9100",
    "__metrics_path__":"/metrics","job":"<operator-job-name>"},
    "scrapeUrl":"http://<rfc1918-ip>:9100/metrics",...}]}}
```

**Demonstrated:** A reader of the target list learns the operator's internal hostname convention, what categories of service the operator runs, and which RFC1918 subnets the operator uses. The PoC does NOT modify any metric value. Does NOT POST to `/api/v1/import`. Does NOT issue PromQL queries.

### PoC 2: Prometheus /api/v1/status/config full configuration disclosure

**Scenario:** Unauthenticated read of `prometheus.yml` content via Prometheus' own runtime introspection endpoint.

```
REQUEST:
  GET /api/v1/status/config HTTP/1.1
  Host: <operator-host>:9090

RESPONSE:
  HTTP/1.1 200 OK
  Content-Type: application/json

  {"status":"success","data":{"yaml":"global:\n  scrape_interval: 15s\n
  scrape_configs:\n  - job_name: '<operator-job>'\n    static_configs:\n
    - targets: ['<rfc1918-ip>:<port>']\n  remote_write:\n
    - url: '<remote-write-endpoint>'\n      basic_auth:\n
        username: '<placeholder>'\n        password: '<placeholder>'\n..."}}
```

**Demonstrated:** Operator's full Prometheus configuration retrievable unauth. On 25 of 475 verified hosts the `basic_auth.password` value is present in plaintext. PoC does NOT extract or use the password value. Does NOT probe the `remote_write` endpoint with the disclosed credential.

### PoC 3: Zep /api/v1/sessions session-ID disclosure

**Scenario:** Unauthenticated read of session UUIDs on a Zep memory-layer instance.

```
REQUEST:
  GET /api/v1/sessions HTTP/1.1
  Host: <operator-host>:8000

RESPONSE:
  HTTP/1.1 200 OK
  Content-Type: application/json

  [{"uuid":"<placeholder-uuid>","id":1,"created_at":"2025-05-21T...",
    "updated_at":"2025-05-21T...","deleted_at":null,...}]
```

**Demonstrated:** Session UUIDs and timestamps disclosed unauth on 6 of 10 verified-unauth Zep hosts. PoC does NOT read message content via `/api/v1/memory/{session}/messages`. Does NOT POST to the write endpoint. The MemMorph paper's attack vector is reachable; not exercised.

### PoC 4: Chroma campaign canary collection presence

**Scenario:** Detection of attacker-deposited canary collection on 201 of 269 verified-1.x Chroma hosts.

```
REQUEST:
  GET /api/v1/collections HTTP/1.1
  Host: <operator-host>:8000

RESPONSE:
  HTTP/1.1 200 OK
  Content-Type: application/json

  [{"id":"<uuid>","name":"probe-base-1780358529676380700","configuration_json":
    {"hnsw":{"space":"l2"},"embedding_function":{"name":"sentence_transformer",
    "config":{"kwargs":{"trust_remote_code":true},
    "model_name":"/nonexistent/cve45829<rand_text_alpha(16)>"}}}}, ...]
```

**Demonstrated:** Hadrian-style detection nuclei template canary collections persist on 201 hosts 6 days after the 119-second burst on 2026-06-02. PoC does NOT modify or remove the collections. Does NOT POST a counter-canary. The persistence count is the finding.

---

*Prepared by NuClide Research (Nicholas Kloster + Claude Sonnet 4.6) · Session date 2026-06-08*
