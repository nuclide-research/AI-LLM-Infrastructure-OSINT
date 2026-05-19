---
title: "Service mesh + workflow-orchestration population surveys: Envoy admin config-dump + Prefect admin/settings + ML pipeline-engine exposures"
date: 2026-05-19
type: survey
sector: commercial
tags: [istio, envoy, linkerd, pomerium, prefect, dagster, bentoml, temporal, kserve, ray, kubeflow, llm-pipeline, workflow-orchestration]
status: complete
---

# Service mesh + workflow-orchestration population surveys

_NuClide Research · 2026-05-19 · Two parallel population surveys covering the network mesh / zero-trust proxy tier and the workflow-orchestration tier. Sourced from the FUTURE-SURVEYS roadmap gaps "Network Perimeter & Service Mesh" and "Workflow & Event Orchestration (LLM lifecycle)." 893 unique candidates across 80+ dorks; 660 verified-classified hosts._

## Summary

Two surveys ran in parallel against unsurveyed FUTURE-SURVEYS roadmap categories:

- **Service mesh / zero-trust proxy**: 590 candidates harvested across Istio, Envoy admin, Linkerd, Pomerium, Authelia, Authentik, Headscale, Cilium Hubble, Kiali, Consul Connect, OSM, Traefik. 430 hosts classified.
- **Workflow orchestration**: 303 candidates across Temporal, Prefect, Dagster, BentoML, Argo Workflows, Kubeflow, KServe, Flyte, Ray Dashboard. 230 hosts classified.

The two surveys produced two distinct critical-finding classes plus broader population mapping.

## Survey 1: Service mesh / zero-trust proxy

### Stage 0 — 50+ dorks across 9 product families

| Family | Top dork | Notes |
|---|---|---|
| Istio control plane | `port:15010/15012/15014 + http.html:"istiod"` | xDS / monitoring ports |
| Envoy admin | `port:9901 + http.html:"envoy"` | Per-instance admin API |
| Linkerd | `http.title:"Linkerd"` + viz package | Service-mesh control |
| Pomerium | `http.title:"Pomerium"` | Zero-trust proxy |
| Authelia / Authentik | titles + `port:9000` | Auth-proxy frontends often paired with mesh |
| Headscale | `http.title:"Headscale"` | Self-hosted Tailscale-compat |
| Cilium Hubble | `http.title:"Hubble"` | eBPF observability |
| Consul Connect | `http.html:"/v1/connect/intentions"` | Service mesh intentions |
| Traefik / OSM | dashboard titles + API paths | Edge / L7 firewall |

### Stage 2 verify — final tally (590 candidates → 430 classifications)

| Platform | Unique hosts | Endpoint |
|---|---|---|
| **Pomerium dashboards** | **186** | `/` rendering the Pomerium UI; auth-state on individual hosts not exercised |
| Envoy admin `/stats` (Prometheus) | 175 | Operator's per-cluster Envoy metrics (request rates, p50/p95 latency, upstream cluster status) |
| **Envoy admin `/config_dump`** | **34** | **Entire Envoy config + listeners + upstream services + cluster topology dumpable unauth on a single GET. The operator's complete L7 routing map.** |
| Envoy admin `/clusters` | 23 | Upstream cluster config + endpoint health |
| Headscale `/health` | 4 | Self-hosted Tailscale-compat mesh VPN health endpoint |
| Linkerd `/api/check` | 2 | Linkerd control plane check |
| Istio control plane `/debug/registryz` | 1 | Istio service registry dumped (hostnames + ports of every meshed service) |
| Envoy admin `/listeners` | 1 | Listener configuration |
| Kiali `/api/status` | 1 | Istio observability dashboard |

### Highest-signal finding: 34 Envoy admin `/config_dump` exposures

Each instance returns a JSON document containing the operator's complete Envoy configuration: bootstrap config, listener filters, upstream cluster definitions, TLS settings, rate-limit policies, retry policies, header rewrites, etc. For service-mesh deployments, this reveals:

