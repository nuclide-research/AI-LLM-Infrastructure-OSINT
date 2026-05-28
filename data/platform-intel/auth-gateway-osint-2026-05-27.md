# Auth / API Gateway Platform OSINT — Pre-Survey Intelligence
**Date:** 2026-05-27
**Purpose:** Tune dork queries, understand auth posture, identify verification probes, document data exposure classes before Shodan harvests.
**Scope:** 13 platforms — API gateways, identity providers, policy engines, SSO infrastructure. Note: LiteLLM proxy (cat-01) and Portkey self-hosted (cost survey) already covered.
**Status:** Pre-survey. No active probing conducted.

**Threat model:** These platforms sit in front of AI stacks. An exposed admin interface bypasses the auth layer protecting the entire downstream AI/LLM infrastructure. Kong, Tyk, and Casdoor ship with default credentials or no admin auth by default. OPA exposes all policy data (which leaks infra topology) unauthenticated by default. Keycloak, Kratos, and Hydra admin ports are explicitly documented as "must not be internet-facing" — they are.

---

## Kong Gateway

**Category:** API Gateway
**Default Ports:** 8000 (proxy HTTP), 8001 (admin API), 8443 (proxy HTTPS), 8444 (admin HTTPS), 8002 (Kong Manager UI), 8003/8004 (Dev Portal)
**Auth Default (Admin):** off — admin API binds `127.0.0.1:8001` by default, but Kong Manager starts with no authentication when `admin_listen` is widened to `0.0.0.0`
**Auth Default (Proxy):** on (configurable per route/plugin)
**Shodan Dork (primary):** `port:8001 "via: kong" http.status:200`
**Shodan Dork (secondary):** `http.html:"Kong" port:8002 http.title:"Kong Manager"`
**Shodan Dork (tertiary):** `http.headers.via:"kong" port:8001`
**Verification Probe:** `GET /` on port 8001 → 200 + JSON with `version`, `hostname`, `tagline:"Welcome to kong"` fields
**Data Exposure Class:** Full gateway config in plaintext — all routes, services, plugins (including auth plugin configs, API keys, JWT secrets), upstream addresses, consumer credentials; write access enables adding routes or stripping auth plugins
**Known CVEs:** No admin-specific auth bypass CVEs, but the misconfiguration is well-documented (Trend Micro, Invicti, Packet Storm papers); Shodan indexation of exposed instances has risen sharply since late 2021
**Default Credentials:** none (no auth mechanism active by default on admin API — relies on network isolation)
**Notes:** Kong adds `Via: kong/<version>` and `X-Kong-Proxy-Latency` headers to proxied responses — these fingerprint the proxy port (8000), not admin. Admin port 8001 responds with JSON at `/`. Kong Manager (8002) requires `admin_gui_auth` setting to enable auth — ships disabled. Avoid `http.title:"Kong"` — high FP rate from unrelated services.

---

## Tyk Gateway

**Category:** API Gateway
**Default Ports:** 8080 (proxy + control API, shared by default), 3000 (Tyk Dashboard), 8081 (control port if separated)
**Auth Default (Admin):** default-creds — gateway API secret defaults to `352d20ee67be67f6340b4c0605b044b7` (documented in `tyk.conf.example`); Dashboard admin uses `admin-auth` header with a separate configurable secret; community notes flag that the control port is public (same as proxy) by default
**Auth Default (Proxy):** on (per-API policy)
**Shodan Dork (primary):** `port:8080 "x-tyk-gateway" http.status:200`
**Shodan Dork (secondary):** `port:3000 http.title:"Tyk Dashboard" http.status:200`
**Shodan Dork (tertiary):** `port:8080 "tyk_listener_port" http.html:"tyk"`
**Verification Probe:** `GET /tyk/reload/` with header `X-Tyk-Authorization: 352d20ee67be67f6340b4c0605b044b7` → 200 + `{"status":"ok"}` on instances not rotating the default secret
**Data Exposure Class:** API definitions, upstream auth credentials, rate limit configs, organization and key data via Dashboard; default-secret instances expose full gateway control
**Known CVEs:** No recent admin auth bypass CVEs, but default secret is publicly documented and widely unrotated in self-hosted deployments
**Default Credentials:** gateway secret `352d20ee67be67f6340b4c0605b044b7` (must be changed); Dashboard admin-auth header value is installation-specific but defaults to a known value in quickstart configs
**Notes:** Tyk Dashboard on port 3000 has a separate `admin_secret` for the super-admin API at `/admin/*` endpoints. The `x-tyk-gateway` response header appears on the proxy port. Do not confuse Tyk OSS (single-node, port 8080 only) with Tyk Pro (adds Dashboard on 3000). FP risk from other services on 3000.

