---
title: "Langfuse Postgres Cert Pivot — Data Tier Survey + CygnusAlpha Production Finding"
date: 2026-05-22
session: 31
category: llm-observability
dork: "ssl.cert.subject.cn:langfuse port:5432"
population: 11
findings:
  - signup-open (HIGH) — agenthub.cygnusalpha.one (production) + agenthub.dev01.cygnusalpha.one (dev)
  - stacked-exposure (OBSERVED) — Redis + Prometheus + Postgres + WireGuard on 34.0.11.208
  - auth-on-default-confirming-negative — 10/11 Cloud SQL SCRAM-SHA-256 enforced
tags: ["LANGFUSE", "POSTGRES", "CERT-PIVOT", "SIGNUP-OPEN", "CLOUD-SQL", "CYGNUSALPHA"]
---

# Langfuse Postgres Cert Pivot — Data Tier Survey + CygnusAlpha Production Finding

**Date:** 2026-05-22  
**Session:** 31 (carry-forward from Session 30 — Agenta LLMOps survey)  
**Dork:** `ssl.cert.subject.cn:langfuse port:5432`  
**Population:** 11 Shodan hits  
**Operators:** 6 distinct (5 Google Cloud SQL + 1 GCE VM)  
**Headline:** Cert pivot on the one non-Cloud-SQL host revealed Langfuse with open signup on both production and dev instances at cygnusalpha.one — an AI agent platform operator.

---

## 1. Discovery

The survey started as an Insight #20 exercise: data-tier ports adjacent to confirmed AI services are an independent exposure class. The dork `ssl.cert.subject.cn:langfuse port:5432` was surfaced during the Agenta survey (Session 30) via the TLS-CN attack class (Insight #46). Eleven hits.

### 1.1 Stage 0 — Harvest

Shodan search via Playwright (API key unavailable — browser auth):

```
ssl.cert.subject.cn:langfuse port:5432 → 11 results
Countries: UK×4, Belgium×2, Singapore×2, US×2, India×1
Org: Google LLC × 10, direct-assign × 1
```

### 1.2 Full Corpus

| IP | Country | GCP Project | Instance CN | Banner |
|---|---|---|---|---|
| 35.195.155.180 | BE/Brussels | dotted-hook-451310 | dotted-hook-451310-s4:langfuse-db | fe_sendauth |
| 104.155.76.72 | BE/Brussels | dotted-hook-451310 | dotted-hook-451310-s4:langfuse-db | fe_sendauth |
| 34.39.118.233 | UK/London | tooling-prd-468115 | tooling-prd-468115:langfuse | fe_sendauth |
| 35.246.76.4 | UK/London | tooling-prd-468115 | tooling-prd-468115:langfuse | fe_sendauth |
| 34.105.158.25 | UK/London | tooling-dev-463909 | tooling-dev-463909:langfuse | fe_sendauth |
| 34.39.63.226 | UK/London | tooling-dev-463909 | tooling-dev-463909:langfuse | fe_sendauth |
| 34.87.61.125 | SG/Singapore | rising-precinct-429608-h9 | rising-precinct-429608-h9:langfuse-db-instance | fe_sendauth |
| 34.124.205.121 | SG/Singapore | rising-precinct-429608-h9 | rising-precinct-429608-h9:langfuse-db-instance | fe_sendauth |
| 34.172.113.104 | US/Council Bluffs | dataplane-development | dataplane-development:pete-langfuse-poc | fe_sendauth |
| 34.41.106.62 | US/Council Bluffs | dataplane-development | dataplane-development:pete-langfuse-poc | fe_sendauth |
| **34.0.11.208** | **IN/New Delhi** | ca-dev-01-426608 | ca-dev-langfuse.asia-south2-a.c.ca-dev-01-426608.internal | **pg_hba.conf FATAL** |

**Dual-IP pattern:** 10 hosts resolve to 5 Cloud SQL instances. Google Cloud SQL with public IP enabled assigns two IPs per instance (primary + replica/failover). Each `*.bc.googleusercontent.com` pair is one instance, not two.

**The anomaly:** `34.0.11.208` is a GCE VM (self-signed cert, internal hostname) not a Cloud SQL instance. Different banner class.

---

## 2. Verification — Auth State

### 2.1 The Shodan Banner Is Not an Auth Signal

The Shodan banner `fe_sendauth: no password supplied` appears in 10 of 11 entries. It reads like an auth failure — it is. But it is the **scanner's** failure, not the server's lapse.

