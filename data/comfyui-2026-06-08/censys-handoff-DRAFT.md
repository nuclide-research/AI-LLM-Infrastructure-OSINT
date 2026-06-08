# Censys ARC hand-off — ComfyUI / GHOST extension data

**To:** research@censys.com (and/or the Censys ARC contact form)
**From:** Nicholas Kloster <nicholas@nuclide-research.com> — NuClide Research
**Date:** 2026-06-08
**Subject:** GHOST campaign tracker — 186-host current measurement + 3 fresh likely-GHOST hosts (extension to your Apr 7 disclosure)

**Status:** DRAFT — not sent. Awaiting researcher review.

---

## Why this email

Censys ARC's April 7, 2026 disclosure on the GHOST cryptominer/proxy botnet
targeting unauthenticated ComfyUI deployments is the canonical public record
of the campaign. NuClide Research ran an independent population measurement
of the same surface on **2026-06-08** and would like to hand off the delta
to extend the ARC tracker.

We are not asking you to do anything; we are giving you data and naming the
specific IPs that match the GHOST behavior profile in our sample, in case
your IR partners want to cross-reference against your IoC list or notify
substrate providers.

---

## Method (one paragraph)

Shodan API on `http.title:"ComfyUI" port:8188` returned 821 results;
`shodan download` saved 808 unique IPs. A two-stage HTTP probe (strict
`/system_stats` marker: HTTP 200 + JSON with `system` + `devices` top-level
keys) classified 186 of them as confirmed unauthenticated ComfyUI on the
default port. We then queried `/queue` (counts only) and `/object_info`
(node class names only) per host; **no `/prompt` submissions, no `/history`
body reads, no `/upload`, no `/view`.** A purpose-built classifier
(`comfyui-ghost-detect`) scored each host against six GHOST IoC signals
(ancient ComfyUI version, deep `/queue` pending depth, absence of artistic
custom-node packages, ComfyUI-Manager presence without artistic context,
same-ancient-version cross-host peers, GPU-running-jobs while showing the
miner profile).

We also surveyed the 175,985-host alt-port population by sample (1,000 IPs)
and found ~0.1 percent direct-IP reachable as unauthenticated ComfyUI — the
remainder are cloud-proxy frontends (RunPod, Vast.ai, Modal, AWS-direct,
A100 ROW Inc) where the substrate enforces auth even though the platform
does not.

---

## Headline numbers

| measurement | value |
|---|---:|
| Shodan hits, default port (Jun 8) | 821 |
| Unique IPs harvested | 808 |
| Live + responding | 240 |
| Confirmed unauthenticated on default port | **186 (77.5% of LIVE)** |
| Total VRAM exposed on default port unauth subset | 6,655 GB |
| Hosts > 80 GB VRAM | 15 |
| Auth-gated (401) | 29 |
| Likely-GHOST per our detector | **3** |
| Suspect per our detector | 67 |
| Clean per our detector | 114 |
| Direct-IP unauth on alt-port sample (1,000/175k) | 1 (~0.1%) |

The April ARC disclosure said "over 1,000 exposed ComfyUI instances
currently visible on the Internet." Our June measurement of 186 confirmed
unauthenticated on the default port suggests either (a) the alt-port
population is the larger Censys count, or (b) the population is shrinking
through compromise + IP shuffling, or (c) both. The auth-gated 12 percent
in our sample is consistent with operators who got compromised, cleaned up,
and added a reverse proxy.

---

## The three likely-GHOST hosts (June 8 measurement)

| IP | ComfyUI version | queue_pending | queue_running | substrate (rDNS / ASN) | reading |
|---|---|---:|---:|---|---|
| `47.239.252.9` | **0.12.2** | **52** | 1 | Alibaba Cloud Hong Kong (`ALIBABA-CLOUD---HK`) | High-confidence GHOST. Ancient version, deep pending queue, zero artistic custom nodes, running job at probe time, paired with `.121`. |
| `47.83.192.121` | **0.12.2** | **58** | 1 | Alibaba Cloud (same `AL-3` netname as `.9`) | High-confidence GHOST. Same ancient version + same behavior as `.9`. **Fleet correlation — likely same operator's miner pair on Alibaba HK.** |
| `64.247.196.123` | **0.8.2** | 11 | 1 | **Massed Compute** (commercial GPU rental, on LightEdge Solutions backbone) | Likely GHOST. Very ancient version, high pending queue, running job. **Commercial GPU cloud carrying a compromised tenant** — parallel to the Lambda Labs finding on the clean side. |

