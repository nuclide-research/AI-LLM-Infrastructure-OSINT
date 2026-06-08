---
type: survey
category: data-labeling-platform
platform: label-studio
date: 2026-06-08
researcher: NuClide Research
---

# Label Studio at Population Scale: 99.8 Percent Auth-Gated, the New Anchor on the Auth-Friction Gradient

_NuClide Research · 2026-06-08_

---

## Summary

Population-scale survey of Heartex/Humansignal **Label Studio** (the open-source data-labeling and RLHF annotation platform) via the Shodan dork `http.title:"Label Studio"`. 1,646 total hits; 500 sampled.

**The thesis-class result.** **1 of 500 sampled hosts (0.2 percent) returned an unauthenticated `/api/projects/` list.** 404 hosts (80.8 percent) returned 401, 72 were dead, 23 had non-LS shape. Of LIVE Label Studio hosts in the sample, **99.75 percent are auth-gated.** This is the strongest auth-by-default measurement across the entire NuClide program.

Label Studio ships with a mandatory account-creation flow on first run. The Django backend will not serve `/api/projects/` until an authenticated session or API token is provided. Operators almost universally retain this default. The 1 unauth in the sample is an empty fresh install (0 projects, 1 user, Alibaba Cloud) that the operator has not finished setting up.

This survey is the **thesis-anchor extension** for the auth-friction gradient. Combined with prior measurements, the platform-cohort distribution now spans from 88.9 percent (Langfuse, open signup by default) to 0 percent (AnythingLLM, hardened by default), with Label Studio at 0.2 percent as the cleanest example of "mandatory first-run signup" as a defense.

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Wardrobe outfit: `ai-infra-hunt`.

- **672 (AI Test & Evaluation Specialist):** T5919, K7044, S7067, T5904.
- **733 (AI Risk & Ethics Specialist):** T5893 / T5882, K7040 (the labeled training data is operator product IP + annotator PII).
- **NICE 541:** T0028, T0188, K0342, S0001, S0051, T0247, K0107, K0118.

<!-- ksat-tag:auto-generated:end -->

---

## Methodology

```
Stage 0    Shodan API on  http.title:"Label Studio"     →  1,646 total
            shodan download --limit 500                  →   500 IP:port saved

Stage 0c   verify.py — 200-thread, 6s timeout
            Step 1: GET /version  → JSON with "release" or "label-studio-os-package"
                    NOTE: Label Studio wraps the /version JSON in <pre>...</pre>
                    HTML. A naive json.loads of the raw body returns dead.
                    The verifier strips the <pre> wrapper before parsing.
            Step 2: GET /api/projects/?page_size=50 → 200 + {"results":[...]}
                    = unauth confirmed; 401/403 = auth-gated (the normal state)
            Step 3 (only if unauth): GET /api/users/ → user count
```

**Restraint posture.** GET on metadata only. No POST to `/api/tasks` (would create or modify annotations). No `/api/projects/{id}/export` (would dump the labeled training data). No `/api/tasks/{id}` reads (would dump individual annotation payloads). The 404 auth-gated hosts were not touched beyond the `/version` probe and the `/api/projects/` 401 check. Project titles, project counts, and user counts only for the 1 unauth host.

---

## The verifier-fix story

The first verifier run returned `0 unauth, 478 dead, 20 fp_version_shape, 2 version_auth_403` from the same 500-host sample. The 478 "dead" was wrong. Manual probing of a sample showed `/version` was returning HTTP 200 with a JSON body, but wrapped in `<pre>...</pre>` HTML tags. `json.loads("<pre>{...}</pre>")` raises `JSONDecodeError`, which the verifier was treating as "not Label Studio shape, continue to next scheme, fall out as dead."

Adding a six-line `<pre>` strip before `json.loads` changed the result from "appears all dead" to the real picture: **99.75 percent auth-gated, 0.2 percent unauth, with the version distribution and substrate breakdown visible.**

This is a generalizable methodology lesson. Insight candidate: **HTML-wrapping of API response bodies defeats naive JSON-only fingerprints; strip canonical wrappers (`<pre>`, `<code>`, leading XML declarations) before parsing.**

---

## Findings

### Distribution

| metric | value |
|---|---:|
| Shodan total | 1,646 |
| Sampled | 500 |
| Live with valid Label Studio `/version` | 407 |
| Confirmed UNAUTH | **1 (0.2 % of sample, 0.25 % of LIVE)** |
| Auth-gated 401 | 404 (80.8 % of sample) |
| Auth-gated 403 | 2 |
| Non-LS shape (FP at `/version`) | 21 |
| Dead | 72 |

### The single unauth host

