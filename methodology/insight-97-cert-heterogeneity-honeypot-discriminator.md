# Insight #97 - Cert-Issuer Heterogeneity Across an Identical-Backend HTTPS Fleet is the Honeypot Operator Discriminator

_NuClide Research · 2026-06-09 founding evidence (Cat-MCP-Cred-Fleet 66 hosts) · 2026-06-10 promoted to numbered after second-cohort reproduction (+22 hosts across two new sub-cohorts on a second port)._

---

## Statement

When N hosts present an identical service backend on TLS (same server name + same version + same exact protocol envelope + same exact tool/method surface), the diversity of TLS subject/issuer pairs across the N hosts is bounded by the operator's legitimacy. A single legitimate operator deploying the same backend at scale produces a narrow cert distribution (1 to 3 issuers, drawn from the operator's own CA or the cloud provider's managed-certificate authority). A coordinated deception/honeypot operator produces a wide and disjoint cert distribution, staged from harvested or fabricated certs across unrelated enterprise verticals (healthcare + industrial DCS + financial + cloud vendor + academic + consumer hardware), designed to attract sectoral-targeted attacker reconnaissance.

The cert-spread-per-identical-backend ratio (I/N) is therefore an operator-legitimacy discriminator, separable from the front-end masquerade and from the backend tool surface itself.

**Boundary condition:** the discriminator requires the cohort to serve TLS. HTTP-only cohorts cannot be evaluated by I/N — and the deliberate TLS deployment is itself part of the deception staging (a legitimate small-scale operator often skips TLS at the application layer; the deception operator must serve TLS in order to stage per-host certs).

## Reproduction summary (promotion data, 2026-06-10)

The candidate insight was promoted to numbered after a 2026-06-10 follow-on survey applied the I/N discriminator to two new sub-cohorts produced by the same operator on a second port. All three measured cohorts return I/N at the deception extreme.

| Cohort | Date | Port | N | I (distinct issuers) | I/N | Backend | Tools | Disposition |
|---|---|---|---|---|---|---|---|---|
| Founding | 2026-06-09 | 9090 | 66 | 55 | 0.833 | mcp-server 1.0.1 | 5 | HONEYPOT_CANDIDATE |
| Reproduction A | 2026-06-10 | 9090 | 9 | 9 | **1.00** | mcp-server 1.0.1 | 5 (identical) | HONEYPOT_CONFIRMED |
| Reproduction B | 2026-06-10 | 3001 | 13 | 13 | **1.00** | mcp-server 1.0.1 | 5 (identical) | HONEYPOT_CONFIRMED |
| **Merged cohort** | **86 unique IPs** | **multi-port** | **86** | **72** | **0.837** | mcp-server 1.0.1 | 5 | HONEYPOT_CONFIRMED |

The two new sub-cohorts surfaced from a `port:9090 "1.0.1"` and `port:3001 "mcp"` Shodan-Playwright harvest (279 + 338 candidates, all probed with the same protocol-strict `mcp-initialize-probe.py` that produced the founding 66). After init-pass filtering, the cred-theft signature (mcp-server 1.0.1 + 5-tool surface: `get_aws_admin_credentials`, `get_aws_session_credentials`, `get_ssh_session_credentials`, `add_cron_job`, `schedule_commands`) survived on 9 + 13 hosts — and **none of the 22 new IPs overlap with the original 66**. The operator is either rotating infrastructure across snapshots or expanding the deployment.

The cert-staging signature reproduced exactly across the new ports. New sub-cohort issuers include `SWIFT Customer Secure CA`, `CENTUM` (Yokogawa industrial DCS), `MySQL_Server_8.4.2_Auto_Generated_CA_Certificate`, `WIN-9QFKHJ39QE9` (Windows IIS default), `WatchGuard Technologies`, `InCommon RSA Server CA` (research/education sector), `HashiCorp Vault`, `VMware Certificate Authority`, `Sectigo RSA EV`, `Microsoft Azure RSA TLS Issuing CA 08`. Subjects include `peardeck.catalog.edu` (academic), `*.your-kyc.bank` (banking/KYC), `queue.hsm.settlement.net` (HSM/settlement banking), `cyberbit.loadbalancer.tech` (cybersecurity vendor impersonation), `Cisco-WLC-*` (network gear), `*.ssl-terminator.private`, `autoscaling-frontend.org`, `legacy-System CA Service`. The vertical-spread profile (banking + industrial + academic + cloud + network gear + consumer device) matches the founding cohort's profile. Same operator, same staging discipline.

