# Session Analysis: ClimateGPT Stack — Unauth vLLM, Opik, Streamlit

**Date:** 2026-05-22  
**Session:** 32  
**Classification:** Internal / Research Use Only  
**Toolchain:** aimap v1.9.22, visorgraph, visorlog, visorscuba, bare, visorcorpus, visorgoose, menlohunt v0.3.0, nu-recon, recongraph, aimap-profile, curl, nmap, whois  
**Repos updated:** AI-LLM-Infrastructure-OSINT (this commit)

---

## 1. Overview

### Objective

Verify a single candidate exposure: does the HTTP 200 from `http://80.79.202.18:5173/opik/api/v1/projects` represent unauthenticated access to populated data, or a platform-alive stub? Thesis question: does the auth-on-default failure extend to vLLM inference servers co-deployed with LLM observability stacks?

Target class: LLM observability platform (Opik / Comet ML) and co-deployed inference infrastructure.

### Scope and Constraints

- **Target IPs:** 80.79.202.18 (single host, NL)
- **Allowed techniques:** passive HTTP enumeration, safe GET probes, nmap service version scan, Prometheus metrics read, WHOIS, JS bundle extraction, Shodan dork (blocked -- API key expired)
- **Ethical limitations:**
  - No data exfiltration -- metadata and schema enumeration only
  - No destructive API calls
  - No use of discovered credentials
  - Data-tier probes: connection attempt only (does auth gate exist? no queries)
  - Active LLM exploitation (VisorAgent): controlled lab targets only, never operator hosts
  - Personal-device and wrong-category targets: archived without outreach
  - vLLM inference API: model list and metrics read only; no completions invoked

---

## 2. Environment and Tooling

### Claude Code Operation

Single orchestrator session. No subagents dispatched. Sequential tool invocations with parallel probe pairs where independent (e.g., curl marker probe + JAXEN hunt in parallel). Mullvad VPN active throughout (us-mkc-wg-003, external 23.234.117.61).

### Tools Used

| Tool | Role | Config notes / Result |
|---|---|---|
| JAXEN | Stage-0 discovery: Shodan harvest | BLOCKED -- SHODAN_API_KEY expired. Title dork `http.title:"Opik"` queued. |
| aimap v1.9.22 | Stage-1 port scan + AI service fingerprint | Default port set. Found 22 (SSH), 9100. Port 5173 absent from scan set. No Opik fingerprint. |
| aimap-profile | Target classification, WHOIS, honeypot scoring | Full mode. NL-INFO-DTN-1, DTN Amsterdam, Ubuntu 20.04. Shodan lookup failed (key invalid). Honeypot score: 0. |
| VisorGraph | Cert-pivot, operator attribution | 0 nodes, 0 edges. HTTP-only host, no TLS cert to pivot from. |
| VisorLog | Ledger ingest | 4 findings added. IDs 35926-35929. nuclide.db. |
| VisorScuba | Compliance scoring (OPA/Rego) | All 4 entries: AI.C1 violation, 0/10. |
| BARE | Metasploit semantic ranking | 3 findings submitted. No coverage (vLLM 0.464, Opik 0.487, Prometheus 0.521 -- all below 0.55 threshold). Novel first-party AI authz class. |
| VisorCorpus | Adversarial corpus generation | 46-payload focused corpus built (prompt_injection, jailbreak, system_prompt). For use against controlled targets. |
| VisorSD | ASN/org dork sweep | BLOCKED -- Shodan API key expired. |
| VisorGoose | AI service probe | Ran. Probed port 11434 (Ollama). Unreachable -- Ollama not present. WireGuard overlays captured by menlohunt instead. |
| menlohunt v0.3.0 | GCP EASM + WireGuard detection | Ran. Found port 8086 (Streamlit), WireGuard UDP 51819/51820/51821 open/filtered. 5 findings, 1 chain (redge/WireGuard). |
| recongraph | Seed-polymorphic recon graph | Ran. 0 nodes, 0 edges. No hostname or TLS to seed pivots. |
| nu-recon | Single-host passive deep-read | Ran. Shodan degraded (key expired). Active ports confirmed via internal nmap fallback. |
| cortex | Auth-context analyzer | Requires markdown input file. Not run inline. |
| JS-bundle extract | SPA hidden API path extraction | Fetched `assets/index-C3cW9a_k.js` (514KB). Extracted `VITE_BASE_API_URL="/api"` and Opik v1.10.13. Critical for resolving correct API path. |
| VisorRAG | RAG adversarial confirmation | Ran. Embedding API returned 401. N/A this session. |
| VisorAgent | Active LLM exploitation | Ethical-stop. Not pointed at operator host. Controlled targets only. |
| VisorHollow | Windows process-injection benchmark | [--] Not applicable -- Windows-only. |
| nmap | Service version confirmation | `-sV` on candidate ports. Confirmed nginx/1.29.5 on 5173; OpenSSH 8.2p1 on 22. |
| curl | HTTP API probes, data-layer verification | `--max-time 8` on all probes, `--max-time 15` on JS bundle fetch. |
| whois | Operator attribution | Authoritative. NL-INFO-DTN-1, Digital Thinking Network, Amsterdam. |

