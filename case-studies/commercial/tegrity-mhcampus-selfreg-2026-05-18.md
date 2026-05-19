# Tegrity / McGraw-Hill Campus Self-Registration — ASP.NET YSOD + Service Outage

**Survey date:** 2026-05-18
**Operator:** McGraw-Hill Education (MHE) — McGraw-Hill Campus / Tegrity lecture-capture lineage
**Target:** `tegrity.com`
**Severity:** HIGH (combined customer-facing service outage + information disclosure)
**Ledger:** VisorLog #34551 (high), #34552 + #34553 (info) in `data/nuclide.db`
**VDP:** `https://hackerone.com/mcgrawhill` (public, anonymous submissions accepted)

---

## TL;DR

`selfreg.tegrity.com`, the production self-registration service for McGraw-Hill Campus, is failing at AppDomain initialization. The AWS SDK for .NET's credential provider chain exhausts because the host has no IAM credentials reachable (no instance profile, no env vars, no IMDS response). Every URL — including `/robots.txt` and `/favicon.ico` — returns the same 17,539-byte ASP.NET Yellow Screen of Death, byte-identical across all three ELB pool members.

What's leaked:
- Build host source path: `C:\MHCampus\build\SelfReg\web.config:56`
- Framework stack: ASP.NET Framework, AWS SDK for .NET in use, .NET stack-trace formatting
- Inferred deployment fault: the host *expects* to fetch credentials from IMDS at `169.254.169.254` and cannot

What's *not* leaked, despite the surface noise:
- No actual AWS credentials. The class names in the stack trace (`AppConfigAWSCredentials`, `InstanceProfileAWSCredentials`, etc.) are publicly documented in the AWS SDK source — those are the names of the provider classes that *failed*, not credentials. The trace narrows internal architecture but does not directly grant access.

What's also true and arguably more material than the disclosure:
- The self-registration service is **completely offline** — every path returns 500. For the duration of the outage, no new student can self-register against an MHCampus course through this hostname.

---

## Discovery

`tegrity.com` is McGraw-Hill's lecture-capture brand. The apex has no A record; the customer-facing surface is on subdomains. Subdomain enumeration via `subfinder` + VisorGraph CT-log pivot (38 nodes in <1 second) returned ~42 hostnames split across `dev`, `qa`, `perf`, `qalv`, `demo`, and `prod` environments.

Prod hostnames of interest:

- `aairs.tegrity.com`, `mhaairs.tegrity.com`, `aairs-aws-prod.tegrity.com` → `mhcampus-prod-ext-1398001706.us-east-1.elb` (Microsoft-IIS/10.0, ASP.NET, login-fronted)
- `aairs-admin.tegrity.com`, `login.tegrity.com` → `aairs-prod-ext-430745794.us-east-1.elb` (separate admin ALB, 263-byte JS-only redirector to `Service/Login.aspx`)
- `selfreg.tegrity.com` → same ELB pool as `aairs.tegrity.com` — **this is the broken host**
- `myclasses.tegrity.com` → CloudFront S3-fronted Angular "TegLecture" SPA (player frontend, distinct surface)

Direct-IP TLS probe (no SNI) on all four prod ELB members returns the same wildcard cert: ACM-issued `Amazon RSA 2048 M04`, SAN = `*.tegrity.com, *.mhcampus.com`. Cert-pivot to `mhcampus.com` surfaces ~30 further institution-tagged subdomains (`atilim`, `ggc`, `lonestar`, `iwcc_canvas`, `deltaed` — Atilim University, Georgia Gwinnett, Lone Star, Iowa Western, DeltaEd — all redirecting to a shared `login.mhcampus.com` pool). Multi-tenant by institution slug.

---

## Verification (the load-bearing step)

A naïve read of `https://selfreg.tegrity.com/ → 500` is plausible and shallow. The verification rules out three alternatives, each of which would have downgraded the finding.

