Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-17

**Re:** Unauthenticated WandB workspace proxy on `vanijmcp.adya.ai` (Adya AI infrastructure)
**IP / Host:** `20.198.18.237` / `vanijmcp.adya.ai`
**Severity:** CRITICAL

---

I'm an independent security researcher conducting good-faith AI infrastructure research under the NuClide Research umbrella (CISA disclosures CVE-2025-4364, ICSA-25-140-11). This is an unsolicited coordinated disclosure. No engagement exists with your organization. I have not queried `/runs/full` with any real entity or project value. The OpenAPI schema is the finding.

---

## Summary

`vanijmcp.adya.ai` on Microsoft Azure India is running seven services on different ports. Port 5005 hosts a custom FastAPI service named "WandB Service" with the operator's Weights & Biases credential embedded inside. Any internet client can reach this proxy and use it to query the operator's entire WandB workspace.

## Infrastructure

| Field | Value |
|---|---|
| IP | `20.198.18.237` |
| Hostname | `vanijmcp.adya.ai` |
| TLS cert SAN | `vanijmcp.adya.ai` (Let's Encrypt) |
| Hosting | Microsoft Azure, India region |
| Operator | Adya AI |

## Open ports

| Port | Service | Auth | Notes |
|---|---|---|---|
| 80 | nginx default | n/a | Welcome page |
| 443 | nginx default | n/a | Welcome page, no app behind TLS |
| 5000 | JavaScript MCP Client | **none** | Returns `{"message":"Javascript McpClient Working fine...."}` |
| 5001 | Structured API | **none** | Returns `{"Data":null,"Error":...,"Status":false}`-schema responses |
| **5005** | **WandB Service (FastAPI)** | **none** | **Embedded WandB credential proxied to any caller** |
| 5006 | Flask | **none** | 404 default; idle service |
| 5009 | Flask | **none** | 404 default; idle service |
| 8090 | Prometheus Node Exporter | **none** | Host metrics endpoint |

## The headline finding: the WandB proxy on :5005

The service's own `/openapi.json` documents it:

```json
{
  "openapi": "3.1.0",
  "info": {"title": "WandB Service", "version": "1.0.0"},
  "paths": {
    "/runs/full": {
      "get": {
        "summary": "Run Full",
        "description": "Single endpoint that returns a comprehensive payload for a W&B run: run metadata, config, summary, full history (no limit), logged artifacts metadata",
        "parameters": [{"name": "run_id"}, {"name": "run_path"}, {"name": "wandb_url"}, {"name": "entity"}, {"name": "project"}]
      }
    }
  }
}
```

`/health` confirms the upstream link is active:

```json
{"status":"healthy","service":"wandb_service","version":"1.0.0","wandb_connection":"connected"}
```

The credential is held inside the service. Any caller who supplies an `entity` and `project` (or a `wandb_url`) receives, per the schema, full run metadata, the training config, the summary metrics, the full step-level history with no limit, and the logged-artifact metadata.

## What's at stake

A WandB workspace is institutional memory for an ML team. Hyperparameter search results. Loss curves across every experiment. Final-evaluation scores. Dataset URIs. Checkpoint paths. Logged-artifact metadata typically embeds S3 or GCS URIs that point at the actual model checkpoint or dataset blob.

By embedding a WandB credential inside an unauthenticated public service, the proxy lets any internet caller pull the operator's full ML history. Calls land in WandB's audit log as queries from the embedded service account, so the actual querier is anonymous to your monitoring.

Quota and billing exposure is secondary: WandB charges by API call and storage on paid tiers; an attacker who scripts `/runs/full` against a discovered entity name can drain quota at the operator's expense.

## Recommended actions

1. **Take port 5005 off the public internet.** Bind the service to `127.0.0.1` and reach it from the upstream application on the same host. Alternatively, put it behind a reverse proxy that requires authentication (FastAPI's `Depends(...)` + a long bearer token works).
2. **Rotate the WandB API key.** The current key has been reachable from the public internet for an unknown period of time. Treat it as compromised. Generate a new key under a service account that has the minimum scopes the proxy needs.
3. **Audit WandB access logs** for queries that did not originate from your own infrastructure.
4. **Apply the same treatment to ports 5000, 5001, 5006, 5009, and 8090.** Each is reachable without authentication. The MCP-client service on 5000 in particular is a tool-execution surface; the Node Exporter on 8090 leaks host metrics that aid further targeting.

## Reference

Full case study with verbatim OpenAPI schema and the per-port enumeration:
AI-LLM-Infrastructure-OSINT/blob/main/case-studies/commercial/adya-ai-vanijmcp-2026-05-17.md

Happy to provide additional detail. No response required.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
