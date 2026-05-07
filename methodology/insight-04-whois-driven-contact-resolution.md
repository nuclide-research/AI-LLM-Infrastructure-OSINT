---
title: "WHOIS-driven contact resolution is non-negotiable"
insight_number: 4
date: 2026-05-04
tags:
  - methodology
  - disclosure-routing
  - contact-derivation
related_disclosures:
  - disclosures/us-ny-suny-buffalo-state.md
source: case-studies/commercial/SYNTHESIS-2026-05.md
---

# Methodology Insight #4 — WHOIS-driven contact resolution is non-negotiable

**ARIN/RIPE/APNIC `OrgName` + `OrgAbuseEmail` from IP-WHOIS is the authoritative input for any disclosure recipient derivation. Filename-friendly identifiers are not institution-domain mappings.**

## Evidence

The 2026-05-04 disclosure batch's only operator-caught misroute was `SUNY Buffalo State University` → University at Buffalo, produced by a slug-string heuristic in `gen_emails.py`. The two institutions are distinct; the slug overlap was coincidental.

WHOIS resolution would have surfaced the correct organization on the first pass — the IP block is registered to Buffalo State, not the University at Buffalo system.

## How to apply

For any unsolicited disclosure:

1. Pull `whois <ip>` and read `OrgName` + `OrgAbuseEmail` first. These fields are authoritative.
2. Treat filename slugs as labels for your own filing, never as institution identifiers.
3. If WHOIS points to a parent / shared-services org (e.g. Hetzner abuse, OVH abuse), still send there — that's the network owner's responsibility for the customer notification.
4. When the operator IP is registered through a hoster, parallel-send to the operator domain's `security@` / `abuse@` if discoverable, but cite the WHOIS-resolved primary recipient.

## Source

Captured in [`case-studies/commercial/SYNTHESIS-2026-05.md`](../case-studies/commercial/SYNTHESIS-2026-05.md). Saved as feedback memory `feedback_disclosure_contact_resolver`.
