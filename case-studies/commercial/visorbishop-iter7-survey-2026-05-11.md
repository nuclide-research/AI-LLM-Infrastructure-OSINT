---
title: VisorBishop iter-7 — MLflow Tracking + Weights & Biases self-host (experiment-tracking tier)
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
stack. **iter-7 expands to the experiment-tracking tier** — the
infrastructure that captures training runs, hyperparameters, model
artifacts, and prompt/response data during ML experimentation.

Three platforms were scoped:

- **MLflow Tracking** — Databricks' open-source experiment-tracking
  server. Largest population of any platform in the chain so far:
  **10,993 Shodan dork hits** (~2× LiteLLM's population).
- **Weights & Biases self-host** — On-prem variant of the wandb.ai
  product. Smaller population (87 confirmed dork hits) but very
  high data sensitivity.
- **Comet ML self-host** and **Trulens** were also evaluated and
  dropped: both have <5 confirmed self-hosts on Shodan, below the
  population threshold for a dedicated prober.

**Methodology continuity:** iter-7 reproduces the iter-5/6 pattern —
a Shodan dork yields a candidate pool, VisorBishop's multi-probe
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
extreme scale yet** — 78% of Shodan hits on `http.title:"MLflow"` are
not actually MLflow. The title is widely reused by unrelated tools
(Frigate camera NVR servers, generic React SPAs with "MLflow" branding,
documentation pages). One sample false-positive that the prober
correctly bailed on: `15.152.78.193:5105` — claimed by Shodan as MLflow,
but `/version` returns Docker daemon shape and `/api/2.0/...` returns a
Frigate camera page.

## Full population sweep

[PENDING — full 10,993-host sweep in progress at writeup time.]

| Metric | Value |
|---|--:|
| Shodan dork | `http.title:"MLflow"` |
| Total Shodan hits | 10,993 |
| Unique URLs after dedup | 10,993 |
| VisorBishop wall time | TBD |
| **Confirmed MLflow** | TBD |
| **CRITICAL unauth** | TBD |
| Auth-fronted | TBD |

## Weights & Biases self-host

Smaller population, but every confirmed instance produced a finding.

| Metric | Value |
|---|--:|
| Shodan dork | `http.html:"wandb"` |
| Total Shodan hits | 87 (note: full population is ~91 worldwide) |
| Confirmed W&B | 42 (48%) |
| **HIGH unauth (anonymous viewer)** | **42 (100% of confirmed)** |

**Every confirmed W&B self-host responds to a viewer GraphQL query
without authentication.** None disclosed an authenticated identity
(all returned `null` viewer), which means the operator has W&B's
"anonymous mode" enabled by default — the platform is reachable
without credentials, but the platform performs identity-aware
filtering on the data layer.

Whether the data layer is actually protected requires deeper probing
on each host (project list, run history, artifact downloads) and was
not included in the iter-7 fingerprint. **Flagged HIGH (not CRITICAL)
pending the data-layer deep-dive.**

## Why MLflow Tracking unauth is severe

MLflow Tracking stores everything that gets attached to an experiment
during model development:

1. **Prompts and prompt templates** — for LLM experiments, the
   `mlflow.log_param("prompt", ...)` pattern is canonical. Tracking
   data captures the full set of prompts under iteration.
2. **Model parameters and hyperparameters** — when a tuning run
   logs `temperature`, `top_p`, `system_prompt`, etc., they end up
   in the run's params dict, reachable via
   `/api/2.0/mlflow/runs/search`.
3. **Artifact URIs** — pointers to S3 / GCS / Azure Blob locations
   containing the model weights, datasets, or evaluation outputs.
   Even when the operator's bucket policy is correct, the URI itself
   discloses internal cloud account names and bucket structure.
4. **Run tags** — operators frequently log credentials to run tags
   ("api_key": "sk-..."). MLflow has no warning against this pattern,
   and the tags are visible to anyone who can read the run.
5. **Model registry** — MLflow's registered-models registry exposes
   the operator's full model catalog, version history, and stage
   transitions (Staging / Production / Archived). This is the
   "model graveyard" that reveals what the operator is shipping.

Unauthenticated MLflow is therefore **a richer data class than even
Phoenix or LiteLLM** — Phoenix exposes traces, LiteLLM exposes API
keys (indirectly via LLMjacking), but MLflow exposes the operator's
entire experimentation history with prompts, parameters, artifacts,
and frequently credentials.

### CVE-2023-1177 still active

MLflow versions before 2.2.1 are vulnerable to **CVE-2023-1177**, a
path traversal in the artifact URI handler that allows reading
arbitrary files on the tracking-server host. The VisorBishop prober
flags any confirmed MLflow with version `< 2.2.1` as
`cve_2023_1177_likely`. Sample sweep showed:

[PENDING — version distribution from full sweep]

## Platform-distribution table (full corpus)

[PENDING from full sweep]

## Top critical hosts

[PENDING from full sweep]

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
4. **W&B data-layer probe expansion** — determine if anonymous-mode
   instances actually expose project/run data
5. **Cumulative disclosure-routing pipeline** — covers iter-1..7
   findings, vendor + per-operator outreach
6. **Phase 5: shift to a different research vector** — observability
   + gateway + experiment-tracking are now thoroughly mapped;
   iter-8+ should pivot to a different tier or research methodology

## Evidence pack

`~/recon/2026-05-11-iter7/`
- `mlflow-full.json.gz` — Shodan harvest (11.4MB, 10,993 records)
- `mlflow-full-urls.txt` — deduplicated URLs
- `mlflow-attribution.tsv` — ip:port → (hostnames, org, country, isp)
- `wandb-sample.json.gz` — W&B Shodan harvest (87 records)
- `wandb-urls.txt` — W&B target URLs

`~/recon/2026-05-11-iter7/results/`
- `mlflow-200-v2.json` — 200-host sample sweep (3 critical, 41 info)
- `mlflow-full.json` — full population sweep (pending)
- `wandb.json` — W&B self-host sweep (42 confirmed, 42 HIGH)

Source: [Nicholas-Kloster/VisorBishop@v0.1.6](https://github.com/Nicholas-Kloster/VisorBishop)

Cross-references:
- [iter-6 case study (LiteLLM full sweep)](visorbishop-iter6-survey-2026-05-11.md)
- [iter-5 case study (gateway + annotation + eval tiers)](visorbishop-iter5-survey-2026-05-11.md)
- [Phase 3 case study](visorbishop-phase3-survey-2026-05-11.md)
- [Methodology Insight #15](/methodology/insight-15-dork-hits-vs-platform-instances/)
