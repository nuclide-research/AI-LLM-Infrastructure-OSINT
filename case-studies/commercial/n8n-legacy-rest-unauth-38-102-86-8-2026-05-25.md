---
type: case-study
title: "n8n 1.120.0: Legacy REST API Open, Production Billing Backup Workflow Exposed"
date: 2026-05-25
severity: HIGH
sector: commercial
tags: [n8n, workflow-automation, AWS-S3, billing, legacy-api, Canada, Cogent, Rica-Web-Services]
summary: "n8n 1.120.0 on port 5678 at 38.102.86.8 exposes its legacy /rest/ API without authentication. A single active production workflow — billing-backup-to-s3 — is enumerable, including node type and tags. The newer /api/v1/ path enforces auth; the /rest/ path does not."
---

# n8n 1.120.0: Legacy REST API Open, Production Billing Backup Workflow Exposed

**Date:** 2026-05-25
**Host:** 38.102.86.8
**ASN:** AS174 Cogent Communications / Rica Web Services (Servarica), Canada
**App:** n8n Workflow Automation 1.120.0
**Severity:** HIGH

---

## What Was Found

### F1 — Unauthenticated Access via Legacy `/rest/` API (HIGH)

`GET /rest/workflows` returns workflow data. No credentials.

```
GET /api/v1/workflows  →  404  (public API disabled: "publicApi": {"enabled": false})
GET /rest/workflows    →  200  [workflow data returned]
```

The public API module is disabled. The `/api/v1/` routes do not exist. The `/rest/` path — the internal API the n8n frontend calls directly — carries no auth gate. Version 1.120.0 ships with user management configured (`showSetupPage: false`). The legacy REST surface is not covered.

### F2 — Production Billing Workflow Enumerable (HIGH)

```
GET /rest/workflows →
{
  "data": [{
    "id": "cxBackupFlow01",
    "name": "billing-backup-to-s3",
    "active": true,
    "tags": ["prod", "billing", "backup"],
    "createdAt": "2026-02-20T11:11:00.000Z",
    "updatedAt": "2026-02-27T02:41:22.000Z"
  }]
}
```

One workflow. Active. Tagged `prod`, `billing`, `backup`. Single node: `n8n-nodes-base.awsS3` (AWS S3 Upload).

### F3 — Execution History Open (HIGH)

```
GET /rest/executions →
{
  "data": [{
    "id": 484021,
    "finished": true,
    "workflowId": "cxBackupFlow01",
    "startedAt": "2026-02-27T19:03:59.180Z"
  }]
}
```

One logged execution. Completed 2026-02-27. No credentials required.

### F4 — Instance Settings Exposed (MEDIUM)

```
GET /rest/settings →
{
  "versionCli": "1.120.0",
  "instanceId": "3c3901f3f0a247d5a2c8ef4b06cde0a9",
  "telemetry": {"enabled": true},
  "userManagement": {"quota": 50, "showSetupPage": false},
  "publicApi": {"enabled": false, "latestVersion": 1},
  "executionMode": "regular"
}
```

Instance ID disclosed. Telemetry enabled. Public API disabled. The only open surface is the legacy `/rest/` path.

---

## Stack

nginx/1.24.0 reverse proxy. n8n/1.120.0 backend (`X-Powered-By: Express`). Port 5678. Port 443 carries a VMware ESXi default certificate (`localhost.localdomain`, self-signed). The n8n service and the ESXi interface share the same IP.

---

## Failure Mode

n8n 1.120.0 enforces auth on `/api/v1/`. The `/rest/` endpoints are the internal API the n8n frontend calls directly. The two surfaces have separate auth middleware. User management is configured. The `/rest/` surface is not covered.

The billing-backup-to-s3 workflow has one execution. The S3 credential is in n8n's encrypted store. The REST metadata endpoints do not expose it. Node parameters were not retrieved.

---

## Operator Attribution

Rica Web Services (Servarica), Canada. AS174 Cogent Communications transit. No domain in HTTP headers or TLS certificate. PTR record not set. Operator identity not confirmed from public surface.
