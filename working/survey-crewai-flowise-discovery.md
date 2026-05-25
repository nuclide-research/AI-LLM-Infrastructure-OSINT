# CrewAI + Flowise Shodan Discovery
Date: 2026-05-25
Method: Playwright browser, authenticated Shodan session (account: Aperire)
Scope: Metadata enumeration only — no probing of discovered IPs

---

## CrewAI Dorks

### Dork 1: `http.title:"CrewAI" port:8000`
- **Result count: 0**
- No hits. CrewAI is not self-identifying with this exact page title on port 8000.

### Dork 2: `http.html:"crewai" http.status:200`
- **Result count: 125**
- Top countries: US (65), CN (12), DE (8), AE (5), IE (5)
- Top ports: 443 (51), 80 (29), 8000 (11), 3000 (7), 8001 (7)
- Top orgs: Google LLC (14), DigitalOcean (13), Hetzner (13), Amazon Technologies (8), Amazon.com (7)
- Top products: nginx (43), Apache httpd (7), AWS ELB (3), OpenResty (1), SimpleHTTPServer (1)

**First 10 IPs (page 1, sorted newest first):**
| IP | Port | Org | Country | Stack | Notes |
|----|------|-----|---------|-------|-------|
| 20.185.107.134 | 8000 | Microsoft Corporation | US/Reston | Python/Uvicorn | cloud tag; JSON API response |
| 100.51.180.31 | 443 | Amazon.com | US/Ashburn | React/Next.js/Webpack | cert CN: *.orchestrateai.tech |
| 185.25.116.174 | 443 | Hosting Ukraine LTD | UA/Kyiv | nginx | title: "iBoost — AI-інтеграції премиум-рівня для українського бізнесу"; self-signed |
| 34.144.209.91 | 80 | Google LLC | US/Kansas City | Google Cloud CDN/LB/Trace | title: "Altostratus CrewAI" |
| 64.227.99.12 | 80 | DigitalOcean | US/Santa Clara | nginx/Ubuntu | title: "CrewAI Application"; eol-product tag |
| 113.108.101.130 | 443 | CHINANET Guangdong | CN/Shenzhen | nginx | title: "智子系"; cubegalaxy.com |
| 152.42.141.63 | 443 | DigitalOcean | NL/Amsterdam | nginx/Ubuntu | title: "AstraNL — Hulp bij uw klus"; astranl.com; eol-product |
| 147.182.219.125 | 8001 | DigitalOcean | US/North Bergen | Python/Uvicorn | cloud; raw JSON API |
| 34.128.137.43 | 443 | Google LLC | US/Kansas City | Google Cloud/TailwindCSS | title: "Defang CrewAI Demo"; cert: *.prod2.defang.dev |
| 98.85.217.68 | 443 | Amazon Data Services NoVa | US/Ashburn | Python/Uvicorn | self-signed; cert CN: hr-agent-alb-*.us-east-1.elb.amazonaws.com |

**Notable patterns:**
- Uvicorn (Python ASGI) appears repeatedly — CrewAI typically exposes a FastAPI/Uvicorn backend.
- "Defang CrewAI Demo" and "Altostratus CrewAI" are named production/demo deployments.
- hr-agent-alb internal ELB cert on 98.85.217.68 — HR agent stack on AWS, self-signed, public-facing.
- orchestrateai.tech on 100.51.180.31 — named AI orchestration service on AWS.
- Most cloud-hosted: Google Cloud (14), DigitalOcean (13), Hetzner (13). Primarily production infra, not dev boxes.

### Dork 3: `http.html:"CrewAI Studio" port:8000,3000`
- **Result count: 0**
- CrewAI Studio is not currently indexed at those ports with that HTML string.

### Dork 4: `"crewai" "8000" country:US`
- **Result count: 0**
- Bare keyword match with port number and country returns nothing. Too narrow / wrong field combination.

---

## Flowise Dorks

