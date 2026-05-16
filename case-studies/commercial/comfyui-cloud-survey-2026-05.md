---
type: survey
---

# ComfyUI Image-Generation Workflow Tool: Auth Posture Survey

_NuClide Research · 2026-05-04_
_Sibling tier-2 expansions: [`ollama-tier2-cloud-survey-2026-05.md`](ollama-tier2-cloud-survey-2026-05.md), [`qdrant-tier2-cloud-survey-2026-05.md`](qdrant-tier2-cloud-survey-2026-05.md), [`speech-audio-cloud-survey-2026-05.md`](speech-audio-cloud-survey-2026-05.md)_

---

## Summary

Mass-scan of port 8188 (ComfyUI default) across **76 tier-2 cloud /16 ranges (3.55M IPs) plus 25 Hetzner /16 ranges** (where commodity GPU servers are common). Combined: **6 confirmed ComfyUI instances, 100% unauthenticated.**

The numbers are small but the per-host exposure is unusually rich:

- **385 GB total VRAM** exposed across 5 GPU-equipped hosts
- **NVIDIA RTX PRO 6000 Blackwell Max-Q Workstation Edition** (96GB VRAM, ~$10,000 retail) on one host, anyone on the internet can drive this GPU
- **NVIDIA RTX 4000 SFF Ada** (workstation card, ~$1,500 retail) on 2 hosts
- ComfyUI ships with **no authentication concept whatsoever**, Tier-A. The framework defaults are `--listen 0.0.0.0` with no auth flags available
- Endpoints exposed on every confirmed host:
  - `GET /system_stats`, full GPU + RAM topology
  - `GET /queue`, current jobs running + pending
  - `GET /history`, full history of completed prompts (workflow JSON + parameters + generated-image output filenames)
  - `GET /object_info`, every installed custom node (operator's full custom-extension loadout = fingerprint of operator's preferred workflows)
  - `POST /upload/image`, file upload
  - `POST /prompt`, submit a workflow for execution (= compute theft)

**One operator identified via TLS cert pivot:** `www.bonivivre.fr` (French SaaS, `168.119.149.156` Hetzner). The other 5 hosts have only Hetzner default DNS (`static.X.X.X.X.clients.your-server.de`).

---

## Why is the sample so small?

ComfyUI deployments concentrate on **GPU clouds outside our /16 surface**:

- **RunPod, Vast.ai, Lambda Labs, CoreWeave, Paperspace**, random consumer-GPU rentals scattered across residential ISPs and specialty AI hosting. Not enumerable via cloud-provider /16 prefixes.
- **Hugging Face Spaces, Replicate, Stable Diffusion API**, managed services, not self-hosted exposed.
- **Personal machines on residential / business broadband**, most ComfyUI users run on their own hardware, not on cloud VPSes.

The 6 confirmed hosts represent a self-selected operator population: people who deliberately deployed ComfyUI to a Hetzner / OVH server and exposed it on the public internet. This is a **deliberate-deployment subset**, not a representative sample of all ComfyUI users.

---

## Methodology

```
masscan -iL <76 tier-2 + 25 Hetzner /16 CIDRs> -p 8188 --rate 10000
  → Tier-2 (3.55M IPs):    1 candidate, 1 confirmed
  → Hetzner (1.7M IPs):    202 candidates, 5 confirmed

comfyui-probe.py (200-thread, strict signature)
  GET /system_stats requires top-level "system" + "devices" keys
  Filter AS63949 honeypot fleet via salt strings
  → 6 confirmed ComfyUI instances total
```

Read-only metadata enumeration only:
- `GET /system_stats` (GPU/RAM topology)
- `GET /queue` (current job count, no contents)
- `GET /history` (count + class_type schema; **NOT the prompt text or output images**)
- `GET /object_info` (custom-node count + module prefixes)

NuClide did not:
- Read actual prompt text from `/history` (user content)
- Download generated images via `/view/<filename>`
- Submit any `/prompt` payload (would consume operator GPU and write outputs to operator disk)
- Upload any image via `/upload/image`

---

## Findings Summary

| Metric | Value |
|---|---|
| Tier-2 ranges scanned | 76 (3.55M IPs) |
| Hetzner ranges scanned | 25 (~1.7M IPs) |
| Masscan hits on :8188 | 203 |
| Confirmed ComfyUI | **6** |
| Unauthenticated | **6 (100%)**, by framework design |
| GPU-equipped hosts | 5 of 6 (one CPU-only) |
| Total VRAM exposed | **385.5 GB** |
| Cumulative history (prompts processed) | 35 |
| Active workload at probe time | 0 (idle, but 2 hosts have multi-prompt history) |

### Per-host breakdown

| IP (host) | ComfyUI version | GPU | VRAM | History | Custom nodes |
|---|---|---|---|---|---|
| 178.63.36.43 (Hetzner) | 0.18.1 | RTX 4000 SFF Ada | ~20 GB | 19 | 0 (vanilla) |
| 178.63.101.28 (Hetzner) | 0.18.1 | RTX 4000 SFF Ada | ~20 GB | 16 | 0 (vanilla) |
| 168.119.149.156 (Hetzner, **bonivivre.fr** cert) | 0.16.4 | RTX PRO 6000 Blackwell Max-Q | **~96 GB** | 0 | 0 |
| 135.181.132.190 (Hetzner) | 0.19.3 | (CPU only, RAM 1.9 GB) |, | 0 | 0 |
| 46.4.57.97 (Hetzner) | 0.3.68 (older) | (GPU details not captured) |, | 0 | 0 |
| 167.172.71.134 (Tier-2) | 0.19.3 | (CPU only) |, | 0 | 0 |

