---
type: case-study
severity: CRITICAL
date: 2026-06-20
title: "US University Oracle Fusion ERP AI Assistant: Unauthenticated Read, Write, and Delete on the RAG Knowledge Base"
summary: "A US higher education institution exposed the Weaviate vector store backing an AI assistant that writes SQL against a live Oracle Fusion ERP. The store held 24 classes and roughly 8,900 records mapping the internal Oracle schema for payroll, finance, supply chain, and Title IV student aid. We confirmed unauthenticated read, write, and delete, and reversed every change with a canary."
tags:
  - weaviate
  - vector-database
  - unauth
  - cwe-306
  - student-financial-aid
  - higher-education
abstract: "An AI assistant for a US university generates SQL queries against a live Oracle Fusion ERP. Its RAG knowledge base ran on a Weaviate 1.35.2 instance with no authentication, publicly reachable on Azure. The store mapped the internal Oracle Fusion schema for HCM, Finance, SCM, and Student Financial Planning, plus an ExpertCorrections class the AI treats as ground truth. We confirmed unauthenticated read, write, and delete, and reversed every change. Documented 2026-06-20."
sidenotes:
  - kind: host
    label: Target
    kv:
      - k: Operator
        v: "US higher education institution"
      - k: Sector
        v: "Higher Education / Oracle Fusion ERP"
      - k: Location
        v: "Microsoft Azure"
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
        v: "LLM02 Sensitive Information Disclosure"
      - k: OWASP
        v: "LLM04 Data and Model Poisoning"
---

# US University Oracle Fusion ERP AI Assistant: Unauthenticated Read, Write, and Delete on the RAG Knowledge Base

_NuClide Research -- Nicholas Kloster -- 2026-06-20_

---

## Summary

A US university runs an AI assistant that generates SQL queries against a live Oracle Fusion ERP. The RAG knowledge base behind that assistant ran on a Weaviate 1.35.2 instance with no authentication, publicly reachable on Microsoft Azure at 20.228.169.116:8080.

The store held 24 classes and roughly 8,900 records. They map the internal Oracle Fusion schema for HCM (HR and payroll), Finance, Supply Chain, and Student Financial Planning, which covers Title IV federal aid. It also holds an ExpertCorrections class that the AI reads as authoritative ground truth when it writes SQL.

We confirmed unauthenticated read, write, and delete. We reversed every change we made with a marked canary.

---

## Attack Surface

| Port | Software | Role | Auth |
|------|----------|------|------|
| 8080 | Weaviate 1.35.2 | RAG vector store -- 24 classes, ~8,900 records mapping the Oracle Fusion schema | None |

The instance ran 35 enterprise integration modules (Anthropic, OpenAI, AWS, Google, Cohere, Mistral, NVIDIA, xAI, JinaAI, VoyageAI, Databricks, FriendliAI, Contextual AI, Anyscale, OctoAI, Morph, HuggingFace, plus multimodal and reranker variants). The node reported `operationalMode: ReadWrite` and `lastSnapshotIndex: 0`, meaning no Weaviate-side recovery point.

---

## What We Confirmed

**Read:** Pulled all 24 classes and their objects without credentials. `/v1/meta` returned version 1.35.2. Class queries against FusionSQLKnowledge and ExpertCorrections returned full property contents at HTTP 200.

**Write:** Inserted a marked canary into ExpertCorrections via `/v1/batch/objects`. The batch response returned `result.status: SUCCESS` at HTTP 200.

**Delete:** Removed the canary object via `DELETE /v1/objects/ExpertCorrections/<uuid>`, which returned HTTP 204.

Canary `189bdfa3-208e-43a1-8549-677aadf5b8e4` was written to ExpertCorrections, confirmed, and deleted. Schema wipe was not tested. Every test artifact we created we removed.

---

## Data Exposed

The store held 24 classes and roughly 8,900 records. These are schema and knowledge artifacts, not personal records. The classes are the finding.

