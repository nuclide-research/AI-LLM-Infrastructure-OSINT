# Check 221 - IdP + Operator-Branding Attribution

**DCWF 221 Cyber Crime Investigator** + **DCWF 212 Forensics adjacency**
Outfit: `idp-branding-attribution-221`
Cohort: 491 LJP-OSS hosts (`~/syllabus/cohort-megaset.txt`)
Run: 2026-06-09 UTC, probe wall time 416s, 18 workers, GET-only
Evidence: `check-221-idp-branding.jsonl` (3,928 records, verbatim raw_excerpt + URL + ISO-8601 ts per record, K0118)

## Headline

Cyber crime investigation of operator-branding + IdP attribution surface across 491 cohort hosts identified **zero** hosts with sensitive customer-side identity provider or organizational branding references.

The cohort is what its banners say it is: a Chinese AI-API-gateway / proxy-SaaS operator population (Sub2API, Grok2API, new-api, CRMEB), not a customer-fronted IdP fleet. No `.gov` / `.edu` / `.mil` / `.bank` issuer URLs were found. No Fortune-500, defense-contractor, healthcare, or financial-institution branding was found in OpenGraph / Twitter Card / `<meta>` / `<link rel="canonical">` surface. No reverse-lookable enterprise SSO tenant IDs (Okta, Auth0, Azure AD, Google SAML, OneLogin, Ping, Duo) were leaked in any parsed head block.

## Investigative posture (K0107, T0181 Advanced)

The attribution thesis under test: *if a cohort host is fronting an enterprise customer\'s identity surface, the customer\'s identity will leak through either (a) RFC-8414 OIDC discovery metadata, since the `issuer` field is normatively the customer\'s IdP URL, or (b) operator-supplied HTML branding (`og:site_name`, `og:url`, `<link rel="canonical">`, `<meta name="author|copyright|organization">`), since SaaS multi-tenancy commonly co-brands per tenant.*

Both surfaces are public-by-design - there is no K0118 evidence-seizure concern, the probes hit URLs an unauthenticated browser would. Verbatim raw HTTP body (capped 512KB), HTTP status, headers, and ISO-8601 UTC timestamp are preserved per record for chain-of-custody replay.

The thesis is refuted for this cohort.

## Per-check tallies

### Check 5 - OIDC discovery (RFC 8414)

Ports probed per host: 8080, 8000, 443, 80, 8443 (2,455 total probes).

| Outcome | Count |
|---|---|
| HTTP 200 returned | 496 |
| HTTP 404 returned | 346 |
| HTTP 401/403 (auth gate) | 24 |
| HTTP 400/4xx other | 19 |
| HTTP 5xx | 11 |
| TCP/TLS connect failure (no listener, timeout, reset) | 1,557 |
| **Parseable OIDC JSON (>=2 standard fields)** | **0** |
| **Sensitive issuer / endpoint hits (.gov/.edu/.mil/.bank / F500 / SSO tenant)** | **0** |
| Hosts reachable on at least one OIDC port | 457 of 491 |

Read: 496 hosts returned 200 on `/.well-known/openid-configuration`, but **not one** returned a body that parses as an OIDC discovery document with two or more standard fields (`issuer`, `authorization_endpoint`, `token_endpoint`, `jwks_uri`, ...). The 200s were SPA index pages, 404-ish landing HTML, or non-JSON gateway responses - the path was being absorbed by a wildcard route, not served by an IdP. **This cohort does not run RFC-8414 OIDC discovery on any of these ports.** Consistent with the AI-API-gateway operator class: these are OpenAI-compatible reverse proxies, not OAuth2/OIDC providers.

### Check 9 - OpenGraph / Twitter Card / meta-tag branding

Ports probed per host: 8080, 443, 80 (1,473 total probes).

| Outcome | Count |
|---|---|
| HTTP 200 with parseable `<head>` (title / meta / link) | 765 |
| Distinct hosts with any parsed head block | 431 of 491 |
| Hosts with `<meta name="description">` populated | 52 |
| **Sensitive-org branding hits (F500 / .gov / .edu / .mil / .bank / defense / healthcare / banks / SSO)** | **0** |

