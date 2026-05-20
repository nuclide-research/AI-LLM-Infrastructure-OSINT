---
type: methodology
insight_number: 39
title: Pooled-account upstream proxy as attribution-laundering layer; one paid API account fans out to N unauthorized end-customers through a middle-tier relay
date: 2026-05-19
tags:
  - methodology
  - attribution
  - llmjacking
  - resale-fraud
  - asymmetric-tos-enforcement
related_research:
  - case-studies/commercial/safety-guardrail-population-survey-2026-05-19.md
  - case-studies/commercial/claude-relay-chinese-reseller-2026-05-19.md
source: case-studies/commercial/claude-relay-chinese-reseller-2026-05-19.md
---

# Insight #39. Pooled-account upstream proxy as attribution-laundering layer

_Source: Safety / guardrail + LiteLLM UNAUTH_FUNCTIONAL deep-dive, 2026-05-19. Surfaced when probing the upstream `api_base` of the Mauritius LiteLLM proxy at 154.36.180.105:4000 revealed `43.167.216.195:38762`, which on probe returned the `claude-relay-service` stats schema. The schema exposed `accounts: 6` Anthropic accounts pooled across `successRequests: 53,655` Claude calls. Cross-correlation with the Wei-Shaw OSS substrate (github.com/Wei-Shaw/claude-relay-service, 11.8K stars) confirmed a structural pattern: paid LLM accounts pooled at an upstream tier, fan-out via mid-tier customer proxies, attribution flattened to a single account from the vendor's side._

## The rule

A subset of LLM-resale fraud operations route through a **three-tier architecture** that flattens attribution from the upstream vendor's perspective:

```
Tier 1 (vendor):  Anthropic / OpenAI / Google
Tier 2 (relay):   Pooled-account upstream proxy (e.g., claude-relay-service)
                  - Holds N paid API / Pro / Max subscriptions
                  - Round-robins requests across the pool
                  - Reports as N distinct account-holders to the vendor
Tier 3 (storefront): Customer-facing proxies (LiteLLM, custom UIs, SDK wrappers)
                     - Holds the relay URL as api_base
                     - Resells the upstream as their own service to end-customers
Tier 4 (end-customer): Pays the storefront; believes they call the vendor directly
```

**From the vendor's side, only Tier 1 -> Tier 2 is visible.** Vendor telemetry shows N accounts making M API calls. The vendor cannot see that each of those N accounts is fanning out to thousands of end-customers through Tier 3.

**From the end-customer's side, only Tier 3 -> Tier 4 is visible.** The customer believes they have purchased direct vendor access. The model IDs match (`claude-sonnet-4-6`, `gpt-4o`, `gemini-2.5-pro`); the SDK CORS headers match (the relay copies the vendor's official SDK CORS config verbatim); the responses are forwarded transparently. The customer never knows they are at Tier 4.

**The attribution-laundering result**: when the vendor bans an account at Tier 2 for terms-of-service violation, the Tier 3 storefront silently rotates to a different account in the pool. The end-customer experiences no service interruption. The vendor's enforcement signal does not propagate to the customer. The ban is invisible.

## Distinct from prior LLMjacking insights

This is NOT the same as **Insight #23-bis (LLMjacking proxy colocation)**, which observed commercial proxy SaaS + unauthenticated open LLM on the same host. That pattern co-locates the resale and the model; this pattern routes the resale through a paid vendor account at an upstream tier. It is a paid-account fraud, not a stolen-compute fraud.

This is also NOT the same as **Insight #38 (litellm-model-impersonation-fraud)**, where the proxy lies about the model (advertising `claude-*` but serving local Gemma). The pooled-account pattern serves the actual claimed model; the lie is about who is paying for it.

The structural distinction matters because the disclosure target differs:
- LLMjacking-colocation -> hosting provider abuse desk (the local LLM is on their infrastructure)
- Model-impersonation -> end-customer (they are being charged for Claude and served Gemma)
- **Pooled-account attribution-laundering -> the vendor whose accounts are pooled** (Anthropic, OpenAI, etc.). The end-customer is getting the model they paid for; the vendor is bearing the cost.

## Empirical basis

### Claude Relay (this survey, 2026-05-19)

