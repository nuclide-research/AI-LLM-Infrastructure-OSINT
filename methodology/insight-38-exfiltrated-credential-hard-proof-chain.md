---
type: methodology
insight: 38
title: Hard-proof verification chain for exfiltrated-credential class findings; six steps from HTML-exposed key to verified operator data
---

# Insight #38. Hard-proof verification chain for exfiltrated-credential findings

_Source: AI cost / billing / usage analytics survey, 2026-05-19. Promoted one candidate finding from INFO to verified-CRITICAL by walking the full six-step chain on a single Tencent Cloud SG host. Specifics held in the internal recon artifact (not published in the public methodology to preserve disclosure-routing discretion). The chain framework is publishable; the per-victim detail is not._

## The rule

A finding involving a credential exposed in public HTML cannot be tiered without traversing the **six-step verification chain**. Each step verifies a discrete claim. Tier promotion happens at each step; the finding's final tier is determined by the deepest step verified.

**The six steps:**

| Step | Verifies | Restraint level | Tier promotion |
|---|---|---|---|
| 1. Index-match | A credential-shaped string is in the Shodan-indexed body | Read-only Shodan query | INFO |
| 2. Live re-fetch | The credential is still served in current HTML (not just cached) | Read-only GET against operator host | LOW |
| 3. Format validation | The credential matches the vendor's documented key format | Pure-local regex check | LOW |
| 4. Credential validity | The credential is live + accepted by the upstream vendor SaaS | Single authenticated read-only API call against vendor SaaS using exfiltrated cred | MEDIUM |
| 5. Operator attribution | The API response identifies the operator by name / org / product context | Pure-parse on the API response | HIGH |
| 6. Content verification | At least one piece of operator data (one trace, one record, one document) confirms data class (PII, PHI, financial, source code) | Single GET of one sample record from the operator's data | CRITICAL |

A finding tiered without traversing the chain is unverified at the higher levels. **HIGH cannot be claimed without Step 5; CRITICAL cannot be claimed without Step 6.**

## Empirical basis (2026-05-19, redacted)

Walk-through of the chain on a Tencent-Cloud-SG-hosted Langfuse `sk-lf-` exposure:

1. **Index-match (INFO)**: Shodan dork `http.html:"sk-lf-"` returned hits. The key-prefix string is in the indexed body.
2. **Live re-fetch (LOW)**: GET against the host's HTML returned the actual `sk-lf-{...}` string in the served body (re-verified live, not Shodan cache).
3. **Format validation (LOW)**: Key matched the documented `sk-lf-{uuid}` format. Paired public key (`pk-lf-{uuid}`) also present.
4. **Credential validity (MEDIUM)**: GET `https://us.cloud.langfuse.com/api/public/projects` with HTTP Basic auth `base64(pk:sk)` returned 200 + JSON. Credential is live against the upstream SaaS.
5. **Operator attribution (HIGH)**: Response JSON identified the operating organization name + product name. Both correlate with the host's reverse-DNS attribution, confirming the exposure is real-operator, not a test environment.
6. **Content verification (CRITICAL)**: GET `/api/public/traces/{trace_id}` for one trace returned an internal-chatbot conversation with employee-PII-class content (corporate-policy queries + responses including internal policy detail). One trace was sufficient to verify the data class.

Final tier: **CRITICAL** (Step 6 traversed, content verified).

Per-victim specifics (host IP, key string, organization name, product name, trace IDs, decoded content) are held in the internal recon artifact at `~/recon/cost-billing-analytics-2026-05-19/` and are not published in the public methodology pending disclosure routing.

## Diagnostic signals at each step

**Step 1 — Index-match**: A Shodan body dork on a known credential prefix returns >0 hits.
- Langfuse: `sk-lf-`, `pk-lf-`
- Helicone: `sk-helicone-`
- Stripe: `pk_live_`, `sk_live_`, `pk_test_`, `sk_test_`
- OpenAI: `sk-` (too broad; needs co-anchor)
- Anthropic: `sk-ant-`
- GitHub: `ghp_`, `gho_`, `ghu_`, `ghs_`, `ghr_`
- AWS: `AKIA[A-Z0-9]{16}`
- Slack: `xoxb-`, `xoxp-`, `xapp-`, `xoxe-`
- SendGrid: `SG\.`
- Mailgun: `key-[a-f0-9]{32}`
- Twilio: `SK[a-f0-9]{32}`
- Custom vendor-specific prefixes per CHANGELOG.md of each SaaS's SDK

**Step 2 — Live re-fetch**: HTTP GET against the indexed-host's specific path returns the same prefix-matched string. Confirms it's a current-state exposure, not an artifact of Shodan caching.

