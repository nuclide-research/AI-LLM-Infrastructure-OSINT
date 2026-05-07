---
title: "Single-word substring matching is unsound at population scale"
insight_number: 6
date: 2026-05-05
tags:
  - methodology
  - fingerprint-discipline
  - false-positives
related_research:
  - case-studies/commercial/ai-safety-eval-cloud-survey-2026-05.md
source: case-studies/commercial/SYNTHESIS-2026-05.md
---

# Methodology Insight #6 — Single-word substring matching on response bodies is unsound at population scale

**A platform fingerprint must require, at minimum: (a) a specific endpoint that the platform alone serves, (b) structured response (JSON parse + named field, or specific HTML title format), (c) anchored keyword match conjoined with (a) and (b).**

## Evidence

The AI safety eval survey's bespoke probe (`data/aisafety-probe.py`) used `b"garak" in body.lower()` and `b"confident" in body.lower()` as platform-identification matches.

At 1,017 prefixes, this produced **6 false positives and 0 true positives**.

Concrete trace: a personal video clip browser had a file named `[F] Garakuta 【Flashアニメ】ガラクタノカミサマ.mp4`. Japanese anime title contains "garak"; the broken probe declared the host an exposed Garak deployment.

## How to apply

The conjunctive matcher pattern, written verbosely:

```python
def is_platform(probe_response):
    return (
        probe_response.url.endswith("/specific-endpoint-only-this-platform-serves") and
        probe_response.status_code == 200 and
        is_json(probe_response.body) and
        json.loads(probe_response.body).get("specific_field_name") == "expected_value" and
        "anchored_keyword" in probe_response.body
    )
```

Three conjuncts minimum: endpoint specificity, structural shape, anchored keyword. Any single one alone produces population-scale false positives.

## How to apply (broader)

The structural lesson is broader than this one bug:

- **Future surveys should add fingerprints to aimap and run aimap on the cohort, not write per-survey bespoke probes.** aimap's existing fingerprint database has the right matcher schema; the bespoke probes don't.
- **All AI safety eval fingerprints are now in aimap with this discipline applied.**

## Source

Captured in [`case-studies/commercial/SYNTHESIS-2026-05.md`](../case-studies/commercial/SYNTHESIS-2026-05.md) and the methodology-correction section of [`ai-safety-eval-cloud-survey-2026-05`](../case-studies/commercial/ai-safety-eval-cloud-survey-2026-05.md).