| | |
|---|---|
| Host | `139.224.51.137:8083` |
| Substrate | Alibaba Cloud, CN |
| Label Studio version | 1.15.0 |
| Project count | 0 |
| User count | 1 (admin) |
| Project titles sample | (empty) |

Fresh install. The operator deployed Label Studio, completed the admin signup, and left it running on `:8083` without creating any project. There is no labeled data exposed because there is no labeled data yet.

### Version distribution (top 10 by count)

| version | hosts |
|---:|---:|
| 1.23.0 | 90 |
| 1.22.0 | 52 |
| 1.21.0 | 44 |
| 1.20.0 | 36 |
| 1.13.1 | 33 |
| 1.15.0 | 20 |
| 1.16.0 | 11 |
| 1.18.0 | 10 |
| 1.17.0 | 8 |
| 1.23.0.dev0 | 7 |

Modern (1.15 +) on 296 hosts; older (1.0 - 1.14) on 204 hosts. Operators on this platform stay current. The 33 hosts on 1.13.1 are the long-tail (1.13.x shipped Q3 2024).

### Substrate (top 10 orgs)

| org | count |
|---|---:|
| Amazon Technologies Inc. | 48 |
| Google LLC | 46 |
| Hetzner Online GmbH | 45 |
| Amazon Data Services NoVa | 32 |
| Aliyun Computing Co., LTD | 30 |
| Amazon.com, Inc. | 27 |
| A100 ROW GmbH | 17 |
| Microsoft Corporation | 16 |
| DigitalOcean, LLC | 15 |
| Tencent cloud computing (Beijing) | 14 |

Standard cloud spread. No operator-fleet concentration like the GCP Kubeflow pair from Cat-48.

---

## Thesis contribution

Label Studio at 0.2 percent unauth extends the auth-friction gradient with a new anchor:

| Platform | Default auth | Unauth at scale |
|---|---|---:|
| Langfuse | open registration | 88.9 % |
| RAGFlow | open registration | 87.2 % |
| ComfyUI | no auth concept | 77.5 % |
| Phoenix | optional env var | 74.5 % |
| Flowise | open chatflows | 68.7 % |
| Open WebUI | optional signup | 11.8 % |
| Meilisearch | optional env, doc-foregrounded | 9.6 % |
| Dify | optional signup, gated | 0.9 % |
| Kubeflow | Dex + Istio + oidc-authservice required | 0.8 % |
| **Label Studio** | **mandatory first-run signup** | **0.2 %** |
| AnythingLLM | hardened by default | 0 % |

The "mandatory first-run signup" pattern produces the cleanest 99.8 percent auth-gated result in the program. The cost to the operator is one HTML form at install time. The return at population scale is the elimination of the auth-permissive-cohort problem.

This anchors the gradient on a measurable middle: not "no auth concept" (ComfyUI), not "optional env var" (Phoenix / Meilisearch), not "complex OIDC stack" (Kubeflow), but a one-form first-run flow. Label Studio's design lets operators deploy without dealing with OIDC providers, yet still produces sub-1-percent unauth at scale.

The methodology takeaway for platform maintainers: **the auth-gradient is driven by the path of least resistance at first run, not by the sophistication of the auth stack offered.** A simple mandatory signup beats an optional sophisticated OIDC integration at population scale, because operators take the shortcut that exists.

---

## Toolchain provenance

```
shodan count "http.title:\"Label Studio\""                  →  1,646
shodan download                                              →   500
verify.py v1 (naive json.loads)                              →   0 unauth (wrong)
debug: curl manual probe                                     →   found <pre>-wrap pattern
verify.py v2 (with <pre>-strip)                              →   1 unauth confirmed,
                                                                 404 auth-gated,
                                                                 21 FP-shape
```

Wardrobe outfit: `ai-infra-hunt`. Syllabus context: PoisonedRAG-class risk applies if a labeled corpus is compromised; the data-labeling layer is upstream of the training stack, and a single annotator account compromise in a multi-tenant LS would propagate.

---

## Honest negative space

- Sample size was 500 of 1,646 Shodan-visible hosts; the unauth rate could differ in the unsampled 1,146. At 0.2 percent sampled with sample-200 verification implicit (the 1 unauth held up under per-host inspection), the population estimate of "~1 percent or less unauth at full scale" is supportable but a complete sweep is owed.
- 21 FP-shape hosts (Shodan title hit but `/version` not LS-shaped) were not investigated further. Some are likely Heartex Cloud customer-tenant front pages that share the title string with the OS version.
- No `/api/users/` or `/api/projects/{id}/members/` deep enumeration was performed on the 404 auth-gated hosts, by design. Identifying annotators by name is a PII surface we deliberately refuse to expose.
- The 1 unauth host is empty and uninteresting as a single finding. The methodology value is the thesis-anchor measurement, not the single-host disclosure.
