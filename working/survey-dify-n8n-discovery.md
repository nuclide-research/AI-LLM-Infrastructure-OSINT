# Dify + n8n Shodan Discovery — 2026-05-25

Metadata enumeration only. No probing. All data from Shodan search result pages.

---

## Dify Dorks

### D1 — `http.title:"Dify"`
**Total results: 2,393**

IPs (first page):
- 85.131.248.160 — XSERVER Inc., Japan, Kobe
- 8.212.160.59 — Alibaba Cloud PH, Philippines, Manila
- 47.100.73.178 — Aliyun, China
- 120.25.191.214 — Aliyun, China
- 47.237.97.254 — Aliyun, China
- 198.58.112.235 — Linode, US
- 8.213.216.81 — Alibaba Cloud
- 172.234.130.211 — Linode
- 8.208.22.38 — Alibaba Cloud
- 45.56.71.80 — Linode

**Top countries:** China 1,160 | United States 362 | Japan 277 | Singapore 144 | Germany 86

**Top ports:** 80 (877) | 443 (318) | 8080 (93) | 3000 (89) | 8143 (3)

**Top orgs:** Aliyun 435 | Linode 202 | Tencent Cloud 149 | Aliyun Co.LTD 116 | XSERVER 116

**Top products:** nginx 1,240 | Dify 411 | Sophos SSL VPN 14 | Ivanti EPMM 12 | OpenResty 6

**Auth indicators from banners (first 8 results):**
All return HTTP/1.1 200 OK. No WWW-Authenticate or 401/403 visible at scan surface.
- nginx/1.27.4 + Next.js (Cache-Control: private, no-cache) — suggests SPA frontend rendered
- WSGIServer/0.2 CPython/3.7.7 — direct Python backend, old runtime
- BANNER[3]: `LoginIP: 224.108.139.84` header present — possible reverse proxy tracking login IP, but still 200
- IBM_HTTP_Server, Jetty(9.4.43.v20210629), PeerSec-MatrixSSL — heterogeneous stack, likely FP noise from `http.title:"Dify"` matching other content

**Signal quality:** High volume but mixed. The Aliyun/Linode/nginx/Next.js cluster is the genuine Dify population. WSGIServer/IBM/Jetty results are likely FP (other content with "Dify" in title). The 411 results fingerprinted as `product:Dify` by Shodan are the clean subset.

**Open-access indicators:** 200 OK across all sampled banners with no auth challenge headers. Dify's standard unauth state serves the login page as 200 (client-side routing) — HTTP status alone does not confirm unauth access. Requires UI-layer verification.

---

### D2 — `http.html:"dify.ai" http.status:200`
**Total results: 9**

IPs:
- 107.191.60.12 — "Dify — The platform for AI workflows" (genuine Dify)
- 218.211.29.61 — "ERP系統 AI 客服專員" (TW ERP chatbot embedding dify.ai)
- 146.56.134.168 — "AI HUB | 所有 AI 在此集合" (AI aggregator with dify.ai ref)
- 183.193.53.122 — "Dify" (genuine)
- 185.4.180.220 — "This is exten.bot: the OpenAI Realtime VoIP Bot" (dify.ai in HTML, not Dify itself)
- 18.234.109.105 — "License Dashboard" (dify.ai ref in page, FP)
- 118.31.43.105 — "PDF智转" (Chinese PDF tool, dify.ai ref)
- 116.62.188.183 — "PDF智转" (same service, second IP)
- 3.1.179.163 — "CC Concept AI | AI Transformation for Asia-Pacific Businesses"

**Signal quality:** Low precision. Most results reference dify.ai in embedded content rather than being Dify instances. Genuine Dify: 107.191.60.12, 183.193.53.122. The PDF智转 cluster (118.31.43.105, 116.62.188.183) is a Dify-built app.

---

### D3 — `http.html:"/api/explore/apps" port:80,443,3000`
**Total results: 0**

No results. The `/api/explore/apps` endpoint path is not indexed as HTML content by Shodan on these ports. This is an API path, not typically present in the crawled HTML body.

---

### D4 — `product:"langgenius/dify"`
**Total results: 0**

No results. Shodan does not fingerprint Dify by Docker image name in the `product` field. Dify does not expose a distinct product banner string that Shodan extracts as a product identifier.

---

## n8n Dorks

### N1 — `http.title:"n8n" port:5678`
**Total results: 5**

