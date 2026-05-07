---
to: abuse@akamai.com, abuse@ovh.net
cc: support@casdoor.org, abuse@nuclide-research.com
severity: HIGH
ip: 139.162.50.110, 141.95.127.178, 51.195.82.158
institution: Casdoor MCP recurring exposure — 3 instances across Linode + OVH
status: DRAFT
outcome: sent
date: 2026-05-04
---

**To:** abuse@akamai.com, abuse@ovh.net
**Cc:** support@casdoor.org, abuse@nuclide-research.com
**Subject:** Three unauthenticated Casdoor MCP servers (OAuth application-CRUD) across providers, recurring template-auth-off pattern

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-04

**Re:** Three unauthenticated `Casdoor MCP Server v1.0.0` instances exposing 5-tool OAuth/IAM application-CRUD
**IPs / Hosts:**
- `139.162.50.110:8888` (Linode US, Akamai)
- `141.95.127.178:8000` (OVH France)
- `51.195.82.158:8000` (OVH France)

**Severity:** HIGH (each individually); recurring-pattern severity is the upstream concern

---

I'm an independent security researcher conducting good-faith AI infrastructure research under the NuClide Research umbrella (CISA disclosures CVE-2025-4364, ICSA-25-140-11). This is an unsolicited coordinated-disclosure notification routed to:

1. **Akamai abuse** (for the Linode-hosted instance)
2. **OVH abuse** (for the two OVH-hosted instances)
3. **Casdoor maintainers** (CC), because the recurring pattern across three independent operators suggests a **template-auth-off-by-default** issue worth addressing upstream

---

## Summary

Three instances of `Casdoor MCP Server v1.0.0` were independently identified during NuClide Research's MCP cross-cloud survey (2026-05-04). All three return identical responses to JSON-RPC `initialize` and expose 5 tools without authentication:

```
get_applications, get_application, add_application,
update_application, delete_application
```

Casdoor is an OAuth 2.0 / SSO identity-as-a-service platform (`casdoor.org`). The MCP server wraps Casdoor's application-management API, i.e., the registration of OAuth applications that authenticate users into the operator's services. **An attacker with unauth access can:**

- **Enumerate** all OAuth applications registered with the operator's Casdoor instance
- **Modify** application configurations including `redirectUris`, the URL OAuth tokens are returned to. Pointing `redirectUris` at attacker-controlled infrastructure is an **account-takeover primitive** for any user who initiates the OAuth flow
- **Delete** applications, breaking the operator's authentication

That all three operators independently deployed the same template with the same auth-off-default suggests the upstream Casdoor MCP template ships without auth on `tools/list` invocation. Three is a small sample but the pattern is striking enough to warrant Casdoor maintainers reviewing the template's default auth posture.

Found during NuClide Research's MCP cross-cloud survey. Full case study: https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/commercial/mcp-cloud-survey-2026-05.md (search for "F7, Casdoor MCP Server").

## Confirmed exposure (each host)

`POST /` (JSON-RPC) returns valid `initialize` response with `serverInfo: {"name": "Casdoor MCP Server", "version": "1.0.0"}`. `tools/list` returns the 5-tool list above. Verification was non-destructive: only `initialize` and `tools/list` were called.

## Remediation (operator)

Bind the MCP transport to localhost or restrict via firewall:

```
# If served by FastMCP / uvicorn:
uvicorn casdoor_mcp:app --host 127.0.0.1 --port <8888 or 8000>

# Or firewall:
ufw deny <port>/tcp
ufw allow from <admin-IP> to any port <port>
```

If the MCP integration is needed for AI client tooling, route through a reverse proxy with API-key auth at the proxy layer.

## Recommendation (Casdoor maintainers)

Consider auditing the Casdoor MCP server template's default auth posture. If the template ships `tools/list` invocation without auth gating by default, the recurring pattern across operator deployments is a predictable consequence, three operators in our sample, likely many more we haven't surveyed. An auth-on default would prevent the population-scale exposure.

## Reference

Full case study + cross-cloud MCP survey context:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/commercial/mcp-cloud-survey-2026-05.md

I'm happy to answer questions or assist with verification on any of the three hosts.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
