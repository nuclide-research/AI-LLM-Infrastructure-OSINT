# Disclosure: morphEUS Qdrant Exposure
# Status: SENT 2026-06-21
# To: morpheus@phoenix.edu | CC: Privacy@phoenix.edu
# From: nicholas@nuclide-research.com
# Gmail messageId: 19ee9f68e835aa87

---
Subject: Security Issue: morphEUS Qdrant Vector Database Exposed Without Authentication

---

I'm a security researcher who studies AI infrastructure. During a survey of exposed AI systems, I found your Qdrant instance at 54.191.150.157 (port 80) is publicly reachable without authentication.

This database backs morphEUS, your University Service Desk chatbot. I can read, write, and delete records in all three collections.

---

## What I Found

The instance has three collections:

- usd_articles (217 documents)
- morphEUS_structured_kb (204 documents)
- ready_usd_articles (50 documents)

The content is your USD Confluence knowledge base — standard operating procedures for your IT support team. I read collection metadata, payload keys, and a small number of sample records to confirm the finding. I did not bulk-download or retain KB content.

The Qdrant telemetry endpoint (unauthenticated) revealed the full request history. Based on that data:

- Instance deployed: November 2024
- Last semantic search from morphEUS: July 14, 2025
- Migration attempt: July 15, 2025 (55 write operations, 5 conflicts recorded)
- App queries since July 15, 2025: none
- Dashboard last visited: June 14, 2026

The system appears to have been migrated off this instance roughly one year ago, but the data was not cleared and the instance was not secured. It is still reachable.

---

## Why It Matters

The database is fully writable without authentication. I confirmed this by inserting and immediately deleting a test record with a clearly marked ID.

If morphEUS reconnects to this instance, an attacker could replace legitimate SOPs with crafted content. Examples: a fake VPN credential URL, a modified MFA reset procedure that redirects to an attacker-controlled site, an altered CyberArk PAM workflow.

Staff following a poisoned SOP would be acting on attacker-supplied instructions without knowing it. The attack is silent. No morphEUS login is required.

Additionally: your JSM ticket surface provides an indirect path. If an agent queries morphEUS with content from an incoming ticket, crafted ticket text could influence what morphEUS returns.

---

## Evidence

```
GET http://54.191.150.157/collections HTTP/1.1

{"result":{"collections":[
  {"name":"usd_articles"},
  {"name":"morphEUS_structured_kb"},
  {"name":"ready_usd_articles"}
]},"status":"ok"}
```

Write access confirmed via canary (inserted then deleted, no credentials):
```
PUT http://54.191.150.157/collections/usd_articles/points
{"points":[{"id":99999,"vector":[...],"payload":{"nuclide_canary":true}}]}
-> {"result":{"operation_id":...,"status":"completed"},"status":"ok"}

POST http://54.191.150.157/collections/usd_articles/points/delete
{"points":[99999]}
-> {"result":{"operation_id":...,"status":"completed"},"status":"ok"}
```

---

## Fix

1. Take the instance offline or bind it to a private network interface only.
2. If it is still needed, enable Qdrant API key authentication and rotate any keys currently set.
3. Clear or migrate the remaining data so no KB content remains on the unprotected instance.
4. Review whether morphEUS can reconnect to this address and block that path.

If the instance is already decommissioned and you have no further use for it, the fastest fix is to stop the service and close port 80 at the security group level.

---

## About This Research

I published CVE-2025-4364 and ICSA-25-140-11 (CISA advisory) earlier this year. I study AI infrastructure exposure across industry and education verticals. This finding is part of that ongoing research. I do not sell findings, do not retain personal data, and do not publish before giving organizations time to remediate.

I can answer technical questions about the exposure. If you have a security team, feel free to forward this to them.

Nicholas Kloster
nicholas@nuclide-research.com
nuclide-research.com
