# University of Maryland College Park: Open WebUI v0.3.32 on `amorgos.umd.edu` — `enable_signup:true` OBSERVED on Very-Old Version

_NuClide Research · 2026-05-19_

---

## Summary

University of Maryland College Park runs an Open WebUI instance at `amorgos.umd.edu` (128.8.235.4, Brookeville MD). `/api/config` returned `enable_signup: true` on Open WebUI v0.3.32 — class membership for signup-open OBSERVED. Version 0.3.32 is significantly older than the current Open WebUI release line; multiple disclosed advisories apply per the publicly-known version-vulnerability mapping. Apache 2.4.58 serving the Ubuntu default "It works" page is present on port 80 alongside the OW deployment on port 8080.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 128.8.235.4 |
| rDNS | `128-8-235-4.umd.edu`; `amorgos.umd.edu` |
| Org (WHOIS) | University of Maryland (`OrgName: University of Maryland`, `NetName: UMDNET-1`, CIDR `128.8.0.0/16`, OrgId `UNIVER-262-Z`) |
| City | Brookeville, MD |
| Shodan reported org | University of Maryland |
| Open ports observed | 22 (OpenSSH 9.6p1 Ubuntu 3ubuntu13.15), 80 (Apache/2.4.58 Ubuntu default page), 8080 (Open WebUI uvicorn) |
| Shodan CVE-tracking | ~44 CVEs across the SSH + Apache stack (`CVE-2024-47252`, `CVE-2024-38475`, etc. — see Shodan host record for current list) |

---

## Observations

### Service 1 — Open WebUI v0.3.32 on :8080

`GET http://amorgos.umd.edu:8080/api/config` returned 200 with:

```json
{
  "status": true,
  "name": "Open WebUI",
  "version": "0.3.32",
  "default_locale": "",
  "oauth": {"providers": {}},
  "features": {
    "auth": true,
    "auth_trusted_header": false,
    "enable_signup": true,
    "enable_login_form": true
  }
}
```

**Class memberships observed:**
- `enable_signup: true` — public self-registration enabled. Class: signup-open.
- `auth_trusted_header: false` — no auth-bypass header behind reverse proxy.
- `oauth.providers: {}` — no OIDC integration.
- Version 0.3.32 is very old — well behind the current Open WebUI release cadence (v0.9.x as of mid-2026 sweep).

**What was NOT tested per restraint ethic:**
- The signup endpoint (`POST /api/v1/auths/signup`) was not invoked.
- Whether the resulting account would have admin or regular-user role is not data-verified.
- Whether the host has been patched against any of the publicly-disclosed Open WebUI vulnerabilities applying to the 0.3.32 version range is not testable without invoking the affected endpoints.

`/api/version` returned `{"version":"0.3.32"}` confirming.
`/api/v1/auths/` returned 403 (`{"detail":"Not authenticated"}`) — content endpoints correctly require auth.
`/openapi.json` returned 200 with full FastAPI OpenAPI spec (~15.7 KB) — API surface enumerable without auth.

### Service 2 — Apache 2.4.58 on :80 (Ubuntu default page)

`GET http://amorgos.umd.edu/` returned 200 with `Server: Apache/2.4.58 (Ubuntu)` and the body content includes `<title>Apache2 Ubuntu Default Page: It works</title>` — the unmodified default Ubuntu Apache install page.

`/server-status` returned 403 (correctly locked).
`/server-info` returned 404.

**Class observed**: default-install posture — port 80 listens but no application has been configured to serve from it. The hostname `amorgos.umd.edu` resolves to this same IP, so the public-facing :80 is the Ubuntu default page. Either deployment is incomplete (intent was to front the OW on :8080 with HTTPS/Apache but never finished) or the operator deliberately left :80 as a placeholder.

### Service 3 — SSH OpenSSH 9.6p1 Ubuntu 3ubuntu13.15 on :22

Currently-patched OpenSSH (3ubuntu13.15 is recent within the 9.6p1 Ubuntu series). Standard institutional SSH; nothing distinctive on this host's record beyond Shodan's catch-all CVE tracking for the SSH stack.

