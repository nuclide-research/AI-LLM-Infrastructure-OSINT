# San Diego Supercomputer Center: Public Ollama on `compute.cloud.sdsc.edu` — 53-Model Inventory + `:cloud`-suffix Cloud-Proxy Class

_NuClide Research · 2026-05-19_

---

## Summary

The San Diego Supercomputer Center (SDSC) operates a publicly-reachable Ollama 0.20.4 instance at `132-249-238-182.compute.cloud.sdsc.edu` (132.249.238.182). `/api/tags` returns 53 models. The first entry in the model list is `gemini-3-flash-preview:cloud` with `remote_model:"gemini-3-flash-preview"` and `remote_host` pointing to a Google API endpoint — Ollama's cloud-proxy configuration class is OBSERVED on this host. SSH (OpenSSH 8.9p1 Ubuntu) is the only other open port.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 132.249.238.182 |
| rDNS | `132-249-238-182.compute.cloud.sdsc.edu` |
| Org (WHOIS) | San Diego Supercomputer Center (`OrgName: San Diego Supercomputer Center`, `OrgId: SDSC-Z`, `NetName: SDSC`, CIDR `132.249.0.0/16`) |
| City | San Diego, CA |
| Shodan reported org | San Diego Supercomputer Center |
| Open ports observed | 22 (OpenSSH 8.9p1 Ubuntu 3ubuntu0.15), 11434 (Ollama 0.20.4) |
| Domain pattern | `compute.cloud.sdsc.edu` — SDSC's institutional cloud-compute environment |

SDSC is an independent ARIN org (SDSC-Z) — administratively distinct from UCSD despite the geographic and academic affiliation. The `compute.cloud.sdsc.edu` subdomain indicates the host sits inside SDSC's research-computing service mesh.

---

## Observations

### Ollama API surface (unauth)

`GET http://132.249.238.182:11434/api/version` → 200, `{"version":"0.20.4"}`.

`GET .../api/tags` → 200, 18,945 bytes containing 53 model entries.

`GET .../api/ps` → 200, 379 bytes — shows `llama3.2:latest` (size 2,481,301,504 bytes / ~2.4 GB) actively loaded in resident memory at probe time.

`GET .../api/show` (POST with model name) → 200, returns LLAMA 3.2 community license + model details.

### Model inventory class memberships

53-model inventory observed. **19 of the 53 are `:cloud`-suffix entries** (Ollama Connect cloud-subscription class). The cloud-proxy portfolio:

- `deepseek-v3.2:cloud`, `deepseek-v4-pro:cloud`, `deepseek-v4-flash:cloud`
- `kimi-k2.5:cloud`, `kimi-k2.6:cloud`, `kimi-k2-thinking:cloud`
- `glm-4.6:cloud`, `glm-4.7:cloud`, `glm-5:cloud`, `glm-5.1:cloud`
- `minimax-m2:cloud`, `minimax-m2.1:cloud`, `minimax-m2.5:cloud`, `minimax-m2.7:cloud`
- `nemotron-3-super:cloud`
- `qwen3.5:cloud` (listed twice — once each case), `qwen3-coder-next:cloud`, `qwen3-next:80b-cloud`
- `gemini-3-flash-preview:cloud`

Each `:cloud` entry shows a `size` of ~340-397 bytes (the cloud-proxy stub size — the actual model lives upstream). This portfolio is **IDENTICAL to the UMaine ECE-Ubuntu-02 host** (see `ME-university-of-maine.md`) and **near-identical to the RIT disco-dgx-spark host** (see `NY-rit.md`). Three independent .edu Ollama deployments running the same Ollama Connect cloud-subscription portfolio — see candidate insight at the bottom of this case study.

The local-model portion of the 53-model inventory includes substantial models:

| Model | Size |
|---|---|
| `Qwen3.5:122b-a10b` | 81.4 GB |
| `Qwen3.5:35b-a3b` | 23.9 GB |
| `qwen3.5:122b-a10b` | 81.4 GB (case-duplicate of above) |
| `qwen3.5:35b-a3b` | 23.9 GB (case-duplicate of above) |
| `qwen3.6:35b` | 23.9 GB |
| `llama3.1:70b-instruct-q4_K_M` | 42.5 GB |
| `qwen3:32b-q4_K_M` | 20.2 GB |
| `gemma3:27b` | 17.4 GB |
| `qwen3:14b-q4_K_M` | 9.3 GB |
| `qwen2.5:14b-instruct-q4_K_M` | 9.0 GB |
| `huihui_ai/deepseek-r1-abliterated:14b` | 9.0 GB |
| `gpt-oss:20b` | 13.8 GB |
| `qwen3:8b-q4_K_M` | 5.2 GB |
| `deepseek-r1:latest` | 5.2 GB |
| `qwen2.5:7b-instruct-q4_K_M` | 4.7 GB |
| `llama3.1:8b-instruct-q4_K_M` | 4.9 GB |
| `LLaVA:latest` | 4.7 GB |
| `Mistral:latest` | 4.1 GB |
| `gemma3:latest` | 3.3 GB |
| `llama3.2:3b-instruct-q4_K_M`, `llama3.2:latest`, `llama3-backup:latest`, `mario:latest` | 2.0 GB each |
| `llama3.2:1b-instruct-q4_K_M` | 808 MB |
| `tinyllama:1.1b-chat-v1-q4_K_M` | 669 MB |
| `mxbai-embed-large:latest` | 670 MB (embedding) |
| `smollm2:135m` | 271 MB |
| `nomic-embed-text:latest` | 274 MB (embedding) |
| `all-minilm:latest` | 46 MB (embedding) |

