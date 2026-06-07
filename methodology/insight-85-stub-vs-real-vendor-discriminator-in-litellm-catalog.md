# Insight #85: Long-tail LiteLLM guardrail integrations are ~20% stubs. The discriminator is absence of a default api_base.

**Codified:** 2026-06-07. Cat-33 Phase 5 Lane D Slice C survey.
**Source:** `data/platform-intel/cat33-lane-d-slice-c-specialized-2026-06-07.md` (10 vendors probed, 2 confirmed stubs).
**Family:** Insight #17 (platform-class-operators-are-mono-platform), Insight #51 (port-number-names-a-candidate-not-a-finding), Insight #25 (falsification-confirmation-tier-c-platforms).
**Falsifiability tier:** low-medium. n=2 stubs out of 10 in the long-tail slice; needs a second long-tail slice to confirm the ratio.

## The pattern

The LiteLLM `guardrail_hooks/` directory contains 41 vendor packages. Reading the LiteLLM integration source per vendor reveals two distinct integration shapes:

1. **REAL vendor integration.** The integration ships with a default `api_base` (or equivalent endpoint configuration) that points at a vendor's actual production SaaS. The vendor has DNS, MX, customer-facing marketing, and a public security contact. Customer adoption flows: install LiteLLM + supply vendor API key + done.

2. **STUB vendor integration.** The integration is a generic adapter that wraps an OSS framework or expects the customer to supply their own endpoint. There is no default api_base. The vendor name in the LiteLLM directory points at an OSS project on GitHub, not a commercial entity with a SaaS endpoint.

The Slice C sample (10 vendors, the most likely-to-have-stubs slice by composition) returned 8 REAL and 2 STUB. Stubs: `semantic_guard` (LiteLLM built-in wrapping `aurelio-labs/semantic-router`) and `vigil_guard` (BYO endpoint, almost certainly `deadbits/vigil-llm` OSS).

The discriminator is mechanical. Read the LiteLLM source. If there is a default `api_base` or a vendor-branded URL anywhere in the module, the integration is REAL. If the only endpoint configuration is a customer-supplied environment variable or constructor parameter with no fallback, the integration is STUB.

## Why this matters for survey design

Treating every LiteLLM directory as a vendor produces an inflated vendor count. A Cat-33 Lane D survey that lists `vigil_guard` as a discoverable SaaS will return zero hits for the right reason: there is no SaaS to discover. The stub deserves a one-line note ("wraps OSS X, no commercial endpoint"), not a tome platform JSON.

For population surveys that want to estimate "how many AI-security guardrail vendors are there," the LiteLLM directory count is an upper bound, not a true count. Subtract the stubs. The 41-package directory likely contains 30-35 real commercial vendors and 5-10 stub adapters.

## How to apply

- When inventorying integrations from a catalog like LiteLLM `guardrail_hooks/`, read the source per entry before writing a tome platform JSON.
- Document stubs as one-line notes in the survey summary; do not create platform JSONs for them.
- When the discriminator is ambiguous (vendor has both an OSS project and a commercial offering with the same name, e.g., Guardrails AI), the integration is REAL if the LiteLLM default points at the commercial SaaS, STUB if it points at the OSS GitHub project.

## Cohort-level extension

If the stub ratio holds at ~20% across the other three slices of the LiteLLM catalog (the Phase 5 Slices A, B, D combined for 22 additional vendors), the catalog-wide stub estimate is around 8 of 41 = ~20%. Slices A and B both reported 0 stubs in their summaries, which would push the catalog-wide rate down toward 6-7%. The high-stub concentration in long-tail slices is itself a sub-pattern worth noting: long-tail commercial-vendor catalogs accumulate experimental and abandoned entries faster than active ones.

## DCWF KSAT fit

- 672: K7044 (V&V tooling: catalog discrimination at survey-design step), K7004 (T&E framework: survey rubric).
- 733: T5882 (responsible AI process: do not inflate vendor counts).
- Overlap: K22 (catalog DNS as discrimination signal).
