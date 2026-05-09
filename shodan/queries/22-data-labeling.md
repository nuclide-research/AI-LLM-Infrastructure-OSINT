# 22. Data Labeling / Annotation Servers

_Section created: 2026-05-09_

Data-labeling and annotation servers sit at the **input boundary of every supervised-learning ML pipeline**. They host raw data being labeled — frequently real customer PII, internal documents, facial imagery, medical scans, support-ticket transcripts, and financial filings. Operators stand them up quickly for crowd-sourced annotation projects, then leave them running after project completion.

**Survey result (2026-05-04):** 348 confirmed cross-cloud (Scaleway + OVH + Linode, 3.55M IPs). **Single-platform dominance: 348/348 are doccano.** Auth posture inverts the thesis — 98.9% auth-on at content endpoints (`/v1/projects` returns 401/403). doccano ships with mandatory auth; operators keep it. The `/v1/health` fingerprint endpoint stays open (enabling discovery) but project/label data is consistently locked. Notable gap: Argilla, LabelStudio, Prodigy, CVAT returned **zero** confirmed instances in this hosting tier; those platforms deploy predominantly in managed cloud or K8s rather than cheap-VPS.

**Auth posture by platform:**
- **doccano**: T2 — auth on by default; `/v1/health` open for fingerprinting, content auth-gated. `/openapi.json` exposed on 5.7% of instances (20/348).
- **Prodigy**: T1 — no built-in auth concept; operators expected to add proxy. Rare on public internet.
- **Argilla**: T2 — auth on since v1.x; `default-public` workspace misconfiguration sometimes seen.
- **LabelStudio**: T2 — mandatory auth; `/api/projects` sometimes misconfigured readable.
- **CVAT**: T2 — auth on by default; `/api/server/about` and project list occasionally left open.

**CVE watch:**
- `CVE-2023-38686` — Argilla < 1.13.0: SSRF via dataset-creation endpoint.
- `CVE-2022-25011` — Label Studio < 1.3.0: path traversal leading to arbitrary file read.
- No public doccano CVEs; risk is auth-bypass misconfiguration and `/openapi.json` API schema disclosure.

---

## doccano

| Shodan Query | Notes |
|---|---|
| `port:8000 "doccano"` | doccano on default port 8000 |
| `http.html:"doccano" port:8000` | HTML-scoped on default port |
| `http.html:"doccano"` | Any port; doccano sometimes reverse-proxied |
| `http.html:"/v1/projects" port:8000` | doccano projects API path in source |
| `http.html:"/v1/health" port:8000` | Health endpoint path in source |
| `"doccano"` | Bare-string in any indexed field |
| `http.title:"doccano"` | Page title |
| `http.title:"doccano" port:8000` | Title + default port |
| `http.html:"doccano" port:80` | Reverse-proxied on port 80 |
| `http.html:"doccano" port:443` | Reverse-proxied HTTPS |
| `hostname:"doccano"` | rDNS pattern |
| `ssl.cert.subject.cn:"doccano"` | TLS cert CN |
| `http.html:"doccano" org:"ovh"` | OVH-hosted (highest density in survey) |
| `http.html:"doccano" org:"linode"` | Linode-hosted |
| `http.html:"doccano" org:"scaleway"` | Scaleway-hosted |
| `http.html:"doccano" org:"hetzner"` | Hetzner-hosted |
| `http.html:"doccano" org:"digitalocean"` | DigitalOcean-hosted |
| `http.html:"doccano" country:US` | US-scoped |
| `http.html:"doccano" country:CN` | China |
| `http.html:"doccano" country:DE` | Germany |
| `http.html:"doccano" country:JP` | Japan (doccano is Japan-origin, Recruit Holdings) |
| `http.html:"doccano" country:KR` | Korea |

---

## Argilla

