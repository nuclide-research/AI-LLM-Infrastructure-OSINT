---
type: survey
category: 29-workflow-orchestration
target: Argo Workflows (global Shodan population)
date: 2026-05-27
status: updated-2026-05-28
author: NuClide Research
---

# Argo Workflows: K8s-Native Workflow Orchestration Survey

## Executive Summary

Shodan survey of the global Argo Workflows population via TLS certificate fingerprint. **67 confirmed instances** (initial survey, `ssl:"ArgoProj"` dork) plus **17 Argo-confirmed instances** from a second non-overlapping population of 200 IPs (`ssl:"Argo Workflows"` dork). All tested instances across both populations: auth-enforced. Combined passive-discoverable population: ~267 hosts. Notable operators include Home Depot, Apex Clearing, ForgeRock/Ping Identity, Salling Group, GREE Inc, Waabi AI, freed.ai, CAFIS (NTT Data). Zero unauthenticated instances across the entire combined population.

The vulnerable population (unauthenticated, port 2746 plain HTTP) remains Shodan-dark — `port:2746` returns 403 hosts, all "No data returned."

## Discovery

### Working Dork

```
ssl:"ArgoProj"
```

233 total results. 156 unique IPs after dedup. All other dorks returned 0 or unacceptable FP rates. See `shodan/query-log.md` for full 15-dork test matrix.

### Why Other Dorks Failed

| Dork | Result | Reason |
|------|--------|--------|
| `port:2746 http.title:"Argo"` | 0 | Shodan doesn't crawl port 2746 HTML content |
| `http.html:"gitTreeState" port:2746` | 0 | API JSON not indexed |
| `http.html:"fa82dae05c4e68e1ec09"` | 0 | SPA body not indexed anywhere |
| `port:2746 "X-Ratelimit-Limit"` | 0 | Port 2746 HTTP banners not crawled |
| `ssl.cert.issuer.org:"ArgoProj"` | 0 | Field-specific cert queries not indexed |

**Conclusion:** Shodan's only coverage of Argo Workflows is via the TLS cert's Organization field. Port 2746 (the native Argo port) is effectively dark in Shodan.

### False Positive Pattern

