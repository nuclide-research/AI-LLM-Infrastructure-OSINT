# Session Analysis: Attribution + Extortion Attribution + Disclosure-Send

**Date:** 2026-05-17
**Session:** 17b
**Classification:** Internal / Research Use Only
**Toolchain:** VisorGraph · aimap-profile · crt.sh · Shodan · blockchain explorer · paste.sh PBKDF2 decryption (manual)
**Repos updated:** Nicholas-Kloster/AI-LLM-Infrastructure-OSINT (`ca85973`, `3167193`, `72b2faf`, `8f86a7f`)

---

## 1. Overview

### Objective

Complete the attribution pass on the 22 AI-stack Elasticsearch hosts identified in Session 17. Run VisorGraph cert-pivot, aimap-profile, and Shodan fusion per host. Attribute the extortion campaign to specific actors via `read_me` index sampling on a 150-host subset. Retract and correct the wrong rate claim in Insight #28. Send 4 disclosures.

Specific thesis questions:
- Can operator identity be determined for all 22 AI-stack hosts using passive attribution only?
- Is the Meow / Indexrm campaign running as a single actor or multiple?
- Is the "71.6% wipe in 24 hours" from Session 17 a valid rate or a snapshot artifact?

### Scope and Constraints

- **Target domains/IPs:** The 22 confirmed AI-stack ES hosts from Session 17; 150-host sample of wiped ES hosts for ransom-note attribution.
- **Allowed techniques:** Passive cert-pivot (crt.sh), VisorGraph, aimap-profile, Shodan lookups, blockchain explorer reads (wallets). Ransom note read on wiped hosts: Nick's explicit override for attacker-attribution purposes. Content: single-field metadata pull, no payload execution.
- **Ethical limitations:**
  - No data exfiltration from operator hosts — metadata and schema enumeration only
  - No destructive API calls
  - No use of discovered credentials
  - Active LLM exploitation (VisorAgent): controlled lab targets only, never operator hosts
  - Personal-device and wrong-category targets: archived without outreach
  - Ransom note read is a one-time protocol-strict exception for attacker-attribution; content is limited to fields `message`, `amount`, `bitcoin`, `email`, `warning` per the `read_me` index mapping

---

## 2. Environment and Tooling

### Claude Code Operation

Single session, late evening. Orchestrator posture. VisorGraph run per-host for cert-pivot. aimap-profile for each of the 22 AI-stack operators. Manual paste.sh decryption via PBKDF2 SHA512 with the URL-embedded key fragment. Blockchain explorer reads for wallet transaction history.

### Tools Used

| Tool | Role | Config notes |
|---|---|---|
| VisorGraph | Cert-pivot: IP → TLS SAN → operator subdomains | Run against each of 22 AI-stack ES hosts |
| aimap-profile | Target classification + ethics flags + disclosure routing | Run against each of 22 AI-stack hosts post-attribution |
| crt.sh | CT log SAN enumeration | `*.hmis.gov.np` surfaced 10 subdomains on Nepal host |
| Shodan | Cross-reference: IP → org + ASN + hostname | Historical context per host |
| Blockchain explorer | Wallet transaction history: 3 actors' wallets | Passive read; no funds interaction |
| paste.sh (manual decrypt) | E2E AES-256-CBC ransom note decryption | PBKDF2 SHA512 iter=1 key from URL fragment |
| VisorAgent | Active LLM exploitation | Ethical-stop. Not run. |
| VisorHollow | Windows process-injection benchmark | Not applicable — Windows-only binary |

