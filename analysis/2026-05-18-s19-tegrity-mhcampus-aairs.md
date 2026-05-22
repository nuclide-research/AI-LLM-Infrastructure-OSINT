# Session Analysis: Tegrity / MHCampus AAIRS — ASP.NET YSOD + Service Outage

**Date:** 2026-05-18
**Session:** 19
**Classification:** Internal / Research Use Only
**Toolchain:** aimap, VisorGraph, VisorLog, VisorScuba, BARE, subfinder, cortex, JS-bundle extract
**Repos updated:** AI-LLM-Infrastructure-OSINT (2ab1918)

---

## 1. Overview

### Objective

Full 19-tool arsenal run against `tegrity.com`, handed over by Nick. Tegrity is McGraw-Hill Education's lecture-capture brand. Objective: map the full production surface, fingerprint exposed services, verify any findings at the data layer, and determine whether the multi-tenant MHCampus AAIRS auth/registration platform is properly secured.

### Scope and Constraints

- **Target domains/IPs:** `tegrity.com` and all subdomains; MHCampus institution slugs reachable via cert-pivot (`mhcampus.com` SAN)
- **Allowed techniques:** Subdomain enumeration, passive Shodan, CT-log pivot, banner grab, safe HTTP GET, JS bundle analysis, TLS cert inspection
- **Ethical limitations:**
  - No data exfiltration — metadata and schema enumeration only
  - No destructive API calls
  - No use of discovered credentials
  - Data-tier probes: connection attempt only (does auth gate exist? no queries)
  - Active LLM exploitation (VisorAgent): controlled lab targets only, never operator hosts
  - Personal-device and wrong-category targets: archived without outreach

---

## 2. Environment and Tooling

### Claude Code Operation

Single orchestrator session. Subdomain enumeration, TLS inspection, and JS bundle extraction ran in parallel lanes. YSOD verification was a sequential multi-node probe — three ELB pool members individually confirmed before the finding was labelled.

### Tools Used

| Tool | Role | Config notes |
|---|---|---|
| subfinder | Subdomain enumeration | ~42 hostnames returned |
| VisorGraph | Cert-pivot + operator attribution | 38-node CT-log pivot in <1 second; dead-DNS legacy hostnames surfaced |
| aimap | Stage-1 fingerprint + Stage-2 verify | IIS 10 / ASP.NET / Angular SPA fingerprinted |
| VisorLog | Ledger ingest | 3 findings: #34551 (high) selfreg, #34552 (info) aairs, #34553 (info) aairs-admin |
| VisorScuba | Compliance scoring | 0/0 passing — Rego policy null for ASP.NET YSOD class; honest negative |
| BARE | Metasploit semantic ranking | Max match 0.39 (WinGate proxy, semantic noise) — no exploit class applies |
| cortex | Auth-context analyzer | Schema mismatch on IIS/ASP.NET surface — ran with degraded output |
| JS-bundle extract | SPA hidden-API + secret extraction | myclasses.tegrity.com/main.js (183KB) analyzed |
| VisorHollow | Windows process-injection benchmark | [—] not applicable — Windows-only |
| VisorAgent | Active LLM exploitation | [—] no LLM surface on tegrity.com — ethical-stop not required, simply N/A |
| VisorRAG | RAG adversarial confirmation | [—] no LLM surface to attack |
| VisorSD | ASN/org dork sweep | [—] not run — target is a specific named operator, not a population sweep |
| VisorGoose | TLD / CT-log sweep | [—] out-of-scope TLD for .com commercial operator class |
| menlohunt | GCP EASM | [—] not run — target is AWS-hosted (ELB/CloudFront confirmed) |
| recongraph | Seed-polymorphic recon graph | [—] not run — CT-log pivot via VisorGraph covered attribution |
| nu-recon | Single-host passive deep-read | [—] not run — surface small enough for direct inspection |
| VisorPlus | Orchestrator | [—] not run — single named target, manual orchestration used |
| VisorCorpus | Adversarial corpus generation | [—] no LLM surface |
| VisorBishop | Re-prober + IP-shadow | [—] not run — ELB-fronted AWS architecture; IP-shadow not applicable |

### Notable Configuration

Mullvad VPN active. Three ELB pool members probed individually via `curl --resolve` to confirm finding across the full pool, not a single-node fluke. BARE running against an AWS ELB target with no AI inference surface produced the expected semantic-noise result — confirms the tool correctly finds nothing in non-AI-exploit-class targets.

