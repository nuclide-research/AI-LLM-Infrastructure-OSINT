---
type: methodology
insight_number: 107
title: "Scanner-poisoning mega-JSON deception fleet: one canned payload baits MANY scanner classes at once (RCE proof + tokens + versions + admin) and rotates its Server header per request to defeat naive body-probe fingerprints"
status: candidate
codified: 2026-06-19
source_survey: Cat-Langflow 2026-06-18 (http.title:"Langflow" 54,685 hits, ~100% FP onto the fleet)
falsifiability_tier: high
falsified_by: a cohort that catch-all 200s on nonsense paths and serves an identical multi-bait mega-JSON across disjoint ASNs but is shown to be a single legitimate platform (the platform itself emits the uid=0(root) RCE proof, the Gitea commit, the TP-Link SetIpMacBindSettings node, and the fabricated JWTs as genuine output)
related_insights: [1, 30, 32, 97, 108]
---

# Insight #107 - Scanner-poisoning mega-JSON deception fleet

## The pattern

A distinct deception-fleet class. Where Insight #32 fleets rotate the HTTP
`<title>` per request to match many title dorks, and Insight #97 fleets stage a
different TLS cert per host, this class concentrates its deception into ONE
canned JSON payload that simultaneously satisfies the success-marker of MANY
unrelated vulnerability scanners at once. The payload is not tailored per
scanner; it is a grab-bag union of every marker the operator wants to trip,
served identically to everyone.

The fleet is a positive-bait machine, not a honeypot in the listen-and-log
sense. Its purpose is to make a scanner report "VULNERABLE / OWNED" against a
host that runs nothing of the kind, poisoning the scanner's output and any
research dataset built from it.

## The four-part signature

A host belongs to this class if ALL of the following fire:

1. **Catch-all 200 on a nonsense path.** `GET /api/v1/nonsense-xyz-12345` and
   `GET /this-path-does-not-exist-99999` both return 200 with the same large
   canned HTML body. A real platform 404s an invented path. This is the cheapest
   single discriminator and the NEGATIVE guard of Insight #108.

2. **Server-header rotation per request.** The same host returns a different
   fake `Server` header on consecutive requests (founding cohort observed:
   `nws/1.0`, `Aerlang`, `Oracle XML DB`, `Jexus`, `kangle`, `istio-envoy`,
   `cloudflare`, `Raspbian`). The `Server` string is a settable value; rotating
   it defeats any fingerprint anchored on it and signals deliberate
   anti-fingerprinting.

3. **Identical canned mega-JSON across disjoint ASNs.** A path-aware bait JSON is
   served on known API paths (founding: `/api/v1/version`) byte-identical across
   hosts on unrelated ASNs (Aliyun CN, Akamai/Linode US, APNIC AU) - same Gitea
   commit `5bda17e7c1cb313eb96266f2fdda73a6b35c3977`, same `stok abcef7192af3`,
   same `"jack"` JWT. Cross-ASN payload identity is the coordination proof: one
   operator, many networks.

4. **The mega-JSON stuffs bait for many scanner classes simultaneously.** This is
   the class-defining property. A single `/api/v1/version` response (founding
   cohort, 2.5KB) carried, in one object:
   - **RCE proof bait**: `"xmsg": "...uid=0(root) gid=0(root) groups=0(root)\nroot\nLinux sensor 5.15.0-106-generic..."`, `"proof_file": "/tmp/a"`, `"result": "root"`, `"group": "root"` - the success strings a dozen command-injection / unauth-RCE templates grep for.
   - **Version-disclosure bait**: `"version": "10.0.1+gitea-1.22.0"`, `"commit": "5bda17e7..."` (Gitea shape) plus a second `"Version": "1.0.36"`.
   - **Token / credential bait**: two fabricated JWTs (`access_token`, `token`), `accessToken`, `refreshToken`, `tempToken`, `CSRFToken`, `csrfToken`, `totpKey`, `Nonce`, `sm_nonce`.
   - **Admin / privilege bait**: `"owner_email": "admin@example.com"`, `"name": "admin"`, `"privileges": ["read","write"]`, `"adminDevices": 2`.
   - **Vendor-specific bait**: `"SetIpMacBindSettingsResponse": {"SetIpMacBindSettingsResult": "OK"}` (TP-Link router config-write success), `"stok"` (TP-Link session token field), `"activeWorkspaceId"`, `"workflow_permanent_id"`.
   - **Locale bait**: `"errmsg": "成功 没有权限"` (Chinese "success / no permission") to satisfy CN-localized scanners.

   No real platform emits a uid=0(root) shell banner, a Gitea commit, a TP-Link
   config-write node, and two JWTs from a single version endpoint. The union is
   the tell.

