---
title: "Methodology Insights — NuClide Research"
date: 2026-05-07
---

# Methodology Insights

Standalone permalink-able findings about *how to do AI-infrastructure OSINT at scale*. Each insight comes from a specific survey or incident in the [case studies](../case-studies/) and is captured here so it can be cited independently of the survey that produced it.

The full inline list lives in [`SYNTHESIS-2026-05.md`](../case-studies/commercial/SYNTHESIS-2026-05.md). This directory is the per-insight permalink layer.

## Index

| # | Insight | First captured | From |
|---|---------|----------------|------|
| 1 | [Protocol-strict surveys self-filter honeypots](insight-01-protocol-strict-self-filters-honeypots.md) | 2026-05-04 | MCP survey vs Milvus tier-2 honeypot rates |
| 2 | [Single-template auth-off failures propagate at population scale](insight-02-single-template-auth-off-propagates.md) | 2026-05-04 | LLM Gateway 98.5% identical-canned-response |
| 3 | [Capabilities-object tool-schema leak](insight-03-capabilities-object-schema-leak.md) | 2026-05-04 | mcp-server-mysql v2.0.1 |
| 4 | [WHOIS-driven contact resolution is non-negotiable](insight-04-whois-driven-contact-resolution.md) | 2026-05-04 | SUNY Buffalo State misroute |
| 5 | [Same-day-remediation feedback loop](insight-05-same-day-remediation-feedback-loop.md) | 2026-05-04 | KTH + NCU/Aiden hours-to-fix |
| 6 | [Single-word substring matching is unsound at scale](insight-06-conjunctive-matchers-required.md) | 2026-05-05 | AI safety eval Garakuta-anime FP |
| 7 | [Shodan-facet bucketing inherits the substring-FP class](insight-07-shodan-facet-bucketing-fp-class.md) | 2026-05-05 | DuckDB-HTTP bucketing |
| 8 | [Auth-bypass-via-misconfiguration is missed by entry-point fingerprints](insight-08-auth-bypass-via-misconfiguration-redirects.md) | 2026-05-06 | Airflow `AUTH_ROLE_PUBLIC=Admin` |
| 9 | [Cross-survey-correlation is a Shodan-free discovery vector](insight-09-cross-survey-correlation-discovery-vector.md) | 2026-05-06 | Langfuse cross-probe at Pharos |
| 10 | [Vendor-template default-no-auth on research instruments](insight-10-vendor-template-default-no-auth.md) | 2026-05-06 | Cortical Labs CL1 / Universität Ulm |

## How these insights are produced

Each insight is the result of a *meta-finding* during a normal survey or incident response — a moment where the methodology itself failed, partially succeeded, or surfaced a generalizable pattern. The discipline is to capture them in the moment rather than treat them as one-off bug fixes.

When an insight is added, it lives both in the inline list of `SYNTHESIS-2026-05.md` (as a numbered paragraph) and as a standalone file here (with frontmatter linking back to the originating case/disclosure).

## Recurring shapes

Several of these insights are instances of broader patterns:

- **Substring-matcher false positives** — Insights #6 and #7 are the same class at different layers (probe-side vs seed-side).
- **Vendor-template root cause** — Insights #2 and #10 are the same root-cause class at different layers (cloud reseller proxy vs embedded research instrument). Both produce population-scale exposure that operator hardening cannot fix.
- **Probe must follow protocol depth** — Insights #3 and #8 both surface auth-gated information at handshake/redirect-following layers that entry-point-only probes miss.
