# Government & Critical Infrastructure — Research Playbook

_Added: 2026-05-28_

---

## Why This Tier Is Different

Government and critical infrastructure targets require a different workflow at every stage. Attribution is harder, disclosure paths are non-standard, and the research record must be cleaner. The chain from discovery to disclosure is longer and the stakeholder on the other end may be a national CERT, not a startup engineer.

This playbook documents the established process so it is repeatable.

---

## Attribution

### IP → Government Operator

Standard operator attribution (cert CN pivot, reverse DNS, org field) works less reliably on government infrastructure. Additional signals:

1. **ASN ownership** — government ASNs are registered to agencies, not ISPs. Look for agency names in ARIN/RIPE org records, not just ISP names.
2. **`.gov` / `.mil` / `.edu` hostnames** — reverse DNS on the IP; if the PTR record points to a .gov domain, that is the operator.
3. **TLS certificate** — CN and SAN fields on the cert. Government certs often use `*.agency.gov` or agency-specific CAs.
4. **WHOIS netblock** — /16 or larger blocks registered to a specific agency. Cross-reference the IP against known government CIDR ranges (ARIN query: `org-name:"Department of" type:NET`).
5. **Shodan org field** — "US Department of", "Department of Defense", "Ministry of", "Gobierno de", etc.

### Critical Infrastructure Attribution

- **ICS/SCADA context signals:** vendor product names (Siemens, Rockwell, Schneider, GE), port patterns (102/Siemens S7, 502/Modbus, 44818/EtherNet-IP), cert names (utility, district, cooperative)
- **Electric utilities:** check NERC CIP registrants against IP; cross-reference with EIA Form-861 reporting entities
- **Water/wastewater:** EPA SDWIS Safe Drinking Water data; cross-reference with AWIA 2018 covered utilities
- **Healthcare:** NPI registry for hospital networks; cross-reference hostnames with hospital name databases

---

## Dork Discipline

Government/critical infrastructure targets warrant tighter dork precision. Do not use coarse dorks (`http.html:"ollama"`) against government IP ranges — the false positive rate is high and unnecessary probing of government systems creates an audit trail without producing useful findings.

**Preferred approach:**
1. Dork first on Shodan **globally** with platform fingerprint
2. Filter results for government indicators in post-processing (`.gov` hostnames, government ASNs, known CIDR ranges)
3. Do not probe government IPs discovered via coarse dorks without first confirming platform identity through a read-only verification probe

**Government-specific Shodan filters:**
- `org:"Department of" product:"LiteLLM"` — agency-operated AI infra
- `hostname:.gov product:"Ollama"` — .gov subdomains
- `net:161.203.0.0/16 port:11434` — specific government CIDR

---

## Verification Standard

Government findings require a higher verification bar than commercial findings before any record is made:

| Step | Commercial | Government / Critical Infra |
|------|-----------|---------------------------|
| Platform identity | Fingerprint match | Fingerprint match + response body + cert SAN |
| Operator attribution | Org field + hostname | Org field + hostname + WHOIS netblock + ARIN registration |
| Data class | Surface assessment | Read-only probe if and only if surface is confirmed open |
| Finding record | Case study with screenshots | Case study + raw probe output + chain-of-custody timestamp |

Do not infer data class from context alone (e.g., "this is a hospital network, therefore PHI is present"). Verify or mark unverified.

---

## Scoping Hard Stops

Stop before proceeding if any of these apply:

- Target is a **defense/ITAR-classified system** — any operator with "Defense", "DOD", "DARPA", "NSA", "DISA", "DIA", "NRO" in the org record
- Target shows **OT/ICS network indicators** — Modbus, DNP3, EtherNet/IP, Siemens S7 responses on any port
- Target has **active incident indicators** — degraded service, anomalous responses suggesting an active compromise already in progress
- Probe would require **authentication bypass** to confirm the finding — read-only unauthenticated probes only

---

## Disclosure Routing

Government disclosure does not go to a security@company.com address. The routing depends on jurisdiction:

### United States
1. **CISA ICS-CERT** — for critical infrastructure (energy, water, healthcare, transportation): submit via `https://www.cisa.gov/report`
2. **US-CERT** — for civilian government agencies: `soc@us-cert.gov`
3. **Agency security contact** — most `.gov` domains have a `security.txt` or `DISA STIG` contact; check `https://<agency.gov>/.well-known/security.txt`
4. **VINCE (CERT/CC)** — for coordinated multi-agency disclosure: `https://kb.cert.org/vince/`

### International
- **EU:** National CERTs via ENISA CERT map; agency-level contact via `security.txt`
- **APAC:** APCERT member CERTs; country-specific (AU: ACSC, JP: JPCERT, TW: TWNCERT)
- **Critical infrastructure operators:** Direct to the operator's PSIRT if one exists; otherwise via national CERT

### Sanitization before disclosure
- Strip cluster-level fingerprinting detail from any CERT submission
- Trim dorks to product-level only (no operator-identifying search strings)
- Hold host-specific detail until acknowledged
- Do not cc: other researchers or post publicly until the CERT confirms notification to the operator

Per `feedback_defense_contractor_disclosure_handling.md` memory: hold cluster-level detail until acknowledged, trim dorks to product-level.

---

## Case Study Template for Government Findings

Unlike commercial case studies, government case studies are held in a sanitized state until disclosure is acknowledged. The draft follows standard format but with:

- Operator section: agency name + jurisdiction only (no specific host or IP until acknowledged)
- Technical section: full detail for our records, redacted in the publishable version
- Disclosure section: CERT ticket number + submission date + acknowledgment date

Publish only after: CERT acknowledgment received AND one of (patch confirmed OR 90-day responsible disclosure window elapsed).
