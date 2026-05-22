# Session Analysis: Code-Assistants 4-Day Delta + Verification Correction

**Date:** 2026-05-18
**Session:** 18
**Classification:** Internal / Research Use Only
**Toolchain:** JAXEN, aimap v1.9.8, VisorGraph, VisorBishop, VisorLog, VisorScuba, BARE, VisorCorpus, VisorSD, cortex
**Repos updated:** AI-LLM-Infrastructure-OSINT (2ab1918)

---

## 1. Overview

### Objective

Second pass on the AI code-assistant tier (category 09). First pass ran 2026-05-14 on 233 hosts and found 54 unauth across 8 platforms. This session re-harvested and ran the full 19-tool chain four days later to measure persistence, detect new entries, and apply Stage-2 data-layer verification the first pass skipped. Thesis question: do unauth code-assistant hosts persist without external pressure, and what is the true unauth rate at the data layer?

### Scope and Constraints

- **Target domains/IPs:** Public internet code-assistant hosts: OpenHands, Sourcegraph, Tabnine, Sourcebot, Sweep AI, CodeGeeX, OpenDevin, bolt.diy, Dyad, gpt-engineer — any reachable from Shodan results
- **Allowed techniques:** Passive Shodan harvest, banner grab, safe HTTP GET and POST to documented API endpoints, cert-pivot, VisorScuba compliance scoring, BARE exploit ranking
- **Ethical limitations:**
  - No data exfiltration — metadata and schema enumeration only
  - No destructive API calls
  - No use of discovered credentials
  - Data-tier probes: connection attempt only (does auth gate exist? no queries)
  - Active LLM exploitation (VisorAgent): controlled lab targets only, never operator hosts — not run this session
  - Personal-device and wrong-category targets: archived without outreach

---

## 2. Environment and Tooling

### Claude Code Operation

Orchestrator + subagent pattern throughout. Parallel lanes for: JAXEN harvest, aimap fingerprint, VisorBishop re-probe, VisorGraph cert-pivot. Stage-2 verification pass ran as a sequential corrective after the initial overclaim was caught mid-session by Nick.

### Tools Used

