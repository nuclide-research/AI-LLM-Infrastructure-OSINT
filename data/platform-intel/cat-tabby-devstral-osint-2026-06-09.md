# Cat-Tabby Stage -1 Intel: Devstral self-hosted

**Date:** 2026-06-09
**Squad:** 4 of 4 (Cat-Tabby AI-infra survey)
**Scope:** Devstral *model* fingerprint as it surfaces inside known LLM serving stacks (vLLM, Ollama, llama.cpp, LM Studio, SGLang). Devstral is NOT a server platform. The "self-hosted Devstral surface" = any serving-stack instance whose model-list endpoint advertises a Devstral checkpoint.

---

## Scope resolution (load-bearing)

Devstral is Mistral AI's open-weight coding-agent model, released under Apache 2.0 (Devstral-Small-2505) and Modified-MIT (Devstral-2-123B-Instruct-2512). It ships as model *weights* on HuggingFace, Ollama Library, Kaggle, Unsloth, and LM Studio. There is no "Devstral server." Operators serve it with vLLM, Ollama, llama.cpp, SGLang, LM Studio, or `mistral-inference`.

Consequence for fingerprinting: this platform is a **model-fingerprint deep-enum over existing serving-stack identity fingerprints**. The serving-stack tomes (ollama.json, vllm.json, llamacpp.json) already exist. The Devstral angle slots in as a model-name marker against `/v1/models` (vLLM/SGLang/LM Studio), `/api/tags` (Ollama), `/v1/internal/model/info` (text-generation-webui). Same pattern as Cat-NIM and Cat-53 (model-loaded-inside-serving-stack is the right model).

**Auth posture is inherited from the serving stack.** A Devstral-loaded host is unauth iff its serving stack is unauth.

---

## Release timeline

| Release | Date | Params | License | SWE-Bench Verified |
|---|---|---|---|---|
| Devstral-Small-2505 | May 21, 2025 | 24B (base Mistral-Small-3.1) | Apache 2.0 | 46.8% |
| Devstral-2 / Devstral-2-Small-2 | Dec 9, 2025 | 123B / 24B | Modified MIT / Apache 2.0 | 72.2% / 68% |

Partnership: Mistral AI x All Hands AI (OpenHands). OpenHands + vLLM is the recommended agent scaffold.

---

## Lane 1 - Auth modes & deploy config

- **vLLM:** no-auth by default. `--api-key` / `VLLM_API_KEY` covers only `/v1/*` (and `/v2`, `/inference`). Sensitive non-`/v1` endpoints (`/invocations`, `/inference/v1/generate`, `/generative_scoring`, `/pooling`, `/classify`, `/score`, `/rerank`) are unauth even when an API key is set. Default bind `0.0.0.0:8000`.
- **Ollama:** no-auth by design. `OLLAMA_HOST=0.0.0.0:11434` is the standard public-bind recipe.
- **llama.cpp `llama-server`:** no-auth by default. Optional `--api-key`. Default bind `0.0.0.0:8080`.
- **LM Studio:** no-auth by default on its OpenAI-compatible server (port 1234).
- **SGLang:** no-auth by default. Default bind `0.0.0.0:30000`.
- **text-generation-webui:** no-auth by default. Default bind `0.0.0.0:7860` (UI) and `5000` (OpenAI API).

Shared finding: every recommended Devstral serving stack is no-auth-default. Operators inherit this posture when they follow the official quickstart commands.

---

## Lane 2 - Shodan fingerprint & population

Model-id dork primitives (substring match inside JSON bodies of model-list endpoints):

```
http.html:"devstral"
http.html:"Devstral-Small-2505"
http.html:"Devstral-2-123B"
http.html:"mistralai/Devstral"
http.html:"devstral:24b"
http.html:"devstral-2:123b"
```

Ranked Shodan dorks (basic / strict / version):

| Stack | Basic | Strict | Version |
|---|---|---|---|
| Ollama+Devstral | `port:11434 "devstral"` | `port:11434 http.html:"devstral"` | `port:11434 http.html:"devstral:24b"` |
| vLLM+Devstral | `port:8000 "mistralai/Devstral"` | `port:8000 http.html:"Devstral-Small-2505"` | `port:8000 http.html:"Devstral-2-123B"` |
| llama.cpp+Devstral | `port:8080 "devstral"` | `port:8080 http.html:"Devstral-Small-2505_gguf"` | n/a |

