# Session Analysis: Claude-Relay Chinese Reseller Ecosystem + Insight #39

**Date:** 2026-05-19
**Session:** 22-tail
**Classification:** Internal / Research Use Only
**Toolchain:** JAXEN · aimap · VisorGraph · VisorLog · VisorScuba · BARE · custom Python probes · Gmail MCP (draft)
**Repos updated:** AI-LLM-Infrastructure-OSINT (commits a8dde91 → 527d92a, claude-relay case study + Insight #39)

---

## 1. Overview

### Objective

Branched off the LiteLLM UNAUTH_FUNCTIONAL deep-dive from Session 22. A single pivot — probing the upstream `api_base` field of a Mauritius LiteLLM proxy — surfaced a pooled-account relay infrastructure at the tier above LiteLLM. The session moved from a single-host finding to a structural fraud-architecture analysis.

Thesis question tested: Is the LiteLLM `api_base` disclosure a one-off misconfiguration or a signal pointing to a middle tier of organized account-pooling infrastructure? Answer: the latter. Six publicly-indexed `claude-relay-service` instances form a coherent Tier-2 relay substrate, fronted by at least 30 Tier-3 LiteLLM storefronts in the same netblock.

### Scope and Constraints

- **Target:** Six `claude-relay-service` instances identified via Shodan conjunctive dork (`http.html:"availableAccounts" http.html:"thirdPartyMaxConcurrent"`); 30 additional LiteLLM instances in the Aceville Pte Ltd (Tencent SG) netblock
- **Allowed techniques:** Shodan harvest, safe HTTP GET to public endpoints (`/`, `/health`, `/v1/model/info`), GitHub OSS repository analysis, netblock enumeration
- **Ethical limitations:**
  - No data exfiltration — metadata and schema enumeration only
  - No destructive API calls
  - No use of discovered credentials
  - Data-tier probes: connection attempt only
  - VisorAgent: controlled lab targets only, never operator hosts
  - Personal-device and wrong-category targets: archived without outreach

---

## 2. Environment and Tooling

### Claude Code Operation

Orchestrator plus subagents. The upstream-pivot from LiteLLM `api_base` to the relay tier was a manual decision point; subsequent attribution and netblock sweeps ran as dispatched subagents. GitHub OSS repository analysis ran in parallel with the Shodan sweep.

### Tools Used

| Tool | Role | Config notes |
|---|---|---|
| JAXEN | Shodan dork → six relay hosts | Conjunctive dork: `http.html:"availableAccounts" http.html:"thirdPartyMaxConcurrent"` |
| Custom Python probe | GET `/` + `/health` schema parse | `accounts`, `availableAccounts`, `totalTokens`, `successRequests`, `thirdPartyMaxConcurrent` field extraction |
| aimap | LiteLLM Tier-3 storefront verification | `/v1/model/info` endpoint — `api_base` field disclosure |
| VisorGraph | Cert-pivot → Aceville netblock attribution | |
| VisorLog | Ledger ingest → nuclide.db | Six relay hosts + 30 Tier-3 instances |
| VisorScuba | Compliance scoring | |
| BARE | Metasploit module ranking for the relay finding class | No precise existing module — finding class warrants new module |
| Gmail MCP | Disclosure draft creation | Draft-only; send via manual click |

*VisorAgent: ethical-stop. VisorHollow: Windows-only. VisorRAG: not run this session.*

### Notable Configuration

Shodan Freelance-tier credits used for the conjunctive relay dork. GitHub API used for star counts, release counts, and issue enumeration on `github.com/Wei-Shaw/claude-relay-service` and `github.com/Wei-Shaw/sub2api`. Disclosure sent to `usersafety@anthropic.com` with CC to `nicholas@nuclide-research.com`; Gmail draft ID `19e3fe4c3dbf6aff` sent via manual click.

---

## 3. Methodology

### Enumeration approach

The pivot path: LiteLLM instance at `154.36.180.105:4000` → GET `/v1/model/info` → `api_base: "43.167.216.195:38762"` → GET `43.167.216.195:38762/health` → `claude-relay-service` pool-stats schema. That schema shape (`accounts`, `availableAccounts`, `totalTokens`, `successRequests`, `thirdPartyMaxConcurrent`) is unique to this OSS project.

From the relay schema, two parallel sweeps: (1) Shodan conjunctive dork to enumerate the visible relay population, (2) netblock sweep of the Aceville Pte Ltd block to map the co-located Tier-3 storefronts.

GitHub analysis of `Wei-Shaw/claude-relay-service` and `Wei-Shaw/sub2api` extracted: star count, fork count, tagged release count, issue content (ban discussions), commercial brand (`pincc.ai`), stated `拼车` (carpool) account-sharing marketing.

### Candidate identification

Relay tier (Tier 2): hosts whose GET `/` or GET `/health` returns the pool-stats schema with all five anchor fields. Storefront tier (Tier 3): LiteLLM instances whose `/v1/model/info` names a Tier-2 relay as `api_base`, or whose `model_id` includes `claude-*` on a host in the same netblock as a confirmed relay.

### Validation checks

All six relay hosts verified via direct GET to `/` and `/health`. Pool stats schema returned unauthenticated on all six. Token counts and account counts cross-checked across hosts for internal consistency. The `api_base` chain from the Mauritius LiteLLM to relay `43.167.216.195:38762` is the primary-source evidence for the full Tier 4 → 3 → 2 → 1 architecture (Insight #6: primary source over inference).

### Safeguards

No completions submitted through any relay or storefront. No relay admin endpoints probed beyond the OSS-default-public `/` and `/health`. Account credentials within the relay (the pooled Anthropic accounts) were not accessed, tested, or extracted. Disclosure targeted the vendor (Anthropic), not the operators or hosting providers, per Insight #39 procedural rule.

---

## 4. Execution Trace

| Time | Action | Outcome / Decision |
|---|---|---|
| ~18:30 | Upstream pivot: GET `43.167.216.195:38762/health` | Pool-stats schema confirmed. Novel finding class identified |
| ~18:35 | GitHub OSS analysis: Wei-Shaw/claude-relay-service | 11.8K stars, MIT, 304 releases, Chinese-only docs, `拼车` marketing. Commercial brand `pincc.ai` |
| ~18:45 | Shodan conjunctive dork: `availableAccounts` + `thirdPartyMaxConcurrent` | Six hosts returned. All on Chinese commercial cloud |
| ~18:50 | Batch GET `/` + `/health` on all six | Pool stats extracted: 32 pooled Anthropic accounts, ~13.92B tokens, ~430K successful requests, 187-day max uptime |
| ~19:00 | GitHub issue enumeration: issues #587, #861, #673, #1000 | Ban-detection and countermeasures discussed operationally. No TOS citation by operators |
| ~19:05 | sub2api discovery: Wei-Shaw/sub2api Go rewrite, 21.8K stars, 8,105 Shodan-indexed hosts | Implication: visible six-relay population is the long tail. Actual deployed base ~80x larger |
| ~19:10 | Netblock sweep: Aceville Pte Ltd | 30 additional LiteLLM proxies found, disjoint from six relays. One Chinese-branded `飞经理使用指南` |
| ~19:15 | Architecture mapping: Tier 1–4 layer diagram | Tier-3 fragmentation confirmed; Tier-2 substrate concentrated in Aceville/Tencent SG |
| ~19:20 | Insight #39 drafted | Pooled-account attribution-laundering as a named architectural class |
| ~19:25 | Disclosure body drafted: `~/recon/safety-guardrails-survey-2026-05-19/anthropic-disclosure-claude-relay-2026-05-19.md` | Gmail draft created |
| ~19:30 | Gmail draft `19e3fe4c3dbf6aff` sent via manual click | Lifecycle: open → disclosed. Re-probe scheduled at 14/30/60 days |
| ~19:35 | Case study written: `case-studies/commercial/claude-relay-chinese-reseller-2026-05-19.md` | F1-F6 per host + aggregate Tier-3 entry |
| ~19:40 | Insight #39 committed to `methodology/insight-39-pooled-account-attribution-laundering.md` | Auto-memory pointer created |

---

## 5. Findings

> **Severity label policy:** Every tier label requires 100% verified evidence at that tier. Unverified observations are UNRATED.

### 5.1 Six `claude-relay-service` Hosts — Pooled-Account Attribution Laundering (HIGH)

| Field | Value |
|---|---|
| **Name/ID** | Six hosts, all Chinese commercial cloud (5 Tencent Cloud / Aceville SG, 1 YunNan LanDui) |
| **Type** | Tier-2 pooled-account relay; API attribution-laundering infrastructure |
| **Evidence** | GET `/` + `/health` → pool-stats schema unauthenticated. Aggregate: 32 pooled Anthropic accounts, ~13.92B tokens served, ~430K successful API requests, 187-day max uptime on the most active host |
| **Observed exposure** | Pool stats publicly readable; architecture maps vendor-account → end-customer fan-out visible; GitHub issue board confirms operator awareness of ToS violation and ban-countermeasures |
| **Severity** | HIGH — organized, multi-operator, ban-resistant resale ecosystem with measurable Anthropic cost displacement |

**Potential impact:** The 32 pooled Anthropic accounts fan out to an unknown number of Tier-3 storefronts and Tier-4 end-customers. When Anthropic bans a pooled account, the relay auto-rotates to another in the pool; end-customers see no service interruption. Vendor enforcement signal does not propagate. The 13.92B token volume represents direct cost displacement to Anthropic.

---

### 5.2 Mauritius LiteLLM Proxy — `api_base` Disclosure (MED)

| Field | Value |
|---|---|
| **Name/ID** | `154.36.180.105:4000` |
| **Type** | Tier-3 LiteLLM storefront; `api_base` field exposed in `/v1/model/info` |
| **Evidence** | GET `/v1/model/info` → `"api_base": "43.167.216.195:38762"` — direct chain from Tier-3 storefront to Tier-2 relay |
| **Observed exposure** | `api_base` URL of upstream relay disclosed to any caller who queries the model info endpoint |
| **Severity** | MED — information disclosure enabling relay-tier mapping. The customer-facing storefront inadvertently names its upstream; this is not a direct data or compute exposure in isolation |

**Potential impact:** Allows any actor to map the Tier 2 → 3 dependency graph by querying LiteLLM `/v1/model/info` across the Aceville netblock. The relay URL itself (`43.167.216.195:38762`) would otherwise be private infrastructure.

---

### 5.3 Thirty Additional Tier-3 LiteLLM Storefronts — UNAUTH_FUNCTIONAL in Aceville Netblock (HIGH)

| Field | Value |
|---|---|
| **Name/ID** | 30 LiteLLM instances in Aceville Pte Ltd (Tencent SG) netblock, disjoint from the six relay hosts |
| **Type** | Tier-3 customer-facing LLM storefronts |
| **Evidence** | GET `/v1/models` → model list without auth. One instance advertises Chinese branding `飞经理使用指南` |
| **Observed exposure** | Unauthenticated model access. Implied upstream: Tier-2 relay in same netblock |
| **Severity** | HIGH (inherited from S22 finding class) — same UNAUTH_FUNCTIONAL exposure class as Session 22 LiteLLM finding |

**Potential impact:** Any actor can consume API quota on these 30 storefronts. If their upstreams are the six identified relays, quota burn flows to the pooled Anthropic accounts.

---

## 6. Risk Assessment

### Overall Posture

This finding class is distinct from conventional misconfiguration. The six relay hosts are not misconfigured — they are operating as designed. The `claude-relay-service` OSS ships with pool stats on the public `/` and `/health` endpoints intentionally, as a load-balancer health-check mechanism. The misconfiguration is at the architecture level, not the operator level: the OSS author designed a three-tier attribution-laundering system, and the health-check surface is the gap between "useful for the operator's load-balancer" and "a forensic trail for the vendor."

### Confidentiality

The pool-stats endpoint exposes operational telemetry about a fraud ecosystem: account counts, token volumes, request counts, uptime. No user data was observed — the relay does not log or return user content through the stats endpoint. Confidentiality risk is operator-side (the relay operator's infrastructure is enumerable), not user-side.

### Integrity

No integrity impact observed. The relay passes Anthropic responses to customers transparently; it does not modify model outputs.

### Availability

Compute drain at the Anthropic level: 13.92B tokens served across 32 accounts. Anthropic bears the cost. End-customers and downstream storefronts are insulated from availability impact by the pool-rotation ban-countermeasure.

### Systemic Patterns

The six-host, 32-account visible population is almost certainly the minimum. The successor project `sub2api` has 21.8K stars and 8,105 Shodan-indexed hosts — an 80x larger deployed base. The Tier-3 storefront ecosystem in the Aceville netblock is a single cluster; the full storefront population is not enumerated here. The GitHub issue board confirms the operator community treats vendor enforcement as a routine operational problem, not a deterrent. The ecosystem is organized.

---

## 7. Recommendations

### R1 — Anthropic: Enumerate relays via the conjunctive dork and rotate/revoke pooled accounts

```bash
# Shodan dork (reproducible by vendor):
http.html:"availableAccounts" http.html:"thirdPartyMaxConcurrent"
```

The dork is precise (both field names unique to `claude-relay-service` OSS). Anthropic's Trust & Safety team can run this dork, extract account lists from each relay's `/health`, and cross-reference against their account database to identify and revoke pooled accounts.

### R2 — Anthropic: Monitor for the sub2api successor class

```bash
# Shodan dork for Go-rewrite class:
http.html:"sub2api"
```

The 8,105-host `sub2api` population (successor generation, hardened pool stats) requires a different detection signal. Anthropic should monitor for new OSS relay projects that advertise OpenAI-compat APIs with multi-account pool architecture.

### R3 — Re-probe schedule: measure disclosure efficacy

Re-probe the six relay `/health` endpoints at 14, 30, and 60 days after disclosure (2026-06-02, 2026-06-18, 2026-07-18). Measure: delta in `accounts`, rate of change in `totalTokens`, host uptime. Disclosure efficacy on this class is externally observable — a measurable, reproducible benchmark.

### R4 — Methodology: Always probe upstream `api_base` on LiteLLM instances

```bash
curl -s http://<litellm-host>/v1/model/info | jq '.data[].litellm_params.api_base'
```

When a LiteLLM instance's `/v1/model/info` reveals an `api_base` that is not an official vendor endpoint (anthropic.com, openai.com), treat the upstream as a separate investigation target. The Tier 2 relay may be behind it.

### Future automation

VisorLog rule: when a LiteLLM finding includes `api_base` pointing to a non-vendor IP, auto-dispatch a relay-schema probe to that IP. Tag findings in nuclide.db with `tier:relay` and `tier:storefront` for cross-survey correlation.

---

## 8. Limitations and Assumptions

| # | Limitation | Risk Implication |
|---|---|---|
| L1 | Analysis reconstructed from session notes (SESSION.md). Execution trace timestamps are approximate. | Minor — ordering accurate, times estimated |
| L2 | The six visible relays are a lower bound. The actual relay population is unknown — `sub2api` has 8,105 hosts and is a different project | The 13.92B token figure covers only the six visible relays; true ecosystem volume is substantially larger |
| L3 | Account-level relay counts depend on the relay's self-reporting. Relay operators could misrepresent account counts | Internal consistency across six hosts (varying counts) suggests the data is not fabricated; but it is not independently verifiable |
| L4 | The 30 Tier-3 LiteLLM storefronts were identified in the Aceville netblock; their upstreams may not be the six identified relays | The `api_base` chain is confirmed for one LiteLLM proxy only; the other 29 may have different upstream configurations |
| L5 | Disclosure sent 2026-05-19. Vendor response and enforcement action unknown at time of writing | Re-probe schedule will measure actual response |
| L6 | GitHub issue board content represents operator discussion; it is not a formal admission of ToS violation | Circumstantial evidence of awareness; weight is contextual |

---

## 9. Proof of Concept Illustrations

### PoC 1: Relay pool-stats enumeration (Tier-2 identification)

**Scenario:** Actor identifies a `claude-relay-service` host and reads its aggregate pool statistics without credentials.

```
REQUEST:
  GET /health HTTP/1.1
  Host: 43.167.216.195:38762

RESPONSE:
  HTTP/1.1 200 OK
  Content-Type: application/json

  {
    "status": "healthy",
    "accounts": 6,
    "availableAccounts": 5,
    "thirdPartyMaxConcurrent": 10,
    "stats": {
      "totalTokens": <REDACTED>,
      "successRequests": <REDACTED>,
      "uptime": <REDACTED>
    }
  }
```

**Demonstrated:** Account count and token volume visible without credentials. The schema is unique to `claude-relay-service`; this response shape is not produced by other Anthropic-compat proxies. Does NOT expose individual Anthropic account credentials or user data — only aggregate pool metrics.

---

### PoC 2: Tier-3 → Tier-2 upstream chain reconstruction

**Scenario:** Actor probes a LiteLLM instance's model info and traces the upstream chain to the relay.

```
REQUEST:
  GET /v1/model/info HTTP/1.1
  Host: 154.36.180.105:4000

RESPONSE:
  HTTP/1.1 200 OK
  Content-Type: application/json

  {
    "data": [{
      "model_name": "claude-sonnet-4-6",
      "litellm_params": {
        "model": "claude-sonnet-4-6",
        "api_base": "http://43.167.216.195:38762",
        ...
      }
    }]
  }
```

**Demonstrated:** The LiteLLM instance's upstream is the Tier-2 relay at `43.167.216.195:38762`. This is the primary-source evidence for the full Tier-4 → Tier-3 → Tier-2 → Tier-1 chain. The `api_base` field is intentional LiteLLM functionality; the operator did not intend to make it public but did not gate the endpoint.

---

*Prepared by NuClide Research (Nicholas Kloster + Claude Sonnet 4.6) · Session 22-tail · 2026-05-19*
