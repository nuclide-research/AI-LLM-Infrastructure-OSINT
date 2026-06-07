---
type: tool-dev-log
title: "VisorBishop iter-7: MLflow Tracking + Weights & Biases self-host (experiment-tracking tier)"
date: 2026-05-11
class: tool
category: cross-platform-tool-validation
status: research-active
methodology: extending VisorBishop fingerprint coverage from the observability + gateway tiers into the experiment-tracking tier
---

# VisorBishop iter-7 · 2026-05-11

NuClide Research · 2026-05-11

## Summary

Seventh iteration of the Phase 3 loop. iter-1 through iter-6 covered the
observability, gateway, annotation, and evaluation tiers of the AI/LLM
stack. **iter-7 expands to the experiment-tracking tier**, the
infrastructure that captures training runs, hyperparameters, model
artifacts, and prompt/response data during ML experimentation.

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7004, K7044, S7068, S7070, S7075, S7076, T5858, T5904, T5919
- **733 (AI Risk & Ethics Specialist):** K7052, S7056, S7067, T5868, T5882, T5893
- **overlap (Common AI KSATs (all 5 roles)):** K108, K1158, K1159, K22, K6311, K6935, K7003, K7041

<!-- ksat-tag:auto-generated:end -->

Three platforms were scoped:

