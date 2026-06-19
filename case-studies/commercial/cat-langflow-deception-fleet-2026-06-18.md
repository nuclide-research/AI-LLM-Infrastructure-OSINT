---
type: survey
title: "Cat-Langflow: The LBot Scanner-Poisoning Deception Fleet"
date: 2026-06-18
category: LLM Orchestration / Deception Infrastructure
slug: cat-langflow
dork: 'http.title:"Langflow"'
indexed_hits: 54685
harvested_ips: 93
real_instances: 2
open_instances: 0
insights: [107, 108]
status: CANDIDATE
---

# Cat-Langflow: The LBot Scanner-Poisoning Deception Fleet

## The answer first

The `http.title:"Langflow"` dork returns 54,685 hits. Almost none of them are Langflow.
The cohort is a scanner-poisoning deception fleet. One canned page, served on every path,
stuffed with bait for hundreds of product fingerprints and dozens of vuln scanners at once.
The page titles itself "LBot." Real Langflow is dark behind this dork. We found two real
instances by a discriminator the fleet never fakes, and both were hardened. Zero open
Langflow. Zero exploitable Langflow. The finding here is not a vulnerable target. The finding
is the fleet, and what it does to every population number that trusts a body substring.

## Recon

Langflow is a visual LLM orchestration builder. It earned its place on the survey list the
hard way. In 2025 and 2026 it took three CISA-KEV CVEs and a botnet named Flodrix that
mass-exploited the first one. An unauthenticated, open, superuser Langflow is remote code
execution on contact. So the dork looked rich: 54,685 indexed titles. That number alone
should have triggered suspicion. Real self-hosted AI orchestration populations run in the
hundreds to low thousands, not five figures.

We harvested ten pages of the authenticated Shodan web UI. Ninety-three unique IPs. Ninety
of them answered on a Langflow port. By the naive matcher this looked like a massive open
population.

## The false-positive cohort

The harvest funnel is where the story turns.

```
HARVEST FUNNEL - http.title:"Langflow"
-------------------------------------------------------------------
Shodan indexed hits                        54,685   inflated
Unique IPs harvested (10 pages)                93
Live on a Langflow port (naabu connect)        90   97%
"Confirmed" by health_check triple-match       35   <-- ALL FALSE POSITIVE
Real Langflow (package:Langflow discriminator)  2   both hardened
Open / superuser Langflow                       0
CVE-exploitable Langflow                        0
-------------------------------------------------------------------
```

Thirty-five hosts "confirmed" on the first matcher. Every one of them was fake. The matcher
read the `status` / `chat` / `db` substrings out of the health-check probe and called it
Langflow. Those substrings were present. They were just present inside a 135KB blob of canned
HTML that the host returns on literally any URL you ask for.

## The deception fleet

Four behaviors define the fleet. Each one is a deliberate inversion of how a scanner decides
what it is looking at.

**1. Catch-all 200 on every path.** We asked for `/api/v1/nonsense-xyz-12345` and
`/this-path-does-not-exist-99999`. Both returned 200. Both returned the same ~135KB page.
A real service 404s on garbage. This host never does. The page titles itself "LBot."

**2. Server-header rotation per request.** The same host returns a different fake `Server`
header on consecutive requests: `nws/1.0`, then `Aerlang`, then `Oracle XML DB`, `Jexus`,
`kangle`, `istio-envoy`, `cloudflare`, `Raspbian`. The header is noise on purpose. Anything
that fingerprints on `Server` gets a different answer every time.

**3. A mega-JSON on /api/v1/version that baits many scanners at once.** This is the core
trick. One response object, byte-identical across hosts on disjoint clouds, stuffs proof for
a dozen unrelated scanner classes into a single body.

**4. Cross-ASN-identical payload.** The same fabricated version, the same commit hash, the
same forged JWT for a user named "jack," reproduced verbatim across hosts on AWS, Linode, and
Alibaba. Disjoint owners returning a byte-identical artifact. That is not a botnet under one
hand. That is a deception appliance, shipped as an image, that anyone can run.

## The mega-JSON bait breakdown

The `/api/v1/version` body is the single most efficient piece of scanner poison we have
documented. It is one object that answers "yes" to many different questions a scanner might
ask. The full payload is in `evidence/fake-version-json.txt`. The bait map:

```
BAIT FIELD(S)                              SCANNER CLASS IT TRIPS
------------------------------------------ ---------------------------------------------
xmsg: "uid=0(root) gid=0(root)...          unauth RCE matcher (command-output grep)
       Linux sensor ... GNU/Linux"
result: "root"  group: "root"              RCE success flag
proof_file: "/tmp/a"                       PoC-write proof matcher
version: "10.0.1+gitea-1.22.0"             Gitea version dork
commit: "5bda17e7c1cb313eb96266..."        Gitea commit fingerprint
stok: "abcef7192af3"                       TP-Link router stok grab
SetIpMacBindSettingsResponse: {OK}         TP-Link SetIpMacBindSettings exploit check
access_token / token (JWT, user "jack")    auth-bypass / autologin matcher
owner_email: "admin@example.com"           default-cred / exposed-admin matcher
totpKey, CSRFToken, csrfToken, sm_nonce    session-token leak matchers
privileges: [read, write]  role            authz-escalation matcher
registerEnabled-class: code:0, success     open-registration config-flag matcher
SetIpMacBind / Nonce / sha1 / sm_nonce     assorted router and CSRF probes
------------------------------------------ ---------------------------------------------
```

The forged JWT decodes to `{"user_id":123,"username":"jack","exp":1763716664}`, which expired
on 2025-11-21, seven months before we pulled it. It does not authenticate anything. It exists
to make an auth-bypass scanner light up green. The `uid=0(root)` line exists to make an RCE
scanner light up green. The Gitea commit exists to make a Gitea version dork light up green.
One body, many lies, all at once.

The page itself goes further than the JSON. The 135KB HTML stuffs the Langflow product string
alongside Gogs/Gitea, a v2board proxy-panel theme path (`/theme/v2board/assets/umi.js`), n8n
base64 config blobs, Splunk MCP, Couchbase, FortiOS, Proxmox, SonicWall, iKuai, and a block of
`WWW-Authenticate` realms. This is the Censys "red herring" pattern: one host that fires
positive on every product dork and every vuln template in the world. The "LBot" title is
cosmetic. The class is anti-honeypot scanner pollution from the Chinese "fuckhoneypot" tool
family. The repo literally named `LBot` on GitHub is an unrelated XSS-bot template. Name
collision, not the source.

## Attribution: a product, not an operator

The 93 hosts split near-evenly across three rival hyperscalers. AWS 28, Linode 27, Alibaba 36.
The 27 AWS hosts scatter across 18 distinct regions on six continents. No operator buys in even
thirds from three competing clouds and then sprinkles boxes across ap-east-1, sa-east-1,
ca-west-1, and eu-north-1 at once. That is the footprint of one image launched by many tenants,
each defaulting to their own home region. Exactly one PTR across all 93 is non-hyperscaler
boilerplate, a DIGI Hungary residential pool. No operator hostname leaks. No shared netblock,
no shared registrant, no shared TLS CN.

The infrastructure leaks no operator on purpose. The only durable identifier is the payload
itself: the fixed Gitea commit `5bda17e7...`, the "jack" JWT, the v2board `umi.js` path, the
"LBot" title. ASN and geography are noise by design. The diversity of hosting is the camouflage.
A scanner sees 54k "Langflow" titles spread across every major cloud and reads a huge, organic,
real population. The spread is what sells the lie.

## The MITM observation-position gate

Before trusting any of this, we checked our own seat. A VPN exit that rewrites L7 content would
produce the same symptoms as a deception host. We were on Mullvad `us-mkc-wg-001`. We probed
three control hosts through the same exit. `example.com` returned "Example Domain."
`scanme.nmap.org` returned "Go ahead and ScanMe!" `api.github.com` returned real JSON. The exit
was not rewriting anything. The fleet hosts stayed stable across re-probes. The deception is
genuinely served by the targets. The gate passed clean. This step is non-optional. A scanner
that skips it cannot tell a deception fleet from its own poisoned uplink.

## The two real instances

The fleet fakes a Gitea version on `/api/v1/version`. It never fakes Langflow's own schema. Real
Langflow returns `"package":"Langflow"` in that body. That key is the discriminator. The fleet's
version body has no `package` key, no `langflow` substring, and a `gitea` value. It cannot pass.

Two hosts passed.

```
REAL LANGFLOW (package:Langflow discriminator)
-------------------------------------------------------------------
172.241.24.136:443   v1.5.0.post2   HARDENED
  auto_login 400 · flows 403 · variables 403
  config 200 leaks feature-flag names only, no secrets
24.152.39.20:7860    v1.7.3         HARDENED
  auto_login 400 · flows 403 · variables 403 · config 403
-------------------------------------------------------------------
Both AUTO_LOGIN=False. 0 open. 0 exploitable.
```

