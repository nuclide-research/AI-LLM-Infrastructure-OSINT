# Cat-33 Lane C platoon -- Inbox Agent / Workspace Addon Middleware

_Created 2026-06-07. Companion to the Phase 3B dispatch spec (`research-program/cat33-phase3b-three-lane-dispatch-2026-06-07.md`) and the Cat-33 deep brief (`categories/33-ai-email-guardrails-deep-brief-2026-06-06.md`). Sibling platoon files: Lane B (`cat33-lane-b-vendors-2026-06-07.md`), Lane D (`cat33-lane-d-vendors-2026-06-07.md`)._

Lane definition: vendors that sit inside the Microsoft 365 / Google Workspace permission model as an addon and intercept agent send via Graph API / Gmail API hooks. Permission-scope governance is the lever; the OAuth scope manifest is the threat-model surface; per Lane-C discipline, scope manifests are READ, not exercised.

---

## Vendors covered

| Vendor | Apex | Stage | Lane verdict | Tome JSON |
|---|---|---|---|---|
| Clawvisor | clawvisor.com (OSS at github.com/clawvisor/clawvisor) | YC 2026, OSS-first | **Lane C confirmed** -- but not as Workspace addon; as per-operator OAuth client wrapping Gmail/Graph APIs | `tome/platforms/clawvisor.json` |
| Alter | alterai.dev (marketing) / alterauth.com (product) | YC W2026 | **Lane C confirmed** -- per-operator OAuth-credential layer across 60+ providers | `tome/platforms/alter.json` |
| Salus | usesalus.ai (corrected apex) | YC W2026, $4M | **Lane C absent** -- product is tool-call proxy (Lane B), not Workspace addon | `tome/platforms/salus.json` (stub for dedup + apex correction) |

Three targets after dedup and verification. Lane-empty short-circuit not triggered.

---

## Apex resolution corrections

- **Salus**: brief listed `salus-ai.com` for verification. Refuted -- that apex is the Italian medication-management product "Salus AI Designed for Life" (Astro landing, unrelated). Lane B platoon flagged the blocker without resolution. Lane C resolved via `ycombinator.com/companies/salus` -> linked website `https://www.usesalus.ai/` -> confirmed landing tagline "A runtime for AI agents that act." Founders Kevin + Vedant Singh (Stanford CS roommates). `trysalus.ai` is a registered variant (DMARC ruf=ceo@trysalus.ai) but Cloudflare-blocked from passive curl, likely an admin/billing host or pre-launch holding apex.
- **Alter**: brief listed `alter.dev` for verification. Refuted -- `alter.dev` has no A record (MX only, pointing at mail.alter.al, a separate Albanian-language vendor). Real marketing apex is `alterai.dev`; real product/docs apex is `alterauth.com` (per the published llms.txt at github.com/AlterAIDev/docs/main/llms.txt).
- **Clawvisor**: brief apex `clawvisor.com` confirmed first try.

---

## OAuth scope manifest -- the load-bearing finding for this lane

Discipline: READ, do not exercise. Captured from published source (Clawvisor's adapter YAMLs and adapter.go scope constants; Alter's published docs repo at AlterAIDev/docs).

### Clawvisor

Source-of-truth: `internal/adapters/definitions/*.yaml` in the public OSS repo. Corroborated by `internal/adapters/google/gmail/adapter.go` Go scope constants.

**Google scopes requested:**

```
Gmail:    https://www.googleapis.com/auth/gmail.readonly
          https://www.googleapis.com/auth/gmail.send
          https://www.googleapis.com/auth/gmail.modify   # RESTRICTED (CASA-required)
          https://www.googleapis.com/auth/userinfo.email
          https://www.googleapis.com/auth/userinfo.profile

Calendar: https://www.googleapis.com/auth/calendar.readonly
          https://www.googleapis.com/auth/calendar.events
          https://www.googleapis.com/auth/userinfo.email

Drive:    https://www.googleapis.com/auth/drive.readonly
          https://www.googleapis.com/auth/drive.file
          https://www.googleapis.com/auth/userinfo.email

Contacts: https://www.googleapis.com/auth/contacts.readonly
          https://www.googleapis.com/auth/userinfo.email
```

**Microsoft Graph scopes requested:**

```
Outlook:  Mail.Read
          Mail.Send
          Calendars.ReadWrite
          offline_access

OneDrive: Files.ReadWrite
          offline_access

Teams:    microsoft_teams.yaml.disabled   # shipped disabled 2026-06-07
```

**Scope-breadth findings:**
- `gmail.modify` is a Google-classified RESTRICTED scope. Self-hosted Clawvisor deployments inherit CASA (Cloud Application Security Assessment) burden on the operator's own GCP project. Hosted Clawvisor carries CASA itself.
- `Mail.Send + Calendars.ReadWrite + Files.ReadWrite + offline_access` under one Microsoft consent is a wide-aperture grant. `offline_access` enables long-lived refresh tokens; vault.key disclosure plus refresh token = attacker re-authentication until tenant admin revokes.

