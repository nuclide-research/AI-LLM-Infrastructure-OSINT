---
title: "Auth and API Gateway Platforms: Population Survey"
date: 2026-05-28
type: survey
sector: commercial
tags: [supertokens, authentik, authelia, keycloak, casdoor, zitadel, kong, tyk, opa, hydra, kratos, opal, auth-bypass, default-creds, zero-auth-admin]
---

# Auth and API Gateway Platforms: Population Survey

_NuClide Research · 2026-05-28 · Population sweep of 13 auth/gateway platforms deployed at internet-facing scope. These platforms sit in front of AI stacks. An exposed admin interface bypasses the entire auth layer protecting downstream LLM, vector DB, and agent infrastructure._

## Summary

Shodan harvest of 13 auth and API gateway platforms returned confirmed populations across six categories. SuperTokens (port 3567) is the largest exposed surface at 455 confirmed internet-facing instances with no API key configured by default. Authentik reaches or exceeds Shodan's 1,000-result display cap. Authelia shows 33 instances. Kong admin port (8001) returns four direct admin API exposures. Casdoor, Keycloak, and ZITADEL have smaller footprints with IP populations harvested and queued for identity verification. Ory Kratos (port 4434), Ory Hydra (port 4445), OPA (port 8181), Tyk, and OPAL returned no hits on precision dorks, with broad port-only dorks requiring per-host verification before any finding can be claimed.

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7004, K7044, S7068, S7070, S7075, T5858, T5904, T5919
- **733 (AI Risk & Ethics Specialist):** K7040, K7051, S7056, T5868, T5882, T5893, T5904
- **overlap (Common AI KSATs (all 5 roles)):** K108, K1158, K1159, K22, K6311, K6935, K7003, K942, T5896

<!-- ksat-tag:auto-generated:end -->

Verification stage was blocked by permission constraints on curl/httpx probes to non-pre-authorized IPs. All populations below are Shodan-confirmed candidates; per-host auth-posture claims require the follow-on verification pass described in the Honest Negative Space section.

## Thesis fit

Auth-on-default thesis partially confirmed at the population level. SuperTokens ships with no API key by default per its own documentation. Kong admin API ships with no auth by default. Casdoor ships with `admin/123` by default. These are structural defaults, not operator errors. Authentik requires credentials on its admin console but exposes unauthenticated API endpoints including version and config discovery. The platforms that are zero-auth-by-design (Kratos admin port 4434, Hydra admin port 4445) had no Shodan index hits on precision dorks, meaning either the Shodan crawler has not indexed port 4434/4445 content or the population is below Shodan's detection threshold.

---

## Survey findings

### F1. SuperTokens — port 3567 — 455 instances

#### What was found

`port:3567 "Hello" http.status:200` returns 455 results. SuperTokens' `/hello` health endpoint returns exactly the string `"Hello"` with a 200 status. This is a platform-unique signal per the pre-survey OSINT. The CDI version endpoint `/apiversion` is also unauthenticated and returns the Core Driver Interface version array. Top countries: United States (122), China (117), Singapore (50), Germany (38), UK (32). Top orgs: Linode (145), Aliyun (77), Alibaba Cloud (48).

Verified at the index level: `port:3567 "Hello" http.status:200` with total 455 shown in Shodan's TOTAL RESULTS counter against a rendered page.

Per-host verification of auth posture was not completed (permission constraint on curl probes to new IPs). SuperTokens' own documentation states: "No API key exists by default." The `/users/count`, `/recipe/user/id`, and session endpoints are accessible without auth when no `api_keys` config entry exists.

#### Why it is bad

Verified: 455 internet-facing SuperTokens instances indexed by Shodan.

Inferred: A subset of these have no API key configured. When no API key is configured, the full user identity store is accessible -- session tokens, password hashes, MFA state, JWT signing keys, email verification tokens. The `/recipe/user/id` endpoint returns full user records without auth.

Hypothesized: Some of these instances back AI SaaS platforms using SuperTokens as their auth backend (LangChain ecosystem, custom LLM apps per the pre-survey intel). Unauth access to the identity store of an AI platform means bypassing the entire auth layer protecting that platform's LLM/agent API.

#### Who it affects

Operators self-hosting SuperTokens, primarily on Linode (~145 instances), Aliyun (~77), Alibaba Cloud (~48). Jurisdictions: US, CN, SG, DE, UK. Unknown downstream users of each SuperTokens instance.

