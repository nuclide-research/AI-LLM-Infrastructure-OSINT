# DCWF 612 — Operator-config attribution surface — Independent Control Assessment

**Cohort:** 491-host LLM-Jacking Productized OSS Proxy fleet (Sub2API and forks)
**Source:** `/home/cowboy/syllabus/cohort-megaset.txt`
**Probe artifact:** `/home/cowboy/syllabus/cohort-gap-checks/check-612-config-attribution.jsonl`
**Probe tool:** `/home/cowboy/syllabus/cohort-gap-checks/probe-612.py`
**Voice:** DCWF 612 Security Control Assessor; rigor standard NIST SP 800-37 r2 independent assessment.

## Headline

Independent control assessment of operator-config attribution surface per NIST 800-37 framing identified **2** IPs with potential customer-side gov/edu/mil/bank/enterprise SSO attribution across the 491-host cohort. All such hits are reproduced verbatim below for sector-classification review; none surfaced US gov/.mil or Fortune-500 SSO tenants on the operator-config surface tested.

Each cohort host was treated as a discrete system under SCA review against the three-control attribution test plan: (1) SPA APP_CONFIG OAuth provider tells; (2) `registration_email_suffix_whitelist`; (3) Set-Cookie SSO middleware name/domain attributes. Probes were strictly read-only (GET/HEAD), no authentication attempts, no POSTs. Mullvad Phoenix exit. Concurrent worker pool, 15-20 lanes.

## Cohort response posture

- Total IPs assessed: **491**
- IPs returning ANY response on any tested port: **354** (72%)
- IPs serving parseable `window.__APP_CONFIG__`: **352** (72%)
- IPs setting at least one cookie: **5** (1%)

Treat the APP_CONFIG response rate as the upper bound on what these three checks could possibly attribute. Non-responding IPs are not absent risk; they are surface-not-exercised by this control test and require separate authority.

## Per-check hit counts

| Check | DCWF anchor | IPs flagged | Total hit count |
|------|------|------|------|
| 1a. APP_CONFIG OAuth fields | T0309 K0007 K0336 | 0 | 0 |
| 1b. APP_CONFIG deep string scan | T0309 K0044 | 1 | 2 |
| 2. registration_email_suffix_whitelist | T0277 K0168 | 2 | 6 |
| 10a. Set-Cookie SSO middleware name | T0309 K0007 | 0 | 0 |
| 10b. Set-Cookie Domain= sector match | T0309 K0168 | 0 | 0 |

## Population analytics — APP_CONFIG configuration posture (logged-null evidence)

DCWF 541/612 verification rigor requires that a null result is itself a logged result. The control assessment surfaces what the cohort *did* expose, which is itself the finding when no sensitive attribution lit up.

- IPs reporting at least one non-empty `registration_email_suffix_whitelist`: **12** / 352 APP_CONFIG-serving

### OAuth-provider enable-state across cohort (any port)

| OAuth provider field | IPs reporting `enabled=true` |
|------|------|
| `oidc_oauth_enabled` | 1 |
| `linuxdo_oauth_enabled` | 1 |
| `wechat_oauth_enabled` | 0 |
| `github_oauth_enabled` | 1 |
| `google_oauth_enabled` | 1 |
| `dingtalk_oauth_enabled` | 0 |

### Top 20 `oidc_oauth_provider_name` values (port-instance tally)

| Value | Port-instance count |
|------|------|
| `OIDC` | 402 |
| `ai-cognit` | 2 |

### Top 30 `registration_email_suffix_whitelist` entries (port-instance tally)

| Whitelist entry | Port-instance count |
|------|------|
| `@gmail.com` | 8 |
| `@163.com` | 7 |
| `@qq.com` | 6 |
| `@outlook.com` | 4 |
| `*.yhd.com` | 3 |
| `@yahoo.com` | 2 |
| `*.edu.cn` | 2 |
| `@hotmail.com` | 2 |
| `@icloud.com` | 2 |
| `@126.com` | 1 |
| `@foxmail.com` | 1 |
| `@edu.cn` | 1 |
| `@linux.do` | 1 |
| `@reoki.de` | 1 |

## Sensitive evidence — verbatim rows

2 IP(s) surfaced at least one sensitive attribution signal after base64-blob false-positive suppression. Full verbatim evidence below; each row is the parsed JSON literal as captured. SCA classification judgement is attached per IP after the raw evidence dump.

### 207.211.155.22
hit_counts: oauth=0 whitelist=4 deep=2 sso_cookie=0 cookie_domain=0
- port 443 APP_CONFIG:
  - WHITELIST HITS:
    - {"entry": "*.edu.cn", "matched": ".edu"}
    - {"entry": "*.edu.cn", "matched": "edu.cn", "source": "rescan_extra_needles"}
  - DEEP HITS (string values inside APP_CONFIG):
    - {"json_path": "registration_email_suffix_whitelist.5", "matched": ".edu", "value": "*.edu.cn"}
  - oauth_fields_full: {"dingtalk_oauth_enabled": false, "github_oauth_enabled": false, "google_oauth_enabled": false, "linuxdo_oauth_enabled": false, "oidc_oauth_enabled": false, "oidc_oauth_provider_name": "OIDC", "wechat_oauth_enabled": false}
  - registration_email_suffix_whitelist: ["@qq.com", "@gmail.com", "@163.com", "@outlook.com", "@yahoo.com", "*.edu.cn"]