## Why it defeats naive body-probe fingerprints

A body-substring fingerprint of the form "if response contains X then platform
is Y" inverts cleanly against this fleet. The fleet stuffs X for many values of X
into one body, so it matches EVERY such fingerprint at once. The founding survey's
`health_check` triple-match (body contains `status` AND `chat` AND `db`)
over-matched because the 135KB canned HTML and the mega-JSON both contain those
generic substrings. The fleet does not need to know your fingerprint; it pre-stuffs
the marker space.

The fleet also impersonates many platforms via keyword stuffing to poison TITLE
dorks specifically. The founding cohort surfaced under `http.title:"Langflow"`
(54,685 Shodan hits) while serving canned HTML whose own `<title>` rotates
(`LBot`, `BigAnt Admin`, `Laravel` all observed in one page capture), and while
embedding platform keywords (Langflow, Gitea, Ghost) and a v2board theme path
(`/theme/v2board/assets/umi.js`). One fleet host therefore appears in the dork
result set for many unrelated products simultaneously - the same multi-dork
contamination Insight #32 described, now driven by payload stuffing rather than
title rotation alone.

## Empirical founding case - Cat-Langflow 2026-06-18

`http.title:"Langflow"` returned 54,685 Shodan hits. 93 unique IPs harvested
across 10 pages, 90/93 live on Langflow ports. 35 IPs "confirmed" via the
health_check triple-match - ALL 35 false positive, all members of this fleet.

- Catch-all 200 confirmed on two distinct nonsense paths.
- Server-header rotation confirmed across consecutive requests.
- Identical mega-JSON on `/api/v1/version` across 31 hosts on disjoint ASNs
  (Aliyun CN, Akamai/Linode US, APNIC AU); same Gitea commit, same `stok`,
  same `"jack"` JWT (`/api/v1/auto_login`, user id 123, exp 2025-11-21,
  expired 7 months).
- Per-host REAL front pages differ ("Smart Mobility Mail", "TM Automacao",
  "Tor Exit Server tor-exit-se1.privex.cc"), with `/theme/v2board/assets/umi.js`
  (v2board proxy-subscription panel) and `cdn.jsdelivr.net/ghost/portal` (Ghost)
  scripts. The hosts run real v2board / Ghost / Tor-exit apps WITH a catch-all
  deception layer fronting the API paths. The deception is a layer bolted onto a
  real app, not a standalone honeypot.