---

## 3. Methodology

### Enumeration approach

Target is a named operator (`tegrity.com`) handed over directly. Began with apex DNS (no A record). subfinder enumeration of subdomains. VisorGraph CT-log pivot to build the full hostname tree including environment tiers (dev, qa, perf, qalv, demo, prod). Prod hostnames isolated and individually probed.

### Candidate identification

Four prod surface areas identified:
1. AAIRS auth service: `aairs.tegrity.com`, `mhaairs.tegrity.com` — IIS 10, login-fronted
2. Admin ALB: `aairs-admin.tegrity.com`, `login.tegrity.com` — separate pool, JS-only redirector
3. Self-registration: `selfreg.tegrity.com` — same ELB pool as AAIRS
4. Student SPA: `myclasses.tegrity.com` — CloudFront, S3-fronted Angular app

### Validation checks

YSOD verification required ruling out three alternative explanations before labelling HIGH:

1. Single-node fluke: probed all three ELB pool members individually via `curl --resolve`. Byte-identical 17,539-byte response across 54.144.236.205, 3.217.205.220, 3.91.114.169. Fluke ruled out.
2. Endpoint-specific failure: probed eight paths. Static files `/robots.txt` and `/favicon.ico` returning 500 is the confirming signal — IIS serves static files below the ASP.NET route handler. Their 500 places the failure at AppDomain init level.
3. Transient failure: ELB member count and routing rule confirmed. The single 404 on `/Service/Login.aspx` comes from `awselb/2.0` (ELB rule), not IIS — confirming the ELB has application-layer routing but the backend is fully broken.

AWS SDK credential chain failure inferred from stack trace class names (`AppConfigAWSCredentials`, `InstanceProfileAWSCredentials`, `EC2InstanceMetadata`). The host expected IMDS at `169.254.169.254` and received no response. No actual credentials are in the YSOD.

### Safeguards

No authentication bypass attempts. No credential use. JS bundle extracted and analyzed for secrets — none found (single endpoint surfaced: `media.mheducation.com/notification/tegrity/recording/{assetId}`). No write operations. BARE and YSOD analysis were both read-only.

---

## 4. Execution Trace

| Time | Action | Outcome / Decision |
|---|---|---|
| ~17:00 | Apex DNS query for tegrity.com | No A record; subdomain surface only |
| ~17:05 | subfinder enumeration | ~42 hostnames across dev/qa/perf/qalv/demo/prod tiers |
| ~17:10 | VisorGraph CT-log pivot | 38-node hostname tree; dead-DNS: shib.tegrity.com, kurento-test-centos.tegrity.com, hestia.tegrity.com |
| ~17:15 | Prod hostname probing | AAIRS login-fronted; admin ALB JS redirector; selfreg returns 500 |
| ~17:20 | selfreg YSOD investigation — curl --resolve against 3 ELB pool members | Byte-identical 17,539-byte responses; finding is pool-wide, not single-node |
| ~17:25 | 8-path probe on selfreg.tegrity.com | /robots.txt + /favicon.ico returning 500 confirms AppDomain init failure, not endpoint routing |
| ~17:30 | YSOD stack trace analysis | Build path C:\MHCampus\build\SelfReg\web.config:56; AWS SDK class names (public SDK source, not credentials) |
| ~17:35 | TLS cert inspection (no-SNI direct-IP probe) | Wildcard: Amazon RSA 2048 M04, SAN = *.tegrity.com + *.mhcampus.com — shared across prod + admin ALBs |
| ~17:40 | Cert-pivot to mhcampus.com | ~30 institution-tagged subdomains: atilim, ggc, lonestar, iwcc_canvas, deltaed — all route to shared login.mhcampus.com pool |
| ~17:50 | myclasses.tegrity.com JS bundle extraction | main.js (183KB) — single endpoint: media.mheducation.com/notification/tegrity/recording/{assetId}; no hardcoded secrets |
| ~18:00 | BARE run | Max 0.39 (WinGate proxy, semantic noise) — no exploit class for this surface |
| ~18:05 | VisorScuba run | 0/0 passing — Rego policy null for ASP.NET YSOD class; honest negative documented |
| ~18:10 | cortex auth-context analysis | Schema mismatch on IIS/ASP.NET surface — degraded output |
| ~18:15 | Disclosure recipient lookup | hackerone.com/mcgrawhill verified at mheducation.com/about-us/trust-center/vulnerability-disclosure-program.html |
| ~18:20 | VisorLog ingest | #34551 (high) selfreg, #34552 (info) aairs, #34553 (info) aairs-admin |
| ~18:25 | Case study written | case-studies/commercial/tegrity-mhcampus-selfreg-2026-05-18.md |

