# DMARC Funding-Stage Proxy — Full-Registry Sweep N=410

Date: 2026-06-07. Cohort: full NuClide AI-infrastructure vendor registry (MASTER-port-vendor-registry.csv, 435 vendor names, 410 unique apex domains resolved after dedup and OSS filtering). Probe: `dig +short TXT _dmarc.<domain>`. Fully passive otherwise.

## Headline numbers

| Bucket | N | % of total | % of resolvable |
|---|---|---|---|
| no-dmarc | 219 | 53.4% | 55.6% |
| p=reject | 71 | 17.3% | 18.0% |
| p=none | 56 | 13.7% | 14.2% |
| p=quarantine | 48 | 11.7% | 12.2% |
| nxdomain | 16 | 3.9% | — |
| **Total** | **410** | **100%** | — |

Headline: **30.2% of AI vendors enforce** (p=reject or p=quarantine). 14.2% publish DMARC but disable enforcement (p=none). 55.6% publish no DMARC record at all.

## Contingency table — known-stage subset (n=31)

The known-stage subset is the n=31 cohort from the prior `2026-06-07-dmarc-funding-stage-proxy-n31-validation.md` analysis (AI-security vendors only), re-dug fresh for this sweep.

| Stage | N | reject | quarantine | none | no-dmarc | nxdomain | % enforced |
|---|---|---|---|---|---|---|---|
| Pre-seed / YC | 6 | 0 | 0 | 5 | 1 | 0 | **0%** |
| Seed | 8 | 1 | 3 | 2 | 2 | 0 | 50% |
| Series A | 4 | 3 | 1 | 0 | 0 | 0 | 100% |
| Series B | 4 | 0 | 2 | 1 | 1 | 0 | 50% |
| Series C | 5 | 5 | 0 | 0 | 0 | 0 | **100%** |
| Public | 4 | 3 | 1 | 0 | 0 | 0 | **100%** |

The N=31 pattern from the prior sweep holds in re-probing:

- Pre-seed / YC: 0% enforce (0/6).
- Series C and Public: 100% enforce (9/9).
- Seed through Series B: mixed (50%, small N).

Note the only delta from the prior pass: AegisAI (seed) flipped from `p=reject` to `p=quarantine` between the 06-06 and 06-07 probes. Either a re-policy by AegisAI's ops team or a stale DNS view in the prior run. The "founder DNA exception" remains real (AegisAI still enforces), the policy strictness just relaxed by one notch.

## Cannot extrapolate to full N=410 without funding data

The full 410-vendor registry has no funding-stage column. Crunchbase-grade cross-reference would require ~410 manual lookups (Crunchbase API not available in this lane). The CSV ships with the `funding_stage` column blank for the 379 vendors whose stage was not on the prior known-31 list. **This is the bottleneck for scaling the methodology, not the dig sweep.**

What we CAN say from the raw distribution:

- 55.6% no-DMARC is a higher absent-rate than the prior small n=31 sample (where absent was 13%). The AI infrastructure category at large is far less email-hygiene-mature than the AI security sub-category specifically. This is expected — most of the 410 are OSS-first or developer-tool companies, not enterprise-sales-first vendors. SOC2 pressure scales with enterprise-sales motion.
- p=none rate is 14.2% across all 410, vs. the n=31 sample where p=none was concentrated in Pre-seed/YC. If the proxy holds, this would imply ~58 of the 410 vendors are at Pre-seed/YC stage. That's plausible given how many of these are OSS startups.

## Sample for manual cross-reference (n=50)

A curated subset for follow-on funding-stage tagging. These are commercial vendors (not Apache projects or pure OSS) where Crunchbase/Pitchbook lookup would close the loop. Drawn proportionally from each policy bucket.

**p=reject (commercial vendors, n=15):**
elastic.co, mongodb.com, databricks.com, snowflake.com, neo4j.com, hashicorp.com, sentry.io, posthog.com, scale.com, replicate.com, pinecone.io, cohere.com, openai.com, anthropic.com, snowflake.com

**p=quarantine (n=10):**
weaviate.io, langchain.com, langfuse.com, helicone.ai, comet.com, clear.ml, dagster.io, prefect.io, wandb.com, supabase.com

**p=none (n=15):**
mindsdb.com, jina.ai, qdrant.tech, llamaindex.ai, crewai.com, portkey.ai, together.ai, zilliz.com, marqo.ai, voyageai.com, runpod.io, getzep.com, flowiseai.com, dspy.ai, agno.com

**no-dmarc (n=10):**
litellm.ai, vllm.ai, openwebui.com, ollama.com, ragas.io, ragflow.io, unsloth.ai, anythingllm.com, xinference.io, vocode.dev

Sampling these 50 by funding stage (~5 minutes per vendor on Crunchbase) yields an N=81 test set (50 + the prior 31). At N=81 the Series B and Seed cells move out of "small N" territory.

## Methodology

1. Source registry: `data/port-vendor-registry/MASTER-port-vendor-registry.csv` (435 unique vendor names).
2. Vendor-name to apex domain: 180 entries in a manual map (commercial vendors, OSS-foundation projects, ambiguous-name resolution). 10 OSS-only vendors with no commercial homepage skipped (e.g., `whisper.cpp`, `Faiss`, `Pgvector`, `FastChat`). Remainder fall through to a `slug.com` heuristic (lower-case, strip parens, glue first 1-2 short words).
3. dedupe by domain (some vendors share an apex, e.g. W&B Weave / Weights & Biases / WandB all -> wandb.com): 410 unique domains.
4. `dig +short TXT _dmarc.<domain>` parallel x20. nxdomain detection: if DMARC record absent, retry A record on apex and `www.` to distinguish nxdomain (16) from "exists but no DMARC" (219).
5. Cross-reference funding stage against the prior n=31 sweep (no other source available in this lane).

## Discipline notes

- **dig is the only active probe.** No HTTP, no banner grab, no scan. This is fully passive otherwise.
- **No fabricated funding stages.** The 31 known stages come from prior recorded work; the remaining 379 are blank, not guessed.
- **Slug heuristic is lossy.** A vendor like "Amulet Scan DuckDB API" gets `amuletscan.com` which won't resolve. That's reported as `nxdomain`, not silently dropped — null result is a logged result.

## Outputs

- `data/dmarc-funding-stage-sweep-2026-06-07.csv` — full 410-row dataset, columns: vendor, domain, dmarc_policy, dmarc_aspf, dmarc_rua, funding_stage, raw.
- This case study — methodology and headline numbers.

## Next steps

1. **Manual stage-tag the 50-vendor commercial subset** (Crunchbase / Pitchbook) -> N=81 contingency.
2. **Promote to numbered Insight** once N >= 100 and the Pre-seed -> p=none (>=80%) and Series-C+ -> p=reject (>=90%) bands both confirm.
3. **Cross-category validation lane**: run the same sweep against a non-AI SaaS vendor list (e.g. devtools, fintech) at matched N. If the same extreme-bands pattern holds, this becomes a sector-agnostic SaaS-maturity heuristic, not an AI-specific one.
4. **Track no-dmarc rate over time.** A 55.6% absent rate in an LLM-infrastructure category is a soft tell about email-attack-surface posture across the whole sector. Re-run quarterly.

## Headline for the registry memo

The DMARC funding-stage proxy hypothesis cannot yet be confirmed at the targeted N >= 100 because funding-stage data does not exist in machine-readable form for 92% of the NuClide vendor registry. The dig sweep half is complete and reproducible (410 rows, ~30 seconds wall time). The funding-stage cross-reference is the bottleneck; bridging it is a 50-vendor Crunchbase task, not an engineering task.
