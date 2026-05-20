# UCLA: Multi-Service AI Stack on `ai.idre.ucla.edu` — Open WebUI Signup-Open + LDAP + LiteLLM Dual-Exposed

_NuClide Research · 2026-05-19_

---

## Summary

UCLA's Institute for Digital Research and Education (IDRE) runs a multi-service LLM stack at `ai.idre.ucla.edu` (128.97.60.220, Los Angeles). Three distinct services on three ports: Open WebUI v0.9.1 on :3000 with `enable_signup: true` and `enable_ldap: true` (signup-open class observed; LDAP federation observed), and LiteLLM Proxy v1.83.4 served twice — once directly via uvicorn on :8000 and once nginx-fronted on :80 — with `/openapi.json`, `/public/providers`, and `/public/litellm_model_cost_map` returning 200 unauth (info-disclosure class observed; content endpoints `/v1/*` correctly enforce authentication).

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 128.97.60.220 |
| rDNS | `ai.idre.ucla.edu` |
| Org (WHOIS) | University of California, Los Angeles (`OrgName: University of California, Los Angeles`, `NetName: UCLANET`, NetRange `128.97.0.0/16`) |
| Department | IDRE (Institute for Digital Research and Education) |
| City | Los Angeles, CA |
| SSH | OpenSSH 8.7 (port 22) |
| Open ports observed | 22 (SSH), 80 (HTTP — nginx 1.20.1), 3000 (Open WebUI uvicorn), 8000 (LiteLLM uvicorn) |
| Shodan CVE-tracking | 16 SSH/Apache CVEs |

---

## Observations

### Service 1 — Open WebUI v0.9.1 on :3000

`GET http://ai.idre.ucla.edu:3000/api/config` returned 200 with:

```json
{
  "status": true,
  "name": "Open WebUI",
  "version": "0.9.1",
  "default_locale": "",
  "oauth": {"providers": {}},
  "features": {
    "auth": true,
    "auth_trusted_header": false,
    "enable_signup_password_confirmation": false,
    "enable_ldap": true,
    "enable_api_keys": false,
    "enable_signup": true,
    "enable_login_form": true,
    "enable_password_change_form": true,
    "enable_websocket": true,
    "enable_version_update_check": true,
    "enable_public_active_users_count": true,
    "enable_easter_eggs": true
  }
}
```

**Class memberships observed:**
- `enable_signup: true` — public self-registration enabled. Class: signup-open.
- `enable_ldap: true` — LDAP authentication backend enabled alongside signup. Class: signup-open + directory-federated (a registered Open WebUI account interacts with a directory backend).
- `enable_api_keys: false` — post-signup API-key minting NOT enabled on this host (contrast with VT host where it is).
- `auth_trusted_header: false` — no auth-bypass header behind reverse proxy.

**What was NOT tested per restraint ethic:**
- The signup endpoint (`POST /api/v1/auths/signup`) was not invoked. Whether an actual signup would produce an admin or a regular user, or whether LDAP federation requires an additional directory step, is not data-verified from this probe.
- The downstream model inventory served via the registered-user path was not enumerated.

### Service 2 — LiteLLM Proxy v1.83.4 on :8000 (uvicorn direct)

`GET http://ai.idre.ucla.edu:8000/openapi.json` returned 200 with `application/json` content-type and 1,148,068 bytes of OpenAPI spec. Title: `"LiteLLM API"`.

`GET .../health/readiness` returned 200 with:

```json
{
  "status": "healthy",
  "db": "Not connected",
  "cache": null,
  "litellm_version": "1.83.4",
  "success_callbacks": [
    "sync_deployment_callback_on_success",
    "SkillsInjectionHook",
    "_PROXY_VirtualKeyModelMaxBudgetLimiter",
    "LeastBusyLoggingHandler",
    "_PROXY_MaxBudgetLimiter",
    "_PROXY_MaxParallelRequestsHandler_v3",
    "_PROXY_CacheControlCheck",
    "ResponsesIDSecurity",
    "_PROXY_MaxIterationsHandler",
    "_PROXY_MaxBudgetPerSessionHandler",
    "ServiceLogging"
  ],
  "use_aiohttp_transport": true,
  "log_level": "WARNING",
  "is_detailed_debug": false
}
```

`GET .../public/providers` returned 200 with 1,562 bytes — the full provider list (132+ entries beginning `a2a, a2a_agent, ai21, ai21_chat, aiml, anthropic, anthropic_text, apertis, ...`).

`GET .../public/litellm_model_cost_map` returned 200 with 1,010,290 bytes — the proxy's pricing table.

`GET .../v1/models` returned 401 `"Authentication Error, No api key passed in."`.