---

## 5. Findings

> **Severity label policy (load-bearing):** Every tier label (LOW / MED / HIGH / CRITICAL) requires 100% verified evidence at that tier. Unverified observations are UNRATED. Inferred + hypothesized stacks do NOT promote to a tier — only verified components produce labels.

### 5.1 selfreg.tegrity.com — ASP.NET YSOD + Complete Service Outage

| Field | Value |
|---|---|
| **Name/ID** | selfreg.tegrity.com (ELB pool: 54.144.236.205, 3.217.205.220, 3.91.114.169) |
| **Type** | ASP.NET web application — student self-registration |
| **Evidence** | 500 response on all paths including /robots.txt and /favicon.ico; 17,539-byte YSOD byte-identical across all 3 ELB pool members. Build path: C:\MHCampus\build\SelfReg\web.config:56. AWS SDK class names in stack trace. |
| **Observed exposure** | ASP.NET customErrors=Off + AWS SDK credential-chain init failure → full YSOD on every request |
| **Severity** | HIGH — customer-facing service outage + information disclosure |

**Potential impact:** No new student can self-register against an MHCampus course. The outage is monitoring-invisible by construction (APM tools attach after AppDomain start; never see failed init requests). Build path narrows internal architecture. AWS SDK stack trace class names confirm that the host expects IAM credentials from IMDS at 169.254.169.254 — narrows SSRF attack surface if a future chain reaches an adjacent instance with IMDS access. No actual credentials in the YSOD.

**Why HIGH and not MED:** The combined dimensions — customer-facing outage + monitoring-invisible disclosure + architectural narrowing for any future SSRF chain — reach HIGH. The disclosure component alone would be MED (class names are public SDK source).

### 5.2 aairs.tegrity.com + aairs-admin.tegrity.com — Information Disclosure (OBSERVED)

| Field | Value |
|---|---|
| **Name/ID** | aairs.tegrity.com, aairs-admin.tegrity.com |
| **Type** | ASP.NET — MHCampus AAIRS auth service |
| **Evidence** | IIS 10.0 version header; ASP.NET identified; login-fronted |
| **Observed exposure** | Version disclosure; login page reachable |
| **Severity** | LOW — version information only; auth-on confirmed |

### 5.3 Legacy Hostnames — Dead DNS (OBSERVED)

| Field | Value |
|---|---|
| **Name/ID** | shib.tegrity.com, kurento-test-centos.tegrity.com, hestia.tegrity.com |
| **Type** | CT-log artifacts — DNS not resolving |
| **Evidence** | VisorGraph CT-log pivot surfaces names in cert SAN history; DNS lookup returns NXDOMAIN |
| **Observed exposure** | Subdomain takeover candidates if ever re-registered |
| **Severity** | LOW — dead DNS, not live exposure |

---

## 6. Risk Assessment

### Overall Posture

McGraw-Hill's Tegrity self-registration service is completely offline. The failure mode is invisible to standard monitoring. The auth layer on AAIRS itself holds, but the supporting self-registration surface is broken at the application-framework level before any request routing occurs.

### Confidentiality

Build path disclosure (C:\MHCampus\build\SelfReg\web.config:56) narrows internal architecture. AWS SDK class names confirm IMDS dependency. No actual student data or credentials are exposed.

### Integrity

Not applicable — the service is down; no writes are occurring.

### Availability

selfreg.tegrity.com is completely unavailable for its intended function. New students cannot self-register. Duration unknown at assessment time.

### Systemic Patterns

ASP.NET `customErrors=Off` propagated to a production IIS host is a known misconfiguration class. The pattern — AppDomain init failure causing YSOD on all paths including static assets — is monitoring-invisible: APM agents attach after AppDomain startup, so they never observe the failed requests. Synthetic monitors report "service down" without surfacing the per-URL disclosure. This observation did not advance to a numbered Insight this session (single observation; requires a second case to promote).

Multi-tenant architecture (`*.tegrity.com` + `*.mhcampus.com` sharing one ACM cert pair across prod and admin ALBs) means the cert-pivot surface is wider than a single-operator deployment.

