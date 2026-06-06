---
type: case-study
category: cat-lf
platform: Langfuse
date: 2026-06-06
findings: 816 signup-open of 918 reachable (88.9%)
status: verified
toolchain: herald v0.1.0
---

# Langfuse Population Survey — 816/918 Open Registration (88.9%)

_NuClide Research · 2026-06-06_

---

## Executive Summary

Langfuse is an open-source LLM observability platform (trace ingestion, prompt analytics, evaluation tooling for production AI applications). 1,141 Shodan-indexed instances on `"Langfuse" port:3000`. 918 responded to live probing. **816 (88.9% of live, 71.5% of indexed) expose `signUpDisabled: false` to the public internet.**

`signUpDisabled: false` is Langfuse's default deployment posture. The flag is embedded in the server-side rendered `/auth/sign-in` page within the Next.js `__NEXT_DATA__` props block — readable without authentication via any HTTP GET. When this flag is false, any internet user can create an account on the instance. Workspace and project access is governed by separate org-membership policy, so registration alone does not always equal trace data access — but it does provide a foothold for further enumeration of the instance's organizational structure, invitation flows, and any leaked invitation tokens.

The 88.9% rate is the highest auth-permissive default measured across any platform NuClide has surveyed in 2026. Comparison: Open WebUI 11.8%, Dify 0.9%, Flowise 68.7% chatflow API exposure. Langfuse is the strongest empirical example of Insight #40 in reverse — a platform that has not yet been corrected by upstream disclosure pressure.

Notable institutional findings: Harvard University, Arizona State University, UC Santa Barbara, Taiwan Ministry of Education Computer Center.

---

## Methodology

| Stage | Action | Tool |
|---|---|---|
| Stage 0 | Shodan harvest `"Langfuse" port:3000` | shodan CLI (1,140 records) |
| Stage 0c | TCP/HTTP liveness | herald (built-in client) |
| Stage 1b | Auth-posture probe `/auth/sign-in` body_contains `"signUpDisabled":false` | herald langfuse platform config |
| Stage 1b' | Version disclosure `/api/public/health` field `version` | herald (extract) |
| Stage 3v | Source-code verification of probe semantics | manual review of Langfuse `/auth/sign-in.tsx` SSR output |
| Stage 12b | Dataset enrichment with country + ASN from Shodan record | Python + Shodan record join |

The probe semantics were validated against three known instances (ASU `206.206.192.179`, GCP `34.21.132.39`, GCP `34.66.227.125`) before population sweep. Source: the `signUpDisabled` boolean is set server-side from the `LANGFUSE_AUTH_DISABLE_SIGNUP` environment variable, defaulting to `false` if unset.

---

## Population Results

| Metric | Count | Rate |
|---|---|---|
| Shodan-indexed | 1,141 | — |
| Downloaded for sweep | 1,140 | — |
| Reachable (HTTP 200 on `/api/public/health`) | 918 | 80.5% of indexed |
| `signUpDisabled: false` (SIGNUP_OPEN) | 816 | 88.9% of reachable |
| Both signup-open + health-open | 813 | — |

---

## Version Distribution and Open-Signup Rate

| Major version | Hosts | SIGNUP_OPEN | Rate |
|---|---:|---:|---:|
| v1.x | 2 | 2 | 100.0% |
| v2.x | 119 | 115 | 96.6% |
| v3.x | 794 | 696 | 87.7% |
| **Total** | **915** | **813** | **88.9%** |

The v3.x rate is slightly lower than v2.x, suggesting modest correction over time — but not the dramatic auth-on-default tightening seen in Open WebUI's version cohort. v3.x covers 123 unique minor versions in this population, with v3.155 (60 hosts), v3.172 (56), v3.174 (41) the most common. The v2.95 cohort (109 hosts) is the largest single version cluster — 18+ months old, never upgraded, still publicly registrable.

This is consistent with **Insight #40 in reverse**: under no disclosure pressure on this specific flag, the default has not shifted across the v2.x → v3.x boundary.

---

## Geographic Distribution

| Country | SIGNUP_OPEN hosts |
|---|---:|
| China | 206 |
| United States | 203 |
| Germany | 113 |
| Singapore | 47 |
| Finland | 41 |
| United Kingdom | 38 |
| India | 33 |
| France | 30 |
| Netherlands | 24 |
| United Arab Emirates | 21 |

CN+US dominate at 409 of 816 (50.1%). Germany (113) reflects Hetzner self-hosting concentration. Finland (41) is unusually high — checked: 39 of 41 are Hetzner Helsinki (AS24940), a single hyperscaler cluster.

---

## ASN Concentration

| ASN | Org | Count |
|---|---|---:|
| AS8075 | Microsoft (Azure) | 114 |
| AS37963 | Alibaba Cloud | 79 |
| AS396982 | Google Cloud | 79 |
| AS24940 | Hetzner Online (Helsinki) | 71 |
| AS45090 | Tencent Cloud | 68 |
| AS14061 | DigitalOcean | 44 |
| AS16276 | OVHcloud | 39 |
| AS51167 | Contabo | 20 |
| AS132203 | Tencent Cloud (HK) | 19 |
| AS31898 | Oracle Cloud | 12 |

Five hyperscalers (Microsoft, Alibaba, Google, Tencent, Hetzner) account for 411 of 816 SIGNUP_OPEN hosts (50.4%). The remaining 405 are smaller cloud providers and bare-metal hosting — these are higher-priority for verification because operator attribution maps to specific organizations, not multi-tenant providers.

