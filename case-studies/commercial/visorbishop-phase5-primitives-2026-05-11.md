---
type: tool-dev-log
title: "VisorBishop Phase 5: Three primitives that turn 492 critical hosts into an impact narrative"
date: 2026-05-11
class: tool
category: cross-platform-tool-validation
status: research-complete
methodology: deriving second-order findings from the cumulative VisorBishop corpus without new sweeps
---

# VisorBishop Phase 5 · 2026-05-11

NuClide Research · 2026-05-11

## Summary

Phase 3 (iter-1..6) built the prober coverage. Phase 4 built the
dashboard. **Phase 5 turns the inventory into impact**, three
primitives that derive second-order findings from data the cumulative
corpus already contains, without launching new sweeps.

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7004, S7068, S7070, S7075, T5904
- **733 (AI Risk & Ethics Specialist):** K7040, S7067, T5868, T5882
- **overlap (Common AI KSATs (all 5 roles)):** K108, K1158, K1159, K22, K6311, K6900, K6935, K7003

<!-- ksat-tag:auto-generated:end -->

The three:

1. **Cross-platform operator correlation**, which operators run
   multiple unauthenticated platforms? Same IP, /24, or org.
2. **MLflow artifact-URI extraction**, what cloud buckets do the
   120 critical MLflow hosts point at? Names, providers, cross-host
   reuse.
3. **LiteLLM model-catalog spend-tier classifier**, what's the
   dollarized cost-at-risk across the 283 LLMjacking primitives,
   assuming attacker abuse at provider rates?

All three run against the existing corpus. No new network traffic,
no Shodan credits burned. The data was there; it just hadn't been
mined yet.

## #1: Cross-platform operator correlation

**Result: 1 IP and 23 hosting orgs run multiple unauth platforms.**

### Same-IP cross-platform finding (the actual chain)

| IP | Country | Org | Platforms | Targets |
|---|---|---|---|---|
| `78.46.88.7` | DE | Hetzner Online AG | **LiteLLM + Phoenix** | `http://78.46.88.7:80`, `https://78.46.88.7:443`, `http://78.46.88.7:4000` |

One Hetzner customer runs both LiteLLM (LLMjacking primitive) and
Phoenix (trace disclosure) on the same machine. Attack chain:
attacker discovers Phoenix unauth at port 80/443, reads the trace
history (which contains prompts + responses + sometimes API keys),
then turns to port 4000 and uses the LiteLLM proxy to burn the
operator's LLM budget while sending prompts that match the
operator's normal usage pattern (extracted from the Phoenix traces).
The trace-extracted prompts make the abuse traffic
indistinguishable from legitimate operator usage until the bill
arrives.

### Same-/24 cross-platform: zero

No /24 network shows multiple distinct IPs running different unauth
platforms. Operators consolidate on single hosts; they don't shard
AI infrastructure across an internal subnet.

### Same-org cross-platform: the hosting-tier pattern

| Org | IP count | Platforms | Breakdown |
|---|--:|---|---|
| Google LLC | 58 | LiteLLM + MLflow + Phoenix | mlflow=34, phoenix=17, litellm=7 |
| Hetzner Online GmbH | 57 | LiteLLM + MLflow + Phoenix | litellm=46, mlflow=9, phoenix=4 |
| Microsoft Corporation | 28 | LiteLLM + MLflow + Phoenix | mlflow=12, litellm=11, phoenix=6 |
| DigitalOcean, LLC | 26 | LiteLLM + MLflow + Phoenix | litellm=12, mlflow=8, phoenix=6 |
| Contabo GmbH | 26 | LiteLLM + MLflow + Phoenix | litellm=23, phoenix=3, mlflow=1 |
| Microsoft Limited (UK) | 12 | LiteLLM + MLflow + Phoenix | phoenix=5, litellm=4, mlflow=4 |
| OVH SAS | 11 | LiteLLM + MLflow + Phoenix | litellm=8, mlflow=2, phoenix=1 |
| Aliyun Computing | 10 | LiteLLM + Phoenix | litellm=6, phoenix=4 |

