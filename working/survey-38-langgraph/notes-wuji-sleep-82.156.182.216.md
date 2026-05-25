# wuji-langgraph / Sleep Doctor — Complete Investigation Notes

**Host:** 82.156.182.216
**Cloud:** Tencent Cloud (AS45090) — Beijing, China
**App:** Sleep Doctor Service / wuji-langgraph (WeChat Mini Program backend)
**Status:** FULLY MAPPED
**Priority:** 9 → re-prioritized HIGH (health data PII exposure confirmed)

---

## Confirmed Services

| Port | Service | Auth |
|---|---|---|
| 8000 | FastAPI/LangGraph — "Sleep Doctor Service", chat_service: "wuji-langgraph" | NONE |

---

## App Description

WeChat Mini Program backend for a Chinese sleep health application. Users are identified by WeChat openid/unionid. The app processes sleep sensor data (AHI, heart rate, HRV, respiratory rate, sleep stages, temperature/humidity) and generates AI-powered sleep analysis and diagnostics. 7,610 API requests processed to date.

Deployment path exposed: `/root/sleepDoctor/` — running as root.

---

## Confirmed Findings

### F1 — Sleep Health Data Accessible by WeChat OpenID (HIGH)

```
GET /api/sleep_analysis/{openid}
```

Takes a WeChat openid directly in the URL path, returns sleep health analysis. No auth. WeChat openids are user-stable identifiers — anyone with a user's openid can pull their sleep health data.

Confirmed endpoint present in openapi.json. Data returned would include AHI trends, sleep stages, heart rate, HRV, respiratory rate, sleep scores.

### F2 — Request Log File Exposed (HIGH)

```
GET /api/monitor/logs
→ 9,244 log entries, 36.9MB JSONL file, no auth
```

Log file: `/root/sleepDoctor/logs/api_monitor_logs.jsonl`

Each log entry contains: timestamp, method, endpoint, status_code, duration_ms, hash, username, request_body, response_body, client_ip.

Successful requests (6,712 of 7,610) would contain:
- User hash/openid values from request bodies
- Sleep data responses
- Client IP addresses

The log confirms our own probe IPs (136.37.103.3) are logged — any researcher accessing this server is traceable in the log.

### F3 — Monitoring Stats Open (MEDIUM)

```
GET /api/monitor/stats
→ {"total_requests": 7610, "success_count": 6712, "error_count": 898, "avg_response_time": 2202.6}
```

### F4 — Root Deployment + File Paths Disclosed (LOW)

`/api/monitor/file_info` reveals:
- Log path: `/root/sleepDoctor/logs/api_monitor_logs.jsonl`
- Stats path: `/root/sleepDoctor/logs/api_monitor_stats.json`
- Service running as root

---

## Full Endpoint Map

| Method | Path | Description |
|---|---|---|
| GET | /api/sleep_analysis/{openid} | Sleep analysis by WeChat openid |
| POST | /api/generate_sleep_analysis_by_unionid | Generate analysis by WeChat unionid |
| POST | /api/data_get_by_hash | Get data by hash |
| POST | /api/device_realtime_status_by_hash | Device status |
| POST | /api/device_status_by_hash | Device status |
| POST | /api/health_sleep_profile_by_hash | Health sleep profile |
| GET | /api/monitor/logs | Full request log (9,244 entries) |
| GET | /api/monitor/file_info | Log file paths + sizes |
| GET | /api/monitor/stats | Aggregate request stats |
| POST | /api/monitor/clear | Clear logs (no auth) |
| POST | /api/monitor/reload_cache | Reload cache |
| POST | /api/monitor/reload_unionid_cache | Reload unionid cache |
| POST | /api/image/ahi_trend | AHI trend chart |
| POST | /api/image/deep_trend | Deep sleep trend |
| POST | /api/image/hr | Heart rate chart |
| POST | /api/image/hrv_trend | HRV trend |
| POST | /api/image/illuminance | Light exposure |
| POST | /api/image/rr | Respiratory rate |
| POST | /api/image/rr_trend | RR trend |
| POST | /api/image/score_trend | Sleep score trend |
| POST | /api/image/stage | Sleep stages |
| POST | /api/image/temp_humidity | Temperature/humidity |
| POST | /api/image/tst_trend | Total sleep time trend |
| POST | /api/images_get_by_hash | Multiple images by hash |
| POST | /chat | Chat endpoint |
| POST | /mcp_chat | MCP chat |
| POST | /mcp_ds_chat | MCP datasource chat |
| POST | /retrieval/build_index | Build index |
| POST | /retrieval/search | Search |
| GET | /retrieval/status | Index status |
| POST | /search | Search |
| POST | /webhook/database | DB webhook |
| POST | /api/bedtime_reminder_prompt_by_hash | Bedtime reminder |
| POST | /api/sleep_data_description_by_hash | Sleep data description |
| POST | /api/sleep_issue_diagnosis_by_hash | Sleep issue diagnosis |
| POST | /api/sleep_report_by_hash | Sleep report |
| POST | /api/user/sleep_context | User sleep context |
| POST | /api/user_profile_by_hash | User profile |
| POST | /api/user_realtime_status_by_hash | Real-time user status |
| POST | /api/user_sleep_experience_by_hash | Sleep experience |
| POST | /api/wake_stage_by_hash | Wake stage |
| POST | /api/wake_up_reminder_prompt_by_hash | Wake reminder |
| POST | /api/weather_by_hash | Weather data |

---

## Data Classification

WeChat health data (sleep sensor metrics, diagnostics, user profiles) + request logs containing user identifiers and IP addresses. Chinese health data regulations (Personal Information Protection Law, PIPL) apply. This is a production service with real users.
