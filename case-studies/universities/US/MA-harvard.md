# Harvard University: Langfuse Unauthenticated User Registration

_NuClide Research · 2026-06-06_

---

## Summary

Harvard University's analytics infrastructure includes a Langfuse instance with public signup enabled by default. The platform ships with `LANGFUSE_AUTH_DISABLE_SIGNUP=false`, allowing any internet user to create an account and access the analytics dashboard without institutional authorization.

---

## Infrastructure

| Field | Value |
|---|---|
| Hostname | Langfuse instance (location TBD) |
| Port | 3000 (HTTP/Reverse-proxied) |
| Organization | Harvard University |
| Country | United States, Massachusetts |
| Langfuse version | v3.x |

---

## Finding

### F1: SIGNUP_OPEN by Default (HIGH)

The Langfuse configuration ships with `enable_signup: true`, the maintainer's default for frictionless demo deployment. At Harvard, this default persists into production.

**Impact:**
- Any internet user can register an account
- Registered accounts access analytics dashboards
- No institutional rate limiting or approval workflow

---

## Cohort Context

This is part of the broader auth-on-default finding documented in Insight #76 of the NuClide methodology: Langfuse maintains an 88.9% (primary survey) to 87.7% (v3.x specific) signup-open rate across its deployed population. The default is maintainer-culture-driven (demo-first optimization) rather than operator-error-specific.

Harvard's instance demonstrates the pattern holding across institutional deployments where IT teams read the documentation but trust upstream defaults.

---

## Remediation

```bash
export LANGFUSE_AUTH_DISABLE_SIGNUP=true
systemctl restart langfuse  # or equivalent
```

Alternatively: Use Langfuse Cloud (SaaS tier) with institutional SAML/SSO instead of self-hosted.

---

## Disclosure

- **Discovered:** 2026-06-06
- **Status:** Queued for outreach
- **Recipient:** `informationsecurity@harvard.edu` (verify on harvard.edu IT security page first)

---

## Related

- [[Insight #76]]: Auth-permissive defaults are the cohort norm for demo-first OSS AI/LLM infrastructure
- [[Langfuse Survey 2026-06-06]]: 88.9% population signup-open rate across 900+ hosts
