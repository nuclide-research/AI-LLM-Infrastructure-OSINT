---
type: methodology
insight_number: 102
title: "Dork-stage schema anchor required for OSS-name-collision platforms (dual of #95): platform-name HTML dorks mass-FP onto the wrong substrate (Docker registries, marketing pages, or distinct same-named projects)"
status: numbered
codified: 2026-06-10
promoted: 2026-06-17
source_survey: Cat-LMDeploy 2026-06-10 (5-IP bootstrap, 100% refuted as LMDeploy)
promotion_surveys:
  - Cat-LMDeploy 2026-06-10 (LMDeploy -> Docker-registry substrate)
  - Cat-Syllabus-Leads 2026-06-09 (AIBrix -> Docker-registry substrate)
  - Cat-RAG-Framework-Servers 2026-06-17 (GraphRAG title -> distinct same-named projects, 46/46 non-Microsoft)
falsifiability_tier: high
falsified_by: an OSS-name-collision platform whose platform-name HTML dork returns predominantly the intended platform instances rather than a collision substrate
related_insights: [6, 15, 95, 97]
---

# Insight #102 - Dork-stage schema anchor required for OSS-name-collision platforms

## The pattern

Insight #95 (codified 2026-06-09) established the discovery direction: an OSS platform's name string surfaces in Docker registry `/v2/_catalog` JSON, and Shodan banner-caches that JSON, so a string-search dork like `http.html:"lmdeploy"` finds Docker registries cataloging the image.

Insight #102 is the methodological dual. When an OSS platform name doubles as a string that lives in some OTHER indexable substrate, a Stage 0 dork of the form `http.html:"PlatformName"` or `http.title:"PlatformName"` returns predominantly hosts of that other substrate, **NOT platform instances**. Without a schema-anchored marker at Stage 0, the dork mass-FPs at population scale.

There are at least two distinct collision substrates, both confirmed:

1. **Docker-registry collision** (the founding class). The platform name is a Docker image string, so the dork lands on Docker Distribution v2 registries whose `/v2/_catalog` enumerates the image. Founding evidence: LMDeploy (Cat-LMDeploy 2026-06-10) and AIBrix (Cat-Syllabus-Leads 2026-06-09).

2. **Distinct-same-named-project collision** (added by Cat-RAG-Framework-Servers 2026-06-17). The platform name is a generic technique label that multiple unrelated projects adopt as a brand, so the dork lands on a population of same-named-but-different platforms. Founding evidence: `title:"GraphRAG"` = 46 hosts, 46/46 non-Microsoft (Tencent Youtu-GraphRAG, ProtonX, ManGAI, Purdue GraphRAG Chat, an OVH "GraphRAG Agentique", 39 custom builds). Zero are the Microsoft GraphRAG the dork was meant to find.

The lesson, shared by both substrates: Insight #6 (conjunctive marker-anchored matchers) applies at Stage 0, not just Stage 3v. The verify stage cannot recover an unbiased population if the dork itself selects for the wrong substrate. The fix is the same in both cases (anchor the dork to a schema marker only the intended platform emits); only the FP substrate differs.

## Empirical founding case - Cat-LMDeploy 2026-06-10

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

## Third platform-class confirmation - Cat-RAG-Framework-Servers 2026-06-17

The RAG-framework survey set out to measure Microsoft GraphRAG exposure. The dork `title:"GraphRAG"` returned 46 hosts. None of the 46 was Microsoft GraphRAG:

| Same-named project | Operator | Port | Count |
|--------------------|----------|------|-------|
| Youtu-GraphRAG | Tencent | 8000 | 5 |
| ProtonX GraphRAG | ProtonX | varies | 1+ |
| ManGAI | independent | varies | 1+ |
| GraphRAG Chat | Purdue (university) | varies | 1 |
| GraphRAG Agentique | OVH-hosted | varies | 1 |
| custom builds | mixed | mixed | ~39 |

