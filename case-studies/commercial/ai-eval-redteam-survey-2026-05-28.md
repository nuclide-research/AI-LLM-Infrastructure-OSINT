---
title: "AI Evaluation and Red-Team Platform Survey — Promptfoo Population Pass"
date: 2026-05-28
type: survey
sector: commercial
tags: [promptfoo, langsmith, eval, red-team, unauth, UNAUTH, ai-safety]
---

# AI Evaluation and Red-Team Platform Survey — Promptfoo Population Pass

_NuClide Research · 2026-05-28 · Population sweep of 13 AI eval/red-team platforms. Four confirmed unauthenticated Promptfoo instances. LangSmith, TruLens, Inspect AI, HELM, DeepEval, PyRIT, Garak all null at population scale._

## Summary

Promptfoo is the only AI eval/red-team platform in the 13-platform scope that produced confirmed unauthenticated exposure at scale. Four instances returned `{"email":null}` on `GET /api/user/email` with eval datasets and provider configurations readable without credentials. The best-characterized instance (evals.dev.generalwisdom.com, AWS Ashburn) exposed 60 LLM provider configurations including the Anthropic Claude 4.x model family and Azure GPT-4o, along with active eval datasets including test case corpora, prompt templates, and token usage statistics from runs as recent as 2026-05-01. LangSmith self-hosted instances were auth-enforced across all 30+ sampled hosts; v0.10+ default auth tightening has held. The six remaining platforms with HTTP server modes (TruLens, Inspect AI, HELM, DeepEval, Arthur Shield, Patronus AI) produced zero confirmed instances on Shodan. Six platforms are CLI-only with no HTTP server; Shodan surface is zero by design.

## Thesis fit

Auth-on-default thesis: **mixed signal**. Promptfoo ships with no auth gate on the web UI or API routes by default — four confirmed instances prove this is not theoretical. LangSmith, which was the thesis anchor for this category (96 hits in prior pass, known `AUTH_TYPE=none` default pre-v0.10), shows auth enforcement holding across the current sample. Two contradictory outcomes in the same category survey: one platform's default hardened over time (LangSmith Insight #40 pattern), one platform's default remains open (Promptfoo).

---

## Per-finding entries

### F1. `evals.dev.generalwisdom.com` (100.50.218.102)

#### What was found

GET `/api/user/email` returned `{"email":null}` — the Promptfoo identity probe for an unauthenticated instance. GET `/api/providers` returned a 60-provider configuration list including:

- `anthropic:messages:claude-haiku-4-5-20251001` (max_tokens: 2048, temperature: 0.5)
- `anthropic:messages:claude-opus-4-6` (max_tokens: 2048, temperature: 0.5)
- `anthropic:messages:claude-sonnet-4-5-20250929` (max_tokens: 2048, temperature: 0.5)
- `azure:chat:gpt-4o` (api_host: your-resource-name.openai.azure.com)
- `azure:chat:gpt-4o-mini`
- Plus 55 additional configured providers

GET `/api/datasets` returned:
- Dataset ID `06fb902...`, count 3 test cases
- Test cases from `file://../datasets/regression-core.yaml`
- Most recent eval: `eval-OJn-2026-05-01T13:29:42`
- Metrics: 32 pass / 0 fail, 213,085 tokens consumed, 547,050ms total latency, cost: $0 (inferred: local/API key with no cost tracking or free tier)

The `providers` endpoint response was served as JSON with status 200 and no authentication challenge. The Azure `api_host` value of `your-resource-name.openai.azure.com` is a placeholder — Azure credentials are not hardcoded in the provider config as stored in the database.

#### Why it is bad

Verified: operator's LLM evaluation configuration is readable by anyone with network access. This includes which model families are being evaluated, the temperature/max_tokens parameters tuned for each, and the structure of the regression test suite.

Inferred (not exercised): individual eval run results accessible via `/api/evals` if the Express catch-all is bypassed or if the API responds to XHR requests from a browser session against the SPA. The identity probe and providers/datasets endpoints confirmed the platform is unauthenticated; full eval history access is the logical downstream.

Hypothesized: if this instance is used for comparing proprietary model variants or testing red-team robustness, the adversarial prompt library and model response comparison data would be in the eval history. Not extracted.

#### Who it affects

Operator: General Wisdom (generalwisdom.com). AWS US-East (Ashburn). Commercial sector. The `evals.dev` subdomain indicates this is a development/staging eval environment rather than production, but the exposure is real and the provider config is active (recent eval run 2026-05-01).