When Shodan's TCP probe connects to port 5432 and sends an SSL negotiation, a Cloud SQL Postgres server sends an `AuthenticationSASL` response (SCRAM-SHA-256). Shodan's probe has no password to offer. The error message `fe_sendauth: no password supplied` is the client-side error that Shodan logs. The server never permitted access; it just explained why the connection failed.

Proof — raw protocol probe:

```python
# Protocol 3.0 startup message → StartupMessage
startup = struct.pack('>I', length) + struct.pack('>I', 196608) + params

# Response from 10/11 hosts:
# R········SCRAM-SHA-256·· 
# (R = AuthenticationSASL, 0x0000000A, then the SASL mechanism list)
```

`R` at byte 0 = `AuthenticationSASL`. The server is challenging, not conceding.

The 11th host (34.0.11.208):

```
FATAL: no pg_hba.conf entry for host "23.234.117.61", user "postgres", 
database "postgres", no encryption
```

pg_hba.conf IP ACL rejection — not even reaching the authentication exchange. More locked down than Cloud SQL.

**Auth state: 11/11 auth-enforced.**

### 2.2 Insight Extension — Insight #16 Applies at the Protocol Layer

Insight #16 established that HTTP 200 is not auth state. The same principle applies at the Postgres protocol layer: `fe_sendauth: no password supplied` is not an auth-open indicator. It is a connection-attempt result. The distinction matters at population scale: a naive scan that treats this banner as "exposed Postgres" would be wrong on every hit.

The correct classification probe is the raw `StartupMessage` → decode the first response byte:
- `R` (0x52) = `AuthenticationXxx` — auth required, connection rejected without creds
- `S` (0x53) = `ParameterStatus` — auth succeeded (would need no-password config)
- `E` (0x45) = `ErrorResponse` — check SQLSTATE code (28000 = pg_hba.conf rejection; 08P01 = malformed packet)

---

## 3. The Cert Pivot — Finding the Inference Tier

The dork targets data-tier ports. The data tier is locked. The pivot is the move.

VisorGraph ran on all 11 IPs. On 10/11 (Cloud SQL), no cert data beyond the Cloud SQL Server CA cert — dead end. On `34.0.11.208`, the TLS ClientHello probe on port 443 (not 5432) returned a **Let's Encrypt cert with CN `agenthub.dev01.cygnusalpha.one`**.

VisorGraph output (key nodes):

```json
{"type":"service","value":"34.0.11.208","attrs":{
  "cert_cn":"agenthub.dev01.cygnusalpha.one",
  "http_status":200,
  "csp":"default-src 'self' https://*.langfuse.com https://*.langfuse.dev ..."
}}
{"type":"domain","value":"agenthub.dev01.cygnusalpha.one","attrs":{"source":"ct-logs"}}
```

The CSP `https://*.langfuse.com` is definitive: this host runs a Langfuse instance.

### 3.1 Inference Tier Probe

```bash
GET https://agenthub.dev01.cygnusalpha.one/api/public/health
→ 200 {"status":"OK","version":"3.146.0"}

GET https://agenthub.dev01.cygnusalpha.one/auth/sign-up
→ 200
  __NEXT_DATA__.props.pageProps = {
    "signUpDisabled": false,
    "authProviders": {"google":true,"credentials":true,"keycloak":true,...}
  }
```

`signUpDisabled: false` in `__NEXT_DATA__` is a **primary source** — the application's own config, served by the Next.js SSR layer, before any authentication. This is not inference; it is the app declaring its own enrollment policy.

### 3.2 DNS Enumeration Pivots to Production

From `agenthub.dev01.cygnusalpha.one`, enumerate `cygnusalpha.one`:

```
cygnusalpha.one          → 141.193.213.10 (Cloudflare)
www.cygnusalpha.one      → 141.193.213.11 (Cloudflare)
agenthub.cygnusalpha.one → 34.36.249.66   (GCP — PRODUCTION)
agenthub.dev01.*         → 34.0.11.208    (GCP — dev)
api.cygnusalpha.one      → 34.36.249.66   (same as production)
```

Production probe:

```bash
GET https://agenthub.cygnusalpha.one/api/public/health
→ 200 {"status":"OK","version":"3.140.0"}

GET https://agenthub.cygnusalpha.one/auth/sign-up → 200
  "signUpDisabled": false
  authProviders: {"google":true,"credentials":true,...}
```

**Both production and dev01 have open signup.**

---

## 4. Stacked Exposure on 34.0.11.208

menlohunt full port scan on the dev01 GCE VM:

| Port | Service | Auth State | menlohunt Severity |
|---|---|---|---|
| 22 | OpenSSH | N/A | — |
| 80 | HTTP | — | INFO |
| 443 | Langfuse v3.146.0 (HTTPS) | signup-open | INFO (tool gap) |
| 3000 | Langfuse (HTTP, prod-CSP) | TBD | INFO |
| 5432 | PostgreSQL | pg_hba.conf rejection | HIGH |
| 6379 | Redis | AUTH REQUIRED | CRITICAL |
| 9090 | Prometheus | 403 Forbidden | MEDIUM |
| 51819–51821/UDP | WireGuard | candidate | MEDIUM |

**Redis :6379 — AUTH REQUIRED.** Not open. The `CRITICAL` label from menlohunt reflects internet exposure of a Redis port, not unauth access.

**Prometheus :9090 — 403 Forbidden.** IP-based ACL or authentication active. Not unauth.

**Port :3000 — second Langfuse instance.** The CSP at port 3000 differs from port 443 in a significant way: it contains production S3 bucket references:

```
https://prod-uk-services-workspac-workspacefilespublicbuck-vs4gjqpqjkh6.s3.amazonaws.com
https://prod-uk-services-attachm-attachmentsbucket28b3ccf-uwfssb4vt2us.s3.eu-west-2.amazonaws.com
https://prod-uk-services-attachm-attachmentsuploadbucket2-1l2e4906o2asm.s3.eu-west-2.amazonaws.com
```

These are CloudFormation-generated names (`prod-uk-services-*`, `eu-west-2`) for the production UK AWS environment. The dev01 GCE VM in India is configured against production AWS S3 in eu-west-2. It also references:
- `https://chat.uk.plain.com` — Plain.com customer support (UK instance)
- `https://*.stripe.com` — Stripe payments
- `https://login.microsoftonline.com` — Azure AD / Microsoft auth
- `https://graph.microsoft.com` — Microsoft Graph API

This operator is a SaaS company running:
- Production: AWS eu-west-2 (UK) + GCP asia-south1 (agenthub.cygnusalpha.one, 34.36.249.66)
- Dev: GCP asia-south2 (agenthub.dev01.cygnusalpha.one, 34.0.11.208)
- Frontend CDN: Cloudflare (cygnusalpha.one, 141.193.213.x)
- Payments: Stripe
- Support: Plain.com
- Auth: Google OAuth + Microsoft/Azure AD + email credentials + Keycloak (dev only)

---

## 5. Operator Attribution

**Operator:** cygnusalpha.one — "CygnusAlpha" — building "AgentHub"

**GCP project ID:** `ca-dev-01-426608` (dev) — the `ca` prefix = CygnusAlpha initials.

**Production project:** appears to be a separate GCP project hosting `34.36.249.66`.

**Infrastructure posture:** UK AWS production + GCP multi-region + Cloudflare CDN + Stripe + Microsoft identity. This is a company building an AI agent platform with enterprise auth support (Azure AD, Keycloak). Not a hobby project.

**Operator intelligence from Cloud SQL instance names in the broader corpus:**

