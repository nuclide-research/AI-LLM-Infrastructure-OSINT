---
to: abuse@akamai.com
cc: abuse@nuclide-research.com
severity: CRITICAL
ip: 172.235.117.122
institution: Akamai Technologies (Linode customer; 172-235-117-122.ip.linodeusercontent.com)
status: DRAFT
outcome: sent
date: 2026-05-04
---

**To:** abuse@akamai.com
**Cc:** abuse@nuclide-research.com
**Subject:** Unauthenticated multi-provider LLM gateway burning Anthropic + OpenAI quotas, 172.235.117.122:4000

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-04

**Re:** Unauthenticated OpenAI-compatible LLM gateway with 87 commercial-API models (10 provider-key tags, including verified-functional Anthropic Claude 4.5 Haiku invocation)
**IP / Host:** 172.235.117.122 (rDNS `172-235-117-122.ip.linodeusercontent.com`, Linode US)
**Severity:** CRITICAL

---

I'm an independent security researcher conducting good-faith AI infrastructure research under the NuClide Research umbrella (CISA disclosures CVE-2025-4364, ICSA-25-140-11). This is an unsolicited coordinated-disclosure notification.

---

## Summary

A Linode customer at `172.235.117.122:4000` is running an unauthenticated **OpenAI-compatible LLM gateway** fronting commercial API keys for 10 distinct upstream providers. An unauthenticated `POST /v1/chat/completions` call to model `claude-4.5-haiku` returned 56 Anthropic API tokens of completion, confirming the operator's Anthropic API key is **functional and burnable by any unauthenticated internet caller**.

Found during NuClide Research's cross-cloud LLM Gateway survey (2026-05-04). Full case study: https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/commercial/llm-gateways-cloud-survey-2026-05.md

---

## Confirmed exposure

- `GET /v1/models` returns 87 models without auth, with `owned_by` tags spanning: alibaba, anthropic, deepseek, google, minimax, moonshot, openai, windsurf, xai, zhipu, i.e., a full multi-provider commercial-API key vault.
- `POST /v1/chat/completions` with `{"model":"claude-4.5-haiku","messages":[{"role":"user","content":"hi"}],"max_tokens":1}` returned `200 OK` with `model: "claude-4.5-haiku"` and `usage: {prompt_tokens:1, completion_tokens:55}`.

Methodology cost: 56 tokens of operator quota consumed (under USD $0.001). No additional probing performed; specifically: no other models invoked, no extended completions, no quota-draining requests.

---

## Why it matters

The exposed gateway represents **direct billing-impact on the operator's commercial API subscriptions across 10 providers**. An attacker can:

- Drain Anthropic quota on Claude Sonnet / Opus / Haiku models
- Drain OpenAI quota on GPT-4 family
- Consume Google Gemini, DeepSeek, Mistral, MiniMax, Moonshot, xAI, Zhipu, and Alibaba commercial inference budgets
- Use the gateway as a free reseller proxy for downstream attackers

For a typical commercial operator, this is uncapped financial bleed bounded only by the operator's payment-method spending limits. At Anthropic Claude Sonnet pricing alone, sustained scripted abuse can reach hundreds to thousands of USD per day without any service-side rate-limiting.

This finding is part of a population-scale pattern: **1,857 of 1,898 confirmed unauth gateways** in the same cross-cloud survey returned functional inference responses to a single-token unauthenticated probe. This gateway is one of the **2 verified Anthropic-key-burnable instances** in that population.

---

## Remediation

The most common deployment is LiteLLM Proxy or a custom OpenAI-compat router. Either:

**Add API-key auth at the proxy:**

```
# LiteLLM example: set master key + virtual keys per consumer
LITELLM_MASTER_KEY=sk-<random> litellm --config config.yaml
```

**Or restrict to internal callers via firewall:**

```
ufw deny 4000/tcp
ufw allow from <internal-network> to any port 4000
```

**Then rotate all upstream provider keys**, assume they have been observed in the wild for the duration the endpoint was exposed.

---

## Reference

Full case study + cross-cloud population data:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/commercial/llm-gateways-cloud-survey-2026-05.md

Per-host empirical proof (status code + tokens consumed):
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/evidence/llm-gateway-tier2-2026-05-04/llm-gateway-key-proofs.jsonl

I'm happy to answer questions or assist with verification.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
