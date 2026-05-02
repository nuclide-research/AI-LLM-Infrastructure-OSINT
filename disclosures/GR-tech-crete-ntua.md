---
institution: Technical University of Crete + NTUA
ip: 147.27.38.32
to: helpdeskadmin@helpdesk.tuc.gr
cc: grnet-cert@grnet.gr
severity: CRITICAL
status: DRAFT
date: 2026-05-01
---

**To:** helpdeskadmin@helpdesk.tuc.gr
**Cc:** grnet-cert@grnet.gr
**Subject:** Unauthenticated AI inference endpoint — Technical University of Crete + NTUA (147.27.38.32)

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-01

**Re:** Unauthenticated Ollama AI inference endpoint — Technical University of Crete + NTUA
**IP / Host:** 147.27.38.32
**Severity:** CRITICAL

---

I'm an independent security researcher. I hold CISA disclosures CVE-2025-4364 and ICSA-25-140-11 and conduct good-faith AI infrastructure research under the NuClide Research umbrella. This is an unsolicited disclosure — no engagement exists with your organization, and I have not accessed, modified, or exfiltrated any data beyond what was necessary to confirm the exposure.

---

## Technical University of Crete

**IP:** 147.27.38.32 (`hp2420.telecom.tuc.gr`) — Heraklion, Greece  
**Models:** 14 (1 cloud proxy)

### MiniMax Cloud Proxy + Credential Leak

```json
{
  "error": "unauthorized",
  "signin_url": "https://ollama.com/connect?name=arian&key=<base64>"
}
```

- **Username:** `arian`
- **SSH pubkey:** `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIASZr/fN5P73o/WF6vT/owMFz3ftTeBlzOpEFpS2QStP`
- **Cloud proxy:** `minimax-m2.7:cloud` (MiniMax API subscription)

14 total models accessible without authentication.

---

## National Technical University of Athens

**IP:** 147.102.40.5 (`p620.cn.ece.ntua.gr`) — Athens, Greece  
**Models:** 20 (0 cloud proxy)

### 235.7B-Parameter Model Exposed

| Model | Size | Notes |
|-------|------|-------|
| deepseek-coder-v2:236b | **123 GB** | 235.7B-param MoE coding model (tag is `:236b`, actual params 235.7B) |
| qwen2.5-coder:32b | 18 GB | Coding |
| qwen3-coder:30b | 17 GB | Coding |
| qwen3-embedding:0.6b | 0 GB | Embedding — RAG component |
| qwen3:latest | 4 GB | General |
| (15 more models) | | |

20 models accessible without authentication. The `deepseek-coder-v2:236b` (235.7B params, 123GB on disk) represents significant dedicated GPU compute accessible to any internet actor for free inference.

RAG pipeline present: `qwen3-embedding:0.6b` suggests active document retrieval workflow.

---

## Findings (Both)

Both institutions have unauthenticated Ollama ports (11434 open, no auth). CVE-2025-63389 model injection applies to all models on both hosts.

TechCrete F2 — credential leak on MiniMax cloud proxy.  
NTUA F2 — free inference on 235.7B model, potential RAG pipeline injection.

---

**Why it matters**

The credential leak (username + SSH public key) exposes your service account to enumeration and credential-stuffing against other services. An embedding model indicates an active RAG pipeline — documents loaded into your vector store are reachable via unauthenticated queries.

**One-line fix**

```
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

This rebinds Ollama to loopback only. If running in Docker: `docker run -p 127.0.0.1:11434:11434 ollama/ollama`.

**CVE-2025-63389**

All models on this instance are injectable via the unauthenticated `/api/create` endpoint — an attacker can overwrite any model's system prompt or delete models entirely. No patch exists as of this disclosure.

**Reference**

Full technical details, parameter counts, and remediation notes are in this public research repository:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/GR/tech-crete-ntua.md

This research is part of a broader sweep of university AI infrastructure exposures documented at:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/OVERVIEW.md

I'm happy to answer questions or assist with verification. No response is required.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
