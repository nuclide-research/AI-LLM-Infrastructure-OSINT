---
title: Code assistants — category 09 population follow-up survey 2026-05-18
---

# Code assistants (category 09), population follow-up 2026-05-18

_NuClide Research · 2026-05-18 · four-day delta against the 2026-05-14
baseline, with a verification-stage correction late in the session._

## Summary

This is the second pass on the AI code-assistant tier. The first pass on
2026-05-14 ran the full chain on 233 hosts and found 54 unauth across 8
platforms. Four days later we re-harvested and ran the chain again. Late in
the session, a Stage-2 verification pass at the data-layer corrected the
headline numbers down by 66 percent and produced two new insights.

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7004, K7044, K7054, S7068, S7070, S7075, T5858, T5904, T5919
- **733 (AI Risk & Ethics Specialist):** K7051, T5868, T5893
- **overlap (Common AI KSATs (all 5 roles)):** K1158, K1159, K22, K6311, K6900, K6935, K7003, S7065

<!-- ksat-tag:auto-generated:end -->

**Verified numbers** (data-layer probe + agent API contract anchor):

- **65 verified-unauth code-assistant hosts** across 3 platforms (down from
  192 originally claimed across 10 platforms)
- **OpenHands carries the survey**: 61 hosts accept unauth POST
  `/api/conversations`; 16 of those allocated a sandbox container in READY
  state without auth, in under 60 seconds
- **127 of 192 original claims were false positives** at the data-layer.
  Some were app-builder generated outputs (bolt.diy, Dyad, gpt-engineer
  — 47 hosts). Others were login pages of platforms with auth-on-default
  (Sourcegraph 19, OpenDevin 2, etc.)
- **Insight #30 codified** (persistence without pressure) — 83.3% of 2026-05-14
  OpenHands baseline still unauth 4 days later
- **Insight #31 codified** (app-builder brand in generated output) — Stage-2
  verify probes anchoring on body text catch the AGENT'S OUTPUT, not the
  agent; the correction is to anchor on the agent's API contract

**Verified vs Inferred vs Hypothesized**, per the post-session feedback
discipline:

- **Verified** (primary-source probe response): OpenHands 61 POST accepts +
  16 RUNNING sandboxes; Sourcebot 1 (CanerTheOz repo enum); Sweep AI 3
  (Sweep backend exposed); 11 cert-pivot operator attributions; OpenDevin
  agent-gated; Sourcegraph all "Private mode required"; Tabnine data-layer
  401; all 47 app-builder hits are generated-output FPs
- **Inferred but not verified**: that the 16 sandbox-READY hosts have
  working LLM provider credentials wired in (would require sending a paid
  message to confirm — outside the restraint ethic)
- **Hypothesized**: that sandbox-escape is reachable from a started
  conversation; that any per-host conversation would call the operator's
  LLM provider if a message were sent

## Thesis fit (corrected)

The auth-on-default thesis is **confirmed** on OpenHands at population
scale. Of 100 confirmed real OpenHands hosts, 61 (61%) accept unauth POST
that creates a conversation; of those, 16 (16% of the total, 26% of the
POST-accepting subset) advanced to RUNNING + READY sandbox state without
authentication. OpenHands ships with no auth concept on the FastAPI
surface by default; the operator is expected to wrap it in an auth proxy;
at population scale, most do not.

The thesis is **also confirmed for the other platforms** but in a
different direction than originally claimed: Sourcegraph, OpenDevin,
Tabnine, and CodeGeeX all enforce auth on the data layer at population
scale. Sourcegraph's "Private mode requires authentication" gate fires on
19 of 19. OpenDevin's `/api/conversations` returns 401 on 2 of 2.
Tabnine's `/api/*` returns 401 on 5 of 5. The catalog (landing page,
`/health`, sometimes `/api/options/*`) is reachable; the data is not.
That is the auth-on-default thesis working in its positive form — these
platforms ship secure defaults and operators inherit them.

## Discovery — Stage 0