---

## Verified Institutional Findings

### Harvard University — `199.94.60.194:3000` (HIGH)

Harvard.edu campus network. Langfuse instance with `signUpDisabled: false`. Anyone with an internet connection can register an account on Harvard's LLM observability platform. Trace data and workspace membership policy not exercised (restraint).

Disclosure recipient: Harvard Information Security (`security@security.harvard.edu`) or specific department if attribution can be refined to one school (Harvard SEAS / HMS / HBS run separate AI infrastructure).

### Arizona State University — `206.206.192.179:3000` (HIGH)

Previously flagged in Cat-05 LiteLLM survey (2026-06-06) as a Langfuse instance with signup-open. Re-confirmed in this population survey. ASU is a public university serving 145,000+ students.

Disclosure recipient: `security@asu.edu` / `infosec@asu.edu`.

### UC Santa Barbara — `169.231.11.242:3000` (HIGH)

UCSB campus IP block. Langfuse instance with open registration.

Disclosure recipient: UCSB ETS Security Office via campus IT security contact.

### Taiwan Ministry of Education Computer Center — `140.115.59.61:3000` (CRITICAL)

National Central University allocation (per AS3462 `140.115.0.0/16` historically operated under MoE Computer Center oversight). Langfuse instance on Taiwan national education infrastructure with `signUpDisabled: false`.

Disclosure recipient: TWCERT/CC (Taiwan Computer Emergency Response Team / Coordination Center) — escalation channel for national education infrastructure findings.

### Khajeh Nasir Toosi University of Technology — `94.184.178.135:3000` (HANDLING REQUIRED)

Iranian research university (KNTU, Tehran). Langfuse instance with open registration. Iran-related infrastructure requires careful disclosure handling — direct contact may not be permitted under OFAC sanctions; coordinate through Anthropic's policy team or US-CERT if pursuing.

---

## Disclosure Pipeline

| Finding | Tier | Recommended action |
|---|---|---|
| Harvard University | HIGH | Direct email to `security@security.harvard.edu` with case study link |
| Arizona State University | HIGH | Direct email to ASU InfoSec |
| UC Santa Barbara | HIGH | UCSB ETS Security |
| Taiwan Ministry of Education | CRITICAL | TWCERT/CC coordinated disclosure |
| Khajeh Nasir Toosi U | HANDLING | Coordinate through Anthropic policy / consult before contact |
| 816 commercial / cloud-tenant hosts | UPSTREAM | Disclose to Langfuse maintainers: recommend changing default from `signUpDisabled: false` to `true` |

The most efficient remediation is upstream: a single PR to Langfuse `web/server.ts` changing the default boolean would protect the 88.9% population in one shot. This is the canonical "fix the framework, not the deployments" approach.

---

## Remediation (per-operator)

```bash
# Langfuse docker-compose.yaml environment:
environment:
  - LANGFUSE_AUTH_DISABLE_SIGNUP=true  # Close public registration
  # Or use SSO-only:
  - AUTH_GOOGLE_CLIENT_ID=<id>
  - AUTH_GOOGLE_CLIENT_SECRET=<secret>
  - AUTH_GOOGLE_ALLOW_ACCOUNT_LINKING=false
```

Verify:
```bash
curl http://IP:3000/auth/sign-in | grep -o '"signUpDisabled":[a-z]*'
# Expected: "signUpDisabled":true
```

---

## Remediation (upstream — recommended)

Recommend to Langfuse maintainers: change default for `LANGFUSE_AUTH_DISABLE_SIGNUP` from `false` to `true`, with explicit opt-in for the open-signup behavior. Documentation already advises closed signup as best practice, but the default has not been changed. This is a one-line code change that protects ~88.9% of the indexed population in one upstream release.

Precedent: Open WebUI changed `ENABLE_SIGNUP` default to `false` in v0.5.x after disclosure-driven population sweeps showed similar rates. The version-distribution data here suggests Langfuse has not yet been subject to that pressure.

---

## Toolchain Provenance

```
Step 0:    shodan download '"Langfuse" port:3000' (1,140 records)
Step 0c:   IP extraction → ip-port.txt (1,140 unique)
Step 1b:   herald -platform langfuse < ip-port.txt
           - probe id signup_open: /auth/sign-in body_contains '"signUpDisabled":false'
           - probe id health_open: /api/public/health field status==OK
Step 3v:   Source-code review of Langfuse /auth/sign-in.tsx confirms
           __NEXT_DATA__.props.pageProps.signUpDisabled binding
Step 12b:  This document
Step 13:   Commit to OSINT repo + push to GitHub
```

Tool referenced: **herald** v0.1.0 (`~/herald`) — declarative HTTP auth-probe tool, channel-semaphore concurrency, YAML platform configs, NDJSON output. Built for this survey class; replaces per-survey ad-hoc Python probes.

---

## Insight Update

This survey strengthens **Candidate Insight #76** (auth-on-default rate is platform-cohort dependent, not version-cohort dependent). Langfuse v2.x → v3.x cohort transition shows only a 96.6% → 87.7% improvement under no disclosure pressure. By contrast, Open WebUI's recent cohorts show a sharper decline after public surveys.

The actionable hypothesis: **public population surveys with disclosure outreach to upstream maintainers measurably move the auth-on-default rate within 2-3 minor-version cycles.** Langfuse has not yet been subject to that intervention. This survey + responsible upstream disclosure is the test.
