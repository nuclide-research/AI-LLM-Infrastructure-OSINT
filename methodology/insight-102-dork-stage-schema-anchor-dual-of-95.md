---
type: methodology
insight_number: 102
title: "Dork-stage schema anchor required for OSS-name-collision platforms (dual of #95): platform-name HTML dorks mass-FP onto Docker registries cataloging the image"
status: candidate
codified: 2026-06-10
source_survey: Cat-LMDeploy 2026-06-10 (5-IP bootstrap, 100% refuted as LMDeploy)
falsifiability_tier: high
falsified_by: an OSS-name-collision platform whose platform-name HTML dork returns predominantly platform instances rather than Docker registries
related_insights: [6, 15, 95, 97]
---

# Insight #102 — Dork-stage schema anchor required for OSS-name-collision platforms

## The pattern

Insight #95 (codified 2026-06-09) established the discovery direction: an OSS platform's name string surfaces in Docker registry `/v2/_catalog` JSON, and Shodan banner-caches that JSON, so a string-search dork like `http.html:"lmdeploy"` finds Docker registries cataloging the image.

Insight #102 is the methodological dual. When an OSS platform name is also a likely Docker image string, a Stage 0 dork of the form `port:N http.html:"PlatformName"` returns predominantly Docker registry hosts whose `/v2/_catalog` enumerates the image, **NOT platform instances**. Without a schema-anchored marker at Stage 0, the dork mass-FPs onto registries at population scale.

The lesson: Insight #6 (conjunctive marker-anchored matchers) applies at Stage 0, not just Stage 3v. The verify stage cannot recover an unbiased population if the dork itself selects for the wrong substrate.

## Empirical founding case — Cat-LMDeploy 2026-06-10

The dork `port:23333 http.html:"LMDeploy"` (basic tier from tome) was extended to a 5-IP bootstrap union with prior Cat-03 model-serving recon. The 5 IPs:

| IP | Stage 0c banner | Stage 3v marker pair |
|----|-----------------|----------------------|
| 115.191.10.126 | :443 self-signed `registry.mingya.com` Docker registry | refuted |
| 120.237.103.186 | :23333 conn refused | refuted (dead host) |
| 124.163.255.214 | :5000 Docker registry, :443 `*.1stcs.cn` | refuted |
| 65.108.11.238 | :8804 / :8808 Docker registry HA twins | refuted |
| 46.62.204.42 | :80 Docker registry | refuted |

100% of the cohort hit Docker Distribution v2 unauthenticated registries cataloging images that contain the substring `lmdeploy` (per Cat-Syllabus-Leads 2026-06-09: `000002/ai-platform/inference/lmdeploy`, `aibrix 0.1.x/0.2.x build train`, etc.). Zero of the 5 IPs ran LMDeploy on `:23333`.

This is not stale Shodan cache. The substring is REAL in the registry HTTP bodies right now. Shodan is correctly indexing what the registries serve. The dork is the methodology error: it does not distinguish "platform instance" from "registry cataloging the platform's image".

## The schema-anchored fix at Stage 0

Two correction strategies, both work — choose by population size:

### Strategy A: positive schema anchor (preferred for small platforms)

Replace the platform-name dork with the platform's openapi-schema-unique fingerprint at the dork level:

```
# LMDeploy specifically:
port:23333 http.html:"/distserve/engine_info"

# vLLM specifically:
port:8000 http.html:"/v1/completions" http.html:"vllm"

# SGLang specifically:
port:30000 http.html:"/v1/models" http.html:"sglang"
```

The Stage 0 dork now matches the platform's openapi-generated `/openapi.json` body (FastAPI / similar autogen), which a Docker registry does NOT serve. This was already the strict-tier dork for LMDeploy in tome; the lesson is to demote the basic-tier dork OR mark it explicitly as "registry-FP-prone".

### Strategy B: negative anchor (preferred for high-population platforms where strict dork sub-samples too narrowly)

Keep the platform-name dork but exclude the registry signature:

```
port:23333 http.html:"LMDeploy" -http.html:"v2/_catalog" -http.html:"registry-version"
```

The negative anchor strips the registry FPs at the dork stage. Cost: registry hosts that censor the catalog response will not be excluded — but they would not have been verified as LMDeploy anyway.

## Generalization

The rule applies to any OSS platform whose name is a likely Docker image string:

| Platform | Name as image string? | Risk of dork FP |
|----------|----------------------|-----------------|
| LMDeploy | yes (`lmdeploy/lmdeploy`, `openmmlab/lmdeploy`) | high (this survey) |
| vLLM | yes (`vllm/vllm-openai`) | high |
| SGLang | yes (`lmsysorg/sglang`) | high |
| TGI | yes (`huggingface/text-generation-inference`) | medium (name less unique) |
| Triton | yes but ambiguous with other "Triton" projects | medium |
| AIBrix | yes (`aibrix/controller-manager`) | confirmed (Cat-Syllabus-Leads) |
| Ollama | yes (`ollama/ollama`) | medium — population large enough that registry FPs are statistical noise |
| Langfuse | yes (`langfuse/langfuse`) | low (port 3000 is universally used; platform-unique HTML on `/api/public/projects`) |

The methodology layer: every tome platform JSON should carry a `dork_fp_risk` field (low / medium / high) and a `schema_anchor` dork tier that defaults to Strategy A.

## Discipline this encodes

The verify stage is load-bearing (methodology §1). But verify cannot recover an unbiased population if the dork selects the wrong substrate. Insight #102 pushes the schema-anchor discipline upstream from Stage 3v to Stage 0. The conjunctive marker-anchored matcher rule (Insight #6) now applies at four stages: Stage 0 dork construction, Stage 0c scanner banner classification, aimap fingerprint matcher (Lane B), Stage 3v verifier (Lane C).

## Promotion criteria

Confirmed at 1 platform (LMDeploy). Promotion to numbered Insight requires 2 more OSS-name-collision platforms whose basic-tier dork mass-FPs onto registries at >50% rate. Candidates: vLLM `http.html:"vllm"`, SGLang `http.html:"sglang"`, AIBrix `http.html:"aibrix"` (last is already confirmed via Cat-Syllabus-Leads).

## Related insights

- Insight #6 — Conjunctive marker-anchored matchers (this is the Stage 0 extension)
- Insight #15 — Dork hits vs platform instances (this is the specific class)
- Insight #95 — OSS platform name as registry-catalog dork (this is the dual)
- Insight #97 — Cert-issuer heterogeneity as honeypot discriminator (different deception class, same methodology family of "the surface signal is not the platform identity")
