---
type: tool-dev-log
title: "VisorBishop iter-8: Six platforms swept, near-zero critical (LLM pipeline + ML orchestration + product analytics)"
date: 2026-05-11
class: tool
category: cross-platform-tool-validation
status: research-complete
methodology: scaling VisorBishop coverage to six adjacent platform classes; documenting the null-finding case where shipping defaults uniformly enforce auth
---

# VisorBishop iter-8 · 2026-05-11

NuClide Research · 2026-05-11

## Summary

Eighth iteration of the Phase 3 loop. iter-1..7 covered observability,
gateway, annotation, evaluation, and experiment-tracking tiers.
**iter-8 expands to three more tiers**: LLM-pipeline builders, ML
orchestrators, and product analytics.

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7004, S7068, S7070, S7075, T5904
- **733 (AI Risk & Ethics Specialist):** K7051, S7067, T5868
- **overlap (Common AI KSATs (all 5 roles)):** K1158, K22, K6311, K6935, K7003

<!-- ksat-tag:auto-generated:end -->

Six platforms were scoped:

- **Langflow**: LLM-pipeline visual builder (33,303 Shodan hits)
- **Dify**: LLM-app builder from LangGenius (2,116 hits with the
  tight title-match dork)
- **Kubeflow**: Kubernetes-native ML platform (661 hits)
- **PostHog self-host**: product analytics with LLM-observability
  features (696 hits)
- **Prefect**: Python workflow orchestrator (402 hits)
- **Airflow**: Apache workflow scheduler (46,048 hits, noisiest dork
  in the chain)

**The headline finding is the absence of a finding.** Across 1,200
hosts probed (200/platform sample), the iter-8 sweep produced
**exactly 1 critical**, a Kubeflow Pipelines standalone on
`13.217.68.246`. Every other confirmed platform host across all six
platforms is auth-protected.

This is the **opposite signal from iter-6/iter-7**: where LiteLLM
shipped without auth (10.4% critical rate) and MLflow shipped without
auth (14.9% critical rate), the iter-8 tier reproduces auth-on at
near-100% rate.

## Per-platform results (200-host sample each)

| Platform | Confirmed | Critical | Auth-protected | Confirm rate |
|---|--:|--:|--:|--:|
| Langflow | 182 | 0 | 182 | 91% (cleanest dork yet) |
| Dify (tightened) | 105 | 0 | 105 | 53% |
| PostHog | 187 | 0 | 187 | 94% |
| Prefect | 3 | 0 | 3 | 1.5% (noisiest of iter-8) |
| Airflow | 59 | 0 | 59 | 30% |
| Kubeflow | 1 | **1** | 0 | 0.5% |

**Aggregate**: 537 confirmed across 1,200 hosts = 45% average confirm
rate (lower than iter-6 LiteLLM's 50% but higher than iter-7
MLflow's 7%). **1 critical** = 0.08% of probed, 0.19% of confirmed.
Two orders of magnitude lower than iter-6/iter-7 critical rates.

## The lone critical finding

**`13.217.68.246`. Kubeflow Pipelines standalone (AWS US-East)**

```
Endpoint: /pipeline/apis/v1beta1/pipelines?page_size=10
Response: 200 OK
Body    : Returns pipeline catalog including tutorial-dsl-control-structures
          and other operator-defined pipelines without authentication
```

The Kubeflow Pipelines distribution differs from the full Kubeflow
stack: Pipelines-standalone has no dex/oidc auth layer by default,
relying on operator network gating instead. When the operator exposes
the Pipelines pod publicly without an ingress-level auth shim, the
pipeline API is reachable. The operator's pipeline code (training
DAGs, parameter ranges, sometimes embedded credentials in pipeline
metadata) is disclosed.

## Why the rest of iter-8 is uniformly auth-protected

Each of the five other platforms reaches auth-on at population scale
through a different mechanism:

- **Langflow**: added auth-by-default in releases after the v0.x
  series. Most public deployments are v1.x+ and require sign-in.
  91% confirm rate, 0% critical.
- **Dify**: first-time setup requires claiming an admin account at
  `/install`; once claimed, all API endpoints behind it require
  session auth. Every confirmed Dify in the sample had setup
  completed.
- **PostHog**: defaults to requiring sign-in for console + API. The
  `/_health` endpoint is public (used here as a clean identity
  marker), but every protected route returned 401/403.
- **Prefect Server**: most installs front the API with Cloudflare
  or similar auth proxy. The dork (`http.title:"Prefect"`) matches
  many non-Prefect tools that include "Prefect" in their title;
  real Prefect hosts are rare and uniformly fronted.
- **Airflow**: defaults to `auth_backends = airflow.api.auth.backend.session`
  in 2.x+, which requires session auth on the REST API. Older 2.x
  deployments do exist but they tend to be fronted by Cloudflare
  Access or similar.

