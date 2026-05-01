# G0I — AI API Gateway Intelligence

_NuClide Research · 2026-05-01_

---

## Platform Summary

G0I (`g0i.ai` / `g0i.shop`) is a commercial AI API aggregator described as "Infrastructure for frontier AI" — a unified OpenAI-compatible gateway proxying 470+ models from multiple closed and open-source backends. The platform supports a white-label API (observed brand variant: `AiCos Theta`).

- **Available languages listed in schema.org:** English, Arabic
- **Contact:** support@g0i.shop / Twitter: @g0ishop
- **Free tier:** 500K tokens / 24h trial (no card)
- **Canonical URL:** g0i.shop

---

## Exposure

### `/api/tags` — Open (No Auth Required)

`https://g0i.ai/api/tags` returns the full model catalog (85 entries) without authentication. This is an information disclosure — full model list including:

- All proxied closed-source API model names
- Internal backend naming conventions
- HauhauCS uncensored model presence

Inference requires `Authorization: Bearer <key>` — confirmed by probe.

### Notable Models in Catalog (85 total)

| Model | Notes |
|---|---|
| `claude-opus-4-7`, `claude-sonnet-4.6`, `claude-haiku-4.5` | Anthropic API proxied |
| `gpt-5`, `gpt-5.4`, `gpt-5.4-pro`, `gpt-5.5`, `gpt-5.4` | OpenAI API proxied (multiple GPT-5 versions) |
| `gemini-3.1-pro-preview`, `gemini-3.1-flash-image` | Google API proxied |
| `grok-4-1-fast` | xAI Grok proxied |
| `gemma-4-26b-uncensored` | Uncensored Gemma 4 |
| `glm-5`, `glm-5.1`, `glm-5-cloud` | GLM family (same as KRENA 433GB deployment) |
| `gervasio-70b` | Portuguese LLM |
| `deepseek-v4-pro`, `deepseek-v4-flash` | DeepSeek |
| `kimi-k2.6`, `zo-kimi-k2.5` | Kimi variants |

---

## Route Pattern Analysis (from active-models PDF)

The public-facing model list at `g0i.ai/models` exposes internal backend routing notation. Route labels use format `[model-NODESUFFIX-PORT]`:

| Pattern | Example | Interpretation |
|---|---|---|
| `[qwen2-60-11434]` | `qwen25 7b (route)` | Node suffix 60, port 11434 (Ollama default) |
| `[meta-llama-3-49-8080]` | Multiple llama3 routes | Node 49, port 8080 |
| `[meta-llama-3-49-9000]` | Same node, port 9000 | Two Ollama instances on same node |
| `[qwen35-35b-cn2]` | Qwen3.5 35B route | "cn2" suffix = China network 2 CDN path |
| `[tinyllama-1-115-8888]` | TinyLlama routes | Port 8888 cluster |
| `[llama-3-instruct-8b-]` | Directory-style | Filesystem path routing |

Node suffixes (60, 100, 115, 124, 141, 168, 179, 199, 206, 213, 215, 223, 230, 241, 253) suggest a /24 cluster with 15+ backend nodes running Ollama on non-standard ports (808, 1234, 8000, 8080, 8081, 8888, 9000).

---

## HauhauCS Operator Link

G0I hosts HauhauCS-branded uncensored Arabic models:
- `Qwen 3.5 9B Uncensored HauhauCS`
- `Qwen3.5 35B A3B Uncensored HauhuCS Aggressive`
- `Qwen3.5 4B Uncensored HauhauCS Aggressive`

**HauhauCS** is a HuggingFace operator publishing GGUF quantizations of uncensored Qwen models (`hf.co/HauhauCS/`). The same operator's models are deployed locally at ENSTINET Egypt NREN (195.43.26.91:3005), with system prompts explicitly disabling content restrictions in Arabic.

G0I's Arabic-language platform focus and HauhauCS model hosting establishes a Middle East/Arabic operator ecosystem connection.

---

## Two SHA256 Blob Hashes in Model Listing

Two raw model blob SHA256 hashes appear in the public model list — likely Ollama model manifest references leaked into the public-facing API response:
- `sha256 667b0c1932bc6ffc593ed1d03f895bf2dc8dc6df21db3042284a6`
- `sha256 87bb374d849f80ebdfabb304189fac9e0bd35a0f74506e6a59c51`

These can be cross-referenced against Ollama registry manifests to identify exact base models.

---

## Niche Model Names as Shodan / Banner Needles

Uncommon model names from G0I model list useful for HTTP banner correlation:

- `TheDrummer Behemoth ReduX 123B v1.1`
- `TheDrummer Skyfall 31B v4.1`
- `Harbinger 24B absolute heresy.i1`
- `WeirdCompound v1.7 24b.i1`
- `iFlow ROME 30BA3B`
- `backrooms 7 8B`
- `massagenearme 3B`
- `CyberSec Qwen3 Hostile 8B`
- `mradermacher Strawberrylemonade L3 70B v1.2 i1`
- `Gervasio 70B Portuguese`
- `Goliath 120B`
- `LFM2 24B A2B`
- `LexJade CivL CL Pro 9.4B A4B`
- `xiaoyu 4b 20260301`
- `MiniMax-M2.5-00001-of-00004.gguf`
- `translatemgemma 12b it.i1`
- `Moonlight 16B A3B Instruct`
- `HauhauCS` (operator tag)

---

## Files

- `g0i-models.pdf` — Full 342-model active models list snapshot (2026-05-01)
