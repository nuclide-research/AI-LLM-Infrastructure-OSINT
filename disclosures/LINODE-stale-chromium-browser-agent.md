---
to: abuse@akamai.com
cc: abuse@linode.com, abuse@nuclide-research.com
severity: HIGH
ip: 139.162.36.70, 172.104.24.241
institution: Akamai Technologies / Linode — 2 customer hosts running unauth Chrome DevTools Protocol on pre-2023 Chromium
status: DRAFT
date: 2026-05-06
---

**To:** abuse@akamai.com
**Cc:** abuse@linode.com, abuse@nuclide-research.com
**Subject:** 2× unauthenticated browser-control endpoints on pre-2023 Chromium (browser-RCE chained-CVE surface) — Linode customer hosts

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-06

**Re:** Unauthenticated Chrome DevTools Protocol (CDP) on 2 Linode customer hosts running pre-2023 Chromium = chained-CVE browser-RCE primitive
**Affected hosts (Linode):** 139.162.36.70, 172.104.24.241
**Severity:** HIGH

---

I'm an independent security researcher conducting good-faith AI infrastructure research under the NuClide Research umbrella (CISA disclosures CVE-2025-4364, ICSA-25-140-11). This is an unsolicited coordinated-disclosure notification covering two Linode customer hosts that share the same exposure class.

A parallel notification covering 3 hosts on OVH is being sent separately to `abuse@ovh.net`.

---

## Summary

Two Linode customer VPSes are running raw Chromium with the Chrome DevTools Protocol (port 9222) exposed unauthenticated AND on pre-2023 Chromium versions. The combination produces a **chained-CVE browser-RCE primitive** beyond the auth-off issue alone.

| Linode host | Port | Platform | Chromium version | Vintage | rDNS |
|---|---|---|---|---|---|
| `139.162.36.70` | 9222 | raw Chromium CDP | **HeadlessChrome 100.0.4896.60** | **April 2022** (~4 years stale) | `139-162-36-70.ip.linodeusercontent.com` |
| `172.104.24.241` | 9222 | raw Chromium CDP | **HeadlessChrome 89.0.4389.72** | **March 2021** (~5 years stale) | `172-104-24-241.ip.linodeusercontent.com` |

Found during NuClide Research's cross-cloud browser-agent survey (2026-05-04). Full case study:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/commercial/browser-agent-cloud-survey-2026-05.md (Section "F4 — Multi-year-stale Chromium on 5+ exposed CDP hosts")

---

## Confirmed exposure (verification was non-destructive)

For each host, a single `GET /json/version` request returned a valid CDP `Browser` / `User-Agent` / `webSocketDebuggerUrl` JSON response without authentication. The `webSocketDebuggerUrl` is the entrypoint for full CDP control of the headless browser instance.

No CDP `Page.navigate`, `Runtime.evaluate`, `Page.captureScreenshot`, or any other state-changing CDP method was invoked on either host. The exposure was confirmed solely by the `/json/version` discovery endpoint.

---

## Why it matters

The Chrome DevTools Protocol on an unauthenticated WebSocket endpoint gives any caller full programmatic control of the browser — navigate to arbitrary URLs, execute JavaScript in the browser context, read cookies/localStorage/IndexedDB, intercept network traffic, capture screenshots and screencasts.

This is the **framework default behavior** — raw Chromium with `--remote-debugging-port=9222` ships with no authentication on the CDP transport; auth must be bolted on via reverse-proxy or token-gating, which the operators in this population have not done.

The **stale-Chromium dimension** elevates this from "operational exposure" to "RCE-equivalent":

- **Chromium 89 (March 2021)** and **Chromium 100 (April 2022)** carry hundreds of public V8 type-confusion + Blink memory-corruption + sandbox-escape CVEs with **working public exploits** (e.g. CVE-2021-21148 V8 heap buffer overflow ITW, CVE-2021-30551 V8 type confusion, CVE-2022-1232 V8 OOB write, CVE-2022-1853 IndexedDB UAF). An attacker who controls the CDP can simply `Page.navigate` the browser to an attacker-hosted exploit page and chain the stale-Chromium RCE — no separate CDP-bug required.

The combination — unauth CDP + stale Chromium with public exploits — gives an attacker code execution **on the operator's host**, not just within the headless browser.

For Akamai/Linode:

- Two customers, identical exposure class. The `linodeusercontent.com` rDNS prefix is Linode's default (no operator branding visible). A short note from Linode abuse to each customer is the cleanest remediation.

---

## Remediation (for each customer)

```bash
# 1) Update Chromium to current stable
sudo apt update && sudo apt upgrade -y chromium-browser
# Or rebuild the container with a current Chromium base

# 2) Bind to localhost or restrict at the firewall
# If launching Chromium directly:
chromium --remote-debugging-address=127.0.0.1 --remote-debugging-port=9222 ...
# Or firewall:
ufw deny 9222/tcp
ufw allow from <admin-IP> to any port 9222

# 3) If external CDP access is required, front it with an auth-token-validating
# reverse proxy — the CDP protocol itself has no native auth.
```

---

## Reference

Full technical detail (per-host CDP fingerprints, browser-version distribution table, chained-CVE threat model):
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/commercial/browser-agent-cloud-survey-2026-05.md

Happy to answer questions or assist with verification.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
