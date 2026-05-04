# LLM Observability + Training Telemetry — Auth Posture Survey

_NuClide Research · 2026-05-04_
_Sibling tier-2 expansions: [`comfyui-cloud-survey-2026-05.md`](comfyui-cloud-survey-2026-05.md), [`speech-audio-cloud-survey-2026-05.md`](speech-audio-cloud-survey-2026-05.md)_

---

## Summary

Mass-scan of port 6006 (Phoenix Arize default + TensorBoard default) across **76 tier-2 cloud /16 ranges (3.55M IPs)**. **4,314 port-open candidates → 9 confirmed AI/ML observability instances** (after filtering 38 non-AI port-6006 services like Juniper firewalls, ASUS routers, USG Flex ATP appliances).

- **6 Phoenix (Arize)** instances — LLM trace/eval platform for prompt-history + cost-tracking + LLM-app debugging
- **3 TensorBoard** instances — ML training observability with active diffusion-model-research workloads visible

All 9 unauthenticated. **Phoenix and TensorBoard ship with no authentication** — Tier-A. The framework defaults are `--host 0.0.0.0` with no auth flag.

The notable findings:

1. **Active Stable Diffusion XL distillation + LoRA fine-tuning research** visible on `51.159.189.219` (Scaleway) — a researcher's Lightning logs for `distill_sdxl/version_11`, `sd15_full_unet/version_0`, `lora8/version_5`, plus validation metrics on a private test set named `ober_test`.

2. **Two-host Phoenix deployment** for `made-doc-analysis-llm-app` (likely a "MADE Doc Analysis" LLM application, name visible in Phoenix project list) — both `51.159.138.130` and `51.159.162.241` (Scaleway France) running the same operator's prod + staging Phoenix instances.

---

## Methodology

```
masscan -iL <76 tier-2 /16 CIDRs> -p 6006 --rate 10000
  → 4,314 port-6006 candidates (port 6006 is heavily shared with
    enterprise networking gear — firewalls, routers, etc.)

observability-probe.py (200-thread, fingerprint-strict)
  GET /  →
    contains "phoenix" / "arize"  → Phoenix
    contains "tensorboard"        → TensorBoard
    contains "mlflow"             → MLflow on alt port (none found)
    other HTML title (firewalls, routers)  → ignored

  Phoenix follow-up:
    GET /v1/projects  → list project names (= operator's app names)

  TensorBoard follow-up:
    GET /data/runs        → list training-run names (Lightning version paths)
    GET /data/experiments → exposed experiment groupings
    GET /data/plugin/scalars/tags → exposed scalar metric names
```

NuClide did not submit any data to either platform.

---

## Findings Summary

| Metric | Value |
|---|---|
| Tier-2 ranges scanned | 76 (3.55M IPs) |
| Masscan hits on :6006 | 4,314 |
| Confirmed AI/ML observability | **9** (Phoenix 6 + TensorBoard 3) |
| Unauthenticated | **9 (100%)** — by framework design |
| Non-AI port-6006 services filtered | 38 (firewalls, routers, network appliances) |

### Phoenix (Arize) hosts

| IP | Cloud | Project names visible |
|---|---|---|
| 51.159.138.130 | Scaleway FR | **`made-doc-analysis-llm-app`**, `default` |
| 51.159.162.241 | Scaleway FR | **`made-doc-analysis-llm-app`**, `default` |
| 137.74.115.133 | OVH FR | `default` only |
| 163.172.146.88 | Scaleway FR | `default` only |
| 172.232.104.32 | Linode | `default` only |
| 192.99.167.90 | OVH-CA | `default` only |

The two `made-doc-analysis-llm-app` hosts are the same operator running prod + staging — same project name, same Scaleway FR IP space (`51.159.x`).

### TensorBoard hosts (with run-name visibility)

| IP | Cloud | Runs | Notable run names |
|---|---|---|---|
| **51.159.189.219** | **Scaleway FR** | **7** | `lora8/lightning_logs/version_5`, `distill_sdxl/lightning_logs/version_11`, `full_unet/lightning_logs/version_0`, `sd15_full_unet/lightning_logs/version_0` |
| 173.230.153.125 | Linode | 1 | `preframr/version_0` |
| 45.33.107.126 | Linode | 1 | `1776341439519107324/train` (numeric ID = Hugging Face / W&B-style auto-generated run name) |

---

## Headline finding: 51.159.189.219 — Active Stable Diffusion research

