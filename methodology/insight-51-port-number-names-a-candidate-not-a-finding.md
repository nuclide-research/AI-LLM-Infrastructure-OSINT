---
type: methodology
insight_number: 51
title: "A port number names a candidate, not a finding"
---

# Insight #51 — A port number names a candidate, not a finding

**Codified:** 2026-05-21 (global university LLM-exposure map, service-verification pass)
**Family:** Insight #25 (auth-on-default thesis), Insight #16 (no status code is identity). This is the population-scale measurement of the METHODOLOGY's load-bearing claim that verification, not scanning, produces findings.
**Falsifiability tier:** high. A single counter-sweep with a materially higher true-positive rate breaks it.

---

## The pattern

A perimeter scanner that derives finding **severity** from a **port number** produces confident, reproducible, wrong CRITICALs. The port number names a candidate ("something here might be Redis"). It is not a finding. Severity is earned only by speaking the protocol.

Stated empirically, with the source case:

`menlohunt`'s phase-1 `port_open` check did a bare TCP connect to each of 28 known ports and emitted a finding at the port's static table severity. Port 6379 scored CRITICAL, 8888 CRITICAL, 9200 CRITICAL, 3306 HIGH, 5000 HIGH, and so on. A connect that completes was labelled by the port number alone.

Across 722 university hosts the scanner emitted **113 CRITICAL/HIGH `port_open` findings** on 47 hosts. `svc-verify.py` then ran one read-only protocol handshake per candidate (Redis PING, MongoDB OP_MSG isMaster, Elasticsearch `GET /`, MySQL greeting parse, PostgreSQL StartupMessage, TDS PRELOGIN, Docker `/version`, kubelet `/pods`, and the rest). It resolved the **74 unique host:port candidates** that fell on verifiable service ports:

| Verified state | Count | A finding? |
|---|---|---|
| VERIFIED_UNAUTH | **1** | yes, one genuine exposure |
| VERIFIED_AUTH | 14 | no, real service with auth enforced (the control works) |
| VERSION_DISCLOSED | 3 | LOW, a version banner, not an exposure |
| REFUTED | 12 | no, the port does not run the guessed service at all |
| FILTERED | 42 | no, no protocol response (34 of them on 2 phantom hosts) |
| ERROR | 2 | no |

One of 74 port-number CRITICAL/HIGH candidates was a real unauthenticated exposure: an unauthenticated Redis 7.4.9 at a National Taiwan University host. The precision of a port-number CRITICAL/HIGH label for "unauthenticated exposure" on this sample is **about 1.4%**.

The verifier is not a refute-everything tool. It surfaced the one real finding and assigned it HIGH from a verified `PING -> +PONG` with no AUTH. Severity tracked the evidence in both directions.

## The failure taxonomy

The 73 non-findings fail for four distinct reasons. Each is a different way a port-number guess goes wrong.

1. **Properly secured (14, about 19%).** Real Jupyter, Elasticsearch, PostgreSQL and Docker daemons with auth enforced. The port number was right and the CRITICAL was wrong. A secured service is not a finding.
2. **Version-only (3, about 4%).** MySQL servers disclosing a version banner pre-auth. Real, but LOW. Information disclosure, not access.
3. **Wrong service entirely (12, about 16%).** The port does not run the guessed service. Port 5000 ("Docker Registry HIGH") was, on different hosts, an nginx server, a Flask/Werkzeug dev server, a plain 404, and three times an Apple AirPlay receiver (`Server: AirTunes/920.10.1`). Port 9000 ("MinIO") was a generic HTTP 400/200. Port 27017 was a honeypot mimicking MongoDB. Developer-convenience ports (5000, 8000, 9000) are the most overloaded and the least predictable from the number alone.
4. **Phantom hosts (about 44, 57%).** Two hosts completed the TCP handshake on every port probed and answered no protocol. A firewall or load balancer that SYN-ACKs everything turns one host into roughly 17 bogus CRITICALs. Two such hosts produced 34 of the 74 candidates.

## Mechanism