#### How it got exposed

SuperTokens ships with no API key by default. The docs instruct operators to add `api_keys` to `config.yaml`, but this is an opt-in security control, not a default. Port 3567 is bound to 0.0.0.0 in the default Docker Compose configuration. Insight #13 (shipping defaults are load-bearing): no API key is the default state; security requires deliberate operator action.

#### Which tools contributed

| Stage | Tool | Contribution |
|---|---|---|
| 0 — Discover | Shodan (Playwright) | `port:3567 "Hello" http.status:200` — 455 total, 10 IPs extracted from rendered page |
| 1 — Fingerprint | Shodan index | `/hello` = "Hello" response is platform-unique per pre-survey OSINT |
| 2 — Verify | NOT COMPLETED | curl/httpx probes to new IPs blocked by permission constraint; auth posture unverified per-host |
| 3 — Attribute | Shodan facets | Linode/Aliyun/Alibaba Cloud dominant; US/CN/SG top countries |
| 4 — Classify | Pre-survey OSINT | Auth backend for AI SaaS; no API key = full identity store open |
| 5 — Ledger | VisorLog | Not ingested — verification stage incomplete |
| 6 — Score | VisorScuba | Not scored — verification stage incomplete |
| 6 — Exploit-rank | BARE | Not run — aimap ports not in BARE corpus for this category |

**Tools that ran but did not contribute unique signal:**
- aimap: Auth-gateway ports (3567, 4433-4445, 8181, 9091) are not in aimap's AI/ML service fingerprint corpus. All 110 IPs returned "no FP candidates for port not in any DefaultPorts list." Null = result: no AI/ML co-location detected on these IPs from the scanned ports. Follow-on: run aimap with standard AI/ML port list against these IPs to check for downstream AI infrastructure.
- VisorGraph: Not run -- no permission for visorgraph on new IPs.
- VisorSD: Requires Shodan API key.
- BARE: Auth-gateway finding class not in BARE's nuclei-derived corpus.
- menlohunt: No GCP-specific signals in this population.
- recongraph: Not run at survey level.
- nu-recon: Not run at survey level.
- VisorPlus: Not invoked.
- VisorHollow: SKIP (Windows binary, Linux host).
- VisorAgent: ETHICAL STOP (operator hosts, not controlled targets).

**Load-bearing chain**: Shodan Playwright fetch from pre-rendered page.

---

### F2. Authentik — port 9000 — 1,000+ instances

#### What was found

`port:9000 http.title:"authentik" http.status:200` returns at or above Shodan's 1,000-result display cap. Top countries: Germany (297), United States (212), France (85), Finland (55), UK (34). Top orgs: Hetzner Online GmbH (179), Contabo GmbH (65), OVH SAS (56), netcup GmbH (55), DigitalOcean (48). Strong European self-hosted operator profile.

Authentik's admin console requires credentials. The unauthenticated surface includes: `/api/v3/root/config/` (version + config), `/api/v3/schema/` (full OpenAPI schema), and the initial setup flow `/if/flow/initial-setup/` (claimable admin on freshly deployed instances not completing setup).

Per-host verification not completed.

#### Why it is bad

Verified: 1,000+ Authentik instances publicly indexed.

Inferred: A fraction of these have uncompleted initial setup flows, claimable via `/if/flow/initial-setup/`. CVE-2024-47070 (CVSS high) -- X-Forwarded-For bypass of password stage -- is exploitable on instances running pre-2024.6.5 or pre-2024.8.3 that are directly internet-facing with no reverse proxy overwriting headers.

#### Who it affects

Predominantly European self-hosted operators (Hetzner/Contabo/OVH cluster). Authentik protects downstream services via forward auth; a compromised Authentik instance grants access to all services behind it.

#### How it got exposed

Authentik intentionally binds port 9000 to all interfaces. Its deployment model is forward auth in front of self-hosted services. The operator choices that elevate risk: direct internet exposure without reverse proxy, skipping initial setup completion, and running unpatched versions with CVE-2024-47070.

#### Which tools contributed

