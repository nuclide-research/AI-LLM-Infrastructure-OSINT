# evidence/

Forensic recon evidence for case studies and methodology insights.
Each subdirectory corresponds to a single survey or single-host
deep-dive and contains the raw artifacts referenced in the case
study's "Evidence pack" section.

## Layout

- `2026-05-10-phoenix-survey/recon/` — Arize AI Phoenix population
  sweep: 92-host Shodan harvest, GraphQL probes, project enumeration,
  span samples (Lillia / Kapture / MCM / brand-monitor), VisorGraph
  traces, BARE semantic-match output, version survey, IP-direct-shadow
  sweep results.
  - Case study: `case-studies/commercial/phoenix-llm-observability-survey-2026-05-10.md`
  - Methodology: `methodology/insight-12-ip-direct-shadow.md`

- `2026-05-10-reputacion-digital/recon/` — single-host multi-surface
  deep-dive on `190.210.105.193`: Phoenix + NFS + Prometheus +
  MailCatcher + 126-subdomain CT-log enumeration + OpenAPI specs
  for `accounts.*`, `manager.*`, `llm.*` (LiteLLM).
  - Case study: `case-studies/commercial/AR-reputacion-digital-multi-surface-2026-05-10.md`

## Disclosure considerations

These directories contain **third-party customer data** sampled during
research-mode probing. Files include:

- Real LLM trace spans with operator-internal data (system prompts,
  agent topology, customer queries, model identity)
- Persistent customer identifiers in some samples (Lillia patient
  food logs, session UUIDs)
- Public OpenAPI specs (already publicly served by the operator,
  re-published here for verifiability)

Pre-disclosure publication of this evidence is intentional in this
repository. The case studies above describe the operators and the
data classes; the evidence pack provides the artifacts that ground
those claims.
