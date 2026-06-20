# Salt at Amelia Island / Ritz-Carlton -- Unauth RWD on Restaurant Chatbot RAG (Test)

**Date:** 2026-06-20
**Tool:** weavscan
**Severity:** HIGH
**Status:** CONFIRMED -- unauth read + write + delete (test/staging deployment)

---

## Target

```
IP:       20.51.140.169
Port:     8080  (Weaviate)
Service:  Weaviate 1.28.16
Hosting:  Microsoft Azure
Auth:     NONE
```

---

## Operator Attribution

**Salt at Amelia Island** -- upscale restaurant at The Ritz-Carlton, Amelia Island, Florida.

Evidence:
- Class `DocumentContent`, container_id `test`, file_name = `https://www.saltameliaisland.com/`
- Scraped content: Salt restaurant menus, private dining packages, chef bio, team, OpenTable integration
- Events referenced: DAOU Vineyards wine dinner, Chef Okan Kizilbayir
- Azure hosting consistent with Ritz-Carlton enterprise cloud infrastructure

Note: `container_id: "test"` and `uploaded_by: ""` indicate this is a test/staging deployment, not production. 7 records from a single URL scrape.

---

## Data (1 Class, 7 Records)

| Class | Records | Content |
|-------|---------|---------|
| DocumentContent | 7 | saltameliaisland.com web scrape, chunked |

### Schema

```
blob_url       text    -- source URL
file_name      text    -- source file/URL identifier
content_type   text    -- "web"
file_type      text    -- "web"
text           text    -- scraped/chunked content
chunk_index    int     -- chunk position (0-6)
total_chunks   int     -- 7
container_id   text    -- "test"
language       text    -- "en"
created_at     date
updated_at     date
uploaded_by    text    -- "" (empty -- no user attribution)
tags           text    -- ""
page_number    int     -- 1
```

### Sample Content

```
"Salt offers two exclusive private dining experiences:
Atlantic Room: sweeping ocean views, terrace with fire towers, up to 30 guests.
Seaview Terrace: al fresco dining, coastal pergola, up to 20 guests."

"Salt Cellar Series: DAOU Vineyards Dinner
Presented by Chef Okan Kizilbayir
Monday, August 25, 2025 -- reception followed by four-course tasting menu"
```

---

## Access Matrix

| Operation | Result | HTTP |
|-----------|--------|------|
| Read | YES | 200 |
| Write | YES -- canary persisted | 200 |
| Delete (object) | YES | 204 |

Note: Canary write on this target returned UUID but was immediately confirmed deleted. Access pattern consistent with full RWD on the class.

---

## Impact

This is a test deployment with 7 records scraped from the public restaurant website. No non-public data is exposed. The significance is as a **pattern indicator**: the same Weaviate deployment pattern with no authentication on a Microsoft Azure IP, connected to a hospitality/Ritz-Carlton property.

If the operator promotes this to production with real reservation data, customer PII, or private dining inquiry details, the severity escalates to CRITICAL immediately. The vulnerability is already present; the data sensitivity depends on what gets ingested next.

---

## Pivot Avenues

1. **Azure tenant** -- 20.51.140.169 is Azure; other services on this tenant may include the production deployment with real customer data
2. **OpenTable integration** -- restaurant uses OpenTable for reservations; if reservation data is ingested into Weaviate for a concierge chatbot, PII (name, email, dining preferences) would be exposed
3. **container_id "test"** -- test containers imply a production container exists; find it

---

## Tool Reference

Found with **weavscan**.
https://github.com/nuclide-research/weavscan