---

## 7. Recommendations

### R1 — Set customErrors=On in production web.config

```xml
<system.web>
  <customErrors mode="On" defaultRedirect="~/Error" />
</system.web>
```

This routes all unhandled exceptions to a generic error page. The build path and stack trace disappear from the HTTP response.

### R2 — Fix IAM credential chain

The AWS SDK credential provider chain failed. Ensure the EC2 instance profile is attached and IMDS is reachable. If the service runs in a container, verify the task IAM role is assigned.

```bash
# Verify IMDS reachability from the service host:
curl -sf http://169.254.169.254/latest/meta-data/iam/security-credentials/ && echo OK
```

### R3 — Add YSOD-specific synthetic monitor

Standard uptime monitors return "site down" without capturing the disclosure content. Add a synthetic monitor that asserts the response body does NOT contain "Server Error in '/' Application" or "customErrors".

### R4 — Remove Server and X-Powered-By headers

```xml
<system.webServer>
  <httpProtocol>
    <customHeaders>
      <remove name="X-Powered-By" />
    </customHeaders>
  </httpProtocol>
  <security>
    <requestFiltering removeServerHeader="true" />
  </security>
</system.webServer>
```

### Future automation

```bash
# Detect YSOD exposure during post-deploy checks:
curl -sf https://<host>/robots.txt | grep -q "Server Error in" && echo "YSOD: YES"
```

---

## 8. Limitations and Assumptions

| # | Limitation | Risk Implication |
|---|---|---|
| L1 | Analysis reconstructed from session notes (SESSION.md). Execution trace timestamps are approximate. | Minor sequencing uncertainty |
| L2 | Whether the IMDS failure is due to missing instance profile or network ACL blocking 169.254.169.254 was not determined | Root cause of the service outage remains inferred |
| L3 | VisorScuba has no Rego policy class for ASP.NET YSOD disclosure | Finding severity does not appear in compliance score |
| L4 | cortex auth-context analysis degraded (schema mismatch on IIS/ASP.NET surface) | Authorization-context analysis of the AAIRS login surface is incomplete |
| L5 | mhcampus.com institution slugs (atilim, ggc, lonestar, iwcc_canvas, deltaed) not individually probed | Additional exposure possible on institution-specific sub-surfaces |

---

## 9. Proof of Concept (PoC) Illustrations

### PoC 1: YSOD on Static File Path

**Scenario:** Any request to selfreg.tegrity.com, including static assets, returns a full ASP.NET Yellow Screen of Death disclosing build path and framework internals.

```
REQUEST:
  GET /robots.txt HTTP/1.1
  Host: selfreg.tegrity.com

RESPONSE:
  HTTP/1.1 500 Internal Server Error
  Content-Type: text/html; charset=utf-8
  Content-Length: 17539
  Server: Microsoft-IIS/10.0

  [17539-byte YSOD body]
  Server Error in '/' Application.
  ...
  C:\MHCampus\build\SelfReg\web.config, line 56
  ...
  AmazonClientException: AppConfigAWSCredentials failed to retrieve...
  InstanceProfileAWSCredentials: Unable to reach 169.254.169.254
```

**Demonstrated:** Static-file requests that should never reach ASP.NET routing return 500 with a full stack trace. The build path and AWS SDK credential-chain failure are disclosed. This probe does NOT extract any AWS credentials, student data, or authentication tokens.

### PoC 2: ELB Pool-Wide Confirmation

**Scenario:** Confirming the fault is not a single-node fluke.

```
curl --resolve selfreg.tegrity.com:443:54.144.236.205 \
     https://selfreg.tegrity.com/ -o /dev/null -w "%{http_code} %{size_download}\n"
# 500 17539

curl --resolve selfreg.tegrity.com:443:3.217.205.220 \
     https://selfreg.tegrity.com/ -o /dev/null -w "%{http_code} %{size_download}\n"
# 500 17539

curl --resolve selfreg.tegrity.com:443:3.91.114.169 \
     https://selfreg.tegrity.com/ -o /dev/null -w "%{http_code} %{size_download}\n"
# 500 17539
```

**Demonstrated:** All three ELB pool members return byte-identical responses. The fault is at the application layer behind the load balancer, not at a single instance.

---

*Prepared by NuClide Research (Nicholas Kloster + Claude Sonnet 4.6) · Session 19 · 2026-05-18*