#### How it got exposed

Promptfoo's Express server serves both the static React SPA and the API routes from the same process. Authentication is not enabled by default — the CSRF middleware is present but no auth gate exists on `/api/*` routes. The `--share` flag (for cloud.promptfoo.app) is the only auth-gating path; local/self-hosted deployments have no equivalent by default. This instance was deployed on AWS with port 443 directly internet-reachable, TLS via Let's Encrypt, and no reverse proxy enforcing authentication.

Root cause: shipping default (auth off). Matches Insight #13 (shipping-defaults-are-load-bearing). The eval platform category is particularly sensitive because the exposure class includes adversarial prompt libraries, red-team test configurations, and model comparison data — outputs of security testing work that operators presumably want to keep internal.

#### Which tools contributed to the finding

| Stage | Tool | Contribution |
|---|---|---|
| 0 — Discover | JAXEN/Shodan (Playwright) | `http.title:"promptfoo"` — 17 hits; evals.dev.generalwisdom.com in page 1 results |
| 1 — Fingerprint | curl | HTTP title + `X-Powered-By: Express` + `Access-Control-Allow-Origin: *` confirmed Promptfoo |
| 2 — Verify | curl | GET `/api/user/email` → `{"email":null}`; GET `/api/providers` → 60-provider JSON; GET `/api/datasets` → eval history with token stats |
| 3 — Attribute | Shodan result | CN: evals.dev.generalwisdom.com; ASN: Amazon.com Inc. US-East |
| 4 — Classify | manual | Commercial, development eval environment |
| 5 — Ledger | VisorLog | Finding #162, severity medium |
| 6 — Score | VisorScuba | AI.C1 violation — unauthenticated AI service |
| 6 — Exploit-rank | BARE | Attempted; binary sandbox-blocked this session; deferred |
| 7 — Codify | manual | See methodology section below |

**Tools that ran but did not contribute unique signal**: aimap (no Promptfoo fingerprint; ports 80/443 confirmed open but no AI service identified); VisorgGraph (sandbox permission denied this session); VisorCorpus (N/A — no LLM corpus surface).

**The load-bearing chain**: Shodan title dork → HTTP identity probe → API dataset extraction.

---

### F2. `103.177.248.237` (Hostup AB, Sweden)

#### What was found

GET `/api/user/email` returned `{"email":null}`. Response headers: `X-Powered-By: Express`, `Access-Control-Allow-Origin: *`. Content-Length: 1034 bytes (index.html). Port 3000.

GET `/api/datasets` returned an eval dataset: prompt "Tell me a good dadjoke", vars `{model: mistral-small}`, 5 test runs, most recent eval `eval-8F5-2026-03-30T12:36:45`.

#### Why it is bad

Verified: unauthenticated Promptfoo with eval history readable. Dataset contains LLM evaluation runs using mistral-small, with adversarial/test prompt content visible.

#### Who it affects

Hostup AB, Sweden. VPS hosting. Likely a personal or small-team eval environment given the "dadjoke" test suite. Most recent eval: March 2026.

#### How it got exposed

Same root cause as F1 — Promptfoo default auth-off. No reverse-proxy auth layer.

#### Which tools contributed to the finding

| Stage | Tool | Contribution |
|---|---|---|
| 0 — Discover | JAXEN/Shodan (Playwright) | `http.title:"promptfoo"` page 1 |
| 1 — Fingerprint | curl | X-Powered-By: Express + title confirmation |
| 2 — Verify | curl | `/api/user/email` → `{"email":null}`; `/api/datasets` → eval history |
| 3 — Attribute | Shodan | Hostup AB, Sweden |
| 4 — Classify | manual | Commercial/personal, small-scale |
| 5 — Ledger | VisorLog | Finding #163, severity medium |
| 6 — Score | VisorScuba | AI.C1 violation |
| 6 — Exploit-rank | BARE | sandbox-blocked this session |

---

### F3. `64.112.124.114` (United States)

#### What was found

GET `/api/user/email` returned `{"email":null}`. Port 3000. GET `/api/datasets` returned: dataset with test case vars `{model: mistral-small}`, prompt "Tell me a good dadjoke", 5 runs, eval date 2026-03-30. Functionally identical dataset to F2.

#### Why it is bad

Same exposure class as F2.

