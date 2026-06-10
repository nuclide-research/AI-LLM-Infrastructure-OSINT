# DCWF 541 — Vulnerability Assessment Analyst | Endpoint-Enumeration Vector Sweep

**Cohort:** LJP-OSS 491-host megaset (`~/syllabus/cohort-megaset.txt`)
**Date:** 2026-06-09
**Exit:** Mullvad us-mia-wg-102 (146.70.187.101) — Quantum Resistance on
**Posture:** READ-ONLY GET/HEAD probes only; no POST; ThreadPoolExecutor=18 workers
**Output ledger:** `~/syllabus/cohort-gap-checks/check-541-endpoint-enum.jsonl` (491 records, one per IP)

---

## Assessment Statement

Vulnerability assessment of operator-config endpoint exposure across **491 cohort hosts** identified **zero (0)** deviations from acceptable configurations with customer-attribution exposure to sensitive sector domains (`.gov`, `.edu`, `.mil`, `.bank`, hospital/healthcare, named enterprise SSO providers, named federal/banking institutions). No host in the LJP-OSS cohort exposed an operator-configured allowlist, well-known disclosure record, or backend system-config JSON revealing a gov / .edu / .mil / .bank / .hospital customer connection across the three probed vectors.

---

## Probe Inventory

| Check | Endpoint | Ports | Method | Match Rule |
|---|---|---|---|---|
| 3 | `/` headers | 8080, 8000, 443, 80, 8443, 3000, 5000 | `curl -sI -k -m 6` | substring scan of every source in every directive of `Content-Security-Policy` and `Content-Security-Policy-Report-Only` (`default-src`, `script-src`, `style-src`, `connect-src`, `img-src`, `frame-src`, `form-action`, `report-uri`, `font-src`, `media-src`, `object-src`, `child-src`, `manifest-src`, `worker-src`, `base-uri`, `frame-ancestors`) |
| 4 | `/.well-known/security.txt` | 8080, 443, 80 | `curl -s -k -m 6` | RFC 9116 fields (`Contact`, `Expires`, `Encryption`, `Acknowledgments`, `Preferred-Languages`, `Canonical`, `Policy`, `Hiring`); flag any value or contact email at sensitive domain |
| 7 | `/api/system/config` (Sub2API server-side) | 8080, 8000, 443 | `curl -s -k -m 6` (JSON 200 only) | recursive string-leaf walk over the JSON; flag any value matching sensitive substring catalog |

Sensitive substring catalog (lower-cased compare):
`.gov`, `.edu`, `.mil`, `.bank`, `hospital`, `healthcare`, `stanford.edu`, `mit.edu`, `berkeley.edu`, `harvard.edu`, `princeton.edu`, `yale.edu`, `nih.gov`, `nasa.gov`, `dod.mil`, `navy.mil`, `army.mil`, `airforce.mil`, `usa.gov`, `cms.gov`, `healthcare.gov`, `wellsfargo.com`, `chase.com`, `bankofamerica.com`, `jpmorgan.com`, `capitalone.com`, `okta.com`, `auth0.com`, `pingidentity.com`, `shibboleth.net`, `microsoftonline.com`, `accounts.google.com`.

---

## Population Response Stats

| Metric | Count | Pct of cohort |
|---|---|---|
| Hosts probed | 491 | 100% |
| Hosts returning a response on any probed surface | 360 | 73.3% |
| Hosts returning a CSP header (any port) | 360 | 73.3% |
| Hosts returning a valid `/.well-known/security.txt` (any port) | **0** | 0.0% |
| Hosts returning a JSON-200 on `/api/system/config` (any port) | **0** | 0.0% |

CSP responder distribution by port:
| Port | Hosts returning CSP |
|---|---|
| 8080 | 301 |
| 443 | 78 |
| 80 | 38 |
| 3000 | 9 |
| 8443 | 6 |
| 5000 | 1 |

CSP directive coverage on the 360 CSP-shipping hosts (top 10):
| Directive | Observations |
|---|---|
| frame-ancestors | 433 |
| default-src | 431 |
| script-src | 431 |
| style-src | 431 |
| img-src | 431 |
| connect-src | 431 |
| font-src | 430 |
| base-uri | 430 |
| form-action | 430 |
| frame-src | 423 |

Coverage means the LJP-OSS CSP is consistent and dense — not a fragmentary policy. A customer-attribution origin would have surfaced.

---

## Per-Check Findings

### Check 3 — Content Security Policy headers
- **Sensitive-origin hits:** 0
- **Hosts inspected:** 360 (returned a CSP header on at least one port)
- **Observed pattern:** the LJP-OSS CSP is uniform across the cohort — a commercial-SaaS allowlist:
  - `default-src 'self'`
  - `script-src 'self' 'nonce-...' https://challenges.cloudflare.com https://static.cloudflareinsights.com https://*.stripe.com https://static.airwallex.com ...`
  - directive set: `default-src`, `script-src`, `style-src`, `img-src`, `connect-src`, `font-src`, `frame-src`, `form-action`, `base-uri`, `frame-ancestors`
