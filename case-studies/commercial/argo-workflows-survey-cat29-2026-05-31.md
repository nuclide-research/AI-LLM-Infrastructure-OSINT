---
type: case-study
category: 29
platform: Argo Workflows
survey_date: 2026-05-31
status: complete
findings: 0 unauth confirmed (3 CVAT retracted as non-reproducible FP)
verification_rung: inner-A / outer-2 (population fingerprinted + auth-classified by content discriminator; no request exercised against a live unauth instance because none found)
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

aimap v1.9.40 scanned all 119 IPs on ports 443, 2746, 80, 8080, 8443. Phase 1 (port discovery): 198 open ports. Phase 2 (fingerprinting): 3 apparent CVAT matches; **0 Argo Workflows** fingerprints fired.

The 0 Argo fingerprints is expected: the `ssl:` dork captures IP addresses behind Kubernetes ingress controllers, which route traffic by `Host:` header. Bare-IP probing hits the default backend or an IAP wall rather than the Argo service.

**CVAT matches — RETRACTED as non-reproducible false positive.** aimap's CVAT fingerprint requires `status_code:200 AND body_contains:"cvat"`. On re-verification, all three IPs (`136.110.132.36`, `34.111.151.62`, `34.149.216.212`) return `HTTP 302, "Invalid IAP credentials: empty token"` (36 bytes) at `/api/server/about` — a GCP IAP wall containing neither a 200 nor the string "cvat". A second aimap run on just these three IPs returned `services_found: 0`. The original 119-host scan caught a transient/nondeterministic IAP response (IAP intermittently returning a 200 under scan concurrency). nuclide.db entries #36121-36123 archived as FP. **No accessible CVAT confirmed in this corpus.** This is logged as a recurring-FP candidate for the aimap CVAT fingerprint: `body_contains:"cvat"` is a single-keyword match (Insight #6 class) that should be anchored to a CVAT-specific JSON field (e.g. `json_field:"version"` on the `/api/server/about` object).

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

