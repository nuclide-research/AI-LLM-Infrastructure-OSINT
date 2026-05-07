# 1. LLM Orchestration Platforms

_Section verified: April 30, 2026_

Low-code/no-code builders, agent runtimes, and chain orchestrators. These platforms typically expose a web UI that, when unauthenticated, grants direct access to flow editors, API keys stored in nodes, and execution endpoints.

## Flowise

| Shodan Query | Notes |
|---|---|
| `title:"Flowise" port:443` | 586 hits, title fingerprint, mixed auth |
| `product:"Flowise"` | 576 hits, Shodan product facet, canonical fingerprint |
| `http.html:"Low-code LLM apps builder"` | 572 hits, HTML title fingerprint |
| `"Flowise"` | 170 hits, broad banner match |
| `"Flowise" http.status:200` | 26 hits, 200-response subset, likely reachable |
| `"Flowise" "chatflows"` | 9 hits, banner + API term |
| `"Flowise" "Express"` | 6 hits, Express-fronted subset |
| `"X-Powered-By: Express" "Flowise"` | 6 hits, header + banner intersect |
| `"Flowise" http.status:401` | 4 hits, auth-enabled subset |

**Deployment note:** As of April 2026, `port:3000` (Flowise default) is effectively dead on the public internet, production deployments now sit behind 443 reverse proxies almost universally. Prefer `product:"Flowise"` as the canonical fingerprint.

**CVE note:** CVE-2024-36420 (auth bypass via path traversal) affects Flowise < 1.8.2. Exposed pre-auth instances are RCE candidates, not just info disclosure.

## Other Orchestrators

| Shodan Query | Notes |
|---|---|
| `http.html:"open-webui"` | 19,549 hits (2026-04-30), package/asset string in HTML body; broader than title-only match, catches builds where the title was customized |
| `http.title:"Open WebUI"` | 18,736 hits, largest AI UI fingerprint on the internet; Ollama frontend |
| `http.title:"Open WebUI" port:8080` | 2,842 hits (2026-04-30), direct default-port subset; first-user-admin = effectively unauth, treat as T1 |
| `http.html:"dify"` | 8,750 hits, broad Dify HTML fingerprint |
| `http.title:"LiteLLM"` | 5,076 hits, LLM proxy, master key often leaked in env |
| `"Jan" port:1337` | 4,624 hits, desktop app in server mode |
| `http.title:"Dify"` | 2,614 hits, tighter Dify title fingerprint |
| `http.title:"Clawdbot Control"` | 1,770 hits ⚠️ `http.title:` is tokenized, sample before trusting, may include false positives |
| `http.html:"Chainlit"` | 1,144 hits, conversational UI layer on LangChain |
| `http.title:"Langflow"` | 844 hits, flow builder, often deployed unauth |
| `"AnythingLLM" port:3001` | 366 hits, known auth bypass history |
| `http.title:"Gradio"` | 225 hits, generic Gradio wrapper (covers oobabooga, demos, custom AI apps) |
| `port:18789 ("openclaw" OR "clawdbot")` | 165 hits, OpenClaw gateway (grouped OR required; unparenthesized breaks Shodan precedence) |
| `"LocalAI" port:8080` | 95 hits, no auth by default |
| `http.html:"Ollama is running" -port:443` | 26,580 hits (2026-04-30), canonical root-response string; `-port:443` drops TLS-fronted noise; T1, Ollama has no auth support, exposure = full model access |
| `product:Ollama port:11434` | 21,067 hits (2026-04-30), Shodan product facet on default port; direct-exposure subset, T1 |
| `"Ollama" port:11434` | 37 hits, banner-only fallback; the two queries above are the canonical fingerprints |
| `"hexstrike-ai" port:11434` | Ollama with HexStrike AI offensive orchestrator loaded, 47 MCP tools, unrestricted shell exec when Flask server running |
| `"qwen3.5-abliterated" port:11434` | Refusal-stripped 35B MoE Qwen model, no safety guardrails |
| `"huihui_ai" port:11434` | huihui-ai abliterated model family (qwen3/qwen3.5 variants) |
| `"abliterated" port:11434` | Broad match for refusal-removed models on exposed Ollama instances |
| `http.html:"AutoGPT"` | 32 hits, project moribund since 2025, retained for completeness |
| `http.favicon.hash:-1404538293` | 11 hits, LlamaIndex favicon |
| `"LangChain" port:8000` | 6 hits, library fingerprint, app varies |
| `http.title:"Create Llama App"` | 6 hits, LlamaIndex default UI (RAG starter) |
| `http.html:"haystack"` | 3,341 hits, ⚠️ generic term, collides with search tools, monitoring, GDS frameworks |
| `"zylon"` | 73 hits, PrivateGPT vendor; ⚠️ collides with anime/gaming names |
| `http.html:"privategpt"` | 7 hits, PrivateGPT-specific HTML match |

**Verified April 2026.** Deployment note: the "service + default port" pattern that dominated 2024 is largely dead, most platforms moved behind 443/80 reverse proxies. Queries below 10 hits are retained when they still identify the platform uniquely.

**OpenClaw / Clawdbot:** This is not a passive reconnaissance target. A publicly reachable OpenClaw gateway is an agent with shell execution, browser automation, email send, and calendar write on whoever deployed it. Treat positive hits as live compromise surface, not data disclosure.

## Prompt / Chain Management

| Shodan Query | Notes |
|---|---|
| `product:"n8n"` | **77,102 hits**, canonical n8n fingerprint; RCE history (CVE-2024-25289 and successors), see n8n note below |
| `"n8n"` | 4,966 hits, banner-only, narrower subset |
| `http.title:"n8n"` | 370 hits (2026-04-30), title-level match, often editor UI; basicauth optional and frequently skipped, lean T1 |
| `http.html:"/rest/login"` | 162 hits (2026-04-30), n8n REST login path leaked into HTML body; tighter than title-only when present |
| `"x-powered-by: Express" port:5678` | 134 hits (2026-04-30), Express header on n8n's default port; direct-exposure subset bypassing reverse-proxy fronting |
| `http.title:"n8n - Workflow Automation"` | 24 hits (2026-04-30), verbose default title; high-confidence editor UI subset |
| `http.html:"langgraph"` | 501 hits, LangGraph Studio / LangChain graph orchestrator |
| `http.html:"rivet"` | 169 hits, ⚠️ polluted; "Rivet" collides with Rivet Networks NIC UIs, storage products |
| `http.title:"Rivet"` | 71 hits, ⚠️ same pollution concern |
| `http.title:"LangGraph"` | 51 hits, title-level match |
| `http.html:"promptflow"` | 5 hits, best PromptFlow variant found |
| `http.title:"PromptFlow"` | 4 hits, title match |

**n8n note:** n8n is by far the most-exposed workflow/orchestration platform observed in this catalogue, roughly 4× the count of Open WebUI and ~130× Flowise. The default-port fingerprint (`port:5678`) is obsolete as of April 2026; nearly all deployments sit behind reverse proxies, n8n.cloud, or containerized ingress. Prefer `product:"n8n"` as the canonical query. Given n8n's "execute code" and HTTP-request nodes, exposed editors with weak or default auth are direct RCE surface, not just workflow disclosure.
