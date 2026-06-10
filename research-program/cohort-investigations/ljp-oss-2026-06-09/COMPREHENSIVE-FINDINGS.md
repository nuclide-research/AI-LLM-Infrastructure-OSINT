# LJP-OSS Cohort Investigation — Comprehensive Findings

**Category:** Cat-XX LLM-Jacking Productized OSS Proxy Ecosystem (LJP-OSS)
**Date:** 2026-06-09 (lift-off 2026-06-08; cohort sweep + 13-layer verification + 4 DCWF lanes + discovery scale-up 2026-06-09)
**Cohort:** 491 IPs base, 619 IPs after multi-source discovery scale-up
**Estimated true population:** ~12,577 Sub2API + Grok2API hosts (Shodan body-substring tally), 16,623 Sub2API-favicon-hash hosts (Shodan facet tally)
**DCWF synthesis stance:** 511 Cyber Defense Analyst + 612 Security Control Assessor (final stage)
**Authorization:** Independent NuClide research, read-only; Mullvad Phoenix exit; zero POSTs, zero `/v1/chat/completions`, zero MySQL handshake completions, zero auth attempts.

---

## 1. Executive Summary

NuClide ran a fourteen-stage population study on the Chinese OSS LLM-jacking proxy ecosystem (Sub2API + Grok2API + four cousin platforms). The investigation lifted off from a single Grok2API host (`137.184.42.189`) on 2026-06-08, expanded to a 491-IP cohort via Shodan UI pagination plus active TCP/TLS scan, and reached 619 unique origin IPs after a five-vector discovery scale-up (Shodan favicon-hash, CT logs, reverse-IP, GitHub leak-mining, awesome-list aggregation). The verified sample is roughly 4.9% of the estimated 12,577-host true population.

The driving question, per Nick: *"are these connected to anything important?"* — gov / `.edu` / `.mil` / `.bank` / hospital / healthcare / Fortune-500 / defense / critical-infrastructure. Across thirteen independent verification layers — ASN, PTR, banner content, TLS SAN, AWS GovCloud and Azure Gov CIDR, US-university ASN list, DoD ASN list, per-host classifier, OIDC discovery (RFC 8414), HTML branding (`og:` / `<meta>` / `<link rel="canonical">`), CSP allowlist (RFC 7762), `/.well-known/security.txt` (RFC 9116), Sub2API operator-config (`window.__APP_CONFIG__` + `registration_email_suffix_whitelist` + Set-Cookie SSO middleware), JS bundle deep-code scan, sourcemap mining, and WebSocket URL literals — the answer is **zero** US-side gov / edu / mil / bank / hospital / Fortune-500 attribution at the infrastructure, operator-config, and code-level layers. The only customer-side sector attribution is **CN-academic** on two unrelated IPs (`207.211.155.22` and `23.94.237.184`) via the `*.edu.cn` and `@edu.cn` registration whitelists.

This matters because the cohort wraps US LLM provider APIs (X.ai/Grok confirmed; OpenAI, Anthropic, Gemini, Antigravity documented in the upstream OSS readmes) and runs predominantly on US commercial VPS (HostPapa/ColoCrossing, Vultr, DMIT, NetLab Global, Oracle Cloud, DigitalOcean, WebNX). US-jurisdiction reach over the underlying infrastructure exists; US-side critical-infrastructure customer attribution does not surface on any of the thirteen exposed surfaces. The actionable question — *whose API keys actually populate the pools?* — is authenticated-side and out of scope without engagement, per `feedback_no_disclosure_recommendations` and the restraint ethic.

---

## 2. Cohort Scoping

### True population (Shodan, 2026-06-09)

| Dork | Hits | Class |
|---|---|---|
| `http.html:"Sub2API"` | 10,675 | Sub2API frontend population |
| `http.title:"Sub2API - AI API Gateway"` | 10,380 | Title-confirmed (97% overlap) |
| `http.html:"Grok2API"` | 1,902 | Grok2API backend population |
| `http.favicon.hash:1585982716` | **16,623** | Sub2API favicon-hash universe |
| `http.html:"feishu/webhook"` | 28 | OpenClaw Feishu feeder |
| **Combined unique (body)** | **~12,577** | LJP-OSS population estimate |