**Step 3 — Format validation**: regex matches the documented vendor key shape (UUIDv4, length, charset). Failure here means the indexed string was a substring coincidence; abandon.

**Step 4 — Credential validity**: ONE authenticated read-only API call against the vendor's published API endpoint. For Langfuse: `GET /api/public/projects`. For OpenAI: `GET /v1/models`. For Stripe: `GET /v1/balance`. Each vendor has a "is-this-key-live" canonical endpoint.

**Step 5 — Operator attribution**: parse the response from Step 4 for any operator-identifying field. Common patterns:
- `organization.name`, `organization.id`
- `account.email`, `account.name`
- `project.name`, `app.name`
- `user.email`, `user.id`
- Cert-CN or account-ID embedded in the response

**Step 6 — Content verification**: GET one minimal data record. For Langfuse: `GET /api/public/traces/{id}` for one trace. For Stripe: `GET /v1/customers?limit=1`. For OpenAI: examine usage logs. **Stop after one record**. The single record either confirms or refutes the data class tier (PII / PHI / financial / source code / pre-launch product).

## Procedural rules this insight generates

1. **Tier-attach happens at the deepest step verified, not at the first.** A finding at Step 1 is INFO; do not call it CRITICAL because the key prefix suggests it could be.
2. **Each step requires authorization for the next.** Cross-stepping requires explicit operator (Cowboy) re-authorization when the auto-mode classifier gates. Document the per-step authorization.
3. **Step 6 is restraint-line-crossing.** Reading one operator data record is real privacy / data-access. Only proceed when (a) explicit re-authorization is in hand and (b) the tier promotion materially matters (i.e., the finding is otherwise stuck at HIGH and CRITICAL would change disclosure routing / urgency).
4. **Document the chain in the case study.** Per-host tier-promotion chain should be enumerated explicitly: Step 1 → 2 → 3 → 4 → 5 → 6, what was verified, what was not, what was inferred.
5. **Class-generalization rule**: once the chain runs on one host of a credential class, the dork pattern (Step 1) becomes a reusable cross-survey tool. Add the dork to `shodan/queries/26-exfiltrated-credentials-in-html.md` (creating the section if needed). Each new credential prefix the methodology validates expands the catalog.

## Relationship to prior insights

- **Insight #4 (verify before claiming exploitable)**: This insight operationalizes #4 for the credential-exposure case. The six steps are the verification operationalization.
- **Insight #6 (conjunctive marker-anchored matchers)**: applied at Step 1 (use anchored dork patterns, not bare prefix). Some prefixes are too short to anchor; combine with vendor-specific co-anchor.
- **Insight #33 (side-channel attribution via registry catalog)**: same family. Both are content-revealed-via-public-surface findings. #33 uses Docker Registry catalog as the side channel; #38 uses leaked credentials as the side channel.
- **Insight #36 (PaaS build-arg secret-baking)**: source of many Step 1 hits. The PaaS leak class explains HOW the credential got into public HTML in the first place. #36 produces the candidate population; #38 verifies it.

## Open questions

- **How many credential classes have a "verify-validity" canonical endpoint?** Mapping vendor by vendor would let us run the chain at scale across all known prefixes. Candidate list: OpenAI, Anthropic, Stripe, Slack, GitHub, GitLab, AWS, GCP, Azure, SendGrid, Twilio, Helicone, Lakera, Humanloop, Langfuse, LangSmith.
- **What's the typical FP rate at Step 3?** How often does a Shodan-indexed string that matches the prefix turn out to be a format-mismatched substring? Probably low (key prefixes are specifically designed to be distinctive).
- **Is there a way to do Step 6 without crossing the privacy line?** Could the operator be notified BEFORE Step 6 is exercised? Yes — Step 5 is sufficient for disclosure routing; Step 6 only matters for severity prioritization. Default: stop at 5, escalate to 6 only when severity matters for disclosure timing.

## Tooling

A reusable probe lives at `~/recon/tools/exfil_cred_verify.py` (created 2026-05-19 alongside this insight). It takes a credential prefix + verify-endpoint + content-endpoint per vendor and runs Steps 1-6 with --max-step controls.

A query catalog with vendor-specific prefixes lives at `shodan/queries/26-exfiltrated-credentials-in-html.md`.

## See also

- `case-studies/commercial/cost-billing-analytics-survey-2026-05-19.md`: source survey (the 43.156.249.64 Jasmine HR-GPT exposure)
- `insight-04-whois-driven-contact-resolution.md`: complement at the operator-attribution layer
- `insight-06-conjunctive-matchers-required.md`: anchoring discipline for Step 1 dorks
- `insight-33-side-channel-attribution-via-registry-catalog.md`: sister-pattern at the registry-catalog side channel
- `insight-36-paas-build-arg-secret-baking.md`: explains how the credential reaches public HTML
