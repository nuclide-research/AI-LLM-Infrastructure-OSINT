---
type: case-study-appendix
parent: openwebui-population-survey-2026-06-06.md
category: cat-ow
date: 2026-06-06
status: calibration-pass
---

# Cat-OW Calibration Deltas — 5 Named Findings Re-Verified

_NuClide Research · 2026-06-06_

A spot-check verification pass on five named-institution findings in the
Open WebUI population survey, applying the attribution hierarchy from
[Insight #79](../../methodology/insight-79-aspirational-name-field-attribution-hierarchy.md).

The original case study cited operators by their `name` field from `/api/config`.
That field is operator-set free text. This pass cross-checked each name against
TLS cert SAN, rDNS, WHOIS, and institutional netblock allocation.

**Result:** 2 of 5 confirmed real institutional infrastructure. 3 of 5 needed
scope corrections — auth-state risk is real for all, but institutional attribution
varies.

---

## Confirmed institutional infrastructure

### PLLuM dla Edukacji — REAL, headline finding

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7004, S7070, T5904, T5919
- **733 (AI Risk & Ethics Specialist):** K7040, T5868
- **overlap (Common AI KSATs (all 5 roles)):** K108, K1158, K22, K6935, K7003

<!-- ksat-tag:auto-generated:end -->

- **IP:** 194.181.158.235:443
- **WHOIS netblock:** `CBiTT-NASK-PIB` — NASK (Polish state cybersecurity / research institute)
- **TLS cert:** `chat.pllum.edu.pl` (institutional `.edu.pl`)
- **State:** `auth: False, signup: False` (auth fully disabled; signup not needed because there's no auth wall)
- **Version:** 0.6.5
- **Calibration:** No change. The case study correctly identified PLLuM as Poland's national LLM operated by NASK. This is the most severe finding in the survey: a state cybersecurity authority running a national-scale AI platform with authentication completely off.

### Dartmouth Offshore Wind Lab AI — REAL, institutional signup-open

- **IP:** 129.170.224.237:443
- **WHOIS netblock:** `DART-ETHER` (Dartmouth College allocation, 129.170.0.0/16)
- **TLS cert:** `*.dartmouth.edu` wildcard (Dartmouth-controlled cert)
- **State:** `auth: True, enable_signup: True`
- **Version:** 0.4.4 (2+ years old)
- **Calibration:** No change. Genuinely on Dartmouth's netblock with a Dartmouth-issued cert. Signup-open finding stands. First-user-admin window status unknown without exercising registration.

---

## Scope corrections (auth-state real, institutional attribution unverifiable)

### CUNY AI Lab — Personal/lab project, not central CUNY IT

- **IP:** 44.199.166.66:443 (AWS us-east-1, generic EC2)
- **rDNS:** `ec2-44-199-166-66.compute-1.amazonaws.com`
- **TLS cert SAN:** `openwebui.cuny.qzz.io`, `dev.cuny.qzz.io` — **`qzz.io` is a free dynamic DNS service**, not `cuny.edu`
- **State:** `auth: True, enable_signup: True`
- **Version:** 0.9.6
- **Original claim:** *"City University of New York — public university system serving 500,000+ students. Open signup on AI research infrastructure."*
- **Calibrated finding:** Personal or lab AWS EC2 deployment branded "CUNY AI Lab". The `dev.cuny.qzz.io` SAN and the `qzz.io` DDNS hosting strongly suggest a graduate-student or single-researcher project, not CUNY central IT. Signup-open is real but scope is instance-only, not the public university system.

### SwiftRef Assistant — Auth-off real, SWIFT attribution unverifiable

- **IP:** 52.204.54.17:80 (AWS us-east-1, generic EC2)
- **rDNS:** `ec2-52-204-54-17.compute-1.amazonaws.com`
- **TLS cert:** None (HTTP port 80 only)
- **State:** `auth: False, enable_signup: False`
- **Version:** 0.9.5
- **Original claim:** *"'SwiftRef' is SWIFT's reference data service for the global financial messaging network."*
- **Calibrated finding:** Generic AWS EC2 instance whose operator wrote "SwiftRef Assistant" in the name field. No cert to verify SWIFT control. Auth-off chat UI is real and accessible to the internet. Could be a SWIFT employee's POC on personal AWS, a vendor demo, or someone unrelated using the branding. **Disclosure target cannot be SWIFT's CISO** without further attribution — the right contact is the AWS account owner, which is opaque from outside.

### deepset \| PepsiCo — Signup-open real, joint deployment unverifiable

- **IP:** 18.211.90.210:80 (AWS us-east-1, generic EC2)
- **rDNS:** `ec2-18-211-90-210.compute-1.amazonaws.com`
- **TLS cert:** None (HTTP port 80 only)
- **State:** `auth: True, enable_signup: True`
- **Version:** 0.6.24 (18+ months old)
- **Original claim:** *"deepset is an enterprise AI company (Haystack framework). PepsiCo branding visible in the name field. Joint deployment or integration test environment."*
- **Calibrated finding:** Operator wrote "deepset | PepsiCo" in the name field on a generic EC2 instance. No cert anchoring it to either company. Signup-open is real. Could be a deepset employee's POC for a PepsiCo pitch, an old demo, or someone unrelated. **Disclosure target cannot be assumed to be deepset or PepsiCo** without further attribution.

---

## Calibrated severity tally for the original survey

The case study reported **39 AUTH_OFF + 564 SIGNUP_OPEN = 603 findings**. The
auth-state count is unchanged — that's an objective property of `/api/config`.
What changes is the **institutional severity** distribution for the named-instance
spotlights. Applying Insight #79 to the rest of the case study's "Selected Notable
Instances" section would likely reduce the count of institutionally-attributable
findings substantially, because the case study leaned on `name` field strings for
most of its spotlights.

**Findings that should be re-checked the same way** (all from the original survey's
notable-instances section):

- Inspirali AI DEV (34.227.208.161) — claimed medical education
- ChatAI / Singular GovTech (136.248.93.247) — claimed Singapore govtech
- LLM-jp Playground (163.220.178.66) — claimed Japanese research consortium
- PromoPharma AI (178.104.191.213) — claimed pharma
- NCU Blockchain Lab (171.102.174.59) — claimed National Chengchi University Taiwan
- Salacommerce AI Agents (109.199.109.81) — claimed commercial product
- Groupe Narbonne (163.172.189.39) — claimed French auto parts
- Enterprise Knowledge Base DEMO (63.33.27.57) — generic
- Ampere Llama Chat (130.61.219.50) — claimed Oracle Ampere subsidiary
- DeepSeek cloud proxy (143.47.38.176) — Ollama Connect compute-theft pattern

Each needs TLS cert SAN + WHOIS netblock check before being cited at
institutional severity. A follow-up calibration pass over those 10 would close
the gap.

---

## Disclosure routing implication

Two findings are ready for disclosure pipeline at institutional severity:

1. **PLLuM / NASK** — disclosure contact: NASK CSIRT (`cert.pl`), Poland's national CERT operated by NASK itself. This is unusual: the institution that runs the exposed system also runs the country's CERT. Disclosure-recipient resolution warrants care.

2. **Dartmouth Offshore Wind Lab AI** — disclosure contact: Dartmouth ITS / `security@dartmouth.edu`. Standard institutional path.

The other three (CUNY-branded, SwiftRef, deepset|PepsiCo) need attribution work
first OR should be disclosed only to the AWS abuse pipeline (since the operator
identity is opaque from outside).

---

## Methodology codification

This calibration pass is now codified as
[Insight #79](../../methodology/insight-79-aspirational-name-field-attribution-hierarchy.md).
Going forward, Stage 3v (verify) for any `name`-bearing platform includes the
attribution hierarchy check before institutional severity is assigned.
