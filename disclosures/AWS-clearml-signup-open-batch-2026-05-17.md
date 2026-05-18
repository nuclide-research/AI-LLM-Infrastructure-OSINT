Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-17

I'm an independent security researcher conducting good-faith AI infrastructure research under the NuClide Research umbrella (CISA disclosures CVE-2025-4364, ICSA-25-140-11). This is an unsolicited coordinated disclosure. No engagement exists with your organization. I have not attempted to create accounts on any of the affected ClearML instances; the auth posture is fingerprintable without sending credentials.

**Re:** Population-scale unauth-by-misconfig ClearML servers on AWS customer hosts
**Severity:** HIGH

---

## Summary

I'm reporting 10 AWS customer hosts in your network running ClearML with `basic.enabled=true`. ClearML is an open-source MLOps platform. Each affected host allows anonymous account creation against the operator's training-experiment workspace. Effectively unauthenticated access for any internet visitor who registers.

I do not have an operator contact for any of these customers. Sending to AWS Trust & Safety with a request to forward to each affected customer.

## The affected hosts

| IP | ClearML version | AWS region |
|---|---|---|
| `18.171.66.180` | 1.10.1-359 | eu-west-2 (London) |
| `18.191.201.148` | 1.10.1-359 | us-east-2 (Ohio) |
| `18.195.219.50` | 1.10.1-359 | eu-central-1 (Frankfurt) |
| `3.123.1.133` | 1.10.1-359 | eu-central-1 (Frankfurt) |
| `3.141.24.158` | 2.4.0-722 | us-east-2 (Ohio) |
| `3.147.86.12` | 1.10.1-359 | us-east-2 (Ohio) |
| `3.149.244.24` | 1.10.1-359 | us-east-2 (Ohio) |
| `3.72.231.152` | 1.10.1-359 | eu-central-1 (Frankfurt) |
| `54.160.159.236` | (via HTTPS) | us-east-1 (Virginia) |
| `63.181.180.110` | 1.10.1-359 | eu-central-1 (Frankfurt) |
## What "signup-open" means

ClearML's server config exposes `POST /api/v2.30/login.supported_modes`. This endpoint is unauthenticated by design. The browser UI reads it to render the correct login screen. The response includes the operator's current auth posture:

```json
{
  "data": {
    "authenticated": false,
    "basic": {
      "enabled": true,
      "guest": {"enabled": false}
    }
  }
}
```

`basic.enabled: true` means anyone reaching the ClearML server on the public internet can register a new account and then read the operator's experiments, datasets, logged artifacts, model checkpoints, and team configuration. This is functionally equivalent to leaving the dashboard unauthenticated.

## What's at stake

A ClearML workspace holds the training run history for the ML team. Hyperparameter search results. Loss curves. Final-evaluation scores. Dataset URIs and checkpoint paths (often S3/GCS URLs). Some operators include API tokens or credentials in their config dictionaries. The institutional memory of the ML org is reachable to anyone who registers.

## One-line fix

Disable basic-auth signup. In `apiserver.conf` (or the `apiserver` service env):

```yaml
services.auth.fixed_users.enabled: true
services.auth.fixed_users.pass_hashed: false
```

Define fixed admin/user accounts and disable `basic.enabled` via the helm chart or docker-compose. ClearML's docs cover the lock-down sequence at https://clear.ml/docs/latest/docs/deploying_clearml/clearml_server_security/.

Alternatively, put the entire ClearML stack behind a reverse proxy that requires authentication (Cloudflare Access, oauth2-proxy, WireGuard).

## Restraint

The `login.supported_modes` endpoint is intended to be read by the UI. Probing it does not send credentials, does not create accounts, and does not access operator data. We did not attempt registration against any host.

## Reference

Companion survey case study with the full 23-host table:
AI-LLM-Infrastructure-OSINT/blob/main/case-studies/commercial/training-observability-survey-2026-05-17.md
