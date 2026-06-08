---
type: survey-mini
category: vector-db
platform: marqo
date: 2026-06-08
researcher: NuClide Research
---

# Marqo Survey — 4 Unauth on 18-Host Population

_NuClide Research · 2026-06-08_

## Summary

Shodan-indexed Marqo population is small (n=18 unique IPs across all dork variants: `http.html:"Welcome to Marqo"`, `http.title:"marqo"`, `port:8882 "marqo"`, etc.). 4 hosts LIVE, all 4 unauthenticated on `/indexes`.

## Confirmed unauth

| ip | indexes | substrate |
|---|---|---|
| 185.216.22.109 | `marqo-production-v5`, `marqo-production-v4` | NexGen (CA) |
| 3.112.41.254 | `fashion_product_catalog`, `fashion_product_search` | AWS Tokyo (ap-northeast-1) |
| 34.66.208.64 | 3 internal indexes (names null) | Google Cloud (US) |
| 46.4.68.5 | `my_knowledge_base` | Hetzner FSN1 (DE) |

Index names alone are the operator-attribution finding. `marqo-production-v5/v4` = an operator's prod vector DB named explicitly. `fashion_product_catalog` = a fashion e-commerce search backend. `my_knowledge_base` = a RAG knowledge base.

## Thesis contribution

Marqo: `auth_default=none`, `MARQO_API_KEY` env var optional and not foregrounded in the production deployment docs. Result: 100 percent of LIVE hosts unauth.

This is the cleanest right-tail data point for the auth-friction gradient (Insight candidate #88, see meilisearch survey): "optional + not foregrounded ⇒ no operator sets it." Compare ComfyUI (no auth concept ⇒ 78%); Marqo sits between ComfyUI and Phoenix on the gradient because the key exists but the docs don't push it.

## Restraint

`/indexes` returns just `[{indexName: …}]` — names + count. Did not call `/indexes/{uid}/search`, `/indexes/{uid}/stats`, or `/indexes/{uid}/documents` (which would return record bodies). Names are the finding.
