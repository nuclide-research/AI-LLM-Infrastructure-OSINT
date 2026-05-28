# AI Evaluation / Red-Team — Shodan Query Catalog
_Generated: 2026-05-27 from pre-survey OSINT pass (13 platforms)_
_See: data/platform-intel/ai-eval-redteam-osint-2026-05-27.md for full intel_
_Companion file: shodan/queries/23-ai-safety-eval.md (prior pass with confirmed hit counts)_

**Confirmed prior pass (2026-05-04):** Promptfoo 22, LangSmith 96, Garak ~0, DeepEval ~0. CLI-dominant ecosystem — Garak, PyRIT, PromptBench, OpenAI Evals, RAGAS have no HTTP server mode and produce 0 Shodan hits as standalone services.

---

## Promptfoo

**Auth default:** off (CSRF present, no auth gate on API routes)
**Exposure class:** Red-team configs, adversarial prompt libraries, eval results with LLM outputs, provider endpoint references

| Label | Query | Rationale | FP Risk |
|---|---|---|---|
| primary | `http.html:"promptfoo"` | HTML-scoped; confirmed 22 hits in prior pass | Low |
| secondary | `http.title:"promptfoo"` | Title-scoped; confirmed 17 hits in prior pass | Low |
| port-only | `port:15500` | ~730 hits but port shared — FP without HTML conjunction | High |
| api-route | `http.html:"/api/evals"` | Unique Promptfoo eval route in HTML (SPA bundle) | Low |
| api-route-2 | `http.html:"/api/redteam"` | Red-team route in SPA bundle | Low |
| mcp-mode | `port:3100 http.html:"promptfoo"` | MCP server mode + HTML confirmation | Low |
| cert | `ssl.cert.subject.cn:"promptfoo"` | TLS cert CN | Low |
| rdns | `hostname:"promptfoo"` | rDNS hostname pattern | Med |
| identity-probe | `GET /api/user/email` → `{"email": null}` | Confirms unauthenticated Promptfoo instance | — |
| identity-probe-2 | `GET /api/evals` → JSON array with `createdAt` + `results` fields | Confirms eval data exposure | — |

---

## LangSmith (self-hosted)

**Auth default:** off on pre-v0.10 deployments (`AUTH_TYPE=none`); v0.10+ defaults to basic auth
**Exposure class:** Full LLM call traces (inputs/outputs/tokens), prompt templates, eval datasets, API keys in trace metadata

| Label | Query | Rationale | FP Risk |
|---|---|---|---|
| primary | `http.html:"langsmith"` | HTML-scoped; confirmed 96 hits in prior pass | Low |
| secondary | `http.title:"LangSmith"` | Title-scoped; confirmed 67 hits in prior pass | Low |
| port-frontend | `port:1980 http.html:"langsmith"` | LangSmith Nginx frontend port + body confirmation | Low |
| port-api | `port:1984 http.html:"langsmith"` | Backend API port + body confirmation | Low |
| port-only | `port:1984 http.status:200` | 3,061 hits; port shared — FP without HTML conjunction | High |
| info-endpoint | `http.html:"/info" port:1980` | LangSmith `/info` endpoint returning `instance_flags` JSON | Med |
| traces-endpoint | `http.html:"/api/v1/runs"` | Run trace API path in HTML | Med |
| header | `http.html:"X-Tenant-Id"` | LangSmith-specific multi-tenancy header reflected in docs/error pages | Med |
| cert | `ssl.cert.subject.cn:"langsmith"` | TLS cert CN | Low |
| rdns | `hostname:"langsmith"` | rDNS hostname pattern | Low |
| identity-probe | `GET /api/v1/runs?limit=10` → JSON array with `run_type`, `inputs`, `outputs` fields | Confirms unauthenticated trace exposure | — |
| identity-probe-2 | `GET /info` → `{"instance_flags": {...}, "version": "..."}` | Confirms LangSmith instance + version disclosure | — |

---

## Inspect AI (UK AISI)

**Auth default:** off (no auth mechanism; binds localhost by default — external binding required for exposure)
**Exposure class:** Eval log files with task inputs, model outputs, scores; full benchmark results; dataset sample contents

