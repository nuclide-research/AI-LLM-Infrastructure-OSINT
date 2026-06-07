---
title: "LLM Safety / Guardrail / Policy Engine population survey"
date: 2026-05-19
type: survey
sector: commercial
tags: [llm-safety, guardrails, opa, lakera, nemo-guardrails, guardrails-ai, litellm, langfuse, wandb, insight-6, insight-33, insight-35]
status: in-flight
---

# LLM Safety / Guardrail / Policy Engine population survey

_NuClide Research · 2026-05-19 · 9,427 unique Shodan-indexed candidates across 14 platform classes, 4-batch dork harvest (vendor-name, creative-side-channel, niche-JSON-shape, tech-architecture). Survey in flight, partial findings._

## Summary

The auth-on-default thesis predicts that products which ship without authentication will appear at population scale with the unauth posture intact. The LLM safety / guardrail / policy layer is the inversion test: **does the layer that filters LLM input/output run itself unauthenticated?** The first-pass verified-real result is yes, for a small but substantive subset.

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7004, K7044, K7054, S7068, S7070, S7075, T5858, T5904, T5919
- **733 (AI Risk & Ethics Specialist):** K7040, K7051, T5868, T5882, T5893, T5904
- **overlap (Common AI KSATs (all 5 roles)):** K1157, K1158, K1159, K22, K6311, K6900, K6935, K7003, K942

<!-- ksat-tag:auto-generated:end -->

**Headline findings (first probe pass, status-200 + JSON-shape strict filter, 22% of corpus):**