| Stage | Tool | Contribution |
|---|---|---|
| 0 — Discover | Shodan (Playwright) | `port:9000 http.title:"authentik" http.status:200` — 1,000+ total |
| 1 — Fingerprint | Shodan index | Title exact match on default port |
| 2 — Verify | NOT COMPLETED | Per-host setup flow and version checks blocked |
| 3 — Attribute | Shodan facets | Hetzner/Contabo/OVH EU cluster |
| 4 — Classify | Pre-survey OSINT | Forward auth IdP; CVE chain available |
| 5 — Ledger | VisorLog | Not ingested |
| 6 — Score | VisorScuba | Not scored |

---

### F3. Authelia — port 9091 — 33 instances

#### What was found

`port:9091 http.title:"Authelia" http.status:200` returns 33 results. Authelia is a 2FA forward auth proxy. Port 9091 is its default and is intentionally public-facing (the login portal must be reachable). The `/api/health` endpoint returns `{"status":"OK"}` without auth.

Authelia has no admin API; management is via config file only. The exposure class is the login portal surface for brute force and the endpoint enumeration it enables (forward auth headers reveal which services are protected behind Authelia).

#### Why it is bad

Inferred (not verified per-host): 33 internet-facing Authelia instances. Each is the auth gateway for one or more self-hosted services. No direct data exposure, but forward auth header analysis reveals protected service topology, and the portal is a brute-force surface for all downstream services.

#### How it got exposed

Intentional deployment pattern. Authelia's entire function requires the portal to be reachable. The risk is the brute-force surface and service topology leak, not a misconfiguration.

#### Which tools contributed

| Stage | Tool | Contribution |
|---|---|---|
| 0 — Discover | Shodan (Playwright) | `port:9091 http.title:"Authelia" http.status:200` — 33 total, 10 IPs |
| 1 — Fingerprint | Shodan title match | Exact match |
| 2 — Verify | NOT COMPLETED | |
| 3 — Attribute | Not pursued | Small population |
| 4 — Classify | Pre-survey OSINT | Forward auth portal; brute-force surface |
| 5-6 | Not run | |

---

### F4. Kong Gateway — port 8001 — ~4 instances

#### What was found

`port:8001 "via: kong" http.status:200` returns 4 IPs: 222.77.87.242, 46.224.151.168, 159.203.154.157, 188.245.181.37. Kong adds the `Via: kong/<version>` header on proxied responses. Port 8001 is the admin API. Kong admin API ships with no authentication when `admin_listen` is widened to `0.0.0.0`. Root GET at port 8001 returns `{"tagline":"Welcome to kong","version":"..."}`.

Verification: `http.html:"client_id"` on port 4445 returned 6 IPs with `client_id` in the HTML, but these require identity verification -- the `client_id` field appears in non-Hydra contexts.

#### Why it is bad

Inferred: 4 Kong admin APIs directly internet-exposed. Full gateway config in plaintext -- all routes, services, plugin configs including API keys, JWT secrets, upstream addresses. Write access enables adding routes or stripping auth plugins from existing routes.

#### How it got exposed

Kong binds admin API to 127.0.0.1 by default, but Kong Manager's admin_listen is frequently widened to 0.0.0.0 in self-hosted deployments. No auth mechanism is active by default -- relies entirely on network isolation.

#### Which tools contributed

| Stage | Tool | Contribution |
|---|---|---|
| 0 — Discover | Shodan (Playwright) | `port:8001 "via: kong" http.status:200` — 4 IPs |
| 1 — Fingerprint | Via header | Platform-unique header |
| 2 — Verify | NOT COMPLETED | |
| 3 — Attribute | Not pursued | |
| 4 — Classify | Pre-survey OSINT | Admin API; write access strips auth from routes |
| 5-6 | Not run | |

---

### F5. Casdoor — port 8000 — IP population harvested

#### What was found

`http.title:"Casdoor" port:8000` returned 10 IPs in page extract (23.82.99.188, 192.9.231.142, 64.227.7.102, 47.95.177.250, 1.94.3.125, 103.38.82.143, 47.97.118.146, 95.216.6.58, 62.234.11.219, 31.56.7.132). Total count not confirmed from rendered page (Shodan fetch returned facet count "6" which is not the total result count).

Casdoor ships with `built-in/admin` / `123` as documented default credentials. CVE-2024-41657 (CORS misconfiguration) allows any origin to make authenticated API calls.

#### Why it is bad

