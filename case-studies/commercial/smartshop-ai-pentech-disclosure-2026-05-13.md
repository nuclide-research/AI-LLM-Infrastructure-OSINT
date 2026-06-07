---
type: host
title: "SmartShop AI / amazonrec.space: Multi-service ML pipeline exposure on a single PENTECH host"
date: 2026-05-13
class: case-study
category: commercial-llmops
status: disclosure-ready
severity: critical
operator: SmartShop AI (amazonrec.space). Turkey-hosted recommendation product
host: 78.135.66.61 (PENTECH BILISIM TEKNOLOJILERI, AS48678, TR)
---

# SmartShop AI · 78.135.66.61 · 2026-05-13

NuClide Research · 2026-05-13

## Summary

A single host on PENTECH BILISIM TEKNOLOJILERI (Turkey, AS48678) exposes
the operator's complete MLOps pipeline to the public Internet without
authentication, plus the operator's production API at
`api.amazonrec.space`. The product, branded **SmartShop AI**, is a
"two-tower recommendation system" trained on what appears to be Amazon
catalog and customer-interaction data.

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7004, K7044, S7068, S7070, S7075, T5904
- **733 (AI Risk & Ethics Specialist):** K7040, K7051, S7067, T5868, T5882, T5904
- **overlap (Common AI KSATs (all 5 roles)):** K1157, K1158, K1159, K22, K6311, K6900, K6935, K7003, K7024, K942

<!-- ksat-tag:auto-generated:end -->

The exposure chains across four tiers:

| Tier | Service | Port | Auth posture | Severity |
|---|---|---|---|---|
| Orchestration | Apache Airflow | 8080 | sign-in page reachable; multiple Airflow CVEs apply | high |
| Tracking | MLflow | 5000 | unauthenticated (`MLFLOW_TRACKING_AUTH` not set) | critical |
| Datastore | PostgreSQL | 5432 | direct Internet exposure | high |
| Datastore | Redis | 6379 | direct Internet exposure | critical |
| Mail | Postfix SMTP/IMAP/POP | 25/110/143/465/587/995 | starttls, eol-product per Shodan tags | medium |
| Product API | `api.amazonrec.space` (FastAPI) | 443 | **zero auth** — `security: {}` in OpenAPI spec; 13 endpoints public | **critical** |

The host carries **27 known CVEs** per Shodan (last update
2026-05-12), tagged `database`, `self-signed`, `eol-product`,
`starttls`.

## Identity and attribution

| Attribute | Value | Source |
|---|---|---|
| IP | `78.135.66.61` | Phase 5 corpus, MLflow artifact backend |
| Reverse DNS | `78.135.66.61.pendns.net` | DNS PTR |
| ASN | AS48678 | WHOIS |
| ISP / org | PENTECH BILISIM TEKNOLOJILERI SANAYI VE TICARET LIMITED SIRKETI | WHOIS |
| Country / City | Turkey / Istanbul | Shodan + WHOIS |
| Hostnames on the IP | `mlflow.amazonrec.space`, `airflow.amazonrec.space`, `api.amazonrec.space`, `mail.nadorawear.com`, `78.135.66.61.pendns.net` | Shodan rDNS + DNS |
| Domains | `amazonrec.space`, `pendns.net`, `nadorawear.com` | Shodan + WHOIS |
| Operator product | "SmartShop AI" / "MLOps Console" | SPA `<title>` + FastAPI `info.title` |
| Frontend hosting | Vercel (`amazonrec.space` SPA at `cle1::hb722-…`) | HTTP `x-vercel-id` |
| Sibling IPs in /29 | `tr5.timeadjust.org` (.58), `server.emersoft.com.tr` (.60) | aimap-profile PTR sweep |

`api.amazonrec.space` resolves directly to `78.135.66.61`. The static
SPA on Vercel calls `https://api.amazonrec.space/api/v1` per the
bundled JavaScript (`/assets/index-B6ZJc83n.js`).

