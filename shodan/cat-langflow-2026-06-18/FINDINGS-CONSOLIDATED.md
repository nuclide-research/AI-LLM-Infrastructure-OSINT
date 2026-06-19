# Cat-Langflow 2026-06-18 — Consolidated Findings (verification stage output)

## Headline
`http.title:"Langflow"` Shodan dork (54,685 hits) is ~100% FALSE POSITIVE, dominated by a
catch-all SCANNER-POISONING DECEPTION FLEET. NOT Langflow. Real Langflow is Shodan-dark via
this dork; the 2 real instances surfaced (port:7860 + functional filter) are BOTH HARDENED.

## Harvest funnel
- http.title:"Langflow" Shodan: 54,685 (multi-service-per-host inflation + deception fleet)
- Unique IPs harvested (10 pages): 93
- Live on Langflow ports (naabu connect): 90/93 (97%)
- "Confirmed" via health_check triple-match: 35 IPs / 76 port-combos  <-- ALL FALSE POSITIVE
- Real Langflow (package:Langflow discriminator): 2 confirmed (both hardened)

## The deception fleet (PRIMARY FINDING)
Every one of the 35 "confirmed" hosts is a catch-all responder, NOT Langflow:

1. CATCH-ALL 200: /api/v1/nonsense-xyz-12345 and /this-path-does-not-exist-99999 both
   return 200 with the same ~135KB canned HTML.
2. SERVER-HEADER ROTATION: same host returns a DIFFERENT fake Server header every request
   (nws/1.0, Aerlang, Oracle XML DB, Jexus, kangle, istio-envoy, cloudflare, Raspbian, ...).
   Deliberate anti-fingerprinting.
3. IDENTICAL CANNED JSON across 31 hosts on DISJOINT ASNs (Aliyun CN, Akamai/Linode US, APNIC AU):
   /api/v1/version  -> {"database":"ok","version":"10.0.1+gitea-1.22.0",
                         "commit":"5bda17e7c1cb313eb96266f2fdda73a6b35c3977","stok":"abcef7192af3",
                         "activeWorkspaceId":...}   (Gitea shape + TP-Link `stok` field grab-bag)
   /api/v1/auto_login -> fabricated JWT, user "jack" id 123, exp 2025-11-21 (EXPIRED 7 months).
4. PER-HOST REAL FRONT PAGE differs: titles "Smart Mobility Mail", "TM Automacao",
   "Tor Exit Server tor-exit-se1.privex.cc". Scripts: /theme/v2board/assets/umi.js (v2board
   proxy-subscription panel), cdn.jsdelivr.net/ghost/portal (Ghost). So hosts run real
   v2board/Ghost/Tor-exit apps WITH a catch-all deception layer fronting the API paths.
5. health_check triple-match (status/chat/db) over-matched because the 135KB canned HTML
   contains those substrings; the fleet ALSO serves path-aware canned JSON for known API paths.

## Observation-position gate (Insight #96 — MANDATORY, passed CLEAN)
On Mullvad us-mkc-wg-001. Control hosts probed through same exit returned their REAL content
(example.com -> "Example Domain"; scanme.nmap.org -> "Go ahead and ScanMe!"; api.github.com -> real JSON).
=> NOT VPN L7 rewriting. The fleet is genuinely serving this. Suspect hosts stable across re-probes.

## Real Langflow tier (SECONDARY FINDING)
Discriminator: GET /api/v1/version returns "package":"Langflow" (fleet fakes Gitea, never this).
- 172.241.24.136:443  Langflow v1.5.0.post2  HARDENED (auto_login 400, flows/vars 403; config 200 leaks feature-flags only)
- 24.152.39.20:7860   Langflow v1.7.3         HARDENED (auto_login 400, flows/vars/config 403)
Both AUTO_LOGIN=False. n=2, but both hardened => consistent with Insight #40 (disclosure-pressure
hardening; Langflow had Flodrix botnet mass-exploitation + 3 CISA-KEV CVEs in 2025-26).
Real Langflow population NOT sizable via title dork (poisoned) -> population-substitution (dork-bias).

## Robust fingerprint (methodology fix)
- POSITIVE anchor: /api/v1/version body contains "package":"Langflow"  (fleet returns Gitea, never this)
- NEGATIVE guard: a nonsense /api/v1/<random> path must NOT return 200 (catch-all detector)
- The health_check status/chat/db triple over-matches the fleet's canned HTML -> insufficient alone
- JWT-functional: real open Langflow's auto_login token authenticates /api/v1/flows/ (200); fleet token does not

## Verdict tally
- Deception fleet hosts (refuted as Langflow): 33 of 35 "confirmed" (+ all 4 version-unresolved also refuted)
- Real Langflow: 2 (both hardened, 0 open)
- Open-superuser Langflow found: 0
- CVE-exploitable Langflow found: 0 (the 2 real ones are v1.5.0.post2 / v1.7.3, hardened)

## CVE reference (for the real-Langflow tier, none exploitable here)
- CVE-2025-3248 (9.8, KEV) unauth RCE /api/v1/validate/code, <1.3.0 (Flodrix botnet)
- CVE-2025-34291 (9.4, KEV) CORS ATO+RCE, <=1.6.9  [v1.5.0.post2 would be in range IF open — it's hardened]
- CVE-2026-33017 (9.3, KEV) unauth RCE /api/v1/build_public_tmp, <=1.8.2 (exploited <20h)  [both real ones in range IF open]