A bare TCP connect verifies exactly one thing: a TCP stack accepted the connection. It does not verify that the service behind the port is the one the number conventionally implies (taxonomy class 3), that the service is unauthenticated (class 1), or that there is any service at all rather than a firewall answering for the host (class 4).

The port-to-severity table conflates two different statements. "This port, if it runs an unauthenticated X, would be CRITICAL" is a triage priority. "This finding is CRITICAL" is a claim about evidence in hand. A scanner that prints the first as the second is wrong at population scale, and not randomly wrong. It is systematically wrong, because the same table produces the same inflated label on every run.

## What this insight is NOT

- NOT "scanning is useless." The port scan is the correct first stage. It produced the 74 candidates that were worth verifying. The error is in the severity label, not the discovery.
- NOT "port-number severity is always wrong." It was about 1.4% right on this sample. The claim is near-zero precision, not zero.
- NOT specific to menlohunt. Any scanner with a port-to-severity table has this failure mode. menlohunt is simply the one whose output was measured and then fixed.
- NOT a claim that the 73 non-findings are all safe. FILTERED means unverified, not secure. The claim is only that none of them were verified exposures.

## Falsification conditions

The insight is wrong if:

1. A verification sweep of port-number CRITICAL/HIGH candidates on a comparable population returns a materially higher true-positive rate, say above 10%.
2. The wrong-service and phantom classes turn out to be artifacts of this corpus (university networks) and do not appear in a commercial-host population.

## The scanner-design corollary, and the fix

The fix is not "verify harder." It is structural. A scanner must not assign finding-severity from a port number. A `port_open` finding is INFO. It reports a fact: a port accepted a connection. Severity is assigned downstream by the protocol-verification stage, or not at all.

Codified into menlohunt, commit `63b8bf1` (2026-05-21):

- `port_open` severity is now always `INFO`.
- The port-table severity field `portDef.sev` was renamed `portDef.potentialSev`. It is a probe-priority hint. The rename stops it being wired back into a finding severity by reflex.
- `risk.go` already excludes INFO findings from attack-chain detection, so the downgrade also stops bare open ports from forming phantom attack chains. A host with three "CRITICAL" open ports no longer auto-generates a chain over threshold.

`svc-verify.py` is the verification stage that resolves the legacy inflated findings. The menlohunt change stops new ones being born inflated. The loop is closed.

## Methodology impact

- This is the empirical quantification of the METHODOLOGY's load-bearing claim that a scanner produces candidates and verification produces findings. The claim now carries a number: a port-number CRITICAL is about 1.4% precise.
- Verification severity must be earned in both directions. The verifier that downgrades 73 false CRITICALs is the same verifier that must promote the one real exposure to HIGH. A tool that only ever refutes is miscalibrated.
- Phantom-host detection (a host with at least 4 probed ports and 0 protocol responses) is a cheap, high-yield pre-filter. It accounted for 57% of the candidate noise on this sample.

## Cross-references

- **Insight #25** auth-on-default thesis. The 14 VERIFIED_AUTH outcomes and the 1-in-74 finding rate are direct supporting evidence.
- **Insight #16** no status code is identity. Same family: a signal short of a protocol handshake (a status code there, a port number here) is not identification.
- **METHODOLOGY.md** verification is the load-bearing stage; most prior insights are verification-stage failures. Insight #51 is the population-scale measurement of that stage.

## Source data

- Verifier: `~/recon/svc-verify.py`
- Result set: `~/recon/global-university-llm-map/results/univ-llm-2026-05-hosts/svc-verify-results.json` (74 candidates, 722 menlohunt scans)
- The one finding: 140.112.107.222:6379, Redis 7.4.9, unauthenticated (`PING -> +PONG`, no AUTH). National Taiwan University.
- menlohunt fix: commit `63b8bf1`, github.com/Nicholas-Kloster/menlohunt

---

*Codified by Nuclide Research (Nicholas Kloster + Claude) 2026-05-21 from the global university LLM-exposure map service-verification pass. Methodology per `~/.claude/nuclide-internal/METHODOLOGY.md`.*
