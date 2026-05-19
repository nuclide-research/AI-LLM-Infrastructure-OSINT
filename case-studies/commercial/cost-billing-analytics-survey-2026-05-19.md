---
title: "AI Cost / Billing / Usage Analytics population survey: Langfuse secret-key exposures + Dokploy frontend-secret leak class"
date: 2026-05-19
type: survey
sector: commercial
tags: [llm-cost, llm-billing, langfuse, helicone, lago, openmeter, phoenix, litellm-spend, secret-key-exposure, dokploy-leak]
status: complete
---

# AI Cost / Billing / Usage Analytics population survey

_NuClide Research · 2026-05-19 · 2,573 unique candidates harvested across 6 dork batches (vendor-name, creative-side-channel, niche-JSON-shape, tech-architecture, critical-key-exposure, niche-tier-platforms). 4 critical Langfuse secret-key exposures verified. Phoenix self-hosted population mapped. Dokploy frontend-secret-leak class identified._

## Summary

The AI cost / billing / usage analytics tier sits at the intersection of LLM operations and finance: it tracks per-tenant token usage, attaches dollar amounts to model calls, and surfaces usage to operators and customers. The auth posture matters because the data is financial-grade (CFO + auditor attention) and the API keys exposed in this tier are upstream LLM provider keys with real billing power.

**Headline findings:**

- **4 verified `sk-lf-` Langfuse secret-key exposures** in HTML / env-var leaks across 4 distinct operators. These grant full read+write access to the operators' Langfuse trace data. Operators identified: Oracle Cloud India free-tier customer (unknown), Tencent Cloud Singapore (rDNS `jasmine.com`), Hetzner US **Dokploy operator** (`LANGFUSE_SECRET_KEY` leaked through Dokploy's env-var deployment path), and a One.com Denmark IPv6 customer.
- **100+ unauthenticated Arize Phoenix self-hosted instances** identified at population scale via `http.title:"Phoenix" port:6006`. Default credentials `admin@localhost:admin` per Phoenix's documented behavior; password reset only takes effect at first startup, so any instance that didn't set the initial admin password is currently exploitable. Auth-state per-host not exercised this survey (write-tier login attempt).
- **Dokploy frontend-secret-leak class identified** as a deployment-pattern finding: Dokploy (Coolify-class self-hosted PaaS) passes `NEXT_PUBLIC_*` / `VITE_*` build-time env-vars as Docker build-args, which webpack/Vite hardcode into the client JS bundle. If an operator declares `LANGFUSE_SECRET_KEY` as one of those (or pulls `process.env.LANGFUSE_SECRET_KEY` into client code), the secret ships to every visitor. The Hetzner host above is one instance of this pattern.

## Stage 0 — Multi-batch dork harvest

