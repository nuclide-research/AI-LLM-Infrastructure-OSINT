---
title: Chrome DevTools Protocol, browser-automation backend cloud survey 2026-05-14
date: 2026-05-14
class: substrate
category: browser-automation
status: surveyed
methodology: port-first discovery (port:9222 JSON) then custom CDP /json confirmation probe
---

# Chrome DevTools Protocol: browser-automation backend cloud survey 2026-05-14

NuClide Research

## Summary

First population survey of the **browser-automation backend tier**, opened
by triaging 60 named browser-automation / testing / scraping platforms down
to the self-hostable, network-exposable subset (see
[`shodan/queries/21-browser-agents.md`](../../shodan/queries/21-browser-agents.md)).

The highest-impact target in that set is **raw Chrome DevTools Protocol
(CDP)** on port 9222. CDP is the wire protocol DevTools, Puppeteer,
Playwright and Selenium-with-Chrome speak to drive a browser. It has **no
authentication mechanism** — not "auth off by default" like MLflow or
Ollama, but *no auth concept in the protocol at all*. Its only intended
boundary is "bound to localhost." When an operator launches Chrome with
`--remote-debugging-port` and binds it to `0.0.0.0` (or publishes the
Docker port, or fronts it with a forwarder), the entire browser becomes
remotely controllable by anyone.

A port-first survey of **1,512 Shodan candidates** (`port:9222
"Content-Type: application/json"`) was confirmed with a custom read-only
CDP probe (`GET /json/version` + `GET /json`). Result: **6 confirmed,
real, unauthenticated CDP endpoints — 100% exposing browser-level
control** — plus a **26-host CDP honeypot fleet** identified and excluded.

| Severity | Count | Finding |
|---|--:|---|
| CRITICAL | 3 | CDP unauth + a live authenticated session open (account takeover) |
| HIGH | 2 | CDP unauth, anti-detect scraping farm, adjacent stack exposed |
| MEDIUM | 1 | CDP unauth, idle browser, browser-level ws still controllable |
| INFO | 1 | 26-host CDP honeypot fleet (threat-intel, not victim infra) |

## Method — the port-first funnel

```
1,512  Shodan candidates   port:9222 "Content-Type: application/json"
  │
  ├─ 1,155  http error      → NOT CDP. Host-header retry recovered 0/1155.
  │                           Other JSON service on :9222, no /json/version.
  ├─   272  net error       → firewalled / dead since Shodan's scan
  ├─    52  JSON, no CDP     → genuine collision (JSON svc, not a debugger)
  │
  └─    32  confirmed CDP /json/version
            ├─ 26  HONEYPOT FLEET  → excluded from victim corpus
            └─  6  REAL EXPOSED CDP ENDPOINTS
```

