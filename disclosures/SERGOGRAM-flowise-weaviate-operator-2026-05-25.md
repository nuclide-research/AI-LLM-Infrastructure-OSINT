---
to: abuse@contabo.com
cc: abuse@nuclide-research.com
severity: CRITICAL
ip: 37.60.255.27
institution: "SerGoGram / gpt.sergogram.com operator — Flowise + Weaviate unauthenticated. Operator identity not confirmed (WHOIS privacy-protected). Contabo GmbH hosting abuse channel used as contact of last resort. Contains client credentials from blutspende.net (German blood donation org) and emovis-tag.co.uk (UK toll road service)."
status: DRAFT
outcome: pending
date: 2026-05-25
note: "Operator contact not found — sergogram.com WHOIS privacy-protected, no security.txt, no GitHub, no social profiles. Disclosing via Contabo abuse channel. Primary victim disclosure sent separately to info@blutspende.net."
---

**To:** abuse@contabo.com
**Cc:** abuse@nuclide-research.com
**Subject:** CRITICAL: Unauthenticated AI database on 37.60.255.27 (gpt.sergogram.com) exposes client credentials — recommend takedown or operator notification

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-25

---

This is an urgent abuse report. The server at **37.60.255.27** (hosted on Contabo GmbH infrastructure) is running an unauthenticated Weaviate vector database on port 8080 that contains plaintext credentials and internal IT documentation from a client organization.

---

## What we found

**Service:** Weaviate 1.23.5, port 8080, no authentication
**Host:** 37.60.255.27 (Contabo Nuremberg), also accessible via gpt.sergogram.com
**Data confirmed in the database:**

The database contains internal IT documents from a German blood donation organization (domain: blutspende.net), including:
- Plaintext server login credentials
- Internal server names and IP addresses
- BitLocker PIN conventions
- Blood donation operational records
- Network architecture details

A second set of documents from emovis-tag.co.uk (UK toll road service) is also present.

**This data has been open to the public internet since at least August 2024.**

---

## What we are asking

We have not been able to identify the operator of gpt.sergogram.com directly (WHOIS is privacy-protected, no contact information surfaced). We are asking Contabo to:

1. Contact the server operator (37.60.255.27) and request they take the Weaviate instance offline or restrict access.
2. If the operator cannot be reached, consider taking the server offline to prevent further exposure of client credential data.

We have already notified the affected client organization (blutspende.net) directly.

---

## About NuClide Research

NuClide Research is an independent security research organization (Denver, CO, USA). CISA disclosures: CVE-2025-4364, ICSA-25-140-11. This report is made in good faith under responsible disclosure practices.

Nicholas Michael Kloster
nicholas@nuclide-research.com
nuclide-research.com
