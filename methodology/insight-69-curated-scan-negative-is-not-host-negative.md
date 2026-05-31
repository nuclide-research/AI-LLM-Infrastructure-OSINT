---
title: "Insight #69: A curated-port scan's negative is not a host-level negative; run a full-range population (Censys) as a standing complement"
date: 2026-05-31
survey: ncku-edge-host-2026-05-31
thesis_touch: methodology (cross-population discipline; not a thesis data point)
extends: ["insight-67-voice-audio-shodan-dark", "insight-21-port-first-discovery-for-low-footprint-platforms", "insight-14-port-selection-by-operator-intent"]
---

# Insight #69: A curated-port scan's negative is not a host-level negative

## The lesson

When aimap (our AI-intent-curated port scanner) reports "no AI/ML service," that
is a true statement about **the ports and fingerprints it checked**, not a
statement about the host. The two are easy to conflate, and conflating them
ships a confident, wrong "clean host" conclusion.

On 140.116.247.125 (NCKU edge host), aimap scanned its 51 AI-relevant ports,
found three open (80, 443, 8000), matched zero AI fingerprints even with
`-scan-all-fingerprints`, and concluded AI-empty. That conclusion was correct
and useless. The host's real exposure lived on ports aimap has no reason to
touch:

- tcp/23180 — a KubeSphere v3.1.0 Kubernetes console (default JWT secret, EOL K8s)
- tcp/2000 — a MikroTik RouterOS bandwidth-test server (the gateway tell)
- eleven SSH services on five-digit DNAT ports (5422, 9722, 11122, 12722,
  16822, 16922, 19022, 19422, 22722, 23222, 23322)

A Censys host record showed **18 services** where the curated scan saw three.

## Why the curated scan misses it (and why Shodan can too)

A curated port set is selected by operator intent (Insight #14): the ports an AI
operator would co-deploy. That is the right design for finding AI services
quickly, and the wrong instrument for asserting a host is clean. Non-AI exposures
(a control plane on 23180, a router on 2000, sshd on 16822) sit outside the set
by construction.

Shodan shares the weakness for a different reason: it scans a scheduled,
curated port list and does not systematically sweep arbitrary five-digit ports.
Censys runs broader full-range sweeps, which is why the SSH fleet and the
MikroTik service were visible there and would likely be thin or absent in
Shodan.

## The rule

1. **A curated scan returning zero is a signal to widen, not a host verdict.**
   The product is unmapped on the ports checked, not absent. (Same shape as
   Insight #67: the absence is in the instrument, not the host.)
2. **Run a full-range internet-wide population as a standing complement.** Censys
   is now a standing Stage-0 source on every assessment, run alongside
   Shodan/JAXEN, and the product is the **delta**: hosts and ports one telescope
   indexed and the other did not. The value is the difference, not the overlap.
3. **A full-range passive read precedes any "clean host" claim.** Do not conclude
   a host is uninteresting from a curated scan alone.

## Corollary: tool-catalog gaps are findings

aimap and VisorBishop have no KubeSphere or Django-debug fingerprint, and
VisorScuba has no control for an exposed Kubernetes control plane (it scored the
host 0/0 "passing," a vacuous pass). These are honest-negative-space entries, not
silent skips. The fix is to add the fingerprints/controls, not to widen the
default port set into a generic scanner (that would dilute the AI-intent design).

## Access note

Censys was operationalized via the authenticated web UI through Playwright (the
same convention as Shodan-Playwright-only), because the free plan gates the v2
API and `data/censys-sweep.py` therefore could not run. The scripted
delta-into-`ips.txt` path is pending a Censys API key.
