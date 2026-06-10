# Insight #101 — LJP-OSS client bundles do not leak customer-side identifiers at population scale

**Status:** Candidate (1 data point, 471 JS bundles + 403 source maps).
**Codified:** 2026-06-09 from LJP-OSS cohort investigation Lane D (DCWF 661 R&D + DCWF 511 CDA).
**Source surface:** Production JS bundles, accompanying source maps, embedded comments, WebSocket / SSE URL literals.
**Population observed:** 491 hosts probed, 424 responsive, 351 hosts with successful JS bundle fetches.

## The rule

For productized OSS LLM API gateway / relay platforms (LJP-OSS class), the client-side JS bundles do NOT leak customer-side organizational identifiers, embedded API tenant IDs, secret-key signatures, or sensitive-domain references at population scale. Therefore client-bundle deep-code analysis is NOT a viable attribution path for identifying downstream customers.

## Why

The client bundle is shipped by the OPEN-SOURCE PROJECT, not regenerated per customer. Sub2API, Grok2API, OpenClaw, etc. are OSS products with a standard build output that the operator deploys. The customer (an application calling the gateway) never receives a custom-bundled client. There is no per-customer build step that could leak customer identity into the bundle.

Server-side environment variables (API keys, customer org IDs, upstream tenant secrets) remain on the server and are not inlined into the public client bundle. This is consistent with standard secure SPA architecture and confirms that customer attribution at this product class lives in the data layer (`/v1/models`, admin endpoints, billing data) not the code layer.

## How to apply

When investigating LJP-OSS-class cohorts:

1. Skip per-host JS bundle deep grep at population scale for customer attribution - yield is 0% across 471 bundles.
2. JS bundle audit IS still useful for OPERATOR provenance (which OSS project the host runs, library supply chain). 74 unique GitHub owner/repo pairs surfaced across the sampled cohort. K0268 forensic catalog purpose.
3. Customer attribution belongs on TLS SAN, cert CN, favicon hash, ingress hostname, `/v1/models` inventory, or authenticated admin-panel surfaces.

## Evidence

LJP-OSS 491-host cohort. Lane D, DCWF 661 R&D Specialist + DCWF 511 Cyber Defense Analyst. Ports probed: 8080, 443, 8000. Mullvad VPN active. 2 MB cap per bundle, 12-worker pool.

| Metric | Value |
|---|---|
| IPs probed | 491 |
| IPs responsive | 424 (86.4%) |
| IPs with >=1 JS bundle fetched | 351 |
| IPs with >=1 source map fetched | 343 |
| Total JS bundles analyzed | 471 |
| Total source maps analyzed | 403 |
| **Sensitive-substring hits across all 471 bundles + 403 maps** | **0** |
| **WebSocket / SSE URL literals** | **0** (cohort speaks HTTP + SSE, not WS) |
| **Secret-key signatures (sk-/AKIA/ghp_/AIza/xox*/sk-ant-)** | **0** |
| **Embedded API tenant IDs (openai_org_id, azure tenant GUID, GCP project, AWS account)** | **0** |
| Unique GitHub owner/repo pairs catalogued | 74 (K0268 forensic footprint) |

Email addresses found: 22 unique, after disambiguation 4 real ones - all from upstream OSS library `@author` / Copyright comments embedded in source maps, identifying the library author NOT the operator.

Build-time path leaks: 2 unique paths from a single host (Vite chunk-name leak, no `/Users/<dev>` or `C:\` identifiable developer paths).

## Generalization scope

Applies to: productized OSS SPA dashboards for API-first products where the customer is an *application*. LJP-OSS class (Sub2API, Grok2API, OpenClaw, etc.).

Does NOT apply to:

- Custom-built per-customer SPAs (rare; ~0% of OSS-product population)
- B2B SaaS with per-tenant build steps (Looker, Tableau, Salesforce embedded apps)
- Browser extensions that ship with hardcoded customer keys

## Related

- [[reference_insight_99_oidc_discovery_not_viable]]
- [[reference_insight_100_operator_self_branding_overwhelms]]
- [[reference_insight_79_llm_jacking_ecosystem]]
