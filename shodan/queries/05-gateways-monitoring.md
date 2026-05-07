# 5. AI Gateways, Proxies & Monitoring

_Section verified: April 22, 2026 11:38_

The control and observability plane between applications and LLM providers. Gateways centralize provider API keys; observability platforms log every prompt and response, when exposed, they reveal both the secrets and the conversational data flowing through them.

## AI Gateway / Proxy

| Shodan Query | Notes |
|---|---|
| `http.html:"litellm"` | 5,100 hits, broadest LiteLLM surface; high-confidence signal |
| `http.title:"LiteLLM"` | 5,076 hits, LiteLLM admin UI exposed; master key in env |
| `http.html:"ai-proxy" "kong"` | 493 hits, Kong AI proxy plugin; proxies provider keys + prompt templates |
| `("kong" "ai-proxy" OR "ai-prompt")` | 492 hits, Kong AI plugins alternate form |
| `http.html:"arize phoenix"` | 358 hits, Arize Phoenix trace UI; contains full prompt/response history |
| `http.title:"AI Gateway"` | 257 hits, catches multiple AI-gateway vendors (Cloudflare, Kong, Portkey docs), not Cloudflare-specific |
| `"LiteLLM"` | 144 hits, LiteLLM bare-string form |
| `http.html:"portkey"` | 44 hits, Portkey gateway; provider API keys in config |
| `"portkey" "gateway"` | 2 hits, Portkey gateway narrow form; provider API keys in config |
| `"unify" "router"` | 20 hits, Unify AI router, multi-provider fallback, keys in config |
| `http.html:"ai-proxy" port:8000` | 16 hits, AI proxy on default port |
| `http.html:"helicone"` | 12 hits, Helicone observability proxy |
| `"Portkey"` | 12 hits, Portkey bare-string form |
| `"Helicone"` | 11 hits, Helicone bare-string form |
| `http.title:"Helicone"` | 7 hits, Helicone admin UI |
| `http.title:"Tyk"` | 6 hits, Tyk API gateway UI |
| `"tyk-gateway"` | 5 hits, Tyk gateway narrow form |
| `http.html:"ai-prompt" "kong"` | 5 hits, Kong AI prompt plugin |
| `"AI Gateway" "Cloudflare"` | 4 hits, Cloudflare AI Gateway specific form |
| `http.html:"ai gateway" "cloudflare"` | 4 hits, Cloudflare AI Gateway HTML form |
| `http.html:"unstructured-api"` | 4 hits, Unstructured API exposure |
| `http.title:"Portkey"` | 6 hits, Portkey admin UI |

## LLM Observability / Monitoring

| Shodan Query | Notes |
|---|---|
| `"Langfuse" port:3000` | 1,131 hits, logs every prompt/response, high-value PII leak |
| `"tyk"` | 1,340 hits, Tyk API gateway bare form ⚠️ bare form; sanity-check before trusting, 1,340 is a large jump from html-scoped form (91); may include low-signal matches |
| `http.html:"tyk"` | 91 hits, Tyk gateway HTML-scoped form; higher confidence than bare string |
| `http.html:"langsmith"` | 94 hits, LangSmith observability; logs prompt chains and agent traces |
| `http.title:"LangSmith"` | 67 hits, LangSmith UI exposed |
| `"arize"` | 65 hits, Arize ML observability bare form |
| `http.html:"arize"` | 407 hits, Arize observability platform; trace data contains prompt history |
| `http.title:"Arize"` | 42 hits, Arize UI exposed |
| `"Prometheus" "/metrics" "llm"` | 6 hits, Prometheus metrics endpoint with LLM labels |
| `http.title:"PromptLayer"` | 5 hits, PromptLayer observability, logs every prompt/response with keys |
| `"LangSmith"` | 37 hits, LangSmith bare-string form |

## Document Loaders / Parsers

| Shodan Query | Notes |
|---|---|
| `http.html:"apache tika"` | 698 hits, Apache Tika HTML form; SSRF history, arbitrary file read |
| `http.title:"Apache Tika"` | 687 hits, Apache Tika UI exposed; SSRF history |
| `"Apache Tika"` | 21 hits, Apache Tika bare-string narrow form |
| `http.title:"Unstructured"` | 25 hits, Unstructured document API UI |
| `http.html:"docling"` | 33 hits, Docling document parser |
| `"Docling"` | 13 hits, Docling bare-string form |
| `http.title:"Docling"` | 2 hits, Docling UI exposed |
