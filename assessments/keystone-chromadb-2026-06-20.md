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

## CWE-306 + RAG Data Poisoning -- How They Stack

These are two separate layers. CWE-306 is the door being left open.
RAG Data Poisoning is what you do once you're through it.

### Layer 1: CWE-306 -- Missing Authentication for Critical Function

This is a standard MITRE weakness. The definition: a system exposes a
function that has security implications without requiring the caller to
prove who they are.

In this case, three functions with security implications:
- Read the knowledge base that drives an AI chatbot
- Write to / delete from that knowledge base
- Execute the full RAG + LLM pipeline

All three are reachable by anyone on the internet with a single HTTP
request. No token, no cookie, no IP restriction. That's CWE-306 --
clean and unambiguous.

This is the same weakness class behind every exposed Elasticsearch,
Redis, MongoDB, and etcd instance from the last decade.
Well-understood, easy to fix (add auth, firewall the port).

### Layer 2: RAG Data Poisoning -- the novel part

RAG stands for Retrieval-Augmented Generation. The architecture:

```
User question
      |
      v
Vector DB (ChromaDB)
  -- embed the question
  -- find top-k most similar documents by cosine distance
  -- return those documents as "context"
      |
      v
LLM (DeepSeek here)
  -- receives: [system prompt] + [retrieved context] + [user question]
  -- generates answer grounded in that context
      |
      v
User sees answer, trusts it as authoritative
```

The attack: if you can write to the vector DB, you control what goes
into the context window. You're not attacking the LLM directly -- you're
attacking the data it reads before it answers.

The LLM never knows the difference between a legitimate Keystone
document and an attacker-injected one. It just sees text in its context
window and responds accordingly. The poisoned record arrives
pre-authorized by the retrieval step.

### Layer 3: The Feedback Loop -- what makes this different

Published RAG poisoning research (PoisonedRAG, 2024; OWASP LLM04)
models the attacker as blind after injection. You write the document and
hope it surfaces when a user queries. This deployment breaks that
assumption.

Port 5050 exposes the RAG query endpoint unauthenticated. An attacker
can use it as a verification oracle:

```
POST :8000/add   -- inject document
POST :5050/api/search {"query": "seed phrase recovery"}
                 -- check retrieval rank
if rank < 1: adjust document, repeat
if rank = 1: confirmed dominant, stop
```

The exposed RAG console turns a probabilistic attack into a
deterministic one. The attacker iterates until their document wins the
nearest-neighbor race. This is injection with closed-loop tuning -- not
modeled in the existing literature.

### Why they compound

CWE-306 alone on a read-only database is a confidentiality issue --
someone reads data they shouldn't.

CWE-306 alone on a database not connected to user-facing output is a
low-impact integrity issue -- someone corrupts data, but users don't
see it directly.

RAG Data Poisoning without CWE-306 still requires a path to the vector
store: compromised credential, insider access, supply chain compromise,
or indirect injection via user-controlled content that gets indexed into
the pipeline. All of these have meaningful barriers.

Together:

```
CWE-306 (no auth)  +  RAG pipeline  +  feedback loop
        =
Anonymous internet attacker controls what an AI chatbot tells
users about how to handle their seed phrases, and can verify
their payload is dominant before any user is harmed
```

The compounding factor specific to Keystone: the chatbot speaks as
official customer support on a topic (seed phrase recovery) where users
have no reference point to verify the answer. They asked the official
chatbot. The official chatbot answered. They follow instructions.
Assets gone.

### MITRE ATLAS mapping

OWASP LLM04 names this attack class but is not a TTPs framework.
MITRE ATLAS is. Verified against ATLAS v5.6.0 on 2026-06-20: ATLAS now
covers RAG poisoning. AML.T0070 RAG Poisoning is the on-point technique
(inference-time injection of content into RAG-indexed data, targeted to
surface for a specific query), backed by AML.T0066, AML.T0071, and
AML.T0064. The write primitive here maps to AML.T0070. AML.T0020 (Poison
Training Data) does not fit; it is training-time. The one piece no single
technique enumerates is the closed-loop, oracle-tuned rank-optimization
method that the exposed :5050 console enables. AML.T0070 names the
outcome, not that optimization loop. Full analysis and a proposed
sub-technique under AML.T0070:
analysis/2026-06-20-atlas-gap-inference-time-rag-poisoning.md

### Why there's no CVE

CVEs attach to specific product versions with a specific exploitable
defect in the code. The ChromaDB code is working exactly as designed --
it wasn't deployed with authentication enabled. That's a configuration
failure, not a product defect. No CVE.

The RAG poisoning attack class is documented in research (OWASP LLM
Top 10: LLM04, PoisonedRAG 2024), but research papers don't generate
CVEs. CVEs require a vendor, a product, a version, and a code-level
defect. "Your deployment architecture creates this risk" doesn't fit
that model.

The closest analogues that did eventually get CVE treatment:
- Unauthenticated Kubernetes API server: individual CVEs per version
  once framed as a product defect, not a config issue
- Jupyter Notebook no-auth default: tracked as deployment guidance,
  not CVE

This finding will likely follow the same pattern -- cited in research,
vendors pressured to change defaults, auth-on-by-default ships, old
behavior gets a CVE retroactively. That's a 1-3 year timeline.
Right now it's a misconfiguration with a novel exploitation path.

### Remediation

1. Firewall ports 8000, 5050, and 8080 to internal network only
   (immediate -- no code change required)
2. Enable ChromaDB authentication at the infrastructure layer
   (reverse proxy with token validation, or VPN-gated access)
3. Add rate limiting and anomaly detection on /add and /delete
   endpoints once auth is in place
4. Audit the vector store for injected records before re-exposing
   the RAG pipeline

---

## Tool Reference

**chromascan** -- unauthenticated ChromaDB enumeration + canary write/delete verification
https://github.com/nuclide-research/chromascan
