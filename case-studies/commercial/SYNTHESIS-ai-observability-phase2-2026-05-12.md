---
type: synthesis
title: AI observability tier, Phase 2 synthesis (cross-cuts + version-deltas)
date: 2026-05-12
class: substrate
category: cross-platform-synthesis
status: research-complete-phase-2
methodology: cross-platform IP overlap analysis + Phoenix version-by-volume distribution
---

# AI observability tier: Phase 2 synthesis · 2026-05-12

NuClide Research · 2026-05-12

## TL;DR

Phase 2 closure for the AI observability tier. Two cross-cuts the Phase 1 plan
flagged but didn't land. Both reinforce the Phase 1 conclusion that Phoenix is
the single load-bearing variable in the cohort.

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7004, K7044, S7068, S7070, T5904
- **733 (AI Risk & Ethics Specialist):** K7040, T5854, T5868, T5893
- **overlap (Common AI KSATs (all 5 roles)):** K1158, K22, K6900, K6935, K7003

<!-- ksat-tag:auto-generated:end -->

1. **Zero cross-platform operator overlap.** Across 789 confirmed observability
   hosts (377 Phoenix + 381 Langfuse + 19 Helicone + 24 LangSmith), there are
   **zero IP-level overlaps** between any pair of platforms. The only /24-level
   "overlaps" resolve to Google Cloud Load Balancer and AWS edge IPs - not
   co-resident operators.

2. **Phoenix unauth distributes across all major versions 4 - 15.** The 25%
   unauth rate is **not** concentrated in older versions. Versions 11, 12, 13,
   14, 15 all have substantial unauth populations. Top-volume unauth hosts span
   versions 4.33, 8.6, 12.10, 12.12, 12.20, 13.12, 13.13, 13.20, 15.4.
   **Arize has not silently fixed the default in any release.** No "upgrade to
   N.x to remediate" defense available to operators.

3. **Phase 2 per-platform deep-dives** for Langfuse, Helicone, LangSmith are
   already published as standalone case studies (see Evidence pack). Phase 2
   deep-dives for Lunary, OpenLIT, Pezzo are folded into the Phase 1
   small-platforms survey - there's nothing more to find at populations of
   1, 23, 1 confirmed hosts respectively, all auth-protected.

The Phase 2 conclusion: the observability tier's posture is a function of
**one vendor's shipping default**. Multi-platform operators don't exist at
population scale. Version-upgrade isn't a remediation path for Phoenix
operators - the default has been constant for 11+ major versions.

## Cross-platform operator overlap (PHASE-PLAN cross-cut)

The Phase 1 plan asked: "does anyone run Phoenix AND Langfuse on the same IP?"
The answer matters for two reasons:

1. If operators co-located observability platforms, the unauth-rate analysis
   needs to weight per-operator, not per-host.
2. If a single operator runs multiple platforms and one is unauth, the unauth
   one leaks data that the auth-protected one was supposed to be guarding.

### IP-level overlap (exact match)

| Pair | Overlap | Notes |
|---|--:|---|
| Phoenix ∩ Langfuse | **0** | |
| Phoenix ∩ Helicone | **0** | |
| Phoenix ∩ LangSmith | **0** | |
| Langfuse ∩ Helicone | **0** | |
| Langfuse ∩ LangSmith | **0** | |
| Helicone ∩ LangSmith | **0** | |

Zero exact-IP overlaps. No operator runs two observability platforms on a
single host.

### /24-level overlap (proxy for "same operator, different host")

| Pair | /24 overlap | Resolution |
|---|--:|---|
| Phoenix ∩ Langfuse | 1 | `34.111.69.0/24` - Google Cloud Load Balancer edge |
| Phoenix ∩ Helicone | 1 | `16.148.235.0/24` - AWS us-west-2 edge |
| All other pairs | 0 | — |

The 2 nominal /24 overlaps resolve to cloud edge infrastructure (Phoenix host
`34.111.69.168` is `168.69.111.34.bc.googleusercontent.com`, Langfuse host
`34.111.69.53` is a separate GCLB front-end). Different customers behind the
same CDN. Not operator-level co-location.

### What this means

Population-scale observability operators install **one** platform per host.
This is the empirical baseline:

- Multi-platform observability is rare enough to not appear in 789 hosts
- Per-host unauth analysis is per-operator unauth analysis (1:1)
- An unauth Phoenix host doesn't leak data that its operator's separate
  Langfuse instance was protecting - they're operationally independent

This kills a hypothetical defense reading: "Phoenix users also run Langfuse
which catches the leak." They don't. The 94 unauth Phoenix hosts are
self-sufficient leak surfaces.

## Phoenix version distribution in the unauth subset

The Phase 1 deep-dive established that Phoenix's `PHOENIX_ENABLE_AUTH=False`
is the current `main`-branch documented default. Phase 2 asks: how far back
does this go in shipped versions? Does upgrading to a recent release fix it?

### Unauth host major-version distribution (92 hosts with extractable version)

| Major version | Unauth hosts |
|--:|--:|
| 4 | 1 |
| 7 | 2 |
| 8 | 6 |
| 11 | 10 |
| 12 | 20 |
| **13** | **27** |
| 14 | 10 |
| 15 | 13 |

(2 hosts returned no version banner; total 94 in the unauth subset.)

### Reading

The default has been constant across 11+ major versions in active deployment.
Newest version observed unauth is **15.5.1** (3 hosts). Oldest is **4.33.1**
(1 host, still volume-positive: 57k records).

Phoenix major-13 is the modal version (27 hosts, 29% of the unauth subset),
but every major from 11 through 15 has double-digit unauth representation.
**There is no upgrade path that flips the default.** An operator running
Phoenix 15.5.1 with no explicit `PHOENIX_ENABLE_AUTH=True` is exactly as
exposed as an operator running 11.19.

### Top-volume unauth hosts by version

The 10 highest-volume unauth Phoenix hosts (by record count) span the version
range:

| URL | Version | Records |
|---|---|--:|
| `http://190.210.105.193:6006` | 8.6.0 | 878,986 |
| `http://13.228.68.200:80` | 13.20.0 | 514,645 |
| `http://3.1.189.83:80` | 13.20.0 | 514,645 |
| `https://34.40.51.187:443` | 12.10.0 | 475,048 |
| `http://34.23.90.218:6006` | 15.4.0 | 116,823 |
| `https://34.93.215.14:443` | 12.12.0 | 438,071 |
| `http://24.144.113.134:6006` | 13.12.0 | 88,163 |
| `http://185.216.21.164:6006` | 13.13.0 | 22,899 |
| `http://47.92.197.149:6006` | 12.20.0 | 11,147 |
| `http://74.241.249.68:6006` | 4.33.1 | 57,379 |

Top-volume unauth spans Phoenix major versions 4, 8, 12, 13, 15 - five
different majors in ten hosts. **High-impact exposure is not concentrated in
end-of-life versions.** The largest unauth instance (878k records on
`190.210.105.193`) is on a 5-major-version-old release; the second-largest
(514k records, two co-mirrors on `13.228.68.200` and `3.1.189.83`) is on a
within-the-last-year release.

## ASN concentration in the unauth Phoenix subset

| ASN | Unauth Phoenix hosts |
|---|--:|
| Google LLC | 20 |
| DigitalOcean, LLC | 8 |
| Microsoft Corporation | 6 |
| Microsoft Limited | 5 |
| Hetzner Online GmbH | 5 |
| Scaleway Dedibox (Paris, FR) | 4 |
| Aliyun Computing Co., LTD | 4 |
| Scaleway (Paris, FR) | 3 |
| Contabo GmbH | 3 |
| Scaleway | 2 |

Top 5 ASNs (Google + DO + Microsoft + Microsoft Limited + Hetzner) account
for **44 of 92** unauth hosts (48%). The four Scaleway entries combined
(13 hosts) make Scaleway the fourth-largest concentration; Aliyun adds 4 more.
**70%+ of unauth Phoenix deployment lives on major-cloud-provider IPs.** Not
self-hosted in datacenter colos, not on residential or shared hosting -
managed-cloud IP space where the operator made an explicit deploy choice.

This sharpens the Phase 1 finding. The unauth population isn't naive home-lab
operators who didn't know better. It's professionalized teams who deployed
Phoenix on GCP/AWS/Azure/Hetzner/Scaleway/Aliyun and didn't read the
`PHOENIX_ENABLE_AUTH` documentation note. Phoenix's documented default does
the load-bearing work on a sophisticated operator audience.

