# Shodan Query Results Log

Every executed dork is logged here — zero hits are results, not skips.

| Date | Query | Total Hits | Survey | Notes |
|------|-------|-----------|--------|-------|
| 2026-05-27 | `ssl.cert.subject.cn:"temporal"` | 961 | workflow-orchestration | Temporal Cloud customers, NOT self-hosted — wrong population |
| 2026-05-27 | `http.title:"Temporal" port:8233` | 0 | workflow-orchestration | dead dork |
| 2026-05-27 | `http.title:"Temporal" port:8080` | 4 | workflow-orchestration | all FP (email demo, TARDIS log, bot dashboard) |
| 2026-05-27 | `port:8233 http.html:"temporal"` | 0 | workflow-orchestration | dead dork |
| 2026-05-27 | `http.html:"supportedClients" "clusterName"` | 0 | workflow-orchestration | dead dork |
| 2026-05-27 | `http.html:"/api/v1/namespaces" "temporal"` | 0 | workflow-orchestration | dead dork |
| 2026-05-27 | `port:7233` | 425 | workflow-orchestration | broad gRPC port, unverified |
| 2026-05-27 | `http.title:"Cadence" port:8088` | 210 | workflow-orchestration | all FP — SaaS products named Cadence (AI social, EDA tools) |
| 2026-05-27 | `http.html:"cadence-web" port:8088` | 0 | workflow-orchestration | dead dork |
| 2026-05-27 | `port:7933 http.html:"cadence"` | 0 | workflow-orchestration | dead dork |
| 2026-05-27 | `http.html:"uber/cadence"` | 0 | workflow-orchestration | dead dork |
| 2026-05-27 | `port:8080 http.html:"netflix/conductor"` | 4 | workflow-orchestration | 4 confirmed: Aliyun CN, GCP US, Contabo DE, Beijing Volcano CN |
| 2026-05-27 | `http.title:"Argo Workflows" port:2746` | 0 | workflow-orchestration | dead dork — Shodan not indexing port 2746 titles |
| 2026-05-27 | `port:2746 http.title:"Argo"` | 0 | workflow-orchestration | dead dork — same reason |
| 2026-05-27 | `ssl.cert.issuer.cn:"Argo Workflows"` | 0 | workflow-orchestration | dead dork — Argo cert has no CN field, only Organization=ArgoProj |
| 2026-05-27 | `port:2746` | 418 | workflow-orchestration | broad port harvest — mostly banner-less; needs content filter |
| 2026-05-27 | `http.html:"assets/favicon/favicon-32x32.png" "noindex"` | 160 | workflow-orchestration | too broad — matches other SPAs; not Argo-specific |
| 2026-05-27 | `ssl:"ArgoProj" port:2746` | 0 | workflow-orchestration | dead — Shodan indexes cert but port 2746 HTTPS content not stored |
| 2026-05-27 | `http.html:"gitTreeState" port:2746` | 0 | workflow-orchestration | dead — API JSON not indexed by Shodan crawler on port 2746 |
| 2026-05-27 | `http.html:"gitTreeState" "gitCommit"` | 0 | workflow-orchestration | dead — API JSON not indexed on any port |
| 2026-05-27 | `ssl:"ArgoProj"` | **233** | workflow-orchestration | WORKING DORK — cert org field; US 81 / JP 50 / DE 33 / IE 26 / CN 20; AWS-heavy; 156 unique IPs harvested. FP class: ACM certs where domain contains "argoproj" as subdomain (e.g. webhook.events.dxsx-argoproj.inside.ai). True positives have self-signed cert Issuer O=ArgoProj; verify via /api/v1/userinfo. |
| 2026-05-27 | `port:2746 http.status:200` | 12 | workflow-orchestration | too broad — Hikvision cameras, Home Assistant, Ollama; not Argo-specific |
| 2026-05-27 | `ssl.cert.subject.org:"ArgoProj"` | 0 | workflow-orchestration | dead — field-specific query not indexed the same way as ssl:"ArgoProj" |
| 2026-05-27 | `ssl:"ArgoProj" port:8080` | 0 | workflow-orchestration | dead — ArgoProj cert instances are on port 443, not 8080 |
| 2026-05-27 | `http.html:"fa82dae05c4e68e1ec09"` | 0 | workflow-orchestration | dead — Shodan does not index Argo SPA HTML body content |
| 2026-05-27 | `port:2746 "X-Ratelimit-Limit"` | 0 | workflow-orchestration | dead — Shodan does not crawl port 2746 HTTP banners. Argo unauth instances (plain HTTP port 2746) are Shodan-dark. Requires direct scan. |
| 2026-05-27 | `http.title:"OpenMetadata" port:8585` | 55 | ml-governance | 30 IPs p1-p3; primary dork confirmed working |
| 2026-05-27 | `http.html:"open-metadata" port:8585` | 0 | ml-governance | dead dork |
| 2026-05-27 | `http.html:"openmetadata" port:8080` | 1 | ml-governance | k8s ingress variant; 1 extra IP |
| 2026-05-27 | `http.title:"DataHub" port:9002` | 25 | ml-governance | 25 IPs confirmed |
| 2026-05-27 | `http.html:"datahubproject" port:9002` | 0 | ml-governance | dead dork — title is the anchor |
| 2026-05-27 | `port:21000 http.title:"Atlas"` | 0 | ml-governance | Apache Atlas not internet-exposed at scale on :21000 |
| 2026-05-27 | `port:21000 http.html:"Apache Atlas"` | 0 | ml-governance | dead dork |
| 2026-05-27 | `http.html:"marquezproject" port:5000` | 0 | ml-governance | Marquez not internet-exposed at scale |
| 2026-05-27 | `http.html:"amundsen" port:5001` | 0 | ml-governance | Amundsen not internet-exposed at scale |
| 2026-05-27 | `http.html:"registered-models" port:5000` | 0 | ml-governance | MLflow registry string not distinctive enough |
| 2026-05-27 | `http.html:"/api/3/action" http.html:"ckan"` | 4 | ml-governance | 2 IPs (129.13.32.206/207), same /29 — likely one operator |
| 2026-05-27 | `port:8585 http.html:"openmetadata"` | 56 | ml-governance | 1 additional IP vs title dork (34.56.227.179); total 57 unique |
| 2026-05-28 | `ssl:"Argo Workflows"` | 214 | argo-workflows | NEW: hits cert CN "Argo Workflows" on commercial certs (Let's Encrypt/ACM) — separate population from ssl:"ArgoProj". 90 IPs harvested (pagination partial). Top operators: Home Depot, Apex Clearing, freed.ai, Waabi AI, BrightInsight, ZOZO Inc, AccelerateLearning (4 envs), INSHUR. Google LLC 93 hosts, AWS ~94. |
| 2026-05-28 | `ssl:"Argo Workflows" -ssl:"ArgoProj"` | 214 | argo-workflows | Zero overlap with ArgoProj cert-org population — entirely distinct deployment class (operator-domain certs vs self-signed) |
| 2026-05-28 | `port:2746` | 403 | argo-workflows | All "No data returned" — confirms port 2746 HTTP body not crawled by Shodan. TCP open detected only. Aliyun 169, Internet Rimon/IL 49, ACEVILLE 38, Fly.io 26. Port 2746 passive discovery is definitively dead in Shodan. |
| 2026-05-28 | `http.html:"assets/favicon/favicon-32x32.png" noindex` | 157 | argo-workflows | HIGH FP — iptel.ua VoIP fleet + Auvious video, not Argo. Path too generic. |
