# LightRAG Security Advisory — /health Endpoint Leaks Runtime Configuration

**Submit at:** https://github.com/HKUDS/LightRAG/security/advisories/new

---

## Summary (paste into GitHub form)

Unauthenticated /health endpoint leaks LLM provider, model, and working directory paths on all instances

---

## Severity

Medium

## CWE

CWE-200 (Exposure of Sensitive Information to an Unauthorized Actor)

---

## Description (paste into GitHub form)

## Summary

The `/health` endpoint is whitelisted by default in `WHITELIST_PATHS` (`config.py:641`), bypassing `combined_auth` entirely. The response includes sensitive runtime configuration — LLM provider, model name, embedding model, working directory paths, and internal host addresses — regardless of whether `AUTH_ACCOUNTS` is configured. Instances with authentication fully enabled are equally affected.

## Affected Versions

All versions with the API server enabled (tested against v1.3.x through v1.5.3).

## Root Cause

**`lightrag/api/config.py:641`**
```python
args.whitelist_paths = get_env_value("WHITELIST_PATHS", "/health,/api/*")
```

`/health` is in the default whitelist. `combined_auth` (`utils_api.py:128-134`) checks whitelist first and returns immediately — no token required.

**`lightrag/api/lightrag_server.py:2286-2357`**

The `/health` response body includes:
- `working_directory` — full filesystem path (leaks cloud provider, username, project name)
- `input_directory` — full filesystem path
- `configuration.llm_binding` — LLM provider (anthropic, openai, azure_openai, aws_bedrock, ollama, openrouter)
- `configuration.llm_model` — model name (e.g. claude-haiku-4-5, gpt-4o-mini)
- `configuration.llm_binding_host` — host address for self-hosted providers
- `configuration.embedding_binding` + `embedding_model`
- `configuration.rerank_binding` + `rerank_model`
- `auth_mode` — reveals whether auth is configured

## Proof of Concept

Against any LightRAG instance regardless of auth configuration:

```bash
curl -s http://<host>:<port>/health | python3 -m json.tool
```

Example response from an auth-enabled instance:
```json
{
  "status": "healthy",
  "working_directory": "/home/azureuser/elitra-light-rag/",
  "configuration": {
    "llm_binding": "anthropic",
    "llm_model": "claude-haiku-4-5",
    "embedding_model": "text-embedding-3-small"
  },
  "auth_mode": "enabled"
}
```

The `working_directory` field names the cloud provider (Azure), OS username, and project name. In a population survey of 67 deployed LightRAG instances, all 67 returned this data — including instances with `auth_mode: enabled`.

## Impact

- **LLM provider and model disclosure** — reveals which AI provider and specific model the operator uses; enables targeted attacks if auth is separately bypassed
- **Operator attribution** — `working_directory` paths name the operator (`/home/azureuser/elitra-light-rag/`, `/usr/local/eagletalent/robot-graphrag/`, `/home/ubuntu/aidsmo-chatbot/`)
- **Infrastructure mapping** — `llm_binding_host` exposes internal host addresses for self-hosted providers
- Affects instances with auth fully enabled, not only misconfigured deployments

## Recommended Fix

**Option A (preferred):** Strip sensitive fields from the `/health` response. Return only liveness signals:

```python
return {
    "status": "healthy",
    "auth_mode": auth_mode,
    "core_version": core_version,
    "api_version": api_version_display,
    "pipeline_busy": pipeline_busy,
}
```

Move full configuration to a separate authenticated endpoint (e.g. `/api/status` or `/admin/config`).

**Option B:** Remove `/health` from the default `WHITELIST_PATHS`. Add a separate unauthenticated liveness probe (`/healthz` or `/ping`) that returns only `{"status":"ok"}` with no configuration data.

## Reporter

Nicholas Kloster — Nuclide Research (nicholas@nuclide-research.com)
Independent security researcher. CISA disclosures: CVE-2025-4364, ICSA-25-140-11.
Discovered during population-scale survey of deployed AI/RAG infrastructure.
