---
type: case-study
title: "wuji Sleep Doctor — Chinese Health Data by WeChat OpenID, 9,244 Request Logs Open"
date: 2026-05-25
severity: HIGH
sector: commercial
tags: [LangGraph, WeChat, health-data, sleep, China, TencentCloud, PIPL, PII, request-log, root-deployment, agent-framework]
summary: "A Chinese sleep health WeChat Mini Program backend runs a LangGraph Sleep Doctor service with no authentication on any endpoint. Sleep sensor data (AHI, heart rate, HRV, sleep stages) is accessible by WeChat openid alone. A 36.9MB request log containing 9,244 entries — including user identifiers, request bodies, response bodies, and client IPs — is served at /api/monitor/logs without auth. The service runs as root."
---

# wuji Sleep Doctor — Chinese Health Data by WeChat OpenID, 9,244 Request Logs Open

**Date:** 2026-05-25
**Target:** 82.156.182.216
**ASN:** AS45090 Tencent Cloud — Beijing, China
**Severity:** HIGH

---

## What Was Found

### F1 — Sleep Health Data Accessible by WeChat OpenID (HIGH)

Port 8000 serves a FastAPI/LangGraph backend identified by its own root response as "Sleep Doctor Service" with `chat_service: "wuji-langgraph"`.

```
GET http://82.156.182.216:8000/api/sleep_analysis/{openid}
```

A WeChat openid in the URL path returns the user's sleep analysis. No authentication. WeChat openids are stable user identifiers assigned by the WeChat platform. They are not secrets; they are passed in API calls between WeChat apps and their backends as a matter of course.

The data class: AHI (Apnea-Hypopnea Index) trends, sleep stages, heart rate, HRV (Heart Rate Variability), respiratory rate, sleep scores, temperature, and humidity readings from a connected sleep sensor device. This is clinical-quality physiological data. AHI specifically is the diagnostic metric for sleep apnea.

Full endpoint coverage:

| Endpoint | Data |
|---|---|
| GET /api/sleep_analysis/{openid} | Full sleep analysis by WeChat openid |
| POST /api/generate_sleep_analysis_by_unionid | Analysis by WeChat unionid |
| POST /api/health_sleep_profile_by_hash | Health sleep profile |
| POST /api/sleep_issue_diagnosis_by_hash | Sleep issue diagnosis |
| POST /api/sleep_report_by_hash | Full sleep report |
| POST /api/user_sleep_experience_by_hash | Sleep experience |
| POST /api/user_profile_by_hash | User profile |

None require authentication.

### F2 — 9,244-Entry Request Log Served Without Auth (HIGH)

```
GET http://82.156.182.216:8000/api/monitor/logs
→ 200 OK — 36.9MB JSONL file
```

Log path: `/root/sleepDoctor/logs/api_monitor_logs.jsonl`

Each entry: timestamp, HTTP method, endpoint, status code, duration, user hash, request body, response body, client IP.

9,244 entries. 7,610 total requests, 6,712 successful. The log records every probe made against this service, including the probe from this investigation (136.37.103.3). Request bodies contain user hashes and openids; response bodies contain the health data those queries returned.

A complete audit trail of every health data access event, all open, with the data itself embedded in the response bodies.

### F3 — Root Deployment (LOW)

```
GET http://82.156.182.216:8000/api/monitor/file_info
→ {
    "log_path": "/root/sleepDoctor/logs/api_monitor_logs.jsonl",
    "stats_path": "/root/sleepDoctor/logs/api_monitor_stats.json"
  }
```

The service runs as root. File paths under `/root/sleepDoctor/` are exposed in monitoring responses. A code execution vulnerability on any of the open endpoints would give immediate root-level access to the host.

### F4 — Destructive Monitoring Endpoints Open (MEDIUM)

```
POST /api/monitor/clear          — clear the request log
POST /api/monitor/reload_cache   — reload user cache
POST /api/monitor/reload_unionid_cache — reload unionid cache
```

All three require no auth. Any caller can clear the 9,244-entry request log or force cache reloads.

---

## Stack Map

| Port | Service | Auth | Severity |
|---|---|---|---|
| 8000 | FastAPI/LangGraph — Sleep Doctor Service | None | HIGH |

All health data endpoints, all monitoring endpoints, all cache management endpoints: no auth.

---

## Request Log Sample (Confirmed Structure)

`/api/monitor/stats`:
```json
{
  "total_requests": 7610,
  "success_count": 6712,
  "error_count": 898,
  "avg_response_time": 2202.6
}
```

Each log entry in the JSONL file contains the `request_body` and `response_body` fields. For successful sleep analysis requests, the response body contains the health data. The log is a complete replay of every user interaction, with the health data embedded.

---

## Attribution

Tencent Cloud, Beijing (AS45090). App name: "wuji-langgraph" from the root response. WeChat Mini Program backend serving Chinese users through WeChat's embedded browser. Chinese Personal Information Protection Law (PIPL) applies to health data collected from Chinese users. Sleep sensor data (AHI, HRV, sleep stages) classifies as sensitive personal information under PIPL.

---

## Regulatory Context

China's PIPL (2021, effective November 2021) requires explicit consent and heightened protections for sensitive personal information, which includes health and medical data. AHI and sleep staging data falls within this category. The `/api/sleep_analysis/{openid}` endpoint makes health data accessible with no credential gate. Direct PIPL compliance failure, in addition to the security exposure.

---

## Thesis Placement

FastAPI/LangGraph no-auth-by-default propagates to a health data backend processing WeChat users' physiological data. The request log extends the failure: the current health data is open, and the entire history of every health data access event is also open, with response data embedded inline. The root deployment creates a privilege escalation path from any open endpoint to full host control.

The log is self-referential. It captured the probe from this investigation, including client IP. This server has built a persistent record of every researcher, crawler, and attacker that has touched it. That record is also open.

**See also:** [LangGraph Server Survey (2026-05-25)](langgraph-server-survey-2026-05-25.md) · [LangGraph Deployment Gap](langgraph-deployment-gap-survey-2026-05-25.md)
