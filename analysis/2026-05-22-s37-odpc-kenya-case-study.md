# Session Analysis: ODPC Kenya Case Study Artifact

**Date:** 2026-05-22
**Session:** 37
**Classification:** Internal / Research Use Only
**Toolchain:** None (artifact-only session)
**Repos updated:** AI-LLM-Infrastructure-OSINT (69b0515)

---

## 1. Overview

### Objective

Categorize and file the ODPC Kenya Rasa finding in the correct case study directory. Session 34 documented the finding in the Rasa population survey. Session 36 performed deep assessment on the host. This session wrote the standalone per-operator artifact at the right path in the `ai-chatbot` category tree.

Thesis question tested: none new. This session is pure documentation work. The finding evidence was produced in S34 and S36.

### Scope and Constraints

- **Target domains/IPs:** No new hosts probed.
- **Allowed techniques:** File writes only. No HTTP probes this session.
- **Ethical limitations:**
  - No data exfiltration — metadata and schema enumeration only
  - No destructive API calls
  - No use of discovered credentials
  - Data-tier probes: connection attempt only (does auth gate exist? no queries)
  - Active LLM exploitation (VisorAgent): controlled lab targets only, never operator hosts
  - Personal-device and wrong-category targets: archived without outreach

---

## 2. Environment and Tooling

### Claude Code Operation

Single orchestrator session. File write + commit. No subagents, no probing tools, no parallel lanes.

### Tools Used

| Tool | Role | Config notes |
|---|---|---|
| JAXEN | [—] not run — carry-forward from S34 | |
| aimap | [—] not run — carry-forward from S34/S35 | |
| VisorBishop | [—] not run this session | |
| VisorGraph | [—] not run this session | |
| VisorLog | [—] not run this session | |
| VisorScuba | [—] not run this session | |
| BARE | [—] not run this session | |
| VisorCorpus | [—] not run this session | |
| VisorSD | [—] not run this session | |
| VisorGoose | [—] not run this session | |
| menlohunt | [—] not run this session | |
| recongraph | [—] not run this session | |
| nu-recon | [—] not run this session | |
| VisorPlus | [—] not run this session | |
| cortex | [—] not run this session | |
| JS-bundle extract | [—] not run this session | |
| VisorRAG | [—] ethical-stop — controlled targets only | |
| VisorAgent | [—] ethical-stop — controlled targets only, never operator hosts | |
| VisorHollow | [—] not applicable — Windows-only | |

All tool gaps noted here are expected for an artifact-only session. Tools were run in S34 (population survey) and S36 (deep assessment). This session produced documentation only.

### Notable Configuration

- VPN state: Mullvad active (za-jnb-wg-002)
- No API keys required
- No HTTP traffic generated

---

## 3. Methodology

### Enumeration approach

No enumeration. The finding was already established. S34 confirmed unauthenticated Rasa webhooks at 98 of 196 probed hosts. S36 performed deep assessment on 102.220.23.140 / bot.odpc.go.ke.

### Candidate identification

Not applicable. ODPC Kenya was attributed via TLS cert pivot in S34 (visorgraph confirmed `*.odpc.go.ke` SAN on 102.220.23.140).

### Validation checks

Validation was performed in prior sessions. The S37 case study reproduces the S34/S36 evidence without re-probing. The probe used: one `POST /webhooks/rest/webhook` with `{"sender":"probe","message":"hello"}` returning HTTP 200 plus bot self-identification string. No further messages sent.

### Safeguards

No probing. No HTTP requests. No write-tier operations. The single prior probe that forms the PoC evidence was sent in S34 (one message, read the response, stopped). This session added no new probe traffic to the operator host.

---

## 4. Execution Trace

Artifact-only session. No enumeration steps. The ODPC Kenya finding was established in S34 (webhook probe) and S36 (deep assessment). This session wrote one case study file and committed it (69b0515).

---

## 5. Findings

No new findings produced this session. The finding documented is ODPC-KE-001, first confirmed in S34, deep-assessed in S36.

### 5.1 ODPC Kenya — Unauthenticated Rasa REST webhook (HIGH, carry-forward)

| Field | Value |
|---|---|
| **Name/ID** | ODPC-KE-001 |
| **Type** | Unauthenticated chatbot REST API (Rasa no-auth default) |
| **Evidence** | POST /webhooks/rest/webhook → HTTP 200 + "Hi, am ODPC Virtual Assistant" (S34); CORS: Access-Control-Allow-Origin: * with Allow-Credentials: true |
| **Observed exposure** | Direct unauthenticated invocation of ODPC's production chatbot |
| **Severity** | HIGH — verified unauth endpoint; bot responds to arbitrary callers without any auth challenge |

