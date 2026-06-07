---
type: survey
title: Browser-automation backend tier cloud survey 2026-05-14
date: 2026-05-14
class: substrate
category: browser-automation
status: surveyed
methodology: 60-platform triage then per-platform read-only confirmation probe
---

# Browser-automation backend tier: cloud survey 2026-05-14

NuClide Research

## Summary

Population survey of the **browser-automation backend tier**, the second
leg of the 2026-05-14 browser-automation work (the first leg, raw Chrome
DevTools Protocol, is the
[CDP browser-control survey](cdp-browser-control-survey-2026-05-14.md)).

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7004, K7044, K7054, S7068, S7075, T5858, T5904
- **733 (AI Risk & Ethics Specialist):** K7051, T5868, T5893, T5904
- **overlap (Common AI KSATs (all 5 roles)):** K1158, K1159, K22, K6900, K6935, K7003, K942

<!-- ksat-tag:auto-generated:end -->

A 60-platform triage (see
[`shodan/queries/21-browser-agents.md`](../../shodan/queries/21-browser-agents.md))
reduced 60 named browser-automation / testing / scraping platforms to the
self-hostable, network-exposable subset. Six corpora were downloaded
(~4,900 Shodan candidates) and confirmed with per-platform read-only
probes. `/wd/hub/status`, `/status`, `/json/version`, `/sse`, Splash's
root + `/_debug`. No session creation, no job submission.

**Result: 2,689 confirmed instances, 100% unauthenticated**, collapsing
to roughly 940 distinct operator findings once two large monocultures are
attributed.

| Platform | Candidates | Confirmed | Real finding |
|---|--:|--:|---|
| Selenium Grid | 2,193 | 1,899 | 270 diverse + 1 mega-operator (1,629 grids) |
| Browserless | 697 | 518 | 518 real; 374 are one Docker-image monoculture |
| Splash | 913 | 139 | 139 — **97% also expose `/_debug`** |
| Selenoid | 212 | 132 | 132 — 1,823 advertised browser slots total |
| Playwright MCP | 775 | 1 | 1 live MCP SSE endpoint |
| Playwright server | 128 | 0 | 0 — not a deployed pattern |

Every confirmed host across every platform was unauthenticated. None of
these platforms ship authentication in their default deployment. The
auth-on-default thesis holds across the entire tier.

## Selenium Grid: 1,899 confirmed, but mostly one operator

`GET /wd/hub/status` returns `{"value":{"ready":true,"nodes":[...]}}` on
an open Grid. An open Grid hub means anyone can `POST` a new WebDriver
session and drive a real browser on the operator's host.

The raw count (1,899) is misleading. The port distribution exposed a
**single-operator mega-cluster**:

- **1,629** of the confirmed grids sit on ports `25001–25010`. A
  deliberate ten-port scheme
- those collapse to **208 unique IPs** in `104.255.171.0/24`, all
  **H4Y Technologies LLC**, each IP running ~7 Grid instances
- this is one industrial Selenium-Grid farm. A single operator finding,
  not 1,629

The genuinely diverse population is the **270 other confirmed Grids** on
normal ports (4444, 4445, 80, 5555…) scattered across unrelated ASNs.
Treating the H4Y cluster as 1,629 separate findings would inflate the
survey by 6×; it is one operator.

## Splash: small population, but a 97% secondary leak

Splash (the Scrapinghub render service) returned only 139 confirmed of
913 candidates. The `http.title:"Splash"` query carries collisions. But
the confirmed population has a striking secondary exposure: **135 of 139
(97%) also expose `/_debug`**, which dumps the render engine's internal
state. Active slots, queued requests, memory. Splash additionally
executes arbitrary Lua via `/execute` with a `lua_source` parameter.
That is SSRF and code-execution *by design*, not a misconfiguration. An
exposed Splash is a scriptable SSRF proxy on the operator's IP.

## Browserless: 518 real exposures, 374 a monoculture

