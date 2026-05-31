# Session Analysis: NCKU Edge Host, Kubernetes Control Plane Behind a MikroTik Gateway

**Date:** 2026-05-31
**Session:** single-target, handed-over IP
**Classification:** Internal / Research Use Only
**Toolchain:** aimap 1.9.41, VisorGraph, aimap-profile 0.1, VisorLog, VisorScuba, BARE, VisorBishop 0.1.7, recongraph, nu-recon, Censys platform (web)
**Repos updated:** AI-LLM-Infrastructure-OSINT (case study + this analysis); nuclide.db (#36158-36161)

---

## 1. Overview

### Objective

Assess a single handed-over IP (140.116.247.125) with the full NuClide arsenal.
The thesis question (does an auth-off-default AI layer ship unauthenticated at
scale) was not directly testable here because the host exposes no AI service.
The session instead became a test of the methodology's negative-space discipline:
what happens when the AI-curated scanner says "nothing here."

### Scope and Constraints

- **Target:** 140.116.247.125 (NCKU, TANet, TW). Handed-over single IP, treated
  as in-scope. Operator chose infra-inclusive scope mid-session.
- **Allowed techniques:** passive Censys, banner grab, safe HTTP GET, cert grab,
  port liveness probes.
- **Ethical limitations:** no data exfiltration, no destructive calls, no
  credential use, no login attempt against the KubeSphere console, no Django
  exception triggering. VisorAgent not fired at the operator host.

---

## 2. Environment and Tooling

### Claude Code Operation

Orchestrator-direct (Opus). Active scans dispatched as background tasks and run
in parallel (aimap, VisorGraph, VisorBishop, recongraph). Censys driven via
Playwright after an orphaned browser-profile lock was cleared.

### Tools Used

| Tool | Role | Notes |
|---|---|---|
| Censys (web) | Passive host record | Substituted for Shodan; the session unlock |
| aimap 1.9.41 | Fingerprint | 3 AI-ports open, 0 AI fingerprints (honest negative) |
| VisorGraph | Cert-pivot | TRAEFIK DEFAULT CERT, no domain pivot |
| aimap-profile | Classify | Shodan-degraded, unclassified; manual sector=university |
| VisorLog | Ledger | 4 findings to nuclide.db |
| VisorScuba | Compliance | 0/0 vacuous pass, no K8s-control-plane control |
| BARE | MSF semantic rank | KubeSphere to multi/kubernetes/exec 0.532 |
| VisorBishop 0.1.7 | Re-prober + IP-shadow | No AI platform confirmed |
| recongraph | Seed graph | Empty (passive-source-degraded) |
| nu-recon | Passive deep-read | Simulated output, discarded |

Null runs recorded: menlohunt (not GCP), VisorSD (Shodan-dependent),
VisorGoose (no seed domain), VisorCorpus/VisorRAG (no LLM endpoint),
VisorHollow (Windows-only), VisorAgent (controlled-target only).

### Notable Configuration

Shodan API key invalid this session, which degraded JAXEN, aimap-profile,
recongraph, and VisorSD. Mullvad VPN active (us-mkc exit). aimap timeouts raised
to 8s for the slow Taiwan link; -scan-all-fingerprints over 5 ports timed out at
240s and was dropped in favor of a lean liveness probe.

---

## 3. Methodology

### Enumeration approach

Single seed. WHOIS first for primary-source attribution (NCKU confirmed, exact
inetnum boundary, abuse contact). aimap port fingerprint. Then Censys for
full-range passive coverage once the curated scan came up AI-empty.

### Candidate identification

The Go default-404 byte signature on 80/443 identified Traefik. The Censys
service list identified the MikroTik gateway (MIKROTIK_BW on 2000) and the SSH
fleet. HTML titles and the KubeSphere window.globals blob identified the apps.

### Validation checks

- 200/identity is not auth state (Insight #16): the KubeSphere finding stays at
  inner rung A because the console was observed but login was not exercised.
- Re-run before propagating prior data (Insight #11): a live re-check found
  tcp/6349 closed, downgrading the PHP-portal finding from the Censys snapshot.
- Source over framing: the WHOIS record, not the IP slug, set attribution; the
  page-source config blob, not a marketing string, set the KubeSphere version.

### Safeguards

No brute force, no privilege escalation, no exfiltration, no write-tier ops, no
credential use. The single most tempting move (the KubeSphere default-credential
or default-JWT path) was deliberately not taken.

---

## 4. Execution Trace

| Time (approx) | Action | Outcome / Decision |
|---|---|---|
| T+0 | WHOIS + rDNS | NCKU / TANet confirmed; no PTR |
| T+2 | nu-recon | Simulated output (no key); discarded |
| T+5 | aimap fingerprint | 80/443/8000 open; 0 AI fingerprints |
| T+10 | VisorGraph | Traefik default cert; architecture, no domain |
| T+12 | Censys host record | 18 services; KubeSphere config blob; Django; MikroTik |
| T+18 | aimap liveness re-check | 23180 + 8002 open now, 6349 closed |
| T+20 | VisorLog add x4 | #36158-36161 |
| T+22 | VisorScuba | Vacuous 0/0 pass, gap documented |
| T+24 | BARE | KubeSphere to multi/kubernetes/exec |
| T+28 | VisorBishop + recongraph | No AI platform, empty graph |
| T+32 | Artifacts | findings-breakdown, case study, this analysis |

---

## 5. Findings

> Severity labels require 100% verified evidence at that tier.

**HIGH**
- **F1 KubeSphere v3.1.0 console (tcp/23180).** Type: Kubernetes management UI.
  Evidence: window.globals leaks version, default encryptKey, preset users;
  port live-confirmed open. Exposure: public control-plane console, unchanged
  default JWT secret, EOL K8s. Rung A/1, login not exercised.
  Impact: potential cluster-wide workload control if the console authenticates.
- **F2 Django DEBUG=True (tcp/8000).** Type: web API. Evidence: live debug 404,
  education.urls, api/ + students/. Exposure: settings/env/stack-trace
  disclosure, potential SECRET_KEY leak. Rung B/1.

**MED**
- **F3 MikroTik gateway + 11 SSH DNAT (tcp/2000 + SSH fleet).** Evidence:
  MIKROTIK_BW banner, 11 SSH services. Exposure: internet-reachable internal
  sshd surfaces through one router. Rung B/1.

**LOW (downgraded)**
- **F4 PHP portal admin self-registration (tcp/6349).** Censys-observed only,
  closed at re-check. Not current. Not exercised.

---

## 6. Risk Assessment

### Overall Posture

Isolated host, but a serious one. The risk is concentrated in F1: a public
Kubernetes control plane on a research network with default secrets and EOL
components. F2 compounds it by leaking app internals on the same host.

### Confidentiality / Integrity / Availability

Confidentiality: Django debug leaks app config and likely the signing key; the
KubeSphere console, if entered, exposes secrets and configmaps. Integrity: a
working console session is cluster write access (deploy, delete, exec).
Availability: cluster control implies the ability to delete workloads. None of
this was exercised.

### Systemic Patterns

Shipping-defaults-are-load-bearing (Insight #13): the unchanged KubeSphere
encryptKey and the production DEBUG=True are both quickstart-leftover states, not
exotic misconfigurations. The operator stood the platform up and did not harden
past the defaults.

---

## 7. Recommendations

### R1 KubeSphere console exposure

```bash
# gate the console; rotate the default jwtSecret
kubectl -n kubesphere-system edit cm kubesphere-config   # set jwtSecret to a random value
# and remove the console from the WAN (VPN / authenticating proxy only)
```

Prevents token forgery from the known-default secret and removes the
internet-facing control plane.

### R2 Django debug mode

```python
# settings.py
DEBUG = False
ALLOWED_HOSTS = ["your.campus.host"]
# rotate SECRET_KEY if any debug page was ever public
```

### Future automation

```bash
# full-range, not AI-curated, on campus edge IPs; the AI port set misses this class
aimap -list campus-edge-ips.txt -ports 80,443,2000,6349,8000,8002,23180 -o report.json
```

---

## 8. Limitations and Assumptions

| # | Limitation | Risk Implication |
|---|---|---|
| L1 | Shodan key invalid; passive tools degraded | Relied on Censys; population context not built |
| L2 | aimap/VisorBishop have no KubeSphere or Django fingerprint | Curated scan reported AI-empty on an exposed host |
| L3 | KubeSphere auth state not tested (restraint) | Cannot confirm whether the console grants access |
| L4 | Censys banner dates redacted (free plan) | Freshness partly inferred; mitigated by live re-checks |
| L5 | Internal hosts behind DNAT not assessed | Eleven sshd surfaces unexamined |

---

## 9. Proof of Concept Illustrations

### PoC 1: KubeSphere version and secret disclosure (read-only)

**Scenario:** an anonymous visitor reads the console landing page source.

```
REQUEST:
  GET / HTTP/1.1
  Host: 140.116.247.125:23180

RESPONSE (excerpt, from page source):
  window.globals = {"config":{"title":"ECPaaS",
    "encryptKey":"kubesphere",
    "version":{"kubesphere":"v3.1.0","kubernetes":"v1.22.9"},
    "presetUsers":["admin","sonarqube"],"disableAuthorization":false ...}}
```

**Demonstrated:** version, default JWT secret, and preset usernames are
disclosed pre-authentication. It does NOT demonstrate console access; no login
was attempted.

---

*Prepared by NuClide Research (Nicholas Kloster + Claude) · 2026-05-31*
