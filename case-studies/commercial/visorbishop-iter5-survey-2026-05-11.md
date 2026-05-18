---
type: tool-dev-log
title: "VisorBishop iter-5: LiteLLM Proxy + Argilla + Promptfoo (gateway + annotation + eval tiers)"
date: 2026-05-11
class: tool
category: cross-platform-tool-validation
status: research-active
methodology: extending VisorBishop fingerprint coverage to adjacent AI-infra tiers beyond pure observability
---

# VisorBishop iter-5 · 2026-05-11

NuClide Research · 2026-05-11

## Summary

Fifth iteration of the Phase 3 loop. Where iter-1/2/3 extended the
IP-direct-shadow port set and iter-4 added adjacent observability
platforms (Opik, AgentOps, Phospho), **iter-5 expands to adjacent
TIERS**:

- **LiteLLM Proxy** (LLM gateway tier, stores provider API keys, serves OpenAI-compatible API)
- **Argilla** (data annotation tier, labels training data for LLM fine-tuning)
- **Promptfoo** (LLM evaluation tier, runs prompt regression tests)

Trulens and LangChain Hub were also scoped but yielded 0 self-hosted
hits on Shodan; not pursued in this iter.

> **Reproduce with VisorBishop ≥ v0.1.5:** `visorbishop -i hosts.txt -ip-shadow`

**Headline findings:**

1. **LiteLLM: 25 of 269 confirmed instances are CRITICAL unauth (9.3%). Population-scale LLMjacking primitive.** From a sample of 500 of the 5,408 Shodan-listed LiteLLM hosts. Extrapolated population-scale unauth count: **~500 instances**. The model catalogs reveal operators paying for Claude Sonnet/Haiku, GPT-4o/GPT-5-nano, Gemini 1.5/3.1 Pro/Flash, Bedrock, Azure OpenAI, Ollama, and various fine-tuned deployments. All of which attackers can prompt at the operator's expense.
2. **Promptfoo: 10 of 17 self-hosted instances are CRITICAL unauth (59%).** `/api/results/` returns full eval history publicly. One operator (`35.227.160.55:3000` / Google Cloud US) exposes **100 evals**. Another (`evals.dev.generalwisdom.com`) exposes 3.
3. **Argilla: 25 of 37 confirmed Argilla instances; 0 unauth.** Auth posture uniformly strong (`argilla.api.errors::UnauthorizedError` returned on every protected route). Notable operators: Climate Policy Radar (4 hosts), 510.global (Red Cross humanitarian AI), Five9 contact-center, algoan fintech.

## Population summary

| Platform | Shodan dork | Total hits | Confirmed | Critical (unauth) |
|---|---|--:|--:|--:|
| LiteLLM Proxy | `http.title:"LiteLLM API"` | **5,408** | 269 of 500 sample | **25 (9.3%)** |
| Argilla | `http.title:"Argilla"` | 37 | 25 | **0** |
| Promptfoo | `http.title:"promptfoo"` | 17 | 11 | **10** |
| Trulens | `http.title:"TruLens"` | 1 | — | — |
| LangChain Hub self-host | various | 0 | — | — |

LiteLLM's 5,408-hit population is **the largest of any platform
surveyed in this entire research chain.** Phoenix was 377; Langfuse
1,333. LiteLLM's order-of-magnitude larger population reflects its
"every dev tries it" posture. The BerriAI/litellm pip install is
~5 lines to run, and the default Swagger UI exposes the title that
matches our dork.

## CRITICAL: Promptfoo public eval-history disclosure

**10 of 17 Promptfoo self-host instances expose `/api/results/` without
authentication.** Promptfoo's OSS server has no auth layer by default.
Operators run `promptfoo view` to expose their local eval browser, and
when they deploy the same command on a public-facing host, the eval
list becomes publicly readable.

The eval data class:
- Full prompts under test
- Model responses and assertion failures
- Configuration including model names, temperature, system prompts
- Dataset metadata

Top yield by eval count:

| Host | Operator | Eval count | Country |
|---|---|--:|---|
| `35.227.160.55:3000` | (Google Cloud US) | **100** | US |
| `3.13.69.153:443` | (AWS US-East-2) | 12 | US |
| `64.112.124.114:3000` | csdi-admin.local (KhanWebHost) | 11 | US |
| `172.96.192.235:12380` | (Cluster Logic) | 8 | US |
| `3.218.253.194:443` | **`evals.dev.generalwisdom.com`** (AWS US-East-1) | 3 | US |
| `103.177.248.237:3000` | (Hostup AB) | 1 | Sweden |
| `43.204.199.18:80` | (AWS Mumbai) | 1 | India |
| `38.105.232.166:3000` | `ped.staging.agence.net.br` | 0 | BR (Contabo) |
| `147.78.130.168:3000` | (Contabo DE) | 0 | DE |
| `49.12.34.32:3000` | `badllama.pranavg.me` | 0 | DE (Hetzner) |