## Falsification probe (2026-06-10)

The harvest also surfaced one B=1, T=1 cohort with N=2 hosts from a different operator: **open-alice 1.0.0** on port 3001 at `66.29.128.25` and `66.29.128.61` (same /24, same 52-tool surface — a financial-trading platform exposing `cancelOrder`, `closePosition`, `calculateIndicator`, etc.). These hosts run **plain HTTP, no TLS**, so the I/N discriminator does not apply — the boundary condition above. This is consistent with Insight #97: legitimate small-scale operators frequently skip TLS at the application layer (it is hard work for the operator and offers no value to a single deployment); the deception operator must run TLS in order to stage the per-host vertical certs. **The TLS deployment itself is operator-legitimacy signal,** orthogonal to but reinforcing the I/N discriminator.

The harvest produced no B=1, T=1 cohort with N ≥ 5 on HTTPS that was not the cred-theft fleet. That negative result is also publishable per Insight #16 (a population that is empty under one selection rule is itself a finding when the selection is principled).

## The incident (founding evidence)

2026-06-09 Cat-MCP-Cred-Fleet. 66 hosts on AWS EC2 across 50+ /16s in 15+ regions. Every host returned an identical JSON-RPC `initialize` handshake:

- `serverInfo.name`: `mcp-server` (66/66)
- `serverInfo.version`: `1.0.1` (66/66)
- `protocolVersion`: `2025-06-18` (66/66)
- `endpoint`: `/mcp` over `https://<ip>:9090` (66/66)
- `tools/list`: identical 5-tool set across all 66 (`get_aws_admin_credentials`, `get_aws_session_credentials`, `get_ssh_session_credentials`, `add_cron_job`, `schedule_commands`)

Cert-resniff (DER parsed via `cryptography.x509`) returned **55 distinct issuer CommonNames** and **65 distinct subject CommonNames** across the same 66 hosts:

Industrial / OT issuers: DeltaV (Emerson DCS), BACnet-Controller, Nordex-Issuing-CA-2-2015 (wind turbines), Realtek, FortiMail (frontend), AXIS IAM, Schneider Electric (implied via BACnet)

Financial / regulated: WellsSecure Public Certificate Authority 01 G2 (Wells Fargo), Verifone Certificate Authority, DirectTrust FBCA (federal bridge)

Healthcare: Epic Systems Certificate Authority, Regional Diagnostics Laboratory, Medical Supply Distribution Corp, Clinical Software Solutions, alt.cpsi.viewer.network

Cloud / SaaS: Salesforce (`container-soc1.global` + `salesforce.com, inc.`), Zendesk (`*.zendesk.com`), Snowflake (`dosage.snowflake.corp`), CloudFlare, Travis CI GmbH, Microsoft Azure RSA TLS Issuing CA 08, HashiCorp Vault Certificate Authority, OpenStack Certificate Authority, Kubernetes, Proxmox Virtual Environment, VMware Inc., docker-registry, tigera-operator-signer (Calico/Tigera)

Edge / consumer / device: UBNT-74:AC:B9:82:90:DB (Ubiquiti), AnyConnect (Cisco), `192.168.50.1` (Asus router default), WMSvc-WEBA13 (Windows IIS management)

Fabricated-but-plausible: `manufacturer-infra.store`, `redundant-annuity.org`, `postdoc-srv.edu`, `scheduler-sbox.com`, `showcase-argocd.cloud`, `defender-autodiscover.private` (ADFS Signing), `dosage.snowflake.corp`

No legitimate enterprise operator deploys 66 identical-backend instances each presenting a different cert pulled from an unrelated vertical. The cert spread is the operator's deception staging: each host is dressed as a different victim type to attract sector-targeted reconnaissance traffic.

## Why this generalizes past front-end masquerade