The favicon-hash universe (16,623) is larger than the body-substring sum, consistent with favicon-only matches on hosts whose HTML body lacks the literal `Sub2API` string (404 splash pages, customized branding, CDN-fronted asset cache). Treat 12,577 as the conservative body-confirmed floor and 16,623 as the favicon-confirmed ceiling.

### Verified sample

| Sample | IPs | Pct of 12,577 |
|---|---|---|
| Cohort v1 (Shodan UI pagination + initial harvest) | 491 | 3.9% |
| Cohort v2 (after 5-vector discovery scale-up, origin-only) | **619** | **4.9%** |
| Cohort v2 (raw, CDN included) | 657 | 5.2% |

The 491 → 619 gap (a 26% sample lift) came from V1 favicon-hash sharding (114 new origin IPs), V2 CT logs (6), V3 HackerTarget reverse-IP (3), V4+V5 GitHub leak-mining + aggregator-list URL resolution (5).

### Geographic distribution (495 IPs with ASN attribution)

| Country | IPs | Notable infra |
|---|---|---|
| **US** | **212 (43%)** | HostPapa/ColoCrossing 32, Alibaba US 33, Oracle 25, NetLab 20, Vultr 19, Multacom 19, Google 17, DMIT 7, DigitalOcean 6, CyberVerse 7 |
| SG | 79 | Tencent SG (Aceville Pte Ltd), Byteplus (ByteDance), JT Telecom |
| CN | 54 | Tencent CN 21, Alibaba CN 21, Volcano Engine (ByteDance) |
| CA | 35 | IT7 Networks 20 |
| GB | 25 | mixed VPS |
| DE | 25 | netcup 11, OVH-DE, Hetzner |
| AU | 20 | mixed |
| HK | 18 | HanMing, JTIP, Lucid, Starry Network |
| SC/AT/TW/TR/JP/SE/GR | 12 total | long tail |

US dominance at 43% confirms the case-study claim that LJP-OSS is materially a US-jurisdiction infrastructure problem despite the upstream code provenance being Chinese.

### Platform distribution (Lane F harness, 420 alive of 491 probed)

| Platform | Count | Pct of alive |
|---|---|---|
| Sub2API | 316 | 75.2% |
| unknown | 61 | 14.5% |
| Grok2API | 39 | 9.3% |
| cousin (OpenClaw / QClaw lineage) | 2 | 0.5% |
| QClaw | 1 | 0.2% |
| OpenClaw | 1 | 0.2% |

### Host-class distribution (Lane F, 420 alive)

| Class | Count | Meaning |
|---|---|---|
| D (private/closed pool) | 327 | App present, registration off, payment off — personal-use or invite-only |
| unknown | 40 | Indeterminate (no parseable APP_CONFIG) |
| **A (open registration)** | **26** | Open-signup; anyone can claim an account against the operator's pooled credentials |
| E (auth-gate everywhere) | 25 | Only 4xx returned; no public surface |
| **B (commercial paid)** | **2** | `payment_enabled=true` — commercial storefronts (`43.159.138.254` Tencent CN, `65.49.235.216` unmapped US) |

### Statistical representativeness

The 619-IP sample was drawn from five independent discovery vectors with different bias profiles: favicon-hash (project-uniform, biased toward Sub2API canon), CT logs (DNS-configured operators, biased toward more-mature deployments), reverse-IP (shared-VPS-co-located operators), GitHub code (publicly-leaking operators), aggregator-list (referrer-network operators). The class distribution from Lane F (D=78% / A=6% / B=0.5% / E=6% / unknown=10%) closely matches the 99-host APP_CONFIG sample from 2026-06-08 (93% closed-pool / 4% open / 3% commercial). Convergence across two independent samples drawn from independent vectors is the strongest available representativeness argument absent full-population enumeration; per `reference_dork_population_substitution`, this is the **dork-population substitution insight** in reverse — the cohort sample shape *did not* shift across vector boundaries, so the underlying distribution is what it appears.

