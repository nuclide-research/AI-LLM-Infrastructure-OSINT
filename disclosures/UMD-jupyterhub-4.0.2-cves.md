---
to: abuse@umd.edu
cc: security@umd.edu, abuse@nuclide-research.com
severity: HIGH
ip: 128.8.235.64
institution: "University of Maryland, JupyterHub on `carrot.umd.edu` running version 4.0.2 (3 unpatched CVEs apply)"
status: DRAFT
outcome: sent
date: 2026-05-07
---

**To:** abuse@umd.edu
**Cc:** security@umd.edu, abuse@nuclide-research.com
**Subject:** JupyterHub on carrot.umd.edu (128.8.235.64) — running 4.0.2 with 3 unpatched CVEs

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-07

This is an unsolicited good-faith coordinated-disclosure notification under the NuClide Research umbrella (CISA disclosures CVE-2025-4364, ICSA-25-140-11). Severity: HIGH.

---

## Summary

`carrot.umd.edu` (128.8.235.64) runs **JupyterHub 4.0.2** on TornadoServer 6.3.3 over HTTPS. The HTTPS posture and CSP (`frame-ancestors 'self'`) are correct, and the auth model is intact (`/hub/api/info` returns 403). The finding is **version currency**: 4.0.2 (released 2023-08) has three unpatched CVEs that subsequent releases address.

## Applicable CVEs

| CVE | Severity | Fixed in | Description |
|---|---|---|---|
| CVE-2024-28233 | 8.1 (HIGH) | 4.0.3, 4.1.0+ | XSS in `/hub/login` allowing session hijack via the user's own browser session |
| CVE-2024-41942 | 7.2 (HIGH) | 5.0.0+ | Admin-role users can self-escalate to other admin scopes |
| CVE-2026-33709 | 5.1 (MED) | 5.4.4+ | Open redirect via the post-login `?next=` parameter |

CVE-2024-28233 is the highest-priority of the three. With HTTPS in place the credential-interception vector is closed, but XSS in the login page can still be used to hijack legitimate user sessions inside the post-auth UI.

## Evidence (passive probes only)

```
$ curl -sI -k https://carrot.umd.edu/
HTTP/2 405
Server: TornadoServer/6.3.3
Content-Security-Policy: frame-ancestors 'self'; report-uri /hub/security/csp-report
X-Jupyterhub-Version: 4.0.2

$ curl -sI -k https://carrot.umd.edu/hub/api/info
HTTP/2 403
X-Jupyterhub-Version: 4.0.2
```

## Recommendation

1. **Upgrade JupyterHub to 5.4.4+** (current as of 2026-05-07). This patches all three CVEs.
2. **Verify the authenticator and spawner configs** survive the 4.x → 5.x major-version migration. JupyterHub's official upgrade guide: `https://jupyterhub.readthedocs.io/en/stable/upgrading.html`.

If the upgrade is operationally blocked for some window, applying the 4.0.3 patch (which addresses CVE-2024-28233) is a low-friction interim mitigation that closes the highest-priority of the three.

## IOCs

| Type | Value |
|---|---|
| Affected host | `128.8.235.64` (`carrot.umd.edu`) |
| Service | JupyterHub 4.0.2 on TornadoServer 6.3.3 |
| Open ports | tcp/80, tcp/443 |
| Vulnerability class | Version currency (4.0.2 with 3 unpatched CVEs) |
| Authoritative WHOIS contact | `abuse@umd.edu` (ARIN OrgAbuseEmail for UMD netblock) |

## Reference

Full triage case study:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/commercial/multi-jupyterhub-edu-survey-2026-05-07.md

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
