---
type: case-study
title: "Chinese Sleep Doctor App — WeChat Health Data Open by Design, 9,244 Request Logs Exposed"
date: 2026-05-25
severity: HIGH
sector: commercial
tags: [LangGraph, FastAPI, WeChat, health-data, PII, China, TencentCloud, sleep-sensor, root-deployment]
summary: "A Chinese WeChat Mini Program backend for sleep health diagnostics runs on TencentCloud Beijing with no authentication. Sleep sensor data is accessible by WeChat openid. 9,244 request logs containing user identifiers, health responses, and client IPs are readable without credentials."
---

# Chinese Sleep Doctor App — WeChat Health Data Open by Design, 9,244 Request Logs Exposed

**Date:** 2026-05-25
**Target:** 82.156.182.216
**ASN:** AS45090, Tencent Cloud, Beijing, China
**Severity:** HIGH

---

## What Was Found

### F1 — Sleep Health Data Accessible by WeChat OpenID (HIGH)

Sleep health data is readable without credentials. Port 8000 runs a FastAPI/LangGraph service identifying itself as "Sleep Doctor Service" with `chat_service: "wuji-langgraph"`. The backend serves a WeChat Mini Program.

The primary data endpoint:

```
GET /api/sleep_analysis/{openid}
→ HTTP 200
→ sleep health analysis for that user
```

WeChat openids are user-stable identifiers issued per app per user. They are not secrets. Any party who has seen a user's openid can pull their full sleep analysis. The openapi.json confirms the endpoint. The data class includes AHI trends, sleep stages, heart rate, HRV, respiratory rate, and sleep scores.

6 additional data endpoints follow the same pattern, keyed by hash or unionid:

```
POST /api/health_sleep_profile_by_hash
POST /api/sleep_issue_diagnosis_by_hash
POST /api/sleep_report_by_hash
POST /api/user_sleep_experience_by_hash
POST /api/user_profile_by_hash
POST /api/wake_stage_by_hash
```

The log exposure below surfaces the hash and unionid values.

### F2 — 9,244 Request Logs, No Auth (HIGH)

```
GET /api/monitor/logs
→ HTTP 200
→ 9,244 entries, 36.9MB JSONL
→ /root/sleepDoctor/logs/api_monitor_logs.jsonl
```

Each log entry contains timestamp, method, endpoint, status code, duration, hash, username, request body, response body, and client IP. Of 7,610 total requests, 6,712 succeeded. Successful records carry user hash, openid, inline sleep data, and the client IP of every requester.

This is the bridge. The log supplies the identifiers. The data endpoints accept those identifiers. The chain requires no credentials at either step.

The log also records researcher probes. Our own IP (136.37.103.3) appears in the file. Any party who accessed this server is traceable.

The monitor layer also exposes 2 write operations:

```
POST /api/monitor/clear    — truncates the log file
POST /api/monitor/reload_cache
```

Neither requires authentication.

### F3 — Service Statistics Open (MEDIUM)

```
GET /api/monitor/stats
→ {"total_requests": 7610, "success_count": 6712, "error_count": 898, "avg_response_time": 2202.6}
```

Confirms production usage. 7,610 real requests processed. Average response time of 2,202ms suggests active LangGraph inference, not idle staging.

### F4 — Root Deployment, File Paths Disclosed (LOW)

```
GET /api/monitor/file_info
→ log_path:   /root/sleepDoctor/logs/api_monitor_logs.jsonl
→ stats_path: /root/sleepDoctor/logs/api_monitor_stats.json
```

The service runs as root. Deployment path is `/root/sleepDoctor/`. Any code execution surface in this stack starts with root-level access.

---

## Stack Map

| Port | Service | Auth | Severity |
|---|---|---|---|
| 8000 | FastAPI/LangGraph "Sleep Doctor Service" | None | HIGH |
| 8000/api/monitor/logs | JSONL request log (9,244 entries) | None | HIGH |
| 8000/api/monitor/clear | Log truncation | None | HIGH |

---

## Data Classification

Sleep sensor metrics from a wearable device: AHI (apnea-hypopnea index), sleep stages, heart rate, HRV, respiratory rate, body temperature, humidity, sleep scores, and AI-generated diagnostics. The application also runs sleep issue diagnosis and generates sleep reports.

This data is not clinical in the HIPAA sense. It is sensitive health behavior data tied to stable user identifiers under China's Personal Information Protection Law (PIPL). PIPL treats health data as a sensitive personal information category requiring explicit consent and heightened protection. The exposure covers real users of a production WeChat Mini Program.

The 36.9MB log file contains user identifiers and health response bodies from 6,712 successful requests. The scope of exposure depends on how many distinct users those requests represent.

---

## Attribution

The service name "wuji-langgraph" and deployment path "sleepDoctor" identify this as the wuji sleep health platform. The WeChat Mini Program backend structure is standard for Chinese consumer health apps. TencentCloud AS45090, Beijing. No TLS. No PTR record. The openapi.json is public and documents the full endpoint surface.

The MCP and retrieval endpoints add a second access layer beyond the direct data endpoints:

```
POST /mcp_chat
POST /mcp_ds_chat
POST /retrieval/build_index
POST /retrieval/search
```

We did not probe these. Retrieval index contents remain unknown.

---

## Thesis Placement

The auth model is structural. The GET endpoint takes an openid in the URL. The POST endpoints take a hash in the body. The server enforces nothing. The WeChat openid is treated as both the identifier and the credential.

This is a pattern from the early mobile backend era: client-supplied user IDs as implicit authentication. It predates session tokens and JWT. On a production sleep health platform in 2026, under PIPL, it is a live exposure.

Logs are an internal audit trail. Here they are a public directory of user identifiers and health responses. Any external party can call the destructor.

**See also:** [LangGraph Server Survey (2026-05-25)](langgraph-server-survey-2026-05-25.md) · [LangGraph Deployment Gap — Systematic Pattern](langgraph-deployment-gap-survey-2026-05-25.md)