| Label | Query | Rationale | FP Risk |
|---|---|---|---|
| primary | `port:7575 http.html:"inspect"` | Inspect AI default port + HTML confirmation | Low |
| port-only | `port:7575` | Port is not a common shared port; lower FP than 8000/8080 | Med |
| api-logs | `port:7575 http.html:"/api/logs"` | Log viewer API endpoint path | Low |
| title | `http.title:"inspect" port:7575` | Title-based (page title may be "Inspect" or "Inspect AI") | Low |
| alt-port | `port:6565 http.html:"inspect"` | Common alternate port from --port flag | Med |
| package-id | `"inspect-ai"` | Package identifier in any indexed field | Med |
| cert | `ssl.cert.subject.cn:"inspect"` | TLS cert CN — high FP risk given common word | High |
| identity-probe | `GET /api/logs` → JSON array of eval log entries with `eval_id`, `task`, `model` fields | Confirms Inspect AI log viewer | — |

---

## HELM (Stanford CRFM)

**Auth default:** off (read-only static result viewer, no auth)
**Exposure class:** Benchmark evaluation results, full prompt/response logs, model comparison tables

| Label | Query | Rationale | FP Risk |
|---|---|---|---|
| primary | `port:8000 http.html:"HELM" http.html:"scenarios"` | HELM-specific "scenarios" terminology + port | Low |
| secondary | `http.title:"HELM" port:8000` | Title-scoped with port | Med |
| api-runs | `port:8000 http.html:"/api/runs"` | HELM result API path | Med |
| field | `port:8000 http.html:"run_spec"` | Unique HELM JSON field name in SPA bundle | Low |
| field-2 | `port:8000 http.html:"adapter_spec"` | HELM adapter specification field | Low |
| alt-port | `port:8080 http.html:"HELM" http.html:"scenarios"` | Some configurations use 8080 | Med |
| crfm | `http.html:"crfm" http.html:"HELM"` | Stanford CRFM identifier in page | Low |
| identity-probe | `GET /api/runs` → JSON array with `run_spec`, `stats`, `adapter_spec` fields | Confirms HELM instance | — |

---

## TruLens

**Auth default:** off (Streamlit, no auth; inherits Streamlit exposure class)
**Exposure class:** LLM eval traces (full input/output per call), feedback scores, leaderboard across app versions, SQLite eval database

| Label | Query | Rationale | FP Risk |
|---|---|---|---|
| primary | `port:8501 http.html:"trulens"` | TruLens on default Streamlit port + body confirmation | Low |
| secondary | `http.title:"TruLens" port:8501` | Title-based | Low |
| generic-streamlit | `port:8501 http.html:"trulens"` | Streamlit with TruLens body marker | Low |
| feedback-field | `http.html:"trulens_feedback"` | TruLens-specific Streamlit component name | Low |
| trace-field | `http.html:"trulens_trace"` | TruLens trace component | Low |
| alt-port | `port:8502 http.html:"trulens"` | Alt Streamlit port (configured via run_dashboard(port=8502)) | Low |
| rdns | `hostname:"trulens"` | rDNS pattern | Low |
| identity-probe | `GET /` → 200 + `<title>TruLens</title>` or `trulens` in Streamlit page body | Confirms TruLens dashboard | — |

---

## Arthur Shield

**Auth default:** on (API key required; no documented defaults — requires explicit K8s secret provisioning)
**Exposure class:** If misconfigured: task configs, rule results, inference IDs, safety rule pass/fail decisions, retrieved context from hallucination detection

| Label | Query | Rationale | FP Risk |
|---|---|---|---|
| primary | `http.html:"arthur" http.html:"validate_prompt"` | Arthur Shield-specific API path terminology | Low |
| secondary | `http.html:"/api/v2/task" http.html:"arthur"` | Arthur Shield API route prefix | Low |
| docs-path | `http.html:"/docs" http.html:"arthur" http.html:"shield"` | Swagger UI path + product name | Med |
| field | `http.html:"rule_results" http.html:"arthur"` | Unique response field name | Low |
| field-2 | `http.html:"inference_id" http.html:"arthur"` | Inference ID field unique to Arthur Shield responses | Low |
| cert | `ssl.cert.subject.cn:"arthur"` | TLS cert CN (FP risk: "arthur" is a common name) | High |
| identity-probe | `GET /docs` → Swagger UI listing `/api/v2/task/{task_id}/validate_prompt` route | Confirms Arthur Shield instance | — |

