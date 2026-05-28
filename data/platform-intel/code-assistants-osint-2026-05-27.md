# Code Assistant Platform OSINT — Pre-Survey Intelligence
**Date:** 2026-05-27  
**Purpose:** Tune dork queries, understand auth posture, identify verification probes, document data exposure classes before Shodan harvests.  
**Scope:** 14 platforms — self-hosted coding assistants, code completion, AI pair programming.  
**Status:** Pre-survey. No active probing conducted.

---

## Tabby (TabbyML)

**Category:** Code Completion / Code Chat  
**Default Ports:** 8080  
**Auth Default:** off (authentication is optional; no token required by default in community edition)  
**Shodan Dork (primary):** `http.html:"tabbyml" port:8080`  
**Shodan Dork (secondary):** `port:8080 http.html:"/swagger-ui" http.html:"completions" http.html:"tabby"`  
**Verification Probe:** `GET /v1/health` → 200 + `{"device":..., "model":..., "chat_model":...}` — the `chat_model` field and `device` field together are Tabby-specific; the field `mode` in `/v1/completions` responses (`"standard"` or `"next_edit_suggestion"`) does not appear in generic OpenAI endpoints  
**Data Exposure Class:** Code completion suggestions (implying codebase context submitted by IDE), model identity, server config via `/v1beta/server_setting`, running model list via `/v1beta/models`  
**Known CVEs:** No CVEs on record as of 2026-05-27. GitHub issue #321 (2022) raised lack of auth as enhancement request — the feature shipped as optional, not mandatory.  
**Default Credentials:** none  
**Notes:** Auth is bolted on via per-user API tokens generated in the admin dashboard. Instances shipped without configuring a token are fully open. `/swagger-ui` is always available and exposes the full API surface. The `debug_data` field in completion responses is Tabby-specific. FP risk on port 8080 is high — use `tabbyml` or `tabby` HTML body string as conjunct.

---

## Sourcegraph / Cody

**Category:** Code Search / Code Chat  
**Default Ports:** 7080 (HTTP), 7443 (HTTPS, if TLS configured)  
**Auth Default:** on (built-in username/password; first user registers as admin; free-license instances make every user a site-admin)  
**Shodan Dork (primary):** `http.title:"Sourcegraph" port:7080`  
**Shodan Dork (secondary):** `port:7080 http.html:"sourcegraph-frontend"`  
**Verification Probe:** `GET /` → 200 + HTML containing `sourcegraph-frontend` script bundle or `data-sourcegraph-app-version` meta tag  
**Data Exposure Class:** On free-license instances, all registered users are site-admins — full code repository index, search history, Cody AI conversation logs, connected code host credentials if configured  
**Known CVEs:** No Sourcegraph-specific CVEs matched code-assistant category in search. Dependency CVEs exist in older versions.  
**Default Credentials:** none (first-run registration sets admin password; no hardcoded creds)  
**Notes:** The Cody AI component routes completions through Sourcegraph's cloud gateway by default in enterprise mode, potentially leaking code context to the SaaS tier even when "self-hosted." The `allowSignup: true` config flag is required for public registration; it defaults to false. FP risk on `http.title:"Sourcegraph"` is low — the title is application-set. Port 3080 appears in some older deployments.

---

## Continue.dev

**Category:** Code Completion / Code Chat (VS Code / JetBrains extension)  
**Default Ports:** N/A — Continue.dev is a pure IDE extension. It proxies requests from the IDE to a configured backend (Ollama, LM Studio, vLLM, etc.). No standalone HTTP server.  
**Auth Default:** N/A  
**Shodan Dork (primary):** N/A  
**Shodan Dork (secondary):** N/A  
**Verification Probe:** N/A  
**Data Exposure Class:** N/A — code context is sent to whatever backend is configured; the exposure class belongs to the backend (Ollama, vLLM, etc.), not Continue itself  
**Known CVEs:** none specific  
**Default Credentials:** N/A  
**Notes:** Not a Shodan target. Continue.dev's network footprint is the backend model server it points to. Those backends (Ollama, llama.cpp, vLLM) are covered in other surveys. The Continue config file `~/.continue/config.json` stored locally may contain hardcoded API keys — a client-side secret exposure risk, not a server exposure.

---

## Refact.ai (self-hosted)