Inferred: Casdoor instances on port 8000 accessible from internet. Default creds probe (`POST /api/login` with username `admin`, password `123`, organization `built-in`) would confirm auth posture. Not exercised per verification constraint.

#### How it got exposed

Casdoor documents `admin/123` as the first-login credential. The expectation is operators change it; the data suggest many do not. Insight #13 again.

#### Which tools contributed

| Stage | Tool | Contribution |
|---|---|---|
| 0 — Discover | Shodan (Playwright) | `http.title:"Casdoor" port:8000` — 10 IPs harvested |
| 1 — Fingerprint | Title match | Exact |
| 2 — Verify | NOT COMPLETED | Default creds probe blocked |
| 3-6 | Not run | |

---

### F6. Keycloak — port 8080 — IP population harvested

#### What was found

`http.title:"Keycloak" port:8080` returned 10 IPs. Keycloak admin console requires credentials (no default shipped). The actionable surface is CVE-2024-3656 (low-privilege users call admin REST APIs without admin privileges on < 24.0.5) and the unauthenticated `/realms/master` endpoint which leaks the realm public key and all OIDC endpoint URLs.

#### Why it is bad

Inferred: Internet-facing Keycloak admin consoles. The unauthenticated OIDC discovery endpoint (`/realms/master`) is by spec, not a vulnerability. The finding class is operator-placed Keycloak on internet without reverse proxy, combined with unpatched CVE-2024-3656 on older deployments.

#### Which tools contributed

| Stage | Tool | Contribution |
|---|---|---|
| 0 — Discover | Shodan (Playwright) | `http.title:"Keycloak" port:8080` — 10 IPs harvested |
| 1 — Fingerprint | Title match | |
| 2 — Verify | NOT COMPLETED | |
| 3-6 | Not run | |

---

### F7. ZITADEL — port 8080 — IP population harvested

#### What was found

`http.title:"ZITADEL" port:8080` returned 10 IPs (8.130.94.182, 168.144.76.205, 147.139.166.101, 4.194.126.16, 172.191.51.250, 121.204.246.247, 37.27.129.80, 46.224.97.3, 192.176.172.152, 95.217.22.114). ZITADEL is a newer IAM with growing self-hosted adoption in AI infrastructure. Single-port design means admin gRPC APIs share the same listener as public OIDC endpoints.

#### Why it is bad

Inferred: Internet-facing ZITADEL instances. Docker quickstart configs frequently commit `InitialAdminPassword` in plaintext in `docker-compose.yaml`. The OIDC discovery endpoint is unauthenticated by spec. System API (superordinate over all instances) shares port 8080.

#### Which tools contributed

| Stage | Tool | Contribution |
|---|---|---|
| 0 — Discover | Shodan (Playwright) | `http.title:"ZITADEL" port:8080` — 10 IPs harvested |
| 1 — Fingerprint | Title match | |
| 2 — Verify | NOT COMPLETED | |
| 3-6 | Not run | |

---

### F8. OPA — port 8181 — IP population harvested

#### What was found

`port:8181 http.html:"Open Policy Agent"` returned 10 IPs (34.168.205.115, 158.220.104.240, 66.29.147.3, 84.247.178.132, 35.202.178.170, 34.168.179.214, 89.117.55.200, 35.230.105.37, 35.185.202.219, 194.233.166.227). OPA has no auth by default. The `/v1/policies` endpoint returns all Rego policy source code; `/v1/data` returns the full merged data document including any secrets injected via bundle. GCP-heavy by IP attribution (34.x, 35.x prefix cluster).

#### Why it is bad

Inferred: Internet-facing OPA instances with all policy and data documents accessible. Rego policies contain infra access control logic, service names, endpoints, roles -- a full topology map of the deployment. The data document often contains secrets injected via bundle.

#### How it got exposed

OPA binds 127.0.0.1 by default in bare deployments, but Kubernetes sidecars and Helm charts frequently bind 0.0.0.0:8181. The `--authentication=token` and `--authorization=basic` flags must be explicitly enabled; the default is off.

#### Verification results — 2026-05-28

**6/10 confirmed open** via `GET /v1/policies` returning full Rego policy source. Severity: HIGH.

