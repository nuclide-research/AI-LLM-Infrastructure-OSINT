---
to: abuse@ovh.net
cc: security@alcy.fr, abuse@nuclide-research.com
severity: CRITICAL
ip: 188.165.203.72
institution: Alcy SAS / OVH SAS (alcy.fr field-service CRM exposed via MCP server) — FOLLOW-UP after 2026-05-04 cc bounce
status: DRAFT
outcome: sent
date: 2026-05-06
---

**To:** abuse@ovh.net
**Cc:** security@alcy.fr, abuse@nuclide-research.com
**Subject:** Follow-up, Unauthenticated Alcy CRM MCP server still live (188.165.203.72:8000); 2026-05-04 cc to contact@alcy.fr bounced

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-06

**Re:** Follow-up to 2026-05-04 disclosure of unauthenticated Alcy MCP Simple v3.2.0 server
**IP / Host:** 188.165.203.72 (rDNS `ns310744.ovh.net`, OVH dedicated server, France)
**Severity:** CRITICAL
**Reference:** Original disclosure thread sent to `abuse@ovh.net` on 2026-05-04 (subject: "Unauthenticated Alcy CRM MCP server (22-tool customer/work-order CRUD) on OVH dedicated server, 188.165.203.72:8000")

---

This is a follow-up to the 2026-05-04 coordinated-disclosure notification regarding `188.165.203.72:8000`. Two new pieces of context warrant a re-touch:

**1. The original `cc: contact@alcy.fr` address bounced.** That guess-address did not deliver, so the operator-side notification did not reach Alcy SAS. I am re-sending with `cc: security@alcy.fr` (re-resolved via WHOIS + pattern-guess against the `alcy.fr` MX record). If `security@alcy.fr` also bounces, the operator-direct path is OVH's customer-notification channel, please consider this email an explicit request to forward to the OVH customer who controls IP `188.165.203.72`.

**2. The exposure remains live as of 2026-05-06.** Re-probe today confirms `Alcy MCP Simple v3.2.0` still responds to `initialize` and `tools/list` without authentication, exposing the same 22 tools (15 read, 7 mutate, including `create_ticket`, `create_ordre_mission`, `create_intervention`, `patch_ticket`, `patch_ordre_mission`, `patch_intervention`).

Original technical detail and reproduction steps:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/commercial/mcp-cloud-survey-2026-05.md (search "F0a, Alcy MCP Simple")

Original disclosure draft (with full tool list, mutation surface analysis, and remediation steps):
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/disclosures/OVH-188-165-203-72-alcy-crm.md

---

## Summary (refresher)

An OVH dedicated-server customer at `188.165.203.72:8000` is running an unauthenticated **Model Context Protocol (MCP) server** identifying itself as `Alcy MCP Simple v3.2.0`. The server exposes 22 tools mapping to admin operations on what appears to be a deployment of [alcy.fr](https://alcy.fr), a French field-service / facility-management SaaS, as a JSON-RPC API readable + writable by any unauthenticated internet caller.

**Mutate tools (record creation + modification):**
- `add_evt`, `patch_ticket`, `patch_ordre_mission`, `patch_intervention`
- `create_ticket`, `create_ordre_mission`, `create_intervention`

**Read tools (CRM data exfil):**
- `search_clients`, `search_installations`, `search_ordre_mission`, `search_intervention`, `search_contact`, `search_user`, `search_agence`, `search_ticket`, `search_produit`, `search_installation_produit`, `search_contrat_produit`, `search_intervention_produit`, `search_evts`, `get_entity_history`, `get_server_datetime`

For a French customer-facing SaaS, this constitutes a significant data-protection / GDPR-relevant exposure. **The mutation primitives elevate this to CRITICAL**, an unauthenticated attacker can inject fake work orders, modify existing tickets, or alter intervention records without leaving an audit trail attributable to a specific user.

---

## Remediation (for the customer)

```
# Bind to localhost or restrict at firewall
uvicorn alcy_mcp:app --host 127.0.0.1 --port 8000
# or
ufw deny 8000/tcp
ufw allow from <admin-IP> to any port 8000
```

For AI-client integration, route through a reverse proxy with API-key auth at the proxy layer, the MCP protocol itself does not require auth at the transport, so auth-on-default is the operator's responsibility.

---

## Outstanding action (OVH side)

Per OVH's standard abuse-handling process, customer notification typically requires either:
1. OVH's internal customer-notification channel (acting on this email), OR
2. Submission via the OVH abuse web form at https://www.ovh.com/abuse/

If a web-form submission is required to advance customer notification, please indicate that in reply and I will fill the form with the same case content.

I'm available for any clarification or verification questions.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
