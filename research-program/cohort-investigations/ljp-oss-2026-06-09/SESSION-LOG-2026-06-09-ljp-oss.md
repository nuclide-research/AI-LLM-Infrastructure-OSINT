# LJP-OSS Cohort Investigation — Session Log

**Date:** 2026-06-09
**Category:** Cat-XX LLM-Jacking Productized OSS Proxy Ecosystem (Insight #79)
**Goal:** Thorough per-IP investigation of all ~12,577 Chinese OSS LLM-jacking proxy hosts to verify NONE are connected to anything important (gov/.edu/.mil/.bank/.hospital/healthcare/critical-infrastructure)

## What Worked

### Discovery
- **Sub2API favicon hash `1585982716`** (computed by jaxen pivot) is the single biggest population-discovery multiplier — bypasses the Shodan UI ~200-link cap entirely with one dork
- **`http.html:"Sub2API"` raw count** in Shodan returns ~10,675 — but pagination cap blocks full enumeration; need favicon dork
- **CT log mining via crt.sh** works free, returned 154 OpenClaw certs, 48 dealonhorizon, 20 sub2api, 16 vacelight, 7 umom
- **Operator-domain WHOIS** worked — surfaced Wikk Zheng (Los Angeles, CA) as US-resident operator for dealonhorizon.us
- **HackerTarget reverse-IP** (50/day free) gave 5-15x multiplier per shared-VPS operator IP
- **GitHub gh search** auth'd successfully as `nuclide-research`; found supply chain (chenyme, Wei-Shaw, ReinerBRO, cnitlrt, qixing-jk, touwaeriol)

### Verification (9-layer null cohort verification across 491 IPs)
- **Team Cymru bulk ASN WHOIS** (1 connection, instant): 0 gov/edu/mil/bank ASN org-name matches
- **AWS GovCloud CIDR check** (232 prefixes): 0 hits
- **Azure Government + DoD CIDR check** (32 prefixes): 0 hits
- **DoD/military specific ASN list** (20 ASNs): 0 hits
- **US university common ASN list** (30 ASNs): 0 hits
- **Reverse DNS PTR sweep** (162 PTRs): 0 hits
- **TLS cert SAN extraction** (185 hosts): 2 substring matches (both verified FP — operator brand names "edutools.eu.cc" and "nadhospital.com")
- **Banner content grep** (1296 banners): 0 hits
- **HTML body grep** (350 alive hosts): 0 hits
- **Per-host classifier** (`cohort-classifier.py`): 0 sensitive flagged

### Architecture findings
- **SNI passthrough on 12 hosts** — verified TCP-level forward to real Apple/Microsoft/Amazon/AMD upstreams (NOT brand compromise; cover technique)
- **Sub2API APP_CONFIG sweep** (101 hosts parsed): 96% closed-pool, 3% commercial paid, 4% open registration
- **`/v1/models` unauth on 154.12.179.166**: 15 Grok variants pooled (DMIT Cloud US)
- **Operator-domain pivots**: api.yunjie.host, www.cfgo.shop, api.holdzywoo.top, api.htops.top, sub2api.org — all 3 of 4 traced to PRC registrars
- **5 commercial-class hosts** identified with Stripe + Airwallex (HK) payment integration
- **Sub2API issue "国安已经在找你了"** on GitHub (`Wei-Shaw/sub2api`): operators self-aware of legal exposure

### DCWF + Wardrobe
- **Wardrobe `try-on` + `render --as prompt`** workflow produced lean DCWF system prompts for each lane — strips unnecessary KSAs, keeps proficiency rungs + custom notes
- **7 custom outfits saved + committed to GitHub** (~/wardrobe/outfits/): reusable for any future cohort investigation
- **Per-lane agent dispatch with custom outfits** worked cleanly — each agent gets just the KSAs it needs, no role-irrelevant ceremony
- **DCWF role mapping** to lanes (Agent A research): 422 Data Analyst, 541 VAA, 612 SCA, 221 CCI, 661 R&D, 511 CDA, 621 SW Dev, 671 T&E, 731 Legal

### Tools
- **scanner** (Go): ~176 handshakes/sec; reliable TCP/TLS banner; works fine on 491 IPs in ~3 minutes
- **aimap** has built-in `-ports-class sub2api` (didn't know that before)
- **jaxen pivot** natively computes Shodan-compat mmh3 favicon hash
- **wardrobe** Python single-file CLI; 1281 atoms, fast lookup

## What Needs Improvement

### Tools that exist but have gaps
- **tome `sub2api.json` + `grok2api.json` are CANDIDATE status** — need to be promoted to CONFIRMED with full route inventory + auth-bearing surface
- **aimap has NO fingerprints for Sub2API / Grok2API** — they're new platforms. Need to write FP YAML.
- **herald has NO YAML configs for sub2api / grok2api** — need to author `~/herald/configs/sub2api.yml` for proper Class A/B/C/D classification at population scale
- **No cohort-orchestrator** — `visor-chain-runner.sh` runs corpus-level not per-IP-fan-out. Need a per-IP wrapper that calls scanner + aimap + herald + visorgraph per host in parallel.
- **No favicon-expander tool** — the favicon-hash dork (`http.favicon.hash:1585982716`) is the discovery key but we don't have a tool that automatically: pull favicon → mmh3 → query Shodan via Playwright → harvest → cross-dedupe.

### Investigations to extend
- **Customer-side credential attribution** — whose API keys are actually being pooled (would require admin panel access; out of scope without engagement)
- **Payment-side customer identity** — Stripe/Airwallex transaction inspection (out of scope)
- **Class A/B/C/D split at full population scale** — APP_CONFIG sample on 99 IPs showed 96% closed/4% open; need to validate across full 12K
- **Defensive operator playbook** — for the 4 hard-evidence Class B commercial storefronts

### Methodology gaps
- **No prior NuClide survey done discovery at 12K+ scale** with Shodan UI pagination broken (rate-limited + 200-link cap)
- **No prior NuClide survey did per-IP investigation orchestrator** running 7-tool chain per host across thousands
- **Insight #15 (~50% dork-marker rule)** suggests true Sub2API count is 6K-8K not 12,577

## What Wasted Time

- **Shodan UI re-pagination** after hitting rate limit — kept trying additional slicing rounds (r3, r4, r5, r6) that all returned 0 hits. Should have pivoted to favicon dork SOONER (cost: ~20-30 minutes).
- **Censys web UI Cloudflare challenge** — couldn't get past the JS challenge in Playwright session (cost: ~10 minutes)
- **Censys API credits exhausted** — `cencli search 'services.banner:"Sub2API"'` returned "insufficient balance" (need fresh credits or alternative)
- **HTML grep regex with `\b` word boundary** — broke under ugrep, had to re-run with POSIX-ERE (cost: 1 background run wasted, ~5 minutes)
- **HTML grep matching "chase" inside "purchase_subscription_enabled"** — 140 false-positive hits from the substring before I added word-boundary check (cost: minor, caught quickly)
- **aimap `-input` flag** — wrong flag (should be `-list`); first aimap run died immediately (cost: 1 background slot)
- **Browser SSL/socket errors** during the Mullvad VPN transition (Nick had VPN on/off) — caused some Playwright + Agent calls to fail (cost: variable)
- **Wardrobe outfit Outfit A render came out 0 bytes** — wardrobe state was different when render ran; had to reload + re-render
- **Asking before doing in early rounds** — clarifying questions cost momentum when Nick had clearly authorized "thorough investigation"

## Authorization Notes

Per Nick (2026-06-09):
- Agents authorized to **CREATE, BUILD, AND ACCESS any tool, script or utility needed**
- VPN was off briefly — caused socket errors; back on now
- Wardrobe can be used to **build custom DCWF outfits**, strip unnecessary attributes
- O'Reilly tool available for methodology lookup
- GitHub for SANS + community tools
- Censys is dead-end (credits exhausted, web UI Cloudflare-blocked) — use other avenues

## Reusable Artifacts

- `~/wardrobe/outfits/*.json` — 7 custom DCWF outfits (committed to GitHub)
- `~/syllabus/cohort-gap-checks/outfits/*.md` — rendered LLM prompts for each outfit
- `~/syllabus/cohort-classifier.py` — per-host enrichment classifier
- `~/syllabus/cohort-deep-probe.py` — per-IP probe orchestrator (Nick rejected; replaced with aimap+harness)
- `~/syllabus/case-study-llm-jacking-cohort-2026-06-09.md` — case study
- `~/syllabus/cohort-master-ips.txt` — 491 unique cohort IPs
- `~/syllabus/cohort-megaset-scan.jsonl` — 1296 banner records
- `~/syllabus/cohort-tls-sans.txt` — 185 host TLS SAN extractions
- `~/syllabus/cohort-asn.txt`, `~/syllabus/megaset-asn.txt` — Team Cymru bulk WHOIS
- `~/syllabus/cohort-ptrs.txt` — 162 reverse DNS results
- `~/syllabus/ct/*.json` — CT log mining results across 21 operator-domain substrings
- `~/AI-LLM-Infrastructure-OSINT/research-program/insights/79-llm-jacking-productized-ecosystem.md` — codified Insight

## Active Background Lanes (as of session log)

| Lane | DCWF outfit | Status |
|---|---|---|
| A | config-attribution-audit-612 | running |
| B | endpoint-enumeration-541 | running |
| C | idp-branding-attribution-221 | running |
| D | jsbundle-ws-deep-analysis-661 | running |
| E | discovery-scale-up-422 | running |
| F | per-ip-investigation-harness-621-671 | running |
| G | threat-scoring-synthesis-511-612 | held until A-F complete |

## Session Continuation — Lift-off #2 BentoML (2026-06-09 evening)

### Path 3: codified 4 Insights (#99-102) from LJP-OSS investigation
- #99 OIDC discovery not viable for LLM-relay customer attribution
- #100 Operator self-branding overwhelms tenant co-branding
- #101 LJP-OSS client bundles don't leak customer-side identifiers
- #102 Shodan favicon-hash dorks dominate HTML-body substring
- INDEX.md updated, committed to OSINT repo (commit 2846f2b)

### Path 1: fresh lift-off on BentoML
- Stage -1 OSINT brief delivered (8,670 stars, auth-OFF-by-default, 14 NVD CVEs)
- Stage 0d: tome platform JSON written (~/tome/platforms/bentoml.json), tome rebuilt, committed (bde8e27)
- aimap fingerprint already exists at fingerprints.go:2119 (BentoML, severity medium)
- Stage 0 Shodan harvest dispatched as sub-agent (browser sole instance locked due to MCP profile contention)

### Known issues
- Playwright browser locked by lingering MCP processes (chrome-devtools-mcp at PID 200667 holding profile); resolved by sub-agent dispatch with fresh context

### Reusable artifacts (committed)
- 7 DCWF outfits in OSINT repo at research-program/dcwf-outfits/
- 4 new Insights codified at research-program/insights/{99,100,101,102}-*.md
- 1 new tome platform at tome/platforms/bentoml.json
- 1 case study at syllabus/case-study-llm-jacking-cohort-2026-06-09.md (491-host LJP-OSS)
- 1 OSINT brief at syllabus/bentoml-stage-minus-1-osint.md
- Comprehensive findings at OSINT repo research-program/cohort-investigations/ljp-oss-2026-06-09/COMPREHENSIVE-FINDINGS.md