**FP risk (Insight #15, ~50% rule):** `devstral` is rare as a French given name but a known proper noun; raw `body_contains:"devstral"` will catch unrelated HTML pages. Anchor to **JSON context**: confirm via `/api/tags` JSON field `"model":"devstral..."` or `/v1/models` `"id":"mistralai/Devstral..."`. Do NOT count any hit that is HTML title text only.

aimap fingerprints exist for Ollama, vLLM, llama.cpp. Devstral surfaces as a *deep-enum signal* in those enumerators' `/api/tags` and `/v1/models` outputs. Recommended aimap change: extend the existing model-list parsers to emit a `loaded_model_family=devstral` tag when any of the listed model IDs matches `devstral|Devstral`.

nuclei templates: existing Ollama/vLLM detection templates apply (no Devstral-specific template needed); the model-id can be added as a matcher.

Population estimate (cross-reference):
- HuggingFace last-month downloads: 5,738 (Devstral-Small-2505) + 8,784 (Devstral-2-123B-Instruct-2512) = ~14.5K/month.
- Ollama Library pulls: 956.5K (devstral) + 234.8K (devstral-2) = ~1.19M cumulative pulls.
- Internet-exposed serving stacks with Devstral loaded: low-thousands range expected (Ollama exposed population per recent NuClide Ollama walk = 16,473 hosts; even a 1-2% Devstral-loaded share gives 150-300 hosts. vLLM and llama.cpp add more).

---

## Lane 3 - API surface & data exposure

Per stack, the **enumerate-only primitive** is the model-list endpoint:

| Stack | Enumerate (safe) | Do-NOT-call (consumes compute / writes / RCE) |
|---|---|---|
| Ollama | `GET /api/tags`, `GET /api/version`, `GET /api/show` (POST body with model name) | `POST /api/generate`, `POST /api/chat`, `POST /api/pull`, `POST /api/push`, `POST /api/create`, `DELETE /api/delete` |
| vLLM | `GET /v1/models` | `POST /v1/completions`, `POST /v1/chat/completions`, `POST /invocations`, `POST /generative_scoring`, `POST /pooling`, `POST /classify`, `POST /score`, `POST /rerank` |
| llama.cpp `llama-server` | `GET /v1/models`, `GET /props` | `POST /completion`, `POST /v1/chat/completions`, `POST /infill`, `POST /tokenize`, `POST /embedding` |
| LM Studio | `GET /v1/models` | `POST /v1/chat/completions` |
| SGLang | `GET /v1/models` | `POST /generate`, `POST /v1/chat/completions` |
| text-generation-webui | `GET /v1/internal/model/info` | `POST /v1/completions`, `POST /v1/chat/completions`, `POST /v1/internal/model/load` |

Insight #67 / VisorAgent ethics: **no completion endpoint is called** under the enumerate-only restraint posture. Model identity comes from the list endpoint alone.

---

## Lane 4 - CVEs & prior research

**Ollama (CVE family, all 2024):**
- CVE-2024-37032 (Probllama) - RCE via path-traversal in CreateModel; affects <0.1.34; Wiz / Oligo disclosure.
- CVE-2024-39719 - file-existence oracle via CreateModel error reflection.
- CVE-2024-39720 - DoS via malformed manifest.
- CVE-2024-39721 - DoS via `/api/create` infinite loop.
- CVE-2024-39722 - file-existence path traversal via PushModel.
- Net: an exposed Ollama on outdated version = trivial host compromise; Docker installs run as root.

**vLLM (2024-2025 family):**
- CVE-2024-9052 (Mooncake distributed-inference RCE).
- CVE-2025-29770 - Mooncake key-validation bypass.
- CVE-2025-32444 - PyNcclPipe deserialization RCE.
- CVE-2025-46570 - prompt-cache timing side channel.
- vLLM advisory GHSA-w6q7-j642-7c25 - non-`/v1` endpoints unauth even with `--api-key` set.

**llama.cpp:**
- CVE-2024-42477, 2024-42478, 2024-42479 - heap OOB in GGML.
- CVE-2024-41129 - rpc-server RCE (rpc-server runs without auth by default).

**text-generation-webui:**
- CVE-2024-5982 - arbitrary file upload -> RCE.
- CVE-2023-43654 (PyTorch torchserve via TGW config). 

Prior research on Devstral-the-model: HuggingFace card, Mistral blog (May 2025), Spheron deployment guides, OpenHands integration docs. No public population survey of internet-exposed Devstral-loaded hosts as of 2026-06-09.

**Gap:** No prior NuClide-style survey of *which* model families are loaded across the exposed Ollama / vLLM populations. Devstral is a clean test case because the model ID is unique to Mistral and has a stable string match.

---

## Lane 5 - Deployment patterns

Operator-default quickstarts:

```bash
# Ollama (1-line)
ollama run devstral
# OLLAMA_HOST=0.0.0.0 if exposed -> port 11434 unauth

# vLLM (production-recommended)
vllm serve mistralai/Devstral-Small-2505 \
  --tokenizer_mode mistral --config_format mistral --load_format mistral \
  --tool-call-parser mistral --enable-auto-tool-choice \
  --tensor-parallel-size 2
# default bind 0.0.0.0:8000 unauth

# vLLM (Devstral 2)
vllm serve mistralai/Devstral-2-123B-Instruct-2512 \
  --tool-call-parser mistral --enable-auto-tool-choice --tensor-parallel-size 8

# llama.cpp
huggingface-cli download mistralai/Devstral-Small-2505_gguf --include "devstralQ4_K_M.gguf"
./llama-server -m devstralQ4_K_M.gguf --host 0.0.0.0 --port 8080
```

Common ports: Ollama 11434, vLLM 8000, llama.cpp `llama-server` 8080, LM Studio 1234, SGLang 30000, text-gen-webui 5000/7860.

GitHub code-search heuristic: `devstral` in `docker-compose.yml`, `config.json` (Continue.dev), `tabby.toml`, `compose.yaml` reveals operator deploy intent.

Reverse-proxy patterns: nginx + basic-auth, Cloudflare Access, Traefik + ForwardAuth. Often *not* applied to lab/personal deploys (Insight #40 - auth-on-default strengthens across OSS generations under disclosure pressure; serving stacks have NOT shifted yet).

---

## Lane 6 - Ecosystem co-deployment (CAT-COHERENCE FINDING)

The Cat-Tabby category coheres around the **coding-agent IDE-plugin + self-hosted model backend** pattern. Devstral is purpose-built for this slot.

**Natural co-deployment pairs (same host or same /32):**

1. **Tabby front-end + Ollama-Devstral backend.** Tabby (Rust server, port 8080 or 8000) configured to talk to Ollama (11434) on `localhost`. Devstral-Small-2505 fits on a single RTX 4090, which is the Tabby reference hardware. Tabby's `model.toml` points at `http://localhost:11434/v1` with `model = "devstral"`.

2. **Continue.dev (IDE plugin) + vLLM-Devstral backend.** Continue's `config.json` carries `"provider": "openai", "model": "mistralai/Devstral-Small-2505", "apiBase": "http://<host>:8000/v1"`. The vLLM server is the exposed surface; Continue itself is client-side.

3. **OpenHands agent scaffold + vLLM-Devstral backend.** Mistral's recommended pairing. OpenHands UI on port 3000, vLLM on 8000.

4. **Sourcegraph Cody bring-your-own-LLM proxy + Ollama-Devstral.** Cody's BYOK config talks to Ollama via OpenAI-compatible shim.

**Shadow-port sweep priorities** when an exposed Ollama or vLLM is found advertising Devstral (Insight #12 IP-direct-shadow):

- Same /32: probe Tabby UI ports (8080, 8000), OpenHands UI (3000), Continue server-side helper (default rarely-exposed), Cody gateway (9000), Open WebUI (3000, 8080), LibreChat (3080).
- Same /24: same operator likely runs multiple inference stacks; sweep 11434, 8000, 8080, 1234, 30000, 5000, 7860.

Port-map priority: Ollama 11434 -> vLLM 8000 -> llama.cpp 8080 -> SGLang 30000 -> LM Studio 1234. Ollama 11434 is the highest-yield single port for Devstral discovery (Library pulls ratio).

---

## Restraint posture

- WebFetch only on Mistral docs, HuggingFace, Ollama Library, vLLM docs, GitHub, CVE databases, OllamaSearch.
- No HTTP requests to suspected operator endpoints in this Stage -1 phase.
- All operator probing is deferred to Stage 1b (aimap deep-enum) with the enumerate-only endpoint set above.

---

## Sources

- [Mistral - Devstral](https://mistral.ai/news/devstral/)
- [HuggingFace - Devstral-Small-2505](https://huggingface.co/mistralai/Devstral-Small-2505)
- [HuggingFace - Devstral-2-123B-Instruct-2512](https://huggingface.co/mistralai/Devstral-2-123B-Instruct-2512)
- [Ollama Library - devstral](https://ollama.com/library/devstral)
- [Ollama Library - devstral-2](https://ollama.com/library/devstral-2)
- [vLLM Security](https://docs.vllm.ai/en/latest/usage/security/)
- [Wiz - CVE-2024-37032 Probllama](https://www.wiz.io/blog/probllama-ollama-vulnerability-cve-2024-37032)
- [Oligo - More ProbLLMs in Ollama](https://www.oligo.security/blog/more-models-more-probllms)
- [Tabby self-hosted](https://github.com/TabbyML/tabby)
- [Spheron - Deploy Devstral with vLLM](https://www.spheron.network/blog/deploy-devstral-gpu-cloud/)