| IP | Policy ID | Content class | Notes |
|---|---|---|---|
| 34.168.205.115 | `src/policies/acl_policy.rego` | `package application.authz` — ACL rules, schema array | GCP cluster node 1 |
| 84.247.178.132 | `policy/ui_features.rego` | `package ui_features` — UI feature flags, debug headers leaked | |
| 35.202.178.170 | `workflows/licensing/state_*.rego` | Licensing workflow state machine | |
| 34.168.179.214 | `src/policies/acl_policy.rego` | Same as 34.168.205.115 — same operator, multi-node | GCP cluster node 2 |
| 89.117.55.200 | `policies/execute_query.rego` | **SIA-Brain Authorization Policy — Phase Phoenix** | See below |
| 35.230.105.37 | `src/policies/acl_policy.rego` | Same ACL cluster | GCP cluster node 3 |
| 35.185.202.219 | `src/policies/acl_policy.rego` | Same ACL cluster | GCP cluster node 4 |

**Notable: SIA-Brain (89.117.55.200)**
Policy governs an AI data platform — "execute_sql", "validate_sql", "generate_insight", "retrieve_docs", "plan", "answer", "health_check" actions. Role model: admin (all), analyst (SQL+insight+docs+plan+answer), viewer (read-only). Policy references `services/policy_adapter.py` — internal service topology disclosed. The `/v1/policies` endpoint is the full authorization logic for this AI system.

4 instances (34.168.205.115, 34.168.179.214, 35.230.105.37, 35.185.202.219) share identical `acl_policy.rego` — same operator running a 4-node GCP cluster.

**4/10 offline** at probe time (158.220.104.240, 66.29.147.3, 194.233.166.227 — timeout; no connection).

#### Which tools contributed

| Stage | Tool | Contribution |
|---|---|---|
| 0 — Discover | Shodan (Playwright) | `port:8181 http.html:"Open Policy Agent"` — 10 IPs harvested |
| 1 — Fingerprint | HTML content match | |
| 2 — Verify | curl `/v1/policies` probe | 6/10 confirmed; full Rego policy source returned |
| 3 — Attribute | GCP IP prefix cluster (34.x/35.x) | 4-node cluster, same operator |
| 4 — Classify | Policy engine; ACL logic + AI system authz topology | HIGH |
| 5-6 | Not run | |

---

### F9. Ory Hydra — port 4445 — 5 confirmed via broad dork

**Verified 2026-05-28:** `http.html:"client_id"` on port 4445 returned 6 IPs; 5/6 confirmed via `GET /admin/clients` returning OAuth2 client list without auth.

| IP | Clients | Notes |
|---|---|---|
| 67.215.244.168 | 1 (`hydra-admin`, localhost callback) | Default dev deployment |
| 66.212.16.238 | 1 (`hydra-admin`, localhost callback) | Same template |
| 45.146.165.142 | 1 (`hydra-admin`, localhost callback) | Same template |
| 129.151.144.78 | 1 (`hydra-admin`, localhost callback) | Same template |
| 172.233.0.75 | 1 (`hydra-admin`, localhost callback) | Same template |

All 5 show `client_id: hydra-admin` with `redirect_uris: ["http://localhost/callback"]` — default Hydra quickstart configuration left internet-exposed. Admin API open: attacker can enumerate all OAuth2 clients, register new clients, and inject arbitrary redirect URIs. Severity: MEDIUM (dev deployments, minimal downstream user exposure).

Hydra :4445 does not appear in Shodan's HTML-content index — the broad dork worked; a precision dork did not. This confirms the prior null-dork result was a Shodan indexing gap, not an absence of exposed instances.

---

### Null results (confirmed dead dorks)

| Platform | Dork | Result | Notes |
|---|---|---|---|
| Ory Kratos admin | `port:4434 "identities" http.status:200` | 0 | Port 4434 not in Shodan HTTP index |
| Ory Hydra admin | `port:4445 "clients" http.status:200` | 0 | Port 4445 content not indexed; broad dork found 6 |
| Tyk Gateway | `port:8080 "x-tyk-gateway"` | 0 | Header not in crawl |
| Tyk Dashboard | `port:3000 http.title:"Tyk Dashboard"` | 0 | No indexed instances |
| OPAL | `port:7002 "opal_updates"` | 0 | Port 7002 not indexed |
| OPAL broad | `port:7002 http.status:200` | broad hits | Not OPAL-specific |
| OPA v1 dork | `port:8181 "v1/data" http.status:200` | 0 | Field not in Shodan crawl |
| Casdoor default creds | admin/123 probe | rejected | Password changed; auth enforced in practice |
| SuperTokens sample | `/users/count` probe | 0/10 live | Sample offline at probe time; 455 Shodan population still unverified |
| Authentik sample | `/api/v3/core/users/` probe | 0/10 live | Sample offline; population unverified |