#### Who it affects

US-hosted, bare IP, unattributed to a specific org from the Shodan result.

#### Which tools contributed to the finding

| Stage | Tool | Contribution |
|---|---|---|
| 0 — Discover | JAXEN/Shodan (Playwright) | `http.title:promptfoo port:3000` page 2 results |
| 1 — Fingerprint | curl | Express headers |
| 2 — Verify | curl | `/api/user/email` → `{"email":null}`; `/api/datasets` → eval data |
| 3 — Attribute | Shodan | US, bare IP |
| 5 — Ledger | VisorLog | Finding #164, severity medium |
| 6 — Score | VisorScuba | AI.C1 violation |

---

### F4. `43.204.199.18` (AWS Asia Pacific — Mumbai, India)

#### What was found

GET `/api/user/email` returned `{"email":null}`. HTTP headers: nginx/1.24.0 (Ubuntu) reverse proxy, X-Powered-By: Express, Access-Control-Allow-Origin: *. Port 80. GET `/api/datasets` returned: test case "Fun animal adventure story" with `vars: {animal: penguin, location: tropical island}`, assertions including `contains-any` and `llm-rubric` checking for child-friendly content. Most recent eval visible.

This is the only instance with an `llm-rubric` assertion in the exposed dataset — it evaluates model outputs using a second LLM call as a judge. The rubric and evaluation criteria are readable.

#### Why it is bad

Verified: eval dataset with LLM-rubric configuration exposed. The rubric criteria and test prompts are visible. If the instance is part of an active pipeline, subsequent eval runs and their rubric-graded outputs are also accessible.

#### Who it affects

AWS ap-south-1 (Mumbai). Commercial operator, unattributed by hostname.

#### Which tools contributed to the finding

| Stage | Tool | Contribution |
|---|---|---|
| 0 — Discover | JAXEN/Shodan (Playwright) | `http.title:"promptfoo"` page 1 |
| 1 — Fingerprint | curl | nginx + Express response chain |
| 2 — Verify | curl | `/api/user/email` → `{"email":null}`; `/api/datasets` → llm-rubric eval config |
| 3 — Attribute | Shodan | Amazon.com, Inc. ap-south-1 |
| 4 — Classify | manual | Commercial, active dev eval |
| 5 — Ledger | VisorLog | Finding #165, severity medium |
| 6 — Score | VisorScuba | AI.C1 violation |

---

## Null results — platforms that ran but produced no confirmed findings

| Platform | Shodan Query | Hits | Verified | Notes |
|---|---|---|---|---|
| LangSmith self-hosted | `http.title:"LangSmith"` | 77 | 0 unauth | All sampled hosts returned 401 on `/api/v1/runs`; v0.10+ auth default is holding |
| TruLens | `http.title:"TruLens"` | 1 | 0 genuine | trulens.asia = Cambodian news website (FP) |
| Inspect AI | `http.title:"Inspect" port:7575` | 0 | 0 | No instances on default port |
| HELM | `http.title:"HELM" port:8000` | 2 | 0 | Both hits = Coolify (Kubernetes Helm package manager) FPs |
| DeepEval/Confident AI | `http.title:"deepeval"` | 0 | 0 | No instances; enterprise-only self-hosted |
| PyRIT | `http.title:"PyRIT"` | 0 | 0 | CLI-only; no HTTP server |
| Garak | `http.title:"garak"` | 4 | 0 | FPs (Chatterbox TTS); CLI-primary per prior pass |
| Patronus AI | `http.title:"Patronus"` | 3 | 0 | FPs (Polish hospital, AWS LBs); K8s-only deployment |
| Arthur Shield | `http.title:"Arthur Shield"` | 13 | 0 | Cloudflare blocked scrape; K8s-only, auth-enforced by design |
| RAGAS | `http.title:"RAGAS"` | 4 | 0 | ragas.app cloud SaaS only; no self-hosted surface |
| PromptBench | N/A | 0 | 0 | Python library; no HTTP server |
| OpenAI Evals | N/A | 0 | 0 | CLI-only; OpenAI deprecated self-hosted |
| LlamaRisk | N/A | 0 | 0 | Out of scope — DeFi org, not AI eval |

---

## Cross-survey analysis

Promptfoo population: 17 title hits, 4 confirmed unauth (24% unauth rate on sample). This is lower than the Ollama population (historically ~60-70% unauth) but comparable to Langfuse (~20% in prior surveys) and higher than LangSmith current (effectively 0% unauth on this pass).

