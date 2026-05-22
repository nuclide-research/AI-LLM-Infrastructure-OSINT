# Session Analysis: Langfuse Postgres Cert Pivot — Data Tier Survey + CygnusAlpha Production Discovery

**Date:** 2026-05-22  
**Session:** 31 (parallel — Langfuse :5432 chain)  
**Classification:** Internal / Research Use Only  
**Toolchain:** JAXEN (Playwright) · aimap · VisorGraph · menlohunt · VisorBishop · VisorLog · VisorScuba · BARE · VisorCorpus · cortex · aimap-profile · VisorSD · VisorGoose · nu-recon  
**Repos updated:** AI-LLM-Infrastructure-OSINT (case-studies/commercial/langfuse-postgres-cert-pivot-2026-05-22.md)

---

## 1. Overview

### Objective

Test the data-tier corollary of the auth-on-default thesis: do Langfuse Postgres instances exposed on the public internet have authentication enforced? The dork `ssl.cert.subject.cn:langfuse port:5432` surfaced 11 hosts during Session 30 (Agenta LLMOps survey). This session ran the full 19-tool arsenal against the corpus.

Secondary objective: if the data tier is locked, pivot via the TLS cert to find the co-located inference tier. Apply the data-tier cert pivot methodology class (Insight #20 + Insight #47).

### Scope and Constraints

- **Target:** 11 IPs, `ssl.cert.subject.cn:langfuse port:5432` Shodan corpus
- **Allowed techniques:** Passive Shodan (Playwright, API key unavailable), PostgreSQL Protocol 3.0 StartupMessage connection attempt (auth-gate check only — no query execution), VisorGraph TLS ClientHello on non-5432 ports, safe HTTP GET against diagnostic endpoints (`/api/public/health`, `/auth/sign-up`)
- **Ethical hard stops:**
  - No account creation on operator systems
  - No API calls consuming operator LLM quota
  - No reading of trace data, prompt bodies, or conversation logs
  - Postgres: connection attempt only — does auth gate exist? No credential submission, no query execution
  - Redis: no AUTH credential attempt, no brute force
  - VisorAgent (active LLM exploitation) and VisorRAG: controlled lab targets only — not fired at operator hosts

---

## 2. Environment and Tooling

### Claude Code Operation

Single terminal. Orchestrator pattern — shell commands via Bash tool, files via Read/Write tools. VisorGraph background-parallelized across all 11 IPs via `for ... &; done; wait`. All other tools sequential per host.

### Tools Used

| Tool | Role | Result |
|---|---|---|
| **JAXEN (Playwright)** | Stage-0 Shodan harvest → shodan-hits.txt | 11 hits; API key unavailable — browser-automated |
| **Python / socket** | Postgres Protocol 3.0 auth-state probe | 11/11 auth-enforced |
| **aimap** | Service fingerprint + lateral port enumeration | No AI fingerprints on :5432; Langfuse at :443 via lateral |
| **VisorGraph** | Cert pivot — TLS ClientHello on all non-5432 ports | 34.0.11.208 → agenthub.dev01.cygnusalpha.one (pivotal) |
| **aimap-profile** | Target classification + ethics flags | WHOIS → Google LLC; commercial AI observability |
| **menlohunt** | GCP EASM on 34.0.11.208 | 9 findings: Redis CRITICAL, Postgres HIGH, Prometheus MEDIUM, WireGuard MEDIUM |
| **VisorBishop** | Platform re-probe + auth state | Both Langfuse instances `auth: auth` — tool gap logged |
| **VisorLog** | Ledger ingest → nuclide.db | 6 events ingested (IDs 35930–35935) |
| **VisorScuba** | Compliance scoring | 9/10; 1 warn (AI.H1 — signup-open) |
| **BARE** | Metasploit semantic ranking | 0/5 MSF coverage; max 0.515 (Redis port exposure) |
| **VisorCorpus** | Adversarial corpus | Built: prompt_injection, system_prompt, kb_exfiltration, cross_tenant_leak |
| **VisorSD** | ASN/org dork sweep | Dry-run; API unavailable |
| **VisorGoose** | TLD / CT-log sweep | Scanned .one TLD |
| **nu-recon** | Single-host passive deep-read | Limited output (no Shodan API) |
| **cortex** | Auth-context analysis | Ran with --force; schema mismatch (tool gap logged) |
| **JS-bundle / vampire.py** | SPA secret extraction | Not applicable — Next.js SSR, no CDN-fronted SPA |
| **recongraph** | Seed-polymorphic recon graph | Not run — VisorGraph covered cert pivot |
| **VisorPlus** | Hands-off chain orchestrator | Not run — per-host VisorGraph pass was the chain |
| **VisorRAG** | RAG adversarial confirmation | **Ethical-stop** — controlled targets only |
| **VisorAgent** | Active LLM exploitation | **Ethical-stop** — controlled targets only |
| **VisorHollow** | Windows benchmark | **Not applicable** — Windows-only |

### Notable Configuration

- Shodan API key unavailable — harvest via Playwright browser automation; user authenticated manually (Cloudflare challenge)
- Mullvad VPN active: 23.234.117.61 (us-mkc-wg-003). External IP visible in pg_hba.conf rejection: `FATAL: no pg_hba.conf entry for host "23.234.117.61"`
- First Postgres probe attempt: hardcoded packet length → `FATAL C08P01 invalid startup packet layout` on all 11 hosts. Fixed: dynamic length calculation

---

## 3. Methodology

### The Data-Tier Cert Pivot Class

The dork `ssl.cert.subject.cn:<platform> port:<data-tier>` is an attribution dork, not an auth-exposure dork. This is the core methodology observation this session confirms:

1. The TLS cert CN is operator identity. On Cloud SQL, it encodes the GCP project ID and instance name.
2. The data tier is auth-enforced by default on managed services (Cloud SQL: SCRAM-SHA-256, no operator configuration required).
3. The productive path when the data tier is locked: enumerate all hosts → identify the anomalous non-managed-service entry → cert-pivot its non-data-tier ports → find the inference tier → DNS-enumerate the operator domain → find production.

### Why `fe_sendauth: no password supplied` ≠ Open Postgres

The Shodan banner appears to signal exposed Postgres. It does not. The sequence:

1. Shodan probe sends TCP connection to port 5432
2. PostgreSQL server responds with `AuthenticationSASL` (SCRAM-SHA-256): `R\x00\x00\x00\x17\x00\x00\x00\x0aSCRAM-SHA-256\x00\x00`
3. Shodan probe has no password. It generates the error `fe_sendauth: no password supplied` — a client-side error — and logs it as the banner.

The server never permitted access. This extends Insight #16 to the Postgres protocol layer: `fe_sendauth` is not an auth-open indicator; it is a connection-attempt result from a probe that failed the challenge.

**Classification probe (raw Protocol 3.0 StartupMessage):**
- Response byte `R` (0x52) = `AuthenticationXxx` — auth required, connection rejected without credentials
- Response byte `S` (0x53) = `ParameterStatus` — auth succeeded (would indicate no-password config)
- Response byte `E` (0x45) = `ErrorResponse` — check SQLSTATE: 28000 = pg_hba.conf rejection; 08P01 = malformed packet

### signUpDisabled as Primary Source

The enrollment policy is read from `__NEXT_DATA__` in the Next.js SSR response — the application's own config, served before any authentication. Not inferred from behavior; the app declares its policy. Per the primary-source-over-framing principle: this is as authoritative as a config file.

### Safeguards Applied

- Postgres probe: `StartupMessage` only — no credentials submitted, no query execution
- Redis: no AUTH submission, no credential testing
- HTTP probes: GET against documented diagnostic endpoints only — `/api/public/health`, `/auth/sign-up`
- No account created on any operator system
- VisorAgent and VisorRAG: not invoked against any operator host

---

## 4. Execution Trace

| Time | Action | Outcome |
|---|---|---|
| ~17:24 | JAXEN harvest via Playwright (Shodan UI) | 11 hits; shodan-hits.txt written |
| ~17:25 | Postgres StartupMessage probe — first attempt | All 11: `FATAL C08P01 invalid startup packet layout` — packet length hardcoded. Bug. |
| ~17:26 | Fix: dynamic length calculation; re-probe | 10: SCRAM-SHA-256. 1 (34.0.11.208): pg_hba.conf ACL. 11/11 auth-enforced. |
| ~17:27 | VisorGraph on all 11 IPs (background parallel) | 10/11: Cloud SQL cert only — no pivot. 34.0.11.208: cert CN = `agenthub.dev01.cygnusalpha.one` |
| ~17:28 | HTTP probe on 34.0.11.208:443 | `/api/public/health` → `{"status":"OK","version":"3.146.0"}`. Langfuse confirmed. |
| ~17:29 | signUpDisabled extraction on dev01 | `signUpDisabled: false`. F2 confirmed. |
| ~17:30 | DNS enumeration of cygnusalpha.one | `agenthub.cygnusalpha.one` → 34.36.249.66 (GCP, different region) |
| ~17:31 | HTTP probe on 34.36.249.66 (production) | `version: 3.140.0`, `signUpDisabled: false`. F1 confirmed. |
| ~17:32 | menlohunt on 34.0.11.208 | Redis :6379 CRITICAL (auth-enforced), Postgres :5432 HIGH, Prometheus :9090 MEDIUM (403), WireGuard MEDIUM |
| ~17:33 | Port :3000 CSP analysis | Production S3 bucket names in CSP: prod-uk-services-*, eu-west-2. Azure AD, Stripe, Plain.com UK. |
| ~17:34 | aimap; VisorBishop; VisorScuba; BARE; VisorCorpus; cortex; aimap-profile | Arsenal chain complete. Tool gaps logged (VisorBishop signup-open, cortex schema). |
| ~17:35 | VisorLog ingest | 6 events → nuclide.db (IDs 35930–35935) |
| ~17:38 | Case study written, committed | case-studies/commercial/langfuse-postgres-cert-pivot-2026-05-22.md |

---

## 5. Findings

> **Severity label policy:** Every tier label requires 100% verified evidence at that tier. Unverified observations are UNRATED.

### 5.1 agenthub.cygnusalpha.one — Langfuse Open Signup (PRODUCTION)

| Field | Value |
|---|---|
| **Host** | `34.36.249.66` / `agenthub.cygnusalpha.one` |
| **Type** | Langfuse LLM tracing + evaluation platform (production) |
| **Evidence** | `signUpDisabled: false` in `/auth/sign-up` `__NEXT_DATA__`; `version: 3.140.0` |
| **Exposure** | Open account registration — any internet user can create a free account |
| **Auth providers** | Google OAuth, email/password credentials |
| **Severity** | **HIGH** |

**Potential impact:** Uncontrolled account creation → full authenticated API access to the production Langfuse instance. Risk surface (depending on multi-tenancy enforcement): LLM trace data (user prompts, model responses, latency), evaluation results, project configurations, API key usage patterns. Storage/compute quota drain. If multi-tenancy is misconfigured: cross-tenant project enumeration.

**Verification command:**
```bash
curl -s https://agenthub.cygnusalpha.one/auth/sign-up \
  | python3 -c "
import sys, re, json
body = sys.stdin.read()
m = re.search(r'__NEXT_DATA__[^{]+({.*?})</script>', body, re.DOTALL)
d = json.loads(m.group(1))
pp = d['props']['pageProps']
print('signUpDisabled:', pp.get('signUpDisabled'))
"
```

---

### 5.2 agenthub.dev01.cygnusalpha.one — Langfuse Open Signup (DEV + PRODUCTION S3)

| Field | Value |
|---|---|
| **Host** | `34.0.11.208` / `agenthub.dev01.cygnusalpha.one` |
| **Type** | Langfuse LLM tracing + evaluation platform (dev instance) |
| **Evidence** | `signUpDisabled: false` in `/auth/sign-up` `__NEXT_DATA__`; `version: 3.146.0` |
| **Exposure** | Open account registration; port :3000 CSP leaks production S3 bucket names |
| **Auth providers** | Google OAuth, email/password, Keycloak |
| **Severity** | **HIGH** |

**Escalating factor:** The port :3000 CSP contains three production S3 bucket names (`prod-uk-services-*`, eu-west-2) and references Azure AD and Stripe. This dev node is configured against production infrastructure. Dev access = production S3 read surface if bucket policies are misconfigured.

---

### 5.3 All 11 Hosts — Postgres Data Tier Internet Exposure

| Field | Value |
|---|---|
| **Hosts** | All 11 (10 Cloud SQL + 1 GCE VM) |
| **Exposure** | Port 5432 internet-accessible |
| **Auth state** | 10/11: SCRAM-SHA-256 (Cloud SQL managed). 1/11: pg_hba.conf ACL rejection (34.0.11.208) |
| **Severity** | **OBSERVED** — auth-enforced, no unauth access; internet exposure is a hardening failure |

Disabling public IPs on Cloud SQL instances costs nothing and eliminates this exposure class. The Cloud SQL Auth Proxy is the intended access pattern.

---

### 5.4 34.0.11.208 — Redis + Prometheus Internet Exposure

| Field | Value |
|---|---|
| **Ports** | Redis :6379 (AUTH required), Prometheus :9090 (403 Forbidden) |
| **Severity** | **OBSERVED** — auth-enforced on both |

Redis AUTH with weak passwords is susceptible to credential stuffing; the attack surface narrows but does not close when internet-exposed. menlohunt classifies Redis CRITICAL on port exposure alone — label reflects internet-reachability, not auth bypass.

---

### 5.5 34.0.11.208 — Production S3 Bucket Names in Dev Node CSP

| Field | Value |
|---|---|
| **Evidence** | Content-Security-Policy at port :3000 lists `prod-uk-services-*` S3 bucket names, eu-west-2 |
| **Severity** | **LOW** — information disclosure; not a credential leak |

Bucket names are stable addresses. If the S3 buckets have any public-read policies or misconfigured IAM, the bucket names are the next pivot surface.

---

## 6. Risk Assessment

### Overall Posture

The data tier (Postgres) is auth-on-default across the entire surveyed population. The dork was an attribution exercise, not an access exercise. The finding came from the anomalous non-managed-service host — following the cert pivot all the way to production.

**CygnusAlpha (cygnusalpha.one)** has two signup-open Langfuse instances. The production instance (34.36.249.66) is the exposure that matters; the dev01 instance compounds it with production S3 references.

### Confidentiality

Langfuse tracing stores user inputs, model responses, latency, API key usage patterns, and conversation history. Open signup on production means an unauthenticated actor needs only an email address to access these. Multi-tenancy enforcement not verified — stopped at account-creation boundary.

### Integrity

Authenticated API access (obtained via self-registration) includes write paths: trace uploads, project creation, evaluation result submission. An actor with a free account could inject false traces, corrupt evaluation baselines, or conduct prompt-based reconnaissance on the system's observability configuration.

### Availability

Mass account creation → storage/compute quota drain. Low effort, measurable impact.

### Systemic Patterns

1. **Managed database services absorb the auth burden.** Cloud SQL enforces SCRAM-SHA-256 without operator action. This is the inverse of the application tier, where platforms often ship Tier-A.
2. **The GCE VM is always the outlier.** Self-managed infrastructure requires explicit auth configuration; managed services don't. The one non-Cloud-SQL host is where the actual surface was.
3. **Dev/production boundary collapse.** Dev01 references production S3, production AWS credentials are likely in its environment, and it has the same signup-open posture as production. The "dev" label does not reduce risk.
4. **TLS-CN data-tier dorks are operator-attribution surfaces, not auth-exposure surfaces.** Insight #47 (TLS-CN is attribution-only) confirmed at the data tier. The dork was valuable not for finding open databases but for finding operator GCP project IDs and the anomalous entry.

---

## 7. Recommendations

### R1 — Disable open signup on both Langfuse instances

```bash
# Add to docker-compose.yml or .env
LANGFUSE_DISABLE_SIGNUPS=true
# Restart
docker compose restart web
```

**Verification:**
```bash
curl -s https://agenthub.cygnusalpha.one/auth/sign-up \
  | python3 -c "
import sys, re, json
body = sys.stdin.read()
m = re.search(r'__NEXT_DATA__[^{]+({.*?})</script>', body, re.DOTALL)
d = json.loads(m.group(1))
pp = d['props']['pageProps']
assert pp['signUpDisabled'] == True, f'still open'
print('REMEDIATED')
"
```

### R2 — Disable public IPs on Cloud SQL instances

```bash
gcloud sql instances patch <instance-name> --no-assign-ip
```

Use Cloud SQL Auth Proxy for all connections. Eliminates the entire data-tier internet-exposure class in one operation across all 10 instances.

### R3 — VPC firewall on 34.0.11.208

Deny external access to ports 5432, 6379, 9090, 3000:
```bash
gcloud compute firewall-rules create deny-data-ports-external \
  --direction=INGRESS --priority=900 \
  --action=DENY --rules=tcp:5432,tcp:6379,tcp:9090,tcp:3000 \
  --source-ranges=0.0.0.0/0 \
  --target-tags=langfuse-dev
```

### R4 — Separate dev from production S3

Dev01 should reference dev S3 buckets with dev IAM roles. Production bucket names and credentials have no place in a dev environment's CSP. If production S3 env vars are in dev01's environment, rotate them.

### R5 — CI/CD signup-gate check

Add a post-deploy check to fail the pipeline if signup is open on any public-facing Langfuse instance:
```bash
DISABLED=$(curl -s https://$LANGFUSE_HOST/auth/sign-up \
  | python3 -c "
import sys, re, json
m = re.search(r'__NEXT_DATA__[^{]+({.*?})</script>', sys.stdin.read(), re.DOTALL)
d = json.loads(m.group(1))
print(d['props']['pageProps'].get('signUpDisabled', False))
")
[ "$DISABLED" = "True" ] || { echo "FAIL: signup open on $LANGFUSE_HOST"; exit 1; }
```

### R6 — Periodic TLS-CN sweep

```bash
# Run quarterly to catch new data-tier exposures + operator pivots
jaxen hunt 'ssl.cert.subject.cn:langfuse port:5432'
jaxen hunt 'ssl.cert.subject.cn:langfuse port:443'
```

The cert pivot from data-tier to inference-tier is a repeatable methodology. Any new data-tier hit may carry an anomalous non-managed entry that pivots to an unprotected inference tier.

---

## 8. Limitations and Assumptions

| # | Limitation | Risk Implication |
|---|---|---|
| L1 | Account creation not attempted | Multi-tenancy enforcement unverified — cross-tenant risk cannot be confirmed or ruled out |
| L2 | Write-tier operations not tested (restraint ethic) | Integrity impact based on GET surface + API schema; may understate actual exposure |
| L3 | `tooling-prd-468115` / `tooling-dev-463909` operator not identified | Production Langfuse pair with public IPs remains unattributed; inference tier not found |
| L4 | Internal-only Langfuse deployments invisible to Shodan | Population underestimates total Langfuse deployment count |
| L5 | Shodan API unavailable — Playwright harvest | Manual browser auth required (Cloudflare); may miss paginated results |
| L6 | Mullvad VPN active during pg_hba.conf probe | External IP in rejection message: 23.234.117.61. Consistent; VPN did not prevent connection attempt |
| L7 | Redis AUTH not tested | Redis password policy unknown; no brute force attempted per restraint ethic |

---

## 9. Proof of Concept (PoC) Illustrations

> All PoCs use read-only probes. No operator data extracted. No accounts created. No credentials used.

### PoC 1: Postgres Protocol Auth-State Classification

**Scenario:** Actor probes a Shodan-flagged Postgres instance to determine true auth state, rather than inferring from the `fe_sendauth` banner.

```
REQUEST (Python, PostgreSQL Protocol 3.0):
  params = b'user\x00postgres\x00database\x00postgres\x00\x00'
  length = 4 + 4 + len(params)
  startup = struct.pack('>I', length) + struct.pack('>I', 196608) + params
  → sent to 35.195.155.180:5432

RESPONSE (raw bytes, hex):
  52 00 00 00 17 00 00 00 0a  53 43 52 41 4d 2d 53 48 41 2d 32 35 36 00 00
  [R] [   length   ] [auth_type=10] [  "SCRAM-SHA-256\x00\x00"  ]
```

**Demonstrated:** Response byte `R` = `AuthenticationSASL`. Server is challenging. Auth is enforced. The Shodan banner `fe_sendauth: no password supplied` was the scanner's client-side error — not a permission grant from the server.

---

### PoC 2: TLS Cert Pivot from Data Tier to Inference Tier

**Scenario:** Data tier is locked. Actor pivots via the TLS certificate on the anomalous GCE host.

```
STEP 1 — VisorGraph TLS ClientHello on 34.0.11.208:443:
  → TLS ServerHello
  → Certificate CN: agenthub.dev01.cygnusalpha.one
  → Issuer: Let's Encrypt

STEP 2 — HTTP probe on discovered host:
  GET /api/public/health HTTP/1.1
  Host: agenthub.dev01.cygnusalpha.one
  
  → 200 OK
  → {"status":"OK","version":"3.146.0"}

STEP 3 — Enrollment policy probe:
  GET /auth/sign-up HTTP/1.1
  Host: agenthub.dev01.cygnusalpha.one
  
  → 200 OK
  → __NEXT_DATA__ ... "signUpDisabled":false ...

STEP 4 — DNS enumeration → production:
  agenthub.cygnusalpha.one → 34.36.249.66
  GET /api/public/health → {"status":"OK","version":"3.140.0"}
  signUpDisabled: false
```

**Demonstrated:** Complete data-tier-cert-pivot-to-inference-tier chain. The data tier yielded nothing via direct probing. The cert named the operator domain. DNS enumeration from the dev subdomain found production. Both signup-open.

---

### PoC 3: signUpDisabled Primary-Source Extraction

**Scenario:** Actor confirms signup enrollment policy before attempting account creation.

```
REQUEST:
  GET /auth/sign-up HTTP/1.1
  Host: agenthub.cygnusalpha.one

RESPONSE (relevant portion of __NEXT_DATA__ SSR block):
  {
    "props": {
      "pageProps": {
        "signUpDisabled": false,
        "authProviders": {
          "google": true,
          "credentials": true
        }
      }
    }
  }
```

**Demonstrated:** The application declares its own enrollment policy in the page HTML before any authentication. `signUpDisabled: false` is the app config, not an inferred state. Reading `__NEXT_DATA__` is read-only — no auth required, no account interaction.

---

*Prepared by NuClide Research (Nicholas Kloster + Claude Sonnet 4.6) · Session 31 (parallel chain) · 2026-05-22*
