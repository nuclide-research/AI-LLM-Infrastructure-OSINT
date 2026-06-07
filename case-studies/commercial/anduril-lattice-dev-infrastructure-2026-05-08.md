---
type: host
title: Anduril Industries, Lattice Monitoring Plane (Telefonica ARO Grafana), Disclosure Sent, Awaiting Acknowledgment
date: 2026-05-08
class: commercial/defense
category: c2-monitoring-plane, public-developer-api
status: disclosure-sent
methodology: passive-dns, viewdns, csp-pivot, http-probing, shodan
disclosure_recipient: disclosures@anduril.com
disclosure_sent_date: 2026-05-09
disclosure_gpg_fingerprint: 67EE B1A4 05BF 0A0A F0A7 EB35 5477 1229 1AE1 D9DF
public_dorks_held: yes-until-acknowledged
---

# Anduril Industries: Lattice Monitoring Plane Exposure

NuClide Research · 2026-05-08 (sent 2026-05-09)

> **Status:** Disclosure **sent** to `disclosures@anduril.com` on 2026-05-09 (GPG-encrypted to fingerprint `67EE B1A4 05BF 0A0A F0A7 EB35 5477 1229 1AE1 D9DF` per their published security.txt). This redacted case study is published; full IP-level operational detail (cluster inventory, per-tier cert SANs, targeted Shodan dorks for individual production tiers) is held in the disclosure pack and will be added to the public artifact only after Anduril acknowledges and a reasonable remediation window has passed.

---

## What This Documents

A focused investigation of Anduril's Lattice infrastructure that surfaced **5 verified findings** (2 HIGH, 1 MEDIUM, 2 LOW, all configuration hygiene, none critical), **5 items surfaced for the team's judgment**, and **1 unverified prior-session claim that did not hold up** on re-test.

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7004, K7044, S7068, S7070, S7075, T5904, T5919
- **733 (AI Risk & Ethics Specialist):** K7051, T5868, T5893
- **overlap (Common AI KSATs (all 5 roles)):** K1158, K1159, K22, K6311, K6900, K6935, K7003, K7048

<!-- ksat-tag:auto-generated:end -->

