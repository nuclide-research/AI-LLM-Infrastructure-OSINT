# emails-pro.fr — French Commercial Appointment-Booking SaaS — Full System Prompt + PII Collection Pattern Exposed

_NuClide Research · 2026-05-01_

---

## Summary

A production French commercial appointment-booking AI assistant — `rdv-bot:latest` — is hosted on an IP attributed to the Romanian National Institute for R&D in Informatics (ICI Bucharest). The PTR record points to `mail.emails-pro.fr`, indicating the IP is operated as a commercial SaaS rather than academic infrastructure. The Ollama API is unauthenticated; the full 5,422-character system prompt is extractable, exposing the SaaS's complete business logic, PII collection pattern, function-call schema, and anti-prompt-injection rules.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 85.122.129.248 |
| Hostname (PTR) | `mail.emails-pro.fr` |
| Shodan Org Tag | Institutul National de Cercetare-Dezvoltare in informatica - ICI Bucuresti |
| Likely Operator | emails-pro.fr (French SaaS, hosted on Romanian IP space) |
| Country | Romania (host) / France (operator/customers) |
| Open ports | 11434 (Ollama — public) |

---

## Model Inventory

11 models. Most are stock open models. The custom artifact is:

| Model | Size | Purpose |
|---|---|---|
| `rdv-bot:latest` | 4GB | **Production French appointment-booking SaaS** |
| `qwen3.6:35b` | 22GB | Likely the larger backing model |
| `gemma2:9b-instruct-q4_K_M` | 5GB | — |
| `qwen2.5:7b-instruct-q4_K_M` | 4GB | — |
| `llama3.1:8b` | 4GB | — |

Plus 6 other stock open models.

---

## Findings

### F1 — Production Commercial SaaS System Prompt Fully Exposed (CRITICAL)

The `/api/show` endpoint returns the complete `rdv-bot:latest` system prompt without authentication. It contains:

**Business identity & target market:**
- Target customers: hairdressers (coiffeur), osteopaths (ostéopathe), beauticians (esthéticienne), and similar appointment-driven small businesses
- Customer-facing language: French only (with explicit instruction to ignore other languages)
- 10 worked few-shot examples covering ambiguous services, English-language clients, medical/product redirects, cancellations, prompt-injection attempts, past dates, off-hours requests

**PII collection schema (function call):**
```
[CREATE_APPOINTMENT]{
  "service_name": "...",
  "date": "YYYY-MM-DD",
  "time": "HH:MM",
  "client_name": "...",
  "client_phone": "...",
  "client_email": "..."
}
```

The bot collects French customer first/last names, phone numbers (e.g., format `0612345678`), and emails for every appointment. The runtime context provided per-request adds: services list, business hours, available slots, current date, business phone number, business name.

**Service catalog (from few-shot examples):**
- Coupe femme (35€), Coupe homme (25€), Coupe enfant (18€), Couleur

**Competitive intelligence exposed:**
- Complete business logic, pricing pattern, anti-prompt-injection ruleset
- The phrase `[CREATE_APPOINTMENT]{...}` is the SaaS's internal tool-call format — competitor or attacker can replicate the exact integration
- Anti-injection rule #7 explicitly named in the prompt — this rule itself is now defeated since attackers know it exists

### F2 — CVE-2025-63389 Injection on Live PII-Collecting AI (CRITICAL)

The unauthenticated `/api/create` endpoint allows overwriting `rdv-bot:latest`'s system prompt. After such a write, the production SaaS would:
- Continue collecting French customer PII (names, phones, emails)
- But process those collections under attacker-controlled instructions
- Could be redirected to exfiltrate the `[CREATE_APPOINTMENT]` payloads to attacker infrastructure
- Could be redirected to silently corrupt all bookings, harm hundreds of small French businesses simultaneously
- Could insert phishing language ("call this number to confirm…") replacing the legitimate cabinet phone

```bash
curl -X POST http://85.122.129.248:11434/api/create \
  -H "Content-Type: application/json" \
  -d '{
    "model": "rdv-bot:latest",
    "from": "rdv-bot:latest",
    "system": "[redacted — attacker-controlled instructions]"
  }'
```

The original prompt explicitly contains an anti-injection rule (rule #7): the customer-facing safeguard is bypassed entirely by writing the **system** prompt at the API level — that rule only addresses prompts injected via the user/customer channel.

### F3 — Hosting Misattribution (MEDIUM)

The Shodan/WHOIS data tags this IP as Romanian academic (ICI Bucharest) but the PTR is `mail.emails-pro.fr`. Either:
- The Romanian institute leases IP space to commercial customers, with stale WHOIS
- A French SaaS is using ICI's IP allocation for hosting

Either way, defenders relying on org-level reputation tagging may misclassify this asset.

---

## Remediation

For the operator (emails-pro.fr or whoever runs `mail.emails-pro.fr`):

```bash
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

If the SaaS architecture requires Ollama to receive remote calls, the call site should authenticate (e.g., reverse-proxy with API key validation) — the `OLLAMA_HOST` flag has no built-in auth; the SaaS frontend must enforce it.

The system prompt should be marked as commercially sensitive; the current Ollama deployment exposes it to anyone who can reach port 11434.

---

## Disclosure

- **Discovered:** 2026-05-01
- **Status:** Pending outreach to emails-pro.fr (operator) + ICI Bucharest (host attribution)
- **Note:** Coordinated disclosure preferred — the system prompt contains ongoing competitive intelligence and live PII pipeline configuration
