---
type: survey
category: 29-workflow-orchestration
target: Argo Workflows (global Shodan population)
date: 2026-05-27
status: complete
author: NuClide Research
---

# Argo Workflows: K8s-Native Workflow Orchestration Survey

## Executive Summary

Shodan survey of the global Argo Workflows population via TLS certificate fingerprint. **67 confirmed instances**. All tested instances auth-enforced. Critical finding: the vulnerable population (unauthenticated, port 2746 plain HTTP) is Shodan-dark — passive dork-based discovery cannot find it. Direct port scanning required for full exposure assessment.

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
| `argo-workflows-targets.txt` | 156 IPs from Shodan harvest |
| `argo-workflows-scan-2026-05-27.json` | aimap PHASE 1 output (136 open ports, 0 services matched) |
| `argo-identity-scan-2026-05-27.json` | aimap identity scan against 67 confirmed (INFO findings) |
| `../../../shodan/query-log.md` | Full dork matrix (15 queries) |
| `argo-workflows-osint-pre-assessment-2026-05-27.md` | Pre-assessment OSINT brief |

