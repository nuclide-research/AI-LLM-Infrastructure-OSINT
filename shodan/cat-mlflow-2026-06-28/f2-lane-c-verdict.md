# F2 Lane C -- Verdict + New Attack Surfaces -- 168.138.146.91
Date: 2026-06-28
Lane: C (DCWF 672 T&E Verification)

## SANDBOX-MITM GATE
Status: CLEAN (observation position not compromised; direct OCI egress, no intercepting proxy detected in this session)
L7 conclusions: VALID

---

## VERDICT
Attacker or owner? EXTERNAL ATTACKER
Confidence: HIGH

Evidence summary:
  - mlflow.user ABSENT on all 100+ pwn runs (raw HTTP API, not Python SDK; owner would use SDK)
  - start_time=0 on all pwn runs (SDK sets this field; raw callers don't -- owner never used SDK)
  - Server idle 370 days before first attack wave; zero legitimate ML artifacts (no metrics, no params, no real model content)
  - Wave 2 explicitly targeted file:///etc/cron.d as artifact_location -- persistence attempt, not a test
  - DNS canary (d74lnhgnaeps72h9noug7k6ujxcdta5oy.a.dnsg.cc) and netcat placeholder (1.2.3.4:4444) in model registry -- attacker staging, not owner debugging
  - ProtectAI scanner left 7 model stubs with random base58 names across 2 sessions -- distinct from Wave 1/2 actor

---

## Attack Chain Reconstruction

2025-08-?? -- Host deployed, MLflow exposed on :5000, never used for legitimate ML work.

2026-05-11 00:00:29 UTC -- Wave 1 begins. Automated directory scan lasting 2m48s. Attacker uses raw HTTP API (no SDK). Creates 100+ registered models with random base58 names. No metrics, no params logged. Pure reconnaissance/enumeration of the surface.

2026-05-11 (between waves) -- ProtectAI scanner (separate actor or tooling) runs two sessions against the exposed MLflow, leaves 7 model stubs. Distinct signature from Wave 1.

2026-06-11 16:29:53 UTC -- Wave 2 begins. 15-second burst. Same attacker (same API fingerprint: user_id="", start_time=0). Persistence attempt:
  - Sets artifact_location=file:///etc/cron.d on run c51fda5721954759ade3a16694cf28e0
  - Registers DNS canary in model source: d74lnhgnaeps72h9noug7k6ujxcdta5oy.a.dnsg.cc/poc.tar.gz
  - Plants netcat reverse shell placeholder: 1.2.3.4:4444

At time of Lane C verification (2026-06-28), host is still live. MLflow unauth on :5000. Portainer CE on :9000 is initialized and auth-gated. Unknown Go service on :8000 alive but minimal exposure.

---

## C1 -- Portainer CE 2.19.5 (port 9000)

Probe results:
  - /api/status: {"Version":"2.19.5","InstanceID":"61da7e44-dcdd-439c-ad83-5c41f933ede0","DemoEnvironment":{"enabled":false}}
  - No isInitialSetup field present in response
  - /api/system/version: 401 Unauthorized
  - /api/endpoints: 401 Unauthorized

isInitialSetup: ABSENT (field not returned -- Portainer is past initial setup)
CVE-2024-33661 applicable: NO
  Reason: CVE-2024-33661 requires isInitialSetup:true. Portainer has been initialized; the admin account exists. The bypass path is closed.
CVE-2024-33662 (CVSS 7.5): Not probed (requires auth; read-only lane cannot evaluate)
Endpoints accessible (unauth): /api/status only
Finding severity: N/A (surface open, access not exercised; no bypass condition met)

Verification rung pair (Insight #68): Depth=A (logic probe -- checked the precondition field), Breadth=1 (single live in-scope host). Result: REFUTED.

---

## C2 -- Golang Service (port 8000)

Probe results:
  - /metrics: 404 "Not found"
  - /debug/pprof/: 404 "Not found"
  - /health: 200 OK, body="OK"
  - /healthz: 404 "Not found"
  - /info: 404 "Not found"
  - /: 404 "Not found", HTTP/1.1, Content-Type: text/plain; charset=utf-8

Service identity: Unknown. Standard Go net/http 404 response shape. No Server header. No pprof exposure (no goroutine stack, no binary name leak). No Prometheus metrics.
Finding: Minimal. /health liveness probe exposed (200 OK), no data. No identity signals recoverable.
Finding severity: N/A (liveness probe is not a finding)

Verification rung pair (Insight #68): Depth=A (endpoint probe), Breadth=1 (single host). Result: REFUTED -- no exploitable surface identified.

---

## Full Finding List (all findings on this host)

F2a [CRITICAL] Live cron.d persistence attempt
  - artifact_location=file:///etc/cron.d on run c51fda5721954759ade3a16694cf28e0
  - Wave 2 attacker staged this 2026-06-11; server still live
  - Verification rung: Depth=B (binary -- run record in MLflow DB), Breadth=1
  - Restraint compliance: read-only, no artifact written

F2b [N/A] Portainer CE 2.19.5 / CVE-2024-33661
  - REFUTED: isInitialSetup field absent, Portainer already initialized
  - /api/status readable unauth (version + InstanceID exposed -- minor info disclosure)
  - CVE-2024-33662 (7.5) remains unverifiable without auth -- surface noted, not exercised

F2c [N/A] Golang service port 8000
  - REFUTED: no pprof, no metrics, no identity leak
  - /health returns 200 -- confirms service is alive, nothing more

F2d [HIGH] DNS canary callback in model registry
  - d74lnhgnaeps72h9noug7k6ujxcdta5oy.a.dnsg.cc/poc.tar.gz registered as model source
  - Attacker-controlled callback; if MLflow server fetches model sources, this phones home
  - Verification rung: Depth=B (registry record visible in MLflow UI/API), Breadth=1

F2e [HIGH] Reverse shell placeholder in model registry
  - 1.2.3.4:4444 netcat placeholder -- staging artifact, not live shell
  - Indicates attacker intended follow-on payload delivery

F2f [MEDIUM] ProtectAI scanner exposure
  - Separate actor (ProtectAI tooling) left 7 model stubs across 2 scan sessions
  - Server appears in ProtectAI's scanner corpus -- amplifies disclosure surface

---

## Chain Summary

```
MLflow :5000 (UNAUTH)
    |
    +-- Wave 1: enumeration + 100+ model stubs planted
    |
    +-- Wave 2: persistence staging
    |       |
    |       +-- artifact_location -> file:///etc/cron.d  [F2a CRITICAL]
    |       +-- DNS canary in registry                   [F2d HIGH]
    |       +-- netcat placeholder 1.2.3.4:4444          [F2e HIGH]
    |
    v
Portainer :9000 (AUTH-GATED)
    |
    +-- CVE-2024-33661: REFUTED (initialized, no bypass)
    +-- CVE-2024-33662: UNVERIFIABLE (requires auth)
    |
    v
Go service :8000
    |
    +-- No identity, no pprof, no metrics
    +-- Dead end
```

The chain that matters: MLflow unauth access -> cron.d artifact write attempt -> if MLflow artifact fetch executes, attacker achieves cron job persistence -> host compromise. Portainer and the Go service are NOT part of the active attacker chain. The Portainer attack path (CVE-2024-33661) is closed; the container escape scenario (MLflow -> cron -> Portainer socket) remains theoretical but the cron.d vector is the established path.

If the file:///etc/cron.d artifact_location resolves and MLflow fetches it during any experiment run, the attacker's payload executes as the MLflow process user. That is the live threat.

---

## Restraint Compliance
Total probes: 8 (5 Portainer, 3 port-8000 families)
State-changing calls: 0
DO_NOT_CALL violations: 0
Restraint compliance: 100%

## Auth-State Distribution (this host)
- MLflow :5000: UNAUTH (confirmed by Lane B)
- Portainer :9000: AUTH-GATED (initialized, admin exists)
- Go service :8000: UNKNOWN (no auth surface probed; minimal endpoints)
- SSH :22: AUTH-GATED (key/password)

## Identity Signals
- OCI instance, sa-saopaulo-1 (Lane A)
- Portainer InstanceID: 61da7e44-dcdd-439c-ad83-5c41f933ede0
- ProtectAI scanner in corpus (F2f)
- No domain, no PTR, no TLS anywhere on host
