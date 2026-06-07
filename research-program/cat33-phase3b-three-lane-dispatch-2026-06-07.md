# Cat-33 Phase 3B — Three-Lane Dispatch Spec

_Created 2026-06-07 as Phase 3B prep work for the 9-item plan. Lane A (MTA-relay) is closed by Sluice. Lanes B/C/D are the remaining work, dispatchable as three parallel OSINT platoons whenever Phase 1 returns compute._

Parent: `categories/33-ai-email-guardrails-deep-brief-2026-06-06.md`. Read that first for the architectural taxonomy and threat model.

---

## Lane B platoon — API Gateway / Bearer-token guardrails

### Scope

The lane sits between an AI agent and an LLM provider over HTTPS with a bearer token. Customer integrates an SDK or curls the JSON contract. Outbound LLM-drafted email is one use case among several, but the same chokepoint covers it.

### Targets

| Vendor | Domain | Stage | Status |
|---|---|---|---|
| AegisAI | aegisai.ai | seed (Sep 2025, $13M, Accel + Foundation Capital) | mislabeled inbound in vendor self-description; the API gateway lane is the real fit. Re-verify. |
| Salus | salus-ai.com (verify) | YC W2026, $4M | adjacent; has PII + budget + content moderation primitives. Email adapter probably not yet shipped. |
| Sluice (B-mode) | sluice.email | pre-seed | already surveyed in Lane A; Lane B mode = same MTA exposed via API contract. |
| Prompt Security | prompt.security | Series A | LLM-agnostic proxy. Email connector not public; verify whether one exists. |
| Lakera Guard | lakera.ai | Series A | dedicated email connector unknown. |

### Per-target deliverables

For each: tome platform JSON, dork set (3 tiers: basic / strict / version), default-port inventory, fingerprint markers, public auth posture, disclosure contact.

### Probe plan (after platoon returns)

1. dig `_dmarc`, `_dkim`, MX on each apex (feeds Insight #80).
2. crt.sh for subdomain population (api., gateway., guard., shield.).
3. Shodan facet `ssl.cert.subject.cn:` on each apex.
4. herald against the public API base for `/health`, `/v1/models`, `/v1/policies`, `/openapi.json`.
5. aimap fingerprint if any candidate platform JSON warrants a new entry.

---

## Lane C platoon — Inbox Agent (Workspace addon middleware)

### Scope

Sits inside the Microsoft 365 / Google Workspace permission model as an addon. Intercepts agent send via Graph API / Gmail API hooks. Permission-scope governance is the real lever.

### Targets

| Vendor | Domain | Stage | Status |
|---|---|---|---|
| Clawvisor | clawvisor.com (verify) | YC 2026 (OSS) | already wires Gmail + Slack; needs output-content scanner. |
| Salus | salus-ai.com | YC W2026 | C/D dual lane; the Workspace integration mode lives here. |
| Alter | alter.dev (verify) | YC W2026 | zero-trust IAM for agents; tool-call guardrails. |

### Per-target deliverables

Same shape as Lane B platoon.

### Probe plan

1. Marketplace presence: Google Workspace Marketplace, Microsoft AppSource listing scrape.
2. OAuth scope manifest if published.
3. dig + crt.sh per apex.
4. GitHub org probe for OSS vendors (Clawvisor) — issues, deployment artifacts, .env leaks.
5. herald against any public-API surface.

### Special discipline note

Workspace addons request OAuth scopes from the customer. The scope manifest is the threat-model surface. Read it; do not exercise it. Names ARE the finding.

---

## Lane D platoon — SDK / Wrapper guardrails (broadest, mostly OSS)

### Scope

Library: `lib.guard(message)` before `send_email()` tool-call. The wrapper sits inside the agent process. Email is one of many tool-calls it can wrap. Many of these are OSS, which means the threat surface is in operator deployments, not vendor infra.

### Targets

| Vendor | Domain / Repo | Stage | Status |
|---|---|---|---|
| Cascade | cascade.dev (verify) | YC W2026 | guardrails + testing for production AI. |
| Galini | galini.ai (verify) | YC F2024 | 100+ pre-built guardrails. Generic. |
| LlamaFirewall | github.com/facebookresearch/PurpleLlama | OSS (Meta) | arXiv 2505.03574. Framework, not service. |
| OpenGuardrails | github.com/openguardrails/openguardrails | OSS | community-driven. |
| Invariant Gateway | github.com/invariantlabs-ai/invariant | OSS | LLM proxy. |
| LiteLLM (policy mode) | github.com/BerriAI/litellm | OSS | already covered in Cat-05 gateways for the inference side; Lane D mode is the policy-hooks side. |

### Per-target deliverables

For OSS: a vendor JSON describing the framework, not the operator. Tome platform entries should distinguish FRAMEWORK (the OSS project) from DEPLOYMENT (a customer running it). The schema-recon discipline applies: fingerprint the deployment, not the schema, and do not exfiltrate.

### Probe plan

1. GitHub org probe per project for issues, configs, deployment artifacts.
2. Shodan facet for distinctive `Server:` headers or banner strings from the OSS project.
3. CVE catalog lookup (NVD + GitHub Advisories).
4. herald scaffolding if the OSS project exposes a network endpoint by default.

### Special discipline note

OSS frameworks deployed on customer infrastructure are a population-substitution risk: a dork that selects the framework will also select the misconfigured deployments. This is exactly the dork-population-substitution pattern from reference-dork-population-substitution. Expect the same blind spots and probe accordingly.

---

## Dispatch readiness

When Phase 1 lanes 1A and 1B return, dispatch the three Lane B/C/D platoons in parallel as subagents (general-purpose, run_in_background). Each platoon prompt should reference this scope spec as the canonical brief. Per-platoon time budget: 90 minutes max.

Cross-platoon dedup: the three lanes overlap on Salus (B+C), LiteLLM (D + Cat-05), Sluice (A+B). Each platoon should NOTE the overlap and avoid duplicating work; the first platoon to reach an overlapping vendor owns the platform JSON.

## Output destinations

- `~/AI-LLM-Infrastructure-OSINT/data/platform-intel/cat33-lane-{b,c,d}-vendors-2026-06-07.md` per platoon
- Tome platform JSONs under `~/tome/` (canonical corpus)
- Dork additions to `shodan/queries/33-ai-email-guardrails.md`
- New aimap fingerprints scaffolded from `tome probe <platform>` for any platform missing one

## Stop conditions

If a platoon's vendor count for its lane drops below 3 after deduplication and verification, the lane is empty enough to short-circuit: write a one-paragraph "lane empty" note and return. Cat-33 is small by design; empty lanes are a finding, not a failure.
