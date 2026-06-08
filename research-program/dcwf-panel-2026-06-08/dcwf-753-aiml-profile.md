# AI/ML Workload Profile: VictoriaMetrics Survey 2026-06-08

_DCWF AI Work Role 753 audit · NuClide Research panel_

NuClide Research surveyed 1,176 internet-exposed VictoriaMetrics hosts and recovered unauthenticated `/api/v1/targets` bodies from 960 of them (the vmagent population). Those bodies leak per-target scrape configuration. This profile filters that population for AI/ML workloads vs. general infrastructure, written from a DCWF AI Work Role 753 (DoD AI/ML Specialist) lens.

---

## 1. AI/ML Metric Signature Extraction

Across the 960 vmagent bodies, the signature scan returned hits in exactly one of the six signature classes:

| Class | Hosts | Match volume |
|---|---|---|
| LLM_SERVING (ollama, vllm, triton, kv_cache, tokens_per_second) | 0 | 0 |
| TRAINING (pytorch, wandb, mlflow, epoch, loss) | 0 | 0 |
| GPU_COMPUTE (dcgm, nvidia_smi, gpu_temp, cuda) | 69 | dominant |
| VECTOR_DB (qdrant, milvus, weaviate, chroma) | 0 | 0 |
| RAG_AGENT (langchain, langfuse, embedding) | 0 | 0 |
| ORCH_AI (kserve, kubeflow, ray-serve, torchserve) | 0 | 0 |

68 of the 69 GPU_COMPUTE hits are `dcgm_exporter` scrape targets sitting inside RunPod pods (`__address__ = safe_runpod_dcgm_exporter:9400`, plus a `runpodip` label and a `user_id` label). One additional host runs `nvidia_gpu_exporter` (job name) but the rest of its scrape config (`flussonic_exporter`, `srt_exporter`, `openresty`, `paired_encoder`) makes it a video-streaming encoder, not an AI workload — GPU present, AI absent. Honest call: **57 hosts** are real AI-relevant (RunPod GPU cloud); the lone outlier is GPU-but-not-AI and gets reclassified.

LLM-serving, vector-DB, RAG, and training-orchestration signatures returned zero hits. That is itself a finding (see §5).

## 2. AI vs Non-AI Corpus Split

- vmagent hosts (targets-200): **960**
- Hosts with at least one AI/ML signature: **69** (raw) / **57** (after reclassifying the streaming-encoder false positive)
- AI/ML share of unauth vmagent population: **~5.9%** (57/960), **~7.2%** if you keep the broader GPU bucket

Reframing for the case study: the original "VictoriaMetrics is substrate for everything" headline holds, but **~6% of the unauthenticated vmagent population is monitoring an AI/ML workload**. That share converts this from a pure Cat-46c-infra (substrate-monitoring) finding into a **Cat-46c-AI (AI-monitoring) finding** for the AI-specific subset.

## 3. Three AI-Workload Case Write-ups

### Case A — EU GPU-cloud tenant, 34-pod fleet (`runpod-tenant-33ae5b`)

