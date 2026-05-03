# Forskningsnettet (Danish Research and Education Network) — Two Nodes, v0.3.0 Ancient + v0.22.0 Current

_NuClide Research · 2026-05-03_

---

## Summary

Two Ollama nodes in Aalborg, Denmark on AS1835 Forskningsnettet (the Danish national research and education network). One node (130.225.39.157) runs Ollama **v0.3.0** — a pre-release build from late 2023, making it one of the oldest Ollama deployments in this sweep. The second (130.225.39.201) runs the current v0.22.0. Both are unauthenticated and injectable. Neither has rDNS configured.

---

## Infrastructure

| Node | IP | Hostname | Version | Models | Notes |
|---|---|---|---|---|---|
| Node A | 130.225.39.201 | — | 0.22.0 | 3 | Current release |
| Node B | 130.225.39.157 | — | 0.3.0 | 4 | **Ancient — pre-0.6 era** |

Both: AS1835 Forskningsnettet — Danish Network for Research and Education. City: Aalborg, North Denmark (57.0480, 9.9187). No rDNS on either.

---

## Model Inventory — Node A (130.225.39.201, v0.22.0)

| Model | Notes |
|---|---|
| `gemma3:27b` | Google Gemma3 27B |
| `nemotron3:33b` | NVIDIA Nemotron-3 33B |
| `llama3.2:3b` | Meta Llama 3.2 3B |

---

## Model Inventory — Node B (130.225.39.157, v0.3.0)

| Model | Notes |
|---|---|
| `smollm2:135m` | **System prompt:** `"You are a helpful AI assistant named SmolLM, trained by Hugging Face"` (default unmodified) |
| `llama3.2:3b` | — |
| `llama3.2:latest` | — |

---

## Findings

### F1 — v0.3.0 Ancient Deployment (HIGH)

Node B (130.225.39.157) runs Ollama v0.3.0 — a pre-release version from the v0.x era (pre-0.6.0, late 2023). This version predates all security audit history for Ollama, including the model management API changes introduced in v0.1.x and later hardening. CVE-2025-63389 applies (all versions, no patch); additional CVEs from the 2.5-year gap of unpatched versions may also apply.

### F2 — No rDNS, Institutional Attribution Unknown (MEDIUM)

Neither node has reverse DNS. Both are in the Forskningsnettet 130.225.39.0/24 block. The operator institution is not identifiable from public data — could be Aalborg University (AAU), a regional research institute, or another Forskningsnettet tenant.

### F3 — CVE-2025-63389 (CRITICAL)

All 6 models across both nodes are injectable via unauthenticated `/api/create`.

### F4 — Unauthenticated gemma3:27b + nemotron3:33b (MEDIUM)

Node A serves a 27B and 33B model to any internet actor. No cloud proxy involvement; pure local compute drain.

---

## Remediation

```bash
# Both nodes
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama

# Node B: update immediately
# Current: v0.3.0 (2023) → target v0.22.0
ollama --version  # verify post-update
```

---

## Disclosure

- **Discovered:** 2026-05-03
- **Status:** Pending outreach to Forskningsnettet NOC / CERT (dk-cert.dk or Forskningsnettet abuse contact)
