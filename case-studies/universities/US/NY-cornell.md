# Cornell University: Open WebUI v0.6.14 on `onepl.aap.cornell.edu` — Auth-On + API Keys Enabled

_NuClide Research · 2026-05-19_

---

## Summary

Cornell University runs an Open WebUI instance at `onepl.aap.cornell.edu` (128.253.41.30:3000). `/api/config` returned Open WebUI v0.6.14 with `enable_signup: false` (auth-on; no signup-open class) and `enable_api_key: true` (post-authentication API key minting enabled). Properly configured for closed enrollment. Documented here as a wave-2 cohort entry: contrasts with wave-1 signup-open hosts.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 128.253.41.30 |
| rDNS | `onepl.aap.cornell.edu` |
| Org (WHOIS) | Cornell University (per ARIN registration of `128.253.0.0/16` Cornell allocation) |
| Department | AAP (College of Architecture, Art, and Planning) per the subdomain |
| Hostname pattern | `onepl` — likely "One PL" referring to a specific compute resource within the AAP college |
| Open ports observed | 3000 (Open WebUI uvicorn) |

---

## Observations

### Open WebUI v0.6.14 on :3000

`GET http://onepl.aap.cornell.edu:3000/api/config` returned 200 with:

```json
{
  "status": true,
  "name": "Open WebUI",
  "version": "0.6.14",
  "default_locale": "",
  "oauth": {"providers": {}},
  "features": {
    "auth": true,
    "auth_trusted_header": false,
    "enable_signup_password_confirmation": false,
    "enable_ldap": false,
    "enable_api_key": true,
    "enable_signup": false,
    "enable_login_form": true,
    "enable_websocket": true,
    "enable_version_update_check": true
  }
}
```

**Class memberships observed:**
- `enable_signup: false` — public self-registration DISABLED. No signup-open class on this host.
- `enable_login_form: true` — login UI present (closed-enrollment users access via existing accounts).
- `enable_api_key: true` — authenticated users CAN mint API keys. Class: post-authentication API-key minting enabled.
- `enable_ldap: false` — no LDAP backend.
- `oauth.providers: {}` — no OIDC integration; either local accounts or some other backend.
- `auth_trusted_header: false` — no auth-bypass header trust.

**Class summary**: properly closed-enrollment Open WebUI deployment. The `enable_api_key: true` flag is worth noting — authenticated users can self-issue API keys that bypass UI-level controls (rate limits, content filters, audit logs that only apply to UI sessions). Whether Cornell's deployment intends this and tracks it auditably is a deployment-policy question, not a finding from external probe.

---

## Operator attribution (per Insight #4)

- **WHOIS OrgName**: Cornell University (Cornell holds `128.253.0.0/16`)
- **Hostname**: `onepl.aap.cornell.edu` — AAP (Architecture, Art, and Planning) college subdomain
- **Distinct from prior Cornell finds**: the existing NuClide baseline doesn't have a Cornell case study (Cornell is a NEW institution surfaced by this 2026-05-19 sweep at the institutional level, though they have prior unrelated infrastructure surveyed)

---

## Cross-tool confirmations

| Tool | Output | Notes |
|---|---|---|
| `aimap -ports-class wide` | Open WebUI matched via `/api/config` and root page | Confirmed via service classification |
| `visorbishop` (post-G5 fix) | Tool-internal output: `open-webui auth=auth severity=info` with `api_keys_enabled` indicator | End-to-end validation that the G5 signature correctly classifies the auth-on case as info (not critical) |
| Direct `/api/config` probe | Verified auth-on, signup-closed independently | |

---

## Notable details

- **Wave-2 cohort posture**: Cornell's Open WebUI matches the wave-2 pattern (5/5 wave-2 OW hosts had `enable_signup: false`). Wave-1 (Duke, Syracuse, UCLA, UMD, VT) was the opposite (5/5 `enable_signup: true`). Cornell, Cooper Union, Red Rocks CC, UCSB ResNet, and RIT seappsvr09 all share the closed-enrollment posture in wave-2.
- **`enable_api_key: true` is the one elevation-class flag** on this host. In wave-1, VT also had this flag set alongside signup-open (which combined to enable self-mint API keys post-signup-takeover). On Cornell, signup is closed, so API-key minting requires a pre-existing authenticated account.
- **AAP college subdomain** suggests this host is a research-instructional Open WebUI for the College of Architecture, Art, and Planning rather than a campus-wide service. The single-host posture (no observed sister hosts on `aap.cornell.edu`) is consistent with a small-scale departmental deployment.

---

## Class-membership summary (no tier labels per survey convention)

- Open WebUI auth-on class — OBSERVED (data: `enable_signup: false`, `auth: true`, login form enabled)
- API-key minting class — OBSERVED (data: `enable_api_key: true` — post-auth elevation surface, not a signup-open exposure)
- Properly-configured wave-2 cohort exemplar — OBSERVED

No tier labels assigned per survey convention. This is a documentation-of-good-deployment case, included for contrast with wave-1 signup-open cohort and for thesis-falsification data.

---

## Discovery method

- **Initial surfacing**: Stage-0 dork-map of 1,629 verified Shodan dorks scoped to `hostname:.edu` — host hit the Open WebUI title-and-port dork.
- **Verification**: direct `/api/config` probe.
- **Cross-validation**: visorbishop post-G5-fix run classified independently as `auth=auth severity=info` matching the manual marker probe.

---

## Source artifacts

- Workspace: `~/recon/edu-llm-infra-2026-05-19/stage2-wave2/`
- Direct probe: `wave2-openwebui-signup-verify.json` (Cornell-onepl section)
- aimap wave-2 report: `aimap-wave2.json`
- visorbishop wave-2: `arsenal/visorbishop-wave2.json`
