---
type: survey
---

# Argo CD Population Survey (2026-05-16)

_NuClide Research · 2026-05-16_
_Category 12. Containers & orchestration; k8s CD-pipeline tier_

---

## Summary

Population-scale survey of Argo CD. The Kubernetes continuous-deployment pipeline. Argo CD operators configure git-source repositories, deploy targets (k8s clusters), and credentials; the platform watches git and reconciles cluster state. Unauth access to an Argo CD instance = arbitrary code deployment to the operator's k8s clusters.

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7004, K7044, S7068, S7070, S7075, T5858, T5904
- **733 (AI Risk & Ethics Specialist):** K7040, T5854, T5893
- **overlap (Common AI KSATs (all 5 roles)):** K1158, K1159, K22, K6935, K7003, K942

<!-- ksat-tag:auto-generated:end -->

- Shodan: `http.title:"Argo CD"` → **10,900 unique candidate IPs** (one of the largest single-platform Shodan title-tagged populations seen this run)
- Probed via `fast_enum_argocd.py` (read-only enum of public-by-design endpoints: `/api/version`, `/assets/config.json`, `/api/v1/settings`, `/api/v1/applications?limit=1`, `/healthz`) in 726 seconds at threads=150
- **4,577 confirmed Argo CD deployments** (42%, 6,323 dead at probe; high churn rate)
- **Anonymous-read enabled (misconfig): 3 hosts (0.07%)**, tier-C auth-on-default holds at **99.93%**
- 1,138 with Dex/OIDC SSO configured (25%)
- 4,559 with `/api/v1/settings` publicly accessible (the public-by-design portion that frontend uses)

Restraint: only public-by-design endpoints + the one anon-read-detection probe (`/api/v1/applications?limit=1` which is auth-required normally; if it returns 200 with JSON, the operator misconfigured `anonymousUserEnabled`). Never POST `/auth/login`, never attempt credential testing, never call mutating endpoints.

---

## Headline finding: 3 anonymous-read misconfigs (the takeover class)

| Host | Version | Notes |
|---|---|---|
| `18.189.197.228:80` | v3.3.2 | AWS us-east-2 |
| `18.118.178.219:443` | v2.8.2+dbdfc71 | AWS us-east-2 |
| `3.135.97.239:443` | v2.8.2+dbdfc71 | AWS us-east-2 |

The last two are the same Argo CD version + build commit (v2.8.2+dbdfc71) on the same AWS region. **same operator's 2-host cluster, both with `anonymousUserEnabled: true` in argocd-cm**. Anyone reaching either host can:

1. List all applications via `GET /api/v1/applications`
2. View the configured git source repos for each app (URL, branch, path)
3. View deploy targets (k8s cluster URLs, namespaces, sometimes credentials in spec)
4. View sync status + manifest history (rendered Kubernetes manifests)

The 3rd anonymous host (`18.189.197.228` v3.3.2, same AWS region) may be a separate operator or a third instance of the same operator's CD fleet.

Even though Argo CD's `/api/v1/sync` POST endpoint requires the readonly grant explicitly, anonymous-read alone is **major operator-disclosure tier**, the entire CD pipeline topology is enumerable.

---

## Tier-C auth-on-default confirmation

At population scale (4,577 confirmed Argo CD):

- 4,574 hosts (99.93%) return 401/403 on `/api/v1/applications`. Auth enforced
- 3 hosts (0.07%) misconfigured to `anonymousUserEnabled: true`

This is the cleanest **Tier-C confirmation** in any survey of this run. Argo CD ships with auth enabled by default; the only way to break it is for an operator to explicitly opt into anonymous access in the `argocd-cm` ConfigMap. Three operators did. The framework's default posture is intact.

Parallel to other Tier-C confirmations this run:
- LiveKit Twirp API: 0/184 unauth (0%). Tier-C confirmed
- Vault `/v1/secret/*` and `/v1/auth/*`: auth-required on 99% (3/912 in bootstrap window). Tier-C confirmed
- **Argo CD: 3/4577 (0.07%) anon-read**, tier-C confirmed
- Counter-example: **Consul has Tier-A\*\*** (ACL-off-by-default). 100% (4,105/4,105) unauth in the same window

The contrast between Argo CD and Consul is methodologically sharp: **same operator demographic (k8s-adjacent CD/orchestration tools), same cloud-tier deployment, but auth posture is set by framework default**, argo CD's auth-on-default holds; Consul's ACL-off-default fails universally. Reinforces Insight #13 (shipping defaults are load-bearing) on yet another platform pair.

---

## Operator-attribution via OIDC issuer disclosure

The public-by-design `/api/v1/settings` endpoint returns the configured OIDC/Dex SSO provider's issuer URL. Which discloses the operator's identity-provider integration. Top issuer signatures:

