# Insight #100 — Operator self-branding overwhelms tenant co-branding for LLM-relay SaaS

**Status:** Candidate (1 data point, 765 head-block samples).
**Codified:** 2026-06-09 from LJP-OSS cohort investigation Lane C (DCWF 221).
**Source surface:** HTML `<head>` block: OpenGraph, Twitter Cards, meta tags, link relations.
**Population observed:** 491 hosts, 1,473 probes, 765 populated head blocks, **0 sensitive-org branding hits**.

## The rule

For LLM API gateway / relay platforms, the operator brands the SPA / dashboard with the OPERATOR's own product name. Customer co-branding on the public HTML head surface is essentially zero. Therefore OpenGraph / Twitter Card / meta-tag harvesting is NOT a viable attribution path for identifying downstream customers.

## Why

The LLM-relay product model is API-first. The customer (an application calling `/v1/chat/completions`) does not load the operator's HTML in a browser, so there is no business reason to co-brand. The operator's HTML SPA exists for the operator's OWN signup / admin / billing UI, and is branded for the operator's product (`Sub2API - AI API Gateway`, `Grok2API - Admin`, etc.).

This is structurally different from SaaS B2B platforms where each customer gets a co-branded portal (Slack workspace pages, Salesforce community sites, Zendesk help centers), and the per-tenant brand does leak through `og:site_name`, `og:url`, `<link rel="canonical">`, and friends.

## How to apply

When trying to attribute customer identity on relay-class cohorts:

1. Skip OpenGraph / Twitter Card / meta-tag harvesting at scale - the population yield is 0%.
2. Acceptable use: identify the OPERATOR's product brand (Sub2API, Grok2API, etc.) and the OSS lineage (new-api, one-api, CRMEB) - operator-side attribution, not customer-side.
3. Customer attribution at this product class requires a different surface (see Insight #99 enumeration).

## Evidence

LJP-OSS 491-host cohort. Lane C, DCWF 221 Cyber Crime Investigator. Ports probed: 8080, 443, 80.

| Outcome | Count |
|---|---|
| HTTP 200 with parseable `<head>` | 765 |
| Distinct hosts with any parsed head block | 431 of 491 |
| Hosts with `<meta name="description">` populated | 52 |
| **Sensitive-org branding hits (F500 / .gov / .edu / .mil / .bank / defense / healthcare / banks / SSO)** | **0** |

Title clustering on the 431 populated heads resolves entirely to operator-product self-branding:

- `Sub2API - AI API Gateway` (dominant)
- `Grok2API - Admin`
- `new-api` (the OSS gateway underneath both)
- `CRMEB! Team and CRMEB UI Team` (Chinese commerce SaaS theme leak; NOT a sensitive customer)
- HTTP redirect / login splash pages

The `<meta name="description">` text is Chinese-language gateway marketing copy ("unified AI model aggregation and distribution gateway, OpenAI/Claude/Gemini cross-format compatible") and one dental-industry SaaS unrelated to LLM-relay. None map to the sensitive-org lexicon (universities, federal agencies, banks, healthcare networks, defense contractors, F500).

## Generalization scope

Applies to: LLM API gateway / relay platforms where the customer is an *application*, not a *user*. Specifically LJP-OSS class (Sub2API, Grok2API, cousins).

Does NOT apply to: B2B SaaS where each customer gets a co-branded portal. There, head-block attribution IS the load-bearing path.

## Related

- [[reference_insight_99_oidc_discovery_not_viable]] — sibling insight on OIDC discovery surface
- [[reference_insight_78_identity_vs_auth_bearing_surface]]
- [[reference_insight_79_llm_jacking_ecosystem]]