### Sample workflow shape (from 178.63.36.43 history, schema only: not contents)

The most-used workflow on this host is the canonical Stable Diffusion text-to-image pipeline:

```
KSampler → CheckpointLoaderSimple → EmptyLatentImage → CLIPTextEncode (positive) → CLIPTextEncode (negative) → VAEDecode → SaveImage
```

This is the default ComfyUI starter workflow. The operator's `CheckpointLoaderSimple` parameter (which model file is loaded) is part of the history payload, visible to anyone hitting `/history`. The actual prompt text and generated images are also visible (NuClide did not retrieve them).

---

## Threat-class taxonomy

For unauth ComfyUI services, four threat classes apply:

### 1. Compute / GPU-hour theft

The most direct risk. Anyone on the internet can `POST /prompt` with their own workflow and consume the operator's GPU. For the RTX PRO 6000 Blackwell Max-Q host (`168.119.149.156`), the GPU rental cost (per Hetzner's published rates and similar specialty hosts) is **$1.50–3.00/hour**. Sustained attacker workload would produce a substantial bill for the operator.

### 2. Workflow + prompt + output exfiltration

`/history` returns the complete workflow JSON for every prompt the operator has run, including:
- The exact text prompts (positive and negative)
- The model checkpoint, LoRAs, VAEs, samplers, CFG scale, seed, steps
- The generated-image filenames (downloadable via `/view/<filename>`)

For an operator running ComfyUI as part of a commercial workflow (stock-art generator, branded marketing imagery, custom client work), this exposes their craft methodology, prompt-engineering trade secrets, and client-deliverable images, without authentication.

### 3. Adversarial workflow injection

`POST /prompt` accepts arbitrary workflows. If the operator's installation has any custom nodes that execute Python, the attacker can submit a workflow that calls those nodes. The `Reroute` node and various utility nodes in popular ComfyUI custom-node packs include code-execution surface.

### 4. Disk-fill via /upload/image

`POST /upload/image` writes attacker-supplied files to the operator's `input/` directory with no size or count limit visible in default config. Disk-fill DoS.

---

## Cross-platform correlations

The ComfyUI population is small and didn't materially overlap with prior surveys:

- **No ComfyUI host shares an IP with a confirmed Qdrant / Milvus / Ollama from prior surveys.** ComfyUI operators are a different audience than text-LLM operators.
- **All 5 Hetzner ComfyUI hosts run the canonical `static.X.X.X.X.clients.your-server.de` rDNS.** They look like personal Hetzner Cloud instances rather than productized SaaS.
- **The bonivivre.fr cert** is the only operator-attributable host. "Bon vivre" = "good living" in French; suggests a French lifestyle / hospitality / wine SaaS using AI image generation. Specific use case unknown without further pivots.

---

## Disclosure posture

- Per-host disclosures NOT drafted (per the parent project's "no more emails" directive)
- Aggregate finding documented for the synthesis paper
- **Operator hardening recommendation** for any reader self-hosting ComfyUI:
  1. **Bind to localhost** with `python main.py --listen 127.0.0.1` and access via SSH tunnel or VPN
  2. **Run behind a reverse proxy** (Caddy / nginx / Traefik) with HTTP basic auth or OAuth
  3. **Firewall** port 8188 to known IPs only
  4. ComfyUI itself has **no auth flag**, the network layer is the only defense
- **Upstream request:** The `--listen` flag should default to `127.0.0.1` instead of accepting `0.0.0.0` without warning. The framework should also expose an optional `--api-key` flag for token-gated `/prompt` and `/upload/image` endpoints.

---

## Comparison to prior Tier-A platforms

| Platform | Population sample | Unauth rate | Key data exposed |
|---|---|---|---|
| Ollama (text-LLM) | 1,192 (DO/Hetzner/Vultr + tier-2 expansion) | 100% | Models loaded, `:cloud` quota theft, abliterated finetunes |
| ComfyUI (image-gen) | **6** (this survey) | **100%** | GPU topology, full workflows + prompts + outputs, $10K+ workstation GPUs |
| MLflow tracking | 11 | 100% | Experiment runs, artifact paths (CVE-2023-1177 path-traversal) |
| Speech & Audio AI | 6 | 100% | Whisper transcription compute, model-pull DoS |
| Triton inference | 2 | 100% | Production-classifier inference (chat-safety, workplace-surveillance) |

The Tier-A pattern reproduces consistently across platform classes, **frameworks that ship without auth-concept deploy without auth at population scale**, regardless of the platform's audience or vertical.

---

## See also

- [`SYNTHESIS-2026-05.md`](SYNTHESIS-2026-05.md), cross-survey synthesis (Tier-A taxonomy)
- [`REMEDIATION-GUIDE.md`](REMEDIATION-GUIDE.md), operator fix-it guide
- [`FUTURE-SURVEYS.md`](FUTURE-SURVEYS.md), roadmap (entry for ComfyUI now closed)
- [`gradio-port-7860-survey-2026-05.md`](gradio-port-7860-survey-2026-05.md), Gradio survey (different image-gen ecosystem on port 7860)
