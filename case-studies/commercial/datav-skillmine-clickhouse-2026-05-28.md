# DataV / Skillmine Technology — Multi-Tenant Analytics Platform, PII Exposed

**Date:** 2026-05-28  
**Host:** 64.227.166.14:8123 (DigitalOcean, US)  
**Platform:** DataV (datav.in) — no-code AI analytics SaaS  
**Operator:** Skillmine Technology Consulting Private Limited  
**Version:** ClickHouse v25.10.1.3832  
**Auth state:** NONE — full SQL access, default user ::\/0 (any IP)  
**Severity:** HIGH (PII — employee HR records, multi-tenant customer data)  
**Disclosure contact:** info@datav.in / +91 22-41701000

---

## Overview

DataV is a no-code AI analytics and data visualization platform built by Skillmine Technology Consulting Private Limited (Mumbai, India). The platform allows customers to upload CSV files, store datasets in ClickHouse, run ML predictions, and build dashboards. Per their website, DataV is used by organizations across BFSI, healthcare, IT services, automotive, and e-commerce sectors.

Their production ClickHouse backend at `64.227.166.14:8123` has no password set on the `default` user and allows connections from any IP address. The `/play` browser SQL interface is publicly accessible. All customer data across all tenants is co-resident in the same unauthenticated database.

The situation has an additional dimension: Skillmine's own employee HR data is stored in the platform they operate — the operator is simultaneously the breached party.

---

## Stack Profile

| Service | Port | Auth |
|---------|------|------|
| ClickHouse HTTP | 8123 | **NONE** |
| ClickHouse Native | 9000 | **NONE** |
| Redis | 6379 | Auth required |
| PostgreSQL | 5432 | Not externally accessible |
| SSH | 22 | Standard |

Only ClickHouse is exposed without authentication.

---

## Database Structure

| Database | Size | Tables | Contents |
|----------|------|--------|----------|
| datav_2_0 | 17.36 GiB | 545 | Customer-uploaded datasets (UUID-named tables) |
| qa_datav_2_0 | 1.02 GiB | 154 | QA environment — same structure |
| prediction_datav_2_0 | 33 KiB | 2 | ML prediction outputs |
| default | 214 MiB | ~35 | Correlation analysis tables, backups |

Total exposed: ~19 GiB of customer data across all tenants.

---

## Tenant Data Model — UUID Isolation Without Auth

Each customer dataset gets a ClickHouse table with a randomized UUID-suffix name:
- `localhost_fc3vsgwc6pxlmg5zbezr` (7.39M rows, 2.70 GiB)
- `dev_ymbhyu4akrypqv34h7oy` (5.14M rows, 1.88 GiB)
- `dev_jk7ykpqriawweq9i7eqt` (5.08M rows, 1.51 GiB)

The naming convention (`localhost_*` for primary workspace, `dev_*` for dev environments) provides no security — all tables are co-resident in a single unauthenticated database. Any user with HTTP access to port 8123 can query any tenant's data via `SHOW TABLES FROM datav_2_0` and then `SELECT * FROM datav_2_0.<table>`.

The primary feature store schema: `id` (Int64), `x_1` through `x_50` (50 Float64 feature columns), `event_module`, `event_dataset`, `@timestamp`. Customer CSVs are parsed into float features for ML processing.

---

## PII Finding — Skillmine Employee HR Records

The `correlation_f4sv4esmzd7xbnzxr8ay` table in the `default` database contains **Skillmine Technology's own employee performance management records** — the company that operates DataV is storing its own HR data in its own unprotected database.

**Exposed fields:**
- Full name, first name, last name, middle name
- Work email address
- Mobile phone number
- Employee code
- Department, sub-department, grade, designation, level
- Business unit, branch, sub-branch, region
- Employment type, employment status
- Reporting manager
- Performance Improvement Plan (PIP) data:
  - `pip_reason_tag` — reason for PIP (e.g., "Unsatisfactory performance")
  - `expected_standards` — "Performance drop", "Code of conduct breach"
  - `reason_of_pip/target_area`
  - PIP start date, end date
  - `1_on_1_meetings_planned`
  - `request_status` — "Approved", "Pending"
  - Approver name, approver remark
  - `pending_with` — chain of approvers