**Class memberships observed:**
- `/openapi.json` PUBLIC — full API surface enumerable. Class: info-disclosure (specification).
- `/public/providers` PUBLIC — backend provider list enumerable. Class: info-disclosure (configuration).
- `/public/litellm_model_cost_map` PUBLIC — pricing table enumerable. Class: info-disclosure (configuration).
- `/v1/models` AUTH-ENFORCED with virtual key. Class: auth-on at content endpoint.
- Callback list discloses internal pipeline structure: `SkillsInjectionHook`, `ResponsesIDSecurity`, `_PROXY_MaxBudgetPerSessionHandler` indicate budget enforcement and a custom `SkillsInjectionHook` worth noting.

### Service 3 — LiteLLM Proxy v1.83.4 on :80 (nginx-fronted)

Identical LiteLLM 1.83.4 surface to Service 2, but served through nginx/1.20.1 on port 80 instead of direct uvicorn on 8000. Same `/openapi.json`, same `/public/*` endpoints, same callback list, same content-endpoint auth enforcement.

This is the SAME LiteLLM instance fronted twice: once with direct uvicorn exposure (anti-pattern) and once through the production nginx path. Either is reachable; the duplicate exposure means a fix to one path doesn't close the other.

---

## Operator attribution (per Insight #4)

- **WHOIS OrgName**: University of California, Los Angeles
- **WHOIS NetName**: UCLANET (CIDR `128.97.0.0/16`)
- **Hostname**: `ai.idre.ucla.edu` — IDRE (Institute for Digital Research and Education), UCLA's HPC/research-computing service unit
- **Shodan reported org**: University of California, Los Angeles

Authoritative attribution chain matches across all three sources. No CDN / proxy obscuring origin.

---

## Cross-tool confirmations

| Tool | Output | Notes |
|---|---|---|
| `aimap -ports-class wide` | Open WebUI + LiteLLM both surfaced via deep-enum | Confirmed via service classification |
| `visorbishop` (post-G5 fix) | `open-webui auth=signup-open severity=critical` (tool-internal) + `litellm auth=public-api severity=high` (tool-internal) | End-to-end validation of the G5 signature fix |
| `nu-recon` (with Shodan key) | open_ports=[22, 80, 3000, 8000]; SSH 8.7 ECDSA fingerprint `78:9b:c3:29:5c:db:0f:5d:59:7c:2e:a2:3f:08:96:c3` | Cross-confirmed Shodan port list |
| `aimap-profile` | classification=`education`, CFAA-CSIRT routing flag | |
| `jaxen profile` | `Research/Academic — MEDIUM` tier (tool-internal) | |
| `visorgraph` | 1 service node (port 80 nginx), 0 cert-pivot edges | Expected: direct-routed institutional IP has no cert chain to pivot |

---

## Notable details

- This is a single host (128.97.60.220) serving three distinct LLM-stack services in a single deployment. The deployment posture is "expose everything that listens" rather than "expose only the user-facing chat UI."
- The Open WebUI version (0.9.1) is recent and includes the multi-feature post-signup environment (LDAP, password change form, API keys are all togglable). The deployer enabled signup + LDAP — that's a combination worth flagging in any institutional review: it allows directory-federated accounts to be self-created from the public internet.
- The LiteLLM proxy's `db: "Not connected"` health-readiness response is consistent with a stateless deployment that proxies upstream providers without persistent session storage. The `SkillsInjectionHook` callback and the `ResponsesIDSecurity` callback suggest a custom configuration with prompt-injection mitigations layered in.
- The presence of `enable_easter_eggs: true` is a UI flag and not material; included only because it's in the same config dict.

---

## Discovery method

- **Initial surfacing**: Stage-0 dork-map of 1,629 verified Shodan dorks scoped to `hostname:.edu` on 2026-05-19. The host hit the Open WebUI title-and-port dork as well as the LiteLLM `/openapi.json` body dork.
- **Verification**: direct `/api/config` and `/openapi.json` probes; WHOIS netblock confirm.
- **Cross-validation**: post-fix visorbishop run produced platform=open-webui auth=signup-open with ldap+signup indicators; visorbishop classifier matched the manual marker probes.

---

## Source artifacts

- Workspace: `~/recon/edu-llm-infra-2026-05-19/`
- Initial probe: `arsenal-out/critical-openwebui-results.json` (UCLA section)
- LiteLLM gap-fill: `arsenal-out/gap-fill.json` (UCLA-80-LLM section)
- Whois: `arsenal-out/whois-5-confirmed.txt`
- Shodan host data: `arsenal-out/shodan-host-ucla.txt`
- aimap full report: `aimap-results.json`
- visorbishop wave-1 revalidation: `stage2-wave2/arsenal/visorbishop-wave1-revalidate.json`
