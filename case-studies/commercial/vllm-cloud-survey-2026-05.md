# vLLM / OpenAI-Compatible LLM Inference Servers on Public Cloud: Auth Posture Survey

_NuClide Research · 2026-05-03_

---

## Summary

Reused the 22,765 port-8000 hits from the prior ChromaDB sweep and fingerprinted them for OpenAI-compatible LLM inference servers via `GET /v1/models` body match (`{"object":"list","data":[{"object":"model",...}]}`). **44 confirmed instances**, all **unauthenticated**. Of these, 19 are confirmed **vLLM** (via `/version` returning a vLLM version string); the remaining 25 are generic OpenAI-compatible servers, a mix of vLLM-with-/version-disabled, `llama.cpp-server`, `text-generation-inference`, `LM Studio`, `FastChat`, and most concerningly **commercial-API reseller proxies** (operators standing up unauth gateways in front of paid OpenAI / Anthropic / xAI / Zhipu accounts).

Each unauth instance is a **free LLM** for anyone who finds it. For the reseller-proxy class, "free LLM" means **direct quota theft from the operator's paid commercial accounts**: an attacker submits prompts, the proxy forwards to OpenAI/Anthropic/etc., the operator's billing meter spins.

---

## Methodology

```
Reused IPs from prior ChromaDB port-8000 masscan: 22,765 hosts

vllm-probe.py (200-thread fingerprint)
  GET /v1/models → match {"object":"list","data":[{"object":"model",...}]}
  GET /version    → if returns {"version":"x.y.z"}, classify as confirmed vLLM
  GET /metrics    → if contains "vllm:"-prefixed metrics, double-confirm vLLM
  → 44 confirmed (19 vLLM + 25 generic OpenAI-compat)
```

NuClide did **not** submit any prompt to `/v1/chat/completions` or `/v1/completions`. Inference would have used the operator's compute (and for the reseller-proxy class, would have spent the operator's commercial-API credits). The model-list endpoint and version probe alone are sufficient to prove exposure.

---

## Findings Summary

| Metric | Value |
|---|---|
| Cloud /16 ranges scanned | 28 (DO/Hetzner/Vultr) |
| Masscan hits on :8000 | 22,765 |
| OpenAI-compatible servers confirmed | **44** |
| Unauthenticated | **44 (100%)** |
| vLLM (confirmed via `/version`) | 19 |
| Generic OpenAI-compatible | 25 |

### Hosting

| Provider | Confirmed |
|---|---|
| Hetzner | 17 |
| DigitalOcean | 14 |
| Vultr | 13 |

---

## Threat Classes

The 44 instances split across four distinct threat classes:

### Class A: Commercial-API reseller proxies (CRITICAL: direct billing theft)

These operators run an OpenAI-compatible gateway in front of paid accounts at OpenAI / Anthropic / xAI / Zhipu / etc. The gateway has no authentication on `/v1/chat/completions`, submitting a prompt routes through to the upstream commercial API, charging the operator's account. An attacker can run unlimited inference using the operator's commercial budget.

The proxy software (`/openapi.json` + `/docs` + `/admin` HTML) is fingerprintable:

| Host | Proxy product | Models exposed |
|---|---|---|
| `178.62.227.102` | **AgentBar LLM Gateway v0.1.0** | **126 models**, all OpenAI lineup (gpt-3.5/4/4o/4.1/5/5-mini/5-nano + audio/realtime variants), embeddings (text-embedding-ada-002, text-embedding-3-small/large), STT (whisper-1), TTS (tts-1, tts-1-hd), images (dall-e-2, dall-e-3), moderation (omni-moderation) |
| `157.90.170.99` | (custom router, `route/*` namespace) | 43 models: Kimi-K2.5/2.6, GLM-5/4.7 + variants, DeepSeek-v3.2/v4, MiniMax-m2.5/2.7, Qwen3.5/3.6, Gemma-4, ElevenLabs (eleven-v3, multilingual-v2), Whisper-large-v3, Hunyuan-Image-3, FLUX-1-schnell, SDXL |
| `206.189.152.172` | (uvicorn-served, `/admin` 307) | 31 models: chatgpt-4o-latest, gpt-4.1, gpt-5/5.1/5.2/5.4/5.5, claude-sonnet-4-6, claude-opus-4-6, claude-sonnet-4-5, gemini-2.5/3.1-pro, grok-3-mini, deepseek, kimi |
| `138.197.121.229` | **Kiro-Go** (Chinese-origin Anthropic proxy, `zh` admin UI) | 21 models: claude-sonnet-4.5/4 + thinking, claude-haiku-4.5 + thinking, deepseek-3.2 + thinking, minimax-m2.5/2.1 + thinking, glm-5 + thinking, qwen3-coder-next + thinking |
| `138.68.228.210` | **Grok2API v2.0.0** (Chinese-origin xAI proxy, `zh-CN` admin UI) | 6 Grok models: grok-3, grok-3-mini, grok-4.1-thinking, grok-4.2-fast, grok-4.2, grok-expert |
| `167.71.19.51` | **Grok2API v2.0.4.rc3** (newer version, served via `granian` Rust ASGI server) | 11 models: grok-4.20-0309 + reasoning/non-reasoning/fast/auto/expert variants, grok-imagine-image-lite, claude-sonnet-4, claude-opus-4, claude-haiku-4, claude-3-haiku |
| `104.236.247.58` | (Zhipu proxy with Anthropic-compat headers) | 11 models: GLM-4.5/4.6/4.7 + thinking + tools + V (vision) variants, GLM-4.5-Air |
| `138.197.17.168` | (nginx-fronted custom proxy) | 4 OpenAI models: gpt-4o, gpt-4o-mini, gpt-4-turbo, gpt-3.5-turbo |
| `138.68.0.205` | (same as above, likely same operator) | Same 4 OpenAI models |
| `65.108.250.0` | (custom proxy) | 4 OpenAI models: gpt-4.1, gpt-4o, gpt-4o-mini, gpt-3.5-turbo |

**Pattern:** several of these are **Chinese-origin open-source LLM proxy projects** (Grok2API, Kiro-Go, AgentBar) deployed on cheap cloud VPSes by operators who want to re-package commercial APIs without authentication. The `zh` / `zh-CN` admin UIs and product naming confirm the origin community. This is a recognised abuse pattern in the broader AI-tooling underground, these proxies are typically pointed at shared/leaked commercial-API credentials and resold to users who cannot easily obtain foreign API keys directly.

**Per-instance financial exposure:** GPT-4o pricing ~$5/1M input + $15/1M output tokens; current xAI Grok pricing ~$3-15/1M tokens; Anthropic claude-sonnet-4.5 ~$3/1M input + $15/1M output. A motivated attacker can drain four-figure dollars per day per exposed proxy without rate limits in their way. The 126-model AgentBar proxy at `178.62.227.102` is the highest-value target in this class, it spans embeddings, audio, image, and multiple LLM families, suggesting sizeable quotas across vendors.

**Admin UI exposure note:** the admin pages render publicly (HTML layout, table headers like "API Key 列表 / API Key List", login forms) but the data-API endpoints (`/admin/api/keys`, `/admin/api/stats`, `/admin/api/users`) return 401 on probes. The stored credentials are not directly leaked. However, the publicly visible product name + version enables CVE/default-credential lookup against the specific upstream project, and the `/openapi.json` discloses the full admin API surface for targeted exploitation if a default-credentials match exists.

### Class B: Operator-attributed proprietary fine-tunes (HIGH: IP exposure)

The model name discloses the operator and their work. Each fine-tune is the product of expensive training runs on operator-curated data; the weights and behavior are now externally probeable.

