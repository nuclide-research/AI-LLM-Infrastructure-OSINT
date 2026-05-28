# RAG Frameworks Shodan Harvest Log
_Survey date: 2026-05-28_
_Method: Playwright authenticated session + fetch() from page context_

## Query Results

| Platform | Query | Hits | IPs Collected | Notes |
|----------|-------|------|---------------|-------|
| RAGFlow | `http.html:"ragflow" port:80` | 540 | 10 (p1) | Subset of title dork |
| RAGFlow | `http.title:"RAGFlow"` | 1,902 | 50 (p1-5) | Primary population signal |
| RAGFlow | `port:9380 http.html:"ragflow"` | 0 | 0 | Internal port not crawled |
| RAGFlow | `http.html:"/api/v1/user/login" http.html:"ragflow"` | 0 | 0 | String not in Shodan index |
| DocsGPT | `http.title:"DocsGPT"` | ~8 | 8 | Full population |
| DocsGPT | `port:5001 http.html:"DocsGPT"` | 0 | 0 | Dead dork |
| DocsGPT | `port:5001 http.html:"docsgpt" http.html:"conversation"` | 0 | 0 | Dead dork |
| DocsGPT | `http.html:"DocsGPT" http.html:"uvicorn"` | 0 | 0 | Dead dork |
| DocsGPT | `port:5173 http.html:"docsgpt"` | 0 | 0 | Dead dork |
| Ragapp | `port:8000 http.html:"ragapp" http.html:"/admin"` | 0 | 0 | Not indexed |
| Ragapp | `port:8000 http.html:"RAGapp" http.html:"llamaindex"` | 0 | 0 | Not indexed |
| Ragapp | `http.html:"/api/management/config"` | 0 | 0 | Not indexed |
| Ragapp | `http.title:"Ragapp"` | 0 | 0 | Not indexed |
| Ragapp | `http.html:"ragapp" http.html:"/admin"` | 0 | 0 | Not indexed |
| Ragapp | `port:8000 http.title:"RAGapp"` | 0 | 0 | Not indexed |
| Ragapp | `http.html:"ragapp" http.html:"FastAPI"` | 0 | 0 | Not indexed |
| LightRAG | `port:9621 http.html:"LightRAG"` | 0 | 0 | Port not crawled |
| LightRAG | `port:9621 http.html:"/query"` | 0 | 0 | Port not crawled |
| LightRAG | `http.html:"LightRAG" port:8020` | 0 | 0 | Dead dork |
| LightRAG | `http.html:"LightRAG" http.html:"/query"` | ~1 | 1 | Narrow signal |
| LightRAG | `http.html:"LightRAG" http.html:"swagger"` | ~5 | 5 | Best LightRAG dork |

## Population Summary

| Platform | Shodan Population | Sampled | Confirmed Instances |
|----------|------------------|---------|---------------------|
| RAGFlow | 1,902 | 50 | 7 confirmed RAGFlow identity; auth enforced |
| DocsGPT | ~8 | 8 | 0 confirmed (1 probable Celery backend) |
| LightRAG | ~6 | 6 | 2 confirmed unauth |
| Ragapp | 0 | 0 | N/A — not indexed |

## Key Signal Notes

- RAGFlow `http.title:"RAGFlow"` is the dominant dork (1,902 hits). The `html` + port dorks are subsets or dead.
- LightRAG best found via `http.html:"LightRAG" http.html:"swagger"` — Swagger UI is the surface Shodan indexes.
- DocsGPT title dork returns only 8 global results — small deployment footprint.
- Ragapp not indexed in Shodan at all — likely too new or port:8000 crawl coverage is low.