Name-first harvest with the JAXEN paginator. The 2026-05-14 query catalog
held up under re-run — 13 of the 14 verified dorks returned populations
in the same range (a few percent variance).

| dork | hits | unique IPs |
|---|---|---|
| `http.title:"OpenHands"` | 208 | 190 |
| `http.html:"openhands"` | 241 | 215 |
| `http.title:"Sourcegraph"` | 36 | 34 |
| `http.title:"Dyad"` | 38 | 30 |
| `ssl.cert.subject.cn:"tabnine"` | 30 | 30 |
| `http.html:"sourcebot"` | 23 | 22 |
| `("bolt.diy" OR "bolt.new")` | 26 | 26 |
| `http.html:"sweepai"` | 18 | 15 |
| `"gpt-engineer" port:8081` | 17 | 16 |
| `"Refact" port:8081` | 11 | 11 |
| `http.html:"OpenDevin"` | 5 | 4 |
| `http.title:"OpenDevin"` | 3 | 3 |
| `http.title:"Refact"` | 2 | 2 |
| `http.title:"CodeGeeX"` | 2 | 1 |

Cross-dork unique total: **405 candidates**. **This is the raw harvest, not
the finding count.** The verification stage below is the load-bearing
filter.

## Verify — Stage 2 (corrected — load-bearing failure surfaced late)

The original Stage-2 probe anchored on "platform name appears in response
body." This produced a 192-host "confirmed unauth" set that, on a
follow-up data-layer probe, collapsed to 65.

The failure was conjunctive-matcher discipline: the anchor predicate was
a single substring test (`"openhands" in body` for example), which is
exactly the Insight #6 failure mode at the verify stage. Body-text anchors
catch platforms' login pages, landing pages, and — for app-builder tools
— the HTML of the apps they generate.

### Data-layer probe results per platform

| Platform | Original Stage-2 claim | Data-layer verified | What the verify probe actually established |
|---|---|---|---|
| OpenHands | 100 | **61 POST-accepts** + 16 sandbox-READY | POST `/api/conversations` with empty body returns 200 + `conversation_id`; sandbox container provisions in <60s |
| OpenDevin | 2 | 0 data-layer | `/api/options/agents` returns 200 (catalog leak) but `/api/conversations` returns 401 "Missing Authorization header" |
| Sourcegraph | 19 | 0 data-layer | All 19 return HTTP 401 "Private mode requires authentication" on GraphQL introspection POST |
| Sourcebot | 14 | 1 data-layer | 12 return 401 on `/api/repos`; 1 leaks operator's GitHub repo list (`CanerTheOz/*`); 1 had non-API URL match |
| bolt.diy | 14 | 0 (all FP) | All 14 are apps GENERATED by bolt.new — `og:image=https://bolt.new/static/og_default.png` proves it. Real titles include "Tron Vanity Address & Contract Admin", "Vortex Exchange", "Secure Data Anonymization Platform" |
| Dyad | 22 | 0 (all FP) | All 22 carry `<title>dyad-generated-app</title>` — the OUTPUT, not the agent. Two also matched on unrelated companies named "Dyad" (a scientific tool, a design agency) |
| Tabnine | 5 | 0 data-layer | All 5 are real Tabnine Context Engine instances; `/health` returns `{"status":"ok",...}` JSON unauth; `/api/*` returns 401 |
| Sweep AI | 3 | 3 | 3 real Sweep backend APIs exposing 2 routes: `/backend/api/feature-flags` (POST), `/backend/plugin_auth` (GET) |
| gpt-engineer | 11 | 0 (all FP) | All 11 are a Russian "ИЗБА" commercial-proposals SPA; `gpt-engineer` string in HTML is from og:image CDN URL `storage.googleapis.com/gpt-engineer-file-uploads/og-images/...` |
| CodeGeeX | 2 | 0 data-layer | Admin SPA with React catch-all routing; `/api/extensions/codegeex` returns HTML chrome (not the API) |
| **TOTAL** | **192** | **65** | 66% of original claims were FPs |

### OpenHands POST verification (the substantive finding)