| Host | Model | Operator inferred |
|---|---|---|
| `65.108.33.72` | `sipgate/call-analysis-qwen35-9b-20260302-merged-experimental` | **sipgate GmbH**, German VoIP/cloud-telephony provider. Call-analysis fine-tune with March 2026 training date. Anyone can probe the fine-tune to learn what call-content classifications sipgate runs on customer voice data |
| `65.109.75.57` | `Infomaniak-AI/vllm-translategemma-12b-it` | **Infomaniak**, Swiss cloud-hosting provider. Italian-language Gemma-12B translation fine-tune |
| `168.119.32.186` | `/opt/app-root/src/models/granite-3.3-8b-instruct` (vLLM `0.13.0+rhai11`) | **Red Hat AI** vLLM distro deployment of IBM Granite-3.3 8B |
| `159.203.44.226` | `Qwen/Qwen2.5-Coder-14B-Instruct-GPTQ-Int4` | Code-generation fine-tune (could be operator product or upstream model) |
| `206.189.88.219` | `vn-accountant`, `vn-accountant-fast` | Vietnamese accounting AI |
| `135.181.113.224` | `deep_researcher` | Custom agent fine-tune |
| `45.63.76.200` | `quinn-glm5` | Custom name-tagged fine-tune |
| `45.76.253.57` | `jarvis` | Custom name-tagged assistant |
| `159.69.80.54` | `digistent-rag` | RAG-tagged custom fine-tune |
| `157.90.12.151` | `qwen3.5-35b` | Possibly fine-tuned Qwen 3.5 35B |

### Class C: Big-model production deployments (HIGH: compute theft scale)

These operators pay real money (multi-thousand-dollar GPU instances) to serve large models. Free LLM inference at this scale ties up GPU memory the operator paid for; sustained queries by an attacker degrade legitimate user experience.

| Host | Model | Compute footprint |
|---|---|---|
| `45.76.23.53` | `amd/Llama-3.3-70B-Instruct-FP8-KV` (vLLM `0.9.2rc2`) | AMD MI300-class GPU; 70B FP8 |
| `149.28.115.34` | `RedHatAI/Llama-4-Scout-17B-16E-Instruct-FP8-dynamic` (vLLM `0.19.0`) | Llama 4 Scout, FP8 dynamic |
| `65.108.32.167` | `openai/gpt-oss-120b` (vLLM `0.16.0`) | OpenAI's open-weight GPT, 120B |
| `45.76.45.65` | `mistralai/Pixtral-12B-2409` (vLLM `0.6.1`) | Vision-language Pixtral 12B |
| `135.181.222.37`, `135.181.56.61`, `65.108.198.21`, `65.108.230.168` | `Qwen/Qwen3-235B-A22B-Instruct-2507-FP8` + `moonshotai/Kimi-K2.6` | **4 Hetzner IPs, identical model list**, single operator running a 4-host cluster of MoE LLMs. Qwen3-235B + Kimi-K2 (1T-class) require multi-A100/H100 hosts each |
| `144.202.51.41`, `149.28.212.148`, `45.32.59.191`, `45.63.39.13` | `Llama-3.1-8B`, `Llama-3.3-70B`, `Mistral-7B-Instruct-v0.3`, `Qwen2.5-7B-Instruct` | **4 Vultr IPs, identical model list**, single operator running a 4-host load-balanced cluster (vLLM `0.6.6.post1` on every host) |
| `144.202.53.99` | `moonshotai/Kimi-K2.6` | Kimi K2 (1T-class MoE) |
| `165.227.37.82` | `moonshotai/Kimi-K2.6` | Same |

### Class D: Specialized / smaller deployments (MEDIUM)