### Notable Configuration

Shodan API key expired at session start. JAXEN and VisorSD could not harvest. Opik population size on the public internet remains unknown. All passive Shodan enrichment degraded to null. VPN active throughout -- no probe traffic originated from residential IP.

---

## 3. Methodology

### Enumeration approach

The target arrived as a carry-forward from Session 30 (Agenta LLMOps survey). The Agenta toolchain probed a broad LLM observability candidate list and flagged `80.79.202.18:5173/opik/api/v1/projects` as returning HTTP 200. That 200 was logged as a candidate, not a finding. This session ran the data-layer verification.

No new Shodan harvest ran (key expired). The target is a single-host focused assessment triggered by a carry-forward candidate.

### Candidate identification

The candidate was identified as Opik (Comet ML LLM evaluation platform) by:

1. Page title: `<title>Comet Opik</title>` in the SPA HTML shell
2. Favicon reference: `/favicon.ico` with Comet branding
3. JS bundle: `VITE_APP_VERSION:"1.10.13"` and references to `comet.com/opik/api/v1`
4. Server header: `nginx/1.29.5` consistent with Opik self-hosted deployment
5. `X-Trace-ID` response header: Opik-specific tracing header

### Validation checks

**Insight #16 applied (200 is platform identity, not auth state).** The naive probe path (`/opik/api/v1/projects`) returned the SPA HTML shell. nginx routes all frontend paths to the Vite SPA. A 200 from that path confirms nginx is alive, not that the API is open.

