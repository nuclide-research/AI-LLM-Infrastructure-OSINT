# 15. Fingerprinting Canaries

_Section verified: 2026-04-30_

Generic fingerprints that catch services regardless of branding. Useful when a target operator has stripped HTTP titles or moved services to non-default ports, but the underlying framework still leaks its identity through favicon hashes, headers, or API surface.

## Favicon Hashes

| Shodan Query | Notes |
|---|---|
| `http.favicon.hash:-1294819032` | Gradio |
| `http.favicon.hash:1279780014` | Streamlit |
| `http.favicon.hash:-1848965666` | Jupyter |
| `http.favicon.hash:-1404538293` | LlamaIndex / Create Llama App |
| `http.favicon.hash:348721092` | Clawdbot / OpenClaw agent UI |

Favicon hashes drift with version bumps. Hashes here were valid in April 2026; for long-term use, pair a hash with a text fingerprint to catch the service even when the icon changes.

## Generic AI Service Detection

| Shodan Query | Notes |
|---|---|
| `"Server: uvicorn" "/docs" "FastAPI"` | Any FastAPI ML service |
| `"/v1/chat/completions" port:8000` | OpenAI-compatible endpoint |
| `"/chat/completions"` | Unscoped form, catches OpenAI-compat APIs on non-standard paths/ports |
| `"/v1/embeddings" port:8000` | |
| `"model" "temperature" "max_tokens" port:8000` | OpenAI-style request schema |
| `"LM Studio" OR "lmstudio" port:1234` | LM Studio desktop server exposure |
| `http.html:"api/tags" port:11434` | Ollama model list (no auth) |
| `http.html:"mcp.json" OR "Model Context Protocol"` | MCP servers, heavily targeted in LLMjacking campaigns |
| `"aiohttp" product:"ComfyUI"` | Quick ComfyUI product-level filter |

## Honeypot / Canary Fingerprints

Tier T3 (recon/fingerprint). These strings are *unreleased / non-existent future-version model names* surfacing on Ollama-style `/api/tags` and similar listing endpoints. A real production node cannot legitimately serve a model that has not been released. Hits are high-confidence honeypot net, proxy/shim infrastructure, or LLMjacking lure boxes, never genuine deployments. Pivoted from the Ollama `/api/tags` cohort discovery on 2026-04-30 (14+ hosts advertising fabricated model identifiers in unison).

| Shodan Query | Hits (2026-04-30) | Notes |
|---|---|---|
| `http.html:"deepseek-v4-pro"` | 10 | Fabricated DeepSeek SKU; v4-pro does not exist. Honeypot/shim indicator. |
| `http.html:"glm-4.7-flash"` | 5 | Zhipu GLM-4.7 unreleased; "flash" suffix is Google-family naming bleed. Lure tell. |
| `http.html:"gemini-3-flash"` | 91 | Largest cohort. Gemini 3 not shipped under this name, proxy/shim or canary at scale. |
| `http.html:"minimax-m2.7"` | 44 | MiniMax M2.7 not released; second-largest cohort, likely the same operator family. |
| `http.html:"kimi-k2.6"` | 9 | Moonshot Kimi K2.6 fabricated; consistent with the cohort. |
| `http.html:"qwen3-coder-next"` | 9 | Alibaba Qwen3-coder-next is a placeholder string, not a published checkpoint. |
| `http.html:"gemma4"` | 27 | Google Gemma 4 not released; suffix-bumped from real gemma3. |

Cross-reference: pair with `http.html:"api/tags" port:11434` from the section above to confirm the honeypot net is wearing Ollama clothing. Total of 195 hosts across the seven canaries; expect heavy operator overlap.
