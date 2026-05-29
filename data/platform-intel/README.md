# Platform Intelligence

Pre-survey OSINT collected before Shodan harvests. Each file documents auth posture, dork candidates, verification probes, and data exposure classes for a platform category. Purpose: tune queries, not replace them.

## Files

| File | Platforms | Date |
|------|-----------|------|
| [workflow-orchestration-osint-2026-05-27.md](workflow-orchestration-osint-2026-05-27.md) | Temporal, Cadence, Conductor, Flyte, Mage.ai, ZenML, Kestra, DolphinScheduler, Windmill, Restate, Hatchet, Argo Workflows, Kubeflow Pipelines, Dagster, Prefect, Airflow | 2026-05-27 |
| [agent-memory-osint-2026-05-29.md](agent-memory-osint-2026-05-29.md) | mem0/OpenMemory, Letta (MemGPT), Zep CE/Graphiti, Redis Agent Memory Server, Cognee, Memobase, Motorhead | 2026-05-29 |

## Format

Each platform entry follows:

- **Auth Default:** off / default-creds / auth-theater / on
- **Shodan Dorks:** primary + secondary candidates
- **Verification Probe:** endpoint + expected response fields for confirmation
- **Data Exposure Class:** what an attacker reads on unauth access
- **Known CVEs:** with CVSS where available
- **Default Credentials:** where applicable
- **Notes:** operational context, FP risks, chain primers
