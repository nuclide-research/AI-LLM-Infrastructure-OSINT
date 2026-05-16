---
title: "Discovery-channel coverage is multiplicative — Shodan-walk and masscan-on-cloud-prefixes are complements, not substitutes"
insight_number: 23
date: 2026-05-15
tags:
  - methodology
  - discovery
  - shodan
  - masscan
  - population-survey
related_research:
  - case-studies/commercial/ollama-population-survey-2026-05-15.md
  - case-studies/commercial/ollama-cloud-survey-2026-05.md
  - case-studies/commercial/ollama-tier2-cloud-survey-2026-05.md
source: case-studies/commercial/ollama-population-survey-2026-05-15.md
---

# Methodology Insight #23: Discovery-channel coverage is multiplicative

## The insight

A population survey can be sourced two ways: **masscan-on-cloud-prefixes**
(scope a set of cloud /16 ranges, scan a port across all of them) or
**Shodan-walk** (page through the Shodan-indexed result set for a brand
dork or service-product facet). Each method has a coverage profile, and
those profiles do not overlap.

The methodology lesson — derived from running the same platform (Ollama)
through both methodologies four weeks apart on overlapping populations —
is that **discovery-channel coverage is multiplicative**: a survey aimed
at population-scale completeness must use both. Picking one and treating
the other as redundant produces a corpus that is wrong in a way that
tracks the discovery channel, not random noise.

## The evidence

The prior tier-1+2 Ollama surveys (2026-05-03 and 2026-05-04) masscanned
**5.38M IPs across six budget-cloud /16 ranges**: DigitalOcean, Hetzner,
Vultr (28 /16s), Scaleway, OVH, Linode (76 /16s combined). Output:
**1,192 confirmed unauth Ollama instances**.

The 2026-05-15 Shodan-walk methodology paged through the Shodan-indexed
Ollama population directly: `product:Ollama port:11434` (18,191 unique
IPs) + `http.html:"Ollama is running"` across 17 country slices (20,890
unique IPs). Union: **25,092 unique candidate IPs → 16,473 confirmed
unauthenticated Ollama** — a **13.8× catalogue extension** of the prior
1,192.

The methodologies surfaced disjoint populations:

| Cloud tier in the Shodan-walk that prior masscans never scoped | Hosts |
|---|---|
| **AWS** (Amazon.com Inc, AWS DataServices ×7 subsidiaries) | **~3,720** |
| Oracle Corporation | 329 |
| Aliyun + Tencent (Chinese clouds) | ~516 |
| Korea Telecom (consumer ISP) | 223 |
| Google LLC + GCP | (smaller, but represented) |
| University / academic / research networks | **117 hostnames** in harvest |

The prior masscan corpus included precisely zero of these. The
methodology's "Ollama lives on tier-2 budget clouds" assumption was
false at population scale, and the only way to discover this was to
walk the other channel.

## Why each method misses what it misses

**Masscan-on-cloud-prefixes catches what Shodan misses:**
- Hosts Shodan hasn't crawled yet (new deployments, blocked-by-firewall,
  rate-limited operators)
- Hosts where the crawler reached the IP but didn't see the canonical
  HTTP response (e.g., default `/` returns 404 but `/api/tags` works)
- Operators who deliberately block Shodan's scanner ranges
- Hosts on cloud prefixes the operator chose for low-friction GPU but
  whose HTTP response doesn't index distinctively

**Shodan-walk catches what masscan-on-cloud-prefixes misses:**
- Hosts on non-default ports (the masscan's `-p 11434` filter is fragile;
  Shodan's `http.html:` matches anywhere)
- Hosts on clouds outside the masscan's chosen tier (AWS, Azure, Oracle,
  GCP, Chinese clouds, ISP-customer, residential, academic)
- Hosts whose port-11434 returns nothing but whose `/` body contains the
  brand string
- Universities, research labs, government infra — none of which live on
  the budget cloud tier-2

## The Shodan-walk subtleties (pre-publication caveats)

Two operational subtleties matter when sourcing a survey from Shodan:

1. **Pagination depth ceiling.** On the basic Shodan plan, the
   `/shodan/host/search` API returns HTTP 500 after a depth cap (~page 70
   for high-population dorks). A dork that reports 40,508 total hits
   delivers only ~6,900 records before the cap fires. The methodology
   workaround: split the population query along a facet that produces
   sub-queries under the depth ceiling. The Ollama survey split
   `http.html:"Ollama is running"` along `country:` — 17 country slices,
   each well under the depth limit. Net-new recovery: **20,890 unique
   IPs** vs the truncated 1,611.

2. **Dork-population dedup rate.** Raw Shodan hit counts overstate the
   unique-IP population. `http.html:"Ollama is running"` returned 6,900
   records but only 1,611 unique IPs (4.3 records per IP); same IP shows
   up on different ports, different crawl timestamps, different banner
   prefixes. Always dedup on `(ip_str, port)` before counting.

## How to apply

When designing a population survey of any AI-stack platform:

- **Use both channels** unless one is provably exhaustive of the other.
  For Ollama, both channels are required.
- **Quote both numbers in the case study**. The 1,192 from masscan and
  the 16,473 from Shodan-walk are both correct — they answer slightly
  different questions. The cross-survey number (the union) is the
  population estimate.
- **Document the discovery channel as a methodology axis** in any
  per-platform survey. "We scoped tier-2 budget clouds" is a real
  scope-limitation that future surveys must extend.
- **Treat the multiplicative finding as itself publishable.** The
  delta between two channels' populations is intelligence about which
  cloud tiers, ISPs, and operator demographics the platform actually
  lives on.

## Anti-patterns (failure modes)

- **"Shodan is comprehensive"** — it isn't. The masscan recovered ~342
  hosts from DO/Hetzner/Vultr that the prior Shodan dork wouldn't have
  found at the time of that survey.
- **"Masscan is comprehensive"** — it isn't. The Shodan-walk recovered
  ~15,000 hosts that the tier-1+2 cloud-prefix masscans never touched.
- **"One Shodan dork covers the population"** — the `product:` facet and
  the `http.html:` facet returned overlapping-but-different populations
  (18,191 vs 20,890 unique IPs, with only 13,989 overlap). The product
  facet catches banner-indexed hosts; the html facet catches body-text
  hosts. Use both, dedup on `(ip, port)`.

## Pairs with

- [[insight-04-whois-driven-contact-resolution]] — once the discovery
  surfaces a new host, attribution is WHOIS-driven; doesn't depend on
  the discovery channel.
- [[insight-15-dork-hits-vs-platform-instances]] — Shodan hit counts ≠
  platform-instance counts; verification still required.
- [[insight-21-port-first-discovery-for-low-footprint-platforms]] —
  port-first vs brand-dork is a different axis (within Shodan); this
  Insight is across discovery channels (Shodan vs masscan).

## See also

- `case-studies/commercial/ollama-population-survey-2026-05-15.md` —
  the survey this insight was extracted from.
- `case-studies/commercial/ollama-cloud-survey-2026-05.md` and
  `ollama-tier2-cloud-survey-2026-05.md` — the prior masscan surveys
  that this complements.
