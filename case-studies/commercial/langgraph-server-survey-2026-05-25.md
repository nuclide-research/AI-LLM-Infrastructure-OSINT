---
type: survey
---

# LangGraph Server Population Survey (2026-05-25)

_NuClide Research · 2026-05-25_
_Category 06: Agent-framework stragglers. First survey of LangGraph Server tier._

---

## Summary

Population-scale survey of LangGraph Server deployments. LangGraph is LangChain's stateful multi-agent execution runtime. The canonical server ships on FastAPI/uvicorn (port 8000) with no authentication by default. Community wrappers (Node.js, custom Python) follow the same pattern.

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7004, K7044, S7068, S7070, S7075, T5858, T5904, T5919
- **733 (AI Risk & Ethics Specialist):** K7040, K7051, S7056, T5854, T5868, T5893
- **overlap (Common AI KSATs (all 5 roles)):** K1158, K1159, K22, K6311, K6935, K7003, S7065, T5896

<!-- ksat-tag:auto-generated:end -->

Shodan harvest across two dorks: `http.html:"langgraph"` (499 hits), `http.title:"LangGraph"` (51 hits). Manual harvest via Playwright (Shodan API quota exhausted). Probed 16 confirmed unauth hosts.

- **16 confirmed unauthenticated LangGraph deployments**
- **7 stacked-exposure hosts**: LangGraph collocated with at least one additional unauth service
- **4 distinct deployment templates** visible across the corpus
- **0 hosts with auth enforced at the LangGraph layer** (100% auth-on-default)

**Top findings by severity:**

| Host | Severity | Stack | Notes |
|---|---|---|---|
| 1.15.66.80 | CRITICAL | LangGraph + Langfuse + Redis Commander + MinIO | Chinese financial multi-agent system, dev mode |
| 72.56.96.229 | CRITICAL | LangGraph + n8n + Qdrant | Three-layer unauth: orchestration + agent + vector store |
| 46.224.86.76 | CRITICAL | LangGraph (Node.js) | Stream execution endpoints unauth, CORS: * |
| 51.15.237.90 / 51.158.97.152 | HIGH | LangGraph (×2) | PII scraper: emails, phones, geo per extraction workflow |
| 138.219.43.172 | HIGH | LangGraph + Ollama + MinIO | Embedding backend fully exposed alongside agent API |
| 157.180.21.126 / 37.27.88.127 / 5.75.229.153 | HIGH | LangGraph + Qdrant (×3) | Same Docu Companion template, 121 user conversations each |

---

## Anchor Finding: Chinese Financial Multi-Agent System (1.15.66.80)

TencentCloud, Shanghai. Port 8000 returns:

```json
{
  "message": "LangGraph多智能体系统 - LangGraph 对话工作流服务",
  "service_type": "langgraph_workflow_service",
  "version": "1.0.1",
  "environment": "dev",
  "endpoints": {
    "consultant_chat_stream": "/api/v1/consultant/chat/stream",
    "general_financial_chat_stream": "/api/v1/financial/chat/stream",
    "loan_product_extraction_extract": "/api/v1/loan-product/extract",
    ...
  }
}
```

Response header: `X-Trace-Id: ad905d34f31443af3eb4b5bbc4701afd`

Four named workflows exposed: PersonalCreditReportWorkflow, LoanProductExtractionWorkflow, ConsultantWorkflow, GeneralFinancialWorkflow. Environment is `"dev"`. No authentication at any layer.

**Stacked services on same host:**

| Port | Service | Auth | Finding |
|---|---|---|---|
| 8000 | LangGraph (uvicorn) | None | Financial agent API, dev mode |
| 8001 | LangGraph (uvicorn) | None | Second agent instance |
| 3000 | Langfuse 3.x | Signup open | LLM observability, trace store |
| 8081 | Redis Commander | None | Direct read/write to agent session store |
| 9090 | MinIO | Access Denied | Object storage, auth enforced |
| 18080 | nginx/1.18.0 | Open | Static/proxy layer |

