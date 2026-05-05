# LLM Gateways / OpenAI-Compatible Proxies — Cross-Cloud Survey (2026-05)

_NuClide Research · 2026-05-04 (in progress)_

> **Status:** Methodology + scaffolding complete. Discovery scan queued behind the MCP cross-cloud pass. Synthesis section will fill as data lands.

---

## Premise

LLM gateway / OpenAI-compat proxy products sit between LLM applications and upstream providers. They normalize multiple provider APIs (Anthropic, OpenAI, Cohere, Together, etc.) behind a single OpenAI-compatible interface, frequently with provider keys baked into operator configuration. When exposed without authentication, they are **direct quota-theft and reseller-proxy primitives**: an attacker hitting `/v1/chat/completions` consumes the operator's upstream credit at scale.

This survey extends the **vLLM cross-cloud finding** (`vllm-cloud-survey-2026-05.md`) — which documented 10 commercial-API reseller proxies burning operator credit in the vLLM survey — into the broader gateway-product class. Different operator tier, same auth-failure pattern.

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

Skip 7860 (already surveyed by gradio survey) and 8000 (already surveyed by vLLM survey — its OpenAI-compat populations are documented there). The 3000 / 8080 ports collide heavily with other AI platforms (MCP, Open WebUI, n8n, ChromaDB v8080-mode); platform identification relies on **response signatures**, not port alone.

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

- **AS63949 honeypot fleet** — apply standard filter (393 hosts at `~/recon/ollama-tier2-2026-05-04/as63949-honeypot-fleet.txt`).
- **vLLM cross-survey overlap** — `try_generic_openai_compat` excludes any `/v1/models` response that has `owned_by: "vllm"` (those belong to the vLLM survey).
- **Auth-required instances** — record presence with `auth_required: true` but exclude from "exposed-models" enumeration.

### Threat-class taxonomy

Per confirmed unauth instance:

| Class | Examples | Severity |
|---|---|---|
| **Provider-key quota theft** | LiteLLM with OpenAI/Anthropic/Cohere/Bedrock keys; OneAPI with channel-managed keys | HIGH — direct billing impact |
| **Reseller proxy** | LiteLLM/OneAPI fronting paid commercial accounts for downstream customers (operator's revenue stream); attacker hits the same endpoint freely | HIGH — same as quota theft + competitive impact |
| **Self-host inference** | LM Studio / Jan AI / oobabooga running a single local GGUF/safetensors model; no provider keys | MEDIUM — compute-theft only |
| **Custom fine-tune exposure** | Operator's proprietary fine-tune accessible unauth | MEDIUM-HIGH — IP exfil |
| **Admin UI access** | OneAPI/NewAPI admin panel reachable, default creds present | HIGH — full proxy reconfiguration |

---

## Discovery results

_(populated as the masscan + probe pipeline completes)_

| Source | Hits | Confirmed | Auth-on | Auth-off |
|---|---|---|---|---|
| Scaleway tier-2 | TBD | TBD | TBD | TBD |
| OVH tier-2 | TBD | TBD | TBD | TBD |
| Linode tier-2 | TBD | TBD | TBD | TBD |
| **Total unique** | TBD | TBD | TBD | TBD |

### By platform

| Platform | Confirmed | Median model count | Notable owned_by tags |
|---|---|---|---|
| LiteLLM Proxy | TBD | TBD | TBD |
| LocalAI | TBD | TBD | TBD |
| oobabooga | TBD | TBD | TBD |
| LM Studio | TBD | TBD | TBD |
| Jan AI | TBD | TBD | TBD |
| OneAPI / NewAPI | TBD | TBD | TBD |
| Generic OpenAI-compat | TBD | TBD | TBD |

---

## Provider-key inventory

For LiteLLM and OneAPI instances where `owned_by` reveals the upstream provider tier, classify by which commercial APIs the operator is fronting:

| Provider | Hosts | Notes |
|---|---|---|
| OpenAI | TBD | TBD |
| Anthropic | TBD | TBD |
| AWS Bedrock | TBD | TBD |
| Google Vertex / Gemini | TBD | TBD |
| Together | TBD | TBD |
| Replicate | TBD | TBD |
| Cohere | TBD | TBD |
| Mistral | TBD | TBD |
| Other | TBD | TBD |

---

## Notable findings

_(populated)_

---

## Cross-reference: vLLM survey

The vLLM cross-cloud survey (`vllm-cloud-survey-2026-05.md`) already documented **10 commercial-API reseller proxies** burning operator credit on every external prompt — Grok2API, Kiro-Go, AgentBar, etc. Those instances served via vLLM-fronted OpenAI-compat endpoints. This survey extends the population to gateway-product instances (LiteLLM, OneAPI, etc.) where the same pattern recurs but at a different operator tier.

The combined "OpenAI-compat reseller proxy" population spans:

- vLLM-fronted (vLLM survey: 10)
- LiteLLM-fronted (this survey: TBD)
- OneAPI-fronted (this survey: TBD)
- Generic-fronted (this survey: TBD)

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

- [`vllm-cloud-survey-2026-05.md`](vllm-cloud-survey-2026-05.md) — vLLM cross-cloud survey (sibling-class, already done)
- [`SYNTHESIS-2026-05.md`](SYNTHESIS-2026-05.md) — companion cross-survey synthesis
- [`FUTURE-SURVEYS.md`](FUTURE-SURVEYS.md) — broader unsurveyed roadmap
- [`data/llm-gateway-probe.py`](../../data/llm-gateway-probe.py) — multi-platform fingerprint prober used for this survey