Embeddings + the local Qwen / Llama / Gemma / DeepSeek stack indicate a research-grade RAG-capable deployment.

**Notable**: `huihui_ai/deepseek-r1-abliterated:14b` (~9 GB) is an **abliterated** variant of DeepSeek-R1 — meaning safety-training has been removed / suppressed. This is a model class deliberately tuned to bypass safety guardrails. Its presence on an SDSC public-unauth Ollama is observation-class evidence; whether SDSC personnel are aware of this specific model's variant and its policy implications is not determinable from external probe. Also notable: `mario:latest` (a Super Mario-themed custom build) suggests at least one operator is making personalized model variants.

The `Qwen3.5:122b-a10b` model (81 GB) and `llama3.1:70b-instruct` (42 GB) are research-class large models — non-trivial GPU memory requirements.

**What was NOT done per restraint ethic:**
- No POST to `/api/chat/completions` or `/api/generate` on any model (local or `:cloud`).
- No POST to `/api/create` (CVE-2025-63389 class endpoint).
- No invocation of the `:cloud`-suffix models — would consume SDSC's Ollama Connect quota AND the upstream provider's quota.
- No SSH credential testing on port 22.
- **Did probe `/api/show` for metadata** (system prompts, license, parameters, model_info keys) — this is metadata-only read, no model state changed.

### What was NOT tested per restraint

- No POST to `/api/chat/completions` or `/api/generate` on either local or cloud-suffix models.
- No POST to `/api/create` (the CVE-2025-63389 class endpoint).
- No SSH credential testing.
- Full `/api/tags` JSON body was inspected; the 53-entry list was enumerated but specific model names beyond the first entry are summarized rather than transcribed verbatim into this case study (held for follow-up if needed).

---

## Operator attribution (per Insight #4)

