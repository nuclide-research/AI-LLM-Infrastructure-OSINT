# NVIDIA NIM + Triton population survey + Docker-Registry LLM-image-catalog finding

**Date:** 2026-06-08
**Lead:** NuClide Research
**Survey dir:** `surveys/nvidia-nim-2026-06-08/`
**Status:** Primary target (exposed NIM/Triton API surface) = NULL. Variant pivot uncovered **48 unauthenticated Docker registries leaking LLM-stack image catalogs** across China, US, EU.

## Summary

We ran the chain against NVIDIA's two flagship inference-serving products: NIM (`nvidia-nim`, `:8000`, OpenAI-compat) and Triton Inference Server (`triton-inference-server`, `:8000` / `:8001` / `:8002`). Both ship with `auth_default=none`. We expected a meaningful exposed-unauth population in line with vLLM (4 verified earlier) and SGLang (1 verified).

Primary target outcome: **NULL** — zero verified-exposed NIM or Triton API. 314 Shodan title-dork hits collapsed to one honeypot host on AWS Italy (7 ports of identical bait HTML), two lifecycle-cycled hosts (Synology DSM, Plex Media Server on Windows 7), and 39 dead IPs.

Variant pivot outcome: a **dorking-zero variant chain** through niche metadata fields surfaced 48 unauthenticated Docker registries advertising `vllm/vllm-openai`, `lmsysorg/sglang`, `ollama/ollama`, `langgenius/dify-*`, `xprobe/xinference`, `ascend/vllm-ascend`, and dozens of other inference-stack images.

The registry leak is a real, verified finding class. The NIM/Triton null result is also a real finding (the load-bearing primary-target methodology insight).

## The Docker Registry LLM-image-catalog leak

**Population:** 64 Shodan candidates matching `"vllm-openai"` substring on any port.
**Verified unauth `/v2/_catalog`:** 49 of 64 (77 %).
**Carrying LLM-stack images:** 48 of 49 (98 %).
**Method:** unauth GET on `/v2/_catalog` per Docker Registry HTTP API v2. Read-only catalog enumeration. No manifest pulls, no blob downloads.

| dominant image | what it is | implication |
|---|---|---|
| `vllm/vllm-openai` | vLLM's OpenAI-compatible inference server | this operator is running OSS LLM inference |
| `lmsysorg/sglang` | SGLang fast-LLM runtime | second-tier inference choice |
| `ollama/ollama` | Ollama local-LLM daemon | broad consumer + small-org deployment |
| `langgenius/dify-{api,plugin-daemon,sandbox,web}` | Dify LLMOps platform full chart | operator runs Dify orchestration over their inference |
| `xprobe/xinference` | Xinference model server | typically paired with Dify |
| `langflowai/langflow` | Langflow agent builder | low-code LLM dev tool |
| `rocm/vllm`, `rocm/vllm-dev` | AMD ROCm vLLM variant | AMD GPU stack, not NVIDIA |
| `ascend/vllm-ascend` | Huawei Ascend NPU vLLM | Chinese-sovereign hardware stack |
| `soar97/triton-cosyvoice` | Triton-served voice synthesis (CosyVoice TTS) | inference for audio gen |
| `eosphorosai/dbgpt` | DB-GPT (db-aware LLM agent) | data-tooling integration |
| `hiyouga/llamafactory` | LLaMA fine-tuning toolkit | local training pipeline |
| `litellm/litellm-database` | LiteLLM proxy with DB | multi-provider proxy + persistence |
| `wechatopenai/weknora-{app,docreader,ui}` | WeChat WeKnora knowledge stack | WeChat-integrated RAG |
| `beclab/aboveos-fastgpt-*` | FastGPT family on AboveOS | self-hosted ChatGPT-clone stack |
| `000002/ai-platform/inference/chatglm3-6b-apiserver` | internal-namespace ChatGLM API server | operator internal naming leak |
| `000002/ai-platform/train/chatglm` | internal training pipeline | full ML lifecycle exposed in catalog |
| `wechatopenai/weknora-app` | WeKnora consumer-facing | brand attribution: WeChat |

### Multi-port operator signature

Six operators ran the same registry on multiple ports of the same host. The image catalog was identical across ports for each operator.

