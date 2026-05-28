# Code Assistants — Shodan Query Catalog
_Generated: 2026-05-27 from pre-survey OSINT pass (14 platforms)_
_See: data/platform-intel/code-assistants-osint-2026-05-27.md for full intel_

---

## Tabby (TabbyML)
**Auth default:** off (auth is optional; no token required in community edition)
**Exposure class:** Code completion endpoint, model identity, server config, running model list — all accessible without credentials

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `http.html:"tabbyml" port:8080` | "tabbyml" appears in bundled JS asset paths and meta tags | Low |
| secondary | `port:8080 http.html:"tabby" http.html:"/v1/completions"` | Combined signal: Tabby JS tag + completion path string in HTML | Low |
| swagger | `port:8080 http.html:"swagger-ui" http.html:"tabby"` | Swagger UI always present; combined with tabby body string | Med |
| identity-probe | `GET /v1/health` → `{"device":..., "model":..., "chat_model":...}` | `chat_model` + `device` fields in health response are Tabby-specific | — |

**FP note:** Port 8080 is heavily shared. Never run `port:8080` alone. The `tabbyml` string is the safest primary signal — appears in static asset paths.

---

## Sourcegraph / Cody
**Auth default:** on (built-in auth; free-license instances promote all users to site-admin)
**Exposure class:** On free/misconfigured instances: full code search index, connected repo credentials, Cody conversation history

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `http.title:"Sourcegraph" port:7080` | Title is application-set; port 7080 is Sourcegraph default | Low |
| secondary | `port:7080 http.html:"sourcegraph-frontend"` | `sourcegraph-frontend` bundle name in HTML source | Low |
| alt-port | `http.title:"Sourcegraph" port:3080` | Older deployments used 3080 | Low |
| identity-probe | `GET /` → HTML with `sourcegraph-frontend` script bundle or `data-sourcegraph-app-version` meta attribute | Confirms Sourcegraph; version extraction possible | — |

**FP note:** The title "Sourcegraph" is application-specific; collision risk is negligible. Port 7080 is not commonly used by other services.

---

## Continue.dev
**Auth default:** N/A — IDE extension only, no server component
**Exposure class:** N/A — exposure belongs to configured backend (Ollama, vLLM, etc.)

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| — | Not applicable | Continue.dev has no standalone server | — |

**FP note:** No Shodan queries. Survey the backend model servers via Ollama/llama.cpp/vLLM surveys.

---

## Refact.ai (self-hosted)
**Auth default:** off initially; community edition accepts any API key value
**Exposure class:** Model capability list, completion and chat endpoints, running model configuration

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:8008 http.html:"refact"` | "refact" appears in the web UI source | Med |
| secondary | `port:8008 http.html:"coding_assistant_caps"` | `coding_assistant_caps` is a Refact-specific endpoint name appearing in JS source | Low |
| caps-path | `port:8008 http.html:"refact-caps"` | `/refact-caps` path string in UI or JS bundle | Low |
| identity-probe | `GET /refact-caps` → `{"code_completion_models":..., "caps_version":..., "cloud_name":...}` | `code_completion_models` + `caps_version` fields are Refact-specific | — |

**FP note:** Port 8008 is shared with some JupyterHub and other services. The `coding_assistant_caps` body string is the strongest low-FP signal.

---

## Aider (browser mode)
**Auth default:** off (Streamlit has no authentication by default)
**Exposure class:** Full terminal/IDE session, git repo content, LLM API keys in environment, conversation history

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:8501 http.html:"aider" http.html:"streamlit"` | Aider Streamlit UI contains "aider" in page content + Streamlit framework identifier | Low |
| secondary | `port:8501 http.html:"AI pair programming"` | Aider's own tagline present in the browser UI | Low |
| identity-probe | `GET /` → 200 + Streamlit HTML with "aider" in title or body text | Confirms Aider Streamlit instance | — |

**FP note:** Port 8501 is Streamlit's default — many non-Aider apps use it. Body string conjunct is mandatory. Population likely small; Aider is primarily a CLI tool.

---

