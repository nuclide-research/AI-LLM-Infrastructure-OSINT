---
title: "Protocol-strict handshakes are the only verifier for multi-protocol honeypot fleets"
insight_number: 22
date: 2026-05-15
tags:
  - methodology
  - verification
  - honeypot-discrimination
  - dicom
  - medical-ai
  - protocol-strict
related_research:
  - case-studies/commercial/medical-edge-ai-survey-2026-05-15.md
source: case-studies/commercial/medical-edge-ai-survey-2026-05-15.md
related_insights:
  - insight-01-honeypots-self-filter-under-protocol-strict-probe
  - insight-13-shipping-defaults-are-load-bearing
  - insight-15-dork-hits-vs-platform-instances
---

# Methodology Insight #22: Protocol-strict handshakes are the only verifier for multi-protocol honeypot fleets

## The insight

Insight #1 established that protocol-strict handshakes filter honeypots:
an exact JSON-RPC `initialize` envelope dropped AS63949 Linode honeypot
pollution from 91.6% to 1.1% in the MCP survey. The medical/edge AI
survey extends this, and surfaces the second-order pattern: **modern
honeypot fleets present multiple service identities simultaneously,
and the cross-fingerprint shape collision is the discriminator that
catches them.**

The Pass-1 single-protocol filter (DICOM A-ASSOCIATE-RQ) confirmed 46
hosts as protocol-correct DICOM SCPs by their PDU 0x02 response,
including the default Orthanc AE title byte sequence `ORTHANC` in the
Called-AE position. Every layer of the DICOM protocol responded
correctly: PDU type, length, protocol version, AE title field, user
information sub-item. By the single-protocol-strict standard, **these
were real Orthanc deployments**.

Pass 2. A separate HTTP fingerprint on port 443 of the same hosts
revealed that 7 of the 46 returned a **byte-identical fake "Citrix
Login" HTML page across unrelated /16 ranges**. The same fleet that
emits a protocol-correct DICOM A-ASSOCIATE-AC also serves a static
deception page on a different port. Without the second-pass check, the
DICOM probe alone would have classified these as legitimate, and a
disclosure based on that count would have been wrong by 15% (7/46).

The lesson: **a single protocol-strict handshake is necessary but not
sufficient. Population-scale verification requires cross-fingerprint
consistency: the host's response on the target protocol must agree with
its response on adjacent ports.** Honeypot fleets are converging toward
multi-protocol authenticity (the DICOM SCP layer they emitted was
*correct*, they implement the protocol). The discriminator is not
protocol-correctness; it is the inconsistency between a "real-looking"
target-protocol response and the host's posture on the rest of its
attack surface.

## What the discriminator looks like

For the medical/edge fleet:

1. **Target-protocol probe**: DICOM A-ASSOCIATE-RQ → AC with `ORTHANC` AE.
   Looks real.
2. **Adjacent-port shape hash**: port 443 body SHA-256 collides across
   7 unrelated IPs in 6 different /16 prefixes.
3. **Adjacent-port content**: every collided IP serves `<title>Citrix
   Login</title>` with the *same form structure, same field IDs, same
   button class names*. The same HTML, the same byte sequence.

A single real Orthanc operator's port 443 might be:
- A Let's Encrypt-issued cert + a React SPA (10 of the 39 real hosts)
- An OpenSSL self-signed default cert + an empty/minimal response (15
  of the 39 real hosts. DICOM-only deployments, no web UI configured)
- A real hospital/clinic web portal (the SPA-front pattern; 5 of the
  39 real hosts)

None of these legitimate variants produce byte-identical responses
across multiple IPs. The honeypot fleet's adjacent-port collision is
the falsifying observation.

## What this means operationally

Every population survey now needs **two protocol-strict probes in
disagreement-mode**:

1. The target-protocol fingerprint (e.g. DICOM A-ASSOCIATE for medical;
   JSON-RPC `initialize` for MCP; a deep platform-specific endpoint).
2. An **adjacent-port shape hash** on the same host, against the most
   web-default port (80/443/8080/8443). Hash the body, tally across
   the survey corpus, flag the most common-shape clusters with >5
   members as deception-suspects.

The second check costs ~one extra HTTP request per host. It catches
the fleet pattern that single-protocol verification cannot.

This is **the second-derivative of Insight #1**. Insight #1 said
honeypots self-filter under protocol-strict probes. Insight #22 says:
when the honeypot also passes the protocol-strict probe, the
discriminator moves up a layer. The inconsistency *between* its
protocol identities is the signal.

## Adjacent honeypot family: already documented

The case study also identified an OVH `nginx-404` default-fleet
pattern: hundreds of OVH IPs in the survey corpus returned byte-
identical nginx 404 on ports 8042/8043. This is the same family but at
a different scale. *cloud-provider-tier deception or default-deploy
artifact*. Distinguishing "deliberate deception fleet" from "lazy
default-deploy fleet" is not load-bearing for the count; for the count
to be correct, both must be filtered out. The shape-hash discriminator
filters both the same way.

## Numbers

- **Survey corpus**: 4,818 port-4242 + port-11112 candidates from
  masscan against the 1,017-CIDR tier-2 cloud range list.
- **Pass-1 (DICOM A-ASSOCIATE-RQ)**: 88 protocol-correct DICOM SCPs
  (40 AC + 48 RJ). 1.8% real rate of the masscan candidate pool.
  Consistent with Insight #1's prediction.
- **Pass-2 (port-443 shape-hash)**: 7 of the 46 AC responders share a
  `<title>Citrix Login</title>` fake-fingerprint body hash across 6
  unrelated /16 prefixes. Flagged as honeypot-fleet contamination.
- **Final real population**: 39 confirmed unauth DICOM SCPs.

The 15% (7/46) honeypot rate that Pass-2 catches is the magnitude of
the count-correction; without Pass-2, the published number would have
been 46 instead of 39.

## Other places this generalizes

Any platform with a deep protocol surface that diverges from its web
fingerprint:

- **MCP servers**: JSON-RPC `initialize` strict probe (Insight #1) +
  adjacent web fingerprint shape-hash. The MCP survey already runs
  step 1; step 2 is the natural extension.
- **gRPC services**: protocol-strict gRPC reflection probe + adjacent
  HTTP/2 fingerprint.
- **Database protocols**: protocol-strict Postgres/MySQL/MongoDB
  handshake (auth-required-or-not) + adjacent web admin UI shape.
- **Modbus / S7 / DNP3**: ICS protocols have well-defined function
  codes that honeypots often half-implement; a function-code-strict
  probe + adjacent HTTP fingerprint is the same pattern, transposed.

The general form: **a real production deployment has a coherent
identity across its surface. A honeypot deployment optimizes per
fingerprint and accumulates inconsistencies between them. The
inconsistency IS the discriminator.**
