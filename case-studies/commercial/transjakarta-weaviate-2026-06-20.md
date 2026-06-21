---
type: case-study
severity: CRITICAL
date: 2026-06-20
title: "TransJakarta: Unauthenticated Read, Write, and Delete on the Jakarta Transit Chatbot Knowledge Base"
summary: "TransJakarta's Weaviate vector store backing the Tara transit chatbot was open with no authentication. Read, write, and delete were all confirmed across 86 records in three knowledge-base classes. A marked canary was written, deleted, and verified gone, proving full control of the data that answers millions of Jakarta commuters."
tags:
  - weaviate
  - vector-database
  - unauth
  - cwe-306
  - transit-chatbot-knowledge-base
  - public-transit
sidenotes:
  - kind: host
    label: Target
    kv:
      - k: Operator
        v: "TransJakarta (PT Transportasi Jakarta)"
      - k: Sector
        v: "Public Transit"
      - k: Location
        v: "Google Cloud Platform"
      - k: Severity
        v: CRITICAL
  - kind: see-also
    label: Classification
    kv:
      - k: Primary
        v: "CWE-306 Missing Authentication for Critical Function"
      - k: Secondary
        v: "CWE-284 Improper Access Control"
      - k: OWASP
        v: "LLM04 Data and Model Poisoning"
---

# TransJakarta: Unauthenticated Read, Write, and Delete on the Jakarta Transit Chatbot Knowledge Base

_NuClide Research -- Nicholas Kloster -- 2026-06-20_

---

## Summary

TransJakarta's Weaviate vector store sat on the public internet with no authentication. The store holds the knowledge base for "Tara," the chatbot that answers commuter questions about routes, fares, and policies. Anyone could read the full knowledge base, write new records, or delete the entire store.

TransJakarta runs the Jakarta Bus Rapid Transit network. It is the largest BRT system in the world by fleet size, serving more than 10 million passengers a year.

We confirmed read, write, and delete. We wrote a marked canary record, deleted it, and verified it was gone. We reversed every change we made.

---

## Attack Surface

| Port | Software | Role | Auth |
|------|----------|------|------|
| 8080 | Weaviate 1.31.2 | Vector store backing the Tara transit chatbot, 86 records across 3 classes | None |

Host 35.240.155.175 on Google Cloud Platform. The node reported HEALTHY, version 1.31.2, with `lastSnapshotIndex: 0` -- no recovery point configured.

---

## What We Confirmed

**Read:** Pulled all 86 records across the three knowledge-base classes without credentials. HTTP 200.

**Write:** Inserted a record into `Tj_dhai_kb`. HTTP 200.

**Delete:** Removed an object by ID. HTTP 204. Re-queried the ID and got 404, confirming the delete took effect.

We wrote canary `2e00b9bf-4cc2-4608-9f59-898909d3850d` to `Tj_dhai_kb`, deleted it with HTTP 204, and re-queried the ID for HTTP 404. Every test artifact we created we removed.

---

## Data Exposed

The store held 86 records across three classes.

| Class | Records | Content |
|-------|---------|---------|
| B62b91p9su1_kb | 32 | TransJakarta chatbot knowledge base (set A) |
| Bip93b47vgp_kb | 22 | TransJakarta chatbot knowledge base (set B) |
| Tj_dhai_kb | 32 | TransJakarta chatbot knowledge base (set C, main) |

Three parallel classes suggest multiple knowledge-base versions or chatbot deployments.

The `Tj_dhai_kb` schema is two text fields:

```
title    text    FAQ/topic title
context  text    full answer text (Bahasa Indonesia)
```

The records are operational chatbot content: route descriptions for Jakarta BRT corridors, fare and payment policy, tenant leasing instructions, and photography rules. The content references official TransJakarta policies, the "Tara" chatbot persona, and the contact email marketing@transjakarta.co.id. This is public-facing FAQ text, not personal records.

Operator attribution rests on four anchors. The `Tj` class prefix names TransJakarta. The records reference "Transjakarta" and "Tara" by name. They list Jakarta BRT corridor routes. They carry the official marketing@transjakarta.co.id contact email.

---

## Impact

**Write, misinformation to 10 million annual passengers.** Tara is the primary digital information channel for Jakarta's BRT network. Inject false fare prices, route changes, or payment-policy records and the chatbot serves that misinformation to commuters. Bad guidance on payment methods, station status, or emergency procedures can cause real harm. Passengers get stranded. Fare-collection instructions become fraud.

**Write, contact-detail manipulation.** The knowledge base carries official TransJakarta contact details. Injecting fake contact records redirects passengers with complaints, lost-property queries, or emergency reports to attacker-controlled channels.

**Delete, chatbot outage.** 86 records across 3 classes can be wiped in three HTTP calls. Tara returns empty on every query until the data is re-ingested.

---

## Remediation

**Immediate:** Firewall port 8080 to the internal network only. No code change required.

**Short-term:** Enable Weaviate's built-in API-key or OIDC authentication so read, write, and schema operations require credentials.

**Medium-term:** Add canary records and retrieval monitoring to detect unauthorized writes. Configure snapshots so a wiped store has a recovery point, given `lastSnapshotIndex` was 0.

---

## Disclosure

Finding documented 2026-06-20 under NuClide Research responsible-disclosure practice. Prior coordinated disclosures from this researcher include CVE-2025-4364 and ICSA-25-140-11, both through CISA.
