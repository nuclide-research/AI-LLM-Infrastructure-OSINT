# Biometric Data Exposure — Unauthenticated Facial Recognition Database
**Finding date:** 2026-06-20  
**Verified by:** NuClide Research (nicholas@nuclide-research.com)  
**Classification:** CRITICAL — Biometric PII, unauth read access  
**Regulatory scope:** GDPR Art. 9 (special category), BIPA, CCPA/CPRA biometric provisions

---

## Affected System

| Field | Value |
|---|---|
| IP | 51.222.138.139 |
| Port | 8080 (TCP, plain HTTP) |
| PTR | vps-f6a3dfeb.vps.ovh.ca |
| Hosting | OVH Canada |
| Software | Weaviate 1.30.0 |
| Node | node1 (HEALTHY, single-node production) |
| Authentication | None — all endpoints return 200 without credentials |
| Auth test timestamp | 2026-06-20T15:48:57Z |

---

## What Is Exposed

Weaviate is an open-source vector database. This instance has the `img2vec-neural` module loaded — the image-to-vector encoder used to convert face photographs into searchable biometric embeddings.

Three collections are present:

| Collection | Objects | Vectorizer | Properties | Notes |
|---|---|---|---|---|
| WWMFacesRecogProd | **14,178** | img2vec-neural | image_blob (blob), text (text) | Active production collection |
| WWMFaces | **6,120** | img2vec-neural | image (blob), text (text) | Earlier batch |
| WWMFacesRecog | 0 | none | filename (text), image_blob (blob) | Staging/import, empty |
| **Total** | **20,298** | | | |

Each record contains:
- A face photograph stored as a binary blob (`image` / `image_blob` property)
- An identity label (`text` property — name or identifier for the subject)
- A neural face embedding vector (the img2vec-neural computed representation, used for similarity/matching queries)

This is a complete facial recognition corpus: photograph + identity + searchable embedding, all in one unauthenticated record.

---

## Reproduction Steps

All requests below require no Authorization header, no API key, no session cookie. Any HTTP client reproduces the finding.

### 1. Confirm service identity and module

```
GET http://51.222.138.139:8080/v1/meta
```

Expected response (trimmed):
```json
{
  "version": "1.30.0",
  "modules": {
    "img2vec-neural": {}
  }
}
```

### 2. Confirm schema (biometric class definitions)

```
GET http://51.222.138.139:8080/v1/schema
```

Key excerpt confirming biometric vectorizer configuration:
```json
{
  "class": "WWMFacesRecogProd",
  "vectorizer": "img2vec-neural",
  "moduleConfig": {
    "img2vec-neural": { "imageFields": ["image"] }
  },
  "properties": [
    { "name": "image_blob", "dataType": ["blob"] },
    { "name": "text",       "dataType": ["text"] }
  ]
}
```

### 3. Confirm object count (aggregate query, no auth)

```
POST http://51.222.138.139:8080/v1/graphql
Content-Type: application/json

{ "query": "{Aggregate{WWMFacesRecogProd{meta{count}}}}" }
```

Response:
```json
{ "data": { "Aggregate": { "WWMFacesRecogProd": [{ "meta": { "count": 14178 } }] } } }
```

### 4. Confirm individual object accessibility (IDs only — no image content retrieved)

```
POST http://51.222.138.139:8080/v1/graphql
Content-Type: application/json

{ "query": "{Get{WWMFacesRecogProd(limit:3){_additional{id creationTimeUnix}}}}" }
```

Response (verified 2026-06-20T15:48:57Z):
```json
{
  "data": { "Get": { "WWMFacesRecogProd": [
    { "_additional": { "id": "14781ede-df29-4812-9f50-c3a3be7187cb", "creationTimeUnix": 1768000491951 } },
    { "_additional": { "id": "14789546-8f37-46e8-92cf-6033da82f257", "creationTimeUnix": 1768005530957 } },
    { "_additional": { "id": "1478d43e-a75a-4abe-b0c8-8a22a5a662a7", "creationTimeUnix": 1772007491141 } }
  ]}}
}
```