The point of including this in the public OSINT repo is methodological: it shows what *not* to do (the prior-session claim that didn't survive verification) and it documents that defense-contractor targets are handled differently from commercial-cloud surveys.

---

## Verified Findings (Detail in Disclosure Pack, Not Public)

### F2. HIGH: Telefonica ARO Grafana. Anonymous Datasource Inventory

A Grafana instance running on a Telefonica-managed Azure Red Hat OpenShift cluster, referenced in the Lattice Developer Platform's CSP `frame-src`, returns the full datasource configuration to unauthenticated requests via `/api/datasources`.

The exposed inventory references Lattice-specific naming (a Prometheus datasource called `lattics-bsidp`, i.e. Lattice Backstage IDP), confirming this is part of the Anduril monitoring plane even though the Grafana sits on Telefonica's infrastructure.

The exposure includes internal Kubernetes service URLs, three plain-HTTP backends in Azure commercial East US, and a PostgreSQL endpoint (auth-protected at the application layer). Full inventory is in the disclosure pack.

**Owner:** Telefonica (operator). Anduril notified to coordinate.

### F3. HIGH: Systemic Private-IP Leakage Across andurildev.com Route53 Zone

A passive DNS sweep of 157 unique subdomains under `andurildev.com` (sourced from public certificate transparency data) shows **44 (28%) resolve to RFC-1918 private IP addresses in public DNS**. The leak spans the zone, not a one-off, and exposes multiple distinct internal subnets across at least nine internal address ranges, including the AI/ML data plane, multiple SIE cluster environments, the Crucible CI/CD cluster, customer/partner demo subnets, and the Maritime ASV's separate 172.16-prefixed network.

The fix is at the zone level (audit + move RFC-1918 records to a private hosted zone), not per-record. Full enumeration with subnets and per-subdomain mapping is in the disclosure pack.

**Owner:** Anduril.

**Why this is impactful:** The internal subnet allocation strategy is partitioned by tier (observability, secrets, data, AI, SIE, customer-demo) at /19–/20 granularity. From an attacker's perspective, knowing which internal subnet hosts which workload class materially shortens the kill chain if any internal foothold is later obtained. A benefit Anduril's defenders would prefer to deny.

### F-NEW-2. MEDIUM: Self-Signed `localhost` Cert Auto-Renewing on 3 Public Lattice Deployments

Three publicly-reachable Lattice login pages (across Microsoft / Oracle / Cloudflare hosting providers) present a self-signed certificate with `Issuer/Subject: O=Anduril, L=Costa Mesa, CN=localhost`. The cert is rotated by automation on a regular cadence. One of the three was rotated to a fresh cert during this investigation, and the new cert was *still* the same broken `CN=localhost` template. This is a deployment-template + cert-renewal-automation defect, not a one-time mistake.

**Owner:** Anduril.

### F-NEW-3. LOW: `fleet.internal` cert SAN on 2 AWS GovCloud Hosts

Two AWS GovCloud Lattice hosts serve a cert with `CN=fleet-core-toc.fleet.internal`. The internal namespace + service identity are leaked in CT logs and to anyone connecting to port 443. Same root cause as F-NEW-2.

**Owner:** Anduril.

### F-NEW-4. LOW: AKM Internal-ALB Names Exposed via Public DNS CNAMEs

Two `*.akm.anduril.com` subdomains CNAME to `internal-altius-key-store-mfgops-*.us-gov-east-1.elb.amazonaws.com` (AWS internal-only ALBs). The IPs aren't externally routable, but the **internal LB names + AKM operational-tier naming** (`mfgops` / `eudops`) + AWS GovCloud-EAST region are now public. AKM = Altius Key Manager. Encryption key infrastructure for the Altius loitering-munition program.

**Owner:** Anduril. Same fix class as F3.

---

## Items Surfaced (Not Findings)

- **`http://route-ytterbic-canidae-openshift-operators.apps.telefonica.centralus.aroapp.io`** appears in the Backstage CSP as a plain-HTTP `frame-src`. Currently 503; not exploitable as observed. Surfaced to Anduril for CSP audit.
- **Certificate Transparency naming**: the andurildev.com cert SAN surface in CT logs uses program codenames, customer identifiers, and (in two cases observed) classification-level labels. Public by RFC 6962 design. Not a security finding. Surfaced for ITAR information-control review at Anduril's discretion. Specific entries listed in the disclosure pack.
- **Okta OIDC discovery** at `dev-okta.developer.anduril.com` and `login.developer.anduril.com` lists `password` grant_type, `implicit` flow, and `none` token_endpoint_auth_method as supported. These are Okta tenant-level defaults (advertised capability ≠ per-app enablement), but worth Anduril's identity team confirming no production app actually has these enabled.
- **Klas Telecom Government / Voyager OEM relationship** is publicly disclosed via a redirect rule in `armory.anduril.com`'s JavaScript bundle (`/voyager-support → klasgroup.com/support`). If the OEM relationship is intended to be customer-only knowledge, route the redirect server-side instead of client-side.
- **Palantir Workshop module ID** (`f8c05d84-ac01-4a9b-8a9e-9cbc401d2cf8`) is in the public 302 Location header from `customerportal.anduril.com → alpha.palantirgov.com`. Stable Palantir RID. Accessible to anyone with credentials on the alpha tenant.

---

## A Prior Claim That Did Not Verify

A prior session claim that the Backstage instance at `20.106.9.145` was leaking the internal service catalog via unauthenticated `/api/catalog/entities` did **not** verify on re-test. The endpoint returns HTTP 500 with a server-side error log ID, not catalog data. The prior session likely hit a User-Agent-gated middleware redirect and misread the result.

This is documented here as a self-correction, and is the reason the disclosure does *not* include a "Backstage public mode" finding. The 500 logIds were surfaced to Anduril for their own review (the error indicates a backend issue, not necessarily a security one).

**Methodology note:** Re-verify single-session claims before they propagate. The advisor pattern caught this one.

---

## Public Lattice Developer API Context

Anduril operates a **public** developer API at `https://developer.anduril.com` for third-party integration with Lattice. This is intentional and documented (Fern-built docs, OAuth 2.0, REST + gRPC, Entity Manager + Task Manager APIs). The portal even publishes `/llms.txt` and `/llms-full.txt` for AI-agent consumption.

This is research context, not a finding. The existence of a public Lattice API confirms the platform's "open SDK for autonomous-system integration" positioning.

---

## What Is Held Until Acknowledgment

Out of respect for an active coordinated-disclosure window, the following are **not** in the public repo until Anduril acknowledges and a reasonable remediation window has passed:

- IP-level cluster inventory (auth/SRE/load-test cluster naming and per-IP attribution)
- Cluster topology pattern (per-node multi-AZ deployment shape)
- Specific subdomain enumeration list beyond what is already public via CT logs
- Targeted Shodan dorks for individual Anduril production tiers (cluster-level cert SANs, etc.)

These are documented in the disclosure pack. They will be redacted into the public case study only after acknowledgment + remediation, with operational detail trimmed to what is already public via CT/Shodan.

---

## Disclosure

- **Recipient:** disclosures@anduril.com (per security.txt)
- **GPG fingerprint:** `67EE B1A4 05BF 0A0A F0A7 EB35 5477 1229 1AE1 D9DF` (their published key)
- **Sent:** 2026-05-09
- **Timeline:** 90 days standard; happy to extend if Telefonica coordination requires
- **Status:** awaiting acknowledgment
