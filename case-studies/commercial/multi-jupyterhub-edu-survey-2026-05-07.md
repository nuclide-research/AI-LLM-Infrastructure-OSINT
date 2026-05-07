---
title: "JupyterHub on .edu networks, Shodan-driven exposure survey with full chain triage (2026-05-07)"
date: 2026-05-07
class: institutional-deployment
category: transport-security + version-currency + adjacent-finding
status: triage-complete
methodology: Shodan dorking + visor-chain-runner (jaxen + visorplus + aimap + visorgraph + aimap-profile + nuclide-contact) + auth-state probe
---

# JupyterHub on .edu networks, Shodan-driven exposure survey

NuClide Research, 2026-05-07

## TL;DR

Shodan dork `hostname:*.edu JupyterHub` returned **252 publicly-discoverable JupyterHub instances** worldwide. A 13-host seed sample (drawn from the lowercase `jupyter` variant + 2 specifically-named JupyterHubs from manual recon) was run through the full canonical chain (`jaxen import → visorplus assess → aimap → visorgraph → aimap-profile → nuclide-contact`) and triaged via auth-state probe.

**6 actionable findings:**

| Severity | Host | Finding |
|---|---|---|
| **HIGH** | Virginia Tech `waingram418808.lib.vt.edu` | JupyterHub 4.0.2 served over **HTTP only** (no HTTPS). Login form transmits credentials in plaintext; campus-WiFi MITM is a realistic threat. |
| **HIGH** | Hampton University `jupyter.cas.hamptonu.edu` | JupyterHub **2.0.0** (released early 2022, multi-year-old). Many JupyterHub CVEs apply to this version. |
| **HIGH** (adjacent class) | UW Atmospheric Sciences `orca.atmos.washington.edu` | Not JupyterHub but found in the sweep. Exposes **rexec/rlogin/rsh on tcp/512-514** (1980s-era plaintext-auth services) + **NFS on tcp/2049**. Per-host fleet (3 Tornados on 8081/8082/8084 are also present). |
| **MED-HI** | UMD `carrot.umd.edu` | JupyterHub 4.0.2 over HTTPS. 3 unpatched CVEs apply (CVE-2024-28233 XSS, CVE-2024-41942 priv-esc, CVE-2026-33709 redirect). |
| **MEDIUM** | NC State `jupyter.csc.ncsu.edu` | JupyterHub 5.3.0, HTTPS-enforced, strong CSP (`frame-ancestors 'none'`). CVE-2026-33709 open-redirect applies; upgrade to 5.4.4. |
| **MEDIUM** | UIC `compaasgold06.evl.uic.edu` | JupyterHub 5.3.0 behind nginx 1.24.0 reverse-proxy. Same CVE-2026-33709 as NCSU. |

