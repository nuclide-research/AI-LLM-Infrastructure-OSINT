---
type: methodology
insight: 49
title: Ollama-Cloud-signin × public-exposure = LLMjacking surface; the operator's Ollama Cloud subscription quota is billable by any public caller
date: 2026-05-19
tags:
  - methodology
  - attribution
  - llmjacking
  - ollama
  - cloud-models
  - vendor-default-no-warning
  - research-compute
related_research:
  - case-studies/universities/US/CA-sdsc.md
  - case-studies/universities/US/CA-ucsb.md
  - case-studies/universities/US/ME-university-of-maine.md
  - case-studies/universities/US/NY-rit.md
  - methodology/insight-23-bis-llmjacking-proxy-colocation.md
  - methodology/insight-39-pooled-account-attribution-laundering.md
source: case-studies/universities/US/CA-sdsc.md
---

# Insight #49. Ollama-Cloud-signin × public-exposure = LLMjacking surface

_Source: .edu LLM-infra Stage-1+2 deeper-enum sweep, 2026-05-19. Surfaced when SDSC's `/api/tags` returned 19 `:cloud`-suffix entries (deepseek-v3.2/v4-pro/v4-flash, kimi-k2.5/.6/-thinking, glm-4.6/4.7/5/5.1, minimax-m2 series, nemotron-3-super, qwen3.5, qwen3-coder-next, gemini-3-flash-preview). Cross-correlation against UMaine ECE-Ubuntu-02 (existing case study), RIT disco-dgx-spark, and UCSB spark-4de1.mcdb confirmed the EXACT same portfolio on four independent research-compute deployments. The initial "shared deployment template" hypothesis was wrong; WebFetch of Ollama's own docs at docs.ollama.com/cloud + ollama.com/blog/cloud-models confirmed the actual mechanism: the `:cloud` entries appear automatically once an operator runs `ollama signin` to activate an Ollama Cloud subscription. The 4 hosts share the portfolio because they all have Ollama Cloud signed in — not because they share a deployment template._

## The rule

An Ollama instance meeting BOTH of these conditions exposes the signed-in operator's Ollama Cloud subscription quota to public invocation:

1. `ollama signin` has been run on the host (per [Ollama Cloud docs](https://docs.ollama.com/cloud): "Cloud models use inference compute on ollama.com and require being signed in to ollama.com")
2. The Ollama HTTP API on port 11434 (or whatever `OLLAMA_HOST` binds to) is reachable from the public internet without authentication

When both conditions hold, the operator's Ollama Cloud account quota becomes a public-billable surface. Any internet caller can invoke `POST /api/chat` against the host with a `:cloud`-suffix model name and route the request through the operator's subscription. The cost-bearer is the operator. The plan limits (Pro $20/mo: 5-hour-reset session limits + 7-day weekly limits; Max $100/mo: higher limits) bound the worst-case impact, but the surface is active during every minute the host is exposed.

## Diagnostic marker (single-shot, restraint-compatible)

```
GET http://<host>:11434/api/tags
→ inspect for entries with ":cloud" suffix in the .models[].name field
→ presence of any :cloud entry = signed-in state confirmed
```

The full reference catalog of 18 cloud models observed across all confirmed instances (2026-05-19):

```
deepseek-v3.2:cloud         kimi-k2.5:cloud         glm-4.6:cloud
deepseek-v4-pro:cloud       kimi-k2.6:cloud         glm-4.7:cloud
deepseek-v4-flash:cloud     kimi-k2-thinking:cloud  glm-5:cloud
                                                    glm-5.1:cloud

minimax-m2:cloud            nemotron-3-super:cloud  qwen3.5:cloud
minimax-m2.1:cloud                                  qwen3-coder-next:cloud
minimax-m2.5:cloud                                  gemini-3-flash-preview:cloud
minimax-m2.7:cloud
```

Per-host variation: some hosts have one additional `:cloud` entry (e.g., `qwen3-next:80b-cloud` on SDSC + UCSB). The catalog evolves as Ollama adds new cloud models; the diagnostic is the **presence of ANY `:cloud` suffix**, not the exact 18-model count.

## Distinct from prior LLMjacking insights

This is NOT the same as **Insight #23-bis (LLMjacking proxy colocation)**, which observed commercial proxy SaaS + unauthenticated open LLM on the same host. That pattern co-locates the resale and the model; this pattern routes invocation through Ollama's vendor-managed inference, charged against the operator's account at Ollama.

This is also NOT the same as **Insight #39 (pooled-account attribution-laundering)**, which observed Tier-2 relays holding N paid vendor accounts and fanning out to Tier-3 storefronts and Tier-4 end-customers. The Ollama-Cloud-signin pattern is two-tier (operator's Cloud sub → public caller); there is no commercial-reseller layer.

The structural class is closer to a **leaked API key** finding (cost-bearer is the legitimate account holder; arbitrary callers consume the quota), but with two key differences:

| Property | Leaked API key | Ollama-Cloud-signin × public exposure |
|---|---|---|
| What's exposed | The key string | The Ollama instance hosting the signed-in session |
| Discovery | Search for `sk-*`/`AIzaSy*`/etc. in scrape data | Port 11434 + `/api/tags` with `:cloud` entries |
| Remediation | Rotate the key | `ollama signout` OR firewall `:11434` |
| Upstream visibility | Vendor sees API key in use | Vendor sees signed-in user invoking models |
| Time to detect | Immediate (key in logs) | None — invocation looks identical to legitimate operator use |

The third row matters: rotating a leaked key is a definite repair; rotating an Ollama-Cloud-signin requires the operator to run `ollama signout` on the host (and re-sign-in elsewhere if they want continued local Cloud use). The fourth row matters even more: Ollama's billing telemetry cannot distinguish "the operator invoked deepseek-v4-pro:cloud locally" from "an internet caller invoked it via the operator's exposed host" — both look like the same signed-in account making API calls.

## Why this surfaces in research-compute environments

All 4 confirmed instances are research-compute deployments:

| Host | Institution context |
|---|---|
| `compute.cloud.sdsc.edu` | San Diego Supercomputer Center (NSF HPC) |
| `ECE-Ubuntu-02.um.maine.edu` | UMaine Electrical & Computer Engineering dept |
| `disco-dgx-spark.wireless.rit.edu` | RIT DISCO (Distributed Computing) group |
| `spark-4de1.mcdb.ucsb.edu` | UCSB Molecular Cellular Developmental Biology dept |

The 24 OTHER .edu Ollama hosts probed in the validation sweep (wireless/eduroam student-laptop hosts on UCSB, DePaul, VT, Berkeley reshall, etc.) were unreachable due to DHCP rotation. The persistent / production-grade deployments — the ones with stable IPs and dedicated GPU compute — are the ones that are (a) reachable at probe time and (b) likely to have an operator who ran `ollama signin` for convenience.

Hypothesis: research-IT staff at these institutions run `ollama signin` to give themselves access to Ollama Cloud's frontier models (Gemini 3, DeepSeek v4, Kimi K2.6, etc.) for evaluation / research use. They bind `ollama serve` to `0.0.0.0` to allow connections from other hosts on their research network. They don't firewall port 11434 from the public internet because the institutional network's public-by-default posture pre-existed the Ollama install. Result: the personal Ollama Cloud subscription becomes a public LLMjacking surface.

## Vendor-side observation

Ollama's documentation describes the signin requirement but does NOT document the security implications of running a signed-in instance with `OLLAMA_HOST=0.0.0.0`. The `ollama serve` command does not warn when both conditions are present. A single ecosystem-level fix — a startup-time warning when `OLLAMA_HOST` is non-localhost AND `ollama signin` has been run — would prevent recurrence across all current and future operators.

## Discovery and validation

Surfaced via the .edu Stage-1+2 verification waves of the 2026-05-19 NuClide .edu LLM-infrastructure sweep. The 18-model catalog match was first observed across SDSC + UMaine ECE + RIT DISCO; UCSB MCDB confirmed as the 4th instance during the same-day validation sweep across 25 US .edu Ollama hosts.

Restraint discipline held throughout: NO `:cloud` model was invoked on any of the 4 confirmed hosts (would consume real Ollama Cloud subscription quota AND the upstream provider's quota). Class-membership is verified via `/api/tags` enumeration alone; data-membership (a successful unauth `:cloud` invocation routing to the operator's quota) is implied by Ollama's documented architecture but not test-verified by this survey.

## Codification level

This insight reaches numbered status (49) on the basis of:
- 4 independent confirmed instances across 3 states and 4 institutional departments
- Mechanism documented via Ollama's own official documentation (vendor-side confirmation)
- Diagnostic marker is single-shot and restraint-compatible
- Distinct structural class from prior LLMjacking insights (#23-bis, #39)
- Identifies an ecosystem-level fix opportunity (vendor-side warning) AND per-host remediations

Promotion criterion (N ≥ 5 confirmations) softened by the strength of the vendor-side documentation confirmation — the mechanism is no longer hypothetical, only the count.

## Validation path forward

- Sweep additional academic TLDs (`.ac.uk`, `.edu.au`, `.ac.jp`, `.ac.kr`) via visorgoose post-G8-fix to find more LLMjacking-class instances internationally
- Probe research-compute-class hosts (`compute.*.edu`, `*.hpc.*.edu`, `*.cluster.*.edu`) for further confirmations
- Re-probe the 24 unreachable .edu Ollama hosts at different times of day (catch DHCP-rotated student/wireless devices when live)
- Submit ecosystem-level fix recommendation to Ollama upstream (security@ollama.com or via GitHub Issues)
- Coordinate per-host disclosure to the 4 confirmed institutions

## Cross-references

- [`case-studies/universities/US/CA-sdsc.md`](../case-studies/universities/US/CA-sdsc.md) — primary source case study with full 19-model SDSC portfolio + the resolution section
- [`case-studies/universities/US/CA-ucsb.md`](../case-studies/universities/US/CA-ucsb.md) — UCSB MCDB spark-4de1 4th confirmation
- [`case-studies/universities/US/ME-university-of-maine.md`](../case-studies/universities/US/ME-university-of-maine.md) — UMaine ECE-Ubuntu-02 (2026-05-03 original case study)
- [`case-studies/universities/US/NY-rit.md`](../case-studies/universities/US/NY-rit.md) — RIT disco-dgx-spark
- [`methodology/insight-23-bis-llmjacking-proxy-colocation.md`](insight-23-bis-llmjacking-proxy-colocation.md) — adjacent LLMjacking class (proxy colocation)
- [`methodology/insight-39-pooled-account-attribution-laundering.md`](insight-39-pooled-account-attribution-laundering.md) — adjacent LLMjacking class (commercial resale layer)
