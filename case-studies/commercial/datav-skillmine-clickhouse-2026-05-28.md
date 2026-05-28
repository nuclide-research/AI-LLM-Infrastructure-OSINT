# DataV / Skillmine Technology — Multi-Party Data Breach via Unauthenticated ClickHouse

**Date:** 2026-05-28  
**Host:** 64.227.166.14:8123 (DigitalOcean, US)  
**Platform:** DataV (datav.in) — no-code AI analytics SaaS  
**Operator:** Skillmine Technology Consulting Private Limited (Mumbai, India)  
**ClickHouse version:** 25.10.1.3832  
**Auth state:** NONE — both users `default` and `datav` have `host_ip: ["::\/0"]` (any IP)  
**Severity:** CRITICAL (financial identity data — PAN numbers, Demat accounts, bank details)  
**Disclosure contact:** info@datav.in / +91 22-41701000 / datav.in/contact-us/

---

## Overview

DataV is a no-code AI analytics and data visualization platform built and operated by Skillmine Technology Consulting Private Limited (Mumbai). The platform allows customers to upload CSV and Excel files, connect SQL databases, run ML predictions, and build dashboards. Per their website, DataV serves organizations across BFSI, healthcare, IT services, automotive, and e-commerce.

Their production ClickHouse backend has no password configured on either user (`default` or `datav`), both accessible from any IP address. The platform is actively serving live customer dashboards — the `datav` application user was running queries at 08:01, 09:04, 11:58, 12:01, 12:03, and 13:40 on the day of discovery. A `SELECT 1` from the `default` user at 15:10 — before our session — indicates prior access by an unknown party.

---

## Technical Surface

| Service | Port | Auth | Notes |
|---------|------|------|-------|
| ClickHouse HTTP | 8123 | **NONE** | Both users, any IP |
| ClickHouse Native | 9000 | **NONE** | Both users, any IP |
| Redis | 6379 | Required | Properly protected |
| PostgreSQL | 5432 | N/A | Not externally reachable |

**Users:**
```json
{"name":"default","host_ip":["::\/0"]}
{"name":"datav","host_ip":["::\/0"],"GRANTS":["S3 ON *.*","full DDL+DML on datav_2_0, prediction_datav_2_0, qa_datav_2_0"]}
```

The `datav` user has `GRANT S3 ON *.*` — ClickHouse can be used as a proxy to read from S3 URIs if cloud credentials are available on the server.

---

## Database Inventory

| Database | Size | Tables | Contents |
|----------|------|--------|----------|
| datav_2_0 | 17.36 GiB | 545 | All customer-uploaded production datasets |
| qa_datav_2_0 | 1.02 GiB | 154 | QA environment — mirrors production structure |
| prediction_datav_2_0 | 33 KiB | 2 | ML prediction outputs |
| default | 214 MiB | ~35 | Cross-dataset correlation tables, backups |

---

## Five Victim Organizations

### Victim 1 — Unknown Mumbai Stock Broker (CRITICAL)

**Table:** `dev_xlg4iv4spmimsftwr9j8`  
**Records:** 7,962 individual clients  
**Source:** `event_dataset: "client_data"`, `event_module: "csv"`

Full KYC (Know Your Customer) client database from a Mumbai-based brokerage or depository participant. 6,617 of 7,962 clients are in Mumbai; Thane, Navi Mumbai, Ahmedabad, Pune round out the remainder.

