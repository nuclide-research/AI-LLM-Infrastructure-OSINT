---
title: "Shodan dork hits are not platform instances (the 50% rule)"
insight_number: 15
date: 2026-05-11
tags:
  - methodology
  - fingerprint-discipline
  - false-positives
  - shodan
  - marker-verification
  - visorbishop
related_research:
  - case-studies/commercial/visorbishop-iter6-survey-2026-05-11.md
  - case-studies/commercial/visorbishop-iter5-survey-2026-05-11.md
source: case-studies/commercial/visorbishop-iter6-survey-2026-05-11.md
---

# Methodology Insight #15: Shodan dork hits are not platform instances. The 50% rule

## Statement

The number of hits returned by a Shodan dork is not the number of
platform instances. Across the AI/LLM infrastructure surveys in
2026-04 and 2026-05, the population of hits that match a single-token
title-based dork contains roughly **half false positives**, services
that are not the target platform but share the dork's signature for
reasons unrelated to identity (re-skinned forks, reverse proxies passing
through the title, coincidental string matches, intentionally-similar
clone projects).

The empirical anchor: **iter-6's full 5,391-host LiteLLM sweep produced
2,710 confirmed LiteLLM (50.3%), with the other 49.7% non-LiteLLM
services that match the dork `http.title:"LiteLLM API"` but fail any
of three subsequent platform-specific marker probes.**

The corollary: **any population-scale finding derived directly from dork
hit counts is off by approximately 2× without further verification**.
This applies to public exposure tracking, vendor remediation rates,
and any quantitative claim about platform install base.

## Evidence

VisorBishop's iter-6 LiteLLM probe runs four sub-probes per dork hit:

1. Root HTML for the Swagger title `LiteLLM API`
2. `/.well-known/litellm-ui-config` for the `proxy_base_url` field
3. `/v1/models` for the OpenAI-shaped JSON response
4. `/openapi.json` for version metadata

Of 5,391 unique URLs returned by `http.title:"LiteLLM API"`:

| Outcome | Count | % |
|---|--:|--:|
| **Confirmed LiteLLM** (marker hit) | **2,710** | **50.3%** |
| Non-LiteLLM (no marker, no `/v1/models` shape) | 2,681 | 49.7% |
| of confirmed: critical unauth | 283 | 5.2% of probed, 10.4% of confirmed |
| of confirmed: auth-fronted | 2,368 | 43.9% of probed |

The 2,681 non-LiteLLM hits fall into several classes:

1. **Reverse proxies passing through the title**, operator front-ends
   (Cloudflare R2 cache, nginx with a static landing page, etc.) that
   include `LiteLLM API` in their HTML but don't actually serve a
   LiteLLM proxy.
2. **OpenAI-compatible alternative servers.** vLLM, Ollama proxies,
   FastChat, OpenRouter rebrands. All serve `/v1/models` in a
   compatible shape, but they're not LiteLLM. They fail the
   `/.well-known/litellm-ui-config` marker check.
3. **Re-skinned forks.** Operators who forked LiteLLM and re-branded
   the Swagger UI title without changing the `/.well-known` route, or
   who shipped a custom proxy with the LiteLLM title for compatibility
   reasons.
4. **Coincidental title matches**, a small fraction of hosts where
   `LiteLLM API` appears in the HTML for unrelated reasons (blog posts,
   documentation pages, etc.).

## How the failure mode arises in real recon

The default workflow when a researcher discovers a platform population is:

1. Find a Shodan dork that returns hits on the platform
2. Quote the hit count as the population: "5,408 LiteLLM instances exposed"
3. Probe a sample, see most are real, generalize

Step 3 is the failure point. The "most are real" sample bias arises
because:

- Most researchers sample the top-N highest-rank hits, which are skewed
  toward production deployments that match the dork most cleanly.
- A 25-host sample produces 1-3 false positives, which feels like noise
  rather than 50%.
- The bias compounds in marketing/awareness work: large numbers are
  more impactful, and "5,408" is more memorable than "2,710 with caveats."

The iter-5 sample of 500 LiteLLM hosts produced 269 confirmed (53.8%),
within 3.5pp of the iter-6 population rate. **At any sample size above
~200 hosts, the false-positive rate converges to roughly half.**

## How to apply

The required discipline: **never quote a dork hit count as a platform
count without a marker-verified subset**.

The recommended fingerprint pattern, per platform:

