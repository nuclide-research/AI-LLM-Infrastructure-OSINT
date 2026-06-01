# Insight #74 — AI gateway exposure is a master-key theft multiplier, not a single-key leak

_Sourced to: Cat-32 AI Gateways survey, 2026-06-01._

## The lesson

An exposed AI gateway is categorically different from an exposed model server. A
single unauth Ollama instance leaks one operator's inference surface. A single
unauth AI gateway yields **every upstream LLM provider API key** the operator has
wired in, across every provider (OpenAI, Anthropic, Gemini, DeepSeek, etc.) and
every downstream user that has stored credentials through the gateway. Impact does
not scale linearly -- it scales with the gateway's user count and provider portfolio.

Concretely: an exposed one-api or new-api admin dashboard holds the API keys for
every downstream user who has registered. An exposed Envoy `/config_dump` returns
plaintext credentials for every configured upstream cluster. An exposed Kong Admin
API at `:8001` gives read-write access to the service registry and plugin chain --
including any pre-function Lua plugins carrying secrets.

The Cat-32 survey quantified the gateway exposure surface:

| Platform | Shodan pop | Threat |
|---|---|---|
| new-api | 13,456 | Default creds; Chinese relay operators brokering OpenAI/Anthropic/DeepSeek keys |
| one-api | 2,449 | Default creds; 1.19M Docker pulls |
| Kong Admin API | 600 | CVE-2020-11710; RCE via pre-function plugin |
| Envoy config_dump | 89 | Plaintext credential dump; 87 confirmed unauth |

The 13,456 new-api instances are predominantly Chinese-region cloud infrastructure
operating commercial relay layers between downstream users and Western LLM providers
(OpenAI, Anthropic, Gemini). Each instance potentially holds dozens to hundreds of
upstream API keys. This is the attribution-laundering pattern from Insight #39 at
population scale.

## Why it generalizes

Any multi-tenant credential relay has this property: the blast radius is bounded
not by "what keys does this host hold" but by "how many accounts route through this
host." The gateway tier is uniquely dangerous because:

1. **Aggregation by design.** Gateways exist to centralize access -- that is the
   product feature. The operational convenience (one key in, many providers out) is
   exactly what makes unauth exposure catastrophic.
2. **Auth is optional in most OSS deployments.** one-api, new-api, and Kong all
   ship with auth disabled or minimally configured by default. The product works
   without auth; auth is a deployment decision the operator makes (or doesn't).
3. **Admin and proxy ports are often co-located.** Kong's admin port `:8001` and
   proxy port `:8000` typically run on the same host. A firewall gap that exposes
   `:8001` often implies `:8000` is also externally accessible.

## How to apply

1. **Elevate gateway category in the survey taxonomy.** A gateway finding should
   trigger deeper provider-key enumeration than a plain model server finding. If
   the gateway is a confirmed unauth admin, the primary artifact is the key
   inventory -- not just the host.
2. **Envoy `/config_dump` as a credential oracle.** Any Envoy admin interface
   exposed on `:9901` or `:15000` should have `/config_dump` attempted. The full
   Envoy config is a structured credential inventory. This is a Depth-A verification
   that requires a single GET and yields the complete upstream auth state.
3. **For relay operators (new-api / one-api), attribution is the finding.** The
   host IP is one operator running dozens of customers' keys. The finding narrative
   is "pooled-account relay at scale" -- Insight #39 applied to AI infrastructure.

## Relationships

- Extends **#39** (pooled-account proxy = attribution laundering): Cat-32 is the
  first survey that measured #39 at population scale in the AI gateway tier.
- The verification primitive for Envoy (GET `/config_dump`) is the strongest
  Depth-A signal in this survey -- higher-confidence than banner-match alone.
