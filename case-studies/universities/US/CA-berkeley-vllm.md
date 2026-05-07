# UC Berkeley: vLLM 4-Node Research Cluster, SecAlign + Nemotron

_NuClide Research · 2026-05-03_

---

## Summary

Four vLLM nodes on UC Berkeley's research computing network (128.32.0.0/16) expose OpenAI-compatible inference APIs without authentication. The most significant node (128.32.112.120) serves `facebook/Meta-SecAlign-8B`, Meta's security-alignment research model, alongside Llama 3.1 8B, with `/metrics` showing 92,769 completed requests and 78.5M prompt tokens processed. A second node (128.32.48.211) leaks researcher username `akshat` via model path and has processed 103K+ requests. All nodes expose Prometheus `/metrics`. The SecAlign node additionally exposes `/pause`, `/resume`, and `/scale_elastic_ep`, unauthenticated administrative endpoints that can abort in-flight inference requests and drain KV cache.

---

## Infrastructure

| Node | IP | Version | Models | Notes |
|------|-----|---------|--------|-------|
| SecAlign | 128.32.112.120 | vLLM 0.14.0 | Llama-3.1-8B-Instruct + Meta-SecAlign-8B | Admin endpoints exposed, 78.5M prompt tokens |
| Qwen3.5 | 128.32.43.204 | vLLM | qwen3.5-9b | Short context config (2048 max_len) |
| Akshat-Qwen | 128.32.48.211 | vLLM | Qwen2.5-3B-Instruct | Username `akshat` in path, 103K+ requests |
| Nemotron | 128.32.48.200 | vLLM | NVIDIA-Nemotron-3-Nano-30B-A3B-BF16 | 30B reasoning model (MoE, 3B active) |
| Millennium | 169.229.48.109 | vLLM 0.1.dev15967 | Qwen2.5-1.5B-Instruct | Berkeley Millennium network, dev build |

All nodes: AS25 (UC Berkeley), 128.32.0.0/16 and 169.229.0.0/16. Port 8000/tcp public.

---

## Node: 128.32.112.120: SecAlign Research Node

### Model Inventory

| Model ID | Root Path | max_len | Notes |
|----------|-----------|---------|-------|
| `/scratch/public_models/huggingface/meta-llama/Llama-3.1-8B-Instruct` | same | 16384 | Meta Llama 3.1 8B |
| `secalign` | `/storage_slow/models/huggingface/facebook/Meta-SecAlign-8B` |, | **Meta's security alignment model** |

### Prometheus Metrics: Request Volume

| Metric | Value |
|--------|-------|
| `request_success_total[stop]` | **92,769** |
| `prompt_tokens_total` | **78,508,878** (78.5M) |
| `generation_tokens_total` | 3,710,842 |
| Avg prompt length | ~846 tokens |
| Avg generation length | ~40 tokens |
| `time_to_first_token_seconds_sum` | 21,294s total |
| Avg TTFT | ~0.23s |
| `prefix_cache_queries_total` | 78,535,811 |
| Prefix cache hit rate | **89.4%** |

The prompt/generation ratio (78.5M input → 3.7M output) indicates automated batch evaluation, thousands of security-relevant prompts being fed through and short outputs collected. This is the SecAlign evaluation pipeline.

### Admin Endpoints (all unauthenticated)

| Endpoint | Method | Impact |
|----------|--------|--------|
| `POST /pause` | Query params: `wait_for_inflight_requests`, `clear_cache` | **Aborts in-flight requests, pauses pipeline** |
| `POST /resume` |, | Resume paused generation |
| `POST /scale_elastic_ep` |, | Scale the elastic endpoint |
| `GET /load` |, | Returns `{"server_load": 0}` |
| `GET /version` |, | Returns `{"version": "0.14.0"}` |

`POST /pause` description: *"Pause generation requests to allow weight updates. When False (default), aborts any in-flight requests immediately."* `clear_cache=true` additionally destroys the KV/prefix cache, evicting the 89.4% cache efficiency this node has built up.

### Filesystem Paths Disclosed

- `/scratch/public_models/huggingface/meta-llama/Llama-3.1-8B-Instruct`, shared scratch storage, publicly accessible model directory
- `/storage_slow/models/huggingface/facebook/Meta-SecAlign-8B`, separate slow-tier storage for the SecAlign model

---

## Node: 128.32.48.211: Akshat Qwen2.5 Node

### Model Inventory

| Model ID | Root Path | max_len |
|----------|-----------|---------|
| `Qwen2.5-3B-Instruct` | `/data/akshat/models/Qwen2.5-3B-Instruct/` | 20000 |

**Username `akshat`** leaked in model path via unauthenticated `/v1/models` response.

### Metrics

| Metric | Value |
|--------|-------|
| `request_success_total[stop]` | 95,836 |
| `request_success_total[length]` | 7,838 |
| Total requests processed | **103,674** |
| `prompt_tokens_total` | 159,121,718 (159M) |
| `generation_tokens_total` | 180,242,852 (180M) |
| `num_requests_running` (at probe time) | **1** (live traffic) |

This node was serving an active request at probe time. The balanced prompt/generation ratio (159M / 180M) indicates interactive or conversational workloads, not batch evaluation.

---

## Node: 128.32.48.200: NVIDIA Nemotron-3-Nano Node

| Field | Value |
|-------|-------|
| Model | `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16` |
| Parameters | 30B total, 3B active (MoE) |
| max_model_len | 32,768 |
| Response type | `reasoning` field present, chain-of-thought model |

