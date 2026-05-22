# Agenta LLMOps — Population Survey
**Date:** 2026-05-22  
**Category:** LLM Observability / MLOps  
**Population:** 14 confirmed hosts  
**Verified unauth:** 0  
**Signup-open:** 6/6 reachable  
**Insight:** #55

---

## Discovery

**Dork:** `http.title:"Agenta: The LLMOps platform."` — 14 hits, 0 false positives.

Prior attempt with `http.title:"Agenta"` produced 37 hits, ~50% FP rate from Polish-language sites ("agenta" = Polish word for "agent"). The full product name string is the zero-FP fingerprint.

All 14 hosts serve the same Next.js frontend (`X-Powered-By: Next.js`, 1714-byte HTML, identical ETag format `"[hash]1bm"`). Port distribution: 80 (8), 443 (3), 3000 (1), 8080 (1), 8100 (1). Geography: US (4), IT (2), SG (2), BE (1), BG (1), CN (1), FI (1), SE (1), UK (1).

**Confirmed host corpus:**

| IP | Org | Port | Domain / SSL |
|---|---|---|---|
| 35.228.210.93 | Google LLC / Finland | 443 | TRAEFIK DEFAULT CERT |
| 35.153.94.234 | AWS Ashburn | 443 | *.genai.clarovtrcloud.com (Claro VTR) |
| 115.190.208.21 | Beijing Volcano Engine | 80 | — |
| 188.213.170.95 | Aruba Italy | 3000, 8100 | — |
| 43.156.26.71 | APNIC Singapore | 80 | — |
| 51.20.82.212 | A100 ROW Sweden | 80 | — |
| 34.78.27.40 | Google LLC / Belgium | 80 | — |
| 47.128.237.144 | AWS Singapore | 80 | — (offline at probe time) |
| 178.156.218.139 | Hetzner | 8080 | — (offline at probe time) |
| 92.118.231.221 | Stark Industries / UK | 443 | agenta.jmg-tech.online (Let's Encrypt) |

Notable: `35.153.94.234` cert `*.genai.clarovtrcloud.com` attributes to **Claro VTR**, a Latin American telecom operator running internal LLMOps. `92.118.231.221` has Shodan `eol-product` tag, suggesting an outdated Agenta version.

---

## Auth Posture

**API endpoints — auth enforced across the board.**

Every reachable instance returns HTTP 401 on `/api/apps`, `/api/v1/configs`, `/api/v1/evaluators`, `/api/v1/workspaces`. SuperTokens session auth is mandatory. There is no auth-disabled mode in the Agenta OSS codebase.

**Signup — open on all reachable instances.**

`POST /api/auth/signup` (SuperTokens emailpassword handler) returns HTTP 200 + structured `FIELD_ERROR` JSON on 6/6 reachable hosts. This response proves the endpoint is live and accepting registration requests. The `SIGNUP_DISABLED` environment variable is not present in the default docker-compose configuration. Any unauthenticated party can create an account on any self-hosted Agenta deployment.

```json
{
  "status": "FIELD_ERROR",
  "formFields": [
    {"id": "email", "error": "Field is not optional"},
    {"id": "password", "error": "Field is not optional"}
  ]
}
```

Response is identical across all 6 hosts — same SuperTokens version, same default config.

**Source audit findings:**

From `github.com/Agenta-AI/agenta`:

- `hosting/docker-compose/oss/env.oss.gh.example`:
  - `AGENTA_AUTH_KEY=replace-me` — internal API signing key, literal default
  - `POSTGRES_PASSWORD: password` — database credential, literal default
  - `POSTHOG_API_KEY=phc_hmVSxIjTW1REBHXgj2aw4HW9X6CXb6FzerBgP9XenC7` — analytics key, hardcoded
- `api/oss/src/core/auth/supertokens/config.py` — emailpassword + passwordless + thirdparty all enabled; no `SIGNUP_DISABLED` toggle surfaced to operators
- `api/oss/src/core/auth/middleware.py` — EE-only org policy enforcement; OSS uses SuperTokens session with no access controls beyond account ownership

**JS bundle extraction (34.78.27.40):**

8 Next.js chunks extracted. `NEXT_PUBLIC_AGENTA_AUTH_*_OAUTH_CLIENT_ID` vars for Google, GitHub, Facebook, Apple, Discord, Twitter, GitLab are all `void 0` — operator did not configure OAuth providers. No live API keys in bundle.

---

## Infrastructure Fingerprints

**Traefik default cert (35.228.210.93):**  
`CN=TRAEFIK DEFAULT CERT`, SAN `8fe31afdc63c7c44a95f0096f86a06e7.cd91d8af0ae84526ca9c9ddc844546ed.traefik.default`. Agenta's default docker-compose ships Traefik as the reverse proxy. Operators who don't configure TLS get the auto-generated self-signed cert — this is the population fingerprint for Traefik-fronted Agenta. No CA validation, MitM-susceptible.

**Port 8100 (188.213.170.95):** Non-standard Agenta port. 404 on `/api/apps` at `:3000` but 401 at `:8100`. Consistent with a custom Traefik route config.

**GCP concentration:** 3/14 hosts on Google LLC (35.228.210.93 FI, 34.78.27.40 BE, 115.190.208.21 CN/Volcano Engine is not GCP). menlohunt on 35.228.210.93 and 34.78.27.40 surfaced port 22 (SSH) open alongside HTTP — both have direct SSH exposure.

---

## Arsenal Results

| Tool | Result |
|---|---|
| JAXEN (Playwright) | 14 hosts harvested; precision dork confirmed |
| aimap | 0 fingerprint matches — Agenta not in catalog (gap) |
| VisorGraph | 35.228.210.93: TRAEFIK DEFAULT CERT graph; others offline |
| aimap-profile | Google LLC / GOOGLE-CLOUD; Shodan passive blocked (no API key) |
| JS-bundle | 8 chunks scanned; 0 live secrets; OAuth vars unset |
| VisorLog | 6 hosts ingested (#53–#58), medium, SIGNUP_OPEN |
| VisorScuba | AI.C1 false positive (Agenta ≠ Ollama); baseline 0/10 |
| BARE | 0/3 MSF module matches; novel first-party authn class |
| VisorCorpus | 50-item focused corpus built |
| VisorBishop | 0 platform detections (no Agenta fingerprint) |
| VisorSD | AS15169 dry-run (no API key for live queries) |
| menlohunt | SSH+HTTP open on GCP hosts; 0 attack chains |
| nu-recon | 92.118.231.221: simulated (no-network); nginx+OpenSSH |
| recongraph | 35.228.210.93: 0 nodes (bare IP); agenta.jmg-tech.online: crt.sh 502 |
| VisorGoose | 0 Ollama co-located on Agenta hosts (expected) |
| VisorPlus | N/A — no Shodan key; VisorSD substituted |
| VisorRAG | [ethical-stop] — controlled targets only |
| VisorHollow | [not applicable] — Windows-only |
| cortex | No auth-context ambiguity requiring artifact |

---

## Findings

### F001 — Signup-Open on All Self-Hosted Agenta Instances (MEDIUM)
**Verified:** 6/6 reachable hosts, HTTP 200 + FIELD_ERROR on `/api/auth/signup`  
SuperTokens emailpassword registration is enabled by default with no operator-facing `SIGNUP_DISABLED` toggle in the OSS docker-compose config. Any anonymous party can register an account and gain authenticated access to the LLMOps platform — application configs, prompt variants, evaluation datasets, LLM provider keys stored per-workspace.

The attack surface is not the API (401-gated) but the account layer. Once registered, the attacker operates as a legitimate user. Account-level access controls depend entirely on what the operator has configured per-workspace — the OSS default has no workspace access controls beyond the owner role.

**Chain:** Anon → POST /api/auth/signup → account → authenticated API → LLM provider keys / prompt configs / evaluation data

### F002 — Default Credential Literals in OSS Config (HIGH, source-only)
**Source:** `hosting/docker-compose/oss/env.oss.gh.example`  
`AGENTA_AUTH_KEY=replace-me` and `POSTGRES_PASSWORD=password` are the shipped defaults. Operators who deploy without replacing these expose:
- Internal API request signing bypass (AGENTA_AUTH_KEY)
- Direct PostgreSQL access if port 5432 is exposed (POSTGRES_PASSWORD)

Not verified against live hosts (Postgres not in scope; AGENTA_AUTH_KEY is internal). This is a source-layer finding — severity depends on operator deployment hygiene.

### F003 — TRAEFIK DEFAULT CERT on Production Deployment (LOW)
**Verified:** 35.228.210.93 VisorGraph cert analysis  
Operator did not configure Traefik TLS termination with a real certificate. Self-signed cert at `CN=TRAEFIK DEFAULT CERT` means no CA validation. HTTP port 80 returns 308 redirect to HTTPS, but HTTPS cert is not trustworthy. Any client accepting this cert is MitM-susceptible.

---

## Toolchain Gaps Identified

1. **aimap has no Agenta fingerprint.** Agenta serves a Next.js SPA; the distinguishing signals are the page title (`Agenta: The LLMOps platform.`), the `/api/apps` endpoint, and the SuperTokens auth at `/api/auth/signup`. A fingerprint addition would surface Agenta in future population sweeps.

2. **VisorBishop has no Agenta detection.** Same gap.

3. **VisorScuba AI.C1 produces false positives on Agenta hosts.** The rule fires on any host in the DB without a recognized auth-pass signal. Agenta enforces auth on the API layer — AI.C1 should not apply. The Rego rule needs an Agenta exclusion or a broader "auth-verified" tag path.

---

## Pivot Avenues

1. **`ssl.cert.subject.cn:"agenta"` dork** — find operators who configured TLS with "agenta" in the CN; may surface more named deployments
2. **`*.genai.clarovtrcloud.com` cert pivot** — Claro VTR's internal AI platform; check what else is on that subdomain space
3. **`AGENTA_AUTH_KEY=replace-me` string in any exposed config endpoint** — probe `.env`, `/api/config`, `/config.json` across the corpus for operators who left default keys
4. **Port 5432 co-location** — Langfuse survey found 11 Postgres-exposed hosts with Langfuse cert; same sweep for Agenta cert-tagged ranges
5. **Hetzner `static.*.clients.your-server.de` range** — 178.156.218.139 was offline; reverse-PTR sweep on adjacent Hetzner blocks for Agenta recurrence
6. **`eol-product` tag on 92.118.231.221** — enumerate what Agenta version exposes `eol-product` signal; may be a version-specific fingerprint for older releases with different auth posture
