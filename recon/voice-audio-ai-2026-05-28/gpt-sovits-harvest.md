# GPT-SoVITS Harvest — 2026-05-28

**CVE scope:** CVE-2025-49833/34/35/36 — unauthenticated RCE via command injection on ports 9871-9874, 9880.

---

## Shodan Harvest

| Dork | Hits | Notes |
|------|------|-------|
| `port:9880 http.html:"GPT-SoVITS"` | 0 | API port not indexed |
| `port:9872 http.html:"GPT-SoVITS"` | 2 | Taiwan + China; both offline at probe time |
| `port:9874 http.html:"GPT-SoVITS"` | 0 | Training WebUI not indexed |
| `port:9871 http.html:"GPT-SoVITS"` | 0 | Proofreading tool not indexed |
| `http.html:"GPT-SoVITS"` (broad) | 23 | All ports; most on :80/:443/:8000/:8800 |
| `port:9880 http.html:"/set_gpt_weights"` | 0 | API endpoint string not indexed |
| `port:7865 http.html:"RVC-Boss"` | 0 | RVC variant not present |

**Total unique IPs harvested: 22**

---

## Full IP List

| IP | Country | Org | Shodan Port | Notes |
|----|---------|-----|------------|-------|
| 140.125.84.53 | Taiwan | Ministry of Education Computer Center | 9872 | uvicorn; offline 2026-05-28 |
| 117.50.138.228 | China | Shanghai UCloud | 9872 | uvicorn; offline 2026-05-28 |
| 163.44.114.51 | Japan | GMO Internet | 80 | Werkzeug; PixivTranslate app |
| 167.179.114.97 | Japan | Vultr | 80 | SimpleHTTP dir listing |
| 138.128.223.77 | US | IT7/16clouds | 80 | nginx |
| 160.251.201.109 | Japan | GMO Internet | 80 | Werkzeug; PixivTranslate app |
| 46.224.19.85 | UAE | Hetzner | 80 | nginx; CELSJUX WORKSHOP |
| 47.96.133.226 | China | Aliyun | 80 | nginx; AI漫剧技术 platform |
| 218.72.79.235 | China | CHINANET-ZJ | 80 | Werkzeug; vits-simple-api |
| 43.167.209.235 | Japan | ACEVILLE | 80 | nginx; personal page |
| 192.3.179.39 | US | HostPapa | 443 | nginx; likikyou.fun |
| 114.55.73.133 | China | Aliyun | 443 | nginx; 文视AI |
| 183.98.27.231 | Korea | Korea Telecom | 443 | uvicorn |
| 104.171.202.229 | US | Lambda | 8000 | uvicorn; Lambda Cloud GPU |
| 122.234.92.74 | China | CHINANET-ZJ | 80 | Werkzeug; vits-simple-api |
| 106.75.1.212 | China | Shanghai UCloud | 443 | nginx; upload.benxianhenl.cn |
| 156.240.76.58 | Singapore | HGC Global | 443 | nginx |
| 47.108.192.1 | China | Aliyun | 8800 | uvicorn |
| 220.187.74.226 | China | CHINANET-ZJ | 80 | Werkzeug; vits-simple-api |
| 125.125.133.225 | China | CHINANET-ZJ | 80 | Werkzeug; vits-simple-api |
| 104.171.202.19 | US | Lambda | 8000 | uvicorn; Lambda Cloud GPU |
| 173.231.48.180 | US | WebNX | 80/443 | nginx; 502 Bad Gateway |

---

## CVE Surface Probe Results

Probed all 22 IPs against ports 9871, 9872, 9873, 9874, 9880.

**CVE-affected ports open: 0 / 22**

The two Shodan-confirmed port 9872 hosts (140.125.84.53, 117.50.138.228 — indexed 2026-05-02) are offline as of 2026-05-28. All remaining hosts responded only on standard ports (80/443/8000) through reverse proxies with no direct CVE port exposure.

