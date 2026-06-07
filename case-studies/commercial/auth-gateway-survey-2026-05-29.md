# Auth / Identity / Gateway survey, 2026-05-29

_Survey type: category survey of the auth layer that sits in front of AI stacks:
API gateways, policy engines, identity providers. Pre-survey intel:
data/platform-intel/auth-gateway-osint-2026-05-27.md._

## Summary

Open Policy Agent ships with no authentication, and five of six sampled hosts
returned their full Rego policy list with no credentials. The policy names are the
finding. They map the operator's authorization model and the topology of whatever
AI stack sits behind them. The admin APIs of Kong and OPA are Shodan-dark because
they serve JSON, so the harvest found OPA only through the diagnostic page string.
Casdoor returned 1,375 identity-platform hosts that ship with the admin/123
default, a different exposure class the restraint ethic left untested.

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7004, K7044, S7068, S7070, S7075, T5904, T5919
- **733 (AI Risk & Ethics Specialist):** T5868, T5882, T5893
- **overlap (Common AI KSATs (all 5 roles)):** K1158, K22, K6311, K6900, K6935, K7003, K942

<!-- ksat-tag:auto-generated:end -->

These platforms are the auth layer. An exposed OPA is the authorization decision
point for everything downstream, and its policy list is the map.

## Stage 0, Discover

| Dork | Total | Verdict |
|------|------:|---------|
| `http.html:"Open Policy Agent" port:8181` | 27 | clean, real OPA decision points |
| `http.html:"casdoor"` | 1,375 | clean, real Casdoor identity platforms |
| `port:8181 "v1/data" "result"` | 0 | OPA JSON-dark |
| `port:8001 "Welcome to kong"` | 0 | Kong admin JSON-dark |

The admin APIs are JSON, so the brand strings live in JSON bodies, not the crawled
HTML, and the Kong and OPA data-path dorks returned zero. OPA surfaced only through
its diagnostic index page string, 27 hosts across India, the United States, and
Germany. Casdoor's web UI renders the brand to HTML, so it returned 1,375, heavily
Alibaba and ByteDance.

## Stage 2, Verify

**OPA, five of six open.** OPA performs no authentication by default. `GET /health`
returned 200 on all six, and `GET /v1/policies` returned the full Rego policy list
on five. The policy IDs are the finding:

- 35.202.178.170 on GCP held thirteen policies under `workflows/licensing/` and
  `workflows/latest_policy_actors/`, a licensing-decision workflow system.
- 158.220.104.240 on Contabo held five: `policies-stillum/stillum.rego`,
  `stillum_workflow.rego`, `main.rego`, `menu.rego`, `strvctvra_authz.rego`. The
  names attribute the operator and name its authorization rules.
- 103.99.36.225 and 84.247.178.132 held the same two, `policy/ui_features.rego`
  and `policy/authz.rego`, the same template on two hosts.
- 34.168.205.115 held one, `src/policies/acl_policy.rego`.
- 66.29.147.3 answered `/health` but not the OPA policy JSON, so it is auth-gated
  or not OPA.

Restraint held. The policy IDs were read because the names are the finding. The
policy bodies in the `raw` field were not read, and `GET /v1/data`, which returns
the full merged data document and often holds secrets injected through bundles,
was not pulled. An exposed OPA leaks the authorization model and, through the data
endpoint left untouched here, frequently the secrets behind it.

**Casdoor, 1,375 identity stores with a known default.** Casdoor is a full identity
platform: users, organizations, OAuth applications. It ships with admin/123. That
is a credential, and submitting it is active authentication beyond a marker probe,
so the per-host auth state was not tested. The survey confirms 1,375 Casdoor
instances and names the default-credential exposure class. It does not log in.

## Stage 3 through 7, the arsenal

menlohunt swept the thirteen-policy OPA host and found only port 80, no stacked
data tier, the host isolated. aimap has no OPA or Casdoor fingerprint, a tool gap,
so the manual verification carried the survey. The five unauthenticated OPA hosts
landed in nuclide.db.

## Impact

- **Authorization model disclosure.** Five OPA decision points expose their full
  policy list with no auth. The policy names reveal the operator's authz rules,
  the workflow structure, and the downstream stack's topology.
- **Secret exposure surface.** OPA's `/v1/data` returns the merged data document,
  often with bundle-injected secrets. It was not pulled, but it is reachable on
  every one of these unauthenticated hosts.
- **Identity store default credentials.** 1,375 Casdoor hosts ship with admin/123.
  The unrotated subset exposes a full identity store. Not tested here.

## Remediation

- Put OPA behind authentication. It ships with none. Enable
  `--authentication=token` and `--authorization=basic`, or bind it to localhost
  and never to 0.0.0.0.
- Rotate the Casdoor admin password off the 123 default immediately.
- Keep Kong, Kratos, and Hydra admin APIs off the public internet, as their own
  docs require.

## What the method could not see

Kong, Kratos, Hydra, Tyk, and OPAL admin APIs are JSON-dark and were not
enumerated past the diagnostic-string dork. The Casdoor default-credential subset
needs a login the restraint ethic forbids. The OPA sample was six of 27.

## Note on footprint

Mullvad was down for this survey, and the host verification ran off-VPN with
operator authorization, from 136.37.103.3. Recorded for an honest footprint.

## Toolchain provenance

```
JAXEN        Playwright; 4 dorks (OPA 27, Casdoor 1375, Kong/OPA-json 0)
aimap        no OPA/Casdoor fingerprint (gap); scan inconclusive (timeout)
aimap-profile N/A this run
VisorGraph   bare cloud IPs, 0 nodes
VisorBishop  menlohunt covered IP-shadow
VisorSD      N/A no Shodan key
VisorGoose   N/A gov/edu scope
menlohunt    35.202.178.170 IP-shadow: port 80 only, 0 chains (isolated)
recongraph   N/A Shodan-dependent
nu-recon     N/A simulated-only
VisorPlus    components individual
VisorLog     5 unauth OPA events -> nuclide.db
VisorScuba   OPA policy-leak not mapped to a control (gap)
BARE         OPA authz first-party class
VisorCorpus  N/A no inference surface
VisorAgent   controlled-target only; not fired at survey hosts
VisorRAG     N/A
VisorHollow  N/A Windows-only
cortex       codify-stage
JS-bundle    N/A OPA JSON, Casdoor React UI, no secret bundle
```
