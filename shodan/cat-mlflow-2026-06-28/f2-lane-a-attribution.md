# F2 Lane A -- Operator Attribution -- 168.138.146.91
Date: 2026-06-28

## A1 Shodan Dossier

Source: https://www.shodan.io/host/168.138.146.91 (authenticated session, in-page read)
Last Seen: 2026-06-28

| Field             | Value                          |
|-------------------|-------------------------------|
| Cloud Provider    | Oracle Cloud Infrastructure   |
| Cloud Region      | sa-saopaulo-1 (Sao Paulo, BR) |
| Country           | Brazil                        |
| City              | Sao Paulo                     |
| Organization      | Oracle Public Cloud           |
| ISP               | Oracle Corporation            |
| ASN               | AS31898                       |
| Tags              | cloud                         |

Open ports per Shodan:
- 22/tcp   OpenSSH 8.2p1 Ubuntu 4ubuntu0.13 (last seen 2026-06-03)
- 5000/tcp  MLflow (gunicorn, Python) (last seen 2026-06-28)
- 8000/tcp  HTTP 404 / plain-text (last seen 2026-06-15)
- 9000/tcp  Portainer 2.19.5 (AngularJS) (last seen 2026-06-27)

Vulnerabilities flagged by Shodan (inferred from Portainer 2.19.5):
- CVE-2024-33662 CVSS 7.5 -- improper AES encryption in Portainer before 2.20.2
- CVE-2024-33661 CVSS 9.1 -- open redirect in Portainer before 2.20.0

Web technologies detected: AngularJS, Python, gunicorn

Favicon hashes:
- Port 5000: http.favicon.hash = -1507094812 (MLflow)
- Port 9000: http.favicon.hash = -1639835336 (Portainer)

## A2 TLS Certificate

Port 5000: No TLS -- plain HTTP only. openssl s_client returned no certificate (exit 1).
Port 443: No TLS -- port not open.

Subject CN: NULL
SANs: NULL
Issuer: NULL
Validity: NULL

Note: No TLS anywhere on this host. All services running unencrypted.

## A3 Reverse DNS

PTR: NXDOMAIN (91.146.138.168.in-addr.arpa does not exist)
SOA authority: ns1.p201.dns.oraclecloud.net -- confirming OCI tenancy DNS management.
HackerTarget passive DNS: no A records found (no domain has resolved to this IP in passive DNS corpus).

## A4 Port Map

Active nmap scan (-sV, T3):

| Port     | State | Service   | Version                           |
|----------|-------|-----------|-----------------------------------|
| 22/tcp   | open  | ssh       | OpenSSH 8.2p1 Ubuntu 4ubuntu0.13  |
| 5000/tcp | open  | http      | Gunicorn (MLflow SPA)             |
| 8000/tcp | open  | http      | Golang net/http (404 plain-text)  |
| 9000/tcp | open  | http      | Portainer CE 2.19.5               |

OS: Ubuntu Linux (confirmed via SSH banner string Ubuntu-4ubuntu0.13)
SSH banner: SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.13

SSH host keys (stable fingerprints for operator tracking):
- ssh-rsa   d3:be:43:47:1f:ae:b9:0e:b7:49:2e:34:54:38:04:a6
- ecdsa-sha2-nistp256 (key in ssh_keys.txt)
- ssh-ed25519 (key in ssh_keys.txt)

Port 8000 response: HTTP 404, content-type text/plain, Golang net/http server. Likely an internal API or background worker that is not the primary surface.

Port 9000: Portainer CE 2.19.5 -- full HTML response, unauthenticated landing page. This is a Docker management UI running exposed on 0.0.0.0. Portainer manages containers on this host.

MLflow on 5000: Gunicorn WSGI, serving MLflow SPA (index.html 645 bytes, last-modified Thu 24 Apr 2025). Server: gunicorn header only -- no operator info in headers.

## A5 VisorGraph

visor-graph: command not found.
visorplus assess 168.138.146.91 ran successfully. Output:
- GreyNoise: no data (host not in GreyNoise threat intel)
- Shodan host detail via visorplus: returned nil for org/country/ports (API key path not populated)
- Passive DNS (HackerTarget): 1 query, result = "No DNS A records found"
- Spamhaus DNSBL: checked
- Ollama port 11434: no route to host (not open)

Files saved to ~/AI-LLM-Infrastructure-OSINT/168_138_146_91/:
dnsbl.txt, greynoise.json, nmap_top1000.txt, passive_dns.txt, rdns.txt, shodan_host.json, ssh_keys.txt, whois.txt

## A6 recongraph

NULL -- ~/Videos/jax/recongraph does not exist on this host. recongraph binary not found on PATH.

## A7 WHOIS

Key fields:

| Field         | Value                                      |
|---------------|--------------------------------------------|
| NetRange      | 168.138.0.0 - 168.138.255.255              |
| CIDR          | 168.138.0.0/16                             |
| NetName       | OC-195                                     |
| NetType (1)   | Direct Allocation -- Oracle Corporation    |
| NetType (2)   | Reassigned -- Oracle Public Cloud (OC-195) |
| RegDate       | 2016-10-14                                 |
| OrgName       | Oracle Corporation                         |
| OrgId         | ORACLE-4                                   |
| Address       | 2300 Oracle Way, Austin TX 78741           |
| Abuse email   | network-contact_ww_grp@oracle.com          |
| Tech contact  | domain-contact_ww_grp@oracle.com           |
| Routing email | network-contact_ww@oracle.com              |

