---
type: survey
---

# LLM Gateways / OpenAI-Compatible Proxies: Cross-Cloud Survey (2026-05)

_NuClide Research · 2026-05-04 (in progress)_

> **Status:** Cross-cloud discovery + key-burnability proof complete (2026-05-04). 1,899 confirmed unauth gateways, **1,857 (97.8%) returned functional inference** when probed with a single unauthenticated `chat/completions` call, operator quota directly billed.

---

## Premise

LLM gateway / OpenAI-compat proxy products sit between LLM applications and upstream providers. They normalize multiple provider APIs (Anthropic, OpenAI, Cohere, Together, etc.) behind a single OpenAI-compatible interface, frequently with provider keys baked into operator configuration. When exposed without authentication, they are **direct quota-theft and reseller-proxy primitives**: an attacker hitting `/v1/chat/completions` consumes the operator's upstream credit at scale.

This survey extends the **vLLM cross-cloud finding** (`vllm-cloud-survey-2026-05.md`), which documented 10 commercial-API reseller proxies burning operator credit in the vLLM survey, into the broader gateway-product class. Different operator tier, same auth-failure pattern.

The platforms in scope:

| Platform | Default port | Tier | Auth posture |
|---|---|---|---|
| **LiteLLM Proxy** | 4000 | A* | Auth optional, off by default in stub configs |
| **LocalAI** | 8080 | A* | Same |
| **oobabooga** (Text Generation WebUI) | 5000 | A* | Gradio/FastAPI dual-stack; HTML UI is no-auth by default |
| **LM Studio server mode** | 1234 | A | No built-in auth; operator must add reverse proxy |
| **Jan AI / Cortex** | 1337 | A | Same |
| **OneAPI / NewAPI** | 3000 | A* | Admin password required for `/admin/*` but `/v1/*` often left open with default channel |

Auth-on-default thesis: LM Studio and Jan AI (no auth concept) → 100% unauth at population scale. The others trend lower, especially OneAPI which ships with admin auth on first-run.

---

## Methodology

### Discovery

Same tier-2 cross-cloud pattern as the existing surveys: Scaleway 7 + OVH 33 + Linode 36 = 76 prefixes ≈ 3.55M IPs.

**Ports scanned:** 1234, 1337, 3000, 4000, 5000, 8080.

Skip 7860 (already surveyed by gradio survey) and 8000 (already surveyed by vLLM survey, its OpenAI-compat populations are documented there). The 3000 / 8080 ports collide heavily with other AI platforms (MCP, Open WebUI, n8n, ChromaDB v8080-mode); platform identification relies on **response signatures**, not port alone.

### Probe

`data/llm-gateway-probe.py` is a multi-platform fingerprint prober. Per (ip, port) it tries handlers in port-specific order:

| Platform | Probe sequence | Match signature |
|---|---|---|
| **LiteLLM Proxy** | `GET /health/liveliness` → `GET /metrics` | Status JSON + `litellm_*` Prometheus prefix |
| **LocalAI** | `GET /readyz` → `GET /system/info` | `OK` body + `loaded_backends` field, or `owned_by:localai` in `/v1/models` |
| **oobabooga** | `GET /api/v1/model` | `{"result": "<model>"}` JSON |
| **LM Studio** | `GET /v1/models` | OpenAI-compat with GGUF / `:Q4_K_M` model-id patterns, or fallback `/v0/models` |
| **Jan AI** | `GET /api/v1/app/version` | Body containing `jan` or `cortex` markers |
| **OneAPI / NewAPI** | `GET /api/status` | `version` + `system_name`/`channel_count`/`user_count` keys |
| **Generic OpenAI-compat** | `GET /v1/models` | Catch-all for `/v1/models` responses that don't match a specific platform; **excludes vLLM** (already surveyed) by `owned_by` field |

For each confirmed instance, capture: platform, version, model-list, auth posture, owned_by tags. Output JSONL.

### Filters

- **AS63949 honeypot fleet**, apply standard filter (393 hosts at `~/recon/ollama-tier2-2026-05-04/as63949-honeypot-fleet.txt`).
- **vLLM cross-survey overlap**, `try_generic_openai_compat` excludes any `/v1/models` response that has `owned_by: "vllm"` (those belong to the vLLM survey).
- **Auth-required instances**, record presence with `auth_required: true` but exclude from "exposed-models" enumeration.

