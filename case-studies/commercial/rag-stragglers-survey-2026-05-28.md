# RAG Stragglers: LightRAG, RAGFlow, DocsGPT, Ragapp Population Survey

**Survey date:** 2026-05-28  
**Category:** RAG frameworks — stragglers population pass  
**Platforms covered:** LightRAG, RAGFlow, DocsGPT, Ragapp  
**Lead findings:** 2 LightRAG unauth (1 general, 1 medical + video RAG); RAGFlow auth-enforced across sampled population  

---

## Background

Four RAG platforms were left unfinished from prior survey runs: LightRAG, RAGFlow, DocsGPT, and Ragapp. This pass closes them out with a full Shodan harvest, verification, and arsenal run.

RAGFlow holds a known pre-auth RCE (CVE-2024-12433: unauthenticated file upload to the web API). DocsGPT holds CVE-2025-0868, a pre-auth RCE via path traversal. Neither was triggered during this survey. The goal was population mapping and auth-on-default verification, not exploitation.

---

## Shodan Harvest

### LightRAG

LightRAG defaults to port 9621. Shodan does not index that port. The only productive dork was `http.html:"LightRAG" http.html:"swagger"` — LightRAG ships a Swagger UI that Shodan does pick up when the service runs on a crawled port.

| Dork | Hits | Yield |
|------|------|-------|
| `port:9621 http.html:"LightRAG"` | 0 | Port not crawled |
| `http.html:"LightRAG" http.html:"swagger"` | 5 | Best dork — 2 confirmed unauth |
| `http.html:"LightRAG" http.html:"/query"` | 1 | Subset of swagger dork |

6 IPs total collected. 2 confirmed unauth. 3 offline at probe time. 1 FP (different service).

### RAGFlow

`http.title:"RAGFlow"` is the dominant dork at 1,902 hits. Port-based and backend-string dorks returned nothing — the backend runs on internal ports that Shodan does not index. 50 IPs sampled from the title dork.

| Dork | Hits |
|------|------|
| `http.title:"RAGFlow"` | 1,902 |
| `http.html:"ragflow" port:80` | 540 |
| `port:9380 http.html:"ragflow"` | 0 |

### DocsGPT

Small deployment footprint. 8 global results from the title dork. All backend dorks dead.

| Dork | Hits |
|------|------|
| `http.title:"DocsGPT"` | 8 |
| All port+string dorks | 0 |

### Ragapp

Zero hits across 6 dork variants. Not indexed in Shodan. Either too new or port 8000 crawl coverage is insufficient.

---

## Verification Results

### RAGFlow — 7 confirmed, auth-enforced

Every confirmed RAGFlow instance returned auth enforcement at `/api/v1/datasets`:

```
{"code":0,"data":false,"message":"`Authorization` can't be empty"}
```

The `/api/v1/user/login` login path returned 404 on most hosts — nginx is not routing the request to the backend on port 80, so the backend likely runs on an internal port. This means CVE-2024-12433 could not be tested from the public surface. Auth-on-default holds for the sampled population.

Two hosts (47.87.138.159, 47.90.204.194) returned GitLab HTML to the RAGFlow API paths — FPs, not RAGFlow. One host (8.130.156.155) returned a Chinese medical decision support system branded separately — FP. ~25 IPs in the sample matched the Linode honeypot fleet pattern (AS63949, salt wW0sffoqsk.EM) and were filtered.

Confirmed RAGFlow hosts (auth-enforced):
- 35.187.151.84
- 82.157.0.110
- 91.98.47.114
- 111.119.205.186
- 149.137.233.28
- 116.63.8.130
- 121.41.168.116

### DocsGPT — 0 confirmed

52.89.37.56 returns Celery PENDING responses consistent with the DocsGPT Celery task backend. The `Access-Control-Allow-Origin` header references `https://docsgpt.testnet3.goat.network` — this is a DocsGPT-adjacent deployment (goat.network blockchain testnet), not confirmed DocsGPT. Not labeled.