**Category:** Code Completion / Code Chat / Agent  
**Default Ports:** 8008  
**Auth Default:** off initially, then first-run registration makes the registering user admin (similar to Sourcegraph model, but the API accepts any key value for local clients in community edition)  
**Shodan Dork (primary):** `port:8008 http.html:"refact"`  
**Shodan Dork (secondary):** `port:8008 http.html:"coding_assistant_caps"`  
**Verification Probe:** `GET /refact-caps` → 200 + JSON with `code_completion_models`, `code_chat_models`, `cloud_name` fields — these field names are Refact-specific  
**Data Exposure Class:** Model capability list, endpoint templates, running model names; completion endpoints accessible with any API key value in community edition  
**Known CVEs:** none specific  
**Default Credentials:** none (first-user-registers-as-admin model)  
**Notes:** The `/refact-caps` and legacy `/coding_assistant_caps.json` endpoints are the strongest fingerprint — the field names `code_completion_default_model`, `endpoint_template`, and `caps_version` do not appear in any other AI service. Refact-lsp (the IDE-side daemon) also exposes a local HTTP port for IDE communication, but that is localhost-only. Port 8008 collision with other services (some JupyterHub configs) is possible — use body string conjunct.

---

## Aider

**Category:** CLI Code Agent  
**Default Ports:** 8501 (when launched with `--browser` flag, runs Streamlit UI)  
**Auth Default:** off (Streamlit UI has no authentication by default)  
**Shodan Dork (primary):** `port:8501 http.html:"aider" http.html:"streamlit"`  
**Shodan Dork (secondary):** `port:8501 http.html:"AI pair programming"`  
**Verification Probe:** `GET /` → Streamlit app with "aider" in title or body  
**Data Exposure Class:** Full terminal session, git repo being edited, LLM conversation history, any secrets present in the working directory  
**Known CVEs:** none specific for aider browser mode  
**Default Credentials:** none  
**Notes:** Aider is primarily a CLI tool. The `--browser` flag launches a Streamlit frontend on port 8501 with no authentication. Instances exposed to the internet give full code editor access to unauthenticated users. Population is likely small — Streamlit port 8501 is noisy (other Streamlit apps share the port), so the body conjunct `"aider"` is essential. A third-party wrapper project `aider-webui` uses NiceGUI on a different port. The official Gradio-based browser mode (older versions) used port 7860.

---

## code-server (Coder)

