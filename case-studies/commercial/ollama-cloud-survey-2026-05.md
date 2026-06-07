---
type: survey
---

# Ollama on Public Cloud: Auth Posture Survey

_NuClide Research · 2026-05-03_

---

## Summary

Mass-scan of port 11434 (Ollama's default) across 28 cloud-provider /16 ranges (DO/Hetzner/Vultr) → 882 hits → **342 confirmed Ollama instances**, all **unauthenticated** (Ollama has no authentication concept, the framework does not implement auth). 8 are fresh installs with 0 models loaded; the other 334 are running real workloads with 1-28 models per host.

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7004, K7044, S7068, S7070, S7075, T5904
- **733 (AI Risk & Ethics Specialist):** K7040, T5854, T5868, T5893
- **overlap (Common AI KSATs (all 5 roles)):** K108, K1158, K1159, K22, K6311, K6900, K6935, K7003, K7024, S7065

<!-- ksat-tag:auto-generated:end -->

The novel findings here are not the unauth state itself (Ollama-on-public-internet ≡ Ollama-unauth, by design). The novel findings are:

1. **Operator paid-quota theft via `:cloud`-suffix models.** Ollama's recent cloud-models feature lets operators register against an Ollama Cloud subscription and serve giant models (Kimi K2.6, Qwen3-coder-next, DeepSeek-v3.1:671b, MiniMax-m2.7, Devstral-2:123b) routed through Ollama's infrastructure but paid against the operator's account. **172 instances in the survey have at least one `:cloud` or `:cloud`-class model loaded**, every external prompt against those routes to the cloud and bills the operator.

2. **22+ abliterated/uncensored models** exposed unauth, including the well-known `huihui_ai/*-abliterated` family, `Llama-3.1-8B-Lexi-Uncensored-V2`, and `Qwen3.5-9B-Claude-4.6-Opus-Uncensored-Distilled`. These are safety-rail-removed models that operators have specifically chosen for their lack of guardrails. Anyone on the internet can query them.

3. **The single most popular model is `llama3.2:3b` (199 instances)**, the small, fast, ubiquitous default. The Ollama operator population skews heavily toward "running a small Llama for personal/internal LLM access," with the longer-tail operators running larger models or specialty fine-tunes.

---

## Methodology

```
masscan -iL <28 cloud /16 CIDRs> -p 11434 --rate 10000
  → 882 port-11434 hits

ollama-probe.py (200-thread fingerprint)
  GET /            → text "Ollama is running" (canonical signature)
  GET /api/version → version JSON
  GET /api/tags    → loaded model list with size, quantization, family
  → 342 confirmed Ollama instances
```

NuClide did not submit any prompt to `/api/generate`, `/api/chat`, or `/api/embeddings`. Inference would have used the operator's compute (and for `:cloud` models, would have spent the operator's Ollama Cloud credits). Model-list enumeration alone is sufficient to characterize the exposure.

---

## Findings Summary

| Metric | Value |
|---|---|
| Cloud /16 ranges scanned | 28 |
| Masscan hits on :11434 | 882 |
| Ollama confirmed | **342** |
| Unauthenticated | **342 (100%)**, by design |
| Fresh installs (0 models) | 8 |
| Active deployments (≥1 model) | 334 |
| Median model count per host | 4 |
| Max model count observed | 28 |
| Instances loading at least one `:cloud` model | 172 |
| Instances loading abliterated/uncensored models | 22+ |

---

## Top Loaded Models

| Model | Instances loaded |
|---|---|
| `llama3.2:3b` | 199 |
| `minimax-m2.7:cloud` | 115 |
| `deepseek-v4-pro:cloud` | 98 |
| `smollm2:135m` | 83 |
| `glm-4.7-flash:latest` | 42 |
| `llama3.2:latest` | 40 |
| `nomic-embed-text:latest` | 36 (embedding model) |
| `qwen3.6:35b` | 30 |
| `qwen2.5:7b` | 20 |
| `llama3:latest` | 19 |
| `qwen3:8b` | 18 |
| `llama3.1:8b` | 18 |
| `bge-m3:latest` | 17 (embedding) |
| `kimi-k2.6:cloud` | 16 |
| `deepseek-v3.1:671b-cloud` | 16 |
| `qwen2.5:3b` | 15 |
| `llama3.2:1b` | 15 |
| `gemma3:latest` | 15 |
| `mistral:latest` | 14 |
| `devstral-2:123b-cloud` | 14 |
| `qwen3-coder-next:cloud` | 12 |