| IP | ports | ASN | image-set hint |
|---|---|---|---|
| `209.141.57.54` | 58000, 55000, 51000 | FranTech Solutions (US) | 89 repos, sglang + vllm-openai |
| `89.117.94.189` paired with `89.117.94.197` | 55000, 51000 | Ethernet Servers (US) | matched 28-repo catalog, sglang + vllm-openai |
| `149.248.14.62` | 55000, 51000 | Vultr Holdings | 50 repos, ollama + vllm-openai |
| `206.237.12.86` | 50003, 50006 | VH Global | 25 repos, ascend + sglang + vllm-openai |
| `114.250.51.185` | 55000, 58000 | Beijing (CN) | 1 repo (vllm-openai) on both ports |
| `163.61.31.178` | 55000, 51000 | (TBD) | 40 repos, ollama + vllm-openai |
| `149.28.8.247` | 51000, 55000 | (TBD) | 15 repos, full Dify chart + vllm-openai |
| `101.71.15.254` adjacent `101.71.15.248` | 5000 each | China | identical 12-repo set, `vllm-openai-x86` (custom build tag) |

The `101.71.15.248`/`101.71.15.254` adjacent-IP pair shipping a *custom* `vllm-openai-x86` tag is the operator-fingerprint move — the rename indicates an internal CI/CD that pulls vllm-openai upstream, retags for x86, and pushes to their own registry. Catalog leak surfaces the rebrand.

### Internal-namespace leak — operator OPSEC failure

`124.163.255.214:5000` (China Unicom Shanxi province network) leaked the most informative image set in the survey:

```
000002/ai-platform/agent/hs-ai-agent-dify
000002/ai-platform/inference/chatglm3-6b-apiserver
000002/ai-platform/inference/embed_n_rerank
000002/ai-platform/inference/llama3-8b-apiserver
000002/ai-platform/inference/vllm-openai
000002/ai-platform/train/chatglm
000002/ai_platform/inference/chatglm3-6b-vllm-apiserver
```

The `000002` prefix is an internal tenant/project ID. The catalog discloses the operator's internal AI-platform namespace structure (`inference/`, `train/`, `agent/`), which models they are running in production (ChatGLM3 6B, Llama3 8B, embedding/rerank), and that the platform integrates Dify as the agent layer (`hs-ai-agent-dify`). This is operator infrastructure architecture leaking via a forgotten unauth registry.

### Geographic + ASN distribution

The 49 unauth registries cluster on:
- **Chinese cloud / ISP networks:** China Unicom (multiple provinces), Tencent Cloud, Huawei Clouds Singapore, Beijing AS, Aliyun
- **Hetzner (DE):** at least 4 hosts
- **Vultr / The Constant Company / DigitalOcean:** common bulletproof / lift-and-shift hosting tier
- **VH Global / Ethernet Servers / FranTech / DMIT / IT7:** smaller-cloud + bulletproof hosts
- **Universities and government:** none in this 64-pool (universities surfaced in the parallel llama.cpp pool — see below)

This skew matches the prior China-operator-ecosystem note: Chinese operators frequently expose Docker registries on high-numbered ports (55000, 51000, 58000) on bulletproof US/EU hosting, not on canonical port 5000 alone.

## Parallel finding — 81 exposed llama.cpp servers serving Meta Llama models

The variant pivot also surfaced a 83-host pool via `"id":"meta/llama"` substring (Shodan-crawled `/v1/models` JSON responses). 81 saved are **llama.cpp HTTP servers** exposing the OpenAI-compat `/v1/models` endpoint with Meta Llama model IDs. ASN distribution: China Mobile, Hetzner, Oracle Public Cloud, AWS Sweden, Clemson University, University of Lancaster, Instituto Politecnico Nacional (Mexico), Comcast Cable home IPs, Aliyun, etc. The single Hetzner host on port 11434 (`116.202.234.227`) is Ollama's default port, suggesting Ollama-via-llama.cpp.

The llama.cpp pool was not deep-verified in this survey (catalog vs API distinction matters — verifying these as actually-serving-inference would have required `/v1/chat/completions` invocation, which crosses the restraint line). Logged here as a deferred secondary finding for a focused llama.cpp survey.

