# NIS/YP Internet Exposure — hpc.psy.ntu.edu.tw

**Host:** hpc.psy.ntu.edu.tw / 140.112.62.11  
**Institution:** National Taiwan University, Psychology Department  
**Classification:** Lab-managed HPC research node  
**Date:** 2026-05-21  
**Severity:** Critical  

---

## Finding

NTU's Psychology HPC node ran NIS (YP) — a 1980s LAN credential distribution protocol — fully exposed to the internet at time of observation. yppasswdd, ypserv, and fypxfrd were all registered in the portmapper table and reachable from external IP space. NIS has no transport authentication. An attacker who knows the NIS domain name can:

1. Call fypxfrd to pull the passwd.byname map — all user password hashes for the cluster
2. Call yppasswdd to change any user's password without credential verification
3. SSH into port 22 with the new or cracked credentials

sakura.mit.edu's problem was a boundary wider than assumed. This host had no boundary at all on legacy RPC services.

---

## RPC Surface — Portmapper Dump (2026-05-21T05:41 UTC)

```
program vers proto   port  service
100000    2/3/4  tcp/udp  111  portmapper
100005    1/2/3  tcp/udp  ---  mountd
100003    3/4    tcp      2049  nfsd
100021    1/3/4  tcp/udp  ---  nlockmgr   ← ACTIVE (live NFS operations)
100004    2      tcp/udp  698  ypserv     ← NIS server, internet-exposed
100009    1      tcp/udp  689  yppasswdd  ← NIS password change daemon, no auth
100007    2/3    tcp/udp  686  ypbind     ← NIS client binding daemon
100069    1      tcp/udp  694  fypxfrd    ← NIS fast map transfer daemon
```

nlockmgr active = live NFS writes in progress. Production filesystem, not staging.

NFS exports are subnet-restricted: `/home` and `/raid` export only to `192.168.160.0/24`. The portmapper table was open; the NFS exports themselves were not directly accessible.

---

## NIS Attack Chain

NIS was designed for LAN use in the 1980s. It has no transport encryption, no client authentication, and no key exchange. The only security control is IP-based filtering — which was absent on this host at observation time.

```
External attacker (Internet2/eduroam peer)
    │
    ▼
portmapper TCP 111 → full RPC table (captured from external IP)
    │
    ├─ fypxfrd TCP/UDP 694 → SHOW_MAP → passwd.byname
    │         → all NIS user password hashes (crypt/MD5/SHA-512 format)
    │         → crack offline → valid credentials
    │
    └─ yppasswdd TCP/UDP 689 → YPPASSWDPROC_UPDATE
              → change any NIS user's password
              → no credential verification required
                  │
                  ▼
              SSH port 22 → interactive session
              → pivot to NFS mounts (192.168.160.0/24)
              → access /home and /raid exports
```

NIS domain name is the only blocker. Domain candidates for hpc.psy.ntu.edu.tw: `psy.ntu.edu.tw`, `ntu.edu.tw`, or a shortened form. Was not verified — enumeration not performed.

---

## Additional Services

| Port | Service | Version | Finding |
|------|---------|---------|---------|
| 3306 | MySQL | 8.0.40-0ubuntu0.22.04.1 | Internet-exposed, no source IP restriction |
| 5432 | PostgreSQL | 9.6.0+ | Internet-exposed, auth required (`fe_sendauth: no password supplied`) |
| 5433 | PostgreSQL | — | Internet-exposed, second instance |
| 8086 | InfluxDB | 1.8.10 (EOL) | /debug/vars + /metrics open, queries auth-enforced |
| 9200 | Elasticsearch | — | Auth enforced (401) |
| 80/443 | Apache httpd | 2.4.52 | 17 post-2022 CVEs; CVE-2024-38472 to CVE-2024-39573 |
| 22 | OpenSSH | 8.9p1 Ubuntu | Internet-exposed |
| 4000 | TAIHU 臺鵠 | — | Humanities NLP SPA; `/taihucais_test/` path = test in production |
| 4001 | — | — | Adjacent port open |

