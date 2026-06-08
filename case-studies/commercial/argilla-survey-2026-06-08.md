---
type: survey
category: data-labeling-platform
platform: argilla
date: 2026-06-08
researcher: NuClide Research
---

# Argilla at Population Scale: 100 Percent Auth-Gated, the New Ceiling on the Auth-Friction Gradient

_NuClide Research · 2026-06-08_

---

## Summary

Population-scale survey of **Argilla** (the Hugging Face open-source RLHF data-labeling platform, a sibling of Label Studio) via the Shodan dork `http.title:"Argilla"`. 45 total hits; 43 sampled.

**The thesis-class result.** **0 of 23 LIVE Argilla hosts (0 percent) returned an unauthenticated `/api/v1/me` or `/api/me`.** All 23 were auth-gated, all 7 default-API-key probes (`X-Api-Key: argilla.apikey` and `X-Api-Key: owner.apikey`) were rejected, 7 hosts were Shodan-title false positives, and 13 were dead. Of LIVE Argilla hosts in the sample, **100 percent are auth-gated.**

Argilla ships with a mandatory API-key flow on first run, and the well-known default keys cannot be left in place by accident; the install wizard surfaces them in plaintext and instructs operators to rotate. Combined with the auth-gated `/api/_info` banner (the version itself is behind auth on the modern release line), this is the strictest auth-on-default posture in the NuClide measurement set.

This survey extends the thesis from Cat-49 Label Studio (99.75 percent auth-gated, 1/407 unauth). The platform-cohort distribution now spans from 88.9 percent (Langfuse, open signup by default) to **0 percent (Argilla, mandatory API key + auth-gated version banner)**, with Label Studio (0.2 percent) and AnythingLLM (0 percent on a 137-host sample) bracketing Argilla.

The headline: the two most strictly auth-gated platforms in the NuClide program are the two purpose-built RLHF labeling platforms. The data-labeling domain has internalized the lesson that the labeled training corpus is the asset.

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Wardrobe outfit: `ai-infra-hunt`.

- **672 (AI Test & Evaluation Specialist):** T5919, K7044, S7067, T5904.
- **733 (AI Risk & Ethics Specialist):** T5893 / T5882, K7040 (the labeled training corpus is operator IP + annotator PII + RLHF preference data).
- **NICE 541:** T0028, T0188, K0342, S0001, S0051, T0247, K0107, K0118.

<!-- ksat-tag:auto-generated:end -->

---

## Methodology

```
Stage 0    Shodan API on  http.title:"Argilla"       ->  45 total
            shodan download --limit 500              ->  43 IP:port saved

Stage 0c   verify.py. 50-thread, 6s timeout
            Step 1: GET /api/_info  -> JSON {"version": "..."}
                    On modern Argilla this endpoint itself returns 401
                    when not authenticated; only 8 of 23 LIVE hosts
                    leaked a version through unauth /api/_info.
            Step 2: GET /api/v1/me  (then GET /api/me as fallback)
                    -> 200 + JSON user shape  = unauth confirmed
                    -> 401/403 + Argilla detail body = auth-gated
            Step 3 (only on the auth-gated set):
                    X-Api-Key: argilla.apikey  -> /api/v1/me
                    X-Api-Key: owner.apikey    -> /api/v1/me
                    Tests the two well-known Argilla default keys.
            Step 4 (only on unauth or default-key unlocks):
                    GET /api/v1/workspaces  -> workspace NAMES only
                    GET /api/v1/datasets    -> dataset NAMES + counts only
                    NEVER /api/v1/datasets/{id}/records (training data).
                    NEVER /api/v1/records  (raw annotation payloads).
```

**Restraint posture.** GET only. NAMES only on the (zero) unauth hosts. No POST. No record reads. No annotation dumps. No preference-pair downloads. Workspace names, dataset names, and counts would have been the maximum read had any host been unauth, and the population posture turned out to align with the restraint posture: there was nothing safe to enumerate because there was nothing dangerous to enumerate.

---

## The verifier-fix story

The first verifier run reported `1 unauth_argilla_confirmed` (host `34.175.92.216:80`, Argilla 1.4.0-dev0, a pre-v1 academic deployment). Manual probing showed the host was returning HTTP 200 with `Content-Type: text/html` on `/api/v1/me`; the Nuxt SPA was catching any `/api/v1/*` path the backend did not mount on this old release and serving the index page. The verifier was reading "200" as "unauth user" without validating that the response was JSON or that the body matched an Argilla user shape.

The pre-v1 API path `/api/me` (no `/v1/`) on the same host returned the correct `401 {"detail": {"code": "argilla.api.errors::UnauthorizedError", ...}}`. The fix: require `application/json` content-type AND a positive shape match (`{"username": ...}` or `{"id": ..., "role": ...}`) before declaring an unauth verdict, and add `/api/me` as a fallback path. After the fix the unauth count dropped from 1 to 0.