### Dork 1: `http.title:"Flowise"`
- **Result count: 47,676**
- WARNING: This count is inflated. "Flowise" in page title matches many non-Flowise pages that happen to contain the string. The 47K population is not meaningful without filtering.
- Top countries: US (7,178), AU (3,525), CA (3,343), JP (2,945), IN (2,892)
- Top ports: 3000 (910), 443 (607), 80 (225), 3001 (88), 444 (38)
- Top orgs: Amazon.com Inc. (6,646), Amazon Technologies (4,182), A100 ROW Inc (3,314), Amazon Data Services Canada (3,098), Amazon Data Services India (2,195)
- Top products: Flowise (492), nginx (294), Apache httpd (20), AstrBot (7), DrayTek Vigor Router (5)
- Note: The DrayTek Router and AstrBot hits confirm FP contamination. AWS domination is suspicious given Flowise default port 3000; likely unrelated S3/CloudFront pages with "flowise" in content.
- Actual confirmed Flowise (product:"Flowise" sub-facet): 492 within this result set

**First 10 IPs (confirmed title "Flowise - Build AI Agents, Visually"):**
| IP | URL |
|----|-----|
| 51.96.22.215 | (AWS region) |
| 18.130.168.109 | AWS eu-west-2 |
| 108.137.100.64 | AWS |
| 16.170.246.115 | AWS eu-north-1 |
| 18.222.132.180 | AWS us-east-2 |
| 13.236.36.39 | AWS ap-southeast-2 |
| 78.14.71.79 | (non-AWS residential/VPS) |
| 16.51.142.176 | AWS ap-south-1 |
| 13.43.92.181 | AWS eu-west-2 |
| 108.131.220.97 | AWS |

**Notable patterns:**
- Heavy AWS presence across all regions — suggests many Flowise deployments on EC2.
- 78.14.71.79 is not a cloud ASN range — likely a residential or small VPS deployment (flag for aimap).

### Dork 2: `http.html:"Flowise" port:3000,8080`
- **Result count: 978**
- This is the precision dork. Port 3000 is Flowise's default. HTML match + port filter = high-confidence hits.
- Top countries: US (272), DE (203), UK (51), FR (47), SG (41)
- Top ports: 3000 (924), 8080 (54)
- Top orgs: Hetzner Online GmbH (138), DigitalOcean (137), Microsoft/Azure (97+21=118), Contabo GmbH (74)
- Top products: Flowise (263), nginx (3), SimpleHTTPServer (1)

**First 10 IPs (page 1, port 3000):**
| IP | Title | Port |
|----|-------|------|
| 51.17.5.170 | Flowise - Build AI Agents, Visually | 3000 |
| 172.237.4.164 | Flowise - Build AI Agents, Visually | 3000 |
| 209.182.235.194 | Flowise - Build AI Agents, Visually | 3000 |
| 146.59.237.33 | Flowise - Low-code LLM apps builder | 3000 |
| 103.248.60.240 | Flowise - Build AI Agents, Visually | 3000 |
| 135.181.178.166 | Flowise - Build AI Agents, Visually | 3000 |
| 78.12.252.87 | Flowise - Build AI Agents, Visually | 3000 |
| 54.187.97.127 | Flowise - Build AI Agents, Visually | 3000 |
| 64.227.99.184 | Flowise - Low-code LLM apps builder | 3000 |
| 135.181.178.156 | Flowise - Build AI Agents, Visually | 3000 |

**Notable patterns:**
- Two title variants: "Build AI Agents, Visually" (current) and "Low-code LLM apps builder" (older version).
- 135.181.178.166 and 135.181.178.156 — sequential IPs, same /24 — likely same operator running multiple nodes.
- Hetzner (138) and DigitalOcean (137) nearly tied as top hosters — budget cloud, consistent with hobbyist/SMB deployments.
- Contabo at 74 — cheap VPS provider popular in EU, often under-administered.
- SimpleHTTPServer hit suggests at least one deployment served via Python's built-in HTTP server with no production hardening.