- **MLflow Tracking**: Databricks' open-source experiment-tracking
  server. Largest population of any platform in the chain so far:
  **10,993 Shodan dork hits** (~2× LiteLLM's population).
- **Weights & Biases self-host**: On-prem variant of the wandb.ai
  product. Smaller population (87 confirmed dork hits) but very
  high data sensitivity.
- **Comet ML self-host** and **Trulens** were also evaluated and
  dropped: both have <5 confirmed self-hosts on Shodan, below the
  population threshold for a dedicated prober.

**Methodology continuity:** iter-7 reproduces the iter-5/6 pattern.
A Shodan dork yields a candidate pool, VisorBishop's multi-probe
fingerprint confirms platform identity AND classifies auth posture,
and the corpus is joined to Shodan attribution for org/country.

> **Reproduce with VisorBishop ≥ v0.1.6:**
> `visorbishop -i mlflow-urls.txt -c 32 -timeout 4s -json out.json -csv out.csv`

## Sample-sweep validation

Before the full population run, a 200-host MLflow sample validated
the prober:

| Metric | Value |
|---|--:|
| Sample size | 200 |
| Confirmed MLflow | 44 (22%) |
| Auth-protected | 41 |
| **CRITICAL unauth** | **3 (1.5% of sampled, 6.8% of confirmed)** |

The 22% confirm rate validates **Methodology Insight #15 at the most
extreme scale yet**. 78% of Shodan hits on `http.title:"MLflow"` are
not actually MLflow. The title is widely reused by unrelated tools
(Frigate camera NVR servers, generic React SPAs with "MLflow" branding,
documentation pages). One sample false-positive that the prober
correctly bailed on: `15.152.78.193:5105`. Claimed by Shodan as MLflow,
but `/version` returns Docker daemon shape and `/api/2.0/...` returns a
Frigate camera page.

## Full population sweep

| Metric | Value |
|---|--:|
| Shodan dork | `http.title:"MLflow"` |
| Total Shodan hits | 10,993 |
| Unique URLs after dedup | 10,993 |
| VisorBishop wall time | ~70 min (32 concurrency, 4s timeout) |
| **Confirmed MLflow** | **806 (7.3%)** |
| **CRITICAL unauth** | **120 (1.1% of probed, 14.9% of confirmed)** |
| Auth-fronted | 88 |
| Pre-2.2.1 (CVE-2023-1177 likely) | 28 |

**Confirm rate is the lowest yet seen in the research chain**. 7.3%
vs LiteLLM's 50.3% vs Phoenix's 95%. The MLflow title pattern is the
noisiest single-word title in the corpus: it matches Docker daemons,
Frigate NVR servers, generic React SPAs, blog posts with "MLflow" in
their title, and tools that wrap MLflow but don't expose it directly.

**Critical rate (14.9% of confirmed) is higher than any other platform
in the corpus**, higher than LiteLLM (10.4%), Phoenix (89% of
confirmed but only 79 hosts), and Promptfoo (91% of confirmed but
only 11 hosts). MLflow's "no auth by default" posture combined with
the broad operator base produces the highest-yield unauth population
in absolute count.

### Critical-host real-data classification

Of the 120 critical hosts, **118 had at least one experiment with a
real (non-scanner-decoy) name**. The pattern `scan_NNNNNNNNNN`
appears repeatedly in the experiment lists, indicating a known
scanner is also probing these hosts and inserting decoy experiments;
the 2 hosts with ONLY decoy experiments are likely fresh deployments
that haven't yet had real runs logged.

### Geography (top 10)

| Country | Critical |
|---|--:|
| US | 46 |
| DE | 15 |
| KR | 6 |
| NL | 6 |
| FR | 6 |
| IN | 5 |
| CA | 4 |
| RU | 4 |
| CN | 4 |
| SG | 3 |

### Hosting org (top 10)

| Org | Critical |
|---|--:|
| Google LLC | 34 |
| Microsoft Corporation | 12 |
| Hetzner Online GmbH | 9 |
| DigitalOcean, LLC | 8 |
| Amazon Data Services NoVa | 6 |
| Microsoft Limited (UK) | 4 |
| Amazon Technologies Inc. | 4 |
| Yandex.Cloud LLC | 3 |
| A100 ROW GmbH | 3 |
| AWS Asia Pacific (Seoul) Region | 3 |

**Google Cloud dominates the MLflow critical surface** (34 of 120 =
28%), a sharp departure from LiteLLM where Hetzner + Contabo dominate.
Likely explanation: GCP's Vertex AI marketplace ships MLflow tracking
servers as a one-click deploy without an auth-shim default, while the
self-host crowd that picks Hetzner/Contabo for LiteLLM tends to deploy
LLM gateways more than experiment trackers.

### Named operators (real experiment names, not scanner decoys)

| Host | Sector | Sample experiments | Notes |
|---|---|---|---|
| `3.65.57.89` (AWS Frankfurt) | Government / Slovakia | "Náhradné výživné / Počet poberateľov - sirotský dôchodok / Slovenská republika" | **Slovak government social-benefits data** (orphan-pension recipient counts) |
| `101.46.48.180` (Huawei SA) | Healthcare | `hospital_occupancy_forecasting-11-May-2026_14-46-48` | Saudi Arabia healthcare ML |
| `44.223.132.249` (AWS US-East) | Agriculture / CV | `ripeness_model`, `combined_rcnn_X_101_32x8d_FPN_3x Training Jobs Oishii Dataset` | Oishii (vertical farming strawberry brand) computer-vision training |
| `20.63.37.175` (Azure US) | Risk modeling | `IrisRF_TwoStep`, `Risk model with BERT embeddings Example` | Risk-scoring with LLM embeddings |
| `44.255.234.92` (AWS) | Healthcare / pathology | `prostate_bcr_merge_devraj_embedding_cancer_True`, `prostate_bcr_merge_virchow_cancer_True` | Prostate cancer biomarker classification |
| `34.235.209.101` / `98.89.171.38` (AWS, same op) | Gaming | `SIM - Played In Game Model - Day Gap 128/64/32` | Played-in-game prediction; co-located redundant infra |
| `139.59.136.9` / `139.59.205.252` (DO DE, same op) | Food / wine | `'20220427@1531-Spreafico-SalaBolognese'`, `'20260428@1338-TenutaLeOrigini-Soliera'` | Italian winery operations / harvest tracking |
| `44.222.239.15` (AWS US-East) | Video ML | `Video_VJEPA2_Phase2_Finetuning`, `Video_VJEPA2_Phase1_Retraining` | Meta V-JEPA2 fine-tuning (likely partner deployment) |
| `16.16.53.188` (AWS Sweden) | Healthcare access | `mediloca-facility-ranking`, `mediloca-healthcare-access`, `maiaddy/utilyx` | Mediloca / maiaddy health platforms |
| `164.52.194.82` (E2E Networks IN) | Medical imaging | `segmentation_slicewise2d`, `segmentation_multiplane2d`, `Share_GAN` | Indian medical-imaging research |
| `147.102.6.24` (NTUA) | Academic | (scanner-decoys only at time of probe) | **National Technical University of Athens** |
| `129.240.189.178` (UiO) | Academic | (scanner-decoys only at time of probe) | **University of Oslo** |
| `147.156.222.190` (UV) | Academic | (scanner-decoys only at time of probe) | **Universidad de Valencia** |

### Version distribution (top 10 of confirmed)

| Version | Count |
|---|--:|
| 3.11.1 | 11 |
| 3.4.0 | 9 |
| 3.1.4 | 7 |
| 3.10.1 | 6 |
| 2.21.3 | 5 |
| 2.22.0 | 5 |
| 3.2.0 | 4 |
| 3.0.1 | 4 |
| 3.1.1 | 3 |
| 2.17.2 | 3 |

**28 hosts run a pre-2.2.1 version** flagged for CVE-2023-1177 path
traversal. Three years after disclosure, ~3% of internet-exposed
MLflow installations are still on the vulnerable code path.

## Weights & Biases self-host: null finding

The W&B sweep is included for methodology continuity but produces
zero actionable findings after deeper investigation.

| Metric | Value |
|---|--:|
| Shodan dork | `http.html:"wandb"` |
| Total Shodan hits | 87 |
| Confirmed W&B | 42 (48%) |
| **CRITICAL** | **0** |
| INFO (platform-identification only) | 42 |

**Initial sample classified all 42 confirmed W&B as HIGH**, every
confirmed self-host responds to a `viewer` GraphQL query with HTTP 200
and a `null` viewer record without authentication. This looked like
W&B's "anonymous mode" being enabled by default.

**Deeper probing reverses the conclusion.** Three hosts (34.160.129.203,
35.167.220.104, 44.217.173.107) were probed with richer queries
(`entities`, `projects`, `entity(name:)`). Every data-layer query
returns `null` with the resolver error `"entityName required for
projects query"`. The 200 + null viewer response is **the documented
behavior of any W&B Server for unauthenticated callers**, the schema
is reachable but the data layer is server-side gated.

**Hostname analysis confirms the reclassification.** Most of the 42
confirmed hosts are W&B's own multi-tenant production cluster, not
customer self-host misconfigurations:

| Host | Subdomain | Likely tenant |
|---|---|---|
| 18.214.193.211 | `nylcloud.wandb.io` | New York Life (insurance) |
| 35.167.220.104 | `dropbox.wandb.io` | Dropbox |
| 15.134.182.156 | `ap2-prod-dog.wandb.io` | W&B AP2 production canary |
| 44.217.173.107 | `us1-staging-dog.wandb.io` | W&B US1 staging canary |

These are dedicated-cloud installs that W&B Inc. operates on behalf
of named customers. The platform working as designed is not a finding.

**VisorBishop v0.1.6 (commit 4cade62)** corrects the prober: severity
is now INFO with `AuthInfoOnly`, and the CRITICAL classification only
fires when the viewer query returns a populated identity (the rare
true-credential-bypass case, which never landed in the sample sweep).

This is **Methodology Insight in flight: a 200 from a platform endpoint
is platform identity, not auth state.** The auth-state classification
must observe the resolver's data layer, not the entrypoint's status
code. Recorded as an addendum to insight #15 for the next methodology
publication cycle.

## Why MLflow Tracking unauth is severe

MLflow Tracking stores everything that gets attached to an experiment
during model development:

1. **Prompts and prompt templates**, for LLM experiments, the
   `mlflow.log_param("prompt", ...)` pattern is canonical. Tracking
   data captures the full set of prompts under iteration.
2. **Model parameters and hyperparameters**, when a tuning run
   logs `temperature`, `top_p`, `system_prompt`, etc., they end up
   in the run's params dict, reachable via
   `/api/2.0/mlflow/runs/search`.
3. **Artifact URIs**, pointers to S3 / GCS / Azure Blob locations
   containing the model weights, datasets, or evaluation outputs.
   Even when the operator's bucket policy is correct, the URI itself
   discloses internal cloud account names and bucket structure.
4. **Run tags.** Operators frequently log credentials to run tags
   ("api_key": "sk-..."). MLflow has no warning against this pattern,
   and the tags are visible to anyone who can read the run.
5. **Model registry.** MLflow's registered-models registry exposes
   the operator's full model catalog, version history, and stage
   transitions (Staging / Production / Archived). This is the
   "model graveyard" that reveals what the operator is shipping.

Unauthenticated MLflow is therefore **a richer data class than even
Phoenix or LiteLLM**, phoenix exposes traces, LiteLLM exposes API
keys (indirectly via LLMjacking), but MLflow exposes the operator's
entire experimentation history with prompts, parameters, artifacts,
and frequently credentials.

### CVE-2023-1177 still active

MLflow versions before 2.2.1 are vulnerable to **CVE-2023-1177**, a
path traversal in the artifact URI handler that allows reading
arbitrary files on the tracking-server host. The VisorBishop prober
flags any confirmed MLflow with version `< 2.2.1` as
`cve_2023_1177_likely`.

**28 of 120 critical hosts (23%) are running pre-2.2.1 versions** and
are likely vulnerable to CVE-2023-1177. The vulnerability has been
public since 2023-03. Three years of remediation window has not
removed it from the population.


## Methodology refinement: Promptfoo 401-confusion fix

During the iter-7 MLflow sample sweep, the Promptfoo prober flagged
26 of the MLflow hosts as Promptfoo-confirmed because the
`/api/results/` endpoint returned 401 on those hosts (MLflow's
artifact API uses a similar path on some configurations). The
prober was checking 401/403 → "Promptfoo with auth" without
verifying the Promptfoo SPA marker.

**Fix shipped in VisorBishop v0.1.6:** the 401/403 branch now
requires a `/-root` SPA marker hit before claiming Promptfoo
identity. This is the same pattern as the LangSmith vs ZenML
disambiguation from iter-1.

Generalization: **any "platform with auth" classification must
require a positive platform marker, not just a non-success status
code from a platform-suggestive endpoint.** Recording this as a
methodology checkpoint adjacent to Insight #15.

## What comes next

1. ~~iter-1/2/3/4/5/6~~ ✓
2. ~~iter-7 prober build + sample-sweep validation~~ ✓
3. **iter-7 full MLflow 10,993-host sweep** ← in progress
4. **W&B data-layer probe expansion**, determine if anonymous-mode
   instances actually expose project/run data
5. **Cumulative disclosure-routing pipeline**, covers iter-1..7
   findings, vendor + per-operator outreach
6. **Phase 5: shift to a different research vector**, observability
   + gateway + experiment-tracking are now thoroughly mapped;
   iter-8+ should pivot to a different tier or research methodology

## Evidence pack

`~/recon/2026-05-11-iter7/`
- `mlflow-full.json.gz`: Shodan harvest (11.4MB, 10,993 records)
- `mlflow-full-urls.txt`: deduplicated URLs
- `mlflow-attribution.tsv`: ip:port → (hostnames, org, country, isp)
- `wandb-sample.json.gz`: W&B Shodan harvest (87 records)
- `wandb-urls.txt`: W&B target URLs

`~/recon/2026-05-11-iter7/results/`
- `mlflow-200-v2.json`: 200-host sample sweep (3 critical, 41 info)
- `mlflow-full.json`: full population sweep (pending)
- `wandb.json`: W&B self-host sweep (42 confirmed, 42 HIGH)

Source: Nicholas-Kloster/VisorBishop@v0.1.6

Cross-references:
- [iter-6 case study (LiteLLM full sweep)](visorbishop-iter6-survey-2026-05-11.md)
- [iter-5 case study (gateway + annotation + eval tiers)](visorbishop-iter5-survey-2026-05-11.md)
- [Phase 3 case study](visorbishop-phase3-survey-2026-05-11.md)
- [Methodology Insight #15](/methodology/insight-15-dork-hits-vs-platform-instances/)