1. **Identity marker (required)**, a platform-specific endpoint, response
   field, or error string that no other platform serves. Examples:
   - LiteLLM: `/.well-known/litellm-ui-config` returning JSON with
     `proxy_base_url`
   - Argilla: `argilla.api.errors::UnauthorizedError` on `/api/v1/me`
   - Phoenix: SPA HTML with `platformVersion` field starting with
     numeric version
   - LangSmith: `/api/v1/info` with `customer_info` OR
     `license_expiration_time` OR known instance_flags
2. **Auth-posture marker (separate)**, a different endpoint that
   classifies the auth state. Often the same endpoint as the data probe
   (`/v1/models` for LiteLLM is both data and auth marker), but the
   classification is separate from identity.
3. **Version marker (optional but recommended)**. `/openapi.json` or
   equivalent for version metadata, to enable temporal analysis.

The first identity marker must be MANDATORY for the row to count as a
platform instance. Soft matches (title-only, fuzzy match, OpenAI-shape
without litellm-ui-config) are deferred to a separate "possible" bucket
that doesn't enter the headline population count.

## Concrete numbers from 12 platforms

The VisorBishop cross-platform corpus exposes the confirmed-vs-dork ratio
for every surveyed platform. The ratio is platform-specific (markers
vary in specificity), but the pattern holds:

| Platform | Probed | Confirmed | Confirmed/Probed |
|---|--:|--:|--:|
| Phoenix (Arize AI) | 94 | 89 | 95% — extremely specific marker (SPA platformVersion) |
| Langfuse | 381 | 242 | 64% — cert subject CN is specific but operators rebrand |
| LangSmith | 96 | 28 | 29% — `/api/v1/info` shape is shared with ZenML |
| LiteLLM | 5,391 | 2,710 | 50% — title pattern is widely reused |
| Argilla | 37 | 25 | 68% — argilla error class is specific |
| Promptfoo | 17 | 11 | 65% — `/api/results/` shape is specific to Next.js + promptfoo |

LiteLLM's 50% rate is roughly the population median. Less-specific
title dorks produce lower confirm rates; more-specific markers (cert
subjects, structured error classes, version fields) produce higher
confirm rates.

## Why this matters at population scale

Three downstream effects of the dork-hits-vs-instances gap:

1. **Public exposure inventories overstate by 2×**. A "5,408 exposed
   LiteLLM" claim is wrong by an order of magnitude in terms of the
   actually-actionable critical population (283 hosts). The accurate
   framing for policy work is "5,408 dork hits, 2,710 confirmed
   LiteLLM, 283 critical unauthenticated."
2. **Vendor remediation rate calculations are biased**. If a vendor
   pushes a fix and the dork hit count drops 30%, the fix may have
   removed mostly false-positives (re-skinned forks updating their
   titles) without touching the real critical surface.
3. **Per-operator disclosure batches need pre-filtering**. Disclosure
   coordination across 5,391 ip:port pairs is materially different from
   coordination across 2,710. Pre-filter via VisorBishop or equivalent
   before populating any disclosure pipeline. The 2,681 non-instances
   would generate noise complaints for operators who don't actually
   run the platform.

## Relation to other insights

- **Insight #6 (single-word substring matching is unsound)** is the
  proximate cousin: same problem at the response-body level. Insight #15
  is the same problem at the Shodan-corpus level. The dork is itself a
  single-token substring match that produces ~50% FPs.
- **Insight #14 (yield-vs-port-class)** is what to do after you've
  filtered to confirmed instances and want to expand to shadow surfaces.
  Insight #15 is what to do at the input stage to make sure the
  population is real before any expansion.
- **Insight #13 (shipping defaults are load-bearing)** only holds for
  the *confirmed* population. Applying it to the raw dork hits
  produces wrong numbers (a re-skinned fork is not bound by the
  upstream's shipping default).

## Concrete checklist for any new platform survey

Before publishing any "N instances exposed" claim:

1. **Define the identity marker**, what specific endpoint/field/error
   string is unique to this platform?
2. **Probe the full corpus, not a sample**, sample bias hides the FP
   rate.
3. **Quote both numbers**, dork hits AND confirmed instances. The
   delta is the methodology disclosure.
4. **Recheck on a slow timescale**, markers can drift (vendors rename
   `/.well-known` routes, error class names change). A six-month-old
   marker may have a different FP rate today.

The 50% rule is a heuristic anchor, not a constant. Specific platforms
will be higher or lower. But assume any new platform's dork has at least
a 25% false-positive rate until proven otherwise. That conservative
default is closer to ground truth than the implicit "dork-hit-count ≈
platform-count" most public exposure tracking uses.
