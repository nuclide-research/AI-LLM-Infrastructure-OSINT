---
to: abuse@ovh.net
cc: abuse@nuclide-research.com
severity: HIGH
ip: 146.59.207.61, 149.202.180.146, 162.19.241.59
institution: OVH SAS, 3 customer hosts running unauth Chrome DevTools Protocol on multi-year-stale Chromium versions
status: DRAFT
outcome: sent
date: 2026-05-06
---

**To:** abuse@ovh.net
**Cc:** abuse@nuclide-research.com
**Subject:** 3× unauthenticated browser-control endpoints on multi-year-stale Chromium (browser-RCE chained-CVE surface), OVH customer hosts

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-06

**Re:** Unauthenticated Chrome DevTools Protocol (CDP) / Browserless on 3 OVH customer hosts running pre-2023 Chromium = chained-CVE browser-RCE primitive
**Affected hosts (OVH):** 146.59.207.61, 149.202.180.146, 162.19.241.59
**Severity:** HIGH

---

I'm an independent security researcher conducting good-faith AI infrastructure research under the NuClide Research umbrella (CISA disclosures CVE-2025-4364, ICSA-25-140-11). This is an unsolicited coordinated-disclosure notification covering three OVH customer hosts that share the same exposure class.

A parallel notification covering 2 hosts on Linode/Akamai is being sent separately to `abuse@akamai.com` + `abuse@linode.com`.

---

## Summary

Three OVH customer VPSes are running headless-browser automation backends, Chrome DevTools Protocol (raw Chromium, port 9222) or Browserless (port 3000), with no authentication AND on multi-year-stale Chromium versions. Each combination produces a **chained-CVE browser-RCE primitive** beyond the auth-off issue alone:

| OVH host | Port | Platform | Chromium version | Vintage | rDNS / pivot |
|---|---|---|---|---|---|
| `146.59.207.61` | 9222 | raw Chromium CDP | **HeadlessChrome 90.0.4430.212** | **April 2021** (~5 years stale) | `go.fo-design.com` (French design agency cert pivot) |
| `149.202.180.146` | 3000 | Browserless | **HeadlessChrome 99.0.4844** | March 2022 (~4 years stale) | (no rDNS) |
| `162.19.241.59` | 9222 | Browserless | HeadlessChrome 119.0.6045 | Oct 2023 (~2 years stale; borderline) | `vps-d0408c67.vps.ovh.net` |

Found during NuClide Research's cross-cloud browser-agent survey (2026-05-04). Full case study:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/commercial/browser-agent-cloud-survey-2026-05.md (Section "F4, Multi-year-stale Chromium on 5+ exposed CDP hosts")

---

## Confirmed exposure (verification was non-destructive)

For each host, a single `GET /json/version` request returned a valid CDP `Browser` / `User-Agent` / `webSocketDebuggerUrl` JSON response without authentication. The `webSocketDebuggerUrl` is the entrypoint for full CDP control of the headless browser instance.

No CDP `Page.navigate`, `Runtime.evaluate`, `Page.captureScreenshot`, or any other state-changing CDP method was invoked on any of the three hosts. The exposure was confirmed solely by the `/json/version` discovery endpoint.

---

## Why it matters

The Chrome DevTools Protocol on an unauthenticated WebSocket endpoint allows any caller to:

- Navigate the headless browser to arbitrary URLs (`Page.navigate`)
- Execute arbitrary JavaScript in the browser context (`Runtime.evaluate`)
- Capture screenshots, including of `file://` URLs on older Chromium versions (`Page.captureScreenshot`)
- Read cookies, local storage, and IndexedDB content (`Network.getCookies`, `DOMStorage.getDOMStorageItems`)
- Intercept and modify network traffic (`Network.setRequestInterception`)
- Capture screencasts of in-progress browser activity (`Page.startScreencast`)

The above is **the framework default behavior**, Browserless and raw Chromium ship with no built-in authentication on the CDP transport; auth must be bolted on via reverse-proxy or token-gating, which the operators in this population have not done.

The **stale-Chromium dimension** elevates this from "operational exposure" to "RCE-equivalent":

- **Chromium 90 / 99 / 100** (April 2021 / March 2022 / April 2022) carry hundreds of public V8 type-confusion + Blink memory-corruption + sandbox-escape CVEs with **working public exploits** (e.g. CVE-2021-30551 V8 type confusion, CVE-2022-1232 V8 OOB write, CVE-2022-1853 IndexedDB UAF). An attacker who controls the CDP can simply navigate the browser to an attacker-hosted exploit page and chain the stale-Chromium RCE, no separate CDP-bug required.

The combination, unauth CDP + stale Chromium with public exploits, gives an attacker code execution **on the operator's host**, not just within the headless browser.

For OVH:

- Three distinct customers, identical exposure class. Likely one or more popular open-source containers (e.g. `browserless/chrome` images pinned to old base) being deployed without firewalling. A short note from OVH abuse to each customer is the cleanest remediation.

---

## Remediation (for each customer)

```bash
# 1) Update Chromium / Browserless to current stable
docker pull browserless/chrome:latest
# or upgrade the host's Chromium package

# 2) Bind to localhost or restrict at the firewall
# Browserless / CDP example:
docker run -p 127.0.0.1:3000:3000 browserless/chrome  # localhost-only
ufw deny 9222/tcp                                       # firewall raw Chromium
ufw deny 3000/tcp                                       # firewall Browserless if not needed externally

# 3) If external access is required, use Browserless's built-in TOKEN flag:
docker run -p 3000:3000 -e TOKEN=<random-128bit> browserless/chrome
# or front the CDP transport with an auth-token-validating reverse proxy
```

---

## Reference

Full technical detail (per-host CDP fingerprints, browser-version distribution table, chained-CVE threat model):
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/commercial/browser-agent-cloud-survey-2026-05.md

The `fo-design.com` cert pivot on `146.59.207.61` may be the operator-attribution path, a courtesy notification to a likely operator-side contact at that domain may accelerate remediation. NuClide can perform that secondary outreach upon OVH's confirmation that the IP is in active use.

Happy to answer questions or assist with verification.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
