# AI Evaluation / Red-Team Platform OSINT — Pre-Survey Intelligence
**Date:** 2026-05-27
**Purpose:** Tune dork queries, understand auth posture, identify verification probes, document data exposure classes before Shodan harvests.
**Scope:** 13 platforms — LLM evaluation, red-teaming, safety testing, benchmark frameworks.
**Status:** Pre-survey. No active probing conducted.

**Prior survey note:** `shodan/queries/23-ai-safety-eval.md` ran a population pass in 2026-05-04 and confirmed the ecosystem is CLI-dominant. Confirmed hit counts from that pass are inline below where available. This file deepens the fingerprinting discipline and adds platforms not covered in the prior pass (Inspect AI, HELM, TruLens, RAGAS, Arthur Shield, Patronus AI).

---

## Promptfoo

**Category:** LLM Eval + Red-Team  
**Default Ports:** 15500 (Express API backend), 3000 (React web UI in dev mode)  
**Auth Default:** off — CSRF middleware present but no authentication gate on the web UI or API routes by default; auth required only for cloud.promptfoo.app features  
**Shodan Dork (primary):** `http.html:"promptfoo"`  
**Shodan Dork (secondary):** `http.title:"promptfoo"`  
**Verification Probe:** `GET /api/evals` → 200 + JSON array of eval history records; `GET /api/user/email` → 200 + `{"email": null}` on unauthenticated instance  
**Data Exposure Class:** Full red-team test results (adversarial prompts + model outputs), eval configs referencing API keys via environment variable names, LLM provider credential references in `promptfooconfig.yaml`, red-team plugin configs listing target LLM endpoints  
**Known CVEs:** None specific. Supply-chain risk via promptfoo npm package; no CVE track record as of 2026-05-27.  
**Default Credentials:** None  
**Notes:** Prior pass confirmed 22 hits on `http.html:"promptfoo"`, 17 on `http.title:"promptfoo"`. Port 15500 alone returns ~730 — port is shared; HTML conjunction required. Web UI is a React SPA served by the Express server. Routes confirmed: `/api/eval`, `/api/providers`, `/api/redteam`, `/api/user`, `/api/model-audit`. The `_conversation` variable and `metadata.openaiEvalsImport` fields appear in eval result JSON and are unique to Promptfoo. MCP server mode (port 3100) is also exposed when `--mcp` flag is used.

---

## DeepEval / Confident AI

**Category:** LLM Evaluation Framework + Observability Platform  
**Default Ports:** 8000 (self-hosted API server, FastAPI/uvicorn), 8443 (TLS variant)  
**Auth Default:** off on the OSS local eval server; Confident AI cloud and enterprise on-prem use API key header `CONFIDENT-API-KEY`  
**Shodan Dork (primary):** `port:8000 http.html:"deepeval" http.html:"confident"`  
**Shodan Dork (secondary):** `http.html:"/api/test-cases" http.html:"deepeval"`  
**Verification Probe:** `GET /api/health` → 200; `GET /api/test-cases` → JSON array with `test_case_id`, `input`, `expected_output`, `actual_output` fields  
**Data Exposure Class:** Test case corpora (prompts + expected outputs + actual LLM outputs), evaluation metric scores (faithfulness, relevancy, etc.), LLM API keys referenced in config, dataset management endpoints  
**Known CVEs:** None specific. Enterprise on-prem deployment requires Docker images provided under Enterprise license — no public image; reduces population density.  
**Default Credentials:** None (API key auth is opt-in for Confident AI cloud)  
**Notes:** Confident AI self-hosted is enterprise-only — not self-serve. OSS DeepEval has no HTTP server mode by default; `deepeval test run` is pytest-based CLI. Population density expected very low. Single-word `"deepeval"` or `"confident"` body matches fire on unrelated pages (FP risk HIGH without conjunction). The `CONFIDENT_BASE_URL` env var allows pointing to a custom endpoint — look for this in leaked configs.

---

## LangSmith (self-hosted)

