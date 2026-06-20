# Agent Platforms — Stage -1 OSINT Intel (cat-agent-platforms)

Date: 2026-06-19. Category source: reference/category-taxonomy.md ("Agent Platforms, Not yet surveyed standalone").
Method: 4 parallel research squads, primary-source confirmation (repo source, default docker-compose, vendor docs). No live host probed.

## Thesis result up front

Every HTTP-surface platform in this category ships **auth-off by default behind a dev/prod toggle the operator must actively flip** (NODE_ENV/ENV=development, no `--auth-config`, no `SECURE=true`, no `auth` block). The auth-on-default thesis does not hold for agent platforms: the design default is open, auth is opt-in. This is a refutation worth codifying as a category-level insight.

## Platform matrix

| Platform | Port(s) | Auth default | HTTP surface | Niche fingerprint | Loot on exposure |
|---|---|---|---|---|---|
| AutoGen Studio | 8081 (127.0.0.1) | auth-off (C) | yes (0.0.0.0 dev) | `title:"AutoGen Studio"` + `/api/` route | provider keys in autogen.db + code-exec tools |
| CrewAI core | none | N/A | NO (library) | n/a | CVE-2026-2275/85/86/87 inject-chain (RCE/SSRF/file-read) |
| CrewAI Studio | 8501 (0.0.0.0) | auth-off (C) | yes | `title:"CrewAI Studio"` + streamlit | keys + one-click crew-run -> core CVEs |
| LangGraph server | 2024 / 8123 | auth-off (C) | yes | `/ok`={"ok":true} + POST `/assistants/search` + `/info` | provider+LANGSMITH keys, agent memory, `/runs` RCE-class |
| Letta (MemGPT) | 8283 | auth-off (C) | yes | `/v1/health/` {version,status:"ok"} + `/v1/blocks/` | agent memory R/W, keys, py-tool exec, CVE-2024-39025 |
| OpenHands | 8000 (3000 legacy) | auth-off (C) | yes | `title:"OpenHands"` + `/api/options/config` APP_MODE | CVE-2026-33718 cmd-inject -> runtime RCE, docker |
| Goose (goosed) | 3000 (127.0.0.1) | mixed (C) | Shodan-dark | `X-Secret-Key` hdr / gaggle `:5115` | host RCE-as-user (no sandbox); keyring/secrets.yaml |
| SuperAGI | 3000 (0.0.0.0) | auth-off (C) | yes | `title:"SuperAGI"` + `/api/` JSON | keys + static ENCRYPTION_KEY + tool-exec; DEV id super6@agi.com |
| MetaGPT | none | N/A | NO (CLI) | config2.yaml (leaked-file) | CVE-2024-23750; cleartext keys in committed config |
| AgentGPT | 3000 + 8000 | auth-off (C) | yes | `"Username, Development Only (Insecure)"` | LLM-jacking, MySQL changeme creds |
| BabyAGI (new) | 8080 (0.0.0.0) | auth-off (C) | yes | `title:"Function Dashboard"` + functionGrid | write-then-run RCE (`PUT /api/function` + `POST /api/execute`) |

C = CONFIRMED from primary source.

## Dork set (Step 0 ready; small + niche, vendor-unique)

```
http.title:"AutoGen Studio"
http.title:"CrewAI Studio" port:8501
port:2024 http.body:"\"ok\":true"
port:8283 "status":"ok" "version"
http.title:"OpenHands"
http.title:"SuperAGI"
http.html:"Username, Development Only (Insecure)"
http.title:"Function Dashboard"
port:5115                                  (goose gaggle manager only)
```

## Non-HTTP targets (route to leaked-file / committed-key, NOT Shodan)
- MetaGPT (CLI-only): hunt public-repo `config/config2.yaml`, baked image layers, world-readable `~/.metagpt/`.
- BabyAGI classic: outbound-only loop, no listener.
- CrewAI core: not a passive-recon exposure; risk is post-interaction inject-chain.

## CVEs surfaced
- CVE-2026-2275 / -2285 / -2286 / -2287 (CrewAI core, CERT/CC VU#221883): sandbox-fallback RCE, SSRF to metadata, file-read.
- CVE-2026-33718 / GHSA-7h8w-hj9j-8rjw (OpenHands <=1.4.0, CVSS 7.6): git-diff command injection; "authenticated" precondition collapses on auth-off deploy.
- CVE-2024-39025 (Letta/MemGPT v0.3.17): incorrect access control, /users data exposure.
- CVE-2024-23750 (MetaGPT <=0.6.6, CVSS 8.8): OS command injection in RunCode.

## CANDIDATE gaps to close before any actionable label
- AgentGPT FastAPI :8000 `dependancies.py` validator enforcement (backend-direct abuse) + `superAdmin` self-grant. Frontend auth-off is the only CONFIRMED AgentGPT finding.
- LangGraph `/store` and custom-node SSRF/path-traversal advisories not checked.
- Goose gaggle :5115 Manager auth posture not pinned to current main.
- All HTML-body dorks need banner/JSON-layer confirmation at Step 0c/1b before labeling (per scope-not-substrate + verify-before-asserting).
