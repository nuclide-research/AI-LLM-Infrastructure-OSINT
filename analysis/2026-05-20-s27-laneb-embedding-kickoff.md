# Session Analysis: Lane B Completion + Embedding-Services Survey Kickoff

**Date:** 2026-05-20
**Session:** 27
**Classification:** Internal / Research Use Only
**Toolchain:** Custom pipeline (institution-sweep.py · attribute.py · verify.py · geo-enrich.py · build-findings-json.py · build-findings-public.py) · julius (63-service LLM fingerprinter) · globe.gl · Shodan CLI/JAXEN · masscan · embed-probe.py · aimap v1.9.22 · menlohunt · svc-verify.py · Astro
**Repos updated:** AI-LLM-Infrastructure-OSINT (d23c273) · embedding-services survey staged for commit 314ecc1

---

## 1. Overview

### Objective

Two objectives, one session.

First: finish Lane B of the global university LLM-exposure hunt. Lane B is the per-institution `hostname:<domain>` port-filter sweep across all 10,224 recognized universities (Hipo dataset, 202 countries). Session 26 built the pipeline, completed Lane A, and left Lane B running at roughly 2,200 of 10,224 institutions. This session ran it to completion, verified the hosts, attributed them, geo-enriched the results, rebuilt the public feed, and updated the live globe.

Second: open Category 27, embedding services. Target class is text-embedding inference endpoints: Hugging Face Text Embeddings Inference (TEI), infinity-embedding, and custom FastAPI wrappers. The thesis question is the same one the program has tested 26 times: does an LLM-adjacent service ship reachable on the public internet without an authentication gate? Embedding APIs are the data-prep tier of a RAG pipeline. They have not been surveyed before.

The auth-on-default thesis is the lens for both. The university hunt measures it at academic-network scale. The embedding survey extends it to a service class that, as the kickoff showed, is largely invisible to passive Shodan discovery.

### Scope and Constraints

- **Target domains/IPs:** University hunt — per-institution `hostname:<domain>` across all 10,224 Hipo institutions (Lane B). Embedding survey — tier-2 cloud IP ranges (Scaleway / OVH / Hetzner / DigitalOcean), masscan ports 7997, 8000, 8001, 8002, 8080, 3000.
- **Allowed techniques:** Shodan harvest and host API, masscan port scan, safe HTTP GET marker probes, aimap service fingerprint, restraint-bound verify.py probes.
- **Ethical limitations:**
  - No data exfiltration — metadata and schema enumeration only
  - No destructive API calls
  - No use of discovered credentials
  - Data-tier probes: connection attempt only (does auth gate exist? no queries)
  - VisorAgent: controlled lab targets only, never operator hosts
  - Personal-device and wrong-category targets: archived without outreach

---

## 2. Environment and Tooling

### Claude Code Operation

Two-lane session. The university hunt is the carry-forward from Session 26: a resumable Python pipeline, run to completion from the `STATE.md` checkpoint, then a deterministic post-processing chain (verify, attribute, geo-enrich, build feeds). The embedding survey is a fresh category opening: masscan sweep, foreground HTTP probe, aimap batch dispatched to the background. Both lanes ran in one orchestrator session. No model-tier switching. The embedding aimap batch (6,273 IPs) was submitted as a background job and left running at session end.

The university-hunt findings also fed a service-verification pass. menlohunt had emitted bare-TCP and HTTP-200 findings against the university host set. svc-verify.py resolved the menlohunt port candidates by speaking the protocol. That verification work is what produced Insights #51, #52, and #53.

### Tools Used

