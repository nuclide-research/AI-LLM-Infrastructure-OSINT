---
to: abuse@hetzner.com
cc: abuse@nuclide-research.com
severity: HIGH
ip: 65.108.197.157
institution: Hetzner DE — unauthenticated LiteLLM proxy fronting internal Ollama + 4 RunPod GPU pods; admin endpoints + virtual key leaked
status: DRAFT
outcome: sent
date: 2026-05-06
---

**To:** abuse@hetzner.com
**Cc:** abuse@nuclide-research.com
**Subject:** Unauthenticated LiteLLM Proxy on Hetzner customer host (65.108.197.157) — 8 model aliases, internal Ollama hostname leaked, RunPod-backed GPU compute fully burnable, virtual-key disclosed

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-06

**Re:** Unauthenticated LiteLLM Proxy v1.x on Hetzner customer host
**IP:** 65.108.197.157 (rDNS `static.157.197.108.65.clients.your-server.de`)
**Severity:** HIGH

---

I'm an independent security researcher conducting good-faith AI infrastructure research under the NuClide Research umbrella (CISA disclosures CVE-2025-4364, ICSA-25-140-11). This is an unsolicited coordinated-disclosure notification.

---

## Summary

Hetzner customer host `65.108.197.157` is running an unauthenticated **LiteLLM Proxy** on port 4000. The proxy fronts:

- The operator's local Ollama CPU instance (internal hostname `ollama-cpu`) with 4 models loaded
- 4 RunPod GPU pods, each fronting a different premium model (DeepSeek-V4, StepFun step-3.5-flash, Qwen3-VL-72B-AWQ, StepFun step-3-256k)

The proxy's admin endpoints (`/v1/model/info`, `/v1/models`, `/user/info`, `/global/spend`, `/spend/tags`) are reachable without authentication. The proxy's `/v1/chat/completions` endpoint accepts requests without authentication and returns valid completions — i.e., **anyone with the IP can consume the operator's compute (local Ollama CPU + RunPod GPU minutes) for free**.

A LiteLLM virtual key was disclosed via `/user/info`:

```json
{
  "token": "ddaffcaea6b1dde352a4dd09d92a43cde54d8e468532c4cdd34fd51ac23d1836",
  "key_name": "sk-...Rnlw",
  "created_at": "2026-02-23T15:10:31",
  "updated_at": "2026-03-15T03:51:41"
}
```

This key was observed in the public response — not used for authentication. The key should be rotated regardless.

The host has been in NuClide's ledger since the original Ollama Cloud survey (2026-05-02) as a billing-theft target; the LiteLLM proxy was surfaced today via cross-survey-correlation probing of port 4000 across the existing ledger IPs. Full case study at:

https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/commercial/hetzner-65-108-litellm-runpod-2026-05-06.md

## Reproduction (non-destructive)

```bash
$ curl -s 'http://65.108.197.157:4000/health/liveness'
"I'm alive!"

$ curl -s 'http://65.108.197.157:4000/v1/models' | jq '.data[] | .id'
"local-primary"
"local-backup"
"local-vision"
"gpu-coder"
"gpu-math"
"gpu-vision"
"gpu-longctx"
"qwen25-14b"

$ curl -s 'http://65.108.197.157:4000/model/info' | jq '.data[] | {model_name, api_base: .litellm_params.api_base}'
{ "model_name": "local-primary",  "api_base": "http://ollama-cpu:11434" }
{ "model_name": "local-backup",   "api_base": "http://ollama-cpu:11434" }
{ "model_name": "local-vision",   "api_base": "http://ollama-cpu:11434" }
{ "model_name": "gpu-coder",      "api_base": "https://api.runpod.ai/v2/{RUNPOD_DEEPSEEK_V4_ID}/openai/v1" }
{ "model_name": "gpu-math",       "api_base": "https://api.runpod.ai/v2/{RUNPOD_STEP35_FLASH_ID}/openai/v1" }
{ "model_name": "gpu-vision",     "api_base": "https://api.runpod.ai/v2/{RUNPOD_QWEN_VL72_ID}/openai/v1" }
{ "model_name": "gpu-longctx",    "api_base": "https://api.runpod.ai/v2/{RUNPOD_STEP3_256K_ID}/openai/v1" }
{ "model_name": "qwen25-14b",     "api_base": "http://ollama-cpu:11434" }

$ # Functional inference verified once with max_tokens=1 (single-token PoC):
$ curl -s -X POST -H 'Content-Type: application/json' \
    -d '{"model":"qwen25-14b","messages":[{"role":"user","content":"OK"}],"max_tokens":1}' \
    'http://65.108.197.157:4000/v1/chat/completions'
{"id":"chatcmpl-...","object":"chat.completion","model":"qwen25-14b",
 "choices":[{"finish_reason":"stop","index":0,
             "message":{"content":"Hello","role":"assistant"}}]}
```

