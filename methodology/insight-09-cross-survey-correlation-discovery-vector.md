---
title: "Cross-survey-correlation is a Shodan-free discovery vector with stacked-finding bias"
insight_number: 9
date: 2026-05-06
tags:
  - methodology
  - cross-survey-correlation
  - alt-port-discipline
  - stacked-findings
related_research:
  - case-studies/commercial/langfuse-cross-survey-2026-05-06.md
source: case-studies/commercial/SYNTHESIS-2026-05.md
---

# Methodology Insight #9: Cross-survey-correlation is a Shodan-free discovery vector with stacked-finding bias

**The existing nuclide.db ledger of confirmed exposures is itself a discovery substrate. Every IP NuClide has previously confirmed running an unauth Tier-A platform is a candidate for additional unauth platforms on adjacent ports. Cross-survey-correlation probes must always sweep alt-ports, not just defaults.**

## Evidence

The 2026-05-06 Langfuse cross-probe ran across **723 ledger IPs × 5 ports (3000, 3001, 8080, 443, 80)** with a strict matcher (HTTP 200 + JSON `status:OK` + `version` field, Methodology Insight #6 conjunctive) and returned **1 confirmed Langfuse hit** at `135.181.252.66:3001` (`pharos.unistarthubs.gr`).

The hit rate is low (0.14%, two orders of magnitude below dedicated tier-2 cloud survey rates), but every hit is *guaranteed to be a stacked exposure on an already-confirmed unauth-Tier-A operator*, a methodology bias toward operator-catastrophe findings over single-platform findings.

The single 2026-05-06 hit demonstrated this: the operator already exposed Mem0/Milvus on the standard Milvus port; the Langfuse find chained into an Attu admin GUI + a leaked `CLIENT_SECRET` in the Pharos webapp's `env.js` for a four-platform AI stack catastrophe.

**The default-port-only sweep found 0 hits**; only the alt-port expansion (3001, 8080) found the operator-shifted instance.

## How to apply

When Shodan API is unavailable and masscan is operationally inappropriate (residential-IP exposure risk):

1. **Use the ledger of confirmed exposures as your candidate set.** Pull `data/nuclide.db` IPs from the existing ledger.
2. **Sweep alt-ports for platforms whose defaults conflict with another popular platform on the same host.** Langfuse's default 3000 conflicts with frontend/Node.js dev servers; operators move it to 3001/8080. Never assume default-port presence.
3. **Apply a strict conjunctive matcher** (Insight #6). Cross-survey rates are low; false positives swamp signal.
4. **Expect operator-catastrophe shapes.** Hits are rare but high-value because they're stacked on existing Tier-A confirmations.

## Source

Captured in [`case-studies/commercial/SYNTHESIS-2026-05.md`](../case-studies/commercial/SYNTHESIS-2026-05.md). Survey: [`langfuse-cross-survey-2026-05-06`](../case-studies/commercial/langfuse-cross-survey-2026-05-06.md).
