---
type: methodology
insight: 38
title: LLM gateway model-impersonation fraud: proxies advertise premium model IDs while serving cheaper local models. `/v1/model/info` is the authoritative discriminator.
---

# Insight #38. LLM gateway model-impersonation fraud

_Source: LiteLLM operator-attribution deep-dive, 2026-05-19. Host `69.30.237.88:4000` (Nocix US, cert SAN `swatweb.org`) advertises Anthropic model IDs (`claude-sonnet-4-20250514`, `claude-sonnet-4-6`, `claude-haiku-4-5-20251001`, `claude-opus-4-6`) via `/v1/models`. `/v1/model/info` reveals the actual backend: `api_base: http://127.0.0.1:3100/v1`, actual model `openai/gemma-4-26b`. The proxy serves local Gemma 4-26b under Claude-branded model IDs. Cost is set to 0 (no upstream billing). Customers paying for "Claude API access" receive Gemma responses._

## The rule

LLM gateway proxies (LiteLLM, Portkey, custom wrappers) expose two distinct surfaces that often disagree:

- **`/v1/models`**: public model list. Shows the model IDs the operator chooses to advertise. Operator-controlled string.
- **`/v1/model/info`** (LiteLLM-specific): internal config showing `litellm_params.api_base` and the actual upstream provider + model name. Authoritative upstream attribution.

**A discrepancy between the two is the fraud signature.** The operator advertises one model class to callers; the proxy serves a different (typically cheaper or local) model. Possible motives:

1. **Model-impersonation reselling**: sell "Claude API access" at Anthropic-tier prices; serve Gemma / Llama / GLM locally; pocket the margin.
2. **Cost arbitrage**: sell at premium-tier pricing; route to a cheaper provider; pocket the spread.
3. **Compliance / sanctions evasion**: route around a provider the operator does not have access to (e.g., serving "OpenAI" from a region OpenAI does not authorize).
4. **Data exfiltration**: the proxy logs everything passed through it; the rebranded "premium model" gives the operator a way to collect prompts + responses without callers realizing the data path.

## Empirical basis (LiteLLM operator-attribution deep-dive, 2026-05-19)

6 LiteLLM hosts deep-read via `/v1/model/info`. Four operator classes emerged:

| Class | Hosts | Discriminator |
|---|---|---|
| Legit paid-API proxy | 104.199.185.105 (GCP, Gemini + Anthropic Opus 4-6 + 4-7-1), 168.144.45.16 (DigitalOcean US, Vertex project `gen-lang-client-0317998519` + Anthropic + Grok + Moonshot), 78.47.217.225 (Positive Future / `arango-api.positive-future.com`) | `api_base` matches advertised vendor (e.g. `generativelanguage.googleapis.com` for Gemini, `api.anthropic.com` for Claude) |
| Multi-provider wrapper / SaaS brand | 109.123.227.237 (`-brain` product: `coding-brain` -> `gemini/gemini-2.5-flash`), 78.47.217.225 (same Positive Future brand) | Wrapper model name maps to a legit upstream; operator runs a commercial brand layer |
| **Model-impersonation fraud** | **69.30.237.88 (swatweb.org)** | `/v1/models` advertises Claude IDs; `/v1/model/info` shows `api_base: http://127.0.0.1:3100/v1` with `openai/gemma-4-26b`. Cost = 0. Local Gemma served under Claude model names. |
| Circuitous routing aggregator | 154.36.180.105 (Mauritius IP) | `api_base` points to `43.167.216.195:38762` Tencent Cloud SG. Circuitous geography (Mauritius → Tencent SG → likely further upstream). Rebranding aggregator or stacked-proxy chain. |

## Diagnostic signals

A LiteLLM host is suspected of model-impersonation if:

1. `/v1/models` advertises premium-tier model IDs (Anthropic Claude family, OpenAI GPT-4+, Google Gemini Pro / Vertex)
2. `/v1/model/info` returns `api_base` that does NOT match the vendor's canonical API endpoints
3. Local `api_base` (`127.0.0.1`, `localhost`, internal IPs, internal Docker network addresses) confirms the model is being served locally rather than proxied to the upstream vendor
4. `cost_per_*` fields set to `0` or `None`. No upstream billing means no actual upstream API call.
5. The actual local model is from a cheaper / smaller family (Gemma, Llama, Qwen) but presented under premium-tier model IDs