The /16 is wholly Oracle's. Sub-org is Oracle Public Cloud (OC-195) = OCI tenant range.
There is no ARIN record for an individual tenant -- OCI does not delegate WHOIS to customers.

## A8 Web presence

Port 5000 (MLflow):
  HTTP 200, Server: gunicorn, Content-Type: text/html, 645 bytes SPA shell.
  No operator-identifying headers. Last-Modified: Thu 24 Apr 2025 (MLflow static bundle age).

Port 8000 (Golang):
  HTTP 404, Content-Type: text/plain, body: "Not found". No operator headers.

Port 9000 (Portainer):
  HTTP 200, full Portainer CE 2.19.5 UI. No authentication wall -- login form served
  (unauthenticated landing page for Portainer, login required to proceed further).
  No operator-identifying headers.

Port 80/443: no response (closed/filtered).
HTTPS everywhere: NULL (zero TLS on any port).

---

## Shodan Query Log

| Dork | Platform | Result |
|------|----------|--------|
| Direct host dossier: shodan.io/host/168.138.146.91 | Shodan web UI | SUCCESS -- full dossier returned |

---

## Attribution Summary

```
Org:               Oracle Corporation (infrastructure registrant)
Sub-org / tenant:  Oracle Public Cloud (OCI) -- region sa-saopaulo-1 (Sao Paulo, Brazil)
                   Individual OCI tenant unknown; WHOIS stops at Oracle cloud layer.

Cloud footprint:
  - OCI compute instance, Sao Paulo region
  - No PTR record (tenant did not configure reverse DNS -- common for individual/personal tenants)
  - No domain resolves to this IP (passive DNS null)
  - Portainer CE exposed: operator manages Docker containers manually via GUI

Likely operator type:  Individual / small team running a personal ML project
                       Evidence: no PTR, no domain, Portainer CE (not enterprise), OCI free-tier
                       or pay-as-you-go single instance, MLflow without auth.

Security function likely?  UNKNOWN -- two competing hypotheses:

  HYPOTHESIS A -- Unauthorized external attack:
    - Experiment names (pwn_tmp_test, pwn_cron_root_d74b03, cve_test, scan_*) read as
      attacker staging: cron-root persistence attempt name, CVE enumeration, scan staging.
    - 100 registered models on an otherwise minimal, no-domain instance is anomalous volume.
    - No TLS anywhere suggests the operator did not harden this for production.
    - Portainer exposed with no auth wall = easy pivot once MLflow is accessed.

  HYPOTHESIS B -- Owner ran authorized red-team / security testing:
    - Instance is in Brazil (sa-saopaulo-1); experiment names could be personal security
      research or coursework (pwn_* naming is common in CTF/lab environments).
    - MLflow is actively maintained (last Shodan scan today 2026-06-28).
    - Portainer CE suggests solo operator managing their own stack.
    - No evidence of exfil or lateral movement visible from external recon.

Discriminating signals STILL NEEDED (verify lane):
  1. MLflow experiment metadata -- who created cve_test/pwn_cron_root entries,
     what artifact URIs are attached (S3/GCS paths reveal org/account).
  2. MLflow model registry details -- model names, tags, description fields may name the org.
  3. Portainer -- if init not completed, admin claim is possible and would reveal env vars
     inside containers (operator identity, API keys, cloud credentials).
  4. Golang port 8000 -- enumerate endpoints; may be an internal API with operator context.

Key evidence:
  - OCI sa-saopaulo-1 = Brazil-based operator
  - No PTR, no domain = individual or small team, not enterprise
  - Portainer CE 2.19.5 (vulnerable: CVE-2024-33661 CVSS 9.1, CVE-2024-33662 CVSS 7.5)
  - Zero TLS across all services
  - GreyNoise: no threat-intel hits (not a known scanner/attacker IP)
  - SSH keys stable (not rotated -- long-running instance, same operator)
```

### Three IPs to Prioritize at Verify Lane

This is a single-host investigation. Three verify-lane targets on this host:

1. **http://168.138.146.91:5000** (MLflow REST API)
   Enumerate /api/2.0/mlflow/experiments/list, /api/2.0/mlflow/registered-models/list,
   and artifact URIs on the pwn_cron_root_d74b03 run. Artifact S3/GCS URI = operator cloud account.

2. **http://168.138.146.91:9000** (Portainer CE 2.19.5)
   Check /api/status (init state). If admin not yet configured, CVE-2024-33661/33662 apply.
   Container list via API would expose image names, env vars, mounted volumes.

3. **http://168.138.146.91:8000** (Golang net/http)
   Enumerate common paths (/metrics, /health, /api, /debug/pprof).
   pprof exposure would confirm Go service identity and potentially goroutine/binary info.
