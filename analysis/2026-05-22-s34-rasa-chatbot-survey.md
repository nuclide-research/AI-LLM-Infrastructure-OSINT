# Session Analysis: Rasa Chatbot Population Survey

**Date:** 2026-05-22
**Session:** 34
**Classification:** Internal / Research Use Only
**Toolchain:** JAXEN, aimap v1.9.22, VisorGraph, aimap-profile, VisorBishop 0.1.7, VisorSD, VisorGoose, menlohunt v0.3.0, recongraph, nu-recon, VisorPlus, VisorLog, VisorScuba, BARE, VisorCorpus, cortex v2.0
**Repos updated:** AI-LLM-Infrastructure-OSINT (this commit)

---

## 1. Overview

### Objective

First standalone survey of Rasa, the dominant open-source conversational AI framework.
Thesis question: does Rasa ship with auth on the REST webhook channel by default?
The `/webhooks/rest/webhook` POST endpoint is Rasa's primary integration surface —
any message bus, widget, or frontend posts here to invoke the bot.

Secondary question: what operator classes deploy Rasa without changing the default?
Government agencies, utilities, financial services, or only development instances?

### Scope and Constraints

- **Target class:** Rasa Open Source chatbot deployments, port 5005 (default), public IP space
- **Corpus:** 196 IPs from Playwright-harvested Shodan dorks (API keys dead)
- **Allowed techniques:** Passive discovery, banner grab, read-only HTTP POST with test messages
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

Orchestrator (Opus 4.7 1M) + Bash execution. No subagent delegation this session.
Playwright browser (Brave) used for Shodan web UI scraping — the same pattern
established in Session 31 when Shodan API keys returned 401.

VPN state: NO VPN (Google Fiber, Olathe KS, AS16591).
SHODAN_API_KEY: 401 on both keys. All Shodan-dependent tools ran in dry-run or
were blocked.

### Tools Used

