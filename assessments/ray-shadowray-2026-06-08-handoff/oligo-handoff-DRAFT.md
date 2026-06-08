# Oligo Security / Anyscale hand-off — ShadowRay 2.0 metadata IoC extension

**To:** Oligo Security (research@oligo.security) and Anyscale Security
       (security@anyscale.com) in parallel
**From:** Nicholas Kloster <nicholas@nuclide-research.com> — NuClide Research
**Date:** 2026-06-08
**Subject:** ShadowRay 2.0 — metadata IoC pattern from a 10,000-host /api/jobs/ population survey + 463 likely-attacker IPs

**Status:** DRAFT — not sent. Awaiting researcher review.

---

## Why this email

Oligo Security's November 2025 ShadowRay 2.0 disclosure is the canonical public record of the renewed CVE-2023-48022 exploitation campaign. Your team named RondoDox, MooBot, KmsdBot as integrating the unauth Jobs API for cryptojacking and self-propagation, and observed roughly 200,000 Ray servers exposed.

NuClide Research ran an independent population measurement on 2026-06-08, sampling 10,000 of the ~175,189 Shodan-visible Ray Dashboards and verifying via the unauthenticated `/api/jobs/` endpoint. We landed on a five-signal metadata IoC pattern that, when applied at scale, separates attacker-fleet nodes from clean real operators — and the population dynamics tell a different story than the raw exposure number suggests.

This email hands off our delta:

1. The five-signal IoC pattern (defender-actionable).
2. The 463 unique IPs we classify as likely-ShadowRay 2.0 attacker fleet (with 274 of them running Ray on ≥ 10 ports each).
3. The 5.5× port-fanout inflation observation (the "200,000+ exposed" framing overcounts attacker infrastructure by ~5×).
4. The methodology correction: probe `/api/jobs/`, not `/api/cluster_status` (the latter is auth-gated on current Ray versions).

---

## Method (compact)

```
Stage 0   Shodan API:  http.title:"Ray Dashboard"    → 175,189 total
            shodan download --limit 10000             → 10,000 IP:port saved

Stage 0c  verify-fixed.py — Python urllib, 300 threads, 6s timeout
            GET /api/jobs/  → 200 + JSON list = unauth confirmed
            → 6,173 host:port hits confirmed unauth (vs 0 with /api/cluster_status)
            → 1,808 unique IPs across 10,000 hits (5.5× port fanout)

Classifier  ~/garlic/shadowray_detect.py — 5 signals scored, summed, thresholded
            → 463 likely_shadowray_2_0  (score ≥ 60)
            → 391 suspect              (score 30-59)
            → 118 clean                (real operators)
            → 1,193 unknown            (unreachable / non-Ray shape)

Restraint   GET only. No POST to /api/jobs/. No /driver_info reads.
            No /api/jobs/<id>/logs. No worker-node interaction.
```

---

## The 5-signal IoC pattern

Each signal is observable from a single `GET /api/jobs/` response. Scored, summed, thresholded.

| signal | description | score |
|---|---|---:|
| **Job count == 10 (uniform cap)** | Every confirmed unauth host returned 1–10 jobs, max=10 across 1,798 hosts. The cap is a single-tool submitter fingerprint. | +25 (==10), +15 (7–9) |
| **`_aa[N]` submission ID suffix** | Submission IDs match `YYYYMMDDxxxx_aaN` where N is a small integer. The `_aaN` suffix is programmatic and shared across the fleet. | +30 (≥3 matches) |
| **1/3-1/3-1/3 status mix (RUNNING / FAILED / SUCCEEDED)** | Real workloads skew to SUCCEEDED. Balanced thirds is a synthetic load generator. | +20 |
| **Same-minute submission prefix shared across hosts** | Two or more hosts share `YYYYMMDDxxxx` prefix; same operator at the same minute. Real operators do not share timestamps across unrelated clusters. | +25 (≥2 peers) |
| **Multi-port same-IP Ray fanout** | IP responds to Ray API on ≥3 different ports. Top: 102 ports on `51.34.20.86`. Real Ray runs one dashboard per cluster. | +20 (≥3 ports) |

Thresholds: ≥60 → likely_shadowray_2_0, 30–59 → suspect, <30 → clean.

Across the 10,000-hit sample, signal frequency:

| signal | observed |
|---|---:|
| shared_prefix_with_other_hosts | 7,818 |
| multi_port_same_ip | 7,488 |
| `_aa[N]` submission_id pattern | 6,289 |
| balanced status thirds | 2,902 |
| job_count 7–9 | 2,377 |
| job_count == 10 | 783 |

---

## Top 20 attacker C2 IPs by port fanout (the inventory)

These IPs each run the Ray API on dozens of ports — far beyond any legitimate single-cluster deployment.