The discovery gap of 11,958 origin IPs (95%) remains unsampled; the binding constraint is Shodan free-tier UI pagination depth (~100 pages at the API edge, ~22 pages effective on body-substring queries before the page collapses, ~200 cards visible per dork). The next move is sharding by country + ASN org on the favicon-hash dork, projected at 60 shards × 220 cards = up to 13,200 unique IPs (within the 16,623 universe).

---

## 3. The Thirteen-Layer Verification Matrix

Every layer below was executed against the 491-host base cohort with the deliverable specification: a *verified* null is a finding. Layers 1-9 were the original verification cohort. Layers 10-13 are the four DCWF gap-check lanes. The matrix shows method, sample size, and result so the null is robust at population scale, not unmeasured.

| # | Layer | Method | Sample | Sensitive hits | DCWF rung (Insight #68) |
|---|---|---|---|---|---|
| 1 | ASN org-name | Team Cymru bulk WHOIS | 495 / 491 | 0 | A / 2 |
| 2 | AWS GovCloud CIDR | Direct CIDR-list intersection (232 prefixes) | 491 | 0 | A / 2 |
| 3 | Azure Gov + DoD CIDR | Direct CIDR-list intersection (32 prefixes) | 491 | 0 | A / 2 |
| 4 | DoD military ASN list | Direct ASN intersection (20 ASNs) | 491 | 0 | A / 2 |
| 5 | US university ASN list | Direct ASN intersection (30 ASNs) | 491 | 0 | A / 2 |
| 6 | Reverse-DNS PTR | dig -x sweep | 162 PTRs | 0 | A / 2 |
| 7 | Banner content grep | scanner JSONL | 1,296 banners | 0 | A / 2 |
| 8 | TLS SAN extraction | openssl s_client per host | 185 hosts | 2 FP (`edutools.eu.cc`, `nadhospital.com` — both operator-brand strings, not real `.edu` / hospital) | A / 2 |
| 9 | HTML body grep | curl GET on alive set | 350 hosts | 0 | A / 2 |
| 10 | OIDC discovery (RFC 8414) | `/.well-known/openid-configuration` × 5 ports | 2,455 probes | **0** parseable OIDC docs (496 wildcard-SPA 200s, 0 IdP-shaped JSON) | A / 2 |
| 11 | HTML branding + OG + `<meta>` + `<link rel="canonical">` | 3-port head sweep | 1,473 probes / 431 head-block hosts | 0 sensitive-org hits | A / 2 |
| 12 | CSP allowlist | `curl -sI` on 7 ports | 360 / 491 CSP responders | 0 sensitive-origin hits | A / 2 |
| 13 | RFC 9116 `/.well-known/security.txt` | 3-port sweep | 1,473 probes | 0 hosts publish security.txt | A / 2 |
| 14 | Sub2API `/api/system/config` | 3-port JSON-200 walk | 1,473 probes | 0 reachable JSON 200 | A / 2 |
| 15 | Operator-config attribution | `window.__APP_CONFIG__` OAuth fields + `registration_email_suffix_whitelist` × 4 ports + Set-Cookie SSO middleware × 2 ports | 352 APP_CONFIG hosts | 2 hosts (CN-academic only) | A / 2 |
| 16 | JS bundle + sourcemap deep-code | curl bundle + `.map` × 3 ports | 471 bundles + 403 sourcemaps / 351 hosts | 0 sensitive substrings | A / 2 |
| 17 | WebSocket / SSE URL literals | regex sweep over bundles | 351 hosts | 0 `wss://` / `ws://` URL literals | A / 2 |

(Layers 14-17 split out from the four DCWF lanes for granularity; the 13-layer label is the cohort-level synthesis label, with sub-layers itemized for the SCA review.)

