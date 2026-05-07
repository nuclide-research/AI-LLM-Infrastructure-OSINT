---
title: "Research/lab-instrument vendors ship web stacks with auth-disabled defaults"
insight_number: 10
date: 2026-05-06
tags:
  - methodology
  - vendor-template
  - research-instruments
  - cortical-labs
  - jupyter
related_research:
  - case-studies/commercial/multi-hilix-jupyter-campaign-2026-05-06.md
  - case-studies/commercial/vendor-template-default-no-auth-research-instruments.md
related_disclosures:
  - disclosures/CORTICALLABS-vendor-CL1-default-no-auth.md
  - disclosures/UNI-ULM-cert-port80-dashboard-followup.md
source: case-studies/commercial/SYNTHESIS-2026-05.md
---

# Methodology Insight #10: Research/lab-instrument vendors ship web stacks with auth-disabled defaults

**Population-scale exposure is the default-config decision of the vendor, not a misconfiguration by the operator. Vendor-template means population-scale exposure.**

## Evidence

A token-disabled-Jupyter Shodan dork on 2026-05-06 surfaced 7 candidate hosts. Of the 2 reachable from the research VPN, **both were already compromised** (100% rate at this small sample).

One, `134.60.110.66` (`labdevice.medizin.uni-ulm.de`), turned out to be a **Cortical Labs CL1** "biological computer" (lab-grown neurons on a Xilinx Zynq microelectrode array, $35K research instrument) at Universität Ulm Medical Faculty.

The CL1's default v0.28.3 deployment ships with:

- **(a)** the operational web dashboard reachable on port 80 with no authentication (`/dashboard`, `/applications/{symbol-classification,pong}/`, `/recordings`, `/system`, `/jupyter/`)
- **(b)** the embedded Jupyter Notebook on port 8888 with token disabled by default
- **(c)** `Support VPN: Enabled` and `Admin Access: Enabled` toggles defaulted ON, exposing a vendor-administered remote-access channel

A Hilix-class IoT botnet exploited the unauth Jupyter on 2026-04-29 → reverse shell to `172.233.96.208:3053` (Akamai/Linode US) → 24h of attacker presence → cryptominer setup in progress + Cortical Labs support-VPN public config exfiltrated via attacker `sudo /usr/sbin/support-vpn-show-public-config`.

**The compromise vector isn't the operator's fault, it's the vendor's choice to ship the default systemd unit with `jupyter notebook --no-token`.**

## Why this generalizes

Whatever fraction of Cortical Labs' global CL1 customer fleet has the device on a public port is, by vendor-template policy, automatically internet-reachable shell-equivalent. The pattern almost certainly recurs across other research-instrument vendors with embedded Linux + web management:

- Neuroscience MEAs
- Bioreactors
- Mass-spec controllers
- Microscopy automation
- Edge-AI inference appliances

Population-scale exposure is the default-config decision of the vendor, not a misconfiguration by the operator.

## How to apply

For new platform-class surveys targeting research / lab instruments:

1. **Survey by Shodan dork on the embedded-platform footprint** (e.g., token-disabled-Jupyter, OpenSSL banner specific to a vendor's BSP), not on the brand name.
2. **Treat 100%-compromise rates at small-N as a signal of vendor-template root cause.** Don't disclose operator-by-operator until the vendor disclosure is in motion.
3. **Disclose to the vendor first**, with a fleet-wide-firmware-push framing. Customer-side hardening cannot fix it without vendor cooperation.
4. **Catalog the adjacent vendors.** The pattern is reproducible, one vendor-template finding implies a roadmap for follow-on fleet audits.

This is the same root-cause shape as Insight #2 (single-template auth-off propagates) but at the embedded-instrument layer instead of the cloud-template layer.

## Source

Captured in [`case-studies/commercial/SYNTHESIS-2026-05.md`](../case-studies/commercial/SYNTHESIS-2026-05.md). Standalone case study: [`vendor-template-default-no-auth-research-instruments`](../case-studies/commercial/vendor-template-default-no-auth-research-instruments.md). Originating incident: [`multi-hilix-jupyter-campaign-2026-05-06`](../case-studies/commercial/multi-hilix-jupyter-campaign-2026-05-06.md). Vendor disclosure: [`CORTICALLABS-vendor-CL1-default-no-auth`](../disclosures/CORTICALLABS-vendor-CL1-default-no-auth.md).