For the 100 OpenHands hosts that passed Stage-2:

| POST /api/conversations status | Count |
|---|---|
| 200/201 (conversation actually created) | **61** |
| 401/403 (auth required) | 6 |
| 405 (method not allowed) | 1 |
| Other / unreachable | 32 |

Of the 61 created conversations, follow-up `GET /api/conversations/{id}`:

| Sandbox runtime state | Count |
|---|---|
| RUNNING + `STATUS$READY` | **16** |
| `STATUS$STARTING_RUNTIME` | 15 |
| `STATUS$BUILDING_RUNTIME` | 5 |
| STARTING (no runtime status reported) | 23 |
| STOPPED before runtime started | 13 |
| None / unreachable | 9 |

**Sandbox-READY hosts include named operators**:
- `https://34.51.151.73` — `ai-pipeline.dinpsykolog.se` (Swedish online psychology service). Sandbox provisioned.
- `https://101.200.30.30` — `xinrenxinshi.com` (Chinese HR SaaS). Sandbox provisioned.
- `http://150.129.9.251:3000` — `herrenlos.online`. Sandbox provisioned.

DELETE cleanup on the 61 created conversations: 45 returned 200, 4 returned
500, 12 were unreachable. The DELETE accepts at the API level but is a
**soft-delete** — 53 of 61 post-DELETE re-GETs still returned the
conversation record. Operator-side database cleanup is required to fully
purge.

### What was NOT verified (carrying-forward)

- That the 16 sandbox-READY hosts have working LLM provider credentials.
  Sending a message would have verified this but would have burned
  operator quota; outside the restraint ethic.
- That the sandbox is escapable. The Docker container exists and is
  marked READY; whether the agent can write outside the container or pivot
  to the host depends on operator-chosen volume mounts.
- That GET `/api/secrets` returns secret names (would require explicit
  per-host probe; one host sampled returned the schema-described
  `CustomSecretWithoutValueModel` shape with no values present)

## Cross-survey delta (2026-05-14 → 2026-05-18)

The 2026-05-14 baseline identified 30 unauth OpenHands hosts via
`/api/v1/settings`. Today's verification identified 93 unique unauth
OpenHands hosts (61 POST-confirmed today + 32 partial-state hosts).
Intersection on the unauth set:

| | count | share |
|---|---|---|
| 5/14 baseline still unauth today | 25 | 83.3% of baseline |
| 5/14 baseline disappeared | 5 | 16.7% of baseline |
| New unauth since 5/14 | 68 | 73.1% of today's set |
| Population growth | 30 → 93 | 3.1× in 4 days |

**No external pressure was applied to the 2026-05-14 set** (no disclosures
sent, no extortion targeting the platform class). The 25 persistent
operators are the empirical basis for Insight #30 (persistence without
pressure).

## Attribute — Stage 3 (VisorGraph cert-pivot, re-verified)

11 named-operator attributions held up under same-day re-resolution. Plus
two refinements caught during re-verify:

| Host | Cert SANs (re-verified) | Operator |
|---|---|---|
| `136.119.115.212` | `vertiv.ctx.tabnine.com` | **Vertiv Holdings Co. (NYSE: VRT)** — Fortune-500 critical-infrastructure thermal management. Tabnine Context Engine on internet. NO data-layer access confirmed; landing page + `/health` only |
| `136.113.251.47` | `ctx.tabnine.com` only (generic) | **Tabnine shared infrastructure OR adjacent customer** — not strictly Vertiv. Originally claimed as Vertiv but cert SAN is generic; needs follow-up to identify the tenant |
| `101.200.30.30` | `*.xinrenxinshi.com`, `xinrenxinshi.com` | Chinese HR-tech SaaS |
| `101.201.107.165` | `*.renruikeji.cn`, `renruikeji.cn` | Chinese SaaS with multiple subdomains |
| `103.168.54.5` | `apptripticket.monamedia.net` | Vietnamese travel ticketing, via Mona Media |
| `106.14.107.134` | `*.dachengrobot.com`, `dachengrobot.com` | Chinese robotics |
| `109.205.177.140` | `dev-api.whyaml.com`, `dev.whyaml.com` (Contabo VM hostname `vmi3039515.contaboserver.net`) | Startup dev infra |
| `125.17.55.153` | `Apps.acceleronsolutions.io`, `www.Apps.acceleronsolutions.io` | Acceleron Solutions |
| `144.126.128.220` | `c.cyberit.com.br`, `cloud.cyberit.com.br`, **`cloud.germinax.com.br`** (different tenant), `crypto.c.cyberit.com.br`, `hotel.c.cyberit.com.br`, `las.c.cyberit.com.br`, `rdp.cyberit.com.br`, `web03.cyberit.com.br`, `webproxy03.cyberit.com.br` | Brazilian IT consultancy — **multi-tenant TLS, 9 subdomains across 2 customers** |
| `150.129.9.251` | `*.herrenlos.online`, `herrenlos.online` | German site |
| `154.12.250.234` | `*.alphabotvips.com`, `alphabotvips.com` (Contabo VM `vmi2897012.contaboserver.net`) | Trading-bot SaaS |
| `157.173.112.228` | `api.workready.africa` (Contabo VM `vmi2995374.contaboserver.net`) | African workforce SaaS |

**Vertiv attribution scope corrected**: 1 host strictly attributed (`136.119.115.212`
with `vertiv.ctx.tabnine.com` SAN), 1 host adjacent (`136.113.251.47` with
generic `ctx.tabnine.com` SAN). Disclosure should be Tabnine-routed for the
adjacent host; Vertiv-direct for the strictly-attributed host.

**cyberit multi-tenant scope**: the 9-SAN cert covers two customer
domains. Disclosure to cyberit covers both.

## Classify — Stage 4 (aimap-profile, full 179 hosts)

| Category | Count | Share |
|---|---|---|
| Unclassified (no signal) | 142 | 79.3% |
| Commercial SaaS | 17 | 9.5% |
| Research lab / HPC | 10 | 5.6% |
| Commercial staging | 9 | 5.0% |
| Education | 1 | 0.6% |
| Multi-tenant flag | 7 | 3.9% |
| Honeypot flag | 0 | 0% |
| Has WHOIS org attached | 95 | 53.1% |

These classifications were run on the 179 unique IPs from the Stage-2
"confirmed unauth" set — 65 of those 179 hold up at the data-layer.
Re-running classification scoped to only the 65 verified hosts is a
follow-up.

## Stage 6 — VisorScuba, BARE, VisorCorpus

- **VisorScuba**: 192 / 192 ingested nodes scored 0 / 10 on the AI baseline
  with AI.C1 Critical (unauth AI service). Note: the score is correct for
  the 65 verified, **overcounted** for the 127 FPs. Re-scoring scoped to
  65 is queued.
- **BARE** (semantic match against 3,904 Metasploit modules): per-platform
  top-1 module scores. Note: Sourcegraph 0.799 against
  `auxiliary_scanner_http_graphql_introspection_scanner` is correct as a
  semantic match but the scanner would have come back negative on these
  hosts — schema is auth-gated per the verification probe.

| Platform | Top match | Score | Verdict (corrected) |
|---|---|---|---|
| Sourcegraph | `auxiliary_scanner_http_graphql_introspection_scanner` | 0.799 | scanner is the right tool but would return empty: introspection gated |
| OpenHands | `exploits_multi_http_apache_apisix_api_default_token_rce` | 0.544 | first-party authz (verified by direct POST chain) |
| Sourcebot | `auxiliary_admin_http_gitstack_rest` | 0.469 | adjacency-class |
| Others | various | < 0.45 | first-party authz / no match |

- **VisorCorpus**: 137 strict-profile cases built; no in-survey use against
  operator hosts.

## Stage 5 ledger

192 events ingested to `data/nuclide.db` via VisorLog. **The 127 FPs need
status update to `archived` with reason `fp-stage-2-anchor`**. Operator
re-scoping is a follow-up task.

## Other arsenal tools — null and partial results

