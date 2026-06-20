# Insight #95 — OSS-Platform-Name Strings Are Docker-Registry Catalog Dorks (Candidate)

_NuClide Research · 2026-06-09 · Origin: Cat-Syllabus-Leads survey, aibrix / lmdeploy / rtp-llm pivot._

---

## Statement

Searching Shodan for an OSS LLM platform name as a raw string (`"LMDeploy"`, `"aibrix"`, `"vllm"`, `"sglang"`) does NOT predominantly surface live instances of that platform. It surfaces **unauthenticated Docker registries whose `/v2/_catalog` response contains image repositories named after that platform.** Shodan banner-grabs the catalog response at scan time and indexes every repository string in it, so a platform name string acts as a proxy dork for "an unauthenticated registry that pulls images for this platform."

The platform-recon problem and the registry-recon problem are the same problem read at two different layers. The image-name string layer is cheaper and more LLM-specific than the `Docker-Distribution-Api-Version` header dork because it filters the registry population by whether the operator pulls LLM-stack images, not whether they run a registry at all.

## Derivation

Cat-Syllabus-Leads survey, 2026-06-09 PM. Three new platforms had just been codified into the tome with `auth_default: none` per their upstream source: aibrix (ByteDance vLLM gateway), lmdeploy (Shanghai AI Lab, port 23333), rtp-llm (Alibaba havenask). Stage 0 ran the platform-specific dorks (`http.html:"<platform>"`, `http.html:"aibrix-system"`, `port:23333 http.html:"LMDeploy"`) and they all collapsed to 0. The reason was Insight #94's restated lesson — the Shodan web UI's `http.html:` filter is HTML-body-only and these inference engines return JSON, not HTML.

As a sanity probe we ran the raw unanchored strings:

| Dork | Hits | What we expected | What we got |
|---|---|---|---|
| `"LMDeploy"` | 3 | LMDeploy instances on port 23333 | 3 unauth Docker registries with `lmdeploy/*` images |
| `"aibrix"` | 4 | AIBrix gateways on port 80 | 4 unauth Docker registries with `aibrix/*` images |

All four hits verified live as unauthenticated registries via single-request `/v2/_catalog` reads (200, no `Www-Authenticate`). Catalog totals across the 4 unique hosts: 2,644 repos, 165 LLM-stack:

| Host | Repos | LLM stack | LLM density |
|---|---|---|---|
| 115.191.10.126:443 (CN, customer "myba") | 35 | 23 | 66% |
| 124.163.255.214:5000 (CN Unicom Shanxi) | 132 | 32 | 24% |
| 65.108.11.238:8804 (FI Hetzner, HA twin) | 1,058 | 65 | 6% |
| 65.108.11.238:8808 (FI Hetzner, twin of :8804) | 1,058 | 65 | 6% |
| 46.62.204.42:80 (FI Hetzner) | 1,419 | 45 | 3% |

The platforms themselves (lmdeploy, aibrix, rtp-llm) were NOT directly probed live in this Stage 0 — their image names were merely mentioned inside someone else's open registry. The platform candidates remain CANDIDATE in the tome; the lateral discovery vector now is captured as `registry_mentions` in each platform's JSON.

## Cross-confirmation with the header-layer dork

This survey's 4-host result extends the AM session's Cat-NIM finding (today-2026-06-09.md 23:18-23:49: 52 unauthenticated registries, 2,141 repos, 67 LLM-stack). The Cat-NIM discovery surfaced registries via the `Docker-Distribution-Api-Version` HTTP header dork. The PM finding surfaces a subset of the same population via image-name string dorks. Crucially, host [4] (124.163.255.214) appears in both — it was found in the AM via the header dork and re-found in the PM via the `"aibrix"` string dork. Same surface, two layers, two queries.

The header dork answers "is this a registry?" The image-name string dork answers "is this a registry that pulls LLM-stack images?" One is broader and more general; the other is narrower and selects the cohort an LLM/AI survey cares about. Use both; they overlap, they do not duplicate.

## Why this is a class of mistake, not a one-time miss

The pattern manifests on any OSS platform that ships an official Docker image with the platform name in the repository path. The Shodan banner-cache makes every repository name in every unauth catalog response a queryable string. Examples worth re-testing at Stage 0:

- `"vllm"` → registries pulling vllm/vllm-openai
- `"sglang"` → registries pulling lmsysorg/sglang
- `"mlflow"` → registries pulling ghcr.io/mlflow/mlflow
- `"langfuse"` → registries pulling langfuse/langfuse
- `"weaviate"` → registries pulling semitechnologies/weaviate
- `"qdrant"` → registries pulling qdrant/qdrant
- `"chromadb"` → registries pulling chromadb/chroma

