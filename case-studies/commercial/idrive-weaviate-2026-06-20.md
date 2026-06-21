---
type: case-study
severity: CRITICAL
date: 2026-06-20
title: "IDrive: Unauthenticated Read, Write, and Delete on the Support Chatbot Knowledge Base"
summary: "IDrive, a major US cloud backup provider, ran the Weaviate store behind its customer support chatbot with no authentication. Anyone could read all 6,894 documentation chunks, inject false guidance into the live knowledge base, or delete the entire corpus with one call. The MSP customer segment makes a poisoned encryption-recovery answer especially dangerous."
tags:
  - weaviate
  - vector-database
  - unauth
  - cwe-306
  - rag-poisoning
  - cloud-backup
sidenotes:
  - kind: host
    label: Target
    kv:
      - k: Operator
        v: "IDrive (idrive.com)"
      - k: Sector
        v: "Cloud Backup and Storage"
      - k: Location
        v: "Vultr"
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

# IDrive: Unauthenticated Read, Write, and Delete on the Support Chatbot Knowledge Base

_NuClide Research -- Nicholas Kloster -- 2026-06-20_

---

## Summary

IDrive is a major US cloud backup and storage provider. The Weaviate vector database behind its customer support chatbot ran on the public internet with no authentication. Anyone could read the full knowledge base, write false guidance into it, or delete the whole corpus with a single request.

The chatbot serves consumers, enterprises, and managed service providers. A poisoned answer about encryption-key recovery, served to an MSP managing hundreds of endpoints, is the worst case here.

We confirmed read, write, and delete. We wrote one marked canary and removed it.

---

## Attack Surface

One host. One open port. No authentication.

| Port | Software | Role | Auth |
|------|----------|------|------|
| 8080 | Weaviate 1.28.5 | Vector store behind the IDrive customer support chatbot | None |

The host is 45.32.137.116 on Vultr. Node health reported `lastSnapshotIndex: 0`, so there is no recovery point.

---

## Data Exposed

One class, 6,894 records.

| Class | Records | Content |
|-------|---------|---------|
| Chatbot | 6,894 | IDrive product documentation, chunked for the RAG chatbot |

Coverage spans every product line: consumer backup, S3-compatible object storage (e2), MSP endpoint protection (IDrive 360), bare-metal disaster recovery, Microsoft 365, and Google Workspace. Operator attribution comes from the records themselves. Tags name IDrive products verbatim and URLs point to idrive.com and idriveonlinebackup.com.

We read the schema and confirmed the record count. We did not exfiltrate the corpus.

---

## What We Confirmed

**Read:** Schema and all 6,894 records returned over plain HTTP, no credentials.

**Write:** A marked canary was accepted into the Chatbot class and returned a success status.

**Delete:** The canary was removed with a 204 and confirmed gone with a 404 on re-fetch.

Canary UUID `4d6eb750-cf8d-40a2-9c48-0c70b6c99b23`. Written, confirmed, deleted, verified. Every change reversed.

---

## Impact

**Knowledge base exfiltration:** The complete 6,894-chunk chatbot corpus across every product line is readable by anyone, including internal product descriptions not necessarily on the public site.

**Customer-facing poisoning:** IDrive runs a live customer chatbot on this store. Injecting false technical guidance causes real customers to receive attacker-controlled answers when they ask about features, encryption, or recovery. The MSP segment is the high-value target. A poisoned encryption-key-recovery answer could route a managed fleet toward attacker-controlled infrastructure. No authentication is required to plant it.

**Chatbot outage:** One delete call against the class destroys all 6,894 chunks. With no snapshot configured, the chatbot returns empty on every query until the corpus is re-ingested.

---

## Remediation

**Immediate (no code change):** Firewall port 8080 to the internal network only.

**Short-term:** Enable Weaviate API-key authentication. Add request logging. Configure snapshots so the store has a recovery point.

**Medium-term:** Add canary records and retrieval-distribution monitoring to detect unauthorized writes before customers see poisoned answers.

---

## Disclosure

Finding documented 2026-06-20 under NuClide Research responsible-disclosure practice. Prior coordinated disclosures from this researcher include CVE-2025-4364 and ICSA-25-140-11, both through CISA.