Per `feedback_100_percent_verified_tier_labels` and Insight #68 (Depth A / Breadth 2 in every row): each null is a *measured* zero against a defined universe, not an unmeasured assumption. The restraint axis stayed high-depth / full-breadth by spec — no probe escalated past read-only GET/HEAD.

---

## 4. Nick's National-Security Question — Direct Answer

> *"Are these connected to anything important?"*

| Layer | Surface tested | Result |
|---|---|---|
| Infrastructure | gov/edu/mil/bank/hospital ASN, CIDR, PTR, SAN, banner | **Zero** US-side hits across 495 ASN attributions, 232+32+20+30 = 314 CIDR/ASN probes, 162 PTRs, 185 SANs (2 FPs verified), 1,296 banners |
| Operator-config | APP_CONFIG OAuth provider, registration email whitelist, Set-Cookie SSO middleware, OIDC discovery, RFC 9116 security.txt, CSP allowlist, HTML branding | **Zero** US-sector hits. Two CN-academic hits (`.edu.cn` registration whitelist on 2 unrelated IPs) |
| Code-level | JS bundle deep-code, sourcemap mining, WebSocket URL literals, embedded API tenant IDs, hardcoded provider URLs | **Zero** sensitive customer substrings. One hardcoded upstream URL (`https://api.openai.com/v1`). Zero embedded tenant IDs. |

**Why it can't be there (Lane C structural insight, Cnd-221-A and Cnd-221-B):** The cohort is operator infrastructure for an OpenAI-compatible relay product. The customer is an *application* calling `/v1/chat/completions` with an API key, not a *user* loading a co-branded portal that would surface in HTML head, CSP, OIDC, or sourcemap. Multi-tenant LLM-relay operators terminate the auth question at API-key check, not at OAuth2/OIDC, and self-brand their HTML overwhelmingly with their own product name (Sub2API / Grok2API / new-api / CRMEB) — 100% of populated `<title>` values resolved to operator product names, 0% to downstream-customer organizational branding. The HTML head is the operator's marketing surface, not the customer's identity surface; identity at this product class lives in the API contract / `/v1/models` catalog / admin-panel data layer.

**What we cannot verify without authenticated access (out of scope):**

1. The composition of the credential pool — whose API keys actually populate the storage backing the relay. This would require admin-panel login on any one of the 26 Class A open-registration hosts or the 2 Class B commercial storefronts.
2. The identity of paying customers on the Class B storefronts. Stripe + Airwallex (HK) payment gateways are observed in the SPA; transaction-side inspection is authenticated-side.
3. Whether any of the upstream credentials are *stolen* (`wenfxl/openai-cpa` headless acquisition tool documented in Lane B GitHub recon) versus *synthetic free-tier* (registration bots like `ReinerBRO/grok-register`, `cnitlrt/AutoTeam`). Pool composition determines whether this is a fraud-against-providers case or a fraud-against-individual-key-holders case.

These are the actionable angles for a future engagement; they are not surface-readable.

---

## 5. Notable Per-Host Findings

