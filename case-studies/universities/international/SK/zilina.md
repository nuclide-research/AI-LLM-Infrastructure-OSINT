# University of Žilina — Student Laptop with 3 Free-Tier Cloud Proxies (200 OK)

_NuClide Research · 2026-05-01_

---

## Summary

A student laptop at the University of Žilina (Slovakia, Faculty of Mechanical Engineering) has Ollama bound to 0.0.0.0 with three Ollama Connect cloud proxy models all returning **200 OK** without credentials. The cloud proxies give any internet caller unauthenticated inference access to Devstral-2 (123B), DeepSeek V3.1 (671B), and Qwen3 Coder (480B) at the operator's expense.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 158.193.144.224 |
| rDNS | `LAPTOP-N7ADDUK8.kst.fri.uniza.sk` |
| Org | University of Žilina |
| Faculty | Mechanical Engineering (kst.fri.uniza.sk) |
| Country | Slovakia |
| Open ports | 11434 (Ollama — **public**) |

---

## Models

| Model | Size | Type | 200 OK? |
|---|---|---|---|
| devstral-2:123b-cloud | 0 GB | ☁️ Cloud proxy | **YES — 48 tokens** |
| deepseek-v3.1:671b-cloud | 0 GB | ☁️ Cloud proxy | **YES — streaming** |
| qwen3-coder:480b-cloud | 0 GB | ☁️ Cloud proxy | **YES — 10 tokens** |
| deepseek-r1:7b | 4 GB | Local | — |
| phi3:latest | 2 GB | Local | — |
| glm-4.7-flash:latest | 17 GB | Local | — |
| llama3.2:3b | 1 GB | Local | — |
| smollm2:135m | 0 GB | Local | — |
| llama3:latest | 4 GB | Local | — |
| codellama:latest | 3 GB | Local | — |

**Devstral** is Mistral's code-specialized frontier model. **DeepSeek V3.1 671B** and **Qwen3 Coder 480B** are among the largest models available via cloud proxy. All three are **free-tier** Ollama cloud models that do not require credentials — any caller can run unlimited inference.

---

## Findings

### F1 — Three Free-Tier Cloud Proxies, 200 OK (CRITICAL)

All three cloud proxy models return full inference responses without authentication. Confirmed token consumption during research:

```bash
curl -X POST http://158.193.144.224:11434/api/chat \
  -d '{"model":"devstral-2:123b-cloud","messages":[{"role":"user","content":"hi"}],"stream":false}'
# 200 OK, 48 tokens returned at operator expense

curl -X POST http://158.193.144.224:11434/api/chat \
  -d '{"model":"qwen3-coder:480b-cloud","messages":[{"role":"user","content":"hi"}],"stream":false}'
# 200 OK, 10 tokens returned at operator expense
```

### F2 — Laptop Exposed via Docker / 0.0.0.0 Binding (HIGH)

Hostname `LAPTOP-N7ADDUK8.kst.fri.uniza.sk` confirms this is a student or researcher's personal laptop connected to the campus network. Ollama bound to `0.0.0.0` routes the port to the internet when the machine is on a campus-facing IP.

### F3 — Model Injection (HIGH)

All 10 models injectable via CVE-2025-63389 — no patch available.

---

## Remediation

```bash
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

---

## Disclosure

- **Discovered:** 2026-05-01
- **Status:** Pending outreach to UNIZA IT / SK-CERT

---

## Second Node: IIKT Main Server (158.193.146.185)

A second University of Žilina machine from the Institute of Information and Communication Technologies (IIKT) has 27 local models and **no cloud proxies** — large reasoning and coding models accessible without authentication:

Key models: `Qwen3-30B` (17GB), `Qwen3-coder-30B` (20GB), `gemma3n:e4b` (7GB), `phi4-reasoning:plus` (10GB), `qwen3:30b` (17GB), 22 additional models.

Both the student laptop (158.193.144.224) and the institutional IIKT server (158.193.146.185) have Ollama bound to 0.0.0.0. The laptop carries the critical cloud proxy exposure; the IIKT server carries the large local model inventory.
