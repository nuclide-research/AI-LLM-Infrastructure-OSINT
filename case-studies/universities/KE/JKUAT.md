# Jomo Kenyatta University of Agriculture and Technology — Cloud Proxy Exposure

_NuClide Research · 2026-05-01_

---

## Summary

Jomo Kenyatta University of Agriculture and Technology (JKUAT), Kenya, is running an Ollama instance on campus with a MiniMax cloud proxy subscription publicly accessible without authentication. One local model alongside the cloud proxy. No credential leak detected on this instance.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 41.89.8.169 |
| rDNS | — (NXDOMAIN) |
| Org | Jomo Kenyatta University of Agriculture and Technology (KENET) |
| Country | Kenya |
| Open ports | 11434 (Ollama — **public**) |

JKUAT connects to the internet via KENET (Kenya Education Network). The IP block (`41.89.8.x`) is assigned to JKUAT's main campus.

---

## Models

| Model | Size | Type |
|---|---|---|
| minimax-m2.7:cloud | 0 GB | ☁️ Cloud proxy — MiniMax API |
| llama3.2:3b | 1 GB | Local |

---

## Findings

**F1 — Unauthenticated Ollama API (HIGH):** Port 11434 publicly accessible. No authentication on `/api/tags`, `/api/show`, or `/api/create`.  
**F2 — Cloud Proxy Subscription Exposed (MEDIUM):** `minimax-m2.7:cloud` accessible to any internet caller. 401 returned without credential leak on this instance.  
**F3 — Model Injection (HIGH):** Both models injectable via CVE-2025-63389 (no patch).

---

## Notes

The cloud proxy 401 response is routed through Google Frontend (Ollama Connect) and does not expose account credentials in the response body on this instance — unlike Hanoi, Armenian Academy, and Purdue NW where Docker container IDs leaked as usernames.

---

## Disclosure

- **Discovered:** 2026-05-01
- **Status:** Pending outreach to JKUAT IT / KE-CIRT
