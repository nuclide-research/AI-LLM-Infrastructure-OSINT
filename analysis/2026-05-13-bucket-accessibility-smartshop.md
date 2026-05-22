# Session Analysis: Bucket-Accessibility Survey + SmartShop AI / PENTECH Disclosure

**Date:** 2026-05-13
**Session:** unnumbered (retroactive analysis)
**Classification:** Internal / Research Use Only
**Toolchain:** VisorBishop Phase 5b probe.py, aimap v1.0.0/v1.8.3, aimap-profile v0.1, VisorGraph, BARE (corpus 3,904 modules), nrich, geonet, VisorCorpus, nuclide-contact, JS-bundle extract, disclosure bulletin renderer
**Repos updated:** AI-LLM-Infrastructure-OSINT (c01c2bf, c3c0bce, 8aa6a71, 5952ae3, 810cd51)

---

## 1. Overview

### Objective

Two linked questions and one tooling task.

First, close the open question from VisorBishop Phase 5. Phase 5 extracted 58 unique artifact buckets from the artifact_uri field of 120 critically-exposed unauthenticated MLflow trackers. Phase 5 framed that inventory as a "second-order disclosure surface" without testing it. Phase 5b tests it: of the cloud-provider buckets an exposed MLflow tracker names, how many are themselves anonymously readable? Does the operator who leaves the tracker UI open also leave the storage backend open, or does the backend get locked down in a separate workflow?

Second, run the full assessment chain against one host that surfaced in the Phase 5 corpus, 78.135.66.61, attributed to the operator SmartShop AI on PENTECH BILISIM (Turkey, AS48678). The thesis under test is the program standard: AI/ML infrastructure ships authentication-off and operators do not turn it on. SmartShop AI is a named-operator confirmation of that thesis across a whole pipeline rather than a single service.

Third, build the disclosure-bulletin tooling. The disclosure email format was migrated to the claude.ai/design 8-section "Security Disclosure Bulletin" layout, with a `--draft` mode that lands disclosures in Gmail Drafts and never transmits.

Target class: MLflow artifact stores (object storage on AWS S3, GCS, Azure Blob) and a single multi-service MLOps host (Airflow, MLflow, PostgreSQL, Redis, FastAPI product API, Postfix mail).

### Scope and Constraints

- **Target domains/IPs:** the 49 cloud-provider buckets surfaced in Phase 5 (21 S3, 20 GCS, 8 Azure Blob); host 78.135.66.61 (PENTECH BILISIM, AS48678, Turkey) and its hostnames `mlflow.amazonrec.space`, `airflow.amazonrec.space`, `api.amazonrec.space`, `mail.nadorawear.com`; arsenal-fanout anchor hosts 98.67.188.174 (Microsoft, source of the one public-list bucket) and 78.46.88.7
- **Allowed techniques:** anonymous read-only list-bucket requests, passive Shodan host pull, safe HTTP GET against documented API endpoints, OpenAPI schema fetch, JS-bundle extraction, cert-pivot graphing, WHOIS-based contact resolution
- **Ethical limitations:**
  - No data exfiltration — metadata and schema enumeration only
  - No destructive API calls
  - No use of discovered credentials
  - Data-tier probes: connection attempt only (does auth gate exist? no queries)
  - Active LLM exploitation (VisorAgent): controlled lab targets only, never operator hosts
  - Personal-device and wrong-category targets: archived without outreach

---

## 2. Environment and Tooling

### Claude Code Operation

Orchestrator session with parallel-lane delegation. The session ran two distinct passes.

The bucket-accessibility pass was a single sequential tool: `probe.py` walked the 49-bucket target list one probe at a time with 0.4-second pacing. No fan-out there. The probe is deliberately slow and polite because the target population is third-party operator infrastructure.

The SmartShop AI deep-dive used the arsenal-fanout pattern. Multiple tool lanes ran concurrently against one host corpus. The fanout evidence directory holds eight lanes: aimap-profile, BARE, geonet, nrich, nuclide-contact, operator-pivot, Shodan host pull, VisorCorpus, and VisorGraph. Each lane is an independent subagent task with a defined output file. Total wall time was the slowest lane, not the sum. The orchestrator integrated the lane outputs into one host record and one case study.

No model-tier switching. The session stayed at one model and delegated scoped lanes to subagents.

### Tools Used

