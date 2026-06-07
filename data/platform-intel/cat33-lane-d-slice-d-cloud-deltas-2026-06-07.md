# Cat-33 Lane D Slice D: Cloud-Native + Sibling-Deltas

_Phase 5 Slice D return, generated 2026-06-07. Parent: `categories/33-ai-email-guardrails-deep-brief-2026-06-06.md`. Lane D summary: `data/platform-intel/cat33-lane-d-vendors-2026-06-07.md`. Question this slice answers: when LiteLLM wraps a cloud-native guardrail, is it a transparent passthrough or does it add attack surface?_

## Slice scope

6 targets, delta-focused: bedrock_guardrails, openai (moderation), azure (content safety, two endpoints), presidio (OSS), lakera_ai (v1 vs v2 delta only). No microsoft_purview entry written here; Slice A produced `~/tome/platforms/microsoft-purview.json` and Azure Content Safety is a SIBLING product, not a duplicate, so I wrote it as its own platform entry with an explicit cross-reference.

## Breakdown by entry type

| Target | Class | Tome action |
|---|---|---|
| AWS Bedrock Guardrails | cloud_native | NEW `bedrock-guardrails.json` |
| OpenAI Moderation | cloud_native | NEW `openai-moderation.json` |
| Azure AI Content Safety | cloud_native | NEW `azure-content-safety.json` (sibling to Slice A's microsoft-purview) |
| Microsoft Presidio | framework (OSS) | NEW `presidio.json` |
| Lakera v1 vs v2 | delta on existing | APPENDED `litellm_v1_vs_v2_delta` block to existing `lakera-guard.json` |

5 files touched: 4 new, 1 delta-appended. Microsoft Purview cross-reference noted in `azure-content-safety.json` only; no duplicate platform JSON written.

## The load-bearing question: transparent passthrough or added surface?

Per cloud target.

### AWS Bedrock Guardrails

**Verdict: NOT a transparent passthrough.**

The cloud-native API is unchanged. LiteLLM wraps it by storing AWS creds (or AWS_BEARER_TOKEN_BEDROCK), formatting the ApplyGuardrail POST, and post-processing the response with `_redact_pii_matches` before returning to the caller. Added surface:

- AWS keys land in the LiteLLM proxy `.env` and DB.
- LiteLLM `/guardrails/list` discloses guardrail presence to anyone with proxy read.
- LiteLLM custom-code guardrail CVE-2026-40217 (sandbox escape) lives in the same `guardrail_hooks/` namespace; one config line away from Bedrock-wrapping operators.
- LiteLLM-side response masking (`_redact_pii_matches`) re-processes Bedrock JSON; an LiteLLM bug here would alter apparent guardrail decisions without touching Bedrock.

The cloud guardrail did not get less secure. The operator's blast radius widened because credentials are now centralized at a CVE-rich proxy.

### OpenAI Moderation

**Verdict: mostly transparent passthrough at the protocol layer.**

Same `POST /v1/moderations`, same Bearer auth, same payload `{model, input}`. The wrapper adds:

- `api_base` is operator-overrideable and NOT allowlisted. Misconfigure it and every moderated message is exfiltrated to attacker host. This is the highest-impact added surface.
- `raise_exception=False` / `mask_response_content` paths allow a "log only" mode where harmful content passes through while dashboards report "guardrail active." Policy ambiguity is the operator failure mode.
- Single OPENAI_API_KEY usually serves BOTH chat completion AND moderation; one leak burns both.

The OpenAI API itself is unchanged. The wrapper introduces a redirection primitive (`api_base` override) that direct callers do not have.

### Azure AI Content Safety

**Verdict: mostly transparent at the API contract.**

Same `/contentsafety/text:shieldPrompt` and `/contentsafety/text:analyze` endpoints, same `Ocp-Apim-Subscription-Key` header, same `api-version=2024-09-01` query pin. The wrapper adds one structural attack surface direct callers do not have:

- `AZURE_CONTENT_SAFETY_MAX_TEXT_LENGTH = 10000` hardcoded chunking with word-boundary splitter. An attacker who knows the chunking boundary can craft cross-chunk evasion: each chunk benign in isolation, malicious in aggregate. Direct API callers handle their own splitting and would not introduce this vector for free.

Plus the standard wrapper additions: subscription key centralization, `/guardrails/list` disclosure, LiteLLM CVE chain inheritance.

Sibling note: Azure Content Safety is NOT Microsoft Purview. Purview = governance/DLP at rest. Content Safety = realtime moderation in transit. Slice A's `microsoft-purview.json` covers Purview; this entry covers Content Safety. Operators commonly conflate the two; the disclosure paths overlap (MSRC) but the products do not.

### Cross-cloud verdict summary

| Cloud target | Passthrough? | Highest-impact added surface |
|---|---|---|
| AWS Bedrock | NO | Credential centralization at CVE-rich LiteLLM proxy |
| OpenAI Moderation | mostly | `api_base` override = trivial exfil redirect |
| Azure Content Safety | mostly | Hardcoded 10K chunking = cross-chunk evasion vector |

**Pattern.** No LiteLLM cloud wrapper is fully transparent. Each one adds at least one of (credential centralization, control-plane disclosure, policy ambiguity, wrapper-side processing, hardcoded behavior). The cloud guardrail itself is unchanged in every case; the operator's blast radius widens in every case. The framework-vs-deployment discipline from the Lane D summary applies here too: the cloud API is the framework, the LiteLLM-wrapping proxy is the deployment.

## Presidio (OSS framework, not cloud-native)

Treated the same as LlamaFirewall and OpenGuardrails in yesterday's Lane D summary: framework count, not deployment count. Notable specifics:

- Two-service architecture: analyzer on :5001, anonymizer on :5002. Both ship with NO authentication.
- LiteLLM wrapper defaults `presidio_*_api_base` to plain `http://` when scheme is missing. PII unencrypted in transit by default. This is the most consequential default I found in the entire slice.
- `pii_tokens` in-memory mapping (original -> masked) lives in proxy memory for un-anonymization. Any LiteLLM memory-disclosing CVE dumps this table.
- `mock_testing=True` is a silent bypass that returns canned `mock_redacted_text` regardless of input. Operators who left it on after dev shipped a fake guardrail.
- `ad_hoc_recognizers` loaded from operator-supplied path = regex-injection foothold if path is writable.

Dork population substitution risk: HIGH. Same logic as the Lane D summary. The library-mode Python-import population is invisible; the docker-compose-on-routable-host population is what Shodan sees.

## Lakera v1 vs v2 delta

Read both LiteLLM modules. Same SaaS (`api.lakera.ai`), same env var (`LAKERA_API_KEY`), same Bearer auth, same network fingerprint, same `ssl.cert.subject.cn` pivot. **One tome entry covers both; v2 does not earn a separate platform JSON.** Decision recorded in `lakera-guard.json` under `litellm_v1_vs_v2_delta.tome_separate_entry_decision: NO`.

What changes:

| Axis | v1 (`lakeraAI_Moderation`) | v2 (`LakeraAIGuardrailV2`) |
|---|---|---|
| Endpoint | POST `/v1/prompt_injection` | POST `/v2/guard` |
| Model field | `lakera-guard-1` (client-supplied) | server-side selection |
| Capabilities | Prompt injection only | Prompt injection + PII detection/masking + per-detector breakdown |
| Scope | Any LiteLLM call type | Chat completions ONLY per source comments (NOT Responses API, NOT /v1/messages, NOT MCP, NOT A2A) |
| Request | `{input: [{role, content}, ...]}` | messages + `payload` (PII redaction) + `breakdown` (per-detector results) |

Added attack surface in v2 vs v1:

1. `payload=true` PII masking creates an in-memory original-to-masked token mapping (same risk pattern as Presidio wrapper).
2. `breakdown=true` returns per-detector results. An attacker reading guardrail responses learns Lakera's detector taxonomy on every call, which feeds evasion development.

Temporal signal: operators still on v1 are either running older LiteLLM or have a non-chat-completions use case. This is an operator-config-layer signal, not a network-layer signal; passive enumeration cannot distinguish v1 from v2 users.

## Files written

- `~/tome/platforms/bedrock-guardrails.json` (new)
- `~/tome/platforms/openai-moderation.json` (new)
- `~/tome/platforms/azure-content-safety.json` (new, cross-references Slice A microsoft-purview)
- `~/tome/platforms/presidio.json` (new, framework-not-deployment)
- `~/tome/platforms/lakera-guard.json` (appended `litellm_v1_vs_v2_delta` block; no second platform entry)
- `~/AI-LLM-Infrastructure-OSINT/data/platform-intel/cat33-lane-d-slice-d-cloud-deltas-2026-06-07.md` (this file)

## Discipline observed

- Names ARE the finding. No probes against AWS / OpenAI / Azure / Lakera production endpoints.
- Source code on GitHub via `gh api`, downloaded to `/tmp/litellm-d` for read-only inspection; no clone.
- No em-dashes.
- Lakera v2 evaluated against the existing Lane B Lakera tome entry; one platform entry, dual endpoint coverage, decision recorded inline.
- Slice A `microsoft-purview.json` not duplicated; Azure Content Safety written as the SIBLING product with explicit cross-reference.
- Framework-vs-deployment discipline applied to Presidio per Lane D summary precedent.
- Cloud-native wrapper analysis follows the same `litellm_wrapper_delta` schema across all three cloud targets so the comparison is auditable.

## Insight candidate (for Lane D consolidation)

**Candidate: cloud-native guardrails wrapped by LiteLLM are never fully transparent passthroughs.** Each wrapper adds at least one of (credential centralization, control-plane disclosure, policy ambiguity, wrapper-side processing, hardcoded behavior). The wrapped cloud API is unchanged; the operator's blast radius widens because the proxy is itself a CVE-rich target. Reporting "operator X uses Bedrock Guardrails" via LiteLLM-presence detection mis-characterizes the surface; the relevant surface is the LiteLLM proxy, not the cloud guardrail. This is the cloud-native analog of the Lane D framework-vs-deployment discipline: the cloud API is the framework, the LiteLLM proxy is the deployment, and the population that Shodan sees is the proxy population, not the cloud-guardrail-customer population.
