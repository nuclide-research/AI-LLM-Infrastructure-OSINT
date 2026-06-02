---
type: methodology
insight_number: 43
title: "VisorSD multi-ASN grouped-OR query construction returns zero even when Shodan direct returns hundreds; the bug is in VisorSD's query templating, not Shodan's index."
---

# Insight #43. VisorSD multi-ASN grouped-OR query construction bug

_Source: LLM orchestration category-01 re-run, 2026-05-19. VisorSD `-asn AS14061` returned 0/21 results across all bundled queries. Shodan direct query `asn:AS14061 port:11434` returns 593 confirmed Ollama hits on AS14061 (DigitalOcean) at the same timestamp._

## The rule

VisorSD's multi-ASN grouped-OR query construction can silently return zero where Shodan direct queries return hundreds. A zero-result VisorSD run against a known-populated ASN is a tooling failure signal, not a population signal. Always cross-validate a zero VisorSD result with a direct Shodan query on the same ASN + dork before recording it as a genuine null.

The root cause is in VisorSD's query templating: when multiple ASNs are passed, the grouped-OR construction (`asn:ASN1 OR asn:ASN2`) may produce a query string that Shodan's API rejects or mis-parses silently (HTTP 200 with empty results rather than a 400 error). The per-ASN direct query works correctly; the combined form does not.

## Empirical basis (LLM orchestration re-run, 2026-05-19)

| Query method | ASN | Platform dork | Result |
|---|---|---|---|
| VisorSD `-asn AS14061` | DigitalOcean | All bundled queries | **0/21 hosts** |
| Shodan direct | AS14061 | `port:11434 product:ollama` | **593 hits** |

The 593:0 discrepancy on the same ASN and same timestamp is unambiguous. The Shodan index is populated; VisorSD's query failed silently.

Secondary confirmation: VisorSD ran successfully against single-ASN targets in the same session (AS16276 OVH, AS24940 Hetzner) with non-zero results. The failure is specific to multi-ASN grouped-OR forms or to large-ASN block handling.

## Procedural rules this insight generates

1. **Treat a VisorSD zero result as tentative.** Before recording `null` in the findings ledger, run the equivalent Shodan direct query on the top-3 ASNs in the target population. If direct returns hits, the zero is a tooling artifact.

2. **Single-ASN mode as fallback.** If multi-ASN VisorSD fails, fall back to sequential single-ASN runs for the top-N ASNs in the survey corpus. Less convenient but produces reliable counts.

3. **File the bug.** When VisorSD zero-vs-Shodan-direct discrepancies are observed, capture the exact VisorSD invocation and the Shodan direct equivalent in the bug report. The fix is in query template construction, not in the discovery workflow.

4. **Do not attribute zero-result VisorSD runs to population absence.** The finding breakdown must distinguish `[VisorSD: null (query-construct bug, not population absence — cross-validated via Shodan direct)]` from `[VisorSD: null (genuine null, Shodan direct also 0)]`.

## Relationship to prior insights

- **Insight #7 (Shodan facet FP class)**: the inverse failure mode. Insight #7 is about false positives from over-broad dork matching; this insight is about false negatives from a tool-side query construction failure. Both require cross-validation against a ground truth.
- **Insight #15 (dork hits vs platform instances)**: applies here in the opposite direction. Shodan's 593 hits still require verification to produce instance count; the point here is that VisorSD's 0 is not even a valid starting count.

## See also

- `case-studies/commercial/llm-orchestration-rerun-2026-05-19.md` §10 (Stage 7 arsenal coverage, VisorSD row)
- `methodology/insight-07-shodan-facet-bucketing-fp-class.md`: complementary failure mode (over-broad)
- VisorSD source: `github.com/nuclide-research/VisorSD` — query-template construction in the ASN-OR branch