**Fields exposed for each client:**
- Full name, father's name, gender, marital status
- Date of birth, age
- PAN number (India's permanent tax/financial identity number — 7,942 of 7,962 records)
- Full residential address (multiple fields: street, city, state, PIN code, country)
- Alternate address fields (registered vs. residential)
- Email address
- Phone numbers (residence + mobile)
- Bank account number, bank name, IFSC code, MICR code (6,788 records)
- UCC (Unified Client Code — securities trading identifier)
- DPID + DPAC (Depository Participant ID and Account — Demat account identifiers for NSE/BSE trading)
- Annual income bracket, occupation
- Relationship Manager code and name
- Account opening date, account status, client category

**Sample fields (Branchid: "HO" across all records = Head Office):**
```json
{
  "ClientName": "[name redacted]",
  "PanNumber": "AAIPG****",
  "BirthDate": "1942-02-01",
  "EmailAddress": "[redacted]@gmail.com",
  "bankaccount": "[redacted]",
  "bankname": "BANK OF BARODA",
  "ifsc": "BARB0GOREGA",
  "dpac": 10064566,
  "dpid": "IN301854"
}
```

The combination of PAN + Demat account + bank account + date of birth + full address constitutes a complete financial identity profile enabling identity theft, securities fraud, and unauthorized account access.

---

### Victim 2 — Questlight (ATS/Recruitment Platform) (HIGH)

**Table:** `dev_glyabcv57urx6ovqd27c`  
**Records:** 4,024 submissions, 3,938 unique candidates, 62 client companies  
**Source:** `event_module: "Questlight"`, `event_dataset: "customersubmissions"`

Questlight is a recruitment/staffing platform whose candidate submission data is stored in DataV. This table was actively queried by the DataV application at 12:01 and 13:40 on the day of discovery.

**Client companies with most submissions:**

| Company | Submissions |
|---------|-------------|
| Sony | 1,261 |
| ICICI Bank | 759 |
| NIC (National Informatics Centre) | 278 |
| Essilor India | 187 |
| NPCI (National Payments Corp. of India) | 146 |
| Tesco | 145 |
| Purchasing Power | 111 |
| ICICI Securities | 109 |
| CSB Bank | 63 |
| EY | 43 |
| Wipro | 33 |
| Godrej | 34 |
| MSCI | 27 |
| Dream11 | 6 |
| Amex | 1 |
| Cisco KSA | 1 |

**Fields per candidate:** `applicant_name`, `status` (SUBMITTED/REJECTED/etc.), `job_client_name`, `job_jobId`, `job_jobPositionTitle`, `job_primaryRecruiter_name`, `job_businessHead_name`, assigned recruiter names (up to 10), `sourceProfile_name`, `createdAt`, `remarks`

Candidates who applied to ICICI Bank, NPCI, and NIC (the government body running India's digital infrastructure) have their application records and current stage exposed.

---

### Victim 3 — Insight Cosmetics — Distribution Intelligence (MEDIUM)

**Table:** `localhost_l4j2amsi5xvzcj463cve`  
**Records:** 383,796 orders  
**Source:** `Product Division: "Insight Makeup Essential"`, `event_module: "xlsx"`

Field sales and distribution data for **Insight Cosmetics** (Indian beauty brand), specifically their East India distribution network.

**Scope:**
- 188 named sales representatives
- 564 named distributors with phone numbers
- ₹11,691,2017 (~₹11.7 crore / ~USD 140K) total GMV
- FMCG distribution orders: SKU code, variant, quantity, order value, client name, beat/territory

Distributor phone numbers and sales employee names create a complete field sales intelligence database.

---

### Victim 4 — Unknown Company, Infor LN ERP (MEDIUM)

**Table:** `dev_hg4dy9h2odct6lchc3uw`  
**Records:** 2,670,000 rows  
**Source:** `event_module: "mssql"`, `event_database: "Reporting_POC"`

Warehouse inventory and shipment data ingested from a Microsoft SQL Server Reporting_POC database, structured in Infor LN (formerly Baan) ERP field naming conventions (`t_bpid`, `t_orno`, `t_shpm`, `t_cwar`, etc.).

**Data class:** Warehouse receipts, order numbers, shipment IDs, item codes, warehouse codes, quantity on hand, business partner IDs, user login codes, timestamps. 2.67 million rows of operational supply chain data.

---

### Victim 5 — Skillmine Technology — Employee HR/PIP Records (HIGH)

**Tables:** `correlation_f4sv4esmzd7xbnzxr8ay`, `correlation_g5yaab59zv9f6jns3gf9`  
**Source:** `event_module: "23r"`, `localhost_26eboajtayxl7uj32gle_*` columns

Skillmine's own employee Performance Improvement Plan records. The operator is simultaneously a breach victim.

**Fields:** Full name, work email (@skill-mine.com), Indian mobile number, employee code, grade (WL 1.4), designation (Incident Manager, Team Lead), department (ICICI, ICICI-ITCC), branch (Bangalore, Hyderabad), business unit, employment type/status, reporting manager name, `pip_reason_tag` ("Unsatisfactory performance"), `expected_standards` ("Performance drop", "Code of conduct breach"), `reason_of_pip/target_area`, PIP start/end dates, approval chain, `request_status` (Approved/Pending), names of all approvers in the pending chain.

PIPs are confidential disciplinary proceedings. These records identify specific named employees by company email and mobile number alongside the reason they are being performance-managed.

Skillmine's clients include ICICI Bank (the department codes ICICI and ICICI-ITCC confirm this). Employees in the ICICI ITCC (IT Command Center) team are represented in the data.

---

### Additional Data Classes (Partially Identified)

**Logistics correlation table** (`correlation_thkt5rp2s7ubqkupu2gc`): Shipment records with Destination (Pune), Cost, Weight (KG), Volume (m³), Status (Delayed), Shipment Date. Cross-correlated with CSV data.

**HR/workforce correlation** (`correlation_dmuwbs8vbvvaufjvj243`): EmpID, Role (Data Scientist), Department, Location — joined HR dataset from `.xlsx` source.

**ML feature tables** (7.39M, 5.14M, 5.08M, 4.18M rows): 50-column float feature vectors from customer CSV uploads. Data class unidentifiable without column names; may contain financial, operational, or behavioral data.

**QA environment** (`qa_datav_2_0`, 1 GiB, 154 tables): Mirror of production with the same customer datasets.

---

## Active Platform Use — Live Production

The `datav` user's query log confirms the platform was actively serving live customer dashboards at the time of discovery:

```
[13:40:48] datav | SELECT `VSKUCode` AS xAxis_0, count() AS doc_count, 
                    sum(`Order Value`) AS yAxis_0 FROM datav_2_0.localhost_l4j2amsi5xvzcj463cve 
                    GROUP BY xAxis_0 ORDER BY...
[12:01:56] datav | SELECT `Address2` AS xAxis_0, count() AS doc_count, 
                    sum(`kycNo`) AS yAxis_0 FROM datav_2_0.dev_xlg4iv4spmimsftwr9j8 
                    GROUP BY xAxis_0 ORDER BY...
```

The KYC table was being actively used in a production dashboard at 12:01. The Insight Cosmetics data was serving a live dashboard at 13:40. These are not stale test datasets.

---

## Prior Unattributed Access

The `system.query_log` shows `SELECT 1` executed by the `default` user at **15:10** — approximately 97 minutes before our session began at 16:47. This query was not from our session. Possible sources:

1. A monitoring/health-check script connected to the database
2. Another researcher or scanner who discovered the open port
3. A DataV internal tool testing connectivity

The query log retention is insufficient to determine if prior data exfiltration occurred.

---

## Regulatory Context

**India DPDPA 2023 (Digital Personal Data Protection Act):** The KYC dataset (PAN numbers, financial account details, full financial identity) and the PIP records (sensitive employment data) are subject to the DPDPA 2023. Unauthorized processing of this data without a valid legal basis constitutes a violation.

**SEBI regulations:** KYC data for securities trading clients (UCC, DPID, DPAC) is governed by SEBI's KYC Registration Agency (KRA) framework. Exposure of this data may trigger mandatory breach notification to SEBI.

---

## Remediation

1. **Immediate:** Set `CLICKHOUSE_PASSWORD` for both `default` and `datav` users
2. Restrict `host_ip` to internal CIDR (server's local network) for both users
3. Close ports 8123 and 9000 to public internet; bind to loopback or internal interface
4. Audit `datav` user's S3 grant; revoke or scope to specific buckets
5. Notify affected customers (stock broker, Questlight, Insight Cosmetics) of the exposure
6. Assess `system.query_log` for prior access by the 15:10 `default` user
7. Consider SEBI and DPDPA breach notification obligations for the KYC dataset

---

## Disclosure Recipients

| Organization | Contact |
|-------------|---------|
| DataV / Skillmine (operator) | info@datav.in / +91 22-41701000 |
| Unknown stock broker | Attributable via client IDs — Skillmine to route |
| Questlight | Via datav.in disclosure — Questlight to be notified |
| Insight Cosmetics | Via datav.in disclosure |