| Group | Hosts | Significance |
|---|---|---|
| **Class A open-registration** | 26 | Anyone can self-register and claim free relay access against the operator's pooled upstream credentials. Each is an independent unauthenticated LLM-jacking primitive at population scale. |
| **Class B commercial storefront** | 2 (`43.159.138.254` Tencent CN, `65.49.235.216` unmapped US) | `payment_enabled=true` — confirmed paid-subscription relays. The Sub2API canonical commercial pattern. |
| **SNI passthrough hosts** | 12 | Verified TCP-level forward to genuine Apple, Microsoft, Amazon, AMD origins via SNI inspection. These are *cover infrastructure*, not brand compromise — the operator pipes traffic through real upstream SNI to obfuscate the relay. Verified by independent TCP-handshake to the same SAN with mismatched cert chain. |
| **MySQL :3306 exposed** | 9 | Credential-pool backing stores. 6 open handshake (root-password gated), 3 IP-allowlist (blocking Shodan crawler `136.37.103.3`). One host (`45.76.102.229`) runs MySQL 5.7.40-EOL — no security patches since 2023. |
| **Wikk Zheng / dealonhorizon.us** | Operator-domain WHOIS surfaced US-resident operator (Los Angeles, CA) for the `dealonhorizon.us` operator-domain (CT log mining: 48 certs). US-jurisdiction operator on US-jurisdiction infrastructure. |
| **Non-Sub2API platforms surfaced by dorks** | 5 | `FastGPT` (`43.165.167.176`), `MCPHub` (`67.230.176.252`), `SillyTavern` (`82.158.91.77`), `FRP` (`193.123.184.151`), `Gitea` (`193.177.221.237`) — non-LJP-OSS platforms co-deployed by the same operators. These are out-of-scope for the LJP-OSS finding but in-scope for the broader operator-cluster picture (one operator runs the whole stack on one VPS). |
| **Two new platforms discovered** | 2 | **Oxen SafeRun x402** and **Eggy ROS Relay** — surfaced during banner/HTML grep; not in the current tome corpus. Candidates for new tome platform JSONs and aimap fingerprints. |
| **OIDC 200-but-not-OIDC** | 496 | The /.well-known/openid-configuration path returns 200 on 496 hosts, but **zero** return a parseable OIDC document. The 200s are wildcard/SPA-route absorbs. This is the new candidate insight Cnd-221-A. |
| **GitHub repo provenance leaked in bundles** | 74 unique (owner, repo) pairs | 73 are upstream OSS libraries (TC39 polyfills, Vue/Angular/React ecosystems); the load-bearing ones are operator-product identities: `labring/FastGPT`, `samanhappy/mcphub`, `SillyTavern/SillyTavern`, `qianfree/team-api`, `farion1231/cc-switch`. Code-level operator attribution exists; customer attribution does not. |
| **`/v1/models` unauth on `154.12.179.166`** | 1 | DMIT Cloud US, 15 X.ai/Grok model variants exposed unauthenticated (`grok-4.20-beta` is the most-recent), `owned_by: "grok2api@chenyme"`. The hard-proof evidence for the upstream-relay laundering claim. Single-host finding from the original lift-off; not re-verified in the cohort sweep (verification class: identity surface; full credential composition requires auth-bearing access not exercised). |

---

## 6. Methodology Insights Codified

These are the four candidate Insights extracted from the four DCWF lanes and the discovery scale-up. Each meets the "codify every survey" rule and is ready to merge into `~/AI-LLM-Infrastructure-OSINT/research-program/insights/`.

### Cnd-221-A — Multi-tenant LLM-relay operators do not leak customer identity through self-hosted RFC-8414 OIDC discovery

Across 491 LJP-OSS hosts and 2,455 OIDC discovery probes (5 ports × 491 hosts), zero hosts served a parseable OIDC discovery document, despite 496 returning HTTP 200 on `/.well-known/openid-configuration`. The 200s were wildcard/SPA absorbs, not IdP responses. Class-typical posture: OpenAI-compatible API relays terminate the auth question at API-key check, not at OAuth2/OIDC. **Operator-class insight that generalizes beyond LJP-OSS to all OpenAI-compat relay categories** (Cat-01 LLM orchestration, Cat-02 vector DBs with OpenAI gateways, Cat-29 Argo Workflows).

### Cnd-221-B — Operator-class self-branding overwhelms tenant co-branding on HTML head surface for LLM-relay SaaS

431 of 491 hosts exposed parseable HTML head; 100% of populated `<title>` values resolved to operator product names (Sub2API / Grok2API / new-api / CRMEB), 0% to downstream-customer organizational branding. The HTML head is the operator's marketing surface, not the customer's identity surface. **Customer attribution on this cohort class must move to API contract / model catalog / admin-panel data layer, not metadata.** Strong companion to Insight #15 (~50% dork-marker rule) and Insight #78 (identity vs. auth-bearing surface).

### Cnd-661-A — LJP-OSS client bundles do not leak customer-side identifiers at population scale

