---
institution: National Taiwan University (CSIE)
ip: 140.112.91.209
to: security@ntu.edu.tw
severity: HIGH
status: DRAFT
outcome: sent
date: 2026-05-03
---

**To:** security@ntu.edu.tw
**Subject:** Unauthenticated AI inference endpoint, NTU CSIE (mvnl-nas.csie.ntu.edu.tw, 140.112.91.209)

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-03

**Re:** Unauthenticated vLLM inference endpoint (Llama-3.3-70B-FP8), NTU CSIE MVNL Lab
**IP / Host:** 140.112.91.209 / mvnl-nas.csie.ntu.edu.tw
**Port:** 8080/tcp (public)
**Severity:** HIGH

---

I'm an independent security researcher. I hold CISA disclosures CVE-2025-4364 and ICSA-25-140-11 and conduct good-faith AI infrastructure research under the NuClide Research umbrella. This is an unsolicited disclosure, no engagement exists with your organization, and I have not accessed, modified, or exfiltrated any data beyond what was necessary to confirm the exposure.

---

## Summary

A machine in CSIE's MVNL Lab (`mvnl-nas.csie.ntu.edu.tw`, 140.112.91.209) is running a vLLM inference server on port 8080 without authentication. The server hosts `nvidia/Llama-3.3-70B-Instruct-FP8`, a 70-billion-parameter instruction model, across two tensor-parallel GPU engines, accessible to any internet actor.

---

## Infrastructure

| Field | Value |
|-------|-------|
| IP | 140.112.91.209 |
| Hostname | mvnl-nas.csie.ntu.edu.tw |
| vLLM version | 0.18.2rc1.dev73+gdb7a17ecc |
| Model | `nvidia/Llama-3.3-70B-Instruct-FP8` |
| Engines | 2 (tensor-parallel multi-GPU) |
| max_model_len | 6,000 tokens |
| Port | 8080/tcp, **no authentication** |

---

## Exposure

```bash
curl http://mvnl-nas.csie.ntu.edu.tw:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"nvidia/Llama-3.3-70B-Instruct-FP8",
       "messages":[{"role":"user","content":"Hello"}],
       "max_tokens":100}'
```

Confirmed: inference executed without credentials. Additionally, `GET /metrics` returns unauthenticated Prometheus telemetry including request counts, token volumes, and per-engine latency distributions.

**Usage at probe time:** 237 completed requests, 450,604 prompt tokens processed.

---

## Remediation

```bash
# Bind to localhost:
vllm serve nvidia/Llama-3.3-70B-Instruct-FP8 \
  --host 127.0.0.1 --port 8080 \
  --tensor-parallel-size 2

# Or add API key authentication:
vllm serve nvidia/Llama-3.3-70B-Instruct-FP8 \
  --api-key <secret> \
  --tensor-parallel-size 2
```

---

Note: I previously disclosed a separate exposure at `g1pc2n108.g1.ntu.edu.tw` (140.112.233.108), Ollama with 11 vision models, to this same address. If that disclosure was received and acted on, this new finding on the CSIE side of campus requires the same remediation.

Please acknowledge receipt.

Nicholas Kloster  
nicholas@nuclide-research.com  
nuclide-research.com
