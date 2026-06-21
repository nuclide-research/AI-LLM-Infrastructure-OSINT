---
type: case-study
severity: CRITICAL
date: 2026-06-20
title: "yuno.education: Unauthenticated Read, Write, and Delete on the Weaviate RAG Backend of an AI School Tutor"
summary: "yuno.education ran a Weaviate vector store as the RAG backend for its AI tutor with no authentication. We confirmed unauthenticated read, write, and delete against ~1,989 lesson records that include complete classroom answer keys. A reversed canary verified all three primitives."
tags:
  - weaviate
  - vector-database
  - unauth
  - cwe-306
  - education-curriculum
  - edtech
sidenotes:
  - kind: host
    label: Target
    kv:
      - k: Operator
        v: "yuno.education"
      - k: Sector
        v: "Education / EdTech"
      - k: Location
        v: "Southeast Asia IP range (hosting unknown)"
      - k: Disclosed
        v: "2026-06-20"
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

# yuno.education: Unauthenticated Read, Write, and Delete on the Weaviate RAG Backend of an AI School Tutor

_NuClide Research -- Nicholas Kloster -- 2026-06-20_

---

## Summary

yuno.education runs an AI tutor for primary and secondary school students in Slovenia. The tutor reads from a Weaviate vector store as its RAG knowledge base. That store sat on the public internet with no authentication.

Anyone on the internet could read, change, or erase the lesson records that power the tutor. The records carry complete answer keys for classroom exercises. We confirmed read, write, and delete with a marked canary, then reversed every change.

The data at risk is academic. The answer keys are the material a teacher uses to grade students. Exposed, they break assessment integrity. Writable, they let an attacker feed wrong answers to students through an AI tutor that students treat as authoritative.

---

## Attack Surface

One host. One port. One vector store. Zero authentication.

| Port | Software | Role | Auth |
|------|----------|------|------|
| 8080 | Weaviate 1.35.2 | RAG vector database -- ~1,989-record lesson knowledge base | None |

The host is 157.173.121.77, node `c5867f7125e8`. The store answered schema, object, write, and delete requests without ever asking who was calling.

---

## Operator Attribution

The content is Slovenian throughout. Subject codes match the Slovenian school system: TJA is Tuji Jezik A (English as a foreign language), SPO is Sport and physical education. Classroom field values 5 and 7 map to Slovenian grade levels. Learning objectives in the records match the Slovenian national primary school curriculum. The operator is yuno.education, a Slovenian educational platform running an AI tutor backed by this Weaviate instance.

---

## What We Confirmed

**Read:** Pulled the schema and Lesson objects without credentials. Schema read returned 200. Object read returned 200.

**Write:** Inserted a marked canary record into the Lesson class. Write returned 200.

**Delete:** Removed the canary. Delete returned 204. Re-querying the canary ID returned 404, confirming it was gone.

Canary UUID: `bf635515-e378-45c2-9da9-7fb2db27aaa0`. Write 200, Delete 204, Verify 404.

Every test artifact we created we removed.

---

## Data Exposed

The store held one class, `Lesson`, with roughly 1,989 objects.

| Field | Type | Description |
|-------|------|-------------|
| title | string | Lesson name |
| externalId | string | External curriculum identifier |
| code | string | Internal lesson code |
| lvl | string | Difficulty or grade level |
| classroom | string | Grade number |
| classroomId | string | Internal classroom identifier |
| subject | string | Subject name |
| subjectId | string | Internal subject identifier |
| notes | text | Full lesson content |
| goals | text | Official curriculum learning objectives |
| answers | text array | Complete answer keys for classroom exercises |
| videoContent | string | Linked video references |
| summary | text | Lesson summary |
| generatedQnA | text | AI-generated question and answer pairs |
| relations | array | Related lesson links |

The high-value field is `answers`. Across the ~1,989 lesson records it holds complete answer keys for classroom exercises: fill-in-the-blank answers, multiple choice correct options, and written assessment responses. Confirmed subject and grade coverage so far is English as a foreign language at grade 7 and physical education at grade 5. The `generatedQnA` field was not read during enumeration; it likely holds AI-generated question and answer pairs tied to each lesson.

Schema names, field names, subject codes, grade values, and the object count are the finding. No student personal data, names of individuals, or actual answer-key contents are reproduced here.

---

## Impact

**Answer key exposure:** The `answers` field across ~1,989 lessons carries complete answer keys for classroom exercises. The platform serves these records to an AI tutor over RAG. A student can phrase a question to match lesson content and have the tutor return the answer key directly. No technical skill is required. This is a direct academic integrity breach.

**Answer key poisoning:** Write access lets an attacker overwrite the `answers` field on any lesson. The AI tutor then serves corrupted answers to students who use the platform for exam preparation. At scale across ~1,989 lessons this can undermine assessment validity across an entire school year.

**Full curriculum map:** The `subject`, `classroom`, `lvl`, and `externalId` fields together expose the structure of the Slovenian national curriculum as implemented by the platform: which grades, which subjects, which lessons. This is competitive intelligence for rival edtech platforms in the same market.

**Version posture:** Weaviate 1.35.2 is two minor versions behind current stable. The 1.36 and 1.37 release notes should be reviewed for any auth-bypass or data-exposure fixes that apply.

---

## Remediation

**Immediate (no code change required):** Firewall port 8080 to internal network only. The store should not be reachable from the public internet.

**Short-term:** Enable Weaviate's built-in API key or OIDC authentication. Add audit logging for writes and deletes.

**Medium-term:** Place canary records in the production vector store to detect unauthorized writes. Monitor retrieval distribution to detect ranking anomalies that signal poisoning. Move the embedding and ingestion pipeline behind an authenticated service so the store is never directly client-reachable.

---

## Disclosure

Finding documented 2026-06-20 under NuClide Research responsible-disclosure practice. Prior coordinated disclosures from this researcher include CVE-2025-4364 and ICSA-25-140-11, both through CISA.
