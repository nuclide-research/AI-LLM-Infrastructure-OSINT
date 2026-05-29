# Category 30: Agent-Memory Layer

_NuClide Research, 2026-05-29. Companion intel:
`data/platform-intel/agent-memory-osint-2026-05-29.md`._

The persistence tier of the agent stack: mem0/OpenMemory, Letta (MemGPT), Zep CE
/ Graphiti, Redis Agent Memory Server, Cognee, Memobase, Motorhead. Stores
long-term user memory by design, so the data-exposure class is PII-dense
(conversation-derived facts, session message history, user profiles).

Harvest note: Shodan API keys are dead, run these through the Shodan web UI
(Playwright) and log each to `shodan/query-log.md` with hit count. Zero is a
result. Expect several of these to be Shodan-dark (JSON-only roots on shared
ports), in which case the masscan-seeded fallback on the listed ports is the
path.

Cross-cutting FP rule: four of these platforms default to port 8000. Never treat
a raw port:8000 hit as a platform instance. Confirm every candidate with the
marker probe in the intel doc before counting it.

---

## Primary dorks (vendor-unique, low collision)

### Zep CE (the cleanest signal in the category)
The `X-Zep-Version` response header is set on every route by `SendVersion`
middleware. It is vendor-unique and Shodan indexes response headers.

```
"X-Zep-Version"
```

FP risk: very low. The header string is Zep-specific. Distinguish Zep CE
(`/healthz` returns `.`) from Graphiti standalone (`/healthcheck`, FastAPI
`/docs`).

### mem0 OpenMemory UI
```
http.html:"OpenMemory"
http.title:"OpenMemory"
```
FP risk: low. The Next.js UI on port 3000 carries the brand. The API on 8765 is
JSON-only and likely Shodan-dark, reach it by pivoting from the UI host or by
masscan on 8765.

### Letta (MemGPT)
```
port:8283
port:8283 "uvicorn"
```
FP risk: port alone is weak. Confirm with `GET /v1/agents/` returning
`agent_type` + `blocks[].label`. The ADE UI is cloud-hosted, do not dork for an
ADE page.

### Memobase
```
port:8019
```
FP risk: medium. Port 8019 is uncommon, which helps, but confirm via the
Memobase OpenAPI title + profile routes. Default token is the literal `secret`.

### Cognee
```
http.html:"/api/v1/cognify"
```
FP risk: low once keyed on the `cognify` verb route, which is unique to Cognee.

### Motorhead (deprecated long-tail)
```
port:8000 "/sessions/"
```
FP risk: high on port 8000. The `/sessions/{id}/memory` + `/sessions/{id}/retrieval`
route pair is the unique signature, confirm with the probe.

---

## Secondary / masscan-seeded fallback ports

If Shodan-dark (likely), masscan the tier-2 cloud ranges on:

```
8765   mem0 OpenMemory API
8888   mem0 /server (auth-on, but old builds open)
8283   Letta
8000   Zep CE / Cognee / Graphiti / Motorhead / Redis-memory REST  (heavy collision, fingerprint hard)
8019   Memobase
9000   Redis Agent Memory Server MCP
6333   Qdrant (mem0 OpenMemory co-resident, corroborating)
```

Shadow-sweep on every confirmed host (operators who ship one service auth-off
ship others auth-off, Insight #12): 5432 Postgres/pgvector, 6379 Redis/FalkorDB,
7474/7687 Neo4j (default creds in the Zep CE stack: `neo4j/zepzepzep`,
`postgres/postgres`), 11434 Ollama, 6333/6334 Qdrant.

---

## Verification probes (definitive, from intel doc)

| Platform | Probe | Confirms |
|---|---|---|
| mem0 OpenMemory | `GET :8765/api/v1/stats/?user_id=default` | JSON has `total_memories`+`total_apps`+`apps` |
| Letta | `GET :8283/v1/agents/` | array w/ `agent_type` enum + `blocks[].label` persona/human |
| Zep CE | hdr `X-Zep-Version` + `GET :8000/api/v2/sessions-ordered` w/ empty Api-Key | 200 session list |
| Cognee | `GET :8000/openapi.json` | paths `/api/v1/cognify` + `/recall` |
| Memobase | `GET :8019/openapi.json` | Memobase title + profile routes |
| Graphiti | `GET :8000/healthcheck` + `/docs` | graph_service title + episode routes |
| Motorhead | `GET :8000/sessions/<id>/memory` | JSON `messages` + context window |

All auth-default claims are doc/source-inferred. Label any finding "surface
open, access not exercised" until the probe is run against an authorized
in-scope host. The Zep empty-Api-Key bypass is code-confirmed only, validate on
a local CE container before asserting exploitable.
