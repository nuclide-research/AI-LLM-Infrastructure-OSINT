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
| 2026-05-27 | `ssl:"ArgoProj"` | **233** | workflow-orchestration | WORKING DORK — cert org field; US 81 / JP 50 / DE 33 / IE 26 / CN 20; AWS-heavy; 156 unique IPs harvested |
| 2026-05-27 | `port:2746 http.status:200` | 12 | workflow-orchestration | too broad — Hikvision cameras, Home Assistant, Ollama; not Argo-specific |
| 2026-05-27 | `ssl.cert.subject.org:"ArgoProj"` | 0 | workflow-orchestration | dead — field-specific query not indexed the same way as ssl:"ArgoProj" |
| 2026-05-27 | `ssl:"ArgoProj" port:8080` | 0 | workflow-orchestration | confirmed: all 233 ArgoProj cert instances are on port 2746, not proxied to 8080 |
