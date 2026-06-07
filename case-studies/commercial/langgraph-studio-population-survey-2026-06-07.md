---
type: case-study
category: cat-lg
platform: LangGraph Studio
date: 2026-06-07
findings: 10/11 desktop-mode misdeployments (90.9%)
status: verified
toolchain: manual probe
---

# LangGraph Studio Population Survey — Local Dev Tool Misdeployed to Public AWS at 90.9%

_NuClide Research · 2026-06-07_

---

## Executive Summary

LangGraph Studio (`github.com/langchain-ai/langgraph`) is **LangChain's local-development debugger / visualizer for LangGraph applications**. It is designed to run on `localhost:2024` during development, with `desktop` auth-type meaning **no authentication is required because access is assumed to be from the same machine as the developer**. LangChain ships separate production tooling — **LangGraph Cloud** (paid SaaS) and **LangGraph Platform** (self-hosted enterprise) — which use proper auth.

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7004, S7068, S7070, S7075, T5904, T5919
- **733 (AI Risk & Ethics Specialist):** K7051, T5868
- **overlap (Common AI KSATs (all 5 roles)):** K108, K1158, K6311, K6900, K6935, K7003

<!-- ksat-tag:auto-generated:end -->

20 instances Shodan-indexed on `http.title:"LangGraph Studio"`. **All 20 are deployed on cloud infrastructure (16 AWS EC2 us-east-1 + eu-central-1, 1 GCP).** 11 reachable. Of the 11:

- **10 (90.9%) are running LangGraph Studio in `desktop` auth-type mode on public IPs** — the local-development default exposed to the internet
- **1 (9.1%) is properly auth-gated** — returns HTTP 403 "User is not authorized to perform this action" on all paths

This is a **maintainer-side correct default applied incorrectly by operators**. The auth-permissive default is appropriate for Studio's intended use (localhost dev). The misdeployment is the operator decision to expose Studio publicly.

The finding is therefore class-distinct from prior 2026-06-06/07 surveys: **the maintainer is not the source of the auth-permissive default**; the operator-side deployment misuse is.

---

## Discovery — `ls-init` runtime config disclosure

LangGraph Studio's React SPA embeds its runtime configuration in a `<script id="ls-init">` tag as base64-encoded JSON. Unauthenticated GET of `/` returns the SPA HTML which contains this config. Decoding the 10 misdeployed instances reveals a **uniform configuration**:

```json
{
  "VITE_STUDIO_LOCAL_GRAPH_URL": "",
  "VITE_SELF_HOSTED_POLLY_ENABLED": "false",
  "VITE_BACKEND_AUTH_TYPE": "desktop",
  "VITE_SINGLE_ORIGIN_ENABLED": "1",
  "VITE_SELF_HOSTED_CLIO_ENABLED": "false",
  "VITE_HOST_ENABLED": "0"
}
```

Each field's semantic:
- `VITE_BACKEND_AUTH_TYPE: "desktop"` — single-user mode, no auth
- `VITE_SINGLE_ORIGIN_ENABLED: "1"` — same-origin deployment (no separate API host)
- `VITE_HOST_ENABLED: "0"` — not a hosted offering
- `VITE_SELF_HOSTED_POLLY_ENABLED: "false"` — Polly (LangSmith tracing forwarder) disabled
- `VITE_SELF_HOSTED_CLIO_ENABLED: "false"` — Clio (LangSmith analytics) disabled

The uniformity across 10 hosts confirms they are all deployed from the **same `npm run dev` / `langgraph dev` template** without modification of the `BACKEND_AUTH_TYPE` env var.

---

## Population Results

| Metric | Count | Rate |
|---|---|---|
| Shodan-indexed | 20 | — |
| Reachable | 11 | 55% of indexed |
| **`desktop` auth-type (misdeployed)** | **10** | **90.9% of reachable** |
| Properly auth-gated (LangGraph Platform) | 1 | 9.1% of reachable |

### Misdeployed hosts (sample)

| Host | PTR | Region |
|---|---|---|
| `34.169.138.175:80` | `175.138.169.34.bc.googleusercontent.com` | GCP us-west |
| `3.229.173.235:80` | `ec2-3-229-173-235.compute-1.amazonaws.com` | AWS us-east-1 |
| `34.199.14.192:443` | `ec2-34-199-14-192.compute-1.amazonaws.com` | AWS us-east-1 |
| `34.202.90.34:443` | `ec2-34-202-90-34.compute-1.amazonaws.com` | AWS us-east-1 |
| `52.58.61.39:443` | `ec2-52-58-61-39.eu-central-1.compute.amazonaws.com` | AWS eu-central-1 |
| `35.157.123.49:443` | `ec2-35-157-123-49.eu-central-1.compute.amazonaws.com` | AWS eu-central-1 |
| `52.29.92.166:443` | `ec2-52-29-92-166.eu-central-1.compute.amazonaws.com` | AWS eu-central-1 |
| `18.197.202.96:443` | `ec2-18-197-202-96.eu-central-1.compute.amazonaws.com` | AWS eu-central-1 |
| `100.50.192.205:80` | `ec2-100-50-192-205.compute-1.amazonaws.com` | AWS us-east-1 |
| `100.24.236.47:443` | `ec2-100-24-236-47.compute-1.amazonaws.com` | AWS us-east-1 |