The LangSmith population at 77 title hits is larger than the 2026-05-04 baseline of 96 but represents a different mix — the prior pass used `http.html:"langsmith"` which would catch page bodies as well as titles. The title-only dork skews toward instances that set a page title explicitly (the nginx-fronted LangSmith Docker deployment does set `<title>LangSmith</title>`). Auth enforcement is consistent across the sample.

F3 and F2 share an identical dataset (mistral-small dadjoke eval, same eval date 2026-03-30). This could be a template or tutorial dataset that multiple operators used when setting up their instances. If so, the dataset itself is not sensitive — but it confirms the auth state.

F1 (generalwisdom.com) is the operationally significant finding: 60 configured providers including the full current Anthropic model lineup suggests this is an active enterprise evaluation environment, not a tutorial instance.

---

## Methodology — what this case study adds

Candidate Insight #50: **Promptfoo default-auth-off is a live exposure class.** At 4/17 confirmed unauth (24% on sampled population), Promptfoo joins the roster of AI infrastructure tools where shipping defaults produce real-world exposure. The signal is distinct from Ollama (model execution) and Langfuse (trace data) — Promptfoo exposes the adversarial test design itself: which models are being compared, on what criteria, with what prompts. For operators doing red-team work, this is the methodology, not just the data.

This also reveals a fingerprinting gap in aimap v1.9.36: Promptfoo is not in the fingerprint corpus. The `/api/user/email` → `{"email":null}` probe is a reliable identity signal. A Promptfoo fingerprint (port 3000/15500, `X-Powered-By: Express`, `Access-Control-Allow-Origin: *`, `/api/user/email` returns `{"email":null}` or `{"email":"user@example.com"}`) should be added.

---

## Honest negative space

The `http.html:` Shodan filter requires a paid plan filter token — not available via the web UI authenticated session. All dorks used `http.title:` which misses Promptfoo instances running behind a custom title or reverse proxy that strips/rewrites the page title. The 17 hits on `http.title:"promptfoo"` is a floor, not a ceiling. The ssl.cert.subject.cn:promptfoo (25 hits) population was not fully probed this session.

LangSmith port 1984 (the backend API) returned 0 results via Shodan title filter — this port likely requires `http.html:` or response-body content filters to enumerate directly. The 77 title-filter hits are also a floor.

---

## Disclosure queue (verified scope)

| Finding | Target | Tier | Status |
|---|---|---|---|
| F1 | evals.dev.generalwisdom.com | MEDIUM (verified) | Queued — development environment; provider configs exposed but no API key leakage confirmed |
| F2 | 103.177.248.237 | MEDIUM (verified) | Queued — low-sensitivity dataset (dadjoke eval); low priority |
| F3 | 64.112.124.114 | MEDIUM (verified) | Queued — low-sensitivity dataset; bare IP operator unknown |
| F4 | 43.204.199.18 | MEDIUM (verified) | Queued — LLM rubric eval exposed; AWS ap-south-1 |

All four: auth-off by shipping default, not by misconfiguration. Remediation is adding auth middleware or placing the Promptfoo instance behind a reverse proxy with auth (nginx + basic auth, or Authelia/Vouch).

---

## Toolchain provenance

```
Shodan (Playwright) → 19 dorks executed → 4 platforms with hits (LangSmith 77, Promptfoo 17, TruLens 1, HELM 2)
  → curl direct probes on IP list
  → /api/user/email identity probe → 4 confirmed unauth (Promptfoo)
    → /api/providers → 60 LLM providers (F1)
    → /api/datasets → eval dataset + run history (F1, F2, F3, F4)
  → aimap (target-by-target) → 2 open ports confirmed; no AI service fingerprint match (Promptfoo not in corpus)
  → VisorLog ingest → Findings #162–165 (medium)
  → VisorScuba assess → AI.C1 violation (4/4)
  → BARE → sandbox-blocked this session; deferred
  → VisorGraph → sandbox permission denied this session; deferred
```

## See also

- `shodan/queries/ai-eval-redteam-queries.md` — full dork catalog
- `data/platform-intel/ai-eval-redteam-osint-2026-05-27.md` — pre-survey platform intel
- `shodan/queries/23-ai-safety-eval.md` — prior 2026-05-04 pass (Promptfoo 22, LangSmith 96)