The General Wisdom find is particularly notable: their `evals.dev.*`
naming implies this is their development-tier eval pipeline.

The **Promptfoo unauth rate at population scale is 59% (10/17)**.
Higher than Phoenix's 25%. Different tier, but same shipping-default
problem: the OSS server has no built-in auth and the operator must
deploy their own.

## Argilla: 0 unauth across 25 confirmed

Argilla's server enforces API-key auth on every protected route by
default. All 25 confirmed Argilla instances returned the same
`{"detail":{"code":"argilla.api.errors::UnauthorizedError","params":{"detail":"Could not validate credentials"}}}` shape on `/api/v1/me`.

Notable Argilla operators (auth-protected, info-class only):

| Operator | Hosts | Sector |
|---|--:|---|
| **Climate Policy Radar** | 4 | UK climate policy AI |
| **510.global** | 1 | Red Cross humanitarian data AI |
| **Five9** | 2 | Contact-center SaaS |
| **algoan.com** | 1 | French fintech |
| **bee.ai** | 1 | AI startup |
| **konzierge.at** | 1 | Austrian AI consultancy |
| **naiveneuron.com** | 1 | Slovak AI shop |
| **radai-systems.com** | 2 | (AI systems vendor) |
| Other AWS/GCP/elestio.app | 12 | Various |

The annotation-training-data exposure surface is real but
operator-controlled. Argilla forces auth from the start, so
misconfiguration is rare. Same class as Langfuse (mandatory-auth
platforms).

## LiteLLM Proxy: order-of-magnitude larger population

LiteLLM is the **LLM gateway tier**, not observability. Operators deploy
it to proxy LLM API calls (OpenAI, Anthropic, Bedrock, Vertex AI, etc.)
through a single endpoint while applying rate-limiting, cost-tracking,
and key management.

The Shodan population at `http.title:"LiteLLM API"` is **5,408 hosts**.
The largest population we've seen in this entire research chain. The
500-host sample probe is in progress.

### 500-host sweep result

| Result | Count |
|---|--:|
| Total probed | 500 |
| Confirmed LiteLLM | **269** (54%) |
| CRITICAL (unauth `/v1/models`) | **25** (9.3% of confirmed, 5.0% of all probed) |
| Auth-fronted | 244 |

**Top deployed versions:**
- 1.82.6 (44 hosts)
- 1.82.3 (27)
- 1.83.10 (18)
- 1.81.14 (17)
- 1.83.14 (13)
- 1.81.12 (10)
- 1.82.1 (8)
- 1.80.8 (7)

Operators run mostly current LiteLLM. Range from 1.77.x to 1.83.x. Last
month or two of releases.

### Sample of unauth LiteLLM hosts: what's behind them

The 25 CRITICAL hosts disclose their model catalogs (no auth needed for
`/v1/models`). The catalogs reveal what attacker-supplied prompts would
get billed to:

| Host | Models exposed | Notable |
|---|---|---|
| `103.52.212.89:4000` | 15 incl. `asisten-desa`, `cadangan-groq`, `cadangan-gemini-1` | Indonesian public-sector AI ("village assistant"), Groq+Gemini fallback chain |
| `204.168.237.160:4000` | 44 incl. `cloud-fallback-1..n` | Large fleet with redundancy |
| `45.124.54.69:4000` | 5 incl. `claude-3-5-sonnet-20241022`, `claude-3-5-sonnet-20240620`, **`claude-sonnet-4-6`** | Anthropic Sonnet across versions including current |
| `144.124.252.251:4000` | 4 incl. `gpt-5-nano`, `gpt-4o-mini`, `text-embedding-3-small` | OpenAI tier with embeddings |
| `159.69.106.84:4000` | 2 incl. `gpt-4o`, `claude-3-5-sonnet` | Dual-provider |
| `74.48.70.26:4000` | 1: `bedrock/anthropic.claude-3-5-sonnet-20241022-v2:0` | AWS Bedrock |
| `172.203.222.133:8000` | 1: `azure/gpt-4o-mini` | Azure OpenAI |
| `47.99.185.244:4000` | 7 incl. `WK-qwen3.6-plus`, `WK-qwen3.5-plus`, `WK-qwen3-max-2026-01-23` | Chinese WK-branded Qwen fine-tunes |
| `121.31.38.238:4000` | 6 incl. `deepseek-v4-pro`, `gpt-4o`, `gpt-4` | DeepSeek + OpenAI multi-provider |
| `110.164.163.24:4000`, `:5555`, `:443` | 2-5 Gemini Flash/Pro variants | One Thai operator running 3 instances on different ports |
| `135.181.26.207:4000` | 2 incl. `gemini-3.1-flash-lite`, `gemini-3.1-pro` | Gemini 3.1 |
| `172.232.115.211:4000` | 1: `kimi-k2.5` | Moonshot Kimi |
| Various | Ollama `qwen2.5`, `deepseek-coder`, `gemma`, `mistral` | Self-hosted models |