**7 non-findings:** SUNY Stony Brook (custom Tornado app on :8888, not Jupyter), Berkeley LiteLLM (master_key set, 401 on /v1/models), UPenn Wharton (SNI-locked, can't probe externally), MIT 6004hub / submit06 / rosettai (filtered to research network), IIT (multi-tenant Apache library digital-collections, not Jupyter).

The 252-instance population is dominated by properly-auth'd JupyterHub deployments. The high-value subset is the slice that combines (a) public exposure with (b) operator-side missteps — old version, transport-layer downgrade, version-currency lapses. This is a different threat class than the Cortical Labs CL1 vendor-template story (Methodology Insight #10): these are operator-configuration choices, not vendor defaults.

## Chain output (per-host)

The full canonical chain ran on all 13 hosts. Per-host artifacts are in `~/recon/jupyterhub-edu-2026-05-06/`. Aimap had to be killed mid-batch (network timeout on IIT 80) and re-run per-host with parallelized 3s/10s timeouts.

### Step 1a: visorplus assess (passive recon)

WHOIS-derived organization + abuse contact per host (Methodology Insight #4):

| Host | Org | Authoritative abuse contact |
|---|---|---|
| 128.173.51.43 | Virginia Polytechnic Institute | `abuse@vt.edu` |
| 128.30.44.81 / 128.30.92.148 / 18.4.134.206 | MIT | `arin-mit-security@mit.edu` |
| 128.8.235.64 | University of Maryland | `abuse@umd.edu` |
| 129.49.105.243 | SUNY Stony Brook | `abuse@stonybrook.edu` |
| 131.193.78.37 | University of Illinois Chicago | `esteban@uic.edu` |
| 137.198.56.13 | Hampton University | `barbara.tibbs@hamptonu.edu` |
| 140.142.30.87 | University of Washington | `abuse@uw.edu` |
| 152.14.199.179 | **MCNC** (regional research network for NC) | `abuse@mcnc.org` (network owner); operator at NCSU `security@ncsu.edu` |
| 165.123.61.253 | University of Pennsylvania | `security@upenn.edu` |
| 216.47.157.220 | Illinois Institute of Technology | `oyewole@iit.edu` |
| 35.212.232.117 | **Google LLC** (GCP-hosted UC Berkeley app) | `google-cloud-compliance@google.com` + Berkeley security |

The MCNC and Google LLC findings illustrate Methodology Insight #4 in practice: **WHOIS-derived contact is authoritative even when the rDNS suggests a different operator**. The UC Berkeley LiteLLM is on Google Cloud (`bearborg.berkeley.edu` is a CNAME pointing at a GCP IP); the abuse contact is Google, parallel to Berkeley's own security office. NCSU's `jupyter.csc.ncsu.edu` IP is registered to MCNC, the regional NREN.

Notable port surface beyond the JupyterHub finding (visorplus nmap top-1000):

- **UW orca.atmos.washington.edu**: 22, 80, 443, **512, 513, 514** (rexec/rlogin/rsh), **2049** (NFS), 8081/8082/8084 (3x Tornado), 9102 (jetdirect-class). 11 ports total. The r-services and NFS exposure is a separate finding from the JupyterHub-class survey, but it surfaced through the same dork because Tornado was classified as "jupyter-shaped" by Shodan.
- **SUNY Stony Brook biology**: 22 (OpenSSH 9.6 modern), 3390 (RDP-alt), 8888 (Tornado 6.4.2). Tornado on classic-Notebook port turned out NOT to be Jupyter (404 on /tree, /lab, /).
- **Berkeley LiteLLM**: 22, 80, 443, **4000 (LiteLLM/Uvicorn)**. LiteLLM auth is intact (401 on /v1/models requires Bearer key).

### Step 1b: aimap (conjunctive matcher)

Aimap classified 5 hosts as `Jupyter Notebook` (severity=high). Auth-state was `unknown` across all — aimap's matchers identify the platform but don't try to bypass auth.

### Step 2: visorgraph (cert + http_status pivot)

Visorgraph captured the HTTP-status + Server-header response for each reachable port:

- **HTTP 405 + frame-ancestors CSP** = JupyterHub (auth required by design; HEAD on /hub/api/info returns 405 Method Not Allowed)
- **HTTP 200 with `<title>JupyterHub</title>`** = JupyterHub login page (root path)
- **HTTP 200 with no CSP** = different platform (Apache landing pages, LiteLLM, etc.)

This is where the SUNY Stony Brook port 8888 and UW orca port 443 turned out to be NOT-Jupyter despite the seed.

### Auth-state probe (the missing chain step)

Aimap's `auth_status: unknown` left the question "is this auth-on or auth-off?" unresolved. A targeted HEAD/GET probe of `/hub/api/info` (JupyterHub) and `/api/sessions` (classic Notebook) per host gave the answer:

```
VT (128.173.51.43)        :80   /hub/api/info → 403 Forbidden  (jh=4.0.2)  AUTH-INTACT
NCSU (152.14.199.179)     :443  /hub/api/info → 403 Forbidden  (jh=5.3.0)  AUTH-INTACT
UMD (128.8.235.64)        :443  /hub/api/info → 403 Forbidden  (jh=4.0.2)  AUTH-INTACT
Hampton (137.198.56.13)   :443  /                → 200 (login)  (jh=2.0.0)  AUTH-INTACT
UIC (131.193.78.37)       :443  /                → 200 (login)  (jh=5.3.0)  AUTH-INTACT
SUNY 8888                 :8888 /tree            → 404           NOT-JUPYTER
UW orca                   :443  /                → 200 Apache    NOT-JUPYTER (different finding class)
Berkeley                  :4000 /v1/models       → 401 Unauthorized  AUTH-PROTECTED LiteLLM
Wharton                   :443  / (SNI strict)   → 421 Misdirected   FILTERED
MIT 6004hub / rosettai    :443  /hub/api/info    → timeout       FILTERED to research network
```

Five JupyterHub auth-intact hosts → finding tier is "version currency" + "transport security", not "unauth-kernel-exec". This is materially different from the Cortical Labs CL1 incident where the kernel-API exec primitive was wide open.

### Step 3-5: aimap-profile + nuclide-contact

Aimap-profile classified all 13 hosts under `Educational institution — CFAA exposure; prefer institutional CSIRT disclosure` ethics flag. Disclosure routing (Methodology Insight #4 derived) per host above.

## The 6 disclosures

Per-institution disclosure drafts:

1. [`VT-jupyterhub-http-only.md`](../../disclosures/VT-jupyterhub-http-only.md) (HIGH) → `security@vt.edu`
2. [`HAMPTON-jupyterhub-2.0-stale.md`](../../disclosures/HAMPTON-jupyterhub-2.0-stale.md) (HIGH) → `barbara.tibbs@hamptonu.edu`
3. [`UMD-jupyterhub-4.0.2-cves.md`](../../disclosures/UMD-jupyterhub-4.0.2-cves.md) (MED-HI) → `abuse@umd.edu`
4. [`NCSU-jupyterhub-cve-2026-33709.md`](../../disclosures/NCSU-jupyterhub-cve-2026-33709.md) (MED) → `security@ncsu.edu` + `abuse@mcnc.org`
5. [`UIC-jupyterhub-cve-2026-33709.md`](../../disclosures/UIC-jupyterhub-cve-2026-33709.md) (MED) → `esteban@uic.edu`
6. [`UW-atmos-rservices-nfs-exposed.md`](../../disclosures/UW-atmos-rservices-nfs-exposed.md) (HIGH, different class) → `abuse@uw.edu`

All drafted at status `DRAFT, outcome: sent` placeholder. Send via the canonical Gmail-API pipeline (`disclosures/send_drafts_api.py`) when ready.

## Methodology notes

This survey validated that the visor chain produces materially better triage than aimap-only or Shodan-only:

- **Shodan-only** would have flagged all 252 instances as "exposed JupyterHub" without distinguishing version, transport, or auth state.
- **aimap-only** classified the 5 hits as "Jupyter Notebook severity=high" with auth=unknown, leaving the "is this actually a finding" question unresolved.
- **Full chain + auth-state probe** narrowed 13 hits to 6 actionable findings, separated by tier: HIGH (transport / version-stale), MED (version-currency CVE), and the orthogonal HIGH for r-services/NFS that surfaced as a side-effect of the dork.

Methodology Insight #6 (conjunctive matchers) applies in full here. The Shodan dork's `JupyterHub` substring matched 252 hosts; the per-host probe-and-validate winnowed to 6.

For the next vendor-template-class sweep (the ~25 adjacent vendors mentioned in the Cortical Labs vendor-template study), expect a similar narrowing ratio: many candidate hits at the dork layer, a meaningful minority that survive aimap classification, and a smaller still subset that produce auth-state findings worth disclosing.

## See also

- [vendor-template-adjacent-sweep-2026-05-07](vendor-template-adjacent-sweep-2026-05-07.md) — the planning doc this came out of
- [vendor-template-default-no-auth-research-instruments](vendor-template-default-no-auth-research-instruments.md) — the parent threat-class study
- [multi-hilix-jupyter-campaign-2026-05-06](multi-hilix-jupyter-campaign-2026-05-06.md) — the originating CL1 incident (different threat class)
- [Methodology Insight #4](../../methodology/insight-04-whois-driven-contact-resolution.md) — WHOIS-driven contact resolution (applied to MCNC + Google LLC findings here)
- [Methodology Insight #6](../../methodology/insight-06-conjunctive-matchers-required.md) — conjunctive matchers
- [Methodology Insight #10](../../methodology/insight-10-vendor-template-default-no-auth.md) — vendor-template default-no-auth (the parent class)
