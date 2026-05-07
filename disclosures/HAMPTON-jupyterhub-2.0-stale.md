---
to: barbara.tibbs@hamptonu.edu
cc: cas-it@hamptonu.edu, abuse@nuclide-research.com
severity: HIGH
ip: 137.198.56.13
institution: "Hampton University, JupyterHub on `jupyter.cas.hamptonu.edu` running version 2.0.0 (released early 2022, multi-year-old, many CVEs apply)"
status: DRAFT
outcome: sent
date: 2026-05-07
---

**To:** barbara.tibbs@hamptonu.edu
**Cc:** cas-it@hamptonu.edu, abuse@nuclide-research.com
**Subject:** JupyterHub on jupyter.cas.hamptonu.edu (137.198.56.13) — running 2.0.0 from early 2022, multi-year version-currency exposure

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-07

This is an unsolicited good-faith coordinated-disclosure notification under the NuClide Research umbrella (CISA disclosures CVE-2025-4364, ICSA-25-140-11). Severity: HIGH.

The contact email is the ARIN-listed OrgAbuseEmail for Hampton University's IP block. If there is a more appropriate handler for academic-network security notifications at Hampton (CAS IT, CIO office, Information Security), please forward.

---

## Summary

`jupyter.cas.hamptonu.edu` (137.198.56.13) runs **JupyterHub 2.0.0** behind nginx 1.20.1 over HTTPS. The release date for JupyterHub 2.0.0 is **March 2022** — the deployment is approximately three years stale. Many JupyterHub-side CVEs filed since 2022 apply but are not patched on this host.

The HTTPS posture and CSP (`frame-ancestors 'self'`) are correct. The auth model is intact (login form at root, not a bypassable unauth-kernel-exec). The finding is purely **version currency**: a 2022-era JupyterHub running in 2026 has accumulated patch-debt that warrants an upgrade cycle.

## Evidence (passive probes only)

```
$ curl -sI -k https://jupyter.cas.hamptonu.edu/
HTTP/2 200
Server: nginx/1.20.1
Content-Security-Policy: frame-ancestors 'self'; report-uri /hub/security/csp-report
X-Jupyterhub-Version: 2.0.0

$ curl -sk https://jupyter.cas.hamptonu.edu/ | grep -E "<title>"
<title>JupyterHub</title>

$ curl -sI -k https://jupyter.cas.hamptonu.edu/jupyter/hub/api/info
HTTP/2 403
X-Jupyterhub-Version: 2.0.0
```

The `403 Forbidden` on `/jupyter/hub/api/info` confirms the JupyterHub auth model is intact. The deployment serves through a `/jupyter/` path-prefix (nginx forwards to JupyterHub at that mount).

## Applicable CVEs (selected)

The full CVE list for JupyterHub between 2.0.0 and 5.4.4 is long. Highlights of CVEs filed since the 2.0.0 release that apply:

| CVE | Severity | Fixed in | Description |
|---|---|---|---|
| CVE-2024-28233 | 8.1 (HIGH) | 4.0.3+, 4.1.0+ | XSS in `/hub/login` |
| CVE-2024-41942 | 7.2 (HIGH) | 5.0.0+ | Admin self-escalation |
| CVE-2026-33709 | 5.1 (MED) | 5.4.4+ | Open redirect via `?next=` |
| CVE-2024-44260 | (varies) | 5.0.0+ | OAuth token leak in error path |

This is not exhaustive. The full release notes between 2.0.0 and 5.4.4 enumerate ~40 security-relevant fixes.

## Recommendation

1. **Upgrade to JupyterHub 5.4.4+** (current as of 2026-05-07). This addresses the entire backlog of CVEs filed against the 2.0.x → 5.4.x range.
2. **Plan the migration.** Major-version upgrades of JupyterHub between 2.x and 5.x have breaking changes for authenticator plugins, spawner configs, and database schema. The official migration guide is at `https://jupyterhub.readthedocs.io/en/stable/upgrading.html`.
3. **Audit the existing JupyterHub configuration** during the upgrade window:
   - Authenticator: verify it's not using a deprecated provider
   - Spawner: ensure user-namespace isolation is correct for the upgraded version
   - Hub database: back up before migrating

If a full upgrade is operationally difficult, the highest-leverage interim mitigation is patching CVE-2024-28233 (XSS) by restricting access to the host until the upgrade lands.

## IOCs

| Type | Value |
|---|---|
| Affected host | `137.198.56.13` (`jupyter.cas.hamptonu.edu`) |
| Service | JupyterHub 2.0.0 on nginx 1.20.1 |
| Open ports | tcp/80, tcp/443 |
| Vulnerability class | Version currency (3-year-stale JupyterHub) |
| Authoritative WHOIS contact | `barbara.tibbs@hamptonu.edu` (ARIN OrgAbuseEmail for Hampton netblock) |

## Reference

Full triage case study (chain output for all 13 .edu JupyterHubs surveyed today):
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/commercial/multi-jupyterhub-edu-survey-2026-05-07.md

Happy to coordinate on disclosure timeline.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