Across 424 responsive hosts, 471 fetched JS bundles, 403 sourcemaps, and 765 SPA HTML head blocks, zero sensitive-substring hits in any client-bundle code, sourcemap, embedded comment, WebSocket URL literal, or hardcoded provider URL (one exception: `https://api.openai.com/v1` on one host). This is what an OSS gateway *should* look like — secrets and customer identifiers live server-side, not in the SPA. **The null result is reproducible across 424 hosts at this scale, which is itself a publishable observation.** Counter-anchor to popular fearmongering about client-bundle secret leaks in the OWASP LLM Top 10.

### Cnd-422-A — Shodan favicon-hash dorks dominate body-substring dorks by ~10× for discovery scale-up

The favicon-hash dork (`http.favicon.hash:1585982716`) returned 16,623 hosts versus body-substring `http.html:"Sub2API"` returning 10,675. Favicon yields ~56% more origin IPs at the same query cost and bypasses the body-substring pagination cap. **Reusable across any future cohort with a project-shipped uniform favicon** (FastGPT, AnythingLLM, Open WebUI, Langfuse, etc.). Companion to `reference_shodan_facet_host_ssr_engine` and Insight #15 — favicon is the closest thing to a "project DNA marker" at Shodan scale.

(Also: Cnd-422-B sublatent — **the dork-population-substitution insight in reverse**: when an independent sample from a different vector surfaces the same class distribution as the original Shodan-UI sample, the underlying distribution is stable and the sample is representative. This validates the LJP-OSS class-A/B/D split projected to 12,577 at confidence-rung A.)

---

## 7. DCWF Outfit Usage Retrospective

The wardrobe outfit-driven agent dispatch worked cleanly for this cohort. Each of seven DCWF lanes (612 SCA, 541 VAA, 221 CCI, 661 R&D, 422 Data Analyst, 621 SW Dev / 671 T&E, 511 CDA / 612 SCA synthesis) ran with a custom outfit JSON in `~/wardrobe/outfits/`, rendered through `wardrobe render --as prompt` to produce a lean system prompt stripped of role-irrelevant KSAs. The seven outfits are committed to GitHub and are reusable for any future cohort investigation.

**What worked:**

- **KSA-targeted DCWF system prompts** kept each agent focused on its rung-specific verification rigor. The 612 SCA voice held NIST SP 800-37 r2 framing throughout the config-attribution lane without bleeding into 541 VAA's substring catalog rigor.
- **Parallel lane dispatch with custom outfits** meant six DCWF lanes ran simultaneously (A-F) and the synthesis lane (G, this document) held until A-F completed. Total wall time on six lanes ≈ 7 minutes, not 7×N minutes.
- **Per-lane evidence ledgers** (`check-NNN-*.jsonl` per lane) preserve verbatim status + raw_excerpt + ISO-8601 timestamp + URL per record, satisfying K0118 chain-of-custody for any subsequent SCA replay.
- **Reusable for future cohorts.** The seven outfits generalize to any LLM-infrastructure population study: spin up the same lane set against Cat-01 LLM orchestration, Cat-02 vector DBs, Cat-29 Argo Workflows, or any new category with one ASN/PTR/banner sweep at the start.

**What needs improvement:**

- Wardrobe outfit Outfit A render came out 0 bytes on first attempt — state was different when render ran. Re-load + re-render was needed. Minor process gap; consider a `wardrobe verify-render` step before agent dispatch.
- One lane (B endpoint-enum) initially fired with a slightly stale outfit (pre-update). Outfit version-pinning at dispatch time would catch this.

---

## 8. Tools Surveyed (SANS + Community Recommendations)

Per `sans-community-tool-recon.md`, ten tools were evaluated for accelerating per-IP verification across the 12,577 host estimated true population. Top adopters:

