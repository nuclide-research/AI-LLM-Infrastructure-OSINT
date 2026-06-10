# Insight #94 — Hybrid Tier-A*/C Platforms Escape Existing Tier Vocabulary (Candidate)

_NuClide Research · 2026-06-09 · Origin: Cat-Tabby survey, Tabby webserver-mode auth posture._

---

## Statement

The auth-on-default thesis (methodology §1) uses a four-tier vocabulary: **Tier-A** (no auth concept), **Tier-A\*** (auth optional, off by default), **Tier-B** (setup wizard required), **Tier-C** (auth on by default). The vocabulary assumes a platform inherits a single tier across its full HTTP surface.

A *hybrid* platform deliberately mixes tiers: its primary front-end (the path operators read about in the README) ships at one tier while a documented "operational API" or "health check" surface ships at a different tier. The published tier is the front-end's tier; the unpublished tier governs the operational surface. Surveys that classify the platform by its README tier miss the operational surface; surveys that classify by the operational surface miss the secured front-end.

Tabby (TabbyML) v0.11.0+ in webserver mode is the canonical example. Its `--webserver` flag enables a Tier-C auth-on-default Next.js SPA (sign-in page, admin-account-create on first visit, JWT session). But the upstream documentation lists three "always-open" endpoints — `/v1/health`, `/v1beta/models`, `/v1beta/server_setting` — at Tier-A. A survey that probes the webserver and finds the sign-in page concludes Tier-C; a survey that probes the API and finds a 200 on `/v1/health` concludes Tier-A. **In practice neither verdict is wrong; both are partial.**

The Cat-Tabby 2026-06-09 survey found that the operational surface tier behaves differently per deployment:

| Operator deployment | `/v1/health` | `/v1beta/models` | `/v1beta/server_setting` | Front-end tier |
|---|---|---|---|---|
| 5.78.203.59 (`ide.cohesia.ai`) | 401 | 401 | 401 | C (sign-in page) |
| (`--no-webserver` API-only deploy) | 200 + HealthState | 200 + model list | 200 + config (per upstream docs) | n/a |
| Mixed-config deploy | 200 + HealthState | 401 | 401 | C |

Three distinct auth postures from the same Tabby v0.11.0+ release. The Cat-Tabby Stage -1 squad reported `/v1/health` as "always-open on all versions" — derived from the upstream docs — but the actual population has at least three configurations of this surface.

## Why the tier vocabulary fails

The four-tier vocabulary descends from Insight #13 ("shipping defaults are load-bearing"). The lesson is that operator skill matters less than the shipping default — Phoenix's `PHOENIX_ENABLE_AUTH=False` produces 25% unauth at population scale because the default is the default.

For *hybrid* platforms the shipping default is **per-endpoint**, not per-host. Tabby's docker-compose quickstart enables `--webserver` (Tier-C for the front-end) AND leaves the operational API endpoints reachable without auth in some configurations. The operator's deployment decision selects which subset of endpoints stays Tier-A. A single-tier population statistic ("Tabby is X% unauth") obscures the real exposure model.

## The discrimination probe

A hybrid platform requires **simultaneous probes on both surfaces** to classify auth posture correctly:

- Front-end identity: `/` SPA title, `/auth/signin` or `/login` redirect — establishes Tier-C front-end
- Operational identity: `/health`, `/v1/models`, `/api/config` — establishes the operational tier

Per-deployment outcomes:

| Front-end probe | Operational probe | Verdict | Risk |
|---|---|---|---|
| 200 + brand title | 200 + data | Hybrid; operational surface open | Compute exfil + config leak |
| 200 + brand title | 401 / 403 | Hybrid; operational surface secured | Identity-only finding |
| 200 + sign-in page | 200 + data | Hybrid; opera surface open even with front-end secured | Subtle: operator believes secured |
| 401 / 403 on all probes | 401 / 403 on all probes | Single-tier C | Working as intended |
| 200 + data on all probes | 200 + data on all probes | Single-tier A | Full exposure |

Row 3 — front-end secured, operational surface open — is the **silent class**. Operators believe their deployment is secured because they set up admin credentials and see the sign-in page work. The operational endpoints remain reachable in the same deployment because they ship at Tier-A by design. This class is the one a survey using a single probe pattern will systematically misclassify in either direction depending on which probe runs first.

## Class membership beyond Tabby

The pattern appears anywhere a platform documents a "health" or "metrics" endpoint and ships it Tier-A "for ops integration" alongside a Tier-C user-facing console. Candidates:

- **Argo Workflows** — `/api/v1/info` Tier-A (documented for ops integration) alongside Argo Server `/workflows` Tier-C
- **MLflow tracking server** — `/api/2.0/mlflow` Tier-A by default (no built-in auth concept) alongside HTTP basic when wrapped in nginx
- **Langfuse v2** — `/api/public/health` Tier-A alongside `/api/auth/signin` Tier-C
- **Prometheus** — Tier-A across the board (`/api/v1/targets`, `/metrics`, `/-/healthy`) — single-tier, not hybrid; included as comparison
- **Phoenix (Arize)** — Tier-A* on `/v1/traces` + Tier-A on `/v1/sessions`; the `/login` setup gates only the management plane

The hunt-focus implication: surveys should explicitly **classify each documented endpoint into its own tier** and report the per-endpoint tier distribution, not a single-platform tier. This is a notational update to the methodology's tier vocabulary, not a discard.

## Tooling

aimap fingerprints should encode the per-endpoint tier expectation. The current `Severity` field on a fingerprint is a single-host classification; for hybrid platforms it should be a *map* keyed on which probe fired:

```go
// Pseudo-extension; currently aimap reports one severity per service
SeverityPerProbe: map[string]string{
    "/auth/signin":         "info",   // Tier-C front-end matched
    "/v1/health":           "high",   // Tier-A operational surface matched
    "/v1beta/server_setting": "high", // Tier-A config-leak matched
}
```

The deep enumerator should report each Tier-A operational endpoint that returned 200-with-data as an individual finding, not roll them up into a single host-level "unauth Tabby" tag.

## Action / discrimination

When a Stage -1 squad reports a platform as Tier-A or Tier-C, ask: *does the upstream README distinguish between the front-end and an operational/ops-integration surface?* If yes, the platform is a hybrid candidate, and Stage 3v must probe both surfaces independently. The squad's tier verdict is then a *per-surface* verdict, not a per-platform verdict.

## Related

- Insight #13 (shipping defaults are load-bearing) — the parent insight; #94 extends it to per-endpoint shipping defaults.
- Insight #16 (a 200 is identity not auth state) — applies *per probe* on a hybrid platform. The 401-on-/v1/health that the 5.78.203.59 host returned was identity-confirming via /auth/signin and auth-on via the operational probe simultaneously.
- Insight #8 (auth-bypass hides from entry-point-only fingerprints) — the inverse-direction sibling. #8 catches when the secured-looking entry point hides the open subsystem; #94 catches when the secured-looking platform hides the open API.
- Insight #6 (conjunctive marker-anchored matchers) — the per-probe identity contract still applies; #94 says the *severity* contract is per-probe too.

## Case study reference

`case-studies/commercial/cat-tabby-survey-2026-06-09.md` — Cat-Tabby Code-Assistant Stragglers Survey.
