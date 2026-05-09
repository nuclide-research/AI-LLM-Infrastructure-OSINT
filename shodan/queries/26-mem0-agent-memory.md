# 26. Mem0 / Agent Long-Term Memory Collections

_Section created: 2026-05-09_

Mem0 ([mem0ai/mem0](https://github.com/mem0ai/mem0)) turns any vector store into agent long-term memory, storing structured per-user JSON payloads with `user_id`, `data`, `hash`, and `created_at` fields. The framework itself has no network interface; exposure is through its **backend vector store** (Qdrant or ChromaDB), which stores Mem0-typed collections recognizable by naming convention.

Exposing a Mem0 backend exposes **complete agent memory for every user** — professional interaction history, personal details, credentials stored by the agent, and business-process context accumulated over months of operation.

**Survey result (2026-05-03):** Cross-referencing 61 unauth Qdrant instances + 48 unauth ChromaDB instances from prior surveys. **8 confirmed Mem0-class instances**, all unauthenticated. Three contain extensive personal/professional history of identifiable individuals (CRITICAL). Highlights: `206.189.97.116` (DigitalOcean) — 8,984-point `mem0` collection with multi-month professional-interaction history (real names, WISE payment workflows). `65.109.11.40` (Hetzner) — Italian marketing-agency `claude_memory` collection with client pricing, subcontractor day-rates. `188.166.208.148` (DigitalOcean) — 1,199-point `my_journal` personal diary corpus.

**Shodan pivot strategy:** Mem0 collections are not findable by direct Shodan query — Shodan does not index Qdrant/ChromaDB collection names. The discovery path is:
1. Enumerate all unauth Qdrant (port 6333) and ChromaDB (port 8000) instances via queries in §2.
2. For each, hit `GET /collections` (Qdrant) or `GET /api/v1/collections` (ChromaDB).
3. Match collection names against the Mem0 naming patterns below.

Queries here target the backend services with Mem0-suggestive signals that Shodan may index.

---

**Shodan indexing note:** `port:6333 "mem0"` and `port:8000 "heartbeat" "mem0"` return 0 — Qdrant/ChromaDB collection names are not indexed by Shodan via port-constrained bare strings. However, `http.html:"mem0"` (147) and `"mem0"` bare (129) work because Shodan indexes the string across all HTTP response bodies globally. `"mem0migrations"` (13) is a high-precision signal — a Django migration table name specific to Mem0.

## Qdrant (primary Mem0 backend)

See also §2 (vector-databases) for full Qdrant query catalog.

| Shodan Query | Verified hits | Notes |
|---|---|---|
| `http.html:"mem0"` | **147** | Best Mem0 signal; HTML-scoped any port/service |
| `"mem0"` | **129** | Bare-string any indexed field |
| `"mem0migrations"` | **13** | Django migration table name; high-precision Mem0 signal |
| `"mem0_memories"` | 2 | Collection name variant |
| `port:6333 http.status:200` | **47** | Unauth Qdrant (all instances, not Mem0-specific — enumerate collections post-discovery) |
| `port:6333` | — | Qdrant default HTTP port |
| `port:6333 "qdrant"` | — | Qdrant identifier |
| `port:6333 "mem0"` | 0 | Port-constrained bare string does not work |
| `port:6333 "memory"` | 0 | Same |
| `port:6333 org:"digitalocean" http.status:200` | — | DigitalOcean unauth Qdrant (two Mem0 finds in survey) |
| `port:6333 org:"hetzner" http.status:200` | — | Hetzner unauth Qdrant (one Mem0 find in survey) |
| `port:6333 org:"vultr" http.status:200` | — | Vultr unauth Qdrant (two Mem0 finds in survey) |

**Post-enumeration collection name patterns to match against (not Shodan queries):**

```
mem0
mem0_memories
mem0migrations
user_memory_*
*_memory          (claude_memory, sovereign_memory, watzis_longterm_memory)
*_longterm_memory
*_long_term_memory
my_journal
*_journal
```

---

## ChromaDB (secondary Mem0 backend)

See also §2 (vector-databases) for full ChromaDB query catalog.

| Shodan Query | Verified hits | Notes |
|---|---|---|
| `http.html:"api/v1/collections"` | **18** | ChromaDB collections API path in HTML body |
| `port:8000 "chroma"` | — | ChromaDB on default port |
| `port:8000 http.html:"chroma"` | — | HTML-scoped |
| `port:8000 "heartbeat"` | 1 | ChromaDB root response field |
| `port:8000 "mem0"` | 7 | `mem0` collection name on port 8000 |
| `port:8000 "heartbeat" "mem0"` | 0 | Conjunction drops to 0; use separately |
| `port:8000 "sovereign_memory"` | — | Specific collection name seen in survey |
| `port:8000 org:"hetzner" http.status:200` | — | Hetzner unauth ChromaDB |
| `port:8000 org:"digitalocean" http.status:200` | — | DigitalOcean unauth ChromaDB |

---

## Mem0 cloud / managed API surface

Mem0 also offers a managed API at `api.mem0.ai`. Shodan may index misconfigured deployments or dev proxies:

| Shodan Query | Notes |
|---|---|
| `"mem0.ai"` | Any indexed reference to the Mem0 managed platform |
| `ssl.cert.subject.cn:"mem0.ai"` | TLS cert CN |
| `hostname:"mem0"` | rDNS pattern for self-hosted Mem0 API proxies |
| `http.html:"mem0ai"` | Package identifier in page source |
| `http.html:"mem0" http.html:"memory"` | Co-occurrence for Mem0-adjacent apps |

---

## Associated agent frameworks (commonly deploy Mem0)

| Shodan Query | Notes |
|---|---|
| `port:6333 http.status:200 org:"digitalocean"` | Unauth Qdrant on DO; enumerate collections for Mem0 |
| `port:6333 http.status:200 org:"hetzner"` | Unauth Qdrant on Hetzner |
| `port:6333 http.status:200 org:"vultr"` | Unauth Qdrant on Vultr |
| `port:8000 "heartbeat" org:"digitalocean"` | Unauth ChromaDB on DO |
| `port:8000 "heartbeat" org:"hetzner"` | Unauth ChromaDB on Hetzner |

---

## Combined discovery pivot

| Shodan Query | Notes |
|---|---|
| `(port:6333 OR (port:8000 http.html:"chroma")) http.status:200` | All unauth Qdrant + ChromaDB; enumerate for Mem0 collections |
| `port:6333 http.status:200 -org:"akamai"` | Unauth Qdrant excluding AS63949 honeypot fleet (Akamai/Linode) |
| `port:6333 http.status:200 (org:"digitalocean" OR org:"hetzner" OR org:"vultr" OR org:"ovh" OR org:"linode" OR org:"scaleway")` | Tier-2 cloud unauth Qdrant sweep |