### Alter

Source-of-truth: `reference/oauth-providers/{google,microsoft}.mdx` in github.com/AlterAIDev/docs.

**Google scope catalog (operator-selectable):**

```
Gmail:    gmail.readonly, gmail.send, gmail.compose, gmail.modify
Calendar: calendar.readonly, calendar.events
Drive:    drive.readonly, drive.file, drive   # 'drive' = full access; broadest available
```

**Microsoft Graph scope catalog (operator-selectable):**

```
offline_access
Mail.Read, Mail.Send
Calendars.Read, Calendars.ReadWrite
Files.Read, Files.ReadWrite
```

**Alter internal capability scopes (Alter's own API key system, not the provider):**

```
grants:read, grants:write
agents:read, agents:write
connect:create
(full catalog: portal.alterauth.com/scopes)
```

**Scope-breadth findings:**
- Alter's design exposes the full Google scope catalog including the unrestricted `drive` (full read/write/delete). Per-call narrowing via Connect SDK `allowed_scopes` is opt-in; the default is operator-broad.
- App-level Alter API keys carry a broad default set; minting per-agent keys with full app scope is the convenient-but-wrong default. `with_constraints(scopes=[...])` provides intersection-only attenuation, but operators must call it explicitly.
- `scope_merge: true` (Clawvisor's INTEGRATION_YAML_SPEC.md, mirrored conceptually in Alter docs) means new scopes merge with existing credential rather than replace -- forgotten/over-broad past scopes persist silently across consent refreshes.

### Salus

Lane C surface absent. Salus's architecture is **policy-aware proxy in front of every tool your agent already calls. Change the URL, the agent does not know the difference.** This is Lane B (API gateway), not Lane C (Workspace addon). No Gmail / Graph OAuth scope manifest is published because the integration mode is endpoint-URL-rewrite, not addon-install. Cross-lane dedup note: Salus belongs to Lane B; this platoon notes apex correction (`usesalus.ai`, not `salus-ai.com` / `trysalus.ai`) and writes a stub JSON in tome for tracking.

---

## Workspace Marketplace / AppSource probe

Probed Google Workspace Marketplace and Microsoft AppSource by passive HTTP scrape. Both surfaces hydrate client-side; the static HTML response carries no result data. Headless-browser probing was not exercised under restraint discipline.

**Verdict:** for all three vendors, no Marketplace / AppSource listing was confirmed via passive scrape. The integration shape across this cohort is per-operator OAuth client registration in the customer's own GCP / Azure AD tenant, not a Marketplace addon. This is the operative finding -- see Insight #79 candidate below.

---

## DNS posture summary

| Vendor | A | MX | DMARC | SPF |
|---|---|---|---|---|
| Clawvisor (`clawvisor.com`) | Google parking (216.239.32-38.21) | smtp.google.com | `p=none; rua/ruf=eric@clawvisor.com; adkim=s; aspf=s` | `include:_spf.google.com -all` |
| Alter (`alterai.dev`) | Cloudflare (104.18.16-17.173) | smtp.google.com | `p=none; rua=Cloudflare DMARC + dmarc@alterai.dev` | `include:_spf.google.com ~all` |
| Salus (`usesalus.ai`) | Vercel-adjacent (216.198.79.1) | smtp.google.com | `p=none;` (no rua/ruf) | absent (gap, same class as Sluice) |
| Salus (refuted `salus-ai.com`) | 76.76.21.21 (Vercel) | salusai-com01c.mail.protection.outlook.com | absent | `include:spf.protection.outlook.com -all` |

All three Lane C vendors run DMARC `p=none`, consistent with Insight #78 (DMARC posture as YC-current cohort proxy). Clawvisor's strict alignment (adkim=s, aspf=s) under p=none is unusual and signals operator competence.

---

## Founder / operator attribution

- **Clawvisor**: DMARC `rua/ruf=eric@clawvisor.com` leaks founder email. Single visible operator "Eric". Repo top author should corroborate; not extracted this session.
- **Alter**: GitHub account is `github.com/AlterAIDev` (user, not org). YC W2026, "Backed by Combinator" tile on landing.
- **Salus**: founders Kevin (last name unconfirmed) + Vedant Singh (Stanford CS, AI researcher), per YC company profile. Roommates at Stanford. GitHub org `trysalus` exists (created at YC W2026 time) but has 0 public repos.

---

## Deployment artifacts observed (OSS Clawvisor only)

Public source-of-truth at `github.com/clawvisor/clawvisor`. Notable artifacts:

- `internal/adapters/definitions/*.yaml` -- the authoritative scope catalog per provider. Tracking this file across releases gives a scope-creep timeline.
- `security/semgrep/` + `security/zap/` -- operator-side SAST + DAST CI harness shipped in-repo. Visible baseline.
- `config.example.yaml` -- production-relevant defaults: `auth.max_users=0` (unlimited), `callback.require_https=false`, `vault.backend=local`, `approval.on_timeout=fail` (safe). Operators flipping `on_timeout=skip` silently auto-approve expired HITL requests.
- `render.yaml` + `deploy/` -- Cloud Run / Render manifests, plus K8s deploy spec likely.
- `skills/` -- Claude Code skill files shipped in-repo for the agent-side integration.
- No plaintext API keys, no JWT defaults, no hardcoded OAuth client_secret observed in passive read. Active GitHub code search for secrets returned 401 unauthenticated; not exercised under restraint.

For Alter (closed source): only the public docs repo at `github.com/AlterAIDev/docs` was probed. No plaintext credentials in the docs source.

---

## Blockers and gaps

- **crt.sh persistently returning HTTP 502** during the platoon window. crt.sh subdomain enumeration was not completed for any of the three apexes. Retry recommended off-platoon. CT-log pivot available via Censys (1 credit per host) if priority.
- **Marketplace listings** (Google Workspace + Microsoft AppSource) not confirmable via passive scrape; requires headless-browser to render SPA. Not exercised under restraint -- and the operative finding (per-operator OAuth client, not addon) makes Marketplace presence the wrong question for this cohort.
- **trysalus.ai** Cloudflare-blocked from sandbox curl. Confirmed via dig (162.255.119.66, ceo@trysalus.ai DMARC contact) but landing content unverified. Likely an admin/billing variant.
- **herald** not exercised. Per Lane-C discipline, the threat surface is the OAuth scope catalog (read), not network endpoints (probe). Building IP:port lists for vendors whose actual product runs behind Cloudflare/Cloud-Run would replicate the Lane B platoon's approach and miss the Lane C surface. Skipped intentionally.

---

## Codified Insight #79 candidate -- Lane C AI-Agent-Authorization-Gateway integration pattern

For the AI-agent-authorization-gateway product class as it stands in YC W2026 -- 2026, the operative Workspace / Microsoft integration shape is **per-operator OAuth client registration in the customer's own GCP / Azure AD tenant**, not a Workspace Marketplace / AppSource addon. The Lane C platoon found zero detectable Marketplace listings across three target vendors (Clawvisor, Alter, Salus). Identifying signals:

1. The vendor publishes a docs page titled "Google OAuth Setup" / "Azure AD Setup" walking the operator through their own Cloud Console. Clawvisor ships `docs/GOOGLE_OAUTH_SETUP.md`; Alter ships `reference/oauth-providers/{google,microsoft}.mdx`.
2. The vendor exposes a scope **catalog** that operators select from per integration, rather than a fixed addon scope set. Clawvisor ships scope sets per adapter YAML; Alter ships a selectable scope catalog per provider.

Implication for OSINT: the right Lane C dork is cert-SAN on the vendor apex, not Marketplace search. The threat-model surface is the **published scope catalog**, not a Marketplace install count.

Confidence: medium (N=3 vendors). Track against the next Lane C cohort that emerges. If the pattern persists, the "Workspace addon" lane framing in the original Cat-33 brief may need rewording to "Workspace permission-model client" -- the trust boundary is still inside the customer's Workspace tenant, but the install shape is OAuth-consent, not Marketplace-addon.

---

## Cross-lane dedup

- **Salus** appears in Lane B too. Lane B noted apex blocker (`salus-ai.com` refuted); Lane C resolved (`usesalus.ai`). Lane B should own the canonical Salus platform JSON; Lane C ships a stub for tracking + the apex-correction record.
- Sluice (Lane A + B) does not overlap with Lane C.

---

## Sources

- Cat-33 deep brief (`categories/33-ai-email-guardrails-deep-brief-2026-06-06.md`)
- Phase 3B dispatch spec (`research-program/cat33-phase3b-three-lane-dispatch-2026-06-07.md`)
- Lane B platoon writeup (`data/platform-intel/cat33-lane-b-vendors-2026-06-07.md`)
- github.com/clawvisor/clawvisor (PRIMARY OSS source)
- github.com/AlterAIDev/docs (PRIMARY public docs source for Alter)
- ycombinator.com/companies/salus (PRIMARY apex resolution for Salus)
- dig A/MX/TXT/_dmarc against each apex 2026-06-07
- HTTP fetch of each apex 2026-06-07
- crt.sh: BLOCKED (502 persistent)
- Workspace Marketplace + AppSource: passive SPA scrape, no static results