**Potential impact:** Any caller can inject messages into the ODPC Virtual Assistant, map response flows, and enumerate the bot's knowledge base. The operator is Kenya's data protection enforcement body — the institution that issues enforcement notices under Section 41 of the Kenya Data Protection Act 2019 for inadequate technical measures.

---

## 6. Risk Assessment

### Overall Posture

Isolated per-operator finding filed as part of a systemic pattern (50% of the 196-host Rasa population is unauthenticated). The institutional context elevates significance: the authority responsible for enforcing data security standards in Kenya runs an unauthenticated production AI endpoint.

### Confidentiality

Rasa's unauthenticated REST channel exposes bot logic, response flows, and internal knowledge base paths to unauthenticated callers. S36 established that 5,041 citizen messages were readable via hardcoded sender_id — that evidence is documented in the S36 analysis and session state, not re-derived here.

### Integrity

The unauthenticated webhook accepts arbitrary sender and message fields. No write-tier operations were tested (restraint ethic). Whether arbitrary sender_id values can be used to inject state into live user sessions was not tested.

### Availability

Unauthenticated access allows any caller to flood the webhook endpoint. No load testing performed. Risk is theoretical at the level documented.

### Systemic Patterns

Root cause is Rasa's default credential configuration. The Rasa REST channel ships with no token requirement. Without explicit `rest: token:` in `credentials.yml`, all callers are accepted. This is the platform default that produced the 50% unauth rate across the S34 population survey. ODPC Kenya is one instance of the class-level pattern.

---

## 7. Recommendations

### R1 — Add REST channel token to Rasa credentials.yml

```yaml
# credentials.yml
rest:
  token: "<strong-random-token-min-32-chars>"
```

Restart Rasa after adding the token. Update the frontend widget or integration to include the token as a query parameter:

```
POST /webhooks/rest/webhook?token=<token>
```

### R2 — Fix CORS policy

`Access-Control-Allow-Origin: *` combined with `Access-Control-Allow-Credentials: true` is a misconfiguration. Lock the CORS origin to the canonical ODPC web domain:

```
Access-Control-Allow-Origin: https://www.odpc.go.ke
```

### Future automation

```bash
# With aimap v1.9.26, Rasa is now detectable in CI
aimap -list corpus.txt -ports 5005 -o rasa_scan.json
visorlog ingest --from rasa_scan.json --format aimap-json
```

---

## 8. Limitations and Assumptions

| # | Limitation | Risk Implication |
|---|---|---|
| L1 | Only one probe sent (S34 validation); full bot flow not mapped | Bot knowledge base depth and sensitive data class are unquantified at this tier |
| L2 | S36 deeper findings (PostgreSQL :5432, Metabase setup-token, citizen messages) documented in S36 analysis, not reproduced here | This case study covers the REST webhook surface only; refer to S36 for the full stacked exposure |
| L3 | Disclosure not sent by session end — operator decision by Nick | Remediation timeline unknown; bot remains unprotected until operator acts |

---

## 9. Proof of Concept (PoC) Illustrations

### PoC 1 — Unauthenticated Rasa webhook invocation

**Scenario:** External caller sends a single probe message to the ODPC Virtual Assistant without any authentication token.

```
REQUEST:
  POST /webhooks/rest/webhook HTTP/1.1
  Host: 102.220.23.140:5005
  Content-Type: application/json

  {"sender": "probe", "message": "hello"}

RESPONSE:
  HTTP/1.1 200 OK
  Access-Control-Allow-Origin: *
  Access-Control-Allow-Credentials: true

  [{"recipient_id": "probe", "text": "Hi, am ODPC Virtual Assistant.\nI was created just to answer your questions..."}]
```

**Demonstrated:** The endpoint accepts messages from any caller and returns bot responses. No token, session cookie, or API key is required. `recipient_id` confirms Rasa platform. `Access-Control-Allow-Origin: *` with `Allow-Credentials: true` confirms any web origin can make cross-origin requests to this endpoint. This PoC does not extract knowledge base content, enumerate flows, or inject conversation state — it confirms the surface exists and the auth gate is absent.

---

*Prepared by NuClide Research (Nicholas Kloster + Claude Sonnet 4.6) · Session 37 · 2026-05-22*
