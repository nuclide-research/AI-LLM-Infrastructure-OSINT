---
to: abuse@akamai.com
cc: abuse@nuclide-research.com
severity: HIGH
ip: 173.255.226.61
institution: Akamai Technologies (Linode customer; 173-255-226-61.ip.linodeusercontent.com)
status: DRAFT
outcome: sent
date: 2026-05-04
---

**To:** abuse@akamai.com
**Cc:** abuse@nuclide-research.com
**Subject:** Unauthenticated LiteLLM Proxy fronting OpenAI + Anthropic + Mistral keys — 173.255.226.61:4000

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-04

**Re:** Unauthenticated LiteLLM Proxy with 4 multi-provider models (OpenAI + Anthropic + Mistral keys configured, OpenAI verified-functional unauth)
**IP / Host:** 173.255.226.61 (rDNS `173-255-226-61.ip.linodeusercontent.com`, Linode US)
**Severity:** HIGH

---

I'm an independent security researcher conducting good-faith AI infrastructure research under the NuClide Research umbrella (CISA disclosures CVE-2025-4364, ICSA-25-140-11). This is an unsolicited coordinated-disclosure notification.

---

## Summary

A Linode customer at `173.255.226.61:4000` is running an unauthenticated **LiteLLM Proxy** fronting commercial API keys for at least three providers (Anthropic, OpenAI, Mistral). An unauthenticated `POST /v1/chat/completions` call to `openai/gpt-4o-mini` returned 14 tokens of completion — confirming the operator's OpenAI API key is functional and burnable by any unauthenticated internet caller. The Anthropic and Mistral keys are similarly exposed and likely functional.

Found during NuClide Research's cross-cloud LLM Gateway survey (2026-05-04). Full case study: https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/commercial/llm-gateways-cloud-survey-2026-05.md

---

## Confirmed exposure

- `GET /v1/models` returns 4 models without auth: `openai/gpt-4o-mini`, `anthropic/claude-sonnet-4-5`, `openai/gpt-4o`, plus a Mistral entry. `owned_by` tags include `anthropic`, `mistral`, `openai`.
- `POST /v1/chat/completions` with `{"model":"openai/gpt-4o-mini","messages":[{"role":"user","content":"hi"}],"max_tokens":1}` returned `200 OK` with `model: "openai/gpt-4o-mini"` and `usage: {prompt_tokens:12, completion_tokens:2}`. Response body: `"Acknowledged."`
- LiteLLM Proxy fingerprint confirmed via `/health/liveliness` returning health JSON + Prometheus `litellm_*` metrics.

Methodology cost: 14 tokens of operator quota consumed (under USD $0.0001). No additional probing performed; Anthropic and Mistral models were listed but not invoked.

---

## Why it matters

LiteLLM Proxy is designed as a multi-provider OpenAI-compatibility router. When deployed without `LITELLM_MASTER_KEY` (the proxy's authentication mode), every configured upstream API key becomes proxiable by any unauthenticated caller:

- Anthropic Claude Sonnet 4.5 — premium tier, ~$3/M input + $15/M output
- OpenAI GPT-4o + GPT-4o-mini — premium + budget tiers
- Mistral La Plateforme — additional commercial quota

The exposure pattern is identical to the **10 commercial-API reseller proxies** documented in NuClide's vLLM cross-cloud survey (e.g., Grok2API, Kiro-Go, AgentBar) and the **1,857 functional unauth gateways** documented in the LLM Gateway survey. This instance is one of the 2 verified Anthropic-key-burnable hosts in that population.

---

## Remediation

LiteLLM has built-in auth — enable `LITELLM_MASTER_KEY` and (optionally) per-virtual-key rate limits:

```
# In LiteLLM config or env:
LITELLM_MASTER_KEY=sk-litellm-<random>

# Restart the proxy
litellm --config config.yaml
```

After enabling auth, **rotate all upstream provider keys** (Anthropic, OpenAI, Mistral) — assume they have been observed for the duration the proxy was exposed.

Alternatively, restrict to internal callers via firewall:

```
ufw deny 4000/tcp
ufw allow from <internal-network> to any port 4000
```

---

## Reference

Full case study + cross-cloud population data:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/commercial/llm-gateways-cloud-survey-2026-05.md

Per-host empirical proof (status code + tokens consumed):
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/evidence/llm-gateway-tier2-2026-05-04/llm-gateway-key-proofs.jsonl

Happy to answer questions or assist with verification.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