**Category:** LLM Tracing + Evaluation Observability  
**Default Ports:** 1980 (Nginx frontend, web UI), 1984 (langchain-backend REST API), 1986 (platform-backend), 1987 (ace-backend), 3001 (playground)  
**Auth Default:** off — `AUTH_TYPE=none` is the Docker Compose default (deprecated as of v0.10, removed in v0.11); production requires explicit auth configuration. PostgreSQL default: `postgres/postgres`. ClickHouse default: `default/password`.  
**Shodan Dork (primary):** `http.html:"langsmith"`  
**Shodan Dork (secondary):** `http.title:"LangSmith"`  
**Verification Probe:** `GET /api/v1/runs` → 200 + JSON array of LLM run traces; `GET /info` on port 1980 → `{"instance_flags": {...}}` JSON with version  
**Data Exposure Class:** Full LLM call traces (inputs/outputs/tokens), prompt templates, eval datasets, run feedback, user/org metadata, API keys in trace headers (`x-api-key`). Traces contain downstream LLM provider keys if logged carelessly. Unique HTTP headers: `X-Tenant-Id`, `X-Organization-Id`.  
**Known CVEs:** None specific to LangSmith. PostgreSQL `postgres/postgres` default credential is a secondary vector.  
**Default Credentials:** PostgreSQL: `postgres/postgres`; ClickHouse: `default/password`; Redis: no auth  
**Notes:** Prior pass confirmed 96 hits on `http.html:"langsmith"`, 67 on `http.title:"LangSmith"`. Port 1984 alone returns 3,061 — port is shared; HTML conjunction required. Auth has been tightened in v0.10+ but older deployments still expose `AUTH_TYPE=none`. The `/otel/v1/traces` endpoint accepts OpenTelemetry trace ingestion without auth on `AUTH_TYPE=none` deployments.

---

## Garak (NVIDIA LLM Vulnerability Scanner)

**Category:** LLM Vulnerability Scanner / Red-Team CLI  
**Default Ports:** N/A — CLI-only tool, no built-in HTTP server mode  
**Auth Default:** N/A (no server mode)  
**Shodan Dork (primary):** N/A — no network surface  
**Shodan Dork (secondary):** N/A  
**Verification Probe:** N/A  
**Data Exposure Class:** Indirect — `garak.<uuid>.report.jsonl` output files contain every adversarial prompt sent and model response received; HTML + JSON report formats. If a deployment pipeline pushes garak output to an exposed web server or object storage, the report files are the exposure surface.  
**Known CVEs:** None specific. Garak probes other systems; it is not itself network-accessible.  
**Default Credentials:** N/A  
**Notes:** Garak's REST generator (`garak.generators.rest`) is an *input adapter* for targeting remote REST LLMs — it is not a server. Deployment surface: garak output files landing in world-readable paths (e.g., S3 buckets without auth, exposed nginx `/reports/` directories). Shodan pivot: search for `garak.<uuid>` pattern in indexed HTML or filenames — `http.html:"report.jsonl"` combined with `http.html:"garak"` could surface accidentally exposed report directories. Population near-zero confirmed in prior pass.

---

## Inspect AI (UK AISI)

**Category:** LLM Evaluation Framework / Benchmark Runner  
**Default Ports:** 7575 (inspect view log viewer web server), configurable via `--port`  
**Auth Default:** off — `inspect view` binds `127.0.0.1:7575` by default; external binding requires explicit `--host 0.0.0.0`; no auth mechanism  
**Shodan Dork (primary):** `port:7575 http.html:"inspect"`  
**Shodan Dork (secondary):** `port:7575`  
**Verification Probe:** `GET /` → 200 + HTML with `robots.txt`, `assets/`, `logs/` structure; `GET /api/logs` → JSON array of eval log entries  
**Data Exposure Class:** Eval log files containing every task/solver/scorer interaction: model inputs, model outputs, evaluation scores, dataset samples. Log format is JSONL under `./logs/` directory. Exposed `inspect view` reveals full benchmark results including dataset contents.  
**Known CVEs:** None specific. Framework created by UK AI Security Institute (AISI) / Meridian Labs; no CVE history.  
**Default Credentials:** None  
**Notes:** Port 7575 is the hard default but is not a well-known shared port — lower FP risk than 8000/8080. `inspect view bundle` creates static HTML export; those bundles may be served via nginx or S3. The `INSPECT_LOG_DIR` env var controls log path; `INSPECT_PY_LOGGER_FORMAT=json` produces machine-parseable output. External host binding is the required precondition for Shodan indexing — treat any port-7575 hit as a likely genuine Inspect AI instance.

