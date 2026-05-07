# Chinese Primary School: Cloud Proxy Subscriptions + Credential Leak

_NuClide Research · 2026-05-01_

---

## Summary

An Experimental Primary School in China (Shodan org: "Experimental Primary School") is running Ollama with three cloud proxy subscriptions, DeepSeek V4 Pro, Devstral-2 (123B), and MiniMax M2.7, alongside a RAG pipeline (BGE-M3 embedding). All three cloud proxies return 401 with the same credential leak: Ollama Connect account `simmir2077-Rack-Server`. Unauthenticated, publicly accessible.

This appears to be a K-12 educational environment, the first primary/elementary school in this research set with cloud AI subscriptions exposed.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 122.225.62.2 |
| rDNS |, (NXDOMAIN) |
| Org | Experimental Primary School (China) |
| Country | China |
| Open ports | 11434 (Ollama, **public**) |

---

## Models

| Model | Size | Type | Cred Leak |
|---|---|---|---|
| deepseek-v4-pro:cloud | 0 GB | ☁️ Cloud proxy | `simmir2077-Rack-Server` |
| devstral-2:123b-cloud | 0 GB | ☁️ Cloud proxy | `simmir2077-Rack-Server` |
| minimax-m2.7:cloud | 0 GB | ☁️ Cloud proxy | `simmir2077-Rack-Server` |
| bge-m3:latest | 1 GB | Embedding, RAG |, |
| qwen2.5:7b | 4 GB | Local |, |
| llama3.2:3b | 1 GB | Local |, |

---

## Credential Leak

All three cloud proxies return the same Ollama Connect account in the 401 response:

```json
{
  "error": "unauthorized",
  "signin_url": "https://ollama.com/connect?name=simmir2077-Rack-Server&key=<base64>"
}
```

- **Username:** `simmir2077-Rack-Server`
- **SSH Public Key:** `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIILnEvW9tXqugnjfQQ1aH3Lk...`

The `Rack-Server` suffix suggests a branded server appliance rather than a personal workstation. All three subscriptions (DeepSeek Pro, Devstral-2 123B, MiniMax M2.7) are registered to the same account.

---

## Findings

**F1, Three Cloud Proxy Credential Leaks on K-12 Network (CRITICAL):** Three cloud AI subscriptions (DeepSeek, Mistral, MiniMax) exposed with operator credentials accessible to any internet caller. Unprecedented finding in a primary school network.

**F2, RAG Pipeline Injection (HIGH):** `bge-m3` embedding model indicates an active RAG pipeline. CVE-2025-63389 injection affects document-augmented responses.

**F3, Model Injection (HIGH):** All models injectable via CVE-2025-63389.

---

## Context

This is the only primary (K-12) institution in this research set with AI cloud subscriptions exposed. The deployment suggests administrative or experimental AI use on a school network, potentially a smart campus initiative or teacher tools, without proper network security controls.

---

## Disclosure

- **Discovered:** 2026-05-01
- **Status:** Pending outreach, unclear disclosure channel for Chinese K-12