IPs + context:
- 168.119.96.100 — Hetzner Online, Germany (Falkenstein) — "n8n ChattyAI - Workflow Automation" — HTTP 200, `Cache-Control: no-cache, no-store, must-revalidate` — scanned 2026-05-24
- 46.62.162.52 — Hetzner Online, Finland (Vaala) — "n8n ChattyAI - Workflow Automation" — HTTP 200 — scanned 2026-05-08
- 88.198.205.101 — Hetzner Online, Germany (Falkenstein) — "n8n ChattyAI - Workflow Automation" — HTTP 200 — scanned 2026-04-30
- 206.190.237.244 — Cluster Logic Inc (16clouds.com), Japan (Osaka) — "n8n - Workflow Automation" — `Server: n8n/1.19.4`, `X-Powered-By: n8n` — HTTP 200 — scanned 2026-04-27
- 38.102.86.8 — Rica Web Services, Canada (Montréal) — "n8n" — `Server: nginx/1.24.0`, `X-Powered-By: Express` — HTTP 200 — Shodan flags **eol-product** — scanned 2026-04-26

**Pattern notes:**
- The three ChattyAI hosts (168.119.96.100, 46.62.162.52, 88.198.205.101) are a single shared n8n-based chatbot service distributed across Hetzner nodes. Consistent banner fingerprint. Not three separate operators.
- 206.190.237.244 runs n8n/1.19.4 under the 16clouds.com reverse-proxy infrastructure (same operator cluster seen in prior surveys).
- 38.102.86.8 is flagged `eol-product` by Shodan -- n8n version is end-of-life.
- All five serve HTTP 200 at port 5678. n8n auth-on-default means the 200 response is the login page (client-side routing). Not confirmed unauth without UI verification.

**Open-access candidates:** 206.190.237.244 (n8n/1.19.4, minimal headers, no security headers) and 38.102.86.8 (EOL, nginx proxy, no CORP/COOP headers) warrant closer review. The ChattyAI cluster appears intentionally public-facing (named chatbot service).

---

### N2 — `http.html:"n8n.io" "instance_id" port:5678`
**Total results: 0**

No results. The `instance_id` field appears in n8n's internal API responses, not in crawled HTML body content. Shodan's crawler would not capture this from the SPA shell.

---

### N3 — `http.html:"n8n" "/healthz" port:5678`
**Total results: 0**

No results. `/healthz` is a backend endpoint path, not present in the HTML body Shodan indexes.

---

## Summary

| Dork | Count | Signal Quality | Notes |
|------|-------|----------------|-------|
| `http.title:"Dify"` | 2,393 | High volume, mixed precision | China-heavy Aliyun cluster is the core Dify population; ~411 Shodan-confirmed |
| `http.html:"dify.ai" http.status:200` | 9 | Low precision | Mostly dify.ai references, not Dify instances |
| `http.html:"/api/explore/apps" port:80,443,3000` | 0 | N/A | API path not in HTML body |
| `product:"langgenius/dify"` | 0 | N/A | Not a Shodan product fingerprint |
| `http.title:"n8n" port:5678` | 5 | Clean, low volume | 3 ChattyAI nodes + 2 standalone; all HTTP 200; EOL flag on 38.102.86.8 |
| `http.html:"n8n.io" "instance_id" port:5678` | 0 | N/A | instance_id not in HTML body |
| `http.html:"n8n" "/healthz" port:5678` | 0 | N/A | /healthz not in HTML body |

## Open-Access Candidates (HTTP 200, no visible auth header)

All require UI-layer verification — HTTP 200 from n8n and Dify is normal for their login page (client-side routing).

**Dify (D1) — worth JAXEN/aimap follow-up:**
- 198.58.112.235 (Linode, US)
- 172.234.130.211 (Linode, US)
- 45.56.71.80 (Linode, US)

**n8n (N1) — worth closer look:**
- 206.190.237.244 (16clouds.com, Japan — n8n/1.19.4, minimal headers, no CORP/COOP)
- 38.102.86.8 (Rica Web Services, Canada — EOL product flag)

## Dork Improvements

The high-signal Dify dork is `http.title:"Dify"` filtered to `org:Aliyun` or `org:Linode` to cut FP noise. The `product:Dify` subset (411) within D1 is Shodan's own fingerprint and would be the cleanest pull. Recommend running JAXEN against the D1 result set filtered by `product:Dify`.

For n8n, the title dork is exhausted at 5 hosts. Broader sweep via `port:5678 http.status:200` (no title filter) would surface installations with custom titles or reverse-proxy rewrites.
