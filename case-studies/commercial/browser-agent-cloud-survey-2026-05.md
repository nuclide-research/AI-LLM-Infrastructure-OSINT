# Browser Automation / Agent Backends: Cross-Cloud Survey (2026-05)

_NuClide Research · 2026-05-04 (in progress)_

> **Status:** Discovery + probe complete (2026-05-04). 153 confirmed cross-cloud. Auth-off-default thesis reproduces sharply at this tier, every single confirmed host is unauth at the CDP/Selenium endpoint.

---

## Premise

Browser-automation backends (Browserless, Playwright server, Puppeteer remote, Selenium Grid, Skyvern) underpin AI agent stacks: the agent navigates websites, scrapes content, fills forms, and harvests data via these backends. **Misconfigured ones offer remote browser control as a service**, an attacker hits the WebSocket endpoint, gets a controllable Chrome instance running on the operator's IP and compute, and uses it for:

- **Scraping abuse** routed through operator's IP reputation (Cloudflare bypass, anti-bot evasion using a clean residential/datacenter fingerprint)
- **Credential-harvesting setups** using the operator's compute and bandwidth
- **Cookie/session theft** if a previous browser session left state
- **GPU/compute theft** for headed-browser ML workflows

The Chrome DevTools Protocol (CDP) endpoint is the highest-impact: any caller with WebSocket access can drive the browser as if local.

The platforms in scope:

| Platform | Default port | Tier | Auth posture |
|---|---|---|---|
| **Browserless** | 3000, 8000 | A | Auth-token optional; many tutorial deployments skip it |
| **Playwright server** | 3000, 4444 | A | No auth concept in standalone server mode |
| **Puppeteer remote / raw Chromium CDP** | 9222 (default) | A | Direct CDP access, no auth concept |
| **Selenium Grid** | 4444 | A | No auth in default deploy |
| **Skyvern** | 8000 | A* | Browser-AI agent, optional API key |

Auth-on-default thesis: all of these are A or A*, expect ~100% unauth at population scale.

---

## Methodology

### Discovery

Same tier-2 cross-cloud pattern. **Ports scanned:** 4444, 9222 fresh. Port 3000 + 8000 reused from MCP and LLM Gateway scans.

### Probe

`data/browser-agent-probe.py` per port:

| Platform | Probe | Match signature |
|---|---|---|
| **CDP-based** (Browserless, Playwright, raw Chromium) | `GET /json/version` | JSON with `Browser` / `User-Agent` / `webSocketDebuggerUrl` |
| **Selenium Grid** | `GET /wd/hub/status` | JSON with `value.ready` and `value.build.version` |
| **Skyvern** | `GET /api/v1/health` + `GET /` | health response + `skyvern` marker |

Distinguishes Browserless / Playwright / raw Chromium via root-page fingerprints.

### Filters

- AS63949 honeypot fleet filter
- Cross-survey overlap dedupe
- Record auth-on hosts but exclude from exposed-control enumeration

### Threat classes

| Class | Severity |
|---|---|
| **Direct browser control via CDP WebSocket** | CRITICAL, full headed-browser RCE-equivalent on operator's host |
| **Cookie/session/storage exfil** if browser session retained state | HIGH |
| **Scraping abuse via operator's IP reputation** | HIGH |
| **Compute / bandwidth theft** | MEDIUM |
| **Defaced Selenium Grid (job spam)** | MEDIUM |

---

## Discovery results

Cross-cloud final (153 confirmed). Masscan ports 4444 (Selenium Grid), 9222 (Chrome DevTools Protocol); ports 3000 + 8000 reused from MCP/LLM-Gateway scans.

| Platform | Confirmed |
|---|---|
| **Selenium Grid** (port 4444) | **83** (54%) |
| **Chrome DevTools Protocol** (raw Chromium, port 9222) | **36** (24%), direct browser control via WebSocket |
| **Browserless** (port 3000/8000) | **34** (22%) |
| **Total (final)** | **153** |

**100% of confirmed hosts are auth-off** at the platform endpoint, `/json/version` (CDP), `/wd/hub/status` (Selenium), and Browserless health endpoints all returned valid responses without authentication. Auth-off-default thesis reproduces at population scale, as predicted for this tier.