A single RunPod customer with **34 GPU pods, every pod in EU-RO-1** (RunPod's Romania datacenter), every pod tagged `secure: True`. 295,848 metric samples per scrape cycle. An unauthenticated reader recovers the tenant's `user_id`, the per-pod `runpodip`, DC placement, and the secure/community tier flag, for the entire fleet. **Failure mode if metric data is poisoned:** DCGM `gpu_utilization` and `DCGM_FI_DEV_GPU_TEMP` flooded with low values silences autoscaling-down; flooded with high values triggers spurious thermal throttle or shutdown automation. **AI safety implication:** a 34-pod cluster in one DC is almost certainly a training run or steady-state inference fleet. The metric layer is a side-channel to influence training duration or inference availability.

### Case B — Multi-DC US tenant, 5-pod fleet (`runpod-tenant-565626`)

5 RunPod pods spread across US-IL-1 and an NO-DC ("no datacenter," RunPod's community-host pool). **Failure mode:** community-host pods are already adversary-adjacent (other tenants on the same physical box) — poisoning their DCGM stream lets an attacker influence the tenant's secure-vs-community migration decisions. **AI safety implication:** any RLHF, eval, or fine-tune run sees a corrupted view of infrastructure health.

### Case C — 4-DC sprawl tenant (`runpod-tenant-10f700`)

5 pods, four different RunPod DCs (EU-FR-1, NO-DC, US-NC-1, US-MO-1). **Failure mode:** small scale means a single poisoned DCGM stream dominates aggregate dashboards. **Governance implication:** if this tenant is an AI-serving SaaS, downstream customers look at SLO dashboards built on metrics any internet user can read.

## 4. AI Metric Names Not in Our Signature List

1. `safe_runpod_*` address prefix — RunPod's docker-network service name pattern
2. `runpodip` label key — unique to RunPod pods
3. `user_id` label key — RunPod tenant identifier
4. `dc` label values `EU-RO-1 | US-IL-1 | US-KS-2 | ...` — RunPod DC naming convention
5. `secure: True|False` — RunPod tier flag
6. `ping_exporter` co-resident with `dcgm_exporter` — RunPod default observability bundle
7. `nvidia_gpu_exporter` (utkuozdemir version) — alternate GPU exporter outside RunPod
8. `kv_cache_usage`, `tokens_per_second`, `prompt_tokens_total`, `completion_tokens_total` — vLLM/TGI
9. `model_load_time_seconds`, `inference_queue_depth`, `batch_size` — Triton/TorchServe
10. `langfuse_traces_total`, `embedding_request_latency` — RAG-stack telemetry

The class of miss is structural: VictoriaMetrics' `/api/v1/targets` exposes what is being scraped, not what those scrapes return. AI-stack metric names live in the response bodies. A follow-up survey hitting `/api/v1/label/__name__/values` is the right place to mine metric-name signatures.

## 5. AI/ML Threat Model Delta

A general-infrastructure metric leak is reconnaissance fuel. The delta when the monitored workload is AI/ML is that **the metric layer is wired into autonomous control loops the operator may not have audited as security-critical**.

- **`DCGM_FI_DEV_GPU_TEMP` poisoning into emergency-shutdown trip.** Sustained injected `gpu_temp = 95` plausibly triggers automatic pod migration, throttling, or shutdown.
- **`gpu_utilization` poisoning into wrong autoscaling decision.** Inject low → scale down mid-run; inject high → spend up without workload to justify it.
- **Inference-latency or `tokens_per_second` poisoning into wrong routing.** Multi-region LLM SaaS routing on observed P99 latency picks wrong region.
- **Training-metric poisoning into stop-training.** Operators wiring early-stopping or loss-divergence alerting see forged `val_loss`/`train_loss` fire a stop-training decision against a healthy run.
- **Sample-count side channel for fleet sizing.** `lastSamplesScraped` leaks fleet activity. Tenant-33ae5b's 295,848 samples/cycle is competitive-intelligence signal.

The unifying delta: **traditional infra-monitoring leaks compromise the operator's situational awareness; AI-monitoring leaks compromise the operator's automated decisions**. Control loops sitting on top of GPU and model metrics are first-class production logic. Auth-off-default on the metric collector is therefore auth-off-default on the control plane it feeds.

## Why this matters to the NuClide research program

The auth-off-default thesis predicts any newly-popular infrastructure category ships with permissive defaults until disclosure pressure forces a shift. VictoriaMetrics fits the pattern at the substrate layer. The AI-specific subset extends the thesis: **the auth-off-default failure on AI-monitoring infrastructure is downstream-coupled to autonomous control loops in a way ordinary monitoring is not**. A RunPod tenant exposing their DCGM stream is not just exposing GPU temperatures — they are exposing the input side of orchestration logic and (via the un-tested write path) the trigger side. The 57-host RunPod subset is the AI-specific case for treating metric-pipe auth as a Cat-46c-AI category in its own right.

---

Key counts: 1,176 surveyed; 960 vmagent (targets-200); 57 AI/ML-relevant (RunPod GPU cloud); 8 RunPod tenants exposed; 57 unique (user_id, runpodip) pod-attribution pairs. Top tenant runs 34 pods in EU-RO-1, all secure-tier.
