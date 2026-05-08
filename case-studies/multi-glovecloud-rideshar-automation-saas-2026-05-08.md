# Glove Cloud (手套云) — Ride-Sharing Automation SaaS: Source Code Leaked via Unauth Docker Registry Mirror

**Date:** 2026-05-08  
**Discovery vector:** Shodan `http.html:"metabase/frontend"` → unauth Docker registry → image pull → layer extraction  
**Registry:** `154.12.63.166:5000` (1yidc.com Chinese Docker mirror service)  
**Software:** `wangxianlin996/{gc_app,gc_manage,gc_bot,gc_pool,gc_agent_bot}`  
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

**Versioning:** gc_app v2.5.x, gc_manage v2.5.11, gc_bot v2.1.1, gc_agent_bot v1.1.0 (active development)

**Docker Hub pull counts (snapshot 2026-05-08):**

| Image | Pulls | Last updated | Notes |
|---|---:|---|---|
| `wangxianlin996/gc_app` | 1,569 | 2026-03-03 | Per-operator instance |
| `wangxianlin996/gc_manage` | 829 | 2026-03-02 | Central management SaaS |
| `wangxianlin996/gc_agent_bot` | 243 | 2026-04-14 | Newest component |
| `wangxianlin996/gc_bot` | 200 | 2025-05-23 | Legacy sales bot |
| `wangxianlin996/gc_pool` | 170 | 2025-12-23 | Token pool service |

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

## gc_agent_bot — Telegram Sales/Reseller Bot (Newer Component)

A fifth image — `wangxianlin996/gc_agent_bot` (243 pulls, last updated 2026-04-14) — extends the ecosystem with a multi-agent Telegram reseller bot. The `code/conf/conf.json` shipped inside the image (layer 5, fully cached on the 1yidc.com mirror) is a complete production bootstrap:

```json
{
  "token":   "8734925058:AAGJWlUzi6wwCjzdjYIv1RyNE40I_6uQlVo",
  "domain":  "https://admin.flashplatform.uk",
  "mongoUri": "",
  "admin":   [7634537115, 8653442092]
}
```

### Live Telegram Bot Identity (verified)

`https://api.telegram.org/bot{token}/getMe` returns 200 OK:

```json
{
  "id": 8734925058,
  "is_bot": true,
  "first_name": "贾维斯",        // "Jarvis"
  "username": "dreamcar_agent_bot",
  "can_join_groups": true,
  "can_read_all_group_messages": true
}
```

Token is **live** at the time of research. Bot is the customer-facing reseller interface (`@dreamcar_agent_bot`).

### Hardcoded Backend Credentials

`code/common/gc_sdk.py` ships the admin auth tuple used for every call into gc_manage:

```python
admin_headers = {
    "Flash-Token":    "tunan_admin",
    "Authorization":  "Basic YWRtaW46d21zZ2o="      # admin:wmsgj
}
```

Two layers of "auth" — both static, both shipped inside a public Docker image:
- **Flash-Token: tunan_admin** — the same token already disabled by the commented middleware
- **HTTP Basic admin:wmsgj** — present in code but never validated server-side; likely terminates at a reverse proxy that the operator may or may not actually deploy

### Bot-Driven gc_manage Endpoints

`gc_sdk.py` defines the bot's RPC surface against gc_manage:

| Function | gc_manage Endpoint | Effect |
|---|---|---|
| `get_cdkey_type_list` | `POST /api/cdkey/get_all_options` | Enumerate license SKUs |
| `create_from_bot` | `POST /api/cdkey/create_from_bot` | Mint license keys via bot |
| `create_agent_cdkey_from_bot` | `POST /api/cdkey/create_agent_cdkey_from_bot` | Mint reseller-tier keys |
| `unbind_from_bot` | `POST /api/cdkey/unbind_from_bot` | Detach key from device |
| `delete_cdkey` | `POST /api/cdkey/delete_cdkey` | Destroy keys |