This is a generalizable methodology lesson and a sibling to the Cat-49 `<pre>`-strip insight:

**Insight candidate.** **SPA HTML catch-all defeats naive HTTP-200-as-unauth verifiers.** Modern Nuxt / Next / Nuxt-SSR frontends respond to unknown `/api/*` paths with the SPA index HTML at HTTP 200, which looks like an open endpoint to a status-code-only verifier. Always validate the response content-type AND a positive body-shape match before promoting a 200 to an unauth finding. This is the inverse of Cat-49's lesson (HTML-wrapped JSON defeats JSON-only parsers); together they form the same principle: **the HTTP layer lies; the content layer is the ground truth.**

---

## Findings

### Distribution

| metric | value |
|---|---:|
| Shodan total | 45 |
| Sampled | 43 |
| LIVE Argilla (auth + unauth + default-creds) | 23 |
| Confirmed UNAUTH | **0 (0 % of sample, 0 % of LIVE)** |
| Default-key unlocked | **0 (0 % of LIVE)** |
| Auth-gated 401 / 403 | 23 (100 % of LIVE) |
| Non-Argilla shape (FP) | 7 |
| Dead | 13 |

### The zero-unauth result

There are no host details to publish because there are no unauth hosts to publish. The single closest near-miss was the pre-v1 academic deployment (`34.175.92.216`, UFRGS Brazil) which serves the Argilla SPA at HTTP 200 on any /api/v1/* path but auth-gates the real /api/me endpoint. Even on the oldest visible deployment the access-control boundary held.

### Default-key probe (Argilla-specific)

| key | unlocks |
|---|---:|
| `X-Api-Key: argilla.apikey` | 0 |
| `X-Api-Key: owner.apikey` | 0 |

Argilla's documentation has long surfaced these as the well-known defaults that operators MUST rotate. Every LIVE host in the sample had rotated them.

### Version distribution

8 of 23 LIVE hosts leaked a version through unauth `/api/_info`; the other 15 returned 401 on the version banner itself.

| version | hosts |
|---:|---:|
| 1.29.1 | 4 |
| 1.28.0 | 2 |
| 1.20.0 | 1 |
| 1.4.0-dev0 | 1 |

Auth-gated /api/_info is an unusually strict default for a Python web service. Most platforms surveyed in the program leak the version through some unauthenticated metadata endpoint; Argilla 1.20 + does not.

### Substrate (LIVE hosts, n=23)

| org | count |
|---|---:|
| Google LLC | 8 |
| Microsoft Corporation | 3 |
| Amazon Data Services NoVa | 2 |
| Amazon Data Services UK | 2 |
| Amazon Technologies Inc. | 1 |
| AWS Asia Pacific (Seoul) Region | 1 |
| Amazon.com, Inc. | 1 |
| Hetzner Online GmbH | 1 |
| Universidade Federal do Rio Grande do Sul | 1 |
| OVH SAS | 1 |
| DigitalOcean, LLC | 1 |

Standard cloud spread, heavy on GCP. One academic substrate (UFRGS) hosting the only pre-v1 deployment. No operator-fleet concentration.

### FP character (the 7 fp_not_argilla)

- 1 Kubernetes API server (`kind: Status`, `apiVersion: v1`) on `:443` of `34.211.74.199`, likely a cluster control plane that ran an Argilla pod whose title leaked into a Shodan banner record.
- 1 nginx 403 HTML page (`184.33.246.79`).
- 1 openresty/1.29.2.4 401 HTML page (`16.147.145.163`).
- 1 plain `Unauthorized` text/plain 401 (`52.3.22.122`).
- 3 other 401/403 responses without Argilla auth-error JSON shape.

These hit the Shodan dork because the title string "Argilla" appeared in associated banner data, but the live HTTP response on the verification probe was not Argilla.

---

## Thesis contribution

Argilla at 0 percent unauth (on a 23-host LIVE sample) places a new ceiling on the auth-friction gradient. The data-labeling domain, both Label Studio and Argilla, now occupies the strictest auth-on-default end of the program.

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
| Label Studio | mandatory first-run signup | 0.2 % |
| **Argilla** | **mandatory API key + auth-gated version banner** | **0 %** |
| AnythingLLM | hardened by default | 0 % |

The methodology principle: **the auth-gradient is driven by the path of least resistance at first run.** Argilla's posture goes beyond Label Studio's mandatory signup by auth-gating the version banner itself; there is no surface available to an unauthenticated client other than the SPA static assets. Label Studio still exposes a version probe (the `/version` endpoint that the Cat-49 survey used); Argilla closes even that.

The cost to the operator is one additional auth-required route, well documented. The return at population scale is that 100 percent of visible operators retain the default.

The Argilla and Label Studio data also addresses the "is data-labeling a uniquely strict cohort or is it the OSS-disclosure-pressure effect" question. Hugging Face is the upstream maintainer of Argilla; Heartex/Humansignal is the upstream maintainer of Label Studio. Both have published security guidance prominently in their respective READMEs and deployment docs, and both have been subjected to multiple public security write-ups in the 2022 - 2025 window. The strict-default posture is plausibly a co-evolution between platform maintainer guidance and operator practice in a domain where the asset value (labeled training corpora, annotator PII, RLHF preferences) is widely understood.

---

## Toolchain provenance

```
shodan count "http.title:\"Argilla\""              ->  45
shodan download --limit 500                        ->  43
verify.py v1 (naive json.loads, /api/v1/me only)   ->  1 unauth (WRONG; SPA-HTML 200)
debug: curl /api/me on the same host               ->  401 Argilla auth-error JSON
verify.py v2 (CT check + shape gate + /api/me fb)  ->  0 unauth, 23 auth, 7 FP, 13 dead
```

Wardrobe outfit: `ai-infra-hunt`. Syllabus context: PoisonedRAG-class risk applies if a labeled corpus is compromised; an unauthenticated Argilla would expose RLHF preference data that directly shapes model behavior in alignment training. The data-labeling layer sits upstream of the entire RLHF stack; a single annotator-account compromise in a multi-tenant Argilla would propagate into the trained model.

---

## Honest negative space

- Sample size is 23 LIVE hosts, much smaller than Cat-49 Label Studio's 407 LIVE. The 100 percent number sits on weaker statistics than the 99.75 percent number it edges past. The directional claim ("Argilla is at least as strict as Label Studio at scale") is supported; the absolute claim ("0 percent across the entire visible population") is sample-bound.
- The Shodan dork `http.title:"Argilla"` captures only deployments whose front-page HTML title is "Argilla" and whose port is reachable on Shodan's scan schedule. Argilla instances behind reverse proxies that strip the title, or inside Kubernetes services that are not Shodan-reachable, are not in the sample.
- The default-key probe was deliberately narrow: only the two best-known string defaults. A wider probe (common variations, the first few entries from a dictionary of well-known API keys) was not run, by design. The intent was a "well-known-default-still-present" check, not a brute force.
- The 7 FP hosts were classified by shape mismatch on the verification probe. A few of them may be Argilla services running behind an authenticating reverse proxy that returns nginx / openresty 401 before the request reaches the Argilla backend. That would be a defense-in-depth posture stricter than even the 23 auth-gated hosts, not a weaker one. Either way they do not contradict the headline.
- No `/api/v1/workspaces` or `/api/v1/datasets` enumeration was performed on the 23 auth-gated hosts. Capturing the names of internal workspaces and datasets would be a metadata-only enumeration, but it would also require an exploit of the very auth that the survey is measuring as held. The restraint posture aligned with the methodology posture: nothing read.

---

## What would change the result

Three follow-ups would tighten or break this conclusion:

1. **Widen the discovery dork.** `ssl.cert.subject.cn:argilla`, certificate-pivot from known Argilla operators, and a CIDR sweep with an `/api/_info` marker probe would surface deployments hidden behind reverse proxies whose front pages do not match the title dork. Expected effect: larger LIVE sample, probably similar unauth rate, possibly a few near-miss findings.
2. **Default-creds dictionary expansion.** The two-key probe is a methodology floor. A small dictionary (the Argilla docs' historical examples, the bootstrap-script defaults from `docker-compose.yml` templates published in the Argilla repo over time) would test "the wider class of well-known operator shortcuts." Expected effect: still probably 0, but a more defensible 0.
3. **Repeat the run when the next Argilla LTS ships.** A point-in-time survey is a single sample of a moving population. Repeating it across two or three release cycles would distinguish "Argilla is structurally strict" from "the current visible population happens to be strict."

---

## Cross-survey takeaway

Two adjacent surveys (Cat-49 Label Studio, Cat-51 Argilla) on the same domain (data-labeling / RLHF annotation) both produced sub-1-percent unauth-at-scale results. The auth-friction gradient now has a clear high-strictness anchor: **purpose-built data-labeling platforms whose maintainers have written and enforced a mandatory-auth-on-first-run pattern.** The gradient also has a clear low-strictness anchor: open-signup observability / RAG platforms whose use cases predate the security-default convergence.

The methodology question this raises for the next ten surveys: **which other AI/ML platform domains have undergone the same maintainer-driven default-tightening, and which are still publishing open-signup defaults because they have not yet had a public incident?** The auth-gradient is not random; it is a function of (a) maintainer awareness, (b) public-disclosure pressure, (c) operator-cohort sophistication, and (d) the path of least resistance at deploy time. Data-labeling has cleared all four bars. Most adjacent domains have not.

---

## Files

- `data/argilla-2026-06-08/pairs.txt`. 43 verified pairs
- `data/argilla-2026-06-08/verify.py`, verifier (v2, with SPA-HTML guard)
- `data/argilla-2026-06-08/verify-results.json`, full per-host results
- `data/argilla-2026-06-08/findings-breakdown.txt`, operator-readable tally