### Properly auth-gated

| Host | Response | Interpretation |
|---|---|---|
| `100.30.28.199:80` | `HTTP 403 {"User is not authorized to perform this action"}` | LangGraph Platform with auth layer |

---

## Why This Finding is Class-Distinct from Prior Surveys

For Langfuse / RAGFlow / Phoenix / OpenHands / LobeChat, the maintainer's deployment template ships with auth-permissive defaults for **production use**. The default is the responsibility of the upstream maintainer.

For LangGraph Studio, the maintainer's intent is clear: Studio is **local-development tooling**. The `desktop` auth-type default is correct for `localhost:2024`. Operators have made a deployment decision to expose Studio to public infrastructure.

**Responsibility model split:**

| Survey | Auth-permissive default is | Remediation responsibility |
|---|---|---|
| Langfuse / RAGFlow / Phoenix / OpenHands / LobeChat | Upstream maintainer default | Upstream maintainer (change default) |
| LangGraph Studio | Operator deployment misuse | Operator (don't expose Studio publicly) |

LangChain's documentation is explicit: Studio is for development; LangGraph Cloud or LangGraph Platform is for production. The 10 misdeployed instances reflect operator-side workflow misalignment, not a LangChain product-design failure.

---

## Maintainer-Culture Hypothesis — Refined Form Confirmed

The Bisheng survey (2026-06-06) refined Insight #76 from jurisdiction-based to **maintainer-culture-based**. LangGraph reinforces this:

| Maintainer | Product | Default | Open rate |
|---|---|---|---|
| LangChain | **LangGraph Cloud / Platform** (production) | auth-required | (not surveyed; assumption) |
| LangChain | **LangGraph Studio** (development) | desktop / no auth (CORRECT for localhost) | 90.9% misdeployed publicly |

LangChain ships **different defaults for different use cases**. The Studio default is operator-deployment-misuse-vulnerable, not maintainer-default-vulnerable. This is **the correct maintainer-culture pattern**: tailor defaults to use case, document the deployment boundary clearly.

The 1 properly auth-gated instance (`100.30.28.199`) is the **counter-example demonstrating LangChain operators DO use the production tooling when intended for production**. So the maintainer culture is sound; the failure mode is operator workflow misalignment.

---

## Comparison with OpenHands (same-category)

OpenHands and LangGraph are both autonomous-agent platforms (LLM06 surface):

| Platform | Upstream | Studio/Dev mode default | Production mode default | Misdeployment rate |
|---|---|---|---|---|
| OpenHands | All-Hands-AI | auth-permissive | auth-permissive | n/a (maintainer-default-vulnerable) |
| **LangGraph** | **LangChain** | **auth-permissive (CORRECT for localhost)** | **auth-required** | **90.9% public misdeployment** |

OpenHands has the maintainer-default failure mode. LangGraph has the operator-deployment failure mode. **Both produce the same operational outcome: public unauth autonomous-agent platforms.** But the responsibility model and remediation pathway are completely different:

- OpenHands: upstream PR to change default
- LangGraph Studio: operator education / better deployment guides / refuse to start when `BACKEND_AUTH_TYPE=desktop` and `0.0.0.0` binding is detected

---

## Disclosure Pipeline

| Finding | Tier | Recommended action |
|---|---|---|
| 10 misdeployed LangGraph Studio instances | HIGH-OPERATOR | Per-operator notification: "your Studio dev tool is public" |
| LangChain upstream | UPSTREAM | Suggest defensive default: refuse to start when `BACKEND_AUTH_TYPE=desktop` AND `--host` is anything other than `localhost` / `127.0.0.1` |
| Documentation | UPSTREAM-DOCS | Strengthen LangChain docs to explicitly call out the Studio-public-IP misdeployment risk |

---

## Toolchain Provenance

```
Step 0:    shodan download 'http.title:"LangGraph Studio"' (20 records)
Step 0c:   Direct urllib probe to all 20 hosts
Step 1b:   /ok endpoint + /threads/search probe
Step 3v:   Base64-decoded ls-init runtime config — VITE_BACKEND_AUTH_TYPE
           field is the auth-state discriminator
Step 12b:  This document
```

**No herald config built for LangGraph Studio at this time.** The body_contains marker would be the literal `"VITE_BACKEND_AUTH_TYPE":"desktop"` after base64 decoding — herald does not currently have a base64-decode mode. Population is small (20) and the finding class is operator-misdeployment, not maintainer-default. Adding a herald config would be marginal value vs the complexity of decoding ls-init payloads at probe time.

---

## Research-Program Contribution

LangGraph Studio adds a **new finding class to the program**: **operator-misdeployment-of-correctly-defaulted dev-tool**. This is class-distinct from the maintainer-default-auth-permissive findings dominant in the 2026-06-06/07 surveys.

The maintainer-culture hypothesis is **strengthened** because LangChain demonstrates the correct pattern: different defaults for different use cases, with clear documentation of the deployment boundary. The 9.1% properly-auth-gated rate shows operators **can** use production tooling when intended — the 90.9% who misdeployed Studio represent a separate workflow problem.

**Methodology insight:** the next round of cohort surveys should distinguish maintainer-default failures from operator-deployment failures. The remediation pathways are different, and conflating them under one finding class obscures the actual remediation lever.