### Why LiteLLM unauth is severe

When `LITELLM_MASTER_KEY` is not set, the LiteLLM proxy:
- Accepts arbitrary `/v1/chat/completions` requests from anyone on the internet
- Forwards them to the operator's configured upstream providers (OpenAI, Anthropic, Bedrock, etc.) using the operator's stored API keys
- **Operator pays the bill**

This is the classic LLMjacking primitive. Attacker-supplied prompts get
billed to the operator's OpenAI / Anthropic / Bedrock account at the
operator's rate-tier. A single hour of automated probe traffic against an
unauth LiteLLM can run thousands of dollars.

### Population-scale extrapolation

If the 9.3% unauth rate in the 500-host sample holds across the full
**5,408-host Shodan population**, the population-scale count is
**~500 unauth LiteLLM instances** worldwide. Each is a per-instance
LLMjacking exposure.

A focused iter-6 against the full 5,408-host population would catalogue
the entire global LiteLLM exposure surface. Worth doing.

### Why LiteLLM unauth is severe

When `LITELLM_MASTER_KEY` is not set, the LiteLLM proxy:
- Accepts arbitrary `/v1/chat/completions` requests from anyone on the internet
- Forwards them to the operator's configured upstream providers (OpenAI, Anthropic, etc.) using the operator's stored API keys
- **Operator pays the bill**

This is the classic LLMjacking primitive. Attacker-supplied prompts get
billed to the operator's OpenAI / Anthropic / Bedrock account at the
operator's rate-tier. A single hour of automated probe traffic against an
unauth LiteLLM can run thousands of dollars.

## Bug fixed live during iter-5

Iter-5 surfaced a **false-positive bug** in the LangSmith prober: it
matched ZenML's `/api/v1/info` response shape (which also has a
`version` field). Fixed in VisorBishop@7b0185a
by requiring LangSmith-specific markers (`license_expiration_time`,
`customer_info`, or known LangSmith instance_flags) before confirming
identity.

This is the third correctness gap iter-N has surfaced (after iter-1's
URL-parser and iter-1's port-parallelism). All three required real
population workloads to manifest. **Iterating produces real
correctness wins**, not just methodology refinement.

This concretely demonstrates Methodology Insight #15 (in draft):
*Generic API shapes are not platform identifiers. Confirmation requires
platform-specific markers; otherwise iter-N will surface false
positives that the original probe set didn't anticipate.*

## Performance

- Argilla 37 hosts: 30.8s (only 1 probe per host)
- Promptfoo 17 hosts: 35.1s (only 1 probe per host)
- LiteLLM 500 hosts: in progress; estimated 10-15min

The LiteLLM prober makes 3-4 probes per host (root for title check, optional `/.well-known/litellm-ui-config`, `/v1/models`, optional `/openapi.json` for version). With 24 concurrency the per-host wall time is the bottleneck on slow Shodan-listed hosts.

## Next steps

1. ~~Build VisorBishop (Phase 3)~~ ✓
2. ~~iter-1 / 2 / 3 / 4: port expansion + platform expansion~~ ✓
3. **iter-5: LiteLLM 500-sweep complete** → update this case study with full numbers
4. **iter-6 candidate**: full LiteLLM 5,408-host sweep (requires Shodan credit budget approval)
5. **Methodology Insight #14, #15 final writeups**
6. **Phase 4 (web UI)**, visorBishop dashboard with cross-platform attribution

## Evidence pack

`~/recon/2026-05-10-llm-sweep/visorbishop-results/iter5/`
- `argilla-noshadow.json` / `.csv`. 37-host Argilla sweep
- `promptfoo-noshadow.json` / `.csv`. 17-host Promptfoo sweep
- `litellm-noshadow.json` / `.csv`. 500-host LiteLLM sample (in progress)

Source: Nicholas-Kloster/VisorBishop@v0.1.5

Cross-references:
- [iter-4 case study](visorbishop-iter4-survey-2026-05-11.md)
- [Phase 3 case study](visorbishop-phase3-survey-2026-05-11.md)
- [Methodology Insight #12](../../methodology/insight-12-ip-direct-shadow.md)