This isn't "same operator". These are independent customers of the
same hosting provider. The signal is **structural: each provider's
customer base reproduces the same shipping-default pattern at
population scale.** Google Cloud's MLflow tilt vs Hetzner's LiteLLM
tilt reflects the deployment shape that each provider's tooling
makes easiest.

The chains aren't at the operator level here. They're at the
**hosting-org level**, where a single subnet sweep across one
provider's IP range will surface a known mix of unauth platforms.

## #2: MLflow artifact-URI extraction

**Result: 901 artifact URIs across 120 critical hosts → 58 unique
cloud buckets surfaced.**

The MLflow REST API at `/api/2.0/mlflow/experiments/search` returns
each experiment's `artifact_location` field. For 120 unauth hosts,
that's the operator's pointer at where the model artifacts and
datasets actually live.

### Provider distribution

| Provider | URI count |
|---|--:|
| `local-fs` (file:// or /path) | 486 |
| AWS S3 | 157 |
| `unknown` (custom or empty) | 110 |
| HTTP (proxied storage) | 66 |
| Google Cloud Storage | 51 |
| Azure Blob | 23 |
| Databricks DBFS | 4 |
| SFTP | 4 |

**40% of MLflow critical hosts store artifacts on local disk**.
Which means the artifacts ride on the same host as the unauth
tracking server. If the artifact-path is queryable (the older
CVE-2023-1177 path-traversal class), the artifacts are reachable
from the same internet entry point.

The other 60% point at cloud buckets. A **separately disclosed
surface that may be public independently of the MLflow server**.

### Top buckets by occurrence

| Provider | Bucket | URIs | Hosts | Notes |
|---|---|--:|--:|---|
| aws-s3 | `mlflow` | 31 | 11 | Generic name, likely many ops |
| aws-s3 | `bia-mlflow` | 20 | 2 | 2 different IPs, same operator |
| aws-s3 | `flow-bucket` | 10 | 1 | DigitalOcean NL operator |
| aws-s3 | `maiaddy-mlflow-artifacts` | 10 | 1 | Mediloca / maiaddy healthcare |
| aws-s3 | `authenta-mlflow` | 10 | 1 | AWS US East |
| aws-s3 | `mlflow-artifacts-631835340943` | 10 | 1 | AWS account 631835340943 (Oishii vertical farming) |
| aws-s3 | `svdeepflow-mlflow-artifacts-dev` | 9 | **3** | **3 IPs in AWS Seoul, same operator redundant infra** |
| aws-s3 | `miles-mlflow-models` | 9 | 1 | Hetzner DE operator |
| aws-s3 | `hia-dev-s3-ew1-hes-ai-000` | 9 | 1 | AWS Sweden — likely HES / Hes-AI |
| aws-s3 | `broadcast-ai` | 9 | 1 | GCP US central |
| gcs | `jrg-mlflow-artifacts` | 8 | 1 | GCS bucket |
| azure-blob | `mlflowartifacts@riskmodelstorage.blob.core.windows.net` | 5 | 1 | Risk modeling, Azure |
| aws-s3 | `gmb-ddal-test-oslo-shared` | 4 | 1 | University of Oslo |
| aws-s3 | `mlperf-mlflow-artifacts` | 4 | 1 | IBM Cloud, MLPerf benchmark |
| gcs | `aircheck-mlflow-tracking` | 4 | 1 | GCP |
| gcs | `kurious-ml-dev` | 4 | 1 | GCP dev bucket |
| gcs | `avaloka-mlflow-artifacts` | 4 | 1 | GCP |
| azure-blob | `mlflowartifacts@mvpusstorage.blob.core.windows.net` | 4 | 1 | Azure |

### Cross-operator bucket reuse

Only one bucket name appears on multiple distinct hosts in a way that
suggests same-operator-redundant-infrastructure (vs different operators
happening to share a name):

- `svdeepflow-mlflow-artifacts-dev` on 3 IPs in AWS Seoul region.
  Same operator running redundant tracking servers pointed at the
  same bucket. Disclosure target: one entity, three servers.

The 78-host "local-fs" set isn't real cross-operator overlap. Every
operator with file:// artifacts has their own local-fs.

### Disclosure implications

The 58 unique buckets are **second-order disclosure surface**. Each
bucket name is searchable: if the operator's bucket policy allows
public list/get, the artifacts are exposed independently of the
MLflow server's auth state. Worth a follow-up pass to check public
accessibility of each named bucket, but out of scope for this Phase
5 primitive.

## #3: LiteLLM model-catalog spend-tier classifier

**Result: 283 unauth LiteLLM hosts represent ~$60,494/month
($725,927/year) in cost-at-risk at provider posted rates.**

### Methodology

Each LiteLLM critical host's `/v1/models` response was already
captured in the VisorBishop indicators payload (full model_ids
when ≤20 models, sample of 20 otherwise). For each model:

1. Match the model ID against a pricing table covering Anthropic
   Claude, OpenAI GPT/o-series/embeddings, Google Gemini, AWS
   Bedrock, Meta Llama, DeepSeek, Moonshot Kimi, Mistral, Cohere,
   xAI Grok, and Ollama-passthrough (free, signaled by deployment).
2. Classify into a tier (`frontier` ≥$15/Mtok, `high` $3-15,
   `mid` $0.5-3, `low` <$0.5, `free` self-hosted).
3. Compute blended $/Mtok across all distinct models on the host.
4. Apply a **conservative 10M tokens/model/month abuse rate**
   (attacker burns one model at 10M tokens for a month). Real
   attacker abuse is faster. Bots can hit a frontier model at
   100M+ tokens/month before detection, so this is a lower-bound
   estimate.

### Tier distribution across all 1,127 exposed models

| Tier | Count | % | Definition |
|---|--:|--:|---|
| frontier | 133 | 11.8% | ≥$15/Mtok (GPT-4/5, Claude Opus, o1/o3) |
| high | 268 | 23.8% | $3-15/Mtok (Claude Sonnet, GPT-4o, Gemini Pro) |
| mid | 310 | 27.5% | $0.5-3/Mtok (Claude Haiku, Gemini Flash, Mistral) |
| low | 373 | 33.1% | <$0.5/Mtok (GPT-3.5, Llama 8B, embeddings) |
| free | 43 | 3.8% | Self-hosted (Ollama, TGI passthrough) |

### Provider distribution (top 10)

| Provider | Models exposed |
|---|--:|
| (unknown / custom model names) | 290 |
| OpenAI | 207 |
| Anthropic | 201 |
| Google Gemini | 120 |
| Alibaba (Qwen) | 99 |
| DeepSeek | 45 |
| Ollama (self-hosted) | 43 |
| Moonshot Kimi | 30 |
| Meta Llama | 27 |
| Mistral | 26 |

### Top 10 operators by cost-at-risk

| $/mo (conservative) | Target | Tier | Models | Frontier sample |
|--:|---|---|--:|---|
| **$4,680** | `20.2.91.83:80` (Azure HK) | frontier | 57 | gpt-5.5, gpt-5.4-pro, gpt-5.4 |
| **$2,640** | `98.149.54.126:4100` (Charter US residential) | frontier | 22 | claude-opus-4-1, claude-opus-4-1-20250805 |
| **$1,898** | `95.216.95.1:4000` (Hetzner FI / netiva.com.tr) | frontier | 11 | gpt-5.4, gpt-5.5, gpt-5.4-mini |
| **$1,854** | `156.227.236.247:4000` (Yisu Cloud JP) | frontier | 18 | gpt-5-image, gpt-5-image-mini |
| **$1,575** | `118.196.116.53:4000` (China) | frontier | 7 | gpt-5.2, gpt-5.3-codex |
| **$1,500** | `103.29.190.142:4000` (Indonesia) | frontier | 6 | chatgpt/gpt-5.4, chatgpt/gpt-5.4-pro |
| **$1,460** | `43.153.66.205:4000` (Tencent US) | frontier | 11 | gpt-4.1, gpt-5.3-codex |
| **$1,447** | `203.149.11.67:443` (Samart Thailand, `api.modelharbor.com`) | frontier | 20 | gpt-5.4, claude-sonnet-4.5 |
| **$1,353** | `107.174.66.118:4000` (RackNerd US) | frontier | 30 | gpt-5, o1, claude-opus-4 |
| **$1,243** | `64.227.146.129:4000` (DigitalOcean IN) | frontier | 16 | gpt-4.1, gpt-4.1-mini |

### What "cost-at-risk" really means

The $60,494/mo aggregate is **the minimum bill the operator's
provider stack would face if every one of these endpoints were
abused at 10M tokens/model/month for a single month**. Real-world
attacker patterns are different:

1. **Concentrated abuse on frontier models**, attackers target the
   highest-cost models because the burn rate is fastest. The
   $4,680/mo operator at `20.2.91.83` exposes 57 models including
   3 frontier. An attacker hitting just those 3 at 100M tokens/mo
   would burn ~$6,750/mo on that single host.
2. **Sustained abuse beyond one month**, most operators don't
   notice the bill anomaly for 1-3 cycles. Cumulative damage over
   a 90-day undetected window is 3× the monthly number.
3. **Indirect costs**, burning the operator's rate limit, exhausting
   their Anthropic / OpenAI capacity allocation, triggering provider
   abuse-investigation that may suspend the operator's account.

A reasonable real-world projection: **multiply the conservative
number by 3-10× to estimate actual undetected-abuse-window blast
radius.** That puts the population-scale annualized risk in the
**$2-7M/year range**.

### Outliers worth noting

- **`98.149.54.126`** is on Charter Spectrum residential. This is
  a developer running LiteLLM at home with their personal
  Anthropic API key, exposing 22 models including frontier Opus.
  An individual's monthly Anthropic bill could be five-figures
  before they notice.
- **`api.modelharbor.com`** (Thailand) reads as a commercial LLM
  routing product. Every paying customer is sharing an unauth
  proxy.
- **9 of the top 10 operators expose frontier-tier models**: the
  abuse-attractive tail is concentrated, not random.

## Cumulative impact picture

The three primitives together turn the inventory into an impact
narrative:

| Primitive | Numeric finding | What it means |
|---|---|---|
| Cross-platform correlation | 1 same-IP chain | Attacker can chain Phoenix trace-disclosure → LiteLLM LLMjacking on the same host (Hetzner DE) |
| Artifact-URI extraction | 58 unique buckets across 120 hosts | Second-order disclosure surface; named buckets like `bia-mlflow`, `maiaddy-mlflow-artifacts`, `svdeepflow` (3× same operator), `riskmodelstorage` |
| Spend-tier classifier | $60K-$725K conservative / $2M-7M realistic | Dollarized LLMjacking blast radius across the 283 critical LiteLLM operators |

**These are the headlines the 492-critical inventory enables.**

## Reproducibility

All three primitives are deterministic functions of the cumulative
corpus. The scripts live at:

`~/recon/2026-05-11-phase5/`
- `01-cross-platform-correlation.py`: reads the dashboard JSON
- `02-mlflow-artifact-uris.py`: reads the raw iter-7 MLflow JSON
- `03-litellm-spend-tier.py`: reads the raw iter-6 LiteLLM JSON

Outputs:
- `correlations.json`: by-IP / by-/24 / by-org operator overlaps
- `mlflow-artifacts.json` / `mlflow-artifact-buckets.tsv`. Bucket inventory
- `litellm-spend-tier.json` / `litellm-spend-tier.tsv`. Per-host
  spend tier + cost-at-risk

The pricing table in #3 is the only piece that needs maintenance
(provider list-prices change quarterly).

## What's next

Phase 5 closes the research arc. The natural next steps:

1. **Public-facing announcement**, the cost-at-risk numbers
   ($725K-$7M/year annualized) are the publishable signal.
2. **Bucket-accessibility pass**, query each of the 58 unique
   buckets surfaced in #2 for public-list / public-get.
3. **Iter-8 platform expansion**, postHog LLM analytics, Kubeflow,
   Airflow ML DAGs.
4. **Disclosure-routing pipeline** for the 492 cumulative critical
   operators.

Cross-references:
- [iter-6 case study (LiteLLM)](visorbishop-iter6-survey-2026-05-11.md)
- [iter-7 case study (MLflow + W&B)](visorbishop-iter7-survey-2026-05-11.md)
- [Methodology Insight #16](/methodology/insight-16-status-code-is-identity-not-auth-state/)
- VisorBishop pipeline scripts: VisorBishop/tree/main/scripts
