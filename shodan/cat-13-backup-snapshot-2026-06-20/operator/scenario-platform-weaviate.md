# Scenario Packet: Weaviate

**Focus type:** `platform`  **Value:** `Weaviate`

## Target Profile

> Population of 5 hosts focused on Weaviate. Top sectors: commercial, university. Most common platform class: Weaviate. Auth posture breakdown reflects details.json subset.

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


## Recon & Surface Mapping

### Surface Elements

| Type | Pattern | Notes |
|------|---------|-------|
| `port` | `8080` | Weaviate REST default |
| `http_path` | `/v1/schema` | Full schema dump; class names and field names |
| `http_path` | `/v1/objects` | Object retrieval; payload = actual stored data |
| `http_path` | `/v1/graphql` | Arbitrary query with no auth |
| `http_path` | `/v1/.well-known/openid-configuration` | OIDC config; presence = auth configured |
| `http_path` | `/v1/meta` | Instance metadata including version and modules |


## Threat Model & Attack Hypotheses

### Assets at Risk

- **`vector_payloads`** -- Stored document chunks, user records, or conversation history in payload fields.
- **`schema_topology`** -- Class and field structure reveals data architecture.

### Hypotheses

**H1** [CRITICAL] Weaviate deployed without API key auth (default); full schema and object access without credentials.
  - Categories: `leaky_data_stores`
  - Attack paths: `flowise_to_weaviate_pii_dump`


## Test Cases

### TC1 [CRITICAL] -- Confirm unauthenticated schema and object access.

**Preconditions:**
- Port 8080 reachable

**Steps:**
1. GET /v1/schema without auth header.
2. Inspect class names and property types for PII indicators.
3. GET /v1/objects?limit=5 to sample actual records.

**Weak signals indicating a finding:**
- HTTP 200 on /v1/schema with class definitions.
- Property names matching PII patterns (email, name, patient_id).
- Object payload fields containing real data values.

> **Note:** Confirm PII class from schema before sampling objects. Sample limit 5 is sufficient.


## Attack Chains

### AC1 -- Weaviate Unauth PII Dump

**Sequence:** `TC1`

Schema enumeration to identify PII-class data, then minimal object sampling to confirm unauth read access to user or patient records.


## Detection & Telemetry

### Logging Recommendations

| Event | Fields | Notes |
|-------|--------|-------|
| `schema_access` | `ip`, `path`, `timestamp` | External schema access. |
| `object_retrieval` | `ip`, `class`, `limit`, `count` | Object reads with class and scale. |

### Detection Patterns

- [CRITICAL] **GET /v1/schema from external IP without API key** -- Data enumeration.

## Hardening & Counterplay

### Quick Wins (< 1 hour)

- Set AUTHENTICATION_APIKEY_ENABLED=true and AUTHENTICATION_APIKEY_ALLOWED_KEYS in Weaviate env.
- Firewall port 8080 to application-tier IPs only.

### Architectural Changes

- Deploy Weaviate in private subnet; no direct Internet route.

### Secure Deployment Template Guidance

- Weaviate template must enable API key auth; unauthenticated template is rejected.