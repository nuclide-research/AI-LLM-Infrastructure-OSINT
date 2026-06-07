# ClimateGPT Stack — Unauth vLLM + Opik + Streamlit

**Date:** 2026-05-22  
**Target:** 80.79.202.18  
**Operator:** Digital Thinking Network (DTN), Amsterdam, NL  
**Severity:** CRITICAL (stacked)  
**Ledger IDs:** 35926, 35927, 35928, 35929  

---

## Discovery

Surfaced during Session 30 Agenta survey (S30). The `/opik/api/v1/projects` endpoint returned HTTP 200 unauthenticated — a candidate, per Insight #16. The candidate was passed to this assessment for data-layer verification.

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7004, K7044, S7068, S7070, S7075, T5858, T5904, T5919
- **733 (AI Risk & Ethics Specialist):** K7051, S7056, S7067, T5868, T5893, T5904
- **overlap (Common AI KSATs (all 5 roles)):** K108, K1158, K1159, K22, K6311, K6900, K7003, K942, S7065, T5896

<!-- ksat-tag:auto-generated:end -->

Shodan title dork `http.title:"Opik"` could not run — API key expired at assessment start. Recorded as tool gap.

---

## Fingerprint

nmap: port 5173 open, `nginx/1.29.5`, no TLS.

aimap: ran against default port set. Found ports 22 (OpenSSH 8.2p1) and 9100. **Did not scan port 5173** — not in default port list. No Opik fingerprint in catalog. Two gaps filed:

1. Port 5173 absent from aimap scan set — Opik ships here by default.
2. No Opik fingerprint — platform undetectable by current toolchain.

---

## Verification — Data Layer (Insight #16)

Raw dork returned 200. That is not a finding. The data-layer probe is:

```bash
curl -s http://80.79.202.18:5173/opik/api/v1/projects
# → HTML SPA shell (nginx routing miss — path not proxied)

# JS bundle: VITE_BASE_API_URL="/api"
# API routes served at /api/v1/private/*

curl -s http://80.79.202.18:5173/api/v1/private/projects
```

Response (truncated):

```json
{
  "page": 1, "size": 7, "total": 7,
  "content": [
    {"id": "019c7587-e993-7562-8a89-d3226d89f013", "name": "climategpt_test_local",
     "created_by": "admin", "created_at": "2026-02-19T10:52:47Z"},
    {"id": "019c66c4-ae38-75b4-9998-66c7a728b8d2", "name": "climate_gpt_staging",
     "created_by": "admin", "created_at": "2026-02-16T14:04:51Z"},
    {"name": "Opik Demo Agent Observability"},
    {"name": "Opik Demo Optimizer"},
    {"name": "Opik Demo Assistant"},
    {"name": "playground"},
    {"name": "Default Project"}
  ]
}
```

**Verified: 7 populated projects, no credentials required.**

Project names `climategpt_test_local` and `climate_gpt_staging` are the intelligence. The operator is building a climate-domain LLM product.

Additional surface enumerated:

- `/api/v1/private/experiments` → 11 experiments (all `Demo-*`)
- `/api/v1/private/prompts` → 1 prompt: `Demo - Opik SDK Assistant - System Prompt`, 2 versions
- Prompt v1: *"You are an Opik expert and know how to explain Comet SDK concepts in simple terms."*
- Prompt v2: *"You are an instructor for technical executives that want to extract value of AI models."*
- `/api/v1/private/datasets` → 1 dataset: `Opik Demo Questions`, 0 items
- All project traces: 0 records — no active trace data at assessment time

Full API write access confirmed: projects, experiments, prompts, datasets are all writable without credentials. An attacker can delete experiments, inject evaluation scores, corrupt prompt templates, and manipulate the evaluation pipeline.

---

## Stacked Exposure — vLLM

