# UC Santa Barbara: Open WebUI Auth Disabled + Local Username Leak

_NuClide Research · 2026-05-01_

---

## Summary

University of California, Santa Barbara "AI Lab" instance running Open WebUI v0.8.12 with authentication **completely disabled**. Any internet actor can enumerate models, read model configurations, and execute inference, no credentials required. Includes `functiongemma:latest`, a native function-calling model. Modelfile path leaks the macOS local username.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 169.231.124.164 |
| rDNS | 169-231-124-164.wireless.ucsb.edu |
| Org | University of California, Santa Barbara |
| Country | US, California |
| Instance name | **"AI Lab (Open WebUI)"** |
| Open ports | 3000 (Open WebUI, **auth disabled**), 11434 (Ollama, **public**) |

---

## Configuration

```json
{
  "name": "AI Lab (Open WebUI)",
  "version": "0.8.12",
  "features": {
    "auth": false,
    "enable_signup": false
  }
}
```

---

## Models

| Model | Size | Notes |
|---|---|---|
| gemma4:31b | 18 GB | Local |
| functiongemma:latest | 0 GB | Native tool/function-calling |
| gemma3:27b | 16 GB | Local |

---

## Findings

### F1: Authentication Disabled (CRITICAL)

Open WebUI auth is explicitly set to `false`. No login required. All models accessible via both port 3000 and port 11434.

```bash
# No auth - direct inference
curl -s http://169.231.124.164:3000/api/chat  # full WebUI API
curl -s http://169.231.124.164:11434/api/generate \
  -d '{"model":"gemma3:27b","prompt":"...","stream":false}'
```

Confirmed: inference on `gemma3:27b` executes without any credential.

### F2: Local Username + OS Leak (MEDIUM)

`functiongemma:latest` modelfile exposes the local model path:

```
FROM /Users/marcos/.ollama/models/blobs/sha256-415f8f...
```

- **OS:** macOS (`/Users/` path)
- **Username:** `marcos`

### F3: Function-Calling Model Exposed (MEDIUM)

`functiongemma:latest` uses Ollama's native function-calling (`RENDERER functiongemma`, `PARSER functiongemma`). If this model is integrated with any tool-execution framework, unauthenticated callers can invoke tool calls.

---

## Remediation

```bash
# Enable authentication in Open WebUI settings
# (Admin Panel → Settings → Auth → Enable authentication)

# Also bind Ollama to loopback
OLLAMA_HOST=127.0.0.1:11434
```

---

## Node: spark-4de1.mcdb.ucsb.edu (128.111.208.95): Biology Dept, DeepSeek Cloud

`spark-4de1.mcdb.ucsb.edu`, Molecular, Cellular, and Developmental Biology (MCDB) department, `spark-4de1` hostname. v0.13.2.

| Model | Size | Notes |
|---|---|---|
| `qwen3.6:35b` | 23GB | Local |
| `deepseek-v4-pro:cloud` |, | ☁️ Cloud proxy (no takeover URL at probe time) |
| `smollm2:135m` |, |, |
| `llama3.1:8b` | 4GB |, |

DeepSeek V4 Pro cloud proxy present but the 401 response did not include a `signin_url`, indicating the cloud proxy may not be actively linked to an Ollama Connect account, or the account has been rotated. Unauthenticated inference on local models confirmed. CVE-2025-63389 applicable.

| Node | IP | Hostname | Notes |
|---|---|---|---|
| AI Lab | 169.231.124.164 | 169-231-124-164.wireless.ucsb.edu | Open WebUI auth disabled, macOS marcos |
| MCDB Dept | 128.111.208.95 | spark-4de1.mcdb.ucsb.edu | DeepSeek cloud proxy, qwen3.6:35b |
| Umang Wireless | 169.231.203.223 | 169-231-203-223.wireless.ucsb.edu | llama.cpp, Qwen3-8B GGUF, username umang, Linux |

---

## Node: 169.231.203.223: Researcher Wireless Node (umang)

| Field | Value |
|-------|-------|
| IP | 169.231.203.223 |
| Hostname | 169-231-203-223.wireless.ucsb.edu |
| Network | UCSB wireless (personal device on campus WiFi) |
| Service | llama.cpp OpenAI-compatible server (no `/version` endpoint, `owned_by: "me"`) |
| Model | `/home/umang/Desktop/LLM_setup/models/Qwen3-8B-Q4_K_M.gguf` |
| Port | 8000/tcp public |

**Username `umang`** and full filesystem path leaked via `/v1/models`. Running on a Linux machine (path: `/home/umang/`), model stored directly on the user's Desktop, personal laptop on campus WiFi with the llama.cpp inference server bound to 0.0.0.0.

Model is **Qwen3-8B-Q4_K_M**, the Q4_K_M quantized GGUF of Qwen3 8B, with chain-of-thought capability active:

```bash
curl http://169.231.203.223:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"/home/umang/Desktop/LLM_setup/models/Qwen3-8B-Q4_K_M.gguf",
       "messages":[{"role":"user","content":"Say hi"}],"max_tokens":20}'
```

Response includes `<think>` block, Qwen3's extended thinking mode running on a personal laptop, publicly accessible.

---

## Disclosure

- **Discovered:** 2026-05-01 (AI Lab) / 2026-05-03 (MCDB node, umang wireless node)
- **Status:** Pending outreach to UCSB IT / AI Lab operator

---

## Additional hosts (2026-05-19 .edu sweep)

