# Insight #81: The Docker Compose EHLO leak generalizes to a class of three MTAs (Haraka, Exim, Sendmail)

**Codified:** 2026-06-07. Lane 1B of the 9-item plan.
**Source survey:** `data/platform-intel/mta-fingerprint-catalog-2026-06-07.md` (6 MTAs probed; 4 live in docker, 2 source-characterized).
**Family:** `reference-haraka-docker-compose-leak` (parent observation), Insight #78 (shared deployment kit operator class exposure), Insight #65 (TLS cert dork selection bias).
**Falsifiability tier:** medium. Mechanism differs per MTA; the shared observable is the load-bearing claim. n=4 live + n=2 source-confirmed.

## The pattern

The Sluice Docker-Compose attribution leak (Haraka echoes `service.project_default` shorthand in its EHLO greeting because `connection.js:844` reverse-resolves the connecting client and includes the PTR) is not a Haraka quirk. It is one observable instance of a class behavior shared by at least three MTA families that all echo client-side reverse DNS in their EHLO response by default.

| MTA | Live EHLO sample (Docker default) | Mechanism |
|---|---|---|
| Haraka 3.1.5 | `Hello agitated_wiles.mtacat_default [172.18.0.6]` | `connection.js:844` reverse-resolves client, echoes PTR |
| Exim 4.92 | `Hello condescending_swartz.mtacat_default [172.18.0.6]` | default `smtp_banner` template includes `$sender_host_name` |
| Sendmail 8.17 | (source-confirmed) | the `$_` macro is reverse-DNS-of-client; default `pleased to meet you` wording embeds it |

Three MTAs from three different software families share one observable: the EHLO response leaks information about the *connecting client* (which, in a Docker Compose deployment, is another container in the same network and carries the Compose project name).

Two MTAs do NOT leak this:
- **Postfix 3.10**: echoes `$myhostname` only. Leaks server identity, not client identity. Different class.
- **OpenSMTPD 7.8**: echoes the *client-supplied* HELO argument verbatim. Inverse class: not an operator-attribution leak; a log-injection / banner-spoofing surface where the client controls server output.
- **qmail 1.03** (source-characterized): Bernstein-minimal banner with no version and no client ID. The absence is itself an attribution signal in 2026.

## Why this matters for dorking

The Haraka-specific class-marker (`mtacat_default` literal) catches one operator class. The class-level dork (`"_default" "Hello"` in Shodan SMTP banners) catches all three leaker families simultaneously. The class-level dork is strictly more useful than the per-MTA dork for operator-attribution work because:

1. It does not require fingerprinting the MTA first.
2. It surfaces operator deployment-platform information (Compose, Swarm, k8s shorthash) without distinguishing which MTA produced it.
3. The same false-positive set (operators who customized `smtp_banner` away from defaults) applies across all three.

## Why this matters for the auth-on-default thesis (Insight #40)

The MTA category is auth-irrelevant at the EHLO stage by design: SMTP banner exchange happens before any AUTH. So the leak is not an authentication failure. It is a deployment-attribution failure that surfaces in the protocol layer below auth. This is structurally similar to TLS-CN attribution surfaces (Insight #46): an information leak that does not break confidentiality but does break operator anonymity.

For NuClide methodology: when the population is MTAs, fingerprinting at the EHLO layer is high-yield AND auth-irrelevant. Verification of the leak itself is a one-shot HELO probe; verification of the *consequence* (correlating the leaked Compose name with the operator) is the harder step and lives at the attribution stage.

## How to apply

- When surveying email-adjacent AI infrastructure (Cat-33 AI-Email-Guardrails, agent-mail relays, transactional email gateways), include the class-level `"_default" "Hello"` dork alongside per-MTA dorks.
- When attributing a hardened operator's deployment topology, the EHLO response is the cheapest leak surface. It is checked passively via Shodan SMTP banners; no active probe needed.
- When writing a Cat-33-class disclosure, mention the leak explicitly. Operators with `_default` shorthashes in their SMTP banner are almost certainly running unmodified compose stacks, which is itself diagnostic of operational maturity.

## Side observations worth codifying as their own candidate insights

1. **OpenSMTPD verbatim-echo is an inverse log-injection surface.** A connecting client can choose its own HELO string, which the server echoes back into its own log lines. If the operator's log pipeline is unsanitized, the client can inject arbitrary log content. The attack class is "log-injection via EHLO echo." Worth its own candidate insight pending live confirmation that operator log pipelines are commonly downstream-unsanitized.
2. **qmail's absent banner is a 2026 attribution signal.** The dataset of internet-facing MTAs running qmail 1.03 (last release 1998) is now small enough that the absence of a vendor banner is itself a fingerprint. A Bernstein-minimal banner says "this operator runs a 28-year-old MTA on purpose." Worth its own candidate insight pending population sweep.
3. **Postfix server-identity leak.** Postfix echoes `$myhostname` only, but in a Docker default this is `<shorthash>.<network>`. Less rich than client-PTR but still leaks compose-network info. Worth folding into the class-level analysis if a sweep finds Postfix-on-Compose with default `$myhostname`.

## Data

- `~/AI-LLM-Infrastructure-OSINT/data/platform-intel/mta-fingerprint-catalog-2026-06-07.md` (full catalog with EHLO samples, regexes, mechanism notes)
- `reference-haraka-docker-compose-leak.md` (parent observation memory)
- Live probes: docker-compose isolated network, MTAs run as containers; banner captured via `swaks` or `telnet`.

## DCWF KSAT fit

- 672: T5904 (risk assessment via passive signal), K7044 (V&V via Docker isolation), K7054 (banner fingerprinting tool class).
- 733: T5882 (Responsible AI: this is operator-info leak, not user data; surface only).
- Overlap: K22 (SMTP protocol), K1158 (auth-adjacent surfaces), K7003 (AI infrastructure attack surface where MTA relays AI agent output).
