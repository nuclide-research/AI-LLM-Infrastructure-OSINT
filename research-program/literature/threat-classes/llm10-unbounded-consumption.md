# LLM10:2025 — Unbounded Consumption

**OWASP rank 2025:** #10 (replaces LLM04:2023 Model Denial of Service)
**OWASP rank 2023:** LLM04 Model Denial of Service

The 2025 revision broadens the scope from traditional DoS (resource exhaustion) to include **cost-based attacks** — also called "Denial of Wallet." This is the class most directly demonstrated by NuClide's 2026-06-06 LiteLLM findings.

## Description

An attacker consumes the operator's LLM resources without authorization:

1. **Traditional DoS** — flood requests until the system is unresponsive
2. **Cost-based attacks ("Denial of Wallet")** — make many legitimate-looking requests against a metered API; the operator pays per token
3. **Resource exhaustion via legitimate use** — large context windows, expensive models, retrieval over huge corpora
4. **Recursive prompt attacks** — prompts that induce extremely long generations
5. **Embedding flood** — repeated embedding calls against expensive models

The cost-based subcategory is the **most economically significant new threat class** for AI/LLM infrastructure: at frontier-model prices (Claude opus-4-7 at ~$15/M input tokens, GPT-5.4 at ~$20/M, etc.), a single open LLM proxy can cost the operator thousands of dollars per day under sustained abuse.

## Academic citations

The cs* corpora cover related ML-side resource attacks:

- **Membership inference + extraction-via-API** (CS 562, CS 598) — relevant to "abuse the API to extract value"
- **Adversarial inputs that induce expensive computation** — earlier work on adversarial latency attacks against ML inference (no direct paper in cs* corpora)

LLM10 is more applied-security than ML-theory; the canonical literature is in production-engineering and SRE work (Anthropic's, OpenAI's, and Microsoft's published abuse-prevention frameworks; the "Denial of Wallet" term originates in cloud-security work, e.g. Khan & Parsa 2023).

## Current survey instances

**LLM10 is the canonical class for NuClide's LiteLLM survey findings:**

- **LiteLLM 18 CRIT findings** (`surveys/2026-06-06-litellm.md`):
  - F-001: `23.238.9.142:4000` Anthropic API direct (Claude Sonnet 4.6 + Haiku 4.5) — any internet user can issue Claude completions billed to the operator's Anthropic key
  - F-002: `85.214.93.104:4000` AWS Bedrock EU (Claude Opus 4.7) — frontier model access via open proxy
  - F-003: `23.100.4.60:4000` Azure OpenAI (GPT-5.4)
  - F-007: `adb-4870463909224736.16.azuredatabricks.net` Databricks AI Gateway proxying Anthropic
  - F-012: Moonshot AI kimi-k2.5 (first non-Western frontier model finding)
  - Plus Vertex AI Gemini 2.5 Pro, Azure GPT-5.2, multiple additional providers across 18 instances

- **Open WebUI Ollama Connect cloud proxy** (`143.47.38.176:3000`) — `deepseek-v4-pro:cloud` model relays through the operator's DeepSeek subscription. Same class, different provider.

- **Flowise open chatflows** (`surveys/2026-06-06-flowise.md`) — 578 instances expose the prediction API. Each prediction call invokes the chatflow's configured LLM, billed to the operator's account.

**The 18 LiteLLM findings represent the highest-economic-impact class in the day's surveys.** At conservative estimates (10 concurrent abusers × $10/hour sustained), each open LiteLLM proxy represents ~$100/hour of operator cost exposure.

## Why the 2025 rename matters

OWASP's 2023 LLM04 was named "Model Denial of Service" — focused on availability. The 2025 rename to "Unbounded Consumption" explicitly recognizes that the **economic dimension** is often more important than the availability dimension. A successful attack might not bring the service down; it might just cost the operator $50,000 quietly before they notice.

NuClide's 18 LiteLLM CRIT findings empirically validate this rename. None of these instances are necessarily failing under load — they're quietly burning the operator's API budget.

## Defensive controls

- API key authentication (LiteLLM `master_key` configured; Phoenix `PHOENIX_ENABLE_AUTH=true`; Ollama `OLLAMA_ORIGINS` restricted)
- Per-user / per-API-key rate limits
- Budget caps with hard cutoffs (LiteLLM supports `max_budget` per key)
- Anomaly detection on token-throughput (sustained high consumption from a single IP)
- Egress-cost monitoring (the operator's Anthropic/Azure/Vertex bill is the canary)

## Related NICE roles

- **541 Vulnerability Assessment Analyst** — discovers the open proxies
- **804 IT Investment Portfolio Manager** — financially impacted role; relevant for cost-attack severity scoring
- **K0126 KSA: Knowledge of Supply Chain Risk Management Practices (NIST SP 800-161)** — LLM API access is a supply-chain link
- **K0202 KSA: Knowledge of application firewall concepts** — rate-limiting + budget-cap implementation

## Insight #76 connection

Less directly tied than other classes. The LiteLLM 0.81% rate is much lower than Langfuse/RAGFlow/Phoenix because LiteLLM's `LITELLM_MASTER_KEY` defaults to required in newer versions — partial counter-evidence to the broad #76 cohort hypothesis. The 18 CRIT findings come from operators who explicitly removed the master key, not from cohort-default behavior.

This is a useful **nuance** for Insight #76: not every new-gen OSS AI/LLM platform ships auth-permissive. The cohort hypothesis applies to platforms where the auth-permissive default is the upstream maintainer's choice; LiteLLM has chosen auth-required default, and the population reflects that.