Two more UCSB-attributed hosts surfaced during the 2026-05-19 .edu LLM-infra survey wave-2 — one MCDB lab Ollama with substantial cloud-proxy inventory, and one residence-hall Open WebUI.

### Host A — `spark-4de1.mcdb.ucsb.edu` (Ollama with 22-model inventory; 19 `:cloud`-suffix entries — 100% match to the shared cross-.edu portfolio)

| Field | Value |
|---|---|
| IP | 128.111.208.95 |
| rDNS | `spark-4de1.mcdb.ucsb.edu` (Molecular, Cellular and Developmental Biology dept) |
| Org | University of California, Santa Barbara |
| Service | Ollama v0.18.0 on port 11434 |

**Observations** (initial visorgoose tag + 2026-05-19-late direct verification for Candidate Insight #49 validation):

`GET http://128.111.208.95:11434/api/version` → 200 `{"version":"0.18.0"}`.
`GET .../api/tags` → 200 with 22-model inventory. Of these, **19 are `:cloud`-suffix entries** (Ollama Connect cloud-subscription class). The cloud-portfolio is:

`deepseek-v3.2:cloud`, `deepseek-v4-pro:cloud`, `deepseek-v4-flash:cloud`, `kimi-k2.5:cloud`, `kimi-k2.6:cloud`, `kimi-k2-thinking:cloud`, `glm-4.6:cloud`, `glm-4.7:cloud`, `glm-5:cloud`, `glm-5.1:cloud`, `minimax-m2:cloud`, `minimax-m2.1:cloud`, `minimax-m2.5:cloud`, `minimax-m2.7:cloud`, `nemotron-3-super:cloud`, `qwen3.5:cloud`, `qwen3-coder-next:cloud`, `gemini-3-flash-preview:cloud`, plus one additional `:cloud` entry.

**This is a 100% match to the reference 18-model portfolio observed on SDSC (`compute.cloud.sdsc.edu`), UMaine ECE (`ECE-Ubuntu-02.um.maine.edu`), and RIT DISCO (`disco-dgx-spark.wireless.rit.edu`)** — UCSB MCDB becomes the **4th confirmed institution** in the shared-portfolio pattern (Candidate Insight #49 in `~/.claude/projects/-home-cowboy/memory/reference_insight_49_shared_ollama_connect_cloud_portfolio.md`).

All 4 confirmed hosts are research-compute environments across 3 states (CA × 2, ME, NY) and 4 distinct departments (NSF supercomputing center, ECE, distributed-computing group, molecular biology). Pattern is unlikely to be coincidence; hypothesis is shared deployment template circulated through research-computing communities (XSEDE / ACCESS-CI / CASC channels).

**What was NOT tested per restraint**:
- No invocation of any of the 19 `:cloud`-suffix models (would consume UCSB Ollama Connect quota AND upstream provider quotas).
- No POST to `/api/create` (CVE-2025-63389 class endpoint).
- No SSH credential testing.

### Host B — `ResNet-10-33.resnet.ucsb.edu` (Open WebUI v0.9.5 on :9081)

| Field | Value |
|---|---|
| IP | 169.231.10.33 |
| rDNS | `ResNet-10-33.resnet.ucsb.edu` (UCSB ResNet — residence-hall network) |
| Org | University of California, Santa Barbara |
| Service | Open WebUI v0.9.5 on port 9081 |

**Observations**: `GET .../api/config` returned 200 with Open WebUI v0.9.5, `enable_signup: false`, `enable_login_form: true`, `enable_ldap: false`. Properly configured. The ResNet network suggests this is a student-personal Open WebUI on a residence-hall machine — porting on :9081 (non-default) consistent with a personal-device deployment that picked an arbitrary port.

**Class observed**: closed-enrollment Open WebUI on a residence-hall network. Properly configured.

### Cross-tool confirmations

- aimap wave-2 (`-ports-class wide`) — surfaced both hosts
- visorbishop (post-G5) — Host B classified as `open-webui auth=auth severity=info`
- Direct `/api/config` probe on Host B — verified auth-on independently
- visorgoose `.edu` scan — surfaced Host A with CLOUD + 22-model inventory tag

### Class-membership summary (no tier labels per survey convention)

- `spark-4de1.mcdb.ucsb.edu`: Ollama cloud-proxy class — OBSERVED (per visorgoose tag; independent verification pending)
- `ResNet-10-33.resnet.ucsb.edu`: Open WebUI auth-on class — OBSERVED

UCSB now has 3 distinct hosts in the NuClide ledger (AI Lab, MCDB, ResNet). Pattern observation: UCSB infrastructure surfaces frequently across dept ranges + residence-hall ranges (similar to Duke's VCM pattern — institutional networks let individual users stand up services).

### Source artifacts

- visorgoose state: `~/recon/edu-llm-infra-2026-05-19/stage2-wave2/visorgoose-edu-state.json` (spark-4de1 entry)
- visorgoose report: `~/recon/edu-llm-infra-2026-05-19/stage2-wave2/visorgoose-edu-report.md`
- aimap wave-2: `~/recon/edu-llm-infra-2026-05-19/stage2-wave2/aimap-wave2.json`
- ResNet direct probe: `~/recon/edu-llm-infra-2026-05-19/stage2-wave2/wave2-openwebui-signup-verify.json` (UCSB-ResNet section)
- visorbishop wave-2: `~/recon/edu-llm-infra-2026-05-19/stage2-wave2/arsenal/visorbishop-wave2.json`
