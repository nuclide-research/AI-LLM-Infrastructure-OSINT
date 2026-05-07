---
title: "Shodan-facet bucketing inherits the substring-FP class"
insight_number: 7
date: 2026-05-05
tags:
  - methodology
  - shodan-discipline
  - false-positives
related_research:
  - case-studies/commercial/SYNTHESIS-2026-05.md
source: case-studies/commercial/SYNTHESIS-2026-05.md
---

# Methodology Insight #7 — Shodan-facet bucketing inherits the substring-FP class

**Shodan's `http.html:` and `product:` matches are themselves substring-style filters at the indexer level. Apply Insight #6's conjunctive-matcher rule at the seed layer, not just the probe layer.**

## Evidence

Discovered during the DuckDB-HTTP bucketing pass: a bare-string Shodan dork returned 8 hits whose actual products were unrelated — Definite.app, Amulet Scan, generic FastAPI swagger pages all matched a substring intended to surface DuckDB-HTTP instances.

The seed list inherited the false-positive class even though the downstream probe was strict.

## How to apply

For any Shodan-driven survey:

1. Use `http.title:` over `http.html:` when the platform has a deterministic `<title>`.
2. Conjoin Shodan filters with multi-token requirements — `product:foo http.title:"Foo Admin"` instead of just `product:foo`.
3. **Always run aimap (or another conjunctive validator) on the Shodan-derived seed list before pulling per-host evidence.** Trust nothing from the dork alone.
4. If Shodan returns ≤ ~20 hits, hand-validate each before publishing exposure counts.

## Source

Captured in [`case-studies/commercial/SYNTHESIS-2026-05.md`](../case-studies/commercial/SYNTHESIS-2026-05.md). Connected to Insight #6 — both are instances of the same substring-FP class at different layers.
