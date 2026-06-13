# Shodan Query Log — Cat-34 Self-Hosted LLM-App / RAG Builders

Date: 2026-06-12 | Method: authenticated Shodan web UI, in-page `fetch()` (0 API credits) | UI: wire.shodan.io v2.5.0
Parser: `<h4 class="total-results">N</h4>` / meta `content="N results found"`. Zero = `No results found`.

## Population census (basic + strict tier)

| Platform | basic dork | basic N | strict dork | strict N | Disposition |
|---|---|---:|---|---:|---|
| open-webui | `http.title:"Open WebUI"` | 18,613 | + favicon/theme-color | 16,910 | REAL (organic VPS) |
| librechat | `http.title:"LibreChat"` | 3,161 | + favicon-32x32 port:3080 | 446 | REAL |
| ragflow | `http.title:"RAGFlow"` | 1,894 | + `infiniflow` | 0 | REAL (strict over-tight) |
| dify | `http.html:"/console/api" http.title:"Dify"` | 1,586 | + `_next` | 1,586 | REAL (basic==strict, clean) |
| anythingllm | exact title | 1,147 | exact long title | 1,129 | REAL |
| maxkb | `http.title:"MaxKB"` | 1,103 | + `/ui/chat/` | 2 | REAL (strict over-tight) |
| vanna | `http.html:"img.vanna.ai"` | 15 | + copilot string | 0 | REAL small |
| quivr | `http.title:"Quivr"` | 9 | + SUPABASE | 0 | REAL small |
| khoj | `http.title:"Khoj"` | 7 | + assets.khoj.dev | 2 | REAL small |
| qanything | `http.title:"QAnything"` | 7 | + /api/local_doc_qa/ | 0 | REAL small |
| privategpt | `http.title:"PrivateGPT"` | 6 | + gradio port:8001 | 0 | REAL small |
| chatbot-ui | `http.title:"Chatbot UI" "Start Chatting"` | 6 | + _next/static | 5 | REAL small |
| verba | `http.html:"The GoldenRAGtriever"` | 3 | + title Verba | 3 | REAL small |
| bionic-gpt | `http.html:"bionicgpt"` | 1 | + Assistants port:3000 | 0 | REAL small |
| **flowise** | `http.title:"Flowise"` | **70,158** | exact long title | 69,926 | **FP-INFLATED** (AWS-uniform; product:Flowise=2) |
| **langflow** | `http.title:"Langflow"` | **74,102** | + port:7860 | 3 | **FP-INFLATED** (AWS-uniform; product:Langflow=404) |
| hayhooks | `http.html:"Hayhooks" "status_all"` | 0 | + yaml_pipeline_deploy port:1416 | 0 | SHODAN-DARK -> Censys/scan |
| ragapp | `http.html:"RAGapp" "/admin"` | 0 | + /api/management/config | 0 | SHODAN-DARK -> Censys/scan |
| morphik | `http.html:"generate_local_uri" "morphik"` | 0 | + retrieve/chunks port:8000 | 0 | SHODAN-DARK -> Censys/scan |
| localgpt | `http.html:"ollama_running" "database_stats"` | 0 | + available_models | 0 | SHODAN-DARK -> Censys/scan |
| r2r | `http.html:"R2R" "v3/health"` | 0 | port:7272 + results | 0 | SHODAN-DARK -> Censys/scan |
| casibase | `http.title:"Casibase"` | 0 | OpenAgent + cdn.openagentai | 0 | SHODAN-DARK -> Censys/scan |
| kotaemon | `http.title:"kotaemon"` | 0 | + ktem_app_data port:7860 | 0 | SHODAN-DARK -> Censys/scan |
| fastgpt | `http.html:"/api/common/system/getInitData"` | 0 | title FastGPT + feConfigs | 0 | SHODAN-DARK (China/Aliyun) -> Censys/Quake |
| cognita | `http.title:"TrueFoundry ..."` | 0 | VITE_QA_FOUNDRY_URL | 0 | SHODAN-DARK -> Censys/scan |
| h2ogpt | `http.title:"h2oGPT"` | 0 | + h2oai/h2ogpt | 0 | SHODAN-DARK -> Censys/scan |
| lobe-chat | `http.title:"LobeChat" port:3210` | 0 | x-lobe-chat-auth | 0 | SHODAN-DARK -> Censys/scan |

## Facet false-positive analysis (Insight #104 candidate)

`http.component:"Gradio"` returns **0 on the web UI** (component/product filters are HTML-body-only here — route to Censys). h2oGPT/kotaemon strict dorks originally used it; replaced with html-string variants.

Flowise + Langflow title dorks return ~70K/74K but the facet sidebars are **near-identical** and AWS-region-uniform:
- Flowise: US 10,834 / AU 5,053 / CA 4,784 / JP 4,681 / IN 4,404 ; orgs Amazon.com 10,323 / Amazon Tech 6,598 / ADS-CA 4,453 / A100 ROW 4,268
- Langflow: US 11,043 / AU 5,539 / CA 5,368 / JP 5,091 / IN 4,526 ; orgs Amazon.com 11,149 / Amazon Tech 6,552 / ADS-CA 4,990 / A100 ROW 4,629
- Two distinct products cannot share the same 70K AWS hosts. Shodan verified-**product** floor: Flowise=2, Langflow=404. The title matches are a replicated AWS artifact (loose title tokenization).
- Contrast Open WebUI (organic): Hetzner 1,403 / China Unicom 727 / Aliyun 710 / Contabo 641 / DigitalOcean 577 — classic self-host VPS spread. 18,613 is trustworthy.

Discriminator: AWS-region-uniform + identical-across-dorks = FP. Organic VPS spread = real. `Top Products` facet = ground-truth floor.

## Harvest dispositions
- REAL harvest-worthy: open-webui (sample), librechat, ragflow, dify, maxkb, anythingllm + 8 small.
- FP-inflated: flowise/langflow harvest via `product:` not title (Flowise=2, Langflow=404).
- Shodan-dark (11 platforms, 0 on niche dork): niche ports/paths Shodan does not index -> Censys (0b) + active scan (0c). NOT absence of population.

## Shodan-dark loose-variant retry (Insight #105 — bare-unique-marker test)

| platform | bare variant dork | N |
|---|---|---:|
| hayhooks | `"yaml_pipeline_deploy"` | 0 |
| localgpt | `"ollama_running" "database_stats"` | 0 |
| cognita | `"VITE_QA_FOUNDRY_URL"` | 0 |
| casibase | `"cdn.casibase.org"` | 0 |
| ragapp | `"/api/management/config" "RAGapp"` | 0 |
| h2ogpt | `"h2oai/h2ogpt"` | 0 |
| r2r | `"R2R-Application"` | 0 |
| morphik | `"retrieve/chunks" "morphik"` | 0 |
| lobe-chat | `"x-lobe-chat-auth"` | 0 |
| kotaemon | `"ktem_app_data"` | 0 |
| fastgpt | `"FastGPT" "feConfigs"` | 0 |
| fastgpt | `"FastGPT"` (bare) | 33 (noisy: ~7 Attu/Milvus, 1 real 401-auth, rest redirects) |

10/11 zero on globally-unique bare markers = genuinely Shodan-dark (absent from index, not dork-artifact).
FastGPT harvest (30 hosts) -> fastgpt_attu_ips.txt; aimap = no AI svc (Milvus gRPC firewalled, no Attu FP).
Censys recovery BLOCKED (cencli search 422 insufficient-balance / feature-credit bucket); deferred to 2026-07-08 reset.
