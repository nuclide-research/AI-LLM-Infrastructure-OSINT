---
to: abuse@uw.edu
cc: uw-noc@uw.edu, abuse@nuclide-research.com
severity: HIGH
ip: 140.142.30.87
institution: "University of Washington Atmospheric Sciences, `orca.atmos.washington.edu` exposes 1980s-era r-services (rexec/rlogin/rsh on tcp/512-514) and NFS (tcp/2049) to the public internet, plus 3 custom Tornado services on alt-ports"
status: DRAFT
outcome: sent
date: 2026-05-07
---

**To:** abuse@uw.edu
**Cc:** uw-noc@uw.edu, abuse@nuclide-research.com
**Subject:** orca.atmos.washington.edu (140.142.30.87). Berkeley r-services (rexec/rlogin/rsh) + NFS exposed to public internet

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-07

This is an unsolicited good-faith coordinated-disclosure notification under the NuClide Research umbrella (CISA disclosures CVE-2025-4364, ICSA-25-140-11). Severity: HIGH.

This finding is in a different threat class than the rest of today's batch (we were sweeping for unauth-Jupyter). The atmospheric-sciences research host surfaced through the dork because it runs Tornado on alt-ports (8081/8082/8084), but it also has a much more concerning surface that warrants its own disclosure.

---

## Summary

`orca.atmos.washington.edu` (140.142.30.87) is a research host on the UW Atmospheric Sciences network that exposes the following services to the public internet:

| Port | Service | Risk |
|---|---|---|
| **tcp/512** | exec (rexec) | **HIGH** — Berkeley r-protocol, plaintext-auth, no encryption, deprecated since the early 1990s |
| **tcp/513** | login (rlogin) | **HIGH** — same as above, transmits credentials in plaintext |
| **tcp/514** | shell (rsh) | **HIGH** — same; rsh permits remote command execution under the same plaintext-auth model |
| **tcp/2049** | NFS v3-4 | **HIGH** — Network File System; depending on export rules, may permit unauthenticated read or write of file shares |
| tcp/22 | SSH (OpenSSH 9.2p1 Debian) | normal |
| tcp/80, tcp/443 | Apache 2.4.65 | normal |
| tcp/8081, tcp/8082, tcp/8084 | TornadoServer 6.3.3 (3 instances) | unknown — see below |
| tcp/9102 | jetdirect-class | unknown |

The r-services exposure is the headline finding. These are 1980s-era Berkeley protocols (rexec, rlogin, rsh) that have been considered insecure for ~30 years; the modern replacement is SSH, which is also running on this host. Their continued availability on a public IP is almost certainly an oversight. They may be running for compatibility with a legacy lab pipeline that nobody has audited recently.

The NFS export on tcp/2049 is a related concern: if the export rules allow read access from any source, an unauthenticated attacker on the public internet can mount and read files. If they allow write access, an attacker can plant files that get read by lab pipelines.

## Evidence (passive probes only)

```
$ nmap -sV -Pn -p 22,80,443,512,513,514,2049,8081,8082,8084,9102 orca.atmos.washington.edu
PORT     STATE SERVICE    VERSION
22/tcp   open  ssh        OpenSSH 9.2p1 Debian 2+deb12u6 (protocol 2.0)
80/tcp   open  http       Apache httpd 2.4.65
443/tcp  open  ssl/http   Apache httpd 2.4.65
512/tcp  open  exec?
513/tcp  open  login?
514/tcp  open  shell?
2049/tcp open  nfs        3-4 (RPC #100003)
8081/tcp open  http       Tornado httpd 6.3.3
8082/tcp open  http       Tornado httpd 6.3.3
8084/tcp open  http       Tornado httpd 6.3.3
9102/tcp open  jetdirect?

$ curl -sI -m 5 http://orca.atmos.washington.edu:8081/
HTTP/1.1 404 Not Found
Server: TornadoServer/6.3.3
```

The Tornado services on 8081/8082/8084 return 404 at the root path. They are custom Python web apps, not exposed-Jupyter. We did not probe deeper paths; if your operator team can confirm what those three services are, NuClide can re-validate against any specific path you'd like checked.

NFS export rules: NuClide did not probe `showmount -e` or attempt mount, since that would cross the line from passive recon to active probing of the export config. We recommend your operator team run `showmount -e localhost` on the host itself to enumerate the export rules.

## Threat model

**Primary**: r-services credential capture + remote command execution.

If anyone is still using rexec/rlogin/rsh against this host:

- A passive observer on any network hop captures credentials in plaintext.
- An MITM can hijack the session entirely (no key-exchange, no message-authentication-code).
- rsh permits direct command execution as the authenticated user.

**Secondary**: NFS unauthenticated read.

If the NFS exports allow `*` or wide subnets, anyone on the internet can mount and read files. This includes any sensitive data stored in lab home directories, research datasets, or shared software repositories.

**Adjacent**: the 3 Tornado services (8081/8082/8084) and the jetdirect service (9102) are unidentified. They may be benign internal services that should never have been on a public IP, or they may be additional research-data services with their own auth concerns.

## Recommendation

1. **Disable r-services** unless there is an active operational dependency. If there is one, migrate that pipeline to SSH (key-based) and then disable. The systemd or xinetd unit is typically `inetd` / `xinetd.d/{exec,login,shell}`. Disable and restart inetd/xinetd, then verify the ports are no longer listening.
2. **Audit the NFS export rules** (`/etc/exports`). If wildcard exports exist for `/home`, `/data`, or shared research directories, restrict to specific subnets.
3. **Triage the three Tornado services** on 8081/8082/8084. If they are research-data viewers without auth, either gate them behind UW campus VPN or add auth via the existing Apache reverse-proxy.
4. **Consider whether `orca.atmos.washington.edu` should be on a public IP at all.** If the use case is researcher access, a campus VPN gateway is a more defensible posture.

## IOCs

| Type | Value |
|---|---|
| Affected host | `140.142.30.87` (`orca.atmos.washington.edu`) |
| Concerning ports | tcp/512, tcp/513, tcp/514, tcp/2049 |
| Supporting context | OpenSSH 9.2p1 Debian, Apache 2.4.65, 3x Tornado on 8081/8082/8084 |
| Authoritative WHOIS contact | `abuse@uw.edu` (ARIN OrgAbuseEmail for UW netblock) |

## Reference

Full triage case study (this finding surfaced via the JupyterHub-edu sweep):
AI-LLM-Infrastructure-OSINT/blob/main/case-studies/commercial/multi-jupyterhub-edu-survey-2026-05-07.md

Happy to help characterize the Tornado services if your operator team would like a deeper probe.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
AI-LLM-Infrastructure-OSINT
