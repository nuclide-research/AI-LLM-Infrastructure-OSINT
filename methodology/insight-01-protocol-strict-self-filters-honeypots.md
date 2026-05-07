---
title: "Protocol-strict surveys self-filter honeypots"
insight_number: 1
date: 2026-05-04
tags:
  - methodology
  - honeypot-filtering
  - protocol-fingerprinting
related_research:
  - case-studies/commercial/mcp-cloud-survey-2026-05.md
  - case-studies/commercial/milvus-tier2-cloud-survey-2026-05.md
source: case-studies/commercial/SYNTHESIS-2026-05.md
---

# Methodology Insight #1: Protocol-strict surveys self-filter honeypots

**The protocol-shape gate is a stronger honeypot filter than IP-based blocklists.**

## Evidence

The MCP survey, which required a strict JSON-RPC `initialize` handshake before scoring a hit, saw only **1.1% AS63949 honeypot pollution on Linode**. The earlier Milvus tier-2 survey, which probed on a more permissive shape, saw **91.6% on the same Linode population**.

The strictest possible handshake fingerprint is the right primary discriminator for any new platform-class survey. IP-based honeypot lists work as a secondary safety net but will never catch a honeypot operator that flips IP allocations between scans.

## How to apply

For new platform-class surveys:

1. Find the most-distinctive single request the platform requires (specific method name, exact JSON-RPC envelope, required headers, version negotiation).
2. Score a hit only on full protocol-shape conformance, not on banner heuristics or substring matches.
3. Layer the IP-based honeypot list on top as a sanity check.

## Source

Captured in [`case-studies/commercial/SYNTHESIS-2026-05.md`](../case-studies/commercial/SYNTHESIS-2026-05.md). See also [`reference/as63949_honeypot_fleet`](../reference/as63949_honeypot_fleet.md) for the IP-based filter list.