"GraphRAG" is a generic graph-RAG technique label, not a Microsoft-unique brand. The companion exclusion dork `Ocp-Apim-Subscription-Key` (the accelerator's APIM placeholder string) returned 14 generic Azure APIM gateways (ADAC, Deloitte) and zero GraphRAG. Both Stage 0 dorks selected the wrong substrate: the platform-name dork landed on distinct same-named projects, the APIM-string dork landed on generic APIM gateways.

This is the second collision substrate. Where LMDeploy and AIBrix collided onto Docker registries (a non-platform substrate cataloging the image), GraphRAG collides onto a population of unrelated platforms that adopted the same technique name. The methodology error is identical: the dork token is not platform-unique, so the verify stage inherits a population that is 100% off-target. The Microsoft-GraphRAG exposure question is unanswerable from the name dork alone; the schema-anchored fix is `http.html:"/manpage/openapi.json"` (the accelerator's renamed OpenAPI path, near-zero collision) plus a LightRAG exclusion (`-http.title:"LightRAG Server API"`, since LightRAG also brands itself a GraphRAG server). The survey logged GraphRAG-accelerator direct exposure as 0 (Shodan-dark `/manpage`, APIM-gated default), which is the correct thesis-confirming negative only because the schema anchor replaced the name dork.

Three independent platform classes now exhibit the failure: LMDeploy (Docker substrate), AIBrix (Docker substrate), GraphRAG (same-named-project substrate). Two distinct substrates, one methodology error. Promotion threshold met.

## The schema-anchored fix at Stage 0

Two correction strategies, both work - choose by population size:

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

The negative anchor strips the registry FPs at the dork stage. Cost: registry hosts that censor the catalog response will not be excluded - but they would not have been verified as LMDeploy anyway.

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
| Ollama | yes (`ollama/ollama`) | medium - population large enough that registry FPs are statistical noise |
| Langfuse | yes (`langfuse/langfuse`) | low (port 3000 is universally used; platform-unique HTML on `/api/public/projects`) |

The methodology layer: every tome platform JSON should carry a `dork_fp_risk` field (low / medium / high) and a `schema_anchor` dork tier that defaults to Strategy A.

## Discipline this encodes

The verify stage is load-bearing (methodology §1). But verify cannot recover an unbiased population if the dork selects the wrong substrate. Insight #102 pushes the schema-anchor discipline upstream from Stage 3v to Stage 0. The conjunctive marker-anchored matcher rule (Insight #6) now applies at four stages: Stage 0 dork construction, Stage 0c scanner banner classification, aimap fingerprint matcher (Lane B), Stage 3v verifier (Lane C).

## Promotion status - NUMBERED (2026-06-17)

The candidate is promoted. The original criterion (2 more OSS-name-collision platforms whose basic-tier dork mass-FPs at >50% rate) is met:

1. **LMDeploy** (Cat-LMDeploy 2026-06-10) - 5/5 = 100% FP onto Docker registries.
2. **AIBrix** (Cat-Syllabus-Leads 2026-06-09) - confirmed FP onto Docker registries cataloging the image.
3. **GraphRAG** (Cat-RAG-Framework-Servers 2026-06-17) - 46/46 = 100% FP onto distinct same-named projects (a second, distinct collision substrate).

The promotion strengthens the insight beyond the original Docker-registry framing: the schema-anchor discipline at Stage 0 is required whenever a platform name collides with ANY indexable substrate, not only when it collides with a Docker image string. The next survey of an OSS-name-collision platform should still log its FP rate and substrate to keep widening the evidence base.

## Related insights

- Insight #6 - Conjunctive marker-anchored matchers (this is the Stage 0 extension)
- Insight #15 - Dork hits vs platform instances (this is the specific class)
- Insight #95 - OSS platform name as registry-catalog dork (this is the dual)
- Insight #97 - Cert-issuer heterogeneity as honeypot discriminator (different deception class, same methodology family of "the surface signal is not the platform identity")
