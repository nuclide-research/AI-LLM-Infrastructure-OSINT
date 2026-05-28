# Insight #66: Fingerprint DefaultPorts Must Be Survey-Driven, Not Doc-Driven

**Date:** 2026-05-27  
**Survey:** Argo Workflows (Category 29), aimap v1.9.35 fix  
**Anchoring data:** 156 hosts, 111 on port 443, 0 on port 2746

## The Finding

aimap's fingerprint matcher filters candidates by `DefaultPorts`. A fingerprint listing only the vendor-documented default port will be silently skipped on every host running the service on a different port — producing a clean scan with 0 findings on a population where the service is actively deployed.

**Argo Workflows case:**
- Vendor docs: port 2746 (argo-server default)
- Fingerprint: `DefaultPorts: []int{2746}`
- Reality: 111 of 136 open instances found on port 443

Result: aimap scanned 156 hosts, found 136 open ports, and matched **0 Argo Workflows services** — because the fingerprint was never tried against port 443 hosts.

## Root Cause

Two factors combine:
1. K8s LoadBalancer deployments expose service on port 443 (external) → internal port 2746. The external port is what Shodan and aimap see.
2. The fingerprint's `DefaultPorts` is read from vendor docs, not from observed deployment data.

Without a survey pass, there's no signal that the effective deployment port differs from the canonical port.

## Generalization

Any service that is commonly deployed behind a reverse proxy, K8s ingress, or cloud load balancer will expose on a different port than its native default. Common patterns:

| Service Type | Native Port | Common Deployment Port |
|---|---|---|
| Argo Workflows | 2746 | 443 (K8s LB) |
| MLflow | 5000 | 80/443 (nginx proxy) |
| Langfuse | 3000 | 443 (Vercel/cloud) |
| Ollama | 11434 | 443 or 80 (proxy) |
| Open WebUI | 8080 | 443 (ingress) |

Any of these fingerprints coded only with the native port will miss the proxy-fronted population.

## The Fix

**Process:** Before finalizing a fingerprint, run a survey pass and check `port_distribution` in the scan results. If the effective port differs from the native port, add it to `DefaultPorts`.

**Code fix (Argo Workflows v1.9.35):**
```go
// Before (doc-driven):
DefaultPorts: []int{2746},

// After (survey-driven):
DefaultPorts: []int{2746, 443, 80, 8080, 8443},
// 81% of Shodan-discovered instances found on port 443 (2026-05-27 survey)
```

## Validation Pattern

After every major fingerprint addition:
1. Run against a Shodan harvest of the target service
2. Check `open_ports` distribution by port number
3. If any port with >10% of hosts is not in `DefaultPorts`, add it
4. Re-run the scan and verify `services_found` increases

## Why the Silent Failure Is Dangerous

The scan produces `services_found: 0` — which looks like "no Argo Workflows instances in the population" rather than "Argo Workflows fingerprint never tried on the population." The false negative is indistinguishable from a true negative without additional diagnostic steps.

The `[!] no FP candidates for <host>:<port>` warning (emitted to stderr) helps, but is easily missed in bulk scan output. Consider adding it to the scan summary when the affected open-port count exceeds a threshold.