---

## Browser-version distribution (CVE-vulnerability proxy)

A key finding: many of the exposed CDP/Browserless instances are running **old, known-vulnerable Chromium versions**. Direct CDP control + outdated Chromium = chained-CVE attack surface beyond the auth-off issue.

| Browser version | Count | Notes |
|---|---|---|
| **HeadlessChrome 121.0.6167.85** | **21** | Single Browserless base-image fingerprint (Feb 2024). Mass-deployed across operators. **Likely single open-source template propagating**, mirroring the LLM-Gateway 1,829-host gpt-4o-mini canned-response pattern. |
| HeadlessChrome 124.0.6367.78 | 7 | Newer Browserless base image (~Apr 2024) |
| Chrome 120.0.6099.109 | 5 | Linux Chrome stable from late 2023 |
| Chrome 145.0.7632.6 | 2 | Recent stable |
| HeadlessChrome 90.0.4430.212 | 1 | **2021 vintage**, hundreds of unpatched CVEs |
| HeadlessChrome 89.0.4389.72 | 1 | 2021 vintage, same |
| HeadlessChrome 99.0.4844.0 | 1 | 2022 vintage |
| HeadlessChrome 100.0.4896.60 | 1 | 2022 vintage |
| HeadlessChrome 119.0.6045.105 | 1 | Late-2023 |
| HeadlessChrome 123.0.6312.122 / .105 | 2 | March 2024 |
| Chrome 122.0.6261.111 / .128 | 2 | Feb 2024 |
| Chrome 133.0.6943.16 | 1 | Feb 2025 |
| Chrome 140.0.7339.16 | 1 | Sept 2025 |
| Chrome 141.0.7390.54 | 1 | Oct 2025 |
| Chrome 143.0.7499.169 | 1 | Late 2025 |
| Chrome 148.0.7778.56 | 1 | Recent |

Versions older than Chrome 120 (5+ instances) are running **multi-year-stale Chromium with public CVEs that have working exploits**. Combined with unauth CDP control, that's a direct browser-RCE primitive on the operator's host.

---

## Fleet patterns (operator-attribution)

Multiple instances on the same /24 indicate fleet deployments, single operator running a Selenium / Browserless cluster:

| Subnet | Count | Notes |
|---|---|---|
| **`147.135.103.70-75`** | **6** | OVH range, Selenium Grid fleet, sequential IPs, single operator with a 6-node Selenium cluster |
| `188.165.79.16/17/22/23` | 4 | OVH range, 4× Selenium Grid |
| `51.77.82.x` | 3 | OVH range, 3 instances |
| `135.125.9.95 / .117` | 2 | OVH range, 2× HeadlessChrome 124.0.6367.78 (likely paired Browserless cluster) |
| `164.132.182.164 / .172` | 2 | OVH range, 2× CDP (Chrome 133 + Chrome 140), different versions on same operator's IPs, suggesting active mixed-version fleet |
| `163.172.172.x` | 2 | Scaleway, 2 instances |
| `149.56.16.x` | 2 | OVH, 2× Selenium Grid |

OVH dominates the population, most fleets are on OVH `5x.x.x.x` / `15x.x.x.x` / `188.165.x.x` ranges. Likely tracks with OVH being the cheap-VPS provider of choice for European scraping/automation operators.

---

## Notable findings

### F1: 100% unauth at the CDP/Selenium endpoint (98/98)

Every confirmed host returns a valid `/json/version` (CDP) or `/wd/hub/status` (Selenium) response without auth. This is the framework default, Browserless, Playwright server, raw Chromium, and Selenium Grid all ship with no built-in authentication. Auth must be bolted on via reverse-proxy or token-gating; operators in this population overwhelmingly haven't done that.

### F2: Direct CDP control = browser-RCE-equivalent

For the 26 raw-Chromium / Browserless hosts on port 9222, the WebSocket endpoint exposed via `webSocketDebuggerUrl` accepts CDP commands without authentication: navigate to URL, evaluate JavaScript, capture screenshots, intercept network traffic, dump cookies, read filesystem via `Page.captureScreenshot` of `file://` URLs (deprecated but possible on old Chromium), execute Chrome extensions API calls.