**Results: 0/33 UNAUTH.** Every host classified by an actual content discriminator on `/api/v1/userinfo`, not by response size (Insight #16 — a 200 is identity, not auth state). The 33 probes cover 31 unique hostnames (5c10.org dev and the hotels-booking platform each map two IPs to one hostname).

Auth pattern breakdown (content-verified, `allow_redirects=False`):
- **GCP Identity-Aware Proxy (IAP):** 18 instances. Response: `HTTP 302` redirecting to the Google IAP challenge; body string `Invalid IAP credentials: empty token`. IAP enforced at the GCP load balancer; bare-IP access returns `404 backend NotFound` or `fault filter abort` (Envoy) — IAP is not bypassable via IP.
- **Azure AD:** 2 instances (lmsinfra.net production + acceptance). Response: `HTTP 302` to `login.microsoftonline.com`.
- **HTTP 401/403:** 9 instances. Auth-enforced; exact mechanism not further probed (native, OIDC, or ingress proxy). scalekit.dev additionally returned Argo's own `{"code":16,"message":"token not valid"}` gRPC-gateway body on a separate probe — confirmed Argo native auth.
- **HTTP 500 (Envoy fault filter):** 1 instance (ZeroTier).
- **HTTP 503 service unavailable:** 3 instances (service down at probe time — not a confirmed auth state; these are inconclusive, not "secure").

Honest caveat on the 3x 503: a service returning 503 was not auth-classified. They are counted as "not-unauth-confirmed," not as "auth-enforced." If all three were unauth-when-up, the worst-case ceiling for this corpus is 3/33 — still bounded, and none observed unauth.

**A 302 to an auth wall is an outer-1 / inner-A observation:** the host is fingerprinted as Argo (by cert CN) and observed to gate `/api/v1/userinfo`, but no request was exercised against an unauthenticated API. We did not attempt IAP bypass, credential replay, or the CVE-2026-28229 `Bearer nothing` probe against these live operator hosts — that would cross from enumeration into exploitation (restraint ethic).

**The other 86 IPs** (no cert-mapped Argo hostname) were probed directly on ports 2746 and 443: 0 unauth, 68 no-response (no service answering on those ports without the correct `Host` header), the rest various non-Argo responses. Corpus-wide: **0/119 unauth**, of which 33 were positively auth-classified by hostname and 86 were not reachable as Argo on bare IP. The meaningful denominator is the 33 cert-mapped hostnames; the 86 are "not confirmed reachable," not "confirmed secure."

---

## Key Finding: Population Gap

The `ssl:"Argo Workflows"` dork selects for **security-conscious operators** — those who have set up proper DNS and TLS certificates. This population uses GCP IAP, Azure AD, or Argo native auth.

The E.V.A Security November 2024 internet-wide scan found ~3,000 unauth instances via direct `/api/v1/userinfo` probing. That population runs **bare port 2746 with self-signed certs** — Shodan-dark and unreachable via this dork methodology. Our survey cannot falsify or confirm the E.V.A count.

**The unmeasured tier:** Operators who did NOT set up proper DNS/TLS are the unauth surface. Reaching them requires a masscan sweep on port 2746 across tier-2 cloud ranges (3.55M IPs), followed by direct userinfo probing. This is the correct methodology for the next survey iteration.

**What this survey does prove:** The "named subdomain" operator tier — companies that productionized their Argo deployment with real domain names — has adopted strong auth controls. IAP is the dominant pattern on GCP, consistent with Insight #40 (auth-on-default strengthens under disclosure pressure).

---

## Dark-Tier Follow-Up (Option A): the `port:2746` "no-data" hosts are not a probeable Argo population

The original case study proposed masscan as the way to reach the Shodan-dark bare-port tier. A cheaper path was tried first: harvest the 355 hosts Shodan already indexes under `port:2746` and probe them directly. The web UI capped at 200 results ("Result limit reached" at page 21 without query credits), yielding **193 unique IPs, 0 overlap with the ssl-dork set** — confirming a structurally distinct population.

**Result: 193/193 returned no application-layer response on `:2746`.** 0 Argo-confirmed, 0 unauth, 0 auth-enforced.

This was diagnosed, not assumed:
- The hosts complete the TCP SYN-ACK (SYN-scanners log "port open") but send a TCP RST the moment a client sends application bytes. `openssl s_client` gets `SSL_ERROR_SYSCALL` immediately after ClientHello; HTTP/1.1, HTTPS, and h2c-prior-knowledge all return HTTP 000.
- **Not a vantage artifact:** identical `SSL_ERROR_SYSCALL` from Mullvad US (Kansas City) and Sweden (Malmö) exits.
- **Not a sandbox egress block:** `portquiz.net:2746` returns HTTP 200 from the same environment, so non-standard-port egress works.

**The key correction this produces:** Shodan's "no data returned" on these 355 means Shodan *also* only captured a SYN-ACK and never pulled a banner — for exactly the reason our probe can't. This tier is connection-filtered (scrubbing middlebox / source-whitelist firewall / tarpit), heavy on Alibaba (8.x/47.x/120.x) and Tencent (43.x) ranges. **It is neither confirmed-Argo nor externally probeable**, so it is not the E.V.A ~3,000 unauth population. A SYN-scan masscan would only replicate the SYN-ACK-only result; reaching a real unauth population needs a full-handshake banner-grab (masscan `--banners` / zgrab2) and may still hit the RST wall from any single vantage. The E.V.A count came from hosts that answered E.V.A at the application layer — a set this methodology has not located.

**Censys cross-check: BLOCKED.** Censys web UI is behind a Cloudflare bot wall that the automated browser cannot pass; the local Censys CLI is installed but unauthenticated (no API ID/secret). Cross-check deferred pending Censys API creds or a manual run. Artifact: `dark-tier/darktier-finding.md`, `dark-tier/darktier-results.json`.

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

**CVAT — none. The 3 apparent CVAT matches were retracted as non-reproducible false positives** (see Fingerprinting). nuclide.db #36121-36123 archived. No accessible co-located service confirmed on the corpus.

---

## Toolchain Provenance

Tools are graded by what they actually produced: REAL (full data), DEGRADED (ran but missing inputs reduced output), NULL (ran, no usable data), BLOCKED (could not run).

```
JAXEN:         REAL     ssl:"Argo Workflows" → 119 IPs (manual Shodan web scrape, 20 pages)
aimap:         REAL     -list ips.txt -ports 443,2746,80,8080,8443 → 0 Argo (bare-IP hits ingress/IAP);
                        3 CVAT matches RETRACTED as non-reproducible FP (re-run: services_found:0)
aimap-profile: DEGRADED --target hostnames → WHOIS org/country only; sector/category NULL (no Shodan key)
VisorGraph:    REAL     -seeds-file ips.txt → 33 cert-mapped hostnames, 147 nodes, 65 edges. The load-bearing tool.
VisorBishop:   REAL     10 Argo hostnames → 0 findings (auth-walled corpus)
VisorSD:       BLOCKED  Shodan API key required — did not run
VisorGoose:    REAL     --no-shodan → 0 gov/edu nodes (correct: Argo is MLOps, not gov/edu)
menlohunt:     PARTIAL  ran on 136.110.x.x (10 IPs) only, not full corpus → ports 80/443, no escalation
nu-recon:      NULL     3 outlier IPs → returned simulated:true (no Shodan key) — no real data
VisorPlus:     REAL     assess 34.8.204.24 → GCP IAP confirmed
VisorLog:      REAL     4 findings added; 3 (#36121-23) later archived as FP, #36124 corrected
VisorScuba:    DEGRADED assessed 22,136 historical nodes (whole DB); survey's own 4 nodes scored 0/10
                        only because no unauth enrichment — aggregate score is not survey-specific
BARE:          REAL     6 findings → etcd chain 0.596 (exploits/multi/kubernetes_exec)
VisorCorpus:   N/A-RUN  built 137 adversarial prompts, but Argo Workflows is not an LLM target —
                        ran to keep the chain complete; output not meaningfully applicable here
VisorAgent:    N/A-RUN  run --corpus against the 137 prompts (controlled/ethical-stop); no LLM target in corpus
VisorRAG:      THIN     --target lmsinfra.net --max-steps 5 — agent loop ran, no new finding beyond auth-wall
VisorHollow:   [—]      Windows-only, not applicable
cortex:        THIN     analyze argo-auth-context.md → 0 violations (input lacked SKELETON/VIOLATIONS sections)
JS-bundle:     BLOCKED  IAP-walled — bundles inaccessible
Verification:  REAL     /api/v1/userinfo content-discriminator probe on 33 hostnames → 0/33 UNAUTH
                        + bare-IP bypass test on IAP hosts → 404/fault-filter (IAP not IP-bypassable)
```

The honest read: **four tools carried this survey** — JAXEN (harvest), VisorGraph (cert-pivot to real hostnames), the verification probe (auth classification), and BARE (chain mapping). aimap's value here was a *negative* (bare-IP fingerprinting correctly found no directly-exposed Argo) plus one retracted FP. The LLM-target tools (VisorCorpus, VisorAgent, VisorRAG, cortex) are not a natural fit for a non-LLM workflow engine and contributed nothing to the finding — they were run to keep the chain complete, and that is the honest label, not a pretense that they added signal.

---

## Honest Negative Space

- **Port 2746 is Shodan-dark.** Our dork cannot reach bare-server deployments — the unauth-dominant population. This is the single biggest gap: the survey measures the security-conscious tier and is blind to the tier the thesis predicts is unauth.
- **The E.V.A ~3,000 unauth count (Nov 2024) is neither confirmed nor falsified** by this survey; our methodology selects a structurally different (DNS-configured) population. Claiming this survey "tests Argo" would be a population-substitution error.
- **3x HTTP 503** hosts were not auth-classified — counted as inconclusive, not secure. Worst-case unauth ceiling for the corpus is 3/33.
- aimap-profile sector classification, nu-recon, and VisorSD were all degraded or blocked by the absent Shodan API key (Playwright-only Shodan posture this session).
- We did **not** fire the CVE-2026-28229 `Bearer nothing` probe, IAP-bypass attempts, or credential replay against live operator hosts — enumeration stopped at the auth wall (restraint ethic). Depth on those hosts is inner-A (cert-fingerprinted + auth-wall-observed), not inner-B.
- JS-bundle extraction blocked by IAP on every instance.

**Next required step:** masscan port 2746 across tier-2 cloud ranges → direct `/api/v1/userinfo` probe → population-level auth classification. That is the only path to an E.V.A-comparable measurement, and it is the correct Cat-29 follow-up.

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
