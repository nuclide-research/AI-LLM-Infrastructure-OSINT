# University of Washington: Streamlit app on `D4-084.ce.washington.edu:8501` (Civil Engineering dept; framework confirmed)

_NuClide Research · 2026-05-19_

---

## Summary

University of Washington's Civil Engineering department surfaces a Streamlit application at `D4-084.ce.washington.edu` (128.95.204.84:8501). Streamlit framework confirmed via `/_stcore/health` returning `ok`. Hostname pattern (`D4-084`) suggests a numbered lab compute host in the CE department. App-level title is the Streamlit default; per restraint ethic, the WebSocket session that would reveal app content was not established.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 128.95.204.84 |
| rDNS | `D4-084.ce.washington.edu` |
| Org | University of Washington (`128.95.0.0/16` UW allocation) |
| Department | Civil Engineering (`ce.washington.edu` subdomain) |
| Hostname semantics | `D4-084` — numbered lab compute pattern (likely "Drumheller Annex 4" or similar building-numbered room-identifier; common in CE/engineering buildings at UW) |
| Open port observed | 8501 (Streamlit default port) |

---

## Observations

`GET http://D4-084.ce.washington.edu:8501/_stcore/health` → 200 with body `ok`.
`GET .../` → 200 with 891 bytes of HTML — Streamlit React shell (smaller bundle than GSU/Stanford, possibly older Streamlit version).
HTML `<title>` tag: `Streamlit` (default — no app-level customization).
JS bundle: `/static/js/main.d55f6a3c.js` (older `main.*.js` naming convention vs the `index.*.js` pattern at Stanford/GSU — indicates an older Streamlit version).

**Class memberships observed:**
- Streamlit framework on UW Civil Engineering subnet — OBSERVED
- Default title — OBSERVED
- Older Streamlit version (smaller HTML shell, `main.*.js` vs `index.*.js` naming) — OBSERVED

### What was NOT done per restraint ethic

- Did NOT connect to the WebSocket at `/_stcore/stream`
- Did NOT enumerate JS bundle for embedded app strings
- Did NOT probe application-specific paths

---

## Class-membership summary (no tier labels per survey convention)

- Streamlit framework deployment on UW Civil Engineering subnet — OBSERVED
- Older Streamlit version class — OBSERVED (`main.*.js` bundle naming convention)
- App content WebSocket-only / not passively enumerable — class consequence
- Auth state UNKNOWN

---

## Discovery method

- **Initial surfacing**: Stage-0 dork-map of 1,629 verified Shodan dorks — host matched the Streamlit port + framework dork.
- **Verification**: framework confirmation via `/_stcore/health`.

---

## Source artifacts

- Workspace: `~/recon/edu-llm-infra-2026-05-19/stage2-wave2/`
- Direct probe: `wave2-streamlit-and-stragglers-deep.json` (UW-Streamlit section)
- aimap wave-2: `aimap-wave2.json`

---

## Cohort note

UW joins the wave-2 Streamlit cohort (GSU, Stanford, UChicago) — see `GA-georgia-state.md` for the survey's Streamlit-observation discipline note. UW's older bundle naming (`main.*.js`) and smaller HTML shell (891 bytes vs 1,522 at GSU/Stanford) suggest an older Streamlit version; worth a follow-up if dating the deployment becomes relevant.