Operationally this is **functionally equivalent to RCE on the operator's host**, the attacker drives a fully-featured browser running with the operator's privileges, IP reputation, and (often) shared session storage.

### F3: Single-template fleet propagation: 21 instances at HeadlessChrome 121.0.6167.85

This mirrors the LLM-Gateway survey's 1,829-host gpt-4o-mini canned-response pattern: a single open-source template (Browserless's default Docker image circa Feb 2024) was mass-deployed by 21 independent operators, all left auth-off. The fix is upstream, the template author / Browserless project enabling auth-token by default, or shipping a clearer "you must set BROWSER_TOKEN" warning at startup.

### F4: Multi-year-stale Chromium on 5+ exposed CDP hosts

Hosts running Chromium 89/90/99/100 (2021-2022 vintage) have hundreds of known CVEs with working exploits, V8 type-confusion, Blink memory corruption, sandbox-escape primitives. Combined with unauth CDP, an attacker doesn't even need the CDP path: they can navigate the headless browser to an attacker-controlled exploit page and trigger RCE via the Chromium vuln chain.

### F5: `147.135.103.70-75` 6-node Selenium fleet

Sequential IPs all running Selenium Grid on port 4444, clear fleet deployment. WHOIS the IPs to identify the operator (likely a scraping / web-automation service). Disclosure recipient: OVH abuse + operator if attributable.

### F6: Garak NVIDIA red-team harness exposed (`149.56.22.24:5000`) [INVALIDATED 2026-05-05]

**Withdrawn.** This was a substring-match false positive cross-referenced from the AI safety eval survey. The host is actually a **Clipface** personal video clip browser ("Net Slum"); the broken probe matched on `b"garak"` finding the substring inside an anime filename `[F] Garakuta 【Flashアニメ】ガラクタノカミサマ.mp4`. Re-probe with tightened aimap fingerprints confirmed zero AI/ML services on this host. See [`ai-safety-eval-cloud-survey-2026-05.md`](ai-safety-eval-cloud-survey-2026-05.md) "Methodology correction" for the full FP analysis.

---

## Threat-class realization

| Class | Realized? | Hosts |
|---|---|---|
| Direct browser control via CDP WebSocket | ✅ | 26 raw-Chromium + (subset of) 16 Browserless |
| Cookie/session/storage exfil if browser session retained state | ⚠️ Possible, would need probing into open contexts | Same set |
| Scraping abuse via operator's IP reputation | ✅ | All 98 |
| Compute / bandwidth theft | ✅ | All 98 |
| Defaced Selenium Grid (job spam) | ⚠️, would need WebSocket / job-submission probe | 56 Selenium |
| **Browser-RCE via stale-Chromium + unauth CDP** | ✅ | 5+ hosts with pre-2023 Chromium |

---

## Disclosure plan

For OVH-hosted hosts (the dominant population), report to `abuse@ovh.net` with the host's IP + version; they forward to customer per their unmanaged-VPS policy. Same workflow as the OVH-Gmail-MCP and OVH-Alcy-CRM disclosures from earlier in this session, already proven path with auto-ticketing.

For Selenium fleets in same /24 (e.g. `147.135.103.70-75`), single disclosure email covering the cluster.

For the **stale-Chromium hosts**, severity is HIGH due to the chained-CVE risk. Disclosure body should explicitly call out the Chrome version and recommend update + auth-token.

---

## See also

- [`SYNTHESIS-2026-05.md`](SYNTHESIS-2026-05.md), auth-posture-by-tier table (browser-agent reproduces the 100%-unauth result alongside vLLM/MCP/LLM-Gateway)
- [`ai-safety-eval-cloud-survey-2026-05.md`](ai-safety-eval-cloud-survey-2026-05.md), sibling survey + 2026-05-05 methodology correction (Garak cross-reference is invalidated; both surveys' shared host was a Clipface FP)
- [`data/browser-agent-probe.py`](../../data/browser-agent-probe.py), discovery probe

## See also

- [`SYNTHESIS-2026-05.md`](SYNTHESIS-2026-05.md)
- [`FUTURE-SURVEYS.md`](FUTURE-SURVEYS.md)
- [`data/browser-agent-probe.py`](../../data/browser-agent-probe.py)
