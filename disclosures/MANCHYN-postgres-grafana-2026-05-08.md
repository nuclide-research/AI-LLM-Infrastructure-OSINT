---
to: admin@manchyn.com
cc: abuse@nuclide-research.com
severity: HIGH
ip: 152.53.82.7
institution: "manchyn.com / na-ai.studio (Jiangsu CN) — PostgreSQL 5432 publicly exposed without SSL on 152.53.82.7; Grafana 11.2.0 on port 3000 version-stale (CVE-2024-9355)"
status: SENT
outcome: sent
date: 2026-05-08
---

**To:** admin@manchyn.com
**Subject:** manchyn.com / na-ai.studio (152.53.82.7) — HIGH: PostgreSQL exposed on public internet without SSL + stale Grafana 11.2.0

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
2026-05-08

This is an unsolicited good-faith coordinated-disclosure notification. I was unable to find a security contact for manchyn.com or na-ai.studio (Cloudflare WHOIS privacy), so I'm reaching admin@manchyn.com. If you maintain the infrastructure at `152.53.82.7`, please review the findings below.

---

## Findings

### HIGH — PostgreSQL 5432 publicly reachable, no SSL/TLS

```
$ psql "host=152.53.82.7 port=5432 sslmode=require"
psql: error: server does not support SSL, but SSL was required

$ psql "host=152.53.82.7 port=5432 sslmode=disable user=postgres"
psql: error: fe_sendauth: no password supplied
```

PostgreSQL on `152.53.82.7:5432` is reachable from the public internet and does not support SSL. Authentication is password-based. Any application connecting to this database over the internet transmits credentials (username/password) and query data in cleartext — trivially interceptable by a passive observer on any network path between client and server.

**Recommended fix:** Either (1) bind PostgreSQL to `127.0.0.1` in `postgresql.conf` (`listen_addresses = 'localhost'`) so it is only reachable locally, or (2) enable SSL by generating a self-signed cert and setting `ssl = on` in `postgresql.conf` and `hostssl all all 0.0.0.0/0 md5` in `pg_hba.conf`. If any application connects over the internet, option 1 plus a VPN or SSH tunnel is the correct architecture.

### MEDIUM — Grafana 11.2.0 version-stale (CVE-2024-9355)

```
$ curl http://152.53.82.7:3000/api/health
{"database":"ok","version":"11.2.0","commit":"2a88694fd3ced0335bf3726cc5d0adc2d1858855"}
Date: Fri, 08 May 2026 05:14:15 GMT
```

Grafana 11.2.0 is several minor releases behind the current 11.5+ branch. Notable patched CVEs between 11.2.0 and current:
- **CVE-2024-9355** (11.2.1) — Markdown renderer XSS via maliciously crafted dashboard panels
- Additional security fixes in 11.3.x, 11.4.x, and 11.5.x

The login page appears auth-enforced; however, running a version with known XSS vectors means a logged-in user with edit access can execute arbitrary JavaScript in other users' browser sessions (cross-site scripting against your own Grafana users).

**Recommended fix:** Upgrade to Grafana 11.5+ (latest stable). Standard Docker pull or package manager update.

---

## Evidence Preservation

Server-asserted `Date:` headers preserved for both findings. Bundle held privately.

---

## IOCs

| Type | Value |
|---|---|
| Affected host | `152.53.82.7` (Netcup, DE) |
| Associated domains | `manchyn.com`, `na-ai.studio` |
| PostgreSQL port | `5432` — no SSL, publicly reachable |
| Grafana version | `11.2.0` on port `3000` |
| Confirmed live | Fri, 08 May 2026 05:14:15 GMT |

---

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
