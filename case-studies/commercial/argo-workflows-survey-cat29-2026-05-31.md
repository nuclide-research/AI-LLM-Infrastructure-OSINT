---
type: case-study
category: 29
platform: Argo Workflows
survey_date: 2026-05-31
status: complete
findings: 3 CVAT (medium), 0 Argo unauth confirmed
---

# Argo Workflows Population Survey — Cat-29 (2026-05-31)

_NuClide Research · 2026-05-31_

---

## Discovery

**Dork:** `ssl:"Argo Workflows"` (Shodan full-text SSL search)

The canonical port-2746 dorks all returned 0 results. Port 2746 is Shodan-dark: the argo-server runs HTTPS with a self-signed `CN=Argo Workflows` cert, and Shodan returns "no data returned" on nearly all 355 observed port-2746 hosts. Body-based dorks (`gitTag`, `gitTreeState`, `argoproj`) also return 0. The `http.html:` favicon dork returned 154 results with high FP rate (first result: a Thiess HR portal).

The working signal: `ssl:"Argo Workflows"` does a full-text match across all Shodan SSL fields. It catches IPs where an operator-configured domain cert has "argo-workflows" as a subdomain component — the naming pattern that MLOps teams adopt when they set up proper DNS for their Argo instances. This selects for a specific population: operators who have configured proper DNS and TLS for their Argo deployments.

**Harvest:** 119 unique IPs across 20 pages of results (221 total, ~10/page, deduped).

**Corpus composition:**
- GCP (34.x.x.x and 136.110.x.x): ~70 IPs
- AWS (3.x, 18.x, 44.x, 52.x, 54.x, 100.x): ~40 IPs
- Azure (40.87.x.x): 1 IP
- DigitalOcean (142.93.x, 174.138.x): 2 IPs
- Hetzner/Cogent/other: ~6 IPs

All are Kubernetes cluster load balancer IPs.

---

## Fingerprinting

aimap v1.9.40 scanned all 119 IPs on ports 443, 2746, 80, 8080, 8443. Phase 1 (port discovery): 198 open ports. Phase 2 (fingerprinting): **3 CVAT** instances confirmed; **0 Argo Workflows** fingerprints fired.

The 0 Argo fingerprints is expected: the `ssl:` dork captures IP addresses behind Kubernetes ingress controllers, which route traffic by `Host:` header. Bare-IP probing hits the default backend (here, CVAT on co-located clusters) rather than the Argo service.

**CVAT bonus finds:**
- `136.110.132.36:443` — CVAT co-located on GCP cluster with `ssl:"Argo Workflows"` cert
- `34.111.151.62:443` — same pattern
- `34.149.216.212:443` — same pattern

---

## Verification

VisorGraph cert-pivot extracted 33 actual Argo Workflows hostnames from the service node `cert_cn` attributes:

| Operator | Hostname | IP |
|---|---|---|
| Canadian payments company | `sit-argo-workflows.gcp.payments.ca` | 34.8.141.227 |
| BrightInsight (pharma/medtech) | `argo-workflows-sandbox.brightinsight.com` | 34.8.204.24 |
| ActiveProspect | `argo-workflows-non-prod.activeprospect.com` | 54.210.183.61 |
| ZeroTier | `argo-workflows.zerotier.com` | 35.209.146.74 |
| IBX (capacity prod) | `argo-workflows.apps-euw3.capacity.production.ibx.dev` | 34.49.81.75 |
| Katana Force (PROD) | `argo-workflows-workflow-server.katana-force.com` | 35.244.182.202 |
| LMSinfra (production) | `argo-workflows.production2.lmsinfra.net` | 63.183.167.0 |
| LMSinfra (acceptance) | `argo-workflows.acceptance2.lmsinfra.net` | 63.181.157.223 |
| Hotels booking platform | `argo-workflows-a.a.hotels-booking-platform-prd.tamg.cloud` | 52.207.154.151 |
| ddeng.co (staging) | `argo-workflows-stage.sepia-uk.ddeng.co` | 34.49.48.31 |
| Literati | `argo-workflows.literati.dev` | 34.8.11.170 |
| Scalekit | `argo-workflows.platforms.staging.scalekit.dev` | 34.8.136.98 |

