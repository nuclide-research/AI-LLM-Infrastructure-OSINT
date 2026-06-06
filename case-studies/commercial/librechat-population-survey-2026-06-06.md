---
type: case-study
category: cat-lc
platform: LibreChat
date: 2026-06-06
findings: 412 REGISTRATION_OPEN of 1,565 reachable (26.3%)
status: verified
toolchain: herald v0.1.2
---

# LibreChat Population Survey — 412/1,565 Open Registration (26.3%)

_NuClide Research · 2026-06-06_

---

## Executive Summary

LibreChat (github.com/danny-avila/LibreChat) is an open-source ChatGPT-alternative chat interface — supports multiple LLM providers, plugins, multimodal, multi-tenant via shared deployments. 3,153 Shodan-indexed instances on `http.title:"LibreChat"`. 2,000 downloaded; 1,565 responded.

**Of 1,565 reachable instances, 412 (26.3%) expose `registrationEnabled: true` to the public internet.**

LibreChat's `registrationEnabled` flag is exposed unauthenticated via `GET /api/config` alongside the application's `appTitle`, `serverDomain`, and `buildInfo.branch`. When the flag is `true`, any internet user can register an account on the operator's deployment. The data layer (chat history, configured models, API keys) is gated behind the registration, but registration alone provides a foothold into a personally-branded LLM deployment running on the operator's infrastructure.

**The 26.3% rate is the first measured case in the 2026 NuClide survey program of a platform in the middle of correction.** Langfuse / RAGFlow / Phoenix (87-89%) represent the uncorrected cohort. Open WebUI (11.8%) and AnythingLLM (0%) represent the corrected cohort. LibreChat sits between, with **strong within-platform version-cohort evidence of the correction in progress**.

Notable findings: 4 legal-AI deployments, 1 mental-health AI (Santepair.fr), University of California Berkeley, a 20-instance "Capitol AI Chat Agent" fleet on AWS.

---

## Methodology

| Stage | Action | Tool |
|---|---|---|
| Stage 0 | Shodan harvest `http.title:"LibreChat"` | shodan CLI (2,000 of 3,153 records) |
| Stage 0c | TCP/HTTP liveness | herald |
| Stage 1b | Auth-posture probe `/api/config` field `registrationEnabled == true` | herald librechat platform config |
| Stage 1b' | Config disclosure capture (appTitle, version, serverDomain) | herald extract |
| Stage 3v | Source-code verification: `registrationEnabled` is set from `ALLOW_REGISTRATION` env var in LibreChat `api/server/services/AppService.js` | manual review |
| Stage 12b | Dataset enrichment via Shodan record join (country, ASN) | Python + Shodan CSV join |

---

## Population Results

| Metric | Count | Rate |
|---|---|---|
| Shodan-indexed | 3,153 | — |
| Downloaded for sweep | 2,000 | — |
| Reachable with valid LibreChat config | 1,565 | 78.3% of downloaded |
| `registrationEnabled: true` (REGISTRATION_OPEN) | 412 | 26.3% of reachable |
| Config disclosure (any LibreChat response) | 1,565 | All reachable |

---

## Version Cohort Analysis — Within-Platform Correction in Action

LibreChat's `buildInfo.branch` field is the version signal. Three cohorts observed:

| Version | REGISTRATION_OPEN | Total | Rate |
|---|---:|---:|---:|
| v0.8.x (tagged stable) | 3 | 29 | **10.3%** |
| `main` (dev branch) | 36 | 110 | 32.7% |
| (no buildInfo — older versions) | 373 | 1,426 | 26.2% |

The **v0.8.x cohort at 10.3%** is dramatically lower than both the older population (26.2%) and the `main` development branch (32.7%). This is **within-platform evidence of Insight #40 (auth-on-default strengthens across OSS generations) in real time** — the LibreChat team has tightened defaults in their tagged stable releases.

The development-branch `main` rate (32.7%) is consistent with the older population, suggesting the correction is in tagged releases but has not propagated to all development paths. Operators deploying directly from `main` (Docker `:latest` builds in some configurations) inherit the older default.

This is the **first 2026-06-06 survey to show a clean within-platform cohort correction.** Open WebUI showed correction across major versions (v0.4 → v0.5+); LibreChat is showing it across the development-vs-tagged-release boundary at the same point in time.

---

## Geographic Distribution

| Country | REGISTRATION_OPEN hosts |
|---|---:|
| United States | 140 |
| Germany | 59 |
| Singapore | 35 |
| France | 21 |
| China | 20 |
| United Kingdom | 16 |
| Japan | 15 |
| Australia | 13 |
| Netherlands | 11 |
| Finland | 8 |

