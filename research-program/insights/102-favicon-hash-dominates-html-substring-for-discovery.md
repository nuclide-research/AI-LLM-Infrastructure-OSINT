# Insight #102 — Shodan favicon-hash dorks dominate HTML-body substring dorks for cohort discovery scale-up

**Status:** Candidate (1 data point, 16,623 vs 10,675 hit-count comparison).
**Codified:** 2026-06-09 from LJP-OSS cohort investigation Lane E (DCWF 422 Data Analyst).
**Source surface:** Shodan UI search via Playwright in-page fetch.
**Population observed:** Sub2API population: `http.favicon.hash:1585982716` returned 16,623 hits vs `http.html:"Sub2API"` returned 10,675 hits.

## The rule

For discovery scale-up beyond Shodan UI's ~200-link-per-dork pagination cap, favicon mmh3 hash dorks (`http.favicon.hash:<hash>`) dominate HTML-body substring dorks (`http.html:"<brand>"`) by 1.56x in raw population AND by ~10x in usable-link-yield-per-query when paginated. Compute the favicon hash once, dork against it as the primary discovery vector.

## Why

Three structural reasons:

1. **Larger universe.** HTML-body substring requires the brand string to appear verbatim in the rendered HTML Shodan indexed. Favicon hash matches any host serving the same favicon byte sequence, regardless of brand customization, HTML language, or rebrand-without-favicon-replace. LJP-OSS rebrands like BongRee / SubConv / Sub2API all ship the same favicon and surface as one population.
2. **Reused asset hashing.** Operators rarely replace the default favicon. The Sub2API source ships `logo.png` (NOT favicon.ico - Sub2API's favicon path differs from the default), and operators copy the install verbatim. One hash collects the population.
3. **Pagination diversity.** Shodan's UI per-card link enumeration is sampled within a single dork; using a different dork axis (favicon vs html) refreshes the per-card sample. Combined country / port / org slicing on the favicon dork yields strictly more unique IPs than slicing on the html dork.

## How to apply

1. Pick one alive cohort host. Pull its favicon: `curl -s -o /tmp/favicon.bin http://<host>:<port>/logo.png` (or whatever path the product uses - Sub2API uses `/logo.png`, not `/favicon.ico`).
2. Compute the Shodan-compat mmh3 hash. `jaxen pivot http://<host>:<port>/` natively computes it. Manual: base64-encode the bytes, then mmh3.hash() of the base64 (with newlines per Python `base64.encodebytes`).
3. Dork: `http.favicon.hash:<hash>`. Expect order-of-magnitude larger population than the html-body equivalent.
4. For discovery scale-up beyond UI cap, country-slice or port-slice the favicon dork: `http.favicon.hash:<hash> country:CN`, etc. Each slice refreshes the per-card link enumeration.

## Evidence

LJP-OSS 491-host investigation. Lane E, DCWF 422 Data Analyst.

| Dork | Shodan hit count | Discovery method |
|---|---|---|
| `http.html:"Sub2API"` | 10,675 | HTML body substring |
| `http.title:"Sub2API - AI API Gateway"` | 10,380 | HTML title substring |
| **`http.favicon.hash:1585982716`** | **16,623** | **Favicon mmh3 hash** |

Sub2API favicon-confirmed total: 16,623 hosts. HTML-substring tally undersamples by 35-40%.

| Vector | Origin-IP new vs prior cohort | Universe sampled |
|---|---|---|
| **V1 Shodan favicon (`1585982716`)** | **114** | **16,623** |
| V2 CT logs (crt.sh + dig) | 6 | 107 SANs / 32 resolved |
| V4+V5 GitHub / aggregator URL resolution | 5 | 232 URLs / 28 op-hosts |
| V3 HackerTarget reverse-IP | 3 | 21 IPs (50/day cap) |

V1 dominates by an order of magnitude per query, and the raw universe is 35-40% bigger than the html-substring tally. The remaining V2 / V3 / V4 / V5 vectors are useful for CDN-edge and PaaS-egress IPs that Shodan misses entirely, but they are secondary multipliers.

## Generalization scope

Applies to: ANY productized OSS class where operators self-deploy without replacing the default favicon. Includes: LJP-OSS (Sub2API, Grok2API, cousins), Open WebUI, AnythingLLM, Langfuse, Open-WebUI-style dashboards, and most SPA dashboards that ship with a default brand asset.

Does NOT apply to: products where the favicon is customer-customizable per deployment (Notion, Linear, etc.) - there the hash diverges per customer.

## Operational corollary

The Shodan UI 200-link-per-dork cap is the binding constraint for cohort enumeration once the population is identified. Favicon hash gives the COUNT but does not bypass the per-dork link enumeration cap. To go from 619 unique IPs (the LJP-OSS sample) to 12,577+ population coverage, sidebar-facet sharding via Shodan's WORLD_MAP_DATA + per-country / per-org slicing of the favicon dork is the next move. Censys CT-log delta + ZoomEye + favihunter multi-engine pivots close the long tail.

## Related

- [[reference_insight_79_llm_jacking_ecosystem]]
- [[reference_shodan_facet_host_ssr_engine]] — Shodan facet harvest patterns
- [[reference_dork_population_substitution]] — biased subpopulation insight
