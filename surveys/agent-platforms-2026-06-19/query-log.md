# Shodan query log — agent-platforms 2026-06-19

| dork | total | harvested | tier | notes |
|---|---|---|---|---|
| `http.title:"OpenHands"` | 190 | 179 | REAL | port 3000 dominant (112), 3001 (27), nginx-fronted; primary target |
| `http.title:"SuperAGI"` | 15 | 15 | REAL | :443 (13) AWS-heavy, reverse-proxied |
| `http.title:"AgentGPT"` | 5 | 5 | REAL | mixed ports 3000/3006/8723/23457 |
| `http.title:"CrewAI Studio"` | 1 | 1 | REAL | 139.162.52.158 Linode |
| `http.title:"Function Dashboard"` | 1 | 1 | CAND | 34.54.190.81 GCP; generic title, verify functionGrid |
| `langgraph` (freetext) | 14 | 14 | CAND | loose; ports 3001/5000/8081/2024; verify /ok+/assistants/search |
| `letta` (freetext) | 3 | 3 | CAND | ports 53/5000/5001, likely FP |
| `http.title:"AutoGen Studio"` | 0 | 0 | DARK | 127.0.0.1 default bind |
| `port:2024 "ok":true` | 0 | 0 | DARK | langgraph dev = 127.0.0.1 |
| `port:8123 assistants` | 0 | 0 | DARK | langgraph prod not exposed w/ marker |
| `port:8283 "status":"ok"` | 0 | 0 | DARK | Shodan probes / not /v1/health/ |
| `port:8283` (bare) | 40,743 | - | NOISE | generic high port (OpenSSH/Socks4A/VNC) |
| `http.html:"Username, Development Only"` | 0 | 0 | DARK | Next.js client-rendered, not in SSR HTML |
| `port:5115` (goose gaggle) | 283 | - | NOISE | generic, no goose discriminator |

Zero = logged result. AutoGen Studio / Goose / Letta / LangGraph-server confirmed Shodan-dark (localhost-default bind); their exposure would require operator reverse-proxy.

## Round 2 — primary-source-derived markers (2026-06-19, chainsaw card-07 re-harvest)

Workflow ww0qggyxp engineered vendor-unique markers from current repo HEAD, adversarially refuted, then harvested:

| dork | total | harvested | tier | notes |
|---|---|---|---|---|
| `port:8283 http.html:"Create LLM agents with long-term memory"` | 0 | 0 | DARK | Letta info.summary lives in /openapi.json, Shodan never fetches it |
| `port:8283 "Create LLM agents with long-term memory and custom tools"` | 0 | 0 | DARK | same; full-banner freetext also 0 |
| `port:8283` (bare, re-confirm) | 40,806 | - | NOISE | "No data returned" dominant — port open, banner-dark (syn-ack-only at scale) |
| `http.html:"AutoGen Studio API" port:8081` | 0 | 0 | DARK | "AutoGen Studio API" is the openapi title, not in SPA root HTML |
| `http.html:"AutoGen Studio"` | 1 | 1 | CAND | **47.109.195.240** Aliyun Chengdu, self-signed, relabel title "Software R&D Intelligent Factory" -> honeypot-gate in verify |
| `"search_assistants_assistants_search_post"` | 0 | 0 | DARK | LangGraph openapi operationId; Shodan never fetches /openapi.json |
| `port:8123 "langgraph_py_version"` | 0 | 0 | DARK | LangGraph /info field; Shodan crawls / not /info |
| `http.html:"LangGraph"` | 590 | 0 | NOISE | freetext collision — Galent/NewRelic/PaellaDoc product+marketing pages embed the framework name; real servers return {"ok":true} JSON at / (not in this set) |
| `http.html:"local-inference" http.html:"code-mode"` (Goose) | 0 | 0 | DARK | goosed serves no HTML; /features is JSON-only |

STRUCTURAL RESULT: JSON-API agent platforms (LangGraph, Letta, Goose, AutoGen-backend) are Shodan-banner-dark BY CONSTRUCTION — their discriminating fingerprints live in non-root JSON endpoints (/info, /openapi.json, /v1/health/, /features, /api/version) that Shodan's crawler never fetches. Ports are populous but bannerless. Only AutoGen surfaced (1) because it serves a brand-bearing React SPA at /. Engine route for these: Censys (deeper endpoint fetch) or targeted active-probe of the port population — NOT Shodan HTML dorking. MetaGPT = leaked-file lane (GitHub config2.yaml), no listener.

## Round 3 — OpenHands population refresh (2026-06-19 PM, authenticated web UI re-pull)

Re-ran Shodan after browser-singleton lock freed; logged in directly to web UI (account Aperire), in-page fetch(), 0 API credits. Goal: refresh the OpenHands population behind finding #24084 (101.200.124.170).

| dork | total | harvested | tier | notes |
|---|---|---|---|---|
| `http.html:"OpenHands"` | 226 | 80 (77 IP) | LIVE | broad body marker; web-UI paged first ~80 of 226 (free-depth cap) |
| `http.title:"OpenHands"` | 190 | - | LIVE | misses renamed-title instances (Nexus Portal, Agentikus, etc.) |
| `http.html:"OpenHands" port:3000` | 112 | - | LIVE | port-3000 is the modal deployment (112/226 = 50%) |
| `http.favicon.hash:-1222104632` | 86 | - | SUBSET | CORRECTION: favicon = 86, a SUBSET of the 226 http.html pop (~62% miss). NOT the complete enumerator the prior memory note claimed. |

FACETS (http.html:"OpenHands", n=226): ports 3000=112 / 3001=29 / 443=25 / 80=19 / 8080=7 · countries US=56 DE=55 CN=19 GB=12 SG=12 · orgs Hetzner=29 Contabo=25 DO=16 Google=11 EE=8 · products nginx=26 (reverse-proxied) Apache=3 SimpleHTTPServer=2.

DELTA vs Round 1 (179 IP this morning): 65 overlap, **12 net-new IPs** (15 ip:port incl. multi-instance op). New file: openhands-round3-NEW.txt. Imported 77 -> empire.db (survey-local).

NET-NEW NOTABLES:
- 164.68.103.130 (Contabo DE) — multi-instance operator, 4 OpenHands on 8005/8008/8009/8010 (sequential-port farm).
- 3.69.4.12 + 52.29.181.139 (A100 ROW GmbH DE) — both "Agentikus | Control Interface for AI Agents" (branded OpenHands fork/wrapper, port 443).
- 165.245.152.183 (DO US) — "Bromure Agentic Coding" (title literally advertises keeping tokens/SSH keys/kubeconfig out of Claude Code & Codex — security-tooling operator running exposed OpenHands).
- 178.104.106.237 (EE UK) — "Moussa S. Ingenieur IA" personal-branded.
- 49.12.187.183 (Hetzner DE) — Hebrew-branded AI consultant.
- 120.48.4.40 (Baidu CN) — "Nexus Portal" relabel.

RESTRAINT: harvest is read-only metadata (names ARE the finding). Active scanner+aimap verify of the 12 net-new from the no-VPN home IP = gated, NOT run. Round-1 verify set already covered the morning population.