---

## Operator attribution (per Insight #4)

- **WHOIS OrgName**: University of Maryland
- **WHOIS NetName**: UMDNET-1 (CIDR `128.8.0.0/16`)
- **WHOIS OrgId**: UNIVER-262-Z
- **Hostname**: `amorgos.umd.edu` — appears to be a named individual researcher / lab compute host (single-word host pattern common to faculty workstations and small lab servers at UMD's `128.8.0.0/16` allocation)
- **Shodan reported org**: University of Maryland

Authoritative attribution chain matches across all three sources. Direct-routed institutional IP; no CDN/proxy.

---

## Cross-tool confirmations

| Tool | Output | Notes |
|---|---|---|
| `aimap -ports-class llm-gateway` | Surfaced :8080 as Open WebUI | Confirmed via service classification |
| `visorbishop` (post-G5 fix) | Tool-internal output: `open-webui auth=signup-open severity=critical` with `signup_open: True` indicator | End-to-end validation of the G5 signature fix on this host |
| Direct `/api/config` probe | Verified signup-open class membership independently | |
| `aimap-profile` | `classification: education`, ethics flag for CFAA-CSIRT routing, `distinct_hostnames: 2` (caught both `amorgos.umd.edu` and `128-8-235-4.umd.edu`) | |
| `jaxen profile` | `Research/Academic — MEDIUM` tier (tool-internal) | |
| `nu-recon` (with Shodan key) | open_ports=[22, 80, 8080]; SSH key fingerprint captured; passive DNS confirmed | |

---

## Notable details

- **Open WebUI 0.3.32 is well behind the current release line.** As of the 2026-05 sweep, current Open WebUI versions are in the 0.9.x range. Each major version since 0.3.x has shipped feature changes and patches. Wave-1 of this survey caught five `enable_signup:true` hosts at version range 0.6.x to 0.9.x; UMD's 0.3.32 is the oldest in the cohort, increasing the surface area of publicly-disclosed advisories that apply.
- **Hostname `amorgos` suggests Mt. Amorgos / Greek-island naming** — common pattern for faculty/lab compute named after geographic places. May identify as a specific research group's server when cross-referenced with UMD's department / faculty directories.
- **Two hostnames on one IP**: Shodan shows both `amorgos.umd.edu` and the reverse-DNS-style `128-8-235-4.umd.edu`. Both resolve to 128.8.235.4. The double-naming is normal for direct-routed institutional IPs.
- **Apache default page on port 80** is a deployment-discipline observation, not a finding per se. It signals an incomplete deployment template that left port 80 unconfigured.

---

## Class-membership summary (no tier labels per survey convention)

- Public Open WebUI signup-open class — OBSERVED (data: `enable_signup: true` in `/api/config`)
- Very-old version class (0.3.32 in a 0.9.x-current line) — OBSERVED
- API enumeration class — OBSERVED (data: `/openapi.json` returns 200 unauth)
- Default-install Apache class — OBSERVED (data: default Ubuntu "It works" page on :80)
- Account-takeover potential class — APPLICABLE per Open WebUI's documented signup-open behavior; not data-verified per restraint.

Data-membership (specific signup, specific account creation, specific model access, specific data accessed) was not tested per restraint ethic.

---

## Discovery method

- **Initial surfacing**: Stage-0 dork-map of 1,629 verified Shodan dorks scoped to `hostname:.edu`. The host hit the Open WebUI title-and-port dork.
- **Verification**: direct `/api/config` probe; WHOIS netblock confirm.
- **Cross-validation**: post-fix visorbishop run produced the same `signup-open` classification independently.

---

## Source artifacts

- Workspace: `~/recon/edu-llm-infra-2026-05-19/`
- Initial probe: `arsenal-out/critical-openwebui-results.json` (UMD-CP section)
- WHOIS: `arsenal-out/whois-5-confirmed.txt`
- Shodan host data: `arsenal-out/shodan-host-umd.txt`
- visorbishop wave-1 revalidation: `stage2-wave2/arsenal/visorbishop-wave1-revalidate.json`
- aimap full report: `aimap-results.json`
