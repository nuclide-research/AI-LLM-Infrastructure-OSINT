# Georgia State University: Streamlit app on `gluon.gsu.edu:8501` (framework confirmed; app content WebSocket-only)

_NuClide Research · 2026-05-19_

---

## Summary

Georgia State University runs a Streamlit application at `gluon.gsu.edu` (131.96.55.92:8501). The Streamlit framework is confirmed via `/_stcore/health` returning `ok`. The application title is the Streamlit default (`<title>Streamlit</title>` in the rendered HTML — no customization). Actual application content is served over Streamlit's WebSocket data channel; static probes cannot enumerate the app's purpose without establishing an interactive session.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 131.96.55.92 |
| rDNS | `gluon.gsu.edu` |
| Org | Georgia State University |
| Hostname semantics | `gluon` — particle-physics naming convention; suggests faculty/lab compute host |
| Open port observed | 8501 (Streamlit default port) |

---

## Observations

`GET http://gluon.gsu.edu:8501/_stcore/health` → 200 with body `ok` (Streamlit-framework canonical health endpoint).
`GET http://gluon.gsu.edu:8501/_stcore/host-config` → 200 with `allowedOrigins` configuration disclosed (lists Streamlit Cloud's domains as allowed CORS origins — default config, no customization).
`GET http://gluon.gsu.edu:8501/` → 200 with 1,522 bytes of HTML — Streamlit's React shell, no per-app content rendered until WebSocket connects.
HTML `<title>` tag value: `Streamlit` (default — no app-level title customization).

**Class memberships observed:**
- Streamlit framework class — CONFIRMED via `/_stcore/health` response
- Default title class — OBSERVED (operator did not customize via `st.set_page_config(page_title=...)`)
- Standard host-config endpoint accessible — OBSERVED (no customization to CORS / origin policy)

### What was NOT done per restraint ethic

- Did NOT connect to the WebSocket at `/_stcore/stream` (would establish a Streamlit session, triggering operator-visible logs and consuming server resources)
- Did NOT enumerate the JS bundle (`/static/js/index.CD8HuT3N.js`) for embedded app strings
- Did NOT attempt any application-specific paths

Without WebSocket session establishment OR JS bundle string-extraction, the application's actual purpose (data dashboard, ML demo, LLM chat, course interactive, internal tool, etc.) is not externally enumerable.

---

## Class-membership summary (no tier labels per survey convention)

- Streamlit framework deployment on .edu network — OBSERVED
- App content WebSocket-only / not passively enumerable — class-membership consequence
- Auth state UNKNOWN — Streamlit doesn't enforce auth at the framework level; per-app auth (`st.session_state` checks, OAuth wrappers, etc.) is implementation-dependent and cannot be tested without interactive probe

---

## Discovery method

- **Initial surfacing**: Stage-0 dork-map of 1,629 verified Shodan dorks — `gluon.gsu.edu:8501` matched the Streamlit port + framework dork.
- **Verification**: framework-class confirmation via `/_stcore/health`; app-level content / auth state remain unverified by passive probe.

---

## Source artifacts

- Workspace: `~/recon/edu-llm-infra-2026-05-19/stage2-wave2/`
- Direct probe: `wave2-streamlit-and-stragglers-deep.json` (GSU-gluon section)
- aimap wave-2: `aimap-wave2.json`

---

## Note — Streamlit observation discipline

This case study documents what CAN and CANNOT be determined about a Streamlit deployment from external passive probe. The Streamlit framework's WebSocket-first architecture means most app-specific data (page title, sidebar content, displayed widgets, model inventory if it's an LLM app) is not visible until a session is established. Per restraint ethic this survey does not establish sessions; the case study documents framework-class observations only.

GSU's `gluon.gsu.edu` joins the wave-2 Streamlit cohort (Stanford, UW, UChicago) all in this same observation state. A targeted follow-up could:
1. Download the JS bundle (`/static/js/*.js`) and grep for strings indicating app purpose
2. Look at the host's `host-config` for any non-default CORS/origin allowances suggesting external embedding intent
3. Use Streamlit's WebSocket protocol with read-only intent to enumerate widget structure without triggering user actions

None of these are necessary for the survey's class-membership documentation purpose.
