# Insight #73 — Header-versioned APIs are invisible to header-less fingerprinters

_Sourced to: the Data Labeling & Annotation survey, 2026-05-31 (CVAT detection miss)._

## The lesson

A fingerprinter that does not send the platform's content-negotiation header will
get **zero** results from a platform that uses header-based API versioning, even
when the platform is present, exposed, and unauthenticated at the identity endpoint.
The absence is a tool artifact, not a population fact.

CVAT uses Django REST Framework `AcceptHeaderVersioning`. Its identity endpoint
`/api/server/about` returns the `{"name":"Computer Vision Annotation Tool",...}`
JSON **only** when the request carries `Accept: application/vnd.cvat+json`. With a
generic `Accept: application/json` (or `*/*`), DRF content negotiation returns 404 /
406, not the JSON. The measured effect in this survey:

- aimap (sends no vendor media type) and the first verification probe pass
  (`Accept: application/json,text/html`): **0 of 30** CVAT candidates confirmed.
- The same 30 candidates re-probed with `Accept: application/vnd.cvat+json`:
  **20 of 30** confirmed (the other 10 down / SSL-mismatch / 404 on the port tried).

The 30 candidates were `http.title:"Computer Vision Annotation Tool"` hits, a
high-precision dork, so "0 confirmed" was obviously wrong and triggered the look.
Tool-humility caught it: a zero from a strong dork is a signal to check the probe,
not to conclude absence (this is the active-probe analogue of "0 results means
generate variants, not stop").

## Why it generalizes

Vendor media types and header-based versioning are common across modern API
frameworks: DRF `AcceptHeaderVersioning` (`application/vnd.<product>+json`),
GitHub-style `Accept: application/vnd.<org>.v3+json`, Kubernetes content-type
negotiation, and any service behind an API gateway that enforces an `Accept`
allowlist. A fingerprinter whose probe model cannot set request headers will
silently miss every one of them at the identity endpoint, and the miss is
**uniform** (0%, not a sample), so it never looks like noise to be averaged out.
It looks like the platform is not deployed.

## How to apply

1. **A zero from a high-precision identity dork is a probe-design alarm, not a
   negative.** Before recording "category X is rare / absent," confirm the probe
   sends whatever the platform's docs say the identity endpoint requires
   (Accept header, custom header, specific path, POST vs GET).
2. **Fingerprint tools need request-header support.** aimap's `Probe` struct is
   `(Path, Matches[])` with no request-header field, so it structurally cannot
   fingerprint header-versioned APIs (CVAT among them). The fix is a `Headers`
   field on `Probe`, passed through to the HTTP client. Until then, header-versioned
   platforms are covered by the survey verification probe (which can set headers),
   and the aimap fingerprint is documented as "will not fire without header support."
3. **Read the platform's content-negotiation contract during Stage -1.** The CVAT
   Stage -1 OSINT explicitly flagged the `application/vnd.cvat+json` requirement;
   it was in the intel doc and still got missed on the first probe pass because the
   probe predated the intel. Wire the Stage -1 header findings into the probe before
   the scan, not after the zero.

## Relationships

- The active-probe form of **"0 results means generate variants, not stop"**: vary
  the request shape (headers), not just the dork.
- A tool-gap sibling of the aimap gRPC gap (Hubble Relay, #71 survey): both are
  cases where aimap's HTTP-GET-only probe model cannot express what the target
  requires (gRPC framing there, a vendor Accept header here).
- Paired with **#72** (the registration-default failure class), the other lesson
  from this survey.
