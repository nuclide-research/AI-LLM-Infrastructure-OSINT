# Insight #62: AI Agent + Service Co-location Creates Compound Attack Surface

**Survey anchor:** Cat-09 code assistants, 2026-05-26  
**Codified:** 2026-05-26  
**Status:** Confirmed, population-verified

---

## Observation

26 of 52 unauth OpenHands hosts also run Evolution API (WhatsApp automation) on port 3000. The port split is consistent across providers and countries: Evolution API on :3000, OpenHands on :3001. This is a shared Docker Compose template — "build a WhatsApp AI bot" starter kit circulating on YouTube or GitHub.

The same pattern appears elsewhere in the survey corpus: n8n + LangGraph (Insight #56 anchor), Redis Commander + OpenHands (cat-02 survey), Qdrant + LangGraph (multiple hosts in cat-06).

---

## The compound surface

An AI coding agent (OpenHands, CrewAI Studio, LangGraph, etc.) co-located with a third-party service automation tool (Evolution API, n8n, Composio) produces an attack surface wider than either service alone:

1. The AI agent has no auth → attacker controls the agent loop
2. The agent has filesystem access inside its Docker workspace
3. The co-located service (Evolution API, n8n, Redis) stores credentials in config files or environment variables
4. The agent can read those files without any additional bypass

**OpenHands + Evolution API chain:**
```
1. GET /api/v1/settings → confirm unauth (no token required)
2. POST /api/conversations → start agent session
3. Instruct agent: read /root/.env or evolution API config path
4. Agent returns WhatsApp session credentials, WAPI keys, phone numbers
5. Use credentials to send messages as the bot's WhatsApp account
```

No code execution outside Docker, no kernel exploit, no CVE. The agent's own design feature — read filesystem files on request — is the primitive.

---

## Why the no-auth default persists in this stack

OpenHands's default Docker Compose does not set `OPENHANDS_AUTH_TOKEN`. The tutorial repos that bundle OpenHands + Evolution API copy the compose file without adding auth. Operators who follow the tutorial inherit the no-auth posture without knowing it.

This is the same root cause as the Ollama default (no `--host 127.0.0.1` flag in documented installs): the default config is permissive, and tutorials don't address network exposure.

---

## Detection signal

Look for hosts with:
- Port 3001 returning `{"APP_MODE":"oss"}` at `/api/options/config` OR settings JSON at `/api/v1/settings`
- Port 3000 returning Evolution API health or WhatsApp instance list

The port split (:3000 service, :3001 OpenHands) is consistent enough to use as a Shodan/masscan dork. `port:3001 "OpenHands"` is a candidate fingerprint for the template pattern.

---

## Methodology implication

When an AI agent platform is found unauth, probe every port on the same host before moving on. The interesting finding is often not the agent itself but the service it was built to automate. The agent is the access primitive; the co-located service is the data or account-control surface.

Add a second-pass service sweep to the standard OpenHands/CrewAI/LangGraph enumeration: after confirming unauth on the agent API, run aimap against the full host to find what else is exposed.

---

## Population

- 26 OpenHands + Evolution API co-located hosts confirmed (2026-05-26 scan)
- 3 OpenHands + Open WebUI co-located hosts  
- 2 OpenHands + MCP Server co-located hosts
- 2 OpenHands + Typesense co-located hosts

Related insights: [[insight-56-langgraph-self-identifying-json-fingerprint]] (n8n+LangGraph+Qdrant three-layer stack)
