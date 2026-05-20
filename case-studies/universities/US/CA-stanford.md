# Stanford University: Streamlit app on `sr24-0915fd81a9.stanford.edu:8501` (DHCP / dynamic host; framework confirmed)

_NuClide Research · 2026-05-19_

---

## Summary

Stanford University surfaces a Streamlit application at `sr24-0915fd81a9.stanford.edu` (128.12.168.8:8501). Hostname pattern (`sr24-{hex-id}.stanford.edu`) suggests a dynamically-assigned campus subnet host — likely a personal device on Stanford's wireless or residential network. Streamlit framework confirmed via `/_stcore/health` returning `ok`; `<title>Streamlit</title>` default (no app-level customization). Per restraint ethic, the WebSocket session that would reveal app content was not established.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 128.12.168.8 |
| rDNS | `sr24-0915fd81a9.stanford.edu` |
| Org | Stanford University (`128.12.0.0/16` is part of Stanford's institutional allocation; `sr*` hostname prefix consistent with Stanford Residential / SUNet-managed dynamic IPs) |
| Hostname semantics | `sr24` prefix + 10-char hex suffix — suggests "Stanford Residential 24" subnet with DHCP-assigned hex ID; consistent with personal-device/wireless rather than faculty/lab static IP |
| Open port observed | 8501 (Streamlit default port) |

---

## Observations

`GET http://sr24-0915fd81a9.stanford.edu:8501/_stcore/health` → 200 with body `ok` (Streamlit framework canonical health endpoint).
`GET .../` → 200 with 1,522 bytes of HTML — Streamlit React shell.
HTML `<title>` tag: `Streamlit` (default — no app-level customization via `st.set_page_config`).
JS entry bundle: `/static/js/index.CbQtRkVt.js` (different hash from other wave-2 Streamlit deployments — independent build of the same Streamlit framework version).

**Class memberships observed:**
- Streamlit framework on Stanford's dynamic / residential subnet — OBSERVED
- Default title (no `st.set_page_config(page_title=...)` customization) — OBSERVED
- Hostname pattern indicates personal-device/wireless, not faculty/lab — OBSERVED

### What was NOT done per restraint ethic

- Did NOT connect to the WebSocket at `/_stcore/stream`
- Did NOT enumerate the JS bundle for embedded app strings
- Did NOT probe any application-specific paths

---

## Class-membership summary (no tier labels per survey convention)

- Streamlit framework deployment on Stanford .edu wireless/residential network — OBSERVED
- App content WebSocket-only / not passively enumerable — class-membership consequence
- Auth state UNKNOWN — Streamlit doesn't enforce auth at the framework level

---

## Notable details — Stanford `sr*` hostname pattern

The `sr24-{hex}.stanford.edu` naming is consistent with Stanford's SUNet-managed dynamic IP assignment on residential/wireless segments (similar to DePaul's `loop-wireless-*.depaul.edu` or VT's `hc{hex}.dhcp.vt.edu` patterns). This is a recurring class across this survey: institutions assign hostnames that embed IP-segment metadata to dynamic devices, meaning the hostname rotates when the lease rotates.

The implications for tracking:
- A future re-probe of this hostname may return a different device (if the original device's lease lapsed and a new device picked up the IP)
- Long-term tracking of "this specific Stanford Streamlit deployment" requires capturing app-level fingerprints (model inventory, content hashes, etc.) and matching across IP changes

For survey purposes: the host was observed at this IP+hostname at probe time on 2026-05-19; subsequent re-probe may find a different device or no service.

---

## Discovery method

- **Initial surfacing**: Stage-0 dork-map of 1,629 verified Shodan dorks — `sr24-0915fd81a9.stanford.edu:8501` matched the Streamlit port + framework dork.
- **Verification**: framework-class confirmation via `/_stcore/health`; app-level content / auth state unverified by passive probe.

---

## Source artifacts

- Workspace: `~/recon/edu-llm-infra-2026-05-19/stage2-wave2/`
- Direct probe: `wave2-streamlit-and-stragglers-deep.json` (Stanford-StL section)
- aimap wave-2: `aimap-wave2.json`

---

## Cohort note

Stanford joins the wave-2 Streamlit cohort (GSU, UW, UChicago) — see `GA-georgia-state.md` for the survey's Streamlit-observation discipline note. All 4 hosts in this cohort have the same observation state: framework confirmed, app content WebSocket-only, auth state unknown without interactive probe.