The `:cloud`-suffix models route through Ollama's commercial cloud, they're the same threat class as the Class-A reseller-proxies in the vLLM survey. Every external prompt = operator billing.

---

## Class A: Operator Cloud-Quota Theft (HIGH, broadly distributed)

172 Ollama instances are configured with at least one Ollama Cloud `:cloud` model. The cloud models route each prompt through Ollama Inc's infrastructure and bill against the operator's subscription. Ollama Cloud pricing scales with usage; an operator's exposed instance turns into uncapped billing for any internet attacker who finds it.

The most-loaded cloud models:

| `:cloud` model | Instances | Implied operator subscription size |
|---|---|---|
| `minimax-m2.7:cloud` | 115 | small-to-medium |
| `deepseek-v4-pro:cloud` | 98 | medium |
| `kimi-k2.6:cloud` | 16 | medium-to-large (Kimi is 1T-class) |
| `deepseek-v3.1:671b-cloud` | 16 | large (671B parameters) |
| `devstral-2:123b-cloud` | 14 | medium-to-large (123B) |
| `qwen3-coder-next:cloud` | 12 | medium |

**Risk class:** financial bleed. Same attack pattern as Grok2API/Kiro-Go/AgentBar in the vLLM survey, but on Ollama's commercial cloud rather than OpenAI/Anthropic. Each external prompt against `/api/chat` routes through `ollama-cloud` → operator's bank account.

### Ollama → Claude Desktop bridge (2026-05 threat-model expansion)

Ollama now ships a `claude-desktop` launcher (`ollama launch claude-desktop`) that wires Ollama's cloud models (the same `:cloud` family enumerated above) into Claude Desktop / Claude Cowork / Claude Code as third-party inference providers. The integration extends every unauth Ollama instance into a **two-stage attack surface**:

1. **Operator's Ollama Cloud quota** is consumed by attacker prompts (the original Class A finding)
2. **End-user Claude Desktop sessions** that route through this Ollama instance, when wired up, execute prompts the attacker can poison via the unauth `/api/create` model-injection vector (CVE-2025-63389). The attacker doesn't just steal quota; they poison the model-system-prompt that downstream Claude Desktop callers receive.

**Implication for the existing 172 cloud-loaded instances:** any operator who later flips on the Claude Desktop bridge, or any operator whose Ollama instance is being reached by a Claude Desktop user via shared-network configuration, gains a new severity class on top of the quota-theft path. The attacker can prefix a malicious system prompt onto the cloud model, and the next Claude Desktop session that uses this Ollama relay receives attacker-shaped responses.

**Remediation guidance for operators:** binding to loopback (`OLLAMA_HOST=127.0.0.1:11434`) defeats both Class A (quota theft) and the new Class A* (Claude Desktop bridge poisoning). The fix is the same; the risk surface just got broader.

---

## Class B: Abliterated / Uncensored Models (HIGH: safety-rail removal)

22+ instances are running models that have explicitly had their safety guardrails removed. Notable model families observed:

| Model | Instances | Source |
|---|---|---|
| `huihui_ai/qwen3.5-abliterated:27b` | 2 | huihui_ai (prolific abliteration researcher on HF) |
| `huihui_ai/deepseek-r1-abliterated:1.5b` | 2 | huihui_ai |
| `huihui_ai/qwen3-coder-next-abliterated:latest` | 1 | huihui_ai |
| `seamon67/Gemma3-Abliterated:27b-q4_K_M` | 2 | seamon67 |
| `VladimirGav/Qwen3.6-27B-16GB-VRAM-Uncensored:latest` | 1 | VladimirGav (Russian-attributed) |
| `sorc/qwen3.5-uncensored:latest` | 1 | sorc |
| `qwen3.5-uncensored-128k:latest` | 1 | local fork |
| `Llama-3.1-8B-Lexi-Uncensored-V2-GGUF` | 2 | Orenguteng / mradermacher quants |
| `Qwen3.5-9B-Claude-4.6-Opus-Uncensored-Distilled-GGUF` | 1 | LuffyTheFox (claims to be a Claude-Opus distillation with safety removed) |
| `Llama-3.2-3B-Instruct-Uncensored-GGUF` (multiple custom variants) | 7 | bartowski quants + multiple per-operator `-custom-custom-custom-...` forks |
| `llama2-uncensored:latest` | 1 | classic uncensored Llama 2 |
| `openhermes:latest` | 1 | OpenHermes (Hermes is uncensored by default) |

