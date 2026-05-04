# Ollama on Tier-2 Cloud — Auth Posture Survey (Scope Expansion)

_NuClide Research · 2026-05-04_
_Companion to: [`ollama-cloud-survey-2026-05.md`](ollama-cloud-survey-2026-05.md) (DO/Hetzner/Vultr baseline)_

---

## Summary

Mass-scan of port 11434 (Ollama default) across **76 cloud /16 ranges spanning Scaleway, OVH, and Linode** — three tier-2 budget clouds outside the original DO/Hetzner/Vultr baseline. **3.55 million IPs scanned → 7,335 port-open candidates → 1,019 confirmed unauthenticated Ollama instances**.

The expansion confirms the auth-off-default thesis is **operator-culture-independent**:

| Cloud | Audience | /16-class ranges | IPs scanned | Unauth Ollama | Density (per M IPs) |
|---|---|---|---|---|---|
| DO/Hetzner/Vultr (baseline) | US/EU mixed | 28 | 1,830,000 | 342 | 187 |
| **Scaleway** | French | 7 | 425,984 | 46 | 108 |
| **OVH** | French/Canadian | 33 | 1,961,984 | 714 | **364** |
| **Linode (Akamai)** | US-anchored global | 36 | 1,162,240 | 259 | 223 |
| **Tier-2 combined** | — | **76** | **3,550,208** | **1,019** | **287** |

OVH alone has roughly the same number of unauth Ollama instances as the entire DO/Hetzner/Vultr baseline times two. The thesis (Ollama framework has no auth concept; operators who put it on the public internet are exposed by default) reproduces cleanly across French, Canadian, and Akamai-anchored populations.

The novel findings extend the original survey:

1. **`:cloud` billing-fraud surface scales linearly.** Across tier-2 clouds, **471 of 1,019 unauth Ollama hosts (46.2%) have at least one `:cloud`-suffix model loaded** — every external prompt against those hosts spends the operator's Ollama Cloud subscription. Top exposures: `minimax-m2.7:cloud` (358 hosts), `deepseek-v4-pro:cloud` (289), `kimi-k2.6:cloud` (68), `qwen3-coder-next:cloud` (66). 22 hosts carry `gemini-3-flash-preview:cloud` — Google Gemini routed through Ollama Cloud, billing back to Google's API contract on the operator's account.

2. **Linode hosts a 197-host frozen-marketplace-template cluster.** Identical signature: Ollama 0.1.33 + identical 5-model loadout (`deepseek-r1:latest`, `llama3:8b-text-q4_K_S`, `qwen:latest`, `llama3:latest`, `mistral:latest`). 197 instances spread across 7 Linode /16s, all running the same one-click Marketplace App template, none upgraded since the Feb 2024 build. None of them have `:cloud` exposure (predates the feature) — but each is a 5-model inference endpoint anyone can drive at the operator's compute cost.

3. **Abliterated/uncensored finetune ecosystem visible at population scale.** 20 unique safety-rail-removed finetunes across the tier-2 surface, including:
   - `huihui_ai/qwen3.5-abliterated:122B` (122B-param abliterated Qwen)
   - `charaf/gemma4-31b-claude-opus-abliterated:latest`
   - `zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2-GGUF:latest`
   - `vaultbox/qwen3.5-uncensored:35b`
   - `frob/mradermacher-Llama3.3-8B-Thinking-Heretic-Claude-4.5-Opus:q8_0`

   These are operators who have *specifically* selected uncensored variants and made them anonymously queryable. The exposure isn't accidental in the same way an admin panel is — these operators want the model running unrestricted, they just left it open to the internet too.

---

## Methodology

```
masscan -iL <76 tier-2 cloud /16 CIDRs> -p 11434 --rate 10000

Scaleway  → 7 prefixes,  425,984 IPs → 111 port-open
OVH       → 33 prefixes, 1,961,984 IPs → 5,341 port-open
Linode    → 36 prefixes, 1,162,240 IPs → 1,883 port-open
TOTAL     → 76 prefixes, 3,550,208 IPs → 7,335 port-open

ollama-probe.py (200-thread fingerprint)
  GET /            → text "Ollama is running" (canonical signature)
  GET /api/version → version JSON
  GET /api/tags    → loaded model list with size, quantization, family
  → 1,019 confirmed Ollama instances
```

