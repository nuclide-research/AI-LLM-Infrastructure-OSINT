#!/usr/bin/env python3
"""Emit visorlog NDJSON event stream for the 66 confirmed-real MCP hosts."""
import json
from pathlib import Path

base = Path("/home/cowboy/AI-LLM-Infrastructure-OSINT/shodan/cat-mcp-cred-fleet-2026-06-09")
recs = [json.loads(l) for l in (base / "mcp-initialize-results.jsonl").read_text().splitlines() if l.strip()]
attr = {r["ip"]: r for r in json.loads((base / "operator-attribution.json").read_text())["hosts"]}

out_path = base / "visorlog-events.ndjson"
with out_path.open("w") as out:
    for rec in recs:
        if not rec.get("init_pass"):
            continue
        ip = rec["ip"]
        a = attr.get(ip, {})
        rdap = a.get("rdap") or {}
        org = (rdap.get("entities") or [{}])[0].get("name") if rdap.get("entities") else rdap.get("name", "AWS")
        rdns = a.get("rdns") or ""
        tools = rec.get("tool_names", [])
        ev = {
            "source": "mcp-fleet-investigation-2026-06-09",
            "ip": ip,
            "port": rec.get("port", 9090),
            "scheme": rec.get("scheme", "https"),
            "endpoint": rec.get("endpoint"),
            "service": "MCP Server",
            "service_version": "mcp-server 1.0.1",
            "protocol_version": "2025-06-18",
            "severity": "critical",
            "auth_status": "none",
            "category": "unauthenticated-access",
            "title": "Unauthenticated MCP server exposes credential-theft and RCE tools",
            "detail": (
                "Protocol-strict MCP initialize+tools/list confirmed mcp-server 1.0.1 exposing "
                "5 tools without authentication: get_aws_admin_credentials, get_aws_session_credentials, "
                "get_ssh_session_credentials, add_cron_job, schedule_commands. No tool was invoked "
                "(restraint: names + schemas only). Host is one of 66 in a coordinated AWS multi-region "
                "fleet with identical MCP backend behind heterogeneous L7 deception chrome and 54 "
                "distinct TLS cert issuers - consistent with honeypot or credential-collection trap."
            ),
            "tags": ["MCP", "UNAUTH", "CREDENTIAL-THEFT-TOOL", "CAT-MCP-CRED-FLEET"],
            "sector": "commercial",
            "operator_org": org,
            "rdns": rdns,
            "tools_exposed": tools,
            "fleet_id": "cat-mcp-cred-fleet-2026-06-09",
            "fleet_size": 66,
            "ts": rec.get("ts"),
            "data_accessed": False,
        }
        out.write(json.dumps(ev) + "\n")
print(f"wrote {out_path}")
