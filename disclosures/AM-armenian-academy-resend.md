---
to: abuse@sci.am
cc: abuse@nuclide-research.com
severity: CRITICAL
ip: 37.26.168.19
institution: Institute for Informatics and Automation Problems, NAS Armenia (resend per session-7 forward-resolution dead-letter)
status: DRAFT
outcome: sent
date: 2026-05-04
---

**To:** abuse@sci.am
**Cc:** abuse@nuclide-research.com
**Subject:** Unauthenticated AI inference endpoint, IIAP NAS Armenia (37.26.168.19) [resend via Armenian-academy abuse contact]

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-04

**Re:** Unauthenticated Ollama AI inference endpoint, Institute for Informatics and Automation Problems (IIAP), NAS Armenia
**IP / Host:** 37.26.168.19 (`h168.019.yerphi.am`)
**Severity:** CRITICAL

---

I'm an independent security researcher conducting good-faith AI infrastructure research under the NuClide Research umbrella (CISA disclosures CVE-2025-4364, ICSA-25-140-11). This is an unsolicited coordinated-disclosure resend.

**Note on previous attempt:** I sent this disclosure on 2026-05-04 to `ipia@ipia.sci.am`; the message was forwarded to `iiap.sci.am` where the local-part `ipia` was rejected as user-unknown, looks like a stale mail-forwarding rule. RIPE WHOIS lists `abuse@sci.am` as the registered abuse-mailbox for the Armenian Academy of Sciences network, resending here. Apologies for the noise if this reaches the wrong inbox.

---

## Summary

The Institute for Informatics and Automation Problems (IIAP) of the National Academy of Sciences of Armenia (Yerevan) has an Ollama instance running inside a Docker container with two cloud proxy subscriptions. The 401 response leaks Docker container credentials.

## Infrastructure

| Field | Value |
|---|---|
| IP | 37.26.168.19 |
| rDNS | h168.019.yerphi.am |
| Org | IIAP, NAS Armenia |
| Open ports | 11434 (Ollama, public) |

## Credential leak

```json
{
  "error": "unauthorized",
  "signin_url": "https://ollama.com/connect?name=c2a68a9aa573&key=<base64>"
}
```

- Username: `c2a68a9aa573` (Docker container ID)
- SSH pubkey: `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIBqWiNKYbTt7XQxVG0OdY/61UHxsXkuGVtuS0UShBD7V`

## Models

| Model | Type |
|---|---|
| `deepseek-v4-pro:cloud` | Cloud proxy |
| `minimax-m2.7:cloud` | Cloud proxy |
| `llama3.2:3b` | Local |

## Findings

- **F1, Docker credential leak (HIGH)**, Container ID + SSH pubkey enumerable via the 401 path.
- **F2, Dual cloud proxy on academic research server (HIGH)**, DeepSeek and MiniMax subscriptions exposed.
- **F3, CVE-2025-63389 model injection (CRITICAL)**, All 3 models injectable.

## Pattern

Docker-container hostname as Ollama username also seen at Hanoi University (Vietnam, `04aa6fb5e0b8`) and Purdue NW (US-IN, `c0ddfaef7764`). All three expose port 11434 via `docker run -p 11434:11434` which binds to 0.0.0.0.

## One-line fix

```
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

If in Docker: `docker run -p 127.0.0.1:11434:11434 ollama/ollama`.

## Reference

Full case study:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/universities/AM/armenian-academy.md

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