Real Langflow population (this dork): 2 hosts, both hardened, 0 open. The
title dork is so poisoned that the real platform is statistically invisible
through it - a population-substitution result (Insight #15 / dork-bias).

## Observation-position gate passed clean (Insight #96)

Survey ran on Mullvad `us-mkc-wg-001`. Control hosts probed through the same exit
returned their real content (`example.com` -> "Example Domain";
`scanme.nmap.org` -> "Go ahead and ScanMe!"; `api.github.com` -> real JSON). The
fleet behavior is NOT VPN L7 rewriting; the hosts genuinely serve this. Suspect
hosts stable across re-probes. Insight #107 is only assertable BECAUSE the #96
gate ruled out the contamination alternative; without it the multi-bait JSON
could have been mistaken for an intercepting proxy injecting canned responses.

## How to apply

1. **Run the negative catch-all guard FIRST.** Before any positive body match,
   issue one request to an invented path (`/api/v1/<random>`). A 200 with a large
   canned body short-circuits the host to `deception_fleet_scanner_poison`. This
   is one round-trip and kills 35/35 of the founding survey's false positives.

2. **Treat a multi-bait union as disqualifying, not confirming.** A response that
   simultaneously contains an RCE success string AND a foreign-platform version
   AND multiple tokens AND an admin email is a poison payload. A real platform
   leaks one of these classes at most, from a path that semantically owns it.
   Add a `multi_bait_union` negative conjunct to aimap fingerprints: if a single
   response trips markers from >=3 unrelated platform/vuln classes, downgrade to
   fleet candidate.

3. **Anchor on cross-ASN payload identity for cohort confirmation.** Hash the
   bait JSON. If the identical hash appears across disjoint ASNs, the cohort is
   one coordinated operator regardless of how many platforms it impersonates.
   Promote the cohort, not the per-host findings.

4. **Never cite an RCE / token / admin finding sourced from a fleet host.** Same
   gating rule as Insight #97 rule 3: the cohort signature overrides the per-host
   "critical" finding. A `cohort_signal_override: scanner_poison_fleet` field
   suppresses per-host criticality. Disclosure to the impersonated vendor is
   wrong-channel; the fleet operator is not the vendor.

## Relationship to prior insights

- **Insight #32 (multi-service deception fleets)**: the parent class. #32 fleets
  rotate the `<title>` per request to match many title dorks and carry one
  consistent body marker (GitLab `og:site_name`). #107 is a sibling sub-class:
  the deception is concentrated in a multi-bait JSON that satisfies many SCANNER
  SUCCESS MARKERS at once (not just title dorks), and the anti-fingerprinting
  moves to the `Server` header rather than the title. A host can exhibit both.
- **Insight #30 (multi-port identical responses)**: HTTP multi-port discriminator.
  #107's discriminator is multi-bait-per-single-response, not multi-port. Same
  family (cheap-deception honeypot detection), different axis.
- **Insight #97 (cert-issuer heterogeneity)**: the TLS-layer deception companion.
  #97 stages disjoint certs per host; #107 stages disjoint bait markers per
  response body. A cohort that fails both runs the highest-sophistication
  deception. #97's I/N test should be run against this fleet to place it on the
  cert axis (the founding cohort served on :443; I/N not yet measured).
- **Insight #1 (protocol-strict probing self-filters honeypots)**: #107 hosts
  PASS a naive substring probe by pre-stuffing the marker space; they FAIL the
  catch-all negative guard and the multi-bait-union test. Protocol-strict still
  helps where the platform has a real handshake (the real-Langflow tier was
  recovered via the `package:Langflow` schema anchor, Insight #108).
- **Insight #15 (dork hits vs platform instances)**: the founding cohort is the
  extreme case - 54,685 dork hits, ~0% real platform. The real-rate-after-fleet-
  filter metric (#32) goes to floor here.
- **Insight #96 (paired-probe / observation-position gate)**: prerequisite. The
  multi-bait JSON is only attributable to the fleet after the gate rules out
  intermediary rewriting.

## Open questions

- **One operator or a kit?** The cross-ASN payload identity (same commit, same
  JWT) argues one operator or one shared kit. The per-host real front pages
  (v2board / Ghost / Tor-exit) argue the deception layer is a drop-in module
  bolted onto whatever the host already runs. Likely a redistributed
  catch-all-responder kit, not a single operator's fleet.
- **Defensive or offensive?** Defensive: poison adversary recon so their scanners
  burn time on fake-owned hosts. Offensive: poison public research datasets and
  scanner-result classifiers at population scale (a `http.title:"X"` dork now
  reports 54,685 "X" that are not X). Either way the methodology cost is the
  same: the title dork is unusable without the #108 schema anchor.
- **What is `/theme/v2board/assets/umi.js`?** The v2board proxy-subscription
  panel co-location suggests the fleet overlaps proxy / VPN-resale
  infrastructure. Worth a dedicated pivot.

## See also

- `shodan/cat-langflow-2026-06-18/FINDINGS-CONSOLIDATED.md` - the founding survey
- `shodan/cat-langflow-2026-06-18/evidence/fake-version-json.txt` - the mega-JSON bait payload
- `shodan/cat-langflow-2026-06-18/evidence/canned-page-101.200.142.223.html` - the 135KB canned HTML (rotating own title)
- `shodan/cat-langflow-2026-06-18/evidence/fake-autologin-jwt.txt` - the fabricated "jack" JWT
- `insight-108-positive-anchor-negative-catchall-fingerprint-pair.md` - the fingerprint rule this fleet forces
- `insight-32-deception-fleet-multi-service-emulation.md` - the parent class
- `insight-97-cert-heterogeneity-honeypot-discriminator.md` - the TLS-layer companion
- `insight-30-multi-port-identical-responses-identify-honeypots.md` - the multi-port companion

---

_Status: CANDIDATE. Promotion pending one additional survey that catches a
second scanner-poisoning mega-JSON fleet (any title dork) under the catch-all +
Server-rotation + cross-ASN-identical-multi-bait signature, OR a clean
falsification (a cohort with the signature shown to be a single legitimate
platform). Cite Cat-Langflow 2026-06-18 as the founding evidence._
