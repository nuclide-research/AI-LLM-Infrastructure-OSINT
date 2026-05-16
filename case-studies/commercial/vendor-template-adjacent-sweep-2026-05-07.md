---
type: vendor
title: "Vendor-template adjacent-vendor sweep, planning doc + Shodan dork catalog (2026-05-07)"
date: 2026-05-07
class: vendor-template
category: planning
status: in-progress
methodology: structural-class dorks + aimap conjunctive validation + per-vendor escalation
---

# Vendor-template adjacent-vendor sweep, planning + dorks

NuClide Research, 2026-05-07

The Cortical Labs CL1 incident ([`multi-hilix-jupyter-campaign-2026-05-06.md`](multi-hilix-jupyter-campaign-2026-05-06.md)) and the standalone vendor-template study ([`vendor-template-default-no-auth-research-instruments.md`](vendor-template-default-no-auth-research-instruments.md)) named ~25 candidate vendors likely sharing the same ship-with-no-auth pattern. This doc is the planning groundwork for the follow-on fleet audits.

## Strategy: class dorks beat vendor dorks

A vendor-by-vendor approach (one Shodan dork per vendor banner) requires public knowledge of each vendor's distinctive fingerprint surface. For most lab-instrument vendors, that surface is not publicly documented. Spending hours per vendor to dig out a banner string is poor leverage.

Better: **dork the class**, not the vendor. Research instruments on public IPs share structural properties:

1. They run embedded Linux on FPGA / SoM hardware (kernel strings: `xilinx`, `tegra`, `allwinner`, `rockchip`, `imx`)
2. They expose a vendor-default web dashboard or token-disabled Jupyter
3. They sit on academic / research network blocks with rDNS suffixes like `.medizin.`, `.bio.`, `.lab.`, `.uni-`, `.edu`, `.ac.<cc>`
4. They have low entropy in default-deployment patterns (same systemd unit invocation across the fleet)

A class dork hits every vendor in the population at once. aimap conjunctive validation classifies what each hit actually is.

## High-yield class dorks

The following dorks are derived from the CL1 finding shape generalised to the broader research-instrument fleet. Each is intended to be runnable in the Shodan UI / API. Counts and sample IPs are TBD until probed; this is the planning catalog, not a results report.

### Dork 1, token-disabled Jupyter on academic networks

```
port:8888 product:"Jupyter Notebook" "token=" -"token=False" hostname:edu
```

Variants for non-`.edu` academic networks:

```
port:8888 product:"Jupyter Notebook" hostname:medizin
port:8888 product:"Jupyter Notebook" hostname:bio
port:8888 product:"Jupyter Notebook" hostname:lab
port:8888 product:"Jupyter Notebook" hostname:research
port:8888 product:"Jupyter Notebook" hostname:ac.uk
port:8888 product:"Jupyter Notebook" hostname:ac.jp
port:8888 product:"Jupyter Notebook" hostname:ac.cn
```

Expected hit shape: institutional research host running a vendor-shipped CL1-class instrument with embedded Jupyter exposed unauth. The CL1 surfaced through this exact pattern.

### Dork 2, Xilinx-FPGA SoM kernels on academic networks

```
"Linux" "xilinx" port:22 hostname:edu
"Linux" "xlnx" port:22 hostname:edu
```

Expected hit shape: SoM-based research instrument (CL1, MCS-class MEAs, scientific-imaging FPGA). Many of these expose SSH banners with the kernel string. Cross-reference with Dork 1 to find the ones that ALSO have token-disabled Jupyter.

### Dork 3, NVIDIA Jetson on academic / lab networks

```
"NVIDIA" "tegra" port:22 hostname:edu
"NVIDIA Jetson" hostname:edu
http.title:"Jetson" hostname:edu
```

Expected hit shape: development boards used as edge-AI inference hosts in research labs. These often have default `nvidia:nvidia` / `ubuntu:ubuntu` credentials. Many also serve Streamlit / Gradio / vLLM on additional ports without auth.

### Dork 4, Coral Dev Board / Mendel Linux

```
"mendel" port:22
"coral-dev" hostname:edu
```

Expected hit shape: Google Coral Dev Boards used for ML demos in research labs. Mendel Linux is the distinctive distro fingerprint. These typically run Streamlit / FastAPI on an additional port for demos.

### Dork 5, Hailo SDK / hailort

```
"hailort" port:22
"Hailo" "Linux" hostname:edu
```

Expected hit shape: Hailo-8 evaluation rigs at research labs. Lower confidence on this one; the SDK doesn't strongly broadcast a network banner.

### Dork 6, generic "lab" / "instrument" / "control" web dashboards on academic networks

```
http.title:"Dashboard" hostname:medizin
http.title:"Control" hostname:lab
http.title:"Instrument" hostname:edu
http.title:"System" hostname:bio
```