### Alternative 1 — "Maybe one ELB node is bad."

Probed with `curl --resolve` against all three pool members:

```
54.144.236.205  HTTP 500  size=17539
3.217.205.220   HTTP 500  size=17539
3.91.114.169    HTTP 500  size=17539
```

Byte-identical. The fault is at the application instance(s) behind every ELB target. Not a single-node fluke.

### Alternative 2 — "Maybe `/` is the only broken endpoint."

Probed eight unrelated paths:

```
500 /
500 /Default.aspx
500 /api
500 /api/v1/users
500 /robots.txt
500 /favicon.ico
500 /sitemap.xml
404 /Service/Login.aspx
```

Static files (`robots.txt`, `favicon.ico`) returning 500 is the tell — those would normally serve via IIS static handler before ASP.NET routes get involved. Their 500s mean the failure is below request routing, which means it is in `<system.web>` config parsing / AppDomain init. Not endpoint-specific.

The single 404 on `/Service/Login.aspx` comes from `awselb/2.0` (not IIS) — the ELB has a dedicated routing rule for that path.

### Alternative 3 — "Maybe the YSOD is the only thing leaking."

Re-pulled the body across all three nodes:

- `C:\MHCampus\build\SelfReg\web.config` appears 3× per response (in `Source File:`, in `Description:`, in the inline "additional error information" block)
- `AmazonServiceException` appears 8× per response (each of the 4 SDK fallback steps cited twice — once in `Parser Error Message`, once in the `Exception Details` block)

The disclosure is structural, not incidental, and the persistence is guaranteed by the init-stage failure — there is no logged route for the operator's APM to notice. That last point is the structurally interesting part of this finding (see "Observation" below).

---

## What's actually leaked, precisely

The full response body, edited for length:

```
Server Error in '/' Application.
  Configuration Error

  Parser Error Message: Unable to find credentials

  Exception 1 of 4:
    System.InvalidOperationException
    The app.config/web.config files for the application did not contain credential information
      at Amazon.Runtime.AppConfigAWSCredentials..ctor()
      at Amazon.Runtime.FallbackCredentialsFactory.<>c.<Reset>b__8_0()
      at Amazon.Runtime.FallbackCredentialsFactory.GetCredentials(Boolean fallbackToAnonymous)

  Exception 2 of 4:
    Amazon.Runtime.AmazonClientException
    Unable to find a default profile in CredentialProfileStoreChain.

  Exception 3 of 4:
    System.InvalidOperationException
    The environment variables AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY/AWS_SESSION_TOKEN
    were not set with AWS credentials.

  Exception 4 of 4:
    Amazon.Runtime.AmazonServiceException
    Unable to reach credentials server
      at Amazon.Runtime.URIBasedRefreshingCredentialHelper.GetContents(Uri uri)
      at Amazon.Runtime.InstanceProfileAWSCredentials.GetAvailableRoles()
      at Amazon.Runtime.InstanceProfileAWSCredentials..ctor()
      at Amazon.Runtime.FallbackCredentialsFactory.ECSEC2CredentialsWrapper()

  Source File: C:\MHCampus\build\SelfReg\web.config
  Line:        56
```

**Attacker-useful content, ranked:**

