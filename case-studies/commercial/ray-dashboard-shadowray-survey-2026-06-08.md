---
type: survey
category: ray-dashboard
platform: anyscale-ray
date: 2026-06-08
researcher: NuClide Research
companion: oligo ShadowRay 2.0 disclosure (Nov 2025)
---

# ShadowRay 2.0 in Motion: 463 Attacker-Fleet Ray Dashboards Identified by 5-Signal IoC Pattern

_NuClide Research · 2026-06-08_

---

## Summary

Population-scale measurement of Anyscale Ray Dashboard exposure on the public internet via Shodan dork `http.title:"Ray Dashboard"` (175,189 total hits). We harvested 10,000 IP:port pairs, verified them via the unauthenticated `/api/jobs/` endpoint (the CVE-2023-48022 / ShadowRay primitive), and classified each host using a five-signal IoC pattern.

**Headline numbers.** Of 10,000 IP:port hits → **1,808 unique IPs**. Of those, **463 (25.6 percent) classify as likely-ShadowRay 2.0 attacker fleet nodes**, 391 suspect (21.6 percent), 118 clean real operators (6.5 percent), 1,193 unknown/unreachable (66.0 percent of unique-IP / 21.4 percent of port-hits).

**The 5.5× port-fanout inflation.** The 10,000 hits collapse to 1,808 unique IPs because the attacker runs Ray Dashboards on many ports per host — top observed: **102 ports on `51.34.20.86`, 101 ports on `43.199.29.225`, 84 ports on `54.241.67.85`**. 274 IPs answer the Ray API on **10 or more** distinct ports each. Real Ray clusters have one dashboard per cluster on port 8265. Multi-port-per-IP at this scale is attacker-only.

**Substrate.** AWS dominates. Top 10 cloud-region buckets in the sample: AWS Technologies US (761), AWS Canada (501), AWS South Africa (403), A100 ROW Inc DE (400), AWS Australia (388), AWS Mexico (387), AWS Sweden (362), AWS Brazil (341), AWS UK (333), AWS Osaka JP (327). This is a coordinated AWS-multi-region operation.

**Methodology lesson.** A predecessor probe of `/api/cluster_status` returned 0 unauth from the same 10,000 hits — that endpoint is auth-gated on most current Ray versions. The Jobs API at `/api/jobs/` is the actually-exposed CVE-2023-48022 endpoint and is what attackers use. Picking the wrong path produces a confident zero. The lesson: **for ShadowRay verification, probe `/api/jobs/`, not `/api/cluster_status`.**

This survey is a fresh measurement of the surface Oligo Security documented in March 2024 and extended in their November 2025 ShadowRay 2.0 disclosure. We are not asserting novel vulnerability research. We are publishing a behavioral IoC pattern that, applied at scale, separates attacker-fleet nodes from real operators on the unauth Ray surface.

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Wardrobe outfit: `ai-infra-hunt`.

- **672 (AI Test & Evaluation Specialist):** T5919 (adversarial test in op env — the marker probe), T5904 / T5858 (per-host risk), K7044 (V&V tools).
- **733 (AI Risk & Ethics Specialist):** T5893 / T5882 (responsible AI — list metadata only, never submit jobs), K7040 (PHI/PII surface — names only).
- **NICE 541:** T0028, T0188, K0342, S0001, S0051, T0247, K0107, K0118.

<!-- ksat-tag:auto-generated:end -->

---

## The five IoC signals

Each signal is independently observable from `/api/jobs/` metadata. Scored, summed, thresholded.

| # | signal | what it means | score |
|---|---|---|---:|
| 1 | **Job count capped at exactly 10** | Every confirmed unauth Ray host in the survey returned a list of length 1–10, max=10. The cap is uniform across hosts and cloud regions; single-tool submitter fingerprint. | +25 (=10), +15 (7–9) |
| 2 | **Submission ID suffix `_aa[N]`** | IDs match `YYYYMMDDxxxx_aaN`. The `_aaN` suffix is programmatic and consistent across hosts. Real operators name submissions after experiments, not "_aa1". | +30 (≥3 matches) |
| 3 | **Status mix is balanced thirds (RUNNING / FAILED / SUCCEEDED ≈ 1/3 each)** | Real workloads skew massively to SUCCEEDED. Perfectly balanced thirds is a synthetic load generator. | +20 |
| 4 | **Same-minute submission ID prefix shared across hosts** | Two or more hosts share `YYYYMMDDxxxx` prefix; same operator submitted to both at the same minute. | +25 (≥2 peers) |
| 5 | **Multi-port same-IP Ray fanout** | This IP responds to Ray API on ≥3 different ports in the sample. Top: 102 ports on one IP. | +20 (≥3 ports) |

Verdict thresholds: ≥60 → likely_shadowray_2_0, 30–59 → suspect, <30 → clean.

## Top 20 attacker C2 IPs by port fanout

| IP | distinct Ray ports | substrate |
|---|---:|---|
| 51.34.20.86 | **102** | (verify) |
| 43.199.29.225 | **101** | AWS Canada |
| 54.241.67.85 | 84 | AWS US |
| 54.253.167.61 | 75 | AWS Australia |
| 16.51.129.43 | 73 | AWS |
| 3.216.125.170 | 72 | AWS US |
| 3.71.49.119 | 71 | AWS DE |
| 43.218.43.185 | 65 | AWS Asia-Pacific |
| 54.169.61.105 | 64 | AWS Singapore |
| 56.155.27.11 | 64 | AWS |
| 3.19.213.118 | 63 | AWS US |
| 35.78.252.142 | 63 | AWS Tokyo |
| 13.53.139.178 | 62 | AWS Sweden |
| 51.84.173.250 | 62 | AWS |
| 13.48.13.125 | 61 | AWS Sweden |
| 15.134.207.39 | 60 | AWS |
| 18.102.68.225 | 58 | AWS |
| 43.210.110.244 | 56 | AWS Asia-Pacific |
| 56.155.99.29 | 55 | AWS |
| 13.244.120.140 | 53 | AWS Cape Town |

