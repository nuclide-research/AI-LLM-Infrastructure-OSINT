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