---

## OPA (Open Policy Agent)

**Category:** Policy Engine
**Default Ports:** 8181 (REST API — all functions on single port)
**Auth Default (Admin):** off — docs state explicitly: "By default, OPA does not perform authentication or authorization and these flags default to `off`"
**Auth Default (Proxy/Data):** N/A (not a proxy; it is the policy decision point)
**Shodan Dork (primary):** `port:8181 "result" http.status:200 "v1/data"`
**Shodan Dork (secondary):** `port:8181 "/v1/policies" http.html:"policies"`
**Shodan Dork (tertiary):** `http.html:"Open Policy Agent" port:8181`
**Verification Probe:** `GET /v1/policies` → 200 + JSON array of all loaded Rego policies; `GET /v1/data` → 200 + full data document
**Data Exposure Class:** All Rego policy source code (leaks full infra access control logic, service names, endpoints, roles), full data document (can include service mesh config, Kubernetes RBAC mappings, API topology), policy decision audit logs; Trend Micro research found 389 unauthenticated OPA servers revealing sensitive infra topology
**Known CVEs:** CVE from Tenable (2025) — attacker tricks CLI/SDK into loading bundle over remote share → NTLM credential exposure; `--authentication=token` and `--authorization=basic` must be explicitly enabled
**Default Credentials:** none (no auth mechanism active)
**Notes:** OPA binds `localhost:8181` by default in bare deployments, but Kubernetes sidecars and Helm charts frequently bind `0.0.0.0:8181`. The `/v1/data` endpoint returns the full merged data document, which often contains secrets injected via bundle. The `/health` endpoint at `GET /health` does not require auth even when auth is enabled — useful as a non-destructive verification probe. FP risk low on port 8181.

---

## OPAL (Open Policy Administration Layer)

**Category:** Policy Administration / OPA Companion
**Default Ports:** 7002 (OPAL server — client subscription websocket + REST), 7766 (OPAL client default), 8181 (downstream OPA instance)
**Auth Default (Admin):** off in demo/development mode — OPAL server token authentication is optional and disabled in quickstart configs; production mode requires RSA key pairs
**Auth Default (Proxy/Data):** N/A
**Shodan Dork (primary):** `port:7002 "opal" http.status:200`
**Shodan Dork (secondary):** `port:7002 "topics" "opal_updates"`
**Verification Probe:** `GET /` or `GET /healthcheck` on port 7002 → 200 + OPAL server info JSON
**Data Exposure Class:** Policy update streams (all policy and data changes), OPA data document updates in real-time, webhook configurations for policy sources (GitHub tokens, S3 bucket URLs); OPAL server REST API exposes data source definitions
**Known CVEs:** No published CVEs; exposure class is architectural — unauthenticated OPAL server leaks policy management credentials and update feeds
**Default Credentials:** none; token auth requires explicit `OPAL_AUTH_PRIVATE_KEY` configuration
**Notes:** OPAL is deployed by Permit.io as their managed layer; self-hosted instances frequently omit token auth. Port 7002 is not a widely-used port for other services — low FP risk. The websocket path `/ws` on port 7002 is used by OPAL clients for live policy updates.

---

## Authentik

