---
to: abuse@ovh.net
cc: abuse@nuclide-research.com
severity: CRITICAL
ip: 51.75.128.16
institution: OVH SAS (hosted operator unknown; ns3131695.ip-51-75-128.eu)
status: DRAFT
date: 2026-05-04
---

**To:** abuse@ovh.net
**Cc:** abuse@nuclide-research.com
**Subject:** Unauthenticated Gmail mailbox MCP server on OVH VPS — 51.75.128.16:3000

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-04

**Re:** Unauthenticated Gmail mailbox Model Context Protocol server on customer VPS
**IP / Host:** 51.75.128.16 (rDNS `ns3131695.ip-51-75-128.eu`, OVH SD-1G-GRA2-G222)
**Severity:** CRITICAL

---

I'm an independent security researcher. I hold CISA disclosures CVE-2025-4364 and ICSA-25-140-11 and conduct good-faith AI infrastructure research under the NuClide Research umbrella. This is an unsolicited disclosure — no engagement exists with your organization, and I have not accessed, modified, or exfiltrated any data beyond what was necessary to confirm the exposure.

---

## Summary

A customer of OVH at `51.75.128.16:3000` is running an unauthenticated **Gmail Model Context Protocol (MCP) server** that exposes the operator's own Gmail mailbox as a 19-tool API readable + writable + destructive by any unauthenticated internet caller.

This finding was surfaced as part of NuClide Research's cross-cloud Model Context Protocol survey (2026-05-04). Full case study: https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/commercial/mcp-cloud-survey-2026-05.md

---

## Confirmed exposure

`POST /` (JSON-RPC 2.0) returns a successful `initialize` response identifying the server as `gmail v1.0.0`. A subsequent `tools/list` enumerates 19 callable tools, all of which mutate or read mailbox state:

```
send_email, draft_email, read_email, search_emails, modify_email, delete_email,
list_email_labels, batch_modify_emails, batch_delete_emails,
create_label, update_label, delete_label, get_or_create_label,
create_filter, list_filters, get_filter, delete_filter, create_filter_from_template,
download_attachment
```

The server requires no authentication on the JSON-RPC handshake. Verification was non-destructive: only the `initialize` and `tools/list` JSON-RPC methods were called, no mailbox content was read, no messages were sent, no filters were created.

---

## Why it matters

The exposed MCP server represents **complete remote control** of the operator's Gmail account by any unauthenticated caller. Specifically:

- **Read:** `read_email`, `search_emails`, `download_attachment` — full mailbox read access
- **Write:** `send_email`, `draft_email` — ability to send outbound mail as the operator (impersonation, phishing-source vector)
- **Destructive:** `delete_email`, `batch_delete_emails`, `delete_label`, `delete_filter` — irreversible mailbox modification
- **Lateral:** `create_filter` — attacker can configure forwarding/redirection of incoming mail to attacker-controlled addresses

The operator likely intends this MCP server for their own private use (Claude Desktop, Cursor, or similar AI client integration) but has bound it to `0.0.0.0` instead of localhost.

---

## Remediation (operator)

Bind the MCP server to loopback only:

```
# Whatever process serves the MCP HTTP+SSE endpoint, restrict to 127.0.0.1
# Example (if Node/Python server):
HOST=127.0.0.1 PORT=3000 node mcp-gmail-server.js
```

Alternatively, restrict access via firewall:

```
ufw deny 3000/tcp
ufw allow from 127.0.0.1 to any port 3000
```

---

## OVH AUP applicability

OVH's AUP and TOS prohibit operating servers that expose unauthenticated administrative interfaces, regardless of operator intent. This MCP server, while presumably configured for the operator's own AI-tooling use, exposes Gmail mailbox CRUD without authentication on a public OVH IP — meeting the standard "exposed administrative service" criterion.

I leave the AUP determination to OVH; reporting the exposure for awareness and customer-notification.

---

## Reference

Full technical details, full tool list, and methodology in this public research repository:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/commercial/mcp-cloud-survey-2026-05.md

(Search for "F0 — Unauthenticated full Gmail mailbox MCP" in the document.)

I'm happy to answer questions or assist with verification. No response is required.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
