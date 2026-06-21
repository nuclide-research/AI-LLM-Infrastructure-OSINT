# Scenario Packet: Leaky Data Stores

**Focus type:** `category`  **Value:** `leaky_data_stores`

## Target Profile

> Population of 5 hosts focused on leaky data stores. Top sectors: commercial, university. Most common platform class: Weaviate. Auth posture breakdown reflects details.json subset.

**Total hosts in scope:** 5

**Severity distribution:**

| Value | Count |
|-------|-------|
| critical | 2 |
| high | 2 |
| medium | 1 |

**Sector distribution:**

| Value | Count |
|-------|-------|
| commercial | 1 |
| university | 1 |
| research | 1 |
| healthcare | 1 |
| government | 1 |

**Typical platforms:** `Weaviate`, `Qdrant`, `Chroma`, `Milvus`, `Pinecone (self-hosted)`, `Elasticsearch+kNN`

## Recon & Surface Mapping

### Surface Elements

| Type | Pattern | Notes |
|------|---------|-------|
| `port` | `8080` | Weaviate REST default |
| `port` | `6333` | Qdrant REST default |
| `port` | `8000` | Chroma default |
| `port` | `19530` | Milvus gRPC default |
| `port` | `9200` | Elasticsearch (used as vector store) |
| `http_path` | `/v1/schema` | Weaviate: full schema dump |
| `http_path` | `/v1/objects` | Weaviate: object listing; default limit returns first N records |
| `http_path` | `/v1/graphql` | Weaviate: GraphQL; arbitrary object queries |
| `http_path` | `/v1/collections` | Qdrant: collection list |
| `http_path` | `/v1/collections/{name}/points` | Qdrant: point (vector+payload) retrieval |
| `http_path` | `/api/v1/collections` | Chroma: collection list |
| `http_path` | `/api/v1/collections/{id}/get` | Chroma: document retrieval |

### HTTP Probe Patterns

**Schema enumeration - maps data model before any object access**
- Methods: `GET`
- Paths: `/v1/schema`, `/_cat/indices?v`, `/api/v1/collections`
- Notes: Schema reveals class/field names. Fields like email, ssn, phone, patient_id, user_id indicate PII-class data. Class names like 'Document', 'Memory', 'Chunk' indicate RAG corpus.

**Object sample retrieval**
- Methods: `GET`
- Paths: `/v1/objects?limit=5`, `/v1/collections/{name}/points?limit=5`
- Notes: Small sample (5 objects) is sufficient to confirm data class. Payload fields are the actual stored data. Vector values confirm embeddings are present but are not the sensitive element.

**GraphQL unrestricted query (Weaviate)**
- Methods: `POST`
- Paths: `/v1/graphql`
- Headers: `Content-Type: application/json`
- Notes: POST a Get query for any class with a limit. Returns objects with all payload fields. No auth = arbitrary query without restriction.

### Mapping Strategy

- 1. Port scan for 6333, 8080, 8000, 19530; fingerprint response to confirm platform.
- 2. GET schema or collection list to understand data model without touching records.
- 3. Identify high-value classes (those with PII-indicative field names).
- 4. Retrieve 1-5 sample objects from highest-value class only to confirm data class.
- 5. Estimate total record count via schema totalCount or collection info endpoint.
- 6. Document schema, record count, and field names; this is sufficient to establish severity.

## Threat Model & Attack Hypotheses

### Assets at Risk

- **`rag_corpus_contents`** -- Embedded document chunks; may contain full text of org documents.
- **`user_pii`** -- Customer or patient records stored as vector payloads with raw field values.
- **`conversation_memory`** -- Agent conversation histories stored as embedding-searchable memory.
- **`proprietary_embeddings`** -- Custom-model embeddings represent IP; extractable without model access.

### Hypotheses

**H1** [CRITICAL] Vector DB is exposed without API key; schema reveals PII-class field names; sample objects confirm unencrypted PII readable.
  - Categories: `leaky_data_stores`
  - Attack paths: `flowise_to_weaviate_pii_dump`


## Test Cases

### TC1 [HIGH] -- Enumerate vector DB schema to identify PII-class collections.

**Preconditions:**
- Vector DB port accessible

**Steps:**
1. GET /v1/schema (Weaviate) or GET /v1/collections (Qdrant) or GET /api/v1/collections (Chroma).
2. Parse class/collection names and field names.
3. Flag fields matching PII patterns: email, name, phone, address, ssn, dob, patient, user.

**Weak signals indicating a finding:**
- Schema contains classes with PII-indicative names.
- No Authorization header required for schema access.
- totalCount or vectors_count field indicates scale of stored data.

> **Note:** Schema alone is high. Confirm actual payload field values in TC2 for critical.

### TC2 [CRITICAL] -- Confirm PII is readable in object payloads without authentication.

**Preconditions:**
- TC1 identified PII-class collection

**Steps:**
1. Retrieve 3-5 sample objects from highest-risk class.
2. Inspect payload fields for real values (email addresses, names, medical terms).
3. Record field names and data class; do not retain actual PII values beyond what is needed for the finding.

**Weak signals indicating a finding:**
- Payload contains actual email addresses or names.
- Medical or financial field content confirms HIPAA/PCI-class data.
- Document text field contains org-internal content (code, reports, internal comms).

> **Note:** Critical if PII confirmed. Do not retrieve more than minimal sample needed to establish data class.


## Attack Chains

### AC1 -- Leaky Vector DB PII Dump

**Sequence:** `TC1` -> `TC2`

Schema dump to identify PII-class collections, then minimal object sampling to confirm data class. At this point unauth full-corpus access is established; regulatory notification may be required by the target org.


## Detection & Telemetry

### Logging Recommendations

| Event | Fields | Notes |
|-------|--------|-------|
| `schema_access_external` | `ip`, `path`, `timestamp` | Any external IP accessing schema endpoint. |
| `bulk_object_retrieval` | `ip`, `collection`, `count` | Large limit query from external IP. |

### Detection Patterns

- [CRITICAL] **GET /v1/schema from external IP without API key** -- Data enumeration in progress.
- [CRITICAL] **GraphQL query with high limit (> 100) from external IP** -- Bulk data exfiltration attempt.

## Hardening & Counterplay

### Quick Wins (< 1 hour)

- Enable Weaviate API key auth (AUTHENTICATION_APIKEY_ENABLED=true) immediately.
- Firewall vector DB ports (6333, 8080, 8000) to only application server IPs.

### Architectural Changes

- Deploy vector DB in a private subnet; application layer is the only network path to it.
- Implement record-level access control via Weaviate multi-tenancy or Qdrant collection-level API keys.

### Secure Deployment Template Guidance

- Vector DB deployments must enable authentication before any data is loaded.
- Template network rules: 6333/8080/8000/19530 must not be reachable from Internet.