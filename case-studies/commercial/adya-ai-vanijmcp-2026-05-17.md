---
type: case-study
---

# Adya AI: WandB workspace exfil via unauth FastAPI proxy (vanijmcp.adya.ai)

_NuClide Research, 2026-05-17_
_Part of the training-observability survey._

---

## Summary

`vanijmcp.adya.ai` (`20.198.18.237`) is an Adya AI infrastructure host on Microsoft Azure India. It exposes seven services on different ports. The headline finding is on port 5005: a custom FastAPI service named "WandB Service" with embedded Weights & Biases credentials. Any internet client can query it and receive the operator's entire WandB workspace, including project metadata, training runs, configs, summaries, full training-history time series, and logged-artifact metadata.

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, S7068, S7075, S7076, T5904
- **733 (AI Risk & Ethics Specialist):** K7040, K7052, S7056, S7067, T5868, T5893
- **overlap (Common AI KSATs (all 5 roles)):** K1158, K1159, K22, K6311, K6935, K7003, K7024, K7041

<!-- ksat-tag:auto-generated:end -->

This is a new exposure class. Most training-observability surveys look at the platform UI (WandB SaaS, ClearML, MLflow). This is a custom proxy service the operator wrote in-house. The proxy holds the credential and gives any caller the operator's workspace.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | `20.198.18.237` |
| Hostname | `vanijmcp.adya.ai` |
| TLS cert SAN | `vanijmcp.adya.ai` (Let's Encrypt) |
| Hosting | Microsoft Azure, India region |
| ASN | AS8075 (Microsoft Corporation) |
| Operator | Adya AI (`adya.ai`) |

## Open ports and services

| Port | Service | Auth | Notes |
|---|---|---|---|
| 80 | (nginx default) | n/a | Welcome page |
| 443 | nginx default | n/a | Welcome page, no app |
| 5000 | JavaScript MCP Client | none | `{"message":"Javascript McpClient Working fine...."}` |
| 5001 | Structured API | none | Returns `{"Data":null,"Error":...,"RequestId":...,"Status":false}` schema; current state returns 500 |
| 5005 | **WandB Service (FastAPI)** | **none** | **Embedded WandB credentials; proxies queries to the operator's WandB workspace** |
| 5006 | Flask | none | 404 default page |
| 5009 | Flask | none | 404 default page |
| 8090 | Prometheus Node Exporter | none | System metrics endpoint |

---

## The WandB proxy in detail

`/openapi.json` returns the full FastAPI schema:

```json
{
  "openapi": "3.1.0",
  "info": {"title": "WandB Service", "version": "1.0.0"},
  "paths": {
    "/runs/full": {
      "get": {
        "summary": "Run Full",
        "description": "Single endpoint that returns a comprehensive payload for a W&B run:\n- run metadata (name, state, tags, timestamps)\n- config, summary\n- full history (no limit)\n- logged artifacts metadata",
        "parameters": [
          {"name": "run_id"},
          {"name": "run_path"},
          {"name": "wandb_url"},
          {"name": "entity"},
          {"name": "project"}
        ]
      }
    },
    "/health": { ... },
    "/": { ... }
  }
}
```

The `/health` endpoint confirms upstream connectivity:

```json
{"status":"healthy","service":"wandb_service","version":"1.0.0","wandb_connection":"connected"}
```

`wandb_connection: "connected"` indicates the service has authenticated to Weights & Biases. The credential is held inside the service and reused for every incoming query.

`/runs/full` with no parameters returns:

```json
{"detail":"Provide run_id or run_path or wandb_url"}
```

A caller who knows the operator's entity name (or any project they own) can supply `entity=adya&project=<name>` and the service will return the full run history, the training config, the summary metrics, and the logged-artifact metadata. The schema explicitly states "full history (no limit)".

### What's reachable through the proxy

| Data class | Exposure via /runs/full |
|---|---|
| Training run names, states, tags, timestamps | Yes |
| Hyperparameter config (every config knob, by run) | Yes |
| Final-summary metrics (accuracy, loss, etc., by run) | Yes |
| Full training-step history (every metric, every step) | Yes |
| Logged-artifact metadata (model checkpoints, datasets) | Yes |

Logged-artifact metadata typically includes the artifact URI in S3 or GCS. A caller who reads the metadata can often follow the URI to the underlying model checkpoint or dataset if those buckets are configured for public read.

---

## Restraint

We did not query `/runs/full` with any real `entity` or `project` value. The OpenAPI schema is the finding. The schema confirms the service exists, identifies its upstream connection state as "connected", and enumerates the exposed query shape. Confirming exploitability beyond that point is not necessary for a coordinated-disclosure record and reads operator data we have no right to read.

We also did not enumerate `/metrics` on the Prometheus Node Exporter (`:8090`) beyond confirming it returned the Node Exporter landing page.

---

## Why it matters

A WandB workspace is where the operator stores everything about their model training. Hyperparameter search results. Loss curves. Final-evaluation scores. Dataset references. Checkpoint paths. For an MLOps-heavy company, the WandB workspace is the institutional memory of the ML org.

By embedding a WandB API key inside an unauthenticated public service, Adya has handed any caller the keys to that institutional memory, with no log entry on the WandB side identifying the actual querier (every call appears to WandB as a query from the embedded service account).

Quota and billing exposure is secondary but real. WandB charges by API call and storage on paid tiers; an attacker who scripts `/runs/full` against a discovered entity name can drain quota at the operator's expense.

---

## Disclosure routing

| Channel | Address | Severity |
|---|---|---|
| Primary | (TBD — Adya AI security contact via adya.ai) | CRITICAL |
| Cloud abuse | abuse@microsoft.com | informational |

Adya AI's public-facing site (`adya.ai`) is a single-page React landing page with no `/contact` route exposing an email. We will reach out via the registered company contact channel (LinkedIn / direct outreach).

---

## One-line fixes (per port)

```yaml
# 5005 — WandB Service
#   Add API-key auth (FastAPI Depends + Authorization header), or bind to
#   127.0.0.1 and front via the authenticated upstream service.
#   Rotate the WandB API key embedded in the service.

# 5000 / 5001 — MCP / structured API
#   Same: bind to loopback or add auth.

# 8090 — Node Exporter
#   Bind to 127.0.0.1 and scrape from a Prometheus on the same host or
#   over a VPN/WireGuard tunnel.
```

---

## See also

- [Companion training-observability survey 2026-05-17](training-observability-survey-2026-05-17.md)
- [`../../methodology/insight-04-whois-over-slug-heuristics-for-disclosure-routing.md`](../../methodology/insight-04-whois-over-slug-heuristics-for-disclosure-routing.md)
