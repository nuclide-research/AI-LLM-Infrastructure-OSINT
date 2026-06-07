---
type: multi-host
---

# Auto F&I Sales Training RAG: Customer Dialogues + Methodology IP Exposed via Unauthenticated ChromaDB

_NuClide Research · 2026-05-03_

---

## Summary

A ChromaDB instance on a DigitalOcean VPS exposes three RAG collections used to train an auto-dealership F&I (Finance & Insurance) sales agent. The collections contain real customer dialogue transcripts (with first names, vehicle models, and dollar figures), authored sales methodology by Sean McNally, a real-name F&I sales consultant, and a "deal history" with at least one customer-identifying transcript. All readable without authentication on port 8000.

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, S7068, S7075, T5904
- **733 (AI Risk & Ethics Specialist):** K7040, K7051, S7067, T5854, T5868
- **overlap (Common AI KSATs (all 5 roles)):** K108, K1157, K1158, K22, K6311, K6900, K6935, K7003

<!-- ksat-tag:auto-generated:end -->

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 104.131.60.234 |
| Hosting | DigitalOcean |
| Port | 8000 (HTTP, no auth) |
| ChromaDB version | 1.0.0 (v2 API) |
| Tenant / DB | `default_tenant` / `default_database` |
| Discovery date | 2026-05-03 |

---

## Collections

| Collection | UUID | Docs | Content |
|---|---|---|---|
| `sarah_training_data` | 16b5db79-4bf4-4f54-8066-6072f2e92b5d | 1,538 | Role-play F&I dialogue transcripts |
| `sarah_deal_history` | e8964a96-c983-4833-94c4-21b272c38ffe | 34 | Apparent real customer transcripts |
| `sean_mcnally_methodology` | f36c3e4b-5a6a-40f1-9906-deec7b79c7ee | 36 | Sean McNally's "Passionate Consulting" methodology |

---

## Findings

### F1: Real Customer Dialogue with Name + Vehicle + Family Detail (HIGH)

`sarah_deal_history` contains transcripts that read as live customer encounters:

```
F&I Manager: Hi Mrs. Patterson, I'm Sean and I'll be helping you finalize
everything today. Congratulations on the new Highlander!
Customer: Thanks, I'm excited about it.
F&I Manager: That's great! So tell me, what made you choose the Highlander?
Customer: We have three kids and needed something reliable for the family.
F&I Manager: Three kids - that's wonderful! I have a little b...
```

Identified data points: customer last name (Patterson), vehicle (Toyota Highlander), family composition (three kids), F&I representative first name (Sean). If "Mrs. Patterson" is a real customer rather than a role-play persona, this is a privacy breach: a finance-and-insurance dialogue would routinely include credit terms, monthly payment, residual value, GAP/warranty premiums, and other commercially sensitive customer financial information.

The collection name `sarah_deal_history` (vs. `sarah_training_data`) suggests this is *Sarah's* historical deals, i.e., a specific F&I manager's logged customer encounters being used to fine-tune or RAG-augment an AI training assistant. That naming distinction makes the live-data interpretation more likely than the role-play interpretation.

### F2: F&I Sales Methodology IP (HIGH)

`sean_mcnally_methodology` exposes proprietary sales coaching material attributed to Sean McNally:

```
Passionate Consulting Core Philosophy by Sean McNally: Passion creates
connection, and connection creates trust. That trust is the bedrock of
every great sale and every meaningful client relationship. Excitement is
about me - my goal, my win. Passion is about them - their needs, their
story, their solution. The shift from salesperson to consultant happens
when the customer says 'What would you do...'
```

Sean McNally is a real-name F&I sales consultant with a public-facing brand. The 36-document collection appears to encode his complete methodology framework, a competitive trade secret to a rival F&I training vendor.

### F3: Training Data Includes Negotiation Patterns and Dollar Figures (MEDIUM)

`sarah_training_data` contains role-play transcripts that read like authentic dealership scenarios:

```
FM: Now, for the backend products. You have a payment of $450, but if
you want the warranty and GAP, it goes up to $520.
Customer: Whoa, $70 more? That's way too much.
FM: Yeah, it is kind of high. But repairs are expensive.
Customer: I think I'll pass.
FM: Okay, no problem. Just sign the waiver here and we can finish...
```

These transcripts encode F&I tactical patterns: how to surface backend products, how to handle pushback, how to retain the deal when the customer declines. The content has commercial value to anyone training competing F&I sales agents, the operator's training advantage is fully exposed.

### F4: Multi-Tenant Risk Indicator: Single Operator Schema (MEDIUM)

The naming pattern `sarah_*` (a specific F&I manager's data) plus a methodology collection by named author suggests this is one user's working environment. If this operator runs identical instances per F&I manager (Sarah, Bob, Maria, etc.), there are likely additional ChromaDBs on adjacent IPs, each one exposing one F&I manager's customer interaction history.

### F5: Root Cause: Default-Off Auth (CRITICAL)

ChromaDB 1.0.0 ships with no authentication. The instance is deployed on the public internet with no token requirement and no firewall on port 8000. Disclosure / exfiltration / overwrite (poisoning the training data) are all possible by any unauthenticated client.

---

## Remediation

Enable token auth in ChromaDB:

```bash
chroma run --host 0.0.0.0 --port 8000 \
  --auth-provider chromadb.auth.token \
  --auth-credentials <strong-token>
```

Then firewall port 8000 to the application backend only. Rotate any token already in use because the unauth state means it could have been read.

If the customer dialogues contain real customer information, FTC Safeguards Rule (US) and applicable state privacy laws (CCPA if any California customers, etc.) likely require breach assessment and possibly notification.

Consider whether `sarah_deal_history` should contain real customer dialogue at all, synthetic role-play data is the standard for F&I training and avoids this entire risk class.

---

## Disclosure

- **Discovered:** 2026-05-03
- **Status:** Pending, operator identity inferable from collection content (Sean McNally methodology); attribution warranted before outreach
- **Note:** If operator identification reveals a US-based F&I training company, FTC Safeguards Rule applies; outreach should reference 16 CFR 314.4 incident notification obligations