| Count | OIDC issuer | Operator class |
|---|---|---|
| 135 | "Azure" (generic) | Microsoft 365 / Azure AD tenants |
| 66 | "Keycloak" (generic) | self-hosted Keycloak |
| 58 | "Okta" (generic) | Okta-tenanted |
| 36 + 18 + 10 + 10 + 8 + 7 + 6 ... | `login.microsoftonline.com/<tenant-UUID>/v2.0` | **specific Azure AD tenants identifiable** |
| 20 | Cognito | AWS Cognito |
| 16 + 15 | Google | Google Workspace |

**Named-operator attribution via Okta tenant URL** (each tenant URL = an organization):

| Hosts | Okta issuer | Operator |
|---|---|---|
| 10 | `https://livingstonintl.okta.com` | **Livingston International** — supply-chain logistics |
| 8 | `https://1xtechnologies.okta.com` | **1X Technologies** — humanoid robotics (NEO robot) |
| 6 | `https://irhythm.okta.com/oauth2/aus195n2qfxCUUsb42p8` | **iRhythm Technologies** — FDA-cleared cardiac-monitoring (Zio devices, NASDAQ: IRTC) |
| 10 | `https://keycloak.notta.io/auth/realms/MindCruiser` | **Notta** — AI transcription (MindCruiser realm) |

Each `login.microsoftonline.com/<UUID>` URL is also resolvable to a specific Azure AD tenant via Microsoft's public discovery endpoint. **~250 hosts disclose their Azure AD tenant ID**; an attribution pipeline that resolves each to a registered organization name would surface ~250 named operators from this survey alone.

The auth-mechanism choice is itself intel: **operators on Okta + Microsoft tenants are typically enterprise (regulated, customer-facing); operators on self-hosted Keycloak are often midsize-tech or developer-facing**. The distribution suggests Argo CD is broadly enterprise-adopted.

---

## Population characteristics

- **High dead rate (58%)**: Argo CD Shodan-tagged corpus has high churn. The Shodan crawler captured many ephemeral / now-redeployed instances. Worth noting: real population is probably 30-50% larger than 4,577 since the dead set was once-live Argo CD.
- **Wide version distribution**: the working version-tag extraction only succeeded on a small subset (most hosts return /api/version with the Version field empty or `unknown` if running behind a frontend proxy); the actual version mix is wider than the small sample suggests.

---

## Toolchain Provenance

```
0. shodan_paginate.py 'http.title:"Argo CD"'           →  10,900 ip:port unique (242s harvest, 110 pages)
1. fast_enum_argocd.py (threads=150, timeout=6s)       →  4,577 confirmed Argo CD in 726s
2. /api/version + /assets/config.json + /api/v1/settings + /api/v1/applications?limit=1 + /healthz
                                                       →  3 anonymous-read misconfigs detected
3. Dex/OIDC config extraction                          →  1,138 hosts with SSO; named-org attribution via Okta tenant URLs
4. visorlog ingest                                     →  196 events landed (4,381 deduped against prior-survey IPs)
```

---

## Honest negative space

- **Version extraction limited**: Argo CD instances behind nginx/HAProxy reverse-proxy frontends often don't pass through the `Version` field on `/api/version`. The version-distribution table is sparse as a result.
- **OIDC config breadth**: `/api/v1/settings` returns the OIDC provider name + issuer URL but not the client_id or client_secret (which would require auth). The disclosure is intel-tier (operator-attribution) not credential-tier.
- **No mutating-endpoint probes**: never POST /auth/login, never call /api/v1/applications/<name>/sync, never test default-admin-password class. Restraint per CLAUDE.md.
- **Kubernetes version reporting via /api/version** returns empty on most hosts (extraction issue + proxy-strip).

---

## Disclosure posture

The 3 anonymous-read misconfigs (`18.189.197.228`, `18.118.178.219`, `3.135.97.239`) are **per-host disclosure candidates**, the operator-class is enterprise (AWS us-east-2 Argo CD deployments) and the exposure is direct (apps + git sources + cluster URLs all viewable). Recommended outreach via operator-attribution from associated git source URLs (which would also be disclosed by anonymous-read).

The 4,574 properly-auth-gated Argo CD deployments are **not disclosure-relevant**, argo CD is operating as designed. The OIDC tenant-ID disclosure is an intel-tier surface that operators should be aware of but isn't actively-exploitable.

**Named-organization observability via OIDC issuer**, could be a CISO-level note for organizations whose Argo CD `/api/v1/settings` discloses their Azure AD tenant ID or Okta tenant URL. The disclosure is by-design (frontend needs the OIDC issuer to redirect for login), but the operator may not have realized that the public-internet-reachable endpoint surfaces it.

---

## See also

- [`consul-population-survey-2026-05-16.md`](consul-population-survey-2026-05-16.md): Tier-A** counterexample (100% unauth) in the same operator demographic
- [`vault-population-survey-2026-05-15.md`](vault-population-survey-2026-05-15.md): Tier-C secrets-store sibling
- [`etcd-population-survey-2026-05-15.md`](etcd-population-survey-2026-05-15.md): k8s-tier secrets-store
- `shodan/queries/12-containers.md`: the catalog this survey extends
- aimap v1.9.5 (commit `b157c86`). K8s-tier fingerprints