| Host | Model | Purpose |
|---|---|---|
| `149.28.221.64` | `gte-Qwen2-1.5B-instruct` | Embedding model |
| `45.76.153.119` | `qwen3-embedding-0.6b-q4_k_m.gguf` | Embedding (llama.cpp) |
| `157.90.34.111` | `tts-1`, `tts-1-hd` | Text-to-speech (OpenAI-compat) |
| `65.109.240.42` | `Systran/faster-whisper-tiny`, `speaches-ai/piper-en_US-ryan-high`, `silero_vad_v5` | Speech stack: Whisper STT + Piper TTS + Silero VAD |
| `135.181.48.68` | `gemma-4-e2b-q4km.gguf` | Quantized Gemma-4 (llama.cpp) |
| `159.69.114.185`, `65.108.121.151` | Generic GGUF models | llama.cpp-server |
| `157.90.170.113` | `./bin/teuken.gguf` | Teuken (German Fraunhofer multilingual LLM) |
| `65.108.32.170` | `Qwen/Qwen3-4B` | Small Qwen serve |
| `65.108.32.167` | `openai/gpt-oss-120b` | (already in Class C) |
| `165.227.38.203` | `meta-llama/Llama-3.1-8B-Instruct` | Standard Llama 3.1 8B |

---

## Per-Class Severity

| Class | Count | Severity | Remediation urgency |
|---|---|---|---|
| A, Commercial-API reseller proxies | 10 | **CRITICAL** | Same-day, financial bleed |
| B, Operator-attributed proprietary fine-tunes | 10 | HIGH | High, IP exposure |
| C, Big-model production deployments | ~12 (incl. clusters) | HIGH | High, compute theft |
| D, Specialized / smaller | 12 | MEDIUM | Standard 30-day window |

For Class A, the operator may not realize free credits are being burned until a billing alert fires, at which point thousands of dollars may already have been charged to their commercial API accounts.

---

## Cross-Survey Pattern (updated)

| Platform | Sample | Unauth |
|---|---|---|
| Qdrant | 61 | 100% |
| ChromaDB | 48 | 100% |
| Milvus | 33 | 100% |
| Triton | 2 | 100% |
| **vLLM / OpenAI-compat** | **44** | **100%** |

The pattern is now overwhelming: every layer of the modern AI stack we have surveyed, vector DB, model-serving, LLM-inference proxy, ships with no authentication and most operators do not enable it.

---

## Remediation

### vLLM / vLLM-class servers

```bash
# Start vLLM with API key required
vllm serve <model> --api-key <strong-random-token>

# Or front it with an auth-enforcing reverse proxy:
# Caddy/Nginx with HTTP Basic auth or JWT validation in front of port 8000
```

Firewall port 8000 to the application backend's CIDR.

### Reseller-proxy class

These operators are running a thin OpenAI-API-compatible router in front of paid commercial accounts. Most such routers (LiteLLM, OpenRouter-self-host, OneAPI) support API-key auth via configuration; the operator has not enabled it. Enabling auth + rotating any compromised commercial-API credentials is the immediate fix; longer-term, putting the proxy behind a customer-facing gateway with per-customer rate-limiting is the architectural fix.

---

## Disclosure Posture

The 10 Class-A reseller proxies are time-sensitive, every hour they remain open is more billable spend on the operator's commercial-API accounts. Disclosure should target the operators directly via WHOIS / brand-domain pivots where possible, with DigitalOcean / Hetzner / Vultr abuse channels as fallback.

The 10 Class-B operator-attributed fine-tunes have identifiable upstream operators (sipgate, Infomaniak, Red Hat AI deployment customer), direct disclosure to those organizations' security teams is the highest-bandwidth path.

NuClide is not opening 44 individual disclosure threads. Same-day priority is the Class-A reseller proxies (financial bleed) and the Class-B sipgate / Infomaniak findings (operator-attributable IP exposure).

---

## NuClide Pipeline Artifacts

| Stage | Notes |
|---|---|
| Discovery | Reused 22,765 port-8000 IPs from chromadb-cloud-survey-2026-05 |
| Fingerprint | `vllm-probe.py`, 200-thread `/v1/models` body-match + `/version` + `/metrics` |
| Findings ledger | To be ingested into `data/nuclide.db` via VisorLog |
| What was NOT done | No `/v1/chat/completions` calls, no inference performed against any operator's compute |

---

## References

- vLLM authentication: https://docs.vllm.ai/en/latest/serving/openai_compatible_server.html#api-key
- OpenAI-compatible API spec: https://platform.openai.com/docs/api-reference
- Cross-survey index: [index.md](index.md)
