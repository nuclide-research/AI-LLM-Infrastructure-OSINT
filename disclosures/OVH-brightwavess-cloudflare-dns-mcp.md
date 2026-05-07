---
to: abuse@ovh.net
cc: abuse@nuclide-research.com
severity: CRITICAL
ip: 15.235.109.186, 158.69.194.62
institution: OVH SAS (brightwavess-monitor MCP server pair with Cloudflare API key baked in)
status: DRAFT
outcome: sent
date: 2026-05-04
---

**To:** abuse@ovh.net
**Cc:** abuse@nuclide-research.com
**Subject:** Unauthenticated Cloudflare-DNS-CRUD MCP servers (operator API key baked in) — 15.235.109.186:3000, 158.69.194.62:3000

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-04

**Re:** Two unauthenticated `brightwavess-monitor` v1.0.0 MCP servers exposing operator's Cloudflare DNS-CRUD API
**IPs / Hosts:** 15.235.109.186:3000, 158.69.194.62:3000 (both OVH)
**Severity:** CRITICAL — domain-takeover primitive

---

I'm an independent security researcher conducting good-faith AI infrastructure research under the NuClide Research umbrella (CISA disclosures CVE-2025-4364, ICSA-25-140-11). This is an unsolicited coordinated-disclosure notification.

---

## Summary

Two OVH-hosted MCP servers identified as `brightwavess-monitor v1.0.0` expose 10 tools each, including **full Cloudflare DNS CRUD** (`cloudflare_list_dns_records`, `cloudflare_create_dns_record`, `cloudflare_update_dns_record`, `cloudflare_delete_dns_record`) plus monitoring (`check_uptime`, `check_db_health`) and Slack alerting. The MCP server has the operator's **Cloudflare API key baked into its configuration** — any unauthenticated caller hitting the JSON-RPC endpoint can:

- List, create, update, or delete DNS records on whatever Cloudflare zone(s) the operator's key authorizes
- **Domain-takeover primitive**: point A records or NS records at attacker-controlled infrastructure to intercept all traffic to the operator's domains (mail, web, API)

Found during NuClide Research's MCP cross-cloud survey (2026-05-04). Full case study: https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/commercial/mcp-cloud-survey-2026-05.md (search for "F12 — `brightwavess-monitor`").

## Confirmed exposure

`POST /` (JSON-RPC) returns a successful `initialize` response identifying both hosts as `brightwavess-monitor v1.0.0`. `tools/list` enumerates 10 tools per host:

```
check_uptime, check_db_health,
cloudflare_list_dns_records, cloudflare_create_dns_record,
cloudflare_update_dns_record, cloudflare_delete_dns_record,
slack_send_message, ...
```

Verification was non-destructive — only `initialize` and `tools/list` were called. No DNS records were enumerated, modified, or deleted; no Slack messages were sent.

## Fleet pattern

Two instances with **identical 10-tool surfaces** and identical version strings on OVH ranges (`15.235.x` Beauharnois + `158.69.x` Beauharnois) suggest either:

1. One operator running a 2-node fleet
2. A common open-source `brightwavess-monitor` template adopted by two operators with shared deployment patterns

Either way: the operator's Cloudflare API key has been reachable on the public internet by any unauthenticated caller for the duration these endpoints have been exposed. **The operator should rotate their Cloudflare API key immediately**, regardless of whether they take any further action.

## Remediation

1. **Rotate the Cloudflare API key** referenced by `brightwavess-monitor` at `dash.cloudflare.com → My Profile → API Tokens → Roll`. Assume the previous key has been observed.
2. **Bind the MCP transport to localhost or restrict via firewall**:
   ```
   # If served by FastMCP / uvicorn:
   uvicorn brightwavess_monitor:app --host 127.0.0.1 --port 3000

   # Or firewall:
   ufw deny 3000/tcp
   ufw allow from 127.0.0.1 to any port 3000
   ```
3. **Audit Cloudflare DNS records** on the affected zone(s) for unauthorized changes during the exposure window.

## Reference

Full technical details + cross-cloud MCP survey context:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/commercial/mcp-cloud-survey-2026-05.md

I'm happy to answer questions or assist with verification.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
