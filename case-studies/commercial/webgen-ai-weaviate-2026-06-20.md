---
type: case-study
severity: CRITICAL
date: 2026-06-20
title: "WebGen AI: Unauthenticated Read, Write, and Delete on an AI Web-Design Platform, With Per-Record API Keys in Schema"
summary: "An AI web-design platform serving b123.be and igt.com.hk exposed its Weaviate store with no authentication. The generation-step schema carries a per-record ai_model_key field plus full system and user prompts. Read, write, and delete were confirmed. The same host also runs an open Qdrant with twelve exposed snapshots, a second vector database on the same infrastructure."
tags:
  - weaviate
  - vector-database
  - unauth
  - cwe-306
  - llmjacking
  - rag-poisoning
sidenotes:
  - kind: host
    label: Target
    kv:
      - k: Operator
        v: "WebGen AI (b123.be / igt.com.hk)"
      - k: Sector
        v: "AI Web Design SaaS"
      - k: Location
        v: "202.66.151.79 (HK)"
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
        v: "LLM02 Sensitive Information Disclosure / LLM04 Data and Model Poisoning"
---

# WebGen AI: Unauthenticated Read, Write, and Delete on an AI Web-Design Platform

_NuClide Research -- Nicholas Kloster -- 2026-06-20_

---

## Summary

An AI web-design and generation platform reachable at b123.be and igt.com.hk exposed its Weaviate vector database on the public internet with no authentication. The schema for its generation log carries a per-record `ai_model_key` field, plus the full system prompt, user prompt, request payload, and response body for every generation step.

We confirmed read, write, and delete. We wrote one marked canary and removed it. We did not retrieve the credential field, per restraint.

The same host also runs an open Qdrant instance with twelve exposed snapshots. Two unauthenticated vector databases on one operator's infrastructure.

---

## Attack Surface

One host, two vector databases, no authentication.

| Port | Software | Role | Auth |
|------|----------|------|------|
| 8080 | Weaviate 1.27.2 | Live store: generation steps, design diffs, fix patterns | None |
| (separate) | Qdrant | Persistent snapshots, twelve exposed (documented in the Cat-13 data-at-rest survey) | None |

The host is 202.66.151.79. Both b123.be (Belgian) and igt.com.hk (Hong Kong) resolve to it.

---

## Data Exposed

Three classes. The risk is concentrated in the schema, not the row count.

| Class | Key fields |
|-------|-----------|
| WebGenStep | request_id, session_id, generation_type, request_payload, response_body, user_prompt, system_prompt, ai_model_key, tokens_used, latency_ms, page_id |
| DesignFixPattern | title, problem_signature, when_to_apply, fix_steps, patch_example_before, patch_example_after, css_snippet, expected_score_gain, source_designer_id |
| DesignDiffPackage | run_id, html_diff_summary, css_diff_summary, selectors_touched, issue_mapping |

`WebGenStep.ai_model_key` is schema-confirmed: an AI provider credential stored per generation record. We confirmed the field exists in the schema and did not read its values, per restraint ethic. If the field is populated with live keys, every record exposes the provider credential used for that generation. The class also stores the platform's full system prompts.

---

## What We Confirmed

**Read:** Schema and the WebGenStep and DesignFixPattern classes returned over plain HTTP, no credentials.

**Write:** A marked canary was accepted into the DesignFixPattern class and returned 200.

**Delete:** The canary was removed with a 204 and confirmed gone with a 404 on re-fetch.

Canary UUID `3f81599b-e47e-4c15-aaec-e4450bd0fb7d`. Written, confirmed, deleted, verified. Every change reversed.

---

## Impact

**AI credential exposure (LLMjacking):** `ai_model_key` is a per-record provider credential. Unauthenticated read allows extraction of every value. Live keys mean billing fraud, quota exhaustion, or pivot into the AI provider account. Records hitting different keys would expose different credentials.

**Prompt and IP leak:** The `system_prompt` and `user_prompt` fields expose the platform's full prompt architecture and generation strategy, complete competitive intelligence for a rival tool.

**Design pattern theft:** DesignFixPattern records hold the platform's core IP, AI-generated fix strategies with before-and-after patch examples and quality scores, readable in full over unauthenticated GET.

**Data poisoning:** Write access injects arbitrary fix patterns or generation steps, causing the platform to recommend harmful CSS or HTML to end users' projects.

**Dual-store exposure:** The same host runs an open Qdrant with twelve snapshots. Snapshots are portable: an attacker downloads them, restores them locally, and recovers the full historical dataset offline. Weaviate live data plus Qdrant persistent snapshots is the combined surface.

---

## Remediation

**Immediate (no code change):** Firewall the Weaviate and Qdrant ports to the internal network only.

**Short-term:** Enable Weaviate API-key authentication and Qdrant API-key authentication. Stop storing provider credentials inside vector records; move them to a secrets manager and reference them out of band. Rotate any key that was stored in `ai_model_key`.

**Medium-term:** Audit snapshot storage exposure. Add canary records and write monitoring to detect poisoning.

---

## Disclosure

Finding documented 2026-06-20 under NuClide Research responsible-disclosure practice. Prior coordinated disclosures from this researcher include CVE-2025-4364 and ICSA-25-140-11, both through CISA.