The `nadorawear.com` co-location is via shared *mail server*, not
shared API. `nadorawear.com` (a Turkish swimwear retailer) uses
Google Workspace MX and serves its storefront from Vercel, but its
`mail.nadorawear.com` MX-target lands on this same PENTECH host. The
operator (the SmartShop AI team) and the nadorawear team appear to
share a sysadmin / IT vendor. Same operator-of-operators
(`pendns.net` / `pendc.com` namespace).

## What is exposed

### 1. SmartShop AI production API (`api.amazonrec.space` → `78.135.66.61`)

**Severity: CRITICAL.**

The product API is publicly served with **no authentication mechanism
defined** (the FastAPI OpenAPI spec's `components.securitySchemes` is
the empty object `{}`). Swagger UI is mounted at `/docs` and
`/openapi.json` is publicly fetchable. Thirteen endpoints:

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/v1/recommend` | Get Recommendations |
| POST | `/api/v1/search` | Search Products |
| GET | `/api/v1/user/{user_id}/features` | Get User Features |
| GET | `/api/v1/item/{item_id}/features` | Get Item Features |
| GET | `/api/v1/products/{product_id}` | Get Product Details |
| POST | `/api/v1/products/batch` | Batch product lookup |
| POST | `/api/v1/interactions` | Track Interaction (writes telemetry) |
| POST | `/api/v1/interactions/batch` | Track Impressions (writes telemetry) |
| GET | `/api/v1/interactions/stats` | Get Interaction Stats |
| GET | `/api/v1/session/init` | Initialize a session, returns a real user_id |
| GET | `/api/v1/session/pool-stats` | Pool stats |
| GET | `/api/v1/for-you` | Recommendations for a user_id |
| GET | `/health` | Health probe |

Single anonymous calls confirm the API serves real data:

**`/health`** →
```json
{"status":"healthy","version":"1.0.0","service":"ml-ops-two-tower"}
```

**`/api/v1/interactions/stats`** (single GET, no auth) →
```json
{"enabled":true,"buffer_size":0,"buffer_capacity":1000,
 "total_logged":15139,"db_writes":6374,"s3_writes":15139,
 "errors":254,"last_flush":"2026-05-13T12:50:52.052854"}
```

The service has logged **15,139 user interactions** with 6,374
PostgreSQL writes and 15,139 S3 writes. The S3 backend confirms the
operator stores raw interaction events in cloud object storage.

**`/api/v1/session/init`** (single anonymous GET) →
```json
{"success":true,
 "user_id":"AH2IJABKXWIZIO2FYJXNFEXNRR6A",
 "interaction_count":19,
 "category_count":3,
 "top_categories":["Buy a Kindle","Books","Toys & Games"],
 "assigned_at":"2026-05-13T16:56:31.269772"}
```

The returned `user_id` follows the **Amazon customer ID format** (28
alphanumeric chars, prefix `AH`). The category history is
human-realistic. The session pool documentation
(`/api/v1/session/pool-stats`) shows the system has **100 pre-loaded
user profiles**, each with an average of 18.86 interactions
spanning categories such as `AMAZON FASHION`, `Prime Video`, `All
Beauty`, `Camera & Photo`. **The training corpus is Amazon catalog +
customer-interaction data, served unauthenticated.**

A passive attacker can:

1. Repeatedly call `/session/init` and harvest all 100 user IDs and
   per-user interaction summaries.
2. Walk `/api/v1/user/{user_id}/features` to extract per-user
   embedding features for each harvested ID.
3. Walk `/api/v1/for-you?user_id=…` to retrieve recommendation
   outputs for each user. Proving model behaviour.
4. POST forged events to `/api/v1/interactions` to poison the
   training feedback loop (the response indicates writes succeed,
   `total_logged` increments).

### 2. MLflow tracking server (`mlflow.amazonrec.space` → `78.135.66.61:5000`)

**Severity: CRITICAL.**

Phase 5 already documented this host's MLflow tracker as
unauthenticated; this case study confirms the same host runs the
*production API* that publishes via that tracker. The MLflow
backend writes to the `wasbs://` bucket family. See Phase 5b
bucket-accessibility survey for the full storage-tier analysis.

The MLflow API answers anonymous calls:
`GET /api/2.0/mlflow/experiments/search?max_results=1000` returns
the full experiment list (real names like
`scan_1778457788`, model training runs for `yolov11`, etc.).