## Primary-target negative result — NIM and Triton are Shodan-dark

### NIM (`nvidia-nim`)

NIM is OpenAI-compat REST. The API serves JSON on `/v1/*`; the Shodan crawler reaches `/`, which on NIM returns empty (404). NIM's HTML-indexable surface is zero. All variant dorks for NIM-specific metadata returned 0 across the survey:

| variant tier | examples | count |
|---|---|---:|
| canonical brand strings | `"NVIDIA NIM"`, `"NVIDIA-NIM"`, `"nvcr.io/nim"`, `"nvcr.io/nvidia"`, `"nvidia/nim"` | 2 / 2 / 0 / 2 / 2 |
| NIM env vars | `"NGC_API_KEY"`, `"NIM_MODEL_NAME"`, `"NIM_HTTP_API_PORT"`, `"NIM_LOG_LEVEL"`, `"NIM_PEFT_SOURCE"` | all 0 |
| NIM response headers | `"X-NIM-Trace-Id"`, `"X-NIM-Request-Id"`, `"NIM-LLM-Version"`, `"x-nim-trace-id"` | all 0 |
| NIM image tags | `"nim:1.0"`, `"nim:1.1"`, `"nim_image"`, `"nvcr.io/nim/meta"`, `"nvcr.io/nim/mistralai"` | all 0 |
| NIM owned_by JSON | `"\"owned_by\":\"nvidia\""`, `"\"vendor\":\"nvidia\""` | 0 / 5 |
| NIM Helm chart | `"nim-deploy"`, `"nim_chart"`, `"nim-llm-helm"`, `"nim-operator"`, `"NIM Operator"` | all 0 / 1 / 1 |
| NIM container model names | `"meta/llama3-8b-instruct"`, `"mistralai/mistral-7b-instruct"`, `"microsoft/phi-3-mini-4k-instruct"` | 0 / 0 / 0 |

The only NIM-specific count >2 was `"NIMS"` = 207 (an unrelated acronym pool — National Information Management Systems and similar) and `"X-NIM"` = 334 (substring; not specific to NIM). The thesis stands: there is no publicly-indexed exposed NIM API surface.

### Triton (`triton-inference-server`)

Triton is a JSON API too (different schema: `/v2/health/ready`, `/v2/models`, `/v2` metadata). Same Shodan-dark pattern at the API layer.

The `http.title:"Triton"` (314 hits) and `"NVIDIA Triton Inference Server"` (50 hits) pools collapsed under verification:
- **1 host** (`15.161.228.100`, AWS Italy, 7 ports) = honeypot bait, identical 2355B HTML on every path
- **2 hosts** = lifecycle-cycled FPs (Synology DSM with cert CN `priv-10.1.1.91`, Plex Media Server on Windows 7 with cert CN `Gozargah` from the Marzban/V2Ray panel ecosystem)
- **39 hosts** = dead (000 no response)
- **0 hosts** = real Triton

`"name":"triton"` (180 hits, the Triton `/v2` metadata JSON signature) downloaded as 0 saved results — a Shodan API artifact where the count index and the download index disagreed.

### The bait host — 15.161.228.100

- AWS Data Services Italy (AMAZON-MXP, AS16509)
- 7 ports advertised: 5558, 5858, 8908, 12108, 12508, 18108, 24808 — all titled "NVIDIA Triton Inference Server" in Shodan
- Body: randomized HTML with a stable favicon (`/favicon_17c62c5b-6450-4c61-a190-9ac65041fd01.ico`, 1078B). Generic favicon hash `-1216248324` (1.9M matches globally, not operator-unique). The UUID in the favicon URL is randomized per host
- Server header: `Amazon-Cloud-Drive`
- Catchall: any request path other than `/v2` or `/favicon*` returns the same 2355B template (verified with `/v2/whatever_garbage_path` → identical 2355B as `/v2/models`)
- `/v2` anomaly: returns 8 bytes `__schema` — the GraphQL introspection query name. Possibly a Hasura fallthrough, possibly a tracking marker

The "Amazon-Cloud-Drive" server header alone has 3,950 hits across Shodan. That broader pool likely contains the same operator's fleet but with different bait personas. Out of scope for this survey but a clean target for a follow-up.

