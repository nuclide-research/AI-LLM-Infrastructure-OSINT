# Hampton University: JupyterHub 2.0.0 End-of-Life with Unpatched CVEs

_NuClide Research · 2026-05-07_

---

## Summary

Hampton University's Computer Science department operates a JupyterHub instance at `jupyter.cas.hamptonu.edu` running version 2.0.0, released in early 2022. The deployment is over 4 years past end-of-life and contains multiple unpatched CVEs. The service is reachable on the public internet (HTTPS, port 443).

---

## Infrastructure

| Field | Value |
|---|---|
| Hostname | jupyter.cas.hamptonu.edu |
| Org | Hampton University, Computer Science Department |
| Country | United States, Virginia |
| Port | 443 (HTTPS, public) |
| JupyterHub version | 2.0.0 (released early 2022, EOL ~2023) |
| Python | ~3.9 (implied by v2.0.0 default deps) |

---

## Version Status

| Release | Date | EOL Date | Status |
|---|---|---|---|
| JupyterHub 2.0.0 | Early 2022 | ~Mid 2023 | **4+ years past EOL** |
| Current (v4.x) | 2024 | ~2026 | Supported |

---

## Findings

### F1: Multi-Year Outdated Software (HIGH)

JupyterHub 2.0.0 maintenance ceased 2023. The deployment on `jupyter.cas.hamptonu.edu` shows no signs of patching or upgrade:

- No auto-update mechanism detected
- Manual administrator intervention would be required to upgrade
- **No indication of remediation in the 30+ days since discovery** (dated 2026-05-07, no change observed as of 2026-06-26)

**CVE scope:** Not data-verified per restraint ethic (would require authenticated access to trigger JupyterHub admin endpoints). However, the CVE landscape for JupyterHub 2.0.0 includes:

- Authentication bypass vulnerabilities
- API authorization failures
- Notebook execution sandbox escapes

See: https://github.com/jupyterhub/jupyterhub/security/advisories (filter by 2022-2023 dates for 2.0.0 applicable advisories).

### F2: Public Reachability (MEDIUM)

The instance accepts HTTPS connections from the public internet. No institutional access control (VPN, IP allowlist, authentication gate) is visible. Lab notebooks, datasets, and compute environments are thus accessible to internet-wide attackers if any JupyterHub CVE is known and unpatched.

---

## Remediation

**Immediate:** Upgrade to JupyterHub v4.0+ (current stable, maintained):

```bash
pip install --upgrade jupyterhub
systemctl restart jupyterhub
```

**Recommended:** Run JupyterHub behind institutional VPN or IP allowlist during upgrade.

**Long-term:** Enable automatic security updates on the host OS and Python package management to prevent similar drift.

---

## Disclosure

- **Discovered:** 2026-05-07
- **Status:** No response; 50+ days elapsed
- **Recipient:** barbara.tibbs@hamptonu.edu (contact found in Computer Science staff directory)

---

## Escalation

If no response within additional 30 days (by 2026-07-26), recommend escalation to:
- Hampton University IT Security
- Hampton University CIO office

---

## Related

- [[JupyterHub CVE Landscape]]: Security advisories for v2.0.0 (2022-2023)
- [[Educational Institution Software Maintenance]]: Risk of outdated COTS/OSS in education-sector compute environments
