---
type: case-study
severity: CRITICAL
date: 2026-06-20
title: "FCE STA. ISABEL and Verto Inspect: Unauthenticated Read, Write, and Delete on a Shared Weaviate Node"
summary: "A single unprotected Weaviate node on Contabo hosted two tenants: a medical center's vectorized clinical database schema and an unreleased insurance product's multi-agent development logs. We confirmed unauthenticated read, write, and delete with a reversed canary. Schema exposure hands an attacker the full query blueprint for a healthcare production database."
tags:
  - weaviate
  - vector-database
  - unauth
  - cwe-306
  - medical-clinical
  - healthcare
sidenotes:
  - kind: host
    label: Target
    kv:
      - k: Operator
        v: "FCE STA. ISABEL / Verto Inspect"
      - k: Sector
        v: "Healthcare / Insurance Software"
      - k: Location
        v: "Contabo GmbH, Germany"
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

# FCE STA. ISABEL and Verto Inspect: Unauthenticated Read, Write, and Delete on a Shared Weaviate Node

_NuClide Research -- Nicholas Kloster -- 2026-06-20_

---

## Summary

One Weaviate node at 147.93.180.34:8080 ran with no authentication. Two unrelated tenants shared it. The first is FCE STA. ISABEL, a physiotherapy and specialty medical center that vectorized the full relational schema of its clinical database for an AI query assistant. The second is Verto Inspect, an unreleased insurance inspection product whose multi-agent development logs sit in the same store.

Anyone on the internet could read every class, every record, and every schema description. They could also write new objects and delete existing ones. We confirmed all three operations and reversed the one change we made.

The clinical schema is the attack blueprint for a healthcare production database. Table names, column definitions, foreign keys, and stored procedure logic for patient radiology and physical examination records are readable with zero reconnaissance.

---

## Attack Surface

| Port | Software | Role | Auth |
|------|----------|------|------|
| 8080 | Weaviate 1.27.9 | Multi-tenant RAG vector database | None |

Two distinct tenants colocated on a single unprotected node. The REST API answered every request without a credential.

---

## What We Confirmed

CONFIRMED: unauthenticated read, write, and delete.

**Read:** `GET /v1/schema` returned the full class list (200 OK). `GET /v1/objects?class=DB_Schema` and `GET /v1/objects?class=ProjectArchive` returned records (200 OK).

**Write:** `POST /v1/objects` inserted a marked canary object into class `DB_Schema` (200 OK). Canary UUID `90a88cf5-29f6-426a-b035-cc2a19f0d2b1`, object name `CANARY_nuclide_2026_06_20`.

**Delete:** `DELETE /v1/objects/DB_Schema/90a88cf5-29f6-426a-b035-cc2a19f0d2b1` returned 204 No Content. A follow-up `GET` for the same UUID returned 404 Not Found, confirming removal.

The only object we created we deleted. We verified the deletion. No operator data was altered.

---

## Data Exposed

The store held five populated classes across two tenants. We enumerated class names, object counts, and property schemas. We did not exfiltrate records. Class names, schema names, and the structure of the data are the finding.

| Class | State | Tenant | Content |
|-------|-------|--------|---------|
| DB_Schema | populated | FCE STA. ISABEL | Full relational schema of the clinical database |
| Academico | populated | shared / academic | Academic book and chapter content |
| RAG_Academico | populated | shared / academic | Academic RAG chunks |
| RAG_Academico2 | populated | shared / academic | Academic RAG chunks, second corpus |
| ProjectArchive | populated | Verto Inspect | Multi-agent conversation and development logs |

**DB_Schema (FCE STA. ISABEL).** Properties include `context_database_id`, `object_id`, `object_name`, `object_type`, `schema_name`, `description`, `texto_embedding`, and `columns_text`. Each schema object carries a full Spanish-language description of its clinical purpose. The enumerated object types span TABLE, VIEW, and PROCEDURE. Object names confirm patient radiology and imaging tables, doctor-to-specialty assignment tables, and stored procedures for physical examination records keyed on a `PACIENTE_ID` patient identifier column. The presence of patient-identifier columns confirms the underlying clinical data class without reading any patient record.

**ProjectArchive (Verto Inspect).** Properties include `projectId`, `phaseId`, `agentType`, `messageType`, `content`, `approvedBy`, `createdAt`, and `sqlRefId`. Agent roles are ProductOwner, ScrumMaster, and AgentDB. Content classes are sprint planning outputs, BDD user story criteria, and database schema design decisions for insurance claim management workflows. This is the complete development record of an unreleased product.

Data class at risk: healthcare clinical database schema (medical clinical) plus pre-release insurance product intellectual property.

---

## Impact

**Healthcare schema exposure.** The full relational schema of FCE STA. ISABEL's clinical database is readable without authentication. An attacker recovers exact table names, column definitions, foreign key relationships, and stored procedure logic for patient radiology records, physical examination appointments, and doctor-specialty assignments. Any production database that is exposed or laterally reachable becomes queryable with zero reconnaissance, because the schema is the map.

**Regulatory.** Schema exposure of a healthcare operator's clinical database carries obligations under local health data protection law. The exposed `PACIENTE_ID` column confirms a patient records table exists in production and bounds the scope of the underlying patient data.

**AI knowledge base poisoning.** Write access to `DB_Schema` allows injection of false schema descriptions. Clinical staff using the AI query assistant would receive incorrect table or column guidance. In a medical context a poisoned schema entry that points a clinical query at the wrong table or stored procedure is a patient safety issue, not only a data integrity issue.

**Insurance product IP theft.** The `ProjectArchive` agent logs expose the full system architecture, BDD requirements, schema decisions, and sprint outputs for an unreleased insurance inspection product. A competitor recovers the complete product specification at zero cost.

---

## Remediation

**Immediate:** Firewall port 8080 to the internal network only. The node should not be reachable from the public internet.

**Short-term:** Enable Weaviate authentication. Weaviate supports API-key and OIDC authentication; the node is currently running with anonymous access enabled. Separate the two tenants onto isolated instances rather than a shared anonymous node.

**Medium-term:** Add canary records and write monitoring to the production vector store to detect unauthorized writes. Audit any production clinical database for direct or laterally reachable exposure now that its schema is public.

---

## Disclosure

Finding documented 2026-06-20 under NuClide Research responsible-disclosure practice. Prior coordinated disclosures from this researcher include CVE-2025-4364 and ICSA-25-140-11, both through CISA.
