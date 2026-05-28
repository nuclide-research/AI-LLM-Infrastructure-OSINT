# Auth / API Gateway — Shodan Query Catalog
_Generated: 2026-05-27 from pre-survey OSINT pass (11 platforms)_
_See: data/platform-intel/auth-gateway-osint-2026-05-27.md for full intel_
_Note: LiteLLM proxy (cat-01) and Portkey self-hosted (cost survey) already covered._

**Threat model:** These platforms are the auth layer in front of AI stacks. An exposed admin interface = full bypass of whatever auth protects the downstream LLM/vector DB/agent infrastructure.

---

## Kong Gateway

**Auth default (admin):** off (admin API binds 127.0.0.1 by default; Kong Manager ships with no auth when bound to 0.0.0.0)
**Exposure class:** Full gateway config — routes, services, all plugin configs including API keys, JWT secrets, upstream addresses; write access strips auth from any route

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:8001 "via: kong" http.status:200` | Via header with "kong" on admin port is a clean signal; admin responds 200 at root | Low |
| secondary | `port:8002 http.title:"Kong Manager" http.status:200` | Kong Manager UI on port 8002; title is exact | Low |
| tertiary | `http.headers.via:"kong" port:8001` | Header-field search; targets banner crawls | Low |
| identity-probe | `GET / port:8001` → JSON `{"tagline":"Welcome to kong","version":"..."}` | Root admin endpoint returns version + tagline; no auth required | — |

---

## Tyk Gateway

**Auth default (admin):** default-creds (`352d20ee67be67f6340b4c0605b044b7` shipped in tyk.conf.example; Dashboard ships with configurable admin secret)
**Exposure class:** API definitions, upstream auth credentials, rate limit configs, organization and key data; default-secret instances expose full gateway control API

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:8080 "x-tyk-gateway" http.status:200` | `X-Tyk-Gateway` response header is unique to Tyk proxy port | Low |
| secondary | `port:3000 http.title:"Tyk Dashboard" http.status:200` | Tyk Dashboard UI title; port 3000 has FP risk from other dashboards | Med |
| tertiary | `port:8080 "tyk" "/tyk/reload" http.status:200` | Control API path present in HTTP crawl body | Med |
| identity-probe | `GET /tyk/reload/ header:X-Tyk-Authorization:352d20ee67be67f6340b4c0605b044b7` → `{"status":"ok"}` | Default secret probe; 200 = unrotated default | — |

---

## OPA (Open Policy Agent)

**Auth default (admin):** off (docs: "OPA does not perform authentication or authorization and these flags default to `off`")
**Exposure class:** All Rego policy source code (full infra access control logic, service names, roles), merged data document (can contain secrets), audit logs; Trend Micro found 389 unauthenticated OPA servers in 2022

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:8181 "v1/data" http.status:200` | OPA REST API path in response body; port 8181 rarely used by other services | Low |
| secondary | `port:8181 "/v1/policies" http.html:"policies"` | Policy endpoint in crawled body | Low |
| tertiary | `http.html:"Open Policy Agent" port:8181` | OPA surfaces its identity in some UI paths | Med |
| identity-probe | `GET /v1/policies port:8181` → 200 + JSON array of Rego policies | No auth required by default; non-empty result = policy data exposed | — |

---

## OPAL (Open Policy Administration Layer)

**Auth default (admin):** off in demo/dev mode (token auth requires explicit RSA key pair config; disabled in quickstart)
**Exposure class:** Policy update streams, OPA data document feeds, webhook configurations including GitHub tokens and S3 bucket URLs used as policy sources

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:7002 "opal" http.status:200` | Port 7002 is OPAL-specific; low ambient traffic | Low |
| secondary | `port:7002 "topics" http.html:"opal_updates"` | OPAL pub/sub topic names in body | Low |
| identity-probe | `GET /healthcheck port:7002` → 200 + OPAL server info | Health endpoint confirms OPAL; REST API then accessible | — |

---

## Authentik

**Auth default (admin):** on (login required); however, `/api/v3/root/config/` and `/api/v3/schema/` accessible pre-auth; initial setup flow may be open on fresh installs
**Exposure class:** Full user database, all OAuth2 client secrets, LDAP/SAML connector credentials, session tokens; CVE-2024-47070 bypasses password stage via X-Forwarded-For manipulation

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:9000 http.title:"authentik" http.status:200` | Title is exact match; port 9000 used by Authentik by default | Med |
| secondary | `port:9000 "/api/v3/" "authentik" http.status:200` | API path in crawled body confirms Authentik | Low |
| tertiary | `http.html:"goauthentik.io" port:9000` | Source URL referenced in Authentik pages | Low |
| initial-setup | `port:9000 "/if/flow/initial-setup/" http.status:200` | Open initial setup flow = admin account creation available | Low |
| identity-probe | `GET /api/v3/root/config/ port:9000` → 200 + `{"error_reporting":...}` JSON | Unauthenticated config endpoint; confirms Authentik version | — |

---

## Authelia

**Auth default (admin):** on (no admin API; management via config file only)
**Exposure class:** Login portal to all downstream services; brute-force surface; endpoint enumeration via forward auth headers; not a direct data store

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:9091 http.title:"Authelia" http.status:200` | Title exact match on default port | Low |
| secondary | `port:9091 "/api/health" http.status:200` | Health endpoint in Authelia; no auth required | Low |
| identity-probe | `GET /api/health port:9091` → 200 + `{"status":"OK"}` | Confirms Authelia running; use primarily as inventory signal | — |