| Tool | Role | Config notes |
|---|---|---|
| JAXEN | Stage-0: Shodan harvest across 15 dorks | Paginator, --clean flag, deduplication across 10 platforms |
| aimap v1.9.8 | Stage-1 fingerprint + Stage-2 verify | Known dcm4chee catchall FP (Insight #22) still present; 38 ASP.NET/Express FPs expected |
| VisorBishop | Re-prober + IP-shadow | -ip-shadow enabled; adjacent-port sweep for stacked services |
| VisorGraph | Cert-pivot, operator attribution | 11 named operators re-verified same-day |
| VisorLog | Ledger ingest | 192 events ingested to nuclide.db (127 need lifecycle update to archived) |
| VisorScuba | Compliance scoring | 192/192 AI.C1 Critical — over-counts the 127 FPs; re-scope queued |
| BARE | Metasploit semantic ranking | Sourcegraph hit 0.799 against graphql introspection scanner |
| VisorCorpus | Adversarial corpus generation | Ran against controlled lab only |
| VisorSD | ASN/org dork sweep | Code-assistant stack absent; 0/3 hits on Contabo + Hetzner ASNs |
| cortex | Auth-context analyzer | Vertiv-Tabnine attribution documented at ~/recon/code-assistants-2026-05-18/cortex-vertiv-tabnine.md |
| JS-bundle extract | SPA hidden-API extraction | Ran against OpenHands + Sourcegraph frontends |
| VisorHollow | Windows process-injection benchmark | [—] not applicable — Windows-only |
| VisorAgent | Active LLM exploitation | [—] ethical-stop — controlled corpus only, never operator hosts |
| VisorRAG | RAG adversarial confirmation | [—] skipped this session |
| VisorGoose | TLD / CT-log sweep | [—] no code-assistant dorks in .gov-TLD catalog — coverage gap noted |
| menlohunt | GCP EASM | [—] not run — no GCP-specific signal in target class |
| recongraph | Seed-polymorphic recon graph | [—] not run — cert-pivot via VisorGraph covered the attribution surface |
| nu-recon | Single-host passive deep-read | [—] not run — per-host deep-read deferred to disclosure-prep stage |
| VisorPlus | Orchestrator | [—] not run — manual orchestration used |

### Notable Configuration

Mullvad VPN active. aimap v1.9.8 has a known dcm4chee-arc catchall FP (Insight #22) — 38 misclassifications expected on ASP.NET/Express hosts. VisorScuba scored 192/192 events, but 127 of those are FPs that need re-scoping. BARE semantic threshold: 0.6 first-party-authorization floor used for interpretation.

---

## 3. Methodology

### Enumeration approach

JAXEN paginator across 15 Shodan dorks covering 10 platforms. Same dork set from 2026-05-14 re-run to enable delta measurement. 405 candidates harvested; deduplication across overlapping platform dorks.

### Candidate identification

Stage-1: aimap fingerprint pass on all candidates. HTTP GET to platform-specific title/route anchors. Stage-2: agent API contract probe rather than body-text match — critical distinction that the 2026-05-14 pass did not apply.

Insight #31 (codified this session): for app-builder platforms (bolt.diy, Dyad, gpt-engineer), the brand string appears in HTML of applications they generate, not in the agent UI. Probe the agent's API contract, not the body text. A host with bolt.diy brand in og:image CDN URL is a generated app, not the agent.

### Validation checks

- OpenHands: POST `/api/conversations` (empty body) returning 200 + valid `conversation_id`. 16 of those 61 advanced to RUNNING + `STATUS:READY` — Docker sandbox allocated, no auth. Agent API shape confirmed per Insight #6 conjunctive-marker rule.
- Sourcegraph: GET `/` returning "Private mode required" = real Sourcegraph, auth-on. Data-layer probe: GET `/api/graphql` returns 401 across 19 of 19 hosts.
- Sourcebot: GET `/` login page = real Sourcebot. One host served CanerTheOz repo listing.
- Tabnine: GET `/` landing page + GET `/api/*` returns 401 across 5 of 5. No data-layer access.
- app-builder FP detection: og:image CDN URL check (bolt.new/static/, gpt-engineer-file-uploads/, storage.googleapis.com/gpt-engineer-*). Title check: `dyad-generated-app`, `Create Next App`. Any match = output of the tool, not the agent.

Insight #30 (codified this session): persistence without pressure. 25 of 30 baseline OpenHands hosts from 2026-05-14 confirmed still unauth four days later. 83.3% persistence rate. Insight #28's extortion-driven ~85× faster decay is the contrast case.

### Safeguards

No brute forcing. No privilege escalation. No data exfiltration. The 16 sandbox-READY hosts were not sent any messages — doing so would burn operator LLM quota (write-tier action). OpenAPI schema read instead of `/api/secrets` or `/api/user/*` deep-enum routes. No credentials used at any point.

---

## 4. Execution Trace

| Time | Action | Outcome / Decision |
|---|---|---|
| ~13:00 | JAXEN harvest: 15 dorks across 10 platforms | 405 candidates harvested, ~169 deduped unique IPs |
| ~13:20 | aimap fingerprint pass (Stage 1) | 192 platform candidates; 38 dcm4chee FPs noted (aimap v1.9.8 Insight #22 bug still open) |
| ~13:45 | Initial Stage-2 summary produced | Claimed "192 confirmed unauth across 10 platforms" — this was the overclaim |
| ~14:00 | Nick flagged the "100% provider catalog leak" framing as overclaim | Halted. Saved feedback_verify_before_claiming_exploitable.md. Began data-layer probe pass |
| ~14:15 | POST `/api/conversations` probe on OpenHands candidates | 61 of 100 reachable accept POST and return valid conversation_id; 16 advance to RUNNING+READY |
| ~14:30 | og:image + og:title FP-trap check on app-builder hits | bolt.diy 14, Dyad 22, gpt-engineer 11 all fail — all are generated outputs, not agents. 47 FPs removed |
| ~14:45 | Data-layer 401 probe on Sourcegraph, OpenDevin, Tabnine, Sourcebot, CodeGeeX | 80 more confirmed auth-on at data layer. 127 total FPs |
| ~15:00 | Insight #31 codified: app-builder brand in generated output | methodology/insight-31-app-builder-brand-in-output.md written |
| ~15:10 | Insight #30 codified: persistence without pressure | methodology/insight-30-persistence-without-pressure.md written (note: later renumbered, file title differs) |
| ~15:20 | VisorGraph cert-pivot: 11 named operators re-verified | Vertiv attribution refined: 136.119.115.212 SAN vertiv.ctx.tabnine.com (strict); 136.113.251.47 generic ctx.tabnine.com (adjacent) |
| ~15:30 | cortex analysis on Vertiv-Tabnine host | Authorization-context report written to ~/recon/code-assistants-2026-05-18/cortex-vertiv-tabnine.md |
| ~15:40 | VisorScuba run | 192/192 AI.C1 Critical — reflects the unfiltered set; re-scope to 65 verified queued |
| ~15:50 | BARE run | Sourcegraph 0.799 semantic match vs graphql introspection scanner (correct class; introspection gated per probe, so moot) |
| ~16:00 | VisorBishop -ip-shadow | 5 of 192 (2.6%) stacked services: node_exporter ×2, MinIO ×1, MLflow ×1, Postgres ×1 — below Insight #12 baseline |
| ~16:05 | VisorSD run | Code-assistant stack absent; 0/3 hits on Contabo + Hetzner ASNs despite ~12 known unauth OpenHands hosts there — coverage gap flagged |
| ~16:10 | Case study + ledger finalized | 192 events ingested; 127 need lifecycle update to archived with reason fp-stage-2-anchor |

---

## 5. Findings

> **Severity label policy (load-bearing):** Every tier label (LOW / MED / HIGH / CRITICAL) requires 100% verified evidence at that tier. Unverified observations are UNRATED. Inferred + hypothesized stacks do NOT promote to a tier — only verified components produce labels.

### 5.1 OpenHands — Unauth Sandbox Allocation at Population Scale

| Field | Value |
|---|---|
| **Name/ID** | 61 hosts accepting POST `/api/conversations`; 16 hosts advancing to RUNNING+READY |
| **Type** | AI coding agent — FastAPI surface |
| **Evidence** | POST `/api/conversations` returns HTTP 200 + valid `conversation_id` JSON on 61 hosts; 16 of those advance state to RUNNING + STATUS:READY within 60s |
| **Observed exposure** | Unauthenticated conversation creation + Docker sandbox allocation |
| **Severity** | HIGH — verified unauth API access + confirmed container provisioning |

**Potential impact:** Unauthenticated actor can allocate Docker sandbox compute on the operator's host. Sending a message (not tested per restraint ethic) would consume LLM provider quota. Sandbox escape from the container environment is hypothesized but unverified.

Named operators confirmed (VisorGraph): `ai-pipeline.dinpsykolog.se`, `xinrenxinshi.com`, `herrenlos.online`.

### 5.2 Sourcebot — One Repo-Enum Instance Verified

| Field | Value |
|---|---|
| **Name/ID** | 1 Sourcebot host (CanerTheOz operator) |
| **Type** | AI code-search — repository enumeration |
| **Evidence** | GET `/` returns repo listing including CanerTheOz repositories |
| **Observed exposure** | Unauthenticated repository enumeration |
| **Severity** | MED — data-layer access to indexed repository structure |

### 5.3 Sweep AI — 3 Hosts, Backend Exposed

| Field | Value |
|---|---|
| **Name/ID** | 3 Sweep AI hosts |
| **Type** | AI code-assistant — backend surface |
| **Evidence** | API routes reachable without authentication |
| **Observed exposure** | Limited unauth route access |
| **Severity** | MED |

### 5.4 Vertiv / Tabnine — Fortune-500 Internal Tooling Presence

| Field | Value |
|---|---|
| **Name/ID** | 136.119.115.212 (SAN: vertiv.ctx.tabnine.com) |
| **Type** | Enterprise AI code-completion — internal deployment |
| **Evidence** | TLS cert SAN strictly attributes to Vertiv; landing page reachable; `/api/*` returns 401 |
| **Observed exposure** | Internet-discoverable internal tooling; no data-layer access confirmed |
| **Severity** | LOW — information disclosure only; auth-on at data layer confirmed |

**Potential impact:** Confirms Vertiv (Fortune-500 critical infrastructure vendor) uses Tabnine internally. Cert-pivot candidate for spearphishing targeting. No code or data accessible.

### 5.5 False Positives Documented (UNRATED)

47 hosts across bolt.diy (14), Dyad (22), gpt-engineer (11) confirmed as generated-output FPs via og:image CDN check. These are applications built by the tools, not deployments of the tools themselves. 80 additional hosts confirmed auth-on at data layer (Sourcegraph 19, OpenDevin 2, Tabnine 5, Sourcebot 13, CodeGeeX 2). Total 127 of 192 original Stage-2 claims corrected.

---

## 6. Risk Assessment

### Overall Posture

The code-assistant tier splits cleanly. OpenHands ships with no auth concept on the FastAPI surface by default — 61% of reachable instances confirm this at population scale. Other platforms (Sourcegraph, Tabnine, OpenDevin, CodeGeeX) ship auth-on and enforce it consistently. The thesis is confirmed in both directions.

### Confidentiality

For OpenHands: conversation metadata and any data a user loads into a sandbox is at risk of access without authentication. Indexed repositories at risk in the Sourcebot case.

### Integrity

For OpenHands: an unauthenticated actor can create conversations and allocate sandboxes. Whether this enables payload injection into the agent's LLM context is hypothesized but not verified (requires sending a message — outside restraint ethic).

### Availability

Compute exhaustion via mass unauthenticated conversation creation is feasible against any of the 61 POST-accepting OpenHands hosts.

### Systemic Patterns

- OpenHands ships without an authentication layer on the FastAPI surface. This is not an operator misconfiguration at scale — it is a platform default propagated across 61% of the reachable population. Matches Insight #13 (shipping defaults are load-bearing).
- App-builder platform FP pattern (Insight #31) applies to any tool that embeds its brand in generated HTML. The category is broad: Vercel v0, Lovable, and similar tools will exhibit the same dork-evasion behavior.
- Persistence at 83.3% over 4 days (Insight #30) establishes the disclosure window. Without external pressure, findings remain actionable for weeks.

---

## 7. Recommendations

### R1 — OpenHands: Add authentication middleware

OpenHands should ship with authentication required by default on the FastAPI surface. Environment variable `OPENHANDS_AUTH_REQUIRED=true` should be the install default.

```bash
# Operator-side mitigation until platform ships auth:
# Run OpenHands behind a reverse proxy with HTTP basic auth
nginx_location_block="
location / {
    auth_basic \"OpenHands\";
    auth_basic_user_file /etc/nginx/.htpasswd;
    proxy_pass http://localhost:3000;
}
"
```

### R2 — Tabnine / Vertiv: Remove from public internet

Internal enterprise tooling with no public-facing purpose. Should bind to 127.0.0.1 or a private network segment only. ACM wildcard certs on public IPs for internal tooling is a systematic exposure pattern.

### R3 — Stage-2 verification: enforce API contract probing

For every platform in the code-assistant catalog, the Stage-2 verify probe must hit an agent-specific JSON endpoint and confirm response schema. Body text or title match alone is insufficient. The og:image FP-trap check is mandatory for any tool in the app-builder category.

### Future automation

```bash
# Run the agent-contract probe on every OpenHands candidate after harvest:
curl -sX POST https://<host>/api/conversations -H "Content-Type: application/json" \
     -d '{}' | jq -e '.conversation_id' >/dev/null && echo "UNAUTH:CONFIRMED"
```

Add og:image CDN-pattern check to aimap's code-assistant deep-enumerator as a first-pass FP filter before counting.

---

## 8. Limitations and Assumptions

| # | Limitation | Risk Implication |
|---|---|---|
| L1 | Analysis reconstructed from session notes (SESSION.md). Execution trace timestamps are approximate. | Minor sequencing uncertainty |
| L2 | 127 ledger events still flagged as AI.C1 Critical in VisorScuba — re-scope to verified-65 set not yet run | VisorScuba numbers overstate the verified population |
| L3 | 16 READY sandbox hosts: whether LLM credentials are wired in was not verified (write-tier action) | Actual quota-drain risk is hypothesized, not confirmed |
| L4 | 236 unreachable candidates not re-probed on alternate ports | Some moved-off-port hosts may still be reachable |
| L5 | TabbyML has no Shodan-visible surface — masscan-seeded port-8080 pass not run | Platform coverage gap |
| L6 | VisorSD has no code-assistant stack | Contabo + Hetzner ASN coverage of OpenHands population missed |
| L7 | aimap v1.9.8 dcm4chee catchall FP (Insight #22) produces ~38 misclassifications per run | Requires manual filter post-run until fix ships |

---

## 9. Proof of Concept (PoC) Illustrations

### PoC 1: OpenHands Unauthenticated Sandbox Allocation

**Scenario:** Unauthenticated actor creates a conversation and advances it to READY state on a production OpenHands host.

```
REQUEST:
  POST /api/conversations HTTP/1.1
  Host: <operator-host>:3000
  Content-Type: application/json
  Content-Length: 2

  {}

RESPONSE:
  HTTP/1.1 200 OK
  Content-Type: application/json

  {"conversation_id": "<uuid>", "status": "RUNNING", "state": "STATUS:READY"}
```

**Demonstrated:** A new conversation and Docker sandbox container were allocated on the operator's infrastructure without authentication in under 60 seconds. What this does NOT do: send any LLM message, consume quota, or exfiltrate any data.

### PoC 2: App-Builder FP Detection via og:image

**Scenario:** Distinguishing a generated bolt.diy app from a deployed bolt.diy agent.

```
REQUEST:
  GET / HTTP/1.1
  Host: <host>:3000

RESPONSE (FP — generated app):
  HTTP/1.1 200 OK

  <html>
    <meta property="og:image" content="https://bolt.new/static/og_default.png" />
    <title>My React App</title>
  </html>
```

**Demonstrated:** The og:image CDN URL (`bolt.new/static/`) identifies this as an application generated by bolt.diy, not the bolt.diy agent itself. The agent has no public HTTP surface; counting this host inflates the agent population count with zero true-positive value.

---

*Prepared by NuClide Research (Nicholas Kloster + Claude Sonnet 4.6) · Session 18 · 2026-05-18*
