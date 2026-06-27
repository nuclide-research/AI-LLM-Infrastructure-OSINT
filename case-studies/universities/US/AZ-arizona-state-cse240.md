# Arizona State University: Langfuse Unauthenticated User Registration (CSE 240)

_NuClide Research · 2026-06-07_

---

## Summary

Arizona State University's CSE 240 (Computer Science course) infrastructure includes a Langfuse analytics instance. Certificate transparency logs and reverse DNS resolution reveal the instance is course-level infrastructure operated by course staff, not central ASU IT. Langfuse ships with SIGNUP_OPEN enabled; the default persists into production.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 206.206.192.179 |
| Hostname | cse240.com (operator domain via cert pivot) |
| Aliases | api.cse240.com, git.cse240.com (course infrastructure co-located) |
| Organization | ASU CSE 240 course staff |
| Port | 3000 (Langfuse, HTTP/Reverse-proxied) |
| Service | Langfuse v3.x |

---

## Certificate Pivot

`206.206.192.179` resolved via TLS certificate subject CN → `cse240.com`. Further WHOIS/DNS enumeration revealed:
- `cse240.com` → operator-purchased domain (not `*.asu.edu`)
- CNAME records point to course infrastructure domains
- Course staff managing deployment directly, not via ASU central hosting

This is **operator-misdeployment attribution** (course staff, not ASU IT) — remediation path is course-level, not institutional.

---

## Finding

### F1: SIGNUP_OPEN by Default (HIGH)

Langfuse default `enable_signup: true` enables public registration to the course analytics backend.

**Impact:**
- Any internet user can create an account
- Course analytics (student submissions, model outputs, performance data) become readable by unauthorized users
- FERPA-class risk if course materials or student work are exposed via the analytics backend

---

## Remediation

**Course-level fix:**
```bash
export LANGFUSE_AUTH_DISABLE_SIGNUP=true
systemctl restart langfuse
```

**Institutional recommendation:** Route course infrastructure deployment through ASU IT security review before production use.

---

## Disclosure

- **Discovered:** 2026-06-06 (initial Langfuse survey)
- **Refined:** 2026-06-07 (cert-pivot attribution to course staff)
- **Status:** Queued for outreach
- **Recipient:** CSE 240 course department head / CS faculty IT contact (not central ASU CISO)
- **Routing note:** Course-level infrastructure requires course-staff notification, not institutional-IT escalation

---

## Related

- [[Mitnick Pivot Analysis 2026-06-07]]: Certificate-based operator attribution refinement
- [[Insight #76]]: Auth-permissive defaults in demo-first OSS platforms