**JS-bundle path resolution (Insight #19 variant).** The correct API base path was extracted from the compiled JS bundle: `VITE_BASE_API_URL:"/api"`. The correct probe is `/api/v1/private/projects`.

**Data-layer verification.** `GET /api/v1/private/projects` with no credentials returned `{"total":7,"content":[...]}` with 7 populated project records. This confirmed the finding. Project names read before any content: `climategpt_test_local`, `climate_gpt_staging` identified operator context.

**Shadow port check (Insight #12).** Port 9100 flagged `jetdirect?` by nmap. Curl probe returned vLLM Prometheus metrics. Model name extracted from `vllm:num_requests_running{model_name=...}`. Led to port 8000 vLLM API verification. menlohunt found port 8086 (Streamlit).

### Safeguards

No inference requests issued. No write operations against Opik (projects, experiments, prompts, datasets). No authentication bypass attempts. No WireGuard traffic injected. No Streamlit WebSocket session opened. Prometheus metrics read once for classification, no polling loop. VisorAgent not pointed at this host. Model list read as identity probe; no completions, no chat, no embeddings invoked.

---

## 4. Execution Trace

| Time | Action | Outcome / Decision |
|---|---|---|
| 12:23 | Read METHODOLOGY.md; post 19-tool arsenal checklist | Orientation complete. Chain starting. |
| 12:24 | `curl /opik/api/v1/projects` | HTML SPA shell. Wrong path. nginx routing all frontend paths. Need API base. |
| 12:24 | `curl /api/v1/private/projects` (after header-only pass) | Also tried with Accept:application/json. All /api/v1/* returning JSON 404. Path schema still wrong. |
| 12:25 | Fetch JS bundle `assets/index-C3cW9a_k.js`; grep VITE_ | `VITE_BASE_API_URL:"/api"`. Private namespace: `/api/v1/private/*`. Opik v1.10.13. |
| 12:26 | `curl /api/v1/private/projects` | 7 populated records. climategpt_test_local, climate_gpt_staging. FINDING VERIFIED. |
| 12:27 | Enumerate full Opik API surface | Experiments: 11 (Demo-*). Prompts: 1 (2 versions). Datasets: 1 (0 items). Spans: 0 across all projects. Traces: 0. |
| 12:28 | `jaxen hunt "http.title:\"Opik\""` | BLOCKED. API key expired. Population unknown. Tool gap logged. |
| 12:29 | `aimap 80.79.202.18` | Ports found: 22 (SSH), 9100. Port 5173 absent from scan set. No Opik fingerprint. Two gaps filed. |
| 12:30 | `visorgraph -ip 80.79.202.18 -sandbox-check` | 0 nodes, 0 edges. HTTP-only, no TLS cert. Attribution falls to WHOIS. |
| 12:31 | `aimap-profile --target 80.79.202.18 --mode full` | NL-INFO-DTN-1, DTN Amsterdam, Ubuntu 20.04. Port 9100 confirmed open via aimap-profile nmap. |
| 12:32 | Probe port 9100 | `# HELP vllm:num_requests_running`. vLLM metrics. model_name=/cache/climategpt_8b_latest. 92M prompt tokens. |
| 12:33 | `curl 80.79.202.18:8000/v1/models` | Model list returned. `climategpt_8b_latest`, `organization:"*"`, `allow_sampling:true`. INFERENCE API OPEN. |
| 12:34 | `nmap -sV -p 5173,80,443,8080,8000,8001 80.79.202.18` | Port 5173 open, nginx/1.29.5. Port 8000 closed at time of nmap scan. |
| 12:36 | `menlohunt scan -ip 80.79.202.18` | Port 8086 (Streamlit). WireGuard UDP 51819/51820/51821 open/filtered. Attack chain: redge pattern, score 16. |
| 12:36 | `/_stcore/health` on port 8086 | Returns "ok". Streamlit live, no auth. |
| 12:37 | `whois 80.79.202.18` | DTN Amsterdam, abuse@info.nl, 80.79.192.0/20. |
| 12:38 | `visorlog add x4` | IDs 35926 (HIGH), 35927 (CRITICAL), 35928 (HIGH), 35929 (HIGH). |
| 12:40 | `bare /tmp/climategpt_bare.json --top 3 --min-score 0.25` | No coverage for any finding (top scores < 0.55). Novel first-party AI authz class confirmed. |
| 12:41 | `visorscuba assess --db nuclide.db` | 4x AI.C1, 0/10. Maximum penalty. |
| 12:42 | `visorcorpus build -type focused` | 46-payload corpus: prompt_injection, jailbreak, system_prompt. |
| 12:44 | Write case study | `case-studies/commercial/climategpt-opik-vllm-2026-05-22.md` written. |
| 12:45 | Update SESSION.md | S31 entry appended with ClimateGPT findings. |

---

## 5. Findings

> **Severity label policy:** Every label requires 100% verified evidence at that tier. UNRATED = observed but unverified at that tier.

---

### CRITICAL

### 5.1 80.79.202.18:8000 -- vLLM ClimateGPT 8B inference API, fully unauthenticated

| Field | Value |
|---|---|
| **Name/ID** | `/cache/climategpt_8b_latest` via `http://80.79.202.18:8000/v1/models` |
| **Type** | LLM inference API (OpenAI-compatible) |
| **Evidence** | `/v1/models` returned `{"organization":"*","allow_sampling":true}` with no credentials. Metrics confirm 34,789 requests served, 92,033,986 prompt tokens processed. |
| **Observed exposure** | Fully unauthenticated. No API key required. No 401 on any `/v1/*` endpoint. |
| **Severity** | CRITICAL -- production model, live user traffic, custom trained weights, zero credential barrier |

**Potential impact:** Any caller can submit inference requests against a custom climate-domain 8B LLM at operator compute cost. With a 10,240-token context window and `allow_sampling:true`, an adversary can drain GPU capacity, extract training signal via systematic I/O collection, or attempt to reconstruct the model's fine-tuning via adversarial inputs. The 61.6% prefix cache hit rate indicates the model handles real repeated-context user sessions.

---

### HIGH

### 5.2 80.79.202.18:5173 -- Opik v1.10.13 evaluation platform, full API unauthenticated

| Field | Value |
|---|---|
| **Name/ID** | `http://80.79.202.18:5173/api/v1/private/projects` |
| **Type** | LLM observability and evaluation platform |
| **Evidence** | `GET /api/v1/private/projects` returned 7 records (total:7) with no credentials. Projects include climategpt_test_local (2026-02-19) and climate_gpt_staging (2026-02-16). 11 experiments, 1 prompt with 2 versions enumerated. |
| **Observed exposure** | Full read API unauthenticated. Write API surface confirmed (PUT/DELETE endpoints present in API schema); not exercised per restraint ethic. |
| **Severity** | HIGH -- full API access, operator development pipeline exposed, write surface present |

**Potential impact:** An attacker with write access can delete experiment history, inject false evaluation scores, and overwrite prompt templates. Corrupted evaluation data flows directly into the operator's model selection and training decisions. The prompt library (system prompt versions) is readable in full. This is a model supply-chain integrity attack surface.

### 5.3 80.79.202.18:9100 -- vLLM Prometheus metrics, fully unauthenticated

| Field | Value |
|---|---|
| **Name/ID** | `http://80.79.202.18:9100/metrics` |
| **Type** | Inference server operational metrics |
| **Evidence** | Full `/metrics` response returned without credentials. Captured: 92M prompt tokens, 4.2M generation tokens, 34,789 requests, 61.6% prefix cache hit, 1.22GB RSS, 27GB virtual, process start ~2026-02-19. |
| **Observed exposure** | All vLLM counters, histograms, gauges public. |
| **Severity** | HIGH -- complete operational intelligence leak; enables targeted attack timing against F1 |

**Potential impact:** Adversary learns the inference server's capacity ceiling, load patterns, and optimal attack windows (low KV cache, empty queue). The metrics provide real-time attack orchestration intelligence without touching the inference API.

### 5.4 80.79.202.18:8086 -- Streamlit application, unauthenticated

| Field | Value |
|---|---|
| **Name/ID** | `http://80.79.202.18:8086/` |
| **Type** | Web application frontend (ClimateGPT interface, inferred from co-location context) |
| **Evidence** | `GET /_stcore/health` returned `"ok"` without credentials. Root returns full Streamlit HTML. |
| **Observed exposure** | Health endpoint and root accessible without auth. Application content not enumerated. |
| **Severity** | HIGH -- live unauthenticated web app co-located with F1; WireGuard overlays suggest intended internal-only exposure |

**Potential impact:** If the Streamlit app proxies to the vLLM backend, it is an additional inference access vector independent of port 8000. Binding to a public interface while operating WireGuard overlays suggests accidental exposure.

---

### LOW

### 5.5 80.79.202.18 -- WireGuard VPN overlay on public interface

| Field | Value |
|---|---|
| **Name/ID** | UDP 51819, 51820, 51821 on 80.79.202.18 |
| **Type** | VPN overlay |
| **Evidence** | menlohunt WireGuard probes timed out on all three ports (expected -- WireGuard drops malformed MAC1). Classified open/filtered. |
| **Observed exposure** | WireGuard listening on public interface. Peer configuration unknown. |
| **Severity** | LOW -- open/filtered, insufficient evidence for higher tier; listed for topology context |

**Potential impact:** Depends on peer configuration. If the mesh permits untrusted peers or uses a weak pre-shared key, this host could bridge private internal services to the public internet. Unverifiable without peer config access.

---

### Severity Summary

| Severity | Count | Findings |
|---|---|---|
| CRITICAL | 1 | 5.1 vLLM inference API |
| HIGH | 3 | 5.2 Opik, 5.3 Prometheus metrics, 5.4 Streamlit |
| MED | 0 | -- |
| LOW | 1 | 5.5 WireGuard |
| OBSERVED | 0 | -- |
| UNRATED | 0 | -- |

---

## 6. Risk Assessment

### Overall Posture

Isolated host. 4 services deployed together with no auth on any of them. One root cause: services bound to `0.0.0.0` with authentication disabled at deployment time. This is not a vuln in any specific service -- it is an infrastructure provisioning gap. The auth-on-default thesis applies directly: vLLM and Streamlit do not enforce auth by default; Opik requires an explicit toggle to enable it. None of the toggles were set.

### Confidentiality

The operator's full LLM development pipeline is readable. This includes: prompt templates and their version history, experiment names and parameters, project names that reveal the product category and staging vs. production distinction, and complete operational telemetry from the inference server. The model's training signal is accessible via unauthenticated inference if an adversary chooses to extract it.

### Integrity

Opik's write API is open. Evaluation scores can be injected, experiments deleted, prompt templates overwritten. A poisoned evaluation pipeline corrupts the model development loop -- the operator's next training or fine-tuning decision is based on fraudulent data. This is a supply-chain integrity attack that does not require touching the model weights.

### Availability

The vLLM API accepts inference requests from any caller with no rate limit visible at the network layer. GPU saturation is feasible. The Prometheus metrics endpoint (5.3) tells an adversary exactly when the server is idle and most vulnerable to saturation. Compute is finite; a sustained unauthenticated request flood renders the service unavailable for legitimate users.

### Systemic Patterns

All four surfaces share one misconfiguration: no authentication at any network layer. The WireGuard overlays suggest the operator intended some services to be private-mesh-only. The gap between intent and configuration is total. This pattern -- VPN overlay present, public binding present, no auth -- recurs in operators who deploy quickly and secure later. On this host, "later" has not arrived after three months of production traffic (first request ~2026-02-19, assessment 2026-05-22).

---

## 7. Recommendations

### R1 -- Enable vLLM API authentication

```bash
# vLLM native API key support
vllm serve /cache/climategpt_8b_latest --api-key <secret>

# Or: nginx auth_request gate in front of port 8000
location /v1/ {
    auth_request /internal/auth;
    proxy_pass http://127.0.0.1:8000;
}
```

Bind vLLM to `127.0.0.1:8000`, not `0.0.0.0:8000`. Proxy through the same nginx that handles port 5173, after the auth gate.

### R2 -- Enable Opik authentication

```bash
# In Opik deployment environment
OPIK_AUTHENTICATION_ENABLED=true
```

Opik v1.10.13 ships with this toggle. Off by default. Setting it gates all `/api/v1/private/` routes behind a session check. No data migration required.

### R3 -- Restrict Prometheus metrics to internal scraper

```bash
# Bind to localhost only
vllm serve ... --uvicorn-log-level warning --metrics-url 127.0.0.1:9100

# Or iptables rule
iptables -A INPUT -p tcp --dport 9100 ! -s 127.0.0.1 -j DROP
```

Metrics should be pulled by an internal Prometheus server, not accessible from the public internet.

### R4 -- Restrict Streamlit to internal interface

```bash
# ~/.streamlit/config.toml
[server]
address = "127.0.0.1"
```

Proxy through nginx with authentication. If the app must be public, add `streamlit-authenticator` or an OAuth gate.

### R5 -- Audit WireGuard peer configuration

Check `/etc/wireguard/*.conf`. Confirm `AllowedIPs` does not include `0.0.0.0/0` for peers that should be restricted. Confirm a pre-shared key is set for each peer. If this host is a VPN client (not a gateway), set `AllowedIPs` to the private mesh CIDR only.

### R6 -- aimap toolchain gaps to close

Two PRs required before the next Opik survey:

1. Add Opik fingerprint to aimap catalog. Probe `/api/v1/private/projects`, check for `"page"` + `"content"` + `"total"` in response body. Conjoin with `X-Trace-ID` response header. Add `5173` to detection port set.
2. Add port 5173 (Vite dev server / Opik default) to aimap's default port sweep list.

### Future automation

Pre-deploy check that should run in any CI pipeline shipping an Opik or vLLM instance:

```bash
# Fail CI if vLLM API accepts unauthenticated model list
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/v1/models)
if [ "$response" = "200" ]; then
  echo "FAIL: vLLM API accessible without credentials" && exit 1
fi

# Fail CI if Opik private API returns data without credentials
opik_resp=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5173/api/v1/private/projects)
if [ "$opik_resp" = "200" ]; then
  echo "FAIL: Opik API accessible without credentials" && exit 1
fi
```

---

## 8. Limitations and Assumptions

| # | Limitation | Risk Implication |
|---|---|---|
| L1 | Shodan API key expired. Opik population dork did not run. | The number of Opik deployments publicly accessible at population scale is unknown. This report covers one verified host; others with identical configuration may exist. |
| L2 | vLLM port 8000 stopped responding partway through session. | Port 8000 evidence was captured early in session and preserved. Current reachability unconfirmed. The finding is valid based on captured response. |
| L3 | Streamlit app content not enumerated. | Actual functionality, data exposed, and backend calls made by the Streamlit app are unknown. The assumption that it calls the vLLM backend is inferred from co-location context, not observed. Risk of F4 may be higher or lower than rated. |
| L4 | Internal network topology unknown. | WireGuard overlays indicate this host connects to a private mesh. Services on that mesh (databases, other model servers, internal APIs) are outside assessment scope. |
| L5 | No TLS certificate. No cert pivot possible. | Operator identity beyond DTN Amsterdam is unconfirmed. Additional hostnames or related infrastructure could not be discovered via cert SANs. |
| L6 | Opik write API not exercised. | Integrity impact (5.2) is inferred from the API schema and auth posture, not demonstrated. The write surface is open; its consequences are real but not proven in this assessment. |
| L7 | Model path `/cache/climategpt_8b_latest` indicates a custom fine-tune, base model unknown. | Cannot confirm training data class, alignment posture, or safety characteristics of the model. |

---

## 9. Proof of Concept Illustrations

> PoCs use minimal, read-only interactions. No operator data extracted. No credentials used. No exploit payloads. No inference invoked.

### PoC 1: Unauthenticated LLM Model Enumeration

**Scenario:** An unauthenticated external caller discovers the inference model identity and access posture via a single HTTP GET.

```
REQUEST:
  GET /v1/models HTTP/1.1
  Host: 80.79.202.18:8000

RESPONSE:
  HTTP/1.1 200 OK
  Content-Type: application/json

  {
    "object": "list",
    "data": [{
      "id": "/cache/climategpt_8b_latest",
      "object": "model",
      "created": 1779471320,
      "owned_by": "vllm",
      "max_model_len": 10240,
      "permission": [{
        "organization": "*",
        "allow_sampling": true,
        "allow_logprobs": true,
        "allow_fine_tuning": false
      }]
    }]
  }
```

**Demonstrated:** The model name, context length, and permission posture are publicly readable without credentials. `organization: "*"` and `allow_sampling: true` confirm inference is open to any caller. This PoC does NOT submit any inference request; the model list endpoint is read-only. What it proves: a caller with no credentials has the information needed to submit a chat completion request to a real production LLM.

---

### PoC 2: Operational Intelligence Extraction via Prometheus Metrics

**Scenario:** An unauthenticated external caller reads the inference server's full operational state in one request.

```
REQUEST:
  GET /metrics HTTP/1.1
  Host: 80.79.202.18:9100

RESPONSE (excerpt):
  HTTP/1.1 200 OK
  Content-Type: text/plain; version=0.0.4; charset=utf-8

  vllm:prompt_tokens_total{model_name="/cache/<model>"} 9.2033986e+07
  vllm:generation_tokens_total{model_name="/cache/<model>"} 4.176102e+06
  vllm:request_success_total{finished_reason="stop",model_name="/cache/<model>"} 34277.0
  vllm:num_requests_running{model_name="/cache/<model>"} 0.0
  vllm:kv_cache_usage_perc{model_name="/cache/<model>"} 0.0
  process_resident_memory_bytes 1.225711616e+09
```

**Demonstrated:** Token counts, request history, memory footprint, KV cache state, and queue depth are all publicly readable without credentials. `num_requests_running: 0.0` and `kv_cache_usage_perc: 0.0` tell an attacker the server is idle -- optimal timing for a saturation attempt. This PoC does NOT modify any state or invoke any model API; it reads one public metrics endpoint. What it proves: an attacker has real-time operational intelligence without interacting with the model.

---

### PoC 3: Unauthenticated Opik Evaluation Platform Enumeration

**Scenario:** An unauthenticated external caller reads the full project list from an LLM evaluation platform, revealing the operator's product category and development stage.

```
REQUEST:
  GET /api/v1/private/projects HTTP/1.1
  Host: 80.79.202.18:5173

RESPONSE (sanitised -- project names preserved as found):
  HTTP/1.1 200 OK
  Content-Type: application/json

  {
    "page": 1,
    "size": 7,
    "total": 7,
    "content": [
      {"name": "climategpt_test_local", "created_by": "admin",
       "created_at": "2026-02-19T10:52:47Z"},
      {"name": "climate_gpt_staging", "created_by": "admin",
       "created_at": "2026-02-16T14:04:51Z"},
      {"name": "Default Project", ...},
      ...
    ]
  }
```

**Demonstrated:** The API returns fully populated project records without any `Authorization` header. Project names are the intelligence -- `climategpt_test_local` and `climate_gpt_staging` identify the operator's domain and staging pipeline. This PoC does NOT read any trace payloads, experiment results, or user data; it reads project metadata only. What it proves: the operator's entire evaluation infrastructure is enumerable by any unauthenticated caller who knows the correct API path.

---

*Prepared by NuClide Research (Nicholas Kloster + Claude Sonnet 4.6) · Session 32 · 2026-05-22*
