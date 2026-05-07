---
title: "Samples — NuClide Research"
date: 2026-05-07
---

# Samples

Public malware samples submitted by NuClide to industry sample-sharing platforms (MalwareBazaar + VirusTotal). Reporter handle on submissions: `nuclide`.

This directory is the index layer. Each sample has a standalone permalink page with full IOCs, attribution context, and links to the originating incident case study.

## Public availability policy

NuClide submits novel samples to public sample-sharing platforms after:

1. **Confirming novelty**, the sample is not already in VirusTotal, MalwareBazaar, AlienVault OTX, or GitHub-indexed code.
2. **Verifying it's malware**, not legitimate operator software (admin panels, AI agent state files, vendor management tools).
3. **Coordinating disclosure**, relevant abuse contacts and victim CERTs have been notified, so AV/EDR detection lands roughly in sync with vendor remediation channels.

Live malware binaries are **not** committed to this repo (GitHub AUP), but the hashes, IOCs, and public-platform URLs are.

## Index

| SHA256 (prefix) | Family / Variant | First public | Originating incident |
|-----------------|------------------|--------------|----------------------|
| `ee51b236…` | Mirai / Hilix-classic | 2026-05-07 | [Cortical Labs CL1 + Tencent](../case-studies/commercial/multi-hilix-jupyter-campaign-2026-05-06.md) |
| `38dce395…` | Mirai / Uirusu/2.0 | 2026-05-07 | [Cortical Labs CL1 + Tencent](../case-studies/commercial/multi-hilix-jupyter-campaign-2026-05-06.md) |

## Researcher access

Samples are retrievable from MalwareBazaar with a free `Auth-Key` from [auth.abuse.ch](https://auth.abuse.ch/), or from VirusTotal with an API tier that permits downloads.

For direct researcher-to-researcher transfer (vendor fleet-audit teams, AV/EDR vendors, academic security research), email `nicholas@nuclide-research.com`.
