---
type: case-study
severity: HIGH
date: 2026-06-20
title: "Italian Coding-Education Chatbot: Unauthenticated Read, Write, and Delete on a Weaviate Knowledge Base"
summary: "A Weaviate vector store on a Hetzner host served the knowledge base of an Italian-language coding-education chatbot with no authentication. We confirmed unauthenticated read, write, and delete on 32 records across two classes. Write access allows poisoning beginner-programmer guidance; all test artifacts were reversed."
tags:
  - weaviate
  - vector-database
  - unauth
  - cwe-306
  - educational-content
  - commercial
sidenotes:
  - kind: host
    label: Target
    kv:
      - k: Operator
        v: "Unattributed SaaS (Hetzner Online)"
      - k: Sector
        v: "Education / Coding Chatbot SaaS"
      - k: Location
        v: "Hetzner Online"
      - k: Severity
        v: HIGH
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

# Italian Coding-Education Chatbot: Unauthenticated Read, Write, and Delete on a Weaviate Knowledge Base

_NuClide Research -- Nicholas Kloster -- 2026-06-20_

---

## Summary

A Weaviate vector database at 5.78.79.3 served the knowledge base for an Italian-language coding-education chatbot. The instance had no authentication. Anyone on the internet could read, write, and delete the records that feed the chatbot's answers to learners.

The content is not high-sensitivity. It is programming Q&A in Italian plus public course material scraped from Codecademy. The risk is not data theft. It is data tampering. A false answer about syntax, variable types, or language choice misleads a beginner who has no way to tell a poisoned record from a correct one.

We confirmed read, write, and delete. We reversed every change we made.

---

## Attack Surface

| Port | Software | Role | Auth |
|------|----------|------|------|
| 8080 | Weaviate 1.33.5 | Vector database -- coding-chatbot knowledge base | None |

The host is on Hetzner Online. The Weaviate REST and GraphQL API answered without a key.

---

## What We Confirmed

**Read:** Pulled all 32 records across two classes without credentials. HTTP 200.

**Write:** Inserted records into the knowledge base. HTTP 200.

**Delete:** Removed records. HTTP 204.

Read, write, and delete were all exercised and confirmed against the live store. Every test artifact we created we removed.

---

## Data Exposed

The store held two classes, 32 records total.

| Class | Records | Content |
|-------|---------|---------|
| ChatbotKnowledgeBase | 29 | Italian-language programming Q&A pairs |
| SecurityTest | 3 | Batch processing queue records |

`ChatbotKnowledgeBase` schema: three text fields -- `botId` (bot identifier, CUID), `sourceId` (source chunk identifier, CUID), and `content` (Q&A pair or documentation chunk). The records belong to a single bot. The content is beginner programming Q&A in Italian plus material scraped from Codecademy's "Coding Fundamentals" course covering 78 languages.

`SecurityTest` schema: a single `batch_id` text field holding batch-processing queue identifiers. No sensitive content.

The CUID identifier pattern (cmk3 prefix) matches an earlier generation of IDs seen on a separate Russian-language chatbot SaaS platform, which suggests a shared underlying SaaS serving Italian-language customers. No personal records, credentials, or customer rows were published. The class names, schema, and record counts are the finding.

---

## Impact

**Read:** Full read exfiltrates the chatbot's knowledge base. The content is low-sensitivity, but the corpus composition is competitor intelligence on how the chatbot is built and sourced.

**Write:** This is the load-bearing risk. Injecting false or deliberately incorrect answers poisons the chatbot's responses to learners. Wrong guidance about syntax errors, variable types, or which language to start with misleads beginner programmers who trust the bot as a teaching tool. A learner has no way to distinguish a tampered answer from a real one.

**Delete:** Delete access removes legitimate guidance quietly. The knowledge base degrades with no alert.

---

## Remediation

**Immediate:** Firewall port 8080 to the internal network only. No code change required.

**Short-term:** Enable Weaviate's API-key or OIDC authentication. Disable anonymous access. Add audit logging on write and delete operations.

**Medium-term:** Seed canary records in the production store to detect unauthorized writes. Monitor record counts and class membership for unexpected changes.

---

## Disclosure

Finding documented 2026-06-20 under NuClide Research responsible-disclosure practice. Prior coordinated disclosures from this researcher include CVE-2025-4364 and ICSA-25-140-11, both through CISA.
