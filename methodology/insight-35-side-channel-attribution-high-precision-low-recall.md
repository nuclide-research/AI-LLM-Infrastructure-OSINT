---
type: methodology
insight_number: 35
title: Side-channel attribution has high precision and low recall; it is for targeted investigation, not population discovery
---

# Insight #35. Side-channel attribution has high precision and low recall; it is for targeted investigation, not population discovery

_Source: Registry-population survey, 2026-05-19. Validation cohort of 9 known-unauth Docker registries gave 33% Jetson attribution rate. Population sample of 2,878 Shodan-broad registries gave 1 low-confidence attribution (0.035%). The methodology is the same; the use case shifts._

## The rule

[Insight #33](insight-33-side-channel-attribution-via-registry-catalog.md) establishes that operator-class attribution via adjacent-service content (Docker Registry `/v2/_catalog`) works when the operator's content carries class signals. **The yield is high when the population is already selected for the class, and very low when the population is not.**

This means side-channel attribution has two distinct deployment patterns, and the wrong pattern wastes both compute and disclosure capacity:

| Use pattern | Setup | Yield expectation |
|---|---|---|
| **Targeted investigation** | Suspect operator X runs class C. Probe their registry. | High precision and high recall on the specific target. |
| **Population discovery** | Harvest every Shodan-indexed registry. Run the class C classifier. | High precision, very low recall. Most registries are commodity dev/staging/mirror, not class C. |

Targeted-investigation use is what Insight #33 was designed for. Population-discovery use is what this survey tested. Population-discovery use is not wrong; it is one tool among several, and its yield is what it is.

## Empirical basis (Registry-population survey, 2026-05-19)

### Validation cohort (9 known unauth registries)

The 9 cross-survey hosts were SELECTED because past surveys had already flagged them as Jetson-adjacent (5 from yesterday's Jetson survey) or as operator-class-attributable (4 cross-survey controls). Validation pass yield:

| Class | High | None | Failed |
|---|---|---|---|
| Jetson | 3 | 4 | 0 |
| Healthcare | 0 | 7 | 0 |
| Finance | 0 | 7 | 0 |

Jetson attribution rate: 33% (3 of 9). Healthcare and Finance: 0%, because the validation cohort wasn't selected for those classes.

### Population sample (2,878 Shodan-broad registries)

The 2,878 hosts came from Shodan dorks: `Docker-Distribution-Api-Version registry/2.0` + `product:"Docker Registry"` (country-split per Insight #28). Population pass yield:

| Outcome | Count | % of 2,878 |
|---|---|---|
| Failed (timeout / decay / not-registry / empty / auth-required) | 2,413 | 84% |
| Reachable, catalog enumerable, no class signal | 464 | 16% |
| Jetson high | 0 | 0% |
| Jetson medium | 0 | 0% |
| Jetson low | 1 | 0.035% |
| Healthcare any | 0 | 0% |
| Finance any | 0 | 0% |

The 1 jetson:low (`122.10.116.132:51000`, Emby ARM64) is marginal: `amilys/embyserver_arm64v8` triggers the arch hint (`_arm`) but Emby is not Jetson; it just happens to be the ARM64 Emby variant. Even that hit is more of a chance signal than a real Jetson operator.

### Yield ratio

Curated cohort gives 33% Jetson rate. Shodan-broad population gives 0.035% Jetson rate. **The yield difference is ~1000x.** The methodology has not changed; what changed is whether the population is pre-selected for the class.

## Why the gap exists

1. **Shodan-indexed Docker registries are dominated by commodity infrastructure.** Most exposed registries hold dev / staging / CI mirror images: `library/postgres`, `library/nginx`, `rancher/mirrored-*`, `bitnamilegacy/redis`. These don't trigger operator-class signals because the operator is generic.
2. **Operator-class registries are rare in the broad population.** A Jetson edge-AI operator runs maybe 0.1% of all exposed registries. A healthcare PACS operator runs less. A finance algotrading operator runs less still.
3. **Pre-selection inflates the yield.** When a sample is drawn from past surveys (e.g., yesterday's Jetson edge survey), the sample is already class-biased. The 33% Jetson rate in the validation cohort is not the population rate; it is the conditional rate given pre-selection.

This is not a methodology failure. It is the difference between a stratified sample (yesterday's survey output) and a random sample (Shodan dork output).

## Procedural rules this insight generates

1. **Choose the deployment pattern before launching a side-channel run.**
   - For **targeted investigation** (one suspect operator, or a small list of candidates): probe their registry directly. Expect high yield.
   - For **population discovery** (broad sweep): expect ~0.1% or lower class-attribution rate. Budget the compute and the disclosure follow-on accordingly. Don't run unless the budget is justified by the expected absolute count.

2. **At population scale, the no-attribution registries are themselves a finding class.** The 464 reachable-but-not-class-attributable registries in this survey are a population worth its own analysis: shared mirror infrastructure, CI registries with leaked images, generic dev environments. A separate `classifyMirrorRepos` / `classifyCIRepos` may surface them; see #33 carry-forward.

3. **Pre-selected validation cohorts overstate the population yield.** When validating a new classifier against known-real hosts, the yield rate is not generalizable. Report two rates side by side: (a) yield on validation cohort, (b) projected yield on population. The 33%-vs-0.035% gap in this survey is the canonical worked example.

4. **Class-specific signal expansion matters more at population scale.** With low base rates, missing a class signal (e.g., not recognizing Russian healthcare terms `krayzdrav`/`zdrav`) costs proportionally more in absolute discovered operators. `88.99.214.110:5000` in this survey is a Russian regional-healthcare operator (`external/krayzdrav/fss-*` repos) that `classifyHealthcareRepos` missed because its signal set is western-DICOM-PACS-centric. International-coverage gaps in the signal set are first-order improvements at population scale.

5. **For population discovery, anchor on a class-specific dork rather than a generic-service dork.** The Docker Registry dork returned 12,297 hosts; the registry-content classifier yielded 1 attribution. A class-specific dork (e.g., `http.html:"dustynv"` or `http.html:"l4t"`) would return a smaller candidate set with a much higher class-conditional attribution rate. The side-channel methodology supplements direct-dork discovery; it does not replace it.

## Relationship to prior insights

- **Insight #33** (side-channel attribution via registry catalog). This insight is a usage-pattern refinement: #33 says the method works; #35 says the method's yield depends on whether the input is class-pre-selected.
- **Insight #15** (dork hits vs platform instances). Same epistemology: real-rate at population scale is class-conditional. #15 documents the gap between Shodan-indexed candidates and verified-real platforms; #35 documents the gap between verified-real registries and operator-class-attributable registries.
- **Insight #9** (cross-survey correlation as a Shodan-free discovery vector). The complement: when population discovery has low yield, cross-survey correlation against known operators can be a higher-yield discovery vector.
- **Insight #6** (conjunctive marker-anchored matchers). Tangential but reinforced: at low base rates, even one substring FP (the `tegra`/`mcintegration` collision in this survey's first pass) is a meaningful fraction of the total signal. Discipline applies harder at population scale.

## Carry-forward

- **Class signal internationalization** is a v1.x aimap roadmap item. Healthcare needs Russian (`zdrav`, `krayzdrav`), German (`klinik`, `praxis`), Spanish (`salud`, `clinica`), French (`sante`, `clinique`), Mandarin (`yiyuan` 医院), Japanese (`byouin` 病院) terms. Finance needs international-broker terms. Jetson is more uniformly English-named (NVIDIA's product naming carries through), but still: international ML lab naming may surface gaps.
- **Mirror / CI classifier** to attribute the 464 no-attribution registries by their CI-pipeline shape (`gitlab-runner`, `drone-runner`, `woodpecker-server`, `concourse-`, etc.) is a v1.x roadmap item.
- **Class-specific dorks beat generic-service dorks** for population discovery. Run a follow-up survey on `http.html:"dustynv"` to compare yield.

## See also

- [`insight-33-side-channel-attribution-via-registry-catalog.md`](insight-33-side-channel-attribution-via-registry-catalog.md). The base method.
- [`insight-15-dork-hits-vs-platform-instances.md`](insight-15-dork-hits-vs-platform-instances.md). The complementary observation at a different layer.
- [`insight-9-cross-survey-correlation-discovery-vector.md`](insight-9-cross-survey-correlation-discovery-vector.md). The higher-yield alternative when population-discovery yield is low.
- aimap v1.9.14 CHANGELOG (Insight #6 extension to the catalog classifier).
- `case-studies/commercial/registry-population-survey-2026-05-19.md` (the source survey, when promoted from draft).
