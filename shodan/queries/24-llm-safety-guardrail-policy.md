# 24. LLM Safety / Guardrails / Policy Engines / Moderation

_Section created: 2026-05-19. Companion to [§23](23-ai-safety-eval.md) (eval / red-team self-hosted). This section covers the **guardrail and policy** layer that sits in front of / after LLM calls, plus content-moderation platforms used as conversational safety filters._

The category is split by deployment mode:

| Subclass | Examples | Deployment mode | Shodan visibility |
|---|---|---|---|
| **LLM-native guardrails (self-hostable)** | Guardrails AI, NeMo Guardrails, Lakera Guard self-hosted, LlamaGuard (deployed via TGI/vLLM/Ollama), Garak REST | Self-hosted HTTP server | Direct, T1/T2 |
| **General-purpose policy engines** | Open Policy Agent (OPA) on port 8181, Styra DAS Edge agent | Self-hosted HTTP server | Direct, T2 |
| **LLMOps / observability with safety dimension** | W&B Weave, Humanloop, Gantry (now shut down), LangSmith (caller-side) | SaaS-mostly | Indirect (caller-side dorks against apps using them) |
| **Content moderation (pre-LLM-era, now used as filters)** | Spectrum Labs, ActiveFence, Two Hat (Microsoft), Hive Moderation | SaaS-only | Indirect (caller-side dorks against apps using them) |
| **AI governance / red-team commercial** | CalypsoAI, Protect AI, HiddenLayer, Robust Intelligence | SaaS-mostly | Indirect (caller-side dorks against customer-deployed apps) |

**Methodology lesson from §23 (carried forward):** Single-word substring matching on response bodies (`"garak"`, `"guardrails"`, `"weave"`) fires on Japanese anime filenames, common English words, and unrelated platforms at population scale. **Conjunctive matching required.** Every query below uses `http.html` / `http.title` scoping; bare-string dorks are documented but starred as `(noisy)`.

---

## 1. LLM-Native Guardrails (self-hostable)

### Guardrails AI (`guardrails serve`)

The open-source guardrails-ai package ships a server mode. Default port 8000. Validates LLM output against operator-defined "guards" (Pydantic-style contracts).

| Shodan Query | Notes |
|---|---|
| `http.html:"guardrails ai"` | Product-name body match. Verified 2026-05-19: 6 hits. |
| `http.html:"/guards"` | Endpoint path. 1,048 hits — **noisy** (matches any `/guards/` UI route in any app). Use as candidate set; verify via `/api/guards` response shape (JSON array). |
| `http.html:"validate_using_guards"` | Package-specific helper string. |
| `http.html:"guardrails-api"` | Alternative package identifier. |
| `port:8000 "guardrails"` | Port + bare string (noisy). |
| `hostname:"guardrails"` | rDNS pattern. |
| `ssl.cert.subject.cn:"guardrails"` | TLS cert CN. |

**Stage 2 verify probe:** `GET /api/guards` returns JSON array of guard definitions when present. `GET /openapi.json` returns FastAPI schema with `/guards` route family. Both confirm Guardrails AI server vs the `/guards/` noise class.

### NeMo Guardrails (NVIDIA)

`nemoguardrails server` default port 8000. CLI-dominant ecosystem; rare in HTTP-server mode.

| Shodan Query | Notes |
|---|---|
| `http.html:"nemo-guardrails"` | Package identifier in source. Verified 2026-05-19: 3 hits. |
| `http.html:"/v1/rails/configs"` | NeMo rails-config endpoint path. Was 0 hits 2026-05-19 (rare deployment). |
| `http.html:"/v1/rails/generate"` | NeMo rails-generate endpoint. |
| `"NeMo Guardrails"` | Product-name any-field (noisy). |
| `hostname:"guardrails"` | rDNS pattern (shared with Guardrails AI; verify with platform-specific probe). |

**Stage 2 verify probe:** `GET /v1/rails/configs` returns JSON array of rail names. aimap fingerprint already present.

### Lakera Guard (self-hosted variant)

Lakera's commercial product is API-only; the self-hosted variant ships a `Server: lakera` header.

| Shodan Query | Notes |
|---|---|
| `Server: lakera` | Header-based; high precision when matched. Verified 2026-05-19: 1 hit. |
| `http.html:"lakera-guard"` | Body marker. Verified 2026-05-19: 8 hits. |
| `http.html:"/v1/guard"` | Lakera guard endpoint path. |
| `http.html:"prompt-injection-attack"` | Detection category name in Lakera responses. |
| `ssl.cert.subject.cn:"lakera"` | TLS cert CN. |
| `hostname:"lakera"` | rDNS pattern. |

**Stage 2 verify probe:** `POST /v1/guard` with empty body should return Lakera-specific error response. aimap fingerprint already present.

### LlamaGuard (Meta — deployed via TGI / vLLM / Ollama)

