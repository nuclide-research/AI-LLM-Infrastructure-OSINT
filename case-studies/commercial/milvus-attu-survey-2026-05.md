---
type: survey
---

# Milvus/Attu on Public Cloud: Auth Posture and Multi-Tenant SaaS Exposure Survey

_NuClide Research · 2026-05-09_

---

## Summary

Shodan pull of `http.title:"Attu" "Milvus"` → 1,389 unique IPs → asyncio probe of Attu port 3000 + Milvus REST port 19530 → **763 confirmed reachable** instances. Of these, **303 have the Attu admin UI open** (full read/write GUI access), **593 have Milvus REST unauthenticated**, and **330 contain populated collections**. RBAC is opt-in in Milvus, disabled by default — the pattern mirrors Qdrant, Weaviate, and ChromaDB: the auth-off default ships and operators rarely change it.

The standout finding class is again the **enterprise multi-tenant SaaS pattern**: AI platforms built on top of Milvus expose their entire client portfolio as enumerable collections without access controls. A RAGFlow deployment (1,224 collections, Attu open) and an Indian chatbot SaaS (704 collections, 194 distinct tenants) represent the highest-volume confirmed exposures.

---

## Methodology

```
shodan download --limit 1500 attu-milvus.json.gz 'http.title:"Attu" "Milvus"'
  → 1,389 unique IPs

attu-probe.py (asyncio, 80 concurrent)
  GET  http://{ip}:3000          → confirm Attu UI (HTTP 200/3xx)
  POST http://{ip}:19530/v2/vectordb/collections/list  body {"dbName":"default"}
       match {"code":0, "data":[...]} → unauthenticated Milvus REST
  GET  http://{ip}:9091/healthz  → Milvus metrics/health fallback
  → 763 confirmed (probe time: ~30 seconds)
```

---

## Findings Summary

| Metric | Value |
|---|---|
| Shodan hits (`http.title:"Attu" "Milvus"`) | 1,418 (1,389 downloadable) |
| Confirmed reachable | **763** |
| Attu UI open (:3000) | **303** |
| Milvus REST unauthenticated (:19530) | **593** |
| Populated (≥1 collection) | **330** |

---

## Notable Findings

### F1 — RAGFlow deployment (HIGH)

**Host:** `183.6.121.94` (ChinaTelecom BACKBONE AS4134, Shenzhen CN)  
**Severity:** HIGH — 1,224 unauthenticated Milvus collections, Attu admin UI open on port 3000

Collection naming pattern matches RAGFlow's internal schema: `_{numeric_id}_{chunk_collection|file_info_collection|structure_info_collection|knowledge_triple|file_link}`. RAGFlow creates this 4–5 collection set per knowledge base — approximately **245–305 distinct knowledge bases** are present given the collection count and naming pattern.

RAGFlow is an open-source RAG engine (GitHub: infiniflow/ragflow) that uses Milvus as its vector backend and Elasticsearch for full-text search. When Milvus's RBAC is off (default), every knowledge base's chunks, file metadata, structure info, and knowledge-graph triples are directly accessible.

**Attu access (port 3000):** The Attu admin GUI is publicly reachable. Attu provides a full React frontend for Milvus administration: collection creation/deletion, data browse, vector search, index management. A reachable Attu is equivalent to a reachable database with no auth — full read/write/delete.

**Reproduction:**
```bash
curl -X POST http://183.6.121.94:19530/v2/vectordb/collections/list \
  -H "Content-Type: application/json" -d '{"dbName":"default"}'
# Returns {"code":0,"data":["_485_file_info_collection","_496_chunk_collection",...1224 total]}
```

**Disclosure status:** Not yet disclosed. ChinaTelecom hosting — direct operator not identified from exposed surface. Disclosure would route via CNCERT/CC (`cncert@cert.org.cn`) if operator not found.

---

### F2 — Indian chatbot SaaS platform (HIGH)

**Host:** `103.180.31.18` (Silver Touch Technologies Limited AS149275, Ahmedabad IN)  
**Severity:** HIGH — 704 collections, 194 distinct chatbot tenant IDs (range 0–1130), Attu UI and Milvus REST both open

Collection naming: `chatbot_{id}`, `chatbot_{id}_title`, `chatbot_{id}_faqs`, `chatbot_{id}_faqs_title` — a 4-collection-per-tenant pattern. With 194 distinct bot IDs and gaps indicating deleted tenants, this is an active SaaS platform serving multiple clients.

Silver Touch Technologies is an Indian IT services company (Ahmedabad, Gujarat). The exposed Milvus instance appears to be the vector backend for their AI chatbot product line.

**Disclosure status:** Not yet disclosed. Routing via Silver Touch Technologies' public contact surface.

---

### F3 — Chinese art museum/cultural platform (MEDIUM)

**Host:** `175.27.225.242` (likely Alibaba Cloud CN)  
**Severity:** MEDIUM — 120 collections, Milvus REST open (no Attu)

Collection names: `yishuguan_f1` (yishuguan = art museum), `shanghai_jjt_v4_colornorm` (Shanghai JJT — likely Jujintian or similar cultural org), `ganhuayan` (感化院 / correctional facility or rehabilitation center), `zhonghe` (Chinese place name). Pattern suggests a multi-institution cultural/arts content management system.

---

### F4 — Crypto trading quant data store (LOW/MEDIUM)

**Host:** `14.103.126.159`  
**Severity:** LOW (financial data, not personal) — 26 collections, Attu open

Collection names: `kline_BTCUSDT_1h_*`, `kline_BTCUSDT_15m_*`, `kline_ETHUSDT_1h_*` — OHLCV kline (candlestick) data stored as vectors in Milvus. This is a quantitative trading research deployment indexing historical price data for vector similarity search (presumably for pattern matching / strategy similarity). The data is financial time-series, not personal data, but the Attu GUI exposes the operator's proprietary trading data structure and potentially their alpha-generating signal encoding.

---

## Auth Posture Analysis

Milvus RBAC is disabled by default. Enabling requires:
```yaml
# milvus.yaml
common:
  security:
    authorizationEnabled: true
```

And creating a root user + per-collection grants. Without this, any connection to port 19530 (gRPC or REST) has full admin access. The Attu UI on port 3000 requires no credentials when Milvus auth is off.

**gRPC blind spot persists:** Milvus's gRPC API on port 19530 (the primary production client interface) cannot be fingerprinted by Shodan banner match — gRPC uses binary HTTP/2 framing. This survey used the Milvus REST API (introduced in Milvus 2.4+) on the same port 19530, which Shodan can't see but asyncio probes can reach. The Shodan `http.title:"Attu"` query finds the admin UI, not the gRPC backend — Attu is the most reliably Shodan-visible signal for Milvus exposure.

---

## Discovery Context

Survey conducted 2026-05-09 as part of NuClide Research vector database exposure series. Shodan pull on `http.title:"Attu" "Milvus"` (1,418 hits, 1,389 downloadable). Asyncio probe of port 3000 (Attu) and port 19530 (Milvus REST).

Companion surveys: `weaviate-cloud-survey-2026-05.md`, `milvus-cloud-survey-2026-05.md`, `milvus-tier2-cloud-survey-2026-05.md`.