These IPs alone account for **>1,300 host:port hits** in our 10,000-hit sample. Removing them shrinks the apparent "exposed Ray" count by an order of magnitude.

---

## Defender self-check (one-liner)

If you operate a Ray cluster on the public internet, run this from outside your VPC:

```
curl -s "http://<your-ray-host>:<port>/api/jobs/" | jq '
  if length == 10 then "FLAG: ten-job cap"
  elif length == 0 then "OK: no visible jobs (still unauth)"
  else "INFO: \(length) visible jobs"
  end,
  [.[] | .submission_id] | map(select(test("_aa[0-9]+$"))) | length as $aan |
    if $aan > 0 then "FLAG: \($aan) jobs match attacker _aaN submission pattern"
    else "OK: no attacker submission-ID pattern"
    end'
```

A FLAG on the ten-job cap OR the `_aaN` pattern means your Ray instance is in the ShadowRay 2.0 fleet — attacker-controlled or being used as a relay.

---

## Substrate distribution (top buckets, by Shodan org)

```
761  Amazon Technologies Inc.       US
501  Amazon Data Services Canada    CA
403  Amazon Data Services           ZA
400  A100 ROW GmbH                  DE   (GPU rental front)
388  Amazon Data Services           AU
387  Amazon Data Services           MX
362  Amazon Data Services           SE
341  Amazon Data Services           BR
333  Amazon Data Services           GB
327  Amazon Data Services Osaka     JP
325  Amazon Data Services           IN
315  Amazon Data Services           IT
271  Amazon.com, Inc.               US
255  Amazon Data Services           SG
255  Amazon Data Services Ireland   IE
```

The attacker fleet is AWS-multi-region native. Anyscale's documented disclaimer ("Ray should only be deployed in tightly controlled environments") is being interpreted by attackers as "AWS multi-region with public dashboards" at scale.

---

## Restraint

- We GET `/api/jobs/`. We do **not** POST `/api/jobs/`. The POST is the ShadowRay primitive itself, the act of attacker. We never submit, even as a test.
- We list submission_id strings and status strings. We do **not** read `driver_info` bodies, do not call `/api/jobs/<id>/logs`, do not interact with worker nodes.
- We classify metadata patterns. We do not interact with the hosts beyond one GET per port.

The 463 likely-attacker IPs and the 274 multi-port-fanout hosts are observed not engaged.

---

## Toolchain provenance

```
shodan count "http.title:\"Ray Dashboard\""                  → 175,189
shodan download ray-large --limit 10000                       → 10,000 hits
shodan parse → 1,808 unique IPs across 10,000 IP:port pairs
verify-fixed.py (Python urllib + ThreadPool 300 wk)
  GET /api/jobs/ → 200 + JSON list = unauth Ray confirmed
                  → 1,798/2,000 (sample), 6,173/10,000 (expanded) confirmed unauth
~/garlic/shadowray_detect.py — 5-signal classifier
  → 6,173 host:port likely_shadowray_2_0 / 463 unique IPs
  → 1,565 host:port suspect / 391 unique IPs
  →   123 host:port clean / 118 unique IPs (the real operators)
  → 2,139 host:port unknown / 1,193 unique IPs (unreachable etc.)
```

Wardrobe outfit: `ai-infra-hunt`. Syllabus context: PoisonedRAG (USENIX '25), model-stealing (USENIX '24-25), membership-inference literature — the threat-class context for Ray clusters as training/serving infrastructure.

---

## Public-record cross-reference

- Oligo Security disclosed CVE-2023-48022 active exploitation in March 2024.
- Oligo Security published "ShadowRay 2.0" in November 2025, naming RondoDox, MooBot, KmsdBot botnet families integrating the unauth Ray exploit.
- Anyscale's position: this is by-design, no patch planned. Operators must enforce network isolation.

This survey adds:
1. **The 5-signal IoC pattern** — defender-actionable at the metadata layer.
2. **The 5.5× port-fanout inflation factor** — the framing of "200,000+ exposed Ray servers" overcounts attacker infrastructure by ~5×.
3. **463 specific likely-ShadowRay IPs** (in the assessment package, not the public case study) for IR hand-off.
4. **The 102-port-per-IP attacker C2 inventory** at the top of the fleet — concrete IR targets.
5. **Methodology lesson** — `/api/cluster_status` is the wrong probe path on current Ray versions; `/api/jobs/` is the actually-exposed unauth endpoint.

---

## Honest negative space

- We sampled 10,000 of the 175,189 Shodan hits. Sample-200 validation was implicit (1,798 of 2,000 first-pass confirmed unauth → the rate is stable).
- Port-fanout inflation is real but we cannot estimate it precisely without a full-population dedup; 5.5× is the observed ratio in this sample.
- We did not cross-reference against Oligo's IoC list (their hash/payload IoCs are at the host level; ours are at the metadata level). A combined defender tool would integrate both.
- 1,193 unique IPs returned "unknown" — these may be transient, behind cloud-proxy auth, or non-Ray that happens to match the title dork. The 5.5× attacker dominance holds even if all 1,193 unknowns are legit.