A LiteLLM host is suspected of cost-arbitrage routing if:

6. `api_base` points to a different vendor than the advertised model name (e.g. Anthropic model ID routed to a Gemini-compatible upstream)
7. The intermediate upstream is itself a proxy (e.g. another LiteLLM, an OpenRouter, a regional reseller)

## Procedural rules this insight generates

1. **`/v1/model/info` is the authoritative discriminator.** Surveys that only probe `/v1/models` miss the fraud class entirely. Always probe `/v1/model/info` and compare advertised model IDs against `litellm_params` to detect mismatches.

2. **Fraud-class disclosure routing differs from other classes.** Legit-proxy + paid-API exposures route to the cloud provider and operator. Model-impersonation fraud routes to the IMPERSONATED VENDOR's brand-protection team (Anthropic for Claude impersonation, OpenAI for GPT impersonation, Google for Gemini). The cloud provider hosts the fraud but doesn't own the fraud claim.

3. **Anthropic brand-impersonation has legal weight.** Anthropic's terms of service explicitly prohibit reselling under their brand without authorization, and trademark / passing-off law applies. Disclosure to Anthropic's `security@anthropic.com` or trademark / brand-protection contact is the right primary path.

4. **Methodology gap**: prior LLM-gateway surveys (LiteLLM-cloud 2026-05-04, safety/guardrail 2026-05-19) probed only `/v1/models` and `/v1/chat/completions`. Re-survey those corpora through `/v1/model/info` to estimate the fraud-class population.

5. **The `cost = 0` signal is the load-bearing tell.** A LiteLLM proxy claiming to serve `claude-opus-4-6` with `input_cost_per_token: 0` is either (a) lying about the model (impersonation fraud), (b) lying about the cost (negligent ops), or (c) genuinely serving a free-tier model under a paid-tier name (fraud). All three cases warrant the fraud-class disclosure path.

## Relationship to prior insights

- **Insight #11 (source code is authoritative; bug reports are framing)**: same epistemology. The operator-authored `/v1/models` response is FRAMING (the operator's claim about what they serve); the `/v1/model/info` response is the AUTHORITATIVE record. Prefer authority.
- **Insight #2 (single-template auth-off propagates at population scale)**: applies here as the leak mechanism. LiteLLM's `/v1/model/info` is auth-off by default in many deployments; the fraud-class hosts are caught precisely because their config is browsable.
- **Insight #33 (side-channel attribution via registry catalog)**: same family at a different layer. The LiteLLM internal config is the operator-authored side channel that authoritatively attributes the proxy's actual upstream + business model.

## Open questions

- **What fraction of unauth LiteLLM hosts at population scale are model-impersonation fraud?** This insight is sourced from a 6-host deep-dive; the broader corpus (~523 LiteLLM hosts in the 2026-05-19 survey) has not been re-probed through `/v1/model/info`. Estimate: 5-15% based on the 1-of-6 sample.
- **Are there model-impersonation fraud sites BEHIND auth?** This survey only catches operators who leave `/v1/model/info` exposed. Operators who gate it might still be running the same fraud against their authenticated customers; that population is invisible to passive recon.
- **What is the operator's customer-side pitch?** swatweb.org's web presence (if any) likely advertises "Claude API access" at competitive prices. A WHOIS + content scrape of swatweb.org would identify whether the fraud has customer-facing marketing.

## See also

- `case-studies/commercial/safety-guardrail-population-survey-2026-05-19.md`: parent survey identifying 28 LiteLLM UNAUTH_FUNCTIONAL hosts
- `case-studies/commercial/llm-gateways-cloud-survey-2026-05.md`: prior 1,857-host LiteLLM-class survey (which did NOT probe /v1/model/info)
- `methodology/insight-11-source-code-is-authority.md`: the epistemology this insight applies
- `methodology/insight-33-side-channel-attribution-via-registry-catalog.md`: same family at the registry-content layer
