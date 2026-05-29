# Session Analysis: Model Serving, management-plane and registry

## 1. Overview

### Objective
Survey the management-plane and registry surfaces of model-serving platforms: vLLM
`/update_weights`, Triton model-load, TorchServe ShellTorch, TGI. The inference
population was surveyed 2026-05-04 (LLM Gateways). Test the auth-on-default thesis
on the management plane. Intel: data/platform-intel/model-serving-registry-osint-2026-05-27.md.

### Scope and Constraints
Commercial cloud. Shodan via Playwright, both keys dead. Probing through Mullvad
(us-lax-wg-007). Restraint: vLLM identity and auth state only; no /update_weights,
no /collective_rpc, no model load, no ShellTorch exploit.

## 2. Environment and Tooling

### Claude Code Operation
Orchestrator-direct. The Bash safety classifier was intermittently unavailable;
Playwright harvest and Write-based codification continued, Bash-gated arsenal and
git steps batched for when the classifier stabilized.

### Tools Used
Full 19-tool arsenal (narrow corpus, one host). Material: JAXEN, aimap,
aimap-profile, menlohunt, VisorLog. Non-runs: VisorSD/recongraph/nu-recon/VisorPlus
(Shodan-blocked), VisorGoose (gov/edu), VisorCorpus/VisorAgent/VisorRAG (ethical-stop /
no controlled run), VisorHollow (Windows), VisorBishop (menlohunt covered shadow),
JS-bundle (JSON API).

### Notable Configuration
aimap v1.9.39. nuclide.db at ~/visorlog/nuclide.db. Workspace ~/recon/model-serving-2026-05-29/.

## 3. Methodology

### Enumeration approach
Five dorks: Triton title, TGI JSON fields, vLLM JSON field, vLLM banner.

### Candidate identification
All 0 or 1. Category Shodan-dark.

### Validation checks
vLLM 144.76.75.252: /version + /v1/models for identity and auth state.

### Safeguards
Mullvad verified. Identity and auth state only. Management endpoints confirmed
present, not invoked.

## 4. Execution Trace

```
1. Read model-serving intel + methodology
2. Mullvad verified; paced dorks
3. Triton title 8000 -> 1 FP (Content Engine CMS)
4. TGI model_sha+tokenization_workers -> 0 (JSON-dark)
5. vLLM owned_by+vllm -> 0 (JSON-dark)
6. vLLM banner "vllm" 8000 -> 1 (144.76.75.252)
7. Verify 144.76.75.252: vLLM 0.19.0, /version + /v1/models unauth, serving GPT-OSS 20B
8. Management endpoints present (/pause /update_weights); NOT invoked (restraint)
9. aimap + menlohunt + VisorLog on the one host
10. Wrote case study, findings-breakdown, this analysis
```

## 5. Findings

### 5.1 vLLM 144.76.75.252 (Hetzner) unauthenticated: HIGH
vLLM 0.19.0, /version + /v1/models unauth, serving GPT-OSS 20B. No --api-key.
Compute theft plus management-bypass surface (not exercised).

### 5.2 Category-level: model-serving is Shodan-dark
vLLM/Triton/TGI/TorchServe JSON-API. Dominant server returns 1 hit on banner. The
management-bypass population is invisible to Shodan.

## 6. Risk Assessment

### Overall Posture
The findable population is one host, open. The real population is dark. The
management-bypass surface exists on every unauthenticated inference server and
Shodan finds almost none.

### Confidentiality
The open vLLM exposes its model roster. Not the severity here.

### Integrity
`/update_weights` enables loading attacker weights with no auth, a model-poisoning
and code-execution vector. Present, not exercised.

### Availability
`/pause` and the header-DoS CVE class are denial vectors. vLLM 0.19.0 is past the
CVE-2025-48956 fix.

### Systemic Patterns
- Insight #67 purest case: an entire category Shodan-dark behind JSON APIs.
- 5th thesis data point: vLLM --api-key opt-in, the one findable host open.
- Management-plane bypass is auth-off even when inference auth is set; a distinct surface.

## 7. Recommendations

### R1: Reverse proxy with auth in front of the whole server
`--api-key` does not protect the vLLM management plane.

### R2: Never expose dev mode
`VLLM_SERVER_DEV_MODE=1` adds unauthenticated `/collective_rpc`.

### R3: Bind Triton and TorchServe management ports to localhost

```
# vLLM behind auth (api-key alone is insufficient for /update_weights)
# front with nginx auth_basic, or bind to 127.0.0.1
```

## 8. Limitations

The category is Shodan-dark, so this survey saw one host of an unknown large
population. The management-bypass and ShellTorch RCE surfaces need masscan on
8000/8080/8081. The inference population was already surveyed 2026-05-04. The Bash
classifier outage deferred the per-host arsenal and git push within the session.

## 9. PoC Illustrations

```
# vLLM unauth identity (management plane open, not exercised)
$ curl -s http://144.76.75.252:8000/version
{"model":"","version":"0.19.0"}
$ curl -s http://144.76.75.252:8000/v1/models
{"data":[{"id":"ggml-org/gpt-oss-20b-GGUF","owned_by":"local"},{"id":"gpt-oss-20b",...}]}
```