**Category:** SSO / Identity Provider
**Default Ports:** 9000 (HTTP), 9443 (HTTPS), 9300 (metrics)
**Auth Default (Admin):** on — login required; however, `/api/v3/` is partially accessible before login for schema/version discovery
**Auth Default (Proxy):** on (forward auth model — Authentik is the auth layer)
**Shodan Dork (primary):** `port:9000 http.title:"authentik" http.status:200`
**Shodan Dork (secondary):** `port:9000 "/api/v3/" "authentik"`
**Shodan Dork (tertiary):** `http.html:"goauthentik.io" port:9000`
**Verification Probe:** `GET /api/v3/root/config/` → 200 + JSON with `error_reporting` field (unauthenticated); `GET /if/flow/default-authentication-flow/` → 200 + flow config
**Data Exposure Class:** When admin credentials compromised — full user database, all OAuth2 client secrets, LDAP/SAML connector configs, session tokens; `/api/v3/` schema endpoint leaks version string unauthenticated
**Known CVEs:** CVE-2024-47070 (CVSS high) — X-Forwarded-For header manipulation bypasses password stage when no reverse proxy overwrites headers (affected < 2024.6.5, < 2024.8.3); CVE-2024-37905 — token user ID manipulation escalates to higher-privilege user; CVE-2026-25748 — Proxy Provider forward auth bypass via malformed cookie with Traefik/Caddy (fixed in 2025.10.4, 2025.12.4); CVE-2025-29928 — session deletion does not revoke session tokens when using database session storage
**Default Credentials:** none shipped; initial admin user created on first boot via `/if/flow/initial-setup/` — instances not completing setup may have open setup flows
**Notes:** The initial setup flow `/if/flow/initial-setup/` is a high-value probe — if accessible post-deployment, admin account creation is open. Authentik binds all interfaces on 9000 by default. `/api/v3/schema/` exposes OpenAPI schema including all endpoint paths unauthenticated. CVE-2024-47070 is particularly dangerous for direct-internet-facing deployments.

---

## Authelia

**Category:** 2FA / Forward Auth Proxy
**Default Ports:** 9091 (HTTP), exposed on all interfaces (0.0.0.0) by default
**Auth Default (Admin):** on — no admin API exists separately; management is via config file only
**Auth Default (Proxy):** on (that is its purpose)
**Shodan Dork (primary):** `port:9091 http.title:"Authelia" http.status:200`
**Shodan Dork (secondary):** `port:9091 "/api/health" "authelia"`
**Verification Probe:** `GET /api/health` → 200 + `{"status":"OK"}` (no auth required); `GET /` → Authelia login page
**Data Exposure Class:** Login page, health status (unauthenticated); no admin API — config file exposure requires filesystem access; Authelia itself is not a data store, but access to the login interface enables brute-force or session attacks against all downstream services it protects
**Known CVEs:** No critical admin bypass CVEs in recent versions; the exposure class is that Authelia's login page being public means an attacker knows which services are protected (endpoint enumeration via forward auth headers)
**Default Credentials:** none (first user created via config)
**Notes:** Authelia is a forward auth companion, not an IdP admin panel — the risk is availability/brute force against the 2FA portal, not an admin API. Port 9091 on internet-facing hosts is often intentional (the login page must be reachable). The Dockerfile hardcodes EXPOSE 9091. More useful as a signal that an AI stack is using Authelia for auth — inventory target, not direct exploit surface.

---

## Keycloak