The 47.x pair is the most cleanly attributable: same `/8`, same ancient
ComfyUI 0.12.2 (which shipped ~Q3-2025 — over six months stale), same
miner-profile queue behavior, same time-of-probe. If ARC's IoC list
already covers them, this is a confirmation; if not, here's the extension.

A further 67 hosts scored as "suspect" (single-signal positive — most
commonly ancient version + same-version peer correlation, but without
deep-pending-queue at probe time). The suspect list is in
`ghost-detect.ndjson` (attached).

---

## What we are NOT doing

- We have not touched any of these hosts beyond the four read-only endpoints
  named above (`/system_stats`, `/queue`, `/object_info`, and the alt-port
  sample's `/system_stats`).
- We have not contacted any operator.
- We have not contacted any substrate provider yet.
- We will not perform any intervention (logging in, modifying state,
  removing miner persistence). That is the substrate provider's job or
  the national CERT's; we are upstream-coordinating with you as the
  publicly-disclosing tracker first.

---

## What we hope you can do (no obligation)

1. **Cross-reference our three likely-GHOST IPs against your IoC list.**
   If they're already on it, great — confirms the detector. If they're
   not, they're a fresh extension to the tracker.
2. **Mention the detector method in any follow-up writeup**, if useful.
   The four-signal classifier (ancient ver + deep pending + no artistic
   nodes + manager presence) ran across 186 hosts in ~3 minutes via three
   public GET requests per host. The IoC pattern is generalizable.
3. **Optionally, if ARC has IR partner contact lists for the substrate
   providers in our sample (Lambda Labs, Hetzner, DigitalOcean, AWS, GCP,
   Alibaba Cloud, Comcast, AT&T, KORNET, Telecom Italia, China Telecom
   Hunan), the 186-host roster is yours to extend the notification
   pipeline.** We will not duplicate that outreach.

---

## Attachments / artifacts

- `confirmed-unauth.txt` — the 186 confirmed-unauth IPs
- `verify.ndjson` — full per-host verification record (verdict + system metadata)
- `deepen.ndjson` — per-host `/object_info` + `/queue` + rDNS enrichment
- `ghost-detect.ndjson` — per-host GHOST classifier output (clean / suspect / likely_ghost)
- `findings-breakdown.txt` — the public NuClide breakdown for context
- Case study (public, already pushed):
  https://github.com/nuclide-research/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/commercial/comfyui-population-survey-2026-06-08.md

Detector source (public, MIT):
`~/garlic/comfyui_ghost_detect.py` — to be published in `nuclide-research` namespace.

---

## Methodology contribution we'd appreciate any feedback on

The 31× yield delta between our June Shodan-pass and the prior 2026-05-04
NuClide masscan-pass (76 tier-2 /16s + 25 Hetzner /16s, 5.25M IPs scanned,
6 unauth found) is the methodological lesson we plan to write up as
"Insight #88 — passive Shodan beats active broadcast scan for
title-indexable platforms." If ARC has used a hybrid approach we'd be
interested in the comparison.

The auth-friction gradient — Langfuse (forced auth) at 0 percent unauth;
Meilisearch (env-var, foregrounded) at ~10 percent; Phoenix (env-var,
not foregrounded) at ~25 percent; ComfyUI (no auth concept) at 78 percent
— is a four-point cross-platform observation that we would frame as a
predictor of population-scale unauth rate by config friction. Curious
whether ARC has independent data points that confirm or refute this
gradient at the same scale.

---

Best regards,
Nicholas Kloster
NuClide Research
nicholas@nuclide-research.com
https://nuclide-research.com
CISA disclosures: CVE-2025-4364, ICSA-25-140-11
