# Session Analysis: Auth / Identity / Gateway

## 1. Overview

### Objective
Survey the auth layer in front of AI stacks: API gateways (Kong, Tyk), policy
engines (OPA, OPAL), identity providers (Casdoor, Authentik, Kratos, Hydra). An
exposed admin or policy interface bypasses the auth protecting the downstream
infrastructure. Intel: data/platform-intel/auth-gateway-osint-2026-05-27.md.

### Scope and Constraints
Commercial cloud (GCP, Contabo, Yotta, Namecheap, Alibaba, ByteDance). Shodan via
Playwright. Mullvad was down; verification ran off-VPN with operator authorization.
Restraint: OPA policy IDs only, no `/v1/data` secret dump, no policy bodies, no
Casdoor or Tyk credential submission, no destructive admin calls.

## 2. Environment and Tooling

### Claude Code Operation
Orchestrator-direct. Shodan harvest paced. menlohunt bounded. The VPN was down;
work continued off-VPN with authorization, footprint recorded.

### Tools Used
Full 19-tool arsenal. Material: JAXEN, menlohunt, VisorLog. aimap ran but has no
OPA/Casdoor fingerprint and timed out (gap). Non-runs: VisorSD/recongraph/nu-recon/
VisorPlus (Shodan-blocked), VisorGoose (gov/edu), VisorCorpus/VisorAgent/VisorRAG
(ethical-stop), VisorHollow (Windows), VisorBishop (menlohunt covered shadow),
JS-bundle (JSON/React, no bundle).

### Notable Configuration
aimap v1.9.39 (no OPA/Casdoor fingerprint). nuclide.db at ~/visorlog/nuclide.db.
Workspace ~/recon/auth-gateway-2026-05-29/.

## 3. Methodology

### Enumeration approach
Four dorks. OPA and Casdoor by HTML; Kong and OPA data-path by JSON string.

### Candidate identification
OPA 27, Casdoor 1,375, Kong/OPA-json 0.

### Validation checks
OPA: /health then /v1/policies for policy-list exposure and IDs. Casdoor: identity
only, no login.

### Safeguards
Off-VPN with authorization. OPA policy IDs only. No /v1/data, no policy bodies, no
credential submission.

## 4. Execution Trace

```
1. Read auth-gateway intel; egress off-VPN (Mullvad down, authorized)
2. OPA v1/data dork -> 0; Kong tagline dork -> 0 (both JSON-dark)
3. OPA html "Open Policy Agent" 8181 -> 27
4. Casdoor html -> 1375
5. OPA verify: /health 200 x6; /v1/policies -> 5/6 full Rego list unauth
   (35.202.178.170=13 policies, 158.220.104.240=5, 103.99.36.225/84.247.178.132=2, 34.168.205.115=1)
6. policy IDs read (names=finding); /v1/data NOT pulled (restraint)
7. menlohunt 35.202.178.170 -> port 80 only, isolated
8. VisorLog: 5 unauth OPA events
9. Wrote case study, findings-breakdown, this analysis
```

## 5. Findings

### 5.1 OPA unauth policy-leak x5: HIGH
5/6 sampled OPA hosts return /v1/policies unauth. Full Rego policy list (authz
model + infra topology). /v1/data secret dump not pulled.

### 5.2 Casdoor 1,375: identity platform, admin/123 default
Identity confirmed at scale. Default credential exposure class. Login not attempted.

## 6. Risk Assessment

### Overall Posture
OPA ships auth-off and the population shows it (5/6 open). Casdoor ships a known
default credential, a distinct exposure class. The auth layer itself is the
exposure, and it gates the downstream AI stack.

### Confidentiality
The OPA policy lists disclose the authorization model and operator topology.
`/v1/data` would disclose injected secrets; not pulled. Casdoor would disclose the
identity store if the default credential is unrotated.

### Integrity
An attacker who can write OPA policy or log into Casdoor controls authorization
for the downstream stack. Neither write nor login was attempted.

### Availability
Not assessed.

### Systemic Patterns
- The auth layer in front of AI is itself unauthenticated (OPA 5/6).
- Names are the finding: OPA policy IDs map the authz model without reading bodies.
- Insight #67: Kong and OPA admin APIs JSON-dark; only the OPA diagnostic page indexed.
- 7th thesis data point: OPA auth-off -> 5/6 open; Casdoor default-cred is a separate class.

## 7. Recommendations

### R1: Authenticate OPA
It ships with none. Enable --authentication=token and --authorization=basic, or
bind to localhost.

### R2: Rotate the Casdoor admin/123 default

### R3: Keep Kong/Kratos/Hydra admin APIs off the public internet

```
# OPA: do not bind 0.0.0.0:8181 without auth
opa run --server --authentication=token --authorization=basic
```

## 8. Limitations

Kong, Kratos, Hydra, Tyk, OPAL admin APIs are JSON-dark and not enumerated past the
diagnostic-string dork. Casdoor's default-credential subset needs a login restraint
forbids. aimap has no fingerprint for this category. OPA sample was six of 27. The
verification ran off-VPN.

## 9. PoC Illustrations

```
# OPA unauth policy list (IDs only, restraint)
$ curl -s http://158.220.104.240:8181/v1/policies | jq '.result[].id'
"policies-stillum/stillum.rego"
"policies-stillum/stillum_workflow.rego"
"policies/strvctvra_authz.rego"
# /v1/data (secret-bearing merged doc) NOT pulled
```
