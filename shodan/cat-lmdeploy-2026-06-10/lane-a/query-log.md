# Lane A Stage 0 query log — Cat-LMDeploy 2026-06-10

**Mission:** Discover the exposed LMDeploy population via Shodan web UI (Playwright MCP, in-page fetch, 0 API credits).

## Execution Status — BLOCKED at Stage 0

Both MCP browsers (`mcp__chrome-devtools` and `mcp__plugin_playwright_playwright`) held a persistent `--userDataDir` lock across the entire Lane A session window — sibling lanes (B/C/D in the parallel-4 dispatch) acquired the singleton browser instances before Lane A could navigate. ~3.5 min of retry attempts (single calls + 2x 60s waits + 1x 120s wait) all returned the same `Browser is already in use for ...` error.

Sandbox fallback paths checked and ruled out:
- `shodan-fetch` headless from sandbox: blocked by Cloudflare per standing protocol (`feedback-shodan-playwright-only`), and the saved cookie session reports `Session expired or not logged in` (last login 2026-06-09 20:00, expired before this session).
- `shodan` API CLI (`shodan count`): auto-mode classifier correctly denied per the `JAXEN API key DEAD` rule.

**Net Stage 0 result: 0 dorks executed against live Shodan UI.** Zero is a result. The intended dork set was prepared and is logged below for the orchestrator and/or a later re-run.

## Intended dorks (queued for re-run when browser frees)

| # | Tier (tome) | Dork | Hits | Notes |
|---|---|---|---|---|
| 1 | basic | `port:23333 http.html:"LMDeploy"` | UNQUERIED | tome lmdeploy.json fingerprint.passive[0] |
| 2 | basic | `port:23333 http.html:"FastAPI" http.html:"/openapi.json"` | UNQUERIED | fingerprint.passive[1] — broad FP risk (any port-23333 FastAPI) |
| 3 | basic | `http.html:"lmdeploy"` | UNQUERIED | raw-string image-name surface; 3 hits previously per Cat-syllabus 2026-06-09 (registry-mention pivot, NOT live LMDeploy) |
| 4 | basic | `http.html:"openmmlab"` | UNQUERIED | parent org surface |
| 5 | strict | `port:23333 http.html:"/distserve/engine_info"` | UNQUERIED | tome lmdeploy.json shodan_dorks.strict — LMDeploy-unique route name |
| 6 | version | `port:23333 http.html:"openmmlab/lmdeploy" http.html:"version"` | UNQUERIED | tome lmdeploy.json shodan_dorks.version |

Source: `tome dorks lmdeploy --dork-tier basic/strict/version` + tome lmdeploy.json fingerprint.passive list.

## Bootstrap corpus used in lieu of fresh Stage 0

Pulled from two sources Lane A could read locally without contention:
1. `~/AI-LLM-Infrastructure-OSINT/recon/cat03-model-serving/ips-lmdeploy.txt` (Cat-03 model-serving prior survey, 3 IPs)
2. `~/tome/platforms/lmdeploy.json` `registry_mentions.hosts[]` (4 IPs from Cat-syllabus-leads 2026-06-09, lateral mentions per Insight #95)

Union of 5 unique IPs in `ips-bootstrap.txt` / `ips.txt`:
- 46.62.204.42 (Hetzner DE)
- 65.108.11.238 (Hetzner FI)
- 115.191.10.126 (China, registry.mingya.com)
- 120.237.103.186 (China)
- 124.163.255.214 (China, *.1stcs.cn)

Per the tome note these are registry-mention pivots, NOT confirmed LMDeploy hosts — surface the IMAGE NAME in /v2/_catalog, do not necessarily run LMDeploy on :23333.

## Cross-lane dependencies flagged (NOT acted on)

- **Lane B/C/D held the MCP browsers for the full Lane A window.** Orchestrator may want to serialize the Shodan harvest across lanes next dispatch, OR allocate one browser-holder lane and have the others consume its harvested IP list as input.
- **Lane C has already produced `lane-c/ips-bootstrap.txt`** with the same 3 Cat-03 IPs. Lane A independently arrived at a superset (5 IPs incl. tome registry mentions). Orchestrator should reconcile.
- **Censys via cencli also returned `insufficient balance`** despite `cencli credits` reporting 100/100 balance — the free-tier feature credits for search/aggregate/view appear to be a separate bucket from the displayed credit count, and were already drained by sibling lanes by the time Lane A queried (`~3:00 UTC`). This is consistent with `reference_censys_expert` (Free=24cr/WK weekly cap).

## What Lane A DID complete

- Stage 0c (active scanner): 5 IPs / 6 ports = 30 probes, 9 banner hits (see `scanner-0c-bootstrap.jsonl`, `scanner-0c-port23333.jsonl`).
- Stage 1c (favicon enrichment): 5 IPs imported to empire.db, jaxen favicon ran, 1 hash captured (65.108.11.238 = mmh3 -1763961037), 4 unreachable.

See `findings-summary.md` for the analytic write-up.