Per the methodology, every tool runs against the survey set and the result
is recorded. Today's full-arsenal record:

- **JAXEN**: 15 dorks, 405 unique IPs ingested to `empire.db`. [primary]
- **aimap v1.9.8**: 405 targets, 300 services found, 154 unauth, 156
  critical at aimap-confidence. Subset overlap with verified-65 is partial;
  aimap matchers and our verify-probe matchers disagree on the FP class
  (aimap classified some app-builder generated outputs as
  `dcm4che/dcm4chee-arc` catchall FPs — Insight #22 bug still present in
  v1.9.8). [primary, with known matcher issue]
- **aimap-profile**: 179/179 classified. [primary]
- **VisorGraph cert-pivot**: 28/30 probed, 11 named operators verified
  same-day. [primary]
- **VisorBishop**: 192-URL re-prober + IP-shadow; 5/192 (2.6%) stacked
  services found. Lower than Insight #12 baseline. [primary]
- **VisorSD**: 0/3 stack hits on Contabo + Hetzner across 6 stacks. No
  `code-assistant` stack exists. [methodology gap recorded]
- **VisorGoose**: .gov density baseline run (15 .gov hits for Ollama, no
  code-assistant dorks in catalog). [coverage gap recorded]
- **menlohunt**: 3 GCP hosts, 0 GCS/Firebase/metadata leaks, all UDP
  51819-51821 WireGuard noise. [null result recorded]
- **nu-recon**: AWS host `100.49.85.6` deep-read. Hostname
  `ec2-100-49-85-6.compute-1.amazonaws.com`, ports 80+443,
  `openhands-sticky` session cookie. Last-modified `2025-10-10` — host
  running same image 7 months. [primary]
- **recongraph**: not run (duplicate-of VisorGraph for this survey).
- **VisorPlus**: equivalent-of, components run discretely.
- **VisorLog**: 192 events ingested. [primary]
- **VisorScuba**: 192/192 AI.C1 Critical (over-counts FPs; re-scope needed).
- **BARE**: 192 findings ranked (over-counts FPs; re-scope needed).
- **VisorCorpus**: 137 strict-profile cases.
- **VisorAgent**: controlled-target run, no operator hosts hit.
- **VisorRAG**: not run.
- **VisorHollow**: not applicable (Windows-only).
- **cortex**: Vertiv-Tabnine authorization-context analyzed (`cortex-vertiv-tabnine.md`).
- **JS-bundle extract**: 0 CDN-fronted hosts in confirmed set; pattern
  doesn't apply.

## Methodology — what this survey adds

Two codified insights:

**Insight #30 — persistence without pressure**. Cross-survey delta on
unauth code-assistants over a 4-day window shows 83.3% operator
persistence. Compared to Insight #28's 71.6% wipe in 24h for
extortion-targeted ES, the rate constant differs by ~85x depending on
attacker pressure. Operators in low-attacker-pressure ecosystems do not
self-remediate.

**Insight #31 — app-builder tools brand the OUTPUT, not the AGENT**. The
Stage-2 verify probe in this survey anchored on body text. For app-builder
tools (bolt.diy, Dyad, gpt-engineer), the brand string appears in the
generated apps' HTML, not the agent's. Shodan dorks catch the OUTPUT
population. 47 of 192 original hits in this survey were app-builder FPs.
The fix is to anchor on agent API contract (specific JSON shape from a
known endpoint), not body text.

## Honest negative space (updated)

- **Stage-2 anchor predicate is the load-bearing methodology surface** and
  it was wrong this survey. The fix is in Insight #31. Stage-2 verify
  must test agent API contract, not body substring. Failure surfaces only
  on follow-up data-layer probe — there is no automated check that catches
  it during the first pass yet.