## Candidate insights

1. **Shodan title dorks for API-only platforms are honeypot- and lifecycle-FP-dominated.** Confirmed for NIM and Triton. Primary failure mode of the passive-dork-then-verify chain on JSON-only APIs.
2. **NIM is Shodan-dark by design.** Real NIM operators are either not exposing the API (auth at the gateway) or the Shodan crawler doesn't reach `/v1/models`. The variant pass exhausted reasonable metadata signatures; the auth-on-default thesis is empirically *unmeasurable* here through Shodan alone.
3. **Variant pivot recovers real findings when primary target is dark.** Going from `"vllm-openai"` (the deployment-time string) to `/v2/_catalog` verification produced 48 confirmed leaks where the original chain produced 0. The dorking-zero variant chain is a productive methodology.
4. **Unauth Docker registries are a quiet operator-OPSEC sink for LLM-infra deployments.** Image catalogs leak: which inference stack is running (vLLM/SGLang/Ollama/Dify), what hardware (NVIDIA/AMD ROCm/Huawei Ascend), the operator's internal namespace structure (`000002/ai-platform/inference/...`), and brand attribution (WeChat, FastGPT). The catalog endpoint is a free names-only enumeration that costs the operator significant attack-surface disclosure.
5. **High-numbered Docker-registry ports (51000, 55000, 58000) cluster on bulletproof hosting + Chinese operators.** Operators using non-canonical registry ports are signaling lift-and-shift LLM deployments on rented infrastructure, often spanning multiple hosts of the same provider.

## Toolchain provenance

- **shodan CLI** with REST API key (9,069 → ~9,061 credits used): 9 dork rounds, ~130 distinct queries logged across `dork-counts.txt` + `dork-pivots*.txt` (rounds 1-9). The variant pivot was driven by Nick's instruction to make ≥5 variants of every 0-result string.
- **tome** (canonical platform corpus): NIM JSON sourced from `Generative AI on Kubernetes` ch01
- **visorgraph** (`-rps 4`, 32 workers): 338 probes across 42 Triton candidates, 0 edges, 2 informative cert CNs (Synology lifecycle FP + Marzban-stack lifecycle FP)
- **aimap** (`-scan-all-fingerprints -threads 12 -timeout 8s`): empty report across 68 shadow ports — no NIM `/v1/models` 200s, no `nvcr.io` markers
- **curl + Python urllib + concurrent.futures**: 64-host Docker Registry verification with `/v2/_catalog` GET + LLM-token catalog grep
- **whois** for the bait host AS attribution

## Files

- `dork-counts.txt` — initial 3 tome dork tiers
- `dork-pivots.txt`, `dork-pivots-r2.txt` through `dork-pivots-r9-variants.txt` — full variant chain
- `bait-fleet-pivot.txt` — favicon-hash + server-header pivot attempts
- `targets.txt` / `ips.txt` / `ports.csv` — 69 ip:port pairs / 42 IPs / 68 ports for Triton-title pool
- `nim-meta-llama-83.json.gz` — 81 llama.cpp servers exposing meta/llama model IDs
- `nim-root-meta-6.json.gz` — 6 high-precision NIM-style `root` field matches
- `nvidia-nim-strict.json.gz` / `nim-llm-strict.json.gz` — Shodan NIM-class direct hits
- `triton-tight.json.gz` — Shodan 48 ClickHouse FP hits on `"triton-inference-server"` substring
- `triton-title.json.gz` — Shodan 312 Triton-title hits (314 reported, 312 saved)
- `title-NIM.json.gz` — Shodan 137 NIM-word hits
- `vllm-openai-66.json.gz` — Shodan 64 hits on `"vllm-openai"` substring
- `vllm-broad-146.json.gz` — Shodan 100-sample of `"vllm"` broad pool
- `ngc-nvidia-42.json.gz` — Shodan 41 hits on `"ngc.nvidia"` (NVIDIA DSX Air cluster, mostly AWS)
- `verify-liveness.csv` — 69-row active probe sweep over Triton-title pool
- `verify-registries.csv` — 49-row verified unauth Docker Registry sweep
- `visorgraph.json` + `visorgraph.err` — cert-pivot run
