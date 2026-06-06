---
type: case-study
category: cat-df
platform: Dify
date: 2026-06-06
findings: 3 setup-open, 6 signup-open, 939 config-disclosure
status: verified
---

# Dify Population Survey — 939 Config-Disclosure, 9 Open Auth Findings

_NuClide Research · 2026-06-06_

---

## Discovery

Dify is an open-source LLM application development platform (drag-and-drop workflow builder, RAG pipelines, agent orchestration). 2,289 Shodan-indexed instances on `http.title:"Dify"`.

The `/console/api/system-features` endpoint returns system auth configuration without authentication on every responding instance. One GET reveals: whether public registration is open, whether SSO is enforced, auth methods enabled, and license tier. No login required.

Two attack surfaces:
1. **SETUP_OPEN**: Instance deployed but setup wizard not completed. First user to register becomes admin.
2. **SIGNUP_OPEN** (`is_allow_register: true`): Public registration enabled on a configured instance. Any internet user can create an account.

Secondary finding: **939 instances expose full auth configuration** via unauthenticated `/console/api/system-features` — a population-scale config disclosure.

---

## Population Results

| Category | Count | Rate |
|---|---|---|
| SETUP_OPEN (uninitialized — first-user-admin) | 3 | 0.3% |
| SIGNUP_OPEN (public registration enabled) | 6 | 0.6% |
| CONFIG_DISC (system-features unauth) | 939 | 99% of reachable |
| Enterprise license exposed | 3 | 0.3% |
| **Total reachable** | **948** | 59% of 1,600 probed |

Survey base: 1,600 instances (Shodan download from 2,289 total, `--limit 2500`).

---

## Public Endpoint: `/console/api/system-features`

Every responding Dify instance exposes its full auth configuration unauthenticated:

```json
GET /console/api/system-features

{
  "sso_enforced_for_signin": false,
  "sso_enforced_for_signin_protocol": "",
  "sso_enforced_for_web": false,
  "sso_enforced_for_web_protocol": "",
  "enable_web_sso_switch_component": false,
  "enable_email_code_login": false,
  "enable_email_password_login": true,
  "enable_social_oauth_login": false,
  "is_allow_register": false,
  "is_allow_create_workspace": false,
  "is_email_setup": false,
  "license": {
    "status": "none",
    "expired_at": ""
  }
}
```

This endpoint is intentionally public — Dify's frontend needs it to render the login UI correctly. But it leaks:
- Whether the operator is a paying enterprise customer (`license.status: active`)
- Whether SSO is enforced (and which protocol — SAML/OIDC)
- Whether public registration is open (`is_allow_register`)
- Whether email is configured (useful for phishing surface mapping)

---

## SETUP_OPEN Instances (3)

| IP:Port | Provider | Region | Status |
|---|---|---|---|
| 138.2.39.120:8099 | Oracle Cloud | Japan | Not started |
| 43.155.249.190:443 | TencentCloud | Korea | Not started |
| 8.155.51.185:80 | Alibaba Cloud | China | Not started |

Uninitialized Dify: operator deployed the Docker stack but never completed the setup wizard. The setup wizard creates the first admin account. With `step: not_started`, any internet user who hits the signup page first becomes the sole admin.

**Verification:** `GET /console/api/setup` returns `{"step": "not_started"}`. No account creation attempted (restraint).

---

## SIGNUP_OPEN Instances (6)

| IP:Port | Provider | Region | SSO | Notes |
|---|---|---|---|---|
| 14.103.197.159:443 | China Telecom | China | No | — |
| 158.101.251.2:30000 | TBD | TBD | No | Non-standard port |
| 47.117.33.199:80 | Alibaba Cloud | China | Yes | SSO + register conflict |
| 47.97.191.11:80 | Alibaba Cloud | China | No | — |
| 47.97.191.11:443 | Alibaba Cloud | China | No | Same host, dual port |
| 47.98.156.142:8080 | Alibaba Cloud | China | No | — |

`47.117.33.199` is the most interesting: `sso_enforced_for_signin: true` AND `is_allow_register: true` simultaneously. SSO enforcement is designed to prevent password-based login — but if registration is also open, the first-user path may bypass SSO enforcement. Dify creates a local account during registration before SSO is enforced at login. The registration endpoint (`/console/api/login`) path warrants closer examination for this configuration.

---

## Enterprise License Exposure — ByteDance Volcano Engine

Three consecutive IPs on AS137718 (Beijing Volcano Engine Technology Co., Ltd. — ByteDance's cloud):

```
115.190.33.251:3000  license=active
115.190.34.12:3000   license=active
115.190.75.228:3000  license=active
```

Consecutive IPs on the same ASN suggest a shared enterprise test cluster. Each exposes `license.status: active` unauthenticated, confirming enterprise Dify deployment by a ByteDance subsidiary or customer. Registration disabled, email auth enabled, no SSO. Auth-locked but license tier and auth configuration publicly disclosed.

---

## The Auth Configuration Intel Surface

The `system-features` endpoint creates an operator-profiling surface at population scale:

- **`is_allow_register: true`** — 6/948 (0.6%). Target for first-user-admin account creation.
- **`sso_enforced_for_signin: true`** — indicates enterprise deployment with identity provider. Corporate environment with AD/LDAP/SAML integration.
- **`enable_email_code_login: true`** — email OTP enabled. Phishing surface if operator's email is known.
- **`is_email_setup: false`** — no outbound email configured. Password reset flows broken; some auth paths may be misconfigured.
- **`license.status: active`** — enterprise customer. Higher-value target; production environment likely.

---

## Toolchain Provenance

```
Step -1:  Platform intel (no prior tome entry; derived from Dify GitHub + live probing)
Step 0:   shodan download --limit 2500 'http.title:"Dify"' (2,289 total; 1,600 downloaded)
Step 0c:  /tmp/dify_probe.py — 3 endpoints per host, 40 workers
          /console/api/system-features (config disclosure)
          /console/api/setup (setup state)
          /console/api/apps (auth gate check)
Step 3v:  Operator attribution via ipinfo.io ASN lookup
          System-features response manual verification
Step 12b: This document
```

Endpoint discovery method informed by: Hacking APIs (Corey Ball, No Starch Press, 2022) Ch. 7 — check for public system info endpoints before assuming all API surface is auth-gated.

---

## Remediation

```yaml
# Dify docker-compose.yaml environment:
INIT_PASSWORD: <strong-random-password>  # Forces password on first admin account

# After setup:
# Disable public registration in Settings > Members > Authentication
# Set is_allow_register: false (default) unless intentional
```

Verify:
```bash
curl http://IP:PORT/console/api/system-features | python3 -c "
import sys, json
d = json.load(sys.stdin)
print('register:', d.get('is_allow_register'))
print('setup:', end=' ')
" && curl http://IP:PORT/console/api/setup | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(d.get('step'))
"
# Expected: register: False, setup: finished
```
