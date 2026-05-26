# OpenHands Autonomous Agent: 52 Unauth Deployments, WhatsApp Bot Builder Pattern

**Survey:** Category 09 — AI Code Assistants  
**Date:** 2026-05-26  
**Method:** Shodan harvest (Playwright, no API token) + aimap v1.9.29 scan + manual verification  
**Platforms scanned:** OpenHands (All Hands AI), Sourcegraph, Sourcebot, Sweep AI, Dyad, bolt.diy, gpt-engineer, Tabby ML, Tabnine, Refact

---

## Summary

191 OpenHands instances in Shodan. We scanned 56. 52 returned `/api/v1/settings` without authentication. On 26 of those 52 hosts, Evolution API (WhatsApp automation gateway) runs on port 3000 alongside OpenHands on port 3001. The same deployment template, the same no-auth posture, repeated across 26 cloud servers.

OpenHands gives a logged-in user full control of a Docker workspace with shell access and an autonomous agent loop. Without auth, it gives that to anyone.

---

## Population

| Platform | Shodan total | Scanned | Unauth confirmed |
|---|---|---|---|
| OpenHands | 191 | 56 | 52 |
| Evolution API (co-located) | — | 56 | 26 |
| Sourcegraph self-hosted | 33 | 36 | 0 (auth-on-default) |
| Sourcebot | 25 | 25 | 0 |
| Dyad | 34 | 14 | pending |
| bolt.diy | 1 | 14 | pending |
| gpt-engineer | 16 | 14 | pending |
| Tabby ML | 1 | — | Shodan-dark |
| Tabnine | 30 | — | all Tabnine SaaS fleet (GCP) |

Shodan count: `http.title:"OpenHands"` = 191. Count at last survey (2026-05-14): ~215. Down 24, likely from deployments rotating off after use.

---

## F1: 52 OpenHands instances with no authentication (CRITICAL)

`GET /api/v1/settings` returns the full agent configuration including LLM model, base URL, and `llm_api_key_set: true`. No token required.

The endpoint exposes:
- LLM provider and model (see anchor samples below)
- `llm_api_key_set: true` when configured — confirms a live API key is wired in
- `provider_tokens_set` — OAuth tokens for connected services
- Conversation and iteration limits
- Agent version and capability flags

OpenHands also exposes `/api/conversations` (task history) and the WebSocket runtime interface at `/ws`. The settings endpoint is the entry point; the agent control surface is behind it.

**Hosting distribution of unauth instances:** Hetzner (12), Contabo (9), DigitalOcean (7), Vultr (4), OVH (4), AWS (3), Aliyun (3), others.

**Country distribution:** DE 18, US 9, FR 5, SG 3, CN 3, AE 2, IN 2, CL 1, VN 1, CA 1, HK 1, others.

---

## F2: WhatsApp bot builder template — 26 hosts (CRITICAL)

26 of 52 unauth OpenHands hosts also run Evolution API on port 3000. Evolution API is a WhatsApp automation gateway built on Baileys; it exposes a REST API for managing WhatsApp sessions and sending messages.

Port layout on affected hosts:
```
:3000  Evolution API (WhatsApp gateway) — unauth or default-key
:3001  OpenHands (autonomous AI coding agent) — unauth
```

Some hosts also add Open WebUI on :3000 or :3001. The consistent port split points to a shared deployment template, likely a Docker Compose stack circulating on YouTube tutorials or GitHub.

The impact chain: unauth OpenHands → instruct agent to read Evolution API config → extract WhatsApp session credentials → send messages as the bot's phone number.

**Sample co-located hosts:**

| IP | Provider | Country | Services |
|---|---|---|---|
| 212.56.36.62 | Contabo | DE | OpenHands :3000/:3001 + Evolution :3000 |
| 46.224.207.253 | Hetzner | AE | OpenHands :3001 + Evolution :3000 + Open WebUI :3000 |
| 51.79.52.79 | OVH | CA | OpenHands :3001 + Evolution :3000 + Open WebUI :3000 |
| 143.89.224.22 | HKUST | HK | OpenHands :3000 + Evolution :3000 |
| 150.129.9.251 | Infra Group | NL | OpenHands :3000 + Evolution :3000 |

---

## F3: HKUST / HKGAI — confirmed unauth (HIGH)

Host: `143.89.224.22:3000`  
Operator: Hong Kong University of Science and Technology  
Network: HKUST campus block (AS4515)

`/api/v1/settings` response (key fields):
```json
{
  "agent_settings": {
    "llm": {
      "model": "openai/DS3.2",
      "base_url": "https://api.hkgai.net/v1",
      "api_key": null
    }
  },
  "llm_api_key_set": true,
  "v1_enabled": true
}
```

`api.hkgai.net` is the Hong Kong Government AI platform. `llm_api_key_set: true` with the API key not returned in the response confirms a live credential is wired in. Unauth access to the settings endpoint does not return the key value, but unauth access to the agent runtime (WebSocket, conversation API) enables triggering inference requests against HKGAI quota without the key being visible.

Also: Evolution API on :3000 co-located. Running the WhatsApp bot builder template on HKUST infrastructure.

