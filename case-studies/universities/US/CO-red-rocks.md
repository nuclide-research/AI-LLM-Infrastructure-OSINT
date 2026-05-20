# Red Rocks Community College: Open WebUI v0.9.2 on `datalab02.rrcc.edu` — Auth-On + LDAP (First Community College in Survey)

_NuClide Research · 2026-05-19_

---

## Summary

Red Rocks Community College runs an Open WebUI instance at `datalab02.rrcc.edu` (164.47.99.16:8080). `/api/config` returned Open WebUI v0.9.2 with `enable_signup: false` (auth-on; no signup-open class) and `enable_ldap: true` (LDAP federation backend enabled). Properly configured closed-enrollment deployment. **First community college observed in the NuClide .edu LLM-infra ledger.**

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 164.47.99.16 |
| rDNS | `datalab02.rrcc.edu` |
| Org | Red Rocks Community College (Colorado Community College System) |
| Hostname semantics | `datalab02` — data lab compute host, server 02 (implying at least a `datalab01`; potentially more) |
| Open port observed | 8080 (Open WebUI uvicorn) |
| Open WebUI version | 0.9.2 (recent) |

---

## Observations

`GET http://datalab02.rrcc.edu:8080/api/config` returned 200 with:

```json
{
  "status": true,
  "name": "Open WebUI",
  "version": "0.9.2",
  "default_locale": "",
  "oauth": {"providers": {}},
  "features": {
    "auth": true,
    "auth_trusted_header": false,
    "enable_signup_password_confirmation": false,
    "enable_ldap": true,
    "enable_api_key": null,
    "enable_signup": false,
    "enable_login_form": true,
    "enable_websocket": true,
    "enable_version_update_check": true,
    "enable_public_active_users_count": true,
    "enable_easter_eggs": true
  }
}
```

**Class memberships observed:**
- `enable_signup: false` — public self-registration DISABLED. No signup-open class.
- `enable_ldap: true` — LDAP authentication backend ENABLED. Authentication flows through RRCC's directory.
- `enable_api_key: null` — API-key minting NOT enabled.
- `auth_trusted_header: false` — no auth-bypass header trust.
- `oauth.providers: {}` — no OIDC (LDAP is the auth path).

**Class summary**: properly configured closed-enrollment Open WebUI with LDAP federation. Same posture as Cooper Union — auth-on + LDAP backend + no post-auth API-key minting. The deployment template (Open WebUI 0.9.2 with LDAP enabled) is identical between RRCC and Cooper Union, suggesting common upstream documentation or a courseware/vendor recommendation.

---

## Operator attribution (per Insight #4)

- **Org**: Red Rocks Community College
- **Hostname**: `datalab02.rrcc.edu` — data-lab compute host, presumably part of a CS / data-science instruction lab
- **Institution type**: community college (2-year associate-degree-granting public institution); part of the Colorado Community College System
- **Hostname `datalab02` implies a sister host `datalab01`** — worth a follow-up `hostname:rrcc.edu` Shodan sweep to enumerate the lab fleet

---

## Cross-tool confirmations

| Tool | Output | Notes |
|---|---|---|
| `aimap -ports-class wide` | Open WebUI matched via `/api/config` on :8080 | |
| `visorbishop` (post-G5 fix) | Tool-internal output: `open-webui auth=auth severity=info` with `ldap_enabled: True` indicator | |
| Direct `/api/config` probe | Verified auth-on + LDAP independently | |
| `aimap-profile` | `classification: education`, CFAA-CSIRT routing flag | |

---

## Notable details

- **First community college in the survey**. Community colleges represent a substantial fraction of US post-secondary enrollment (~30% of undergraduates) but are not typically thought of as deploying advanced LLM infrastructure. RRCC's `datalab02` shows the LLM-deployment trend has reached the 2-year college sector.
- **Identical deployment template to Cooper Union**: both run Open WebUI 0.9.2 with `enable_ldap: true` + `enable_signup: false` + `enable_api_key: null`. Same upstream documentation (Open WebUI's own LDAP integration guide) or a common courseware vendor's reference deployment. Worth tracking whether more `enable_ldap` deployments appear at version 0.9.2 in future surveys — could indicate a vendor-recommended configuration template.
- **`datalab` naming** typical of CS-instruction infrastructure ("data lab" suggests intro-to-data-science / SQL / analytics courses). Open WebUI at this scale is presumably a student-accessible LLM for coursework, gated through LDAP-federated student credentials.
- **No public model inventory observed** — the OW UI requires login, so model lists aren't visible without authentication (correct posture).

---

## Class-membership summary (no tier labels per survey convention)

- Open WebUI auth-on class — OBSERVED (`enable_signup: false`, `auth: true`)
- LDAP federation class — OBSERVED (`enable_ldap: true`)
- Community-college sector LLM deployment — OBSERVED (new institution type)
- Common-template-with-Cooper-Union pattern — OBSERVED (identical config flags, identical version)

No tier labels assigned per survey convention. Documented for sector expansion (first 2-year college) and for the common-template pattern.

---

## Discovery method

- **Initial surfacing**: Stage-0 dork-map of 1,629 verified Shodan dorks scoped to `hostname:.edu` — host hit the Open WebUI title-and-port dork.
- **Verification**: direct `/api/config` probe.
- **Cross-validation**: visorbishop post-G5-fix run independently classified `auth=auth` with `ldap_enabled` indicator.

---

## Source artifacts

- Workspace: `~/recon/edu-llm-infra-2026-05-19/stage2-wave2/`
- Direct probe: `wave2-openwebui-signup-verify.json` (RedRocks-CC section)
- aimap wave-2: `aimap-wave2.json`
- visorbishop wave-2: `arsenal/visorbishop-wave2.json` (Red Rocks with `ldap_enabled` indicator)

---

## Sector expansion note

This is the first community college in the NuClide university ledger. Earlier sweeps focused on 4-year research universities (the population most likely to deploy LLM infrastructure). The presence of RRCC in this sweep suggests the .edu LLM-infra population extends to 2-year colleges and possibly K-12 districts (the Hungarian Szemere Bertalan Vocational High School caught by visorgoose in the same wave-2 run is the international parallel — see `WAVE2-FINDINGS.md`).

A follow-up survey scoped to `hostname:.cc.*.edu` (community college subdomain convention in many state systems) and `hostname:.k12.*.us` (K-12 district convention) would extend the sector coverage and validate whether the deployment template observed here (Open WebUI 0.9.2 + LDAP) is more broadly used in lower-resource institutional contexts.