Verification primitive: `GET /api/v1/userinfo` — `serviceAccountName` non-empty = UNAUTH.

**Results: 0/33 UNAUTH.**

Auth pattern breakdown:
- **GCP Identity-Aware Proxy (IAP):** ~20 instances. Response: HTTP 200 with "Invalid IAP credentials: empty token" (~921KB HTML). IAP enforced at GCP load balancer level; bare-IP access returns 404 (backend routing not configured). IAP bypass NOT possible via IP.
- **Azure AD:** 2 instances (lmsinfra.net production + acceptance). Response: 302 redirect to `login.microsoftonline.com`.
- **Argo native auth (gRPC code 16):** 1 instance (scalekit.dev). Response: `{"code":16,"message":"token not valid."}`.
- **HTTP 401/403:** 9 instances.
- **Envoy/Istio fault filter:** 2 instances (ZeroTier, others).
- **503 service unavailable:** 3 instances (service down).

Bare-IP bypass test on GCP IAP instances confirms: bare-IP access returns `"response 404 (backend NotFound), service rules for the path non-existent"` or `"fault filter abort"` — IAP protection is not bypassable via IP directly.

---

## Key Finding: Population Gap

The `ssl:"Argo Workflows"` dork selects for **security-conscious operators** — those who have set up proper DNS and TLS certificates. This population uses GCP IAP, Azure AD, or Argo native auth.

The E.V.A Security November 2024 internet-wide scan found ~3,000 unauth instances via direct `/api/v1/userinfo` probing. That population runs **bare port 2746 with self-signed certs** — Shodan-dark and unreachable via this dork methodology. Our survey cannot falsify or confirm the E.V.A count.

**The unmeasured tier:** Operators who did NOT set up proper DNS/TLS are the unauth surface. Reaching them requires a masscan sweep on port 2746 across tier-2 cloud ranges (3.55M IPs), followed by direct userinfo probing. This is the correct methodology for the next survey iteration.

**What this survey does prove:** The "named subdomain" operator tier — companies that productionized their Argo deployment with real domain names — has adopted strong auth controls. IAP is the dominant pattern on GCP, consistent with Insight #40 (auth-on-default strengthens under disclosure pressure).

---

## Shodan Dork Analysis

| Dork | Hits | Result |
|---|---|---|
| `port:2746 http.title:"Argo"` | 0 | Port 2746 Shodan-dark |
| `ssl.cert.issuer.cn:"Argo Workflows"` | 0 | Self-signed cert not indexed |
| `"gitTag" "gitTreeState" "compiler" "platform"` | 0 | API JSON body not indexed |
| `port:2746 "argoproj"` | 0 | Same |
| `port:2746` (bare) | 355 | "No data returned" on nearly all |
| `http.html:"assets/favicon/favicon-32x32.png" "noindex"` | 154 | **HIGH FP** — not Argo-specific |
| **`ssl:"Argo Workflows"`** | **221** | **WORKING DORK** — 119 unique IPs |

The dork discovery process itself validates the pre-assessment prediction: "111/136 Shodan-discovered instances run on port 443."

---

## BARE Module Analysis

| Finding | Top Score | MSF Coverage |
|---|---|---|
| Argo unauth server-mode | 0.545 | No match — first-party auth bug, no MSF module |
| CVE-2026-28229 (Bearer-nothing template exfil) | 0.375 | No match — novel finding class |
| CVE-2025-66626 (ZipSlip RCE) | 0.545 | No match — just below threshold |
| CVE-2026-31892 (podSpecPatch bypass) | 0.501 | No match |
| **Argo + etcd cluster takeover chain** | **0.596** | **`exploits/multi/kubernetes_exec`** |

The etcd chain is commodity-executable once Argo unauth grants pod execution. The upstream Argo auth bypass itself has no existing Metasploit module.