**Category:** Identity Provider / SSO
**Default Ports:** 8080 (HTTP), 8443 (HTTPS), 9990 (legacy WildFly management, deprecated in Quarkus distro)
**Auth Default (Admin):** on — admin console requires credentials; BUT no admin user exists on first boot until `KC_BOOTSTRAP_ADMIN_USERNAME` / `KC_BOOTSTRAP_ADMIN_PASSWORD` env vars are set or bootstrap credentials entered via localhost; `/auth/realms/master` and `/.well-known/openid-configuration` are unauthenticated per OIDC spec
**Auth Default (Proxy):** on (Keycloak is the IdP)
**Shodan Dork (primary):** `port:8080 http.title:"Keycloak" http.status:200`
**Shodan Dork (secondary):** `port:8080 "/auth/realms/master" "public_key"`
**Shodan Dork (tertiary):** `http.html:"Keycloak" http.html:"realm" port:8080`
**Verification Probe:** `GET /auth/realms/master` (v18 and earlier) or `GET /realms/master` (v19+) → 200 + JSON with `realm`, `public_key`, `token-service` fields (unauthenticated per OIDC spec)
**Data Exposure Class:** `/realms/master` leaks realm public key and OIDC endpoint URLs (info disclosure, no auth required by spec); admin console breach exposes all users, groups, roles, OAuth2 client secrets for all realms, LDAP bind credentials, SAML signing keys, session tokens; recent CVE exposes client secret via unauthenticated `/admin/{realmId}/console/config` endpoint when admin console client is configured as confidential
**Known CVEs:** CVE-2024-3656 (CVSS high) — low-privilege authenticated users can call admin REST API endpoints (`testLDAPConnection`, `getUnmanagedAttributes`, `getProviders`) without admin privileges (affects < 24.0.5); CVE-2024-8698 — SAML signature validation bypass, all versions ≤ 25.0.5; CVE-2025-7365 — account merge during IdP login allows email modification to match victim; CVE-2025-13881 — limited-privilege admin accesses custom user attributes via `/unmanagedAttributes`; CVE-2026-4633 — user enumeration; unauthenticated `/admin/{realmId}/console/config` client secret leak (open GitHub issue, no CVE assigned yet)
**Default Credentials:** none on fresh install (bootstrap user created via env vars or first-run localhost access only)
**Notes:** Keycloak's OIDC discovery endpoints (`/realms/{realm}/.well-known/openid-configuration`) are intentionally unauthenticated — do not flag these as vulnerabilities. The actionable finding is admin console exposure + CVE chain. The `/auth/` path prefix was dropped in Keycloak v17+ (Quarkus distro) — dorks should cover both path variants. High population on Shodan via `http.title:"Keycloak"`.

---

## Zitadel

**Category:** Identity Provider / IAM
**Default Ports:** 8080 (single port — gRPC + HTTP + management console, multiplexed)
**Auth Default (Admin):** on — System API requires service account JWT or PAT; Management API requires OAuth token; but `/.well-known/openid-configuration` is unauthenticated; console UI (`/ui/console`) login required
**Auth Default (Proxy):** on
**Shodan Dork (primary):** `port:8080 "/ui/console" http.title:"ZITADEL" http.status:200`
**Shodan Dork (secondary):** `port:8080 "zitadel.system.v1.SystemService" http.status:200`
**Shodan Dork (tertiary):** `http.html:"ZITADEL" port:8080 http.html:"Login"`
**Verification Probe:** `GET /.well-known/openid-configuration` → 200 + JSON with `issuer` containing "zitadel" in the hostname; `GET /ui/console` → Zitadel login page with `ZITADEL` title
**Data Exposure Class:** OIDC discovery metadata (unauthenticated); admin breach exposes all organizations, users, roles, OAuth2 clients, service accounts, and their secrets; System API (superordinate) controls all instances
**Known CVEs:** No critical admin bypass CVEs in public databases as of 2026-05-27; architecture is single-port, meaning admin APIs share the same listener as public OIDC endpoints — misconfigured reverse proxy rules can inadvertently expose admin gRPC paths
**Default Credentials:** Initial admin credentials set via `FirstInstance.Org.Human` config block or Helm values; quickstart/Docker configs often ship with `InitialAdminEmail`/`InitialAdminPassword` in plaintext in `docker-compose.yaml`
**Notes:** Zitadel is a newer IdP with growing self-hosted adoption in AI infrastructure. The single-port design (8080 for everything) means Shodan dorks on the proxy port will also catch admin interfaces. `http.title:"ZITADEL"` is a clean primary signal. System API path prefix is `/zitadel.system.v1.SystemService/` — gRPC over HTTP/2, not REST.

---

## Ory Kratos

