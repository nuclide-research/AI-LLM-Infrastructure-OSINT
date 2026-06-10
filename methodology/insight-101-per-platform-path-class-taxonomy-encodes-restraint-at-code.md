---
type: methodology
insight_number: 101
title: "Per-platform path-class taxonomy encodes restraint at code level: DOC / READ / COMPUTE / ADMIN — verify-scripts ask 'class?' not 'pattern-match URL?'"
status: candidate
codified: 2026-06-10
source_survey: Cat-LMDeploy 2026-06-10 (3-host CN-skewed cohort)
falsifiability_tier: high
falsified_by: an OSS inference-serving platform whose route set does not decompose cleanly into the 4-class structure, OR a survey where the 4-class allowlist (DOC|READ only) is insufficient to confirm platform identity + ethics class
related_insights: [41, 52, 68, 98]
---

# Insight #101 — Per-platform path-class taxonomy encodes restraint at code level

## The pattern

OSS inference-serving platforms (LMDeploy, vLLM, SGLang, TGI, AIBrix, Triton) ship between 10 and 30 HTTP routes per server. Verify-scripts that pattern-match URLs ("if path == '/v1/models' then GET; if path startswith '/v1/chat' then SKIP") accumulate per-platform special cases and drift. When a new route family ships (LMDeploy's `/distserve/*` P2P control plane added 2026, the Anthropic-compat `/v1/messages` mounted on the same port), the pattern-match approach silently degrades — the verifier either misses the route family or hand-rolls an exception.

A taxonomy that pre-encodes EVERY route into one of four safety classes — **DOC**, **READ**, **COMPUTE**, **ADMIN** — moves the restraint decision from URL-pattern logic into a single allowlist lookup. The verify-script asks `class(path) in {DOC, READ}?` instead of replicating per-platform URL semantics. Restraint becomes a property of the platform record (tome), not the verifier.

## The four classes

| Class | Semantics | Side effects | Verify allowed? |
|-------|-----------|--------------|-----------------|
| **DOC** | Self-describing: schema, UI, health, version, metrics. GET returns identity. | None. Idempotent. | **Yes** — single GET sufficient. Marker-conjunct fingerprint by body. |
| **READ** | Read-only inventory: model list, engine info, sleep state, config dump. GET enumerates what the operator chose to expose. | None. Names are the finding (Insight #41). | **Yes** — GET, capture body, extract field-name set. Do not exfiltrate values beyond minimal severity confirmation. |
| **COMPUTE** | Inference / generation. POST consumes operator-billable resources (GPU, tokens, electricity). | Compute-cost theft surface; prompt-injection surface. No persistent state change. | **No** — proof by READ-class `/v1/models` is sufficient. Calling COMPUTE crosses Insight #98's do-not-call class as applied to billing. |
| **ADMIN** | Lifecycle / model-management / P2P-control. POST mutates persistent operator state. | Destructive (terminate, sleep, weight-update, P2P-drop). | **No** — even on null-auth-default, calling crosses authorized assessment into unauthorized modification. Disclosure body says "admin surface OPEN, not exercised." |

## Empirical basis

### LMDeploy founding case (Cat-LMDeploy 2026-06-10)

Tome's 23 documented LMDeploy paths decompose cleanly:

| Class | Count | Paths |
|-------|-------|-------|
| DOC | 4 | `/`, `/openapi.json`, `/health`, `/metrics` |
| READ | 3 | `/v1/models`, `/is_sleeping`, `/distserve/engine_info` |
| COMPUTE | 7 | `/v1/chat/completions`, `/v1/completions`, `/v1/embeddings`, `/v1/chat/interactive`, `/v1/encode`, `/generate`, `/pooling` |
| ADMIN | 9 | `/terminate`, `/sleep`, `/wakeup`, `/update_weights`, `/abort_request`, `/distserve/p2p_initialize`, `/distserve/p2p_connect`, `/distserve/p2p_drop_connect`, `/distserve/free_cache` |

Total 23 / 23. Zero ambiguous routes. Verify-script allowlist = 7 of 23. The remaining 16 routes are surface-only — their NAMES are the finding (per Insight #41) when surfaced in `/openapi.json`.

### Generalization conjecture (falsifiable)

vLLM (`port:8000`), SGLang (`port:30000`), TGI (`port:80`), Triton (`port:8000`) all share the OpenAI-compat surface (`/v1/models`, `/v1/chat/completions`) and add their own ADMIN families. The 4-class structure is platform-agnostic; the per-class path lists differ. If a future survey discovers an OSS inference platform whose route set does not partition cleanly into the 4 classes, Insight #101 is refuted.

## The discipline this encodes

1. **Restraint at code, not at policy.** Lane C's verify-script imports `tome/platforms/<p>.json :: classes` and refuses any path outside DOC|READ. Refusal counts toward the restraint-violation-zero metric. Per-platform exceptions become tome edits, not verifier patches.
2. **Compute-cost theft is treated as a distinct restraint class.** Insight #98 framed do-not-call physical-safety; this is its OSS-inference analogue. Even with authorization to assess, calling COMPUTE on an unauthorized operator costs them money.
3. **Admin-surface "OPEN, not exercised" is the canonical phrasing.** Disclosure-routing language must distinguish "we found this open" from "we proved it works." Reaching for the second on null-auth-default ADMIN routes is the prosecutorial hook a defender uses to invert the encounter.
4. **Names ARE the finding** (Insight #41) — `/openapi.json` body listing `/update_weights` is sufficient evidence of admin-surface exposure. No POST needed.

## Integration

- Tome platform JSON gets a `path_classes` block: `{"DOC": [...], "READ": [...], "COMPUTE": [...], "ADMIN": [...]}`. Backfill priority: top 10 inference-serving platforms by tome surveyed-population.
- aimap probe-config generator (Stage 0d) reads `path_classes` and emits banner probes for DOC routes only; deep-enum gets READ routes.
- Verify-scripts (Lane C in every parallel-survey) consume `path_classes` directly. Per-platform URL semantics live in tome.
- VisorScuba (Stage 7) compliance scoring upgrades to per-class: an operator with all 9 ADMIN routes null-auth-exposed receives a different score than one with 9 COMPUTE routes — both are critical but the latter is billing-theft surface, the former is destructive surface.

## Cross-jurisdiction note (K0107 atom)

LMDeploy's 100% CN concentration in this 3-host snapshot suggests the disclosure-routing class mapping per host also needs class-aware sub-typing: ADMIN-open + financial-tenant + CN-jurisdiction routes to CNCERT/CC + tenant security@; ADMIN-open + individual + ADSL routes to ISP-abuse + adjacency-pivot CSIRT. Path-class taxonomy at the artifact layer enables jurisdiction-class taxonomy at the disclosure layer. This is the right Lane D output: MAP path classes onto disclosure classes; do not DRAFT.

## Refutation conditions

Insight #101 is refuted if:
1. A surveyed OSS inference platform has a route that materially belongs to none of {DOC, READ, COMPUTE, ADMIN}. (Streaming-only routes that consume compute = COMPUTE. WebSocket routes = COMPUTE or ADMIN by side effect. SSE = COMPUTE.)
2. The allowlist `{DOC, READ}` is insufficient to confirm platform identity, forcing a verifier to call COMPUTE or ADMIN. (Refuted only if no DOC route returns identifying content; not yet observed.)
3. The class boundary leaks: e.g., a documented `/health` (DOC) endpoint accepts POST with a body that mutates state. (LMDeploy's `/terminate` accepts GET — already an ADMIN special-case noted in tome misconfig_patterns. Other platforms may have analogues; treat as platform-specific overrides in the JSON.)

## Status

Candidate. Founding case Cat-LMDeploy 2026-06-10 (3 hosts, n too small for population claim but n=23 paths is large enough for the structural claim). Promotion to confirmed requires (a) 3 additional inference-serving platforms surveyed against the 4-class structure and (b) verify-script consuming `path_classes` from tome without per-platform URL logic.