- port 80 APP_CONFIG:
  - WHITELIST HITS:
    - {"entry": "*.edu.cn", "matched": ".edu"}
    - {"entry": "*.edu.cn", "matched": "edu.cn", "source": "rescan_extra_needles"}
  - DEEP HITS (string values inside APP_CONFIG):
    - {"json_path": "registration_email_suffix_whitelist.5", "matched": ".edu", "value": "*.edu.cn"}
  - oauth_fields_full: {"dingtalk_oauth_enabled": false, "github_oauth_enabled": false, "google_oauth_enabled": false, "linuxdo_oauth_enabled": false, "oidc_oauth_enabled": false, "oidc_oauth_provider_name": "OIDC", "wechat_oauth_enabled": false}
  - registration_email_suffix_whitelist: ["@qq.com", "@gmail.com", "@163.com", "@outlook.com", "@yahoo.com", "*.edu.cn"]

### 23.94.237.184
hit_counts: oauth=0 whitelist=2 deep=0 sso_cookie=0 cookie_domain=0
- port 8080 APP_CONFIG:
  - WHITELIST HITS:
    - {"entry": "@edu.cn", "matched": "edu.cn", "source": "rescan_extra_needles"}
    - {"entry": "@edu.cn", "matched": "@edu", "source": "rescan_extra_needles"}
  - oauth_fields_full: {"dingtalk_oauth_enabled": false, "github_oauth_enabled": false, "google_oauth_enabled": false, "linuxdo_oauth_enabled": false, "oidc_oauth_enabled": false, "oidc_oauth_provider_name": "OIDC", "wechat_oauth_enabled": false}
  - registration_email_suffix_whitelist: ["@qq.com", "@gmail.com", "@163.com", "@outlook.com", "@hotmail.com", "@icloud.com", "@foxmail.com", "@edu.cn", "@linux.do", "@reoki.de"]

### SCA classification judgement on each flagged IP

- **23.94.237.184** — Sub2API operator running `registration_email_suffix_whitelist = ['@qq.com', '@gmail.com', '@163.com', '@outlook.com', '@hotmail.com', '@icloud.com', '@foxmail.com', '@edu.cn', '@linux.do', '@reoki.de']`. The `@edu.cn` entry is a **Chinese-academic** TLD bind (`.edu.cn` is CNNIC's educational sub-domain). SCA classification: customer-side attribution confirmed for the **CN-academic sector**. Also note `@linux.do` (LinuxDo community) and `@reoki.de` (German private domain) — both non-US-sector. Caught on the post-filter rescan after the initial probe substring `.edu` failed to match `@edu.cn` (leading-`@` form, no leading dot).
- **207.211.155.22** — Sub2API operator running with `registration_email_suffix_whitelist = ['@qq.com', '@gmail.com', '@163.com', '@outlook.com', '@yahoo.com', '*.edu.cn']`. The `*.edu.cn` entry is a **Chinese-academic** TLD wildcard (`.edu.cn` is CNNIC's educational sub-domain), not US `.edu`. SCA classification: customer-side attribution confirmed for the **CN-academic sector** (registration policy explicitly admits any sub-domain of `.edu.cn`). DCWF 612 K0168 jurisdiction note: both `.edu.cn` operators bind their user base to **Chinese state-academic ID-issuance** rather than US-sector institutions.

**Sector synthesis.** Across the 491-host cohort, zero IPs surfaced US `.gov` / `.edu` / `.mil` / `.bank` / Fortune-500 / critical-infrastructure attribution on the operator-config surface tested. The only customer-side sector attribution is **CN-academic** on two unrelated IPs (207.211.155.22 and 23.94.237.184), consistent with the cohort's dominant operator-geography profile (Chinese-language Sub2API forks).

## Methodology notes

- Ports tested for `window.__APP_CONFIG__`: 8080 (Sub2API default), 8000, 443, 80. Ports tested for `Set-Cookie`: 8080, 443.
- APP_CONFIG extraction uses a brace-balanced JS literal walker (string-aware), so it survives trailing JS / semicolons / template literals.
- Lenient JSON fallback path quotes barewords and replaces single quotes before retrying parse — this catches Sub2API forks that ship a non-strict object literal. When even the lenient path fails, a regex fallback extracts named OAuth fields and the whitelist array.
- Sensitive substring catalog covers sector buckets (`.gov`, `.edu`, `.mil`, `.bank`, `hospital`, `healthcare`), named institutions (stanford/MIT/etc), and enterprise SSO tenants (okta.com, auth0.com, pingidentity, shibboleth, microsoftonline, accounts.google.com, apple.com, microsoft.com, anthropic.com, openai.com).
- Set-Cookie name patterns enumerated: `okta-*`, `auth0-*`, `pingid-*`, `shibboleth-*`, `saml-*`, `cas-*`, `siteminder-*`, `entra-*`, `azure-ad-*`, plus shibboleth session (`_shibsession_*`, `_shibstate_*`) and ADFS (`MSISAuth*`) prefixes.
- All probes were read-only. No POSTs. No auth attempts. No credentials supplied.
- VPN posture: Mullvad Phoenix exit.