---

## Patronus AI

**Auth default:** on (OIDC/OAuth2 in production; basic auth in POC)
**Exposure class:** If misconfigured: eval logs with LLM traces, evaluator profiles, dataset contents, account metadata

| Label | Query | Rationale | FP Risk |
|---|---|---|---|
| primary | `http.html:"patronus" http.html:"/evaluate"` | Patronus + evaluation endpoint path | Low |
| secondary | `http.html:"/v1/" http.html:"patronus"` | V1 API prefix + brand | Low |
| docs | `http.html:"/docs" http.html:"patronus"` | Swagger UI with Patronus brand | Med |
| mcp | `http.html:"patronus-mcp-server"` | Patronus MCP server package identifier | Low |
| identity-probe | `GET /v1/evaluate` → 200 or 401 with `{"detail": "..."}` JSON body | Confirms Patronus instance | — |

---

## DeepEval / Confident AI

**Auth default:** off (OSS local eval server); on for enterprise/Confident AI cloud
**Exposure class:** Test case corpora (prompts + expected/actual outputs), evaluation metric scores, LLM API key environment variable references

| Label | Query | Rationale | FP Risk |
|---|---|---|---|
| primary | `port:8000 http.html:"deepeval" http.html:"confident"` | Conjunction of both identifiers on default port | Low |
| secondary | `http.html:"/api/test-cases" http.html:"deepeval"` | Test-case endpoint path + product name | Low |
| health | `port:8000 http.html:"/api/health" http.html:"deepeval"` | Health endpoint + product name | Low |
| field | `http.html:"test_case_id" http.html:"deepeval"` | Unique test-case ID field | Low |
| cert | `ssl.cert.subject.cn:"deepeval"` | TLS cert CN | Low |
| rdns | `hostname:"deepeval"` | rDNS pattern | Low |
| identity-probe | `GET /api/test-cases` → JSON array with `test_case_id`, `input`, `expected_output`, `actual_output` fields | Confirms DeepEval eval server | — |

---

## No Shodan Surface (CLI-only / no HTTP server)

These platforms produce zero Shodan hits as standalone services. Indirect pivots noted.

| Platform | Indirect Shodan Pivot |
|---|---|
| Garak | `http.html:"garak" http.html:"report.jsonl"` — accidentally exposed output directories |
| PyRIT | `port:5000 http.html:"pyrit"` — Playground Labs only |
| PromptBench | Pivot to Jupyter fingerprint on port 8888 |
| OpenAI Evals | `http.html:"oaieval" http.html:"eval_results"` — exposed result files |
| RAGAS | Pivot to LangSmith/Langfuse fingerprints where RAGAS results are ingested |
| LlamaRisk | N/A — not an AI eval/red-team tool (DeFi org) |

---

## Combined Sweeps

| Label | Query | Rationale |
|---|---|---|
| port-sweep | `(port:15500 OR port:1980 OR port:1984 OR port:7575 OR port:8501)` | AI eval dedicated-port sweep |
| html-sweep | `(http.html:"promptfoo" OR http.html:"langsmith" OR http.html:"trulens")` | Auth-off platforms with confirmed population |
| title-sweep | `(http.title:"promptfoo" OR http.title:"LangSmith" OR http.title:"TruLens")` | Title-scoped sweep |
| rdns-sweep | `(hostname:"promptfoo" OR hostname:"langsmith" OR hostname:"deepeval" OR hostname:"trulens")` | rDNS sweep |
| cert-sweep | `(ssl.cert.subject.cn:"promptfoo" OR ssl.cert.subject.cn:"langsmith" OR ssl.cert.subject.cn:"deepeval")` | TLS cert sweep |
| api-route-sweep | `(http.html:"/api/evals" OR http.html:"/api/redteam" OR http.html:"/api/v1/runs" OR http.html:"/api/test-cases")` | Unique API route paths |