### Dork 3: `product:"Flowise"`
- **Result count: 513**
- Shodan's product fingerprint match — highest confidence Flowise identifier (banner-confirmed).
- All 10 page-1 results titled "Flowise - Low-code LLM apps builder" (older version banner) or omitted.

**First 10 IPs:**
| IP | Title |
|----|-------|
| 34.205.149.76 | Flowise - Low-code LLM apps builder |
| 176.98.237.53 | Flowise - Low-code LLM apps builder |
| 8.140.154.255 | Flowise - Low-code LLM apps builder |
| 146.59.237.33 | Flowise - Low-code LLM apps builder |
| 64.227.99.184 | Flowise - Low-code LLM apps builder |
| 45.76.216.226 | Flowise - Low-code LLM apps builder |
| 51.159.170.54 | Flowise - Low-code LLM apps builder |
| 147.93.132.222 | Flowise - Low-code LLM apps builder |
| 37.60.255.27 | Flowise - Low-code LLM apps builder |
| 104.42.195.61 | 403 Forbidden (Flowise behind reverse proxy) |

**Notable patterns:**
- 146.59.237.33 and 64.227.99.184 appear in both dork 2 and dork 3 — high-confidence repeat targets.
- 104.42.195.61 returns 403 — Flowise behind a reverse proxy or auth layer; worth flagging but not unauth.
- 8.140.154.255 — Aliyun (Alibaba Cloud China) IP.
- 34.205.149.76 — AWS us-east-1.

---

## Summary

### CrewAI
- Population is small but real. 125 confirmed HTTP-200 responses with "crewai" in HTML.
- No standalone "CrewAI" page title — CrewAI doesn't ship with a default UI on port 8000 the way Flowise does.
- The actionable signal is the Uvicorn/FastAPI backend pattern: `http.html:"crewai" http.status:200 product:"Uvicorn"` would be a sharper next dork.
- Named deployments worth deeper look: orchestrateai.tech, Altostratus CrewAI, Defang CrewAI Demo, hr-agent-alb (HR agent stack).

### Flowise
- Flowise has a large exposed population. Best population estimate from precision dorks:
  - `product:"Flowise"`: 513 (banner-confirmed)
  - `http.html:"Flowise" port:3000,8080`: 978 (port-filtered HTML match)
  - Real population likely 800-1,500 after dedup.
- Primary cloud hosts: AWS (many regions), Hetzner, DigitalOcean, Contabo, Azure.
- Port 3000 is the canonical Flowise port — 924 of 978 dork-2 results are on 3000.
- Flowise does not enforce auth by default — these are candidate unauth surfaces pending aimap verification.
- Recommended next dorks for aimap queue:
  - `http.html:"Flowise" port:3000 country:US` (272 US hits on default port)
  - `http.html:"Flowise" port:3000 org:"Hetzner Online GmbH"` (138 hits, budget cloud, likely unmanaged)
  - `product:"Flowise" port:3000` (precision + default port)

### Pivot Avenues
1. Run aimap against a sample of the 978 port-3000 Flowise IPs — default install has no auth, API key stored in SQLite.
2. Check 135.181.178.{156,166} sequential pair — same /24 operator running multi-node Flowise, likely single owner, possible shared misconfig.
3. `product:"Flowise" org:"Contabo GmbH"` — Contabo is cheap/unmanaged, high yield for unauth.
4. Cert-pivot on *.orchestrateai.tech (100.51.180.31) — find other hosts in that fleet.
5. CrewAI: narrow to Uvicorn banner — `http.html:"crewai" server:"uvicorn"` would drop noise and target actual API backends.
6. 78.14.71.79 (Flowise dork 1, non-cloud ASN) — residential/small VPS Flowise, likely personal project, possible default creds.
