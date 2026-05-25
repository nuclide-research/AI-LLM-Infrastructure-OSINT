# modengy_v3 — Working Notes

**Host:** 72.56.96.229
**Cloud:** DigitalOcean
**Status:** Initial probe complete
**Priority:** 5

---

## Confirmed Services

| Port | Service | Auth |
|---|---|---|
| 8000 | LangGraph — "modengy_v3", engine: LangGraph | NONE |
| 6333 | Qdrant 1.13.4 | NONE |
| 5678 | n8n 2.13.4 | ENFORCED (401 on /rest/workflows) |

## Root Response

```json
{"status": "ok", "bot": "modengy_v3", "engine": "LangGraph"}
```

## Qdrant

- Version: 1.13.4 (commit 7abc6843)
- Collections: ["modengy"] — single collection, name matches bot identity
- Auth: NONE

## n8n

- Version: 2.13.4
- Environment: development
- Auth: ENFORCED — 401 on /rest/workflows

## Key Pattern

Bot name in LangGraph root (`modengy_v3`) matches the Qdrant collection name (`modengy`). Single-tenant stack. One agent, one knowledge base. The n8n workflow automation layer is enforced while the LangGraph and Qdrant layers are open — inconsistent auth posture within the same stack.

## Pending Probes

- [ ] GET /qdrant/collections/modengy — point count (not content)
- [ ] LangGraph /threads — thread list
- [ ] PTR / ASN attribution
- [ ] What "modengy" is — product or operator name?
- [ ] n8n version implies the operator knows n8n needs securing — why not LangGraph/Qdrant?