LlamaGuard is a model, not a server. Discovery via the underlying inference server's `/v1/models` response.

| Shodan Query | Notes |
|---|---|
| `http.html:"Llama-Guard"` | Model name in HTML response. Was 0 hits 2026-05-19 (Shodan indexes JSON `/v1/models` responses sparsely). |
| `http.html:"meta-llama/Llama-Guard-3"` | Hugging Face model ID variant. |
| `http.html:"LlamaGuard"` | Camel-case variant. |
| `http.html:"unsafe_categories"` | LlamaGuard taxonomy term. |

**Side-channel discovery (recommended):** re-query past LLM-Gateway surveys' `/v1/models` outputs for `Llama-Guard` model name. The model is server-agnostic; deployment population surfaces in already-harvested LLM-Gateway corpora more efficiently than via Shodan.

### Garak REST (NVIDIA adversarial harness)

See [§23](23-ai-safety-eval.md). CLI-dominant; 0 confirmed at population scale 2026-05-04.

---

## 2. General-Purpose Policy Engines

### Open Policy Agent (OPA)

The dominant general-purpose policy engine. `opa run -s` ships an HTTP server on port 8181 by default. Used as the central policy layer in K8s, microservice meshes, and increasingly AI tool-use authorization.

| Shodan Query | Notes |
|---|---|
| `port:8181 http.status:200` | OPA default port; broad. Use with body filter. |
| `http.html:"/v1/policies"` | OPA REST API endpoint. |
| `http.html:"/v1/data"` | OPA data API. |
| `port:8181 "opa"` | Port + bare string (noisy). |
| `http.title:"OPA"` | Title-based; rare since OPA has no UI by default. |
| `product:"Open Policy Agent"` | Shodan product tag if indexed. |
| `hostname:"opa"` | rDNS pattern. |
| `ssl.cert.subject.cn:"opa"` | TLS cert CN. |

**Stage 2 verify probe:** `GET /v1/policies` returns JSON array of policy IDs. `GET /v1/data` returns JSON of policy data tree. Either confirms OPA + reveals operator-authored policy structure.

**Risk class:** policy data may include role assignments, allowed-action lists, tenant routing rules, AI-API quota policies. Reading `/v1/data` is read-only — but the policy structure itself is sensitive.

### Styra DAS Edge agent

Commercial OPA distribution. Self-hosted edge agent reports to a SaaS control plane.

| Shodan Query | Notes |
|---|---|
| `http.html:"styra"` | Vendor-name body match. |
| `http.html:"styra-das"` | Product identifier. |
| `port:8181 http.html:"styra"` | OPA-port + Styra wrapper. |

---

## 3. LLMOps / Observability with Safety Dimension

These platforms blend evaluation, tracing, and policy-style guardrails. SaaS-mostly, but visibility through caller-side dorks.

### W&B Weave (Weights & Biases)

LLM-call tracing with quality / safety gates. Hosted at `wandb.ai/weave`; some self-hosted exposure exists.

| Shodan Query | Notes |
|---|---|
| `http.html:"wandb.ai/weave"` | Caller-side: apps that embed the W&B Weave dashboard URL. |
| `http.html:"weave-python"` | Package identifier. |
| `http.html:"weave-trace"` | Trace identifier in HTML. |
| `http.html:"weave_server"` | Server-mode identifier. |
| `http.html:"/weave/"` | Path-based; noisy (any app with `/weave/` route). Verified 2026-05-19: 1,032 hits — high FP suspicion. |
| `http.html:"wandb-weave"` | Package alternate. |

**Caller-side discovery:** customer apps that mention W&B Weave in their HTML reveal which orgs are using it for LLM observability — useful for population mapping of the observability tier.

### Humanloop

LLM app development with feedback loops + guardrail-like evaluation criteria. SaaS-primary.

| Shodan Query | Notes |
|---|---|
| `http.html:"humanloop"` | Vendor-name body match. |
| `http.html:"app.humanloop.com"` | Caller-side: apps embedding Humanloop dashboard URL. |
| `http.html:"humanloop-python"` | Package identifier. |
| `ssl.cert.subject.cn:"humanloop"` | TLS cert CN. |

### Gantry

Observability + quality + safety policies for ML/LLM. **Note: company shut down 2024**; queries here for historical/forensic discovery only.

| Shodan Query | Notes |
|---|---|
| `http.html:"gantry.io"` | Vendor-domain body match. |
| `http.html:"app.gantry.io"` | Caller-side dashboard URL. |
| `http.title:"Gantry"` | **Noisy** — gantry is a real word (shipping/manufacturing). Verified 2026-05-19: 44 hits, most unrelated. |
| `http.html:"/gantry-"` | Path prefix. **Noisy** — 2,229 hits 2026-05-19, mostly unrelated. |

### LangSmith (LangChain observability + eval)

See [§5 / §23](23-ai-safety-eval.md). Already documented; carried here for cross-reference.