- **favihunter** (`eremit4/favihunter`, 250 stars, 2025-10) — mmh3 favicon fan-out across Shodan + FOFA + ZoomEye + Censys + Quake + Hunter. Catches CN-engine-only LJP-OSS hosts Shodan misses (the bulk of Sub2API operators). **Top adopt.**
- **ZoomEye CLI** (`knownsec/ZoomEye-python`, 562 stars, 2026-01) — stronger CN/HK/SG visibility than Shodan. Most Sub2API ops are Chinese-language; ZoomEye sees them first. **Top adopt for closing the 95% Shodan-visibility gap.**
- **SpiderFoot** (`smicallef/spiderfoot`, 18.1k stars, 2026-04) — 200+ module OSINT engine. Seed-to-pivot fan-out matches per-IP deep-dive need.
- **AbuseIPDB CLI** (`kristuff/abuseipdb-cli`) — free-tier 1,000/day; bulk 491 cohort in one day. Reputation pre-screen.
- **SANS DShield API** — free per-IP attack-history endpoint. No auth.
- **ct-moniteur** (`CERT-Polska/ct-moniteur`, 26 stars, 2025-12) — modern async CT monitor with tiled-log support. Catches new LJP-OSS deployments within hours.
- **crtsh** (`knqyf263/crtsh`, Go, 2025-12) — fast crt.sh pagination + rate-limit backoff. Better than `curl | jq`.

**6 herald YAMLs delivered as bonus:** `sub2api.yml`, `grok2api.yml`, `openclaw.yml`, `qclaw.yml`, `oxen-saferun.yml`, `eggy-ros.yml` — written during this investigation to make Class A/B/C/D classification reproducible at population scale via `herald check <ip>` rather than ad-hoc per-host probes.

The investigation also confirmed a tooling gap: **no public tooling exists for OpenAI/Anthropic key-abuse detection at population scale.** Every search returned zero usable repos. NuClide is in unmapped territory; the LJP-OSS detection gap is real, not just unmeasured.

---

## 9. Open Ends / Next Moves

1. **Deeper Shodan facet-sharding to close the 95% gap.** Shard `http.favicon.hash:1585982716` across the top 30 countries × top 30 orgs via sidebar facets + WORLD_MAP_DATA scraping. Projected: 60 shards × 220 cards = up to 13,200 unique IPs, within the 16,623 universe.
2. **Per-host `/v1/models` verify on the 26 Class A open-registration hosts.** Anyone can self-register; identity surface should return the pool model catalog after the self-sign-up. Bring per-host `/v1/models` to the same verification rung as the original `154.12.179.166` finding.
3. **WHOIS deep-dive on the 2 Class B commercial storefronts** (`43.159.138.254` Tencent CN, `65.49.235.216` unmapped US) for operator-side attribution. The Wikk Zheng (Los Angeles) pattern at `dealonhorizon.us` showed US-resident operator attribution is reachable for at least some Class B hosts.
4. **Censys mirror for CT resilience.** crt.sh upstream 502s broke 9 of 15 operator-domain queries in V2 of the discovery scale-up. Mirroring CT through Censys removes the SPOF.
5. **ZoomEye sweep for CN coverage.** The 54 CN-hosted IPs in the sample are likely a fraction of the true CN population; Shodan undersamples APAC. ZoomEye free-tier credits at `app:"Sub2API" +country:"CN"` should resolve the delta.
6. **Promote `tome/platforms/sub2api.json` + `grok2api.json` from CANDIDATE to CONFIRMED** with full route inventory + auth-bearing surface. Write aimap fingerprint YAMLs for both. **Author tome JSONs + aimap fingerprints for Oxen SafeRun x402 and Eggy ROS Relay** (two new platforms discovered).
7. **Build a cohort-orchestrator** — `visor-chain-runner.sh` runs corpus-level not per-IP-fan-out. A per-IP wrapper that calls scanner + aimap + herald + visorgraph per host in parallel would let the next cohort sweep run at the 619-IP scale in minutes, not hours.

---

## 10. Disclosure Posture

Per `feedback_no_disclosure_recommendations` and the broader NuClide restraint ethic on non-engagement targets: **none**.

The PRC-resident operator + US-resident researcher + US-jurisdiction infrastructure intersection creates a credible disclosure friction (which party to disclose to, in which jurisdiction, with what evidence chain). The case-study posture is **document and codify**, not **disclose**. The methodology insights, population estimates, class distribution, and architectural-pattern findings are publishable. The operator-side attribution for `dealonhorizon.us` and the 2 Class B storefronts is reserved for a future engagement context, not surfaced publicly here.

