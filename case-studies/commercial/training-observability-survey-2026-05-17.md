---
type: synthesis
---

# Training observability survey, 2026-05-17

_NuClide Research, 2026-05-17_
_Survey #18 in the AI infrastructure series._

---

## Summary

We surveyed self-hosted training-observability platforms: Weights & Biases (self-hosted), ClearML, Aim, Ray Dashboard, MLflow. The aim was to map the population of public-facing experiment trackers and characterize the auth posture per platform class.

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7004, K7044, S7068, S7075, S7076, T5904
- **733 (AI Risk & Ethics Specialist):** K7052, S7056, S7067, T5868, T5893
- **overlap (Common AI KSATs (all 5 roles)):** K1158, K22, K6311, K6935, K7003, K7041

<!-- ksat-tag:auto-generated:end -->

Three findings carry the survey.

**One. Adya AI's `vanijmcp.adya.ai`** runs a custom FastAPI service called "WandB Service" on port 5005 with a Weights & Biases API key embedded inside it. The schema documents `/runs/full` with parameters `entity`, `project`, `run_path`, `wandb_url`, returning "full history (no limit) + logged artifacts metadata". Any caller who knows the operator's entity name gets the full WandB workspace through the embedded credential. This is a new exposure class. The full case study is at [`adya-ai-vanijmcp-2026-05-17.md`](adya-ai-vanijmcp-2026-05-17.md).

**Two. ClearML signup-open at population scale.** Of 72 confirmed ClearML hosts in the 286-host corpus, 23 (32%) have `basic.enabled=true` in the response to `POST /api/v2.30/login.supported_modes`. Anyone on the internet can register an account against those servers and read the operator's experiments, datasets, and logged artifacts. The endpoint is reachable without authentication and reveals the auth posture without sending credentials, so this is a fingerprintable property at scale, not a per-host investigation.

**Three. Six WandB self-hosted UI hosts.** Smaller population than ClearML but each is a single-org workspace with its own experiment history. We did not enumerate beyond the title-bearing landing page.

---

## Tooling shipped

- **aimap v1.9.10** ships fingerprints for "Weights & Biases" (the SaaS/self-hosted UI), "WandB Service (custom FastAPI proxy)" (the Adya pattern), "ClearML", and "Aim". The Adya custom-proxy fingerprint matches on the FastAPI `/openapi.json` title plus the `service: wandb_service` field on the root.
- A follow-up enumerator can be added to ClearML that issues the `login.supported_modes` POST and classifies `basic.enabled` automatically, instead of the post-survey one-off probe we did here.

---

## Population overview

| Platform | Confirmed hosts | Notes |
|---|---:|---|
| ClearML | 72 | unique IPs; 23 confirmed signup-open |
| Ray Dashboard | (mixed) | aimap's Ray fingerprint and the `ray-dashboard` Shodan string overlap with random services |
| Weights & Biases (self-hosted UI) | 6 | unique IPs from the SPA fingerprint |
| WandB Service (custom proxy) | 1 | Adya AI's vanijmcp host |
| Aim | 1 | matches `aim-ui` body anchor |
| MLflow | (already surveyed prior) | excluded from this corpus |

---

## ClearML signup-open hosts (23)

| IP | ClearML version | basic.enabled |
|---|---|---|
| `157.180.90.89` | (via HTTPS) | true |
| `179.106.229.26` | 1.10.1-359 | true |
| `18.171.66.180` | 1.10.1-359 | true |
| `18.191.201.148` | 1.10.1-359 | true |
| `18.195.219.50` | 1.10.1-359 | true |
| `195.251.122.130` | (via HTTPS) | true |
| `20.39.54.4` | (via HTTPS) | true |
| `3.123.1.133` | 1.10.1-359 | true |
| `3.141.24.158` | 2.4.0-722 | true |
| `3.147.86.12` | 1.10.1-359 | true |
| `3.149.244.24` | 1.10.1-359 | true |
| `34.117.184.56` | 1.10.1-359 | true |
| `34.162.62.10` | (via HTTPS) | true |
| `34.36.87.48` | 1.10.1-359 | true |
| `34.78.14.206` | (via HTTPS) | true |
| `35.209.212.30` | 1.10.1-359 | true |
| `35.212.96.34` | 1.10.1-359 | true |
| `3.72.231.152` | 1.10.1-359 | true |
| `51.15.232.118` | 1.10.1-359 | true |
| `5.196.234.192` | (via HTTPS) | true |
| `54.160.159.236` | (via HTTPS) | true |
| `61.245.156.102` | 1.10.1-359 | true |
| `63.181.180.110` | 1.10.1-359 | true |

Cluster of `1.10.1-359` builds across most of the AWS-hosted set indicates a common deployment template or container image. ClearML 1.10 is two years old; the current open-server stream is 2.x.

---

## Method

- **Shodan harvest:** `html:"Weights & Biases"` (28 hits), `html:"ClearML"` (102), `"ray-dashboard"` (1,113 with mixed-quality matches), `html:"aim-ui"` (2), `port:43800 http` (71). Union: 286 unique IPs.
- **aimap port scan:** 15 ports per host covering training-obs defaults (`5000, 5005, 5001, 8000, 8008, 8080, 8081, 8085, 8090, 8888, 28080, 43800, 11434`) plus `80`/`443`.
- **aimap fingerprint:** new entries for WandB SaaS/self-hosted UI, WandB Service (custom proxy), ClearML, Aim. Already present: MLflow, Ray Dashboard.
- **Auth-mode probe** for ClearML: `POST /api/v2.30/login.supported_modes` (unauthenticated, returns server config; no credentials sent, no signup attempted).

---

## Restraint

We did not attempt user-account creation against any ClearML server. The `login.supported_modes` endpoint is intended to be read by the browser UI to decide which auth modes to render; reading it is consistent with the restraint ethic. We did not query `/runs/full` against `vanijmcp.adya.ai` with any real entity or project value. The OpenAPI schema is the finding.

---

## Disclosure routing

The Adya AI WandB-proxy disclosure is drafted and queued at [`disclosures/IN-adya-ai-vanijmcp-wandb-proxy-2026-05-17.md`](../../disclosures/IN-adya-ai-vanijmcp-wandb-proxy-2026-05-17.md). Primary recipient: `atma@adya.ai` (sourced from the JS bundle on `adya.ai`). CC: `adya.omnichannel@gmail.com` (WHOIS-registered registrant address) + `abuse@microsoft.com` (Azure abuse).

ClearML signup-open hosts: 23 separate disclosures pending. Per-IP recipient resolution required; many appear to be AWS / GCP / Azure customer hosts and will need WHOIS lookups.

---

## See also

- [`adya-ai-vanijmcp-2026-05-17.md`](adya-ai-vanijmcp-2026-05-17.md)
- [`../../methodology/insight-04-whois-over-slug-heuristics-for-disclosure-routing.md`](../../methodology/insight-04-whois-over-slug-heuristics-for-disclosure-routing.md)
