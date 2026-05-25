---
type: case-study
title: "Chinese Financial LangGraph Agent — Credit Reports, Loans, and an Open Session Store"
date: 2026-05-25
severity: CRITICAL
sector: commercial
tags: [LangGraph, Redis, Langfuse, RAGFlow, financial, PII, China, TencentCloud, agent-framework]
summary: "A Chinese financial services multi-agent system built on LangGraph — running personal credit report and loan extraction workflows — is deployed in development mode with no authentication, with the agent session store directly accessible via Redis Commander."
---

# Chinese Financial LangGraph Agent — Credit Reports, Loans, and an Open Session Store

**Date:** 2026-05-25
**Target:** 1.15.66.80
**ASN:** AS132203 — Tencent Cloud, Shanghai, China
**Severity:** CRITICAL

---

## Context

During the LangGraph Server population survey, one host stood out from the rest. Most exposed LangGraph deployments are generic assistants or research tools. This one names its workflows: `PersonalCreditReportWorkflow`, `LoanProductExtractionWorkflow`, `ConsultantWorkflow`, `GeneralFinancialWorkflow`. The environment is `"dev"`. The host is on Tencent Cloud in Shanghai. All five services on it are internet-facing.

This is not a chatbot. It is a financial data processing pipeline.

---

## What Was Found

### F1 — LangGraph Multi-Agent Financial System, Unauthenticated (CRITICAL)

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

Translation of the message field: "LangGraph multi-agent system — LangGraph conversational workflow service."

Four named workflows are registered. `PersonalCreditReportWorkflow` and `LoanProductExtractionWorkflow` indicate this system processes financial identity data and loan product information. `ConsultantWorkflow` and `GeneralFinancialWorkflow` are advisory layers on top of that data. A second identical instance runs on port 8001 (`X-Trace-Id: 5edd3a13c2ddf3a112248c75035eac72`).

The system is in `"environment": "dev"`. It is on the public internet.

### F2 — Redis Commander Exposes the Agent Session Store (CRITICAL)

Port 8081 serves Redis Commander — a browser-based Redis management UI — with no authentication:

```
GET http://1.15.66.80:8081/
→ HTTP 200
→ Redis Commander: Home   (30KB page, full UI loaded)
```

Redis is the session and state backend for LangGraph agents. Every in-flight and completed agent interaction is stored there: thread IDs, conversation state, intermediate workflow outputs, any PII that passed through the agent between LLM calls. Redis Commander gives a browser interface for reading and writing all of it. No token. No login prompt. The root path loads the full UI.

### F3 — Langfuse LLM Observability, Signup Open (HIGH)

Port 3000 serves Langfuse 3.x with open user registration:

```
GET http://1.15.66.80:3000/
→ HTTP 200  (Langfuse Next.js application)
Content-Security-Policy: default-src 'self' https://*.langfuse.com ...
```

Langfuse records every LLM call made by the agent: the prompt sent, the model response, token counts, latency, and any structured metadata attached to the trace. For a system processing personal credit reports and loan applications, the trace store contains the input data those workflows operated on. Open registration means any external party can create an account on this Langfuse instance and read those traces.

### F4 — RAGFlow Document Intelligence, Port 18080 (HIGH)

Port 18080 serves RAGFlow, an open-source RAG framework with document parsing, knowledge base management, and vector retrieval:

```
GET http://1.15.66.80:18080/
→ HTTP 200  (RAGFlow web application, nginx/1.18.0)
→ <title>RAGFlow</title>   (logo.svg served)
```

RAGFlow's knowledge bases would contain the document corpus the financial workflows retrieve against — potentially loan product documentation, credit scoring reference materials, or uploaded financial records. Auth state on the RAGFlow instance was not further probed.

### F5 — MinIO Object Storage (AUTH ENFORCED)

Port 9090 returns `AccessDenied` on all requests. MinIO is the one layer on this host where authentication is enforced. The agent stack as a whole is not, but the object store is.

---

## Stack Map

| Port | Service | Version | Auth | Severity |
|---|---|---|---|---|
| 8000 | LangGraph (uvicorn) | 1.0.1 | None | CRITICAL |
| 8001 | LangGraph (uvicorn) | 1.0.1 | None | CRITICAL |
| 8081 | Redis Commander | — | None | CRITICAL |
| 3000 | Langfuse | 3.x | Signup open | HIGH |
| 18080 | RAGFlow | — | Unknown | HIGH |
| 9090 | MinIO | — | Enforced | — |
| 8888 | nginx | — | 404 | — |

---

## Attribution

No PTR record. VisorGraph returned 0 nodes, 0 edges (plain HTTP across all ports, no TLS, no certificate to pivot from). TencentCloud AS132203, Shanghai. No reverse DNS beyond the bare IP.

The `x-trace-id` header on LangGraph responses is the only signal that places this deployment on LangChain's own infrastructure pattern rather than a community wrapper. It is the only host in the 16-host survey corpus that returned this header.

---

## Thesis Placement

This is the highest-severity single-host finding in the LangGraph survey. The five-service stack (LangGraph + Redis Commander + Langfuse + RAGFlow + MinIO) is the Pharos-class pattern: multiple unauth services on one host, each one individually significant, collectively giving full visibility into the system's data and state.

The specific combination of `PersonalCreditReportWorkflow` and `LoanProductExtractionWorkflow` by name, in a `"dev"` environment, running on a Chinese financial cloud, with an open session store, is the data-class signal. Financial identity data is being processed by this workflow. The session store is readable.

**See also:** [LangGraph Server Survey (2026-05-25)](langgraph-server-survey-2026-05-25.md) · [LangGraph Deployment Gap — Systematic Pattern](langgraph-deployment-gap-survey-2026-05-25.md)
