# Cooper Union for the Advancement of Science and Art: Open WebUI v0.9.2 on `kahan.ee.cooper.edu` — Auth-On + LDAP

_NuClide Research · 2026-05-19_

---

## Summary

Cooper Union runs an Open WebUI instance at `kahan.ee.cooper.edu` (199.98.27.237). `/api/config` returned Open WebUI v0.9.2 with `enable_signup: false` (auth-on; no signup-open class) and `enable_ldap: true` (LDAP federation backend enabled). Properly configured closed-enrollment deployment with directory integration. Documented as a wave-2 cohort entry — first private engineering school in the survey.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 199.98.27.237 |
| rDNS | `kahan.ee.cooper.edu` |
| Org | The Cooper Union for the Advancement of Science and Art (per ARIN registration of `199.98.27.0/24` Cooper Union allocation) |
| Department | EE (Electrical Engineering) per the `ee.cooper.edu` subdomain |
| Hostname semantics | `kahan` — likely named after mathematician William Kahan (numerical analysis, IEEE 754); a common convention for math/CS/EE compute hosts |
| Open port observed | 3000 (Open WebUI uvicorn) |
| Open WebUI version | 0.9.2 (recent) |

---

## Observations

`GET http://kahan.ee.cooper.edu:3000/api/config` returned 200 with:

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
- `enable_ldap: true` — LDAP authentication backend ENABLED. Authentication flows through Cooper Union's LDAP directory.
- `enable_api_key: null` — API-key minting NOT enabled (the `null` value rather than `false` is the same effective state in Open WebUI 0.9.x; both block the post-auth API-key minting path).
- `auth_trusted_header: false` — no auth-bypass header trust.
- `oauth.providers: {}` — no OIDC backend (LDAP is the auth path).
- `enable_easter_eggs: true` — UI flag, not material.

**Class summary**: properly configured closed-enrollment Open WebUI with LDAP federation. Cooper Union's LDAP directory is the source of truth for who can authenticate. No public signup, no post-auth API-key minting elevation surface.

---

## Operator attribution (per Insight #4)

- **Org**: The Cooper Union for the Advancement of Science and Art (small private engineering school in NYC)
- **Hostname**: `kahan.ee.cooper.edu` — EE department, faculty/lab compute host
- **Hostname naming pattern**: mathematician name (`kahan`) — Cooper Union may have a department-wide convention of naming compute hosts after mathematicians/scientists (worth a follow-up enumeration of `cooper.edu` to see if other hosts follow the pattern)

---

## Cross-tool confirmations

| Tool | Output | Notes |
|---|---|---|
| `aimap -ports-class wide` | Open WebUI matched via `/api/config` and root body | |
| `visorbishop` (post-G5 fix) | Tool-internal output: `open-webui auth=auth severity=info` with `ldap_enabled: True` indicator | End-to-end validation; the LDAP indicator surfaces in the JSON output |
| Direct `/api/config` probe | Verified auth-on + LDAP independently | |
| `aimap-profile` | `classification: education`, CFAA-CSIRT routing flag | |
| `jaxen profile` | `Research/Academic — MEDIUM` (tool-internal) | |

---

## Notable details

- **Cooper Union is a small private engineering school** — relatively low-population institution (~1,000 students) but with significant historical legacy in engineering education. Worth noting as a category: the survey was originally framed around larger research universities, but Cooper Union demonstrates that smaller institutions are also standing up Open WebUI deployments.
- **LDAP + signup-closed combination is the correct pattern** for institutional authentication. Compare to UCLA `ai.idre.ucla.edu` which has LDAP + signup-OPEN (anyone can self-register AND that account is then directory-federated — a layered exposure). Cooper Union's posture is what UCLA's should look like.
- **`kahan` hostname** — if this is part of a department convention, other Cooper Union hosts (`turing.ee.cooper.edu`, `hopper.cs.cooper.edu`, etc.) may exist. A `hostname:cooper.edu` Shodan sweep would surface the pattern.

---

## Class-membership summary (no tier labels per survey convention)

- Open WebUI auth-on class — OBSERVED (`enable_signup: false`, `auth: true`)
- LDAP federation class — OBSERVED (`enable_ldap: true`)
- Properly-configured closed-enrollment-with-directory exemplar — OBSERVED

No tier labels assigned per survey convention. Documented for wave-2 cohort contrast.

---

## Discovery method

- **Initial surfacing**: Stage-0 dork-map of 1,629 verified Shodan dorks scoped to `hostname:.edu` — host hit the Open WebUI title-and-port dork.
- **Verification**: direct `/api/config` probe.
- **Cross-validation**: visorbishop post-G5-fix run independently classified `auth=auth` with `ldap_enabled` indicator.

---

## Source artifacts

- Workspace: `~/recon/edu-llm-infra-2026-05-19/stage2-wave2/`
- Direct probe: `wave2-openwebui-signup-verify.json` (Cooper-Union section)
- aimap wave-2: `aimap-wave2.json`
- visorbishop wave-2: `arsenal/visorbishop-wave2.json` (Cooper Union with `ldap_enabled` indicator)