| Tool | Role | Config notes |
|---|---|---|
| JAXEN | Shodan harvest (university Lane B); import mode for embedding masscan data | Embedding survey: `import --no-lookup`, Shodan search credits exhausted both keys |
| institution-sweep.py | Per-institution `hostname:<domain>` sweep, all 10,224 | Resumable; checkpointed; resumed from Session 26 STATE.md |
| attribute.py | IP → institution attribution via Hipo dataset | rDNS + cert CN + org-name match |
| verify.py | Restraint-bound marker probes per platform class | HTTP GET only; no write-tier; no auth bypass |
| geo-enrich.py | Institution → lat/lon for globe | Hipo geographic data |
| build-findings-json.py | Findings → canonical internal JSON feed | Lane A + Lane B merged |
| build-findings-public.py | Anonymizer — strips host / IP / institution | Lat/lon jittered approx 38km |
| julius | 63-service LLM fingerprinter | `~/go/bin/julius` |
| globe.gl | 3D globe visualization | Astro page in portfolio repo |
| masscan | Tier-2 cloud port sweep (embedding survey) | 6,544 open-port hits across approx 3.5M IPs |
| embed-probe.py | HTTP probe against masscan hosts | 0/6,526 confirmed; HTTP-only, stale-hit gap |
| aimap v1.9.22 | Service fingerprint — confirmed embedding host + 6,273-IP batch | 50 threads; batch dispatched to background, running at session end |
| menlohunt | GCP/cloud EASM on university host set | Emitted the inflated `port_open` and `gcp_metadata` findings later verified |
| svc-verify.py | Protocol-handshake verification of menlohunt port candidates | One read-only handshake per candidate; 74 candidates resolved |
| TOME | Platform corpus passive scan (embedding host) | 0 confidence — embedding-api and OVMS not yet in corpus |
| VisorPlus | Host enrichment (embedding host) | Hetzner AS24940, GreyNoise clean, 1 hostname |
| VisorGraph | Cert-pivot (embedding host) | HTTP-only on both ports; no TLS cert; no pivot surface |
| aimap-profile | Target classification (embedding host) | `unclassified`; bare VPS; research or personal deployment |
| BARE | Metasploit semantic ranking (embedding host) | No specific embedding module in corpus (closest 0.448) |
| VisorLog | Ledger ingest → nuclide.db | Session 26 entries committed in nuclide.db |
| VisorScuba | Compliance scoring | Post-ingest node assessment |
| VisorCorpus | Adversarial corpus generation (embedding host) | RAG-adjacent surface present |
| VisorSD | [—] not run — Shodan credits exhausted | |
| VisorGoose | [—] not run — no Ollama / TLD-sweep target this session | |
| recongraph | [—] not run — bare cloud IP, no domain pivot chain | |
| nu-recon | [—] not run — no Shodan API available | |
| cortex | [—] not run — no auth-context ambiguity on the confirmed host | |
| VisorRAG | [ethical-stop] controlled targets only | |
| VisorAgent | [ethical-stop] controlled lab targets only, never operator hosts | |
| VisorHollow | [—] not applicable — Windows-only | |

### Notable Configuration

- Public globe feed: no host, no IP, no institution name. Lat/lon jittered approx 38km (city-level). Country plus exposure-class explainers only. Existing `/map` page untouched.
- Lane B sweep is checkpointed per institution. Fully resumable; this session resumed it from the Session 26 checkpoint and ran it to 10,224.
- Embedding survey: Shodan search credits exhausted on both API keys (monthly reset pending). JAXEN ran `import --no-lookup`, ingesting masscan data without Shodan enrichment. Discovery dorks were unavailable for the whole survey.
- embed-probe.py is HTTP-only. HTTPS embedding services were not reachable. Hetzner `46.4.0.0/16` was absent from `tier2-ranges.txt`. Both logged as fix items.
- The single confirmed embedding host was found via the Shodan host API, not the masscan sweep.

---

## 3. Methodology

### Enumeration approach

**University Lane B.** Iterate every Hipo institution. For each, run `hostname:<institution_domain>` over the AI/LLM port set via Shodan. Checkpoint after each institution. Lane B catches plain-ccTLD and custom-domain universities that the Lane A academic-TLD dork matrix (`.edu` / `.ac.*` / `.edu.*`) misses entirely. Session 26 ran Lane A and started Lane B; this session finished Lane B: 15,985 hosts verified, 1,970 confirmed platforms, 1,970 findings across 55 countries. Merged with Lane A's 742, the corpus is 2,710 confirmed exposures across 71 countries and 206 institutions.

**Embedding survey.** Tier-2 cloud IP ranges swept with masscan across six candidate ports. Per-host HTTP probe with embed-probe.py. Confirmed hosts fingerprinted with aimap, then handed the full arsenal. A parallel Shodan host API lookup ran for known-pattern IPs. The masscan-to-probe path produced zero confirmations; the host API path produced the one confirmed host.

### Candidate identification

