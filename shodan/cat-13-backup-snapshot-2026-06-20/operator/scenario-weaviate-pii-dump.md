# Scenario Packet: Flowise To Weaviate Pii Dump

**Focus type:** `attack_path`  **Value:** `flowise_to_weaviate_pii_dump`

## Target Profile

> Population of 5 hosts focused on flowise to weaviate pii dump. Top sectors: commercial, university. Most common platform class: Flowise. Auth posture breakdown reflects details.json subset.

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

**Typical platforms:** `Flowise`, `Weaviate`, `Qdrant`

## Recon & Surface Mapping

### Surface Elements

| Type | Pattern | Notes |
|------|---------|-------|
| `http_path` | `/api/v1/chatflows` | Flowise flow list -> Weaviate host extraction |
| `http_path` | `/api/v1/credentials` | Flowise credentials -> Weaviate API key (if any) |
| `port` | `8080` | Weaviate REST on pivot target |
| `http_path` | `/v1/schema` | Weaviate schema dump |
| `http_path` | `/v1/objects` | Weaviate object retrieval |

### HTTP Probe Patterns

**Flowise -> Weaviate pivot chain**
- Methods: `GET`, `POST`
- Paths: `/api/v1/chatflows`, `/api/v1/credentials`, `/v1/schema`, `/v1/objects`
- Notes: Flowise chatflow JSON contains weaviate.apiKey and weaviate.host. If weaviate.apiKey is empty, Weaviate is unauth. Extract host from flow config, then probe directly.

### Mapping Strategy

- 1. GET /api/v1/chatflows (Flowise); parse flow node configs for weaviate host/apiKey fields.
- 2. GET /api/v1/credentials (Flowise); check if credential values returned include Weaviate key.
- 3. Direct probe of Weaviate host from step 1: GET /v1/schema without auth.
- 4. GET /v1/objects?limit=5 to sample records and confirm PII data class.
- 5. Estimate total scale: GET /v1/meta or class totalCount from schema.

## Threat Model & Attack Hypotheses

### Assets at Risk

- **`weaviate_vector_payloads`** -- Full text of document chunks embedded in RAG pipeline.
- **`user_pii_records`** -- Customer/patient records stored as vector payloads.
- **`flowise_connected_systems`** -- All external systems reachable via Flowise node configs.

### Hypotheses

**H1** [CRITICAL] Flowise exposes Weaviate host and empty API key in flow config; Weaviate is unauth; full PII corpus accessible.
  - Categories: `agent_surfaces`, `leaky_data_stores`
  - Attack paths: `flowise_to_weaviate_pii_dump`


## Test Cases

### TC1 [HIGH] -- Extract Weaviate host from Flowise flow configs.

**Preconditions:**
- Flowise port 3000 reachable

**Steps:**
1. GET /api/v1/chatflows; inspect node configs for weaviate_url or host fields.
2. GET /api/v1/credentials; check for Weaviate credential entries.
3. Record Weaviate host address and any API key value (empty = unauth).

**Weak signals indicating a finding:**
- Flow config JSON containing weaviateApiKey field (empty or populated).
- Weaviate host IP or hostname in node config.
- Credential entry for Weaviate with empty value field.

> **Note:** Flowise access alone is high. Successful Weaviate pivot in TC2 = critical.

### TC2 [CRITICAL] -- Confirm unauthenticated Weaviate access and PII data class.

**Preconditions:**
- TC1 extracted Weaviate host

**Steps:**
1. GET http://{weaviate_host}:8080/v1/schema without auth.
2. Identify PII-class collections from field names.
3. GET /v1/objects?limit=3 from highest-risk class.
4. Document field names and data class (not actual PII values).

**Weak signals indicating a finding:**
- HTTP 200 on Weaviate schema endpoint from attacker IP.
- Class property names matching PII schema.
- Object payload fields containing real values.

> **Note:** This completes the two-hop pivot: Flowise flow config -> Weaviate host -> unauth PII dump.


## Attack Chains

### AC1 -- Flowise to Weaviate PII Dump

**Sequence:** `TC1` -> `TC2`

Extract Weaviate host from open Flowise flow config, pivot to direct Weaviate REST API access, enumerate schema to identify PII-class collections, sample records to confirm data class. Two unauthenticated hops to complete PII corpus access.


## Detection & Telemetry

### Logging Recommendations

| Event | Fields | Notes |
|-------|--------|-------|
| `chatflow_config_access` | `ip`, `flow_id`, `nodes_count` | Flow config read revealing internal hosts. |
| `weaviate_external_read` | `ip`, `class`, `object_count` | Weaviate access from Flowise pivot. |

### Detection Patterns

- [CRITICAL] **Weaviate schema access from IP that recently accessed Flowise API** -- Two-hop pivot chain.

## Hardening & Counterplay

### Quick Wins (< 1 hour)

- Enable Flowise auth immediately (FLOWISE_USERNAME + FLOWISE_PASSWORD).
- Enable Weaviate API key auth on same timeline.

### Architectural Changes

- Weaviate must only accept connections from Flowise application server IP; no Internet routing.
- Flowise credential store must not return raw values; ID reference only.

### Secure Deployment Template Guidance

- Agent platform + vector DB co-deployment template: both services must have auth; network segment isolates vector DB from Internet.