#!/usr/bin/env python3
"""Extract (ip, platform, posture) and (ip, subject_cn) for nash-recon
from Cat-MCP-Cred-Fleet 2026-06-09 artifacts.

Platform partitioning: the fleet was identified as 88 hosts serving an
identical MCP credential-theft toolset, but the *frontend* presented to
HTTP scanners varies (Apache, 4D_WebSTAR, directory listings, error
pages, empty-200, etc.) -- a classic operator-camouflage pattern. We
partition by the camouflage cluster so nash-recon measures deviation
within each cluster's empirical equilibrium.

Posture mapping from frontend probe status:
  200 with MCP body       -> AUTH_OFF (real MCP exposed)
  200 with decoy body     -> AUTH_OFF (camouflaged but still serving)
  401/403                 -> AUTH_ON_DEFAULT
  301/302/308             -> NET_ISOLATED (redirect-only)
  500/502/503/504         -> UNKNOWN (error)
  no response             -> UNKNOWN
"""
import json, sys, re
from pathlib import Path
from collections import Counter

base = Path(__file__).parent
frontend = json.loads((base / "frontend-probe-results.json").read_text())
certs    = json.loads((base / "cert-resniff-results.json").read_text())
tools    = json.loads((base / "mcp-tools-inventory.json").read_text())

mcp_ips = set()
if isinstance(tools, dict):
    for k in ("hosts", "results", "inventory"):
        if k in tools and isinstance(tools[k], list):
            for r in tools[k]:
                if isinstance(r, dict) and r.get("ip"):
                    mcp_ips.add(r["ip"])
elif isinstance(tools, list):
    for r in tools:
        if isinstance(r, dict) and r.get("ip"):
            mcp_ips.add(r["ip"])

def cluster(rec):
    """Bin the frontend camouflage into a platform label."""
    srv = (rec.get("server") or "").strip()
    title = (rec.get("title") or "").strip()
    body = (rec.get("body_head") or "")[:200]
    status = rec.get("status")
    if rec.get("ip") in mcp_ips:
        return "MCP-CredFleet-confirmed"
    if status in (401, 403):
        return "MCP-CredFleet-authgated"
    if status in (301, 302, 307, 308):
        return "MCP-CredFleet-redirect"
    if status and 500 <= status < 600:
        return "MCP-CredFleet-error"
    if not status:
        return "MCP-CredFleet-unresponsive"
    if "Directory Listing" in title or "Index of" in body:
        return "MCP-CredFleet-dirlist"
    if "4D_WebSTAR" in srv:
        return "MCP-CredFleet-4dwebstar"
    if "AdSubtract" in srv:
        return "MCP-CredFleet-adsubtract"
    if "Apache" in srv:
        return "MCP-CredFleet-apache"
    if "nginx" in srv.lower():
        return "MCP-CredFleet-nginx"
    if srv:
        return f"MCP-CredFleet-other-{re.sub(r'[^A-Za-z0-9]', '', srv)[:12].lower()}"
    return "MCP-CredFleet-blank"

def posture(rec):
    status = rec.get("status")
    if status == 200:
        return "AUTH_OFF"
    if status in (401, 403):
        return "AUTH_ON_DEFAULT"
    if status in (301, 302, 307, 308):
        return "NET_ISOLATED"
    return "UNKNOWN"

# Build population.csv
out_pop = base / "nash-population.csv"
with out_pop.open("w") as f:
    f.write("ip,platform,posture\n")
    seen = set()
    for rec in frontend:
        ip = rec.get("ip")
        if not ip or ip in seen:
            continue
        seen.add(ip)
        f.write(f"{ip},{cluster(rec)},{posture(rec)}\n")

# Build certs.tsv
out_cert = base / "nash-certs.tsv"
with out_cert.open("w") as f:
    for c in certs:
        ip = c.get("ip")
        if not ip:
            continue
        subj_block = None
        for k, v in c.items():
            if k.startswith("sni_") and isinstance(v, dict):
                subj_block = v.get("subject")
                break
        if not subj_block:
            continue
        cn = subj_block.get("commonName") or subj_block.get("organizationName") or ""
        if cn:
            f.write(f"{ip}\t{cn}\n")

print(f"wrote {out_pop} ({sum(1 for _ in out_pop.open())-1} hosts)")
print(f"wrote {out_cert} ({sum(1 for _ in out_cert.open())} cert rows)")