- **aimap v1.9.8 still has the dcm4che-arc catchall FP** (Insight #22) —
  38 false positives in this survey. Fix outstanding.
- **VisorSD has no `code-assistant` stack**.
- **VisorGoose has no code-assistant dorks** in its catalog.
- **TabbyML remains Shodan-dark**; only masscan-seeded port-8080 pass
  would surface it.
- **Continue.dev has no server footprint** — Shodan-unmappable.
- **236 unreachable candidates** from the original harvest still need a
  follow-up fingerprint pass.

## Disclosure queue (verified scope)

The disclosure-ready set is now 65 verified hosts, not 192:

1. **Vertiv (strictly attributed: `136.119.115.212`) + Tabnine
   coordinated**. Vertiv: notify directly. Tabnine: vendor disclosure with
   the adjacent host `136.113.251.47` (generic `ctx.tabnine.com` SAN) as
   well — Tabnine routes that one. Severity: "internet-discoverable
   internal tooling presence" (NOT confirmed source-code exfil — Tabnine
   data layer is gated).
2. **10 other named code-assistant operators** from the cert-pivot table
   for OpenHands hosts. Each gets a direct WHOIS-org disclosure.
3. **The 16 OpenHands hosts with READY sandboxes** are the highest-impact
   disclosure tier — primary-source evidence of provisioned compute
   accepting unauth control. Include cleanup conversation_ids.
4. **The 25 OpenHands hosts persistent since 5/14** — re-verify within 7
   days per Insight #30, then send.
5. **The 68 OpenHands hosts new since 5/14** — standard discovery →
   notify.
6. **Aliyun + Contabo + Hetzner + DigitalOcean** abuse — bulk
   hosting-provider notifications.
7. **Sourcebot operator (CanerTheOz)** — single-host notification for the
   exposed `/api/repos` (low severity).
8. **Sweep AI operators** (3) — limited exposure, info-disclosure tier.

## Toolchain provenance

```
JAXEN (Shodan paginator) → harvest 405 IPs across 15 dorks
  ↓
aimap v1.9.8 (Phase 1+3) → 300 services found, dcm4che FP class present (Insight #22)
  ↓
codeassist_verify.py (Stage-2 conjunctive marker probe) → 192 "confirmed"
  ↓  ← Insight #31 caught here: 127 FPs at data-layer
verify_post_auth.py + verify_full_chain.py + per-platform probes
  → 65 verified at data-layer, 61 OpenHands POST-accept, 16 sandbox-READY
  ↓
VisorGraph cert-pivot (Stage 3) + same-day re-verify → 11 operators
  ↓
aimap-profile (Stage 4) → 17 SaaS + 9 staging + 10 research-lab disclosable
  ↓
VisorBishop --ip-shadow (Stage 5) → 5/192 stacked services
  ↓
VisorLog ingest → 192 events (127 need fp-archive status update)
  ↓
VisorScuba assess (Stage 6) → AI.C1 Critical on all 192 (over-counts; re-scope)
  ↓
BARE (Stage 6 exploit-rank) → Sourcegraph 0.799 (scanner gated by Private mode)
  ↓
VisorCorpus 137 cases · VisorAgent controlled-target · cortex Vertiv doc ·
  VisorSD/VisorGoose/menlohunt nulls recorded · nu-recon AWS deep-read
  ↓
Codify case study + Insight #30 + Insight #31
```

## See also

- 2026-05-14 baseline: `~/recon/2026-05-14-code-assistants/`
- Insight #28: `methodology/insight-28-survey-shelf-life-exposure-to-extortion.md`
- Insight #29: `methodology/insight-29-overwhelming-prior-state-look-at-deltas-not-snapshots.md`
- Insight #30 (new): `methodology/insight-30-persistence-without-pressure.md`
- Insight #31 (new): `methodology/insight-31-app-builder-brand-in-output.md`
- Vertiv-Tabnine cortex doc: `~/recon/code-assistants-2026-05-18/cortex-vertiv-tabnine.md`
- Verification artifacts:
  `~/recon/code-assistants-2026-05-18/verify_post_auth.jsonl`,
  `verify_full_chain.jsonl`,
  `verify_sourcegraph_full.jsonl`
- Query catalog: `shodan/queries/09-code-assistants.md`
- Restraint ethic: nuclide-research.com `/stack` "How we test" blocks
