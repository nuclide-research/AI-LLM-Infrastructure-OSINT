# AI Gateways OSINT -- Stage -1
_NuClide Research · 2026-06-01_

Survey category: AI Gateways (threat model: API key aggregation + request routing)
Platforms in scope: 9 (Portkey, Kong AI, Bifrost, one-api, new-api, sub2api, TensorZero, Helicone, Envoy AI Gateway)

---

## Threat Model

Gateway tier concentrates ALL provider keys in one process. Unauth access = master-key compromise:
- All upstream LLM API keys readable from config/env
- Full prompt/response logs accessible (privacy + IP exposure)
- Cost abuse: attacker bills to victim's provider accounts
- SSRF pivot from request routing surface
- Admin API (Kong) = cluster-level RCE via plugin injection

Gateway exposure is categorically worse than individual LLM exposure because the blast radius is the entire provider portfolio, not one model endpoint.

---

## Platform Inventory

### 1. Portkey

| Field | Value |
|---|---|
| Repo | `portkey-ai/gateway` (Apache 2.0) |
| Port | 8787 (default) |
| Auth state | Auth-on-default: API key required (`x-portkey-api-key`) |
| Admin UI | None (pure API proxy) |
| CVE | CVE-2025-66405 -- SSRF via `x-portkey-custom-host` header, `< v1.14.0`, CVSS 6.9 |
| Verification primitive | `GET / → "AI Gateway says hey"` (body string, no auth required for health check) |
| Favicon | None (no web UI) -- body string dork only |
| CT findings | 963 certs; `grafana.portkey.ai` + `loki.portkey.ai` (observability stack); `panic-button-{doordash,xero,jhu,pge,cba,ascend,analog}` SANs confirming enterprise verticals (finance, utilities, healthcare, education) |
| Population estimate | Low (API proxy, no web UI for favicon dork) |
| Self-host exposure | SSRF via custom-host header if unpatched; auth bypassable if `PORTKEY_API_KEY` env not set |
| Notes | panic-button-* = Portkey SaaS, not self-hosted. Self-hosted instances: fingerprint via body string only. |

### 2. Kong AI Gateway

| Field | Value |
|---|---|
| Repo | `Kong/kong` (BSL) |
| Port | 8000 (proxy), 8001 (Admin API), 8002 (Kong Manager UI), 8443/8444 (TLS) |
| Auth state | Admin API **unauth by default** in docker-compose deployments (CVE-2020-11710, CVSS 9.8) |
| Admin UI | Kong Manager at :8002 |
| CVE | CVE-2020-11710 -- Admin API bound to `0.0.0.0:8001` in default docker-compose; pre-function plugin enables RCE via unauthenticated Admin API |
| Verification primitive | `GET :8001/ → {"version":"...","tagline":"Welcome to kong"}` |
| Favicon hash | `-112038367` (Kong Manager at :8002) |
| CT findings | 4,000 certs, 2,305 unique names; `admin.konnect-{dev,dev2,stage,prod,prod2}.konghq.com`; per-engineer dev subdomains (`admin.colin-*.konnect-dev2.konghq.com`); staging environments with public certs; Konnect SaaS tiered (dev/stage/prod lanes visible) |
| Population estimate | HIGH -- "Welcome to kong" :8001 is a well-documented exposed surface; large Docker install base |
| Self-host exposure | Admin API RCE chain: `POST /services` + `POST /plugins` (pre-function) → arbitrary Lua execution |
| Notes | Konnect (SaaS) is separate from self-hosted Kong; CT reveals full Konnect infra naming convention |

### 3. Bifrost (maximhq/bifrost)

