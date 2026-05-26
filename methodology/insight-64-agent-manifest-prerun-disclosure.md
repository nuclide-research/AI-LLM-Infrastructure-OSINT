# Insight #64: AI Agent Manifests Are Pre-Run Disclosure

**Date:** 2026-05-26  
**Survey anchor:** Cat-06 stragglers — Agno (AIRIAD Risk Advisor, Collision Analysis AgentOS)  
**Status:** Confirmed

---

## Statement

The `/agents` endpoint on an unauth Agno (or similar framework) deployment is a finding in itself — before any run is invoked. The agent description tells you what data sources the system can reach. Invoking a run is not required to establish severity.

---

## Evidence

**`34.57.75.173` — AIRIAD Risk Advisor (GCP/US)**

```json
[
  {"name": "ContractAgent", "description": "Parse project contract documents (SOW, Change Requests, BRD) for a given project"},
  {"name": "EmailsAgent", "description": "Analyze client email threads for project risk signals. Produces RED/YELLOW/GREEN"},
  {"name": "CallsAgent", "description": "Analyze Fireflies call transcripts for project risk signals."},
  {"name": "DeliveryAgent", "description": "Analyze Asana task snapshots and Smartsheet timeline data for delivery risk"},
  {"name": "AdvisorAgent", "description": "Synthesize sub-agent reports (contract summary, email risks, call risks, delivery)"}
]
```

No run triggered. The manifest alone confirms: client SOW documents, email threads, Fireflies call transcripts, Asana project data, and Smartsheet timelines are in scope for this system and accessible to any caller who can reach the API.

**`5.78.111.11` — Collision Analysis AgentOS (Hetzner/DE)**

```json
[
  {"name": "Router Agent"},
  {"name": "PDF Knowledge Agent"},
  {"name": "PostgreSQL Data Agent"}
]
```

"PostgreSQL Data Agent" confirms a live database connection behind this agent. No run triggered. The name proves the data class.

---

## Mechanism

Agent frameworks describe their agents in natural language for usability. The description is human-readable documentation of what the agent does and what it can access. When this manifest is publicly readable without authentication, the documentation becomes an attack surface map.

For classification purposes: an unauth `/agents` endpoint where any agent description references:
- A database (PostgreSQL, MySQL, MongoDB, Elasticsearch)
- Email or communication data (Gmail, Outlook, Slack, Fireflies)
- Confidential document types (contracts, SOW, BRD, medical records)
- Financial or PII data sources

...is CRITICAL regardless of run-invocation state. The manifest proves what the attacker can reach by invoking a run.

---

## Relation to prior insights

- **Insight #3** (handshake leaks structure): the agent manifest is the equivalent of the MCP `initialize` response's capabilities object — structure disclosed before the operation is exercised.
- **Insight #63** (install experience predicts auth posture): Agno is local-first, single-binary-install, and ships auth-off-default. The manifest is unprotected for the same reason the API is unprotected.
- **Restraint ethic**: names ARE the finding. Stop at the manifest. Do not invoke agent runs against operator deployments.

---

## Implication for enumeration

When fingerprinting agent framework deployments, the auth-classification probe should be:

1. Can you reach `/agents` (or equivalent manifest endpoint) without credentials?
2. Do any agent descriptions reference sensitive data sources?

If both: CRITICAL, regardless of whether runs are accessible or blocked downstream.

This generalizes beyond Agno: LangGraph (`/info`), OpenHands (`/api/v1/settings`), CrewAI Studio (`/api/crews`), and any agent framework with an unauth API catalog endpoint follows the same pattern.

---

## Cross-references

- Cat-06 case study: `case-studies/commercial/agno-gptresearcher-agentgpt-cat06-stragglers-2026-05-26.md`
- Insight #3: MCP handshake structure disclosure
- Insight #63: install experience predicts auth posture