This Scaleway FR host runs a TensorBoard tracking a multi-experiment diffusion-model research workflow:

```
Visible runs:
  lora8/lightning_logs/version_5         — LoRA rank-8 fine-tune, version 5
  distill_sdxl/lightning_logs/version_11 — SDXL distillation, version 11
  full_unet/lightning_logs/version_0     — full UNet fine-tune, version 0
  sd15_full_unet/lightning_logs/version_0 — Stable Diffusion 1.5 full UNet, version 0

Visible scalar metrics per run:
  train/backbone/attention_mask_loss_{step,epoch}
  train/backbone/diffusion_mse_loss_{step,epoch}
  train/backbone/total_loss_{step,epoch}
  validation/ober_test/psnr      — peak signal-to-noise ratio on private "ober_test" set
  validation/ober_test/ssim      — structural similarity on private "ober_test" set
  hp_metric                      — hyperparameter optimization metric
  epoch
```

The runs are PyTorch Lightning logs (the `version_X/lightning_logs/` directory pattern). The operator is iterating across:
- LoRA fine-tunes (rank 8)
- Full UNet fine-tunes
- SDXL → smaller-model distillation experiments

Anyone on the internet can read:
- The complete loss curves (training + validation) for every run
- The hyperparameter sweep history
- The model architecture (TensorBoard exposes the model graph)
- Sometimes: training data samples in image/text summary tabs

For a diffusion-model researcher, this exposes the operator's research methodology, training-data choices, and progress against private benchmarks (`ober_test`). For a competing lab, this is operational intelligence.

---

## Threat-class taxonomy

For unauth LLM observability + ML training telemetry:

### Phoenix (LLM observability)

1. **LLM trace exfiltration** — `/v1/traces` (OTLP) returns the full prompt + response + cost + latency for every LLM call the application has made. For a customer-facing LLM app, this is the operator's user-facing prompt and the model's responses — PII risk if user content is in either.
2. **Project-name disclosure** — `/v1/projects` reveals what the operator builds. Names like `made-doc-analysis-llm-app` are operational-intelligence leaks even before pulling traces.
3. **Eval-result exfiltration** — Phoenix supports running evals on traced data; the eval results expose how the operator measures their LLM app's quality.

### TensorBoard (ML training)

1. **Loss-curve exfiltration** — full training history, validation metrics, model architecture
2. **Hyperparameter sweep history** — `hp_metric` exposes the operator's HPO choices (which combinations of LR, batch size, warmup, optimizer they tried)
3. **Training-data sample disclosure** — TensorBoard's image/text/audio summaries can include actual training samples. NuClide didn't pull these (PII risk if real data) but the surface exists.
4. **Model architecture leak** — TensorBoard graph view exposes the full model graph, layer-by-layer.

---

## Cross-platform correlations

- The Phoenix `made-doc-analysis-llm-app` project on 2 hosts and the TensorBoard SDXL host are all on Scaleway FR `51.159.x` IP space — possibly a single research/SaaS team running multiple AI-observability tools side by side.
- No overlap with prior Qdrant / Milvus / Ollama tier-2 hosts. AI-observability operators are a distinct audience from RAG/inference-server operators.
- 38 non-AI port-6006 services (firewalls, routers, USG Flex ATP appliances) were filtered out — these would have polluted any naive port-6006 scan.

---

## Disclosure posture

- Per-host disclosures NOT drafted (per the parent project's "no more emails" directive)
- The exposure is operational-IP and research-methodology, not user-PII (the Phoenix project named `made-doc-analysis-llm-app` could change if/when actual customer-document analysis traces are added — re-evaluate)
- Operator hardening recommendation:
  - **Phoenix:** Phoenix supports basic auth via `PHOENIX_AUTH_TOKEN` env var (Phoenix 4.0+). Set it. Or front with reverse proxy + SSO.
  - **TensorBoard:** No native auth. Bind to `127.0.0.1` and access via SSH tunnel only, or front with a reverse proxy + auth.
  - For both: `--host 0.0.0.0` should be considered an explicit decision, not the default.

---

## See also

- [`SYNTHESIS-2026-05.md`](SYNTHESIS-2026-05.md) — cross-survey synthesis
- [`FUTURE-SURVEYS.md`](FUTURE-SURVEYS.md) — roadmap (entry for Phoenix now closed; Langfuse, Helicone, TruLens still open)
- [`mlflow-cloud-survey-2026-05.md`](mlflow-cloud-survey-2026-05.md) — adjacent ML-tracking surface (different platform, same threat class)
