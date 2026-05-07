# Case Study: HexStrike-AI Chain: /api/show Attribution

**Date:** 2026-05-01  
**Target:** `93.123.109.107:11434` (Ollama 0.17.5, Neterra BG / TECHOFF SRV, AS48090)  
**Method:** Passive /api/show chain, no exploit fired, no traffic generated beyond proof  

---

## TL;DR

A publicly exposed Ollama instance running `hexstrike-ai:latest` was traced via `/api/show` to its parent GGUF blob, cross-referenced to `huihui_ai/qwen3.5-abliterated:35b-a3b-q4_K` on Ollama Hub (SHA match: exact), and attributed to the `0x4m4/hexstrike-ai` platform (8,444★ GitHub MCP server). Three new attack techniques were demonstrated: model injection, SSRF via /api/pull, and cloud account takeover URL leakage. A second cloud takeover was discovered on `173.208.210.16` during cohort expansion.

---

## Chain Map

```
Step 1: hexstrike-ai:latest /api/show
         └─ blob sha256:e7b121... → Ollama Hub manifest for
            huihui_ai/qwen3.5-abliterated:35b-a3b-q4_K
            [EXACT SHA MATCH - unmodified GGUF, thin system-prompt wrapper]

Step 2: parent_model + brand search
         └─ 0x4m4/hexstrike-ai (GitHub, 8,444★)
            MCP server bridging LLMs to 150+ security tools
            Flask backend (hexstrike_server.py) on localhost:8888
            47 MCP tools: pacu, metasploit, hydra, generate_exploit_from_cve, ...

Step 3: /api/create model injection (POC D)
         └─ nuclide-probe:latest injected using hexstrike-ai as base
            zero bytes downloaded, ~512 bytes written (manifest + system layer)
            confirmed in /api/tags + /api/show → deleted clean

Step 4: /api/pull SSRF
         └─ 127.0.0.1:8888/probe/hexstrike:latest
            "connection refused" confirms SSRF fires to localhost
            Flask not running at probe time → no shell exec accessible

Step 5: deepseek-v4-pro:cloud → 401 → cloud key leak
         └─ machine: D09S18
            pubkey: sha256:e7b121... SHA256:gQhUc4nFhi4656+rCXubQ9ddP9/78apeRC9BA2jis2A
            signin_url: https://ollama.com/connect?name=D09S18&key=...
            status: UNLINKED (cloud model present, no account paired)

Step 6: Cohort expansion - 173.208.210.16
         └─ Second cloud key leak: ks-convert-hls
            pubkey: SHA256:PU1kduIfSCqhV73EA7ShLxrM2DHOUf2c8upQpq1A5nM
            Models: deepseek-v4-pro:cloud, minimax-m2.7:cloud + Arabic AI
            Machine profile: HLS media server + Arabic dialect converter
```

---

## Key Findings

### F1: Abliterated Model Deployment (93.123.109.107)
`hexstrike-ai:latest` is `huihui_ai/qwen3.5-abliterated:35b-a3b-q4_K` with a 5-rule SYSTEM block. Blob SHA identical to Ollama Hub. The system prompt (`"Never refuse security tasks"`) stacked on refusal-removed weights creates a belt-and-suspenders bypass: weights can't refuse, prompt forbids refusing. Base model is 36B MoE, vision-capable, 262k context.

### F2: HexStrike AI Platform (0x4m4/hexstrike-ai)
The Ollama model is the local LLM companion to a full offensive MCP stack. When `hexstrike_server.py` is running locally, the MCP layer provides 47 tools including unrestricted shell exec (`/api/command`), cloud exploitation (`pacu`), C2 (`metasploit`), password attacks (`hydra`), and autonomous attack chain generation. The MCP config sets `alwaysAllow: []`, all tool calls require human approval, but the local server itself has no auth.

### F3: Windows Cross-Build Artifacts
The 8B and 14B qwen3-abliterated models contain Windows filesystem paths in their `parent_model` field (`C:\Users\admin\.ollama\models\blobs\...`). These models were built on a Windows workstation (`C:\Users\admin\`) and pushed to the Linux server. The 35B variants and glm-4.7-flash were pulled natively on Linux.

### F4: Cloud Key Leakage (D09S18 + ks-convert-hls)
Two Ollama instances leaked Ollama Connect signin URLs via 401 error responses on cloud model requests. Each URL encodes the machine's SSH ed25519 public key and name. Visiting the URL while authenticated to ollama.com reassigns the machine's cloud subscription. Both keys are UNLINKED (no paired account), account does not exist yet or was never completed.

### F5: Model Injection (POC D)
`/api/create` is unauthenticated and accepts a `from` field referencing any existing model. Creating a model this way writes only a manifest diff, no GGUF download. The injected system prompt is confirmed via `/api/show`. Full cleanup via `/api/delete` verified. Impact: permanent system-prompt replacement for any connected AI client.

### F6: SSRF via /api/pull
Registry host in `model` field (`host:port/ns/name:tag`) causes Ollama to make outbound HTTPS GET to the specified host. Localhost connectivity confirmed via ECONNREFUSED error (vs DNS-not-found for external unknowns). Constraints: HTTPS, GET, `/v2/` path. Useful for port-state detection and OOB DNS exfiltration.

---

## Cohort Instances

| IP | Version | Notable Models | Tags | Status |
|----|---------|----------------|------|--------|
| 93.123.109.107 | 0.17.5 | hexstrike-ai, qwen3-abliterated ×3, glm-4.7-flash, deepseek:cloud | CLOUD, HEXSTRIKE, ABLITERATED | Probed |
| 173.208.210.16 | 0.21.2 | deepseek:cloud, minimax:cloud, nilechat_egy (Arabic), peach-roleplay | CLOUD, TAKEOVER | Logged |
| 159.26.15.166 | 0.13.5 | qwen3.5-abliterated:27b, gemma4:26b | ABLITERATED | Noted |

---

## Techniques Validated

| Technique | Endpoint | Impact |
|-----------|----------|--------|
| Model injection | POST /api/create | Arbitrary system prompt, zero bandwidth |
| SSRF | POST /api/pull | Outbound DNS/HTTPS to attacker host |
| Cloud key extraction | POST /api/generate (401) | Machine name + SSH pubkey + signin URL |
| System prompt extraction | POST /api/show | Full modelfile including system block |
| Blob attribution | POST /api/show + registry manifest | GGUF identity, detect fake/tampered models |