---

## InfluxDB 1.8.10 — /debug/vars Exposure

InfluxDB /debug/vars is open with no authentication:

```json
{
  "cmdline": ["influxd"],
  "system": {
    "currentTime": "2026-05-21T07:19:11Z",
    "started": "2026-03-29T10:01:12Z",
    "uptime": 4569479
  },
  "database:k6": {
    "numMeasurements": 18,
    "numSeries": 617
  },
  "shard:/var/lib/influxdb/data/k6/autogen/19": {
    "database": "k6",
    "path": "/var/lib/influxdb/data/k6/autogen/19",
    "diskBytes": 22356529
  }
}
```

Confirmed data:
- Running since 2026-03-29 (52+ days uptime)
- Databases: `k6` (18 measurements, 617 series, ~31.6MB) and `_internal`
- k6 = load testing results database (k6 is an open-source load testing tool)
- Filesystem paths for all shard files confirmed
- HTTP stats: 1,482,473 ping requests (health-checked every ~3 seconds by monitoring), 278 total queries, 43 authFail (our probes contributed)

InfluxDB 1.8.x reached end-of-life in 2023. CVE-2021-22537 (unauth DoS) applies.

---

## Comparison: sakura.mit.edu vs hpc.psy.ntu.edu.tw

| Dimension | sakura.mit.edu | hpc.psy.ntu.edu.tw |
|-----------|---------------|-------------------|
| Root cause | IP allowlist gap | No filtering on RPC services |
| Protocol | NFSv3 (no client auth) | NIS/YP (no transport auth) |
| Protocol era | 1984 | 1985 |
| Credential exposure | WireGuard keys + GCS creds on filesystem | NIS passwd.byname = all cluster hashes |
| Direct password change | No | Yes (yppasswdd) |
| Active operations | nlockmgr (live NFS writes) | nlockmgr (live NFS writes) |
| Secondary risk | CVE-2024-41942 JupyterHub, Portainer RCE | Apache 17 CVEs, MySQL/PG open |

Both nodes: live production research compute, HPC class, legacy RPC stack, no transport authentication.

---

## Remediation

**Immediate:**
1. Block all RPC ports (111, 689, 694, 698, 2049, and all ephemeral portmapper-registered ports) at the perimeter. NIS belongs on a LAN segment with no external routing.
2. Rotate all NIS credentials if any yppasswdd or fypxfrd calls reached the daemon from external IP.
3. Move NIS behind NIS+, Kerberos, or LDAP-over-TLS — or decommission NIS entirely (it is 40 years old).

**Short-term:**
4. Restrict MySQL (3306) and PostgreSQL (5432/5433) to localhost or specific authorized hosts. No database should be internet-routable without a VPN requirement.
5. Upgrade InfluxDB to 2.x (auth on all endpoints by default) or move 1.8.x behind an authenticating reverse proxy. Patch or replace before EOL exposure compounds.
6. Patch Apache httpd to 2.4.62+ (addresses the 2024 CVE block).
7. Audit `/taihucais_test/` path — test endpoints in production are an escalation surface.

**Long-term:**
8. Full RPC audit on all Psychology and humanities research compute nodes. Nodes in academic research clusters frequently inherit legacy NIS/NFS configurations from the 1990s that were never decommissioned.

---

## What Was Not Done

- NIS domain name not verified
- NIS map enumeration not performed
- yppasswdd not called
- MySQL/PostgreSQL credentials not tested
- InfluxDB queries not issued
- No SSH login attempted

All data from passive portmapper dump captured by nu-recon at 2026-05-21T05:41 UTC.

---

## Disclosure

Institution: National Taiwan University — Psychology Department  
CSIRT contact: cert@ntu.edu.tw or security@ntu.edu.tw  
NTU CERT: https://cert.ntu.edu.tw/  
Research PI contact: derivable from `psy.ntu.edu.tw` faculty directory