| Field | Value |
|---|---|
| Repo | `maximhq/bifrost` (Apache 2.0) |
| Port | 8080 (default) |
| Auth state | Basic auth configurable but **root path bypass** (Issue #937) -- `/` returns 200 unauthenticated even with auth enabled |
| Admin UI | Web UI at :8080 |
| CVE | No CVE assigned; auth bypass on root path documented in GitHub issues |
| Verification primitive | `GET :8080/ → HTTP 200 with Bifrost UI` (even with auth configured) |
| Favicon hash | `1651823509` (163,670 bytes, multi-res ICO bundle) |
| CT findings | crt.sh 502 at query time -- retry pending |
| Population estimate | Medium -- newer project, growing Docker install base |
| Self-host exposure | Root path bypass leaks UI; deeper paths may expose config depending on version |
| Notes | Positioned as multi-provider gateway; auth bypass means the web UI is accessible regardless of auth config |

### 4. one-api (songquanpeng/one-api)

| Field | Value |
|---|---|
| Repo | `songquanpeng/one-api` (MIT) |
| Port | 3000 (default) |
| Auth state | **Default credentials: `root` / `123456`** -- no forced change on first run |
| Admin UI | Full admin dashboard at :3000 |
| CVE | No CVE; default creds documented in README and actively exploited |
| Verification primitive | `GET :3000/ → "One API" title`; `POST /api/user/login {"username":"root","password":"123456"}` → JWT |
| Favicon hash | `1318451613` |
| CT findings | Pending (openai-proxy.com crt.sh timeout) |
| Population estimate | HIGH -- 1.19M Docker Hub pulls; Chinese LLM relay ecosystem primary relay |
| Self-host exposure | Default creds = full admin: read all configured API keys, add/remove providers, view all usage logs |
| Notes | Most-deployed platform in this category; default creds have been exploited in the wild. Chinese-operator ecosystem primary aggregator for OpenAI/Claude/Gemini relay. |

### 5. new-api (QuantumNous/new-api)

| Field | Value |
|---|---|
| Repo | `QuantumNous/new-api` (fork of one-api) |
| Port | 3000 (default) |
| Auth state | Inherits one-api default creds (`root` / `123456`) -- same vuln, different favicon |
| Admin UI | Full admin dashboard at :3000 |
| CVE | No CVE; same default-cred pattern as one-api |
| Verification primitive | `GET :3000/ → "New API" title`; same login endpoint as one-api |
| Favicon hash | `-1643864359` (distinct from one-api -- no cross-dork FP) |
| CT findings | Pending |
| Population estimate | Medium -- smaller install base than one-api; growing in Chinese operator ecosystem |
| Self-host exposure | Same as one-api: default creds → full key read |
| Notes | Distinguish from one-api via favicon hash or title string. Both share the root/123456 vector. |

### 6. sub2api

| Field | Value |
|---|---|
| Repo | Various (subscription-to-API relay) |
| Port | Varies (commonly 3000 or 8080) |
| Auth state | Varies by deployment; commonly no auth on admin routes |
| Admin UI | Varies |
| CVE | None assigned |
| Verification primitive | TBD -- needs fingerprinting pass |
| Favicon hash | TBD |
| CT findings | crt.sh timeout (sub2api.org) |
| Population estimate | Unknown -- small niche operator ecosystem |
| Self-host exposure | Subscription relay: exposes payment + API key associations if admin unauth |
| Notes | Niche relay platform; scope TBD pending fingerprint research |

### 7. TensorZero

| Field | Value |
|---|---|
| Repo | `tensorzero/tensorzero` (Apache 2.0) |
| Port | 3000 (gateway), no admin UI |
| Auth state | Auth-on-default: function-level auth via config |
| Admin UI | None (pure API) |
| CVE | None |
| Verification primitive | `GET :3000/health → {"status":"ok"}` |
| Favicon hash | `1457979471` (⚠ SVG only -- Shodan returns 404 for .ico; do not use) |
| CT findings | 473 certs; `autopilot.staging.tensorzero.com`, `nanoagent.staging.tensorzero.com` (agentic pipeline staging with public certs); `proxy.code.tensorzero.com` (Cursor/coding agent proxy); `api-kube.tensorzero.com` (K8s surface); `authapi.tensorzero.com` (separate auth endpoint) |
| Population estimate | Low -- newer project, smaller install base |
| Self-host exposure | Config file exposes all model credentials if readable; no admin RCE surface |
| Notes | `proxy.code.tensorzero.com` = Cursor proxy endpoint; confirms coding-agent use case. Staging envs on public certs = internal infra naming exposed permanently. |

### 8. Helicone (self-hosted)

| Field | Value |
|---|---|
| Repo | `Helicone/helicone` (Apache 2.0) |
| Port | 8585 (worker), 3000 (web UI) |
| Auth state | Auth-on-default: Supabase auth for hosted; self-hosted may skip auth in dev configs |
| Admin UI | Web UI at :3000 |
| CVE | None |
| Verification primitive | `GET :8585/ → Helicone worker response` |
| Favicon hash | `-794809853` (187,078 bytes) |
| CT findings | crt.sh 404 at query time -- retry pending |
| Population estimate | Low-medium -- in maintenance mode for self-hosted path; SaaS primary |
| Self-host exposure | Dev/staging deploys may lack auth; worker endpoint at :8585 logs all LLM traffic |
| Notes | Company shifted focus to SaaS; self-hosted instances persist but may be unmaintained. Worker port different from web UI port. |

### 9. Envoy AI Gateway

| Field | Value |
|---|---|
| Repo | `envoyproxy/ai-gateway` (Apache 2.0) |
| Port | 9901 (Envoy admin), 10000+ (gateway listener) |
| Auth state | Admin endpoint **unauth by default**: `GET :9901/config_dump` returns full Envoy config |
| Admin UI | Envoy admin at :9901 |
| CVE | None specific to AI gateway; Envoy admin exposure is well-documented |
| Verification primitive | `GET :9901/config_dump → full JSON config including upstream cluster auth tokens` |
| Favicon hash | N/A (no web UI favicon) |
| CT findings | N/A (infrastructure component, not a product with its own domain) |
| Population estimate | Medium -- Envoy is widely deployed; AI gateway extension adoption growing |
| Self-host exposure | config_dump at :9901 leaks all upstream cluster credentials: API keys, JWTs, auth hashes in plaintext |
| Notes | Worst-case single-endpoint exposure in this category: one HTTP GET yields the entire credentials config. The admin port must be firewalled. |

---

## Population Estimates by Platform

| Platform | Estimated Exposed Pop | Confidence | Basis |
|---|---|---|---|
| one-api | HIGH (>1,000) | High | 1.19M Docker pulls; prior Shodan surveys confirm large exposure |
| Kong Admin API | HIGH (>500) | High | CVE-2020-11710 documented; well-known attack surface |
| new-api | MEDIUM (100-500) | Medium | Fork of one-api; smaller but growing install base |
| Bifrost | MEDIUM (50-200) | Medium | Newer project; growing; favicon hash dork TBD |
| Helicone | LOW-MEDIUM (50-150) | Medium | Maintenance mode; legacy installs persist |
| Portkey | LOW (10-50) | Low | Pure API proxy; no web UI; harder to fingerprint |
| TensorZero | LOW (<50) | Low | Newer/niche; no admin UI surface |
| Envoy AI Gateway | UNKNOWN | Low | Envoy admin :9901 exposure size unknown; needs survey |
| sub2api | UNKNOWN | Low | Niche; needs fingerprint research |

---

## CVE Summary

| CVE | Platform | CVSS | Vector | Fixed in |
|---|---|---|---|---|
| CVE-2025-66405 | Portkey | 6.9 | SSRF via `x-portkey-custom-host` header | v1.14.0+ |
| CVE-2020-11710 | Kong | 9.8 | Admin API bound to 0.0.0.0:8001 in docker-compose | Admin API must be explicitly secured |
| N/A | Bifrost | N/A | Auth bypass: root path returns 200 unauth (Issue #937) | Patch TBD |
| N/A | one-api | N/A | Default creds `root`/`123456` in README; no forced change | Operator must change |
| N/A | new-api | N/A | Inherits one-api default creds | Operator must change |
| N/A | Envoy AI GW | N/A | Admin :9901 `/config_dump` plaintext credentials | Admin port must be firewalled |

---

## Verification Primitives (aimap probe targets)

```bash
# Portkey -- health check (no auth)
GET :8787/
# Expect: body contains "AI Gateway says hey"

# Kong Admin API -- version probe (unauth)
GET :8001/
# Expect: {"version":"...","tagline":"Welcome to kong"}

# Kong Admin API -- deep enum (read all services)
GET :8001/services
# Expect: {"data":[...],"next":null} -- any data = unauth admin

# Bifrost -- root bypass (even with auth configured)
GET :8080/
# Expect: HTTP 200 with web UI (not 401/403)

# one-api / new-api -- default creds check
POST :3000/api/user/login
{"username":"root","password":"123456"}
# Expect: {"success":true,"data":{"token":"..."}} = default creds active

# one-api / new-api -- title fingerprint
GET :3000/
# Expect: "One API" or "New API" in <title>

# TensorZero -- health check
GET :3000/health
# Expect: {"status":"ok"}

# Helicone worker -- fingerprint
GET :8585/
# Expect: Helicone worker response (varies)

# Envoy AI Gateway admin -- config dump (the money shot)
GET :9901/config_dump
# Expect: full JSON config; grep for "api_key", "authorization", "bearer"
```

---

## VisorGraph Seeds

| Platform | CT-derived seeds |
|---|---|
| Portkey | `api.portkey.ai`, `gcp-proxy.portkey.ai`, `gateway-proxy.privatelink-gcp.portkey.ai`, `grafana.portkey.ai` |
| TensorZero | `api.tensorzero.com`, `authapi.tensorzero.com`, `gcp-us-central1.api.tensorzero.com`, `api-kube.tensorzero.com` |
| Kong | `admin.konnect-prod.konghq.com`, `admin.konnect-prod2.konghq.com`, `api-basic.konnect-prod.konghq.com` |
| Others | Pending CT retries (Bifrost, Helicone) |

---

## Checklist Notes (METHODOLOGY alignment)

- **Stage 0 (JAXEN):** 15 dorks ready in `shodan/queries/32-ai-gateways.md`
- **Stage 0b (Censys):** 7 credits remaining; use for Kong + Bifrost CT enrichment
- **Stage 1 (aimap):** 6 new fingerprints needed (Portkey :8787, Kong :8001, Bifrost :8080, one-api :3000, Envoy :9901, TensorZero :3000)
- **Stage 3 (VisorGraph):** Seeds listed above; additional seeds after JAXEN harvest
- **Verification gate:** Default-cred check and root-bypass check are destructive-equivalent -- stop at confirmed-accessible, do not authenticate; log "default cred state confirmed" not "logged in"