Expected hit shape: vendor-shipped web dashboards on instruments that don't carry a strong vendor banner. Will surface a high false-positive rate; aimap conjunctive validation (Methodology Insight #6) is required here, not optional.

### Dork 7, Cortical Labs follow-up sweep

```
http.html:"Cortical Labs"
ssl.cert.subject.cn:"corticallabs.com"
http.title:"CL1"
```

Expected hit shape: more CL1 instances. The first probe surfaced 7 candidates (2 reachable, both compromised). A wider sweep with looser hostname filters may surface the rest of the global CL1 fleet.

## Per-vendor speculative dorks

For the vendors where I have weaker public-banner signal, speculative dorks to try if the class dorks don't cover them:

| Vendor | Speculative dork | Confidence |
|---|---|---|
| Multi Channel Systems (MCS) | `"MC_Rack" OR "MEA2100"` | low, software is desktop-only per MCS docs |
| MaxWell Biosystems | `"MaxOne" OR "MaxTwo" hostname:edu` | low, brand is software-internal |
| 3Brain BioCAM | `http.html:"BioCAM" OR "BrainWave"` | low |
| Plexon OmniPlex | `"OmniPlex" OR "PlexControl" port:80` | low |
| Eppendorf DASware | `"DASware" OR "DASGIP" hostname:bio` | medium, DASware Connect is web-based |
| Sartorius BIOSTAT / MFCS | `"BIOSTAT" OR "MFCS"` | medium |
| Applikon ez-Control | `"ez-Control" OR "Applikon"` | low |
| Thermo Xcalibur | `"Xcalibur" port:80` | low, not normally web-exposed |
| Agilent OpenLab | `"OpenLab CDS" OR "ChemStation" port:80` | medium |
| Waters Empower | `"Empower" port:80 hostname:lab` | low |
| Nikon NIS-Elements | `"NIS-Elements" port:80` | low |
| Leica MMI | `"MicroLab" OR "Leica MMI" port:80` | low |
| Olympus cellSens | `"cellSens"` | low |

These are starting points. None has been validated. The expected yield from the per-vendor list is much lower than from the class dorks above, because lab-instrument software is mostly desktop-only or LAN-internal in practice.

## Probe + validate workflow

When IPs come back from Shodan:

1. `jaxen import --no-lookup <ips>` — ingest into the ledger without burning Shodan API quota (Shodan key has been invalid since session 8).
2. `bash data/visor-chain-runner.sh vendor-template-adjacent-2026-05-07` — runs the canonical 11-step chain (visorgraph → aimap → aimap-profile → JS-extract → nuclide-contact → visorlog → visorscuba → BARE → visorcorpus).
3. For Dork 6 (generic web dashboards), aimap conjunctive validation is non-negotiable; the substring-match FP class (Methodology Insights #6 + #7) applies in full.
4. Per-finding triage: vendor-template default-no-auth → vendor disclosure (route via [`vendor-template-default-no-auth-research-instruments.md`](vendor-template-default-no-auth-research-instruments.md) framework). Operator-specific compromise → CERT + abuse + vendor parallel disclosure (the Hilix / CL1 / Ulm shape).

## Disclosure routing (anticipated)

Per-vendor disclosure routing mirrors the Cortical Labs flow:

- Vendor security contact (`security@<vendor>` or via published security.txt) — fleet-audit + firmware push framing
- Affected operator's CERT — per-instance compromise notification
- Network owner's abuse contact — IP-block-level takedown if the host is compromised
- DFN-CERT or country-level CSIRT for institutional research hosts

The vendor advisory should pre-empt operator-by-operator outreach. Once one customer is shown to be compromised, the assumption is fleet-wide vulnerability and the vendor is responsible for fleet-wide remediation.

## Status

This is the planning doc. No probes have been run yet. Updates expected:

- 2026-05-XX: results from Dork 1 (token-disabled Jupyter on academic networks)
- 2026-05-XX: results from Dork 7 (Cortical Labs follow-up sweep)
- 2026-05-XX: aimap fingerprint additions for any vendor surfaced

When findings come in, this doc gets superseded by per-vendor case studies under `case-studies/commercial/vendor-<vendor>-*.md`. Until then, this is the survey roadmap.

## See also

- [vendor-template-default-no-auth-research-instruments](vendor-template-default-no-auth-research-instruments.md) — the threat-class study
- [multi-hilix-jupyter-campaign-2026-05-06](multi-hilix-jupyter-campaign-2026-05-06.md) — the originating CL1 incident
- [Methodology Insight #10](../../methodology/insight-10-vendor-template-default-no-auth.md) — vendor-template default-no-auth
- [Methodology Insight #6](../../methodology/insight-06-conjunctive-matchers-required.md) — conjunctive matchers required