---

## Keycloak

**Auth default (admin):** on (login required for admin console); `/realms/master` and OIDC discovery endpoints are unauthenticated by spec; unauthenticated `/admin/{realmId}/console/config` leaks client secret when console client is confidential (open issue)
**Exposure class:** Admin breach → all users, groups, roles, OAuth2 client secrets for all realms, LDAP bind credentials, SAML signing keys; CVE-2024-3656 lets low-privilege users call admin REST APIs

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:8080 http.title:"Keycloak" http.status:200` | Title exact match; large population | Low |
| secondary | `port:8080 "/realms/master" "public_key" http.status:200` | Master realm metadata endpoint in crawled body | Low |
| tertiary | `port:8080 "/auth/realms/master" http.html:"public_key"` | Legacy path prefix (Keycloak < v17); still present in many deployments | Low |
| identity-probe | `GET /realms/master port:8080` → 200 + `{"realm":"master","public_key":"...","token-service":"..."}` | Unauthenticated OIDC metadata; confirms Keycloak + version inference from key algorithm | — |

---

## Zitadel

**Auth default (admin):** on (System API requires JWT/PAT); but OIDC discovery unauthenticated; Docker quickstart configs often commit `InitialAdminPassword` in plaintext
**Exposure class:** Admin breach → all organizations, users, service accounts, OAuth2 clients, secrets; System API is superordinate over all instances

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:8080 http.title:"ZITADEL" http.status:200` | Title exact match | Low |
| secondary | `port:8080 "/ui/console" http.html:"ZITADEL"` | Console path in body | Low |
| tertiary | `http.html:"zitadel" port:8080 http.html:"Login"` | ZITADEL login page content | Med |
| identity-probe | `GET /.well-known/openid-configuration port:8080` → 200 + JSON `issuer` containing "zitadel" | Unauthenticated OIDC discovery; issuer URL uniquely identifies Zitadel | — |

---

## Ory Kratos

**Auth default (admin):** off (admin port 4434 has zero auth by design; Ory docs: "must not be available to public")
**Exposure class:** Full user identity database (emails, usernames, credentials metadata), session data, recovery/verification tokens; write access enables creating admin users and invalidating sessions

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:4434 "identities" http.status:200` | Admin API identity endpoint in body; port 4434 near-unique | Low |
| secondary | `port:4434 "/admin/identities" http.html:"identities"` | Admin path in crawled content | Low |
| tertiary | `port:4433 "csrf_token" "flow" http.status:200` | Public API fingerprint (lower risk, inventory signal) | Med |
| identity-probe | `GET /admin/identities port:4434` → 200 + JSON array of user objects | No auth; non-empty array = live user database exposed | — |

---

## Ory Hydra

**Auth default (admin):** off (admin port 4445 has zero auth by design; Ory docs: "must not be available to public")
**Exposure class:** All OAuth2 client IDs and secrets, consent/login session state, JWT grant issuers, trusted key sets; write access enables creating OAuth2 clients with arbitrary redirect URIs

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:4445 "clients" http.status:200` | OAuth2 clients endpoint on admin port; 4445 near-unique | Low |
| secondary | `port:4445 "/admin/clients" http.html:"client_id"` | Admin clients path + field name in body | Low |
| tertiary | `port:4444 "hydra" "/.well-known/openid-configuration"` | Public OIDC endpoint confirms Hydra; inventory use | Low |
| identity-probe | `GET /admin/clients port:4445` → 200 + JSON array with `client_id`, `client_secret` fields | No auth; client secrets exposed if Hydra stores them (non-PKCE clients) | — |

---

## Casdoor

**Auth default (admin):** default-creds (`built-in/admin` / `123`; documented in official docs and pentest-tools.com)
**Exposure class:** Full IAM — users, organizations, OAuth2 apps, LDAP configs, SAML providers, MCP server configs; CORS CVE-2024-41657 allows any origin to make authenticated API calls

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:8000 http.title:"Casdoor" http.status:200` | Title exact match; port 8000 has FP risk | Med |
| secondary | `port:8000 "/api/get-app-list" http.status:200` | Casdoor-specific API path in body | Low |
| tertiary | `http.html:"casdoor" port:8000 http.html:"built-in"` | "built-in" organization name unique to Casdoor | Low |
| identity-probe | `GET /api/get-app-list port:8000` → 200 + JSON array (may not require auth on older versions); `POST /api/login` with `{"username":"admin","password":"123","organization":"built-in","application":"app-built-in"}` → session token | Default creds probe | — |

---

## SuperTokens

**Auth default (admin):** off by default (no API key configured = all endpoints accessible from any source)
**Exposure class:** Full user identity store — session tokens, password hashes, MFA state, JWT signing keys, refresh tokens, email verification codes; `/recipe/user/id` returns full user records without auth when API key absent

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:3567 "Hello" http.status:200` | `/hello` returns exactly "Hello" on SuperTokens; port 3567 is near-unique | Low |
| secondary | `port:3567 "/apiversion" http.status:200` | CDI version endpoint; unique to SuperTokens | Low |
| tertiary | `port:3567 "supertokens" http.status:200` | SuperTokens in response body (error messages, headers) | Med |
| identity-probe | `GET /hello port:3567` → 200 `"Hello"` (no auth); `GET /apiversion` → 200 + `{"versions":["...","3.0"]}` | Clean two-step confirmation; then `GET /recipe/user/id?userId=X` to test auth posture | — |