| GCP Project | Instance | Operator Profile |
|---|---|---|
| tooling-prd-468115 / tooling-dev-463909 | langfuse (prod + dev) | Enterprise — prod/dev pair, "tooling" prefix suggests internal AI infra team |
| dotted-hook-451310 | langfuse-db | Unknown |
| rising-precinct-429608-h9 | langfuse-db-instance | Unknown |
| dataplane-development | pete-langfuse-poc | Individual developer POC — "pete" first name, "poc" confirms experimental |
| ca-dev-01-426608 | ca-dev-langfuse.* | CygnusAlpha dev (this survey's pivot host) |

The `tooling-prd-468115` + `tooling-dev-463909` pair shares the "tooling-" prefix and the instance name "langfuse" — almost certainly the same operator running Langfuse as production observability tooling (prod + dev environments). Two IPs per instance = Cloud SQL public IP primary/replica pair.

---

## 6. Findings

### F1 — Langfuse Open Signup: agenthub.cygnusalpha.one (PRODUCTION)

**Tier:** HIGH (signup-open primary source)  
**Host:** `34.36.249.66` / `agenthub.cygnusalpha.one`  
**Version:** Langfuse v3.140.0  
**Evidence:** `signUpDisabled: false` in `/auth/sign-up` `__NEXT_DATA__`  
**Auth providers:** Google OAuth + email/password credentials  

Any internet user can create a free account on CygnusAlpha's production Langfuse instance. After registration, the user has API access to the Langfuse platform. Depending on multi-tenancy enforcement, the risk surface includes: reading own-project traces (minimal), consuming storage and compute (quota drain), and potentially enumerating other tenant projects if multi-tenancy is misconfigured.

**Verification command:**

```bash
curl -s https://agenthub.cygnusalpha.one/auth/sign-up \
  | python3 -c "
import sys, re, json
body = sys.stdin.read()
m = re.search(r'__NEXT_DATA__[^{]+({.*?})</script>', body, re.DOTALL)
if m:
    d = json.loads(m.group(1))
    pp = d.get('props',{}).get('pageProps',{})
    print('signUpDisabled:', pp.get('signUpDisabled'))
    print('authProviders:', pp.get('authProviders'))
"
# Expected output:
# signUpDisabled: False
# authProviders: {'google': True, 'credentials': True, ...}
```

### F2 — Langfuse Open Signup: agenthub.dev01.cygnusalpha.one (DEV)

**Tier:** HIGH (signup-open primary source)  
**Host:** `34.0.11.208` / `agenthub.dev01.cygnusalpha.one`  
**Version:** Langfuse v3.146.0  
**Evidence:** `signUpDisabled: false` in `/auth/sign-up` `__NEXT_DATA__`  
**Auth providers:** Google OAuth + email/password credentials + Keycloak  

Same signup-open posture on the dev01 instance. Dev instances carry more risk in some configurations (debug endpoints, verbose error messages, less rigorous access controls).

### F3 — Data Tier Internet Exposure (OBSERVED, auth-enforced)

**Tier:** OBSERVED  
**Hosts:** All 11  
**Detail:** Postgres port 5432 internet-accessible. Auth enforced (SCRAM-SHA-256 on Cloud SQL, pg_hba.conf ACL on GCE VM). No unauth access confirmed. Internet exposure of database ports is a hardening failure even when auth is present.

**Remediation:** Disable public IPs on Cloud SQL instances. Use Cloud SQL Auth Proxy for all connections. For the GCE VM: add VPC firewall rules to deny external access to port 5432.

### F4 — Redis + Prometheus Internet Exposure (OBSERVED, auth-enforced)

**Tier:** OBSERVED  
**Host:** `34.0.11.208`  
**Ports:** Redis :6379 (AUTH required), Prometheus :9090 (403)  
**Detail:** Both services are internet-reachable but have auth active. Not an active breach; hardening failure. Redis AUTH can be brute-forced with weak passwords; the attack surface shrinks but does not disappear when it's internet-exposed.

---

## 7. Chain Analysis — What the Data-Tier Dork Actually Finds

The `ssl.cert.subject.cn:langfuse port:5432` dork was framed as a data-tier exposure hunt. The data tier (Langfuse Postgres) is **100% auth-enforced** across 11 hosts. The dork is not an auth-exposure dork. It is an **operator-attribution dork**.

What it actually finds:
1. **GCP project IDs** — revealed in Cloud SQL cert CNs (e.g., `tooling-prd-468115`, `dataplane-development`). These are permanent operator identifiers.
2. **Instance names** — `pete-langfuse-poc` = individual developer experimenting with Langfuse.
3. **The anomalous host** — the one non-Cloud-SQL entry. When every other hit is a managed service, the outlier deserves the deepest look.

The productive path through this survey was: enumerate all 11 → observe auth-enforced on 10 → identify the anomalous 11th → cert-pivot its non-5432 ports → find the inference tier → DNS-enumerate the domain → find production.

The data-tier dork delivered an operator attribution surface. The finding came from following the one anomalous entry all the way to production.

---

## 8. Tool Coverage

| Tool | Result |
|---|---|
| JAXEN (Playwright) | 11 hosts harvested via Shodan UI |
| aimap | Ran; no AI service fingerprints on :5432; Langfuse detected at :443 via lateral |
| VisorGraph | Cert pivot on 34.0.11.208 → agenthub.dev01.cygnusalpha.one (pivotal finding) |
| aimap-profile | Ran; WHOIS resolved Google LLC; Shodan API unavailable |
| JS-bundle | Not applicable — Next.js SSR, no CDN-fronted SPA pattern |
| VisorLog | 6 events ingested to nuclide.db |
| VisorScuba | Score 9/10; 1 warn (signup-open = AI.H1 effective-unauth path) |
| BARE | 0/5 MSF coverage; novel finding class; top score 0.515 (Redis) |
| VisorCorpus | Focused corpus built (prompt_injection, system_prompt, kb_exfiltration, cross_tenant_leak) |
| VisorBishop | Both Langfuse instances confirmed; classified auth-on-API (signup-open gap — tool gap logged) |
| VisorSD | Dry-run; observability stack 4 queries; Shodan API unavailable |
| VisorGoose | Scanned .one TLD |
| menlohunt | 9 findings on 34.0.11.208: Redis CRITICAL, Postgres HIGH, Prometheus MEDIUM, WireGuard MEDIUM |
| recongraph | N/A — VisorGraph covered cert pivot |
| nu-recon | Ran; limited output (no Shodan API) |
| VisorPlus | N/A — VisorGraph ran per-host pass |
| VisorRAG | [ethical-stop — controlled target only, not fired at operator hosts] |
| VisorAgent | [ethical-stop — controlled target only, not fired at operator hosts] |
| VisorHollow | [not applicable — Windows-only] |
| cortex | Ran with --force; schema mismatch (tool gap: needs SKELETON/VIOLATIONS/CONTEXT sections) |

**Tool gap logged:** VisorBishop classifies Langfuse API as `auth: auth` but does not probe `signUpDisabled` in `__NEXT_DATA__`. The signup-open state (Insight #55) requires a separate probe class. Gap: `registration-open` prober for Langfuse fingerprint.

---

## 9. Methodology Observation — Candidate Insight

**Candidate Insight:** TLS-CN data-tier dorks (`ssl.cert.subject.cn:<platform> port:5432`) are operator-attribution surfaces, not auth-exposure surfaces. Langfuse Postgres is auth-on-default (11/11 SCRAM-SHA-256 or pg_hba.conf rejection). The cert pivot on the anomalous non-managed-service entry was the productive path to the inference tier.

Parallels:
- Insight #16: HTTP 200 ≠ auth state. Extended here to: `fe_sendauth: no password supplied` ≠ auth-open Postgres.
- Insight #47: TLS-CN is attribution-only on the inference tier. Confirmed on the data tier: the cert is operator identity, not exposure.
- Insight #20: Data-tier ports adjacent to confirmed AI services are independent signals. Confirmed: the data tier itself was locked; the inference tier co-located with it was not.

The operative move: **data-tier cert pivot to inference tier**. When a data-tier port is locked, the cert names the operator; the operator's domain names the product; the product has an inference tier that may not be.

---

## 10. Remediation

**For cygnusalpha.one:**

1. Set `LANGFUSE_DISABLE_SIGNUPS=true` in environment variables on both `agenthub.cygnusalpha.one` and `agenthub.dev01.cygnusalpha.one`. This flips `signUpDisabled` to `true` in the Next.js config.
2. Remove public IP from the Cloud SQL / GCE Postgres instance. Use VPC-internal connections only.
3. Add VPC firewall rules: deny external access to ports 5432, 6379, 9090, 3000. Allow only from internal VPC CIDRs.
4. Consider whether `agenthub.dev01.cygnusalpha.one` should be internet-accessible at all. Dev instances with production S3 credentials in the CSP carry production-equivalent risk.

**Verification:**

```bash
curl -s https://agenthub.cygnusalpha.one/auth/sign-up \
  | python3 -c "
import sys, re, json
body = sys.stdin.read()
m = re.search(r'__NEXT_DATA__[^{]+({.*?})</script>', body, re.DOTALL)
d = json.loads(m.group(1))
pp = d['props']['pageProps']
assert pp['signUpDisabled'] == True, f'still open: {pp}'
print('REMEDIATED — signUpDisabled: True')
"
```

---

## Toolchain Provenance

```
Dork:       ssl.cert.subject.cn:langfuse port:5432
Harvest:    Playwright → Shodan UI (11 hits)
Auth-probe: python3 raw StartupMessage → SCRAM-SHA-256 / pg_hba.conf
Cert-pivot: visorgraph -ip 34.0.11.208 → agenthub.dev01.cygnusalpha.one
DNS-enum:   socket.gethostbyname * 8 subdomains
App-probe:  urllib.request → /api/public/health, /auth/sign-up, __NEXT_DATA__
Port-sweep: menlohunt scan -ip 34.0.11.208 → 9 findings
Ingest:     visorlog ingest → nuclide.db (6 events)
Score:      VisorScuba 9/10 (1 warn signup-open)
BARE:       0/5 MSF coverage (novel class)
Corpus:     visorcorpus build -type focused
Bishop:     visorbishop -i targets.txt -ip-shadow-all → auth-on-API confirmed
```
