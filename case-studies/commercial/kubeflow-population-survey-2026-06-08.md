---
type: survey
category: ml-pipeline-orchestration
platform: kubeflow-pipelines
date: 2026-06-08
researcher: NuClide Research
---

# Kubeflow Pipelines at Population Scale: 0.8 Percent Unauth, and the Long Tail is a Fortune-500 Customer Book

_NuClide Research · 2026-06-08_

---

## Summary

Population-scale survey of Kubeflow Pipelines via the Shodan dork `http.title:"Kubeflow"`. 619 total hits, all harvested. Verified via the `/pipeline/apis/v1beta1/experiments` endpoint.

**The thesis-class result.** **5 of 619 hosts (0.8 percent) returned the unauthenticated experiments list.** 14 hosts returned a 401 at root (Dex login enforced); 3 returned 403. The rest of the population (~560) was Shodan-title FP. Kubeflow at population scale is **mostly auth-gated**.

This is the cleanest break we have logged from the auth-permissive-cohort thesis (Insight #76). Where Langfuse SIGNUP_OPEN, RAGFlow REGISTER_OPEN, ComfyUI, and Ray Dashboard all sit at 9-to-89 percent unauthenticated at population scale, Kubeflow sits at 0.8 percent. The deploy friction (Dex + Istio + oidc-authservice) is enough to flip the platform out of the cohort. Five operators chose the single-user `apiServerMultiUser=false` shortcut. Five hundred and sixty did not.

**The long-tail finding.** Of the five misconfigured operators, two are co-located on Google Cloud at `35.212.46.10` and `35.212.83.172` and **share 11 customer experiment names**. Same SaaS, two Kubeflow instances, 557 experiments total, all in single-user (no-auth) mode. The experiment names disclose the operator's entire customer book.

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Wardrobe outfit: `ai-infra-hunt`.

- **672 (AI Test & Evaluation Specialist):** T5919 (adversarial test in op env), K7044 (V&V tools), S7067 (low-prob high-impact data risks), T5904 (per-host risk assessment).
- **733 (AI Risk & Ethics Specialist):** T5893 / T5882 (responsible AI, names-not-payloads), K7040 (PII surface), T5854 (third-party data class implications).
- **NICE 541:** T0028, T0188, K0342, S0001, S0051, T0247, K0107, K0118.

<!-- ksat-tag:auto-generated:end -->

---

## Methodology

```
Stage 0    Shodan API on  http.title:"Kubeflow"        →  619 total
            shodan download                            →  619 IP:port saved

Stage 0c   verify.py — 200-thread, 6s timeout
            Step 1: GET /  → confirm "Kubeflow" in HTML title or body
            Step 2: GET /pipeline/apis/v1beta1/healthz → Pipelines alive
            Step 3: GET /pipeline/apis/v1beta1/experiments?page_size=20
                    → 200 + JSON with "experiments" key = unauth confirmed
            Step 4: GET /pipeline/apis/v1beta1/runs?page_size=20
                    → 200 + JSON with "runs" key (only if unauth confirmed)

Result: 5 confirmed unauth, 14 401, 3 403, 560 not-Kubeflow at root,
        18 dead, 6 FP-shape, 1 timeout
```

**Restraint posture.** GET on metadata endpoints only. No POST to `/runs` (which would trigger a pipeline). No `/runs/{id}` reads (which would dump the run's input parameters, secrets, and artifact paths). No notebook reads via `/jupyter`. No view of individual experiment details via `/experiments/{id}`. The five unauth hosts had their experiment names + counts + runs counts captured; nothing more.

---

## The five confirmed unauth hosts

| host | substrate | Kubeflow ver | experiments | multi_user |
|---|---|---|---:|---|
| `35.212.46.10` | Google Cloud US | 2.3.0 | **297** | false (deliberate single-user) |
| `35.212.83.172` | Google Cloud US | 2.14.0 | **260** | false (deliberate single-user) |
| `110.239.88.22` | Huawei Cloud Indonesia POP | unknown | 113 | false |
| `20.249.68.212` | Microsoft Azure | 2.0.5 (Dec 2023) | 2 | false |
| `54.146.201.111` | AWS EC2 us-east-1 | unknown | 2 | false |

All five report `apiServerMultiUser: false`. This is the Kubeflow single-user deployment mode, in which the operator explicitly skips Dex + Istio auth setup. It is the framework's documented "easier deploy"; it is also the deploy that ships the Pipelines API on the public internet with no authentication.

---

## The Google Cloud SaaS finding

The two GCP hosts (`35.212.46.10` and `35.212.83.172`) are operator-co-located. They share 11 customer experiment names exactly, run Kubeflow 2.3.0 and 2.14.0 respectively (an 18-month version gap suggesting two generations of the same operator's infrastructure), and host 557 total experiments together. Both report single-user mode. Neither presents a TLS certificate. Adjacent `/24` hosts are unrelated SiteGround VPS tenants, ruling out cluster-level attribution from neighbor analysis.

The operator is identifiable only from the experiment names. The names form a B2B-retail-execution AI SaaS customer pattern.

### Shared customer experiments (visible on both hosts)

| name | almost-certain customer brand |
|---|---|
| `BAT UZ` | British American Tobacco, Uzbekistan |
| `Coremark_Canada_AI_Training` | Core-Mark, $20B+ convenience-store distributor |
| `Eurpac-US` | Eurpac, US military commissary distributor |
| `Kenvue_SaudiArabia_Pilot` | Kenvue (Johnson & Johnson consumer-health spinoff), KSA |
| `Kenvue_Turkey_AI Training` | Kenvue, Turkey |
| `Kenvue_UAE_AI_training` | Kenvue, UAE |
| `Penafiel Pilot` | Peñafiel (Keurig Dr Pepper Mexico) |
| `Tienda_Neto_Mexico_AI_Training` | Tienda Neto, Mexican supermarket |
| `3dim_chi_AI_Training` | 3DIM Chile (likely) |
| `Driveline_Rollout_US_DL` | Driveline Retail Merchandising, US |

### Per-host customer experiments

`35.212.46.10` (Kubeflow 2.3.0) additional:

| name | customer |
|---|---|
| `Alsuper - Pilot` | Alsuper, Mexican supermarket chain |
| `BAT Denmark - Prod` | British American Tobacco |
| `Bacardi_Travel_Review_AI_Training` | Bacardi |
| `Luce-IT-Portugal_POC` | Luce IT, Portuguese IT services |
| `Massy_Guyana_POC` | Massy Group, Caribbean conglomerate |
| `Mondelez-Vietnam(Pilot)-MT` | Mondelez International, Vietnam |
| `Nutrabolt_Pilot_AI_Training` | Nutrabolt ($1B+ supplement maker, Bloom + Cellucor brands) |
| `Roamler (Pierre Fabre)- POC` | Pierre Fabre (French pharmaceutical $2B+) via Roamler |
| `VJ_Salomone` | VJ Salomone, Maltese F&B distributor |

`35.212.83.172` (Kubeflow 2.14.0) additional:

| name | customer |
|---|---|
| `BAT Poland Int Prod` | British American Tobacco |
| `Bacardi_Travel_Review_Pilot _Sticker_Training_POC` | Bacardi |
| `J&J_SouthAfrica_Pilot` | Johnson & Johnson |
| `Kellanova_AI_Training` | Kellanova (Kellogg's snack-foods spinoff) |
| `Mondelez_MT_Pilot` | Mondelez International |
| `SIGMA` | SIGMA Alimentos (Mexican food group) |

### Operator inference

The cluster reads as a **B2B retail-execution / shelf-audit / planogram AI SaaS** with global Fortune-500 brand coverage. The geographic concentration (Mexican retail anchors Tienda Neto + Alsuper + Peñafiel + SIGMA) and "POC / Pilot / Prod / AI_Training" lifecycle suffixes are characteristic of a LatAm-headquartered or LatAm-specialist retail-AI vendor. The Eurpac entry is the DOD-adjacent surface (military commissary distributor).

The operator is not identified by NuClide. The naming-based attribution stops at "approximately 15 to 25 Fortune-500 consumer-goods brands as a global B2B AI customer book."

---

## Risk

For each unauth Kubeflow host, the exposed surface is:

1. **Experiment + run name disclosure** — customer book, project naming conventions, lifecycle stage. For a SaaS operator, this is competitive intelligence + customer relationship disclosure.
2. **Pipeline trigger** — `POST /pipeline/apis/v1beta1/runs` is unauth-callable. An attacker can submit arbitrary pipeline runs against the operator's compute.
3. **Run input parameter disclosure** — `GET /pipeline/apis/v1beta1/runs/{id}` returns pipeline input parameters, which commonly include cloud-storage credentials, model URIs, dataset URLs, and secrets injected via Kubeflow secrets.
4. **Notebook exposure** — `/jupyter` endpoints on the same gateway are typically equally unauth in single-user mode.
5. **Cluster-level pivot** — Kubeflow Pipelines runs inside a Kubernetes cluster; an attacker who can submit pipelines gets code execution inside the cluster's namespace, then can pivot through Kubernetes RBAC to other workloads if the namespace has cross-resource permissions.

Per-host severity for the two GCP hosts: **critical** (Fortune-500-tier customer disclosure + pipeline-trigger surface + cluster-level pivot). For the Huawei / Azure / AWS hosts: **high** (smaller experiment counts, no clear customer disclosure, but the same pipeline-trigger and cluster-pivot surface).

---

## Toolchain provenance

```
shodan count "http.title:\"Kubeflow\""                       →  619
shodan download kubeflow                                     →  619 IPs
verify.py (200-thread urllib + ThreadPool)                  →  5 confirmed unauth
dig + whois on 5 confirmed                                   →  GCP / Huawei / Azure / AWS
adjacent /24 cert probe                                       →  unrelated SiteGround tenants
public-record check via WebSearch                             →  CVE-2026-47237 Istio
                                                                permissions + multiple
                                                                Kubeflow exposure reports
```

Wardrobe outfit: `ai-infra-hunt`. Syllabus context: Kubeflow's auth design surfaces in
PoisonedRAG-adjacent literature only via the pipeline-trigger primitive (attacker-submitted
training that poisons a downstream RAG corpus).

---

## Thesis contribution

Kubeflow at 0.8 percent unauth is the cleanest break we have logged from the auth-permissive-cohort thesis. The same-cohort spread now reads:

| Platform | Default auth | Unauth at scale |
|---|---|---:|
| Langfuse | open registration | 88.9 % |
| RAGFlow | open registration | 87.2 % |
| ComfyUI | no auth concept | 77.5 % |
| Phoenix | optional env var | 74.5 % |
| Flowise | open chatflows | 68.7 % |
| Meilisearch | optional env var (doc-foregrounded) | 9.6 % |
| Open WebUI | optional signup | 11.8 % |
| Dify | optional signup (gated) | 0.9 % |
| **Kubeflow** | **Dex + Istio + oidc-authservice required** | **0.8 %** |
| AnythingLLM | hardened-by-default | 0 % |

The Kubeflow result strengthens Insight #76 by giving the thesis a clean control: when default-auth requires non-trivial deploy work (a multi-component OIDC stack), the platform stays out of the auth-permissive cohort at population scale. The cost is operator deploy friction. The five unauth Kubeflows are the operators who paid the opt-out: they explicitly set `apiServerMultiUser=false` to skip the auth setup.

This is the deploy-friction story from the inverse direction. Where Meilisearch shows "documented opt-in flips ~10 percent to unauth," Kubeflow shows "documented mandatory setup keeps sub-1 percent unauth even with a defined opt-out."

---

## Disclosure routing

NuClide does not directly contact the operator. Routing:

1. **GCP abuse@google.com** for the two `35.212.x` hosts, with a sanitized customer-count description. GCP will route to their tenant.
2. **Huawei Cloud Indonesia** abuse channel for `110.239.88.22`.
3. **Microsoft Azure** abuse for `20.249.68.212`.
4. **AWS abuse** for `54.146.201.111`.
5. **Kubeflow project maintainers** for upstream: a stronger warning in the single-user-mode docs that single-user mode is public-internet-exposed-by-default and should never be used on a public IP.

Draft routing template lives in the assessments package (not in this case study).

---

## Honest negative space

- 560 Shodan-title hits did not present Kubeflow at HTTP root. The Shodan title-match is firing on cached banners where Kubeflow appears in `<meta>` or elsewhere but the current root is a different application (ingress controller, default nginx, generic API). A deeper sweep would re-check those 560 against `/pipeline/apis/v1beta1/healthz` directly; the present survey accepted the root-shape FP rate as a known cost.
- The operator behind the GCP pair was not identified by name. Pivoting via cert (no TLS), via Whatsapp/Linkedin, or via Roamler's public partner page is possible but not done here per the restraint discipline (we stop at "this is a B2B retail-AI SaaS with this customer pattern" until we have a route to disclose to the operator directly).
- Run names, run statuses, pipeline parameters, artifact URIs were not captured. The pipeline-trigger surface was identified by API documentation, not exercised.