Same probe script as the DO/Hetzner/Vultr baseline. Read-only metadata enumeration only — no `/api/generate`, no `/api/chat`, no `/api/embeddings`. Submitting an inference request would have spent the operator's compute (and for `:cloud` models, the operator's Ollama Cloud quota).

Confirm rate (Ollama / port-open):
- Scaleway: 41.4% (46/111) — high, suggests cleaner port allocation discipline
- OVH: 13.4% (714/5,341) — many port-11434 hits are non-Ollama (filtered, honeypot, other service)
- Linode: 13.8% (259/1,883)

---

## Findings Summary

| Metric | Value |
|---|---|
| Tier-2 /16 ranges scanned | 76 |
| Total IPs scanned | 3,550,208 |
| Masscan hits on :11434 | 7,335 |
| Ollama confirmed | **1,019** |
| Unauthenticated | **1,019 (100%)** — by design |
| Fresh installs (0 models) | 21 |
| Active deployments (≥1 model) | 998 |
| Median model count per host | 5 |
| Max model count observed | 46 |
| Instances loading at least one `:cloud` model | **471 (46.2%)** |
| Unique abliterated/uncensored finetunes | 20 |
| Frozen-template cluster (Linode 0.1.33) | 197 |

---

## Top Exposed `:cloud` Models (Operator Billing-Fraud Surface)

Every external prompt against these endpoints spends the operator's Ollama Cloud quota:

| Model | Tier-2 hosts exposed | Notes |
|---|---|---|
| `minimax-m2.7:cloud` | **358** | MiniMax M2.7 — Chinese long-context reasoning model |
| `deepseek-v4-pro:cloud` | **289** | DeepSeek V4 Pro — top-of-stack DeepSeek inference |
| `kimi-k2.6:cloud` | 68 | Moonshot Kimi K2.6 |
| `qwen3-coder-next:cloud` | 66 | Alibaba Qwen3-Coder (next-gen) |
| `glm-5.1:cloud` | 33 | Zhipu GLM-5.1 |
| `deepseek-v3.2:cloud` | 29 | DeepSeek V3.2 |
| `kimi-k2.5:cloud` | 24 | Moonshot Kimi K2.5 |
| `deepseek-v4-flash:cloud` | 22 | DeepSeek V4 Flash |
| **`gemini-3-flash-preview:cloud`** | **22** | **Google Gemini 3 Flash via Ollama Cloud — bills the operator's GCP/Google API contract** |
| `glm-5:cloud` | 22 | Zhipu GLM-5 |
| `minimax-m2.5:cloud` | 21 | MiniMax M2.5 |
| `glm-4.6:cloud` | 20 | Zhipu GLM-4.6 |
| `glm-4.7:cloud` | 20 | Zhipu GLM-4.7 |
| `kimi-k2-thinking:cloud` | 20 | Moonshot Kimi K2 Thinking |
| `minimax-m2.1:cloud` | 20 | MiniMax M2.1 |

**Aggregate**: 1,034 distinct `:cloud`-host-model bindings across 471 hosts. The most-exposed pair (MiniMax M2.7) means an attacker with a 30-second curl loop can drain the quota of any of 358 unauthenticated operators.

---

## Linode Frozen-Marketplace Cluster

197 of the 259 Linode unauth Ollama instances (76%) match an identical signature:

```
Ollama version: 0.1.33   (Feb 2024 release)
Models (always exactly these 5):
  - deepseek-r1:latest
  - llama3:8b-text-q4_K_S
  - qwen:latest
  - llama3:latest
  - mistral:latest
```

Spread across multiple Linode /16s (`103.3.x`, `109.74.x`, `139.144.x`, etc.) — not a single tenant. The signature matches Linode's official **Ollama Marketplace App** template's default-model set. Hypothesis: 197 customers spun up the one-click Ollama deployment, never upgraded, and never enforced authentication at the network layer.