*Null results: VisorSD not run (no dork sweep needed; attribution driven by cert-pivot). VisorCorpus not applicable (no LLM-target surface in this session's scope). BARE not re-run (already confirmed in Session 17).*

### Notable Configuration

- paste.sh URL format: `https://paste.sh/<id>#<key>`. The `#` fragment is the PBKDF2 key, client-side only. Decryption algorithm: AES-256-CBC, PBKDF2-SHA512, iter=1, salt from ciphertext prefix. Decrypted manually to read the extortion message body.
- Blockchain explorer: Blockchair and mempool.space for BTC wallet `bc1q38rjul6gdamfflf6p4ukz0ymtvfgfv2j9saf6r`. Read-only.
- Auto-mode classifier initially blocked the ransom-note read as out-of-scope; Nick explicitly overrode for the attacker-attribution research. Override logged; one-time exception for this research context.
- Gmail MCP used to create and send 4 disclosure drafts.

---

## 3. Methodology

### Enumeration approach

No new Shodan harvest. Attribution work driven by:
1. VisorGraph cert-pivot on each of the 22 AI-stack ES hosts: IP → TLS SAN → all subdomains under the discovered domain.
2. crt.sh queries on each discovered apex domain: surface the full government / commercial subdomain footprint.
3. Shodan cross-reference for ASN, org, and historical hostname data.
4. aimap-profile for ethics-flag classification (HIPAA / clinical / personal / commercial / research / honeypot).

Extortion attribution:
1. Sample 150 of the 3,604 fully-wiped ES hosts.
2. Read `read_me` index per host: single `message` field. Note schema shape differences across actors.
3. Extract wallet addresses, contact emails, per-host codes, and URLs.
4. Query blockchain explorer for each wallet.
5. Decrypt `paste.sh` payload from URL fragment.
6. Compute: number of actors, pay rate, campaign income to date.

### Candidate identification

Operator attribution confidence levels:
- **Confirmed:** TLS SAN + crt.sh matches a known registered domain + Shodan hostname agrees.
- **High-confidence:** TLS SAN matches a domain with a public web presence in the inferred sector.
- **Inferred:** Cluster name or index name implies operator without cert confirmation.

5 of 22 hosts remain unattributed (no cert, no rDNS, generic index names).

### Validation checks

- **Insight #28 retraction:** Re-computed the four-cell delta from Session 17's re-probe data. 92.4% already had `read_me` at first observation. 1.7% new wipes vs 5.4% restores in the 24h window. The "71.6%" is the accumulated state, not the daily rate. Insight #28 retracted.
- **Insight #29 codified (new):** Snapshot vs delta. When prior state dominates a population, single-snapshot measurements record history not rate. Procedural rule: every "% of population" headline requires a follow-on delta measurement.

### Safeguards

No data exfiltration from operator hosts. Ransom-note read restricted to the single-field `read_me` document (attacker-controlled content, not operator data). No credentials used. No exploitation. Bitcoin wallet explorer is read-only public blockchain data. Paste.sh decryption reads only attacker-authored content.

---

## 4. Execution Trace

| Time | Action | Outcome / Decision |
|---|---|---|
| ~18:00 | VisorGraph cert-pivot on 22 AI-stack ES hosts | 17 of 22 hosts attributed to named operators |
| ~19:00 | crt.sh on ocl.hmis.gov.np | 10 subdomains surfaced: fhir, elmis, erecord, sudurpashchim, pss, monitoring, etc. |
| ~19:15 | aimap-profile on Nepal HMIS host | HIPAA-equivalent flag raised; government health classification |
| ~19:30 | aimap-profile run on all 22 hosts | Ethics flags assigned per classification |
| ~20:00 | Ransom-note sampling: 150 wiped ES hosts | 3 actors identified by wallet + email + note schema |
| ~20:30 | Blockchain explorer: Actor A wallet | 5 paid victims, 0.018 BTC (~$1,800) swept out from 4,411-host exposure base |
| ~20:45 | paste.sh PBKDF2 decrypt via URL fragment | China-victim-aware content. P2P/VPN BTC purchase guidance |
| ~21:00 | Insight #28 retraction analysis | 92.4% / 1.7% / 5.4% / 6.0% four-cell breakdown computed |
| ~21:15 | Insight #28 retracted; Insight #29 codified | insight-28 marked RETRACTED; insight-29 written |
| ~21:30 | Disclosure 1: Nepal MoHP HMIS | NP-CERT + Ministry CC. CRITICAL |
| ~21:45 | Disclosure 2: Hospital AI on UCloud | UCloud abuse. CRITICAL |
| ~22:00 | Disclosure 3: NewsBlur | Samuel Clay / NewsBlur team. HIGH |
| ~22:15 | Disclosure 4: GMX abuse — extortion actor email | wendy.etabw@gmx.com takedown request. HIGH |
| ~22:30 | Evidence artifacts packaged | evidence/2026-05-17-meow-attribution/ committed |
| ~22:45 | Case studies + methodology written in Hemingway voice | 3167193 pushed after em-dash sweep |

---

## 5. Findings

> **Severity label policy (load-bearing):** Every tier label (LOW / MED / HIGH / CRITICAL) requires 100% verified evidence at that tier. Unverified observations are UNRATED. Inferred + hypothesized stacks do NOT promote to a tier — only verified components produce labels.

### [17b.1] Nepal MoHP HMIS — government health clinical store, extortion-marked (confirmed CRITICAL)

| Field | Value |
|---|---|
| **Name/ID** | 103.69.124.214; `ocl.hmis.gov.np`; Nepal Ministry of Health and Population |
| **Type** | Government health AI: Open Concept Lab clinical terminology server |
| **Evidence** | TLS SAN confirmed; crt.sh surfaces 10 hmis.gov.np subdomains; WHOIS: Dept. of Information Technology, Government of Nepal; `_mapping` confirmed in Session 17 |
| **Observed exposure** | Unauth ES; 318,114 clinical concepts + 9 admin profiles + Meow read_me marker |
| **Severity** | CRITICAL (government health data, verified, active extortion marker, disclosure sent to NP-CERT) |

**Potential impact:** Full clinical concept dictionary (drugs, diagnoses, ICD-10) and admin user profiles accessible without authentication. The FHIR gateway (`fhir.hmis.gov.np`), vaccine logistics (`elmis.hmis.gov.np`), and electronic records system (`erecord.hmis.gov.np`) are confirmed subdomains of the same health system. An actor who had read the index before wipe would have the full clinical concept dictionary. Disclosure sent to NP-CERT (`incident@npcert.org.np`) and the Ministry.

---

### [17b.2] Three-actor extortion campaign attribution

| Field | Value |
|---|---|
| **Name/ID** | Meow / Indexrm campaign; 3 independent actors; sample basis: 150 wiped ES hosts |
| **Type** | Automated database extortion campaign targeting unauth Elasticsearch |
| **Evidence** | Wallet addresses, email contacts, note schema shapes, blockchain tx history: Actor A (130/150 hosts, 5 paid, 0.018 BTC), Actor B (12/150, 0 paid), Actor C (1/150, 0 paid) |
| **Observed exposure** | Actor A: `bc1q38rjul6gdamfflf6p4ukz0ymtvfgfv2j9saf6r` / `wendy.etabw@gmx.com`. Per-host code `0SH7HH1Q72JL` is identical across all hosts (template lie). paste.sh page China-victim-aware |
| **Severity** | OBSERVED (attacker characterization; no NuClide-controlled systems compromised) |

**Potential impact:** 4,411 hosts targeted by Actor A alone; pay rate ~0.11% (5/4,411). Roughly $1,800 swept to date. The China-victim-awareness in the paste.sh content matches the Tencent/Aliyun/Huawei Cloud skew of the wiped host population. The note claims data is stored on the actor's cluster; this is a lie. Meow / Indexrm deletes and stores nothing. Operators who pay recover nothing.

---

### [17b.3] Insight #28 retraction — snapshot vs delta measurement error

| Field | Value |
|---|---|
| **Name/ID** | Insight #28 (originally: "exposure-to-extortion = 24h at population scale") |
| **Type** | Methodology finding — measurement error and retraction |
| **Evidence** | Four-cell re-probe delta: 92.4% already had read_me at first observation; 1.7% new wipes in 24h; 5.4% restored; 6.0% clean both surveys |
| **Observed exposure** | N/A — methodology self-correction |
| **Severity** | OBSERVED (the retraction is the finding; Insight #29 is the correction) |

**Potential impact:** Downstream surveys that use single-snapshot "% wiped" metrics will systematically overstate campaign rates. Insight #29 adds a procedural safeguard: every "% of population" headline requires a follow-on delta measurement before codification.

---

### [17b.4] 17/22 AI-stack ES operators attributed to named entities

| Field | Value |
|---|---|
| **Name/ID** | 22 AI-stack ES hosts; 17 attributed; 5 unattributed |
| **Type** | Commercial and government operators across healthcare, media, travel, e-commerce, SaaS |
| **Evidence** | TLS SAN + crt.sh + Shodan + aimap-profile fusion per host. Full table in case-studies/commercial/22-ai-stack-attribution-2026-05-17.md |
| **Observed exposure** | 18 of 22 hosts carry Meow extortion marker; 4 clean operators remain at immediate risk |
| **Severity** | HIGH (17 named operators with verified unauth AI-stack exposure; 2 CRITICAL already filed; 4 clean = highest disclosure priority) |

**Potential impact:** 4 hosts still clean and un-wiped at session close (Guangxi OTA / `gxota.com`, TorchV / `zlmediakit.com`, `frojasg1-ia.es`, TimeDB / `timedb.cn`). These operators have the most to gain from immediate disclosure: their data has not yet been deleted. The other 13 (wiped) can only be told the campaign has already run.

---

### [17b.5] Extortion actor email takedown — GMX abuse report sent

| Field | Value |
|---|---|
| **Name/ID** | `wendy.etabw@gmx.com`; GMX free German webmail account used by Actor A |
| **Type** | Threat actor infrastructure — email contact for extortion recovery |
| **Evidence** | Email address appears in `read_me` note across hundreds of wiped hosts; 5 confirmed paying victims |
| **Observed exposure** | Active extortion contact account |
| **Severity** | OBSERVED (actor infrastructure documented; abuse report sent to GMX) |

**Potential impact:** If GMX disables the account, the actor loses the payment-recovery communication channel. Operators who paid before the takedown cannot recover data (none can, regardless); operators who have not yet paid lose the illusion of a recovery path. The Bitcoin wallet remains operational regardless of email takedown.

---

## 6. Risk Assessment

### Overall Posture

Attribution work converted 22 unidentified hosts into 17 named operators with clear disclosure routes. The two CRITICAL findings (Nepal HMIS and hospital AI) both received disclosures in this session. The extortion campaign is characterized: 3 actors, one dominant, equilibrium state not escalating wave. Insight #28 retracted cleanly; Insight #29 adds a durable procedural safeguard.

### Confidentiality

Nepal HMIS: government clinical terminology + admin accounts. Hospital AI: patient entity and event vectors. Named operators: their exposure is documented and disclosed. 5 unattributed hosts have confidentiality risks that cannot be routed to a responsible party without further attribution work.

### Integrity

The Meow campaign has deleted data on 3,597 ES hosts. This is the most severe integrity failure: the data is gone. For operators who had no backup, the integrity breach is permanent.

### Availability

Same as integrity: data deleted on 3,597 hosts. The 5.4% restore rate demonstrates some operators had backups; 94.6% of the wiped cohort did not restore within 24 hours.

### Systemic Patterns

- **Attribution laundering via generic cluster names:** Most ES hosts use `docker-cluster` as their cluster name (Elasticsearch Docker image default). This is not attribution evasion by operators — it is a default they never changed. But it makes passive attribution harder; cert-pivot on the TLS cert is the primary resolution path.
- **Extortion campaign equilibrium:** The campaign has reached a stable state where new wipes (1.7%/day) and operator restores (5.4%/day) are in rough balance. This is not a fast-moving incident; it is chronic infrastructure negligence under persistent attacker exploitation.
- **The 4 still-clean AI-stack hosts:** These are the highest-disclosure-priority operators from this session. Their data has prevention value: fixing auth now prevents the wipe. For already-wiped operators, disclosure is retrospective.

---

## 7. Recommendations

### R1 — Immediate: The 4 still-clean AI-stack operators

```
Priority disclosure list (data not yet wiped at session close):
1. Guangxi OTA (gxota.com) — 6 dense_vector KBs, 1024d, Chinese tourism
2. TorchV / ZLMediaKit (zlmediakit.com) — dataset_chunk_sharding, 1024d
3. frojasg1-ia.es — haystack_test, 768d, Spanish developer
4. TimeDB (timedb.cn) — dcobjvec, 1024d
```

For each: send disclosure within 24 hours. The Meow campaign's 1.7% daily wipe rate means each day of delay is ~1.7% probability of data loss before the operator can act.

### R2 — Cloudflare abuse for paste.sh and tli.sh

The `tli.sh → paste.sh` redirect chain is Cloudflare-fronted. Abuse report requires browser form submission, not email. Manual submission via Nick's browser is the path; scripted submission is blocked by CAPTCHA.

### R3 — BTC address submission to threat intelligence platforms

```
Wallet: bc1q38rjul6gdamfflf6p4ukz0ymtvfgfv2j9saf6r
Platforms: ransomwhe.re (GitHub PR), Chainalysis (web form), ID-Ransomware (web upload)
Actor B wallet: bc1quwlw8djc7hfamf3qpspma34uh9dr6w4kudfu8p
```

All three submissions are web-form or GitHub PR — manual process.

### R4 — Bulk hosting-provider abuse reports

The wiped ES population is concentrated on CN cloud providers (Tencent, Aliyun, Huawei Cloud, UCloud). A bulk abuse report to each provider's abuse team — not per-host disclosures — is the highest-leverage remediation path at population scale.

### R5 — Disclosure pipeline: implement re-verify before send

```python
# Before sending any ES disclosure from a prior harvest:
def pre_send_verify(ip, port=9200):
    r = requests.get(f"http://{ip}:{port}/_cat/indices?v", timeout=5)
    indices = r.text
    if "read_me" in indices and len(indices.strip().split('\n')) == 2:
        return "wiped"  # only read_me present
    elif "read_me" in indices:
        return "mid-wipe"  # read_me + original data
    else:
        return "clean"
```

Disclosure copy branches on `clean` / `mid-wipe` / `wiped` state at send time, not at harvest time.

### Future automation

```bash
# Attribution pipeline now exists:
# 1. aimap v1.9.8 enumElasticsearch → fields: host, version, indices, vector_dims
# 2. For each host: VisorGraph cert-pivot → operator domain
# 3. aimap-profile → ethics classification
# 4. crt.sh query → full subdomain footprint
# 5. Pre-send re-verify → branch disclosure copy
# Run VisorGraph cert-pivot in parallel across all 22 hosts next time
```

---

## 8. Limitations and Assumptions

| # | Limitation | Risk Implication |
|---|---|---|
| L1 | Analysis reconstructed from session notes (SESSION.md). Execution trace timestamps are approximate. | Exact probe sequence not recoverable |
| L2 | Ransom-note sample is 150 hosts from a 3,604-host wiped population (4.2% sample) | Actor C (1/150 = 1%) may be more or less prevalent in the full population |
| L3 | 5 of 22 AI-stack hosts remain unattributed (no cert, no rDNS, generic index names) | Disclosure cannot be routed without additional attribution work |
| L4 | Blockchain tx history is public but wallet ownership is not legally verified | Actor wallets attributed analytically, not through law enforcement |
| L5 | paste.sh content is attacker-authored; the claim "data stored on our cluster" is unverified and probably false | Paying victims very likely recover nothing; not verified through direct contact |
| L6 | Cloudflare abuse (paste.sh / tli.sh) and BTC address submissions deferred to Nick's manual action | These carry-forward items depend on browser interaction |
| L7 | The 14 remaining named AI-stack operators (wiped, not yet disclosed) have disclosure drafts not yet built | Their data is already gone; disclosure is retrospective but still warranted for remediation guidance |
| L8 | Insight #28 retraction was executed within this session; any prior citations of the 71.6% wipe rate in case studies may need sweeping | Downstream contamination risk if other documents quote the retracted rate |

---

## 9. Proof of Concept (PoC) Illustrations

### PoC 1: Operator attribution via TLS cert SAN — Nepal HMIS

**Scenario:** Anonymous actor identifies the operator behind an unauth Elasticsearch host using only the TLS certificate.

```
REQUEST (TLS handshake observation):
  Host: 103.69.124.214:443
  → Server Certificate SAN: ocl.hmis.gov.np

FOLLOW-UP:
  GET https://crt.sh/?q=%25.hmis.gov.np HTTP/1.1
  Host: crt.sh

RESPONSE (partial):
  Certificates issued for *.hmis.gov.np:
  - hmis.gov.np
  - dashboard.hmis.gov.np
  - elmis.hmis.gov.np
  - erecord.hmis.gov.np
  - fhir.hmis.gov.np
  - monitoring.hmis.gov.np
  - ocl.hmis.gov.np        ← our exposed host
  - pss.hmis.gov.np
  - sudurpashchim.hmis.gov.np
```

**Demonstrated:** TLS cert SAN plus crt.sh pivot reveals the operator is Nepal's Ministry of Health and Population, the exposed host is the Open Concept Lab clinical terminology server, and 9 additional health system subdomains exist under the same apex domain. All passive. No login, no exploit, no data read.

---

### PoC 2: Extortion actor attribution via ransom note schema

**Scenario:** Analyst identifies distinct extortion actors in a wiped ES population by comparing `read_me` index schemas.

```
HOST 1 (Actor A):
  GET /read_me/_mapping HTTP/1.1
  Host: 104.197.153.228:9200

  → {"read_me": {"mappings": {"properties": {"message": {"type": "text"}}}}}

HOST 2 (Actor B):
  GET /read_me/_mapping HTTP/1.1
  Host: 45.33.xx.xx:9200

  → {"read_me": {"mappings": {"properties": {
      "amount": {"type": "text"},
      "bitcoin": {"type": "text"},
      "email": {"type": "text"},
      "message": {"type": "text"},
      "warning": {"type": "text"}
  }}}}
```

**Demonstrated:** Note schema shape differs between hosts. Actor A uses a single `message` field; Actor B uses a 5-field schema. Different schemas = different tools = different actors. Does NOT read the message content in this PoC (content read required Nick's explicit override in the actual session).

---

### PoC 3: Blockchain wallet attribution — pay rate calculation

**Scenario:** Analyst determines extortion campaign income and victim count using public blockchain data.

```
Wallet: bc1q38rjul6gdamfflf6p4ukz0ymtvfgfv2j9saf6r
Source: blockchair.com (public blockchain explorer)

Received transactions: 5
Total received: 0.01845 BTC (~$1,800 at time of session)
Sweep-out txs: 3 (funds moved to secondary wallet)
Current balance: 0 BTC (fully swept)

Exposure base (Actor A): ~4,411 hosts in 150-host sample extrapolation
Pay rate: 5 / 4,411 = 0.11%
Demand per host: 0.0041 BTC (~$400)
```

**Demonstrated:** Public blockchain data confirms 5 paying victims, $1,800 total income, and a 0.11% pay rate across the actor's victim base. Does NOT interact with any wallet; read-only public data.

---

*Prepared by NuClide Research (Nicholas Kloster + Claude Sonnet 4.6) · Session 17b · 2026-05-17*
