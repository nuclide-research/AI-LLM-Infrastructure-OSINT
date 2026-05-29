---
type: operational
category: agent-memory
date: 2026-05-29
status: pre-assessment (Stage -1) complete; harvest pending
---

# Agent-Memory Layer: Pre-Assessment OSINT

_NuClide Research, 2026-05-29. Stage -1 intelligence for the agent-memory survey._

The agent-memory layer is the persistence tier of the modern agent stack. It
stores long-term user memory by design: names, preferences, conversation-derived
facts, session message history, sometimes the LLM provider config the agent runs
on. That makes its data-exposure class PII-dense in a way a raw vector index is
not. This category was unmapped before this survey. There is no prior population
research, no nuclei templates, and no aimap fingerprint for any of these
platforms.

Three platforms were named at survey start (mem0, Letta, Zep). An ecosystem sweep
added two clean in-scope siblings (Redis Agent Memory Server, Cognee), one
default-credential server (Memobase), one shared-org standalone (Graphiti
server), and one deprecated long-tail target (Motorhead). Libraries and
SaaS-only products were excluded with reasons.

---

## The category-level hazard: port 8000 collision

Four of the in-scope servers default to port 8000 (Zep CE, Cognee,
Graphiti-server, Motorhead, and the Redis memory server's REST face). Per
Insight #7 and Insight #15, fingerprinting on port plus a generic `/docs`
Swagger title would inherit a heavy false-positive rate against the thousands of
unrelated FastAPI/uvicorn apps on 8000. Every fingerprint below anchors on a
vendor-unique signal: an OpenAPI `info.title`, a unique route-name set, or a
vendor response header. Port is a candidate filter only.

---

## Platform 1: mem0 / OpenMemory

mem0 ships two self-hosted servers with opposite auth postures. Do not conflate
them.

| Component | Repo path | Host port | Auth |
|---|---|---|---|
| OpenMemory (MCP memory server) | `/openmemory` | 8765 (API+MCP), UI 3000, Qdrant 6333 | NO auth, CORS `*`. The soft target. |
| mem0 OSS REST server ("Self-Hosted Server") | `/server` | 8888 (to container 8000), Postgres 8432 | Auth ON by default (JWT + `X-API-Key m0sk_`) |

OpenMemory is being sunset, with users steered to the auth-on `/server`. This is
Insight #40 inside one project: the deprecated component is auth-off, the
actively-developed replacement closed the hole.

- **Auth Default:** OpenMemory = OFF (no auth middleware, `allow_origins=["*"]`,
  routers mounted with no `Depends()`). Multi-tenancy is a caller-supplied
  `user_id` query param, an identifier not a credential. mem0 `/server` = ON
  (`AUTH_DISABLED=true` exists for local dev and logs a startup warning).
- **Default Ports:** OpenMemory 8765, UI 3000, Qdrant 6333/6334. mem0 /server
  8888, Postgres/pgvector 8432, dashboard 3000.
- **Verification Probe:** `GET http://<host>:8765/api/v1/stats/?user_id=default`.
  Confirms mem0-OpenMemory AND unauth-readable iff 200 JSON contains the field
  triple `total_memories`, `total_apps`, `apps`. Escalation read (same auth =
  none): `GET /api/v1/memories/?user_id=<id>` returns `content` (raw stored
  memory text, the PII payload). `user_id` is a required query param: omitting it
  returns 422, so the probe must include it. Enumerate `default` / `user` /
  `admin`.
- **Distinctive Fingerprint:** `/api/v1/stats/` returning
  `{total_memories,total_apps,apps}`, low collision. Strongest signature is the
  OpenAPI listing the `/api/v1/{memories,apps,stats,config}` prefix set together.
  FP traps: bare `/docs` Swagger is generic FastAPI, do not key on it;
  co-resident Qdrant on 6333 corroborates only when paired with 8765 on the same
  IP.
- **Data Exposure Class:** stored long-term memories as raw user text (PII),
  app enumeration via `/api/v1/apps`, and `/api/v1/config` exposing LLM/embedder
  provider config (can leak API keys / Ollama endpoint). Read AND write (POST
  `/api/v1/memories` works, a memory-poisoning vector). Genuine AI/LLM scope,
  not substrate.
- **Known CVEs:** none specific to mem0 application logic. No GHSA, no NVD entry,
  no public nuclei template. Greenfield.
- **Co-deployment / shadow ports:** 6333/6334 Qdrant, 3000 dashboard, 8888/8432
  if the `/server` variant, 11434 Ollama (documented local-LLM pairing),
  7474/7687 Neo4j if graph mode. TLS typically none.
- **Confidence:** HIGH on auth split, ports, endpoint shapes (all read from
  `main` source). Version drift: pre-auth `/server` builds existed before the
  auth-default flip, so an old `/server` on 8888 with no JWT is a second
  soft-target class.

Source: `mem0ai/mem0` `openmemory/api/main.py`, `routers/memories.py`,
`routers/stats.py`, `openmemory/docker-compose.yml`, `server/docker-compose.yaml`;
`docs.mem0.ai/open-source/features/rest-api`; GH Security Advisories (none).

---

## Platform 2: Letta (formerly MemGPT)

- **Auth Default:** OFF (passwordless), confirmed at source level. In
  `letta/server/rest_api/app.py` the password middleware is attached only when
  `LETTA_SERVER_SECURE == "true"` or `--secure` is passed. The canonical
  quickstart `docker run ... -p 8283:8283 letta/letta:latest` sets neither, so
  the documented happy-path deploy is fully open. The autogenerated password is
  a red herring: it only matters inside the `if` block.
- **Default Port:** 8283/tcp (FastAPI/uvicorn). API base `/v1`. Docs at `/docs`,
  spec at `/openapi.json`.
- **Verification Probe:** `GET http://<host>:8283/v1/agents/`. Expect 200 with a
  JSON array of agent objects carrying `agent_type` (enum
  `memgpt_agent`/`react_agent`/`workflow_agent`), `blocks[]` with `label` of
  `human`/`persona` and a `value`, plus `system`, `llm_config`,
  `embedding_config`. `agent_type: "memgpt_agent"` plus `blocks[].label ==
  "persona"` is the smoking gun: product AND memory served without a token. Auth
  on returns 401/403.
- **Distinctive Fingerprint:** the `/v1/agents/` `agent_type` enum plus `blocks`
  array, vendor-unique MemGPT vocabulary, very low collision. FP traps: port
  8283 alone is weak; the ADE UI is cloud-hosted at `app.letta.com` and is NOT
  served by the self-hosted server, so fingerprinting on an "ADE page" string
  misses every real instance. Anchor on the API JSON.
- **Data Exposure Class:** core memory `blocks` (the `human` block holds
  end-user personal facts, `persona` holds agent config), `system` prompts,
  `llm_config`/`embedding_config` (provider, endpoint, model handles), and
  per-agent archival memory (densest PII surface). Provider keys generally live
  in server env, not echoed in agent JSON: verify per instance, do not assume.
- **Known CVEs:**
  - CVE-2024-39025 (GHSA-7p2g-2vxc-5g55), incorrect access control, MemGPT
    <= 0.3.17. `GET /users` returned all users with no authz. CVSS 7.5 High. The
    pre-rename admin API was later removed.
  - CVE-2026-4965, letta 0.16.4, `resolve_type` in
    `letta/functions/ast_parsers.py`, code injection, flagged an incomplete fix
    of CVE-2025-6101. Remotely triggerable where user-controlled input reaches
    the AST type resolver, i.e. the network-exposed agent endpoints. CVSS not yet
    captured (NVD/VulDB returned 403); pull before citing severity.
  - No public nuclei template for Letta/MemGPT detection or these CVEs.
- **Co-deployment / shadow ports:** Postgres + pgvector is the confirmed default
  backend (bundled in the image, `/var/lib/postgresql/data`; external via
  `LETTA_PG_URI`). Shadow map: 8283 primary, 5432 Postgres, 11434 Ollama or
  8000/8080 vLLM if local LLM. ADE requires HTTPS for non-localhost, so
  internet-facing instances often sit behind nginx/Caddy/Traefik on 443: cert
  CN/SAN there is an attribution pivot.
- **Confidence:** HIGH on auth-off (read from `app.py`), port, Postgres backend,
  CVE-2024-39025, the probe field set, the ADE-is-cloud FP trap. GAP:
  `CheckPasswordMiddleware` body not retrieved, so whether it exempts
  `/v1/health` or `/openapi.json` in secure mode is unconfirmed.

Source: `docs.letta.com/guides/{docker,selfhosting}`,
`docs.letta.com/api-reference/agents/list`, `hub.docker.com/r/letta/letta`,
`letta-ai/letta` `server/rest_api/app.py`, GHSA-7p2g-2vxc-5g55.

---

## Platform 3: Zep CE / Graphiti

Scope: the self-hostable open-source server is Zep Community Edition (Go, now
parked in `legacy/` of `getzep/zep`). The current cloud product is closed.
Graphiti (`getzep/graphiti`) is separately deployable as a FastAPI REST server.

- **Auth Default:** auth-theater / effectively OFF. The shipped `legacy/zep.yaml`
  sets `api_secret:` empty. `SecretKeyAuthMiddleware` is always wired onto
  `/api/v2`, but the check is a plain compare: `if tokenString !=
  config.ApiSecret()`. With `api_secret` blank, a request carrying
  `Authorization: Api-Key ` (prefix plus empty token) splits to `["Api-Key",""]`,
  passes the prefix gate, and `"" == ""` passes the compare. So any client
  sending an empty Api-Key authenticates fully when the operator never set a
  secret, which is the out-of-box state. No startup warning, no refuse-to-boot.
  Graphiti standalone server has no auth layer at all.
- **Default Ports:** 8000 Zep CE HTTP API and Graphiti FastAPI; 8003 Graphiti
  NLP service as co-deployed by Zep CE; 5432 Postgres/pgvector (published to
  host); 7474/7687 Neo4j; 6379 Redis/FalkorDB.
- **Verification Probe:** two-step, both GET, no destructive action.
  1. Fingerprint: `GET http://<host>:8000/healthz` returns literal `.` and every
     response carries header `X-Zep-Version: <version>` (set by `SendVersion`
     middleware on all routes). The header is the hard tell.
  2. Unauth data read: `GET /api/v2/users-ordered` or `/api/v2/sessions-ordered`
     with header `Authorization: Api-Key ` (empty token). 200 with a JSON
     user/session list confirms Zep CE AND data readable unauth. Per-session
     content: `GET /api/v2/sessions/{sessionId}/memory` returns `messages[]`
     (role + raw `content`), `summary`, `facts[]`. Base path is `/api/v2`, not
     `/api/v1` (older blog docs say v1; primary source says v2).
- **Distinctive Fingerprint:** the `X-Zep-Version` response header, vendor-unique,
  present on 200s and most errors. Secondary: `/healthz` returning `.`, the
  `/api/v2/{sessions,users}-ordered` route names, lowercase `unauthorized` error
  body. FP traps: "zep" is a common token (ZeroMQ, Zeppelin), do not key on it;
  port 8000 is noisy; require the header. Graphiti standalone shares 8000 but
  exposes `/healthcheck` (not `/healthz`) and FastAPI `/docs` titled Graphiti:
  keep them as separate fingerprint specs.
- **Data Exposure Class:** PII-dense conversational memory. Unauth reach exposes
  chat message history (raw `content`), LLM-generated summaries, extracted user
  facts (`facts[]`), user records, session metadata. Graphiti backend holds the
  temporal knowledge graph in Neo4j/FalkorDB.
- **Known CVEs:** none Zep-specific, no GHSA, no nuclei template (the
  `X-Zep-Version` header would make a trivial reliable matcher, an aimap
  opportunity). The `pac4j-jwt` CVE-2026-29000 that surfaces on "JWT bypass"
  searches is unrelated (Java). The empty-default-`api_secret` behavior is
  undocumented as a risk and is the headline.
- **Default credentials in the CE stack (real foothold material):** Neo4j
  `neo4j/zepzepzep` (CE) or `neo4j/demodemo` (Graphiti `.env.example`) or
  `neo4j/password` (root compose); Postgres `postgres/postgres`. TLS: none in the
  shipped stack, bare HTTP on 8000.
- **Confidence:** HIGH on ports, empty-secret default, the auth compare logic,
  `/api/v2` base, route map, `X-Zep-Version`, co-deployed default creds, no CVE.
  The empty-Api-Key bypass is logic-confirmed from source, NOT validated against
  a running binary: label "surface open by code reading, live behavior not
  exercised" until confirmed on a local CE container. `image: zepai/zep:latest`
  is a moving tag, do not pin a fingerprint to a version string.

Source: `getzep/zep` `legacy/docker-compose.ce.yaml`, `legacy/zep.yaml`,
`legacy/src/api/{routes.go,server_ce.go}`,
`legacy/src/api/middleware/{secret_key_auth_ce.go,send_version.go}`;
`getzep/graphiti` `docker-compose.yml`, `mcp_server/.env.example`;
docs.getzep.com.

---

## Ecosystem additions (in scope)

Ranked most survey-worthy first. All auth-default claims are doc-inferred and
must be exercised on an authorized in-scope host before any tier label.

### Redis Agent Memory Server (`redis/agent-memory-server`)
First-party Redis project, actively maintained, ships FastAPI REST + MCP server.
- Auth: OFF in the documented dev path. Quick-start MCP config sets
  `"DISABLE_AUTH": "true"`; production guidance says to remove it. Default-deployed
  instances likely run unauthenticated.
- Ports: REST 8000, MCP 9000 (9050 under Compose).
- Probe: `GET /openapi.json`, expect a title referencing the service plus
  working-memory / long-term-memory route namespace. FP-risk HIGH on port 8000,
  anchor on title + memory routes.
- Data: conversation working memory + long-term semantic memory (message
  history, extracted facts, user/session IDs) in Redis.
- Source: `github.com/redis/agent-memory-server`.

### Cognee (`topoteretes/cognee`)
Knowledge-graph memory engine, real FastAPI server (`uvicorn
cognee.api.client:app`).
- Auth: effectively OFF. Gating is conditional on `REQUIRE_AUTHENTICATION=true`;
  default leaves guards inactive. Verify live.
- Port: 8000.
- Probe: `GET /openapi.json`, expect the Cognee verb routes `/api/v1/cognify`,
  `/api/v1/remember`, `/api/v1/recall`, `/api/v1/forget`, unique to Cognee, low
  collision once keyed on `/api/v1/cognify`.
- Data: ingested documents + derived knowledge graph (entities, relations,
  embeddings), dataset contents, pipeline-run/activity logs.
- Source: `docs.cognee.ai/guides/deploy-rest-api-server`,
  `topoteretes/cognee/docker-compose.yml`.

### Memobase (`memodb-io/memobase`)
User-profile long-term memory, ships a server image.
- Auth: default-creds. Local default project token is the literal string
  `secret`, a predictable bearer. Verify the check is enforced.
- Ports: container 8000, documented host mapping 8019.
- Probe: `GET /openapi.json` or `/docs`, expect Memobase title + profile/blob
  memory paths. Port 8019 is uncommon enough to assist.
- Data: per-user structured profiles (name, preferences, attributes),
  conversation blobs, extracted facts, direct PII.
- Source: `memodb-io/memobase/src/server/readme.md`.

### Graphiti server (`getzep/graphiti`, `server/` graph_service)
Standalone FastAPI over Graphiti core. Distinct deployable from Zep CE, same org.
- Auth: none documented on the REST layer; the boundary is the backing
  Neo4j/FalkorDB creds. Verify.
- Port: 8000, hard dependency on Neo4j (7474/7687) or FalkorDB.
- Probe: `GET /docs`, expect graph_service title + search/episode endpoints.
- Data: temporal knowledge graph derived from conversations.
- Source: `getzep/graphiti/server/README.md`, `hub.docker.com/r/zepai/graphiti`.

### Motorhead (`getmetal/motorhead`), legacy long-tail
Rust memory+retrieval server, DEPRECATED. Worth a low-priority sweep precisely
because abandoned-but-still-deployed instances are the unpatched tail.
- Auth: OFF, no mechanism in docs.
- Port: 8000.
- Probe: `GET /sessions/<probe-id>/memory`, expect JSON with `messages` + context
  window. The `/sessions/{id}/memory` + `/sessions/{id}/retrieval` route pair is a
  unique low-collision Motorhead signature.
- Data: raw conversation message history per session + vector retrieval store, no
  redaction.
- Source: `getmetal/motorhead`.

## Ecosystem exclusions (not self-hostable HTTP servers)

- **Memori (GibsonAI)**: Python library (BYODB) + SaaS. No first-party server.
- **Memary**: library; only HTTP surface is an optional Streamlit dashboard, the
  memory store is external Neo4j (already covered by graph-DB sweeps).
- **LangMem (LangChain)**: SDK only, "a library, not a service."
- **txtai memory mode**: ships a FastAPI server but it is general
  embeddings/semantic-search, wrong identity for an agent-memory survey. Note as
  adjacent if scope widens.
- **EmbedChain**: rebranded into mem0 (July 2024), standalone repo archived. Its
  successor is mem0, already in scope.

---

## aimap fingerprint specs to build (none exist yet)

1. **mem0-OpenMemory** (port 8765): `GET /api/v1/stats/?user_id=default` JSON has
   `total_memories` AND `total_apps` AND `apps`. Escalate to
   `/api/v1/memories/?user_id=` for `content`. Pair with co-resident Qdrant 6333
   for confidence.
2. **mem0 /server** (port 8888): `/openapi.json` lists `/memories` + `/search` +
   `/configure`; `X-API-Key` / `m0sk_` tell. Check whether auth is actually
   enforced (old builds open).
3. **Letta** (port 8283): `GET /v1/agents/` JSON array with `agent_type` enum +
   `blocks[].label` in {`persona`,`human`}. Do not key on port or an ADE page.
4. **Zep CE** (port 8000): response header `X-Zep-Version` present; `/healthz`
   returns `.`. Unauth read via empty Api-Key on `/api/v2/sessions-ordered`.
5. **Graphiti server** (port 8000): `/healthcheck` + FastAPI `/docs` titled
   Graphiti + Neo4j sidecar (7474/7687).
6. **Cognee** (port 8000): `/openapi.json` paths `/api/v1/cognify` + `/recall`.
7. **Memobase** (port 8019): Memobase OpenAPI title + profile routes; default
   token `secret`.
8. **Redis Agent Memory Server** (port 8000, MCP 9000): OpenAPI title + working /
   long-term memory routes.
9. **Motorhead** (port 8000, deprecated): `/sessions/{id}/memory` +
   `/sessions/{id}/retrieval` pair.

Cross-cutting rule: never fingerprint on port 8000 alone; anchor on the
OpenAPI title, the unique route set, or the vendor header (`X-Zep-Version`,
`m0sk_`). Auth-default claims are doc-inferred until exercised on an authorized
in-scope host.

---

## Negative space (what this method cannot see yet)

- These servers are likely Shodan-dark in the same way the embedding services
  were: JSON-only roots on shared ports that Shodan's crawler does not index
  with a distinctive string. Expect the Shodan-seeded harvest to under-count and
  to need a masscan-seeded pass on 8283 / 8765 / 8019 / 8000.
- No aimap fingerprint exists for any platform: the unknown FP rate is exactly
  why this pre-assessment ran. Fingerprints get built and sample-200 validated
  before population scale.
- Auth-default claims are read from source and docs, not from a live binary. The
  Zep empty-Api-Key bypass in particular is code-confirmed only.