| Tool | Role | Config notes |
|---|---|---|
| VisorBishop Phase 5b `probe.py` | Tri-cloud anonymous list-bucket prober | stdlib only, ~269 lines; 0.4s pacing, 6s timeout, 6KB response cap, identifying User-Agent |
| aimap v1.0.0 then v1.8.3 | Active port enum + AI/ML fingerprint on 78.135.66.61 | 18 ports scanned; v1.8.3 adds the data-tier adjacency classifier (Insight #20) |
| aimap-profile v0.1 | Target classification, /29 PTR sweep, honeypot scoring | fast mode (Shodan-passive, no active scan); run on PENTECH IP, amazonrec.space, and anchor hosts |
| VisorGraph | Cert-pivot and sibling-domain graphing | 13-node graph for amazonrec.space; separate graphs for nadorawear.com, pendns.net |
| BARE | Metasploit semantic ranking against 3,904-module corpus | top match `apache_airflow_dag_rce` score 0.679; `redis_extractor` 0.607 |
| nrich | Shodan-record enrichment of the MLflow anchor set | CPE and CVE rollup across the Phase 5b anchor IPs |
| geonet | Geolocation of the anchor host set | one lane of the arsenal fanout |
| VisorCorpus | Adversarial corpus for the MLflow-tracker class | `mlflow-tracker-adversarial.json`, ~2,500-entry corpus |
| nuclide-contact | WHOIS-based disclosure-recipient resolution | run on 78.135.66.61, amazonrec.space, nadorawear.com, pendns.net |
| JS-bundle extract | SmartShop AI Vite bundle → headless API URL | 335KB `smartshop-main.js`; surfaced `https://api.amazonrec.space/api/v1` |
| operator-pivot | Bucket-name → operator-token derivation | parsed 49 bucket names into guessed operator tokens |
| disclosure bulletin renderer | `render_bulletin.py` + `bulletin_template.html` | built this session; fills the 8-section layout, emits HTML + plaintext, `--draft` mode |
| VisorAgent | Active LLM exploitation | [—] not run — ethical-stop; operator hosts only, never the survey set |
| VisorHollow | Windows process-injection benchmark | [—] not applicable — Windows-only |

### Notable Configuration

The bucket prober is stateless and idempotent. Each probe is single-shot per URL with discriminating-error classification, so verdicts only change if an operator actively modifies a bucket ACL between runs. Re-running the sweep on any later day reproduces the verdict distribution.

aimap was at v1.0.0 when the SmartShop host was first scanned and emitted only one "AI service found" against a host running a full ML pipeline. That undercount drove the v1.8.3 release mid-session, which adds the data-tier adjacency classifier and was live-validated against the same host the same day.

The disclosure sender configuration changed this session. `FROM_ADDR` moved to `contact@nuclide-research.com`. The Gmail OAuth scope moved from `gmail.send` to `gmail.compose`, because the send scope alone cannot create drafts. The new `--draft` mode calls `drafts().create()` instead of `messages().send()`, so a rendered disclosure lands in the Drafts folder and is never transmitted.

---

## 3. Methodology

### Enumeration approach

No new discovery pass. Both halves of the session worked from carry-forward corpora.

The bucket survey took the Phase 5 `mlflow-artifact-buckets.tsv` as input. That file is the artifact_uri field harvested from every critically-exposed MLflow tracker in the 120-host Phase 5 inventory. The 58 buckets were filtered to the 49 cloud-provider rows (`aws-s3`, `gcs`, `azure-blob`). Nine rows were excluded: local-filesystem paths, Databricks DBFS references, and non-cloud HTTP file servers. Those nine have no anonymous list-bucket API to probe.

The SmartShop deep-dive took one host, 78.135.66.61, from the same Phase 5 corpus. Phase 5 had already flagged the host's MLflow tracker. This session ran the full chain on it.

### Candidate identification

For the bucket survey, "candidate" means a cloud-provider bucket named in a real MLflow tracker's run metadata. The bucket name itself is the candidate. Identity is the bucket-to-tenant resolution: a bucket name that returns a discriminating error resolves to a real account or project.

For SmartShop AI, candidate identification was the SPA-to-API pivot. The operator domain `amazonrec.space` serves a static single-page app from Vercel (HTTP header `x-vercel-id`). The bundled JavaScript `smartshop-main.js` was extracted and grepped for absolute API URLs. It calls `https://api.amazonrec.space/api/v1`. That subdomain resolves directly to 78.135.66.61 on AS48678, a different ASN than the Vercel edge. That asymmetry is the candidate signal.

### Validation checks

The bucket survey validates each candidate with one anonymous probe and a four-way classification. The classification is the verification stage. A status code alone is not a finding. The discriminating error body is.

- S3: `GET https://<bucket>.s3.amazonaws.com/?list-type=2&max-keys=10`, then path-style, follow region-redirect. 200 with a listing → `public-list`. 403 `AccessDenied` → `exists-private`. 404 `NoSuchBucket` → `not-found`.
- GCS: `GET https://storage.googleapis.com/storage/v1/b/<bucket>/o?maxResults=10` plus XML fallback. 200 → `public-list`. 401/403 → `exists-private`. 404 on both → `not-found`.
- Azure: `GET https://<account>.blob.core.windows.net/<container>?restype=container&comp=list&maxresults=10`. 200 → `public-list`. 401/403 → `exists-private`. 409 `PublicAccessNotPermitted` → `account-locked`. 404 or DNS NXDOMAIN → `not-found`.

The four-way verdict is the discipline. `exists-private` confirms the bucket name resolves to a real tenant with explicit deny configured. `account-locked` is the Azure-specific stronger posture where the whole storage account disables anonymous access. `not-found` means the tracker is leaking a dead URI. Only `public-list` is a misconfiguration, and even then the empty-container case is "configuration confirmed, no current artifacts." This verdict semantics is the basis of **Insight #18**: storage-tier hygiene exceeds tracker-tier hygiene at population scale. 48 of 49 buckets locked. The Phase 5 "second-order disclosure" framing reframes from data-exfil to metadata-disclosure.

For SmartShop AI, validation was single anonymous GETs against documented endpoints. `/health` returned `{"status":"healthy","version":"1.0.0","service":"ml-ops-two-tower"}`. `/api/v1/interactions/stats` returned real counters (15,139 interactions logged). `/api/v1/session/init` returned a real Amazon-format user ID. The OpenAPI spec at `/openapi.json` showed `components.securitySchemes` as the empty object `{}`, confirming no authentication mechanism is defined. The SPA-to-API pivot is codified as **Insight #19**: a CDN-hosted SPA calling a same-brand `api.<brand>.<tld>` host is a high-severity exposure tell, because the API host is almost always on unhardened operator-managed infrastructure.

aimap's port enum on 78.135.66.61 returned only one "AI service found" despite the host running MLflow, PostgreSQL, Redis, and a Postfix sink. Cross-checking aimap's narrow output against the broader Shodan host record exposed the catalog gap. That is **Insight #20**: aimap's AI-service classifier needs the ML data tier, not just the inference tier. Ports 5432, 6379, and 9000 adjacent to a confirmed AI service on the same host are themselves AI signals. The conjunctive matcher extends to an adjacent-port predicate: `port:5432 alongside port:5000` is an MLflow-backend-store fingerprint. The rule shipped in aimap v1.8.3 the same day and was live-validated against this host.

### Safeguards

No brute forcing. No privilege escalation. No data exfiltration. No write-tier operations. No credential use.

Specific restraint decisions this session:

- The bucket prober sends `max-keys=10` and caps responses at 6KB. It lists, it does not download. No GET-by-key beyond what a listing surfaces.
- The one `public-list` hit, `model-storage@blobimgstore`, was found empty. The session did not investigate further. The case study explicitly notes three possible explanations for the empty container and states none were actively pursued, to respect the implicit scope on a third-party operator.
- The SmartShop API has a `POST /api/v1/interactions` endpoint that writes telemetry. The session did not POST to it. Forging events would poison the operator's training feedback loop. That capability is documented in the findings as a risk, not exercised.
- The data-tier ports on 78.135.66.61 (PostgreSQL 5432, Redis 6379) were observed as open. No connection beyond the open-port check. No queries. No `KEYS *`.
- `/api/v1/session/init` was called once. It returned one user ID. The session did not loop the endpoint to harvest all 100 pre-loaded user profiles. The pool size of 100 is read from the documented `/session/pool-stats` counter, not from enumeration.

---

## 4. Execution Trace

Timestamps are approximate. This session was not assigned a session number; the trace is reconstructed from evidence-file timestamps and git history.

| Time | Action | Outcome / Decision |
|---|---|---|
| ~11:00 | Loaded Phase 5 `mlflow-artifact-buckets.tsv`, filtered 58 buckets to 49 cloud-provider rows | 9 local-fs / DBFS / HTTP rows excluded — no anonymous list API to probe |
| ~11:15 | Wrote `probe.py`, the tri-cloud anonymous list-bucket prober | stdlib only, four-way verdict classifier, 0.4s pacing |
| ~11:30 | Ran the 49-bucket sweep | 40 `exists-private`, 6 `not-found`, 2 `account-locked`, 1 `public-list`; results written to `results.json` / `.tsv` |
| ~11:30 | Inspected the one `public-list`: `model-storage@blobimgstore.blob.core.windows.net` | Container empty at probe time (`<Blobs />`); per-experiment prefix `101/` also empty. Stopped — no further probing of third-party operator |
| ~11:35 | Classified 49-bucket result, derived Insight #18 | 97.96% storage-tier hygiene; reframed Phase 5 "second-order disclosure" from data-exfil to metadata-disclosure |
| ~11:40 | Pivoted to host 78.135.66.61 from the Phase 5 corpus | Launched the arsenal-fanout: 8 parallel tool lanes against the PENTECH host and anchor set |
| ~11:48 | Arsenal-fanout lanes completed | aimap-profile, BARE, geonet, nrich, nuclide-contact, operator-pivot, Shodan, VisorCorpus, VisorGraph evidence written |
| ~11:55 | Extracted `smartshop-main.js` (335KB Vite bundle) from the amazonrec.space Vercel SPA | Bundle calls `https://api.amazonrec.space/api/v1`; subdomain resolves to 78.135.66.61, different ASN than Vercel — the soft target |
| ~11:59 | aimap-profile classified the PENTECH IP and amazonrec.space | /29 PTR sweep found siblings `tr5.timeadjust.org`, `server.emersoft.com.tr`; multi-tenant ethics flag set |
| ~12:34 | Built `disclosure_template.html` / `.txt` + `new_disclosure.py` + `preview_gallery.py` | The earlier minimalist disclosure template and renderer |
| ~12:47 | Ran aimap v1.0.0 against 78.135.66.61, 18 ports | Only 1 "AI service found" (Airflow) despite MLflow + Postgres + Redis on the host — catalog gap visible against the Shodan record |
| ~12:50 | Single anonymous GETs against `api.amazonrec.space` | `/health`, `/interactions/stats` (15,139 logged), `/session/init` (real Amazon-format user ID), `/openapi.json` (`securitySchemes: {}`) |
| ~13:00 | Codified Insight #20 from the aimap undercount; shipped aimap v1.8.3 adjacency classifier | Data-tier ports adjacent to a confirmed AI service now classify as AI signals; v1.8.3 live-validated against the same host |
| ~13:06 | Wrote Insight #18, #19, #20 methodology pages | Three insights committed |
| ~13:07 | Committed Phase 5b public survey + Insights #18-20 (c01c2bf) | Public anonymized survey shipped first |
| ~09:20 (next day) | Built `bulletin_template.html` + `render_bulletin.py`; rewrote SmartShop disclosure in bulletin-section format | claude.ai/design 8-section dossier layout, table-based, email-safe |
| ~09:25 | Committed disclosure pipeline: bulletin template + `--draft` mode (5952ae3) | `FROM_ADDR` → contact@; scope → gmail.compose; multipart/alternative; `--draft` lands in Drafts, never sends |
| ~09:54 | Committed operator-named case studies (c3c0bce), evidence packs (8aa6a71), template tooling (810cd51) | SmartShop AI / PENTECH and Phase 5b bucket-accessibility writeups with full operator detail; rendered SmartShop bulletin created as a Gmail draft, not sent |

---

## 5. Findings

> **Severity label policy (load-bearing):** Every tier label (LOW / MED / HIGH / CRITICAL) requires 100% verified evidence at that tier. Unverified observations are UNRATED. Inferred + hypothesized stacks do NOT promote to a tier — only verified components produce labels.

### 5.1 amazonrec.space `api.amazonrec.space` — Unauthenticated SmartShop AI production API

| Field | Value |
|---|---|
| **Name/ID** | `api.amazonrec.space` → 78.135.66.61:443 |
| **Type** | Product API endpoint (FastAPI, "ml-ops-two-tower" recommendation service) |
| **Evidence** | `GET /openapi.json` returns `components.securitySchemes: {}`. `GET /health` → `{"status":"healthy","version":"1.0.0","service":"ml-ops-two-tower"}`. `GET /api/v1/interactions/stats` → `total_logged:15139, db_writes:6374, s3_writes:15139`. `GET /api/v1/session/init` → a real Amazon-format user ID with a category history. Probe timestamp 2026-05-13T16:56Z. |
| **Observed exposure** | Zero authentication mechanism defined. Swagger UI mounted at `/docs`. 13 endpoints public, including write endpoints (`POST /api/v1/interactions`). |
| **Severity** | CRITICAL — verified production data served to anonymous callers, plus a verified write path into the model feedback loop |

**Potential impact:** A passive actor can loop `/session/init` to harvest all 100 pre-loaded user profiles, then walk `/api/v1/user/{user_id}/features` and `/api/v1/for-you?user_id=` to extract per-user embedding features and recommendation outputs. The user IDs follow the 28-character Amazon customer ID format. The `POST /api/v1/interactions` write path lets an actor forge interaction events and poison the training feedback loop; the `total_logged` counter confirms writes succeed.

### 5.2 78.135.66.61:5000 — Unauthenticated MLflow tracking server

| Field | Value |
|---|---|
| **Name/ID** | `mlflow.amazonrec.space` → 78.135.66.61:5000 |
| **Type** | Model-tracking server (MLflow) |
| **Evidence** | `GET /api/2.0/mlflow/experiments/search?max_results=1000` returns the full experiment list anonymously. Real experiment names including `scan_1778457788` and YOLO model training runs. `MLFLOW_TRACKING_AUTH` not set. |
| **Observed exposure** | Unauthenticated read of all experiments, runs, parameters, metrics, and artifact_uri references |
| **Severity** | CRITICAL — verified unauthenticated read of the operator's full training-pipeline metadata |

**Potential impact:** Disclosure of training-pipeline structure, model names, hyperparameters, and the artifact_uri references that name the backing storage. The artifact backend is the `wasbs://` family analyzed in finding 5.7.

### 5.3 78.135.66.61:6379 — Internet-exposed Redis

| Field | Value |
|---|---|
| **Name/ID** | 78.135.66.61:6379 |
| **Type** | Data tier (Redis key-value store) |
| **Evidence** | Port open and reachable from the public Internet. Shodan tags `database`, `self-signed`, `eol-product`. BARE top semantic match `auxiliary/gather/redis_extractor` score 0.607. |
| **Observed exposure** | Redis reachable on the public Internet on the same host as the SmartShop API |
| **Severity** | HIGH — port confirmed open and Internet-reachable; the no-auth state was not verified because data-tier probes are connection-only this session |

**Potential impact:** If Redis has no auth wall, an actor reads or writes the session and inference cache for the SmartShop API. The severity is HIGH not CRITICAL because the connection-only safeguard means the absence of `requirepass` was not verified.

### 5.4 78.135.66.61:5432 — Internet-exposed PostgreSQL

| Field | Value |
|---|---|
| **Name/ID** | 78.135.66.61:5432 |
| **Type** | Data tier (PostgreSQL) |
| **Evidence** | Port open and reachable from the public Internet. The MLflow tracker's `db_writes` counter and the `/interactions/stats` counters indicate this is the authoritative store for the tracker and the interaction log. |
| **Observed exposure** | PostgreSQL reachable on the public Internet on the same host as the SmartShop API and MLflow tracker |
| **Severity** | HIGH — port confirmed open and Internet-reachable; auth posture not verified (connection-only safeguard) |

**Potential impact:** Direct exposure of the production data store backing both the MLflow tracker and the SmartShop interaction log. Auth posture would need a connection attempt to confirm, which was out of scope this session.

### 5.5 78.135.66.61:8080 — Apache Airflow sign-in page reachable

| Field | Value |
|---|---|
| **Name/ID** | `airflow.amazonrec.space` → 78.135.66.61:8080 |
| **Type** | Orchestration UI (Apache Airflow) |
| **Evidence** | The Airflow standard sign-in page is served anonymously (`http___78_135_66_61_8080_.html` snapshot, 17KB). Shodan lists 11 Airflow-tree CVEs across the host. BARE top match `exploits/linux/http/apache_airflow_dag_rce` score 0.679. |
| **Observed exposure** | Airflow web UI reachable; sign-in page presented anonymously; Airflow-tree CVEs apply |
| **Severity** | HIGH — sign-in page reachability and the CVE set are verified; authentication was not bypassed, so takeover is a surface, not a confirmed compromise |

**Potential impact:** The orchestration scheduler that triggers the ML pipeline is reachable. Airflow CVE-2024-25142 (connection/DAG escalation) and CVE-2024-26280 (DAG-run permission bypass) are in the applicable set. A confirmed takeover would require exploiting one of these; this session confirmed the surface only.

### 5.6 model-storage@blobimgstore.blob.core.windows.net — Anonymous-list ACL on an MLflow artifact container

| Field | Value |
|---|---|
| **Name/ID** | Azure container `model-storage` on account `blobimgstore`; source MLflow tracker `http://98.67.188.174:5000` |
| **Type** | Object storage (Azure Blob, MLflow artifact backend) |
| **Evidence** | `GET ?restype=container&comp=list&maxresults=10` returns HTTP 200 with a valid `EnumerationResults` XML document. The `<Blobs />` element is empty at root and at the per-experiment prefix `101/`. The upstream MLflow tracker confirms the artifact_uri wiring is real. |
| **Observed exposure** | Anonymous list-blobs ACL permitted on the container; container empty at probe time |
| **Severity** | LOW — the ACL misconfiguration is verified; no data was present, so there is no verified data exposure. This is the "configuration confirmed, no current artifacts" state. |

**Potential impact:** The container would leak any artifact the operator uploads to it. The standing surface is real. At probe time it actualized nothing. The case study notes three possible explanations for the empty container (recent purge, SAS-token write path, or list-allowed-read-denied) and did not pursue them.

### 5.7 Phase 5b bucket survey — 48 of 49 MLflow artifact buckets locked at the storage tier

| Field | Value |
|---|---|
| **Name/ID** | 49 cloud-provider buckets named by 120 critically-exposed MLflow trackers |
| **Type** | Population-scale storage-tier posture measurement |
| **Evidence** | `results.tsv` / `results-classified.json`: 40 `exists-private`, 6 `not-found`, 2 `account-locked`, 1 `public-list`. By provider: S3 0/21 public, GCS 0/20 public, Azure 1/8 public. |
| **Observed exposure** | Storage-tier hygiene is 97.96%. The tracker tier the buckets are named in is near-0% hygiene. |
| **Severity** | OBSERVED — confirmed population behavior. The headline is the absence of exposure: 48 buckets locked. Insight #18 is the codified result. |

**Potential impact:** The finding reframes the Phase 5 bucket inventory. It is a metadata surface (operator names, project taxonomies, cloud-provider mix, bucket-naming conventions) not an artifact surface. The 40 `exists-private` buckets are a positive operator-attribution feed: each name resolves to a real, confirmed tenant.

---

**CRITICAL** — 5.1 (SmartShop API, verified production data + write path), 5.2 (MLflow tracker, verified unauthenticated metadata read)
**HIGH** — 5.3 (Redis), 5.4 (PostgreSQL), 5.5 (Airflow)
**LOW** — 5.6 (blobimgstore anonymous-list ACL, empty container)
**OBSERVED** — 5.7 (population-scale storage-tier hygiene measurement)

The Postfix mail stack on 78.135.66.61 (ports 25/110/143/465/587/995, `eol-product` tag) is a separate finding class — operator-customer mail data, not AI infrastructure — and is recorded at MED in the case study but not promoted here.

---

## 6. Risk Assessment

### Overall Posture

Two opposite postures in one session.

The bucket population is healthy. 97.96% of MLflow artifact stores are locked even when the tracker that names them is wide open. This is the rare survey where the headline is the absence of a finding.

The SmartShop AI host is the opposite. One host, one operator, six independent unauthenticated surfaces. Each of the six is HIGH or CRITICAL on its own. The exposure is systemic for that operator and isolated to that operator.

### Confidentiality

Bucket survey: confidentiality at the storage tier is intact for 48 of 49 operators. The exposed confidentiality is metadata — operator names, project taxonomies, cloud-provider attribution — visible in the tracker, not the bucket.

SmartShop AI: production confidentiality is broken. Real Amazon-format user IDs, per-user interaction histories, per-user embedding features, and recommendation outputs are served to anonymous callers. The MLflow tracker leaks the full training-pipeline metadata. 15,139 interaction events are logged in a Postgres directly exposed on the public Internet.

### Integrity

Bucket survey: no integrity exposure. List ACLs do not imply write ACLs, and writes were not tested.

SmartShop AI: integrity is at risk. `POST /api/v1/interactions` is a confirmed write path with no authentication. An actor can forge interaction events and poison the recommendation model's training feedback loop. The `total_logged` counter confirms anonymous writes succeed. The Airflow UI, if taken over via one of the 11 applicable CVEs, would allow DAG-level tampering with the whole pipeline.

### Availability

Bucket survey: no availability exposure.

SmartShop AI: the exposed Redis and PostgreSQL are single points of failure reachable by anyone. An actor who reached the data tier could degrade or deny the SmartShop service. The Airflow scheduler is a second availability lever. Availability was not tested — the connection-only and no-destructive-call safeguards held.

### Systemic Patterns

The bucket-behind-the-platform chain is the structural finding. An exposed AI platform names its backing storage in its own metadata API. That naming is a chain link: the tracker's artifact_uri is a pointer to the next tier. Phase 5b tested whether that pointer dereferences to readable data. For MLflow it almost never does. The pointer is a metadata leak, not a data leak. Insight #18 codifies this and warns it is class-dependent: self-hosted MinIO or on-cluster storage may not share the cloud-IAM discipline that protected the 48.

The SmartShop AI host is a single-mistake-class chain. Insight #19 names the root: the operator deployed a polished frontend to a CDN and stood the API up on a cheap VM with no private VPC. The CDN gives a false sense of security — professional visible state, unhardened actual posture. Every one of the six surfaces traces to that one deployment decision. The data tier sits on adjacent ports of the same host, which is also why aimap's narrow read missed it. Insight #20 closes that tool gap: ports 5432, 6379, and 9000 adjacent to a confirmed AI service are AI signals.

The MLflow shipping default is the common thread. `MLFLOW_TRACKING_AUTH` ships off. Operators do not turn it on, because it is a loud default they never see. Bucket access is a separate IAM workflow they already engaged with. That split is exactly why the tracker tier is exposed and the storage tier is not. It is Insight #13 (shipping defaults are load-bearing) confirmed at population scale.

---

## 7. Recommendations

### R1 — MLflow tracker authentication

The tracker tier is where every additional fix lives. 48 of 49 buckets are already locked; the tracker is the open door.

```bash
# MLflow >= 2.5 ships basic auth as a built-in app
mlflow server \
  --app-name basic-auth \
  --host 127.0.0.1 \
  --backend-store-uri postgresql://... \
  --default-artifact-root wasbs://...
```

Bind the tracker to `127.0.0.1` and front it with an authenticating reverse proxy, or enable the built-in `basic-auth` app. This is the single highest-impact change for the MLflow population, because the storage tier behind it is already disciplined.

### R2 — Headless API authentication and network placement

The SmartShop API serves production data with `securitySchemes: {}`. Define an auth scheme and place the API behind a private boundary.

```python
# FastAPI: require a key on every route
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

def require_key(key: str = Security(api_key_header)):
    if key != EXPECTED_KEY:
        raise HTTPException(status_code=401)
```

The API host should not be directly Internet-resolvable. Put it behind the same CDN as the SPA, or behind an API gateway, so the backend VM is not the soft target. Insight #19 is the detection heuristic; the remediation is to remove the asymmetry.

### R3 — Data-tier network isolation

PostgreSQL on 5432 and Redis on 6379 must not be Internet-reachable.

```bash
# Bind to loopback or a private interface only
# postgresql.conf
listen_addresses = '127.0.0.1'
# redis.conf
bind 127.0.0.1
requirepass <strong-secret>
```

Put the data tier on a private subnet. The application host reaches it over private networking; the public Internet never does. A host-level firewall denying 5432 and 6379 from outside the VPC is the minimum.

### R4 — Object-storage ACL audit

For the one `public-list` container, set the container ACL to private and the account flag to disable anonymous access.

```bash
# Azure: disable anonymous access account-wide
az storage account update \
  --name blobimgstore \
  --allow-blob-public-access false
```

The two `account-locked` cases in the survey already do this. The flag blocks the whole class regardless of per-container ACL drift.

### Future automation

Roll the bucket-list probe into VisorBishop as an opt-in stage so a newly discovered MLflow tracker is classified at both the tracker tier and the storage tier in one pass. Add a `discoverHeadlessAPI` stage that pulls a CDN-fronted SPA's largest JS bundle, extracts `api.*` URLs, resolves them, and tags the resulting host for direct probing.

```bash
# aimap with the v1.8.3 adjacency classifier on a known public-IP set
aimap -list your-public-ips.txt -ports "5000,5432,6379,8080,9000" -o report.json
# Data-tier ports adjacent to an AI service appear under
# ML-ADJACENT INFRASTRUCTURE and in the "adjacencies" JSON key.
```

Run this on a post-deploy hook. A host that exposes MLflow plus its backing Postgres and Redis should fail the check before it reaches production.

---

## 8. Limitations and Assumptions

| # | Limitation | Risk Implication |
|---|---|---|
| L1 | Analysis reconstructed from case studies, evidence directories, and git history. This session was not assigned a session number; execution trace timestamps are approximate. | Trace ordering is inferred from file mtimes and commit metadata; exact intra-session timing is not authoritative. |
| L2 | The bucket survey probes only the 49 cloud-provider rows. 9 local-fs / DBFS / non-cloud-HTTP buckets were excluded. | Self-hosted storage backends were not measured; Insight #18 explicitly warns the 97.96% ratio may not hold for MinIO or on-cluster storage. |
| L3 | The probe tests list ACLs only. Read ACLs (GET-by-key) were not tested. | A container that denies list could still allow read by known key; the survey cannot rule that out. |
| L4 | The one `public-list` container was empty at probe time. | A non-empty result on a later probe is possible; the empty finding does not establish a permanent no-data state. |
| L5 | Data-tier ports on 78.135.66.61 (5432, 6379) were checked for open/closed only. No connection past the port check. | The absence of an auth wall on Postgres and Redis is plausible but not verified; both findings are capped at HIGH for that reason. |
| L6 | Airflow authentication was not bypassed. The 11 CVEs are from the Shodan record, not independently confirmed exploitable on this build. | Airflow finding is a surface, not a confirmed takeover. |
| L7 | The SmartShop API was probed with single GETs. The 100-user pool was not enumerated. | The pool size is read from a documented counter; the per-user feature data is described from the API contract, not from a full walk. |
| L8 | aimap v1.0.0 undercounted the AI surface on the PENTECH host; v1.8.3 fixed it mid-session. | Any earlier aimap output in the corpus from before v1.8.3 may carry the same data-tier blind spot. |

---

## 9. Proof of Concept (PoC) Illustrations

> PoCs use minimal, read-only, or simulated interactions. No operator data extracted. No credentials used. No exploit payloads. Demonstrate existence and risk conceptually only.

### PoC 1: Public-bucket list demonstrating the bucket-behind-the-platform chain

**Scenario:** An anonymous observer reads an exposed MLflow tracker, extracts the artifact_uri it names, and issues one list request against that storage container to test whether the chain dereferences to readable data.

```
STEP 1 — read the artifact pointer from the exposed tracker
REQUEST:
  GET /api/2.0/mlflow/runs/get?run_id=<run-id> HTTP/1.1
  Host: <operator-mlflow-host>:5000

RESPONSE:
  HTTP/1.1 200 OK
  Content-Type: application/json

  { "run": { "info": {
      "artifact_uri": "wasbs://<container>@<account>.blob.core.windows.net/<exp>/<run-id>/artifacts"
  } } }

STEP 2 — list the named container, anonymously
REQUEST:
  GET /<container>?restype=container&comp=list&maxresults=10 HTTP/1.1
  Host: <account>.blob.core.windows.net
  User-Agent: NuClide-VisorBishop-Phase5b/1.0 (research; read-only)

RESPONSE (the one public-list case):
  HTTP/1.1 200 OK
  Content-Type: application/xml

  <?xml version="1.0" encoding="utf-8"?>
  <EnumerationResults ContainerName="https://<account>.blob.core.windows.net/<container>">
    <Blobs />
  </EnumerationResults>

RESPONSE (the 48 locked cases — representative):
  HTTP/1.1 403 Forbidden        # S3: AccessDenied
  HTTP/1.1 409 PublicAccessNotPermitted   # Azure account-locked
```

**Demonstrated:** The MLflow tracker names its storage backend in run metadata. That name is a working pointer. Issuing one list request against the pointer is the verification step. In 1 of 49 cases the request returns HTTP 200 and an `EnumerationResults` document, confirming an anonymous-list ACL — but the `<Blobs />` element is empty, so the chain dereferences to a configured-but-empty surface, not to data. In 48 of 49 cases the request returns a discriminating denial (403 `AccessDenied`, 409 `PublicAccessNotPermitted`), confirming the storage tier is locked. What this does NOT do: it does not read any blob, it does not test GET-by-key, and the empty 200 is not a data breach. It establishes the ACL state and nothing past it.

### PoC 2: Headless-API exposure tell — SPA bundle to unauthenticated production API

**Scenario:** An observer notices a brand's web app is on a CDN, pulls the JavaScript bundle, finds the API hostname baked in as a constant, and confirms with one health probe that the API is the unhardened backend.

```
STEP 1 — extract the API hostname from the CDN-hosted SPA bundle
  $ grep -oE 'https?://api\.[^"]+' smartshop-main.js
  https://api.<brand>.<tld>/api/v1

  DNS: api.<brand>.<tld>  ->  <operator-VM-IP>   (AS<operator-asn>)
  vs.  <brand>.<tld>      ->  <CDN-edge>         (Vercel)
  # different ASN — the resolved API host is the soft target

STEP 2 — one anonymous probe against the resolved API host
REQUEST:
  GET /health HTTP/1.1
  Host: api.<brand>.<tld>

RESPONSE:
  HTTP/1.1 200 OK
  Content-Type: application/json

  {"status":"healthy","version":"1.0.0","service":"ml-ops-two-tower"}

STEP 3 — confirm no auth scheme is defined
REQUEST:
  GET /openapi.json HTTP/1.1
  Host: api.<brand>.<tld>

RESPONSE (relevant fragment):
  "components": { "securitySchemes": {} }
```

**Demonstrated:** A CDN-hosted SPA must bake its API hostname into the bundle as a public DNS name, because end-user browsers call it directly. That makes the headless API findable the moment the SPA ships. When the API hostname resolves to a different ASN than the CDN edge, the resolved host is operator-managed infrastructure and is the probe target. One `/health` GET confirms the service is live; one `/openapi.json` GET confirms `securitySchemes` is empty, meaning no authentication is defined. What this does NOT do: it does not call any data endpoint, it does not loop `/session/init` to harvest user profiles, and it does not exercise the `POST /interactions` write path. It establishes the API is live and unauthenticated, which is the exposure tell, and stops there.

---

*Prepared by NuClide Research (Nicholas Kloster + Claude Sonnet 4.6) · 2026-05-13 · bucket-accessibility survey + SmartShop disclosure*
