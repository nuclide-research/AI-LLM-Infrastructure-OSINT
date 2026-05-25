# Insight #56: LangGraph Self-Identifying JSON Root as Primary Fingerprint

**Date codified**: 2026-05-25
**Survey anchor**: LangGraph Server population survey
**File**: `case-studies/commercial/langgraph-server-survey-2026-05-25.md`

---

## The Finding

Every LangGraph Server deployment returns a custom JSON object at the root path (`GET /`). The message field always contains the string "LangGraph" (case-insensitive, in the `message`, `service_type`, `engine`, or `service` key). This is true across the canonical LangChain Python server, Node.js community wrappers, and custom FastAPI builds.

The `x-trace-id` response header appears only on LangChain's own infrastructure (confirmed: 1.15.66.80 only, a 2-host match out of 16). It is a secondary signal, not the primary fingerprint.

**Primary fingerprint (15/16 hosts, 94%):**
```
server: uvicorn
content-type: application/json
body contains: "langgraph" (case-insensitive)
```

**Secondary fingerprint (2/16 hosts, 13%):**
```
header: x-trace-id: <hex32>
```

**Conjunctive fingerprint (both conditions)**: highest precision, lowest recall. Use the primary fingerprint for population sweeps; x-trace-id for LangChain-managed infrastructure detection.

---

## Root Response Examples

```json
{"message":"LangGraph多智能体系统 - LangGraph 对话工作流服务","service_type":"langgraph_workflow_service","version":"1.0.1","environment":"dev"}
{"message":"Docu Companion LangGraph API","version":"3.0.0"}
{"message":"LangGraph Conversational Stock Analyzer API is running"}
{"message":"Vantage Coach API - LangGraph Conversational Agent","version":"1.0.0"}
{"status":"ok","bot":"modengy_v3","engine":"LangGraph"}
{"ok":true,"service":"Sleep Doctor Service","chat_service":"wuji-langgraph"}
{"service":"standalone-langgraph-server","version":"1.0.0"}
{"status":"running","service":"SharePoint Assistant API - LangGraph Agent","version":"2.0.0"}
```

The variety confirms this is not a framework default. Each operator customizes the root message, but "LangGraph" (or a variant) appears in every case. The body is the fingerprint, not the structure.

---

## Why This Matters

The standard Shodan dork (`http.html:"langgraph"`) catches ~500 candidates but includes false positives (landing pages, docs, repos). The body fingerprint from a direct probe cuts false positives to near zero: uvicorn serving JSON with "langgraph" in the body at port 8000 is the deployed server, not a documentation page.

The self-documenting root is a developer convenience. LangGraph server operators return it to make the API discoverable. It is also the exact signal that makes the deployment enumerable at population scale without any path traversal or authentication bypass.

---

## aimap Fingerprint (Current State)

Lines 1635-1653 in `~/ai-recon/aimap/fingerprints.go`: partial fingerprint using `body_contains: ["langgraph"]`. Enhancement needed:

1. Add `header_contains: {"Server": "uvicorn"}` conjunct
2. Add `/info` endpoint probe (returns `{"langgraph_version": "..."}` on canonical server)
3. Add x-trace-id as secondary confirmation signal (not required)
4. Add port 8000 as preferred scan target

The current fingerprint will catch the body signal; adding the uvicorn conjunct reduces FPs from other Python frameworks that mention LangGraph in their API description.

---

## BARE Module Gap

BARE corpus has no LangGraph-specific module. Top semantic matches resolve to Langflow CVE modules (CVE-2025-3248, CVE-2026-27966) because both are LangChain-family Python frameworks. A LangGraph-specific module class should be added to the BARE corpus when a confirmed RCE or auth-bypass CVE is published for LangGraph Server.

---

## Population Signal

LangGraph Server is newer than Ollama or vLLM. The 3.2% live rate (16/499) reflects early-adopter deployment density, not a reduced auth-on-default rate. Auth-on-default is 100% in this survey cohort (0/16 hosts enforced auth at the LangGraph layer). The population will scale as LangGraph adoption grows.