- Every internal service the operator has put behind the mesh (cluster names + endpoint addresses)
- Operator-defined routing rules (which paths go to which upstream)
- mTLS configuration (which clusters require mTLS, which don't)
- Any operator-defined Lua / Wasm filters loaded into the data path

The Envoy admin API binds to `0.0.0.0:9901` by default in many deployment templates. The operator's intended use is "local debugging only"; the reality at population scale is internet-reachable.

### Pomerium population (186 hosts)

Pomerium is a zero-trust identity-aware proxy. The 186-host population represents either successful zero-trust deployments (auth-required at the dashboard layer) or misconfigured deployments where the dashboard is reachable without auth. Per-host auth-state verification is the next step. The population-size finding alone is methodology-relevant: zero-trust proxy adoption is meaningful enough to justify a dedicated platform-tier survey.

## Survey 2: Workflow orchestration

### Stage 0 — 35+ dorks across 9 product families

| Family | Top dork | Notes |
|---|---|---|
| Temporal | `http.title:"Temporal"` + port 8233 / 8080 | Workflow engine |
| Prefect | `port:4200` + `http.title:"Prefect"` | Orion workflow scheduler |
| Dagster | `http.title:"Dagster"` + port 3000 | Pipeline engine |
| BentoML | `http.title:"BentoML"` + Yatai | ML serving + model packaging |
| Argo Workflows | `http.title:"Argo Workflows"` + port 2746 | K8s-native workflows |
| Kubeflow / KServe | title + paths | K8s ML platform |
| Flyte | `http.title:"Flyte"` | Workflow + ML platform |
| Ray | `port:8265 + http.title:"Ray Dashboard"` | Distributed compute (existing CVE-2023-48022 class) |

### Stage 2 verify — final tally (303 candidates → 230 classifications)

| Platform | Unique hosts | Endpoint |
|---|---|---|
| Prefect Orion `/api/health` | 152 | Health endpoint (intentionally public per Prefect docs; most are auth-required at the data layer) |
| **Prefect `/api/admin/settings`** | **28** | **Operator's full Prefect admin config exposed unauth. Includes the live PREFECT_* settings tree — database URLs, scheduler timeouts, S3 storage block credentials, broker URLs, encryption key references.** |
| BentoML `/healthz` | 17 | ML model-serving runtime (unauthenticated healthz; the model inference surface itself is the next probe step) |
| Dagster `/graphql?query={version}` | 5 | Dagster pipeline engine reachable via GraphQL |
| **KServe `/v1/models`** | **5** | **K8s-native LLM/model serving — `/v1/models` lists deployed models unauth** |
| BentoML `/api/v1/bentos` | 3 | Bento metadata (model packaging) |
| Temporal Web API `/api/v1/namespaces` | 4 | Workflow namespace enumeration |
| Temporal Web cluster-info | 4 | Cluster topology |
| Kubeflow Pipelines `/apis/v1beta1/runs` | 2 | ML pipeline run data |
| Ray Dashboard `/api/jobs` | 2 | Ray cluster job submission surface (CVE-2023-48022 class) |

### Highest-signal finding: 28 Prefect `/api/admin/settings` exposures

The Prefect Orion admin endpoint returns the live PREFECT_* settings tree. In typical operator deployments this includes:

- `PREFECT_API_DATABASE_CONNECTION_URL` — full Postgres connection string (user, password, host, db name)
- `PREFECT_API_DATABASE_PASSWORD` — DB password directly (if not embedded in the URL)
- `PREFECT_MESSAGING_BROKER` — message broker config (Redis, RabbitMQ URLs)
- `PREFECT_API_TLS_INSECURE_SKIP_VERIFY` — TLS verification posture
- `PREFECT_LOGGING_TO_API_BATCH_INTERVAL` — log-forwarding config
- Various block credentials (S3, Snowflake, custom) referenced by name

Per Prefect's documentation, `/api/admin/settings` is supposed to be gated behind authentication. 28 of the surveyed Prefect Orion instances either skipped auth or had it removed. Each exposure gives an attacker the operator's pipeline-infrastructure credential set.

### LLM/AI-relevant subset (per the survey's "discover exposed LLM/AI infrastructure" goal)

| Platform | Hosts | LLM/AI relevance |
|---|---|---|
| KServe `/v1/models` | 5 | K8s-native model serving — operator's deployed model list reachable unauth. Models likely include LLMs (Llama, Mistral, custom fine-tunes) given KServe's positioning |
| BentoML | 17 (healthz) + 3 (bentos) | ML model serving runtime + bento packaging; LLM-class operators commonly use BentoML for OpenAI-compatible serving |
| Temporal Web (4 + 4) | 8 | Workflow engine increasingly used for LLM pipeline orchestration (eval, RAG-index-refresh, retraining); namespace + cluster-info reveals workflow architecture |
| Dagster (5) | 5 | Pipeline engine for LLM ETL + eval workflows |
| Kubeflow Pipelines (2) | 2 | ML pipeline platform |
| Ray Dashboard `/api/jobs` (2) | 2 | Distributed compute; CVE-2023-48022 (ShadowRay) job-submission RCE class. Both hosts confirm the class still exists at population scale 2+ years after initial disclosure |

## Methodology notes

### Insight #2 + #13 confirmed at the mesh tier

The 34 Envoy admin `/config_dump` exposures align with the auth-off-default thesis. Envoy admin API binds to `0.0.0.0:9901` by default; the operator must explicitly bind to localhost or wrap with auth. At population scale, the shipping default produces 34 unauth dumps. Same pattern as the Phoenix asymmetric-auth finding (Insight #37) and the Open WebUI population finding from prior surveys.

### Insight #15 generalized at the workflow tier

Prefect's `/api/health` is intentionally public. Probing only `/api/health` would have found 152 hosts and missed the 28 actually-exposed `/api/admin/settings`. Probing only `/api/admin/settings` would have missed the broader population. **Per-platform probes must enumerate BOTH the intentionally-public health endpoint AND the operator-misconfig-revealed admin path.** Same rule applied at the safety-guardrail survey for Phoenix's `/v1/traces` vs `/login` split.

### Ray CVE-2023-48022 (ShadowRay) class persists

2 Ray Dashboard `/api/jobs` exposures in this survey. Each one is the job-submission RCE class first disclosed publicly in late 2023. Population persistence at 2+ years matches the operator-decay rate documented in Insight #30.

## Honest negative space

- Istio control plane is rarely directly internet-reachable (only 1 `/debug/registryz` hit). Most Istio deployments are K8s-internal; the control plane endpoint is gated by network policy or K8s-mesh-internal-only.
- Linkerd small population (2 hits) — Linkerd ships with auth tightly gated; the few hits surfaced via the `/api/check` endpoint suggest legitimate-but-incomplete deployments.
- Cilium Hubble + Open Service Mesh returned 0 verified hits. Either rare deployment patterns or both products have tighter shipping defaults than Envoy admin.
- Authelia + Authentik populations not probed in this pass — those are auth-proxy frontends, separate-tier disclosure (would be Insight #8's family).

## See also

- [`shodan/queries/`](../../shodan/queries/) — query catalog (mesh + workflow-orch dorks documented inline in this case study; will fold into a new shodan/queries/25-service-mesh-and-orchestration.md file if useful)
- [`methodology/insight-13-shipping-defaults-load-bearing.md`](../../methodology/insight-13-shipping-defaults-load-bearing.md) — confirmed at the mesh tier
- [`methodology/insight-37-asymmetric-auth-gating-dashboard-vs-api.md`](../../methodology/insight-37-asymmetric-auth-gating-dashboard-vs-api.md) — same pattern at the workflow tier (Prefect health vs admin)
- [`methodology/insight-30-persistence-without-pressure.md`](../../methodology/insight-30-persistence-without-pressure.md) — Ray ShadowRay class still present at 2+ years
- [`case-studies/commercial/compute-orchestration-cloud-survey-2026-05.md`](compute-orchestration-cloud-survey-2026-05.md) — prior survey (Spark/Airflow/Ray) that this completes the "compute-orch leftovers" gap for