University platform fingerprints, per class: JupyterHub by HTML body plus title plus `/hub/login`; Ollama by port 11434 plus `/api/tags` JSON shape; Open WebUI by title plus uvicorn header plus `/api/version`; LiteLLM by `/openapi.json` schema; Streamlit by port 8501 plus Streamlit headers. Exposure classes: `signup-open` (registration POST returns 200 plus FIELD_ERROR), `llmjacking` (`/api/tags` returns `:cloud`-suffix entries), `litellm-openapi-public`, `jupyterhub-info-public`, `jupyterhub-auth-enforced`.

Embedding service fingerprint: root GET returns JSON carrying `embedding_dimension`, `model_name`, and `backend` fields. Conjunctive match, per Insight #6 — no single field alone identifies the service. BAAI/bge-m3 confirmed via `/openapi.json` and `POST /embed` response shape. OVMS backend confirmed via `GET /v1/config` returning model-version-status JSON.

### Validation checks

verify.py runs marker probes only. A status code is not identity (Insight #16); each platform class gets a content check.

This session sharpened the verification stage with three new insights, all codified from the university service-verification pass. They are the layer-4, layer-7, and attribution-stage statements of the same rule: a cheap signal is a candidate, not a finding.

- **Insight #51 — a port number names a candidate, not a finding.** menlohunt's `port_open` check did a bare TCP connect to 28 known ports and labelled each finding by the port's static severity table. Across 722 university hosts it emitted 113 CRITICAL/HIGH `port_open` findings. svc-verify.py ran one read-only protocol handshake per candidate (Redis PING, MongoDB isMaster, Elasticsearch `GET /`, MySQL greeting, PostgreSQL StartupMessage, and the rest) and resolved the 74 unique candidates. One was a genuine unauthenticated exposure: Redis 7.4.9 at a National Taiwan University host. A port-number CRITICAL is about 1.4% precise. The other 73 split into properly-secured services, version-banner-only, wrong-service-entirely, and firewall phantom hosts. The fix is structural: menlohunt commit `63b8bf1` makes `port_open` always INFO; severity is earned downstream by protocol verification.
- **Insight #52 — an HTTP 200 at an API path is not that API.** menlohunt's `gcp_metadata` check requested GCP metadata paths against the target's own public IP and confirmed the API on `status == 200 && body non-empty`. It fired 147 times across 37 university hosts. Every evidence body was an HTML document — the target's own web server answering for a path it does not implement. 0% precision. A web server returns 200 for paths it does not serve. The metadata API lives at link-local `169.254.169.254` and is unreachable by an external scan. Fixed at the source (menlohunt `b335dea`: require the `Metadata-Flavor: Google` response header, reject HTML bodies) and as a `winnow` screening signature. First insight to ship as executable code the day it was codified.
- **Insight #53 — a hostname label is not a cloud project identifier.** menlohunt's `checkFirebase` guessed Firebase project names from a host's reverse-DNS labels and probed `<label>.firebaseio.com`. It produced 4 CRITICALs from 2 real, public Firebase databases. Neither belonged to the universities. `earth` (lifted from `jupyterhub2.earth.ox.ac.uk`) is a music-gigs app. `marine` (from `manglillo.marine.usf.edu`) is an unrelated developer's project. A short generic word in a global namespace belongs to whoever registered it first. The exposure is real; the attribution is false. The corollary flagged `checkGCS` and `checkCloudRunFunctions`; a 12-of-12 sample of the survey's `gcs_public` buckets confirmed all of those were misattributions too. Fixed in menlohunt (`9b99efa`, `f6234fc`: `isBareLabel` skip) and as `winnow` signatures.

For the embedding host: `/` returns JSON with `embedding_dimension` confirms the FastAPI wrapper; `/openapi.json` inventories endpoints; a single `POST /embed {"text":"test"}` returning a 1024-float vector confirms live inference; `GET /v1/config` on port 9000 returning model-version-status confirms OVMS.

### Safeguards

No brute forcing, no privilege escalation, no data exfiltration, no write-tier operations, no credential use. svc-verify.py issued one read-only protocol handshake per candidate and nothing else — a Redis PING, not a KEYS scan; a MongoDB isMaster, not a collection dump. The Firebase and GCS marker reads used `?shallow=true` to confirm a database is public without reading its contents. On the embedding host, a single test vector confirmed live inference; the batch endpoint was not used for volume extraction; the OVMS backend was read at `/v1/config` and `/v1/models/{name}/metadata` only, never the raw TF Serving predict API. The public globe feed strips every operator-identifying field. VisorRAG and VisorAgent were deferred to controlled-target sessions.

---

## 4. Execution Trace

| Time | Action | Outcome / Decision |
|---|---|---|
| ~09:30 | Resume Lane B from Session 26 STATE.md checkpoint | institution-sweep.py restarted at approx 2,200/10,224 |
| ~11:00 | Lane B sweep completes all 10,224 institutions | 15,985 hosts verified |
| ~11:20 | verify.py marker probes across Lane B hosts | 1,970 confirmed platforms |
| ~11:40 | attribute.py runs Hipo institution attribution | Findings bound to institutions; per-country tally built |
| ~12:00 | geo-enrich.py + build-findings-json.py | Lane B: 1,970 findings / 55 countries. Merged total 2,710 / 71 countries / 206 institutions |
| ~12:20 | build-findings-public.py — anonymized feed rebuilt | Host / IP / institution stripped; lat/lon jittered approx 38km |
| ~12:40 | Globe feed redeployed to nuclide-research.com/map/universities/ | 71-country dot map live with Lane B data |
| ~13:00 | menlohunt findings on university host set triaged | 113 inflated `port_open` CRITICAL/HIGH; 147 `gcp_metadata` CRITICAL/HIGH; 4 `firebase_public` CRITICAL flagged for verification |
| ~13:30 | svc-verify.py: one protocol handshake per port candidate | 74 candidates resolved; 1 VERIFIED_UNAUTH (NTU Redis 7.4.9), 14 VERIFIED_AUTH, rest refuted/filtered/version-only |
| ~14:00 | gcp_metadata findings checked — all 147 evidence bodies are HTML | 0% precision; the target's own web server, not the metadata API |
| ~14:15 | firebase_public CRITICALs checked via `?shallow=true` marker reads | `earth` and `marine` are unrelated public projects; misattributed to Oxford and USF |
| ~14:30 | Insights #51 / #52 / #53 drafted; menlohunt fixes scoped | port_open → INFO; Metadata-Flavor header required; isBareLabel skip |
| ~15:00 | 3 commercial case studies finalized into the repo | claude-relay-chinese-reseller, llm-orchestration-rerun, sub2api-population |
| ~15:30 | Texas-universities dork catalog written | 66 TX institutions, 6 hostname-group system batches |
| ~16:00 | Category 27 opened: embedding-services survey kickoff | Tier-2 cloud ranges + ports 7997/8000/8001/8002/8080/3000 |
| ~16:20 | masscan: tier-2 cloud prefixes × 6 ports | 6,544 open-port hits; Hetzner 46.4.0.0/16 absent from ranges file |
| ~16:40 | embed-probe.py: 6,526 hosts probed | 0/6,526 confirmed — stale port-7997 hits, HTTP-only gap |
| ~16:55 | 46.4.204.44 surfaced via Shodan host API | Hetzner DE bare VPS; ports 8001 + 9000 + 22 |
| ~17:10 | Port 8001 probe: custom FastAPI embedding wrapper | `/` → JSON health (BAAI/bge-m3, 1024-dim); `POST /embed` → 1024-vector |
| ~17:20 | Port 9000 probe: OpenVINO Model Server backend | `/v1/config` → bge-m3 status; `/v2/` → version 2026.0.0 with git hash |
| ~17:30 | Candidate Insight #50 formulated — OVMS backend co-location | FastAPI wrapper and OVMS backend both exposed on separate ports |
| ~17:45 | aimap batch dispatched: 6,273 IPs × 39 ports, 50 threads | Background job; results deferred to the embedding-survey resume |
| ~18:00 | Lane B commit d23c273 written | OVERVIEW + index + 3 case studies + TX dorks + nuclide.db |
| ~18:10 | Embedding survey staged; runbook drafted | Carry-forward: parse aimap batch, run full arsenal on any new host |

---

## 5. Findings

> **Severity label policy (load-bearing):** Every tier label (LOW / MED / HIGH / CRITICAL) requires 100% verified evidence at that tier. Unverified observations are UNRATED. Inferred + hypothesized stacks do NOT promote to a tier — only verified components produce labels.

### 5.1 Global University Hunt — Lane B Complete (Corpus-Level Result)

| Field | Value |
|---|---|
| **Name/ID** | Lane B per-institution `hostname:<domain>` sweep, all 10,224 Hipo institutions |
| **Type** | Population-scale survey result |
| **Evidence** | 15,985 hosts verified → 1,970 confirmed platforms → 1,970 findings across 55 countries. Merged with Lane A: 2,710 confirmed exposures, 71 countries, 206 institutions |
| **Observed exposure** | Dominant class is JupyterHub auth-enforced (1,964). Exposure classes of concern: JupyterHub info-public (170), Open WebUI (33), Ollama unauth (30+), signup-open (21), LLMjacking cloud-proxy (16) |
| **Severity** | Corpus-level — not a single tier. Per-host verification status varies (see Insight #51, #52). Individual hosts carry their own labels below |

**Potential impact:** Aggregate map of exposed LLM infrastructure across the university sector. The corpus is the artifact. It is published, anonymized, on the live globe. Per-host severity is established only by per-host verification, not by the corpus count.

### 5.2 Embedding Survey Kickoff — Insight #50 Codified (OBSERVED)

| Field | Value |
|---|---|
| **Name/ID** | Category 27 embedding-services survey, first run |
| **Type** | Survey kickoff + structural pattern |
| **Evidence** | Tier-2 cloud masscan: 6,544 open ports, 0/6,526 confirmed as embedding services via probe. One host confirmed via Shodan host API. aimap 6,273-IP batch dispatched, running at session end |
| **Observed exposure** | Embedding tier is largely Shodan-dark: bare-JSON responses are not indexed by Shodan's HTML crawler; default ports overlap with many unrelated services. Active masscan plus an HTTPS-capable probe is required to find this class |
| **Severity** | OBSERVED — kickoff result; population size for the embedding tier is not yet measured |

**Potential impact:** The survey kickoff produced Insight #50 (OVMS backend co-location, see 5.4) and a publishable negative result: passive Shodan discovery does not find embedding services. The numbered population remains open pending the aimap batch.

### CRITICAL

No finding is labelled CRITICAL this session. No verified data-in-hand exposure was reached under the restraint policy. The university corpus contains hosts that warrant per-host CRITICAL review (cloud-proxy live, credential-leak-via-401 classes documented in the university OVERVIEW), but corpus membership is not per-host verification.

### HIGH

### 5.3 National Taiwan University — Unauthenticated Redis 7.4.9

| Field | Value |
|---|---|
| **Name/ID** | `140.112.107.222:6379` (sanitised to institution + service) |
| **Type** | Data-tier service — Redis key-value store |
| **Evidence** | svc-verify.py protocol handshake: `PING` → `+PONG`, no `AUTH` required. Redis 7.4.9. The one VERIFIED_UNAUTH result of 74 menlohunt port candidates |
| **Observed exposure** | Unauthenticated Redis reachable from the public internet on a university host |
| **Severity** | HIGH — verified unauthenticated access to a data-tier service via a protocol handshake. Not labelled CRITICAL: no data was read, data class is unknown |

**Potential impact:** An unauthenticated Redis instance permits read, write, and `CONFIG` operations to any caller. On a university host this can mean session-cache exposure, key enumeration, or `CONFIG SET dir` write-primitive abuse. NuClide verified only the absence of the auth gate (`PING` → `+PONG`); no keyspace was touched.

### MED

### 5.4 46.4.204.44 — Custom FastAPI Embedding API + OVMS Backend, Both Unauthenticated

| Field | Value |
|---|---|
| **Name/ID** | `46.4.204.44` ports 8001 and 9000 (Hetzner DE, AS24940, bare VPS) |
| **Type** | Embedding inference API (port 8001) + OpenVINO Model Server backend (port 9000) |
| **Evidence** | Port 8001: `GET /` → `{"status":"healthy","model_name":"BAAI/bge-m3","embedding_dimension":1024,"backend":"openvino-int8-throughput"}`; `POST /embed` → 1024-float vector; CORS `*`; no auth. Port 9000: `GET /v1/config` → `{"bge-m3":{"model_version_status":[...]}}`; `GET /v2/` → `{"name":"OpenVINO Model Server","version":"2026.0.0.4d3933c5c"}`; no auth |
| **Observed exposure** | Unauthenticated embedding extraction with no rate limiting. OVMS inference backend exposed directly on a separate port, bypassing the FastAPI wrapper's input validation |
| **Severity** | MED — verified unauthenticated API; no PII or credential access; compute abuse and architecture disclosure are the risks |

**Potential impact:** Any origin can extract BAAI/bge-m3 embeddings at the operator's bandwidth cost, with no attribution — requests look like normal inference traffic. The OVMS backend leaks model inventory, exact version string with git commit hash (CVE-matchable), and input tensor architecture (BERT-family, DT_INT64 dynamic shapes). This host anchors **Insight #50 — OVMS backend co-location**: when a custom FastAPI embedding wrapper is exposed, its OpenVINO Model Server backend is frequently exposed too, on a co-located port that needs its own firewall rule. Candidate status — one host; additional confirmations are needed before it is a numbered population pattern.

### LOW

### 5.5 University Hunt — Information-Disclosure Classes

| Field | Value |
|---|---|
| **Name/ID** | JupyterHub info-public (170 hosts) · LiteLLM openapi-public (2 hosts) · MySQL version-banner-only (3 hosts, from svc-verify.py) |
| **Type** | API endpoint / config-info disclosure |
| **Evidence** | JupyterHub hub config returns server list without auth; LiteLLM `/openapi.json` returns API schema without auth; svc-verify.py read 3 MySQL servers disclosing a version banner pre-auth |
| **Severity** | LOW — server list, routing schema, or version banner disclosed; no credential or data access |

**Potential impact:** Information disclosure that aids fingerprinting and target selection. No direct access.

### OBSERVED

### 5.6 University Hunt — JupyterHub Auth-Enforced (Dominant Class)

| Field | Value |
|---|---|
| **Name/ID** | JupyterHub auth-enforced — 1,964 hosts across the merged corpus |
| **Type** | Confirmed platform behavior |
| **Evidence** | `/hub/login` returns a login page; no bypass attempted or found |
| **Observed** | The dominant class by a wide margin. Direct supporting evidence for the auth-on-default thesis: the overwhelming majority of university JupyterHub deployments enforce authentication |

### 5.7 menlohunt False-Positive Classes — Quantified (OBSERVED)

| Field | Value |
|---|---|
| **Name/ID** | Scanner false-positive classes measured during the university verification pass |
| **Type** | Tool-state finding / verification-stage measurement |
| **Evidence** | 113 inflated `port_open` CRITICAL/HIGH → 1 real exposure (about 1.4% precision, Insight #51). 147 `gcp_metadata` CRITICAL/HIGH → 0 real (0% precision, all HTML bodies, Insight #52). 4 `firebase_public` CRITICAL → 0 belonging to the named host; 12-of-12 sampled `gcs_public` buckets misattributed (Insight #53) |
| **Observed** | A scanner produces candidates. Verification produces findings. Port number, HTTP 200, and hostname label are each a candidate-grade signal, never a finding-grade one. All three failure classes are now fixed at the source (menlohunt) and as `winnow` screening signatures |

---

## 6. Risk Assessment

### Overall Posture

Two distinct postures.

The university sector shows LLM exposure at scale: 2,710 confirmed platforms across 71 countries. The reassuring half of that number is that the dominant class — 1,964 JupyterHub instances — enforces authentication. The exposure of concern is the long tail: 30-plus unauthenticated Ollama instances, 33 Open WebUI, 21 signup-open platforms, 16 LLMjacking cloud-proxy hosts, and the verified data-tier exposure (NTU Redis). The pattern is systemic but not universal. Most institutions are doing the basic thing right; a consistent minority are not, and they are spread across every region.

The embedding tier shows a different posture: not "many exposed hosts" but "a discovery blind spot." The kickoff confirmed embedding services are largely invisible to passive Shodan survey. The single confirmed host is unauthenticated on two ports. Whether that generalizes is unmeasured — the aimap batch will inform it.

### Confidentiality

University corpus: LLMjacking instances expose operator Ollama Cloud quota; signup-open instances expose post-registration access to system prompts and conversation logs depending on platform; the NTU Redis exposes whatever its keyspace holds (unread, unknown class). Embedding host: model architecture and embedding dimensions disclosed without auth. Embeddings are vector representations — reversal is academically studied but not a direct practical risk on a general-purpose BAAI/bge-m3 model.

### Integrity

University corpus: low at the verification depth reached. No write-tier probes performed. The NTU Redis would, in principle, accept writes from any caller — not tested. Embedding host: no model-modification surface observed.

### Availability

University corpus: 16 LLMjacking instances permit quota exhaustion within Ollama Cloud plan windows. Embedding host: unauthenticated API with no rate limiting; a high-volume batch could exhaust Hetzner bandwidth. No availability impact was tested under the restraint policy.

### Systemic Patterns

- **Auth-on-default holds at academic scale.** 1,964 of the corpus's JupyterHub instances enforce auth. The thesis is confirmed: the secured posture is the majority. The exceptions are the finding.
- **The verification stage is load-bearing, and now quantified.** Insight #51 puts a number on it: a port-number CRITICAL is about 1.4% precise. Insight #52 puts a number on the layer-7 analogue: an HTTP-200-at-an-API-path CRITICAL was 0% precise on 147 findings. A scanner that derives severity from a cheap signal is not randomly wrong — it is systematically wrong, the same inflated label on every run. This is the program's central methodological claim, measured at population scale on the university corpus.
- **Attribution is a separate failure surface from verification.** Insight #53: a finding has two parts, the host and the exposure. menlohunt verified the exposure (a real public Firebase database) and failed the host (it belonged to an unrelated developer, not the university whose DNS carried the word). Getting the exposure right and the host wrong is still a wrong finding.
- **Non-standard ports defeat default-port filtering.** The university corpus documents Ollama on ports 5004, 3005, 12345, and 22222. Defenders who filter only the default port miss these.

---

## 7. Recommendations

### R1 — University LLMjacking and Signup-Open Classes

The 16 LLMjacking-class instances need port 11434 firewalled from external routing, or `ollama signout`. The 21 signup-open platforms need registration disabled in deployment config.

```bash
# Ollama — bind to loopback so the cloud-signin token is not publicly invocable:
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama

# Open WebUI — disable open registration:
ENABLE_SIGNUP=false
```

This removes the public quota-drain and uncontrolled-account-creation surfaces.

### R2 — NTU Unauthenticated Redis

```bash
# redis.conf — require a password and stop binding to all interfaces:
requirepass <strong-random-secret>
bind 127.0.0.1 ::1
# If Redis must be reachable across a trusted subnet, firewall 6379 to that subnet only.
```

An unauthenticated Redis is a write primitive, not only a read exposure. Closing the auth gate closes both.

### R3 — Embedding Host 46.4.204.44

```python
# FastAPI — require an API key on the embedding endpoints:
from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Depends(api_key_header)):
    if api_key != VALID_API_KEY:
        raise HTTPException(status_code=403)
```

```bash
# Firewall the OVMS backend — it should only be reachable from the wrapper:
ufw deny 9000
```

Per Insight #50, ports 8001 and 9000 are two separate firewall decisions. An operator who secures the wrapper but forgets the backend leaves the inference engine exposed.

### R4 — Scanner-Design Fix (Insights #51, #52, #53)

A scanner must not assign finding-severity from a cheap signal. Already shipped this session:

- menlohunt `63b8bf1`: `port_open` severity is always `INFO`; severity is earned by the protocol-verification stage.
- menlohunt `b335dea`: `gcp_metadata` fires only with the `Metadata-Flavor: Google` response header and a non-HTML body.
- menlohunt `9b99efa` / `f6234fc`: `checkFirebase` / `checkGCS` / `checkCloudRunFunctions` skip bare hostname labels via `isBareLabel`.
- `winnow` signatures `gcp-metadata-html`, `firebase-name-from-hostname-label`, `gcs-name-from-hostname-label` screen these classes in any scanner's output.

### Future automation

```bash
# Globe refresh after any university-hunt re-run:
python3 build-findings-json.py && python3 geo-enrich.py && python3 build-findings-public.py
# Portfolio submodule pull redeploys the globe on push.

# Embedding-service discovery once Shodan credits reset:
jaxen dork 'http.html:"embedding_dimension"' --download --limit 500
jaxen dork 'http.html:"Infinity Emb"'        --download --limit 500
jaxen dork 'http.html:"OpenVINO Model Server"' --download --limit 500
# Then aimap batch on the downloaded IPs; full arsenal on confirmed hosts.

# Standing posture check for an operator's own public IPs:
aimap -list your-public-ips.txt -ports 8001,9000,11434,6379,3000 -o report.json
```

---

## 8. Limitations and Assumptions

| # | Limitation | Risk Implication |
|---|---|---|
| L1 | Analysis reconstructed from case studies, sweep data, and git history. SESSION.md has no Session 27 header; execution trace timestamps are approximate. | Trace is a faithful reconstruction, not a logged record |
| L2 | Lane B finding counts are corpus-level; per-host verification status varies — see Insight #51 / #52. | Corpus membership is not a per-host severity label; only verified hosts carry tier labels |
| L3 | Lane C (bare-IP netblock sweep) was not built. | University-allocated IP ranges with no domain pivot are not covered; some deployments are missed entirely |
| L4 | verify.py applies marker probes only; per-host deep enumeration was not run at corpus scale. | Exposure depth (data class, chain potential) is not assessed for most of the 2,710 |
| L5 | Embedding survey: Shodan search credits exhausted; JAXEN ran import-only. | Discovery dorks were not executed; the embedding-tier population size is unmeasured |
| L6 | embed-probe.py is HTTP-only; Hetzner `46.4.0.0/16` was absent from `tier2-ranges.txt`. | The masscan path found 0 hosts; the one confirmed host came from the Shodan host API. True embedding population is understated |
| L7 | The embedding aimap batch (6,273 IPs) was still running at session end. | Full tier-2 cloud fingerprint results are deferred to the embedding-survey resume |
| L8 | Insight #50 (OVMS co-location) rests on one confirmed host. | Candidate status; additional confirmations are needed before it is a numbered population pattern |
| L9 | Write-tier operations were not tested anywhere (restraint ethic). | Integrity impact (Redis writes, model modification) is assessed conceptually, not verified |

---

## 9. Proof of Concept (PoC) Illustrations

> PoCs use minimal, read-only interactions. No operator data extracted. No credentials used. No exploit payloads. Demonstrate existence and risk conceptually only.

### PoC 1: Lane-B University LLM Unauthenticated Probe

**Scenario:** The Lane B pipeline identifies an unauthenticated Ollama instance on a university network using a single marker probe, no model invocation.

```
REQUEST (verify.py marker probe):
  GET /api/tags HTTP/1.1
  Host: <university-host>:11434

RESPONSE:
  HTTP/1.1 200 OK
  Content-Type: application/json

  {
    "models": [
      {"name": "llama3.3:70b", "size": 42520413916},
      {"name": "deepseek-v3.1:cloud", "size": 0}
    ]
  }
```

**Demonstrated:** The `/api/tags` endpoint answers without authentication, so the Ollama instance is publicly reachable. A `size: 0` `:cloud`-suffix entry signals an Ollama Cloud signin state — any caller could direct quota at the operator's cloud subscription. What this does NOT do: invoke a model, consume quota, send a `/api/chat` request, or interact with the Ollama Cloud infrastructure. The probe reads the model list and stops.

### PoC 2: Embedding-Service Identity Probe

**Scenario:** A researcher confirms a host runs a custom embedding service, with one read-only GET, before any extraction is attempted.

```
REQUEST:
  GET / HTTP/1.1
  Host: <operator-host>:8001

RESPONSE:
  HTTP/1.1 200 OK
  Content-Type: application/json

  {
    "status": "healthy",
    "model_loaded": true,
    "model_name": "BAAI/bge-m3",
    "embedding_dimension": 1024,
    "backend": "openvino-int8-throughput"
  }
```

**Demonstrated:** The conjunction of `model_name`, `embedding_dimension`, and `backend` in the root JSON identifies a custom FastAPI embedding wrapper (Insight #6: a conjunctive match, not a single field). The `backend` value names an OpenVINO runtime, the cue to probe port 9000 for a co-located OVMS server (Insight #50). What this does NOT do: POST to `/embed`, extract a vector, use the batch endpoint, or touch the OVMS backend. Identity is confirmed from the health endpoint alone; severity is assigned only after a separate, single, read-only confirmation probe.

---

*Prepared by NuClide Research (Nicholas Kloster + Claude Sonnet 4.6) · Session 27 · 2026-05-20*