- **WHOIS OrgName**: San Diego Supercomputer Center
- **WHOIS OrgId**: SDSC-Z (independent — distinct from UCSD's UCSDN-Z)
- **WHOIS NetName**: SDSC (CIDR `132.249.0.0/16`)
- **Hostname pattern**: `*.compute.cloud.sdsc.edu` indicates the host is inside SDSC's research-cloud service environment
- **Shodan reported org**: San Diego Supercomputer Center

Authoritative attribution chain matches across all three sources. SDSC's relationship to UCSD is parent-org adjacent (the center is housed at UCSD) but ARIN registration is independent.

---

## Cross-tool confirmations

| Tool | Output | Notes |
|---|---|---|
| `visorgoose --tld .edu` (G8 fix) | Surfaced with 53-model inventory, tagged CLOUD + RAG | Tool tags this host as "cloud proxy exposed" |
| `aimap -ports-class wide` | Open port 11434 confirmed via direct probe | |
| Direct `/api/version`, `/api/tags`, `/api/ps`, `/api/show` | All return 200 unauth | Verified live Ollama, not redirected (contrast with G22 Michigan Tech FP) |
| `shodan host` | 2 open ports (22 + 11434), no other services exposed | Minimal attack surface beyond Ollama |

---

## Notable details

- **Supercomputing-scale compute reachable from an unauth LLM API**: SDSC operates Comet, Expanse, and related NSF-funded HPC resources. Whether the host backing this Ollama instance is a head node, a service VM, or a dedicated inference box is not determinable from the external probe. The `compute.cloud.sdsc.edu` naming convention suggests SDSC's cloud-compute service mesh rather than a bare-metal HPC scheduler.
- **First model in inventory is `gemini-3-flash-preview:cloud`**: this is class-observable documentation that SDSC personnel configured this Ollama instance with at least one `:cloud`-suffix model. Ollama's `:cloud` class requires authentication to Ollama's cloud subscription service via the operator's Ollama account; the configured presence implies a valid Ollama-account token is on this host.
- **`llama3.2:latest` actively loaded in resident memory** at probe time. This is class evidence that the host serves actual inference traffic, not just an idle deployment.
- **Authentication on `/api/*` is absent**. Standard Ollama HTTP API is open to the internet. The endpoint set (version, tags, ps, show, chat, generate, embeddings, create, delete, push, pull, copy) is reachable without any auth header.

---

## Class-membership summary (no tier labels per survey convention)

- Public unauth Ollama HTTP API class — OBSERVED (data: `/api/version` returns 200)
- Model-inventory enumerable class — OBSERVED (data: 53 entries returned from `/api/tags`)
- Resident-memory model class — OBSERVED (data: `llama3.2` shown loaded in `/api/ps`)
- Ollama cloud-proxy class — OBSERVED (data: first inventory entry has `:cloud` suffix + `remote_model` + `remote_host` fields)
- CVE-2025-63389 applicability class — APPLICABLE per public version-vulnerability mapping (Ollama 0.20.x predates the `/api/create` patch); we did NOT verify the host is unpatched by POSTing `/api/create`.

Data-membership (actual unauthorized model invocation, actual quota consumption, actual data exfiltration) was not tested per restraint ethic.

---

## Discovery method

- **Initial surfacing**: visorgoose `--tld .edu` scan on 2026-05-19 20:56 UTC after the G8 fix added `.edu` to the supported TLD table. The scan combined CT-log harvest (crt.sh on sdsc.edu) + DNS resolution + Shodan org-tagged + Ollama-default port-11434 probe.
- **Verification**: direct `/api/version` + `/api/tags` probes confirmed live Ollama 0.20.4. WHOIS confirmed SDSC institutional attribution.
- **Cross-validation**: aimap `-ports-class wide` independently identified open port 11434 (but did not deep-enum this specific host as it was added to wave-2 corpus mid-run).

---

## Source artifacts

- visorgoose state: `~/recon/edu-llm-infra-2026-05-19/stage2-wave2/visorgoose-edu-state.json`
- visorgoose report: `~/recon/edu-llm-infra-2026-05-19/stage2-wave2/visorgoose-edu-report.md` (SDSC entry)
- Direct probe: `~/recon/edu-llm-infra-2026-05-19/stage2-wave2/vg-priority-direct-probe.json` (SDSC section)
- aimap on visorgoose-priority hosts: `~/recon/edu-llm-infra-2026-05-19/stage2-wave2/aimap-vg-priority.json`
- WHOIS: `whois -h whois.arin.net "n + 132.249.238.182"` (re-runnable)

---

## Pattern observation — academic supercomputing centers

This is the first NuClide-surveyed supercomputing-center-administered Ollama in the .edu population. The pattern worth tracking: NSF-funded HPC consortia (SDSC, NCSA, TACC, PSC, NERSC, etc.) increasingly stand up institutional LLM-serving alongside their traditional batch-compute services. The deployment posture of those services merits its own survey lane. SDSC's `compute.cloud.sdsc.edu` naming convention may be a discovery handle for the broader pattern — variants like `compute.cloud.{ncsa|tacc|psc}.edu` are worth a follow-up dork.

---

## Candidate Insight (queued): shared Ollama Connect cloud-subscription portfolios across .edu deployments

SDSC's 19-model `:cloud` portfolio is **near-identical** to two other .edu Ollama deployments documented in the NuClide ledger:

| Host | `:cloud`-suffix model count | Common entries |
|---|---|---|
| **SDSC `compute.cloud.sdsc.edu`** | 19 | deepseek-v3.2/v4-pro/v4-flash, kimi-k2(.5/.6/-thinking), glm-4.6/4.7/5/5.1, minimax-m2(/2.1/2.5/2.7), nemotron-3-super, qwen3.5, qwen3-coder-next, gemini-3-flash-preview |
| **UMaine ECE-Ubuntu-02** | 18 (per existing case study) | Same family — deepseek-v4-pro/-flash, kimi-k2, glm-4.7 / glm-5, minimax-m2 series, nemotron-3-super, qwen3.5, qwen3-coder-next, gemini-3-flash-preview, devstral-2:123b |
| **RIT disco-dgx-spark** | 18 | Same family — deepseek-v4-pro/-flash, kimi-k2(.5/.6/-thinking), glm-4.6/4.7/5/5.1, minimax-m2 series, nemotron-3-super, qwen3.5, qwen3-coder-next, gemini-3-flash-preview |

Three independent institutions (SDSC supercomputing center, UMaine ECE dept, RIT DISCO group) running the same Ollama Connect cloud-subscription portfolio cannot be coincidence. Hypotheses:

1. **Shared operator** — one individual or small team has admin access to all three Ollama instances and configured them identically.
2. **Shared documentation** — an Ollama Connect "subscribe to all popular models" guide or a courseware/vendor recommendation that operators are following.
3. **Vendor-bundled subscription package** — Ollama Connect may offer an academic / educational subscription bundle that pre-populates these specific models.
4. **Independent convergence on Ollama's popular-models list** — possible but unlikely given the specific version selections (e.g., all three have `deepseek-v4-pro:cloud` not just generic `deepseek:cloud`).

**Candidate Insight #49** (queued for codification after second-observation confirmation, per Insight methodology). Worth following up with:
- A `hostname:*.edu product:Ollama` Shodan sweep + per-host `/api/tags` enumeration to count how many .edu Ollama instances have this exact portfolio.
- Ollama Connect product page review to identify if there's an academic / institutional subscription bundle.
- WHOIS / contact-info on the three confirmed instances to identify operator overlap (Insight #4 + contact-info-from-disclosure-trail).

If the portfolio shows up on N more .edu hosts (with N ≥ 3), the deployment-template pattern is confirmed and the Insight enters numbered status.

### 2026-05-19-late validation: 4th match confirmed (UCSB MCDB)

A validation sweep across 25 US .edu Ollama hosts (Shodan `hostname:.edu product:Ollama`) found **24 unreachable** (DHCP-rotation pattern on wireless/eduroam student-laptop hosts) and **1 strong match**:

- **UCSB `spark-4de1.mcdb.ucsb.edu`** (128.111.208.95) — Ollama v0.18.0, 22 models, **18/18 reference-portfolio match + 1 additional `:cloud` entry**

Four confirmed institutions now: SDSC + UMaine ECE + RIT DISCO + UCSB MCDB. **All 4 are research-compute environments** across 3 states (CA×2, ME, NY) and 4 distinct departments (NSF supercomputing, ECE, distributed-computing group, molecular biology). The pattern's concentration in research-compute IT contexts (rather than faculty workstations or student devices — those mostly DHCP-rotated and were unreachable in the validation sweep) refines the hypothesis: **shared deployment template circulated through research-computing communities** (XSEDE / ACCESS-CI / OSG / CASC inter-institutional channels) is the most likely upstream explanation, ahead of vendor-bundled subscription or single-shared-admin hypotheses.

Pattern now strong enough that disclosure-routing strategy shifts: instead of per-institution outreach, identifying the upstream documentation source / vendor bundle would close the exposure across N institutions at once. Validation continues — next-step: search XSEDE/ACCESS-CI mailing-list archives and GitHub for the exact 18-model `:cloud` list as a deployment script.

### 2026-05-19-late upstream RESOLVED — Ollama-Cloud-signin × public-exposure (LLMjacking class)

The "shared deployment template" hypothesis was wrong. WebFetch of Ollama's own docs (https://docs.ollama.com/cloud and https://ollama.com/blog/cloud-models) confirms:

> "Cloud models use inference compute on ollama.com and require being signed in to ollama.com" — via `ollama signin`

The `:cloud` entries in `/api/tags` are **Ollama's own curated cloud-models catalog** — exposed automatically once the operator runs `ollama signin` to enable an Ollama Cloud subscription (Pro $20/mo or Max $100/mo). Every Ollama-Cloud-signed-in instance lists the same 18-ish models because they all see the same vendor catalog.

The 4 confirmed instances aren't 4 operators converging on a deployment template — they're 4 operators who all ran `ollama signin` AND left their `:11434` publicly reachable without authentication.

**Refined finding (promotable to numbered Insight)**:

> Ollama-Cloud-signin × public-exposure = LLMjacking surface. Any Ollama instance that (a) ran `ollama signin` AND (b) is publicly reachable on port 11434 without auth is exposing the operator's Ollama Cloud account quota to public invocation via `POST /api/chat`. The `:cloud`-suffix entries in `GET /api/tags` are the diagnostic marker. Cost-bearer: the operator.

Same attack class as Insight #39 (pooled-account attribution-laundering on Claude relays) but with Ollama Cloud subscriptions as the bag-holder instead of Claude relay pools. The research-compute-institutional parallel of the commercial-reseller pattern.

Per restraint, we did NOT invoke any `:cloud` model on SDSC to verify the billing path — the `:cloud` entries are class-membership evidence; data-membership (a successful unauth invocation routing to SDSC's quota) is implied by Ollama's documented architecture but not test-verified.

**Disclosure routing now has two complementary targets**:

1. **Per-host (SDSC + UMaine ECE + RIT DISCO + UCSB MCDB)**: `ollama signout` on the host OR firewall port 11434 from public reach
2. **Upstream (Ollama themselves)**: could add a warning when `ollama serve` binds to 0.0.0.0 AND `ollama signin` is active. Single ecosystem-level fix prevents recurrence.
