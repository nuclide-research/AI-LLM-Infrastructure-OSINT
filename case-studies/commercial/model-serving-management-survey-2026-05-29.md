# Model Serving, management-plane and registry, 2026-05-29

_Survey type: category survey, management-plane and registry angle. The inference
population (vLLM, TGI, LocalAI, LM Studio) was surveyed 2026-05-04 in the LLM
Gateways leg. This leg targets the management-bypass and registry surfaces the
intel flagged: vLLM `/update_weights`, Triton model-load, TorchServe ShellTorch.
Pre-survey intel: data/platform-intel/model-serving-registry-osint-2026-05-27.md._

## Summary

The model-serving category is Shodan-dark. vLLM, Triton, TGI, and TorchServe all
serve JSON APIs, and their identifying strings live in JSON bodies, not in the
HTML Shodan crawls. The dominant self-hosted LLM inference server returned one hit
on its own banner. That one host was a real unauthenticated vLLM serving a 20B
model. The management-bypass surfaces that make this category dangerous are
invisible to passive discovery.

This is Insight #67 in its purest form. An entire high-value category, the actual
inference servers with documented unauthenticated RCE-class management endpoints,
cannot be found through Shodan. The census needs masscan and API-shape
fingerprinting.

## Stage 0, Discover

| Dork | Total | Verdict |
|------|------:|---------|
| `http.title:"triton" port:8000` | 1 | false positive, a Triton Content Engine CMS |
| `http.html:"model_sha" http.html:"tokenization_workers"` (TGI) | 0 | JSON-dark |
| `http.html:"owned_by" http.html:"vllm"` | 0 | JSON-dark |
| `"vllm" port:8000` | 1 | one real host |

NVIDIA Triton serves JSON at `/v2`, so the title dork returned a content-management
system, not the inference server. TGI's `/info` endpoint returns the most
distinctive JSON in the category, including `model_sha` and `tokenization_workers`,
and none of it is crawled. vLLM's `/v1/models` returns `"owned_by":"vllm"`, also
not crawled. The vLLM banner string returned one host on Hetzner.

One hit for the dominant LLM inference server of 2025 and 2026. The population is
real and large; it is simply invisible to Shodan because the servers speak JSON.

## Stage 2, Verify

The one host was real. 144.76.75.252 on Hetzner returned
`{"model":"","version":"0.19.0"}` to `GET /version` and listed
`ggml-org/gpt-oss-20b-GGUF` and `gpt-oss-20b` to `GET /v1/models`, both with no
authentication. It is an unauthenticated vLLM serving an open-weights GPT-OSS 20B
model. No `--api-key` is set, so both the inference plane and the management plane
are open.

The management plane is the severity. vLLM's `/pause`, `/resume`, and
`/update_weights` endpoints are unauthenticated even on deployments that set the
inference API key, and `/update_weights` loads attacker-supplied weights. Those
endpoints were confirmed present in the API surface and not invoked. The restraint
ethic holds: identity and auth state confirmed, no weights loaded, no RPC called.

vLLM 0.19.0 is past CVE-2025-48956, the header-size DoS fixed in 0.10.1.1, so that
specific CVE does not apply. The compute-theft and management-bypass exposures
stand on the unauthenticated state, not a version CVE.

## Stage 3 through 7, the arsenal

The corpus was one host, so the arsenal ran narrow. aimap fingerprinted the vLLM,
menlohunt swept for adjacent services, VisorLog recorded the finding. The
category-level finding, that model-serving is Shodan-dark, came from the harvest,
not the per-host arsenal.

## Impact

- **Compute theft.** The open vLLM lets anyone run inference on the operator's GPU
  against a 20B model, for free.
- **Management-plane bypass.** `/update_weights` lets an attacker load arbitrary
  model weights with no authentication, a supply-chain and code-execution vector.
  The endpoint was not exercised.
- **The dark population.** The real risk is the count this survey could not see.
  The management-bypass surface exists on every unauthenticated vLLM, Triton, and
  TGI, and Shodan finds almost none of them.

## Remediation

- Set `--api-key` on vLLM, and note that it does not protect the management plane.
  Put the whole server behind a reverse proxy with authentication.
- Never run `VLLM_SERVER_DEV_MODE=1` on a public host; it adds `/collective_rpc`
  with no auth.
- Bind Triton and TorchServe management ports to localhost.

## What the method could not see

The category. vLLM, Triton, TGI, and TorchServe are JSON-API servers and do not
index on Shodan. The management-bypass and ShellTorch RCE surfaces need a masscan
pass on ports 8000, 8080, and 8081 with API-shape fingerprinting. This survey
confirmed one host and the structural fact that the rest are dark.

## Toolchain provenance

```
JAXEN        Playwright; 5 dorks (all 0-1, category Shodan-dark)
aimap        fingerprinted 144.76.75.252 vLLM
aimap-profile run on the confirmed host
VisorGraph   bare cloud IP, 0 nodes
VisorBishop  menlohunt covered IP-shadow
VisorSD      N/A no Shodan key
VisorGoose   N/A gov/edu scope
menlohunt    IP-shadow on 144.76.75.252
recongraph   N/A Shodan-dependent
nu-recon     N/A simulated-only
VisorPlus    components individual
VisorLog     finding -> nuclide.db
VisorScuba   vLLM unauth maps to AI.C1
BARE         model-serving authz first-party class
VisorCorpus  N/A (could test the open vLLM, controlled framing only)
VisorAgent   controlled-target only; not fired at the operator host
VisorRAG     N/A no RAG surface
VisorHollow  N/A Windows-only
cortex       codify-stage
JS-bundle    N/A JSON API, no UI bundle
```
