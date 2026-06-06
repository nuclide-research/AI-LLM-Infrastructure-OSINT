# OWASP Top 10 for Large Language Model Applications (2025)

The current canonical taxonomy of LLM application security risks. Every NuClide AI/LLM survey finding is mapped to one or more of these categories.

**Source:** OWASP LLM AI Security & Governance Top 10 (2025 update).
**Background:** "AI-Native LLM Security" (Packt, December 2025) Appendix A documents the 2023 → 2025 evolution.

## The 2025 list

| Rank | ID | Title | 2023 position | Change |
|---|---|---|---|---|
| 1 | LLM01:2025 | Prompt Injection | LLM01 (#1) | Retained — enhanced focus on indirect attacks + multimedia vectors |
| 2 | LLM02:2025 | Sensitive Information Disclosure | LLM06 (#6) | **PROMOTED #6 → #2** — Samsung/healthcare breaches drove the rank jump |
| 3 | LLM03:2025 | Supply Chain | LLM05 (#5) | Promoted; concrete poisoned-foundation-model incidents |
| 4 | LLM04:2025 | Data and Model Poisoning | LLM03 (#3) | Expanded to include RAG knowledge-base poisoning + fine-tuning manipulation |
| 5 | LLM05:2025 | Improper Output Handling | LLM02 (#2) | Renamed + repositioned downward; emphasis on downstream-system validation |
| 6 | LLM06:2025 | Excessive Agency | LLM07 + LLM08 (Plugin + Agency) | **MERGED** — covers autonomous agent risks |
| 7 | LLM07:2025 | System Prompt Leakage | NEW | New entry; real-world prompt extraction incidents |
| 8 | LLM08:2025 | Vector and Embedding Weaknesses | NEW | New; RAG architecture attack surface |
| 9 | LLM09:2025 | Misinformation | LLM09 (Overreliance) | Renamed + expanded |
| 10 | LLM10:2025 | Unbounded Consumption | LLM04 (Model DoS) | Replaced; covers cost-attacks (Denial of Wallet) + token exhaustion |

(LLM10:2023 Model Theft was absorbed into LLM02 Sensitive Information Disclosure — model weights are intellectual property and unauthorized access is a data breach.)

## How NuClide surveys map to OWASP LLM Top 10 (2025)

### LLM01:2025 Prompt Injection

- **Flowise** (CVE-2024-36420 PoC lab, 146.190.128.73): `deepseek_admin` chatflow contains a prompt-injection canary in its system prompt designed to leak `{context}` template variables. The researcher is testing both direct prompt injection (the leak) and the implicit security failsafe (the canary).

### LLM02:2025 Sensitive Information Disclosure (Promoted #6 → #2)

- **Phoenix** (2026-06-06): `/v1/projects` exposes project names + IDs unauthenticated; `/v1/users` exposes user records (account IDs, timestamps). 34 of 55 reachable Phoenix instances expose user records publicly.
- **Open WebUI**: AUTH_OFF instances expose chat history including model context and prompts.
- **LiteLLM**: `/model/info` discloses `litellm_params` including endpoint hostnames (Azure resource names, GCP project IDs, Databricks workspace IDs) without auth.

### LLM03:2025 Supply Chain

- (Not yet exercised in 2026-06-06 surveys. aimap-profile findings would surface here when an unauth-discovered host depends on a known-compromised model or library.)

### LLM04:2025 Data and Model Poisoning

- **RAGFlow** (87.2% REGISTER_OPEN): an attacker who registers a tenant can potentially poison the shared knowledge base depending on tenant isolation configuration. This is the *enablement* of LLM04, not the exploitation.

### LLM05:2025 Improper Output Handling

- **Flowise** (Custom Tool node): output from a Custom Tool node is JavaScript code executed server-side; improper output handling here is the same as the Excessive Agency class.

### LLM06:2025 Excessive Agency (Merged Plugin + Agency)

- **Flowise** (CVE-2024-36420): the Custom Tool node grants pre-auth code execution. This is the canonical LLM06:2025 finding in the current survey corpus.
- **Dify** SSO+register conflict (47.117.33.199): registration creates local account before SSO enforcement — a partial-LLM06 scenario where the agent's permissions are decoupled from the authentication path.

### LLM07:2025 System Prompt Leakage (NEW in 2025)

- **Flowise deepseek_admin**: the embedded system prompt itself is leaked (alongside the prompt injection test) via the public `/api/v1/chatflows/{id}` endpoint. Every chatflow's system prompt is readable.

### LLM08:2025 Vector and Embedding Weaknesses (NEW in 2025)

- **RAGFlow**: a registered tenant with knowledge-base creation rights can affect the shared embedding model behavior across tenants depending on configuration. NuClide has not exercised this; the class is documented as enabled.
- **Pinecone** (in Flowise FDA case): an unauthenticated Flowise instance with a configured Pinecone API key means anyone can read or write to the operator's Pinecone index.

### LLM09:2025 Misinformation

- (Not yet surveyed; relevant when an AI-LLM finding could be used to inject misinformation into RAG corpus or fine-tuning data of a target.)

### LLM10:2025 Unbounded Consumption

- **LiteLLM CRIT findings (18 instances)**: open LiteLLM proxy with no master_key = anyone calls `claude-sonnet-4-6` or `gpt-5.4` and bills the operator's Anthropic / Azure / Vertex / Bedrock account. **This is the canonical Denial of Wallet attack the 2025 revision is named for.**
- **Open WebUI + Ollama Connect cloud proxy** (143.47.38.176 with `deepseek-v4-pro:cloud`): same class — operator's DeepSeek subscription billed by any internet user.

## Why the 2023 → 2025 evolution matters for our program

The 2025 revision reflects "shifts in the threat landscape based on documented incidents." The promotions of LLM02 (#6 → #2) and LLM03 (#5 → #3) tell us that **enterprise AI is leaking sensitive information at scale, and that supply-chain attacks against AI infrastructure are now concrete, not hypothetical**.

The two new entries (LLM07 System Prompt Leakage, LLM08 Vector and Embedding Weaknesses) reflect the RAG-architecture shift: 2023 was about standalone LLM API calls; 2025 is about RAG + agent ecosystems. The NuClide survey program covers exactly this attack surface (RAG: RAGFlow, Pinecone, Weaviate; observability: Langfuse, Phoenix; agent: Flowise, LangGraph queued).

## Threat-class detail files

Each LLM01–LLM10 category has its own file in `threat-classes/` linking academic citations and survey instances. Build status: pending fan-out.
