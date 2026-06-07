---
type: case-study
title: "FAIS MCP Server: Dual-Node Workflow Tool API Open Without Authentication"
date: 2026-05-25
severity: HIGH
sector: commercial
tags: [MCP, ModelContextProtocol, DotNet, SemanticKernel, Kestrel, workflow, Azure, dual-node]
summary: "Two identical FAIS MCP Server instances on Azure Pune expose their full tool API without authentication. Three workflow tools are open on both nodes: GetAllWorkflows, GetWorkflowConfiguration, and GetWorkflowLogsByTransaction. Any caller can enumerate organizations, retrieve workflow configurations, and query execution logs by workflow and transaction ID."
---

# FAIS MCP Server: Dual-Node Workflow Tool API Open Without Authentication

**Date:** 2026-05-25
**Hosts:** 4.187.183.11, 4.187.178.249
**Cloud:** Microsoft Azure (AS8075), Pune, India
**App:** FAIS MCP Server (FAIS Backend System, Powered by .NET and Semantic Kernel)
**Severity:** HIGH

---

## What Was Found

### F1 — Full Tool API Open Without Authentication on Both Nodes (HIGH)

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, S7075
- **733 (AI Risk & Ethics Specialist):** K7051
- **overlap (Common AI KSATs (all 5 roles)):** K1158, K22, K6311, K6935, K7003, K942

<!-- ksat-tag:auto-generated:end -->

Both hosts expose identical API surfaces without credentials. Port 80. Server: Kestrel (.NET runtime).

```
GET  /              → FAIS MCP Server landing page
GET  /api/tools     → full tool catalog (3 tools)
GET  /api/tools/health → {"success":true,"status":"healthy","toolCount":3,"timestamp":"..."}
```

`Last-Modified: Fri, 22 May 2026` on both nodes.

### F2 — Three Workflow Tools Exposed (HIGH)

```
GET /api/tools →
{
  "success": true,
  "count": 3,
  "tools": [
    {
      "name": "GetAllWorkflows",
      "description": "Gets a list of all workflow configurations available for a specific organization",
      "parameters": { "organizationId": {"type":"string", "required": true} }
    },
    {
      "name": "GetWorkflowConfiguration",
      "description": "Gets the detailed configuration for a specific workflow by ID",
      "parameters": {
        "workflowId": {"type":"string", "required": true},
        "organizationId": {"type":"string", "required": false}
      }
    },
    {
      "name": "GetWorkflowLogsByTransaction",
      "description": "Find recent workflow execution logs for a workflow ID that include a specific transaction ID",
      "parameters": {
        "workflowId": {"type":"string", "required": true},
        "transactionId": {"type":"string", "required": true},
        "limit": {"type":"integer", "default": 25}
      }
    }
  ]
}
```

`GetAllWorkflows` takes an `organizationId` and returns all workflows for that organization. `GetWorkflowLogsByTransaction` returns execution logs including transaction IDs. `GetWorkflowConfiguration` returns full workflow configuration by ID. We confirmed the tool schemas. We did not call the tools against live data.

### F3 — Dual-Node Deployment, Identical Surface (MEDIUM)

4.187.183.11 and 4.187.178.249 return identical responses and identical tool schemas. Both carry the same `Last-Modified` timestamp. Both are on port 80. We found no load balancer or shared domain on public surfaces.

---

## Stack

Kestrel HTTP server (.NET runtime). Microsoft Semantic Kernel referenced in landing page. MCP (Model Context Protocol) tool format, using the OpenAI function-call schema for tool definitions. Azure Pune IN (Microsoft Corporation AS8075). Port 80. No TLS.

---

## Failure Mode

The MCP tool API is open without authentication. Any caller who knows the organization ID can enumerate all workflows for that organization. Any caller who knows a workflow ID can retrieve full workflow configuration. Execution logs are queryable by workflow and transaction ID.

The `Last-Modified` timestamp is 2026-05-22. The deployment runs on two nodes. We found no staging markers.

---

## Operator Attribution

"FAIS" appears in the application name and landing page. No domain in HTTP headers. No PTR on either IP. Both resolve to Microsoft Corporation AS8075, Pune, India region. Operator identity not confirmed from public surface.