The front-end deception layer (Insight #32, multi-service emulation via rotating titles) operates at the HTTP layer where the operator can change the response per request and where Shodan's title-anchored dorks are the targeted detection surface. The cert layer operates one level deeper: the TLS handshake happens before HTTP, and the cert presented is what the host has provisioned, not what it rotates per request. A multi-service-emulation operator that swaps `<title>` values per HTTP request would still tend to present one consistent cert per host because cert rotation per connection is operationally expensive. An *operator-grade* deception fleet provisions a different cert per host as well, drawn from a curated pool of harvested/fabricated certs.

Insight #32 surfaces the deception at the HTTP body layer; Insight #97 surfaces the deception at the TLS layer. Together they cover the full L7 stack. A host that passes both checks (uniform body shape + narrow cert distribution + identical backend) is a legitimate-scale operator; a host that fails either is a deception candidate.

## The discriminator formula

For an N-host cohort with identical-backend protocol shape on TLS, compute:

- **B** = number of distinct backend serverInfo (name, version, protocolVersion) tuples
- **T** = number of distinct backend tool/method surfaces (sorted tuple of canonical method names)
- **I** = number of distinct TLS issuer CommonNames
- **S** = number of distinct TLS subject CommonNames or organizationNames

Legitimate-scale operator profile (on TLS): B = 1, T = 1, I ≤ 3, S ≤ N (subjects can vary per host within one operator's domain hierarchy).

Honeypot/deception fleet profile (on TLS): B = 1, T = 1, I → N, S → N (cert diversity scales with host count; both subject and issuer trend toward N distinct values).

The cohort's I/N and S/N ratios are the discriminator. A cohort where I/N ≥ 0.3 with identical backend B/T is operator-deception with high confidence. Reproduction data (above) keeps all three measured cohorts in the I/N ≥ 0.83 band; the I/N ≤ 0.05 band remains uninstantiated in the MCP corpus because no legitimate operator deploys at HTTPS+N≥5 scale in the surveyed population yet (the falsification half of the partition awaits a non-MCP comparison cohort).

In the Cat-MCP-Cred-Fleet case: I/N = 55/66 = 0.833, S/N = 65/66 = 0.985, B = 1, T = 1. In the reproduction sub-cohorts: I/N = 9/9 = 1.00 and I/N = 13/13 = 1.00 respectively. The ratios are at the deception extreme.

## How a single-vertical cohort fools the front-end check but not the cert check

A multi-service emulation fleet on the HTTP layer alone (Insight #32 case) might still get caught by the cert check if it's lazy about cert provisioning (all hosts use a self-signed `localhost` cert, or all use the cloud provider's default ACM cert). The Cat-MCP-Cred-Fleet operator is more sophisticated: they have provisioned per-host certs from disjoint verticals, indicating either:

1. **Cert harvesting**: scraping public TLS handshakes from real targets and re-presenting the cert at the honeypot (cert-DN reuse, but the private key is the honeypot's). This works because most cert validation by attacker-side scanners is name-based, not chain-trusted.

2. **Cert fabrication via a controlled CA**: spinning up dozens of internal CAs and issuing signed certs with plausible subject names. The DeltaV/BACnet/WellsSecure/Epic/Nordex distribution is too coherent for harvesting; some of these (especially the made-up plausible names like `redundant-annuity.org`, `postdoc-srv.edu`, `defender-autodiscover.private`) appear fabricated.

3. **Hybrid**: real harvested certs for the high-reputation issuers (Salesforce, Microsoft, Snowflake) interleaved with fabricated certs for the made-up names.

The operator is operating at a sophistication level above the AS63949 Linode honeypot fleet (reference `reference_as63949_honeypot_fleet` in memory), which used a single-issuer salt-based fingerprint. The Cat-MCP-Cred-Fleet operator is staging by vertical, not by template.

## Operator behavior change observed 2026-06-09 → 2026-06-10

The 2026-06-10 follow-on survey produced three operationally relevant operator-behavior observations:

1. **All 66 original IPs still alive at 24-hour mark.** Same backend, same toolset, same 5-tool surface. The fleet is not ephemeral.
2. **22 net-new IPs detected** matching the same backend signature on the same or adjacent port. The operator is expanding, or these were present at the original snapshot but not Shodan-indexed yet, or the operator is rotating IPs at a slow cadence. The new IPs are AWS multi-region matching the original profile.
3. **Multi-port deployment confirmed.** 1 of the original 66 hosts also responds on port 3001 with the identical backend. The operator runs the same canned MCP service on multiple ports for at least one host — relevant for Insight #30 cross-port honeypot-discriminator complementarity.

## Procedural rules this insight generates

1. **Add cert-issuer-distribution / cert-subject-distribution to every Stage 1c / Stage 2 cluster summary.** The aimap output schema, the visor-chain-runner.sh stage outputs, and the VisorGraph cert-pivot all should include I/N and S/N ratios per identified-backend cohort. Today this is computed ad-hoc from `cert-resniff-results.json`; it should be first-class. **The 2026-06-10 reproduction shipped this as `harvest-2026-06-10/cohort-analysis.py` — fold the analyzer into the chain runner permanently.**

2. **VisorCAS signature class: `honeypot-cert-diversity-overload`.** Any cohort where B=1 and T=1 and I/N ≥ 0.3 (with HTTPS) ships as a `confirmed_honeypot_fleet` disposition. Sample artifact: `shodan/cat-mcp-cred-fleet-2026-06-09/methodology/visorcas-signature-mcp-cred-theft-honeypot.yaml`.

3. **aimap deep-enum should NOT cite high-criticality findings on cert-diversity-overload cohorts.** The 86 hosts in this fleet would individually trigger an aimap `MCP-Server unauth, get_aws_admin_credentials exposed, critical` finding. The cohort-level cert distribution overrides the per-host finding. The aimap output needs a `cohort_signal_override: honeypot_fleet` field that downgrades per-host criticality when the cohort signature is matched.

4. **Disclosure pipeline gating.** Any candidate disclosure where the host belongs to a `cohort_signal_override: honeypot_fleet` cohort must route through Lane D (DCWF 733) for restraint review before contact. Honeypot operators are the customer; disclosure to AWS abuse@ is wrong-channel. Routing groundwork (the case study's "Sectoral classification + disclosure-channel candidates" table) stays as-is; the decision is "do not contact" until cohort-level disambiguation completes.

5. **Cross-survey replay.** Past surveys where B=1, T=1 single-template cohorts were classified as "single-operator misdeployment" deserve a cert-distribution re-check. Insight #32's Shinobi/Triton fleets, the AS63949 Linode fleet, and any "vendor-template-default-no-auth" cohort (Insight #10) should be re-examined. **The 51-host Linode `mcp-server 1.0.1` fleet from `mcp-server-survey-2026-05-17.md` is the highest-priority replay target** — it is a B=1, T=1 cohort on the same canned backend but a different operator profile (multi-port + canary-bait at the HTTP layer per Insight #30, not cert-staging). The expected I/N is low or N/A (Linode default cert).

6. **HTTPS-only applicability.** Document the boundary condition: I/N requires TLS. HTTP-only cohorts route to Insight #30 (multi-port discriminator) or fall through to per-host classification. The decision to serve TLS is itself operator-legitimacy signal — deception operators *must* run TLS to stage the per-host certs.

## Relationship to prior insights

- **Insight #1 (protocol-strict probing self-filters honeypots)**: catches honeypots that fail JSON-RPC envelope or schema completeness. Insight #97 catches the honeypots that *pass* the protocol-strict check by being protocol-correct (the Cat-MCP-Cred-Fleet operator is implementing the full MCP 2025-06-18 spec correctly), but stage the surrounding cert layer for sectoral attribution bait. The two checks are complementary at different layers.
- **Insight #6 (conjunctive matchers required)**: same principle applied at the cohort level. Single-condition matchers (one backend identity check) are insufficient when the operator is deliberately staging multiple disjoint layers. Multi-condition checks at multiple layers (backend identity + cert distribution + front-end shape) compound the discrimination.
- **Insight #10 (vendor template default no auth)**: the template-default insight assumed legitimate operators shipping unsafe defaults. Insight #97 partitions the template-default population further: legitimate operators (I/N narrow) versus honeypot operators (I/N wide).
- **Insight #15 (~50% real-rate on raw dorks)**: the Cat-MCP-Cred-Fleet was harvested via the Tabby `/auth/signin` title literal that overmatched. The real-rate calculation should now also exclude honeypot-cert-distribution-overload hosts as a separate category, not just deception-fleet-from-rotating-title hosts (Insight #32). The 2026-06-10 follow-on shows this rate is dork-dependent: `port:9090 "1.0.1"` returned 279 candidates but only 9 init-pass on the MCP signature (3.2%); the rest are substring noise. `port:3001 "mcp"` returned 338 candidates with 33 init-pass (9.8%) — more permissive port + protocol-anchored dork.
- **Insight #16 (200 is identity not auth state)**: I/N is computed at the cohort level *after* a full initialize handshake. The handshake is the identity check, the I/N is the disposition check. Treating an init-pass as "verified-finding" is the failure Insight #97 specifically prevents at cohort scale.
- **Insight #30 (multi-port identical responses identify honeypots)**: HTTP-layer companion. Catches honeypot operators that respond canned on multiple ports per host (the 51-host Linode mcp-server 1.0.1 fleet). Insight #97 catches the operators who run on a single port per host but stage a different cert per host. The two discriminators partition the honeypot operator universe: Insight #30 catches multi-port template-honeypot operators (cheap deception), Insight #97 catches single-port cert-staged operators (expensive deception). A cohort that fails both is operating at the highest deception sophistication tier.
- **Insight #32 (multi-service deception fleets)**: HTTP-layer companion. #97 is the TLS-layer extension.
- **Insight #68 (verification rung Depth x Breadth)**: cohort-level cert-distribution is a Breadth-2 cross-observation that promotes the verification rung over per-host probes. A single-host probe is Depth-A / Breadth-0 even when the probe is precise; cohort-level cross-cert-distribution checks promote to Depth-B / Breadth-2.
- **Insight #88 (scrape topology as operator org chart)**: cert distribution is a related but distinct topology view. Scrape-topology shows operator scheduling/automation patterns; cert-topology shows operator staging/disguise patterns.

## Open questions

- **Are the cert subjects/issuers in the Cat-MCP-Cred-Fleet predominantly real-harvested or fabricated?** Spot-check by re-validating the cert chain trust against the issuers' real root stores. Wells Fargo's `WellsSecure Public Certificate Authority 01 G2` should not validate a `redundant-annuity.org` cert under Wells's real chain; if the chain validates, the cert is fabricated under a controlled CA. If the chain does not validate, the cert was harvested and re-presented without the matching private key (which means the TLS handshake should fail, but the operator may be intercepting at a lower layer).

- **Operator identity beyond "single coordinated AWS customer."** Possible attributions to test:
  - AWS GuardDuty / Inspector internal canary fleet
  - Shadowserver, GreyNoise, ProjectDiscovery, Censys, or other research/scanning operator running paid-for honeypot infrastructure
  - Microsoft Defender Threat Intel (the `defender-autodiscover.private` ADFS Signing cert is a strong lead toward Microsoft)
  - Trellix, Mandiant, CrowdStrike threat-intel fleet
  - Academic / red-team operator (e.g., a university Honeynet Project deployment)
  - Adversarial operator running a counter-intel fleet against other adversaries (less likely given the AWS-only spread and the absence of any operational signal that points to adversarial provenance)

- **Does the operator log `tools/call` invocations and publish the data?** If yes, the fleet is a research-grade honeypot and someone in the disclosure-receiver community already has the dataset. Look for published analyses of MCP server reconnaissance attacks (Shadowserver, GreyNoise, ENISA reports) and cross-reference timing.

- **Scope of the operator's deployment.** 66 hosts in the 2026-06-09 snapshot, 86 unique IPs across the 2026-06-09 + 2026-06-10 snapshots (with the new 22 not appearing in the original 66). Census expansion via Censys / FOFA / a third snapshot would clarify whether the fleet is growing, churning, or both. Operator behavior so far suggests churn-plus-expansion.

- **51-host Linode `mcp-server 1.0.1` cohort I/N measurement.** Open replay target per procedural rule 5. Expected I/N is narrow (single Linode-default cert or no TLS at all). If narrow, Insight #30 and Insight #97 together partition the honeypot operator universe into "multi-port template" and "single-port cert-staged" classes with no overlap, and the partitioning itself becomes a candidate sub-insight.

## See also

- `shodan/cat-mcp-cred-fleet-2026-06-09/case-studies/commercial/cat-mcp-cred-fleet-2026-06-09.md` - the founding survey
- `shodan/cat-mcp-cred-fleet-2026-06-09/harvest-2026-06-10/` - the 2026-06-10 reproduction artifacts (probe + cert + cohort-analysis output)
- `shodan/cat-mcp-cred-fleet-2026-06-09/methodology/visorcas-signature-mcp-cred-theft-honeypot.yaml` - signature draft
- `insight-30-multi-port-identical-responses-identify-honeypots.md` - HTTP-layer / multi-port complement
- `insight-32-deception-fleet-multi-service-emulation.md` - HTTP-layer body-rotation complement
- `insight-68-verification-rung-grid.md` - cohort-level breadth promotes the rung
- `reference_as63949_honeypot_fleet.md` (memory) - the prior-generation single-issuer template, less sophisticated than this fleet

---

_Status: **NUMBERED INSIGHT** (promoted 2026-06-10). Founding cohort: 66 hosts, I/N=0.833. Reproduction cohorts: 9 hosts at I/N=1.00 + 13 hosts at I/N=1.00 on a second port, same backend, no IP overlap. Promotion criterion (apply the I/N check to a second identical-backend cohort) satisfied by two independent reproductions plus the boundary-condition observation that the only available open-alice 2-host falsification cohort runs HTTP-only and thus correctly falls outside the discriminator's scope._
