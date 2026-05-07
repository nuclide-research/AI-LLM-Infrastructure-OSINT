---
to: abuse@ovh.net
cc: abuse@nuclide-research.com
severity: HIGH
ip: 92.222.230.219
institution: OVH SAS (hindsight-mcp v3.1.1 personal-AI-memory CRUD fully exposed)
status: DRAFT
outcome: sent
date: 2026-05-04
---

**To:** abuse@ovh.net
**Cc:** abuse@nuclide-research.com
**Subject:** Unauthenticated personal-AI-memory MCP server (29-tool CRUD incl. clear_memories/delete_bank) — 92.222.230.219:8888

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-04

**Re:** Unauthenticated `hindsight-mcp-server v3.1.1` exposing 29-tool personal-AI-memory CRUD
**IP / Host:** 92.222.230.219 (OVH France)
**Severity:** HIGH

---

I'm an independent security researcher conducting good-faith AI infrastructure research under the NuClide Research umbrella (CISA disclosures CVE-2025-4364, ICSA-25-140-11). This is an unsolicited coordinated-disclosure notification.

---

## Summary

An OVH customer at `92.222.230.219:8888` is running `hindsight-mcp-server v3.1.1`, a personal-AI-cognition / memory MCP server. The server exposes **29 tools** without authentication, covering full CRUD on the operator's AI memory state — including destructive operations (`clear_memories`, `delete_bank`, `delete_mental_model`).

Found during NuClide Research's MCP cross-cloud survey (2026-05-04). Full case study: https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/commercial/mcp-cloud-survey-2026-05.md (search for "F6 — `hindsight-mcp-server` cluster").

## Confirmed exposure

`POST /` (JSON-RPC) returns valid `initialize` response identifying the server as `hindsight-mcp-server v3.1.1`. `tools/list` enumerates 29 callable tools, all unauthenticated:

```
retain, recall, reflect,
list_banks, create_bank, get_bank, get_bank_stats, update_bank, delete_bank, clear_memories,
list_mental_models, get_mental_model, create_mental_model, update_mental_model, delete_mental_model, refresh_mental_model,
list_directives, create_directive, delete_directive,
list_memories, get_memory, delete_memory,
list_documents, get_document, delete_document,
list_operations, get_operation, cancel_operation, list_tags
```

Verification was non-destructive: only `initialize` and `tools/list` were called. No memories were retrieved, no documents accessed, no banks deleted, no operations canceled.

## Why it matters

The server's name + tool surface suggests this is the operator's **personal AI cognition store** — every memory, mental model, and document the operator has accumulated for their AI assistant to use is reachable + readable + **destructible** by any unauthenticated internet caller.

- Read tools (`recall`, `list_memories`, `get_memory`, `get_document`) leak the operator's accumulated AI-assistant context — personal notes, conversation history, ingested documents
- Mutate tools (`update_mental_model`, `create_directive`) allow injection of attacker-controlled content into the operator's AI working memory
- **Destructive tools (`clear_memories`, `delete_bank`, `delete_memory`)** allow irreversible destruction of the operator's accumulated context

## Fleet context

We identified **18 instances** of `hindsight-mcp-server` across our cross-cloud scan; **17 returned empty `tools/list`** (auth-gated in v3.2.x), but **this v3.1.1 instance returned the full 29-tool surface**. The version-3.1.1 outlier suggests an older deployment that pre-dates an auth-gating fix in v3.2.x. The operator should upgrade to a current version OR enforce auth at the network edge.

## Remediation

Either upgrade the deployment to a current `hindsight-mcp-server` release with auth-gated `tools/list` invocation, or restrict network access:

```
# Bind to localhost:
HOST=127.0.0.1 PORT=8888 hindsight-mcp-server

# Or firewall:
ufw deny 8888/tcp
ufw allow from 127.0.0.1 to any port 8888
```

If destructive tools (`delete_*`, `clear_memories`) have been called from an unrecognized source during the exposure window, restore from backup.

## Reference

Full case study:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/commercial/mcp-cloud-survey-2026-05.md

I'm happy to answer questions or assist with verification.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