| Shodan Query | Notes |
|---|---|
| `port:6900` | Argilla default port; near-unique signal |
| `port:6900 "argilla"` | Argilla on default port |
| `port:6900 http.html:"argilla"` | HTML-scoped |
| `port:6900 http.status:200` | Live + responding |
| `http.html:"argilla" port:6900` | HTML-scoped on default port |
| `http.html:"/api/_info"` | Argilla API info endpoint path in source |
| `http.html:"/api/workspaces"` | Argilla workspace API path |
| `"argilla" port:6900` | Bare-string on default port |
| `"argilla"` | Bare-string broadest |
| `http.title:"Argilla"` | Page title |
| `http.title:"Argilla" port:6900` | Title + default port |
| `http.html:"argilla" port:80` | Reverse-proxied on port 80 |
| `http.html:"argilla" port:443` | Reverse-proxied HTTPS |
| `hostname:"argilla"` | rDNS pattern |
| `ssl.cert.subject.cn:"argilla"` | TLS cert CN |
| `http.html:"argilla" org:"hetzner"` | Hetzner-hosted |
| `http.html:"argilla" org:"amazon"` | AWS-hosted |
| `http.html:"argilla" org:"google"` | GCP-hosted |
| `http.html:"argilla" org:"university"` | Academic deployments (fine-tuning research) |
| `http.html:"argilla" org:"hospital"` | Healthcare (highest-impact labeling context) |

---

## Label Studio

| Shodan Query | Notes |
|---|---|
| `port:8080 "label-studio"` | Label Studio on common alt port |
| `port:8080 "LabelStudio"` | Capitalized form |
| `http.html:"label-studio" port:8080` | HTML-scoped |
| `http.html:"LabelStudio"` | Any port; Label Studio reverse-proxied |
| `http.html:"/api/version"` | Label Studio version endpoint in source |
| `http.html:"/api/projects"` | Label Studio projects API path |
| `"label-studio"` | Bare-string in any field |
| `"Label Studio"` | Product name |
| `http.title:"Label Studio"` | Page title |
| `http.title:"Label Studio" port:8080` | Title + common port |
| `hostname:"label-studio"` | rDNS pattern |
| `hostname:"labelstudio"` | Compressed rDNS |
| `ssl.cert.subject.cn:"labelstudio"` | TLS cert CN |

---

## Prodigy (Explosion AI)

| Shodan Query | Notes |
|---|---|
| `port:8080 "prodigy"` | Prodigy on reverse-proxy port (no default server port; ships with `--port` flag) |
| `http.html:"prodigy" port:8080` | HTML-scoped |
| `http.html:"prodigy" port:80` | Reverse-proxied |
| `http.html:"prodigy"` | Any port; highest false-positive rate of the platforms here |
| `http.html:"spacy" http.html:"prodigy"` | Prodigy + spaCy co-occurrence (same vendor, often co-deployed) |
| `"prodigy" "annotation"` | Conjunction reduces false positives |
| `hostname:"prodigy"` | rDNS; check results carefully (name collision with Prodigy Music) |

---

## CVAT (Computer Vision Annotation Tool)

| Shodan Query | Notes |
|---|---|
| `port:8080 "CVAT"` | CVAT on default port |
| `http.html:"cvat" port:8080` | HTML-scoped |
| `http.html:"Computer Vision Annotation Tool"` | Full product name; high precision |
| `http.html:"/api/server/about"` | CVAT server-info endpoint path in source |
| `"CVAT" port:8080` | Bare-string on default port |
| `http.title:"CVAT"` | Page title |
| `hostname:"cvat"` | rDNS pattern |
| `ssl.cert.subject.cn:"cvat"` | TLS cert CN |
| `http.html:"cvat" org:"university"` | Academic CV research deployments |

---

## Combined

| Shodan Query | Notes |
|---|---|
| `(http.html:"doccano" OR port:6900 OR http.html:"Label Studio" OR http.html:"CVAT")` | Full data-labeling sweep |
| `(http.html:"doccano" OR http.html:"argilla" OR http.html:"label-studio") org:"university"` | Academic annotation sweep |
| `(http.html:"doccano" OR http.html:"argilla" OR http.html:"label-studio") org:"hospital"` | Healthcare annotation (HIPAA/GDPR risk) |
| `port:6900 OR (port:8000 http.html:"doccano")` | Argilla + doccano combined port sweep |
| `(http.html:"doccano" OR http.html:"CVAT" OR http.html:"Label Studio") http.html:"medical"` | Medical-data labeling projects |
| `(http.html:"doccano" OR http.html:"argilla") country:JP` | Japan-scoped (doccano origin country) |
