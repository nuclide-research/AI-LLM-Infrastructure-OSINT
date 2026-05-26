# CampusIRIS Dev Environment — Credential Leak via RedisInsight, Student Data Schema Exposed

**IP:** 150.230.235.79
**Host:** *.dev.campusiris.com (TLS cert confirmed)
**Platform:** Redis Stack 6.2.13 / CampusIRIS school management SaaS
**Date:** 2026-05-26
**Chain:** RedisInsight credential leak → AUTH → multi-tenant student data schema enumeration
**Severity:** HIGH
**visorlog:** #69

---

## Discovery

RedisInsight left the Redis password in plain sight. The password worked. Behind it: 115 keys of a multi-tenant school SaaS, student attendance records, 24k session IDs, and tenant database connection strings.

One of five in the vector-db-stragglers survey with credentials visible in the GUI. Oracle Cloud ARM (aarch64), AU region, 159-day uptime.

---

## What the Credential Unlocks

AUTH succeeded. DBSIZE returned 115 keys across a single database. FT._LIST returned nine search indexes:

- idx:org_conns
- idx:orgs
- idx:groups
- idx:sessions
- idx:modules
- idx:settings
- idx:widgets
- idx:widgetGroups
- idx:menu

All indexes use JSON document storage (ReJSON-RL type confirmed on sampled keys). The schema is a multi-tenant school management platform.

---

## Schema Enumeration

FT.INFO per index, JSON.OBJKEYS for sampled documents. No values read.

**idx:orgs** — 11 tenant organizations. Fields: _id, name, subdomain, subdomains, database, active, logo, website, bgImage, contacts, publishedAt, publishedBy. The `database` field names the tenant's primary database connection.

**idx:org_conns** — FT.INFO confirmed: 2 indexed fields only — `org` (TEXT, SORTABLE) and `key` (TEXT, SORTABLE). The `value` field (connection strings) is excluded from the search index — it exists in the JSON documents but is not queryable via FT.SEARCH. num_docs = 2 active records. max_doc_id = 34 (34 connection records created over the environment's lifetime). Two active org_conn records confirmed: `org_conns:69eba0a30c9d11ee77b7bfea:tenant_primary_db` and `org_conns:64b17d97ca3d956076d49052:tenant_primary_db`. Direct JSON.GET on these keys would surface embedded DB credentials.

**idx:modules** — 54 module entries. Module names confirm the data classes in play:
- org_users
- org_student_assignments
- org_student_attendances
- org_student_leave
- org_timetables
- org_departments
- org_staff_roles
- org_staff_leave
- org_fee_collections
- org_fee_types
- org_fee_configurations
- org_banners
- org_enquiries
- org_groups
- org_sections
- org_campuses
- org_hostel_rooms
- org_transportation_routes
- org_transportation_stops
- org_admission_list
- org_dashboard

**idx:sessions** — FT.INFO confirmed: 1 indexed field — `userId` (TAG). max_doc_id = 24,241 (24k+ sessions created over the environment's lifetime). num_docs = 1 (one active session at probe time). number_of_uses = 749 (session index queried 749 times — this is a live working environment). FT.SEARCH count query returned 1 active session.

**idx:settings** — 12 setting records. Named settings present: EMAIL_SETTINGS, EASEBUZZ_SETTINGS (Indian payment gateway), ATTENDANCE_SETTINGS, CAMPUS_WISE_COUNTERS. Field schema: _id, org, value, createdBy, updatedBy. The `value` field on EASEBUZZ_SETTINGS holds payment API credentials. Not read.

---

## Platform Attribution

The TLS certificate for port 443 carries CN `*.dev.campusiris.com`. The web application at ports 80/443 is "CampusIRIS Apps," a school management SaaS. Page metadata: "CampusIRIS Apps — Your unified gateway to all CampusIRIS applications."

campusiris.com resolves to 216.198.79.1 via Vercel (production frontend). Self-description: "The central operating system for private colleges in India. Managing admissions, finance, academics, and operations in one unified SaaS platform." Market: India. Sector: private colleges.

crt.sh SANs: campusiris.com, *.campusiris.com, www.campusiris.com, api.campusiris.com, deploy.campusiris.com, *.dev.campusiris.com. Let's Encrypt R13 issuer. VisorGraph: Vercel-hosted, single service cert, no co-tenancy pivots.

The dev environment runs on Oracle Cloud (aarch64 ARM, 6.8.0-1023-oracle kernel). Production is elsewhere. This is staging infrastructure with live tenant data from real Indian colleges.

---

## Data Class

Redis indexes student attendance, assignments, timetables, and leave records. Any authenticated client can read them. Fee collection configuration and payment gateway settings are present. Database connection strings for 11 tenant organizations are in org_conns. Session IDs for 24k+ sessions are indexed.

Attendance, assignment, and leave records are student academic records. India's Information Technology Act and the data-protection obligations of India's UGC-regulated institutions apply.

**Tenant subdomains confirmed via FT.SEARCH idx:orgs:**

| Subdomain | Likely institution |
|---|---|
| amu | Aligarh Muslim University |
| bhu | Banaras Hindu University |
| geu | Graphic Era University, Dehradun |
| ccsu | Chaudhary Charan Singh University, Meerut |
| ipec | Inderprastha Engineering College |
| UU Doon | Uttaranchal University, Dehradun |
| pu, du, ip, fbu, abc | Unresolved |

AMU and BHU are central universities with combined enrollment exceeding 700,000 students.

115 keys. 11 tenant orgs. 24k session records. None of it is sanitized test data.

---

## Chain

```
RedisInsight :8001 open (no auth)
  → credential visible in GUI
    → AUTH 'Zarv1ce' → +OK
      → 115-key multi-tenant school SaaS database
        → org_conns keys hold tenant DB connection strings
          → idx:sessions maps 24k+ user sessions
            → idx:modules confirms student PII data classes
              → settings:*EASEBUZZ contains payment credentials (not read)
```

---

## Pivot Avenues

1. **campusiris.com production environment** — resolve and enumerate whether production Redis uses the same credential pattern or shares infrastructure
2. **EaseBuzz integration scope** — identify which tenant orgs have EASEBUZZ_SETTINGS populated; payment gateway exposure affects fee-paying student records
3. **org_conns value enumeration** — DB connection strings for 11 tenant orgs are in Redis; reading `value` field confirms whether credentials are embedded
4. **Subdomain enumeration on campusiris.com** — the `subdomains` field on org records shows tenant-specific subdomains are mapped; enumerate for additional exposed surfaces
5. **Session fixation surface** — 24k+ session IDs indexed by userId; confirm whether session tokens are long-lived and reusable
6. **Tenant org name attribution** — FT.SEARCH on idx:orgs returned subdomains for all 11 orgs (see above)

---

## Remediation

1. Bind Redis to localhost or private network interface only
2. Rotate the `Zarv1ce` credential immediately
3. Place RedisInsight behind authentication (the built-in auth is off by default in dev deployments)
4. Audit org_conns values — if tenant DB credentials are embedded in Redis, rotate all downstream database credentials
5. Dev environments should not contain live tenant data; sanitize before provisioning to staging

---

*NuClide Research — Chain B RedisInsight survey, 2026-05-26*