**Notable:** the `bartowski/Llama-3.2-3B-Instruct-Uncensored-GGUF-custom-custom-custom-local-custom-dev:v18` naming pattern is from a single operator who has been iteratively forking and re-quantizing the same base Lexi-uncensored Llama. They're on at least version 41 of one variant and version 18 of a deeper "dev" variant, production iterative work on uncensored model serving.

**Risk class:** these are models trained or modified to bypass content-moderation refusals. Operators choose them for one of:
- Adult content generation (sexting/NSFW chat)
- Malware / phishing-content generation
- Harassment / abuse content
- Research on jailbreak resistance

Either way, exposure unauth = anyone can query the operator's de-restricted model. The `Claude-4.6-Opus-Uncensored-Distilled` finding is particularly concerning, that's a model claiming to be a distillation of Claude Opus with safety removed.

---

## Class C: Specialty / Niche Models (MEDIUM informational)

Beyond the cloud and uncensored clusters, the long tail includes:

- Embeddings: `nomic-embed-text` (36), `bge-m3` (17), various Qwen embedding fine-tunes
- Code: `qwen2.5-coder`, `devstral-2`, `qwen3-coder-next`
- Multilingual: many Qwen 2.5/3 variants
- Tiny models: `smollm2:135m` (83), `llama3.2:1b` (15), `tinyllama:latest` (10)
- Embeddings + chat combos suggesting RAG deployments

---

## Cross-Survey Pattern (updated, final-form)

| Tier | Platform | Sample | Unauth |
|---|---|---|---|
| Vector DB | Qdrant / ChromaDB / Milvus | 142 | 100% |
| Inference (raw) | Triton / vLLM / Ollama | **388** | **100%** |
| Image-gen | A1111 | 1 | 100% |
| MLOps | MLflow Tracking | 11 | 100% |
| Data App | Streamlit | 551 | 100% |
| Orchestration UI | Flowise / n8n / Open WebUI / Langflow | 1170 | 0% (small misconfig %) |

**388 inference servers (Triton + vLLM/OpenAI-compat + Ollama), 100% unauth.** Across 5 distinct platforms. The pattern is now overwhelming: any inference layer that doesn't ship with auth-on-default is deployed unauth at population scale on the public internet.

---

## Disclosure Posture

342 individual operators is past triage capacity for this survey class. Disclosure focus:

1. **Class B (abliterated/uncensored models)**, coordinated disclosure to Ollama Inc. + relevant cloud providers' abuse channels. The model-serving-with-no-safety-rails class is the highest-priority for external-action.
2. **Class A (`:cloud` quota theft)**, operator-direct contact where IP is identifiable. For unattributable IPs, hosting-provider abuse channel routing.
3. The general body of 342 unauth Ollamas, informational; Ollama Inc. would need to ship an auth-by-default change upstream for the population to fix at scale (same path Flowise + n8n took).

NuClide is not opening 342 individual disclosure threads.

---

## What Was NOT Done

- No `/api/generate` calls, would burn operator compute or Cloud-quota
- No `/api/chat` calls, same
- No model file downloads via `/api/show`, would exfiltrate operator-tuned model weights for the abliterated/uncensored fine-tunes
- No interaction with the model serving plane

The model-list capture is metadata-only.

---

## NuClide Pipeline Artifacts

| Stage | Notes |
|---|---|
| Discovery | masscan port 11434 → 882 IPs |
| Fingerprint | `ollama-probe.py`, `Ollama is running` text match + `/api/tags` for model list |
| Findings ledger | 174 high-impact instances (cloud-quota + abliterated) ingested into `data/nuclide.db` |
| What was NOT done | No inference, no model downloads |

---

## References

- Ollama auth (lack thereof): https://github.com/ollama/ollama/issues/849 (longstanding "ollama needs auth" tracker)
- Abliteration overview: https://huggingface.co/blog/mlabonne/abliteration
- Cross-survey index: [index.md](index.md)