**iter-8 is the validation case for Methodology Insight #13**:
"shipping defaults are load-bearing." Every one of these six
platforms ships with auth-on (or trivially-claimable-then-auth-on,
in Dify's case), and the population-scale outcome is auth-on at
99.9% rate.

The contrast with the iter-6 LiteLLM finding (auth-off default →
10.4% critical) and iter-7 MLflow finding (auth-off default →
14.9% critical) is the cleanest empirical evidence yet for the
shipping-defaults principle. **Same operator population, opposite
defaults, opposite outcomes.**

## Methodology refinements in flight

Three prober bugs caught and fixed during iter-8 sample sweeps:

### 1. PostHog `/_health` substring match (commit `6a4d3b1` previous)

Initial PostHog prober used `strings.Contains(body, "ok")` on the
`/_health` response. **False-positived on GitLab Help pages** which
return 200 + HTML body with "ok" buried in unrelated markup. Fix:
require `strings.TrimSpace(body) == "ok"` (exact match after strip).

### 2. Dify SPA-only marker → missed real Dify hosts

Initial Dify prober required `<title>Dify</title>` in the root HTML.
**Many real Dify hosts return only a one-line redirect target at "/"
with no HTML title.** Re-anchored on `/console/api/system-features`
which returns Dify-specific JSON with `sso_enforced_for_signin`
field. Unique to Dify, parseable, reliable. SPA root is now an
enrichment indicator, not a gate. Result: 0/200 → 105/200 confirmed.

### 3. Kubeflow loose-substring marker AND missed standalone deployment

Initial Kubeflow prober had two bugs:
- **False-positive**: a `strings.Contains(body, "centraldashboard")`
  fallback matched any HTTP response containing the literal string,
  including nginx redirect-target text leaks. 84 unrelated hosts
  got tagged as Kubeflow in the Dify sweep.
- **False-negative**: the primary marker required
  `kubeflow-oidc-authservice` which is only present in the full
  Kubeflow distribution with dex. Kubeflow Pipelines standalone has
  no dex; its marker is `<title>Kubeflow Pipelines</title>` + the
  `KFP_FLAGS` JS variable.

Fix: extend the marker set to require explicit Kubeflow signals
(OIDC client name, Pipelines title + KFP_FLAGS, or branded dashboard
HTML). The single critical finding (`13.217.68.246`) was correctly
detected in both pre- and post-fix sweeps.

All three fixes were caught at sample-sweep stage, not at population
stage. The iter-7/iter-8 discipline of "sample 200, validate, then
scale" caught what a full-population sweep would have produced as
systematic noise.

## What this means for the research arc

iter-8 closes the Phase 3 loop with a clean **null-finding result**
that **validates the existing chain's signal**:

- iter-2 Phoenix: auth-off default → 89% critical
- iter-5 Promptfoo: auth-off default → 91% critical
- iter-6 LiteLLM: auth-off default → 10.4% critical
- iter-7 MLflow: auth-off default → 14.9% critical
- **iter-7 W&B: auth-on default → 0% critical**
- **iter-8 (6 platforms): auth-on default → 0% critical (1 lone unauth Kubeflow Pipelines)**

The shipping-defaults dichotomy is now visible across **20 distinct
platforms** sampled at 200+ hosts each. Auth-off platforms reproduce
critical exposures at population scale; auth-on platforms do not.

## What's not in scope

iter-8 explicitly did NOT pursue:
- **Full-population sweeps**. The sample-sweep null-finding is strong
  enough to conclude the tier; full sweeps of Langflow (33K) or
  Airflow (46K) would consume Shodan credits to confirm the same
  null result.
- **Comet ML self-host re-check, Trulens re-check, ZenML re-check**:   all <5 self-hosts on Shodan, below population threshold.
- **PostHog product-analytics LLM-observability disclosure**: the
  `/api/projects/` route is auth-protected; investigating whether
  specific PostHog plugins (e.g. LLM observability) have weaker
  routes would require operator-side cooperation, not population
  recon.

## Evidence pack

`~/recon/2026-05-11-iter8/`
- `langflow-sample.json.gz` / `langflow-urls.txt`. Shodan harvest
- `dify-sample.json.gz` / `dify-urls.txt`. First dork (noisier)
- `dify-html.json.gz` / `dify-html-urls.txt`. Tighter dork
- `kubeflow-sample.json.gz` / `kubeflow-urls.txt`
- `posthog-sample.json.gz` / `posthog-urls.txt`
- `prefect-sample.json.gz` / `prefect-urls.txt`
- `airflow-sample.json.gz` / `airflow-urls.txt`

`~/recon/2026-05-11-iter8/results/`
- `langflow.json` / `dify-v5.json` / `kubeflow-v3.json` /
  `posthog.json` / `prefect.json` / `airflow.json`

Source: Nicholas-Kloster/VisorBishop@v0.1.7. Commits `c4d0eeb` (six new probers), `6a4d3b1` (Dify + Kubeflow marker fixes)

Cross-references:
- [iter-7 case study (MLflow + W&B)](visorbishop-iter7-survey-2026-05-11.md)
- [Methodology Insight #13 (shipping defaults are load-bearing)](/methodology/insight-13-shipping-defaults-load-bearing/)
- [Methodology Insight #15 (dork hits ≠ platform instances)](/methodology/insight-15-dork-hits-vs-platform-instances/)
- [Methodology Insight #16 (200 is identity, not auth state)](/methodology/insight-16-status-code-is-identity-not-auth-state/)