---

## HELM (Stanford CRFM — Holistic Evaluation of Language Models)

**Category:** LLM Benchmark / Evaluation Framework  
**Default Ports:** 8000 (helm-server, Flask/Gunicorn); some configurations use 8080  
**Auth Default:** off — `helm-server` is a read-only static result viewer with no authentication  
**Shodan Dork (primary):** `port:8000 http.html:"HELM" http.html:"scenarios"`  
**Shodan Dork (secondary):** `http.title:"HELM" port:8000`  
**Verification Probe:** `GET /` → 200 + HTML with HELM leaderboard; `GET /api/runs` → JSON array with `run_spec` + `stats` fields  
**Data Exposure Class:** Benchmark evaluation results (model scores across scenarios), full prompt/response logs per run, model comparison tables. Eval results may include proprietary model outputs submitted by organizations under NDA.  
**Known CVEs:** None specific.  
**Default Credentials:** None  
**Notes:** `helm-server` is intended for local inspection; internet exposure is atypical. Port 8000 is heavily shared — FP risk HIGH on port alone. The `scenarios` path and HELM-specific result JSON structure (fields: `run_spec`, `stats`, `adapter_spec`) are the distinguishing signals. `helm-summarize` must run before `helm-server` has data. Population expected very low.

---

## PromptBench (Microsoft Research)

**Category:** LLM Robustness Evaluation Library  
**Default Ports:** N/A — Python library only, no HTTP server mode  
**Auth Default:** N/A  
**Shodan Dork (primary):** N/A  
**Shodan Dork (secondary):** N/A  
**Verification Probe:** N/A  
**Data Exposure Class:** No network surface. Indirect: result files or Jupyter notebooks containing evaluation outputs may be accessible via exposed Jupyter (port 8888) or served as static assets.  
**Known CVEs:** None specific.  
**Default Credentials:** N/A  
**Notes:** Microsoft archived the primary promptbench repo. No HTTP server component confirmed. Population = 0 expected on Shodan as a standalone service. If encountered, it will be inside an exposed Jupyter notebook environment — pivot to the Jupyter fingerprint instead.

---

## PyRIT (Microsoft — Python Risk Identification Tool)

**Category:** LLM Red-Team Automation Framework  
**Default Ports:** N/A — Python library / CLI, no built-in HTTP server. AI Red Teaming Playground Labs uses port 5000.  
**Auth Default:** N/A (library); Playground Labs: token-based (`/login?auth=<AUTH_KEY>`)  
**Shodan Dork (primary):** N/A for standalone PyRIT  
**Shodan Dork (secondary):** `port:5000 http.html:"pyrit" http.html:"auth"`  
**Verification Probe:** N/A for standalone; Playground: `GET /login` → redirect to auth page  
**Data Exposure Class:** No persistent HTTP server in production use. PyRIT stores attack results in a local SQLite database (`pyrit_results.db`). Indirect exposure: leaked SQLite files or Jupyter notebook outputs.  
**Known CVEs:** None specific.  
**Default Credentials:** N/A  
**Notes:** PyRIT targets `HTTPTarget` endpoints — it is not itself a server. The AI Red Teaming Playground Labs environment uses Flask on port 5000 with token auth. `pyrit_results.db` is the artifact to hunt if exposed object storage is in scope. Population = 0 expected for standalone PyRIT on Shodan.

---

## OpenAI Evals (openai/evals)

**Category:** LLM Benchmark / Evaluation Framework  
**Default Ports:** N/A — CLI-only tool (`oaieval` command), no HTTP server mode  
**Auth Default:** N/A  
**Shodan Dork (primary):** N/A  
**Shodan Dork (secondary):** N/A  
**Verification Probe:** N/A  
**Data Exposure Class:** No network surface for the OSS framework. OpenAI's hosted evals product (evals.openai.com) is SaaS — not self-hosted. Eval result files (JSONL) may land in accessible storage.  
**Known CVEs:** None specific.  
**Default Credentials:** N/A  
**Notes:** OpenAI deprecated the self-hosted evals workflow and now recommends the Evals API. The open-source `openai/evals` repo is a CLI runner. Population = 0 expected on Shodan. Pivot: look for `oaieval` result JSONL files in exposed S3 buckets or web directories — `http.html:"oaieval"` or `http.html:"eval_results"` combined with `http.html:"openai"`.