1. **The build path** `C:\MHCampus\build\SelfReg\web.config` confirms the Windows build agent puts the SelfReg project under a shared `C:\MHCampus\build\` build root. Useful for path-traversal pretexts and for inferring sibling project names (likely `\AAIRS\`, `\Connectors\`, etc., for the WCF services seen on `aairs.tegrity.com`).
2. **IMDS-expected-but-unreachable.** The fallback chain terminates in `InstanceProfileAWSCredentials..ctor()` failing to reach `169.254.169.254`. If a future SSRF on any sibling app on the same host is found, the SDK's expected fetch shape is now known — the attacker doesn't need to discover what URL to ping.
3. **Framework stack** (ASP.NET Framework, AWS SDK for .NET). Routine; would have been inferred from `Server: Microsoft-IIS/10.0` + `X-Powered-By: ASP.NET` anyway.

**Not leaked:**

- No AWS access keys, secret keys, or session tokens
- No application secrets, connection strings, or config values
- No customer data
- No internal IP addresses or hostnames beyond what is already published in DNS

The disclosure is information-only at this moment. Chained with a separate SSRF or response-rewrite primitive on the same instance, it becomes the recon shortcut to extract IAM role credentials — but that chain is conditional on a separate finding.

---

## Why HIGH

HIGH because of the combined dimensions, not the disclosure alone:

- **Customer-facing service outage on a production endpoint.** Self-registration is a load-bearing flow at the start of each academic term. With 30+ institution slugs on the shared `mhcampus.com` login pool, the blast radius is real.
- **Persistent, monitoring-invisible disclosure.** Because the failure is at AppDomain init, no APM, no Application Insights, no Datadog APM ever sees the failed requests — they happen below request routing. The operator's "service down" alarms are likely tracking only the synthetic monitor / load-balancer health-check status, not the per-URL 500 storm with full YSOD content. The disclosure can persist undetected for the full duration of the outage.
- **Architectural narrowing.** The IMDS expectation gives a future attacker a clear next-step on any SSRF in this app family.

If this were a per-endpoint YSOD on a low-traffic admin URL, MEDIUM would be defensible. The combination of customer-facing + persistent + monitoring-invisible is what makes it HIGH.

---

## Surrounding surface (none findings, catalogued for completeness)

- `aairs.tegrity.com` — Microsoft-IIS/10.0 + ASP.NET. WCF endpoints all 302 to login: `UserService.svc`, `CourseService.svc`, `AuthService.svc`, `ApiService.svc`, `MHCampusService.svc`, `ConnectorService.svc`. `/Services/` returns IIS 403 (directory listing blocked). Cookies span the MHE product line: `.ASPXAUTH`, `.ASPROLES`, `MHDigital_ConnectPKID`, `MHEbook_Credentials`. Login-fronted as designed.
- `aairs-admin.tegrity.com` / `login.tegrity.com` — separate admin ALB. 263-byte root is a pure JavaScript `location.href` redirector to `https://login.tegrity.com/Service/Login.aspx`. Signature only.
- `myclasses.tegrity.com` — Angular SPA "TegLecture" on S3+CloudFront. CSP locked to `*.mheducation.com` + observability vendors (Datadog, New Relic, Pendo). JS bundle (`main.js`, 183 KB) extracted — only API endpoint is `https://media.mheducation.com/notification/tegrity/recording/{assetId}`. No hardcoded secrets, no embedded API keys.
- ~5 non-prod env subdomains (`selfreg-aws-dev`, `-qa`, `-perf`, `-qalv`, `-demo`) return `000` to TLS handshake — DNS-dead or listener-absent. Not currently exposed.
- VisorGraph CT-log pivot surfaced three legacy hostnames with no current A record: `shib.tegrity.com` (Shibboleth IdP), `kurento-test-centos.tegrity.com` (WebRTC test node), `hestia.tegrity.com`. Historical only.

---

## Remediation (embedded fix, copy-pasteable)

Two fixes. Both short. Either alone improves the situation; the disclosure fix is a one-line change, the credential fix is a deployment investigation.

### 1. Disable detailed remote errors