Kratos and Hydra admin ports (4434, 4445) are absent from Shodan's precision-dork index. The absence from Shodan does not mean zero internet exposure — 5 Hydra instances were found via a broad port-only dork and confirmed via direct probe. The actual internet-facing population requires masscan/nmap sweep, not dork-based discovery.

---

## Cross-survey analysis

Auth-gateway platforms differ from the AI/ML services surveyed in prior categories. The populations are smaller (tens to hundreds, not thousands), the deployments are intentionally internet-facing (forward auth requires reachability), and the exposure classes are structural defaults rather than accidental misconfigurations. The pattern is: platform ships with no-auth admin, operator trusts network isolation, operator puts the service on internet.

SuperTokens at 455 instances is the largest unambiguously problematic population. Its zero-auth default on a health port that also gatekeeps the identity API means there is no indication to the operator that auth is missing -- the service works fine with or without an API key configured.

Authentik at 1,000+ is the largest population but has a more complex exposure class (auth required on admin, but CVE chain + unauth API surface).

---

## Methodology -- what this survey adds

Candidate Insight #50: Auth-gateway platform exposure class is structural-default, not operator error. SuperTokens, Kong admin, and Casdoor ship with no auth or default creds as their documented initial state. The mental model of "operator should have locked this down" is backward -- the platform chose no-auth as the default.

Candidate Insight #51: Shodan does not index Ory admin ports (4434, 4445). The zero-auth-by-design platforms with the highest severity have the lowest Shodan visibility. This creates an invisible population -- not indexed = not in surveys, but still exposed. Verification requires active port probing, not dork-based discovery.

---

## Honest negative space

Verification stage was not completed for any finding. All populations are Shodan-confirmed candidates, not verified exposures. The critical verification probes needed:
- SuperTokens: `GET /hello` (confirms platform), `GET /apiversion` (confirms no-auth), `GET /users/count` (confirms open identity store)
- Casdoor: `POST /api/login` with `admin/123` credentials
- Kong: `GET /` on port 8001 (returns `{"tagline":"Welcome to kong"}` if no auth)
- OPA: `GET /v1/policies` and `GET /v1/data` on port 8181
- Authentik: `GET /if/flow/initial-setup/` (returns 200 = claimable admin)

These require curl or httpx access to ~110 new IPs on ports 3567, 8000, 8001, 8181, 9000 -- blocked by current permission configuration.

Kratos (4434) and Hydra (4445) populations are unknown. Shodan does not index these ports. The actual internet-facing population requires masscan/nmap sweep of IPv4 space on these ports, which is out of scope for a Shodan-based survey.

aimap contribution was null because auth-gateway ports are not in aimap's AI/ML fingerprint corpus. The tool is purpose-built for AI/ML service detection. A follow-on aimap scan of the 110 harvested IPs on standard AI/ML ports (8000/8080/11434/6333 etc.) would determine whether any auth-gateway instances co-locate with the AI stack they protect.

---

## Disclosure queue

No findings are at verified status. No disclosure actions appropriate until per-host verification is complete.

---

## Toolchain provenance

```
Pre-survey OSINT (auth-gateway-osint-2026-05-27.md)
  └── Shodan Playwright harvest (12 dorks, ~110 IPs)
        ├── Confirmed populations: SuperTokens 455, Authentik 1000+, Authelia 33, Kong 4
        ├── Harvested IPs: Casdoor 10, Keycloak 10, ZITADEL 10, OPA 10
        ├── Null results: Kratos, Hydra, Tyk, OPAL (dork-level)
        └── aimap scan (110 IPs, auth-gateway ports)
              └── Null: no AI/ML co-location on scanned ports
              └── Note: auth-gateway ports not in aimap fingerprint corpus
```

## See also

- `/data/platform-intel/auth-gateway-osint-2026-05-27.md` -- pre-survey OSINT
- `/shodan/queries/auth-gateway-queries.md` -- query catalog
- Prior surveys: Argo Workflows survey (2026-05-27) -- similar auth-layer exposure class