---

## 4. Content Moderation (pre-LLM-era, now used as filters)

SaaS-only platforms. Visibility through caller-side dorks — find apps that integrate them.

### Spectrum Labs

| Shodan Query | Notes |
|---|---|
| `http.html:"spectrumlabsai.com"` | Caller-side. |
| `http.html:"spectrum-labs"` | Package / API identifier. |

### ActiveFence

| Shodan Query | Notes |
|---|---|
| `http.html:"activefence.com"` | Caller-side. |
| `http.html:"activefence-api"` | API identifier. |

### Two Hat (Microsoft Azure Content Safety)

Two Hat acquired by Microsoft; now integrated into Azure Content Safety.

| Shodan Query | Notes |
|---|---|
| `http.html:"twohat.com"` | Caller-side (legacy). |
| `http.html:"contentsafety.cognitive.microsoft.com"` | Azure Content Safety endpoint (caller-side). |

### Hive Moderation

| Shodan Query | Notes |
|---|---|
| `http.html:"hivemoderation.com"` | Caller-side. |
| `http.html:"thehive.ai"` | Vendor domain. |
| `http.html:"hive-api"` | API identifier. |

---

## 5. AI Governance / Red-Team Commercial

SaaS-mostly; caller-side dorks find customer-deployed apps that integrate them.

### CalypsoAI

| Shodan Query | Notes |
|---|---|
| `http.html:"calypsoai.com"` | Caller-side. |
| `http.html:"calypso-ai"` | Vendor identifier. |

### Protect AI

Multi-product: Recon, Sightline, Guardian, ModelScan.

| Shodan Query | Notes |
|---|---|
| `http.html:"protectai.com"` | Caller-side. |
| `http.html:"protect-ai"` | Vendor identifier. |
| `http.html:"modelscan"` | ModelScan CLI / report identifier. |
| `http.html:"sightline"` | Sightline product identifier. |
| `http.html:"guardian"` | Generic; needs Protect-AI co-occurrence to disambiguate. |

### HiddenLayer

| Shodan Query | Notes |
|---|---|
| `http.html:"hiddenlayer.com"` | Caller-side. |
| `http.html:"hiddenlayer-ai"` | Vendor identifier. |

### Robust Intelligence

| Shodan Query | Notes |
|---|---|
| `http.html:"robustintelligence.com"` | Caller-side. |
| `http.html:"robust-intelligence"` | Vendor identifier. |
| `http.html:"robust-ai"` | Alternate identifier. |

---

## 6. Cross-Category Caller-Side Discovery

Apps that reference SaaS safety platforms in their HTML / JS bundles reveal the **deployment population of the SaaS safety layer** without requiring access to the SaaS itself. Useful for mapping which orgs use which guardrails.

**Pattern:** combine vendor-domain in HTML with a customer-identifying signal.

```
http.html:"lakera.ai" http.html:"customer"
http.html:"openai.com/v1/moderations" http.html:"production"
http.html:"calypsoai.com" http.html:"login"
```

**Caveat:** caller-side discovery surfaces customers, not exposures. The customer's own AI infrastructure may still need separate discovery via §1 / §22 / etc.

---

## Tier System (this section)

| Subclass | Default tier | Population deployment shape |
|---|---|---|
| Guardrails AI server | T2 (auth optional) | Rare; CLI-dominant ecosystem |
| NeMo Guardrails server | T2 | Rare; CLI-dominant |
| Lakera Guard self-hosted | T1 (no auth default on self-host variant) | Rare; commercial product mostly SaaS |
| LlamaGuard via TGI/vLLM/Ollama | A (no auth concept on the underlying server) | Counted within §3 model-serving |
| OPA on 8181 | T1 (default config has no auth on REST API) | Common in K8s; rare on public internet |
| W&B Weave / Humanloop / Gantry | n/a (SaaS) | Caller-side dorks only |
| Content moderation SaaS | n/a (SaaS) | Caller-side dorks only |
| AI governance commercial | n/a (SaaS) | Caller-side dorks only |

---

## See also

- [§5 Gateways / Monitoring](05-gateways-monitoring.md): LangSmith / Helicone / Langfuse / Phoenix
- [§23 AI Safety Evaluation / Red-Team Self-Hosted](23-ai-safety-eval.md): Promptfoo / DeepEval / Garak / LangSmith / NeMo Guardrails (eval angle)
- [`methodology/insight-06-conjunctive-matchers-required.md`](../../methodology/insight-06-conjunctive-matchers-required.md): Why every safety-category dork above uses `http.html` / `http.title` scoping rather than bare-string matches
- [`methodology/insight-33-side-channel-attribution-via-registry-catalog.md`](../../methodology/insight-33-side-channel-attribution-via-registry-catalog.md): Caller-side dorks for SaaS safety platforms are an instance of the same principle applied at the application layer rather than the registry layer