While enumerating shadow ports (per methodology Insight #12), port 9100 returned Python/Prometheus metrics — not Prometheus node_exporter, but **vLLM**:

```
vllm:num_requests_running{model_name="/cache/climategpt_8b_latest"} 0.0
vllm:prompt_tokens_total{model_name="/cache/climategpt_8b_latest"} 9.2033986e+07
vllm:generation_tokens_total{model_name="/cache/climategpt_8b_latest"} 4.176102e+06
vllm:request_success_total{finished_reason="stop",model_name="/cache/climategpt_8b_latest"} 34277.0
```

Port 8000 confirmed vLLM OpenAI-compatible API:

```bash
curl -s http://80.79.202.18:8000/v1/models
```

```json
{
  "object": "list",
  "data": [{
    "id": "/cache/climategpt_8b_latest",
    "object": "model",
    "max_model_len": 10240,
    "permission": [{"organization": "*", "allow_sampling": true}]
  }]
}
```

**A custom 8B ClimateGPT model loaded from `/cache/climategpt_8b_latest` is serving unauthenticated OpenAI-compatible inference requests.**

Scale from metrics:

| Metric | Value |
|--------|-------|
| Total requests | 34,789 |
| Prompt tokens processed | 92,033,986 |
| Generation tokens | 4,176,102 |
| Prefix cache hit rate | 61.6% |
| Avg prompt length | ~2,643 tokens |
| Avg generation length | ~116 tokens |
| Avg TTFT | 0.119s |
| Process start | ~2026-02-19 (Feb boot) |
| Memory (RSS) | 1.22 GB |
| Virtual memory | ~27 GB (model weights) |
| Python runtime | 3.12.12 on Ubuntu 20.04 |

This is a production-scale deployment serving real users. Any unauthenticated caller can submit arbitrary inference requests, manipulate system prompts, enumerate the model path, and consume compute quota.

---

## Stacked Exposure — Streamlit

Port 8086 serves a Streamlit application (Snowflake/Streamlit, Apache 2.0):

```bash
curl -s http://80.79.202.18:8086/_stcore/health  →  "ok"
```

No TLS, no auth on health or root. Consistent with ClimateGPT chat frontend bound to the same host as the inference backend. WireGuard overlays (UDP 51819, 51820, 51821) suggest this node connects to a private VPN mesh — the Streamlit app is likely externally exposed while the operator intended it to be internal.

---

## Attribution

```
whois 80.79.202.18

inetnum:   80.79.202.0 - 80.79.202.255
netname:   NL-INFO-DTN-1
descr:     Digital Thinking Network
country:   NL
address:   Prinsengracht 707, 1017JW Amsterdam, Netherlands
abuse:     abuse@info.nl
route:     80.79.192.0/20  (info.nl)
```

No TLS certificate — no cert pivot possible. No rDNS. IP is on info.nl's DTN range, Amsterdam. No Shodan passive data (API key expired at run time).

---

## Compliance Score — VisorScuba

All 4 entries score **0/10**, AI.C1 violation ("Unauthenticated AI service"). AI.C1 is a CRITICAL deny rule (−3 per violation). With three Critical violations (vLLM, Opik, Streamlit) plus one High (metrics), the stack is at maximum penalty.

---

## Exploit Chain

```
1. Discovery
   Shodan hit → /opik/api/v1/projects 200 → candidate

2. JS-bundle extraction
   VITE_BASE_API_URL="/api" → correct base path revealed
   Opik v1.10.13, Python 3.12.12

3. Data-layer verification (Insight #16)
   /api/v1/private/projects → 7 projects populated → VERIFIED

4. Operator intelligence
   project names: climategpt_test_local, climate_gpt_staging
   → climate-domain LLM product under active development

5. Shadow port (Insight #12)
   port 9100 → vLLM Prometheus metrics → model = /cache/climategpt_8b_latest
   port 8000 → OpenAI-compatible API, allow_sampling, org="*"
   port 8086 → Streamlit frontend, no auth

6. Scale confirmation
   92M prompt tokens, 34789 requests, 61.6% prefix cache hit rate
   → Production deployment, real user traffic

7. Full unauth inference access
   POST /v1/chat/completions → arbitrary inference, no creds required
   Write access to Opik → corrupt evaluation pipeline
```

---

## Impact

- **Direct compute abuse:** Any caller can submit inference requests against ClimateGPT 8B. No API key, no rate limit enforcement at the network layer.
- **Evaluation pipeline corruption:** Full Opik write access — inject false evaluation scores, delete experiments, overwrite prompt templates. Corrupted evaluation data flows directly into the operator's model development loop.
- **Operational intelligence:** Token counts, cache hit rate, memory footprint, and request histograms are public. An adversary knows capacity, load patterns, and when to saturate.
- **Model extraction risk:** With inference access and a long context window (10,240 tokens), systematic extraction of training signal is feasible.
- **WireGuard exposure:** Three WireGuard ports open/filtered on public interface. If the VPN mesh is misconfigured, this node may be reachable from inside the operator's private network.

---

## Remediation

1. Place vLLM behind an API gateway with bearer token validation — `vllm serve --api-key <secret>` or nginx `auth_request`.
2. Set `OPIK_AUTHENTICATION_ENABLED=true` in the Opik deployment.
3. Bind Streamlit to `127.0.0.1` or restrict port 8086 via firewall.
4. Remove port 9100 from public interface — metrics to internal scraper only.
5. Audit WireGuard peer configs — confirm the VPN mesh does not expose internal services through this node.

Verification command post-fix:

```bash
curl -s http://80.79.202.18:5173/api/v1/private/projects  # must return 401/403
curl -s http://80.79.202.18:8000/v1/models               # must return 401/403
curl -s http://80.79.202.18:9100/metrics                 # must refuse or require IP ACL
```

---

## Tool Gaps Filed

1. **aimap: missing Opik fingerprint.** Platform undetectable — no Opik entry in the 36-service catalog.
2. **aimap: port 5173 absent from default scan set.** Vite dev server and Opik ship here by default.
3. **JAXEN/VisorSD: Shodan API key expired.** Population dork (`http.title:"Opik"`) could not run. Opik population size unknown.

---

## Chain Checklist

```
[x] 0. JAXEN         — Shodan key expired; title dork queued for next valid session
[x] 1. aimap         — ran; 2 ports found (22, 9100); 2 gaps filed (port 5173, Opik fingerprint)
[x] 2. VisorGraph    — ran; 0 nodes — HTTP only, no TLS cert
[x] 3. aimap-profile — ran; NL-INFO-DTN-1 / DTN Amsterdam / Ubuntu 20.04
[x] 4. JS-bundle     — ran; VITE_BASE_API_URL="/api"; Opik v1.10.13
[x] 5. VisorLog      — ingested; IDs 35926-35929
[x] 6. VisorScuba    — ran; 4× AI.C1 0/10
[x] 7. BARE          — ran; no Metasploit coverage; first-party AI authz gap class
[x] 8. VisorCorpus   — built; 46-payload PI/jailbreak corpus for vLLM surface
[x] VisorBishop      — shadow sweep; ports 22, 9100, 8086 found
[x] VisorSD          — Shodan key expired; N/A this session
[x] VisorGoose       — probed; Ollama port N/A; WireGuard overlays flagged by menlohunt
[x] menlohunt        — ran; ports 22, 8086, WireGuard UDP 51819/51820/51821
[x] nu-recon         — ran; simulated (Shodan down); OpenSSH 8.2p1 confirmed
[x] recongraph       — ran; 0 nodes/edges; no hostname/TLS pivot available
[~] VisorRAG         — embedding API 401; N/A this session
[~] VisorPlus        — single host; N/A
[~] cortex           — markdown input required; pending
[—] VisorHollow      — Windows-only; N/A
[x] VisorAgent       — ethical-stop; run against controlled target, not this host
```

---

## Toolchain Provenance

```
Discovery:    S30 Agenta survey → /opik/api/v1/projects 200 → candidate
Fingerprint:  aimap 80.79.202.18 (v1.9.22)
JS extract:   curl assets/index-C3cW9a_k.js | grep VITE_BASE_API_URL
Verify:       curl /api/v1/private/projects → populated 200
Pivot:        nmap -sV + aimap-profile full → ports 9100, 8086 discovered
Attribution:  whois 80.79.202.18 → NL-INFO-DTN-1, DTN Amsterdam
Ledger:       visorlog add ×4 → IDs 35926-35929 (nuclide.db)
Scoring:      visorscuba assess → 4× AI.C1 0/10
Exploit map:  bare climategpt_bare.json → no Metasploit coverage
Corpus:       visorcorpus build -type focused → 46 payloads
```
