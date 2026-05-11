---
to: security@vt.edu
cc: abuse@vt.edu, abuse@nuclide-research.com
severity: HIGH
ip: 128.173.51.43
institution: "Virginia Polytechnic Institute and State University, JupyterHub on `waingram418808.lib.vt.edu` served over HTTP-only with credentials in plaintext on every login; running version 4.0.2 (3 unpatched CVEs)"
status: DRAFT
outcome: sent
date: 2026-05-07
---

**To:** security@vt.edu
**Cc:** abuse@vt.edu, abuse@nuclide-research.com
**Subject:** JupyterHub on waingram418808.lib.vt.edu (128.173.51.43) — HTTP-only login form transmits credentials in plaintext + 3 unpatched CVEs in 4.0.2

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-07

This is an unsolicited good-faith coordinated-disclosure notification under the NuClide Research umbrella (CISA disclosures CVE-2025-4364, ICSA-25-140-11). Severity: HIGH.

---

## Summary

`waingram418808.lib.vt.edu` (128.173.51.43) runs **JupyterHub 4.0.2** on **port 80 only** — no HTTPS redirect, port 443 is closed. The login form at `http://waingram418808.lib.vt.edu/hub/login` accepts username + password POSTed as plaintext over the wire. Any attacker on the campus WiFi, eduroam, or the network path to the host can intercept VT user credentials in cleartext on every login.

The JupyterHub version (4.0.2, released 2023-08) is also stale; three CVEs apply:

| CVE | Severity | Fixed in | Description |
|---|---|---|---|
| CVE-2024-28233 | 8.1 (HIGH) | 4.0.3, 4.1.0+ | XSS in `/hub/login` allowing session hijack via the user's own browser session |
| CVE-2024-41942 | 7.2 (HIGH) | 5.0.0+ | Admin-role users can self-escalate to other admin scopes |
| CVE-2026-33709 | 5.1 (MED) | 5.4.4+ | Open redirect via the post-login `?next=` parameter |

The XSS combined with HTTP-only transport is particularly bad: a network-layer attacker can inject script content into the login page, harvesting credentials before the user even submits the form.

## Evidence (passive probes only)

```
$ curl -sI http://waingram418808.lib.vt.edu/
HTTP/1.1 405 Method Not Allowed
Server: TornadoServer/6.3.3
Content-Security-Policy: frame-ancestors 'self'; report-uri /hub/security/csp-report
X-Jupyterhub-Version: 4.0.2
Set-Cookie: _xsrf=2|...; Path=/hub/

$ curl -sI -k https://waingram418808.lib.vt.edu/
(no response, port 443 closed)

$ curl -s http://waingram418808.lib.vt.edu/hub/login | grep -E "<title>|name=\"username\"|action="
<title>JupyterHub</title>
action="/hub/login?next="
name="username"

$ curl -sI http://waingram418808.lib.vt.edu/hub/api/info
HTTP/1.1 403 Forbidden
X-Jupyterhub-Version: 4.0.2
```

The 403 on `/hub/api/info` confirms the JupyterHub auth model itself is intact. The disclosure is not about an unauthenticated kernel-exec primitive (CL1-class). It is about the transport-layer consent failure: every legitimate VT user authenticating to this service is exposing their credentials in plaintext.

## Threat model

**Primary**: campus-WiFi MITM credential capture.

An attacker on VT's campus network, eduroam, or any shared WiFi hop on a student/faculty member's path to this server can:

1. ARP-spoof or DNS-cache-poison `waingram418808.lib.vt.edu` on the local segment.
2. Intercept the unencrypted POST to `/hub/login`.
3. Recover the user's username + password in cleartext.
4. Use those credentials against the user's other VT services (single sign-on patterns are common).

Beyond credentials, the entire post-auth session — notebook content, model outputs, library searches, any uploaded files — also transits plaintext. A passive observer can read everything, not just the auth handshake.

**Secondary**: CVE-2024-28233 XSS combined with HTTP-only transport allows injection of credential-stealing script into the login page itself. The `frame-ancestors 'self'` CSP partially mitigates clickjacking but does not prevent same-origin XSS.

## Recommendation

1. **Front the JupyterHub instance with HTTPS.** Typical pattern is an Apache or nginx reverse proxy that terminates TLS and forwards to JupyterHub on a localhost port. VT presumably has institutional certificate provisioning for `*.lib.vt.edu` via InCommon / Internet2.
2. **Upgrade to JupyterHub 5.4.4+.** This is the most recent patched release as of 2026-05-07 and addresses all three of the CVEs listed.
3. **Optional: add HSTS** via the reverse proxy once HTTPS is in place, to prevent downgrade attacks.

NuClide will not re-probe this host without coordination. We do not run automated re-probes; this is a one-time disclosure.

## IOCs

| Type | Value |
|---|---|
| Affected host | `128.173.51.43` (`waingram418808.lib.vt.edu`) |
| Service | JupyterHub 4.0.2 on TornadoServer 6.3.3 |
| Open ports | tcp/80 only (port 443 closed) |
| Vulnerability class | Transport-layer plaintext credentials + version-currency CVEs |
| Authoritative WHOIS contact | `abuse@vt.edu` (ARIN OrgAbuseEmail for VT netblock) |

## Reference

Full triage case study (with the chain output for all 13 .edu JupyterHubs surveyed today):
AI-LLM-Infrastructure-OSINT/blob/main/case-studies/commercial/multi-jupyterhub-edu-survey-2026-05-07.md

Methodology Insight #4 (WHOIS-derived disclosure routing):
AI-LLM-Infrastructure-OSINT/blob/main/methodology/insight-04-whois-driven-contact-resolution.md

Happy to coordinate on disclosure timeline or hand off the chain output for VT IT's records.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
AI-LLM-Infrastructure-OSINT