Redis Commander on port 8081 is the highest-severity secondary surface. It provides a browser-based GUI for the Redis instance backing the LangGraph agent session store. No authentication required.

**Attribution**: No PTR record. VisorGraph returned 0 nodes, 0 edges (plain HTTP, no TLS, no cert to pivot). Tencent Cloud AS132203.

---

## Pattern A: Docu Companion Template Cluster

Three hosts running identical LangGraph + Qdrant stacks:

| Host | ASN | Qdrant version | user_conversations points |
|---|---|---|---|
| 157.180.21.126 | Hetzner (Hel1) | 1.14.1 (`530430fa`) | 121 |
| 37.27.88.127 | Hetzner (Fsn1) | 1.14.1 (`530430fa`) | 121 |
| 5.75.229.153 | Hetzner | 1.14.1 (`530430fa`) | 121 |

All three respond: `{"message":"Docu Companion LangGraph API","version":"3.0.0"}`. All three run Qdrant 1.14.1 at **the same Git commit** (`530430fac2a3ca872504f276d2c91a5c91f43fa0`). Each exposes a `user_conversations` Qdrant collection with 121 points plus 10 or more `knowledge_*` collections (RAG knowledge bases).

Identical commit hash across three separate Hetzner VPSes means these are provisioned from the same Docker Compose template. The `user_conversations` count (121) is also identical across all three, suggesting shared seed data or a replicated state. A single disclosure to the Docu Companion operator covers all three nodes.

---

## Pattern B: PII Extraction Service (Collector Scraper API)

Two OVH hosts (51.15.237.90, 51.158.97.152) return identical responses:

```json
{
  "message": "Collector Scraper API",
  "version": "2.0.0",
  "features": [
    "Enhanced phone extraction with regex and phonenumbers library",
    "Fast email extraction with optimized regex",
    "LangGraph-based extraction workflow",
    "Multi-strategy field extraction",
    "Geographic location detection",
    "Cluster-based country detection"
  ]
}
```

The service scrapes emails, phone numbers, and geographic location from target URLs using a LangGraph multi-step workflow. Both nodes are unauth. The `/docs` Swagger endpoint exposes the full extraction API schema. Two-node deployment from the same operator.

---

## Pattern C: Three-Layer Unauth Agent Stack (72.56.96.229)

DigitalOcean, US. Three services, none authenticated:

| Port | Service | Version |
|---|---|---|
| 5678 | n8n | (web UI, login page accessible) |
| 8000 | LangGraph (modengy_v3) | `{"status":"ok","bot":"modengy_v3","engine":"LangGraph"}` |
| 8001 | LangGraph (uvicorn) | second instance |
| 6333 | Qdrant | 1.13.4, collection: `modengy` |

n8n is the workflow orchestration layer above LangGraph. The agent pipeline runs from n8n (trigger/scheduler) through LangGraph (agent execution) to Qdrant (vector retrieval). All three layers are exposed without authentication. n8n's unauth surface includes its credential store, workflow definitions, and execution history.

---

## Pattern D: Node.js LangGraph Wrapper (46.224.86.76)

Express/Node.js implementation of a LangGraph server wrapper. Root response:

```json
{
  "service": "standalone-langgraph-server",
  "version": "1.0.0",
  "endpoints": {
    "threads": "POST /threads",
    "threadStatus": "GET /threads/:threadId",
    "streamRun": "POST /threads/:threadId/runs/stream",
    "waitRun": "POST /threads/:threadId/runs/wait"
  }
}
```

CORS header: `Access-Control-Allow-Origin: *`. The `/threads/:threadId/runs/stream` and `/threads/:threadId/runs/wait` endpoints are write/execute surfaces. An unauthenticated caller can create threads and trigger agent runs. This is a community-built alternative to the standard LangGraph Python server; the self-documenting root is a community convention, not an LangChain default.

---

## Cert Attribution

