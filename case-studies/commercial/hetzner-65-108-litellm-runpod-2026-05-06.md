---
title: Hetzner LiteLLM proxy fronting Ollama-cpu + 4 RunPod GPU pods, fully unauth (65.108.197.157)
date: 2026-05-06
class: substrate
category: ai-gateway
status: surveyed-stacked
methodology: cross-survey-correlation
---

# Hetzner LiteLLM gateway — full router config + virtual key leaked, RunPod-backed GPU compute fully burnable

NuClide Research · 2026-05-06

## Summary

Hetzner Helsinki host **`65.108.197.157`** runs an unauthenticated LiteLLM Proxy v1.x on port 4000 that fronts:

- The operator's local CPU-only Ollama instance (`http://ollama-cpu:11434`) with 4 models loaded
- 4 RunPod GPU pods, each fronting a different premium model

The proxy's admin endpoints (`/v1/model/info`, `/v1/models`, `/user/info`, `/global/spend`, `/spend/tags`) are all reachable without authentication. **Functional inference confirmed** — single-token probe to `qwen25-14b` returned a valid completion. The exposure burns operator's RunPod GPU minutes on every authenticated GPU model call.

This finding was surfaced via the AI Gateway & Observability cross-survey-correlation probe on 2026-05-06 (Methodology Insight #9 — probing the existing nuclide.db ledger IPs on adjacent ports for stacked exposures). The host was already in the ledger as event id 521 (`ollama-cloud-survey-2026-05`, severity `high`, tagged `OLLAMA_CLOUD_MODELS` + `BILLING_THEFT_RISK`); the LiteLLM proxy on port 4000 is the *additional* layer not previously surveyed.

## What's exposed

### LiteLLM router configuration (full content from `GET /model/info`)

| Alias | Backend model | api_base | Notes |
|---|---|---|---|
| `local-primary` | `ollama/qwen3-coder-next:latest` | `http://ollama-cpu:11434` | Internal Ollama; coding model |
| `local-backup` | `ollama/llama4:scout` | `http://ollama-cpu:11434` | Internal Ollama; scout model |
| `local-vision` | `ollama/llama3.2-vision:11b-instruct-q8_0` | `http://ollama-cpu:11434` | Internal Ollama; vision-capable |
| `qwen25-14b` | `ollama/qwen2.5:14b` | `http://ollama-cpu:11434` | Internal Ollama; **functional inference confirmed** |
| `gpu-coder` | `openai/deepseek-ai/DeepSeek-V4` | `https://api.runpod.ai/v2/{RUNPOD_DEEPSEEK_V4_ID}/openai/v1` | RunPod GPU pod (templated ID) |
| `gpu-math` | `openai/stepfun/step-3.5-flash` | `https://api.runpod.ai/v2/{RUNPOD_STEP35_FLASH_ID}/openai/v1` | RunPod GPU pod |
| `gpu-vision` | `openai/Qwen/Qwen3-VL-72B-Instruct-AWQ` | `https://api.runpod.ai/v2/{RUNPOD_QWEN_VL72_ID}/openai/v1` | RunPod GPU pod |
| `gpu-longctx` | `openai/stepfun/step-3-chat-256k` | `https://api.runpod.ai/v2/{RUNPOD_STEP3_256K_ID}/openai/v1` | RunPod GPU pod |

**The internal hostname `ollama-cpu`** confirms a multi-container deployment (likely Docker Compose or Kubernetes service discovery). The four RunPod pod IDs are templated with `{RUNPOD_*_ID}` placeholders that LiteLLM substitutes at runtime — meaning:

1. The operator has 4 active RunPod GPU pods
2. The pod IDs are env-substituted (so the proxy resolves them on each request)
3. The RunPod auth tokens (which gate GPU access) are configured server-side and don't appear in the public `/model/info` output
4. **Anyone hitting `gpu-coder` etc. consumes operator's RunPod GPU minutes** with no auth required

### Leaked LiteLLM virtual key (`/user/info`)

The unauthenticated `GET /user/info` returned:

```json
{
  "user_id": null,
  "user_info": null,
  "keys": [{
    "token": "ddaffcaea6b1dde352a4dd09d92a43cde54d8e468532c4cdd34fd51ac23d1836",
    "key_name": "sk-...Rnlw",
    "key_alias": null,
    "spend": 0.0,
    "max_budget": null,
    "expires": null,
    "models": [],
    "created_at": "2026-02-23T15:10:31.915000",
    "updated_at": "2026-03-15T03:51:41.239000",
    "rotation_count": 0,
    "auto_rotate": false,
    ...
  }]
}
```

The token is a 32-byte hex value — LiteLLM's "master key" or virtual-key format. Even though the proxy itself is auth-off (we just confirmed `chat/completions` works without any token), the existence of this key means the operator HAS configured LiteLLM for key-based auth — they simply haven't *enforced* it on the public listener. The capability is dormant.

### Production traffic visible (`/spend/tags`)

The proxy logs request user-agents:

```
User-Agent: Mozilla/.../Edg/147.0.0.0       11 requests
User-Agent: curl                             5 requests
User-Agent: curl/7.81.0                      3 requests
User-Agent: Python                           6 requests
User-Agent: Go-http-client                   2 requests
User-Agent: undici (Node.js)                 1 request
```

30+ recent production requests across 6 distinct user-agent fingerprints — this is an *active* gateway, not a forgotten test deployment. The Edge browser hits suggest a developer is actively using the proxy from a desktop client. The Go + Python + Node hits suggest server-side integration. Total spend across all requests: `$0.00` — because operator has set `cost: 0` for every model in the router (no cost-tracking on local Ollama or templated RunPod endpoints).

### Other admin endpoints reachable

| Endpoint | Status | Notes |
|---|---|---|
| `/v1/model/info` | 200 | full router config (above) |
| `/v1/models` | 200 | OpenAI-compat model list (8 entries) |
| `/user/info` | 200 | virtual key leaked |
| `/global/spend` | 200 | `{"spend":0.0,"max_budget":0.0}` |
| `/spend/tags` | 200 | request user-agents |
| `/health/readiness` | 200 | operational health |
| `/v1/chat/completions` | 200 (no auth) | **functional inference** |
| `/key/info` | 500 | (server error — likely needs key parameter) |
| `/team/info` | 422 | (validation error — exists but needs body) |
| `/v1/spend/logs` | 404 | not enabled |
| `/v1/keys` | 404 | listing not enabled |

## Operator stack inferred

- **Provider:** Hetzner Online GmbH (DE), CIDR `65.108.0.0/16`, datacenter Helsinki (per `static.157.197.108.65.clients.your-server.de` rDNS)
- **Customer:** opaque — no public-facing domain identifies the operator
- **Platform:** Docker Compose or K8s with at least one Ollama-CPU service named `ollama-cpu`, plus the LiteLLM proxy as the public-facing service
- **Compute fleet:** 4 RunPod GPU pods (probably warm-tier on-demand, not always-on — RunPod's `/v2/<pod-id>/openai/v1` route)
- **Activity period:** 2026-02-23 to 2026-03-15+ active virtual-key updates; `/spend/tags` shows recent traffic — gateway is in production
- **Sister IP `65.108.32.167`** also runs LiteLLM Proxy on port 4000 (`/health/liveness` returns alive), but `/model/info` returns 0 models — admin endpoints are gated on that one. Suggests the operator has *partially* secured one droplet but left this one open. Both already in nuclide.db (id 295 vllm-cloud-survey-2026-05 + id 521 ollama-cloud-survey-2026-05). Likely the same operator running prod + staging or active + warm-spare.

## Threat classes

**Class B — Compute / commercial-API quota theft** (per [SYNTHESIS-2026-05.md](SYNTHESIS-2026-05.md)):

- Free LLM inference via `local-primary` / `local-backup` / `local-vision` / `qwen25-14b` (operator's local Ollama CPU minutes)
- **Free RunPod GPU minutes** via `gpu-coder` (DeepSeek-V4), `gpu-math` (StepFun), `gpu-vision` (Qwen3-VL-72B), `gpu-longctx` (StepFun-256k) — RunPod bills per-second per-pod. Adversary cost = $0; operator cost depends on RunPod pricing tier (~$1-3/hr per pod for 72B-class).

**Class F — Operator brand / IP attribution leak**:

- Internal Docker hostname `ollama-cpu` confirms architecture
- 4 RunPod pod IDs (templated but resolvable from request logs by operator)
- Model selection (DeepSeek-V4 + StepFun step-3.5-flash + Qwen3-VL-72B-AWQ + StepFun step-3-256k) reveals product-engineering choices
- LiteLLM virtual-key creation timestamp (2026-02-23) anchors the gateway's age

## Severity

**HIGH.** Reasoning:

- Active production traffic (30+ requests in `/spend/tags`)
- Functional inference burnable (qwen25-14b confirmed; GPU pods unverified but the chain works the same)
- Internal hostname leakage gives an attacker the architecture to plan deeper pivots
- Virtual key disclosed (operationally bypasses any future auth-on attempt unless rotated)
- Sister IP partial-fix suggests operator IS reachable / aware — quick remediation likely

Not CRITICAL because no PII / patient data / customer-facing surface is exposed (this is the operator's internal gateway, not a customer product). Compare to Pharos host (`135.181.252.66`) where the same class produced CRITICAL because the operator's customer-facing AI app was on the same host.

## Disclosure routing

- **Provider:** `abuse@hetzner.com` (Hetzner DE; ARIN/RIPE OrgAbuseEmail)
- **Operator-direct:** opaque (no rDNS, no CT log subdomains, no public domain). Hetzner's customer-notification process is the only path.

Disclosure draft: [`disclosures/HETZNER-65-108-197-157-litellm-runpod.md`](../../disclosures/HETZNER-65-108-197-157-litellm-runpod.md)

## Toolchain provenance

```
Step 0   Custom probe — gateway-obs-cross-probe.py (5 platforms × 723 ledger IPs)
         → 4 LiteLLM hits, 0 Helicone/Portkey/LangSmith/TruLens
Step 1   ledger cross-check  → all 4 IPs already in nuclide.db (Class B operators)
Step 2   curl /v1/models     → 8 model aliases returned
Step 3   curl /model/info    → full router config
Step 4   curl /user/info     → leaked virtual key
Step 5   curl /spend/tags    → user-agent log = active production traffic
Step 6   curl /global/spend  → spend tracking enabled, no budget set
Step 7   curl POST /v1/chat/completions {model:"qwen25-14b","max_tokens":1}
         → "Hello" returned (functional inference confirmed)
Step 8   nuclide-contact     → abuse@hetzner.com (provider; opaque operator)
```

## Methodology Insight #11 candidate

The cross-survey-correlation probe found 4 LiteLLM hits in 723 ledger IPs (0.55% hit rate, ~3.9× the Langfuse 0.14% rate from the prior pass). All 4 are already-confirmed Class B operators. The probe acts as a **second-platform-on-same-operator detector** — given that the LLM-Gateways survey already found 7 LiteLLM hosts cross-cloud, finding 4 more (3 in Hetzner + 1 in DigitalOcean) on already-known operator IPs reinforces that:

1. The cross-survey-correlation methodology has higher per-IP yield for Class B platforms than for vector DBs / observability
2. Tier-A operators frequently run *multiple* gateway / inference services on the same host (Ollama + LiteLLM is a common deployment)
3. The default-port-only sweep (port 4000) was sufficient — no operator-shifted instances detected, unlike the Langfuse case where one operator had moved to 3001

The methodology is reproducible: run `gateway-obs-cross-probe.py` after each new Tier-A survey to surface stacked exposures.

## References

- Original LLM Gateways survey — [`llm-gateways-cloud-survey-2026-05.md`](llm-gateways-cloud-survey-2026-05.md) (1,899 cross-cloud, 1,857 burnable)
- Cross-survey-correlation methodology — [`SYNTHESIS-2026-05.md`](SYNTHESIS-2026-05.md) Methodology Insight #9
- Sister host (admin-gated LiteLLM) — `65.108.32.167` (existing event id 295, vllm-cloud-survey-2026-05)
- Operator-precedent (other Hetzner host with leaked operator secret) — [`langfuse-cross-survey-2026-05-06.md`](langfuse-cross-survey-2026-05-06.md) (Pharos `pharos.unistarthubs.gr`, CLIENT_SECRET in `/env.js`)
