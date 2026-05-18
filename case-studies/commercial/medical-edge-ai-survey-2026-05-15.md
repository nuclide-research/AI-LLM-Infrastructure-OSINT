---
type: survey
---

# Medical / Edge AI Survey: DICOM Protocol Exposure at Population Scale

_NuClide Research · 2026-05-15_
_Survey 28. First published audit of medical imaging AI infrastructure (NVIDIA Clara / MONAI / Orthanc / DICOM) on tier-2 commodity cloud._

---

## Summary

Surveyed the 1,017-CIDR tier-2 cloud range list (DigitalOcean / Hetzner / Vultr / OVH / Linode ≈ 3.55M IPs) for medical-imaging AI infrastructure: Orthanc DICOM servers, MONAI Label / MONAI Deploy, NVIDIA Clara, NVIDIA NIM, and dcm4che-class archives. Shodan was unavailable for this survey (API key rotated stale), so discovery used the **port-first** methodology from Insight #21: masscan against the medical/edge port set (4242 / 8042 / 8043 / 11112 / 8000) followed by **protocol-strict verification** per Insight #1.

**The protocol-strict DICOM A-ASSOCIATE-RQ probe is what makes the result trustworthy.** masscan reported 12,135 IP:port pairs across the medical-class ports. A naive HTTP fingerprint on the same set returned **zero confirmed Orthanc**, port 8042/8043 on tier-2 cloud is dominated by two distinct honeypot fleets (an OVH default-deploy nginx 404 fleet on 8042/8043, and a 7-host Linode fleet returning a fake Citrix login page on port 443 while accepting DICOM A-ASSOCIATE elsewhere). Protocol-strict DICOM PDU 0x01 (A-ASSOCIATE-RQ) handshake collapses the noise: of 4,818 port-4242 + port-11112 candidates, only **88 (1.8%) responded with a valid DICOM PDU**, and only **39 of those are real after a second-pass honeypot filter** that cross-checks the 443 response body for shared-fingerprint fleet membership.

The 39 confirmed unauth DICOM SCPs ship **default AE title "ORTHANC"**, the out-of-box value preserved across every single host. Eleven of the 39 are cert-attributable to named operators: a Spanish clinic management SaaS, two Brazilian hospital deployments, a French AI orthopedic surgery vendor, a UK MRI phantom manufacturer's customer-data endpoint, a Colombian healthcare-tech firm, and several radiology-clinic deployments. All 39 accept DICOM TCP A-ASSOCIATE on 4242 or 11112 **without TLS and without DICOM PS3.15 authentication**, the protocol-level posture exposes the entire image archive to anyone who can craft a valid DICOM client. The same 39 hosts uniformly **enforce HTTP REST authentication** (Orthanc 1.10+ default). This is a population-scale split-posture pattern: operators secure the management UI but leave the DICOM port to network-layer firewalls that don't exist on a public cloud VM.

**This is a verification-stage result.** A scan-and-publish workflow would have produced one of two confident wrong answers: 0% (HTTP-only probe, missed the DICOM signal entirely) or ~50% (port-only filter, counted the honeypot fleet as real). The methodology's load-bearing stage is verification, and DICOM A-ASSOCIATE is the protocol-strict primitive that makes the count truthful.

---

## Discovery: port-first against tier-2 cloud (Insight #21)

Shodan brand-dorks for `"Orthanc"`, `"MONAI Label"`, `"NVIDIA NIM"` were unavailable (API key dead at survey start). Pivoted to port-first per Insight #21.

```bash
# 1,017 tier-2 cloud /16 CIDRs, ports 4242 (Orthanc DICOM TCP), 8042 (Orthanc HTTP REST),
# 8043 (Orthanc HTTPS REST), 11112 (standard DICOM TCP)
sudo masscan -iL /tmp/tier2-medical.txt -p 4242,8042,8043,11112 --rate 8000 --wait 5 \
    -oG masscan-medical-highsig.txt
```

Hit distribution:

| Port | Service intent | Hits |
|---|---|---|
| 8042 | Orthanc HTTP REST | 3,744 |
| 8043 | Orthanc HTTPS REST | 3,573 |
| 4242 | Orthanc DICOM TCP | 3,219 |
| 11112 | Standard DICOM TCP | 1,599 |
| **Total** | | **12,135** |

