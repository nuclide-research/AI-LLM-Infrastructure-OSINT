# Pemerintah Provinsi Kalimantan Utara — Account Takeover, Claude-Distilled Model

_NuClide Research · 2026-05-02_

---

## Summary

The North Kalimantan Province Government (Pemerintah Provinsi Kalimantan Utara) exposes an Ollama node at `ip-103-156-110-80.kaltaraprov.go.id` (103.156.110.80). The node runs cloud proxy subscriptions and a live account takeover URL. Notable: one local model is a Qwen3.5-27B fine-tuned via knowledge distillation from Claude 4.6 Opus, running on a provincial government server.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 103.156.110.80 |
| Hostname | ip-103-156-110-80.kaltaraprov.go.id |
| Organization | Pemerintah Provinsi Kalimantan Utara |
| Network | `.kaltaraprov.go.id` (North Kalimantan Province Government) |
| Country | Indonesia |
| Ollama version | 0.13.4 |
| Open port | 11434 (public) |

---

## Model Inventory

| Model | Notes |
|---|---|
| `deepseek-v4-pro:cloud` | Cloud proxy — **account takeover** |
| `minimax-m2.7:cloud` | Cloud proxy |
| `aliafshar/gemma3-it-qat-tools:27b` | Gemma 3 27B with tool-calling support |
| `hf.co/Jackrong/Qwen3.5-27B-Claude-4.6-Opus-Reasoning-Distilled-GGUF:Q3_K_M` | **Claude 4.6 Opus reasoning distillate** |
| `llama3.2:3b` | Local 3B model |
| `smollm2:135m` | SmolLM — default system prompt |

---

## Findings

### F1 — Account Takeover via Live Claim URL (CRITICAL)

Querying `deepseek-v4-pro:cloud` returns a live Ollama Connect claim URL:

```json
{
  "error": "unauthorized",
  "signin_url": "https://ollama.com/connect?name=7a3686b3df54&key=<base64>"
}
```

- **Username:** `7a3686b3df54` (MAC address / container ID)
- **SSH pubkey:** `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAILmUNnGe5hcVp/9f8nTolAN49G+s1RbNMN5uYm1Zfc8y`

### F2 — Claude 4.6 Opus Reasoning Distillate on Government Server (HIGH)

`Jackrong/Qwen3.5-27B-Claude-4.6-Opus-Reasoning-Distilled-GGUF` is a Qwen3.5-27B model fine-tuned to replicate the reasoning patterns of Claude 4.6 Opus. Running on a provincial government IP at Q3_K_M quantization (approx. 11–13GB). This model is accessible without authentication to any internet actor.

### F3 — Tool-Calling Model Exposed (HIGH)

`gemma3-it-qat-tools:27b` has function-calling capability. Tool-enabled models on unauthenticated government infrastructure expand the injection surface — attacker can inject a system prompt that chains tool calls to government resources.

### F4 — CVE-2025-63389 Injectable (CRITICAL)

v0.13.4. All six models injectable via unauthenticated `/api/create`.

---

## Remediation

```bash
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

---

## Disclosure

- **Discovered:** 2026-05-02
- **Status:** Pending outreach to Dinas Kominfo Kalimantan Utara / Pemprov Kaltara