**Category:** Web IDE (VS Code in browser)  
**Default Ports:** 8080  
**Auth Default:** on (password required; auto-generated on first run, stored in `~/.config/code-server/config.yaml`)  
**Shodan Dork (primary):** `http.html:"code-server" port:8080`  
**Shodan Dork (secondary):** `port:8080 http.html:"coder-options"`  
**Verification Probe:** `GET /` → 200 + HTML containing `<meta id="coder-options"` and password form with `name="password"` — distinctive combination  
**Data Exposure Class:** Full VS Code IDE, terminal access to the underlying server, filesystem browser, extension installation; if password is weak or leaked via config file, complete server compromise  
**Known CVEs:** Issue #7696 (2026-03) — hashed password value from config.yaml can be used directly as a session cookie, bypassing auth without knowing the plaintext password  
**Default Credentials:** auto-generated random password (no default hardcoded value; but instances misconfigured with `auth: none` are fully open)  
**Notes:** The `<meta id="coder-options">` element is highly distinctive and unlikely to appear in non-code-server apps. The `auth: none` config option disables all password requirements — users set this to avoid entering passwords and expose full IDE to the network. The password hash-as-cookie issue (#7696) means config file exfiltration (via path traversal or Docker volume leak) directly yields auth bypass.

---

## OpenDevin / All-Hands OpenHands

**Category:** Dev Agent (Covered in Category 09)  
**Default Ports:** 3000  
**Auth Default:** off  
**Shodan Dork (primary):** See category-09 survey  
**Shodan Dork (secondary):** See category-09 survey  
**Verification Probe:** See category-09 survey  
**Data Exposure Class:** Full agent execution environment, code repos, LLM conversation history  
**Known CVEs:** CVE-2026-34444 (lupa ≤2.7 sandbox escape); first-message WebSocket auth bypass patched in recent release  
**Default Credentials:** none  
**Notes:** Covered in cat-09 survey. Noted here for completeness. The CVE-2026-34444 lupa sandbox escape is significant — it allows code execution outside the Docker sandbox.

---

## SWE-agent

**Category:** Dev Agent (automated GitHub issue resolution)  
**Default Ports:** 3000 (frontend), 8000 (Flask backend API)  
**Auth Default:** off (no authentication documented in web UI; experimental feature)  
**Shodan Dork (primary):** `port:3000 http.html:"SWE-agent"`  
**Shodan Dork (secondary):** `port:8000 http.html:"swe-agent" http.html:"socket.io"`  
**Verification Probe:** `GET /` on port 3000 → HTML with "SWE-agent" in title; backend: `GET /socket.io/?EIO=4&transport=polling` → 200 with socket.io handshake  
**Data Exposure Class:** GitHub credentials / tokens submitted to the agent, repository content, LLM API keys configured for agent use  
**Known CVEs:** none specific  
**Default Credentials:** none  
**Notes:** SWE-agent web UI is described as "experimental" in official docs. No authentication. Requires GitHub PAT and LLM API key at runtime — both are visible to anyone with network access to the running instance. Port 3000 is heavily polluted by Node.js/React dev servers; use body string conjunct. Flask backend on port 8000 may be separately accessible.

---

## Cursor

**Category:** AI Code Editor (Desktop Application)  
**Default Ports:** N/A  
**Auth Default:** N/A (desktop app; authenticates to Cursor cloud)  
**Shodan Dork (primary):** N/A  
**Shodan Dork (secondary):** N/A  
**Verification Probe:** N/A  
**Data Exposure Class:** N/A — no server component  
**Known CVEs:** none specific  
**Default Credentials:** N/A  
**Notes:** Not a Shodan target. Cursor is a desktop app (Electron-based VS Code fork). All AI calls route to Cursor's SaaS backend. No self-hosted server component. Enterprise teams deploying Cursor use Cursor's SaaS with enterprise SSO, not a self-hosted server.

---

## GitHub Copilot (Enterprise / GHES)

**Category:** Code Completion (Enterprise SaaS + GitHub Enterprise Server)  
**Default Ports:** 443 (HTTPS, GitHub Enterprise Server); 8080 (various proxy configs)  
**Auth Default:** on (GitHub OAuth / GitHub Enterprise auth; no unauthenticated paths)  
**Shodan Dork (primary):** `http.title:"GitHub Enterprise" port:443`  
**Shodan Dork (secondary):** `ssl.cert.subject.cn:"github" port:443 -site:github.com`  
**Verification Probe:** `GET /api/v3/` → 200 + `{"current_user_url": "https://.../user", "hub": ...}` — GitHub Enterprise REST API root  
**Data Exposure Class:** On misconfigured GHES: code repositories, pull requests, issues, user data; Copilot itself requires per-user seat assignment  
**Known CVEs:** CVE-2024-9487 (GHES SAML auth bypass, CVSS 9.5), CVE-2024-9539 (GHES info disclosure)  
**Default Credentials:** none (admin account created during setup wizard)  
**Notes:** GitHub Copilot itself has no self-hosted server — it runs as a plugin calling GitHub's cloud API. GHES is the closest self-hosted component. GHES instances on port 8080 or non-standard ports sometimes appear without TLS. The Copilot Proxy feature (internal network proxy for GHES) relays Copilot traffic but does not eliminate cloud dependency. FP risk on GHES title dork is low.

---

## Codeium Enterprise (Windsurf Enterprise)

**Category:** Code Completion / Code Chat  
**Default Ports:** 443 (client → server HTTPS), internal GPU inference ports vary  
**Auth Default:** on (SSO / SAML 2.0 enforced for enterprise; no unauthenticated paths documented)  
**Shodan Dork (primary):** `ssl.cert.subject.cn:"codeium" port:443`  
**Shodan Dork (secondary):** `http.html:"/_route/api_server" port:443`  
**Verification Probe:** `GET /_route/api_server/` → TLS + proprietary JSON response; client config path `/_route/` is Codeium-specific  
**Data Exposure Class:** Code context sent for completion, conversation history in Codeium chat; enterprise deployment keeps code on-prem but inference server connectivity is required  
**Known CVEs:** none specific  
**Default Credentials:** none  
**Notes:** Codeium Enterprise is a fully licensed product requiring enterprise onboarding. Auth is enforced. The `/_route/api_server` path pattern in client configuration is the strongest fingerprint for identifying Codeium Enterprise deployments. Self-hosted deployments run GPU inference containers internally; the external-facing surface is the API gateway at port 443 with TLS. Shodan population expected to be very small (enterprise only, licensed).

---

## FauxPilot

**Category:** Code Completion (Copilot protocol emulator)  
**Default Ports:** 5000 (Python proxy API); 8000 (Triton HTTP); 8001 (Triton gRPC); 8002 (Triton metrics)  
**Auth Default:** off (dummy API key accepted; no real authentication)  
**Shodan Dork (primary):** `port:5000 http.html:"codegen" http.html:"fauxpilot"`  
**Shodan Dork (secondary):** `port:5000 "/v1/engines/codegen/completions"`  
**Verification Probe:** `POST /v1/engines/codegen/completions` with dummy key `Authorization: Bearer dummy` → 200 + `{"object": "text_completion", "model": "codegen-..."}` — `engines/codegen` path is FauxPilot-specific  
**Data Exposure Class:** Code completion (implying submitted code context), model identity, Triton metrics on port 8002 (GPU utilization, queue depths, model load state)  
**Known CVEs:** none specific; project appears to be in maintenance mode (last major commit 2023)  
**Default Credentials:** dummy API key `"dummy"` accepted as valid  
**Notes:** Binds on `0.0.0.0:5000` by default — all interfaces. No auth. The Triton metrics port (8002) exposes GPU and inference queue metrics without any authentication and is a secondary fingerprint surface. Port 5000 collides with many services; the `/v1/engines/codegen/` path is the strong signal. Project is largely unmaintained; deployments in the wild will be older versions. Triton on port 8000 may also be accessible independently.

---

## WizardCoder / CodeLlama via llama.cpp

**Category:** Code Completion (via general LLM server)  
**Default Ports:** 8080 (llama.cpp server default)  
**Auth Default:** off  
**Shodan Dork (primary):** See Ollama/llama.cpp survey (covered in Category 01 / 03 surveys)  
**Shodan Dork (secondary):** `port:8080 http.html:"llama.cpp" http.html:"codellama"` or `http.html:"wizardcoder"`  
**Verification Probe:** `GET /v1/models` → 200 + model name containing `codellama` or `wizardcoder`  
**Data Exposure Class:** Same as any exposed llama.cpp instance — full code completion access, model inference  
**Known CVEs:** See llama.cpp survey entries  
**Default Credentials:** none  
**Notes:** WizardCoder and CodeLlama are model weights loaded into llama.cpp, vLLM, Ollama, or similar servers — they are not standalone platforms. Detection is via the serving framework (llama.cpp port 8080 survey, Ollama survey). Noted here for completeness. Not a separate Shodan category — fold into model-serving or Ollama surveys.

---

## JetBrains AI Service (IDE Services / Mellum)

**Category:** Code Completion / Code Chat (IDE-proxied)  
**Default Ports:** No externally-facing port for standard configuration. The JetBrains IDE connects to JetBrains' cloud AI service. For enterprise/on-prem: configurable, typically 443 (via configured OpenAI-compatible endpoint).  
**Auth Default:** on (JWT/Bearer token; JetBrains AI Enterprise requires token configuration)  
**Shodan Dork (primary):** N/A (no standard self-hosted server with a fixed fingerprint)  
**Shodan Dork (secondary):** Community proxy projects (jetbrains-ai-proxy) on port 8080: `port:8080 http.html:"jetbrains-ai"`  
**Verification Probe:** N/A for official product; community proxy: `GET /v1/models` → OpenAI-format response  
**Data Exposure Class:** Code context and conversation history routed through the configured backend  
**Known CVEs:** none specific to JetBrains AI Service  
**Default Credentials:** none (requires JetBrains license + token)  
**Notes:** JetBrains AI Service (JBA) routes completions to JetBrains cloud by default; enterprise customers can configure Mellum on-prem or point to any OpenAI-compatible endpoint. The official on-prem Mellum engine is not publicly released as a standalone server — it requires JetBrains IDE Services enterprise licensing. Community proxy projects (jetbrains-ai-proxy on GitHub) emulate an OpenAI endpoint and accept JetBrains JWT tokens; these are the most likely "self-hosted JetBrains AI" instances visible on Shodan, but they carry the user's own JetBrains credentials and are not a platform exposure in themselves.