Live hosts responding at probe time:
| IP | Port | Status | Server |
|----|------|--------|--------|
| 192.3.179.39 | 443 | 400 | nginx/1.24.0 |
| 114.55.73.133 | 443 | 200 | nginx |
| 183.98.27.231 | 443 | 400 | openresty |
| 106.75.1.212 | 443 | 400 | nginx/1.18.0 |
| 156.240.76.58 | 443 | 400 | nginx/1.27.4 |
| 104.171.202.19 | 8000 | 200 | uvicorn |
| 173.231.48.180 | 80/443 | 502 | nginx |

---

## Geographic / Cloud Distribution (from Shodan)

| Country | Count |
|---------|-------|
| China | 9 |
| United States | 6 |
| Japan | 4 |
| UAE | 1 |
| Korea | 1 |
| Singapore | 1 |

| Cloud/Org | Count |
|-----------|-------|
| Aliyun (Alibaba Cloud) | 3 |
| CHINANET-ZJ | 4 |
| GMO Internet | 2 |
| HostPapa | 2 |
| Lambda Cloud | 2 |
| Shanghai UCloud | 2 |
| Hetzner | 1 |
| HGC Global | 1 |
| IT7/16clouds | 1 |
| Korea Telecom | 1 |
| ACEVILLE | 1 |
| Vultr | 1 |
| WebNX | 1 |

---

## Key Findings

**Population size:** 23 Shodan-indexed instances (broad dork). Small population — GPT-SoVITS is a niche voice cloning framework, not mass-deployed infrastructure.

**CVE surface: 0 directly accessible.** Shodan's top ports (80:5, 8800:4, 8000:3, 443:2, 9872:2) show most deployments run behind nginx/uvicorn reverse proxies on standard ports. The CVE-affected native ports (9871-9874, 9880) are not internet-facing in any live instance found.

**Pattern classes:**

1. **vits-simple-api wrapper** — CHINANET-ZJ cluster (218.72.79.235, 122.234.92.74, 220.187.74.226, 125.125.133.225): four hosts running Werkzeug/2.3.6 with vits-simple-api, which embeds GPT-SoVITS as a backend. Port 80. Chinese hobbyist/operator class.

2. **PixivTranslate** — GMO Internet Japan (163.44.114.51, 160.251.201.109): GPT-SoVITS used as voice component in a manga translation platform. Werkzeug on port 80. Not standalone deployment.

3. **Lambda Cloud GPU** — (104.171.202.229, 104.171.202.19): uvicorn on port 8000 with `content-type: application/json` — API wrapper pattern. Lambda Cloud = pay-per-GPU, these are likely ephemeral research instances.

4. **AI platform integrations** — 47.96.133.226 (AI漫剧技术), 114.55.73.133 (文视AI): Chinese SaaS platforms embedding GPT-SoVITS as voice cloning backend.

5. **Direct Docker exposure (offline)** — The two port 9872 Shodan hits (Taiwan MoE, Shanghai UCloud) were the only instances where CVE-affected ports were directly exposed. Both offline 26 days after indexing.

**Verdict:** CVE-2025-49833/34/35/36 attack surface is near-zero in the current internet-exposed population. The framework's Docker deployment model does bind all five ports to 0.0.0.0, but operators appear to be routing through nginx reverse proxies on standard ports in practice. The two confirmed direct-exposure instances self-remediated (or were ephemeral) within the Shodan index window.

**Pivot avenues:**
1. Re-run broad dork monthly — population is small enough that new instances are easy to track.
2. Dork on `vits-simple-api` separately — it's a GPT-SoVITS wrapper with its own API surface and the CHINANET-ZJ cluster is a distinct operator pattern worth its own survey.
3. `port:8800 http.html:"GPT-SoVITS"` — Shodan top ports showed 4 hits on :8800; this dork was not run.
4. Check Lambda Cloud instances (104.171.202.229, 104.171.202.19) for `/docs` FastAPI endpoint — uvicorn + JSON response may expose API spec.
5. Cert pivot on `upload.benxianhenl.cn` (106.75.1.212) — Let's Encrypt cert; check for other subdomains.
6. `http.html:"vits-simple-api"` broad sweep — separate population, same CVE class risk if GPT-SoVITS backend is exposed.

---

_Probed: 2026-05-28 | Tool: aiohttp async, 8s timeout, 20 concurrency | Read-only, no RCE paths invoked_