Read: 431 of 491 hosts exposed at least one parseable HTML head. Title clustering is overwhelmingly operator brands of the same class:

- `Sub2API - AI API Gateway` - dominant cluster, OpenAI-compatible relay
- `Grok2API - Admin` - sibling product, same class
- `new-api` - generator tag for the open-source gateway underneath both
- `CRMEB! Team and CRMEB UI Team` - Chinese commerce SaaS theme leaking through, **not** a sensitive customer
- 404 / login splash pages

The descriptions in `<meta name="description">` are Chinese-language gateway marketing copy (unified AI model aggregation & distribution gateway, OpenAI/Claude/Gemini cross-format compatible) and one dental-industry SaaS (digital consulting platform for dental practice owners). None map to the sensitive-org lexicon (universities, federal agencies, banks, healthcare networks, defense contractors, F500).

No `og:site_name`, no `og:url`, no `<link rel="canonical">` pointed at any monitored sensitive parent domain.

## Verbatim sensitive-hit rows

**None.** Zero rows across both checks. This section is intentionally empty rather than omitted, per the deliverable spec.

## What the negative result means (S0359)

1. **Customer attribution via IdP discovery is not viable for this cohort on the probed surface.** The cohort hosts are operator infrastructure for the operator\'s own AI-gateway product, not multi-tenant per-customer IdPs. They speak OpenAI-compatible API, not OIDC.

2. **Customer attribution via HTML branding is not viable for this cohort on the probed surface.** Operators self-brand consistently with their own product name; they do not co-brand HTML head with their downstream API consumers. Consistent with the AI-API-gateway business model - the customer is an *application* calling `/v1/chat/completions`, not a *user* loading a co-branded portal.

3. **Customer attribution would have to come from another surface.** Candidates the cohort does expose, observed in passing during this probe but out of scope for the 221 check: gateway model catalogs (`/v1/models`), admin panel customer lists if auth-bypassable, JWT `iss` claims if a token can be coaxed out unauth, payment-page favicon hashes, TLS SNI logs (passive), and CT-log subjectAltName populations for operator domains.

4. **For DCWF 221 disposition: the operator-side attribution is solid (Sub2API / Grok2API / new-api / CRMEB lineage, Chinese operator ecosystem, consistent with the broader LJP-OSS cohort fingerprint), and the customer-side attribution surface is closed on the two channels checked here.** No US gov / .edu / .mil / .bank / F500 / defense / healthcare nexus surfaces through IdP discovery or HTML branding.

## Insight (candidate, to codify)

**Insight #Cnd-221-A - Multi-tenant LLM-relay operators do not leak customer identity through self-hosted RFC-8414 OIDC discovery.** Across 491 LJP-OSS cohort hosts and 2,455 OIDC discovery probes (5 ports x 491 hosts), zero hosts served a parseable OIDC discovery document, despite 496 returning HTTP 200 on the path. The 200s were wildcard/SPA absorbs, not IdP responses. This is class-typical: OpenAI-compatible API relays terminate the auth question at API-key check, not at OAuth2/OIDC.

**Insight #Cnd-221-B - Operator-class self-branding overwhelms tenant co-branding on HTML head surface for LLM-relay SaaS.** 431 of 491 hosts exposed parseable HTML head; 100% of populated `<title>` values resolved to operator product names (Sub2API / Grok2API / new-api / CRMEB), 0% to downstream-customer organizational branding. The HTML head is the operator\'s marketing surface, not the customer\'s identity surface. Customer attribution on this cohort class must move to API contract / model catalog / admin-panel data layer, not metadata.

## Files

- Raw evidence: `~/syllabus/cohort-gap-checks/check-221-idp-branding.jsonl` (3,928 lines, verbatim status + raw_excerpt + ts + URL)
- Probe source: `~/syllabus/cohort-gap-checks/probe-221.py`
- This synthesis: `~/syllabus/cohort-gap-checks/summary-221.md`