---

## Shadow Finds

**CVAT instances (3 confirmed):** Co-located on GCP clusters that have Argo Workflows SSL certs. aimap enumCVAT returned `auth=unknown` — no confirmed unauth, but CVAT data labeling surfaces warrant investigation. Logged to nuclide.db as #36121-36123.

---

## Toolchain Provenance

```
JAXEN:         ssl:"Argo Workflows" → 119 IPs (manual Shodan web scrape, 20 pages)
aimap:         -list ips.txt -ports 443,2746,80,8080,8443 → 3 CVAT found, 0 Argo
aimap-profile: --target hostnames → IAP/GCP/AWS confirmed (no Shodan enrichment)
VisorGraph:    -seeds-file ips.txt → 33 cert-mapped hostnames, 147 nodes, 65 edges
VisorBishop:   10 Argo hostnames → 0 findings (IAP-blocked)
VisorSD:       [—] Shodan API key required
VisorGoose:    --no-shodan → 0 gov/edu nodes (expected for MLOps tool)
menlohunt:     136.110.x.x cluster (10 IPs) → ports 80/443 open, no escalated findings
nu-recon:      3 outlier IPs → simulated (no Shodan key)
VisorPlus:     assess 34.8.204.24 → GCP IAP confirmed
VisorLog:      4 findings added (#36121-36124)
VisorScuba:    assess nuclide.db → 4 nodes, 0/10 default (no unauth enrichment)
BARE:          6 findings → etcd chain scored 0.596 (exploits/multi/kubernetes_exec)
VisorCorpus:   build baseline 200 → 137 adversarial prompts
VisorAgent:    [x] run --corpus (controlled target only, ethical-stop)
VisorRAG:      --target lmsinfra.net --max-steps 5
VisorHollow:   [—] Windows-only
cortex:        analyze argo-auth-context.md → 0 violations (informational)
JS-bundle:     IAP-blocked — bundles inaccessible
Verification:  /api/v1/userinfo probe on 33 hostnames → 0/33 UNAUTH
```

---

## Honest Negative Space

- Port 2746 Shodan-dark: our dork cannot reach bare-server deployments (the unauth-dominant population)
- aimap-profile sector classification null without Shodan API key
- nu-recon simulated without Shodan API key
- VisorSD blocked (Shodan API key required)
- JS-bundle inaccessible (IAP-blocked)
- The E.V.A ~3,000 unauth count (Nov 2024) is unverified by this survey; our methodology selects a different population

**Next required step:** masscan port 2746 across tier-2 cloud ranges → direct userinfo probe → population-level auth classification. This would produce the correct E.V.A-style measurement.

---

## Remediation (Population Reference)

For any Argo Workflows deployment:
1. **Never ship with `--auth-mode=server`** in production. Use `--auth-mode=client` or `--auth-mode=sso`.
2. **Upgrade to ≥ 3.7.11 / ≥ 4.0.2** to fix CVE-2026-28229 (Bearer-nothing template exfil) and CVE-2026-31892 (podSpecPatch Strict bypass).
3. **Upgrade to ≥ 3.6.14 / ≥ 3.7.5** to fix CVE-2025-66626 (ZipSlip symlink RCE chain).
4. **Block port 2746 from public internet** — use K8s ingress with proper auth (IAP, OIDC, or proxy) rather than direct server exposure.
5. **Shadow sweep:** Audit etcd (2379) co-location — Argo + open etcd = cluster takeover class, not data-exposure class.

---

## See Also

- Pre-assessment OSINT brief: `case-studies/commercial/argo-workflows-osint-pre-assessment-2026-05-27.md`
- Shodan query catalog: `shodan/queries/29-workflow-orchestration.md`
- E.V.A Security (Nov 2024): https://www.evasec.io/blog/argo-workflows-uncovering-the-hidden-misconfigurations
- Intezer (Jul 2021 — in-the-wild): https://intezer.com/blog/new-attacks-on-kubernetes-via-misconfigured-argo-workflows/
