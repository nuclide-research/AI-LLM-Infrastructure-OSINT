# Insight #83: Inbox-agent guardrails in 2026 are per-operator OAuth clients in the customer's own tenant, not Workspace Marketplace addons. The right dork is cert-SAN, not Marketplace search.

**Codified:** 2026-06-07. Cat-33 Phase 3B Lane C survey.
**Source:** `data/platform-intel/cat33-lane-c-vendors-2026-06-07.md` (3 vendors).
**Family:** Insight #75 (HTTP admin ports kill cert-pivot), Insight #65 (TLS cert dork selection bias), Insight #71 (network placement as auth).
**Falsifiability tier:** medium. n=3 confirmed at architectural level; the next sibling vendor would promote to high.

## The pattern

The Cat-33 deep brief (2026-06-06) described Lane C as "Workspace addon as middleware" with the implicit assumption that Google Workspace Marketplace and Microsoft AppSource are the discovery surfaces. Three Lane C vendors (Clawvisor, Alter, Salus) all REJECT this architecture. They deploy as per-operator OAuth clients registered inside the customer's own Google Cloud Platform project or Azure Active Directory tenant, not as Marketplace listings.

| Vendor | Discovery surface | Wrong assumption | Right approach |
|---|---|---|---|
| Clawvisor | per-operator GCP OAuth client | Marketplace search returns 0 hits | cert-SAN on `clawvisor.com` apex, GitHub OSS repo |
| Alter | per-operator OAuth client, 60+ provider catalog | AppSource search returns 0 hits | cert-SAN on `alterauth.com` product apex |
| Salus | endpoint-URL-rewrite architecture (Lane B, not Lane C) | Marketplace search returns 0 hits | cert-SAN on `usesalus.ai` apex (corrected from salus-ai.com) |

All three are AI-startup-era patterns: ship a thin client SDK, ask the customer to register an OAuth app in their own tenant, hold no Workspace-scope consent in vendor-side infrastructure. The Marketplace addon model belongs to a previous deployment generation (Abnormal Security, Material Security, Sublime). New vendors do not deploy this way.

## Why this matters

The discovery methodology for Lane C had to be rebuilt from "scrape Marketplace listings" to "cert-pivot the vendor apex and follow OAuth-client registration documentation backward." This is not a small change in tooling. It is an architectural shift in how Lane C vendors deploy, and the deep-brief assumption that they would resemble Abnormal/Material is now refuted at n=3.

There is a corollary about discovery exhaustiveness. A Marketplace-only researcher would have concluded that Cat-33 Lane C is empty. The lane is not empty; it is mis-discovered. This is the same risk shape as Insight #65 (TLS cert dork selection bias) at the discovery-surface level: the dork ladder must include the architecture's actual discovery surface, not a default that the population has migrated away from.

## Founder-attribution side finding

Clawvisor's DMARC `ruf` and `rua` records leak `eric@clawvisor.com` as the single visible operator. This is the same class of leak that Insight #80 (DMARC funding-stage proxy) used as a passive primitive, here surfacing personnel attribution. Worth folding into the DMARC primitive catalog as a separate use case: DMARC reporting-address leakage as a one-call founder-identification probe.

## How to apply

- For Cat-33 Lane C and structurally similar lanes: do not scrape Marketplaces. The 2026 vendor population is not there.
- Discovery starts at the vendor apex: cert-SAN sweep + GitHub org probe + documentation pages that describe OAuth-client setup.
- For OSS-Lane-C vendors (Clawvisor): the GitHub org is the platform; deployment artifacts are the threat surface.
- The OAuth scope manifest in vendor documentation is the threat-model surface. Read it. Do not exercise it. The scopes a vendor REQUESTS are the finding; the data a vendor READS under those scopes is downstream and out of scope for restraint-discipline OSINT.

## Sample scope highlights from this survey (read-only, do not exercise)

- Clawvisor Google: `gmail.readonly + gmail.send + gmail.modify` (RESTRICTED, CASA-required) + calendar.events + drive.file + contacts.readonly.
- Clawvisor Microsoft: Mail.Read + Mail.Send + Calendars.ReadWrite + Files.ReadWrite + offline_access (long-lived refresh tokens; vault-key disclosure means persistent re-auth surface).
- Alter Google: full operator-selectable catalog including `drive` (full read/write/delete) scope, broadest available; per-call narrowing is opt-in.
- Alter Microsoft: mirrors Clawvisor's catalog.
- Salus: n/a, endpoint-URL-rewrite architecture, no Workspace integration.

The scope catalog is itself the finding. It tells a customer security team what the vendor is asking for access to, before any deployment happens.

## DCWF KSAT fit

- 672: K7044 (V&V tooling rebuild required), T5904 (risk assessment: scope manifests as risk surface).
- 733: T5882 (Responsible AI process: OAuth scope review IS the RAI review for Lane C), K7040 (PHI/PII: gmail.modify scope is unbounded read/write of customer mailbox).
- Overlap: K7003 (AI security risks at the architecture level), K22 (OAuth flow on TLS).