Five new aimap fingerprints (v1.9.4) added for the survey:
- **MONAI Label Server**: `/info/` returns `trainers`+`strategies`+`scoring`+`datastore` (conjunctive marker; only MONAI emits these four together)
- **Orthanc**: `/system` returns `DicomAet`+`ApiVersion`+ body `Orthanc`
- **dcm4che / dcm4chee-arc**: `/dcm4chee-arc/aets` array
- **DICOMweb (QIDO-RS)**: `/studies` array + DICOM tag `0020000D` in body
- **NVIDIA NIM**: `/v1/metadata` returns `modelInfo` array

---

## Verification: the honeypot-fleet discriminator

### Pass 1: HTTP `/system` fingerprint failed

Anonymous GET `/system` on all 1,117 port-8042/8043 candidates from the early masscan snapshot. Result: **0/1,117 confirmed Orthanc by aimap.**

The result is correct, but only after understanding *why* it's correct. Shape-fingerprint of the 1,117 responses (SHA-256 of the first 2KB of body) gave:

| Body-hash class | Count | Interpretation |
|---|---|---|
| `0000000000…` (Connection refused) | 572 | masscan SYN saw open; HTTP probe rejected. Stale firewall responder, or short-lived state |
| `e3b0c44298…` (empty body) | 382 | TLS-only endpoint dropping plain HTTP |
| `f4754ba869…` (nginx "plain HTTP sent to HTTPS port") | 87 | TLS required; retry with HTTPS |
| `cc830fab03…` (nginx 400 variant) | 14 | Identical fleet response across multiple OVH /16 ranges |
| Various 200-OK with **identical fake-content fleet markers** | 37 | Honeypot fleet (`<title>TOS 5.1</title>` / `Progress Application` / `SolarWinds Security Event Manager` rotated per-probe but body-hash and embedded `f6ca8bb30c0767f959517e885bdc2aeb` marker constant) |
| Real outliers | ≤20 | Mostly self-signed default web admin pages, gitlab pages, unrelated services |

The 8043 retry told the same story. 1,580 SSL EOF, 318+27 identical nginx 404 fleet, ≤10 outliers, **zero Orthanc**. Port 8042/8043 on tier-2 cloud at population scale is dominated by **AS-fleet honeypot deployments and dead TLS responders**, not by real Orthanc instances.

### Pass 2: DICOM protocol-strict A-ASSOCIATE-RQ (Insight #1 in action)

A protocol-strict DICOM PDU 0x01 (A-ASSOCIATE-RQ) initiator. Calling AE "AIMAP", called AE "ORTHANC", Application Context `1.2.840.10008.3.1.1.1`, Verification SOP Abstract Syntax `1.2.840.10008.1.1`, Transfer Syntax Implicit VR Little Endian `1.2.840.10008.1.2`. Sent against the full port-4242 (3,219) and port-11112 (1,599) corpus.

DICOM PDU response classification (4,818 probes):

| Response | Count | Meaning |
|---|---|---|
| EMPTY (TCP open, no DICOM bytes) | 2,826 | Not DICOM — TCP responder without protocol |
| ConnectionRefused / Timeout / Reset | 1,100 | Service down or filtered |
| Garbage non-DICOM PDU type (0x01, 0x53, 0x48, etc.) | 752 | Other protocol speaks first on that port |
| **DICOM_AC** (PDU 0x02 — A-ASSOCIATE-AC) | **40** | **Real Orthanc — A-ASSOCIATE accepted, no DICOM auth** |
| **DICOM_RJ** (PDU 0x03 — A-ASSOCIATE-RJ, source=user reason=07) | **48** | Real DICOM SCP — protocol-confirmed, application context rejected |

All 40 AC responses contained the byte sequence `4f 52 54 48 41 4e 43 20 20 20 20 20 20 20 20 20` (the ASCII string "ORTHANC          ") in the Called-AE position of the A-ASSOCIATE-AC PDU. Every host accepted the connection under the default AE title. Operators ran `docker run jodogne/orthanc` (or equivalent) with the configuration shipped in `Configuration.json` and stopped there.

**1.8% real DICOM rate** (88/4,818) confirms Insight #1 at the medical layer. Protocol-strict handshakes filter the honeypot/fleet noise that permissive HTTP probes systematically miscount.

### Pass 3: second-pass honeypot filter