## code-server (Coder)
**Auth default:** on by default (auto-generated password); `auth: none` config option disables all auth — common misconfiguration
**Exposure class:** When `auth: none`: full VS Code IDE, integrated terminal (root shell on container), filesystem, extension install; when password-protected: hash-as-cookie bypass (issue #7696) possible if config file is readable

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `http.html:"code-server" port:8080` | "code-server" appears in page title and HTML | Med |
| secondary | `port:8080 http.html:"coder-options"` | `<meta id="coder-options">` is unique to code-server login page | Low |
| no-auth | `port:8080 http.html:"coder-options" -http.html:"password"` | Login page without password form = `auth: none` = fully open | Low |
| identity-probe | `GET /` → HTML with `<meta id="coder-options"` and `name="password"` input | Confirms code-server; absence of password field = auth disabled | — |

**FP note:** Port 8080 is heavily shared. The `coder-options` meta element is the strongest discriminating signal. Linuxserver.io Docker images use port 8443 as the default — add `port:8443` variant.

---

## OpenDevin / All-Hands OpenHands
**Auth default:** off
**Exposure class:** Full agent execution environment — see category-09 survey

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| — | See category-09 survey | Covered in prior survey | — |

**FP note:** Covered in cat-09. CVE-2026-34444 (lupa sandbox escape) and WebSocket auth bypass are load-bearing for this platform.

---

## SWE-agent
**Auth default:** off (no authentication on web UI or Flask backend)
**Exposure class:** GitHub PAT submitted to agent, repository content, LLM API keys, full agent execution log

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:3000 http.html:"SWE-agent"` | "SWE-agent" in page HTML | Low |
| secondary | `port:8000 http.html:"swe-agent"` | Flask backend port with body string | Low |
| identity-probe | `GET /` on port 3000 → HTML with "SWE-agent" title; `GET /socket.io/?EIO=4&transport=polling` → socket.io handshake | socket.io endpoint confirms SWE-agent backend | — |

**FP note:** Port 3000 is heavily polluted. Body string conjunct required. Population expected to be very small — SWE-agent is primarily a research tool not typically left running.

---

## Cursor
**Auth default:** N/A — desktop application, no server
**Exposure class:** N/A

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| — | Not applicable | Desktop app only; no self-hosted server component | — |

---

## GitHub Copilot Enterprise / GHES
**Auth default:** on (GitHub OAuth enforced; Copilot itself has no unauthenticated path)
**Exposure class:** Misconfigured GHES: code repos, issues, PRs, user data; CVE-2024-9487 SAML bypass enables auth bypass on affected versions

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `http.title:"GitHub Enterprise" port:443` | GHES serves this title on the front page | Low |
| secondary | `ssl.cert.subject.cn:"github" port:443 -http.title:"GitHub"` | Self-signed certs on internal GHES with "github" in CN | Med |
| saml-bypass | `http.title:"GitHub Enterprise" http.html:"saml"` | SAML-enabled GHES instances (CVE-2024-9487 surface) | Low |
| identity-probe | `GET /api/v3/` → `{"current_user_url":..., "hub":...}` | GitHub Enterprise REST API root — confirms GHES | — |

**FP note:** GitHub.com itself will match `http.title:"GitHub"` — use `port:443 -http.title:"GitHub"` to exclude. `http.title:"GitHub Enterprise"` is specific to GHES deployments.

---

## Codeium Enterprise (Windsurf Enterprise)
**Auth default:** on (SSO / SAML 2.0 enforced; no unauthenticated paths)
**Exposure class:** Auth-gated; no known unauthenticated exposure class; the `/_route/` path pattern identifies the deployment

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `ssl.cert.subject.cn:"codeium" port:443` | Enterprise deployments use certs with "codeium" in CN | Low |
| secondary | `http.html:"/_route/api_server" port:443` | Client-configured enterprise endpoint path appears in HTML/JS | Low |
| identity-probe | `GET /_route/api_server/` → TLS-gated proprietary JSON | `/_route/` path prefix is Codeium-specific | — |

**FP note:** Population will be small (enterprise-only licensed product). Auth is enforced. These dorks identify the deployment for version/attribution purposes, not unauthenticated access.

---

## FauxPilot
**Auth default:** off (dummy API key `"dummy"` accepted; no real auth mechanism)
**Exposure class:** Full code completion access, submitted code context, Triton model identity, GPU metrics on port 8002

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:5000 http.html:"codegen"` | "codegen" in HTML/response body of FauxPilot proxy | Med |
| secondary | `port:5000 http.html:"fauxpilot"` | "fauxpilot" in page source or error responses | Low |
| triton | `port:8000 http.html:"fauxpilot"` | Triton HTTP port co-located with FauxPilot | Low |
| metrics | `port:8002 http.html:"nv_inference"` | Triton metrics endpoint exposes `nv_inference_*` Prometheus metrics | Low |
| identity-probe | `POST /v1/engines/codegen/completions` with `Authorization: Bearer dummy` → `{"object":"text_completion","model":"codegen-..."}` | `/v1/engines/codegen/` path + dummy key acceptance confirms FauxPilot | — |

**FP note:** Port 5000 is heavily used (Flask default, AirPlay on macOS, etc.). The `engines/codegen` path is the strongest discriminating signal. Project is in maintenance mode; wild instances will be old deployments.

---

## WizardCoder / CodeLlama via llama.cpp
**Auth default:** off
**Exposure class:** See llama.cpp / model-serving survey

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| model-filter | `port:8080 http.html:"llama.cpp" http.html:"codellama"` | llama.cpp server with CodeLlama model loaded | Low |
| model-filter-2 | `port:8080 http.html:"llama.cpp" http.html:"wizardcoder"` | llama.cpp server with WizardCoder model | Low |

**FP note:** These are sub-queries against the llama.cpp population, not standalone platform dorks. Run against existing llama.cpp survey results.

---

## JetBrains AI Service
**Auth default:** on (JWT/Bearer token required; no unauthenticated paths in official product)
**Exposure class:** Auth-gated; community proxy deployments may expose OpenAI-compatible endpoint

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| proxy | `port:8080 http.html:"jetbrains-ai"` | Community jetbrains-ai-proxy projects may expose this string | Med |
| identity-probe | `GET /v1/models` → OpenAI-format model list (if community proxy) | Confirms OpenAI-compatible proxy frontend | — |

**FP note:** No standard self-hosted JetBrains AI server fingerprint exists. Official Mellum on-prem is enterprise-licensed and not publicly accessible. These dorks target community proxy instances only.