In every case the platform-name dork returns BOTH live instances of the platform AND open registries that pull its image. The two populations are distinct but discoverable through the same query string.

## Action — add the registry-pivot dork to every tome platform

Stage -1 squads codifying a new platform JSON should add a `registry_mentions` field (sibling to `sources`) to capture this lateral vector. The field carries the four pieces of evidence:

1. The raw string dork that surfaced the lateral mention (`"<platform>"`)
2. The image namespace pattern observed (`<platform>/*`, `<vendor>/<platform>`)
3. The list of IPs where the image name appeared in unauth catalogs
4. The date of the survey that confirmed the pattern

Codification-discipline rule: a platform's `status` remains CANDIDATE while only its image name has been seen in registries — the platform itself is not yet verified live. Verifying the platform live requires a direct probe against a host running it, not a registry catalog mention. The two findings are distinct and should not be conflated.

## Restraint

Catalog enumeration only. Image layers were NOT pulled. Tags were NOT inspected. Manifests were NOT fetched. The repository names ARE the finding — they leak stack composition (vLLM vs sglang vs lmdeploy), tenant attribution (`myba/`, `000002/`), dev/prod separation (`myba/genai-backend-{dev,prod}`), customer-product names (`myba/myba-customer-service-dev`, `myba/mybarag`), and model capability inventory (Qwen, Hunyuan 3.0, FunASR, Whisper). The source-of-truth image content is out of scope; the metadata layer is sufficient to demonstrate severity.

## Falsifiability

The insight is falsified if:

1. A platform-name string dork returns >50% live platform instances and <50% registry mentions at population scale. The PM survey saw 0% live platform / 100% registry mentions on a 7-hit sample — the dork mode appears to be entirely registry-selective for the platforms tested, but a 7-hit sample is small.
2. Shodan changes its banner-grab policy to truncate or drop `/v2/_catalog` response bodies, removing the indexed strings.
3. The image-name string dork returns the same population (within ±10%) as the `Docker-Distribution-Api-Version` header dork. Currently they overlap but do not coincide — the header dork is broader.

A future survey should run both dork families against the same window and report the overlap matrix. If overlap >90%, the image-name dork is redundant; if overlap is the 7%/93% pattern seen here, the two dorks address different research questions and both belong in the playbook.

## When it applies

- The target is an OSS platform with an official Docker image whose namespace contains the platform name.
- Direct `http.html:` dorks for the platform collapsed to 0 or low single-digit population.
- The survey is allowed to widen from "find live instances of X" to "find any operator that runs X."
- Catalog metadata is in scope; layer/tag/manifest reads are not.

The insight is NOT useful when the platform's Docker image namespace is generic (`python:3.11`, `nginx:latest`) — the dork degrades to "find a registry that pulls python," which is uselessly broad.

## Tooling

- shodan-fetch in-page `fetch()` for the raw string dorks — 0 query credits, returns the per-host hit set and lets each candidate get a single-request `/v2/_catalog` verify in the same Playwright session.
- aimap fingerprint for Docker registries already exists; the addition is that registries which carry LLM-stack catalog entries deserve LLM-cohort tagging in `agent-logging-system` so the FP-candidate scanner separates "registry FP" from "LLM-stack registry FP."
- tome `registry_mentions` field on every platform JSON — feeds the cross-platform query "which platforms have ever been seen in unauth catalogs, and at which IPs?"

## Related

- Insight #15 (50% rule) — applies to the image-name string dork. A `"lmdeploy"` string match on a Shodan banner without a `/v2/_catalog` verify is still an unverified candidate.
- Insight #16 (a 200 is identity not auth state) — applies per probe. The `/v2/_catalog` 200 verifies BOTH identity (this is a Docker registry) AND auth state (the catalog is readable without `Www-Authenticate`).
- Insight #76 (auth-permissive cohort default) — the open registries here are the same population class. Operators who run open registries also tend to run unauth LLM stacks.
- Insight #79 (LLM-jacking productized ecosystem) — image-name catalog leaks are upstream of LLM-jacking; they tell an attacker which inference stack to expect before any inference call.
- Insight #94 (hybrid Tier-A*/C platforms escape tier vocabulary) — the methodology lesson restated in Stage 0 of this survey (`http.html:` is HTML-body-only) is why the surprise pivot was needed at all.

## Case study reference

`shodan/cat-syllabus-leads-2026-06-09/findings-breakdown.txt` — Cat-Syllabus-Leads survey, full PM session breakdown including the 4 verified registries and the 165 LLM-stack repos.

`case-studies/commercial/cat-nim-survey-2026-06-09.md` — Cat-NIM AM survey, the 52-registry parent population this finding extends.
