# Insight #99 — OIDC discovery is not viable for LLM-relay customer attribution

**Status:** Candidate (1 data point, 2,455 OIDC probes).
**Codified:** 2026-06-09 from LJP-OSS cohort investigation Lane C (DCWF 221).
**Source surface:** `/.well-known/openid-configuration` (RFC 8414).
**Population observed:** 491 hosts, 2,455 probes across 5 ports each, 496 HTTP 200 responses, **0 parseable OIDC discovery documents**.

## The rule

For multi-tenant LLM API gateway / relay infrastructure (Sub2API, Grok2API, OpenAI-compat proxies, cousins), the operator does NOT self-host RFC 8414 OIDC discovery on the public surface. Therefore `/.well-known/openid-configuration` is not a viable attribution path for identifying which customer / tenant / parent organization is using a given relay instance.

## Why

LLM-relay infrastructure speaks the OpenAI / Anthropic / Gemini HTTP API contract on `/v1/chat/completions`, not the OAuth 2.0 / OIDC contract on `/.well-known/openid-configuration`. The customer interacting with this surface is an *application* presenting an API key, not a *user* completing an OAuth flow. There is no IdP to discover because no IdP was deployed.

Even where SPA config flags claim OAuth providers are present (LinuxDo, WeChat, Google, GitHub, custom OIDC), the OIDC `issuer` URL is the OPERATOR's own login endpoint (operator-as-IdP), not the customer's IdP. Issuer URLs point at the operator's domain, not a downstream customer's domain.

## How to apply

When trying to attribute customer identity on relay-class cohorts:

1. Skip `/.well-known/openid-configuration` — sample showed 0% useful return on 2,455 probes despite 496 HTTP 200s. The 200s were SPA fallback / wildcard route absorbs, not IdP responses.
2. Customer attribution at this product class lives elsewhere:
   - `/v1/models` catalog (which upstream provider, which model variants)
   - Admin panel customer roster (gated by JWT, out of scope without engagement)
   - Payment-page favicons (Stripe / Airwallex / EasyPay observed across cohort)
   - JWT `iss` claims (only obtainable post-authentication)
   - CT-log SAN populations for operator domains (already covered in Stage 2)
   - Co-located service hostname patterns (MySQL backing-store hostnames, FRP tunnel admin UI)

## Evidence

LJP-OSS 491-host cohort. Lane C, DCWF 221 Cyber Crime Investigator + DCWF 212 Forensics. Ports probed: 8080, 8000, 443, 80, 8443.

| Outcome | Count |
|---|---|
| HTTP 200 returned on `/.well-known/openid-configuration` | 496 |
| HTTP 404 | 346 |
| HTTP 401/403 (auth gate) | 24 |
| HTTP 4xx other | 19 |
| HTTP 5xx | 11 |
| TCP/TLS connect failure | 1,557 |
| **Parseable OIDC JSON (>=2 standard RFC 8414 fields)** | **0** |
| **Sensitive issuer / endpoint hits (.gov/.edu/.mil/.bank / F500 / SSO tenant)** | **0** |

## Generalization scope

Applies to: LLM API gateway / relay platforms (OpenAI-compatible). Specifically Sub2API, Grok2API, OpenClaw, QClaw, SubConv, new-api, one-api, and the broader productized OSS LLM-jacking class (Insight #79).

Does NOT apply to: multi-tenant SaaS that deliberately exposes per-customer IdPs (Slack-class, Notion-class). For those, OIDC discovery IS the load-bearing attribution path.

## Related

- [[reference_insight_79_llm_jacking_ecosystem]] — LJP-OSS cohort founding
- [[reference_insight_78_identity_vs_auth_bearing_surface]] — identity surface vs auth-bearing
- [[reference_insight_39_pooled_account_attribution_laundering]] — pooled-account proxy class
