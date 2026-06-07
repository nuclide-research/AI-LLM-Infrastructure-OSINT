# Cat-33 Lane D Platoon Intel: SDK / Wrapper Guardrails (OSS-heavy)

_Generated 2026-06-07 as Phase 3B Lane D OSINT platoon return. Parent brief: `categories/33-ai-email-guardrails-deep-brief-2026-06-06.md`. Dispatch spec: `research-program/cat33-phase3b-three-lane-dispatch-2026-06-07.md`. Companion Lane B intel landed earlier same day in this directory._

## Scope

Lane D = library / wrapper guardrails. `lib.guard(message)` before the `send_email()` tool-call. Email is one tool-call among many. Most targets are OSS, so the threat surface is in operator DEPLOYMENTS, not vendor infra. Per the brief, the vendor JSON must distinguish FRAMEWORK (the OSS project) from DEPLOYMENT (a customer running it).

## Targets covered

| Target | Stage | Status | JSON written |
|---|---|---|---|
| LlamaFirewall (Meta, github.com/meta-llama/PurpleLlama, repo moved from facebookresearch) | OSS, arxiv 2505.03574 | covered | `~/tome/platforms/llamafirewall.json` |
| OpenGuardrails (github.com/openguardrails/openguardrails) | OSS, 356 stars | covered | `~/tome/platforms/openguardrails.json` |
| Invariant Gateway (github.com/invariantlabs-ai/invariant-gateway) | OSS Apache-2.0, 72 stars | covered | `~/tome/platforms/invariant-gateway.json` |
| LiteLLM policy mode (github.com/BerriAI/litellm) | OSS, 49.5k stars | DELTA ONLY -- pre-existing Cat-05 JSON | (existing) `~/tome/platforms/litellm.json` |
| Cascade (cascade.dev) | YC W2026 (claimed) | SKIPPED -- domain returns unrelated S3 page (verified 2026-06-07) | none |
| Galini (galini.ai) | YC F2024 (claimed) | SKIPPED -- parent brief line 286 reclassifies as consulting firm, not product | none |

Framework count covered: **4** (3 net-new + 1 delta).

## Per-target findings

### 1. LlamaFirewall (Meta)