| Class | Records | Content |
|-------|---------|---------|
| OsmGetEndpoint | 1,539 | Oracle REST API endpoint catalog |
| HCMTablesApr26Json | 2,729 | Oracle Fusion HCM table and view schemas (Apr 2026) |
| Scmviewsjson | 1,371 | SCM database view definitions |
| Finviewsjson | 887 | Finance view definitions |
| Hcmviewsjson | 690 | HCM view definitions |
| Reportmetadatav18 | 531 | Report definitions (latest version) |
| FusionSQLKnowledge | 103 | SQL query knowledge (payroll, HR, comp, procurement) |
| OracleStudentKnowledge_v3 | 65 | Oracle student management knowledge |
| ExpertCorrections | 11 | Human expert behavior corrections |
| Rpt_agent_kb_summary_20march | 5 | Report agent knowledge summaries |
| Reportmetadatav1..v17 | varies | Versioned report metadata (17 prior versions) |

The sensitive slices are schema maps, not raw records:

- **FusionSQLKnowledge** describes internal payroll tables (Calculation Card detail values, statutory deductions, tax calculations, garnishments) and their Oracle column structure.
- **ExpertCorrections** is the AI behavior control surface. The AI reads these 11 records as authoritative ground truth for how to write SQL.
- **Student Financial Planning views** name FSEOG allocation, R2T4 Return to Title IV calculation, NSLDS federal student loan, and IPEDS federal enrollment reporting views.
- **Student report definitions** name enrollment, ethnicity, gender, diversity, and student age profile reports.

Evidence of operator type: the `sfp` product with FSEOG, R2T4, NSLDS, and IPEDS views (US federal financial aid reporting), OracleStudentKnowledge classes with Higher Education Development API endpoints, the Oracle Fusion FUSION schema and FUSION_TS_SEED tablespace, and a source path of `D:\rag_documents2\hcm\` on a Windows dev machine.

No personal records, names, SSNs, or student data are published here. The store maps where that data lives in the live Oracle Fusion ERP; it does not hold the records themselves.

---

## Impact

**Read -- internal Oracle Fusion schema map.** The full internal database structure for payroll, HR, finance, supply chain, and student financial aid. An attacker learns the exact column names needed to query salaries, tax withholdings, student loan balances, and grant allocations against the live ERP.

**Read -- 1,539 Oracle API endpoints.** The complete REST API surface of the university's Oracle Fusion deployment, every endpoint path and resource name. Useful to enumerate misconfigured or unauthenticated Oracle REST endpoints on the live ERP.

**Write -- ExpertCorrection poisoning.** The AI reads ExpertCorrections as authoritative ground truth. An attacker can inject an instruction that causes the AI to add sensitive columns to every payroll query run by legitimate users. This is indirect exfiltration. The attacker does not query Oracle directly. The legitimate user does, and the AI hands the attacker-influenced result back through the normal channel.

**Write -- SQL knowledge poisoning.** False table mappings injected into FusionSQLKnowledge cause the AI to generate malicious or incorrect SQL for real users.

**Delete -- knowledge base destruction.** Deleting the knowledge classes makes the AI assistant return empty or wrong answers on all queries. With `lastSnapshotIndex: 0`, there is no Weaviate-side recovery point. Recovery requires rebuilding from the source files at `D:\rag_documents2\`.

Regulatory exposure spans Title IV and FERPA for student financial aid, FERPA for enrollment and diversity reporting, and trade-secret or IP exposure for the internal Oracle Fusion schema.

---

## Remediation

**Immediate:** Firewall port 8080 to internal network only. No code change required.

**Short-term:** Enable Weaviate API-key or OIDC authentication. Set the instance to require credentials on every endpoint. Rotate any AI provider API keys configured in the 35 integration modules, since module config can leak keys through an open instance.

**Medium-term:** Add canary records to the production vector store to detect unauthorized writes. Monitor retrieval distribution to catch ranking anomalies from poisoned records. Configure Weaviate snapshots so a recovery point exists; the current `lastSnapshotIndex: 0` leaves no rollback path.

---

## Disclosure

Finding documented 2026-06-20 under NuClide Research responsible-disclosure practice. Prior coordinated disclosures from this researcher include CVE-2025-4364 and ICSA-25-140-11, both through CISA.