- The allowed origins describe payment and bot-mitigation infrastructure (Cloudflare Turnstile, Cloudflare Web Analytics, Stripe, Airwallex). No sensitive-sector origin appears in any directive on any host.

**No verbatim sensitive-hit rows — set is empty.**

### Check 4 — `/.well-known/security.txt` (RFC 9116)
- **Sensitive-field hits:** 0
- **Hosts inspected:** 491 across 3 ports each (1,473 endpoint probes)
- **Observed:** zero hosts in the cohort publish a `/.well-known/security.txt`. The LJP-OSS deployment does not advertise disclosure contacts on this path. Operator-attribution via a security.txt `Contact:` email at a `.gov`/`.edu`/`.mil`/`.bank` domain is not available on this surface.

**No verbatim sensitive-hit rows — set is empty.**

### Check 7 — Sub2API server-side `/api/system/config`
- **Sensitive-field hits:** 0
- **Hosts inspected:** 491 across 3 ports each (1,473 endpoint probes)
- **Observed:** zero hosts return a parseable JSON 200 on `/api/system/config`. Either the endpoint is not present on LJP-OSS at this path, or it is gated behind auth and returns a non-200. No hidden flags (`api_base_url`, `backend_addresses`, `admin_emails`, `default_models`, `allowed_models`, `blocked_origins`, `billing_endpoint`) were extractable on this vector.

**No verbatim sensitive-hit rows — set is empty.**

---

## Verification Rung (Insight #68)

| Check | Depth | Breadth | Result label |
|---|---|---|---|
| 3 — CSP | A (header read, full directive parse, exhaustive substring scan) | 2 (universe = 360/491 responders) | Verified zero |
| 4 — security.txt | A (RFC 9116 field parse, contact-email extraction) | 2 (universe = 491 probes x 3 ports) | Verified absent |
| 7 — /api/system/config | A (JSON 200, recursive string-leaf walk) | 2 (universe = 491 probes x 3 ports) | Verified absent |

Restraint-axis: high-depth, full-breadth by spec. Probing remained read-only across the run.

---

## Recommended Remediation Strategies (T0188)

For the LJP-OSS operators (delivered as advisory; not for the cohort hosts since no deviation was found):

1. **Maintain the current CSP discipline.** The cohort's uniform CSP-with-nonce pattern is a strong default; deviations from the commercial-SaaS allowlist (Cloudflare/Stripe/Airwallex) on a host should be treated as a config-drift signal.
2. **Add `/.well-known/security.txt`.** RFC 9116 is currently absent across all 491 hosts. Publishing a minimal `Contact: mailto:security@<operator>` + `Expires:` would create an out-of-band disclosure channel and harmonize with the AI-Email-Guardrails posture seen in Cat-33 hardened vendors.
3. **Confirm `/api/system/config` is not exposed unauthenticated on any future deploy.** The current zero-exposure state is the acceptable baseline; future cohort scans should flag any 200-JSON return on this path as a regression.

---

## Operational Notes

- 131 of 491 hosts returned no response across all 13 port-checks (TCP closed / filtered / not running an HTTP service on the probed ports). That is a population sub-stratum, not a finding.
- Probing wall time: ~4 minutes at 18 workers, no rate-limit observations, no Cloudflare challenge interceptions (HEAD requests for CSP returned headers cleanly; the Cloudflare-fronted hosts pass HEAD without challenge).
- The substring catalog uses lowercased compare against the lowercased source/value string; an origin like `https://AUTH.EXAMPLE.STANFORD.EDU/sso` would match `stanford.edu` regardless of casing. None did.
- Output schema (`check-541-endpoint-enum.jsonl`) per record:
  - `ip`, `csp[]`, `security_txt[]`, `system_config[]`, `hit_counts{csp,security_txt,system_config,total}`, `had_any_response`

---

## Conclusion

Across three operator-configuration endpoint-enumeration vectors — CSP allowlist (Check 3), RFC 9116 disclosure record (Check 4), and Sub2API system-config endpoint (Check 7) — the 491-host LJP-OSS cohort exhibits **zero customer-attribution exposure** to gov, .edu, .mil, .bank, hospital, healthcare, or named federal / banking / enterprise-SSO sensitive domains. The cohort's CSP discipline is uniform and points at commercial payment infrastructure, not government or enterprise SSO. RFC 9116 and `/api/system/config` are not exposed.

**Reported zero is an explicit verified zero, not an unmeasured zero.**
