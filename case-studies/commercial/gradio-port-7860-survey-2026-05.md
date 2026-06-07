---
type: survey
---

# Gradio / Stable Diffusion / Langflow on port 7860: Auth Posture Survey

_NuClide Research · 2026-05-03_

---

## Summary

Mass-scan of port 7860 (Gradio's default) across 28 cloud-provider /16 ranges (DO/Hetzner/Vultr) returned 481 hits → fingerprinted via title + product-specific endpoints → **16 confirmed** real Gradio-class deployments. Sparse result vs. earlier surveys; most A1111/ComfyUI/Langflow operators run their UIs on `--listen 127.0.0.1` or behind reverse proxies on 80/443.

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7004, K7044, S7068, S7070, S7075, T5904
- **733 (AI Risk & Ethics Specialist):** K7040, T5854, T5868, T5893
- **overlap (Common AI KSATs (all 5 roles)):** K108, K1158, K1159, K22, K6311, K6935, K7003, S7065

<!-- ksat-tag:auto-generated:end -->

Findings split:
- **9 Langflow**, 1 fully unauth (researcher lab, see below), 8 gated by post-1.5 API-key requirement (auto_login still enabled but token-protected)
- **1 Stable Diffusion WebUI (Automatic1111)** with 4 models installed
- **6 generic Gradio apps** including 2 operator-attributable branded LLMs and 1 ByteDance Ark commercial-API tester

This is the smallest survey in the NuClide commercial-AI series, but it adds a new finding shape: **CVE-research labs discoverable on the public internet**. The single fully-unauth Langflow (`157.90.168.61`) is a security researcher's CVE-2026-33017 lab, not a careless production operator. Documented for completeness but excluded from disclosure pack.

---

## Methodology

```
masscan -iL <28 cloud /16 CIDRs> -p 7860 --rate 10000
  → 481 port-7860 hits

gradio-probe.py (200-thread fingerprint)
  GET /                           → HTML title
  GET /sdapi/v1/options           → A1111-specific config endpoint
  GET /system_stats               → ComfyUI-specific
  GET /config                     → generic Gradio config
  → 16 confirmed (9 Langflow + 1 A1111 + 6 Gradio)
```

---

## Findings Summary

| Metric | Value |
|---|---|
| Cloud /16 ranges scanned | 28 |
| Masscan hits on :7860 | 481 |
| Gradio-class confirmed | **16** |
| Stable Diffusion WebUI (A1111) | 1 |
| Langflow | 9 |
| Generic Gradio | 6 |

### Langflow auth state breakdown

| Auth state | Count |
|---|---|
| Fully unauth (anonymous = superuser) | 1 (researcher lab) |
| auto_login=200 but post-1.5 API-key required | 3 |
| auto_login=400 (disabled, requires login flow) | 4 |
| auto_login=403 (denied) | 1 |

The Langflow upstream community shipped LANGFLOW_AUTO_LOGIN gating in v1.5; eight of nine instances we found have respected that change. The one outlier is on v1.7.3 with auto_login left fully open, and the operator pattern (CVE-named flows) suggests intentional rather than oversight.

---

## Finding 1: Stable Diffusion WebUI (Automatic1111) Exposed (HIGH)

**Host:** `167.172.175.48:7860` (DigitalOcean)

**Product:** Stable Diffusion WebUI (Automatic1111 fork), `/sdapi/v1/options` returns config; `/sdapi/v1/sd-models` lists installed checkpoints.

**Active model:** `dreamshaper_8.safetensors [9aba26abdf]`
**Installed checkpoints:** 4

**Risk class:**

1. **Free image generation on operator's GPU.** A1111's `/sdapi/v1/txt2img` endpoint accepts arbitrary prompts and produces images using the operator's compute. No auth in front of it.
2. **Model identification + supply-chain pivot.** The hash suffix `[9aba26abdf]` is a SafeTensors content fingerprint; `dreamshaper_8` is a popular community-trained checkpoint. Whoever manages this VPS has a specific creative-AI use case (community checkpoints + LoRAs).
3. **Loras / embeddings / upscalers exposure.** A1111 exposes `/sdapi/v1/loras`, `/sdapi/v1/embeddings`, `/sdapi/v1/upscalers`, all the operator's added components are listable. (NuClide did not enumerate these in detail; counts only.)
4. **Model exfiltration via the model repository API.** A1111's HTTP API includes endpoints that allow the operator to download model files; whether those endpoints are exposed at this instance was not tested.

A1111 has no built-in auth. The operator-recommended fix is launching with `--api-auth user:pass` (HTTP Basic) or fronting with nginx auth.

---

## Finding 2: Langflow CVE-Research Lab (HIGH informational, not for disclosure)

**Host:** `157.90.168.61:7860` (Hetzner)
**Langflow version:** 1.7.3
**Auth state:** fully unauth, `/api/v1/users/whoami` returns the `langflow` superuser account without any credentials. `/api/v1/auto_login` returns 200.

The flows on this instance are **not a production AI workload**. The 19 custom user-created flows have names that strongly indicate this is a security researcher's CVE-investigation lab:

| Flow name pattern | Count | Inferred purpose |
|---|---|---|
| `Echo Flow (0-5)` | 6 | Basic Langflow input/output sanity tests |
| `nuclei-cve-2026-33017 (0-2)` | 3 | Nuclei templates for CVE-2026-33017 (a Langflow vulnerability, presumably) |
| `poc-flow (0-5)` | 6 | Proof-of-concept exploitation flows |
| `test_flow` | 1 | Generic test |
| `cve-2026-33017-lab-{hash}` | 3 | Lab variants (each with a different short-hash suffix) |

**This is almost certainly a peer security researcher's working environment.** The CVE-naming pattern + Nuclei template work + iterative `poc-flow (1-5)` versioning + dated lab snapshots (Feb 19, Mar 11, Mar 18-19, Mar 28, Apr 28) match the pattern of someone reproducing a Langflow vulnerability and developing detection signatures.

NuClide is not extracting flow contents from this instance. Other researchers' WIP work warrants the same professional courtesy a private repo does. The instance is documented here for completeness of the survey; **it is excluded from the disclosure pack** for this survey class.

If the operator finds this case study and wants the IP redacted, NuClide will redact on request.

---

## Finding 3: Generic Gradio Branded Deployments (MEDIUM informational)

The six generic Gradio apps include two operator-attributable branded LLM frontends and one commercial-API tester:

| Host | Brand / title | Gradio ver | Components |
|---|---|---|---|
| `135.181.63.198` | **ArchiX Prompt Optimizer Playground** | 6.6.0 | 38 |
| `138.68.151.234` | Player Similarity Finder (sports analytics?) | 5.44.1 | 30 |
| `138.68.159.183` | (default "Gradio") | 6.3.0 | 12 |
| `157.90.236.100` | **NourGPT Hybride** | 5.38.1 | 15 |
| `167.71.90.104` | **Barilife IA** | 4.39.0 | 21 |
| `65.108.32.156` | **ByteDance Ark · img-to-video Tester** | 5.34.2 | 20 |

Notable:

- **NourGPT Hybride** and **Barilife IA** are operator-branded LLM frontends, small commercial AI products with their own naming. Worth tracking for follow-up.
- **ByteDance Ark img-to-video Tester** at `65.108.32.156` is a customer-built playground in front of ByteDance's commercial Ark img-to-video API. Same threat class as the vLLM Class-A reseller-proxies (commercial-API quota theft) but on a different protocol.
- **ArchiX Prompt Optimizer Playground** is interesting, an unauth playground for an "ArchiX" prompt-optimization product, suggesting the operator's product is itself an LLM service.

Gradio apps don't expose auth state in `/config` the same way Open WebUI does; "auth" for a Gradio app usually means HTTP Basic in front of the proxy or `gr.Blocks(auth=...)` set per app. None of these six showed auth challenge on `/`.

---

## Cross-Reference: LiteLLM proxy port 4000

A parallel masscan of port 4000 (LiteLLM default) across the same 28 cloud /16 ranges returned only 100 hits, much sparser than expected. Probing for `/v1/models` confirmed **1 OpenAI-compatible proxy at `45.32.91.23:4000`** (Vultr) serving `gpt-4o`, `gpt-4o-mini`, `claude-3-5-sonnet-20240620`. Did not match LiteLLM-specific markers (`/health/liveliness`, `litellm:` Prometheus prefix). Same threat class as Class-A reseller proxies in the vLLM survey, recorded here for completeness.

---

## Cross-Survey Pattern (updated)

| Tier | Platform | Sample | Unauth |
|---|---|---|---|
| Vector DB | Qdrant / ChromaDB / Milvus | 142 | 100% |
| Inference | Triton / vLLM | 46 | 100% |
| Orchestration UI | Flowise | 43 | 0% |
| Orchestration UI | n8n | 1006 | 0% |
| Orchestration UI | Open WebUI | 112 | 0.9% (14 with open-signup) |
| Orchestration UI | **Langflow** | **9** | **11% (1 unauth, researcher lab)** |
| Image-gen | **A1111** | **1** | **100%** |
| Image-gen / generic | **Gradio apps** | **6** | (no built-in auth concept) |

The orchestration-UI tier remains auth-on-default. The image-gen tier (A1111, ComfyUI) ships without built-in auth, same pattern as the data/inference tier. Operators are expected to put a reverse proxy in front, and most do; the few that don't are exposed.

---

## Disclosure Posture

- **A1111 at `167.172.175.48`**, community A1111 deployment, low-stakes for operator (free GPU but no PII / customer data exposed by the model). DigitalOcean abuse channel for AUP routing.
- **Langflow at `157.90.168.61`**, researcher lab, intentionally excluded from disclosure.
- **ByteDance Ark tester at `65.108.32.156`**, Class-A-equivalent commercial-API quota exposure. Operator-direct contact via brand if identifiable; otherwise Hetzner abuse.
- **Branded Gradio LLMs (NourGPT, Barilife IA, ArchiX)**, informational; operator brand visible, no immediate exploitation primitive without trying inference.

---

## NuClide Pipeline Artifacts

| Stage | Notes |
|---|---|
| Discovery | masscan port 7860 → 481 IPs |
| Fingerprint | `gradio-probe.py`, title + product-specific endpoints |
| What was NOT done | No PoC flow contents extracted from researcher Langflow; no inference run against any operator's GPU; no model files downloaded |

---

## References

- A1111 API auth: https://github.com/AUTOMATIC1111/stable-diffusion-webui/wiki/API
- Langflow auth (v1.5+): https://docs.langflow.org/configuration-authentication
- Cross-survey index: [index.md](index.md)
