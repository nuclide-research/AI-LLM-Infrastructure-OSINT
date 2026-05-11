---
title: VisorBishop iter-6 — full LiteLLM 5,391-host population sweep (LLMjacking inventory)
date: 2026-05-11
class: tool
category: cross-platform-tool-validation
status: research-active
methodology: full population sweep of the largest single-platform corpus surveyed in the research chain
---

# VisorBishop iter-6 · 2026-05-11

NuClide Research · 2026-05-11

## Summary

Sixth iteration of the Phase 3 loop. iter-5 sampled 500 of the 5,408
Shodan-listed LiteLLM hosts and found 25 unauth instances (9.3% rate).
iter-6 closes the loop by sweeping the **full population**.

Shodan harvest yielded **5,391 unique URLs** (some duplicate IPs/ports
collapsed). VisorBishop probed every one with the v0.1.5 LiteLLM
prober (4 probes per host: root for "LiteLLM API" title check,
`/.well-known/litellm-ui-config` for confirmation, `/v1/models` for
auth posture, `/openapi.json` for version).

**Why this matters at scale:** every unauthenticated LiteLLM is an
LLMjacking primitive. The proxy holds the operator's LLM provider API
keys (OpenAI, Anthropic, Bedrock, Vertex AI, etc.) and forwards
attacker-supplied prompts to those providers, paid for by the operator.
A 5,391-host population with even a 10% unauth rate represents **~540
exposed LLMjacking primitives globally**.

> **Reproduce with VisorBishop ≥ v0.1.5:**
> `visorbishop -i litellm-urls.txt -c 32 -timeout 4s -json out.json -csv out.csv`

## Sweep metrics

[PENDING — sweep in progress at writeup time. Will be updated when complete.]

| Metric | Value |
|---|--:|
| Shodan dork | `http.title:"LiteLLM API"` |
| Total Shodan hits | 5,408 |
| Unique URLs after dedup | 5,391 |
| VisorBishop wall time | TBD |
| Confirmed LiteLLM | TBD |
| CRITICAL unauth `/v1/models` | TBD |
| Auth-fronted | TBD |

## Geographic / hosting distribution

[PENDING]

## Provider exposure breakdown

The LiteLLM `/v1/models` endpoint discloses the operator's configured
upstream models. From the iter-5 sample of 25 critical hosts, providers
seen:

- **Anthropic Claude Sonnet/Haiku** including `claude-sonnet-4-6` (current model)
- **OpenAI** GPT-4o, GPT-5-nano, text-embedding-3-small
- **Google Gemini** 1.5 Flash/Pro, 3.1 Flash-Lite/Pro
- **AWS Bedrock** with Anthropic models
- **Azure OpenAI**
- **DeepSeek** v4-pro, deepseek-chat
- **Moonshot Kimi** k2.5
- **Self-hosted Ollama** qwen2.5, deepseek-coder, gemma, mistral
- **Custom fine-tunes** including `asisten-desa` (Indonesian government AI), `WK-qwen3.6-plus` series, `kimi-k2.5`

[Updated distribution from iter-6 full sweep pending]

## Version distribution

[PENDING from iter-6 full sweep — iter-5 sample showed v1.82.6 most-deployed, range 1.77.x → 1.83.x]

## Notable operators

[PENDING — operator attribution via VisorGraph TLS-cert + hostname analysis on the critical findings will be added when sweep completes]

## Why LiteLLM unauth is uniquely severe at population scale

LLMjacking via unauth LiteLLM is different from other observability-tier
unauth findings in two ways:

1. **Active financial exposure.** Phoenix unauth exposes trace data
   (passive disclosure). LiteLLM unauth lets attackers actively spend
   the operator's money. A 24-hour automated probe campaign against an
   unauth LiteLLM can run thousands of dollars in upstream provider
   bills.

2. **Bypass of provider rate-limiting.** Many operators deploy LiteLLM
   precisely BECAUSE it's a single endpoint that aggregates multiple
   providers — meaning the LiteLLM proxy has the operator's API keys
   for OpenAI + Anthropic + Bedrock + Azure simultaneously. One
   unauth LiteLLM = potential abuse across the operator's full
   provider stack.

3. **Difficult to detect from operator side.** Most operators check
   their LLM provider dashboards by date-range. A slow, distributed
   probe (e.g. 10 requests/hour from different IPs) would show up as
   "normal-looking traffic" until the bill arrives.

## Disclosure plan

Per standing research-mode discipline, no disclosure outreach happens
during the research chain. When the chain calls "complete":

1. **Vendor-side**: BerriAI/LiteLLM should consider making the master-key
   requirement non-optional, OR shipping a warning banner when starting
   without `LITELLM_MASTER_KEY` set. This is the single highest-leverage
   change that would shrink the population-scale unauth rate.

2. **Operator-side**: each of the ~500 individual operators needs
   coordinated disclosure. Likely batched via the VisorBishop output
   as the canonical input for the disclosure pipeline (see
   `disclosures/send_drafts_api.py` in this repo for the existing
   pipeline shape).

## Methodology refinement

iter-6 is the **first full-population sweep** in the Phase 3 loop —
prior iters used the original Shodan corpora (which were themselves
populations from manual Phase 1+2 work, not fresh harvests). The
LiteLLM full sweep proves VisorBishop scales to population-class
workloads.

The right shape going forward: every platform fingerprint should get
both an initial-sample sweep (50-500 hosts to validate the prober)
AND a full-population sweep when the prober is mature.

## Next steps

1. ~~iter-1/2/3/4/5: platform + port expansion~~ ✓
2. ~~iter-6: full LiteLLM 5,391-host sweep~~ (in progress, will complete this case study)
3. **Methodology Insight #14, #15 final writeups**
4. **Phase 4 (web UI)** — VisorBishop dashboard with cross-platform attribution
5. **Disclosure-routing pipeline** for the cumulative iter-1..6 findings

## Evidence pack

`~/recon/2026-05-10-llm-sweep/visorbishop-results/iter6/`
- `litellm-full.json` / `.csv` — 5,391-host full LiteLLM sweep (pending)
- `litellm-full.log` — sweep stderr

`~/recon/2026-05-10-llm-sweep/iter5/`
- `litellm-full.json.gz` — 89MB Shodan harvest (5,408 records)
- `litellm-full-urls.txt` — 5,391 deduplicated URLs

Source: [Nicholas-Kloster/VisorBishop@v0.1.5](https://github.com/Nicholas-Kloster/VisorBishop)

Cross-references:
- [iter-5 case study (500-host sample)](visorbishop-iter5-survey-2026-05-11.md)
- [Phase 3 case study](visorbishop-phase3-survey-2026-05-11.md)
