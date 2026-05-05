# Browser Automation / Agent Backends — Cross-Cloud Survey (2026-05)

_NuClide Research · 2026-05-04 (in progress)_

> **Status:** Methodology + scaffolding complete. Discovery scan queued. Synthesis fills as data lands.

---

## Premise

Browser-automation backends (Browserless, Playwright server, Puppeteer remote, Selenium Grid, Skyvern) underpin AI agent stacks: the agent navigates websites, scrapes content, fills forms, and harvests data via these backends. **Misconfigured ones offer remote browser control as a service** — an attacker hits the WebSocket endpoint, gets a controllable Chrome instance running on the operator's IP and compute, and uses it for:

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

Auth-on-default thesis: all of these are A or A* — expect ~100% unauth at population scale.

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
| **Direct browser control via CDP WebSocket** | CRITICAL — full headed-browser RCE-equivalent on operator's host |
| **Cookie/session/storage exfil** if browser session retained state | HIGH |
| **Scraping abuse via operator's IP reputation** | HIGH |
| **Compute / bandwidth theft** | MEDIUM |
| **Defaced Selenium Grid (job spam)** | MEDIUM |

---

## Discovery results

_(populated)_

| Source | Hits | Confirmed | Auth-on | Auth-off |
|---|---|---|---|---|
| Combined tier-2 (3 providers) | TBD | TBD | TBD | TBD |

---

## Notable findings

_(populated)_

---

## See also

- [`SYNTHESIS-2026-05.md`](SYNTHESIS-2026-05.md)
- [`FUTURE-SURVEYS.md`](FUTURE-SURVEYS.md)
- [`data/browser-agent-probe.py`](../../data/browser-agent-probe.py)
