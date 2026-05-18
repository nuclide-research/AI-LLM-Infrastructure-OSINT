---
title: "Shodan-facet FP rate escalates with token commonality"
insight_number: 26
date: 2026-05-16
tags: [methodology, shodan, fp-rate, verification, dorks]
related_research:
  - case-studies/commercial/image-generation-population-survey-2026-05-16.md
  - case-studies/commercial/voice-cloning-population-survey-2026-05-15.md
  - case-studies/commercial/data-labeling-population-survey-2026-05-16.md
source: 2026-05-16 image-gen survey (50,058 Shodan candidates → 548 real-unauth)
---

# Insight #26: Shodan facet FP-rate escalates with token commonality; 97% is real at acronym-tier

> The FP rate of a single-token Shodan dork scales not just with token specificity but with **the number of unrelated services that happen to share the string**. Common-string facets at population-scale can be 97% FP, not the 50% Insight #15 estimated at LiteLLM's tier.

## The escalation

Codified by Insight #15 (`http.title:"LiteLLM API"` → 5,391 hits, 2,710 real LiteLLM = 50% FP). Sharpened by the 2026-05-15 RVC voice-cloning survey (`http.title:"RVC"` → ~34 hits, ~6 real = ~82% FP). **Now further sharpened by the 2026-05-16 ComfyUI survey:**

| Survey | Dork | Total hits | Real positives | FP rate |
|---|---|---|---|---|
| LiteLLM (original Insight #15 case) | `http.title:"LiteLLM API"` | 5,391 | 2,710 | **50%** |
| RVC voice-cloning | `http.title:"RVC"` | 34 | ~6 | **~82%** |
| Label Studio (this batch) | `http.title:"Label Studio"` | 1,663 | 3 | **~99.8%** |
| **ComfyUI (this batch)** | **`product:"ComfyUI"`** | **50,058** | **1,359** | **97.3%** |

The 97.3% from ComfyUI is the highest measured FP rate so far, and it came from Shodan's `product:` facet. Which should be banner-precise, not body-substring. **Even the product facet is subject to this collision class.** Reasonable hypothesis: Shodan's `product:` facet is built on combined banner + page-content matching; a Synology DSM management page that happens to contain the string "ComfyUI" anywhere gets tagged with product=ComfyUI.

## Why this happens

A token-string FP collision class scales with three independent factors:

1. **Token specificity**. `LiteLLM API` is distinctive; `RVC` is an acronym shared with hundreds of other domains.
2. **Token presence in unrelated services' metadata**. `<title>ComfyUI</title>` is the literal default ComfyUI HTML title, but SoC management consoles (ISX1104), security appliances (Fireware XTM), BI dashboards (Qlik Sense), and surveillance products (NVR301) all coincidentally use the string "ComfyUI" somewhere. Possibly because of NVR301's vendor-branded UI naming convention that includes "Comfy".
3. **Population scale**, at 50K candidates, even a 1% intrinsic collision rate produces 500 FPs; at 5K candidates it's 50.

These factors compound multiplicatively. The 97% rate on ComfyUI suggests the worst case: a popular default-title-string colliding with multiple unrelated products' deployment templates, surveyed at scale.

## Methodology consequence

For any new platform-class survey, before publishing a dork-based candidate count:

1. **Sample 30 random hits and verify each manually via a strict-conjunctive probe** before assuming the dork is accurate. The probe must check the platform's documented JSON-shape (not just status code, not just title), per [[insight-06-conjunctive-marker-anchored-fingerprints]].
2. **Quote both populations** in the case study: raw Shodan-dork count + verified-real count. Never publish a population number derived from raw dork counts without the verification ratio.
3. **Anchor the dork with a second conjunct** when re-running. For ComfyUI: `product:"ComfyUI" AND http.html:"materialdesignicons.min.css"` filters most FPs without losing real hits. The double-conjunct dork is the standard approach for any title-based facet at population scale.
4. **For population numbers cited externally** (in a synthesis paper, a public talk, a disclosure), use only the verified-real count, never the raw dork count. The raw dork count is intelligence about Shodan's tagging, not the actual population.

## When NOT to assume FP escalation

The pattern doesn't apply uniformly to every Shodan facet:

- **`product:"Typesense"`** (this same batch) returned 9,837 candidates → ~0 unauth but a high fraction are real Typesense. The product facet here matched accurately. The difference: "Typesense" is a brand-only word; "ComfyUI" is brand-AND-substring-of-many-things. Token semantics matter more than token length.
- **`http.title:"Vespa"`** would likely be high-FP (Vespa is a common motorbike model); `product:"Vespa"` is precise (Yahoo's Vespa-the-platform's banner is distinctive).

Methodology consequence: **the FP rate of a dork is a property of the token's collision space, not the platform's deployment surface.** Two platforms with similar deployment counts can have wildly different FP rates depending on whether their brand-string collides with other products' metadata.

## Where the survey budget goes

A 50K-candidate Shodan harvest at 97% FP rate means **48,500 of the probes are wasted on unrelated services.** Some practical consequences:

- Prober runtime: 70 minutes for 50K hosts at threads=200. Most of that time is wasted on dead/unrelated responses.
- Shodan query credit consumption is the same regardless of FP rate (you pay to download the candidate list).
- The case study's "honest negative space" section must enumerate the FP class: not just "Shodan had 50K hits" but "Shodan had 50K hits dominated by Synology/Fireware/Qlik/PRTG/NVR products with `<title>ComfyUI</title>`, of which ~3% are real ComfyUI."

## See also

- [[insight-15-dork-hits-vs-platform-instances]]. The original 50% framing this Insight builds on
- [[insight-06-conjunctive-marker-anchored-fingerprints]]. The verification step that catches FP-class
- [[insight-07-shodan-facet-substring-fp]]. `http.html:` / `product:` are themselves substring filters
- [[insight-16-status-code-is-not-auth]]. The distinct trap of trusting 200s as auth state
- [`image-generation-population-survey-2026-05-16.md`](../case-studies/commercial/image-generation-population-survey-2026-05-16.md): the 97% measurement
- [`voice-cloning-population-survey-2026-05-15.md`](../case-studies/commercial/voice-cloning-population-survey-2026-05-15.md): the 82% RVC measurement
