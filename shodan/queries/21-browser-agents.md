# 21. Browser Automation / Agent Backends

_Section created: 2026-05-09_

Browser-automation backends (Browserless, Playwright server, Puppeteer/raw CDP, Selenium Grid, Skyvern) underpin AI agent stacks. Misconfigured ones offer **remote browser control as a service** — the CDP WebSocket endpoint is equivalent to full headless-browser RCE on the operator's host and IP reputation. Attackers use exposed instances for scraping abuse (Cloudflare bypass via clean datacenter IP), credential harvesting, and GPU/compute theft for headed-browser ML workflows.

**Survey result (2026-05-04):** 153 confirmed cross-cloud (Scaleway + OVH + Linode, 3.55M IPs). **100% unauthenticated**. Distribution: Selenium Grid 83 (54%), raw CDP/Chromium 36 (24%), Browserless 34 (22%). Browser versions ranged from Chrome 89 (2021, hundreds of unpatched CVEs) to Chrome 148 (2025). Six-node sequential-IP Selenium fleet on OVH `147.135.103.70-75` flagged as single-operator deployment.

**Auth posture:**
- **CDP** (Browserless, Playwright server, raw Chromium): T1 — no auth concept. `/json/version` responds to anyone.
- **Selenium Grid**: T1 — no auth in default deploy. `/wd/hub/status` open.
- **Skyvern**: T2 — optional API key; many deployments skip it.

**CVE watch:**
- Chrome/Chromium ≤ 120: multiple memory corruption CVEs with public PoC (e.g., CVE-2024-0519). Combined with unauth CDP = arbitrary code execution on the operator's host via malicious page navigation.
- Browserless v1 deployments (HeadlessChrome 121.0.6167.85 base image, Feb 2024): mass-deployed from a single open-source template; single CVE affecting that image propagates to all 21 identified instances sharing that fingerprint.

---

**Shodan indexing note:** Port-constrained bare strings (`"webSocketDebuggerUrl" port:9222`, `port:9222 "HeadlessChrome"`) return 0. Shodan does not index CDP JSON response bodies via bare-string search on port constraints. Use `http.html:` prefix — Shodan treats the CDP JSON response as an HTML body for HTTP services. `port:9222 http.status:200` returns 6,478 (too noisy; catches all port-9222 services).

## Chrome DevTools Protocol (CDP) — Browserless / Playwright / raw Chromium

| Shodan Query | Verified hits | Notes |
|---|---|---|
| `http.html:"HeadlessChrome"` | **570** | Best HeadlessChrome signal; any port |
| `http.html:"devtools/browser"` | **28** | CDP browser DevTools path in HTML body |
| `http.html:"webSocketDebuggerUrl"` | **19** | CDP WebSocket URL in indexed response |
| `http.html:"json/version" port:9222` | **20** | CDP version endpoint on default port |
| `port:9222 http.status:200` | 6,478 | Broadest; all port-9222 HTTP-200 services (noisy) |
| `port:9222` | — | Raw CDP default port |
| `port:9222 -port:443` | — | Non-HTTPS direct exposure |

---

## Browserless

| Shodan Query | Verified hits | Notes |
|---|---|---|
| `http.html:"browserless"` | **697** | Best signal; HTML-scoped any port |
| `http.title:"browserless"` | **674** | Title-based; slightly tighter |
| `"browserless"` | 110 | Bare-string any field |
| `http.html:"browserless" port:3000` | — | HTML-scoped on port 3000 |
| `http.html:"browserless" port:8000` | — | HTML-scoped on port 8000 |
| `http.html:"/chromium" port:3000` | — | Chromium endpoint path |
| `"browserless/chrome"` | — | Browserless Chrome image identifier |
| `http.html:"puppeteer" port:3000` | — | Puppeteer integration path in Browserless source |
| `http.html:"playwright" port:3000` | — | Playwright integration path |
| `hostname:"browserless"` | — | rDNS pattern |
| `ssl.cert.subject.cn:"browserless"` | — | TLS cert CN |
| `port:3000 "browserless"` | 0 | Port-constrained bare string; does not work — use http.html: |
| `"HeadlessChrome 121.0.6167.85"` | 0 | Exact version string not indexed; use `http.html:"HeadlessChrome"` (570) |

---

## Selenium Grid

