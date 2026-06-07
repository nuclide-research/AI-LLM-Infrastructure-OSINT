---
type: case-study
title: "Chinese Financial LangGraph Agent — Credit Reports, Loans, and an Open Session Store"
date: 2026-05-25
severity: CRITICAL
sector: commercial
tags: [LangGraph, Redis, Langfuse, RAGFlow, financial, PII, China, TencentCloud, agent-framework]
summary: "A Chinese financial services multi-agent system on LangGraph runs credit report and loan extraction workflows in development mode with no authentication. The agent session store is accessible via Redis Commander on port 8081."
---

# Chinese Financial LangGraph Agent — Credit Reports, Loans, and an Open Session Store

**Date:** 2026-05-25
**Target:** 1.15.66.80
**ASN:** AS132203, Tencent Cloud, Shanghai, China
**Severity:** CRITICAL

---

## What Was Found

### F1 — LangGraph Multi-Agent Financial System, Unauthenticated (CRITICAL)

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7004, S7068, S7070, S7075, T5904
- **733 (AI Risk & Ethics Specialist):** K7040, K7051, T5854, T5868, T5882
- **overlap (Common AI KSATs (all 5 roles)):** K1158, K22, K6311, K6935, K7003

<!-- ksat-tag:auto-generated:end -->

Port 8000 responds without authentication:

```
GET http://1.15.66.80:8000/
→ HTTP 200
→ {
    "message": "LangGraph多智能体系统 - LangGraph 对话工作流服务",
    "service_type": "langgraph_workflow_service",
    "version": "1.0.1",
    "environment": "dev",
    "docs": "/docs",
    "health": "/health",
    "api_prefix": "/api/v1",
    "endpoints": {
      "consultant_chat_stream": "/api/v1/consultant/chat/stream",
      "consultant_health":      "/api/v1/consultant/health",
      "general_financial_chat_stream": "/api/v1/financial/chat/stream",
      "general_financial_health":      "/api/v1/financial/health",
      "loan_product_extraction_extract": "/api/v1/loan-product/extract",
      ...
    }
  }
```

Response header: `X-Trace-Id: ad905d34f31443af3eb4b5bbc4701afd`

Translation: "LangGraph multi-agent system — LangGraph conversational workflow service."

Four named workflows are registered. `PersonalCreditReportWorkflow` and `LoanProductExtractionWorkflow` process financial identity data and loan products. `ConsultantWorkflow` and `GeneralFinancialWorkflow` are advisory layers on that data. A second identical instance runs on port 8001 (`X-Trace-Id: 5edd3a13c2ddf3a112248c75035eac72`).

The environment is `"dev"`. The host is on the public internet. This is a financial data processing pipeline.

### F2 — Redis Commander Exposes the Agent Session Store (CRITICAL)

Port 8081 serves Redis Commander, a browser-based Redis management UI, with no authentication:

```
GET http://1.15.66.80:8081/
→ HTTP 200
→ Redis Commander: Home   (30KB page, full UI loaded)
```

Redis is the session and state backend for LangGraph agents. Every agent interaction is stored there: thread IDs, conversation state, workflow outputs, any PII that passed through between LLM calls. Redis Commander gives a browser interface for reading and writing all of it. No token. No login prompt. The root path loads the full UI.

### F3 — Langfuse LLM Observability, Signup Open (HIGH)

Port 3000 serves Langfuse 3.x with open user registration:

```
GET http://1.15.66.80:3000/
→ HTTP 200  (Langfuse Next.js application)
Content-Security-Policy: default-src 'self' https://*.langfuse.com ...
```

Langfuse records every LLM call: the prompt, the model response, token counts, latency, and any metadata on the trace. Any external party can create an account on this instance and read those traces. For a system running `PersonalCreditReportWorkflow` and `LoanProductExtractionWorkflow`, those traces hold the inputs those workflows processed.

### F4 — RAGFlow Document Intelligence, Port 18080 (UNRATED — Auth Not Probed)

Port 18080 serves RAGFlow, a RAG framework with document parsing, knowledge base management, and vector retrieval:

```
GET http://1.15.66.80:18080/
→ HTTP 200  (RAGFlow web application, nginx/1.18.0)
→ <title>RAGFlow</title>   (logo.svg served)
```

We did not probe the RAGFlow auth state. The knowledge bases could include loan product documentation, credit scoring materials, or uploaded financial records. Auth state requires a follow-up probe before severity is assigned.

### F5 — MinIO Object Storage (AUTH ENFORCED)

Port 9090 returns `AccessDenied` on all requests. MinIO enforces authentication. The rest of the stack does not.

---

## Stack Map

| Port | Service | Version | Auth | Severity |
|---|---|---|---|---|
| 8000 | LangGraph (uvicorn) | 1.0.1 | None | CRITICAL |
| 8001 | LangGraph (uvicorn) | 1.0.1 | None | CRITICAL |
| 8081 | Redis Commander | — | None | CRITICAL |
| 3000 | Langfuse | 3.x | Signup open | HIGH |
| 18080 | RAGFlow | — | Not probed | UNRATED |
| 9090 | MinIO | — | Enforced | — |
| 8888 | nginx | — | 404 | — |

---

## Attribution

No PTR record. VisorGraph returned 0 nodes, 0 edges. Plain HTTP across all ports. No TLS, no certificate to pivot from. TencentCloud AS132203, Shanghai.

The `x-trace-id` header on LangGraph responses is the only signal tying this deployment to LangChain's own infrastructure pattern. It is the only host in the 16-host survey corpus that returned this header.

---

## Thesis Placement

This host is the highest-severity finding in the LangGraph survey. The five-service stack is the Pharos-class pattern: multiple unauth services on one host, each individually confirmed, collectively giving full read/write access to the system's data and state.

The workflow names confirm the data class. `PersonalCreditReportWorkflow` and `LoanProductExtractionWorkflow`, in a `"dev"` environment, with an open session store. This workflow processes financial identity data. The session store is readable.

**See also:** [LangGraph Server Survey (2026-05-25)](langgraph-server-survey-2026-05-25.md) · [LangGraph Deployment Gap — Systematic Pattern](langgraph-deployment-gap-survey-2026-05-25.md)
