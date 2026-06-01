# Session Analysis: Swiss ML Training Server Attribution and Disclosure

**Date:** 2026-06-01  
**Classification:** Internal / Research Use Only  
**Toolchain:** Full 19-tool arsenal  
**Repos updated:** AI-LLM-Infrastructure-OSINT

---

## 1. Overview

### Objective

Attribution and full infrastructure mapping of a Swiss-hosted ML training server (185.66.109.62) with an unauthenticated Python SimpleHTTPServer on port 8000 serving the operator's home directory. The session included full operator identification, ecosystem mapping, and same-day coordinated disclosure.

### Scope and Constraints

- **Target:** 185.66.109.62 / velutina-service.ch (single host, operator-provided context)
- **Allowed techniques:** Passive DNS, TLS cert probes, HTTP GET on public-facing surfaces, directory listing enumeration, schema.org / JSON-LD extraction, Gravatar hash verification, public API probing
- **Ethical limitations applied:**
  - No credential retrieval from exposed directories
  - No use of any discovered credentials (GCP, SSH, FTP, Vast.ai)
  - No interaction with active Vast.ai GPU session
  - No Zammad API calls beyond the public `/api/v1/getting_started` endpoint
  - No data exfiltration from training dataset or label exports

---

## 2. Environment and Tooling

### Tools Used

| Tool | Result | Notes |
|---|---|---|
| JAXEN | 5 Shodan records, ports [22,80,443,5000,8000] | Org: OptimaNet Schweiz AG |
| aimap | 0 findings | Sandbox connectivity; ports confirmed via other means |
| aimap-profile | 0 | Same connectivity issue |
| VisorGraph | cert SAN pivot | scan.velutina-service.ch, api.velutina-service.ch |
| recongraph | 38 nodes / 36 edges | velutina-service.ch cert graph |
| VisorBishop | 0 | Sandbox connectivity |
| VisorSD | 0 | Invocation not successful from sandbox |
| VisorGoose | 0 | Gov/edu TLD scope tool; not applicable |
| menlohunt | Port scan + SSH fingerprint | Ports 22/443/5000 confirmed; Not GCP |
| nu-recon | 0 | Connectivity |
| VisorPlus | 22 passive DNS hostnames | itservicehabluetzel.ch surfaced; GreyNoise: clean |
| VisorLog | 3 findings ingested | F1 CRITICAL, F2 HIGH, F3 CRITICAL |
| VisorScuba | 9/10, BLUE-EXP-001 | Publicly indexed/discoverable |
| BARE | no_high_confidence_match | Top scores 0.438/0.417; first-party config mistake |
| VisorCorpus | N/A | No LLM API surface |
| VisorRAG | 0 prior findings | Target not previously surveyed |
| VisorAgent | [—] ethical-stop | Controlled targets only |
| VisorHollow | [—] | Windows-only, not applicable |
| cortex | N/A | Requires pre-built case study artifact |
| JS-bundle | app.js extracted | 339KB, donation/payment/social URLs, API paths |
| Manual HTTP | Primary discovery surface | Dir listing, TLS probes, schema.org extraction |

---

## 3. Methodology Notes

### Attribution chain depth

This session produced the deepest single-target attribution chain run to date. Seven independent pivot points connected an anonymous Swiss VPS to a named operator with two business lines, a home NAS, a Google account, social media profiles, and a Swiss company registration -- without retrieving any credentials. The pivots in order:

1. JAXEN Shodan → velutina-service.ch
2. TLS cert SAN → scan.velutina-service.ch → HTTP redirect → velutinaportal.eu
3. WordPress Impressum JSON-LD → organization name + address
4. Gravatar SHA256 hash → email confirmed (brute-force over likely addresses)
5. umsiedlungen.ch JSON-LD → mobile phone, Facebook handle
6. YouTube embed in JS bundle → video channel → full name confirmed
7. VisorPlus passive DNS → second business domain → Zammad helpdesk → group email addresses

### Zammad getting_started disclosure

Zammad's `/api/v1/getting_started` endpoint is documented as public (setup wizard use), but in this deployment it returned the full internal group structure including group inbox email addresses. This is a Zammad configuration disclosure: two group mailboxes (`technik@` and `onaxis@`) were returned without authentication. This is not a vulnerability in Zammad itself but a configuration choice with information disclosure consequences.

### Synology NAS on residential IP

The export script contained a hardcoded Label Studio URL pointing to a Swisscom dynamic residential IP (83.76.254.176:8081). That IP's port 80 serves the Synology Web Station default page. The NAS hosted Label Studio for the annotation workflow, connected to the VPS via script. This is a common DIY ML pipeline pattern: home hardware for annotation, cloud VPS for serving/inference, rented GPU for training.

### BARE result interpretation

Both findings scored below the 0.55 no-match threshold (0.438 and 0.417). This confirms there is no Metasploit module that directly covers "unauthenticated Python HTTP server exposing ML training credentials." The finding is a first-party operational error, not a CVE-class vulnerability. This is expected and correct.

### VisorScuba score interpretation

The 9/10 score (only BLUE-EXP-001 fires) reflects that the VisorLog entry was ingested with metadata tags rather than structured platform data. The AI.C1 (unauth service) control did not fire because `classifyService` did not recognize the platform class (SimpleHTTPServer is not in the AI/ML service map). The score is not representative of actual severity. The human-assessed severity is CRITICAL.

---

## 4. Findings Summary

| ID | Severity | Title | Verification |
|---|---|---|---|
| F1 | CRITICAL | SimpleHTTPServer exposes home directory on port 8000 | Inner-B / Outer-1 |
| F2 | HIGH | Werkzeug dev server on port 5000, no auth | Inner-B / Outer-1 |
| F3 | CRITICAL | Credential chain accessible through F1 (GCP, SSH, Vast.ai, FTP) | Inner-A / Outer-1 |

---

## 5. Infrastructure Map (Internal Reference)

Omitted from public case study. See VisorLog nuclide.db for operator identity fields.

---

## 6. Disclosure

- Same-day disclosure via email to operator business contact
- Both German and English in one message
- Commands embedded verbatim (per Insight #5: disclosures with verbatim fixes remediate faster)
- No acknowledgement section (per disclosure structure guidelines)
- Sent via Gmail API pipeline (send_drafts_api.py)

---

## 7. Limitations

- aimap, aimap-profile, VisorBishop, VisorSD: all returned 0 due to sandbox connectivity issues reaching the Swiss VPS. Ports confirmed via JAXEN Shodan records and direct curl probes instead. This does not affect finding confidence.
- VisorScuba score (9/10) understates severity due to platform classification gap for SimpleHTTPServer.
- No Swiss WHOIS data: nic.ch blocks automated queries. Domain registration data was unavailable; attribution relied entirely on web-surface pivots.
- Vast.ai instance status at time of discovery: active (confirmed by current_training_instance.txt metadata). Instance may have been terminated or migrated; not probed.

---

## 8. Artifacts

- `case-studies/commercial/velutina-service-ch-unauth-ml-training-server-2026-06-01.md`
- `recon/velutina-swiss-ml-2026-06-01/findings-breakdown.txt`
- VisorLog nuclide.db: 3 findings, IDs logged (185.66.109.62, Swiss citizen science AI project)
- `disclosures/_gmail_drafts.json`: slug `velutina-service-ch-185-66-109-62-unauth-homedir-2026-06-01`, sent 2026-06-01
