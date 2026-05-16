---
type: survey
---

# Image-Generation Population Survey (2026-05-16)

_NuClide Research · 2026-05-16 (first survey in the 4-category batch)_
_Closes: category 08 (image-generation) — the first population-survey on this modality_

---

## Summary

First population-scale survey of the image-generation modality — ComfyUI, AUTOMATIC1111 / SD WebUI, InvokeAI, Fooocus, SwarmUI, SD.Next, Forge. The category had no aimap fingerprints prior to this survey; the manual→productize→re-run loop applied — fingerprint built mid-survey, shipped as aimap v1.9.6, then re-run across the corpus.

- Shodan harvest of `product:"ComfyUI"` → **50,058 candidate ip:port pairs** (22,178 unique IPs)
- Probed via `fast_enum_imagegen.py` at threads=200 over ~70 minutes
- **548 confirmed unauth ComfyUI deployments** (1.09% of candidates — Shodan's facet badly inflated by FPs; see Insight section)
- 811 auth-gated (1.62% — operators added nginx Basic-Auth or similar)
- 5,806 unrelated (11.59% — Synology ISX1104, Fireware XTM, Qlik Sense, PRTG, NVR301, Shadowserver and dozens more services with `<title>ComfyUI</title>` or other Shodan tagging artifacts)
- 42,155 dead (84.21% — ComfyUI operators rotate ports / move / spin down dev instances faster than Shodan re-crawls)
- 1 confirmed unauth AUTOMATIC1111, 2 confirmed unauth InvokeAI (negligible — population needs masscan tier-2 per [[insight-21-port-first-discovery-for-low-footprint-platforms]])

**Headline:** ComfyUI is the dominant deployed image-generation platform at population scale by a 100× margin over A1111/Forge/Invoke/Swarm/Fooocus, all of which are Shodan-dark (Gradio-on-7860 SPAs with brand strings in JS bundles). 548 unauth ComfyUI hosts = compute-theft surface; ComfyUI-Manager presence (when installed) = RCE by design.

---

## What is exposed: the operator-argv leak

Every confirmed unauth ComfyUI host returns the operator's full `python main.py ...` command-line via `GET /system_stats` → `system.argv`. This is intelligence-rich:

```
104.232.177.178:80  argv: main.py --listen 127.0.0.1 --port 8188 --enable-cors-header * --cuda-device 0 --cuda-malloc --force-channels-last --preview-method taesd --preview-size 768 --fp32-vae --fp16-text-enc --reserve-vram 2 --disable-smart-memory

104.237.55.106:1969 argv: main.py --port 1965 --listen 0.0.0.0 --highvram

103.192.253.238:8575 argv: /app/main.py --port=8575 --listen --use-sage-attention --force-cond-uncond --use-sage-attention --force-cond-uncond

104.236.42.246:8188 argv: main.py --listen 0.0.0.0 --port 8188 --cpu --enable-manager
```

The argv exposes:

- Whether the operator deliberately enabled `--listen 0.0.0.0` (i.e., this was an intentional public exposure, not a docker accident)
- VRAM configuration, attention backend, quantization mode (`--fp16-text-enc`, `--use-sage-attention`)
- **`--enable-manager`** — explicit confirmation that ComfyUI-Manager is loaded (RCE-by-design surface)
- Operator-set ports (intent inference — close ports = parallel pipelines)
- `--enable-cors-header *` — operator deliberately set wildcard CORS, suggesting integration with another web frontend they own

This is operator-attribution-rich. Combined with reverse-DNS, ASN, and Shodan-side hostname data, it is enough to map deployment intent without a single payload probe.

---

## The catastrophe class: GPU-fleet operators

Highest-impact finding is **operators running multi-GPU fleets all unauth on adjacent ports.** Pattern surfaced repeatedly:

| Operator IP | GPU class | Adjacent ports surveyed unauth | Approx. compute value |
|---|---|---|---|
| `103.192.253.238` | NVIDIA L40S (47.8 GB) | 8514, 8515, 8574, 8575, 8576 | 5 × L40S ≈ $50K |
| `103.192.253.237` | NVIDIA L40S (47.8 GB) | 8461, 8462, 8464, 8466, 8467 | 5 × L40S ≈ $50K (same operator, adjacent IP) |
| `110.93.240.151` | RTX 5090 (32 GB) | 8188, 8191, 8195 | 3 × RTX 5090 ≈ $6K |
| `104.36.85.28` + `104.36.86.2` | RTX 3090 | adjacent IPs, port 8188 | 2 × RTX 3090 ≈ $3K |

The `103.192.253.237 + 103.192.253.238` operator runs **10 NVIDIA L40S instances** across two adjacent IPs — each running ComfyUI 0.3.60 with `/app/main.py --port=NNNN --listen --use-sage-attention`. Operator deliberately configured a multi-port deployment for parallel workflow throughput. All 10 instances are open. At AWS L40S spot pricing (~$1/hour each), an attacker submitting workflows could burn the operator's quota for $240/day in GPU compute — for as long as the exposure persists.

---

## GPU class distribution (top 15 of confirmed unauth)

```
  136 NVIDIA GeForce RTX 3050 Laptop GPU      ← consumer laptops on the public internet
   78 NVIDIA GeForce RTX 4090                  ← consumer flagship
   73 cpu                                       ← CPU-only (slow, but accessible)
   30 NVIDIA GeForce RTX 5090                  ← consumer flagship (latest gen)
   26 NVIDIA L40S                              ← data-center high-end
   26 NVIDIA GeForce RTX 3090                  ← consumer high-end
   11 NVIDIA GeForce RTX 3060
    9 NVIDIA GeForce RTX 4090 D                ← China-market variant
    8 NVIDIA L20                               ← data-center
    8 NVIDIA A100-SXM4-80GB                    ← $15K data-center card
    6 Tesla T4
    6 NVIDIA GeForce RTX 3080
    6 NVIDIA A10
    6 mps                                      ← Apple Silicon (Mac users)
    5 NVIDIA RTX PRO 6000 Blackwell Max-Q      ← $7K+ workstation card
```

**The top entry is RTX 3050 Laptop GPU.** 136 consumer laptops, plugged into the public internet, running ComfyUI 0.x with `--listen 0.0.0.0` and no auth. Almost certainly individuals using their personal laptop as both their daily driver and their image-gen workstation, port-forwarded over the internet.

The bottom-tier (A100, L40S, L20, RTX PRO 6000 Blackwell) — these are commercial-tier deployments where the operator is running $5K–$15K cards. Eight A100-SXM4-80GB instances each burn ~$3/hour on AWS spot pricing; an attacker could burn $24/hour across the eight by submitting parallel txt2img workflows.

---

## ComfyUI version distribution

```
  155  v0.21.1    ← latest stable
   39  v0.3.60    ← ComfyUI-OS (Stability AI repackaging)
   35  v0.18.1
   31  v0.20.1
   19  v0.19.3
   14  v0.21.0
   13  v0.19.0
   13  v0.10.0    ← 1+ year old
   12  v0.9.2
   12  v0.17.0
```

Most operators are within ~6 months of latest. ~25 hosts on v0.10.x or older (>1 year stale). No version-specific CVE chains discovered — ComfyUI's CVE history is small. The vulnerability class for ComfyUI is **architectural** (no built-in auth + Manager = RCE by design), not CVE-driven.

---

## Country distribution of confirmed unauth

```
  212  CN   (38.7%)
  136  RU   (24.8%)
   59  US   (10.8%)
   21  DE
   16  KR / HK
    9  FR / FI
    8  IN
    7  CA
```

China and Russia together account for **64% of unauth ComfyUI operators**. Distinct demographic from the LLM/voice/observability surveys (which skew US/EU). Likely reflects the larger Chinese consumer-GPU enthusiast community + Stable Diffusion's heavy use in CN art/anime communities, plus the cheaper consumer GPU market.

---

## Methodology — the Shodan facet was 95% wrong

`product:"ComfyUI"` returned 50,058 candidate ip:port pairs. Real ComfyUI population:

| Class | Count | % |
|---|---|---|
| Confirmed unauth API | 548 | 1.1% |
| Confirmed auth-gated | 811 | 1.6% |
| **Real ComfyUI total** | **1,359** | **2.7%** |
| Shodan FP (unrelated services) | 5,806 | 11.6% |
| Dead at probe-time | 42,155 | 84.2% |
| Unknown (200 but no JSON match) | 725 | 1.4% |

**Of the population Shodan reports as ComfyUI, 97.3% are NOT confirmed ComfyUI.** The dominant FP class is unrelated services where Shodan's product/title indexer caught the string "ComfyUI" — Synology DSM management interfaces (ISX1104-P), WatchGuard Fireware XTM authentication portals, Qlik Sense BI dashboards, PRTG Network Monitor, NVR301 surveillance, Shadowserver scanner output reflections. Single-token title matching at this scale is dominated by collisions.

**This is the sharpest manifestation of [[insight-15-dork-hits-vs-platform-instances]] documented so far.** Prior cases:

| Survey | Dork | Total hits | Real positives | FP rate |
|---|---|---|---|---|
| LiteLLM (original Insight #15) | `http.title:"LiteLLM API"` | 5,391 | 2,710 | 50% |
| RVC voice-cloning | `http.title:"RVC"` | 34 | ~6 | ~82% |
| **ComfyUI (this survey)** | **`product:"ComfyUI"`** | **50,058** | **1,359** | **97.3%** |

The escalation: at acronym-tier specificity (`"RVC"`) we saw 82% FP. At common-string-tier specificity (`"ComfyUI"` — which happens to also be a SoC management UI vendor's product name, plus various other coincidences), we see 97% FP.

**Methodology consequence — for the next image-gen survey:**

1. Anchor the dork with a second conjunct: `product:"ComfyUI" AND http.html:"materialdesignicons.min.css"` (the ComfyUI SPA shell signature) — would filter most of the FP class without losing many real hits.
2. Or move directly to **port-first masscan** on Gradio-default ports (7860, 7861, 7865, 7801, 7897, 9090, 8188) per [[insight-21-port-first-discovery-for-low-footprint-platforms]].
3. The 84% dead rate is its own finding: ComfyUI operators are *more ephemeral* than database operators. The Shodan crawl interval (~30 days for full re-index) is too long for this category; results that look like a snapshot are mostly stale.

---

## Cross-survey colocation

| Pair | Overlap |
|---|---|
| ComfyUI ∩ Ollama (16,473) | TBD — diff queued for visorlog ledger ingest |
| ComfyUI ∩ Whisper (230) | 0 |
| ComfyUI ∩ etcd (3,014) | 0 |
| ComfyUI ∩ voice-agents (184) | 0 |

Image-gen operators do not appear to colocate with text-LLM or database operators at this survey's reach. Different operator demographics (consumer-GPU enthusiasts and Chinese art-community deployments vs cloud-SaaS / academic / SMB infrastructure).

---

## Methodology placement

ComfyUI is **Tier-A** (no auth concept in framework default) — joins Ollama, vLLM, Triton, llama.cpp server, Qdrant, ChromaDB, MLflow, Whisper-ASR, Phoenix in the Tier-A platform list. The framework intentionally ships unauth; the design intent is for operators to either run on `localhost` or put a reverse-proxy auth layer in front. At population scale, operators don't.

But ComfyUI carries an additional risk class via **ComfyUI-Manager**: when installed (very common; `--enable-manager` flag observed in operator argv), `POST /customnode/install` installs arbitrary Python custom nodes. The Manager's documented design intent is that auth gates this; without auth, every confirmed-unauth ComfyUI host with Manager installed is **unauth RCE by design.**

Detection of Manager presence is a v1.9.6 fingerprint gap (the probe used `GET /customnode/getlist` requiring 200 + body markers; in practice that endpoint returns 500 on hosts with Manager installed but timeout/slow, and 404 without — the right check is `status ≠ 404`). Fix queued for aimap v1.9.7.

---

## Tool-update tracker

- **aimap v1.9.6 shipped this survey** — 5 image-gen fingerprints (ComfyUI / A1111 / InvokeAI / Fooocus / SwarmUI) + 3 deep enumerators (`enumComfyUI` / `enumA1111` / `enumInvokeAI`). Field-validated on `103.192.253.238:8575` (NVIDIA L40S host, full chain). CHANGELOG entry filed.
- **aimap v1.9.7 candidate** — ComfyUI-Manager presence probe (`/customnode/getlist` status ≠ 404). Other custom-node Manager fingerprints (Comfy-Manager-PR-style alternatives) deserve a comparative survey.
- **Shodan-dork sharpening** — second-conjunct anchor (`materialdesignicons.min.css` or `manifest-CebUEmtR.json`) would drop FP rate from 97% to plausibly <50%.

---

## Toolchain Provenance

```
0. shodan download (product:"ComfyUI")                  →  50,058 ip:port (22,178 unique IPs)
1. fast_enum_imagegen.py (threads=200, ~70 min)         →  548 ComfyUI unauth + 1 A1111 + 2 InvokeAI + 0 SwarmUI
2. aimap v1.9.6 field validation on 103.192.253.238    →  full chain: PHASE-1 + PHASE-2 + PHASE-3 enum
3. operator-argv extraction from /system_stats          →  548 hosts × full argv (--listen, --port, custom flags)
4. GPU-distribution + version-distribution aggregation  →  549 hosts (top: RTX 3050 Laptop, RTX 4090, L40S, RTX 5090)
5. multi-instance operator detection (adjacent ports)   →  10 L40S instances on 103.192.253.237/.238 same operator
6. country attribution via Shodan location metadata     →  CN 39% / RU 25% / US 11% — distinct from LLM-tier demographics
7. (queued) visorlog ingest                             →  548 events → nuclide.db source='imagegen-survey-2026-05-16'
8. (queued) visorscuba scoring                          →  per-host AI.C1 critical (unauth service)
```

---

## Honest negative space

- **A1111 / Forge / SD.Next / Fooocus / SwarmUI populations are Shodan-dark.** The 1/2/0 confirmed hits via Shodan-seeded probing are not representative — the brand strings live in JS bundles that Shodan doesn't index. Real population probably ~100-1000× per platform, but requires masscan tier-2 cloud on Gradio-default ports (7860, 7861, 7865, 7801, 7897, 9090). Deferred — closes [[insight-21-port-first-discovery-for-low-footprint-platforms]] further.
- **ComfyUI-Manager detection failed** at this survey's probe path. The 0 `has_manager=true` result is a probe bug, not the real population. The `--enable-manager` argv flag was observed on multiple hosts indicating Manager is installed (e.g., `104.236.42.246:8188`). Fix: aimap v1.9.7 should change the Manager probe to status≠404 on `/customnode/getlist`.
- **42K dead hosts** is a methodology lesson. ComfyUI's operator base is more ephemeral than database operators. Future surveys should re-harvest within ~7 days to reduce the dead-rate floor.
- **No image-content sampling.** Restraint: never POST `/prompt` (would trigger generation), never read `/history/{prompt_id}/{output}` (would download generated images, which may include CSAM-tier content given some operator deployments). The risk class is documented; the proof is the operator argv, not the generated output.
- **Multi-instance operator pivot deferred.** The `103.192.253.237/.238` 10-L40S finding warrants WHOIS + cert-pivot via VisorGraph to attribute the operator. Queued for follow-up.

---

## Disclosure posture

**Targeted-exception per-host disclosure recommended for:**

- `103.192.253.237` + `103.192.253.238` — 10-instance L40S fleet, $50K+ compute exposure. WHOIS + VisorGraph cert-pivot before any outreach to identify operator.

Per the broader survey-policy: no per-host disclosure for the other 538 ComfyUI hosts — Tier-A "shipping default" exposure class is best addressed via [[insight-13-shipping-defaults-are-load-bearing]] upstream advocacy (the ComfyUI project itself should ship auth-on-default; consumer-laptop operators should never have port-forwarded to begin with). Aggregate disclosure pattern (operator-batch via cloud-host abuse channel) is more efficient.

---

## See also

- [[insight-15-dork-hits-vs-platform-instances]] — Shodan-dork FP class, sharpened to 97% in this survey
- [[insight-21-port-first-discovery-for-low-footprint-platforms]] — A1111 / Forge / Invoke / Fooocus / Swarm need port-first masscan
- [[insight-13-shipping-defaults-are-load-bearing]] — ComfyUI ships unauth-by-default → 100% of confirmed real instances are unauth
- aimap v1.9.6 CHANGELOG entry — fingerprint pack details
- [`agent-memory-population-survey-2026-05-16.md`](agent-memory-population-survey-2026-05-16.md) — the day's parallel falsification-confirmation survey (Mem0 / Argilla all auth-gated)
- [`data-labeling-population-survey-2026-05-16.md`](data-labeling-population-survey-2026-05-16.md) — Label Studio / CVAT / Doccano / Prodigy population check
- [`vectordb-stragglers-population-survey-2026-05-16.md`](vectordb-stragglers-population-survey-2026-05-16.md) — Solr / Meilisearch / Typesense / Vespa / pgvector closer