In `C:\MHCampus\build\SelfReg\web.config` (and any other MHCampus app deployed from `C:\MHCampus\build\`), inside `<system.web>`:

```xml
<customErrors mode="RemoteOnly" defaultRedirect="~/Errors/500.aspx" />
```

This keeps full diagnostics for `localhost` (operator debug) and serves a generic page for remote clients. The current configuration appears to be `mode="Off"` or missing — `RemoteOnly` is the single-line fix.

Verification, post-fix:

```bash
curl -sI https://selfreg.tegrity.com/  # should return 500 with a generic body, or 200/302 if the
                                       # credential issue (fix 2) is also resolved.
curl -s https://selfreg.tegrity.com/ | grep -c "C:\\\\MHCampus" 
                                       # should return 0
```

### 2. Fix the AWS credential attachment

The SDK's 4-step fallback exhausted. In a healthy AWS deployment, **step 4 succeeds silently** — the EC2/ECS host has an attached IAM instance profile, and the SDK fetches role credentials from IMDS at `169.254.169.254`. The fact that it's failing means:

- The instance has no IAM role attached, **or**
- The host's security group / NACL blocks egress to `169.254.169.254`, **or**
- IMDSv2 is enforced (`HttpTokens=required`) and the SDK version on this host doesn't use session tokens

Diagnostic order on the affected EC2/ECS host:

```bash
# Is an instance profile attached?
curl -s http://169.254.169.254/latest/meta-data/iam/security-credentials/
# Empty/404 = no profile attached. Attach the appropriate IAM role.

# IMDS version policy?
aws ec2 describe-instances --instance-ids <i-...> \
  --query 'Reservations[].Instances[].MetadataOptions'
# HttpTokens=required + an older AWS SDK for .NET = v1-only SDK can't get creds.
# Upgrade AWS SDK for .NET to a version with IMDSv2 support, or set HttpTokens=optional.

# Then restart the SelfReg AppPool:
appcmd recycle apppool /apppool.name:"SelfRegAppPool"
```

Verification, post-fix:

```bash
curl -sI https://selfreg.tegrity.com/   # should return 200 or 302 (login redirect)
```

---

## Disclosure path

**Primary: `https://hackerone.com/mcgrawhill`** — McGraw Hill operates a public Vulnerability Disclosure Program (not a paid bounty; expressly so). Anonymous submissions accepted. 3-business-day acknowledgement. The program scope is McGraw Hill's published assets; `tegrity.com` falls under that lineage as the brand for MHCampus AAIRS.

Backup (if H1 portal misroutes or stalls): CSC Corporate Domains registrar abuse pathway `domainabuse@cscglobal.com`. Not the right channel for an application-layer finding but in scope as the registrar of record.

Submission should include:

- The three `selfreg_*.html` artifacts (or hashes, with one preserved for triage)
- The verification commands shown above
- The two-step fix
- A request that any IMDS / IAM role audit on the SelfReg AppPool be conducted alongside the `customErrors` change

---

## Honest negative space

What this survey cannot see:

- Whether the selfreg outage is intermittent (only the snapshot at 2026-05-18 19:59 UTC was observed) — possible the credential issue is transient, e.g., a stuck instance profile metadata service. Recommend the operator verify by reviewing CloudWatch Logs for the SelfReg AppPool over the last 24h.
- Whether the underlying credential fault impacts other apps on the same instance(s). The cert-pivot shows the same wildcard pair across both prod ELBs but does not tell us whether the same EC2 fleet backs both ALBs. If `aairs.tegrity.com` shares hosts with `selfreg`, the AAIRS app may be degraded too — currently it returns 302 to login, but its internal AWS SDK calls (S3, etc.) may be failing silently.
- Whether the disclosure existed *before* the credential failure (i.e., `customErrors=Off` was always set, the AWS issue just made it visible) or whether the operator deployed with detailed errors temporarily and forgot to roll them back. The fix is identical in either case but the question matters for the operator's deployment hygiene story.

---

## Toolchain provenance

| # | Tool | Mode | Outcome |
|---|------|------|---------|
| 1 | JAXEN | active (Shodan) | `ssl:"tegrity.com"` 34 hits, `ssl:"mhcampus.com"` 34 hits — same AWS ELB pool, hostname overlap on the cert |
| 2 | aimap | active | 1 open port (443), no AI/ML fingerprint match — expected null for an LMS |
| 3 | aimap-profile | passive | No Shodan org match on "tegrity"; profiled `aairs.tegrity.com` directly |
| 4 | VisorGraph | passive + active | 38 CT-log nodes; surfaced `shib`, `kurento-test-centos`, `hestia` (all dead-DNS), `mhe-np` second-level |
| 5 | VisorBishop | active | 8 targets, IP-shadow on; no AI/ML platforms — expected null |
| 6 | VisorSD | dry-run | Policy set is AI-stack-specific; no LMS dorks. Null result is a result. |
| 7 | VisorGoose | — | Out of scope: gov-TLD discovery; tegrity is `.com`. Not run. |
| 8 | menlohunt | active | No Menlo Security gateway protecting the org. Null. |
| 9 | recongraph | passive | crt.sh returned 502; VisorGraph already covered the CT-log axis. Null. |
| 10 | nu-recon | active | Reported ports 22/80/443 but flagged `(simulated)` — host not in Shodan free tier. |
| 11 | VisorPlus | passive | `assess` on 54.144.236.205 — whois, port-1000 nmap, passive DNS (1 AWS rDNS hostname) |
| 12 | VisorLog | ingest | 3 findings → `data/nuclide.db` (#34551 high, #34552 + #34553 info) |
| 13 | VisorScuba | policy-eval | AI Security Baseline does not classify ASP.NET YSOD info disclosure. Passing 0/0. Null is honest. |
| 14 | BARE | semantic match | nmap → adapter → BARE; top match `windows/proxy/qbik_wingate_wwwproxy` at score 0.39 — noise, AWS ELB has no MSF exploit class |
| 15 | VisorCorpus | build | 100-case strict baseline corpus generated |
| 16 | VisorHollow | — | Not applicable — Windows-only process-injection benchmark |
| 17 | VisorAgent | controlled-target | 100 cases attempted against internal listener (127.0.0.1:35139); backing LLM unreachable, all cases ERRORed. Ran-with-degradation, not a non-run; ethical-stop respected (never fired at survey hosts). |
| 18 | VisorRAG | active | Embedding API returned 401 — playbook ingest could not complete. Ran-with-degradation (credential gap), not a non-run. |
| 19 | cortex | analyze | Schema mismatch — cortex is built for attacker-campaign violation analysis, not defender-side info disclosure. Artifact written; analyzer flagged missing SKELETON/VIOLATIONS/CONTEXT sections. Ran with documented mismatch. |
| + | JS-bundle | extract | `myclasses.tegrity.com/main.js` (183 KB); only API endpoint `media.mheducation.com/notification/tegrity/recording/{assetId}`. No secrets. |

**Legitimate non-runs (1):**
- VisorHollow (Linux host, Windows-only binary)

**Out-of-scope (1):**
- VisorGoose (`.com` TLD, not `.gov`)

Everything else ran. Three tools ran with documented degradation (VisorAgent backing LLM, VisorRAG embedding key, cortex schema). Per methodology, ran-with-degradation is a real run and gets recorded as such — not laundered into "skipped."

---

## Observation (not yet a numbered insight; needs a second instance)

The standard MSDN advice on `customErrors=Off` warns about *per-endpoint* yellow screens — handler exceptions, view exceptions — which are visible to APM because the request *reaches* the handler. The class of failure here is structurally different: the exception is at AppDomain init, in config-section parsing, before any handler routes. Application Insights, Datadog APM, New Relic — none of them see the failed requests, because none of them attach until after the AppDomain spins up. The operator's monitoring will likely show "synthetic monitor failing" without any per-URL evidence.

That gap matters because it explains how a YSOD storm can persist undetected on a customer-facing endpoint while normal monitoring tells the operator only that "the service is down." If a similar pattern shows up on a second target, it becomes worth promoting to a numbered insight: *AppDomain-init YSOD storms are monitoring-invisible by construction; treat any 500 from a static path as a config-init failure until proven otherwise.*

Recording the candidate here so the codifier surface picks it up on the next observation.
