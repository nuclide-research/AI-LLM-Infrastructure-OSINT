---
id: 50
title: "OVMS Backend Co-location: FastAPI Wrapper + OpenVINO Model Server Both Exposed"
date: 2026-05-21
survey: embedding-tier2-2026-05-21
anchor: 46.4.204.44
status: candidate
---

# Insight #50 — OVMS Backend Co-location

## Observation

Custom FastAPI embedding services often sit in front of an Intel OpenVINO Model Server (OVMS) backend on a co-located port. When the FastAPI wrapper is exposed without auth, the OVMS backend is also exposed without auth — and on a different port than the wrapper.

**Anchor:** 46.4.204.44  
- Port 8001: Custom FastAPI embedding wrapper (user-facing, `/embed`, `/embed/batch`)  
- Port 9000: OpenVINO Model Server 2026.0.0 backend (raw inference engine)  

## The Pattern

```
internet → FastAPI wrapper (:8001) → OVMS backend (:9000) → model weights
                                              ↑
                                      also internet-exposed
```

The FastAPI wrapper handles tokenization, request validation, and the user-friendly embedding endpoint. The OVMS backend is the actual inference engine and is typically reached only by the wrapper. When both are deployed on a bare VPS without firewall rules, both ports are internet-accessible.

## What the OVMS Backend Leaks (without auth)

```
GET /v1/config → {"bge-m3":{"model_version_status":[{"version":"1","state":"AVAILABLE"}]}}
```
Model names and operational state — full model inventory disclosed.

```
GET /v1/models/bge-m3/metadata → TF Serving SignatureDef
```
Input tensor shapes, dtypes (DT_INT64), dynamic dimensions — model architecture class inference.

```
GET /v2/ → {"name":"OpenVINO Model Server","version":"2026.0.0.4d3933c5c"}
```
Exact version string including git commit hash → CVE matching, patch level inference.

## Why It Matters Beyond the Wrapper

The FastAPI wrapper provides a convenience layer but the OVMS backend gives adversaries:

1. **Architecture inference** — tensor shapes reveal model family (BERT-base vs BERT-large, etc.) without needing the model weights
2. **Backend bypass** — with tokenized input, direct inference without the wrapper's input length limits or validation
3. **Version-exact fingerprint** — OVMS git commit hash narrows the attack surface to a specific build

## Enumeration Primitive

When you find any custom embedding service:
```bash
# Probe co-located backend ports
for port in 9000 9001 8080 8088; do
  result=$(curl -s -m 2 "http://$ip:$port/v1/config")
  echo "$port: $result" | head -1
done
```

For OVMS confirmation:
```bash
curl -s "http://$ip:9000/v2/"  # → {"name":"OpenVINO Model Server",...}
```

## Discovery Signal

Shodan doesn't typically index the OVMS response (Shodan crawls `/` and gets an error, not the version endpoint). Active probing is required.

TOME active probe now covers this via `openvino-model-server.json` (added 2026-05-21 commit 84344a6).

## Scope

This pattern is specific to:
- Intel OpenVINO Model Server deployments
- Co-located with FastAPI/uvicorn embedding wrappers
- Bare VPS deployments (no cloud IAM, no firewall rules)

Hypothetical prevalence: low — this is an enterprise embedding stack (Intel OVMS) deployed on a consumer VPS, suggesting a developer or small research team rather than a commercial operator.

## Comparison to Prior Insights

- **Insight #37 (asymmetric auth gating):** there, the dashboard is open and the API is gated. Here, the FastAPI wrapper is open and the backend is also open — symmetric zero-auth.
- **Insight #33 (side-channel attribution via registry catalog):** analogous pattern — the backend service leaks what the frontend doesn't expose.
