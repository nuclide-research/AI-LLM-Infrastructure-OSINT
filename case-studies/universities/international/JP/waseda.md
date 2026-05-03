# Waseda University — Account Takeover (`tokoko`), Custom DeepSeek Academic/JP Models, qwen3-vl:235b

_NuClide Research · 2026-05-03_

---

## Summary

Waseda University (`tokoko.human.waseda.ac.jp`, 133.9.184.47) exposes Ollama with 10 models including a live Ollama Connect account takeover. The username is `tokoko` — a human-chosen name, not a container ID or MAC address, indicating deliberate (though insecure) account registration. Two custom fine-tuned models are present: `deepseek-r1-70b-academic:latest` and `deepseek-r1-70b-jp:latest` — suggesting internal Waseda research customization of DeepSeek R1 70B for academic and Japanese-language use. Also present: `qwen3-vl:235b` (235B vision-language model) and `deepseek-v4-pro:cloud`.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 133.9.184.47 |
| Hostname | tokoko.human.waseda.ac.kr |
| Organization | Japan Network Information Center (JPNIC — AS2527) |
| Institution | Waseda University, Tokyo, Japan |
| Department | Human Sciences (`.human.waseda.ac.jp`) |
| Ollama version | 0.13.4 |
| Open port | 11434 (public, no auth) |

---

## Account Takeover

```json
{
  "error": "unauthorized",
  "signin_url": "https://ollama.com/connect?name=tokoko&key=<base64>"
}
```

- **Username:** `tokoko` — **human-readable name, deliberately set**
- **SSH pubkey:** `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJsFYwODwN1Qk5qyciNtJANLeEvm/PIrSTn0Srhuzrq1`

Unlike most takeover targets where the username is an auto-generated MAC address or container ID, `tokoko` was explicitly chosen. The operator consciously registered an Ollama Connect account under this name but left the port publicly accessible.

---

## Model Inventory

| Model | Size | Notes |
|---|---|---|
| `deepseek-r1-70b-academic:latest` | ~40 GB | **Custom fine-tune — academic research variant** |
| `deepseek-r1-70b-jp:latest` | ~40 GB | **Custom fine-tune — Japanese-language variant** |
| `qwen3-vl:235b` | ~120 GB | Qwen3 235B vision-language — frontier scale |
| `qwen2.5:72b` | ~41 GB | Default Alibaba system prompt |
| `deepseek-r1:70b` | ~40 GB | Base DeepSeek R1 70B |
| `deepseek-r1:32b` | ~19 GB | DeepSeek R1 32B |
| `qwen3:32b` | ~19 GB | Qwen3 32B |
| `qwen2.5vl:latest` | ~14 GB | Vision-language model |
| `qwen2.5:32b` | ~19 GB | Default Alibaba system prompt |
| `deepseek-v4-pro:cloud` | 0 GB | ☁️ Cloud proxy — account takeover |

---

## Findings

### F1 — Deliberate Account Name + Takeover (CRITICAL)

`tokoko` is not auto-generated — it was chosen by the operator. The same person registered the Ollama Connect account, chose a personal username, and left port 11434 bound to 0.0.0.0. The live claim URL means any actor visiting the URL inherits full control over the DeepSeek V4 Pro cloud subscription.

### F2 — Custom Waseda Research Models (HIGH)

`deepseek-r1-70b-academic:latest` and `deepseek-r1-70b-jp:latest` are fine-tuned variants of DeepSeek R1 70B. These are internal research artifacts — not published on Ollama Hub under standard names — indicating active NLP research at Waseda's Human Sciences department. Both models are injectable and fully accessible to unauthenticated callers, leaking the existence and outputs of non-public research fine-tunes.

### F3 — qwen3-vl:235b Frontier Vision-Language Model (HIGH)

`qwen3-vl:235b` is a 235B-parameter vision-language model. Accessible at Waseda's GPU compute cost, no authentication, no rate limit.

### F4 — CVE-2025-63389 (CRITICAL)

v0.13.4. All 10 models injectable via unauthenticated `/api/create`.

---

## Waseda Human Sciences Department Context

The `.human.waseda.ac.jp` hostname places this server in Waseda's Faculty/Graduate School of Human Sciences (人間科学部・大学院人間科学研究科). Japanese-language and academic fine-tunes of DeepSeek R1 suggest NLP research involving Japanese text or academic corpus training. The `tokoko` persona name may correspond to a researcher or lab identity.

---

## Remediation

```bash
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

Change Ollama Connect username and rotate SSH key via ollama.com settings.

---

## Disclosure

- **Discovered:** 2026-05-03
- **Status:** Pending outreach to Waseda IT / JPCERT (jpcert.or.jp)
- **Contact:** it-security@list.waseda.jp (or Waseda security team)