34.19.189.101 returns React SPA HTML on all /api/* paths — reverse proxy catching all routes, backend not exposed. FP (assistant.mannyroy.com).

### LightRAG — 2 confirmed unauth

---

## Finding 1: LightRAG Server API — config and document exposure

**Host:** 54.249.87.30  
**Hosting:** AWS ap-northeast-1 (ec2-54-249-87-30.ap-northeast-1.compute.amazonaws.com)  
**Platform:** LightRAG Server API v0267  
**Auth mode:** disabled (confirmed from `/health` response field `"auth_mode": "disabled"`)  

### What is exposed

`/health` returns the full runtime configuration without authentication:

```json
{
  "status": "healthy",
  "auth_mode": "disabled",
  "configuration": {
    "llm_binding": "openai",
    "llm_model": "gpt-4",
    "embedding_binding": "openai",
    "embedding_model": "text-embedding-3-small",
    "kv_storage": "PGKVStorage",
    "graph_storage": "PGGraphStorage",
    "vector_storage": "PGVectorStorage"
  },
  "core_version": "1.4.9.11",
  "api_version": "0267"
}
```

`/documents` lists ingested files without authentication. The document store contains AI research content — a Gemini 3 Pro (November 2025) technical writeup was indexed.

`/documents/upload` is exposed. The endpoint requires a `file` parameter but no authentication token. Unauthenticated file injection into the knowledge graph is the attack surface — not tested beyond the 422 parameter-validation boundary.

`/graphs?label=default` is exposed. Returned empty at probe time (graph not yet populated or cleared after failed indexing). The endpoint itself required no auth token.

### Attack surface

The `/query` endpoint connection-reset on POST during this survey. Either firewalled for POST or a transient block. The knowledge graph is queryable when POST is accepted. With document upload and graph label access both unauth, an attacker could poison the knowledge base with injected content and query the poisoned graph — a RAG poisoning chain.

The OpenAI gpt-4 binding is also visible in the health response. If the API key is stored as an env variable on this host, it is not directly readable from the API — but the binding confirms active API key usage, making the host a potential LLMjacking vector if any other unauth RCE surface exists.

### Severity

HIGH (unrated pending further investigation of /query accessibility)

Evidence:
- `/health` config leak: verified
- `/documents` unauth list: verified (document content read)
- `/documents/upload` surface: verified (endpoint reachable, auth not required)
- `/query` accessibility: connection reset — not confirmed functional

---

## Finding 2: LightRAG Medical Pipeline + Video RAG — Pukaar Cry infant health app

**Host:** 35.200.236.6  
**Hosting:** GCP asia-northeast1 (6.236.200.35.bc.googleusercontent.com)  
**Platform (port 8000):** LightRAG Pipeline API v0.1.0 — custom medical wrapper  
**Platform (port 9000):** Video RAG Search API v0.1.0  
**Auth mode:** none on both services  

This is a single GCP host running two separate unauth RAG APIs. The operator is Pukaar Cry, an Indian infant health app (S3 bucket prefix `pukaarcry`, region ap-south-1). Both services are live and unauthenticated.

### Port 8000 — Medical LightRAG Pipeline

The LightRAG wrapper exposes a five-step clinical assessment pipeline for infant diagnosis:

```
/initial-symptoms   — Step 1: critical/emergency condition screening
/red-flag-response  — Step 2: common non-emergency condition identification
/differentiate      — Step 3: top-2 probable conditions with rationale
/in-depth-questions — Step 4: follow-up questions for top conditions
/final-diagnosis    — Step 5: final diagnosis and recommendation
```

The schema accepts `infant_age_months` and `day_of_illness` as required fields alongside symptom arrays. The knowledge base contains medical conditions: intracranial tumors, infectious diseases (diphtheria, encephalitis, rubella, tuberculosis), congenital malformations (Down syndrome, DiGeorge, dextrocardia), pediatric hematologic conditions, neurological disorders, and respiratory conditions.

Unauth LLM query execution confirmed. The `/query` POST returned a full LLM response to a test query with medical KB context, disclosing the breadth of the indexed corpus.

### Port 9000 — Video RAG Search API

A separate FastAPI service returns video content metadata from the Pukaar Cry library. Unauth `/search` POST returns:
- `chunk_text`: content descriptions for infant health education videos
- `video_url`: direct S3 URLs (pukaarcry.s3.ap-south-1.amazonaws.com)
- `thumbnail_url`: direct S3 thumbnail URLs

Sample query `"infant symptoms fever"` returned a video titled "Baby Fever: When to Visit the Doctor vs. When to Wait" with direct media URLs for infants aged 1-3 months.

### What this chain means

An anonymous caller can:
1. Submit infant symptoms to `/initial-symptoms` and walk the full 5-step diagnosis pipeline
2. Search the infant health video library via `/search` without credentials
3. Retrieve S3 media URLs for any content in the video corpus

The S3 URLs are direct — no signed URL expiry was observed in the returned payload format. Bucket policy is not confirmed open, but the API is serving URLs without any access gate.

menlohunt flagged port 9000 as open (MinIO candidate — it is not MinIO, it is the Video RAG service). No attack chain constructed beyond the direct API access surface.

### Severity

HIGH (two unauth RAG APIs; medical context; infant health data; S3 URL exposure confirmed)

Evidence:
- Port 8000 `/query` LLM response: verified
- Port 8000 `/openapi.json` schema: verified (infant_age_months, day_of_illness fields documented)
- Port 9000 `/search` response: verified (video metadata + S3 URLs returned)
- Port 9000 `/openapi.json`: verified

Not labeled CRITICAL: no patient PII confirmed in direct API responses. Medical KB content queried is educational/clinical reference material, not patient records. Severity is HIGH based on verified unauth LLM exec on medical context + S3 URL leak.

---

## Arsenal Coverage

| Tool | Host 1 (54.249.87.30) | Host 2 (35.200.236.6) | Notes |
|------|----------------------|----------------------|-------|
| JAXEN | x — prior pass | x — prior pass | Shodan harvest complete |
| aimap | running on 64-IP corpus | running on 64-IP corpus | Background scan; output pending |
| VisorGraph | No graph nodes returned | No graph nodes returned | No cert pivots found — bare AWS/GCP PTR only |
| aimap-profile | AWS ap-northeast-1, commercial | GCP asia-northeast1, healthcare | Shodan API key expired — fast mode only |
| VisorLog | added #150 HIGH | added #151 HIGH + #152 HIGH | Three findings logged |
| VisorScuba | AI.C1 violation | AI.C1 + AI.H4 violations | Healthcare sector fires AI.H4 |
| BARE | No MSF module coverage (top score 0.416) | No MSF module coverage (top score 0.376) | Novel attack class — no existing msf module |
| menlohunt | N/A (AWS host) | 5 findings — port 9000 HIGH + SSH LOW | Port 9000 Video RAG discovered via menlohunt |
| recongraph | 0 nodes, 0 edges | 0 nodes, 0 edges | No pivot surface via passive graph |
| nu-recon | uvicorn service, public_intended | Port 8000 not reachable on scan port | nu-recon confirms port 80 exposure |
| visorplus assess | passive DNS: 1 hostname | passive DNS: 1 hostname | PTR records only |
| VisorHollow | SKIP — binary-can't-execute | SKIP | |
| VisorAgent | ETHICAL STOP | ETHICAL STOP | Survey set — never run |
| VisorCorpus | N/A | N/A | Not LLM-target-facing |
| VisorBishop | Not installed | Not installed | |
| VisorRAG | ETHICAL STOP | ETHICAL STOP | |

---

## Population Summary

| Platform | Shodan Population | Sampled | Auth Status | Finding |
|----------|------------------|---------|-------------|---------|
| RAGFlow | 1,902 | 50 | Auth-enforced | 7 confirmed; CVE-2024-12433 not testable at port 80 |
| LightRAG | 6 | 6 | 2 unauth / 3 offline / 1 FP | 2 HIGH findings |
| DocsGPT | 8 | 8 | 0 confirmed | 1 probable Celery backend (goat.network); unconfirmed |
| Ragapp | 0 | 0 | Not indexed | Shodan-dark |

---

## Dork Intelligence

**LightRAG discovery path:** Default port 9621 is invisible to Shodan. The Swagger UI (`http.html:"LightRAG" http.html:"swagger"`) is the only working surface. At 5 hits, this is near-complete population coverage. The actual deployment count is larger — any LightRAG instance not running on a Shodan-crawled port is invisible.

**RAGFlow signal:** `http.title:"RAGFlow"` at 1,902 is strong and likely reflects most public deployments. Backend-string dorks add nothing because nginx proxies the frontend but blocks direct API port access at the firewall layer in most deployments.

---

## Pivot Avenues

1. LightRAG Shodan coverage gap: the 9621 default port is not crawled. Any census DNS/PTR sweep against known cloud CIDRs for uvicorn-serving services on 9621 would find the hidden population.
2. Pukaar Cry S3 bucket: `pukaarcry.s3.ap-south-1.amazonaws.com` is directly referenced in video search responses. Bucket policy and object listing warrant a separate passive check.
3. LightRAG PGVectorStorage on 54.249.87.30: the health endpoint confirms PostgreSQL backends for all three storage layers. If the Postgres port is exposed, the graph and vector index are directly readable.
4. LightRAG v0267 auth_mode field: this is a configuration flag, not a hardened default. Other deployments using the same version will have the same field. A dork for the version string in Shodan body could find the broader v0267 population.
5. RAGFlow backend port 9380: Shodan does not index it. A targeted scan of confirmed RAGFlow IPs on 9380 would determine whether the RCE surface (CVE-2024-12433 upload endpoint) is accessible on the internal port from the public internet.

---

## References

- CVE-2024-12433: RAGFlow pre-auth RCE via unauthenticated file upload
- CVE-2025-0868: DocsGPT pre-auth RCE via path traversal
- LightRAG: entity extraction whitelist bypass (no CVE; documented class)
- LightRAG project: github.com/HKUDS/LightRAG
- Insight #35: population-pass yield ~0.03% for targeted investigation