Six publicly-indexed `claude-relay-service` instances expose pool stats unauthenticated on GET `/` and GET `/health`. The endpoint is OSS-default-shipping behavior, not an operator misconfiguration. The schema returns `accounts: N`, `availableAccounts: M`, `successRequests`, `totalTokens`, and uptime.

Aggregate visible population (six hosts):
- **32 pooled Anthropic accounts** (range 1 to 8 per host)
- **~13.92 billion tokens** of Claude inference served
- **~430,000 successful Anthropic API requests**
- **187-day max uptime** for the most-active relay
- All six hosting concentrated on Chinese commercial cloud (Tencent SG / Tencent Beijing / YunNan LanDui)

### Wei-Shaw substrate (github.com/Wei-Shaw)

- `claude-relay-service`: 11,798 stars, MIT, 304 tagged releases, Chinese-only docs, marketed as `拼车` (carpool) account-sharing
- `sub2api`: Go rewrite, 21,800 stars, 8,105 Shodan-indexed deployments. Suggests the visible Claude Relay v1 population is the long tail (operators who left `/health` public); the actual deployed base is two orders of magnitude larger
- Commercial brand `pincc.ai`: slogan "Claude Code Max 20X, saves 60%+"; the OSS author monetizes the tooling rather than running the pools, displacing legal-risk surface to downstream operators

### Downstream Tier 3 confirmation