---

## LlamaRisk

**Category:** NOT an LLM red-team tool — DeFi risk analysis organization  
**Default Ports:** N/A  
**Auth Default:** N/A  
**Shodan Dork (primary):** N/A  
**Shodan Dork (secondary):** N/A  
**Verification Probe:** N/A  
**Data Exposure Class:** N/A  
**Known CVEs:** N/A  
**Default Credentials:** N/A  
**Notes:** LlamaRisk (github.com/llama-risk) is an independent DeFi risk analysis team focused on Aave, Curve, and LlamaLend protocols. Not related to LLM red-teaming or llama.cpp. No AI infrastructure surface. REMOVE from AI eval/red-team category scope; the name collision with llama.cpp is a false association.

---

## Arthur Shield

**Category:** LLM Safety Firewall / Self-Hosted Monitoring  
**Default Ports:** No fixed default; Kubernetes deployment via DNS hostname routing (e.g., `shield.mycompany.com`); API interactive docs at `<hostname>/docs`  
**Auth Default:** on — API key required (`access_token` in auth header); Shield API key is a required Kubernetes secret at deployment  
**Shodan Dork (primary):** `http.html:"arthur" http.html:"shield" http.html:"validate_prompt"`  
**Shodan Dork (secondary):** `http.html:"/api/v2/task" http.html:"arthur"`  
**Verification Probe:** `GET /docs` → 200 + Swagger UI with `/api/v2/task/{task_id}/validate_prompt` route listed  
**Data Exposure Class:** If auth misconfigured: task configurations, rule settings (PII/hallucination/injection detection config), `inference_id` linkages, `rule_results` arrays showing which safety rules passed/failed, retrieved context from hallucination checks  
**Known CVEs:** None public.  
**Default Credentials:** None (requires explicit secret creation at deploy time)  
**Notes:** Arthur Shield requires Kubernetes 1.31, PostgreSQL with pgvector, and Azure OpenAI GPT-3.5 Turbo — heavyweight dependency chain that limits casual self-hosting. Admin console password and Shield API key are provisioned at deployment; no hardcoded defaults documented. Kubernetes deployment model means this rarely lands on raw VPS IPs — look for it behind TLS with company-specific CNs. `/api/v2/task` and `validate_prompt`/`validate_response` are the unique path signals. `http.html:"/api/v2/task"` is the best body fingerprint.

---

## Patronus AI

**Category:** LLM Evaluation + Guardrails Platform  
**Default Ports:** 8000 (local/POC API, FastAPI); Kubernetes production uses DNS routing at `model-proxy-api.internal.patronus.ai`  
**Auth Default:** on — `vouch-proxy` OIDC/OAuth2 in production; username/password for POC environments  
**Shodan Dork (primary):** `http.html:"patronus" http.html:"/evaluate"`  
**Shodan Dork (secondary):** `http.html:"/v1/" http.html:"patronus"`  
**Verification Probe:** `GET /v1/evaluate` → 200 or 401 + `{"detail": "..."}` JSON; Swagger at `/docs`  
**Data Exposure Class:** If auth misconfigured: evaluation logs with LLM traces, evaluator profiles and prompt templates, dataset contents, account/org metadata, Redis cache state  
**Known CVEs:** None public.  
**Default Credentials:** POC: username/password provisioned at install (no documented defaults)  
**Notes:** Patronus runs on Kubernetes with PostgreSQL (eval logs), Redis (caching), and telemetry stack. Public API routes use `/v1/...` prefix. Self-hosted is enterprise-only — not self-served from Docker Hub. Expected population density low. The `vouch-proxy` OIDC integration is the production auth layer; POC deployments with basic auth are the misconfiguration risk. `patronus-mcp-server` on GitHub indicates MCP exposure surface as a separate vector.

---

## TruLens

