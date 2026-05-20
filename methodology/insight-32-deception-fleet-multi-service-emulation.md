---
type: methodology
insight_number: 32
title: Multi-service deception fleets emulate target-specific services for Shodan scanners; filter on body markers, not title
---

# Insight #32. Multi-service deception fleets emulate target-specific services

_Source: Jetson/TensorRT-edge population survey, 2026-05-18. Two distinct deception
fleets surfaced in one survey: 22 hosts emulating Triton, 576 hosts emulating Shinobi.
Distinct from the AS63949 Linode honeypot fleet documented in Insight #1's source case._

## The rule

For every Shodan title-anchored dork in our methodology, **assume a multi-service
deception fleet is mixed into the result set**. The fleet operators emulate
target-specific services at Shodan crawl time by rotating titles per request,
while the response body carries one consistent marker (e.g., GitLab `og:site_name`
meta tags + ~137KB rotating-title pages). Filter on body markers and response
size, not Shodan title alone.

These fleets are operationally distinct from honeypot fleets like AS63949
(which emulates target services consistently). Deception fleets serve different
fake titles per request, designed to match many different scanner dorks
simultaneously. One host can therefore appear in dorks for unrelated products.

## Empirical basis (this survey, 2026-05-18)

Two fleets surfaced as separate Stage 2 verify outputs:

### Fleet A. Triton / Icecast pattern
- 27 hosts matched `"Server: Triton" port:8000` dork on Shodan
- All 27 had **byte-identical 92-byte Shodan-cached responses**: `HTTP/1.1 200 OK\nServer: Triton\nContent-Type: application/json\nContent-Length: 92` (identical content length across geographically/AS-diverse IPs is the fleet fingerprint)
- 22 currently return `Server: Icecast 2.4.4` with empty body on every `/v2/*` path (5 unreachable)
- **0 host runs actual NVIDIA Triton Inference Server**
- ASN distribution: Linode (multiple), Leaseweb, **STARK INDUSTRIES SOLUTIONS LTD ×3 (UA/HU/AL, bulletproof hosting)**, Oracle Svenska, Reliable Communications, Webhorizon, others. Not concentrated to a single ASN.

### Fleet B. Shinobi / GitLab rotating-title pattern
- 1,926 unique IP:port candidates matched `http.title:"Shinobi"` dork
- **576 hosts (30%)** serve rotating fake titles per request: `TamasiPHNAS`, `Cisco Codec`, `Acorn Management`, `wiportal-mobile`, `BigAnt Admin`, `Laravel`, `Shinobi` (the dork-matching title), and others
- Body consistently contains GitLab markers: `og:site_name="GitLab"`, `og:type="object"`
- Response size ~137KB per page
- Heavy Aliyun CN concentration (`101.200.0.0/16` range)

### Real Shinobi (anchored on body marker, not title)
- 361 hosts pass the body-marker check (`shinobi` in body, no `gitlab` markers)
- Distinguishable from fleet B by response size (~10KB vs ~137KB) and absence of GitLab markers

## Diagnostic signals

A host belongs to a multi-service deception fleet if **any** of these fire:

1. **Body marker mismatch with title.** Title says product X (e.g., Shinobi), body carries marker for unrelated product Y (e.g., GitLab `og:site_name`).
2. **Rotating titles.** Repeated GET / requests against the same host return different titles (the fleet picks from a pool to maximize Shodan-dork match coverage).
3. **Identical content length across diverse IPs.** Fleet B serves 137KB pages from many ASNs; Fleet A served byte-identical 92-byte responses across 27 ASN-diverse IPs.
4. **Generic / oversize response on every path.** Real platforms return distinct content per route; deception fleets often return the same 100KB+ blob on every path including obviously non-existent ones.
5. **Server-header rotation.** Fleet A's hosts moved from `Server: Triton` (Shodan crawl) to `Server: Icecast 2.4.4` (today). Server header is a settable string; rotating it is part of the deception pattern.

## Procedural rules this insight generates

1. **Stage 2 verify probes must check body markers separately from title.** A Shodan-matched title is necessary but not sufficient. The probe must inspect the response body for the expected platform's marker and the absence of unexpected-platform markers.

2. **Reject deception-fleet hosts before classification.** Add an explicit `deception_fleet_*` verdict to every verify-probe classifier. Hosts with GitLab markers + rotating titles + ~137KB responses are flagged; they are not the target platform.

3. **Cross-survey re-check.** Past harvests (2026-05 surveys especially: Triton, Frigate, Shinobi, OpenHands, Ollama, LLM-gateways) should be re-verified against this signature. Real findings remain real; deception-fleet hosts get retroactively reclassified.

4. **Stage 0 dork construction stays the same**. Title-anchored dorks are still the right entry point. The protection happens at Stage 2.

5. **Build the fleet-filter into aimap.** The deception-fleet signature (body-marker mismatch + size + title rotation) should be a first-class aimap response-shape conjunct, available to every fingerprint as a negative filter (`body_not_contains: gitlab`, `response_size_max: 50000` for platforms that should be small).

## Relationship to prior insights

- **Insight #1 (protocol-strict probing self-filters honeypots/deception fleets)**: validates the underlying principle. Insight #32 documents a new, larger fleet that exercises the same rule.
- **Insight #6 (conjunctive marker-anchored matchers)**: the response-shape conjuncts already in #6 are the right defense; this insight makes the conjunct rule mandatory for title-only dorks across all platform classes.
- **Insight #15 (~50% real-rate on raw dorks)**: the Shinobi class real-rate is well below 50% (361 real / 1,926 candidates = 18.7%); the deception fleet drags real-rate down. Surveys should now report "real-rate after deception-fleet filter" as a separate metric.

## Open questions

- **How many other platform classes does this fleet emulate?** Today's survey caught it on Triton and Shinobi. Random sampling of the fleet's rotating-title pool (TamasiPHNAS, Cisco Codec, Acorn Management, wiportal-mobile, BigAnt Admin, Laravel, GitLab) suggests it can match dorks for IP cameras, NVR systems, ERP, GitLab, and PHP applications.

- **Is there one fleet operator or many?** Fleet A and Fleet B have different signatures (size, Server header rotation pattern). They may be different fleets sharing technique, or one fleet with multiple emulation modes.

- **Why Aliyun 101.200.0.0/16 concentration?** Fleet B has heavy Aliyun heritage. The deception infrastructure may be deployed on Chinese cloud for cost reasons, or operated by a Chinese-cloud-customer entity.

- **Are these defensive (canary) or offensive (data poisoning)?** Defensive: catch reconnaissance traffic for honeypot-style alerting. Offensive: poison public-internet research datasets that train scanner-result classifiers. The motive is not yet clear.

## See also

- `case-studies/commercial/jetson-tensorrt-edge-survey-2026-05-18.md`. The source survey.
- `insight-01-protocol-strict-self-filters-honeypots.md`. The family this insight extends.
- `reference_as63949_honeypot_fleet.md` (memory). The AS63949 Linode fleet, distinct from today's findings.