- **Type:** Framework, no network port. Python import: `from llamafirewall import LlamaFirewall, Scanner, Trace`.
- **Repo move:** Brief lists `facebookresearch/PurpleLlama`; the canonical is now `meta-llama/PurpleLlama` (4209 stars, 735 forks, NOASSERTION license, last update 2026-06-07). Old URL redirects.
- **Components:** PromptGuard 2 (BERT injection classifier), AlignmentCheck (CoT audit), CodeShield (code static analysis), Regex/Custom scanners.
- **CVEs:** NVD keyword "llamafirewall" returns **0**. GitHub Security Advisories on PurpleLlama: **0 published**. Issues are dependency bumps and feature requests (most recent #233-#239 are Dependabot PRs against `LlamaFirewall/website/`, NOT vuln reports).
- **Per-brief direction:** "arxiv 2505.03574 exists; cite it and let the paper carry the threat model." Done. Paper carries layered defense framing; no implementation CVE backs the threat model yet.
- **Default-deployment artifacts:** examples/ shows wrapper-pattern only. No docker-compose. No `.env`. Operator surface = thin FastAPI wrappers that operators write themselves.
- **Dork-population-substitution risk:** **HIGH.** Any LlamaFirewall dork measures the operators who chose to ship it as a service. Library-mode users are invisible. The visible deployment population is a self-selected security-conscious subset that already invested in shipping wrapper infra. Inverse selection bias.

### 2. OpenGuardrails

- **Type:** Framework AND deployment. Ships full docker-compose stack with admin UI, Postgres, Redis, vLLM model server. 356 stars, 55 forks, "Zero Trust Firewall for AI Agents," last update 2026-06-05.
- **Default ports:** 54321 (Postgres host-mapped from container 5432), 58002 (vLLM Text-2510), 58003 (optional VL model), 58004 (bge-m3 embedding), 6379 (redis, internal), 80/443 (platform).
- **CVEs:** NVD: **0**. GH Advisories: **0**. Only 1 open issue (#29, Windows initPersonalDashboard ESM URL bug). Pre-CVE project; risk lives in default-cred replication, not disclosed bugs.
- **Default-credential surface (load-bearing):** `.env.example` ships:
  - `SUPER_ADMIN_PASSWORD=CHANGE-THIS-PASSWORD-IN-PRODUCTION`
  - `JWT_SECRET_KEY=your-secret-key-change-in-production`
  - `POSTGRES_PASSWORD=your_password`
  - `GUARDRAILS_MODEL_API_KEY=EMPTY` (intended for vLLM, but ambiguous if pointed at OpenAI)
  Operators copy `.env.example` to `.env` and forget to rotate. Three exploitable paths: super-admin login literal, JWT forgery, direct Postgres takeover via :54321 if reachable.
- **Network exposure default:** Postgres :54321 host-mapped to 0.0.0.0 by docker-compose. vLLM model APIs on 58002/58004 also bind broadly; designed for private VPC but often flat-deployed.
- **Dork-population-substitution risk:** **HIGH, multi-axis.** The brand dork `http.html:"OpenGuardrails"` selects operators who exposed the frontend. The port-54321 + supervisord dork selects operators who left compose defaults. Different subsets that overlap but are not the same; conclusions from one do not transfer to the other.

### 3. Invariant Gateway

- **Type:** Proxy-style guardrail. Sits between agent and LLM provider via `base_url` swap on the client. Apache-2.0, 72 stars, last update 2026-05-17.
- **Org context:** invariantlabs-ai also ships `invariant` (core lib, 424 stars), `explorer`, `invariant-sdk`, `mcp-injection-experiments` (195 stars, MCP tool poisoning research), `mcp-streamable-http` (129 stars). The org publishes the attacks AND ships the defenses. Self-aware threat model.
- **Default ports:** `8005:8000` on self-hosted (gateway/docker-compose.local.yml). Traefik routing on `/api/v1/gateway/` prefix when fronted.
- **Auth default:** Bearer `Invariant-Authorization` header when used via the SaaS Explorer. **Self-hosted gateway has NO BUILT-IN AUTH on port 8005** unless `INVARIANT_API_KEY` is set, AND `INVARIANT_API_KEY` is only required when `GUARDRAILS_FILE_PATH` is supplied. Without guardrails file, the self-hosted gateway is an unauthenticated forwarding proxy that traces every agent call.
- **Misconfig pattern:** operator runs `bash run.sh up` with no flags -> guardrails disabled, gateway is pass-through trace collector with no auth. The provider creds (OPENAI_API_KEY, ANTHROPIC_API_KEY) live in the gateway container env and route through every call.
- **CVEs:** NVD keyword "invariantlabs": **0**. GH Advisories on `invariant` or `invariant-gateway`: **0**.
- **Dork-population-substitution risk:** **MEDIUM-HIGH.** Two populations: SaaS users via explorer.invariantlabs.ai (cert-pivot only, no Shodan body match) and self-hosted operators on 8005. The self-hosted population self-selects for stricter data-residency requirements; conclusions about self-hosted operators do not generalize to SaaS users.

### 4. LiteLLM (Lane D delta, NOT a re-survey)

Cross-references Cat-05. Per brief: "do not re-survey Cat-05; just write the Lane D delta." Existing tome: `~/tome/platforms/litellm.json` (current).

- **Lane D delta:** Same proxy at port 4000, same `/health/liveliness` fingerprint, same `litellm_version` marker. What changes when used as a Lane D wrapper rather than an inference gateway is the `guardrails:` config block and the `/guardrails/*` endpoints. **Network fingerprint is identical.** Passive enumeration cannot distinguish the two modes.
- **The `guardrail_hooks/` directory IS the Lane D landscape map.** Each subdirectory is an integrated guardrail vendor. The full set as of 2026-06-07: aim, akto, aporia_ai, azure, bedrock_guardrails, block_code_execution, cato_networks, crowdstrike_aidr, custom_code, dynamoai, enkryptai, generic_guardrail_api, grayswan, guardrails_ai, hiddenlayer, ibm_guardrails, javelin, lakera_ai, lakera_ai_v2, lasso, litellm_content_filter, llm_as_a_judge, mcp_end_user_permission, mcp_jwt_signer, mcp_security, microsoft_purview, model_armor, noma, onyx, openai, pangea, panw_prisma_airs, pillar, presidio, prompt_security, promptguard, qohash, qualifire, rubrik, semantic_guard, tool_permission, tool_policy, unified_guardrail, vigil_guard, xecguard, zscaler_ai_guard. **This single directory enumerates the entire commercial Lane D vendor space in one place.** Survey leverage: enumerate which Lane D vendors are present on a corpus by reading LiteLLM `/guardrails/list` (active probe required).
- **CVEs (Lane-D-relevant):** 14 NVD hits + 8 GH Advisories on `BerriAI/litellm`. Lane-D-specific subset:
  - **GHSA-wxxx-gvqv-xp7p / CVE-2026-40217 (HIGH)** -- **Sandbox escape in custom-code guardrail.** Bytecode rewriting at `/guardrails/tests` endpoint. The guardrail USER is the attacker model. Affects through 2026-04-08. This is the canonical Lane D vulnerability: the policy hook IS the attack surface.
  - GHSA-4xpc-pv4p-pm3w / CVE-2026-49468 (critical, auth bypass via Host header).
  - GHSA-r75f-5x8p-qvmc / CVE-2026-42208 (critical, SQLi in proxy key verification, CISA-KEV).
  - GHSA-xqmj-j6mv-4862 / CVE-2026-42203 (high, SSTI in `/prompts/test`).
  - GHSA-jjhc-v7c2-5hh6 / CVE-2026-35030 (critical, OIDC userinfo cache key collision).
  - GHSA-53mr-6c8q-9789 / CVE-2026-35029 (high, privesc via unrestricted proxy config endpoint).
  - GHSA-v4p8-mg3p-g94g / CVE-2026-42271 (high, authenticated command execution via MCP stdio test endpoints).
  - GHSA-69x8-hrgq-fjj8 (high, password hash exposure + pass-the-hash bypass).
  - Plus older: CVE-2025-45809 (SQLi), CVE-2025-11203 (info disclosure via health API key), CVE-2024-4888 (arbitrary file deletion), CVE-2024-10188 (DoS), CVE-2026-47101 / CVE-2026-47102 (key/role escalation).
- **Default branch oddity:** `default_branch=litellm_internal_staging` per API (not `main`). Operators pulling from `main` are running stable; `litellm_internal_staging` is the active dev branch. Worth noting for any fingerprint anchored on branch state.
- **Dork-population-substitution risk:** **HIGH.** The Cat-05 Shodan dork measures all LiteLLM proxy operators. The Lane D subpopulation (operators using LiteLLM as a guardrail wrapper) is invisible to passive enumeration. Reading Cat-05 conclusions onto Lane D mis-characterizes the population.

## CVE summary per framework

| Framework | NVD hits | GH Advisories | Lane D-relevant |
|---|---|---|---|
| LlamaFirewall | 0 | 0 | None |
| OpenGuardrails | 0 | 0 | None (default-creds risk is policy, not CVE) |
| Invariant Gateway | 0 | 0 | None (org publishes attacks on others) |
| LiteLLM (Lane D mode) | 14 | 8+ | CVE-2026-40217 directly Lane-D (sandbox escape in custom-code guardrail) |

## Dork-population-substitution risk per framework

| Framework | Risk level | Mechanism |
|---|---|---|
| LlamaFirewall | HIGH | Dork measures wrapper-mode operators; library-mode users invisible |
| OpenGuardrails | HIGH (multi-axis) | Brand dork vs port-54321 dork select different subsets |
| Invariant Gateway | MEDIUM-HIGH | Self-hosted vs SaaS bifurcation; self-hosted skews data-residency-strict |
| LiteLLM (Lane D) | HIGH | Cat-05 dork measures the gateway population; Lane D mode invisible to passive |

**Cross-cutting Insight candidate:** for an OSS framework category, the population that a brand-string dork selects is structurally smaller than and qualitatively different from the framework's actual user population, biased by deployment-style self-selection (publicly-shipped-as-service vs in-process library). When a dork count is reported for an OSS framework, the framing must say "X operators chose to publicly expose the framework," NOT "X operators use the framework."

## herald scaffolding

Per brief: "herald scaffolding ONLY if the project exposes a network endpoint by default (most won't - they're libraries)."

| Framework | Exposes network by default | Herald scaffolding warranted |
|---|---|---|
| LlamaFirewall | No (Python import) | No |
| OpenGuardrails | Yes (docker-compose ships admin UI + Postgres + vLLM) | Yes (deferred to follow-on; fingerprints recorded in JSON) |
| Invariant Gateway | Yes (port 8005 self-hosted) | Yes (deferred; fingerprints recorded) |
| LiteLLM | Yes (port 4000) | Already herald-scaffolded in Cat-05 |

Herald scaffolding for OpenGuardrails and Invariant Gateway is queued; the fingerprint markers in their tome JSONs are sufficient to build the scaffold when herald is next opened.

## Files written

- `~/tome/platforms/llamafirewall.json` (new)
- `~/tome/platforms/openguardrails.json` (new)
- `~/tome/platforms/invariant-gateway.json` (new)
- `~/AI-LLM-Infrastructure-OSINT/shodan/queries/33-ai-email-guardrails.md` (appended Lane D section with 3 tiers of dorks per target)
- `~/AI-LLM-Infrastructure-OSINT/data/platform-intel/cat33-lane-d-vendors-2026-06-07.md` (this file)

## Stop-condition check

Per brief: "If a platoon's vendor count for its lane drops below 3 after deduplication and verification, the lane is empty enough to short-circuit." Lane D vendor count after dedup: **4** (LlamaFirewall, OpenGuardrails, Invariant Gateway, LiteLLM-Lane-D-mode). Above threshold. Lane D is not empty -- the LiteLLM `guardrail_hooks/` directory alone enumerates 40+ commercial Lane D integrations that could each be candidate platforms for follow-on surveys.

## Follow-on candidates (out of scope for this platoon)

The LiteLLM `guardrail_hooks/` directory is the canonical Lane D vendor catalog. Per-vendor Cat-33 Lane D surveys could be dispatched against: Hiddenlayer, Pangea AI Guard, Pillar Security, Aporia, Aim Security (the EchoLeak research house), Lasso Security, Javelin Sentinel, Noma, Cato AI, CrowdStrike AIDR, Microsoft Purview / Model Armor, Zscaler AI Guard, Qualifire, GraySwan, EnkryptAI, DynamoAI, Akto AI, Onyx, Rubrik, Qohash, Xecguard, ibm_guardrails (watsonx.governance). Most are commercial SaaS, fingerprint-only via cert pivot.

## Brief discipline observed

- Names ARE the finding. No record reads performed. No inference calls invoked.
- No em-dashes.
- Cascade and Galini skipped per brief verification; explicit one-line reason for each.
- LiteLLM treated as a delta, not a re-survey, per Cat-05 cross-reference rule.
- LlamaFirewall carried by arxiv 2505.03574, not by independent threat-model derivation.
- Dork-population-substitution risk noted per framework, per brief discipline note.
- FRAMEWORK vs DEPLOYMENT distinction encoded in tome JSON `entry_type` field per platform.