**Sample record (representative — actual personal data redacted in publication):**
- Company: Skillmine Technology Consulting Private Limited
- Department: ICICI (ICICI Bank-related ITCC team)
- Grade: WL 1.4 / Senior Associate
- Designation: Incident Manager / Team Lead IT Command Center
- PIP reason: "Performance drop & Code of conduct breach"
- PIP status: Approved
- Work email: [name]@skill-mine.com
- Mobile: Indian mobile number (10 digits)

PIP records are among the most sensitive HR data categories — they document ongoing disciplinary proceedings against named employees. These records include the names of approvers, pending signatories, and the complete chain of performance management decisions.

This data is likely governed by India's Digital Personal Data Protection Act (DPDPA) 2023. Its exposure in an unauthenticated production database is a compliance violation.

---

## ATS Data — Prediction Database

The `prediction_datav_2_0.demo_74rnrysrqz5urojmmtqp` table (435 rows) contains Applicant Tracking System (ATS) candidate records labeled `ATS_DataV_UseCase_Sample`:

**Fields:** `Candidate_ID`, `Candidate_Name`, `Gender`, `Job_Role`, `Location`, `Recruiter`, `Source`, `Current_Stage`, `Applied_Date`, `Stage_Updated_Date`

**Sample record:**
```json
{
  "Candidate_Name": "James Hanson",
  "Current_Stage": "Applied",
  "Gender": "Other", 
  "Job_Role": "Product Manager",
  "Location": "Bangalore",
  "Recruiter": "B. Patel",
  "Source": "LinkedIn"
}
```

435 candidate records including names, gender, job role, current application stage (Applied/Rejected/Joined), and recruiter attribution. Labeled as demo/sample data but contains personal information.

---

## S3 Access via datav User

The `datav` application user has `GRANT S3 ON *.* TO datav` — permission to use ClickHouse's S3 table function to read from and write to S3 buckets. Combined with `::\/0` (any-IP) access on both the `default` and `datav` users, an attacker could:

1. Use ClickHouse as a proxy to read S3 URIs: `SELECT * FROM s3('s3://bucket/path', 'csv')`
2. If AWS credentials are configured on the server (instance role or environment variables), exfiltrate data from the platform's S3 storage tier
3. Write arbitrary data to configured S3 buckets

---

## Users with Zero IP Restriction

```json
{"name":"default","host_ip":["::\/0"],"host_names":[]}
{"name":"datav","host_ip":["::\/0"],"host_names":[]}
```

Both users can authenticate from any IP on both HTTP (8123) and native TCP (9000). Port 9000 is confirmed open. No brute-force protection observed on the HTTP interface.

---

## Impact

**Multi-tenant data breach:** All DataV customers' uploaded datasets are accessible to anyone who queries port 8123. The UUID-based table naming provides no protection — table names are enumerable via `system.tables`.

**Employee PII and HR disciplinary records:** Real Skillmine employees' performance management data including PIP reasons, mobile numbers, work emails, and approver chains. This data has heightened sensitivity — PIPs are confidential disciplinary proceedings.

**Operator/victim identity:** Skillmine built DataV and operates the platform. Their own HR data is in their own misconfigured database. The security posture of the product they sell is demonstrated by how they manage their own data.

**S3 lateral movement:** If the ClickHouse server has cloud credentials (instance role or envvar), the S3 grant on the `datav` user creates a lateral movement path to the platform's storage tier.

---

## Remediation

1. Set `CLICKHOUSE_PASSWORD` for both `default` and `datav` users immediately
2. Restrict `host_ip` to `127.0.0.1` or internal CIDR for both users
3. Close ports 8123 and 9000 to public internet; bind to internal interface only
4. Audit S3 access credentials on the server; remove or scope-restrict the S3 grant
5. Rotate any credentials that may have been accessible via `system.environment`

---

## Disclosure

**Contact:** info@datav.in  
**Phone:** +91 22-41701000  
**Address:** Level 2, Imperium Building, Vijaynagar, Marol, Andheri East, Mumbai – 400059