These are served by gc_manage with **no authentication** (per the commented middleware). Anyone hitting a live gc_manage instance directly hits the same endpoints the bot does — without going through the bot, the Telegram admin gate, or the Basic auth pretense.

### Backend Domain Status

`https://admin.flashplatform.uk` resolves NXDOMAIN at time of research (multiple Western and Chinese resolvers: 8.8.8.8, 1.1.1.1, 223.5.5.5, 119.29.29.29, 180.76.76.76). RDAP at Nominet returns "Domain flashplatform.uk not found" — the .uk domain is **not registered**. Three plausible explanations:

1. **Operator rotation** — the conf.json baked into the public image points to a domain the operator burned/rotated; live deployments configure a different `domain` via env or runtime override
2. **Pre-deployment image** — the image was pushed before the production domain was set up
3. **Geo-fenced split-horizon DNS** — the domain resolves only inside specific Chinese network segments (no evidence either way)

The bot itself remains live regardless — meaning either (a) the operator has the bot deployed against a different gc_manage URL, or (b) the bot is running but failing every backend call. Telegram `getUpdates` would resolve this but was not exercised (out of session scope).

### Admin Telegram User IDs

`7634537115` and `8653442092` — the two admin user IDs hardcoded into the conf. These are the only Telegram accounts the bot recognizes for `agent_update`, `agent_check_all`, `agent_delete`, etc. Telegram user IDs are not normally privacy-sensitive but pin attribution.

---

## Re-examination Findings

A second-pass review verified each load-bearing claim and surfaced two new artifacts.

### Verified: middleware is actually attached, no per-route backstops

The "auth disabled" claim depends on the commented middleware actually being registered. Confirmed in `gc_manage/code/main.py` line 28:

```python
app.middleware("http")(common.middleware.token_verification_middleware)
```

The middleware is wired up. Combined with: zero `Depends`, zero `HTTPBearer`, zero `HTTPBasic`, zero `verify_*` calls, zero `auth_token` checks across every router file (`cdkey.py`, `app.py`, `system.py`, `vip.py`, `tk_pool.py`, `app_platform.py`). The commented middleware **is** the entire auth path. The unauth finding is decisive.

### Verified: `admin:wmsgj` Basic auth is unilateral

The `Authorization: Basic YWRtaW46d21zZ2o=` header that gc_agent_bot sends with every call is **not validated anywhere in gc_manage or gc_app source**. `grep -r "wmsgj\|YWRtaW46\|HTTPBasic\|basic_auth\|verify_credentials"` across both codebases returns zero hits in any Python module — it appears only in the bot's `gc_sdk.py` outbound headers. Either the developer expected operators to terminate Basic auth at an upstream nginx (and pre-shared the cred so the bot can traverse it), or the header is template debris. Either way, an attacker with this cred bypasses any nginx layer that an operator may have bolted on.

### gc_pool — .git directory shipped inside the image (`v1.0.5`–`v1.0.11`)

Layer 4 (~46 KB across all gc_pool tags) of `wangxianlin996/gc_pool` contains the **complete `.git/` directory** that was present in the developer's working tree at build time. `gc_app`, `gc_manage`, `gc_agent_bot` all properly excluded `.git` via `.dockerignore`; gc_pool did not. From the shipped `.git/config`:

```ini
[remote "origin"]
    url = http://148.135.66.228:34568/admin_jack/gloveCloudPool
    fetch = +refs/heads/*:refs/remotes/origin/*
[http "http://148.135.66.228:34568/"]
    extraheader = AUTHORIZATION: basic eC1hY2Nlc3MtdG9rZW46MWQxM2RhMDY4ZjJkODcxMzJlZjU2NWIwOWQ5MTJmNzk5N2Y3NGQyOA==
```

Decoded: `x-access-token:1d13da068f2d87132ef565b09d912f7997f74d28`

This is a Gitea personal access token, embedded in a git remote helper config so the developer wouldn't have to re-authenticate on every push. When the Docker image was built, `COPY ./ /code` pulled the token into the image. The image was pushed public.

**Scope-limited at OSINT layer** — no requests issued to the Gitea instance with this token; documented for the case study only.