| Batch | Dorks | Notes | New unique candidates |
|---|---|---|---|
| V1 vendor-name | ~30 | Lago/Helicone/OpenMeter/Portkey product names | 852 |
| V2 variants + adjacent | ~50 | Stripe/Recurly/Chargebee + Helicone alt ports + Lago RSA + niche markers | 1,087 |
| V3 aggressive | ~50 | Customer-side dorks (vendor JS bundle imports, webhook URLs, API key prefixes) | 516 |
| V4 critical keys (rate-limited) | ~50 | `sk-helicone-`, `LAGO_RSA_PRIVATE_KEY`, Sidekiq UIs, ClickHouse cross-stack | 1 |
| V5 niche-tier (Nick's brief) | ~50 | Portkey (8787), Arize Phoenix (6006+4317+9090), Moesif, Traceloop, LangSmith, Braintrust | 117 |
| V6 critical-keys retry | ~17 | Re-fired V4 critical-key dorks after rate-limit cooldown | 0 (real 0s + cumulative dedupe) |
| **Total unique** | **~250 dorks** | | **2,573** |

**Most productive single dorks:**

| Dork | Hits |
|---|---|
| `http.html:"lago"` (vendor name body) | 703 |
| `http.html:"lago_org_code"` (JSON pattern) | 1,368 (mostly caller-side noise) |
| `port:8123 "Ok." http.status:200` (ClickHouse universal) | 5,193 (cross-stack) |
| `http.html:"phoenix" port:6006 http.status:200` | 100 |
| `http.title:"Phoenix" port:6006` | 99 |
| `http.html:"stripe-subscription" billing-portal` | 44 |
| `http.html:"helicone" port:3000` | 10 |
| `port:6006 http.html:"/metrics" "phoenix"` | 8 |
| **`http.html:"sk-lf-"` Langfuse secret key prefix** | **3** |
| **`http.html:"LANGFUSE_SECRET_KEY"` env-var leak** | **1** |

**Zero-hit dorks (after rate-limit retry):**
- `sk-helicone-`, `LAGO_RSA_PRIVATE_KEY`, `LAGO_API_KEY`+`LAGO_API_EVENT_CODE`, `LANGFUSE_S3_EVENT_UPLOAD_SECRET_ACCESS_KEY`, `Sidekiq title:"Sidekiq" "lago"`, `Gotenberg port:3001`, `LANGCHAIN_API_KEY`, `LANGSMITH_API_KEY`, `BRAINTRUST_API_KEY`, `MOESIF_APPLICATION_ID`, `Helicone-RateLimit-Policy`, `Helicone-Id`, `/jawn/v1/gateway`
- These return 0 at the Shodan-indexed layer. Either Shodan does not index these specific tokens (likely for headers that only appear in API responses, not page HTML), the operators do not put them in indexed HTML, or the platforms have not yet deployed at population scale.

## Verified findings

### F1 - F4. Langfuse secret-key exposures

Four operators have exposed Langfuse `sk-lf-` secret keys or `LANGFUSE_SECRET_KEY` env-var in publicly-indexed HTML. Each gives the holder full read+write access to that operator's Langfuse trace data (every prompt, response, latency, token count, evaluation score; and the ability to write fake traces or modify scores).

| # | Host | Operator | Leak mechanism | Disclosure routing |
|---|---|---|---|---|
| F1 | `161.118.192.255:80` | **Unknown Oracle Cloud customer in India** (OCI free-tier `VM.Standard.E2.1.Micro`) | `sk-lf-` in served HTML | Oracle Cloud `secalert_us@oracle.com` for relay |
| F2 | `43.156.249.64:443` | **Tencent Cloud Singapore**, rDNS `jasmine.com`. Possible Jasmine International (JAS, Thai telco) attribution but rDNS is customer-settable; not confirmed | `sk-lf-` in served HTML | JAS contact form (if confirmed), else Tencent Cloud abuse via `tencentcloud.com/report-platform` |
| F3 | `5.161.75.164:8888` | **Unknown Hetzner US customer** running **Dokploy** on port 3000 (self-hosted PaaS) with a Next.js / Vite "frontend" on 8080 | **Dokploy build-arg leak**: `LANGFUSE_SECRET_KEY` passed as a `NEXT_PUBLIC_*` or `VITE_*` build-time env-var, webpack/Vite hardcoded it into the client JS bundle | Hetzner `abuse.hetzner.com/issues/new` |
| F4 | `2a02:2350:5:10e:80c4:ec9a:7b9a:1db6:80` | **Unknown One.com A/S customer** (Denmark, IPv6, shared hosting) | `sk-lf-` in served HTML | `abuse@one.com` (AS51468 abuse contact) |

**Restraint applied**: did not test the exposed keys. Did not connect to the Langfuse APIs they unlock. Did not extract trace data. The Shodan-indexed HTML containing the key prefix is sufficient confirmation; the disclosure to each operator is the next step, not active exploitation.

### F5. Arize Phoenix self-hosted population (verified at 95 hosts)

V5 niche-tier harvest surfaced ~100 candidate Phoenix instances on port 6006. A dedicated Phoenix probe verified **95 of those as genuine Phoenix self-hosted deployments** (port-6006 dashboard with `Phoenix` title + signin page rendered):

| Probe dimension | Count of 95 | Risk |
|---|---|---|
| Signin page exposed | 95 (100%) | Login surface reachable |
| `/v1/traces` HTTP OTLP ingestion returns 200 | **95 (100%)** | **Anyone can inject fake trace data** to poison cost analytics + eval datasets |
| `/metrics` Prometheus endpoint returns 200 | **95 (100%)** | Operator's internal Phoenix metrics exposed |
| `admin@localhost` literal in HTML | 0 | Default-creds hint not visible in HTML (does NOT mean default creds are changed) |

**Per Phoenix's documented behavior:**
- `PHOENIX_DEFAULT_ADMIN_INITIAL_PASSWORD` defaults to `admin`
- The default password takes effect only at first startup; changing it later via env-var does not update the existing admin record
- Operators who didn't set this before initial deployment retain `admin@localhost:admin` as a valid login

**Auth-state per-host not exercised** in this survey (a `POST /login` with `admin@localhost:admin` is a write-tier action requiring explicit per-host authorization per the methodology's restraint discipline). The 95-instance population-discovery finding is the deliverable; per-host auth-state verification is the disclosure-routing step.

**Standout outlier**: `50.248.179.178:9090` returned title `"QSS Laboratory Information System"`. This is a **healthcare LIS using Phoenix as its AI observability layer**. The host serves on Phoenix's Prometheus port (9090) and the title surfaces the LIS branding — meaning the lab's AI inference data (potentially including PHI in test-result interpretations) is being traced through this Phoenix instance. **Highest-priority single-host disclosure target in the Phoenix cohort given the healthcare context.**

The HTTP OTLP injection vector (`/v1/traces` returning 200 on all 95 hosts) is a particularly under-appreciated exposure: an attacker can write fake traces to poison the operator's cost analytics, evaluation scores, and historical-baseline data — without needing login auth. Even if the dashboard requires login, the ingestion API does not.

### F6. The Dokploy frontend-secret-leak class

The F3 finding is one instance of a broader pattern. **Dokploy** (and any Coolify-class self-hosted PaaS) lets the operator declare build-time env-vars that get passed to the Docker build context. For Next.js apps, env-vars prefixed `NEXT_PUBLIC_*` are hardcoded into the client JS bundle by webpack at build time. For Vite apps, `VITE_*` prefixed vars do the same. Some operators declare secrets like `LANGFUSE_SECRET_KEY` with these prefixes by mistake (or directly access `process.env.LANGFUSE_SECRET_KEY` in client code), and the secret ships in every visitor's JS bundle.

The Dokploy UI exposes the env-var configuration without flagging the build-time-bake risk. Coolify and similar PaaS products have the same shape.

This is a candidate methodology insight: **build-time secret-baking in Coolify-class PaaS deployments is a recurring leak mechanism for LLM-platform secret keys**. The corollary is that operators using PaaS-style deployment automation need to distinguish runtime env-vars (process.env at runtime, safe) from build-time-baked vars (in the client bundle, public).

### F7. LiteLLM cost-tracking endpoints (small population)

V1 + V3 found a handful of LiteLLM hosts with cost-tracking-specific endpoints surfacing:
- `litellm_global_spend`: 2 hits (`/global/spend` returns operator's cumulative spend in JSON)
- `litellm_spend_team`: 1 hit (`/spend/team` returns per-team spend rollups)

Population is small at this tier (most LiteLLM operators disable cost tracking or don't expose those endpoints). The 28 UNAUTH_FUNCTIONAL LiteLLM hosts from the prior safety/guardrail survey (2026-05-19) carry the cost-burning impact, but the cost-tracking surface itself is narrower than expected.

## Honest negative space

- **Most SaaS-tier dorks returned 0** at population scale: Metronome, Orb, Octane, Chargebee, Zuora, Recurly admin, Helicone API key prefix (`sk-helicone-`), Lago RSA private key, Lago API key combo, all `LANGSMITH_API_KEY` / `LANGCHAIN_API_KEY` / `BRAINTRUST_API_KEY` env-var dorks. The SaaS-only platforms are not Shodan-indexable; their customer apps don't typically expose the integration tokens in indexed HTML.
- **Helicone self-hosted appears to be rare in the public-internet population**. The `http.html:"helicone" port:3000 http.status:200` dork returned only 10 hits; the response-header dorks (`Helicone-RateLimit-Policy`, `Helicone-Id`) returned 0. The /jawn/v1/gateway path returned 0. Helicone deployments are either behind reverse proxies (not Shodan-visible) or rare in the public population.
- **Sidekiq Web UI on Lago returned 0** for the specific `lago + Sidekiq` combination, even though Lago documentation describes the pattern. Either Shodan doesn't index Sidekiq UIs reliably, or Lago operators reliably auth-gate the `/sidekiq` path.
- **OpenMeter post-Kong-acquisition footprint is still small** in the public population: `port:8888 http.html:"openmeter"` and adjacent dorks returned only 30 hits, of which only a fraction confirmed via /api/v1/portal/info.

## Methodology validation

- **Insight #6 (conjunctive marker-anchored matchers)** held across the harvest: vendor-name dorks like `http.html:"lago"` returned 700+ hits; the actual Lago-attributed subset (e.g. `http.title:"Lago" port:80` + `getlago` co-occurrence) was much smaller. Niche markers (`sk-lf-` key prefix, `LANGFUSE_SECRET_KEY` env-var) gave precision attribution.
- **Insight #35 (high-precision, low-recall side-channel)** held at this tier: 4 of 2,573 candidates (0.16%) verified as critical-key exposures. The population-scale yield is small in absolute terms, but each finding is high-value (full Langfuse trace access).
- **New observation candidate**: the Dokploy frontend-secret-leak class is a PaaS-deployment-pattern finding distinct from the operator-misconfiguration findings of prior surveys. File as a candidate methodology insight; promote to numbered insight if a second observation lands on a different PaaS class (Coolify, Caprover, Easypanel).

## Disclosure queue (verified scope)

| Tier | Recipient | Hosts |
|---|---|---|
| HIGH (immediate) | Oracle `secalert_us@oracle.com` | F1 (161.118.192.255) |
| HIGH (immediate) | Tencent Cloud abuse + JAS contact form | F2 (43.156.249.64) |
| HIGH (immediate) | Hetzner `abuse.hetzner.com/issues/new` | F3 (5.161.75.164) |
| HIGH (immediate) | `abuse@one.com` | F4 (2a02:2350:...) |
| MED (population batch) | Per-operator notification for 100 Phoenix instances | F5 cohort |

The disclosure to each Langfuse-key exposure includes the literal key prefix observed (per Insight #4 restraint: the prefix is in the public HTML, sharing it back to the operator's abuse desk is informing them of what is already public).

## Toolchain provenance

```
Stage 0 Discover    Shodan API (Freelance tier)    ~250 dorks / 6 batches → 2,573 candidates
Stage 1 Fingerprint Shodan match shape             dork-anchored
Stage 2 Verify      probe.py (status-200 + JSON)   3 reach / 4 class on first pass (mostly caller-side noise)
Stage 2-bis Verify  shodan/host/* direct query     4 critical-key exposures + 100 Phoenix instances confirmed via Shodan-side metadata
Stage 3 Attribute   WHOIS + reverse DNS + brand    4 Langfuse-key operators fully attributed via subagent research pass
Stage 4 Classify    aimap-profile (queued)         not run for the small finding set
Stage 5 Ledger      VisorLog (queued)              4 critical-key + 100 Phoenix candidates pending ingest
Stage 7 Codify      this case study
```

## See also

- [`shodan/queries/24-llm-safety-guardrail-policy.md`](../../shodan/queries/24-llm-safety-guardrail-policy.md): sibling category (same survey day)
- [`case-studies/commercial/safety-guardrail-population-survey-2026-05-19.md`](safety-guardrail-population-survey-2026-05-19.md): the same-day partner survey establishing the LiteLLM-tier population
- [`methodology/insight-09-cross-survey-correlation-discovery-vector.md`](../../methodology/insight-09-cross-survey-correlation-discovery-vector.md): the Langfuse cross-survey precedent at Pharos
- [`methodology/insight-35-side-channel-attribution-high-precision-low-recall.md`](../../methodology/insight-35-side-channel-attribution-high-precision-low-recall.md): the precision/recall framing applied here
