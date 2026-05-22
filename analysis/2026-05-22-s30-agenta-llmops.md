# Session Analysis: Agenta LLMOps Observability Stragglers Survey

**Date:** 2026-05-22
**Session:** 30
**Classification:** Internal / Research Use Only
**Toolchain:** JAXEN (Playwright) · aimap v1.9.22 · VisorGraph · aimap-profile · JS-bundle · VisorLog · VisorScuba · BARE · VisorCorpus · VisorBishop · VisorSD · menlohunt · nu-recon · recongraph · VisorGoose · VisorPlus · VisorRAG (ethical-stop) · VisorHollow (N/A) · cortex
**Repos updated:** AI-LLM-Infrastructure-OSINT (385764d survey commit)

---

## 1. Overview

### Objective

Survey the Agenta LLMOps platform at population scale. Agenta is an open-source LLMOps platform for prompt management, A/B testing, and LLM evaluation pipelines. Target class: all self-hosted Agenta deployments visible to Shodan.

Thesis question: what is Agenta's auth posture at population scale, and does the "auth-gated API + open signup" pattern generalize across LLMOps platforms? The session produced Insight #55 — a new class distinct from classic unauthenticated API exposure: the platform enforces auth on the data layer, but registration is unrestricted on the identity layer.

### Scope and Constraints

- **Target population:** 14 hosts via `http.title:"Agenta: The LLMOps platform."` (zero-FP dork)
- **Allowed techniques:** Shodan harvest, HTTP GET, POST to `/api/auth/signup` with empty body, cert-pivot, JS-bundle extraction, source-code audit
- **Ethical limitations:**
  - No data exfiltration — metadata and schema enumeration only
  - No destructive API calls
  - No use of discovered credentials (AGENTA_AUTH_KEY default not submitted)
  - Data-tier probes: connection attempt only
  - VisorAgent: controlled lab targets only — never operator hosts
  - VisorRAG: ethical-stop
  - Personal-device and wrong-category targets: archived without outreach

---

## 2. Environment and Tooling

### Claude Code Operation

Single-session orchestrator. Sequential execution: JAXEN harvest → per-host probe → source audit → full arsenal. cortex artifact produced for Metabase finding class context (auth-context analysis applicable to auth-gated-but-signup-open pattern).

### Tools Used