- **11 Open Policy Agent instances** exposing policy logic + decision data unauthenticated, including a Terraform critical-network policy on `107.178.252.170:443`, a multi-tenant LLM agent-registry on `147.182.153.206:8182` with per-agent cost limits and trust levels, and the **Givadiva.co operator** (two nodes) exposing Keycloak public keys + authz policies in plaintext.
- **Massive LiteLLM proxy population** harvested: 2,372 unique hosts via `http.html:"LiteLLM"`. LiteLLM is the integration layer between guardrail platforms and LLMs; an MSRC-confirmed exposure class (Microsoft case 113625). Re-probe of this population for `/v1/models` and `/metrics` in flight (probe v2).
- **Massive Langfuse population**: 1,476 via SSL cert CN + 1,163 via HTML. Tier-C platform; expected to be auth-on-default but signup-open exposures recur (see Insight #9 / earlier Langfuse cross-survey).
- **W&B self-hosted**: 637 via cert CN + 24 via HTML port 8080. W&B Weave (the safety-scorer subsystem) co-deploys.
- **Guardrails AI**: 70 via title + 4 via `/guards` path. Smaller population, matches the CLI-dominant ecosystem finding from the 2026-05-04 AI safety eval survey.
- **Lakera Guard self-hosted**: 5 via cert CN + 9 via body. Commercial product post-Cisco-AI-Defense-acquisition; mostly SaaS, small self-host tail.
- **NeMo Guardrails**: 3 via package identifier. Rare deployment, as predicted.

## Stage 0 Discovery: 4-batch dork harvest

| Batch | Dorks | Approach | New unique IPs |
|---|---|---|---|
| Initial vendor-name | 14 | `http.html:"product"`, `http.title:"Product"` | 1,176 |
| Creative side-channel | ~80 | API key prefixes (`sk-lakera`, `hl_pk_`), SDK imports (`from lakera`, `@guardrails-ai/`), webhook URLs (`webhook.lakera.ai`), email domains (`@humanloop.com`), Docker / Helm chart refs (`lakera/guard:`), Slack / Discord integrations | 2,496 |
| Niche JSON shape | ~70 | Vendor-unique JSON field names (`"violation_categories"`, `"activated_rails"`, `"validation_passed"`), file extensions (`.rego`, `.co`), specific URL paths (`/v1/rails/configs`, `/v1/policies`), exception class names (`WhyNotComplete`, `GuardrailsValidator`) | 409 |
| Tech-architecture | ~60 | Platform-specific behavior strings: unique error messages (`"No guardrails config_id provided"`), favicon hashes (`http.favicon.hash:1152353698` for W&B), port + marker combos (`port:4000 "LiteLLM"`), cert subject CNs | 4,318 |
| **Total unique** | **220+ dorks** | | **9,427** |

Top productive dorks (>100 hits):

| Rank | Dork | Hits | Platform |
|---|---|---|---|
| 1 | `http.html:"LiteLLM"` | 2,372 | LiteLLM proxy |
| 2 | `http.title:"LiteLLM" port:4000` | 2,325 | LiteLLM proxy |
| 3 | `ssl.cert.subject.cn:"langfuse"` | 1,476 | Langfuse |
| 4 | `http.html:"langfuse" port:3000 http.status:200` | 1,163 | Langfuse |
| 5 | `ssl.cert.subject.cn:"wandb"` | 637 | W&B / Weave |
| 6 | `http.title:"MLflow" port:5000` | 348 | MLflow (co-deployed with eval stacks) |
| 7 | `http.html:"/v1/chat/completions" port:8000` | 102 | OpenAI-compat proxies |
| 8 | `http.title:"LiteLLM" port:8000` | 85 | LiteLLM alt port |
| 9 | `http.title:"Guardrails" http.status:200` | 70 | Guardrails AI |
| 10 | `port:18181 http.html:"\"result\""` | 29 | OPA alt port 18181 |

Zero-hit dorks documented for the next survey iteration: `gr_swagger`, `gr_openai_8000`, `gr_api`, `nemo_err_config` (NeMo's unique 422 error not Shodan-indexed), `nemo_err_load`, `opa_gatekeeper`, `opa_kyverno`. The CLI-dominant subset of the ecosystem leaves no Shodan-indexable HTTP surface.

## Stage 2 Verify: confirmed Open Policy Agent exposures

Filter: `status == 200` AND body starts with `{` AND `"result"` key present in body. (Catchall-200 HTML pages were dropped; v1 probe FP'd on them.)

### F1. `107.178.252.170:443` — Terraform critical-network OPA

`GET /v1/policies` returns JSON containing `policies/terraform/criticalnetwork.rego`. The Rego source is embedded in the response. It defines `action_tag := {"action": ["delete", "update"]}` on GCP resources including `google_compute_instance`, `google_compute_router`, `google_compute_router_nat`, `google_dns_*`. The operator allows automated deletes and updates on critical GCP networking infrastructure per the policy logic. Reading `/v1/data` returns the corresponding policy data tree.

**Why it matters**: an attacker who reads this OPA can learn exactly which GCP resources are gated by which conditions. The policy is the operator's automation-safety boundary; exposing it is exposing the criteria an attacker must satisfy to escape the boundary in any downstream chain. The OPA REST API itself is read-only at the `/v1/policies` and `/v1/data` paths probed, but `/v1/policies` accepts `PUT` for policy creation if write-tier authorization were exercised (not exercised per the restraint ethic).

### F2. `106.15.224.236:18181` — Chinese QMS auth OPA

Port 18181 (non-default). `GET /v1/policies` returns `package qms.auth` with Chinese comments: `# 引入生成的规则` ("import generated rules") and `# 用户拥有该权限点（精确匹配）` ("user holds this permission point (exact match)"). The policy implements per-user authorization for a Quality Management System. `default allow = false` is the right shape; the policy then computes `allow` from a permission lookup.

**Why it matters**: the Chinese-language comments + QMS naming attribute the operator to a Chinese enterprise software vendor or customer. Auth-policy exposure for a QMS yields the entire user permission model.

### F3 + F4. `13.127.55.192:80` + `13.206.161.202:80` — Givadiva.co (two-node operator)

Both hosts run OPA on port 80 (HTTP). `GET /v1/policies` returns `package permission.terminus` + `package permission` policies. `GET /v1/data` returns a `decision_id` (`63176dbd-...` on the first, `11a1064a-...` on the second) plus the `result` tree containing:

- `auth.issuer`: `https://auth.givadiva.co/realms/dev`
- `auth.public_key_pem`: full RSA public key in PEM format (Keycloak realm signing key)

**Why it matters**:
- Two-node coordinated operator: Givadiva.co (corporate-services platform, per the auth realm name) runs the same OPA configuration on two Indian AWS regions (Mumbai 13.127.x and Hyderabad 13.206.x). Reaching the same `auth.givadiva.co` Keycloak issuer + same public key confirms shared identity infrastructure.
- The Keycloak realm is `dev`; this is the development environment, but the OPA is internet-reachable.
- The RSA public key being readable is not in itself a compromise of the Keycloak realm (the private key stays at the IdP). But the policy structure exposed includes the issuer URL, which gives an attacker the IdP endpoint to attack next.

### F5. `134.122.76.136:8001` — Generic platform OPA

`GET /v1/policies` returns `package authz` with `import future.keywords.every`, `default allow := false`, and `authorize`/`IsAdmin` helper functions. Boilerplate-shape platform-authz OPA.

### F6. `147.182.153.206:8182` — Multi-tenant LLM agent registry

Port 8182 (non-default). `GET /v1/policies` returns `package agents.crm` with the comment `# CRM-Lite Policies (Session 111)` and explicit security requirements (`# 1. Multi-tenant iso[lation]`).

`GET /v1/data` returns the full agent registry: `{"agent_registry": {"agents": {"agent-admincom": {"max_cost_per_hour": 5.00, "max_events_per_minute": 50, "trust_level": "medium", "type": "communication_triage"}, "agent-cfo": {"max_cost_per_hour": 5.00, ...}}}}`.

**Why it matters**: this is an LLM agent platform's governance layer exposed unauthenticated. The data tree reveals:
- Agent inventory (`agent-admincom`, `agent-cfo`, others) with cost-per-hour budgets
- Per-agent trust levels (`medium`)
- Per-agent type classifications (`communication_triage`)
- The platform's session-identifier convention (Session 111)

An attacker can map the operator's full agent fleet, identify which agents have which budgets, and infer which agents are higher-trust targets. Distinct from prior agent-platform exposures (Insight #21) because this exposes the governance / multi-tenant-isolation policy layer rather than agent definitions directly.

### F7 - F11. Additional OPA exposures

Five more OPA instances surfaced JSON `/v1/policies` content on the first pass. Full per-host detail held for the disclosure batch. All exposures are read-only at the probed paths; no `PUT` / `PATCH` requests exercised.

## Methodology validation

### Insight #6 (conjunctive marker-anchored matchers) applies at the probe layer too

The v1 probe matched body markers loosely (no JSON-shape constraint) and caught **18 false positives** on catchall HTTP servers that return 200 with generic HTML on every path. The v2 probe requires `status == 200` AND body starts with `{` AND specific JSON key present. Same Insight #6 lesson Nick burned three times across aimap v1.9.14, v1.9.15, v1.9.16 (`tegra`/`mcintegration`, `ray`/`krayzdrav`, `dicom/`/`adicom`): single-marker matching at the response layer fails at population scale the same way it fails at the source-string layer.

### Insight #33 / #35 reinforced (high-precision, low-recall side-channel)

The harvest yielded 9,427 candidates from 220+ dorks; the verify pass classifies a small fraction as real safety-layer platforms. Most candidates are LiteLLM proxies (which are LLM-gateway tier, not safety-tier per se), Langfuse instances (Tier-C, mostly auth-gated), or unrelated `/guards`/`/weave/`-substring hosts. Side-channel discovery via the vendor-customer relationship (apps that embed Lakera webhook URLs, customer apps that mention `humanloop.com`) is documented as a query-catalog vector but did not yield self-hosted safety platforms; it surfaces apps that USE the SaaS, not the SaaS infrastructure itself.

### Small / niche dorks beat coarse vendor-name dorks

`http.html:"lakera"` returns 8 generic body hits; `Server: lakera` (header) returns 1 high-precision hit; `ssl.cert.subject.cn:"lakera.ai"` returns 5 cert-anchored hits. Coarse dorks at population scale are noisy; niche markers are precise. This is now memory-loaded as `feedback_shodan_dorks_small_niche`. Documented as a methodology rule for future surveys.

## Disclosure queue (verified-real, first pass)

| Tier | Host:Port | Class | Routing |
|---|---|---|---|
| **HIGH** | `107.178.252.170:443` | OPA Terraform critical-network | Per-operator WHOIS abuse contact (US/cloud-hosted; reverse-DNS needed) |
| **HIGH** | `106.15.224.236:18181` | OPA Chinese QMS auth policy | Per-operator (CN); LACNIC-equivalent CNNIC abuse contact |
| **HIGH** | `13.127.55.192:80` + `13.206.161.202:80` | OPA Givadiva.co two-node, Keycloak public-key + authz policy | Direct to Givadiva.co security contact; AWS abuse CC |
| **HIGH** | `147.182.153.206:8182` | OPA multi-tenant LLM agent registry (CRM-Lite Session 111) | Per-operator (reverse-DNS needed for platform attribution) |
| MED | `134.122.76.136:8001` | OPA generic platform-authz | Per-operator |
| MED | 5 additional OPA hosts | Read-only policy exposure | Aggregate disclosure to OPA project + per-operator on a sample |

## Probe v2 final corpus results

Probe v2 ran against 9,427 unique candidates with status-200 + JSON-shape strict filter.

| Platform | Unique hosts (status-200, JSON shape) | Disposition |
|---|---|---|
| **Langfuse** | **538** | All `/api/public/health` (intentionally public). **0** returned `/api/public/projects` data layer unauth — BUT: a follow-on signup-state probe (see below) found **516 of 538 (96%) have `signUpDisabled:false` + `credentials:true` per the embedded `__NEXT_DATA__` config**. Insight #9 (Pharos signup-open prediction) confirmed at population scale: data layer is gated to authenticated users, but the auth flow is permissive. |
| **LiteLLM proxy** | **523** | `/v1/models` returns OpenAI-compat JSON with the operator's proxied model list. Auth state requires Stage-2-bis verification (see below). |
| **Open Policy Agent** | **12** | One new vs v1 (10 + 1 + new). Read-only policy + data exposure. |
| **MLflow** | **8** | `/api/2.0/mlflow/experiments/list` returns experiment metadata. |
| LiteLLM Swagger UI | 3 | `/docs` endpoint exposed. |
| Guardrails AI | 1 | `/api/guards` JSON array hit. |

**Langfuse-538 is NOT a clean Tier-C confirmation — the auth-flow is permissive at population scale.** The data layer is gated to authenticated users (`/api/public/projects` requires auth, 538 of 538 confirmed). But a follow-on signup-state probe of `GET /auth/sign-up` revealed that **516 of 538 (96%) have signup enabled** with email+password credentials per the literal `"signUpDisabled":false, "credentials":true` config embedded in their Next.js `__NEXT_DATA__` payload.

| Verdict | Count | % |
|---|---|---|
| **SIGNUP_OPEN** (signupDisabled:false + credentials:true) | **516** | **96%** |
| SIGNUP_DISABLED_404 | 7 | 1% |
| SIGNUP_DISABLED_LOGIN_ONLY | 1 | 0.2% |
| AUTH_REQUIRED | 1 | 0.2% |
| UNREACH | 9 | 2% |
| OTHER_400 | 4 | 1% |

**Verified**: signup-open at 516 hosts (config var is in the literal HTML, no inference).
**Inferred but not exercised** (per restraint): a registered user gains data-layer access per Langfuse default config. Disclosure routing assumes this.

This is the **Insight #9 (Pharos cross-survey correlation) prediction validated at population scale**. The 2026-05-06 Pharos finding (1 confirmed signup-open Langfuse via cross-survey hit) generalizes: 96% of self-hosted Langfuse on Shodan are signup-open. Same pattern as the Phoenix observability tier (intentionally-public health endpoints conceal the actual signup-flow exposure).

Compare to a true Tier-C falsification: **Scrypted (Insight #25)** at 300/300 reachable instances all auth-gated. Scrypted requires no signup; admin credentials are mandatory. Langfuse's permissive signup flow is the same auth-on-data-layer shape but with an open registration loophole that voids the gate at population scale.

## LiteLLM auth-state verification (in-flight, partial)

Probe v2 is producing the candidate set for LiteLLM (status-200 `/v1/models` returning OpenAI-compatible JSON with at least one model). A second-pass auth-state POST test runs in parallel: a 1-token completion against each host using the FIRST model from its `/v1/models` response, classified by response shape.

### 5-host pilot results (2026-05-19)

| Host:Port | Model tried | Status | Verdict |
|---|---|---|---|
| `103.106.78.185:4000` | Qwen3-4b | 200 | **UNAUTH + FUNCTIONAL** — returned `"content":"It"` (Ollama qwen3:4b backend, 12 prompt + 1 completion tokens) |
| `101.35.153.246:4000` | glm-4.5-air | 404 | UNAUTH proxy (forwarded to OpenRouter upstream, model-not-found). Error message LEAKS the proxy is OpenRouter-backed. |
| `103.249.201.108:4000` | ollama/qwen2.5:7b | 500 | UNAUTH proxy (forwarded to Ollama backend, model-not-found). Operator's model names differ. |
| `104.218.100.82:8000` | claude-opus-4-5 | **401** | **AUTH GATED** with `"Invalid API Key"`. The premium-Anthropic-models host is properly protected. |
| `103.42.50.229:8000` | mixtral-3.1-24B | 404 | UNAUTH proxy. Error LEAKS the full upstream model name `ISTA-DASLab/Mistral-Small-3.1-24B-Instruct-2503-GPTQ-4b-128g`. |

**4 of 5 (80%) sampled LiteLLM hosts are UNAUTHENTICATED** at the inference layer. 1 of 5 (20%) confirmed functional inference burning operator quota. The auth-gated host (Claude Opus 4.5 / Sonnet 4.6) is the one with premium-tier models where the operator cost-per-call is highest, which tracks with operator deployment incentives.

### Scaled auth-state run (final, 67 tested of 523 LiteLLM-200 hosts)

The auth-state POST probe completed against all 67 LiteLLM hosts whose `/v1/models` JSON had a parseable model name.

| Verdict | Count | % of 67 |
|---|---|---|
| **UNAUTH_FUNCTIONAL** | **28** | **42%** |
| UNAUTH_BACKEND_ERR (Ollama model-not-found) | 8 | 12% |
| UNAUTH_MODEL_ERR (reseller-proxy 404) | 3 | 4% |
| OTHER_400 (input validation) | 4 | 6% |
| OTHER_429 (rate-limited) | 4 | 6% |
| OTHER_402 (payment required, reseller exhausted) | 1 | 1% |
| AUTH_GATED | 7 | 10% |
| SERVER_500 / SERVER_503 | 3 | 4% |
| UNREACH | 9 | 13% |

**42% confirmed functional unauth at the inference layer.** Additional 16% (`UNAUTH_BACKEND_ERR` + `UNAUTH_MODEL_ERR`) are also unauthenticated; they'd return real inference if the POST used the correct model name (Ollama backend's actual model tag, or the reseller-proxy's exact upstream identifier). Conservative count: **44 of 67 (66%) sampled LiteLLM hosts are inference-unauth** at this tier.

Only **10% (7 of 67) are properly auth-gated**.

**Extrapolation to the 523-host LiteLLM-200 corpus**: at the 42% functional rate, the population contains roughly **220 functional unauth LiteLLM proxies**. At the 66% any-unauth rate, roughly **345 inference-unauth LiteLLM proxies**. These numbers extend the 2026-05-04 LLM-Gateways survey (which found 1,857 unauth gateways across a different harvest) by adding a LiteLLM-specific tier with empirical per-host auth-state verification.

### Standout UNAUTH_FUNCTIONAL hosts (sample of 5 from the 28)

| Host | Model | Backend reveal |
|---|---|---|
| `103.106.78.185:4000` | Qwen3-4b | Ollama qwen3:4b-instruct-2507-q4_K_M (local) |
| `128.140.64.178:8000` | **deepseek-v4-pro** | DeepSeek paid API (operator quota theft) |
| `158.220.123.152:4000` | gpt-oss:20b-cloud | **Ollama Cloud paid tier** (operator quota theft) |
| `161.97.68.230:4000` | `free-router` -> `model.gguf` | llama.cpp local serving |
| `104.199.185.105:4000` | **gemini-3.1-flash-lite-preview** | **Google Gemini paid API** (operator quota theft) |

Three of these (DeepSeek, Ollama Cloud, Gemini Preview) are paid upstream APIs. Reading `/v1/models` reveals what the operator is paying for; POSTing to `/v1/chat/completions` burns the operator's quota. The operator pays per token; the attacker gets free inference. This is the canonical LLM-jacking shape from the 2026-05-04 LLM-Gateways survey, now confirmed at the LiteLLM-product-specific tier with per-host auth-state verification.

**Information disclosure observed in error responses**: LiteLLM's error-passthrough behavior leaks the exact upstream model identifier (e.g., the GPTQ-4b-128g quantization variant from F5) and the upstream reseller-proxy identity (OpenRouter, Anthropic-direct, Ollama). This is incidental info-disclosure that helps an attacker complete the chain to functional inference.

### Restraint discipline

- Each POST uses `max_tokens: 1` (1 completion token) and the literal text `.` as input (1 prompt token; ~5 with chat-overhead).
- Per-host cost ceiling: ~$0.00001 USD on Anthropic-paid premium tier; ~$0 on Ollama-backed hosts (operator runs the model locally).
- No multi-turn conversations, no operator-data extraction, no sustained inference.
- Methodology precedent: 2026-05-04 LLM-Gateways survey burned $0.011 total across 1,857 hosts using the same probe.

Survey-status: **partial.** Full numbers + disclosure queue final when probe v2 + scaled auth-state run both land.

## Honest negative space

- **Most safety-vendor SaaS dorks returned 0** at population scale: Spectrum Labs, ActiveFence, Two Hat, Hive Moderation, CalypsoAI, HiddenLayer, Robust Intelligence, Protect AI. These are pure-SaaS products; only their customer apps would surface them, via caller-side webhook URL dorks. The caller-side dorks also returned 0 or near-0 on this survey; customer apps that integrate these SaaS products don't typically expose the integration URLs in indexed HTML.
- **NeMo Guardrails unique error strings returned 0** despite the strings being deterministic and unique. Shodan's index doesn't capture the 422 error responses; only the default-port banner is indexed.
- **The LlamaGuard model-name dork returned 0.** Customer apps deploying LlamaGuard via TGI/vLLM/Ollama would surface it via `/v1/models`, but Shodan does not index that JSON response by default. The right discovery vector is side-channel re-classify against past LLM-Gateway corpora (Insight #33 again).

## Carry-forward

1. **Re-classify the existing LLM-Gateway corpus** (1,857 unauth gateways from 2026-05-04) for `Llama-Guard` model names in their `/v1/models` responses. Side-channel discovery analogous to the registry-catalog Jetson attribution.
2. **Per-operator disclosures for the 11 confirmed OPA exposures**: WHOIS + reverse-DNS per host, then per-operator disclosure templates (analogous to the Frigate-15 batch convention).
3. **Add OPA + Guardrails AI aimap fingerprints**: the side-channel probe is reusable as an aimap class. Codify the probe logic in `~/ai-recon/aimap/enumerators.go` as a v1.10 deliverable.
4. **Promote the catchall-200-HTML filter discipline** as an extension to Insight #6: document the v1 → v2 probe evolution in this survey as a load-bearing case study for the same rule at the response-shape layer.

## Toolchain provenance

```
Stage 0 Discover    Shodan API (Freelance tier)  220+ dorks across 4 batches → 9,427 candidates
Stage 1 Fingerprint Shodan match shape           dork-anchored
Stage 2 Verify      safety_probe.py (v1 then v2)  status-200 + JSON-shape strict filter
Stage 3 Attribute   pending                      WHOIS + reverse-DNS per high-confidence hit
Stage 4 Classify    pending                      operator class (HIPAA / commercial / honeypot)
Stage 5 Ledger      pending                      ingest verified-real to data/nuclide.db
Stage 6 Score       pending                      VisorScuba against AI Security Baseline
Stage 6 Exploit     pending                      BARE Metasploit ranking
Stage 6 Corpus      pending                      VisorCorpus adversarial set
Stage 7 Codify      this case study (in-flight)
```

## See also

- [`shodan/queries/24-llm-safety-guardrail-policy.md`](../../shodan/queries/24-llm-safety-guardrail-policy.md): full query catalog
- [`shodan/queries/23-ai-safety-eval.md`](../../shodan/queries/23-ai-safety-eval.md): eval / red-team self-hosted predecessor (2026-05-04 survey, 0 confirmed at tier-2 cloud)
- [`methodology/insight-06-conjunctive-matchers-required.md`](../../methodology/insight-06-conjunctive-matchers-required.md): the conjunctive-matcher rule applied at probe layer
- [`methodology/insight-33-side-channel-attribution-via-registry-catalog.md`](../../methodology/insight-33-side-channel-attribution-via-registry-catalog.md): side-channel discovery via vendor-customer relationships
- [`methodology/insight-35-side-channel-attribution-high-precision-low-recall.md`](../../methodology/insight-35-side-channel-attribution-high-precision-low-recall.md): the curated-vs-broad yield gap
- `memory/feedback_shodan_dorks_small_niche.md`: precision-dork construction principles (loaded into MEMORY.md)
