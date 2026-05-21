---
title: "Embedding Services Survey — Tier-2 Cloud (2026-05-21)"
category: embedding-services
survey_date: 2026-05-21
status: in-progress
hosts_confirmed: 1
---

# Embedding Services Survey — Tier-2 Cloud

**Date:** 2026-05-21  
**Category:** 27 — Embedding Services (TEI, infinity-embedding, custom FastAPI)  
**Scope:** Tier-2 cloud IP ranges (Scaleway/OVH/Hetzner/DigitalOcean) + masscan ports 7997,8000,8001,8002,8080,3000  
**Tool chain:** JAXEN→aimap→VisorPlus→VisorGraph→aimap-profile→TOME→VisorLog→BARE→VisorCorpus  

---

## Discovery

**Masscan:** 6,544 open ports across tier-2 cloud prefixes (~3.5M IPs). Port distribution: 8080 (2,577), 8000 (1,396), 3000 (1,334), 8001 (504), 8002 (399), 7997 (334).

**embed-probe.py:** 0 of 6,526 targets confirmed as embedding services. Port-7997 hits (target: infinity-embedding) were stale — masscan scan time vs probe time gap. Port-8080/8000 hits were generic web servers.

**aimap batch:** Running against 6,273 unique IPs. Results pending.

**JAXEN:** Shodan search credits exhausted on both API keys (monthly reset). JAXEN `import --no-lookup` populated masscan data into empire.db; discovery dorks unavailable.

---

## Confirmed Host: 46.4.204.44

**Operator:** Hetzner Online GmbH, Köln, Germany (AS24940)  
**Hostname:** `static.44.204.4.46.clients.your-server.de` (bare Hetzner default — no custom domain)  
**GreyNoise:** No data  
**Discovery:** Shodan passive via TOME scan / Shodan host API  

### Surface Map

| Port | Service | Auth | Finding |
|------|---------|------|---------|
| 8001 | Custom FastAPI embedding (uvicorn) | none | Full vector extraction, model info disclosed |
| 9000 | OpenVINO Model Server 2026.0.0 | none | Model list exposed, backend inference accessible |
| 22 | OpenSSH | key | — |

### Port 8001 — Unauth Embedding API

Root response:
```json
{"status":"healthy","model_loaded":true,"model_name":"BAAI/bge-m3",
 "embedding_dimension":1024,"backend":"openvino-int8-throughput","parallel_streams":0}
```

OpenAPI schema (`/openapi.json`): "OpenVINO INT8 Embedding Service" v2.0.0  
Endpoints: `POST /embed` (single text), `POST /embed/batch` (list)  
CORS: `*` (all origins)  
Auth: none

Verified — `POST /embed {"text":"test"}` returns 1024-float vector.

### Port 9000 — OpenVINO Model Server (Backend Exposed)

```json
GET /v1/config → {"bge-m3":{"model_version_status":[{"version":"1","state":"AVAILABLE"}]}}
GET /v1/models/bge-m3/metadata → TF Serving SignatureDef with input tensor shapes
```

OVMS version: 2026.0.0.4d3933c5c  
Model: `bge-m3` (BAAI/bge-m3), input tensors: `input_ids`, `attention_mask`, `token_type_ids` (all DT_INT64, dynamic shape)  
CORS: `*`  
Auth: none

### Attack Surface

1. **Unlimited embedding extraction** — no rate limiting, no auth, CORS wildcard. Any origin can POST text and receive BAAI/bge-m3 embeddings at Hetzner bandwidth.

2. **OVMS backend directly reachable** — bypasses the FastAPI wrapper. TF Serving predict API accepts raw tokenized input. Adversary with tokenized inputs can infer directly against the backend model without going through the wrapper's input validation.

3. **Model architecture disclosure** — full input tensor spec, serving version string, quantization level (INT8), backend runtime (OpenVINO) all exposed without auth.

### Tool Chain Results

**aimap:** `Embedding API` at 8001, `severity=medium`, `auth_status=none`. FastAPI wrapper correctly identified.

**TOME:** 17 platforms scanned (passive); all confidence=0 — embedding-api and openvino-model-server are not in the TOME corpus (tracked as gap — add `platforms/embedding-api.json`, `platforms/openvino-model-server.json`).

**VisorPlus:** Hetzner AS24940, GreyNoise clean, passive DNS 1 hostname (Hetzner default), no domain.

**VisiorGraph:** No TLS cert (HTTP-only on both ports). No cert pivot surface.

**aimap-profile:** `unclassified` — Hetzner bare VPS, 1 distinct hostname, no multi-tenant signals. Research or personal deployment.

**BARE module ranking:**
- Port 8001: `auxiliary_server_capture_imap` (0.448), `auxiliary_scanner_openvas_openvas_otp_login` (0.439) — no specific embedding API module in corpus
- Port 9000: `exploits_linux_http_ollama_rce_cve_2024_37032` (0.369) — inference backend analogy match

**VisorScuba:** 37 nodes assessed in nuclide.db post-ingest.

**VisorCorpus:** 26KB adversarial corpus built (kb_exfiltration, system_prompt, config_secrets).

---

## Corpus Gaps Identified

Two platforms needed in the TOME corpus:

1. **embedding-api** — Custom FastAPI wrapper pattern: root GET returns JSON with `embedding_dimension`, `model_name`, `backend` fields. Probe path `/`, matcher `json_field:embedding_dimension`. Default port 8001.

2. **openvino-model-server** — OVMS: `/v1/config` returns model version status. `/v1/models/{name}/metadata` returns TF Serving SignatureDef. Default port 9000.

---

## Dork Catalog

| Dork | Platform | Precision | 2026-05-21 result |
|------|---------|-----------|-------------------|
| `http.html:"embedding_dimension"` | Custom FastAPI | high | credits exhausted |
| `http.html:"Infinity Emb"` | infinity-embedding | high | credits exhausted |
| `http.html:"model_pipeline_tag"` | HuggingFace TEI | high | credits exhausted |
| `port:7997` | infinity-embedding | medium | 334 masscan hits, 0 confirmed live |
| `http.html:"OpenVINO Model Server"` | OVMS | high | not tested |
| `http.html:"bge-m3"` | BAAI embedding | medium | not tested |

---

## Next Steps

- [ ] Wait for aimap batch (6,273 IPs) to complete → parse embedding service findings
- [ ] Add Hetzner `46.4.0.0/16` to tier2-ranges.txt for future masscan runs
- [ ] Add HTTPS support to embed-probe.py (aiohttp + SSL)
- [ ] Add `embedding-api.json` and `openvino-model-server.json` to TOME corpus
- [ ] Re-run Shodan dorks when credits reset (monthly)
- [ ] Run full arsenal on any additional confirmed hosts from aimap batch