| Shodan Query | Notes |
|---|---|
| `port:4444` | Selenium Grid default port; near-unique signal |
| `port:4444 "selenium"` | Selenium identifier on default port |
| `port:4444 http.html:"selenium"` | HTML-scoped |
| `port:4444 http.html:"webdriver"` | WebDriver references in Grid UI |
| `port:4444 http.html:"grid"` | Grid UI identifier |
| `port:4444 http.html:"wd/hub/status"` | Selenium hub status endpoint path |
| `port:4444 http.status:200` | Live Grid (Grid root returns 200 with status page) |
| `"selenium" port:4444` | Bare-string on default port |
| `"Selenium Grid"` | Full product name in any indexed field |
| `"Selenium Grid" port:4444` | Full name on default port |
| `http.html:"Grid Console" port:4444` | Selenium 3.x Grid console UI |
| `http.html:"selenium-server"` | Selenium server JAR identifier |
| `port:4444 org:"ovh"` | OVH (6-node fleet found on `147.135.103.70-75` in survey) |
| `port:4444 org:"digitalocean"` | DigitalOcean |
| `port:4444 org:"hetzner"` | Hetzner |
| `port:4444 country:US` | US-scoped |
| `port:4444 country:DE` | Germany |
| `port:4444 -port:443` | Non-HTTPS direct exposure |
| `hostname:"selenium"` | rDNS pattern |

---

## Playwright Server (standalone)

| Shodan Query | Notes |
|---|---|
| `port:3000 "playwright"` | Playwright server on default port |
| `port:4444 "playwright"` | Playwright on Selenium-compat port |
| `http.html:"playwright" port:3000` | HTML-scoped on port 3000 |
| `http.html:"/json/protocol" port:3000` | CDP protocol endpoint; Playwright exposes this |
| `"playwright-server"` | Process/image identifier |

---

## Skyvern

| Shodan Query | Notes |
|---|---|
| `port:8000 "skyvern"` | Skyvern on default port |
| `http.html:"skyvern" port:8000` | HTML-scoped |
| `http.html:"/api/v1/health" port:8000` | Skyvern health endpoint |
| `"skyvern"` | Any indexed field |
| `hostname:"skyvern"` | rDNS pattern |
| `ssl.cert.subject.cn:"skyvern"` | TLS cert CN |

---

## Version-specific / CVE targeting

| Shodan Query | Notes |
|---|---|
| `"HeadlessChrome/8"` | Chrome 80-89 vintage (2020-2021); hundreds of unpatched CVEs |
| `"HeadlessChrome/9"` | Chrome 90-99 vintage |
| `"HeadlessChrome/100"` | Chrome 100-109 vintage |
| `"HeadlessChrome/11"` | Chrome 110-119 vintage |
| `"HeadlessChrome/120"` | Chrome 120; last version before several memory CVEs patched |
| `port:9222 "HeadlessChrome/8"` | Old Chrome on CDP port; chained RCE surface |
| `port:9222 "HeadlessChrome/9"` | Same, Chrome 90-99 |

---

## Combined

| Shodan Query | Notes |
|---|---|
| `(port:4444 OR port:9222) ("selenium" OR "webSocketDebuggerUrl" OR "HeadlessChrome")` | Full browser-agent sweep |
| `("webSocketDebuggerUrl" OR "HeadlessChrome") -port:443` | CDP endpoints, non-HTTPS |
| `(port:4444 "selenium") OR (port:9222 "HeadlessChrome") OR (port:3000 "browserless")` | All three platform types |
| `port:4444 org:"ovh"` | OVH Selenium sweep (6-node fleet found here) |
| `(port:9222 OR port:4444 OR port:3000) country:US -port:443` | US non-HTTPS browser-agent sweep |

---

# 2026-05-14 Update — 60-Platform Triage & Re-Validation

_Section appended: 2026-05-14. Freelancer-tier Shodan API count sweep across 60 named browser-automation / testing / scraping platforms. Goal: separate self-hosted exposable services from client libraries and pure-SaaS noise, and re-validate the 2026-05-09 fingerprints._

## What does NOT survey (no exposable network surface)

Excluded from the survey set — these are **client libraries / CLI tools** (run in CI, no listening service) or **pure SaaS** (vendor cloud, not operator infrastructure):