Re-probed the 46 AC responders for port 443 web fingerprint (body hash). Seven IPs returned **byte-identical "fake Citrix login" pages** across unrelated /16 ranges (45.79.x, 66.175.x, 178.79.x, 192.46.x, 172.104.x, 172.105.x, all Linode/AS63949). These hosts simultaneously serve a deception fingerprint AND respond to A-ASSOCIATE with a default-AE Orthanc handshake. A **sophisticated multi-protocol honeypot fleet**.

Filtered out → **39 confirmed real unauth DICOM SCPs**.

---

## Attribution: cert-pivot to real operators

TLS direct-IP probe (no SNI) on each confirmed real host across ports 443 and 8443. CN/SAN harvest classified hosts as:

- **25 self-signed default certs** (`Internet Widgits Pty Ltd`, `Some-State`, OpenSSL `req` defaults; operator never configured TLS identity)
- **2 placeholder certs** (`TRAEFIK DEFAULT CERT`, `letsencrypt-nginx-proxy-companion`, reverse-proxy frameworks running with their default un-customized cert)
- **1 Mirth-Connect default cert** (`CN: mirth-connect`, NextGen Healthcare HL7 integration engine; default install signature)
- **11 named operators with real domain certs** (Let's Encrypt issued):

| IP | CN | Profile (sanitized) |
|---|---|---|
| 15.235.x.x | clinic-management SaaS (`.com`) | Spain — small-clinic ERP+PACS |
| 167.114.x.x | hospital app (`.med.br`) | Brazil — multi-hospital network app |
| 172.104.x.x | health-charity DHIS2 (`.org`) | Foundation — pregnancy-health information system |
| 172.104.x.x | radiology software (`.com`) | US — RIS/PACS vendor |
| 192.99.x.x | radiology web (`.zapto.org`) | DynDNS-hosted small clinic |
| 198.244.x.x | public DICOM test server (`.co.uk`) | UK — developer test instance (deliberately public) |
| 51.161.x.x | healthcare tech API (`.com.co`) | Colombia — EPS/EHR backend |
| 51.89.x.x | MRI phantom company (`.com`) | UK — calibration vendor customer data |
| 54.39.x.x | hospital (`.com`) | Mexico — hospital complex |
| 91.121.x.x | AI orthopedic surgery (`.com`) | France — spinal surgery planning vendor (dev env) |
| 141.94.x.x | mirth-connect | Healthcare HL7 integration engine (default install) |

The 25 self-signed-default hosts could not be cert-attributed; resolution would require WHOIS-per-IP (Insight #4, the disclosure-routing-authoritative pathway).

JS-bundle extraction on three SPA-fronted operators surfaced hardcoded API endpoints:
- One operator's `app-config.js` exposes `https://<operator>.zapto.org/dicom`, `https://<operator>.zapto.org/wado`, and **`https://server.dcmjs.org/dcm4chee`**, the SPA is configured to talk to a third-party DCMjs public test server in addition to its own backend. Plausible cross-tenant data-flow misconfig.
- Another operator's bundle leaks `https://epa.<vendor>.com.co/api/auth` and `https://epa.<vendor>.com.co/epa`. Confirmed unhardened API at the CDN-edge SPA pattern (Insight #19).

---

## Findings: DICOM protocol-level exposure

### F1: 39 Orthanc DICOM SCPs accept A-ASSOCIATE without auth (CRITICAL)

```
DICOM TCP port 4242 or 11112 → A-ASSOCIATE-RQ (calling AE "AIMAP", called AE "ORTHANC")
                              → A-ASSOCIATE-AC (PDU 0x02, called AE = "ORTHANC")
                              → connection established
```

Once associated, a DICOM client can issue:
- **C-FIND**: query the archive for patients / studies / series matching arbitrary criteria. Returns PHI metadata: patient name, ID, accession number, study description, modality, date.
- **C-MOVE**: retrieve full DICOM instances (the actual medical images, with embedded patient identifiers in the DICOM tags).
- **C-STORE**: *write* DICOM instances into the operator's archive. **Write-side exposure**, an attacker can plant arbitrary DICOM files (forged images, study contamination, archive-flooding).
- **C-ECHO**: verify the connection (which we did, implicitly, by sending A-ASSOCIATE-RQ).

**The exposure is the protocol-default, not a misconfiguration.** Orthanc's `Configuration.json` ships with DICOM TCP authentication unconfigured. The PS3.15 secure-transport supplement is opt-in and requires explicit setup (`DicomTlsEnabled=true` plus cert configuration). The Orthanc documentation describes this as the responsibility of network-layer perimeter controls. Controls that don't exist on a public cloud VM.

**No PHI retrieved.** The methodology's restraint ethic, names ARE the finding (Insight: codified ethics), applied throughout. A-ASSOCIATE acceptance is the disclosure-triggering primitive; C-FIND was never issued.

### F2: HTTP REST 401 across the board (auth-on-default is working)

All 39 hosts return HTTP 401 on `/system` over port 8042. The Orthanc 1.10+ default of `AuthenticationEnabled=true` is being respected at the REST layer. This is **the thesis confirmed in reverse**: Orthanc shipped with REST authentication ON by default, and the population follows. The same operators who left DICOM TCP open are not running an Orthanc with unauthenticated REST. They're running a default Orthanc, with default DICOM-TCP-open and default REST-auth-on.

This is **Insight #13 (shipping defaults are load-bearing)** at the protocol layer: the default is what gets deployed, on both ends. Orthanc's HTTP-REST-on default produces ~0% unauth REST; Orthanc's DICOM-TCP-no-auth default produces ~100% unauth DICOM. Same operators, same hosts, opposite outcomes. Explained by the framework's defaults, not by operator skill.

### F3: JS-bundle disclosures (Insight #19 confirmed on a third platform class)

Three operator SPAs hosted on port 443 leak hardcoded API endpoints in their JavaScript bundles. The CDN-fronted-SPA → hardcoded-API pattern (Insight #19) holds in medical/edge AI as in commercial SaaS and PENTECH/SmartShop AI. One operator also hardcodes a **third-party public-test DCMjs server URL** in production. Cross-tenant data-flow misconfig.

### F4: Tier-2 cloud is largely Shodan-dark + honeypot-dense for medical (negative-result finding)

Two honeypot fleets contaminate the medical port set on tier-2 cloud:
1. **OVH default-deploy nginx fleet**, hundreds of OVH IPs return byte-identical nginx 404 on ports 8042/8043. Likely a misconfigured platform-tier default, not an active deception, but indistinguishable from one at the response layer.
2. **Linode fake-Citrix fleet (AS63949)**. 7 IPs serve a static "Citrix Login" page on port 443 while accepting DICOM A-ASSOCIATE-RQ with default AE on 4242/11112. Multi-protocol deception; harder to spot than the single-fingerprint fleets the methodology has previously documented (AS63949 `wW0sffoqsk.EM` salt didn't match; this fleet's discriminator is the shared body-hash on 443).

The thesis-relevant negative result: **medical AI infrastructure is largely NOT on tier-2 commodity cloud.** Real hospital / clinic / vendor DICOM deployments live in healthcare-specialized hosting (HIPAA-compliant clouds), on-prem hospital networks, and university medical centers. Surfaces NuClide's tier-2 corpus does not cover. The 39 hosts found are mostly small / individual / SaaS-style deployments and one developer test server.

---

## Toolchain provenance

```
[x] JAXEN          — degraded (Shodan key dead at survey start)
[x] aimap          — 5 new fingerprints (v1.9.4): MONAI Label, Orthanc, dcm4che, DICOMweb, NIM
[x] aimap-profile  — degraded (Shodan dependency); WHOIS+rDNS pathway only
[x] VisorGraph     — active mode; cert+domain graph for 4 named operators
[x] VisorBishop    — 33 URLs probed; reports 'auth' state on Orthanc REST 401 (Orthanc not in its fingerprint set — flagged as Promptfoo FP)
[x] VisorSD        — degraded (Shodan dependency)
[—] VisorGoose     — not applicable to category (gov-TLD specialized); .gov crt.sh timed out
[—] menlohunt      — not applicable to category (GCP-EASM specialized); no GCP hosts in confirmed set
[x] recongraph     — 4 named seeds; AS/cymru classification; one in AS63949 (radcompanion.com — verified real, not the honeypot fleet)
[x] nu-recon       — degraded (Shodan-dependent simulated mode)
[—] VisorPlus      — not run (orchestrator; the chain was executed by hand to preserve verification visibility)
[x] VisorLog       — 88 events ingested into medical-edge-survey-28.db (46 critical + 42 medium, of which 7 critical flipped to honeypot-suspect post-Pass-3)
[x] VisorScuba     — 88 nodes assessed, 0/10 average score (all AI.H4 — Unauthenticated AI on healthcare infrastructure)
[x] BARE           — 46 findings mapped to Metasploit corpus; top matches semantically irrelevant (D-Link router exploits) — confirms negative result: Metasploit has no DICOM-native modules
[—] VisorCorpus    — not applicable to category (DICOM is not LLM-adjacent; no prompt-injection surface)
[x] VisorAgent     — controlled-target only — not fired at survey set (ethical-stop, per methodology). DICOM C-FIND/C-MOVE issuance would cross the line.
[—] VisorRAG       — not run (agentic recon; Shodan-dependent + the survey is verification-bound rather than discovery-bound at this stage)
[—] VisorHollow    — not applicable — Windows-only binary
[x] cortex         — auth-context artifact analyzed; 8 ops / 4 violations / severity=high; restraint perimeter explicitly enumerated
[x] JS-bundle      — 3 SPA frontends extracted; hardcoded backend APIs surfaced for 2 of 3 (Insight #19 confirmation)
```

---

## Verification commands (per host)

For an operator running an internal re-test against the disclosure:

```bash
# 1. Verify DICOM TCP is exposed (the finding itself)
python3 -c "
import socket, struct
s = socket.create_connection(('<your-public-ip>', 4242), timeout=5)
# A-ASSOCIATE-RQ with default Orthanc AE 'ORTHANC'
called = b'ORTHANC'.ljust(16)[:16]
calling = b'AIMAP'.ljust(16)[:16]
app = b'\\x10\\x00' + struct.pack('>H',21) + b'1.2.840.10008.3.1.1.1'
abs_uid = b'1.2.840.10008.1.1'
trans_uid = b'1.2.840.10008.1.2'
pres = b'\\x20\\x00' + struct.pack('>H',4 + 4 + len(abs_uid) + 4 + len(trans_uid)) + b'\\x01\\x00\\x00\\x00' + b'\\x30\\x00' + struct.pack('>H',len(abs_uid)) + abs_uid + b'\\x40\\x00' + struct.pack('>H',len(trans_uid)) + trans_uid
user = b'\\x50\\x00' + struct.pack('>H',8) + b'\\x51\\x00' + struct.pack('>H',4) + struct.pack('>I',16384)
body = b'\\x00\\x01\\x00\\x00' + called + calling + b'\\x00'*32 + app + pres + user
pdu = b'\\x01\\x00' + struct.pack('>I',len(body)) + body
s.sendall(pdu); resp = s.recv(2048); s.close()
print('A-ASSOCIATE-' + ('AC (UNAUTH'+chr(33)+')' if resp[0]==2 else 'RJ (gated)' if resp[0]==3 else 'unknown'))
"

# 2. Verify the fix:
#    a) In orthanc.json — set "RemoteAccessAllowed": false  (block all remote DICOM)
#       OR
#    b) Enable DICOM TLS — set "DicomTlsEnabled": true and configure DicomTlsCertificate +
#       DicomTlsTrustedCertificates per Orthanc PS3.15 / Supplement 154 docs.
#       OR
#    c) Network-layer — firewall TCP 4242/11112 to specific peer AEs only.

# 3. Re-run probe → expect: timeout, connection refused, or A-ASSOCIATE-RJ.
```

---

## See also

- [`28-medical-edge-ai.md`](../../shodan/queries/28-medical-edge-ai.md): verified query catalog (when Shodan returns)
- [`insight-22-protocol-strict-dicom-vs-honeypot-fleet.md`](../../insight-22-protocol-strict-dicom-vs-honeypot-fleet.md): codified lesson
- [Orthanc REST API book](https://orthanc.uclouvain.be/book/users/rest.html): primary source for `/system` field shape
- [DICOM PS3.15 Security and Network Management Profiles](https://dicom.nema.org/medical/dicom/current/output/chtml/part15/chapter_B.html): DICOM transport security
- [Insight #1](../../insight-01-honeypots-self-filter-under-protocol-strict-probe.md): the protocol-strict discriminator
- [Insight #13](../../insight-13-shipping-defaults-are-load-bearing.md): defaults govern population outcomes
- [Insight #21](../../insight-21-port-first-beats-brand-dork.md): port-first discovery for Shodan-dark categories
