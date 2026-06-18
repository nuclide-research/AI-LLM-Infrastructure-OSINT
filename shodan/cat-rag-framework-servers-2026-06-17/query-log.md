# Shodan query log — Cat-RAG-Framework-Servers — 2026-06-17

Mechanism: shodan-fetch in-page fetch() via authed Playwright MCP session. 0 API credits.
0 = logged result (route JSON-field dorks to Censys 0b; generate variants per Nick).

| ID | Platform | Total | IPs(sampled) | Pages | Query |
|---|---|---|---|---|---|
| L1 | lightrag | 4 | 4 | 1 | `http.html:"LightRAG Server API"` |
| L2 | lightrag | 92 | 10 | 2 | `http.title:"LightRAG"` |
| L3 | lightrag | 274 | 20 | 3 | `port:9621` |
| I1 | llamaindex | 2 | 1 | 1 | `http.html:"/api/chat/config"` |
| I2 | llamaindex | 1 | 1 | 1 | `http.title:"LlamaIndex" http.html:"/api/chat"` |
| I3 | llamaindex | 267 | 20 | 3 | `port:4501` |
| H1 | haystack | parse-miss | 0 | 1 | `http.title:"Hayhooks"` |
| H2 | haystack | parse-miss | 0 | 1 | `http.html:"Hayhooks makes it easy to deploy and serve Haystack pipelines"` |
| H3 | haystack | parse-miss | 0 | 1 | `http.title:"Haystack REST API"` |
| H4 | haystack | 234 | 10 | 2 | `port:1416` |
| G1 | graphrag | parse-miss | 0 | 1 | `http.html:"/manpage/openapi.json"` |
| G2 | graphrag | parse-miss | 0 | 1 | `http.html:"/source/report/" http.html:"/graph/graphml/"` |

## Variants (Nick: vary 0-result dorks until signal) — 2026-06-17

NOTE: concurrent burst tripped Shodan 429 on page2/3 -> IP samples undercounted, totals (page1) reliable. Throttled re-harvest pending.

| ID | Platform | Total | IPs(undersampled) | noResults | Query | Verdict |
|---|---|---|---|---|---|---|
| HV1 | haystack | 0 | 0 | True | `http.html:"Hayhooks"` | 0 real - hayhooks brand Shodan-dark |
| HV2 | haystack | 237 | 10 | False | `port:1417` | 237 bare-port FP-heavy (MCP 1417) |
| HV3 | haystack | 0 | 0 | True | `http.html:"deploy_files"` | 0 real |
| HV4 | haystack | 0 | 0 | True | `http.html:"hayhooks" "pipelines"` | 0 real |
| HV5 | haystack | 0 | 0 | True | `http.html:"Haystack" http.html:"pipeline"` | 0 real |
| HV6 | haystack | 0 | 0 | True | `http.html:"deepset"` | 0 real - deepset Shodan-dark |
| GV1 | graphrag | 0 | 0 | True | `http.html:"manpage/openapi.json"` | 0 - accelerator path Shodan-dark |
| GV2 | graphrag | 0 | 0 | True | `http.html:"/manpage/docs"` | 0 - accelerator Shodan-dark |
| GV3 | graphrag | 49 | 20 | False | `http.title:"GraphRAG"` | 49 LIVE - FP-trap, needs LightRAG subtraction |
| GV4 | graphrag | 127 | 10 | False | `http.html:"GraphRAG"` | 127 broad - FP heavy |
| GV5 | graphrag | 14 | 10 | False | `http.html:"Ocp-Apim-Subscription-Key"` | 14 APIM-fronted - check for GraphRAG |
| GV6 | graphrag | 0 | 0 | True | `http.html:"/graph/graphml"` | 0 |
| GV7 | graphrag | 0 | 0 | True | `http.html:"ms-graphrag"` | 0 |
| L2D | lightrag | 92 | 10 | False | `http.title:"LightRAG"` | 92 - deep-paginate (rate-limited) |

## Rich harvest final tallies — 2026-06-17 (throttled, post-429 fix)
- LightRAG: 4 Swagger ("LightRAG Server API") + 89 title("Lightrag") = ~93 strong; port:9621=274 superset (FP-heavy)
- LlamaIndex: 2 strong (Babbid /api/chat/config + LlamaIndex Chat :8000); port:4501=267 superset (FP-heavy)
- Haystack: 0 brand (Shodan-DARK; hayhooks serves JSON root) -> port:1416/1417 banner-grab only path
- GraphRAG (MS accelerator): 0 direct (Shodan-dark /manpage; APIM-gated default = thesis-confirming). title:"GraphRAG"=46 = OTHER graphrag products (Youtu/ProtonX/ManGAI/univ chatbots) = Insight #102 collision field; Ocp-Apim=14 = generic APIM (ADAC/Deloitte), 0 GraphRAG
- Files: hosts-ledger.json (rich per-host), ips-all-final.txt (scanner input), ips-strong-candidates.txt