Both run `AUTO_LOGIN=False`. Both reject the autologin path with 400. Both return 403 on flows
and variables. Neither is open. This is consistent with Insight #40, disclosure-pressure
hardening: Langflow shipped through Flodrix and three KEV CVEs, and the surviving exposed
instances are the ones that locked the door.

The CVEs that make Langflow worth hunting, for the record, none exploitable on these two:

- **CVE-2025-3248** (CVSS 9.8, CISA-KEV) - unauth RCE via `/api/v1/validate/code`, versions
  before 1.3.0, the Flodrix botnet vector.
- **CVE-2025-34291** (CVSS 9.4, CISA-KEV) - CORS account takeover chaining to RCE, up to and
  including 1.6.9. v1.5.0.post2 falls in range, but only if open. It is hardened.
- **CVE-2026-33017** (CVSS 9.3, CISA-KEV) - unauth RCE via `/api/v1/build_public_tmp`, up to
  and including 1.8.2, exploited in the wild within 20 hours of disclosure. Both real hosts fall
  in range, but only if open. Both are hardened.

Surface in range is not access exercised. We found zero exploitable Langflow.

## Population substitution

There is a second, quieter finding. The title dork is poisoned, so it does not select real
Langflow. The two real instances we found did not come from the title. One came in on a port
filter (`port:7860`), the other on a functional probe. Real Langflow is Shodan-dark behind its
own title dork because the fleet drowns it. The dork selects the deception population, not the
product. Any population number built on `http.title:"Langflow"` measures the fleet, not Langflow.

## Cross-corpus contamination

This matters past one survey. The fleet poisons two things at once: title-population dorks
(rotating fake titles per request) and success-matchers (catch-all 200 JSON carrying
`code` / `data` / `message` / `registerEnabled`-class fields, fake versions, fake tokens). Any
prior survey whose "confirmed" or "open" verdict was a flag read out of a 200-wrapped JSON body
inherited a matcher the fleet forges.

A contamination audit of 85 title-dork case studies surfaced the exposure. The corpus was not
silently corrupted; the fleet was already documented as Insight #32's "Fleet B" (the Langflow
canned-page IP `101.200.142.223` sits inside the `101.200.0.0/16` Aliyun range named there), and
38 of 85 surveys already cite fleet-awareness. But roughly twelve flag-read surveys are forgeable,
and five warrant re-verification. One carries real stakes: a RAGFlow survey reporting 618
REGISTER_OPEN of 709 live, where the verdict was a `registerEnabled` flag read from
`/v1/system/config`, exactly the wrapper class the fleet stuffs. The corrected RAGFlow figure is
likely lower than 618. That re-verification is the load-bearing follow-up, and it runs with the
same discriminator pair this survey forced into existence.

## Methodology impact

This survey produced two candidate insights.

**Insight #107 - the deception-fleet class.** A new class distinct from #32 (title rotation) and
#97 (cert staging): one canned mega-JSON baits many scanner classes at once. The four-part
signature is catch-all 200 on a nonsense path, per-request Server-header rotation,
cross-ASN-identical payload, and the multi-bait union. The defense is structural: a body
substring is a stuffable token, so a body substring cannot be a fingerprint by itself.

**Insight #108 - the positive-anchor / negative-catchall fingerprint pair.** The fix the fleet
forces. A fingerprint needs two halves. A POSITIVE anchor on a vendor-unique schema key the fleet
never fakes (`package:Langflow`), and a NEGATIVE guard that a nonsense path must not return 200
(the catch-all detector). Either half alone is forgeable. The pair is not.

Both halves shipped into the aimap Langflow fingerprint the same day. The primary probe is now
`/api/v1/version` under four conjunctive conditions: 200, `json_field "package"`,
`body_contains "langflow"`, and `body_not_contains "gitea"`. The fleet's version body has no
`package` key, no `langflow` substring, and a `gitea` value. It cannot fire. The old health-check
triple is demoted to confirm-only and hardened with a parseable-JSON requirement that defeats the
135KB HTML blob.

## Bottom line

54,685 hits. 93 harvested. 35 "confirmed" by the naive matcher, all fake. 2 real, both hardened,
0 open, 0 exploitable. The product was never the finding. The fleet was. It taught the corpus that
a body substring is bait until a vendor-unique schema key and a nonsense-path 404 say otherwise.