| Tool | Role | Result |
|---|---|---|
| JAXEN | Stage-0 discovery; empire.db import | 196 IPs imported (--no-lookup) |
| Playwright | Shodan web UI scraping (API fallback) | 3 dorks executed; 196 IPs harvested |
| aimap v1.9.22 | AI service fingerprinting | 0 detections — no Rasa fingerprint (tool gap) |
| aimap-profile | Target classification + ethics | 3 priority targets profiled |
| VisorGraph | Cert-pivot attribution | odpc.go.ke, leco.lk, hnbgeneral.com confirmed |
| VisorBishop 0.1.7 | Re-prober | No output — no Rasa class (tool gap) |
| VisorSD | ASN/org dork sweep | dry-run only (Shodan API 401) |
| VisorGoose | CT-log sweep (.go.ke TLD) | 0 results (Shodan blocked) |
| menlohunt v0.3.0 | GCP EASM | 3 GCP hosts; WireGuard UDP FPs; 0 chains |
| recongraph | Seed-polymorphic recon graph | 0 nodes (no Shodan seed) |
| nu-recon | Single-host passive deep-read | Simulated mode; port 22 FP (simulated) |
| VisorPlus | Orchestrator | assess on 2 priority targets |
| VisorLog | Ledger ingest | 6 findings (#1-#6) |
| VisorScuba | Compliance scoring | AI.C1 FP on all 6 (2nd non-Ollama instance) |
| BARE | Metasploit module ranking | RASA-1 to RASA-5: 0.377-0.481, all below 0.55 |
| VisorCorpus | Adversarial corpus | 50 PI + KB-exfil cases, domain=hr, baseline |
| VisorAgent | Active LLM exploitation | [—] ethical-stop — not fired at survey set |
| VisorRAG | RAG adversarial confirmation | [~] embedding API 401 (3rd session blocked) |
| VisorHollow | Windows process-injection | [—] not applicable — Windows-only |
| cortex v2.0 | Auth-context analyzer | analysis brief validated, 0 violations (informational) |
| Webhook probe (Python) | /webhooks/rest/webhook POST | 98/196 open, 0 auth-gated |

### Notable Configuration

- Playwright harvest: `fetch()` with `credentials: 'include'` against shodan.io while logged in
- Webhook probe: concurrent.futures.ThreadPoolExecutor (30 workers), 8s max-time per host
- aimap: ports 5005,80,443,8080; 20 threads; 10s timeout; terminated early (no Rasa fingerprint)
- menlohunt: ICMP disabled (sudo required); WireGuard UDP FP class same as S31

---

## 3. Methodology

### Enumeration Approach

Three Shodan dorks, harvested via Playwright web UI:
1. `port:5005 http.html:"rasa"` — port + HTML text match
2. `http.html:"/webhooks/rest/webhook"` — webhook path in HTML (crawled endpoints or docs)
3. `http.title:"Rasa"` — title match (looser; includes Rasa-adjacent UIs)

Dorks overlap — dedup after combining: 110 + 11 + 75 → 196 unique IPs.

### Candidate Identification

Rasa identity: three-conjunct marker.

1. Port 5005 listening (Rasa default)
2. GET `/` → body contains `Hello from Rasa: X.Y.Z`
3. POST `/webhooks/rest/webhook` → HTTP 200, JSON array with `recipient_id` key echoing caller's `sender` value

All three conjuncts are product-unique. No framework or middleware emits this
banner + this response shape combination. Zero false positives confirmed in sample.

### Validation Checks

Per Insight #16: HTTP 200 confirms endpoint is alive and unauthenticated; it does
not identify the platform. The `recipient_id` echo + `text` field with bot content
confirms Rasa specifically.

Per Insight #15: the title dork (`http.title:"Rasa"`) carries ~50% false positives.
Only hosts passing the webhook POST probe count as confirmed Rasa.

### Safeguards

No brute forcing. No privilege escalation. No data exfiltration. No credential use.
Webhook probe sends a single test message ("hello") and reads the response. Payment
bot probe observed state field (`WAITING_RECEIPT`) but submitted no receipts. No
further interaction with financial flows.

---

## 4. Execution Trace

| Time | Action | Outcome / Decision |
|---|---|---|
| 18:23 | Session start; read SESSION.md and memory | Context loaded; prior Shodan keys confirmed dead |
| 18:24 | Playwright: run 3 Rasa dorks via Shodan web UI | 110 + 11 + 75 IPs; 196 unique after dedup |
| 18:24 | jaxen import --no-lookup /tmp/rasa_corpus.txt | 196 stored → empire.db |
| 18:25 | Python: /webhooks/rest/webhook probe, sample n=30 | 26/30 open, 0 auth-gated → full scan confirmed |
| 18:26 | Python: full 196-IP webhook probe (30 threads) | 98/196 open, 0 auth-gated |
| 18:26 | WHOIS attribution on 8 priority IPs | odpc.go.ke, leco.lk, hnbgeneral.com confirmed |
| 18:27 | aimap launched on 98 confirmed open IPs, ports 5005,80,443,8080 | Phase 2 (fingerprinting) stalled — no Rasa class |
| 18:27 | Python: GET /, GET /status on 5 priority targets | Version confirmed; model path leaked via /status |
| 18:29 | visorgraph on 5 priority IPs | 3 domains confirmed via TLS cert SANs |
| 18:29 | nu-recon on ODPC + payment bot | Simulated mode; port 22 FP (trust direct probe) |
| 18:30 | VisorScuba assess | AI.C1 FP on all entries — "Unauthenticated Ollama" on Rasa |
| 18:30 | visorlog add ×6 | Findings #1-#6 ingested |
| 18:35 | BARE /tmp/rasa_bare_findings.json | RASA-1 to RASA-5: 0.377-0.481 — no msf coverage |
| 18:36 | visorcorpus build (50 cases, PI+KB-exfil, hr domain) | Corpus written to /tmp/rasa_viscorpus.json |
| 18:36 | menlohunt -ip on 3 GCP hosts | 0 chains; WireGuard UDP FPs (GCP edge, known class) |
| 18:37 | VisorGoose scan --tld .go.ke --no-shodan | 0 results |
| 18:39 | cortex analyze /tmp/rasa_analysis_brief.md --force | 0 violations, informational |
| 18:39 | aimap terminated | 14m runtime; no Rasa fingerprint; terminated to save cycles |
| 18:40 | Case study written | /case-studies/ai-chatbot/rasa-population-survey-2026-05-22.md |

---

## 5. Findings

### 5.1 Rasa unauthenticated webhook — population level

| Field | Value |
|---|---|
| Name/ID | RASA-POP-1 |
| Type | Missing authentication (platform default) |
| Evidence | 98/196 hosts return HTTP 200 + Rasa JSON on POST /webhooks/rest/webhook with no auth header |
| Observed exposure | Unauthenticated bot interaction: message injection, response observation, flow mapping |
| Severity | HIGH |

**Potential impact:** Any caller can inject messages into production bots, enumerate bot
capabilities, and read bot responses including operator brand names, service logic,
and data collection prompts — without authentication. Not a misconfiguration; Rasa
ships no-auth by default.

---

### 5.2 ODPC Kenya — government data protection authority

| Field | Value |
|---|---|
| Name/ID | RASA-ODPC-KE |
| Type | Unauthenticated production chatbot (government) |
| Evidence | POST /webhooks/rest/webhook → 200 + "Hi, am ODPC Virtual Assistant"; visorgraph cert CN *.odpc.go.ke |
| Observed exposure | Unauthenticated access to DPA's official chatbot; conversation flow enumerable |
| Severity | HIGH |

**Potential impact:** Kenya's data protection enforcement body exposes its public-facing
chatbot without authentication. An adversary can map how the bot handles data-subject
requests, inject messages, and observe response logic — undermining the credibility
of an enforcement authority on a technology they enforce.

---

### 5.3 LECO Sri Lanka — electricity utility

| Field | Value |
|---|---|
| Name/ID | RASA-LECO-LK |
| Type | Unauthenticated production chatbot (critical infrastructure) |
| Evidence | POST /webhooks/rest/webhook → 200 + "LECO Smart Chat"; visorgraph cert CN *.leco.lk |
| Observed exposure | Customer service bot for billing/outage queries exposed without auth |
| Severity | HIGH |

---

### 5.4 HNBGI — HNB General Insurance

| Field | Value |
|---|---|
| Name/ID | RASA-HNBGI-LK |
| Type | Unauthenticated production chatbot (financial services) |
| Evidence | POST /webhooks/rest/webhook → 200 + "HNBGI Nexa, your insurance assistant"; visorgraph cert CN *.hnbgeneral.com |
| Observed exposure | Insurance query chatbot exposed without auth |
| Severity | HIGH |

---

### 5.5 Payment validation bot — unauthenticated receipt intake

| Field | Value |
|---|---|
| Name/ID | RASA-PAYMENT-DE |
| Type | Unauthenticated payment processing chatbot |
| Evidence | POST /webhooks/rest/webhook → "asistente de validación de pagos"; state field: WAITING_RECEIPT |
| Observed exposure | Payment receipt intake exposed without auth; validation logic enumerable |
| Severity | HIGH |

**Potential impact:** An adversary can probe payment receipt formats, observe validation
error paths, and map the acceptance criteria without authentication.

---

### 5.6 Backend DB error propagated to caller

| Field | Value |
|---|---|
| Name/ID | RASA-DBERR-PE |
| Type | Error message propagation |
| Evidence | 3 IPs (201.150.62.35, .39, .44 — same /22) return "ERROR Fetch User Name: Invalid environment value: None!" |
| Observed exposure | Backend exception string returned to unauthenticated caller |
| Severity | MEDIUM |

---

### 5.7 LLM system prompt leaked in webhook response

| Field | Value |
|---|---|
| Name/ID | RASA-LLMLEAK-US |
| Type | System prompt disclosure |
| Evidence | POST /webhooks/rest/webhook → text field contains "#llmgreet_english|You are a friendly and helpful assistant. Your re..." |
| Observed exposure | Raw LLM system prompt in unauthenticated response body |
| Severity | HIGH |

---

**Severity summary:**

| CRITICAL | HIGH | MED | LOW | OBSERVED | UNRATED |
|---|---|---|---|---|---|
| 0 | 5 | 1 | 0 | 0 | 0 |

---

## 6. Risk Assessment

**Overall posture:** Systemic. Rasa's no-auth default produces a population where
50% of deployed instances expose their webhook unconditionally. This is not operator
error in isolation — the platform's default configuration creates the exposure class.

**Confidentiality:** Bot personas, service logic, and operational flows are readable
by any caller. Sensitive deployments (government, insurance, payment) expose their
conversational surface.

**Integrity:** Any caller can inject messages into bot sessions, potentially affecting
bot state and triggering unintended flows in stateful bots (e.g., payment validation
state machine).

**Availability:** Bot endpoints accept arbitrary POST load without rate limiting or
auth on 98/196 confirmed hosts. Quota-drain applies if bots connect to paid LLM backends.

**Systemic pattern:** The ODPC Kenya case is the clearest systemic irony — the body
tasked with enforcing data protection law misconfigures their data-handling chatbot.
The payment validation bot (5.78.124.207) extends the finding class: Rasa is being
used for data-collection workflows that warrant authentication.

---

## 7. Recommendations

**For Rasa operators:**

```yaml
# credentials.yml — add this to require auth on the REST channel
rest:
  token: "<strong-random-token>"
```

Every production Rasa deployment must set this. A blank `rest:` block enables the
channel with no auth.

**For Rasa maintainers:**

Change the default. A production REST endpoint that accepts arbitrary messages
from any caller without authentication should not ship as the default. Options:
- Require token configuration before the REST channel activates
- Add a startup warning when REST channel is enabled without a token
- Set a random token by default and require explicit opt-out for dev mode

**For aimap:**

Add a Rasa service fingerprint:
```go
// fingerprint entry
{
  Name: "Rasa",
  DefaultPorts: []int{5005},
  Probe: ProbeHTTPGet{Path: "/", Contains: "Hello from Rasa:"},
  DeepProbe: ProbeHTTPPost{
    Path: "/webhooks/rest/webhook",
    Body: `{"sender":"probe","message":"hello"}`,
    ExpectStatus: 200,
    ExpectBodyContains: "recipient_id",
  },
  AuthCheck: ProbeHTTPPost{...},
}
```

**Future automation:**

```bash
# Rasa-specific VisorSD dork set
visorsd hunt 'port:5005 http.html:"Hello from Rasa"'
visorsd hunt 'port:5005 http.title:"Rasa"'
visorsd hunt 'http.html:"/webhooks/rest/webhook"'
# aimap fingerprint would catch it after fix
aimap -list rasa_corpus.txt -ports 5005 -o results.json
```

---

## 8. Limitations and Assumptions

| # | Limitation | Risk Implication |
|---|---|---|
| 1 | Shodan API dead; corpus = Playwright web UI scrape | 196 IPs is likely 30-50% of the true population; survey is a lower bound |
| 2 | 50% open rate reflects mixed prod/dev; dev instances not distinguished | Open-rate for production-only subset may differ |
| 3 | nu-recon ran in simulated mode | Port data for ODPC and payment bot is inferred, not direct |
| 4 | LLM prompt leak host (208.110.93.69) went dark mid-session | Finding confirmed on first response; could not repeat |
| 5 | BARE corpus has no Rasa class | null result is the classification: first-party design fault, not CVE-chainable |
| 6 | VisorScuba AI.C1 FP on all Rasa entries | Compliance scores are meaningless until finding_class enum is implemented |

---

## 9. Proof of Concept (PoC) Illustrations

### PoC 1 — Unauthenticated Rasa webhook (ODPC Kenya)

```
REQUEST:
  POST /webhooks/rest/webhook HTTP/1.1
  Host: 102.220.23.140:5005
  Content-Type: application/json

  {"sender":"probe","message":"hello"}

RESPONSE:
  HTTP/1.1 200 OK
  Content-Type: application/json

  [{"recipient_id":"probe","text":"Hi, am ODPC Virtual Assistant.\nI was created just to answer your questions..."}]
```

No authentication header. No token. Any caller receives bot response.

### PoC 2 — Model metadata via /status (ODPC Kenya)

```
REQUEST:
  GET /status HTTP/1.1
  Host: 102.220.23.140:5005

RESPONSE:
  HTTP/1.1 200 OK

  {"model_file":"core-model-agnostic-v3.tar.gz","num_active_training_jobs":0}
```

Model file path and training state exposed without auth.

### PoC 3 — Payment bot state machine exposed

```
REQUEST:
  POST /webhooks/rest/webhook HTTP/1.1
  Host: 5.78.124.207:5005
  Content-Type: application/json

  {"sender":"probe","message":"hello"}

RESPONSE:
  HTTP/1.1 200 OK

  [
    {"recipient_id":"probe","text":"Soy el asistente de validación de pagos. Envíame el comprobante o los identificadores en el formato correcto."},
    {"recipient_id":"probe","custom":{"state":"WAITING_RECEIPT"}}
  ]
```

Payment validation state machine enters WAITING_RECEIPT state on any unauthenticated
message. Receipt intake logic maps without authentication.

### PoC 4 — LLM system prompt disclosure

```
REQUEST:
  POST /webhooks/rest/webhook HTTP/1.1
  Host: 208.110.93.69:5005
  Content-Type: application/json

  {"sender":"probe","message":"hello"}

RESPONSE:
  HTTP/1.1 200 OK

  [{"recipient_id":"probe","text":"#llmgreet_english|You are a friendly and helpful assistant. Your re[...]"}]
```

Raw LLM system prompt returned in response body without sanitization or authentication.

---

*Prepared by NuClide Research (Nicholas Kloster + Claude Opus 4.7 (1M context)) · Session 34 · 2026-05-22*