### 3. Apache Airflow (`airflow.amazonrec.space` → `78.135.66.61:8080`)

**Severity: HIGH.**

Airflow's web UI presents its standard sign-in page anonymously.
The host carries CVE references for the Airflow tree across the 27
total Shodan-listed CVEs, including:

- CVE-2024-25142. Connection / DAG escalation
- CVE-2024-26280. DAG run permission bypass
- CVE-2024-27906, CVE-2024-28746, CVE-2024-31869, CVE-2024-39863,
  CVE-2024-39877, CVE-2024-41937, CVE-2024-45034, CVE-2024-45784,
  CVE-2024-50378

BARE module ranking against the Metasploit corpus returns
`exploits/linux/http/apache_airflow_dag_rce` as the top semantic
match (score 0.679).

### 4. PostgreSQL on `:5432`

**Severity: HIGH.**

Direct Internet exposure of the production data store. This is the
authoritative store for the MLflow tracker and the SmartShop AI
interaction log (per `/interactions/stats` `db_writes`).

### 5. Redis on `:6379`

**Severity: CRITICAL.**

Direct Internet exposure of a Redis instance, tagged `database`,
`self-signed`, `eol-product` by Shodan. Likely caches session state
for the SmartShop AI API. BARE top match:
`auxiliary/gather/redis_extractor` (score 0.607).

### 6. Mail server (`mail.nadorawear.com` → `78.135.66.61`)

Postfix SMTP/IMAP/POP on `25/110/143/465/587/995`. The host serves
mail for `nadorawear.com` (Turkish swimwear retail) and
`pendns.net` (the PENTECH-internal namespace). Mail data is
operator-customer data. Separate finding class.

## Chain analysis

The four-tier chain enables:

```
SmartShop AI SPA on Vercel
  │
  │  fetch https://api.amazonrec.space/api/v1/* (CORS open: *)
  ▼
api.amazonrec.space   ← public, unauth, 78.135.66.61:443
  │
  │  internal calls (PostgreSQL + Redis + S3)
  ▼
PostgreSQL :5432  ←─── Internet-exposed
Redis :6379       ←─── Internet-exposed
  │
  │  MLflow tracking writes
  ▼
MLflow :5000      ←─── Internet-exposed
  │
  │  Artifacts upload to wasbs:// (see Phase 5b)
  ▼
Azure Blob bucket  ← bucket hygiene analyzed in Phase 5b
  │
  │  Triggered/scheduled by Airflow
  ▼
Airflow :8080     ←─── Internet-exposed sign-in page
```

A single operator misconfiguration class. **"deploy MLOps stack
behind a Vercel SPA without standing up a private VPC"**, produces
six independent unauth surfaces, each high-or-critical on its own.

## Methodology insight surfaced

### Insight #19: SPA + headless API is a high-severity exposure tell

When a JavaScript bundle hosted on a CDN (Vercel, Cloudflare Pages,
Netlify) calls `https://api.<same-brand>.<tld>/api/v1`, that API
endpoint is *almost always* on infrastructure the operator manages
directly. The CDN provides TLS, a global edge, and DDoS protection
for the static frontend, but the API surface lands on whatever host
the developer chose, and very often that host is unhardened.

Three field-validated cases of the pattern:

1. **PromptLayer 34.95.65.63** (2026-04, project memory
   `project_promptlayer_disclosure`). Make.com webhook secrets
   baked into the SPA, callable anonymously.
2. **SmartShop AI / amazonrec.space** (this survey). Full
   unauthenticated FastAPI behind a Vercel SPA.
3. Multiple Phase 5 MLflow operators show the same shape (Vercel /
   Netlify SPA + tracker on raw cloud VM).

The detection heuristic for VisorBishop / aimap: when an HTTPS host
is on a CDN with `x-vercel-id` or `cf-ray` or `x-vercel-cache`, pull
the largest JS asset, grep for `https?://api\\..*` and follow the
DNS to find the headless API host. If that host is on a different
ASN than the CDN, it is the soft target.

## Disclosure routing