---

## F4: Fluid Attacks researcher — home directory exposed (HIGH)

Host: `40.160.235.43:8080`  
Server: `SimpleHTTP/0.6 Python/3.13.3` — `python3 -m http.server` running in `$HOME`  
Hosting: OVH US LLC  
Attribution: `.gitconfig` → `cristian.vargas@fluidattacks.com`, Cristian Vargas, Fluid Attacks

Fluid Attacks is a Colombian application security firm (fluidattacks.com). This researcher's home directory is fully browsable without authentication.

**Exposed paths:**

| Path | Contents |
|---|---|
| `.claude/.credentials.json` | Claude Code OAuth token |
| `.claude/history.jsonl` | Full Claude Code conversation history |
| `.claude/sessions/` | Active session data |
| `.claude/projects/` | Per-project Claude Code memory |
| `.claude.json` | Account metadata (`oauthAccount.emailAddress` confirmed) |
| `.openhands/` | OpenHands agent configuration |
| `.augment/`, `.codeium/`, `.kiro/`, `.roo/`, `.continue/` | API keys for 15+ other AI coding tools |
| `ics/` | ICS/SCADA security research directory |
| `zb.conf` | Zigbee protocol configuration |
| `zb_capture.log` | Zigbee packet captures |
| `zb_mosq.log` | Mosquitto (MQTT) broker log |
| `gateway_debug.log` | ICS gateway debug output |
| `.ssh/authorized_keys` | SSH authorized public keys (no private key exposed) |

`.claude/.credentials.json` is the Claude Code OAuth token file. The token grants API access under the researcher's subscription. Values not read — presence confirmed from directory listing.

The `ics/` directory, Zigbee captures, and gateway logs indicate active ICS security work. AI-assisted penetration test artifacts against industrial infrastructure are accessible.

**Root cause:** `python3 -m http.server 8080` started from the home directory, not a project subdirectory. Port 8080 open outbound on OVH.

---

## F5: MCP Server + wildcard CORS

Host: `178.104.254.115:3001`  
Service: MCP Server (JSON-RPC 2.0, error method: `HTTP method GET is not allowed`)  
Finding: `Access-Control-Allow-Origin: *`

The wildcard CORS header on an MCP server enables cross-origin POST requests from any web page. A user visiting a malicious site while authenticated to this MCP server can trigger tool calls. Combined with OpenHands on the same host, this is a second-order attack surface.

---

## What Sourcegraph, Sourcebot, and Sweep AI look like

**Sourcegraph (33 Shodan):** 28 of 33 are Sourcegraph's own SaaS fleet (AWS, GCP, Cloudflare). 5 self-hosted. All 5 returned either the auth-required error (`/.api/graphql` → "Private mode requires authentication") or the login page. Auth-on-default holds for Sourcegraph.

**Sourcebot (25 Shodan):** 25 self-hosted instances across 18 countries. Auth status from aimap: 9 returned `X-Powered-By: Next.js` but no data findings — Sourcebot prompts login before code browsing.

**Sweep AI (15 Shodan):** All 15 are Google LLC CDN nodes — Sweep AI's SaaS. No self-hosted surface found.

**Tabnine (30 Shodan):** 27 GCP, 3 AWS — Tabnine's own cloud. No self-hosted Tabnine Context Engine instances found.

**Tabby ML:** Confirmed Shodan-dark. `http.html:"tabbyml"` = 1 (Aliyun, banner-noise). `"tabby-webserver"` = 0. The assessment file note from 2026-05-14 stands: Tabby ML requires masscan-seeded port-8080 discovery.

---

## Insight candidate: OpenHands + Evolution API deployment template

26 of 52 unauth OpenHands hosts run Evolution API on port 3000. The port split (:3000 Evolution, :3001 OpenHands) is consistent across providers and countries. This is not coincidence — it is a shared Docker Compose template. Someone published a "build a WhatsApp AI bot" tutorial or starter repo that bundles both services, and the no-auth posture of OpenHands is the default in that template.

**Candidate Insight #61:** AI agent + third-party automation service co-location is a compound attack surface. The agent can read or write to the co-located service without any additional credential. The attack chain is: unauth OpenHands → agent workspace → read Evolution API config → WhatsApp session credentials.

---

## Recon artifacts

```
~/AI-LLM-Infrastructure-OSINT/recon/cat09-2026-05-26/
  shodan-openhands.txt          58 IP:PORT from 4 Shodan queries
  shodan-sourcegraph-sourcebot-sweep.txt   87 IP:PORT from 7 queries
  shodan-dyad-tabnine-bolt.txt  ~80 IP:PORT from 8 queries
  ips-openhands.txt             56 unique IPs scanned
  ips-sourcegraph-selfhosted.txt   36 filtered self-hosted IPs
  ips-dyad-bolt-gpteng.txt      14 filtered IPs
  aimap-openhands.json          56 targets, 91 services, 60 findings
  aimap-sourcegraph.json        36 targets, 35 services, 21 findings
  aimap-dyad-bolt.json          (pending)
```