Inference confirmed: chat completions return a `reasoning` field (extended thinking) before final answer. No system prompt observed.

---

## Node: 169.229.48.109: Millennium Network Qwen2.5 Node

| Field | Value |
|-------|-------|
| IP | 169.229.48.109 |
| Hostname | brewster.millennium.berkeley.edu |
| Network | UC Berkeley Millennium Computing cluster (169.229.0.0/16) |
| vLLM version | `0.1.dev15967+gf7f52215b`, ancient dev build from git |
| Model | `Qwen/Qwen2.5-1.5B-Instruct` |
| max_model_len | 32,768 |
| Traffic | prefix_cache_queries: 36 total, essentially fresh deployment |

The Millennium cluster is Berkeley's high-performance research computing environment. This node runs an extremely old vLLM dev build (pre-0.1 release, 15,967 commits in) with a small 1.5B model and essentially no usage. Likely a test or development setup. The hostname `brewster` references Brewster Kahle (of Internet Archive), Berkeley has historically named Millennium nodes after notable technologists.

---

## Node: 128.32.43.204: Qwen3.5-9B Node

| Field | Value |
|-------|-------|
| Model | `qwen3.5-9b` (root: `Qwen/Qwen3.5-9B`) |
| max_model_len | 2,048 (constrained) |

Short context configuration (2048 tokens) suggests controlled experiment settings, limiting context deliberately for research comparison.

---

## Findings

### F1: Unauthenticated vLLM Inference on Research Cluster (HIGH)

All four nodes expose OpenAI-compatible inference without authentication. Any internet actor can send inference requests to Berkeley's GPU allocation using models from active research projects.

```bash
curl http://128.32.112.120:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"secalign","messages":[{"role":"user","content":"Hello"}],"max_tokens":100}'
```

### F2: Unauthenticated Admin Endpoints on SecAlign Node (HIGH)

`POST /pause` and `POST /resume` require no credentials. An adversary can abort all in-flight inference requests and halt the SecAlign evaluation pipeline.

```bash
# Would abort in-flight requests (NOT executed):
# POST http://128.32.112.120:8000/pause?wait_for_inflight_requests=false&clear_cache=true
```

Operational impact: destroys accumulated prefix cache (89.4% hit rate on 78.5M queries) and interrupts any active batch evaluation run.

### F3: Prometheus /metrics Exposes Research Telemetry (MEDIUM)

All nodes expose `/metrics` without authentication. For the SecAlign node, this reveals:
- 92,769 completed inference requests since deployment
- Prompt token distribution showing batch evaluation pattern (avg 846 tokens → avg 40 output)
- Model names and filesystem paths
- TTFT distribution (median ~0.25s), GPU performance benchmarking

### F4: Filesystem Path and Researcher Identity Disclosure (MEDIUM)

Three distinct storage tiers and a researcher username disclosed via unauthenticated API responses:
- `akshat`, researcher/student username (128.32.48.211 model path)
- `/scratch/public_models/huggingface/`, shared cluster scratch space
- `/storage_slow/models/huggingface/`, long-term model storage tier
- `/data/<username>/models/`, per-user data directory

### F5: Active Research Pipeline Accessible (HIGH)

128.32.112.120 is the infrastructure for active **SecAlign** security alignment research. With 78.5M prompt tokens processed at 89.4% prefix cache hit rate, this is an automated evaluation pipeline currently running. Any actor can:
- Inject adversarial prompts into the evaluation run
- Measure model responses to edge-case inputs
- Consume GPU allocation from Berkeley's research budget
- Observe what inputs the research team is using (via query volume patterns in /metrics)

---

## vLLM Attack Surface Notes

Unlike Ollama, vLLM has no `/api/create` system-prompt injection vector. The attack surface here is:
- **Compute theft**, unauthenticated inference drains GPU allocation
- **Pipeline disruption**, `/pause` endpoint (SecAlign node specific)
- **Operational intelligence**, `/metrics` reveals research activity patterns
- **Path/identity disclosure**, model root paths in `/v1/models` responses

---

## UC Berkeley vLLM Footprint

| Node | IP | Service | Research Context |
|------|-----|---------|-----------------|
| SecAlign | 128.32.112.120 | vLLM 0.14.0 | Security alignment (Meta-SecAlign-8B), 78.5M tokens |
| Qwen3.5 | 128.32.43.204 | vLLM | Research config (2K context) |
| Akshat | 128.32.48.211 | vLLM | Individual researcher, 103K requests |
| Nemotron | 128.32.48.200 | vLLM | Reasoning model benchmark |

Combined with the existing Ollama node (`lal-99-178.reshall.berkeley.edu`, 169.229.99.178) and the Course AI Assistant memory injection finding (`roar-art.EECS.Berkeley.EDU`, documented in `CA-berkeley-course-ai.md`), Berkeley now has **7 documented unprotected AI inference nodes** across residential, research, and production course infrastructure.

---

## Remediation

```bash
# Bind vLLM to localhost only:
vllm serve <model> --host 127.0.0.1 --port 8000

# Or add API key authentication:
vllm serve <model> --api-key <secret>

# Disable /metrics endpoint:
vllm serve <model> --disable-log-stats

# For the admin API endpoints (SecAlign node):
# Use --uvicorn-log-level warning and place behind nginx with auth
```

---

## Disclosure

- **Discovered:** 2026-05-03
- **Status:** Pending outreach to security@berkeley.edu and secalign research team