Unlike RAGFlow (CN-heavy at 69%) and Langfuse (CN/US even), LibreChat's population is **US-dominant (34%) with strong EU presence (Germany, France, UK, Netherlands, Finland combined = 115, 28%)**. Consistent with LibreChat's English-language community and Discord-centric development.

---

## Notable Institutional Findings

### University of California, Berkeley — `169.229.156.181:3080` (HIGH)

UCB campus IP block. LibreChat instance with `registrationEnabled: true`. The instance uses the default `LibreChat` appTitle — suggests a research-group or course deployment that was not customized after install.

Disclosure recipient: `security@berkeley.edu`

### Santepair.fr — `51.77.213.247:443` (HIGH-SENSITIVE)

Title: "Santepair.fr - ChatBot IA Bien-être et santé psychique" (Wellbeing and mental health AI chatbot). French mental health AI deployment with open registration. Mental health is a sensitive data class under GDPR Article 9 (special categories of personal data).

Disclosure recipient: CNIL (Commission Nationale de l'Informatique et des Libertés) coordination, or direct to Santepair.fr DPO.

### Legal AI Deployments (4 distinct operators) — HIGH-PRIVILEGE

LibreChat instances explicitly branded as legal-AI services, all with open registration:

| IP:Port | Title | Likely operator |
|---|---|---|
| `144.126.133.109:3080` | "TruslerLegal AI Assistant" | Trusler Legal (US firm) |
| `18.207.2.243:80` | "LegalMatch AI" | LegalMatch (consumer legal directory) |
| `20.77.81.170:443` | "Legal-Knowledge-Graph-Chatbot" | Unknown |
| `34.75.202.219:80` | "Atticus: Legal Assistant" | Unknown ("Atticus" branding) |

Legal AI deployments with open registration risk:
- Attorney-client privileged conversations leaking across user boundaries depending on workspace isolation
- Operator account takeover if the first-user-admin pattern applies (LibreChat's pattern: first registered user gets admin role by default)
- Prompt content used as training/eval data being readable by any registered user

Disclosure path: vendor-mediated to LibreChat maintainer (danny-avila) with the recommendation to surface registration-state warning UI when a deployment is branded for sensitive sectors.

### Capitol AI Chat Agent Fleet — 20 AWS Instances (PATTERN)

Twenty distinct AWS IPs (across us-east-1, us-east-2, eu-west, ap-southeast) all running LibreChat with `appTitle: "Capitol AI Chat Agent"` and `registrationEnabled: true`. Consistent IP distribution across AWS regions suggests a single operator deploying a fleet — either a Capitol AI commercial product offering or a multi-tenant SaaS reseller.

```
3.13.42.244       18.143.96.158     50.17.46.127      3.214.248.175
13.228.31.196     18.169.146.161    51.24.30.245      3.232.23.192
18.190.182.205    3.140.90.49       54.162.236.213    3.248.138.181
44.193.187.49     3.18.147.161      54.164.58.252     63.33.237.33
98.87.219.108     3.23.37.53        100.55.210.190    108.131.230.229
```

If a single operator: a 20-instance LibreChat fleet with open registration on AWS. If a multi-tenant SaaS: every client of "Capitol AI Chat Agent" inherits open-registration default.

Disclosure path: trademark + WHOIS-search on "Capitol AI" to identify operator; vendor-mediated to LibreChat upstream if pattern reflects a popular deployment guide that needs hardening.

### Other distinctive deployments

- "PetersChat" (Hetzner, DE)
- "Smollan Nexus" (Smollan, retail intelligence firm)
- "I C P Fertilizer : AI Private Chat" (industrial)
- "Eigenentwickelte KI umgebung" (DE; "self-developed AI environment")
- "SONNCO KI" (DE)
- "Spingarn", "Atticus", "ZaraAI", "Qonaev AI", "Talk To Replica", "TTG.AI" — distinctive brandings indicating production commercial deployments

---

## Risk Severity Classification

Why 26.3% open registration on LibreChat is more concerning than 88.9% on Langfuse despite the lower rate:

| Factor | Langfuse | LibreChat |
|---|---|---|
| Post-registration access | Workspace-gated traces only | **Full LLM chat interface; operator's API keys consumed** |
| Default admin promotion | No | **First-user admin (LibreChat pattern)** |
| Sensitive deployments | Observability of dev/staging | **Production-branded user-facing apps including legal/medical** |
| Cost exposure | $0 direct (storage) | **Token-cost exposure on Anthropic/OpenAI/Google keys** |

The **LLM10 Unbounded Consumption** class applies to every open-registration LibreChat instance: a registered user invokes the operator's configured LLM, billed to the operator. With LibreChat's multi-provider support (OpenAI, Anthropic, Google, Azure, Bedrock, custom OpenAI-compatible), the cost surface is large.

---

## Disclosure Pipeline

| Finding | Tier | Recommended action |
|---|---|---|
| University of California, Berkeley | HIGH | security@berkeley.edu |
| Santepair.fr (mental health AI, FR) | HIGH | CNIL coordination + DPO contact |
| Trusler Legal AI | HIGH | trademark identification → direct |
| LegalMatch AI | HIGH | LegalMatch corp security contact |
| Atticus / Legal-Knowledge-Graph (2) | HIGH-UNK | Vendor-mediated via LibreChat |
| Capitol AI Chat Agent fleet (20 hosts) | HIGH-FLEET | WHOIS → operator identification |
| 412 commercial / individual hosts | UPSTREAM | LibreChat (danny-avila): change `ALLOW_REGISTRATION` default to `false` in tagged release; surface registration-state warning UI |

The upstream remediation is most efficient: LibreChat's v0.8.x cohort already shows 10.3% — proving the tagged-release default has tightened. Recommendation: backport the v0.8.x default to the `main` branch with a deprecation notice on the older default. Document the security implications of registration-open more prominently in the README and Docker compose templates.

---

## Remediation (per-operator)

```bash
# LibreChat .env or docker-compose environment:
ALLOW_REGISTRATION=false        # Close public registration
ALLOW_EMAIL_LOGIN=false         # Optional: SSO-only
ALLOW_SOCIAL_LOGIN=true         # If using Google/GitHub/etc auth
```

Verify:
```bash
curl http://IP:PORT/api/config | python3 -c "import sys,json; print(json.load(sys.stdin)['registrationEnabled'])"
# Expected: false
```

---

## Toolchain Provenance

```
Step 0:    shodan download 'http.title:"LibreChat"' (2,000 of 3,153 records)
Step 0c:   IP extraction → ip-port.txt (2,000 unique)
Step 1b:   herald -platform librechat < ip-port.txt
           - probe id registration_open: /api/config field registrationEnabled == true
           - probe id config_disc: /api/config field appTitle exists
Step 3v:   Manual cohort validation against LibreChat v0.8.x release notes
           and main branch source (api/server/services/AppService.js)
Step 12b:  This document
```

Tool: **herald** v0.1.2 (`github.com/nuclide-research/herald`). LibreChat platform config added with two probes.

---

## Research-Program Contribution

LibreChat is the **first 2026-06-06 survey to show within-platform version-cohort correction at the time of measurement.** The 10.3% rate on v0.8.x vs 32.7% on `main` and 26.2% on older versions is direct evidence for Insight #40 (auth-on-default strengthens under disclosure pressure — even when the pressure is internal-quality-driven rather than external-disclosure-driven).

This is the **falsification-test case** for the strong form of Insight #76. If Insight #76 said "auth-permissive defaults are the cohort norm, period," LibreChat at 10.3% on v0.8.x would refute it. But Insight #76's weaker form ("auth-permissive defaults are the cohort norm; rates can be moved by surveys+disclosure") is *supported* by LibreChat: the within-platform correction shows the rate is movable, and LibreChat's maintainer corrected without external pressure.

**Updated four-platform corpus (2026-06-06):**

| Platform | Rate | Cohort interpretation |
|---|---:|---|
| Langfuse | 88.9% | Uncorrected default |
| RAGFlow | 87.2% | Uncorrected default (different maintainer + jurisdiction) |
| Phoenix | 74.5% (PROJ) / 61.8% (USR) | Uncorrected default + data-layer-direct |
| Flowise | 68.7% (chatflow API) | Uncorrected default |
| **LibreChat (overall)** | **26.3%** | **Partial correction — tagged-release default tightened** |
| Open WebUI | 11.8% | Corrected via disclosure pressure |
| Dify | 0.9% | Different cohort (LLM-app-builder) |
| AnythingLLM | 0% | Population hardened |

**The LibreChat v0.8.x = 10.3% data point is the strongest evidence to date that internal-quality-driven correction works and reaches Open-WebUI-equivalent rates.** This adds nuance to the disclosure-pressure clause of Insight #76: external disclosure may not be required if the maintainer team has internal security review.