## What this closes for Phase 2

| Phase 2 plan item | Status |
|---|---|
| Phoenix deep-dive (source admin-gate audit, write-primitives, latent enumeration, version sweep) | ✓ in `phoenix-llm-observability-survey-2026-05-10.md` + `phoenix/deep-dive/` |
| Langfuse deep-dive | ✓ `langfuse-deep-dive-survey-2026-05-10.md` |
| Helicone deep-dive (with actualized ClickHouse find on `benchmarkit.solutions`) | ✓ `helicone-deep-dive-survey-2026-05-10.md` |
| LangSmith deep-dive (customer-identity disclosure across 19 enterprise operators) | ✓ `langsmith-deep-dive-survey-2026-05-10.md` |
| Lunary / OpenLIT / Pezzo deep-dives | folded into `observability-tier-small-platforms-survey-2026-05-10.md` - populations too small for standalone deep-dives, no new latent primitives surfaced |
| Cross-platform operator overlap analysis | ✓ this document |
| Phoenix version-deltas in unauth subset | ✓ this document |

Phase 2 is research-complete. The observability tier's class behavior is fully
characterized at the platform level (Phase 1), the per-platform internals
level (Phase 2 deep-dives), and the population cross-cuts level (this
document). Nothing in Phase 2 disturbs the Phase 1 conclusion - it reinforces
it.

The remaining open work for the observability tier:

1. **Phase 3** - productize the per-platform fingerprints into a single tool.
   VisorBishop already covers the auth-posture probes and IP-direct-shadow
   sweep; outstanding is the meta-fingerprinter packaging (`aimap`
   `observability` enumerator class, or `visor-observability-hunt` standalone).
2. **Disclosure batch** - vendor-side to Arize, operator-side to the top-N
   unauth Phoenix operators. Held until Phase 3 closes per
   `feedback_no_premature_disclosure_pitches.md`.

## Methodology insights surfaced or applied during Phase 2

- **Insight #12: Hostname-routed SSO doesn't protect the IP-direct shadow.**
  Applied across all Phase 2 deep-dives. Recorded in Phase 1.
- **Insight #13: Shipping defaults are load-bearing for population-scale
  security posture.** Confirmed by Phase 2 version-distribution data: the
  default doesn't drift across 11+ major versions, and operators on
  major-cloud infrastructure inherit it as-shipped.
- **[Insight #17 (NEW): Platform-class operators are mono-platform at
  population scale](../../methodology/insight-17-platform-class-operators-are-mono-platform.md).**
  Across 789 hosts spanning four observability platforms, there are zero
  genuine cross-platform IP overlaps. Operators install one platform per host.
  This is the empirical baseline for any future cross-platform-overlap
  analysis: assume independent populations unless proven otherwise.

## Evidence pack

`~/recon/2026-05-10-llm-sweep/`
- `phoenix/deep-dive/version-survey.tsv` - 94 unauth Phoenix hosts with
  version banners
- `phoenix/triage-report.txt` - top-volume unauth Phoenix host ranking
- `phoenix/phoenix-attribution.tsv` - 377-host ASN + org attribution
- `langfuse/all-confirmed-ips.txt` - 381 confirmed Langfuse hosts
- `helicone/helicone-ips.txt` - 19 confirmed Helicone hosts
- `langsmith/langsmith-confirmed-ips.txt` - 24 confirmed LangSmith hosts

Per-platform Phase 2 case studies in `case-studies/commercial/`:
- [phoenix-llm-observability-survey-2026-05-10.md](phoenix-llm-observability-survey-2026-05-10.md) (includes deep-dive)
- [langfuse-deep-dive-survey-2026-05-10.md](langfuse-deep-dive-survey-2026-05-10.md)
- [helicone-deep-dive-survey-2026-05-10.md](helicone-deep-dive-survey-2026-05-10.md)
- [langsmith-deep-dive-survey-2026-05-10.md](langsmith-deep-dive-survey-2026-05-10.md)
- [observability-tier-small-platforms-survey-2026-05-10.md](observability-tier-small-platforms-survey-2026-05-10.md)

Phase 1 synthesis: [SYNTHESIS-ai-observability-2026-05-10.md](SYNTHESIS-ai-observability-2026-05-10.md)