The single completion above is the only inference call NuClide made. No further requests against the GPU-backed models were issued. The disclosure-PoC consumed the operator's local Ollama CPU for ~35 prompt + 1 completion token.

## Why this matters

For the customer (operator):

- **RunPod billing theft.** Each call to `gpu-coder` / `gpu-math` / `gpu-vision` / `gpu-longctx` invokes RunPod's per-second pod billing. A 72B-class GPU pod runs ~$1–3/hr; sustained external traffic against the gateway directly translates to operator GPU spend.
- **Internal architecture leakage.** The hostname `ollama-cpu` and the RunPod pod-ID env templating (`{RUNPOD_DEEPSEEK_V4_ID}` etc.) reveal the operator's internal Docker / K8s service-discovery layout.
- **Virtual key disclosed.** Even though the proxy is currently auth-off (anyone hits `/v1/chat/completions` directly), the disclosed key indicates the operator has configured key-based auth in LiteLLM. The key should be rotated as part of remediation.
- **Active production traffic.** `/spend/tags` shows real client requests across 6+ distinct user-agents (Edge browser, curl, Python SDK, Go HTTP client, Node undici). The gateway is being used by real consumers.

For Hetzner abuse:

- Customer needs notification. The fixes are operator-side and cheap (LiteLLM has built-in master-key auth via `LITELLM_MASTER_KEY` env var). The customer is reachable through Hetzner's standard customer-channel.

## Remediation (for the customer)

Three fixes (any one closes the exposure; all three is best practice):

```bash
# 1. Enable LiteLLM's master-key auth (one env var):
export LITELLM_MASTER_KEY="sk-<random-32-bytes>"
# Restart the proxy. All requests now require Bearer <key>. The disclosed
# virtual key (ddaffcaea6...23d1836) should be rotated via /key/regenerate
# before re-enabling.

# 2. Restrict the admin endpoints separately:
# Set general_settings.disable_admin_endpoints in litellm config.yaml
# Or: ufw deny 4000/tcp on the host and reverse-proxy through nginx with
# auth at the proxy layer.

# 3. Bind LiteLLM to localhost-only (since `ollama-cpu` is internal anyway):
# In docker-compose or run command:
#   --host 127.0.0.1 --port 4000
# Then reach it via SSH tunnel or VPN, not the public IP.
```

For the disclosed virtual key: rotate via the LiteLLM admin API:
```
POST /key/regenerate -H 'Authorization: Bearer <master-key>'
     -d '{"key": "ddaffcaea6b1dde352a4dd09d92a43cde54d8e468532c4cdd34fd51ac23d1836"}'
```

## Reference

LiteLLM auth documentation: https://docs.litellm.ai/docs/proxy/virtual_keys
LiteLLM master-key setup: https://docs.litellm.ai/docs/proxy/quick_start#step-2-make-a-test-request

NuClide LLM Gateways cross-cloud survey context (1,899 confirmed unauth gateways across DO/Hetzner/Vultr/Scaleway/OVH/Linode):
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/commercial/llm-gateways-cloud-survey-2026-05.md

Happy to coordinate verification or extract additional traffic-pattern detail if Hetzner abuse needs it for the customer notification.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
