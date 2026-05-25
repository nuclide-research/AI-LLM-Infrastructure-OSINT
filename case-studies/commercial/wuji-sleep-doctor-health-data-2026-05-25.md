---
type: case-study
title: "wuji Sleep Doctor — WeChat Health Data and 9,244 Request Logs Exposed on Tencent Cloud"
date: 2026-05-25
severity: HIGH
sector: commercial
tags: [LangGraph, WeChat, health-data, China, TencentCloud, PIPL, sleep, IoT, request-logs]
summary: "A Chinese sleep health application on Tencent Cloud exposes per-user sleep sensor data by WeChat openid and serves 9,244 logged API requests without authentication. The service runs as root with log file paths disclosed."
---

# wuji Sleep Doctor — WeChat Health Data and 9,244 Request Logs Exposed on Tencent Cloud

**Date:** 2026-05-25
**Target:** 82.156.182.216
**ASN:** AS45090 Shenzhen Tencent Computer Systems Company Limited, Beijing, China
**App:** Sleep Doctor Service / wuji-langgraph
**Severity:** HIGH

---

## What Was Found

### F1 — Sleep Health Data Accessible by WeChat OpenID (HIGH)

Sleep sensor data for WeChat users is readable by openid on port 8000. No authentication.

```
GET http://82.156.182.216:8000/api/sleep_analysis/{openid}
```

WeChat openids are user-stable identifiers tied to a specific WeChat account. The endpoint takes the openid in the URL path and returns the user's sleep analysis. No token. No rejection.

The application processes AHI trends, heart rate, HRV, and respiratory rate. It also processes sleep stages, temperature, humidity, sleep scores, and total sleep time. Each metric has its own open endpoint:

```
POST /api/image/ahi_trend
POST /api/image/hr
POST /api/image/hrv_trend
POST /api/image/rr
POST /api/image/stage
POST /api/image/score_trend
```

The `/api/sleep_issue_diagnosis_by_hash` and `/api/health_sleep_profile_by_hash` endpoints provide diagnostic output, not only raw metrics.

### F2 — 9,244 Request Logs Exposed (HIGH)

```
GET http://82.156.182.216:8000/api/monitor/logs
→ {"logs": [...], "total": 210, "showing": 100, "source": "memory"}
```

The response serves request logs from a 36.9MB JSONL file. Each entry includes: timestamp, method, endpoint, status_code, duration_ms, hash, username, request_body, response_body, client_ip.

Log file: `/root/sleepDoctor/logs/api_monitor_logs.jsonl`. 9,244 entries. 6,712 successful. Successful requests carry user hash and openid values in request_body and sleep data in response_body.

Our probe IPs appear in the log from 2026-05-26T01:30:42. Any party that accessed this endpoint is logged and visible to any other party who reads the log.

### F3 — Monitoring Stats Open (MEDIUM)

```
GET http://82.156.182.216:8000/api/monitor/stats
→ {"total_requests": 7610, "success_count": 6712, "error_count": 898, "avg_response_time": 2202.6}
```

### F4 — File Paths and Root Deployment Disclosed (LOW)

```
GET http://82.156.182.216:8000/api/monitor/file_info
→ {
    "log_file": "/root/sleepDoctor/logs/api_monitor_logs.jsonl",
    "stats_file": "/root/sleepDoctor/logs/api_monitor_stats.json",
    "log_file_size_kb": 36917.52
  }
```

The service runs from `/root/sleepDoctor/`. Root deployment.

---

## Stack and Use Case

The application is a WeChat Mini Program backend. Users connect sleep monitoring hardware. Sensors track AHI, heart rate, respiratory rate, temperature, and humidity. Users register via WeChat. The app generates nightly analysis, sleep reports, bedtime reminders, and wake-up timing. A LangGraph agent backs the `/chat`, `/mcp_chat`, and `/search` endpoints.

The monitoring endpoints (`/api/monitor/clear`, `/api/monitor/reload_cache`, `/api/monitor/reload_unionid_cache`) are state-modifying. All are open without authentication.

The app name "wuji" (无极) means limitless in Chinese. The service runs on Tencent Cloud in Beijing.

---

## Data Classification

Sleep stages, AHI, heart rate, HRV, and respiratory rate for individual identified WeChat users. Under China's Personal Information Protection Law (PIPL), Article 28, health data qualifies as sensitive personal information and requires separate consent and stricter protection obligations.

The log file holds 6,712 request records from real user interactions. Each carries a client IP address.