| Host | CN (via VisorGraph) |
|---|---|
| 51.83.237.63 | `admin.allergiescleanedbowled.com` (Let's Encrypt, E7) |
| 43.143.225.104 | `www.aiweather.top` (Let's Encrypt, R11) |

`admin.allergiescleanedbowled.com` is the SharePoint Assistant API noted in the previous session. The domain is a plausibly-generated placeholder name, no registrant linkage to a known operator. `aiweather.top` is a Chinese AI weather/outfit recommendation service.

---

## Arsenal Results

| Tool | Result |
|---|---|
| JAXEN | Manual Shodan harvest (API quota exhausted). 16 confirmed unauth in `/tmp/shodan-langgraph-hits.txt` |
| aimap | 66 open ports across 16 hosts. LangGraph on 8000 confirmed by uvicorn + JSON body match |
| VisorGraph | 16/16 processed. Cert attribution on 2 hosts (allergiescleanedbowled, aiweather.top) |
| aimap-profile | 7 profiles. All bare-IP TencentCloud/DO/Hetzner, no Shodan passive (API key expired) |
| JS-bundle | Skipped for batch. Flutter SPA on 20.193.252.230:80 noted (no hidden API surface) |
| VisorLog | 66 events ingested to nuclide.db |
| VisorScuba | 22,020 Critical nodes (full DB assessment, not survey-specific) |
| BARE | 9 findings ranked. Top match: `exploits_multi_http_langflow_rce_cve_2026_27966` (score 0.364). BARE has no LangGraph-specific module; Langflow modules match semantically (LangChain-family) |
| VisorCorpus | 26KB corpus built. Profile: strict, type: baseline, includes kb_exfiltration/system_prompt/config_secrets |
| VisorPlus | Per-host assess logs in `/recon/langgraph-2026-05-25/visorplus/` |
| VisorSD | [NULL] Shodan API key exhausted. No results |
| VisorGoose | [N/A] TLD/gov/academic domain scanner; survey corpus is raw IPs |
| menlohunt | Ran on 20.193.252.230 (Azure host). 11 findings, all GCP metadata FPs (catch-all SPA returns HTTP 200 on all paths). PostgreSQL 5432 open confirmed HIGH. WireGuard candidates (UDP, unverified) |
| nu-recon | [SIMULATED] bare-IP host, no PTR record. Output is placeholder |
| recongraph | 0 nodes, 0 edges on 1.15.66.80. Expected: plain HTTP, no TLS, no PTR |
| VisorRAG | 5 recall files written |
| VisorBishop | 5 targets. 1 PostHog signal (1.15.66.80, via Langfuse telemetry). 4 no match |
| cortex | [DEFERRED] Takes markdown case study as input; will run on this file post-publish |
| VisorHollow | [N/A] Windows-only |
| VisorAgent | [ETHICAL STOP] Not fired against survey hosts. Corpus built; run against controlled target |

---

## menlohunt FP Note

menlohunt classified the Flutter SPA on 20.193.252.230 as "GCP Metadata API: full instance metadata" (CRITICAL). Evidence body was `<!DOCTYPE html>...Flutter base href placeholder...`. The host returns HTTP 200 for all paths (catch-all SPA). This extends Insight #16 (menlohunt status-code FP class): any catch-all serving 200 on arbitrary paths will fire all GCP metadata checks. The fix requires response body to match GCP metadata JSON schema, not just status code.

---

## Methodology Placement

LangGraph Server joins the Tier-A "no auth concept in framework default" list. The `langchain-langgraph-api` PyPI package (the core server component) has no authentication configuration in its default startup. The pattern is structurally identical to Ollama: install, run, port open, world-readable.

**Auth-on-default population yield**: 16 confirmed unauth from 499 candidates (3.2% live rate). Lower than Ollama (16K) or vLLM because LangGraph Server is newer and less deployed at scale. The absolute count will grow as LangGraph adoption increases; this survey captures the early-deployment cohort.

See [Insight #56](../../methodology/insight-56-langgraph-self-identifying-json-fingerprint.md).

---