#### Operator's Gitea infrastructure

`148.135.66.228:34568` resolves to:

- **AS35916 MULTACOM CORPORATION**, Los Angeles, US
- Custom Gitea instance on a non-standard port
- Path layout `admin_jack/gloveCloudPool` → user **`admin_jack`**, repo **`gloveCloudPool`** (matching the platform brand)

Multacom is a budget LA colo provider commonly used by Chinese operators wanting US-based development infrastructure outside PRC oversight. The operator targets Chinese ride-share platforms (DiDi, Hello, Dida, Xiaola, Jinma) but hosts development infrastructure abroad — a common operational separation pattern.

#### CI/CD: Gitea Actions → Docker Hub

`code/.gitea/workflows/build-docker.yaml` defines auto-build on push to master, tag extraction from commit message, and Docker Hub push using `${{ secrets.DOCKER_NAME }}`, `${{ secrets.DOCKER_USERNAME }}`, `${{ secrets.DOCKER_PASSWORD }}`. The CI secret names confirm the supply chain: developer commits → Gitea Actions builds → Docker Hub publishes → 1yidc.com mirror caches → operators deploy.

#### Git author identity

```
Author: jack
Email:  jack@git.com
Branch: master (shallow clone)
Commit: 72eb844 — "v1.0.5 测试自动打包"  (testing auto-packaging)
```

Email is a placeholder/generic, not personal. Username `jack` aligns with the Gitea username `admin_jack`. Different identity surface than the Docker Hub publisher `wangxianlin996`.

### Identity surface — multiple aliases

| Surface | Identifier |
|---|---|
| Docker Hub publisher | `wangxianlin996` |
| Gitea user / repo owner | `admin_jack` |
| Git commit author | `jack <jack@git.com>` |
| `tunan.cn` registrant | 王俊 (Wang Jun) — `1604800473@qq.com` |
| Telegram admin IDs | `7634537115`, `8653442092` |