This cluster shows **two failure modes simultaneously**:
1. **Marketplace template defaults expose customers.** Linode's template doesn't ship an auth proxy or firewall rule. Customers assume the marketplace one-click is "production-ready"; it isn't.
2. **Operator behavior is "deploy-and-forget."** None of the 197 templates have been upgraded in ~14 months. Each one is also running an unpatched 0.1.33 with whatever upstream Ollama bugs that build carries.

The 197 Linode hosts predate the Ollama Cloud feature, so they have **zero `:cloud`-billing exposure** — but each one is still a 5-model inference endpoint anyone on the internet can drive at the operator's per-hour Linode compute cost. Probable abuse vector: cryptominers and automated scrapers running inference for free.

---

## Abliterated / Uncensored Finetunes (Tier-2 Surface)

These are operator-curated safety-rail-removed models. The operator selected them deliberately. They are also exposed unauth.

| Model | Description |
|---|---|
| `huihui_ai/qwen3.5-abliterated:122B` | 122B-param abliterated Qwen 3.5 |
| `huihui_ai/Qwen3.6-abliterated:35b` | 35B abliterated Qwen 3.6 |
| `huihui_ai/deepseek-r1-abliterated:32b` | Abliterated DeepSeek R1 |
| `huihui_ai/qwen3.5-abliterated:4B` / `:2b` | Smaller abliterated Qwen variants |
| `huihui_ai/qwen2.5-abliterate:0.5b` | 0.5B abliterated Qwen 2.5 |
| `hf.co/huihui-ai/Huihui-granite-4.1-3b-abliterated:BF16` | Abliterated IBM Granite |
| `charaf/gemma4-31b-claude-opus-abliterated:latest` | Abliterated Gemma 4 31B (Claude-Opus distilled) |
| `gemma4-26b-abliterated:latest` | 26B Gemma 4 abliterated |
| `gemma4-uncensored:latest` | Gemma 4 uncensored |
| `gemma4-e4b-heretic:latest` | Gemma 4 e4b "heretic" finetune |
| `juilpark/gemma-4-31B-it-uncensored-heretic:q4_k_m` | Gemma 4 31B uncensored "heretic" |
| `hf.co/Andycurrent/Gemma-3-4B-VL-it-Gemini-Pro-Heretic-Uncensored-Thinking_GGUF:Q4_K_M` | Vision-language Gemma 3 uncensored "heretic" |
| `Hudson/llama3.1-uncensored:8b` | Llama 3.1 uncensored |
| `vaultbox/qwen3.5-uncensored:35b` | 35B uncensored Qwen 3.5 |
| `hf.co/SpaceTimee/Suri-Qwen-3.5-9B-Uncensored-GGUF:Q8_0` | 9B uncensored Qwen 3.5 |
| `hf.co/Ex0bit/Elbaz-Olmo-3-7B-Instruct-abliterated:latest` | Abliterated AI2 OLMo 3 |
| `hf.co/bartowski/Qwen2.5-Coder-7B-Instruct-abliterated-GGUF:Q5_K_M` | Abliterated Qwen 2.5 Coder |
| `frob/mradermacher-Llama3.3-8B-Thinking-Heretic-Claude-4.5-Opus:q8_0` | Llama 3.3 "heretic" Opus-distilled |
| `zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2-GGUF:latest` | Uncensored Opus-distilled coding model |

The pattern across the tier-2 surface: **abliterated/uncensored models are concentrated on OVH** (operators who chose OVH for low-cost GPU + low-policy-friction hosting), with a smaller cluster on Linode. Scaleway shows only one example (`rnj-1:8b`) — likely because the Scaleway operator population skews toward enterprise/SaaS tenants who use the standard model stack.

---

## Cross-Cloud Comparison (vs. DO/Hetzner/Vultr baseline)

| Metric | DO/Hetzner/Vultr | Scaleway | OVH | Linode | Tier-2 total |
|---|---|---|---|---|---|
| /16 ranges | 28 | 7 | 33 | 36 | 76 |
| IPs scanned | 1.83M | 426K | 1.96M | 1.16M | 3.55M |
| Unauth Ollama | 342 | 46 | 714 | 259 | 1,019 |
| Density per M IPs | 187 | 108 | **364** | 223 | 287 |
| `:cloud` exposure rate | 50.3% | 50.0% | **59.4%** | 9.3% | 46.2% |
| Median models / host | 4 | (sm) | (sm) | 5 | 5 |
| Max models / host | 28 | — | — | — | 46 |