Object creation timestamps:
- `14781ede...` — 2026-01-09T23:14:51Z
- `14789546...` — 2026-01-10T00:38:50Z
- `1478d43e...` — 2026-02-25T08:18:11Z

The February 25 record confirms the database was actively populated **4 months before discovery**. This is not a dev/test instance.

Similarly for WWMFaces (6,120 objects, earliest records from 2026-01-07):
- `0008a53c-a470-4b83-9255-4f61511d6128` — 2026-01-07T23:28:01Z
- `000a566e-cec3-4e71-819c-d0d6a95c3979` — 2026-01-08T00:12:55Z
- `000b353e-484a-441e-91bf-c58e63589732` — 2026-01-08T00:52:10Z

---

## What an Adversary Can Do

Any unauthenticated party can:

```
# Pull all face photographs + identity labels for all 14,178 Prod records:
GET http://51.222.138.139:8080/v1/objects?class=WWMFacesRecogProd&limit=100

# Run face-matching search against the exposed corpus (near-vector query):
POST http://51.222.138.139:8080/v1/graphql
{ "query": "{Get{WWMFacesRecogProd(nearImage:{image:\"<base64>\"},limit:5){text _additional{distance}}}}" }
```

The second query lets an attacker submit an arbitrary face photo and identify who it matches in the corpus — the complete facial recognition capability, unauthenticated.

**NuClide did not execute either of these requests.** The proof above (schema + count + IDs) establishes access without downloading images or identity labels.

---

## Regulatory Exposure

| Framework | Basis | Exposure |
|---|---|---|
| GDPR Art. 9 | Biometric data "for the purpose of uniquely identifying a natural person" = special category | Unlawful processing without explicit consent + DPA notification obligation |
| Illinois BIPA | "Scan of face geometry" explicitly covered | $1,000 per negligent violation, $5,000 per intentional/reckless violation, per person |
| CCPA/CPRA | "Faceprints" enumerated as sensitive personal information | Right to disclosure + deletion |
| Texas CUBI / Washington MY Health DA | Biometric identifiers | Similar obligations |

---

## Remediation

1. **Immediate:** Enable Weaviate authentication (`AUTHENTICATION_APIKEY_ENABLED=true` or OIDC). Weaviate ships with auth disabled by default — this is a deployment misconfiguration, not a software vulnerability.
2. **Network:** Bind port 8080 to localhost or an internal interface. This port should never be internet-facing.
3. **Audit:** Review who has accessed `/v1/objects` and `/v1/graphql` in application logs since January 2026.

---

## Timeline — Post-Discovery State Change

| Timestamp (UTC) | Event |
|---|---|
| 2026-06-20T15:48:57Z | **First probe.** WWMFacesRecogProd: 14,178 objects. WWMFaces: 6,120. Both classes in schema. Object UUIDs confirmed (see above). |
| 2026-06-20T16:02:42Z | **Re-verify.** WWMFacesRecogProd count: 0. WWMFaces: 6,120 (unchanged). |
| 2026-06-20T16:03:27Z | **Re-verify.** WWMFacesRecogProd **class dropped from schema entirely**. WWMFaces: 6,120 confirmed, original object UUID `0008a53c-a470-4b83-9255-4f61511d6128` still accessible. |

The 14,178-record production collection was deleted and the class removed within 14.5 minutes of initial discovery. WWMFaces (6,120 objects) remains fully exposed as of 16:03:27Z.

The operator can correlate this timeline against their application and access logs to confirm the exposure window. The evidence above (UUIDs, counts, schema) was captured before removal.

---

## Notes on Evidence Scope

- No face images were downloaded.
- No identity labels (`text` field values) were read.
- No face-matching queries were run.
- Evidence is limited to: service metadata, schema, aggregate counts, and object UUIDs.
- The object UUIDs above are sufficient for the operator to independently verify which records were confirmed accessible.
