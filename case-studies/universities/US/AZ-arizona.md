# University of Arizona: Branded "U of A GenAI" — Open WebUI v0.7.2 with University-OIDC + Auth-On

_NuClide Research · 2026-05-19_

---

## Summary

The University of Arizona operates a branded institutional Open WebUI service at `genai.arizona.edu` (128.196.254.101). The deployment is reachable on port 80 (reverse-proxied; Open WebUI's typical :3000 not directly exposed). `/api/config` returned Open WebUI v0.7.2 with `name: "U of A GenAI (Open WebUI)"` — customized service title — and an OIDC backend identified as `"University of Arizona"`. Signup is closed (`enable_signup: false`). Properly configured institutional LLM service with institutional OIDC integration; documented here as a wave-2 cohort exemplar of correct deployment posture.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 128.196.254.101 |
| rDNS | `genai.arizona.edu` |
| Org (WHOIS) | University of Arizona (per ARIN registration of the `128.196.0.0/16` Arizona allocation) |
| Subdomain | `genai.arizona.edu` — institutionally-branded generative-AI service URL |
| Open port observed | 80 (reverse-proxied Open WebUI) |
| Open WebUI version | 0.7.2 |

---

## Observations

`GET http://genai.arizona.edu/api/config` returned 200 with:

```json
{
  "status": true,
  "name": "U of A GenAI (Open WebUI)",
  "version": "0.7.2",
  "default_locale": "",
  "oauth": {"providers": {"oidc": "University of Arizona"}},
  "features": {
    "auth": true,
    "auth_trusted_header": false,
    "enable_signup_password_confirmation": false,
    "enable_ldap": false,
    "enable_api_key": false,
    "enable_signup": false,
    "enable_login_form": true,
    "enable_websocket": true,
    "enable_version_update_check": true
  }
}
```

**Class memberships observed:**
- `name: "U of A GenAI (Open WebUI)"` — customized branding (not the default `"Open WebUI"`). The deployment has been intentionally branded for institutional use.
- `oauth.providers.oidc: "University of Arizona"` — institutional OIDC backend configured. Authentication routes through U-Arizona's identity provider.
- `enable_signup: false` — public self-registration DISABLED. No signup-open class.
- `enable_api_key: false` — post-auth API-key minting DISABLED.
- `enable_ldap: false` — no LDAP backend (OIDC is the auth path).
- `enable_login_form: true` — login form rendered (presumably routes to the OIDC flow).
- `auth_trusted_header: false` — no auth-bypass header.

**Class summary**: properly configured institutional LLM service. OIDC-only authentication, signup closed, no post-auth API-key minting. Title customization indicates the deployment is part of a formal institutional service rather than an ad-hoc instance.

`GET http://genai.arizona.edu/api/version` returned `{"version":"0.7.2","deployment_id":""}`.
`GET http://genai.arizona.edu/health` returned `{"status":true}`.

---

## Operator attribution (per Insight #4)

- **WHOIS OrgName**: University of Arizona
- **Hostname**: `genai.arizona.edu` — institutional subdomain dedicated to the generative-AI service (the `genai.` prefix indicates this is an officially-named service URL, not a faculty/lab personal host)
- **OIDC provider name**: `"University of Arizona"` — backend authentication goes through the institution's identity provider, confirming institutional administration
- Authoritative attribution chain matches across all sources

---

## Cross-tool confirmations

| Tool | Output | Notes |
|---|---|---|
| `aimap -ports-class wide` | Surfaced :80 as Open WebUI via `/api/config` body match | aimap caught it but the wave-2 wide-profile scan classified it because `/api/config` returned 200 with `Open WebUI` text in body |
| `visorbishop` (post-G5 fix) | Did NOT confirm — Bishop's signature anchors on the raw `"Open WebUI"` substring; the U-Arizona deployment uses a customized title `"U of A GenAI (Open WebUI)"` which Bishop's substring matcher missed | **Logged as G5-extension follow-up**: signature should match `"Open WebUI"` substring within `name` field, not exact equality. Branded institutional deployments will increasingly hit this. |
| Direct `/api/config` probe | Verified independently | |

---

## Notable details

- **First institutionally-branded Open WebUI** seen in this survey. Other hosts (Duke `vcm-51699`, UCLA `ai.idre`, etc.) all returned the default `"Open WebUI"` name without customization. U-Arizona's branding indicates a formal institutional service rather than an ad-hoc faculty deployment.
- **OIDC backend identified as `"University of Arizona"`** — this label is configured server-side and tells Open WebUI to route login through the institutional IDP. Combined with `enable_signup: false`, only U-Arizona-credentialed users can access.
- **Reverse-proxied on port 80** rather than the default `:3000` — typical for an institutional service that wants the URL to be `https://genai.arizona.edu` rather than `https://genai.arizona.edu:3000`. The Open WebUI behind the reverse proxy is otherwise the same.
- **Documented here as a contrast** to wave-1 signup-open cohort: U-Arizona's deployment is what "Open WebUI done correctly" looks like at an institutional level — closed enrollment, institutional IDP, customized branding, no post-auth API-key minting flag.

---

## Class-membership summary (no tier labels per survey convention)

- Open WebUI auth-on class — OBSERVED
- Institutional OIDC backend class — OBSERVED (provider name configured server-side as institution-specific)
- Customized branding class — OBSERVED (non-default `name` field)
- Closed-enrollment + IDP-gated access class — OBSERVED

No tier labels assigned per survey convention. This is a documented-as-properly-configured exemplar; included for cohort contrast and to identify the G5-extension follow-up gap (visorbishop substring vs exact-match on the platform `name` field).

---

## Discovery method

- **Initial surfacing**: Stage-0 dork-map of 1,629 verified Shodan dorks scoped to `hostname:.edu` — host hit the Open WebUI title-and-port dork (the `Open WebUI` substring in title appears in customized branding too).
- **Verification**: direct `/api/config` probe; OIDC provider name confirmed institutional administration.
- **Cross-validation gap**: visorbishop's G5 signature didn't classify this host because it anchors on bare `"Open WebUI"` title equality; customized branding bypasses. Logged for follow-up.

---

## Source artifacts

- Workspace: `~/recon/edu-llm-infra-2026-05-19/stage2-wave2/`
- Direct probe: `wave2-stragglers-and-jupyterhub.json` (Arizona-genai section)
- aimap wave-2 report: `aimap-wave2.json`
- WAVE2-FINDINGS doc: `WAVE2-FINDINGS.md`