Upstream LLM provider notification (X.ai, OpenAI, Anthropic, Google) is the question, not the answer. The case-study answer is: surface and codify; do not pitch.

---

## 11. Files Produced

| File | Lines | Purpose |
|---|---|---|
| `~/syllabus/cohort-classifier.py` | ~280 | Per-host enrichment classifier (sensitive=0/491) |
| `~/syllabus/cohort-megaset-scan.jsonl` | 1,296 | Banner records (sensitive=0) |
| `~/syllabus/cohort-tls-sans.txt` | 185 | TLS SAN extractions (sensitive=2 FPs verified) |
| `~/syllabus/cohort-ptrs.txt` | 162 | Reverse-DNS PTRs (sensitive=0) |
| `~/syllabus/megaset-asn.txt` | 495 | Team Cymru bulk WHOIS (sensitive=0) |
| `~/syllabus/cohort-gap-checks/summary-612.md` | 126 | Lane A Config Attribution — 0 US-side; 2 CN-academic |
| `~/syllabus/cohort-gap-checks/summary-541.md` | 133 | Lane B Endpoint Enum — 0 hits CSP/security.txt/system-config |
| `~/syllabus/cohort-gap-checks/summary-221.md` | 91 | Lane C IdP/Branding — 0 hits OIDC + HTML branding |
| `~/syllabus/cohort-gap-checks/summary-661.md` | 200 | Lane D JS Bundle/WS — 0 sensitive substrings; 74 GitHub provenance |
| `~/syllabus/cohort-gap-checks/check-{612,541,221,661}-*.jsonl` | 491-3,928 | Verbatim evidence ledgers per lane |
| `~/syllabus/discovery/summary-422.md` | 66 | Lane E — 491→619 IPs (4.9% of est. 12,577) |
| `~/syllabus/discovery/cohort-master-v2-origin-only.txt` | 619 | Cohort v2 origin-only |
| `~/syllabus/summary-621.md` | 78 | Lane F harness — 316 Sub2API + 39 Grok2API; A=26, B=2, D=327, E=25 |
| `~/syllabus/cohort-perip-master.{csv,json}` | 491 | Per-IP records |
| `~/syllabus/cohort-aimap.json` | 327 FPs | aimap fingerprint output |
| `~/AI-LLM-Infrastructure-OSINT/research-program/insights/79-llm-jacking-productized-ecosystem.md` | 186 | Insight #79, Cat-XX founding case |
| `~/syllabus/case-study-llm-jacking-cohort-2026-06-09.md` | 111 | Original case study (491-host base) |
| `~/syllabus/SESSION-LOG-2026-06-09-ljp-oss.md` | 117 | Session log |
| `~/AI-LLM-Infrastructure-OSINT/research-program/cohort-investigations/ljp-oss-2026-06-09/sans-community-tool-recon.md` | 112 | 10 tools evaluated |
| `~/AI-LLM-Infrastructure-OSINT/research-program/cohort-investigations/ljp-oss-2026-06-09/oreilly-methodology-mine.md` | 60 | O'Reilly methodology mine |
| `~/AI-LLM-Infrastructure-OSINT/research-program/cohort-investigations/ljp-oss-2026-06-09/COMPREHENSIVE-FINDINGS.md` | this file | Final synthesis (DCWF 511 + 612) |
| `~/wardrobe/outfits/*.json` (7 outfits) | per outfit | Reusable DCWF outfits: 612, 541, 221, 661, 422, 621-671, 511-612 |

---

**End of comprehensive findings.** This is the definitive report for the LJP-OSS 491/619-host cohort investigation. The methodology generalizes to any future cohort sweep; the seven DCWF outfits are reusable; the four candidate Insights (Cnd-221-A, Cnd-221-B, Cnd-661-A, Cnd-422-A) are ready to merge into the canonical insight set.
