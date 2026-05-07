---
title: "Single-template auth-off failures propagate at population scale"
insight_number: 2
date: 2026-05-04
tags:
  - methodology
  - vendor-template
  - response-uniformity
related_research:
  - case-studies/commercial/llm-gateways-cloud-survey-2026-05.md
source: case-studies/commercial/SYNTHESIS-2026-05.md
---

# Methodology Insight #2 — Single-template auth-off failures propagate at population scale

**Pattern detection on response uniformity is a powerful "single root-cause / many victims" classifier.**

## Evidence

The LLM Gateway survey documented **1,829 of 1,857 functional unauth gateways (98.5%)** returning the **identical canned response** `"Hello! I'm doing well, thank you. How about you?"` from `gpt-4o-mini`. The uniformity is the signature of a single open-source reseller-proxy template mass-deployed without auth across 1,829 independent operators.

The fix is not 1,829 individual disclosures. It's upstream — the template author enabling auth by default.

## How to apply

When sweeping a platform population:

1. Bucket responses by exact text/structure equivalence, not just service-up status.
2. If a single response shape dominates (>50%) the unauth population, the cause is upstream — find the template/Docker image/install script.
3. Disclose to the template author first. Operator-by-operator outreach is rate-limited by your own bandwidth; vendor-side fix is rate-limited by the vendor's release cadence.

This is the same shape as Insight #10 (vendor-template default-no-auth on research instruments) — both cases trace population-scale exposure to a single shipping default.

## Source

Captured in [`case-studies/commercial/SYNTHESIS-2026-05.md`](../case-studies/commercial/SYNTHESIS-2026-05.md). Survey: [`llm-gateways-cloud-survey-2026-05`](../case-studies/commercial/llm-gateways-cloud-survey-2026-05.md).