The 2.1% confirmation rate (32/1,512) is the methodology working as
designed: Shodan indexes `:9222/` but not `/json/version` where the
identifying `webSocketDebuggerUrl` lives, so the raw count is a *candidate
pool*, not a finding count. Confirmation requires a direct probe of the
sub-path Shodan does not fetch — the same port-first pattern as
[Methodology Insight #21](../../methodology/insight-21.md).

## The honeypot fleet (excluded)

26 of the 32 confirmed hosts were a coordinated **CDP honeypot fleet**:

- byte-identical `Chrome/120.0.6099.109` across 26 unrelated ASNs
  (Stark Industries, Beget, RackNerd, HostUS, HostPapa, IONOS, Oracle,
  Linode, MassiveGrid…)
- uniform 6 open targets, but **empty `target_types`** — the decoy fakes
  `/json/version` but not a real `/json` target list
- **220–340 open ports per host** — the respond-to-everything signature

Detection rule (consistent with the [AWS Flowise honeypot fleet][awsfleet]):
absurd port count + identical software fingerprint across unrelated ASNs +
malformed secondary endpoint. Cross-checked and dropped before analysis.

[awsfleet]: ../../surveys/flowise-cloud-survey-2026-05.md

## The 6 confirmed exposures

| Host | Org | Chrome | Driver | Live session |
|---|---|---|---|---|
| `24.199.71.227` | DigitalOcean US | 148 | port-forwarder | **OnlyFans `/my/settings`** |
| `64.23.176.77` | DigitalOcean US | 148 | port-forwarder | **OnlyFans `/my/settings`** |
| `116.203.42.109` | Hetzner DE | 108 (EOL) | raw Chrome | **Ticketmaster account** |
| `159.195.70.69` | DXC Technology DK | 146 | aiohttp anti-detect farm | FilmFans + Google Maps |
| `23.19.231.93` | LeaseWeb US | 146 | aiohttp anti-detect farm | Axialy (quant invest) |
| `143.110.166.3` | DigitalOcean GB | 144 | raw Chrome | idle (0 targets) |

Every host exposes a **browser-level `webSocketDebuggerUrl`** — full
remote headless-browser control, zero authentication.

### Three operator archetypes

The driver behind Chrome — not Chrome itself — is the operator
fingerprint. The WebSocket-path shape and HTTP `Server` header split the
six into three classes:

**1. Port-forwarder pair — `24.199.71.227`, `64.23.176.77`**
Both expose a ws URL with a `/port/35901/devtools/...` prefix: a
forwarding layer (Docker `socat`/`websockify` bridge or a port
multiplexer) rewriting CDP paths. *Same forwarder port (35901), same
Chrome 148, and an identical open-page GUID* (`96BB7FF88CAC...`) — this
is one operator running a duplicated deployment. Both have a live
authenticated OnlyFans session sitting on `/my/settings`.

**2. aiohttp anti-detect farm — `159.195.70.69`, `23.19.231.93`**
The HTTP server on `:9222` is not Chrome's — it is `Python/3.12
aiohttp/3.13.5`. The root path returns:
```json
{"status":"ok","active":1,"processes":{"__default__":{"pid":13,
 "port":5100,"seed":"71062","connections":2,"timezone":null,
 "locale":null,"proxy":null}}}
```
Per-process `seed`, `proxy`, `timezone`, `locale` are anti-fingerprinting
controls — each browser process gets a randomized fingerprint seed and
can be pinned to a proxy/timezone/locale. This is a commercial-grade
**anti-detect scraping farm**. Both hosts run the identical aiohttp +
Chrome 146 stack — same software, likely same operator or same
off-the-shelf product.

`159.195.70.69` exposes its **entire backend stack** on the same host:
`:80/443` Traefik (default cert — proxy deployed with no TLS config),
`:4000` app API, `:5432` PostgreSQL 9.6+, `:8083` web UI (unauth,
`/v1/models` 200), `:8084` API (401), `:9090` Prometheus (unauth),
`:9100` Node Exporter (unauth). The CDP exposure is one port of a fully
exposed scraping operation.

**3. Raw Chrome — `116.203.42.109`, `143.110.166.3`**
No wrapper. Chrome's own CDP HTTP server bound directly to
`0.0.0.0:9222` instead of loopback — the classic "ran Chrome in Docker,
bound to all interfaces to make it reachable, forgot it's public."
`116.203.42.109` runs **EOL Chrome 108** (multiple public RCE PoCs) and
has a live Ticketmaster "My Vikings Account" session plus
`ip.undetect.io` open — a ticket-scalping bot caught with its account
session exposed.

## What the exposure is, technically

An exposed CDP endpoint is **unauthenticated remote control of a browser
that is already logged into things**. Connecting to the
`webSocketDebuggerUrl` and speaking CDP gives an attacker:

| CDP command | Capability |
|---|---|
| `Network.getAllCookies` | Every cookie incl. HttpOnly session tokens — DevTools sees through HttpOnly |
| `Runtime.evaluate` | Arbitrary JavaScript in any page's origin context |
| `Page.navigate` | Drive the browser anywhere — attacker infra, internal services, `169.254.169.254` cloud metadata |
| `Target.createTarget` | Open new tabs even when none exist (why an idle host is still a finding) |
| `Input.dispatchKeyEvent` | Synthesize input — operate the live session as the user |
| `Page.captureScreenshot` / `printToPDF` | Visual exfil |
| `Fetch` / `Network.enable` | Intercept and rewrite all browser traffic |

The impact is not theoretical: three of six hosts have a live
authenticated session open *right now*. `Network.getCookies` on
`24.199.71.227` or `64.23.176.77` returns an OnlyFans session token —
account takeover with no password and no MFA prompt, because the session
is already past MFA. `116.203.42.109` is the same for a Ticketmaster
account. It also chains: `Page.navigate` to a Chrome-memory-CVE exploit
page on the EOL Chrome 108 host escalates to code execution on the VPS
itself.

## Auth posture

CDP is the purest case of the auth-on-default thesis — it is
**auth-never**. There is no credential to enable, no config flag to
harden. The only mitigations are network-level: bind to `127.0.0.1`
(the default that operators override), or firewall `:9222`. The 100%
unauth rate is therefore not a finding *about* the platform — it is the
platform.

## New aimap fingerprint

The **`aiohttp` anti-detect CDP server** is a discoverable pattern worth
adding to aimap: `Server: Python/3.12 aiohttp` on `:9222` + a valid CDP
`/json/version` + a root path returning `{"status","active",
"processes":{...,"seed","proxy"}}`. It points to a specific class of
commercial anti-detect browser-automation tooling, distinct from raw
Chrome and from port-forwarder deployments.

## Cross-references

- [`shodan/queries/21-browser-agents.md`](../../shodan/queries/21-browser-agents.md) — the 60-platform triage and validated query set
- [`methodology/insight-21.md`](../../methodology/insight-21.md) — port-first discovery
- [`surveys/flowise-cloud-survey-2026-05.md`](../../surveys/flowise-cloud-survey-2026-05.md) — honeypot-fleet detection rule
- VisorLog findings #883–889