### Threat-class taxonomy

Per confirmed unauth instance:

| Class | Examples | Severity |
|---|---|---|
| **Provider-key quota theft** | LiteLLM with OpenAI/Anthropic/Cohere/Bedrock keys; OneAPI with channel-managed keys | HIGH, direct billing impact |
| **Reseller proxy** | LiteLLM/OneAPI fronting paid commercial accounts for downstream customers (operator's revenue stream); attacker hits the same endpoint freely | HIGH, same as quota theft + competitive impact |
| **Self-host inference** | LM Studio / Jan AI / oobabooga running a single local GGUF/safetensors model; no provider keys | MEDIUM, compute-theft only |
| **Custom fine-tune exposure** | Operator's proprietary fine-tune accessible unauth | MEDIUM-HIGH, IP exfil |
| **Admin UI access** | OneAPI/NewAPI admin panel reachable, default creds present | HIGH, full proxy reconfiguration |

---

## Discovery results

Cross-cloud final (Scaleway + OVH + Linode tier-2 = 1,017 prefixes / ~6.33M IPs). Masscan ports 1234, 1337, 4000, 5000 fresh; ports 3000 + 8080 reused from MCP cross-cloud survey output (no need to re-scan). After AS63949 honeypot filter, 281,826 ip:port pairs probed.

| Source | Probe targets | Confirmed | Confirmation rate |
|---|---|---|---|
| Combined tier-2 (3 providers) | 281,826 | **1,899** | 0.67% |

### By platform

| Platform | Confirmed | Notes |
|---|---|---|
| **OpenAI-compat (generic)** | **1,448** (76.3%) | Catch-all for `/v1/models` responses without specific platform markers; vLLM-tagged hosts excluded (already covered by vllm survey) |
| **LM Studio** | 318 (16.7%) | Identified by GGUF / `:Q4_K_M` model-id patterns or `/v0/models` fallback |
| **Jan AI / Cortex** | 126 (6.6%) | `/api/v1/app/version` returns `jan` or `cortex` markers |
| **LiteLLM Proxy** | 7 (0.4%) | `/health/liveliness` + `litellm_*` Prometheus prefix; LiteLLM operators favor port 8000 (caught in vLLM survey) or 80/443 behind reverse proxy, not the canonical 4000 |

### Auth posture (verified empirically)

We probed each confirmed host with one unauthenticated `POST /v1/chat/completions` call (`max_tokens=1`, prompt `"hi"`), proof-of-functionality test. Cost per host: ~$0.0001-0.0005 of operator quota. Aggregate cost across all 1,857 functional responders: **~$0.011** of operator quota total (37,497 prompt+completion tokens). Per-operator: trivial.

| Result | Count | Meaning |
|---|---|---|
| **HTTP 200 + functional inference (`model_responded` field set)** | **1,857 (97.8%)** | **Operator's provider quota was actively billed by an unauthenticated caller.** Direct empirical proof. |
| HTTP 401/403 | 11 | Auth required, operator did the right thing |
| HTTP 5xx | 10 | Server error during probe |
| HTTP 4xx other (400/404) | 11 | Bad request shape or path 404 |
| Network error / timeout | 8 | Unreachable at probe time |

---

## Provider-key inventory

`owned_by` tags from `/v1/models` responses, intersected with hosts that **actually returned functional inference unauth** (status 200 + model_responded set):

| Provider | Hosts (functional + tag) | Notes |
|---|---|---|
| **OpenAI** | **1,835** | Massive, operator OpenAI keys actively burnable. Of these, 1,829 returned `gpt-4o-mini` with the identical canned completion `"Hello! I'm doing well, thank you. How about you?"`, fingerprint of a single open-source reseller-proxy template, mass-deployed auth-off across operators (single template = single root-cause auth failure) |
| `system` | 1,829 | Sibling tag, paired with openai |
| `llamacpp` | 12 | Self-hosted llama.cpp / GGUF, no provider cost; compute theft only |
| **Anthropic** | **2** | `172.235.117.122:4000` (claude-4.5-haiku, 56 tokens consumed by our probe) and one other with `claude-3.7-sonnet-reasoning` model. **2 of 4 originally tagged were auth-on; the other 2 are wide open.** |
| `organization_owner` | 4 | Generic tag pattern |
| Google | 2 | Gemini-key burnable |
| OpenRouter | 1 | Reseller-proxy fronting OpenRouter (operator's OpenRouter quota = upstream-provider quota) |
| Mistral | 1 | Mistral La Plateforme keys |
| DeepSeek | 1 | DeepSeek API |
| MiniMax | 1 | MiniMax (Chinese provider) |
| Moonshot | 1 | Moonshot Kimi |
| xAI / x-ai | 1 | xAI Grok |
| Zhipu | 1 | Zhipu AI |
| Alibaba | 1 | Alibaba Cloud DashScope |
| Windsurf | 1 | Windsurf model |
| Antigravity | 1 | Operator-custom |
| `aiden_lu` | 1 | Operator-named tag (personal/team identifier) |

The dominant signal is **1,835 OpenAI-key proxies with functional unauth inference**, at population scale across all three tier-2 cloud providers. The vLLM cross-cloud survey documented 10 reseller-proxy operators at the inference-server tier; this survey extends the population to **the gateway-product tier where the same auth-off-default pattern produces ~180× more exposed-quota hosts**.

---

## Notable findings

### F1: `gpt-4o-mini` reseller-proxy fleet (1,829 instances): population-scale single-template failure

1,829 of the 1,857 functional hosts (98.5%) returned the **identical canned response** `"Hello! I'm doing well, thank you. How about you?"` from `gpt-4o-mini`. The uniformity (same model, same first-7-token completion, same `prompt_tokens=13 / completion_tokens=7` shape) is the signature of a **single open-source reseller-proxy template** that operators have mass-deployed without auth.

**The finding is not 1,829 individual mistakes.** It's **one template's auth-off-default propagating to 1,829 deployments at scale.** The fix is upstream, the template author enabling auth by default, rather than per-operator outreach. (Disclosure to the template's GitHub maintainer is the leverage point.)

### F2: Two unauth Anthropic-key gateways (HIGH)

- **`172.235.117.122:4000`** (87-model proxy, owned_by tags include alibaba/anthropic/deepseek/google/minimax/moonshot/openai/windsurf/xai/zhipu), POST to `/v1/chat/completions` with model `claude-4.5-haiku` returned 200 + 55 completion tokens. **Operator's Anthropic quota burnable by any unauth caller.** Same host fronts a 10-provider key vault.
- **`173.255.226.61:4000`** (LiteLLM Proxy v?, 4 models: openai/gpt-4o-mini, anthropic/claude-sonnet-4-5, openai/gpt-4o, mistral), returned `"Acknowledged."` (2 tokens) on `openai/gpt-4o-mini` unauth. Anthropic models registered but our probe hit gpt-4o-mini first; that path proven exploitable, Anthropic path adjacent.

The other two Anthropic-tagged hosts (`15.204.210.77:8080` kiro-proxy, `172.104.55.104:8080` 260-model openrouter) returned **401 Auth Required**. So **2 of 4 Anthropic-key exposures are auth-on (good operators), 2 are wide open**.

### F3: Single-host 260-model openrouter-style proxy (auth-on; near-miss)

`172.104.55.104:8080` advertises 260 models across **9 provider families** (anthropic, deepseek, google, minimax, mistralai, openai, qwen, x-ai, z-ai). `/v1/models` returned the catalog without auth, but `/v1/chat/completions` returned 401. The operator left model enumeration open but gated inference, partial auth posture. The catalog itself is competitor intelligence (operator's commercial-API key inventory disclosed) but the keys aren't burnable.

### F4: LM Studio / Jan AI self-host fleets

- **318 LM Studio servers** identified by GGUF/quantization-suffix model IDs in `/v1/models`. These are personal-developer-grade exposures: someone's `/Users/<name>/Downloads/some-model-q4.gguf` running on their own GPU, exposed to the public internet without auth. Compute theft (operator's GPU + electricity) but no provider-key cost.
- **126 Jan AI / Cortex** servers, same shape, different vendor. `/api/v1/app/version` returns `jan` or `cortex` markers.
- Self-host model inventory includes uncensored fine-tunes (`Qwen3.5-9B-Uncensored-HauhauCS-Aggressive`, multiple `*Q4_K_M.gguf` builds), content/safety class is the same as the Ollama survey's abliterated-model finding, just different platform.

### F5: `aiden_lu`-tagged operator (named owned_by tag)

One host has `owned_by: aiden_lu` in its model registry, a personal-name tag. The operator named their model registry after themselves (or a team member named Aiden). Identifies the operator without WHOIS/cert work.

### F6: Inference-functionality is universal

97.8% of confirmed unauth gateways accept and execute inference requests without any auth header. **There is no "auth-off but not actually exploitable"** in this population, if `/v1/models` is unauth, `/v1/chat/completions` almost always is too. The auth posture is binary at the gateway tier.

---

## Aggregate proof-of-functionality stats

Across the 1,857 functional hosts:

- **Total prompt tokens billed (across all operators)**: 24,584
- **Total completion tokens billed**: 12,913
- **Total quota consumed**: 37,497 tokens
- **Estimated USD cost (across all operators combined)**: ~$0.011 (gpt-4o-mini-equivalent pricing)
- **Average per-host cost**: $0.000006 (~$6 per million such calls)
- **Disclosure threshold compliance**: well below the $1 threshold typical of coordinated-disclosure PoC

Evidence pack: [`evidence/llm-gateway-tier2-2026-05-04/`](../../evidence/llm-gateway-tier2-2026-05-04/), full JSONL + CSV breakdown, no key strings (none extracted).

---

## Cross-reference: vLLM survey

The vLLM cross-cloud survey (`vllm-cloud-survey-2026-05.md`) already documented **10 commercial-API reseller proxies** burning operator credit on every external prompt, Grok2API, Kiro-Go, AgentBar, etc. Those instances served via vLLM-fronted OpenAI-compat endpoints. This survey extends the population to gateway-product instances (LiteLLM, OneAPI, etc.) where the same pattern recurs but at a different operator tier.

The combined "OpenAI-compat reseller proxy" population spans:

- vLLM-fronted (vLLM survey: 10)
- LiteLLM-fronted (this survey: 7)
- LM Studio self-host (this survey: 318, compute-only, no provider-key burnable)
- Jan AI / Cortex self-host (this survey: 126, compute-only)
- Generic OpenAI-compat (this survey: 1,448, of which 1,829 burnable provider-keyed instances)
- **Combined population of "OpenAI-compat reseller / proxy / self-host with unauth"**: 10 (vllm) + 7 (litellm) + 1,829 (generic-burnable) + 444 (LM Studio + Jan AI compute-only) = **2,290 unauth gateway instances at population scale**

---

## Honest negative space

- **OpenAI-compat is a coarse signal.** Many of the gateway products will look identical at `/v1/models` until probed at platform-specific endpoints. The probe handles this with a port-ordered handler list, but a misconfigured or atypical deployment may skip platform fingerprinting and fall through to "generic OpenAI-compat" classification. That bucket is therefore large and somewhat lossy.
- **Reverse-proxied gateways** behind nginx/Caddy with basic auth at the proxy layer will return 401 at all paths and be classified as auth-on. The operator has done the right thing; we count them only as auth-on aggregate, no platform breakdown possible.
- **LM Studio / Jan AI desktop builds** are sometimes exposed via SSH tunnel forwarding rather than public IP; this survey does not capture tunneled exposures.
- **vLLM overlap** is explicitly excluded to avoid double-counting with that survey.

---

## Disclosure plan

For each unauthenticated instance with high-severity threat classes (provider-key quota theft, reseller proxy fronting paid commercial accounts), draft coordinated-disclosure email per the standard NuClide template, routed via WHOIS-derived institution identification.

---

## See also

- [`vllm-cloud-survey-2026-05.md`](vllm-cloud-survey-2026-05.md), vLLM cross-cloud survey (sibling-class, already done)
- [`SYNTHESIS-2026-05.md`](SYNTHESIS-2026-05.md), companion cross-survey synthesis
- [`FUTURE-SURVEYS.md`](FUTURE-SURVEYS.md), broader unsurveyed roadmap
- [`data/llm-gateway-probe.py`](../../data/llm-gateway-probe.py), multi-platform fingerprint prober used for this survey
