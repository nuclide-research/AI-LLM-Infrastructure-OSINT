---
type: survey
---

# Data-Labeling Population Survey (2026-05-16)

_NuClide Research · 2026-05-16 (third survey in the day's 4-category batch)_
_Closes: category 22 (data-labeling) — Label Studio / CVAT / Doccano / Argilla / Prodigy_

---

## Summary

Survey of the data-labeling platform population — the systems that store training-data annotation tasks, often containing PII or sensitive labels. Smaller surface than other categories surveyed today; the mixed result is informative.

- 772 unique candidates harvested across the 5 platforms
- Probed via `fast_enum_data_labeling.py` (~2 min total)
- **16 unauth Prodigy** instances (Prodigy is by-design auth-free for its annotation web UI — see methodology section)
- **0 Label Studio unauth** at the data layer (3 real instances on legacy 0.7.x; all auth-gated when projects requested)
- **0 CVAT unauth** at the data layer (auth-gated where reachable)
- **0 Doccano unauth** at the data layer (auth-gated where reachable)
- **0 Argilla unauth** (same 4 instances surfaced in [`agent-memory-population-survey-2026-05-16.md`](agent-memory-population-survey-2026-05-16.md), all auth-gated)

**Headline:** the Label Studio / CVAT / Doccano / Argilla quartet is Tier-C at population scale — framework defaults enforce auth. Prodigy is a deliberate exception: its annotation UI is intentionally auth-free as a workflow choice.

---

## Prodigy — auth-free by-design

Prodigy (Explosion AI) is a paid annotation tool. Its server-side architecture is **deliberately single-user** with no built-in auth — operators are expected to run it on `localhost` or behind their own access control. 16 hosts confirmed via root-page title `<title>Prodigy</title>` and `/sessions` returning JSON.

Per the auth-on-default thesis: Prodigy is **Tier-A* (auth optional, off-by-default per framework design)**. It's the cleanest example of "the framework chose not to ship auth at all; the operator's job is to provide it externally." Same family as Ollama, vLLM, etc., but in the data-labeling tier.

The risk is not the platform; the risk is that operators expose Prodigy to the public internet without the expected `localhost`-only deployment. 16 hosts crossed that line. Each represents an open annotation workflow — labels assigned to whatever the operator was annotating, fully visible.

---

## Label Studio — the legacy-version probe gap

Label Studio at v1.x exposes version via `GET /api/version`:

```json
{"label-studio-os-package":{"version":"1.20.0",...},"label-studio-frontend":{...}}
```

But at v0.7.x (legacy), the path was `GET /version` returning a different shape:

```json
{"label-studio-backend":"0.7.4","label-studio-frontend":{...}}
```

My initial probe only checked `/api/version`. Re-probe with both paths surfaced:

- 3 real Label Studio v0.7.x hosts (`116.202.182.74:8140`, `116.202.182.74:8139`, etc. — legacy version, /version path)
- 0 real Label Studio v1.x with unauth data layer (`/api/projects` requires auth)
- 60 of 63 re-probed candidates were Shodan FPs (the Shodan title-match was on unrelated services or stale references)

Confirms [[insight-15-dork-hits-vs-platform-instances]] again: `http.title:"Label Studio"` returned ~1,663 Shodan candidates → ~3 real Label Studio instances confirmed → **FP rate ~99.8%**. The title string is uncommon enough to assume specificity, but the dork still over-counts dramatically.

Label Studio's data layer (`/api/projects?page_size=1`) is auth-gated at the population-scale population observed. Tier-C confirmed.

---

## CVAT / Doccano — Tier-C confirmed

CVAT (Computer Vision Annotation Tool, originally by Intel/Datumaro) and Doccano (text annotation, by Hironsan) both ship with auth-on-default. The probes:

- CVAT: `/api/server/about` returns version unauth (informational), but `/api/tasks` requires Django session auth → 401/403
- Doccano: `/v1/projects` returns DRF paginated 200 — but the response is empty until operator logs in to create projects, AND when projects exist, listing returns 401

The few real instances surfaced (~10 across CVAT + Doccano combined) all returned auth-gated at the data layer. Tier-C confirmed for both.

---

## Cross-survey colocation

Argilla appears in both this survey and [`agent-memory-population-survey-2026-05-16.md`](agent-memory-population-survey-2026-05-16.md) — the same 4-host set is observed from both angles. Argilla intentionally sits at the data-labeling / agent-feedback boundary, so cross-category coverage is appropriate. All 4 instances auth-gated under both probe angles.

No colocation with same-day ComfyUI (548) or vector-DB-stragglers (881) unauth populations.

---

## Methodology placement

Adds 4 platforms (Label Studio, CVAT, Doccano, Argilla) to Tier-C confirmed-at-population-scale and 1 platform (Prodigy) to Tier-A* (auth optional, off-by-design).

The data-labeling tier as a whole confirms the auth-on-default thesis. The thesis predicts: platforms designed with multi-tenant annotation workflows (Label Studio, CVAT, Doccano) ship auth-on-default — observed. Platforms designed as single-user annotation tools (Prodigy) don't ship auth — observed. The mapping from framework intent to population behavior is the load-bearing principle.

---

## Toolchain Provenance

```
0. shodan search × 9 dorks → 772 unique ip:port candidates
1. fast_enum_data_labeling.py (threads=60, 142s) → initial classify
   (Prodigy 16, others 0 unauth, 135 auth-gated, 28 shell-only, 440 dead, 56 unrelated)
2. Label Studio re-probe (legacy /version + new /api/version) → 0 unauth, 3 real (legacy), 60 FP
3. CVAT/Doccano spot checks → confirmed Tier-C
4. (queued) visorlog ingest → 16 Prodigy events into nuclide.db source='data-labeling-survey-2026-05-16'
```

---

## Honest negative space

- **Label Studio v1.x population not separately surveyed at high N.** The candidate pool surfaced mostly legacy or non-LS instances. A future port-first masscan on Label Studio's default port (8080) on tier-2 cloud would surface the modern LS population for a fair Tier-C confirmation.
- **CVAT 354 Shodan candidates not exhaustively probed.** The probe identified CVAT only when `/api/server/about` returned a JSON with `cvat`/`computer vision annotation` markers. Of the 354 candidates, only a small fraction were real CVAT — the rest are Shodan FPs (CVAT is an abbreviation that conflicts with `CVAT Insurance` and similar). A second-conjunct dork (`http.title:"CVAT" "computer vision annotation"`) would tighten the candidate set.
- **Prodigy's 16 unauth instances are operator-attribution-rich.** Each runs a research/annotation project; reading the `<title>` plus `/sessions` JSON discloses what's being labeled. Not pursued in this survey (out of scope — the platform is intentionally auth-free; the per-host disclosure would be a workflow recommendation to put it behind a VPN).
- **No data sampling.** Restraint: read project counts (when reachable) but never read annotation contents. Several Doccano / Label Studio hosts could probably be queried for project metadata, but the auth-gated outcome means no data is read.

---

## See also

- [[insight-13-shipping-defaults-are-load-bearing]] — confirms in this survey: Label Studio / CVAT / Doccano all auth-on-default → 0% unauth; Prodigy auth-off-by-design → all 16 reachable Prodigy hosts unauth
- [[insight-15-dork-hits-vs-platform-instances]] — `http.title:"Label Studio"` 1,663 candidates → 3 real = 99.8% FP rate
- [`agent-memory-population-survey-2026-05-16.md`](agent-memory-population-survey-2026-05-16.md) — Argilla overlap (same 4 instances observed from both angles)
- [`image-generation-population-survey-2026-05-16.md`](image-generation-population-survey-2026-05-16.md) — companion same-day Tier-A counter
- [`vectordb-stragglers-population-survey-2026-05-16.md`](vectordb-stragglers-population-survey-2026-05-16.md) — same day's high-volume Tier-A finding (Solr 7.6.0 cluster)