The Mauritius LiteLLM at `154.36.180.105:4000` was empirically confirmed to use `43.167.216.195:38762` (one of the six Tier 2 relays) as its `api_base`. The LiteLLM advertised model IDs `claude-sonnet-4-6`, `claude-sonnet-4.6`, `claude-haiku-4-5-20251001`, `claude-haiku-4.5` to its own customers. The chain Tier 4 -> Tier 3 LiteLLM -> Tier 2 Claude Relay -> Tier 1 Anthropic was reconstructed from primary-source artifacts (the LiteLLM's own `/v1/model/info` response).

A wider sweep of the Aceville Pte Ltd (Tencent SG) netblock surfaced 30 additional LiteLLM proxies disjoint from the six visible relays, all in the same operator-class cohort. One advertises in Chinese branding ("飞经理使用指南"). The architecture pattern repeats.

### Operator awareness of vendor enforcement

GitHub issues on the `claude-relay-service` repo confirm operators understand the activity is in TOS violation and discuss countermeasures openly:
- Issue #587: "Heavy account bans these past few days, any good solutions?"
- Issue #861: feature request for automatic ban-detection + pool-rotation
- Issue #673: silent fallback to direct connection flagged as a ban-risk for the pool
- Issue #1000: vendor overage-throttle (HTTP 429 "Extra usage required") misclassified as rate-limiting, causing the pool to auto-lock the upstream account

None of the issues reference Anthropic's TOS or abuse program by name. The bans are discussed operationally, never legally. The operator class treats vendor enforcement as a routine operational hazard, not a deterrent.

## Diagnostic signals

A host is operating Tier 2 (pooled-account upstream) when:

1. **GET / or GET /health returns a JSON object with `accounts: N`, `availableAccounts: M`, and `totalTokens`** as top-level fields. This schema is unique to `claude-relay-service` and not produced by other Anthropic-compat proxies surveyed
2. **The CORS response includes the full Stainless SDK header set** (`x-stainless-os`, `x-stainless-lang`, `x-stainless-package-version`, `x-stainless-runtime`, `x-stainless-runtime-version`, `x-stainless-arch`) verbatim copied from the official Anthropic SDK config. This is intentional, designed to make the relay transparent to clients using the official SDK
3. **The hostname or banner includes 拼车 (carpool), claude relay, claude code mirror, or pincc-class branding**
4. **The host is in a Chinese commercial cloud netblock** (Tencent Cloud, YunNan LanDui, Aceville Pte Ltd) AND advertises Anthropic-compat API
5. **An upstream `api_base` is named by a downstream LiteLLM, OpenWebUI, or custom proxy in the SAME netblock**, especially on a non-standard port (the relay's `api_base` is typically the relay's internal LB port, e.g., `:38762`)

## Procedural rules this insight generates

1. **Always probe the upstream of a customer-facing Tier 3 proxy.** When a LiteLLM or custom proxy exposes `/v1/model/info`, `/v1/models`, or any endpoint revealing `api_base`, treat that upstream as a separate target. The upstream may be Tier 2 attribution-laundering infrastructure, not a vendor endpoint.

2. **The vendor is the disclosure target for Tier 2 findings.** End-customer disclosure is not appropriate when the customer is receiving the model they paid for; the harm flows upstream to the vendor whose accounts are pooled. Disclose to vendor Trust & Safety / abuse, not to the customer or the hosting provider.

3. **Severity tiering for pooled-account findings**:
   - One relay, low account count (1-2), low token throughput = MEDIUM (single-operator resale, limited blast radius)
   - One relay, high account count (5+) or high token throughput (>1B tokens) = HIGH (substantial vendor cost displacement)
   - Multiple relays + same OSS substrate + cross-operator coordination via GitHub issues = HIGH-CRITICAL (organized resale ecosystem, ban-resistance built in as a feature)

4. **Reproducibility dorks for population-scale findings should be vendor-shareable.** The vendor's response capacity scales with their ability to independently reproduce. For Claude Relay: `http.html:"availableAccounts" http.html:"thirdPartyMaxConcurrent"` is the precise dork; `http.html:"sub2api"` widens to the Go-rewrite class.

5. **Re-probe schedule after vendor disclosure.** Vendor enforcement is observable from the outside: re-probe the relay's `/health` 14, 30, and 60 days after disclosure and measure the delta on `accounts`, `totalTokens` rate, and uptime. Disclosure efficacy is empirically measurable here in a way it is not for most security disclosures.

## Relationship to prior insights

- **Insight #23-bis (LLMjacking proxy colocation)**: same family of LLM-resale fraud, different topology. #23-bis co-locates stolen-compute LLM + commercial proxy on one host. #39 separates paid-account substrate (Tier 2) from customer-facing storefront (Tier 3) across hosts.
- **Insight #37 (asymmetric auth gating)**: the relay's pool stats endpoint is the signature of asymmetric gating at the OSS level. The auth-gated `/admin` is the operator-facing surface; `/` and `/health` are the machine-facing stats. The OSS ships with the stats path open by default; operators do not lock it because it is the load-balancer health check.
- **Insight #38 (litellm-model-impersonation-fraud)**: a different lie about the same call. Impersonation claims to be Claude and serves Gemma; pooled-account claims to be a direct vendor channel and is a fan-out. The two patterns coexist in the same ecosystem (the same Aceville netblock contains both).
- **Insight #6 (conjunctive matchers required)**: the relay-detection dork is conjunctive (`availableAccounts` + `thirdPartyMaxConcurrent`); either token alone produces false positives against unrelated AI-stack instances.

## Open questions

- **What fraction of the Tier 3 storefront base is downstream from Tier 2 attribution-launderers vs. operating as standalone resellers?** A survey of LiteLLM proxies whose `/v1/model/info` exposes `api_base` would map the dependency graph.
- **Do other vendors face the same architecture?** OpenAI-compat and Gemini-compat proxy infrastructure (sub2api advertises multi-vendor support) likely runs the same pattern. The visible Claude Relay v1 population may be only the most-explicit case.
- **What is the disclosure-response rate from vendor Trust & Safety on this class?** The Anthropic disclosure of 2026-05-19 is the first such case in the NuClide ledger; re-probe schedule will measure the response.
- **Is the OSS author legally liable, or does selling-the-tool retain plausible deniability?** Wei-Shaw operates pincc.ai as a commercial brand while disclaiming responsibility for downstream operators. The legal-risk surface is structured to land on the customers, not the substrate provider.

## See also

- `case-studies/commercial/claude-relay-chinese-reseller-2026-05-19.md`: source case study
- `case-studies/commercial/safety-guardrail-population-survey-2026-05-19.md`: the LiteLLM UNAUTH_FUNCTIONAL upstream-trace that surfaced the Tier 2 pivot
- `insight-23-discovery-channel-coverage-is-multiplicative.md`: the discovery-channel mechanics that surfaced this population
- `insight-37-asymmetric-auth-gating-dashboard-vs-api.md`: the OSS-default open-stats-endpoint pattern that exposes Tier 2
- `insight-38-litellm-model-impersonation-fraud.md`: adjacent fraud pattern in the same operator ecosystem