**Category:** LLM Evaluation + Tracing (Streamlit Dashboard)  
**Default Ports:** 8501 (Streamlit default — `run_dashboard()` uses dynamic port selection but Streamlit falls back to 8501); configurable via `run_dashboard(port=N)`  
**Auth Default:** off — Streamlit dashboard has no authentication; data access controlled only by network reachability  
**Shodan Dork (primary):** `port:8501 http.html:"trulens"`  
**Shodan Dork (secondary):** `http.title:"TruLens" port:8501`  
**Verification Probe:** `GET /` → 200 + Streamlit HTML with `trulens` in body; leaderboard shows application version names, aggregate feedback scores  
**Data Exposure Class:** Full LLM eval traces (inputs/outputs per app call), feedback scores (faithfulness, relevancy, groundedness), leaderboard across all application versions, `trulens_feedback` clickable pills revealing raw evaluator outputs, SQLite database (`default.sqlite`) accessible if `TruSession()` uses local path  
**Known CVEs:** None specific to TruLens; inherits Streamlit exposure class (see survey 19).  
**Default Credentials:** None  
**Notes:** TruLens uses Streamlit as its dashboard renderer — all Streamlit generic fingerprints apply. The distinguishing signal is `trulens` in the page body alongside Streamlit's standard HTML structure. Port 8501 is shared with all Streamlit deployments; body conjunction is required. SPCS mode uses OAuth token from mounted Docker container — production Snowflake deployments are auth-gated. Local/research deployments on raw VPS are the exposure class. `default.sqlite` is the default backing store — if the host has exposed file listing, this file contains the complete eval history.

---

## RAGAS

**Category:** RAG Evaluation Framework (Python library)  
**Default Ports:** N/A — Python library, no built-in HTTP server. Cloud dashboard at app.ragas.io is SaaS.  
**Auth Default:** N/A (library); app.ragas.io cloud: API key auth  
**Shodan Dork (primary):** N/A  
**Shodan Dork (secondary):** N/A  
**Verification Probe:** N/A  
**Data Exposure Class:** No standalone network surface. RAGAS outputs evaluation scores (context_precision, faithfulness, answer_relevancy, context_recall) as Python objects or DataFrames. Indirect: if eval results are exported to a shared notebook or pushed to an exposed Langfuse/LangSmith endpoint, the data is accessible via those platforms' fingerprints instead.  
**Known CVEs:** None specific.  
**Default Credentials:** N/A  
**Notes:** RAGAS is a pip-installable library (`pip install ragas`). Primary LLM backend is OpenAI GPT-4 by default. No HTTP server shipped. Population = 0 on Shodan as standalone. RAGAS results commonly flow into LangSmith or Langfuse for visualization — fingerprint those platforms to find RAGAS-generated eval data indirectly. The `context_precision` and `faithfulness` field names are unique RAGAS metric identifiers; search these in exposed LangSmith/Langfuse trace bodies.

---

## Summary: Auth Posture Matrix

| Platform | Has HTTP Server | Auth Default | Shodan Population (prior pass) |
|---|---|---|---|
| Promptfoo | Yes (port 15500 + 3000) | off | 22 confirmed |
| DeepEval/Confident AI | Enterprise only | on (API key) | near-zero |
| LangSmith self-hosted | Yes (port 1980/1984) | off (pre-v0.10) | 96 confirmed |
| Garak | No | N/A | 0 |
| Inspect AI | Yes (port 7575) | off | unknown — not in prior pass |
| HELM | Yes (port 8000) | off | near-zero |
| PromptBench | No | N/A | 0 |
| PyRIT | No (Playground: 5000) | N/A / token | 0 |
| OpenAI Evals | No | N/A | 0 |
| LlamaRisk | N/A (not AI eval) | N/A | N/A |
| Arthur Shield | Yes (K8s DNS) | on | near-zero |
| Patronus AI | Yes (port 8000 POC) | on | near-zero |
| TruLens | Yes (port 8501) | off | unknown — not in prior pass |
| RAGAS | No | N/A | 0 |

**Primary targets for Shodan harvest (HTTP server + auth off):** Promptfoo, LangSmith (pre-v0.10), Inspect AI, HELM, TruLens