**Headline numbers across both surveys combined:**

- **1,361 unauthenticated Ollama instances** across 5.38M cloud IPs scanned
- **643 instances** loading at least one `:cloud` model (operator-quota-theft surface)
- **42+ unique abliterated/uncensored finetunes** anonymously queryable
- **0 surveys returned an authenticated Ollama instance** — the framework cannot enforce auth, and no operator in the survey deployed a reverse-proxy auth layer

The auth-on-default thesis (from the cross-survey synthesis paper) holds without exception: Ollama is in the **"auth concept doesn't exist in the framework"** tier, alongside vector DBs, MLflow, and pre-2.x inference servers. Operators who put it on the public internet are exposed.

---

## Auth-On-Default Tier Map (Updated)

| Tier | Auth in framework default | Surveyed deployments | Unauth rate observed |
|---|---|---|---|
| **A — No auth concept** | No | 1,361 Ollama, 151 Qdrant, 32 Milvus, 33 MLflow, 313 Elasticsearch | 100% |
| **B — Auth optional, off by default** | Off | 1,432 ChromaDB, 47 Mem0, 178 Triton, 122 vLLM | 100% |
| **C — Setup wizard / first-run takeover** | First user wins | Dify (5 takeable / 100s deployed) | <5% |
| **D — Auth on by default** | On | 852 MinIO, OpenWebUI, n8n, Flowise | 0% (all bounced) |

The original survey's hypothesis that **"auth-on-default is load-bearing"** holds. The Linode marketplace cluster adds a fifth observation: **template defaults that ship without auth are functionally equivalent to having no auth concept**, regardless of which tier the underlying framework is in. Linode's Ollama template inherits Ollama's "no auth concept" framework, but the failure mode is platform-mediated (197 customers, one template, one default).

---

## Disclosure Posture

The aggregate exposure (1,019 unauth instances, 471 cloud-billing-exposed, 197-host marketplace cluster, 20+ uncensored finetunes) is too large for per-host disclosure. NuClide's posture:

1. **No per-host abuse reports** — the framework has no auth, the operators chose to deploy unauth on the public internet. Per-host disclosure load would scale to thousands of emails with no fix path beyond "add a firewall rule."

2. **Platform-level disclosure to Linode** for the 197-host marketplace cluster — the template default is the systemic issue. Linode can update the marketplace App to ship with `OLLAMA_HOST=127.0.0.1` + a proxy auth layer, and that single change patches all current and future deployments.

3. **Ollama upstream awareness** — the `:cloud` model billing-fraud surface is a framework-level design issue. Loading a `:cloud` model on an unauth Ollama instance creates a quota-theft endpoint; the framework should require local auth before allowing `:cloud` model registration. Disclosure draft pending.

4. **Aggregate publication** — this case study is the public-facing record. Operators who find their IP listed in the supplementary data can apply the fix (firewall rule, reverse proxy with auth, or `OLLAMA_HOST=127.0.0.1`).

---

## Raw Data

Per-host JSONL with version + model list + flags — for VisorLog ingest:

```
~/recon/ollama-tier2-2026-05-04/scaleway-ollama-confirmed.jsonl  (46 hosts)
~/recon/ollama-tier2-2026-05-04/ovh-ollama-confirmed.jsonl        (714 hosts)
~/recon/ollama-tier2-2026-05-04/linode-ollama-confirmed.jsonl     (259 hosts)
```

Each record:
```json
{
  "ip": "...",
  "port": 11434,
  "service": "Ollama",
  "version": "0.x.x",
  "models": [{"name": "...", "size": ..., "family": "...", "param_size": "...", "quantization": "..."}],
  "model_count": N
}
```

---

## See Also

- [`ollama-cloud-survey-2026-05.md`](ollama-cloud-survey-2026-05.md) — DO/Hetzner/Vultr baseline (28 /16s, 342 instances)
- [`SYNTHESIS-2026-05.md`](SYNTHESIS-2026-05.md) — cross-survey synthesis paper (auth-on-default thesis, positive controls, active-attack evidence)