| Recipient class | Address | Source | Rank |
|---|---|---|---|
| Hosting (PENTECH IP space) | `abuse@pendc.com` | WHOIS:abuse-mailbox | 1 |
| Hosting (DNS namespace) | `abuse@pendns.net` (+ `csirt@`, `incident@`, `infosec@`, `security@`, `soc@`) | pattern-guess+MX | 5 |
| Frontend CDN | `dns@cloudflare.com` (amazonrec.space + nadorawear.com DNS) | DNS:SOA-RNAME | 1 |
| Domain registration (TR) | `domain@isimtescil.net` | WHOIS:body-scan | 2 |
| Nadorawear domain registrar | `abuse@domaintime.biz`, `abuse@isimtescil.net`, `domain@salutegroup.com.tr` | WHOIS:body-scan | 2 |
| Pendns domain registration | `abuse-contact@publicdomainregistry.com`, `gdpr-masking@gdpr-masked.com` | WHOIS:body-scan | 1 |
| Operator brand contact | (no security.txt, no published bounty program) | — | — |

**Recommended first email:** to `abuse@pendc.com` (the immediate
hosting abuse-mailbox per WHOIS) with the SmartShop AI / amazonrec
team CC'd via the brand's general info-mailbox once that's
identified from the website's contact page. Cloudflare is *not* the
right disclosure target. They're DNS-only here, no traffic is
proxied for the API.

The brand-side contact requires one extra step (the SmartShop AI
website doesn't currently publish a security.txt or a team-page
email). Suggested probe: pull the LinkedIn / GitHub footprint of
the developers from the JavaScript bundle's `index-B6ZJc83n.js`
filename hash and the Vercel deployment metadata.

## Severity rollup

| Finding | Severity | Class |
|---|---|---|
| Unauth FastAPI `api.amazonrec.space` (13 endpoints, real Amazon-format user data) | **CRITICAL** | Production-data disclosure + model-feedback poisoning |
| Unauth MLflow `78.135.66.61:5000` | **CRITICAL** | Training-pipeline disclosure (folded into Phase 5) |
| Unauth Redis `78.135.66.61:6379` | **CRITICAL** | Session/cache disclosure + write |
| Apache Airflow `78.135.66.61:8080` sign-in page reachable, 11 Airflow CVEs apply | HIGH | Orchestration takeover surface |
| PostgreSQL `78.135.66.61:5432` Internet-exposed | HIGH | Data tier exposure |
| Postfix mail stack with `eol-product` tag | MEDIUM | Mail-server class |

## Evidence pack

`~/recon/2026-05-13-pentech/`

- `aimap-profile/pentech-ip.json`: IP-side classification (multi-tenant ethics flag, /29 PTR sweep)
- `aimap-profile/amazonrec.space.json`: domain-side classification
- `visorgraph/amazonrec.space.json`: 13-node graph (services, certs, sibling domains)
- `visorgraph/nadorawear.com.json`, `pendns.net.json`. Sibling-domain graphs
- `nuclide-contact/*.json`: full disclosure-recipient resolution (4 targets)
- `js/smartshop-main.js`: SmartShop AI Vite bundle (335KB)
- `js/http___78_135_66_61_8080_.html`: Airflow sign-in page snapshot
- `artifacts/api-probes/openapi.json`: full SmartShop API schema
- `artifacts/api-probes/probe-results.json`: single-call anonymous probe evidence

Phase 5b cross-references:
- `visorbishop-phase5b-bucket-accessibility-2026-05-13.md`: bucket-tier analysis (covers `broadcast-ai` bucket which Phase 5 traced to this host's MLflow tracker)
- Arsenal-fanout evidence at `evidence/2026-05-13-arsenal-fanout/`

## What's next

1. **Draft + send disclosure**, to `abuse@pendc.com` with the SmartShop AI brand contact CC'd once identified.
2. **VisorLog ingest**, three new findings (SmartShop API critical, plus folding Airflow/Postgres/Redis into the host record).
3. **Methodology Insight #19 page**, publish the SPA+API exposure tell as a reusable detection heuristic.
4. **VisorBishop iter-9**, add a `discoverHeadlessAPI` stage: pull the largest JS asset of any CDN-fronted SPA, extract `api.*` URLs, follow DNS, and tag the resulting host for direct probing.
