---
type: case-study
severity: CRITICAL
date: 2026-06-20
title: "Trading AI Agent: Unauthenticated Weaviate Read, Write, Delete and Agent Memory Poisoning"
summary: "A personal trading AI assistant exposed its Weaviate vector store on the public internet with no authentication. We confirmed unauthenticated read, write, and delete with a reversed canary. The agent's memory and email pipeline are writable, which lets an attacker plant fabricated trade recommendations and broker alerts the agent treats as ground truth."
tags:
  - weaviate
  - vector-database
  - unauth
  - cwe-306
  - financial
  - personal-finance
sidenotes:
  - kind: host
    label: Target
    kv:
      - k: Operator
        v: "Personal trading AI assistant (unattributed)"
      - k: Sector
        v: "Personal Finance / Trading"
      - k: Location
        v: "165.22.230.132 (DigitalOcean)"
      - k: Severity
        v: CRITICAL
  - kind: see-also
    label: Classification
    kv:
      - k: Primary
        v: "CWE-306 Missing Authentication for Critical Function"
      - k: Secondary
        v: "CWE-284 Improper Access Control"
      - k: OWASP
        v: "LLM04 Data and Model Poisoning"
---

# Trading AI Agent: Unauthenticated Weaviate Read, Write, Delete and Agent Memory Poisoning

_NuClide Research -- Nicholas Kloster -- 2026-06-20_

---

## Summary

A personal trading AI assistant ran its Weaviate vector store on the public internet with no authentication. Weaviate is both the agent's memory and the semantic search engine for its email pipeline. Anyone on the internet could read the store, write new records, and delete records.

We confirmed read, write, and delete. We wrote a canary into the store, confirmed it landed, then deleted it.

The primary risk is not the data sitting in the store today. It is the writable agent memory. An attacker can plant fabricated trade recommendations and broker alerts that the agent reads back as authoritative ground truth on its next session, with the human approval gate bypassed and no audit trail.

---

## Attack Surface

| Port | Software | Role | Auth |
|------|----------|------|------|
| 8080 | Weaviate 1.27.3 | Vector memory store and semantic search engine | None |

The store is configured with `text2vec-ollama` and `generative-ollama` modules. A local Ollama instance handles vectorization and generation. Ollama is not externally reachable on port 11434, internal only.

---

## What We Confirmed

**Read:** Pulled the schema and all stored objects without credentials. HTTP 200.

**Write:** Inserted a marked canary record into the `TradingEmails` class. The batch API returned `STATUS=SUCCESS`. HTTP 200.

**Delete:** Removed the canary object. HTTP 204.

Canary UUID `050e1c0f-e910-4134-91e0-bdfbc615cdb0` was written to `TradingEmails`, confirmed, then deleted. Every test artifact we created we removed.

Node topology reported `lastSnapshotIndex: 0`, meaning the store has no recovery point. A delete is permanent.

---

## Data Exposed

The store held two collections.

| Class | Records | Content |
|-------|---------|---------|
| TradingEmails | 0 | Schema defined, email pipeline ready, not yet populated |
| AgentMemory | 2 | Agent conversation history and learnings |

`TradingEmails` is empty today but its schema is live and waiting for ingestion. The schema names the data class that will flow through it: `messageId`, `subject`, `senderEmail`, `senderName`, `contentClean` (full cleaned email body), `dateReceived`, an LLM-generated `summary`, a `sentiment` score, a `priorityScore`, auto-generated `tags`, and `extractedTickers` (stock tickers auto-extracted from each email). Once populated this becomes a readable trading inbox: broker communications, position-revealing emails, and machine-scored sentiment and priority.

`AgentMemory` held two records. Its schema is `query`, `context`, `toolsUsed`, `outcome`, `learning`, `timestamp`, and an `approved` boolean human-approval gate. The two stored records were a capability-map greeting and an embedding integration test. They expose the agent's tool list: email search, market data, trade planning, news research, and diary search.

We do not publish record values. The schema names, class names, and counts are the finding.

---

## Impact

**Read.** The agent's full capability map is exposed through `AgentMemory`, including its live tool integrations. When `TradingEmails` is populated, the entire trading inbox becomes readable: broker mail, positions, extracted tickers, and LLM sentiment and priority scores.

**Write, the primary risk.** Both classes are writable. An attacker can insert an `AgentMemory` record with `approved: true`, which bypasses the human approval gate. The agent reads that record as authoritative ground truth on its next session. There is no audit trail. An attacker can plant a fabricated learning such as a standing instruction to always recommend selling a given ticker, and the agent will act on it. The attacker can also inject a fabricated broker alert into `TradingEmails` with a maximum `priorityScore` and a strongly negative `sentiment`, so it surfaces first in semantic search and shapes trade decisions.

**Delete.** A single batch delete wipes all agent memory and reverts the agent to a blank state with all learnings lost. A schema delete is full destruction. With `lastSnapshotIndex: 0` there is no recovery point.

The asymmetry is total. The attacker writes one record and leaves. The user triggers the harm on their next session by trusting their own assistant. The financial outcome is real and may never be traced back to the poisoned store.

---

## Remediation

**Immediate (no code change required):** Firewall port 8080 to the internal network only.

**Short-term:** Enable Weaviate's API-key or OIDC authentication. Set `AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=false`. Add audit logging for writes and deletes.

**Medium-term:** Plant canary records in the production store to detect unauthorized writes. Configure snapshots so a destructive change has a recovery point. Monitor retrieval-distribution for ranking anomalies that signal a planted record surfacing.

---

## Disclosure

Finding documented 2026-06-20 under NuClide Research responsible-disclosure practice. Prior coordinated disclosures from this researcher include CVE-2025-4364 and ICSA-25-140-11, both through CISA.
