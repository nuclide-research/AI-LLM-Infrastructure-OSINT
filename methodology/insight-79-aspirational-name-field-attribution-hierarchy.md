# Insight #79 — The `name` field is aspirational free text; attribution needs a hierarchy

**Survey:** Cat-OW (Open WebUI population survey) calibration pass, 2026-06-06.

## Statement

When a platform exposes an operator-set string in its public config (Open WebUI's
`name`, Langfuse's `app_name`, OneAPI's `system_name`, V2Board's `app_name`), that string
is **aspirational free text**. Taking it at face value for severity scoring is the
single biggest source of overclaimed institutional findings.

Anyone running a self-hosted instance can write "SWIFT", "PepsiCo", "CUNY AI Lab",
or "U.S. State Department" into that field. The platform validates nothing. Severity
scoring that treats the name as institutional ground truth inflates findings.

## Attribution hierarchy (use this order)

| Tier | Signal | Strength | What it proves |
|---|---|---|---|
| 1 | TLS cert SAN (OV/EV) | Authoritative | The org named in the cert controls the listed DNS names |
| 2 | rDNS PTR / institutional ASN netblock | Strong | The IP block is allocated to or used by the named org |
| 3 | WHOIS organization | Moderate | Block-level owner — often a parent ISP, not the deployer |
| 4 | Hostname → forward DNS via institutional domain | Moderate-Strong | Subdomain on an institutional TLD (e.g. `*.cuny.edu`) |
| 5 | Operator-set `name` field in `/api/config` | **Aspirational** | Anyone can write anything; proves nothing |

**Rule:** A finding cited at institutional severity needs at least Tier 1 OR Tier 2.
Without one of those, the finding is "signup-open Open WebUI calling itself X" — the
auth-state risk is real, but the scope claim shrinks to whatever the actual operator
built.

## Evidence (Cat-OW calibration deltas, 2026-06-06)

| Original case study claim | Hosting evidence | Calibrated finding |
|---|---|---|
| **Dartmouth Wind Lab** (129.170.224.237) | DART-ETHER netblock + `*.dartmouth.edu` cert | **Confirmed REAL** — genuine Dartmouth institutional infra |
| **PLLuM / NASK Poland** (194.181.158.235) | CBiTT-NASK-PIB block + `chat.pllum.edu.pl` cert | **Confirmed REAL** — genuine state-cybersecurity authority infra (most severe finding in survey) |
| **CUNY AI Lab** (44.199.166.66) | Generic AWS EC2 + `openwebui.cuny.qzz.io` dynamic DNS | **Personal/lab project branded CUNY**, not central CUNY IT — case study overstated scope |
| **SwiftRef Assistant** (52.204.54.17) | Generic AWS EC2, HTTP only, no cert | **Auth-off risk real, SWIFT attribution unverifiable** — could be POC, vendor demo, or unrelated |
| **deepset \| PepsiCo** (18.211.90.210) | Generic AWS EC2, HTTP only, no cert | **Signup-open risk real, deepset/PepsiCo attribution unverifiable** — same as above |

3 of 5 named-institution findings needed scope corrections after applying the
hierarchy. The original case study took Tier 5 (`name` field) at face value.

## Why this matters

Disclosure pipelines route by attributed organization. Sending a "CUNY AI Lab signup
open" disclosure to CUNY central IT when the deployment is a grad student's personal
qzz.io EC2 wastes a CISO's attention and damages NuClide's signal-to-noise reputation.
Sending a "SwiftRef Assistant auth-off" disclosure to SWIFT's CISO when the box is a
random EC2 in someone's personal AWS account is worse — it asserts a SWIFT compromise
that doesn't exist.

The auth-state finding is real either way. The **target of the disclosure** depends
on attribution, and Tier 5 cannot determine the right target.

## Operational rule for case studies

Before citing an institutional name in a case study heading:

1. **Pull the TLS cert** — `openssl s_client -connect IP:PORT -servername IP | openssl x509 -noout -subject -ext subjectAltName`. OV-validated cert subject = institutional ground truth.
2. **Run rDNS + WHOIS** — `host IP` and `whois IP`. Institutional ASN or netblock allocation = strong signal.
3. **If both come up generic cloud** (AWS, GCP, Azure, Hetzner, Vultr, OCI) **and there is no institutional domain on the cert**, the finding is hosted on **personal/operator-controlled cloud**. Replace the institutional name with a descriptor like "operator-branded `name` claim, hosted on AWS EC2" and bound the disclosure accordingly.
4. **If the operator-set name is the only attribution signal**, say so explicitly: *"Operator self-identifies as X; no cert or netblock confirmation."* Severity stays at signup-open / auth-off, scope stays at instance-only.

## Related insights

- [[insight-02-single-template-auth-off-propagates]] — template-class exposure pattern
- [[insight-31-app-builder-brand-in-output]] — same anti-pattern for app-builder tools (brand in output, not agent)
- [[insight-39-pooled-account-attribution-laundering]] — attribution laundering at the pooled-account layer
- [[insight-78-shared-deployment-kit-operator-class-exposure]] — kit-level exposure where favicon/version are the population selector

## Codification

This calibration pass cost ~15 minutes (4 hosts × `curl /api/config` + `openssl s_client` + `whois`). Adding it to the standard verification phase (Stage 3v) for any `name`-bearing platform is cheap and catches the overclaim before it propagates into case-study, disclosure, or aggregate stats.
