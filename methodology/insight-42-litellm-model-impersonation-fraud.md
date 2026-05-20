---
type: methodology
insight_number: 42
title: "LLM gateway model-name mismatch: proxies advertise premium model IDs while serving different backends. /v1/model/info is the authoritative discriminator; the motive (convenience alias vs fraud) requires per-host verification."
---

# Insight #38. LLM gateway model-name mismatch

_Source: LiteLLM operator-attribution deep-dive, 2026-05-19. Host `69.30.237.88:4000` (Nocix US, cert SAN `swatweb.org`) advertises Anthropic model IDs (`claude-sonnet-4-20250514`, `claude-sonnet-4-6`, `claude-haiku-4-5-20251001`, `claude-opus-4-6`) via `/v1/models`. `/v1/model/info` reveals the actual backend: `api_base: http://127.0.0.1:3100/v1`, actual model `openai/gemma-4-26b`. Behavioral verification (3 POSTs with different model names): all return identical "I am a large language model, trained by Google" (Gemma's self-identification) with the same backend `system_fingerprint`._

**Initial framing of "fraud" was incorrect.** The operator is **Jo Lab** (`jolab.ai`, `jolab.app`), an academic biomedical AI research lab marketing "AI for Disease Prediction & Early Diagnosis." `swatweb.org` is their SWAT-web Sliding Window Association Test bioinformatics tool. No customer-facing "Claude API access" pitch exists. The model-name aliasing is most plausibly a convenience pattern: name local models with Claude-compatible IDs so client code written against Anthropic SDK Just Works without changing model strings.

**The configuration mismatch is verified. The motive is ambiguous and requires per-host verification.**

## The rule

LLM gateway proxies (LiteLLM, Portkey, custom wrappers) expose two distinct surfaces that often disagree:

- **`/v1/models`**: public model list. Shows the model IDs the operator chooses to advertise. Operator-controlled string.
- **`/v1/model/info`** (LiteLLM-specific): internal config showing `litellm_params.api_base` and the actual upstream provider + model name. Authoritative upstream attribution.

**A discrepancy between the two is a model-attribution-integrity issue.** The operator advertises one model class to callers; the proxy serves a different (typically cheaper or local) model. The MOTIVE for the mismatch is ambiguous and requires per-host investigation. Possible motives (not mutually exclusive):

1. **Convenience alias (Jo Lab case, verified)**: operator names local models with Anthropic-SDK-compatible IDs so client code defaults work without changing model strings. No fraud claim, no customer-facing API resale. The lab is the only user of the proxy.
2. **Model-impersonation reselling (requires customer-pitch evidence)**: operator sells "Claude API access" at Anthropic-tier prices; serves Gemma / Llama / GLM locally; pockets the margin. Verification requires finding the customer-facing site / pricing / receipts.
3. **Cost arbitrage**: operator sells at premium-tier pricing; routes to a cheaper provider; pockets the spread. Same evidence requirement as #2.
4. **Compliance / sanctions evasion**: routes around a provider the operator does not have access to (e.g., serving "OpenAI" from a region OpenAI does not authorize).
5. **Data exfiltration**: the proxy logs everything passed through it; the rebranded "premium model" gives the operator a way to collect prompts + responses without callers realizing the data path.
6. **Test/demo placeholder**: scaffolding for a future Claude integration that never landed; operator never updated the model IDs.

**Per `feedback_hard_proof_for_critical_label` and `feedback_100_percent_verified_tier_labels`**: do NOT label a host as "fraud" without verified customer-facing evidence (a website selling Claude access, a price page, a customer complaint, a receipt). The configuration mismatch alone is a **model-attribution-integrity** finding, not a fraud finding.

## Empirical basis (LiteLLM operator-attribution deep-dive, 2026-05-19)

6 LiteLLM hosts deep-read via `/v1/model/info`. Four operator classes emerged:

| Class | Hosts | Discriminator |
|---|---|---|
| Legit paid-API proxy | 104.199.185.105 (GCP, Gemini + Anthropic Opus 4-6 + 4-7-1), 168.144.45.16 (DigitalOcean US, Vertex project `gen-lang-client-0317998519` + Anthropic + Grok + Moonshot), 78.47.217.225 (Positive Future / `arango-api.positive-future.com`) | `api_base` matches advertised vendor (e.g. `generativelanguage.googleapis.com` for Gemini, `api.anthropic.com` for Claude) |
| Multi-provider wrapper / SaaS brand | 109.123.227.237 (`-brain` product: `coding-brain` -> `gemini/gemini-2.5-flash`), 78.47.217.225 (same Positive Future brand) | Wrapper model name maps to a legit upstream; operator runs a commercial brand layer |
| **Convenience-alias / academic-lab** | **69.30.237.88 (swatweb.org / jolab.ai — Jo Lab biomedical AI research)** | `/v1/models` advertises Claude IDs; `/v1/model/info` shows `api_base: http://127.0.0.1:3100/v1` with `openai/gemma-4-26b`. Cost = 0. Behavioral probe confirmed: 3 different model name POSTs all returned "I am a large language model, trained by Google" with same `system_fingerprint: b1-d12cc3d`. No customer-facing API resale; lab is the only user. Most plausible motive: convenience alias for Anthropic-SDK-compatible client code. NOT fraud. |
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

1. **`/v1/model/info` is the authoritative discriminator.** Surveys that only probe `/v1/models` miss the mismatch class entirely. Always probe `/v1/model/info` and compare advertised model IDs against `litellm_params` to detect mismatches.

2. **Behavioral verification is required before any fraud label.** A configuration mismatch is necessary but not sufficient evidence for fraud. The verification chain is: (a) configuration mismatch in `/v1/model/info`, (b) behavioral probe (POST with each advertised model name; compare response content + `system_fingerprint`) to confirm the same backend is serving all model IDs, (c) operator-context check (customer-facing site, pricing page, marketing pitch) to determine whether the operator is selling the impersonated model to paying customers.

3. **Per the tier-label discipline**: do NOT label a mismatch host as fraud without all three pieces of evidence. The mismatch alone is a model-attribution-integrity finding, not a fraud finding.

4. **Methodology gap**: prior LLM-gateway surveys (LiteLLM-cloud 2026-05-04, safety/guardrail 2026-05-19) probed only `/v1/models` and `/v1/chat/completions`. Re-survey those corpora through `/v1/model/info` to estimate the mismatch-class population, then per-host operator-context-verify before claiming any fraud subset.

5. **The `cost = 0` signal is suggestive but not conclusive.** A LiteLLM proxy claiming to serve `claude-opus-4-6` with `input_cost_per_token: 0` could be (a) running a local model under that ID (convenience alias, Jo Lab pattern), (b) lying about the cost while passing to a real upstream (genuine fraud), (c) misconfigured (negligent ops). Distinguishing requires the behavioral probe + operator-context check.

## Relationship to prior insights

- **Insight #11 (source code is authoritative; bug reports are framing)**: same epistemology. The operator-authored `/v1/models` response is FRAMING (the operator's claim about what they serve); the `/v1/model/info` response is the AUTHORITATIVE record. Prefer authority.
- **Insight #2 (single-template auth-off propagates at population scale)**: applies here as the leak mechanism. LiteLLM's `/v1/model/info` is auth-off by default in many deployments; the mismatch-class hosts are caught precisely because their config is browsable.
- **Insight #33 (side-channel attribution via registry catalog)**: same family at a different layer. The LiteLLM internal config is the operator-authored side channel that authoritatively attributes the proxy's actual upstream + business model.

## Open questions

- **What fraction of unauth LiteLLM hosts at population scale have the mismatch pattern?** This insight is sourced from a 6-host deep-dive plus a 74-host probe-v2 follow-up (2 mismatch candidates of 74 = 2.7%). The 523-host LiteLLM corpus full re-probe is still pending. Of mismatch candidates surfaced, the Jo Lab case was the first verified-via-behavioral-probe and the first per-operator-context-checked: confirmed convenience-alias, not fraud.
- **What fraction of mismatch candidates actually verify as fraud (not convenience-alias)?** Unknown until per-host operator-context checks complete. Initial hypothesis (Jo Lab generalizes): most academic / research / hobbyist hosts will be convenience-alias. Commercial customer-facing API resale sites with "Claude" in the marketing will be fraud. The split likely correlates with whether the operator has a customer-facing site selling Claude access at all.
- **Are there mismatch sites BEHIND auth?** This survey only catches operators who leave `/v1/model/info` exposed. Operators who gate it might still be running the same pattern (either convenience or fraud) against authenticated customers; that population is invisible to passive recon.

## See also

- `case-studies/commercial/safety-guardrail-population-survey-2026-05-19.md`: parent survey identifying 28 LiteLLM UNAUTH_FUNCTIONAL hosts
- `case-studies/commercial/llm-gateways-cloud-survey-2026-05.md`: prior 1,857-host LiteLLM-class survey (which did NOT probe /v1/model/info)
- `methodology/insight-11-source-code-is-authority.md`: the epistemology this insight applies
- `methodology/insight-33-side-channel-attribution-via-registry-catalog.md`: same family at the registry-content layer