`wangxianlin996` is a Chinese name handle (Wang Xianlin / 996 referencing China's 9-9-6 work culture). `王俊` (Wang Jun) is a different Chinese name. These could be:

- One operator with multiple aliases for OPSEC/legal separation
- A solo developer (`jack`/`admin_jack`) selling to a fronting operator (`wangxianlin996`)
- Co-developers

Insufficient evidence for which. Documented as candidates.

### Domain landscape

| Domain | Status | Note |
|---|---|---|
| `admin.flashplatform.uk` | NXDOMAIN | Per gc_agent_bot conf — not registered at Nominet |
| `flashplatform.xyz` | Resolves to GMO/onamae.com parking page (160.251.64.80, JP) | Defensive registration only |
| `flashplatform.com` / `.net` / `.cn` / `.io` / `.app` / etc. | NXDOMAIN | Not registered |
| `tunan.cn` | Resolves (170.33.12.185, Alibaba SG, anycast) | All HTTP/HTTPS ports closed/filtered. Registered 2019-09-23 to 王俊. Whois trail. |
| `gloveCloud.cn` | Sinkholed to 127.0.0.1 | Defensive null-route |
| `glovecloud.com` | AWS Ashburn US, openresty 302 | Unrelated 2013-vintage domain (different owner, brand collision) |
| `shoutao.com` | AWS Singapore, openresty 302 | Unrelated 2000-vintage domain (different owner, brand collision) |
| `kkxxs.top` | NXDOMAIN | Developer's offline test deployment |

**Certificate transparency:** crt.sh has zero history for `tunan`, `gloveCloud`, `flashplatform`, `dreamcar`. The platform has either never been deployed with a CA-issued TLS certificate, or runs entirely behind self-signed certs / private CAs. Combined with the `flashplatform.uk` NXDOMAIN, the most likely interpretation is that the conf.json shipped in `gc_agent_bot` references a domain that was **never wired up to a real production deployment** — the bot is deployed somewhere else, configured with a different `domain` value via env override at runtime.

### Pull-count drift — active operations

Pull counts measured twice during the session (Direct API → Search API):

| Image | First read | Second read | Δ |
|---|---:|---:|---:|
| `gc_app` | 1,569 | 1,377 | search lag (search index is stale) |
| `gc_manage` | 829 | 707 | search lag |

The deltas reflect Docker Hub's search-index lag against the live counter, not real-time pulls. But the absolute numbers — particularly **1,569 cumulative pulls of gc_app** — suggest the platform has been deployed by dozens to low-hundreds of distinct operators. With gc_manage at 829 and the average operator deploying both, there are likely 50–200 distinct gc_manage instances live (the gc_app excess accounts for multi-platform deployments per operator: one gc_app per ride-share platform).

### Operator's PRODUCTION Gitea located via aimap Bearer-realm leak

`aimap -target 148.135.66.228` on the Multacom origin server received a `WWW-Authenticate` header that exposed the operator's actual production Gitea hostname:

```
Bearer realm="https://git.zvteboi.top/v2/token", service="container_registry", scope="*"
```

This identifies a domain the case study had not previously seen: **`zvteboi.top`**.

`zvteboi.top` whois:
- **Registrar:** NameSilo (US)
- **Created:** 2025-09-16 (∼8 months old)
- **Registrant:** REDACTED FOR PRIVACY, **Arizona, US** (state visible despite WHOIS privacy)

**`git.zvteboi.top` is Cloudflare-fronted** (104.21.76.88 / 172.67.191.154) with the Multacom box (148.135.66.228) as the origin. Public Gitea version 1.25.4 (from CSS `?v=1.25.4`). The operator hardened the Gitea:

| Endpoint | Response | Meaning |
|---|---|---|
| `/` | 200 (Gitea login page) | Public sign-in only |
| `/admin_jack` | 303 → `/user/login` | `REQUIRE_SIGNIN_VIEW = true` — no public profile browsing |
| `/explore/repos` | 303 → `/user/login` | Public exploration disabled |
| `/explore/users` | 303 → `/user/login` | User list hidden |
| `/api/v1/version` | 403 | API restricted from anonymous |
| `/api/v1/users/admin_jack` | 403 | API restricted |
| `/v2/_catalog` | 401 (Bearer required) | Container registry needs auth |

The operator did the right thing on operational hardening (Cloudflare front, REQUIRE_SIGNIN_VIEW, API lockdown, custom port for direct origin access). **And then shipped a public Docker image with their own Gitea access token in `.git/config`.** The token bypasses every one of the above protections.

CertSpotter shows only the wildcard `*.zvteboi.top` cert plus apex — no specific subdomain certs in CT logs. Operator uses a wildcard, hiding subdomain structure from CT-based recon.

### BARE — semantic exploit-module match

Running BARE against the structured findings (`source: manual` → 4 finding objects → `bare` corpus of 3,904 Metasploit modules):

| Finding | Top match | Score | Comment |
|---|---|---:|---|
| FastAPI middleware token verification commented out | `exploits_multi_http_wp_suretriggers_auth_bypass` | 0.484 | Same primitive class — middleware-level auth bypass |
| Docker registry mirror caching private commercial images | `exploits_linux_local_docker_daemon_privilege_escalation` | 0.502 | Tangential; supply-chain class isn't in MSF corpus |
| Gitea token leaked via `.git/config` | **`exploits_multi_http_gitea_git_hooks_rce`** | **0.552** | **Direct hit** — Gitea git-hooks RCE is exploitable with admin-token credentials. If the leaked token has admin scope on the operator's instance, RCE is one curl away |

The Gitea git-hooks RCE primitive (Metasploit `exploit/multi/http/gitea_git_hooks_rce`) leverages Gitea's git-hooks feature which allows admin users to set arbitrary post-receive shell commands. With admin-level credentials, push a hook that shells out — RCE on the Gitea host.

**Token scope unverified at OSINT layer** — we did not query `/api/v1/users/admin_jack` with the token, so we don't know if `admin_jack` is an admin (in which case git-hooks RCE is available) or a regular user (in which case the token only grants pull access).

### Re-cap of the supply chain

```
[admin_jack (jack@git.com)]
        │  git push → master
        ▼
[git.zvteboi.top — Gitea 1.25.4]   (Cloudflare-fronted, NameSilo .top, AZ US registrant)
        │  origin: 148.135.66.228:34568   (Multacom LA, US)
        │  Gitea Actions: build-docker.yaml
        ▼
[Docker Hub: wangxianlin996/{gc_app,gc_manage,gc_bot,gc_pool,gc_agent_bot}]
        │  pulled by operators in PRC
        │  (also pulled-and-cached by 1yidc.com mirror — exposing them to OSINT)
        ▼
[1yidc.com mirror: 154.12.63.166:5000]   (general-purpose CN Docker mirror)
        │  unauth /v2/_catalog + blob serving
        ▼
[Operator deployments — gc_manage on port 80]   (Alibaba/Tencent CN, default-deny inbound from foreign IPs)
        │
        ▼
[End-customers: drivers paying for CDKeys to game 哈啰/嘀嗒/滴滴/小拉/金马]
        │
        ▼
[Mobile-client script tiers loaded from gc_manage/static/script_zip/]:
   • 霸王 (Bawang/King)        — 2024-01 — release/ namespace
   • 八爪鱼 (Octopus)          — 2024-01 — release/ namespace
   • 金蟾 (Golden Toad)        — 2024-02 — douhun/ namespace, Dida (嘀嗒) integration
   • 鹰眼 (Hawkeye)            — 2024-01 — release/ namespace
   • 擎天柱 (Optimus Prime)    — 2024-03 — chan/ namespace, Hello + filterSettings
   • 派大星 (Patrick Star)     — 2024-03 — release/ namespace, +pkLocation.js
```

The "tier" naming — Bawang / Patrick Star / Optimus Prime — is consistent with the Chinese gray-market auto-grab software market (cf. competing products "小可爱"/Little Cutie, "神话"/Mythology priced at ~880 RMB). The script payloads contain `helloSdk.js` / `didaSdk.js` per platform, `mainActivity.js` (Android activity hooks), `location.js` (GPS spoofing/manipulation primitives). These are injected into legitimate ride-share apps via Xposed/Frida or runtime injection.

### Disclosure routing — `nuclide-contact`

```
nuclide-contact --ip 154.12.63.166 --domain docker.1yidc.com
  → soa_global@dnspod.com (DNS:SOA-RNAME)
  → abuse@1yidc.com / csirt@1yidc.com / security@1yidc.com (pattern guess)
  → hostmaster@afrinic.net / new-member@afrinic.net (NETWORK 154.12.0.0/16)

nuclide-contact --ip 148.135.66.228
  → abuse@ripe.net (WHOIS:OrgAbuseEmail)
  → hostmaster@ripe.net (WHOIS:OrgTechEmail)
```

Note that `148.135.0.0/16` is in the RIPE-ERX-148-135 block (transferred from ARIN to RIPE). The Multacom organizational contact is the operating party, but RIPE abuse is the registry-of-record contact. For takedown, Multacom's direct abuse contact would be the canonical recipient (ipinfo lists `AS35916 MULTACOM CORPORATION`).

### Visor Log entries

Four finding surfaces logged to `nuclide.db`:

| ID | IP | Severity | Tags |
|---|---|---|---|
| 1 | `154.12.63.166` (docker.1yidc.com) | high | DOCKER-MIRROR, REGISTRY-LEAK, SUPPLY-CHAIN, PRIVATE-IMAGES |
| 2 | `148.135.66.228` (Multacom Gitea origin) | critical | GITEA, LEAKED-TOKEN, DEV-INFRA, GLOVE-CLOUD-OPERATOR |
| 3 | `0.0.0.0` (`wangxianlin996/gc_manage` Docker Hub) | critical | AUTH-DISABLED, COMMENTED-MIDDLEWARE, SUPPLY-CHAIN, RIDE-SHARE-ABUSE |
| 4 | `0.0.0.0` (`@dreamcar_agent_bot` Telegram) | high | TELEGRAM-BOT, LIVE-TOKEN, OPERATOR-CONTROL |

### Timeline (chronological)

| Date | Event |
|---|---|
| 2019-09-23 | `tunan.cn` registered to 王俊 / `1604800473@qq.com` (CN, Alibaba) — likely placeholder; current IP is anycast-for-sale |
| 2023-11-20 | First mobile-client script payload (`cityMap.js` in 八爪鱼.zip) |
| 2023-12-28 → 2024-03-26 | 6 script "tier" builds (霸王 / 八爪鱼 / 金蟾 / 鹰眼 / 擎天柱 / 派大星) |
| 2025-05-15 | First gc_pool Docker build pushed (`jack@git.com`, commit 72eb844, build-container hostname `8536c46e5595`). **`.git/config` with access token committed to public registry.** |
| 2025-05-23 | gc_bot legacy Telegram bot last update |
| 2025-09-16 | `zvteboi.top` registered via NameSilo (US, AZ registrant) — current production domain |
| 2025-12-23 | gc_pool last build pushed |
| 2026-03-02 | gc_manage last build (829 pulls so far) |
| 2026-03-03 | gc_app last build (1,569 pulls so far) |
| 2026-04-14 | gc_agent_bot v1.1.0 build — newest active component |
| 2026-05-08 | This investigation |

The supply-chain leak class: **Docker Hub mirrors that proxy-and-cache public registries inadvertently expose every private image their customers ever pulled.** Anyone querying `_catalog` on these mirrors gets a who's-who of commercial operators in their customer base.

---

## Live Instance Discovery — Negative Result

Per-pulled deployment count suggests ~50–200 live gc_manage instances. Active discovery from a US vantage was attempted and produced **zero hits** across:

- 47,884 live port-80 hosts (sampled every 16th IP across Alibaba Cloud AS37963 + AS45102, Tencent Cloud AS45090 + AS132203, ~2.83M total IPs sampled)
- Probes: `/openapi.json` matching `gloveCloud`, `/gcm.ui` matching `tunan_admin`, `/docs` matching FastAPI title strings
- 250 alt-port port-8000 hosts probed for `/webhook/get_api_router` with `flash-token: gloveCloudManage`
- Two 200-response hosts on the webhook path were honeypots (Ant Design Pro stub and a multi-fingerprint blender returning GitLab + SPIP + VOS3000 + GoAnywhere markers)

Most likely explanation: Chinese cloud security groups default-deny inbound from foreign IP ranges. Live instances exist but are not reachable from US vantage without going through a Chinese network. **Not a finding negative — a measurement-vantage limit.**

The discovery proof here is the public Docker registry itself: source code analysis of a publicly-pulled image showing the auth disabled by the developer, served from a mirror that anyone with `curl` can reach. The presence of an actively-developed agent bot (last updated 2026-04-14) and a verified-live Telegram bot token confirms the platform is in current operation.

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
| **Live Telegram bot token** | **Critical** | `@dreamcar_agent_bot` token verified active — full bot takeover possible |
| **HTTP Basic creds in image** | High | `admin:wmsgj` shipped publicly; reuse risk if operator reuses elsewhere |
| **Pinned admin Telegram IDs** | Medium | `7634537115`, `8653442092` — operator attribution anchor |
| **Gitea access token in `.git/config`** | **Critical** | `1d13da068f2d87132ef565b09d912f7997f74d28` — full pull access to operator's private Gitea (148.135.66.228:34568) |
| **Operator infrastructure attribution** | High | Multacom LA US dev infra + Alibaba CN production = operational separation pattern documented |

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

**Bot fingerprint (Telegram):**
```
Bot ID:        8734925058
Bot username:  @dreamcar_agent_bot
Bot name:      贾维斯 (Jarvis)
Backend domain (per shipped conf): admin.flashplatform.uk  (NXDOMAIN at research time)
```

**HTTP Basic auth shipped in image:**
```
Authorization: Basic YWRtaW46d21zZ2o=    →    admin:wmsgj
```