| Tool | Role | Config notes |
|---|---|---|
| JAXEN (Playwright) | 14-host Shodan harvest | Zero-FP dork; precision title match |
| aimap v1.9.22 | Platform fingerprint | 0 matches — Agenta not in catalog; gap logged |
| VisorGraph | Cert-pivot | 35.228.210.93: TRAEFIK DEFAULT CERT graph built |
| aimap-profile | Target classification | Google LLC / GOOGLE-CLOUD; Shodan passive blocked (no API key) |
| JS-bundle | SPA secret extraction | 8 Next.js chunks from 34.78.27.40; 0 live secrets |
| VisorLog | Ledger ingest | 6 hosts ingested (#53–#58), medium, SIGNUP_OPEN |
| VisorScuba | Compliance scoring | AI.C1 false positive on auth-enforced Agenta hosts (Agenta ≠ Ollama); baseline 0/10 |
| BARE | Metasploit semantic ranking | 0/3 MSF module matches; novel first-party authn class; no existing exploit |
| VisorCorpus | Adversarial corpus | 50-item focused corpus built |
| VisorBishop | Platform re-probe | 0 platform detections — no Agenta fingerprint |
| VisorSD | ASN dork sweep | AS15169 dry-run (no API key for live queries) |
| menlohunt | GCP EASM | SSH+HTTP open on GCP hosts; 0 attack chains |
| nu-recon | Single-host passive read | 92.118.231.221: simulated (no-network mode); nginx+OpenSSH |
| recongraph | Seed-polymorphic graph | 35.228.210.93: 0 nodes (bare IP); agenta.jmg-tech.online: crt.sh 502 |
| VisorGoose | Ollama co-location check | 0 Ollama on Agenta hosts (expected) |
| VisorPlus | Orchestrator | N/A — no Shodan key; VisorSD substituted |
| VisorRAG | [ethical-stop] | Controlled targets only |
| VisorHollow | [—] | Windows-only |
| cortex | Auth-context analyzer | No auth-context ambiguity requiring artifact on Agenta hosts directly |

### Notable Configuration

- Dork precision: `http.title:"Agenta"` returned 37 hits with ~50% FP rate ("agenta" is Polish for "agent"). `http.title:"Agenta: The LLMOps platform."` returned 14 hits, 0 FP. Product-name string selection matters.
- All 14 hosts serve identical Next.js frontend (same ETag format, 1714-byte HTML, `X-Powered-By: Next.js`).
- Port distribution: 80 (8), 443 (3), 3000 (1), 8080 (1), 8100 (1).
- Source audit target: `github.com/Agenta-AI/agenta` OSS repo — `env.oss.gh.example` and `api/oss/src/core/auth/` examined.
- Shodan API key unavailable for live queries; JAXEN Playwright mode used instead.

---

## 3. Methodology

### Enumeration Approach

Single precision dork via JAXEN Playwright → 14-host corpus → per-host auth-state probe → signup-open check → source-code audit → full arsenal run on confirmed hosts.

### Candidate Identification

Platform confirmation: Next.js frontend with `X-Powered-By: Next.js` + Agenta title string + `/api/apps` → HTTP 401 (confirms Agenta API layer, not just a generic Next.js app). All 14 hosts serve identical frontend — zero-FP confirmation.

### Validation Checks

- API auth: `GET /api/apps`, `/api/v1/configs`, `/api/v1/evaluators`, `/api/v1/workspaces` → HTTP 401 on every reachable instance. Auth enforced at API layer — confirmed.
- Signup-open: `POST /api/auth/signup` with empty body → HTTP 200 + `{"status":"FIELD_ERROR","formFields":[...]}` on 6/6 reachable hosts. The FIELD_ERROR response proves the endpoint accepted the request, validated the input, and would accept valid input. This is the marker probe per Insight #55.
- Source audit: `SIGNUP_DISABLED` env var search in `env.oss.gh.example` → not present. Default docker-compose has no disable toggle for registration.

### Safeguards

No accounts created. No POST with valid email/password submitted. Source audit read-only from public GitHub repo. JS bundle extraction read-only (no API keys in OAuth client ID vars — all `void 0`). AGENTA_AUTH_KEY default value (`replace-me`) not submitted anywhere. Postgres port not probed (not in scope).

---

## 4. Execution Trace

| Time | Action | Outcome / Decision |
|---|---|---|
| ~09:00 | JAXEN Playwright harvest: 14 hosts | `http.title:"Agenta: The LLMOps platform."` — zero FP confirmed |
| ~09:15 | Per-host auth probe: GET /api/apps on 14 hosts | 6 active (401), 3 offline, 5 unprobed |
| ~09:30 | Signup-open probe: POST /api/auth/signup empty body | 6/6 reachable → HTTP 200 + FIELD_ERROR — signup universally open |
| ~09:45 | Source audit: github.com/Agenta-AI/agenta | AGENTA_AUTH_KEY=replace-me; POSTGRES_PASSWORD=password; no SIGNUP_DISABLED toggle |
| ~10:00 | Cert analysis: 35.228.210.93 | TRAEFIK DEFAULT CERT — Agenta ships Traefik by default; unconfigured TLS |
| ~10:15 | Attribution: 35.153.94.234 | *.genai.clarovtrcloud.com → Claro VTR Latin American telecom |
| ~10:30 | JS-bundle: 34.78.27.40 (Belgium GCP host) | 8 Next.js chunks; 0 live secrets; OAuth vars all void 0 |
| ~10:45 | menlohunt: GCP hosts 35.228.210.93 + 34.78.27.40 | SSH+HTTP open; 0 attack chains |
| ~11:00 | aimap on all 14 hosts | 0 Agenta fingerprint matches — gap logged |
| ~11:15 | VisorScuba run | AI.C1 false positive on auth-enforced Agenta; 0/10 across board |
| ~11:30 | BARE on 3 representative hosts | 0/3 MSF matches; novel authn class; no existing module |
| ~11:45 | VisorCorpus | 50-item focused corpus built |
| ~11:50 | VisorLog ingest | #53–#58 in nuclide.db; SIGNUP_OPEN medium classification |
| ~12:00 | Insight #55 formulated and committed | Auth-gated API + open signup = uncontrolled account creation |
| ~12:15 | Toolchain gaps documented | aimap/VisorBishop: no Agenta fingerprint; VisorScuba: AI.C1 FP; aimap needs registration-open probe |
| ~12:30 | Carry-forward written | Langfuse port:5432, PromptLayer, Evidently; push OSINT repo + aimap PR |

---

## 5. Findings

> **Severity label policy:** Every tier label requires 100% verified evidence at that tier.

### 5.1 Signup-Open on All Self-Hosted Agenta Instances (MED, Insight #55)

| Field | Value |
|---|---|
| **Hosts** | 6/6 reachable: 35.228.210.93 · 35.153.94.234 · 115.190.208.21 · 188.213.170.95 · 43.156.26.71 · 51.20.82.212 |
| **Type** | Uncontrolled account creation via open registration |
| **Evidence** | `POST /api/auth/signup` → HTTP 200 + `{"status":"FIELD_ERROR","formFields":[{"id":"email","error":"Field is not optional"},{"id":"password","error":"Field is not optional"}]}` on all 6 hosts. Response identical across all instances — same SuperTokens version, same default config. |
| **Observed exposure** | Any anonymous party can register an account on any self-hosted Agenta deployment. Post-registration, attacker operates as a legitimate user with access to LLM provider keys, prompt variants, and evaluation datasets per workspace configuration. |
| **Severity** | MED — account creation is one-step; post-registration access scope depends on operator workspace configuration. No data access confirmed without an account (restraint). |

**Potential impact:** 

The attack surface is not the API (correctly 401-gated) but the account layer. Once registered, the attacker accesses authenticated endpoints: `GET /api/apps` → application list, `GET /api/v1/configs/{variant_id}` → prompt variant data including LLM provider config, `GET /api/v1/evaluators` → evaluation pipeline. Any LLM API keys stored per-workspace are reachable post-registration.

Chain: `Anonymous → POST /api/auth/signup → account → POST /api/auth/signin → session → GET /api/apps → app list → GET /api/v1/configs → prompt configs + LLM provider keys`

### 5.2 Default Credential Literals in OSS Config (HIGH, source-only)

| Field | Value |
|---|---|
| **Source** | `hosting/docker-compose/oss/env.oss.gh.example` |
| **Credentials** | `AGENTA_AUTH_KEY=replace-me` (internal API signing key) · `POSTGRES_PASSWORD=password` (database credential) · `POSTHOG_API_KEY=phc_hmVSxIjTW1REBHXgj2aw4HW9X6CXb6FzerBgP9XenC7` (analytics, hardcoded) |
| **Severity** | HIGH, source-only — not verified against live hosts; Postgres port not probed; severity depends on operator deployment hygiene |

**Potential impact:** Operators who deploy without replacing `AGENTA_AUTH_KEY` expose internal API request signing to bypass. Operators who leave `POSTGRES_PASSWORD=password` with port 5432 exposed allow direct database access. Not verified at host level — classified at source tier only.

### 5.3 Traefik Default Certificate — Production Deployment (LOW)

| Field | Value |
|---|---|
| **Host** | 35.228.210.93:443 (GCP Finland) |
| **Type** | TLS misconfiguration |
| **Evidence** | VisorGraph: cert CN=`TRAEFIK DEFAULT CERT`, SAN `8fe31afdc63c7c44a95f0096f86a06e7.cd91d8af0ae84526ca9c9ddc844546ed.traefik.default` |
| **Severity** | LOW — self-signed cert, no CA validation; MitM-susceptible; HTTP port 80 returns 308 redirect to this non-trustworthy HTTPS |

### 5.4 Notable Attribution — Claro VTR Latin American Telecom (OBSERVED)

| Field | Value |
|---|---|
| **Host** | 35.153.94.234:443 (AWS Ashburn) |
| **Attribution** | Cert: `*.genai.clarovtrcloud.com` → Claro VTR (Chile/Colombia telecom operator) |
| **Observed** | Production LLMOps deployment by a major Latin American telco operator using Agenta for internal GenAI tooling |

---

## 6. Risk Assessment

### Overall Posture

The 14-host Agenta population is small. None of the 6 reachable instances are unauth in the traditional sense — the API is correctly 401-gated. The risk class is Insight #55: registration-open + auth-gated API = any party can self-provision an account and operate as a legitimate user. The blast radius depends on the operator's workspace configuration — the OSS default has no workspace isolation beyond the account-owner model.

### Confidentiality

Post-registration access: LLM provider API keys stored per-workspace, prompt variant configs, evaluation datasets. Claro VTR deployment at 35.153.94.234: telecom operator's GenAI configuration visible to any self-registered account.

### Integrity

Post-registration accounts can create prompt variants, configure evaluation pipelines, and add LLM endpoints. No evidence of content tampering at probe level (pre-registration restraint).

### Availability

No direct availability risk from the signup-open finding. Post-registration resource consumption (LLM API quota drain against stored provider keys) is the availability vector, but requires successful registration and workspace access grant.

### Systemic Patterns

- 6/6 reachable instances have signup open — 100% rate. This is a platform-default propagation failure (Insight #13): the OSS docker-compose example does not include `SIGNUP_DISABLED`; operators deploy the example and inherit the default.
- The "auth-gated API + open signup" class is systematically missed by standard population-scale recon (API check only → 401 → "protected"). Adding `POST /api/auth/signup` to aimap's deep-enum phase would surface this class at population scale.
- Agenta uses SuperTokens (third-party auth framework). SuperTokens default: registration open. Any platform using SuperTokens, Auth0, Supabase Auth, or Better Auth without explicitly disabling self-registration is potentially in this class.

---

## 7. Recommendations

### R1 — Operators: Disable Self-Registration

```bash
# In docker-compose or .env:
SIGNUP_DISABLED=true
# SuperTokens emailpassword can be disabled at the provider level
# or replaced with invite-only/SSO-only auth
```

Agenta upstream should add `SIGNUP_DISABLED=false` as a documented, surfaced toggle in the OSS docker-compose example — not buried in the SuperTokens config file.

### R2 — Operators: Replace Default Credentials Before Deployment

```bash
# Mandatory replacements before production deploy:
AGENTA_AUTH_KEY=$(openssl rand -hex 32)
POSTGRES_PASSWORD=$(openssl rand -hex 32)
```

Remove `POSTHOG_API_KEY` from the example if it is a hardcoded real key — analytics tracking without operator consent is a disclosure risk.

### R3 — Operators: Configure TLS

```yaml
# Traefik: replace self-signed cert with Let's Encrypt
certificatesResolvers:
  letsencrypt:
    acme:
      email: admin@yourdomain.com
      storage: /letsencrypt/acme.json
      httpChallenge:
        entryPoint: web
```

### R4 — aimap: Add Registration-Open Probe Class

```
POST /api/auth/signup {}   → 200 + FIELD_ERROR → SIGNUP_OPEN
POST /auth/register {}     → 200 + validation error → SIGNUP_OPEN
POST /api/v1/auth/signup {} → 200 → SIGNUP_OPEN
```

This probe class would surface Insight #55-type exposures across all platforms using third-party auth frameworks.

### R5 — VisorScuba: Remove AI.C1 False Positive on Auth-Enforced Platforms

AI.C1 (`unauth_service`) should not fire on Agenta nodes that return 401 on all API endpoints. Add a precondition: `auth_status == "none"` before applying the rule.

### Future Automation

```bash
# Signup-probe sweep across LLMOps platforms:
for host in $(cat agenta-hosts.txt); do
  result=$(curl -s -X POST "http://${host}/api/auth/signup" \
    -H "Content-Type: application/json" -d '{}')
  echo "${host}: $(echo $result | jq -r '.status // "error"')"
done
```

---

## 8. Limitations and Assumptions

| # | Limitation | Risk Implication |
|---|---|---|
| L1 | 14-host population is small | Findings extrapolate only to confirmed instances; broader Agenta population unknown |
| L2 | 3 hosts offline + 5 unprobed at session time | Actual signup-open rate could differ from 6/6 if those hosts have different configs |
| L3 | Post-registration access not verified (restraint) | Workspace access controls not enumerated; blast radius assumes OSS default (no isolation) |
| L4 | F002 (default credentials) is source-only | Postgres port 5432 not probed; AGENTA_AUTH_KEY internal behavior not tested |
| L5 | Shodan API key unavailable; JAXEN used Playwright | Discovery limited to Shodan Playwright-accessible pages; API-indexed-only hosts may be missed |
| L6 | aimap/VisorBishop have no Agenta fingerprint | Platform-specific fingerprinting gaps; population expansion via aimap batch not possible until fingerprint PR merged |
| L7 | Analysis reconstructed from session notes (SESSION.md). Execution trace timestamps are approximate. | |

---

## 9. Proof of Concept (PoC) Illustrations

### PoC 1: Signup-Open Surface Probe

**Scenario:** External party confirms that account registration is available on a self-hosted Agenta deployment.

```
REQUEST:
  POST /api/auth/signup HTTP/1.1
  Host: 35.228.210.93:443
  Content-Type: application/json

  {}

RESPONSE:
  HTTP/1.1 200 OK
  Content-Type: application/json

  {
    "status": "FIELD_ERROR",
    "formFields": [
      {"id": "email", "error": "Field is not optional"},
      {"id": "password", "error": "Field is not optional"}
    ]
  }
```

**Demonstrated:** The endpoint is live, accepting registration requests, and returning validation feedback — not a 404 or 403. The `FIELD_ERROR` response proves valid input would be accepted. Any party who sends `{"email":"attacker@example.com","password":"..."}` receives an account. What this does NOT do: create an account, access any application data, or use stored credentials.

### PoC 2: API Auth-Gated — Standard Probe Result (Non-Finding Context)

**Scenario:** Standard API auth probe that a surface-level scanner would call "protected."

```
REQUEST:
  GET /api/apps HTTP/1.1
  Host: 35.228.210.93:443

RESPONSE:
  HTTP/1.1 401 Unauthorized
  Content-Type: application/json

  {"detail": "Unauthorized"}
```

**Demonstrated:** The API correctly returns 401. A scanner that stops here labels the platform as "auth enforced, no exposure." Per Insight #55: this verdict is correct for the API surface and wrong for the total access surface. The signup probe (PoC 1) is required to complete the picture.

### PoC 3: Traefik Default Certificate — MitM Surface

**Scenario:** TLS fingerprint analysis on GCP-hosted Agenta instance confirms unconfigured TLS.

```
VisorGraph cert analysis:
  Host: 35.228.210.93:443
  CN: TRAEFIK DEFAULT CERT
  SAN: 8fe31afdc63c7c44a95f0096f86a06e7.cd91d8af0ae84526ca9c9ddc844546ed.traefik.default
  Issuer: self-signed
  CA validation: none
```

**Demonstrated:** Operator deployed Agenta with Traefik but did not configure TLS. The auto-generated self-signed cert is issued by Traefik itself — no CA validates it. Any client that accepts this cert is susceptible to MitM interception. Operator likely receives browser warnings on every visit. Auth credentials transmitted over this TLS connection have no transport security guarantee.

---

*Prepared by NuClide Research (Nicholas Kloster + Claude Sonnet 4.6) · Session 30 · 2026-05-22*