| IP | distinct Ray ports observed | substrate |
|---|---:|---|
| `51.34.20.86` | **102** | (AWS — region TBD) |
| `43.199.29.225` | **101** | AWS Canada |
| `54.241.67.85` | 84 | AWS US |
| `54.253.167.61` | 75 | AWS Australia |
| `16.51.129.43` | 73 | AWS |
| `3.216.125.170` | 72 | AWS US |
| `3.71.49.119` | 71 | AWS Germany |
| `43.218.43.185` | 65 | AWS Asia-Pacific |
| `54.169.61.105` | 64 | AWS Singapore |
| `56.155.27.11` | 64 | AWS |
| `3.19.213.118` | 63 | AWS US |
| `35.78.252.142` | 63 | AWS Tokyo |
| `13.53.139.178` | 62 | AWS Sweden |
| `51.84.173.250` | 62 | AWS |
| `13.48.13.125` | 61 | AWS Sweden |
| `15.134.207.39` | 60 | AWS |
| `18.102.68.225` | 58 | AWS |
| `43.210.110.244` | 56 | AWS Asia-Pacific |
| `56.155.99.29` | 55 | AWS |
| `13.244.120.140` | 53 | AWS Cape Town |

The top 20 account for 1,300+ host:port hits in our 10,000-hit sample. They are the most efficient IR targets: AWS abuse@ contacted on each will collapse a disproportionate share of the fleet.

The full 463-IP roster + full classifier output is in `shadowray-detect.ndjson` (attached).

---

## Cloud substrate distribution

The attacker fleet is AWS-multi-region native. Top buckets:

```
761  AWS US           327  AWS Tokyo
501  AWS Canada       325  AWS India
403  AWS South Africa 315  AWS Italy
400  A100 ROW DE      271  AWS US-east
388  AWS Australia    255  AWS Singapore
387  AWS Mexico       255  AWS Ireland
362  AWS Sweden
341  AWS Brazil
333  AWS UK
```

The "A100 ROW GmbH" bucket (400 hits) is a German GPU rental front — worth a separate look as the only non-AWS top-15 substrate.

---

## What we hope you can do (no obligation)

1. **Cross-reference our 463 likely-attacker IPs against your IoC list.** Where overlap is high, the metadata IoC pattern is confirmed. Where you have IPs we missed, the pattern needs refinement.
2. **Consider integrating the 5-signal pattern into your published IoC list.** Defender-side, the pattern is checkable with one curl + jq command (see the public advisory we drafted alongside this hand-off).
3. **AWS abuse hand-off:** AWS Trust & Safety can be contacted with the top-20 multi-port IPs. NuClide will not duplicate that outreach; if Oligo's IR partner pipeline already covers AWS, we are content to defer.
4. **Anyscale engagement:** The five signals are observable inside Ray's own job model. Anyscale could ship an in-product detector that flags `_aa[N]` submission patterns and the job-count cap. We would value Anyscale's stance on whether they consider that "user behavior data" or actionable.

---

## What we are NOT doing

- No POST to `/api/jobs/` on any host. The POST is the ShadowRay primitive; we never crossed that line.
- No `/api/jobs/<id>/logs` reads. We have status strings + submission_id strings only.
- No operator notification. The 118 clean real-operator hosts in our sample are not being contacted directly; substrate-provider routing via AWS abuse is the cleaner channel.
- No public publication of the 463-IP roster. The case study and public advisory are deidentified; the IP roster is in the assessment package shared only with you and (optionally) Anyscale.

---

## Methodology note we'd appreciate Oligo's view on

We initially probed `/api/cluster_status` and got 0/2,000 unauth — confidently wrong. Switching to `/api/jobs/` gave 1,798/2,000 unauth on the same hosts. We suspect this is because `/api/cluster_status` returns 401 on current Ray versions while `/api/jobs/` does not (Anyscale's "Ray must run in a tightly controlled environment" stance applies to the cluster admin API but not the Jobs API, which is the actual ShadowRay primitive). Worth flagging in any future scanner specification — the probe path matters.

---

## Attachments

- `confirmed-unauth-rosters/` — 1,798 IP:port (sample) + 6,173 IP:port (expanded)
- `shadowray-detect.ndjson` — full per-host classifier output
- `verify-fixed.ndjson` — full per-host verification record
- `pairs-large.txt` — the 10,000 IP:port roster
- `case-study.md` — the public case study draft
- `defender-advisory.md` — the public defender self-check article (drafted alongside this hand-off)

---

Best regards,
Nicholas Kloster
NuClide Research
nicholas@nuclide-research.com
https://nuclide-research.com
CISA disclosures: CVE-2025-4364, ICSA-25-140-11