**Category:** Identity Server (headless)
**Default Ports:** 4433 (public API — user-facing flows), 4434 (admin API — internal only by design)
**Auth Default (Admin):** off — admin API on port 4434 ships with no authentication; Ory documentation explicitly states admin port "must not be available to public" and must be deployed behind a VPN/firewall
**Auth Default (Proxy):** on (public API requires session cookies/tokens)
**Shodan Dork (primary):** `port:4434 "identities" http.status:200`
**Shodan Dork (secondary):** `port:4434 "/admin/identities" http.html:"identities"`
**Shodan Dork (tertiary):** `port:4433 "csrf_token" "flow"` (public API, lower risk)
**Verification Probe:** `GET /admin/identities` on port 4434 → 200 + JSON array of user identities (no auth required if exposed)
**Data Exposure Class:** Full user identity database (emails, usernames, profile data, credential metadata), session data, recovery/verification flows, identity schema definitions; write access enables creating admin users, deleting identities, invalidating sessions
**Known CVEs:** CVE-2026-33503 (High) — SQL injection via forged pagination tokens in `ListCourierMessages` admin API (requires knowledge of pagination secret); Ory Oathkeeper CVE-2026-33494 (Critical) — path traversal bypasses authentication rules via un-normalized paths
**Default Credentials:** none (no auth on admin port — network isolation is the entire security model)
**Notes:** Ory Kratos admin port (4434) is the highest-risk Ory component — zero auth by design. Port 4434 has very low noise (not a common port for other services). Any HTTP 200 on port 4434 returning `identities` JSON is a confirmed finding. Oathkeeper (Ory's auth proxy, port 4455) CVE-2026-33494 is relevant when Kratos is deployed behind an Oathkeeper instance — path traversal bypasses the proxy protecting Kratos.

---

## Ory Hydra

**Category:** OAuth2 / OIDC Server
**Default Ports:** 4444 (public OAuth2/OIDC endpoints), 4445 (admin API — internal only by design)
**Auth Default (Admin):** off — admin API on port 4445 ships with no authentication; Ory docs: "Port 4445 is for Hydra Admin and must not be available to public"
**Auth Default (Proxy):** on (OAuth2 flows require client credentials)
**Shodan Dork (primary):** `port:4445 "clients" http.status:200`
**Shodan Dork (secondary):** `port:4445 "/admin/clients" http.html:"client_id"`
**Shodan Dork (tertiary):** `port:4444 "/.well-known/openid-configuration" "hydra"`
**Verification Probe:** `GET /admin/clients` on port 4445 → 200 + JSON array of all OAuth2 clients (no auth required if exposed); `GET /health/ready` → `{"status":"ok"}`
**Data Exposure Class:** All OAuth2 client IDs and secrets, consent/login request data, JWT grant issuers, token introspection results, trusted key sets; write access enables creating OAuth2 clients with arbitrary redirect URIs (OAuth2 client injection)
**Known CVEs:** CVE-2026-33504 (High) — SQL injection in `listOAuth2Clients`, `listOAuth2ConsentSessions`, `listTrustedOAuth2JwtGrantIssuers` admin APIs via forged pagination tokens; no auth bypass CVEs (auth is simply absent by design on admin port)
**Default Credentials:** none (no auth mechanism on admin port — architecture relies entirely on network-level isolation)
**Notes:** Hydra's admin API (4445) manages OAuth2 consent flows — an exposed admin port allows an attacker to approve/reject login requests and inject OAuth2 clients, effectively owning SSO for any service using Hydra as its OAuth2 provider. Port 4445 has low ambient traffic on Shodan. Combine with port 4444 OIDC discovery to confirm Hydra deployment before probing admin port.

---

## Casdoor

**Category:** IAM / SSO (AI-native, MCP gateway)
**Default Ports:** 8000 (HTTP — single port for web UI, API, and admin)
**Auth Default (Admin):** default-creds — fresh installs ship with `built-in/admin` / `123`; documented in official docs and pentest-tools.com vulnerability database; login at `http://localhost:8000` with these credentials on first boot
**Auth Default (Proxy):** on (Casdoor is the auth layer)
**Shodan Dork (primary):** `port:8000 "Casdoor" http.title:"Casdoor" http.status:200`
**Shodan Dork (secondary):** `port:8000 "/api/get-app-list" http.status:200`
**Shodan Dork (tertiary):** `http.html:"casdoor" port:8000 http.html:"built-in"`
**Verification Probe:** `GET /api/get-app-list` → 200 + JSON array of configured applications (unauthenticated on some versions); `GET /` → HTML with `<title>Casdoor</title>` and Casdoor branding
**Data Exposure Class:** All IAM data — users, organizations, OAuth2 applications, LDAP configs, SAML providers, MCP server configs (Casdoor markets itself as an "Agent-first IAM / LLM MCP gateway"); full admin access via default creds enables creating users/tokens for any connected application
**Known CVEs:** CVE-2022-24124 (CVSS 7.5) — SQL injection in versions < 1.13.1; CVE-2023-34927 / exploit-db 51961 — CSRF on `/api/set-password` in v1.331.0 and below; CVE-2024-41657 — CORS misconfiguration (beego `CorsFilter` prefix-match logic error) allows any origin to make authenticated cross-domain requests (≤ 1.577.0); CVE-2024-41658 — related CORS issue
**Default Credentials:** `built-in/admin` : `123` (documented default; pentest-tools.com entry confirms active exploitation)
**Notes:** Casdoor positions itself as an "AI-native" IAM with MCP server support — it is increasingly deployed in front of AI agent stacks. Port 8000 conflicts with many other services (high FP risk); use `http.title:"Casdoor"` conjunction. The CORS CVE-2024-41657 is particularly dangerous in AI deployments where browser-based LLM frontends are on different origins — any page can make authenticated API calls to an exposed Casdoor instance.

---

## SuperTokens

**Category:** Authentication Backend (self-hosted core)
**Default Ports:** 3567 (HTTP — single port for all core API endpoints)
**Auth Default (Admin):** off by default (no API key configured) — docs note "No API key exists by default"; when no `api_keys` config entry exists, the core accepts requests from any source; `/hello` health endpoint always returns 200 with no auth
**Auth Default (Proxy):** on (API key must be added manually in `config.yaml`)
**Shodan Dork (primary):** `port:3567 "Hello" http.status:200`
**Shodan Dork (secondary):** `port:3567 "/apiversion" http.status:200`
**Shodan Dork (tertiary):** `port:3567 http.html:"SuperTokens"` (lower precision — may not appear in body)
**Verification Probe:** `GET /hello` on port 3567 → 200 + `"Hello"` (confirms running, no auth); `GET /apiversion` → 200 + JSON with `versions` array (confirms SuperTokens, no auth required)
**Data Exposure Class:** When no API key configured — full user session database, user identity records, email/password hashes, MFA state, JWT signing keys, refresh tokens, all recipe state (passwordless codes, email verification tokens); `/recipe/user/id` endpoint returns full user records without auth if API key absent
**Known CVEs:** No published CVEs as of 2026-05-27; the exposure class is architectural — missing API key config is not a CVE, it is a deployment misconfiguration
**Default Credentials:** none (API key mechanism, not username/password)
**Notes:** SuperTokens `/hello` returns exactly the string "Hello" with a 200 — this is a clean, low-FP health probe. Port 3567 has low ambient traffic. The `/apiversion` endpoint returns the supported CDI (Core Driver Interface) version array — unique to SuperTokens. SuperTokens is increasingly used as the auth backend for AI SaaS platforms (LangChain ecosystem, custom LLM apps). No API key = full read/write on the identity store.

---

## Notes on Already-Covered Platforms

**LiteLLM proxy** — surveyed in Category 01 (LLM Orchestration). Admin port 4000, no auth by default, exposes all model configs and API keys. See `01-llm-orchestration.md`.

**Portkey self-hosted** — covered in cost/usage monitoring survey. LLM gateway with admin dashboard. See relevant cost survey file.