- **Client libs / CLI:** WebdriverIO, Nightwatch.js, TestCafe, Cypress, Mechanize, Watir, Capybara, Ferrum, Zombie.js, JSDOM, undetected-chromedriver, playwright-extra / puppeteer-extra, patchright, camoufox, Playwright Test, Scrapy
- **Deprecated, no server mode:** PhantomJS, CasperJS
- **Pure SaaS:** BrowserStack, Sauce Labs, LambdaTest, CrossBrowserTesting / SmartBear, Apify, Bright Data, Oxylabs, Browserbase, Steel, Hyperbrowser, AgentQL, Ghost Inspector, Testim, Mabl, Percy, Endtest, Functionize, Rainforest QA, Reflect, Applitools, Screener, Checkly, Datadog / New Relic / Pingdom / Dynatrace Synthetics, TestComplete, Katalon, Ranorex

**Term-collision warning:** several SaaS names return large counts that are *not* exposed infrastructure — they are the vendor's JS beacon snippet embedded in customers' page HTML (`http.html:"dynatrace"` 2,649, `http.html:"pingdom"` 505, `http.html:"browserstack"` 1,443). `http.html:"splash"` returns **403,968** — pure English-word collision ("splash screen / splash page"). Do not treat these as findings.

## Validated download set — real, surveyable populations

| Platform | Best query | Verified count (2026-05-14) | Risk |
|---|---|---|---|
| **Selenium Grid** | `http.title:"Selenium Grid"` | **2,216** | Hub control + `/wd/hub` session hijack |
| **Raw CDP** | `port:9222 "Content-Type: application/json"` | **1,535** | Full remote headless-browser control |
| **Splash** | `http.title:"Splash"` | **928** | Scrapinghub render service `:8050` (collision killed: 403,968 → 928) |
| **Browserless** | `http.html:"browserless"` | **708** | Self-hosted, `:3000` |
| **Playwright MCP** | `port:8931` | **783** | New agent-control surface — candidate pool, see note |
| **Selenoid** | `http.title:"Selenoid"` | **212** | Aerokube self-hosted Selenium |
| **Playwright server** | `http.title:"Playwright"` | **130** | Remote Playwright endpoint |

## New platforms vs. 2026-05-09 section

- **Selenoid** (Aerokube) — `http.title:"Selenoid"` = 212. Self-hosted Selenium alternative with a distinct UI; not covered in the original section. T1 — no auth in default deploy.
- **Splash** (Scrapinghub) — `http.title:"Splash"` = 928. Render-as-a-service on `:8050`. T1. The `http.html:"splash"` form is unusable (403k word-collision); the title form is clean.
- **Playwright MCP** — `port:8931` = 783. The MCP server for Playwright. Like raw CDP, the identifying `playwright-mcp` string lives on the `/sse` endpoint Shodan does not fetch — `"playwright-mcp"` bare-string returns only 7. **The 783 is a port-first candidate pool; confirm with a direct `/sse` probe.** Highest-impact category (agent browser control). Cross-ref MCP methodology: [`10-mcp-servers.md`](10-mcp-servers.md).

## Re-validated fingerprints (counts shifted since 2026-05-09)

| Query | 2026-05-09 | 2026-05-14 | Note |
|---|---|---|---|
| `http.html:"browserless"` | 697 | 708 | Stable |
| `http.title:"Selenium Grid"` | — | 2,216 | New: title form far broader than `"Selenium Grid"` bare-string (118) |
| `port:9222 "Content-Type: application/json"` | — | 1,535 | New: best raw-CDP discriminator; `port:9222` alone = 115,567 (mostly non-CDP) |

## Dropped after triage

- **Puppeteer** — `http.html:"puppeteer"` (948) is dominated by documentation / blog pages; `"puppeteer" "browserWSEndpoint"` = 0. No clean server-side fingerprint distinct from Browserless/CDP. Survey raw CDP instead.
- **Browser-Use** — `http.html:"browser-use"` (390) collapses to 3 real exposed UIs (`http.title:"Browser Use"` = 3). Too thin for a population survey; revisit as case-study material if a notable instance appears.
- **Zalenium / Moon** — ~0–6 hits; effectively dead deployments.

## Indexing note (extends the 2026-05-09 note)

The port-first pattern (Methodology Insight #21) applies to **both raw CDP and Playwright MCP**: Shodan crawls `:9222/` and `:8931/` but does not fetch the JSON/SSE sub-paths (`/json/version`, `/sse`) where the identifying strings live. Discovery is port + generic discriminator; confirmation is a direct NuClide probe of the sub-path.