All 518 confirmed Browserless instances are CDP-backed: `/json/version`
returns a live `webSocketDebuggerUrl`, so the impact is identical to the
[raw CDP survey](cdp-browser-control-survey-2026-05-14.md). Full
unauthenticated remote browser control.

Port counts on the confirmed hosts are low (2–11), so this is **not** a
honeypot fleet. But **374 of 518 run the byte-identical
`HeadlessChrome/121.0.6167.85`**, the Browserless v1 base-image
fingerprint already flagged in the 2026-05-09 browser-agent section. One
Docker image, mass-deployed; a single CVE affecting that image
propagates to all 374. Real exposures, but a monoculture, not 374
independent decisions.

## Selenoid: 132 confirmed, a large stealable compute farm

Aerokube Selenoid's `/status` endpoint is open by default and returns
`{total,used,queued,browsers}`. 132 confirmed instances **advertise a
combined 1,823 browser slots**, several hosts advertise 100–150-slot
capacity. An open Selenoid is free, attributable browser compute: an
attacker runs scraping / credential-stuffing / CAPTCHA-solving workloads
on the operator's hardware and IP reputation.

## Playwright MCP: the port-first method working correctly

The Playwright MCP candidate pool was built port-first: `port:8931`
returned 775 candidates because the identifying `playwright-mcp` string
lives on the `/sse` endpoint Shodan does not fetch. Probing `/sse` on all
775 confirmed **exactly 1** live MCP SSE endpoint (`172.104.41.106`,
serving `event: endpoint` with a session-scoped message path).

This is the port-first methodology working as designed: it told us the
candidate pool was almost entirely *not* Playwright MCP, rather than
producing 774 false positives. `:8931` is simply a common application
port; the one real instance is the finding, the 774 are noise correctly
identified as noise.

## Playwright server: not a deployed pattern

0 of 128 `http.title:"Playwright"` candidates served a standalone
Playwright server (`launchServer`) endpoint. This is a real negative
result: Playwright's server mode is ephemeral. Spun up per-test-run and
torn down, so it does not exist as a persistent exposed population the
way Selenium Grid or Browserless do. The 128 title matches are
documentation pages and test-report artifacts.

## Cross-platform pattern: two monocultures inflate raw counts

Two of the six platforms have a dominant single-template population: the
H4Y Selenium-Grid farm (1,629 grids, 1 operator) and the Browserless v1
image (374 hosts, 1 Docker image). This is the same class of finding as
the [n8n SPA-decoy pattern][n8n] and the [AWS Flowise honeypot
fleet][awsfleet]. A raw Shodan count is a *candidate pool shaped by a
few large deployers*, not a finding count. The survey discipline is to
attribute the monoculture and report the diverse population separately.

## Auth posture

100% unauthenticated across all 2,689 confirmed hosts. Selenium Grid,
Selenoid, Splash, Browserless, and Playwright MCP all ship without
authentication in their default deployment; the only boundary is
network-level (bind to localhost, firewall the port). The tier confirms
the auth-on-default thesis without exception.

## Cross-references

- [`cdp-browser-control-survey-2026-05-14.md`](cdp-browser-control-survey-2026-05-14.md): the raw CDP leg of this survey
- [`shodan/queries/21-browser-agents.md`](../../shodan/queries/21-browser-agents.md): the 60-platform triage and validated query set
- [`methodology/insight-21-port-first-discovery-for-low-footprint-platforms.md`](../../methodology/insight-21-port-first-discovery-for-low-footprint-platforms.md): port-first discovery, validated again here by Playwright MCP
- aimap v1.9.2. `Anti-detect CDP server` fingerprint added from the CDP leg
- VisorLog findings. Selenium Grid (H4Y operator + diverse), Splash, Selenoid, Browserless, Playwright MCP

[n8n]: n8n-cloud-survey-2026-05.md
[awsfleet]: flowise-cloud-survey-2026-05.md