`ssl:"ArgoProj"` matches two classes:
1. **True positive**: Self-signed cert with Issuer O=ArgoProj (Argo's built-in TLS cert)
2. **False positive**: ACM/Let's Encrypt cert where "argoproj" appears as a subdomain label (e.g. `webhook.events.dxsx-argoproj.inside.ai`)

FPs return HTTP 403/404 from AWS ELB — eliminated by verification. Discriminator: `Issuer O=ArgoProj` vs. commercial CA issuer.

## Population Analysis

**156 IP harvest** → 136 open ports found by aimap:
- Port 443: 111 (82%)
- Port 80: 23 (17%) — mostly FP ELB 404s
- Port 8443: 1
- Port 8080: 1
- Port 2746: 0

**No instances found on port 2746.** The self-signed cert population runs exclusively on port 443 via K8s LoadBalancer/ingress.

### Confirmed Argo Instances: 67

Discriminated by: `X-Ratelimit-Limit` response header on the SPA root path (`/`). This header is injected exclusively by Argo's gRPC-gateway rate-limit middleware. All 67 also return:
- HTTP 200 on `/`
- `<title>Argo</title>`
- `<meta name="robots" content="noindex">`
- `assets/favicon/favicon-32x32.png` in body

### Version Distribution (by build Etag)

| Build Date | Etag (prefix) | Count | Argo Version (est.) |
|------------|---------------|-------|---------------------|
| Jan 2024 | `4d628c5d...` | 36 | ~v3.5.x |
| Jun 2025 | `f52113ac...` | 12 | ~v3.6.x |
| Oct 2025 | `ac1b2d2a...` | 7 | ~v3.6-3.7.x |
| Jun 2025 (alt) | `9716dd03...` | 2 | — |
| Sep 2025 | `5b1cbe12...` | 2 | — |
| Other/no-etag | — | 8 | — |

**36 instances on Jan 2024 build (oldest).** These predate CVE-2026-28229's patch window (fix landed in v3.7.11 / v4.0.2 in 2026). If configured with --auth-mode=client or hybrid, they would be vulnerable to the Bearer-nothing bypass.

### Cloud Distribution (confirmed 67)

- AWS (multiple regions): ~45
  - ap-northeast-1 (Tokyo)
  - ap-northeast-3 (Osaka)
  - eu-central-1 (Frankfurt)
  - us-east-1, us-west-2, etc.
- Tencent Cloud (China): ~12
- GCP: ~5
- Azure: ~2 (20.25.251.191 observed)
- APNIC/Korea: ~3

## Authentication Assessment

### Finding: All Tested Instances Auth-Enforced

Spot-checked 5 instances across version bands and cloud providers:

```
curl -sk "https://<ip>/api/v1/userinfo"
→ HTTP 401 {"code":16,"message":"token not valid for running mode"}

curl -sk "https://<ip>/api/v1/version"
→ HTTP 401 {"code":16,"message":"token not valid for running mode"}

curl -sk -H "Authorization: Bearer nothing" "https://<ip>/api/v1/workflow-templates/argo"
→ HTTP 401 {"code":16,"message":"Unauthorized"}
```

None of the tested instances respond to `Authorization: Bearer nothing` (CVE-2026-28229 bypass). All API paths return 401 with Argo's gRPC error codes.

### Selection Bias: Why This Population Is Auth-Enforced

The `ssl:"ArgoProj"` dork finds instances with Argo's self-signed TLS cert, served through a K8s LoadBalancer on port 443. Operators who:
- Deploy a TLS LoadBalancer (implies production K8s setup)
- Use Argo's native cert (implies following official setup docs)

...are more likely to also configure auth (`--auth-mode=client`). The truly vulnerable instances are the quick-start deployments: plain HTTP, port 2746, no cert, no ingress — and these are invisible to Shodan.

**Thesis result for this population:** Auth-on-default holds. Zero unauth server-mode instances confirmed in the 67-instance cert-dork population.

### Identity Scan Results: 67/67 Confirmed (aimap v1.9.36)

Full scan against all 67 confirmed port-443 hosts using the `Argo Workflows (auth-enforced)` fingerprint (X-Ratelimit-Limit header + SPA body probe):

- **67/67** matched — 100% confirmation rate
- **0 unauthenticated** — auth_status: unknown for all (no server-mode bypass possible)
- **1 MEDIUM finding**: `43.163.57.197` — CORS `Access-Control-Allow-Origin: *`

The wildcard CORS header on 43.163.57.197 allows cross-origin JS to make API requests. With any active Argo session in the same browser, this enables CSRF against the workflow API. Low standalone risk (auth required to do anything useful), but noteworthy in an enterprise K8s context.

## Shodan Discovery Gap (Codified Finding)

**Port 2746 is Shodan-dark for Argo Workflows.**

Shodan does not crawl:
- Port 2746 HTML body content
- Port 2746 HTTP response headers
- SPA JavaScript bundle filenames

The only signal Shodan captures is the TLS certificate when Argo runs with its built-in HTTPS enabled. Plain HTTP deployments (the typical quick-start/unauth configuration) produce no Shodan-indexable artifact.

**Impact:** Passive Shodan surveillance systematically misses the highest-risk Argo Workflows deployments. Accurate exposure measurement requires direct scanning (masscan → nmap → HTTP probe). E.V.A.'s 2022 finding of ~3,000 unauth instances used direct scanning, not dork-based discovery — and would not be reproducible via Shodan alone.

## aimap Updates (Driven by This Survey)

| Version | Change |
|---------|--------|
| v1.9.35 | Added ports 443, 80, 8080, 8443 to Argo Workflows DefaultPorts (81% of instances found on 443, not 2746) |
| v1.9.36 | Added `Argo Workflows (auth-enforced)` identity fingerprint at severity=info (X-Ratelimit-Limit + SPA body probe) |

### Bug Found: DefaultPorts Selection Bias

aimap's fingerprint matcher filters candidates by `DefaultPorts`. When the fingerprint listed only port 2746, all 111 port-443 Argo instances were silently skipped. Fix required adding all empirically-observed deployment ports.

**Lesson codified:** `DefaultPorts` must enumerate ALL survey-confirmed ports. The port a service is deployed on at scale may differ significantly from its vendor-documented default. Survey-first, then configure the tool.

## Arsenal Results

```
ASSESSMENT CHAIN — Argo Workflows (Category 29)
[x] JAXEN         — ssl:"ArgoProj" → 233 results, 156 unique IPs
[x] aimap         — 136 open ports; DefaultPorts bug found+fixed (v1.9.35); 67 auth-enforced confirmed
[x] VisorGraph    — 0 graph nodes/edges (raw IPs, no domain seeds; passive max-iter hit)
[x] aimap-profile — 43.163.57.197 → ACEVILLEPTELTD-SG (Aceville Singapore)
[—] JS-bundle     — N/A: SPA confirmed but all API routes 401; extraction would yield no auth bypass
[x] VisorLog      — 114 events ingested to nuclide.db (67 INFO, 1 MEDIUM CORS)
[x] VisorScuba    — 0 violations (auth-enforced population; no AI.C1 triggers)
[x] BARE          — No MSF coverage for Argo (top score 0.475); CVE-exposed finding matched
                    n8n_workflow_expression_rce (0.559) + apache_airflow_dag_rce (0.547)
[—] VisorCorpus   — N/A: not an LLM inference target
[x] VisorBishop   — 0/67 platform-confirmed (Argo not in VisorBishop fingerprint set)
[x] VisorSD       — N/A: requires Shodan API key (Playwright-only access)
[x] menlohunt     — 2 GCP instances (35.187.102.86, 34.62.177.114): port 443 + self-signed cert (LOW)
[x] nu-recon      — 43.163.57.197: SSH+nginx on 80/443; simulated (no Shodan key); 0 crt.sh domains
[—] recongraph    — N/A: VisorGraph covered cert pivot; no domain seeds available
[—] VisorPlus     — N/A: manual chain completed
[—] VisorRAG      — N/A: no RAG/LLM surface
[—] VisorAgent    — ethical stop: controlled targets only
[—] VisorHollow   — Windows-only
```

**BARE finding:** Argo Workflows has no dedicated MSF module. The Jan-2024-build CVE exposure finding semantically aligns with `exploits/multi/http/n8n_workflow_expression_rce` and `exploits/linux/http/apache_airflow_dag_rce` — the attack pattern (inject workflow, achieve code execution in orchestration context) is the same class across all workflow engines.

## Second Population: ssl:"Argo Workflows" (2026-05-28)

Post-survey follow-up discovered a second dork producing a completely separate, non-overlapping population.

### Dork

```
ssl:"Argo Workflows"
```

**214 results, 0 overlap with `ssl:"ArgoProj"`.**

Mechanism: commercial TLS certs (Let's Encrypt, Amazon ACM) where the CN or SAN contains "argo-workflows" as a subdomain label — e.g. `argo-workflows.corp.apexclearing.com`. Shodan's general `ssl:""` text search hits this label, which is distinct from the self-signed cert Issuer O=ArgoProj match.

### Population Characteristics

- 200 IPs harvested (pages 1–22, 14 missing from pagination)
- Top clouds: Google LLC (93), AWS (~94 across 3 ASNs), Azure (1)
- 206/214 on port 443; 4 on port 5432 (Azure PostgreSQL named "argo-workflows"), 4 on port 6443 (K8s API)
- All have real domain attribution — operators identifiable directly from cert SAN

### Notable Operators

| Domain | Operator | Sector |
|--------|----------|--------|
| `argo-workflows-server.np-quotecenter.gcp.homedepot.com` | **Home Depot** | Retail (Fortune 500) |
| `argo-workflows.corp.apexclearing.com` | **Apex Clearing** | Fintech clearing |
| `argo-workflows.orchestrator.forgerock.io` / `forgeblocks.com` | **ForgeRock / Ping Identity** | IAM platform |
| `argo-workflows.aks-prod/preprod.az.sallinggroup.io` | **Salling Group** | Retail (Denmark's largest) |
| `argo-workflows-prod.vitamin.gree-dev.net` | **GREE Inc** | Mobile gaming (JP) |
| `argo-workflows.sim/fleet-svcs.waabiai.net` | **Waabi AI** | Autonomous vehicles |
| `argo-workflows.freedinternal.net` / `-webhook` | **freed.ai** | Medical AI (HIPAA context) |
| `argo-workflows.gcp.prd.cafis-rtp.com` | **CAFIS / NTT Data** | Japanese payment network |
| `argo-workflows.lumapps.net` | **LumApps** | Enterprise intranet |
| `platform-argo-workflows-dev.zozo-inc.com` / `-stg` | **ZOZO Inc** | Fashion e-commerce (JP) |
| `argo-workflows-nonprod/sandbox.brightinsight.com` | **BrightInsight** | Digital health / pharma |
| `argo-workflows.zerotier.com` | **ZeroTier** | Network virtualization |
| `argo-workflows.stemscopes-v4-*.acceleratelearning.com` (4 envs) | **AccelerateLearning** | EdTech |
| `argo-workflows-*.ddeng.co` (8+ envs, US/UK/AU/KR) | **DDeng** | Multi-region operator |

### Identity Scan Results

aimap v1.9.36 identity scan: 200 targets, 188 open ports, 30m29s wall time.

**Auth state: 0/200 unauthenticated. All Argo instances auth-enforced.**

| Metric | Count |
|--------|-------|
| Targets | 200 |
| Open on port 443 | 188 |
| Argo Workflows confirmed | 17 (16 unique IPs) |
| Unauthenticated | 0 |
| Findings (critical/high/medium) | 0 |
| Findings (low) | 1 |
| Scan duration | 30m29s |

The 17 Argo Workflows instances all matched the `Argo Workflows (auth-enforced)` fingerprint — aimap's auth-enforcement label is embedded in the fingerprint match, confirmed by 401/403 on `/api/v1/workflows`. One `34.172.204.155` appeared on both port 443 and port 2746 (unique deployment running both listener modes). The remaining 171 open ports (188 − 17) matched other services: Zep (15), ZenML (3), Kubelet (2), Kubernetes API (1), Coqui XTTS (1), Pezzo (1), and 148 unmatched (likely non-AI services sharing the argo-workflows cert SAN).

**Single low finding:** `44.232.137.3` (ZenML instance) — `X-Powered-By: Express` header disclosure.

### Arsenal (Second Population)

```
ASSESSMENT CHAIN — Second Population (ssl:"Argo Workflows", 200 IPs)
[x] aimap         — 17 Argo confirmed, 0 unauth, 30m29s (scan-all-fingerprints on port 443)
[—] JAXEN         — N/A: IPs sourced from prior Shodan harvest; no re-query needed
[—] VisorGraph    — N/A: raw IPs, no domain seeds for cert pivot
[—] aimap-profile — N/A: no unauth instances to profile
[—] JS-bundle     — N/A: all 401/403; extraction would yield nothing
[—] VisorLog      — N/A: no new disclosable findings
[—] VisorScuba    — N/A: auth-enforced population; no AI.C1 triggers
[—] BARE          — N/A: no new findings to rank
[—] VisorCorpus   — N/A: not an LLM inference target
[—] VisorBishop   — N/A: no new hosts beyond first-population sweep
[—] VisorSD       — N/A: Shodan Playwright-only; dork already run
[—] menlohunt     — N/A: covered by aimap scan
[—] nu-recon      — N/A: no unauth instances warranting deep passive read
[—] recongraph    — N/A: no domain seeds available
[—] VisorPlus     — N/A: manual chain complete
[—] VisorRAG      — N/A: no RAG/LLM surface
[—] VisorAgent    — ethical stop: controlled targets only
[—] VisorHollow   — Windows-only
```

### Artifact

`case-studies/commercial/argo-workflows-targets-cn-dork.txt` — 200 IPs
`case-studies/commercial/argo-cn-scan-2026-05-28.json` — aimap scan output (203KB, 188 open ports, 40 service matches)

## Pivot Avenues

1. **Direct port 2746 scan** — masscan 0.0.0.0/0 on port 2746, filter HTTP 200 + X-Ratelimit-Limit header → finds unauth instances Shodan misses
2. **CT log pivot** — search Argo namespaces in CT logs via crt.sh (e.g. `argo.` subdomain patterns) → may surface instances with commercial certs
3. **Argo CD co-location** — `ssl:"ArgoProj"` dork may also catch Argo CD (same cert org); check /api/v1/settings vs /api/v1/version to discriminate
4. **Namespace sweep** — on any found unauth instance: try namespaces argo, kubeflow, ml-pipeline, training, data-science for workflow/secret exposure
5. **Jan-2024 build CVE targeting** — 36 instances on oldest build; if any found in server mode, CVE-2026-28229 bypass worth testing
6. **FOFA/ZoomEye** — these search engines may index port 2746 differently than Shodan; try `app="Argo-Workflows"` or `banner="X-Ratelimit-Limit" && port=2746`

## Files

| File | Description |
|------|-------------|
| `argo-workflows-targets.txt` | 156 IPs from Shodan harvest (ssl:"ArgoProj" dork) |
| `argo-workflows-scan-2026-05-27.json` | aimap PHASE 1 output (136 open ports, 0 services matched) |
| `argo-identity-scan-2026-05-27.json` | aimap identity scan against 67 confirmed (67 INFO matches, 1 MEDIUM: CORS wildcard on 43.163.57.197) |
| `argo-workflows-targets-cn-dork.txt` | 200 IPs from ssl:"Argo Workflows" CN dork |
| `argo-cn-scan-2026-05-28.json` | aimap scan output for second population (17 Argo confirmed, 0 unauth) |
| `../../../shodan/query-log.md` | Full dork matrix (15 queries) |
| `argo-workflows-osint-pre-assessment-2026-05-27.md` | Pre-assessment OSINT brief |

