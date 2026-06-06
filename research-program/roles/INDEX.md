# NICE Roles — Research Program Mapping

Mapping each NICE Cybersecurity Workforce Framework role (DoD-8140) to the research-program activities it covers. Source PDFs in `~/Documents/dod-cyber-pathways/`. Detail files in this directory contain extracted Core Tasks (T-IDs), KSAs, Competencies, On/Off Ramps, and a research-program-relevance assessment per role.

## Composite primary role (active in current program)

| Role | Function in this program | Detail |
|---|---|---|
| **422 Data Analyst** | Population analysis, ASN/geo enrichment, longitudinal metrics, dataset validation | [422-data-analyst.md](422-data-analyst.md) |
| **541 Vulnerability Assessment Analyst** | Audit-report generation (case studies + breakdowns), finding classification, verification stage | [541-vulnerability-assessment-analyst.md](541-vulnerability-assessment-analyst.md) |
| **631 Information Systems Security Developer** | Tool design and testing (herald, aimap, scanner), documented SDLC | [631-information-systems-security-developer.md](631-information-systems-security-developer.md) |
| **661 Research and Development Specialist** | Capability gap analysis, new-tool design, methodology evolution | [661-research-and-development-specialist.md](661-research-and-development-specialist.md) |

## Supporting roles (referenced for specific activities)

| Role | When invoked | Detail |
|---|---|---|
| 461 Systems Security Analyst | Primary disclosure-recipient mirror role | [461-systems-security-analyst.md](461-systems-security-analyst.md) |
| 511 Cyber Defense Analyst | SOC-side / internal-detection mirror to NuClide's external recon | [511-cyber-defense-analyst.md](511-cyber-defense-analyst.md) |
| 521 Cyber Defense Infrastructure Support Specialist | Hardening / IDS-IPS-VPN admin context | [521-cyber-defense-infrastructure-support-specialist.md](521-cyber-defense-infrastructure-support-specialist.md) |
| 531 Cyber Defense Incident Responder | CERT coordination on consolidated disclosures | [531-cyber-defense-incident-responder.md](531-cyber-defense-incident-responder.md) |
| 612 Security Control Assessor | Closest NICE analog to NuClide work (inside-the-boundary SP 800-37 assessor) | [612-security-control-assessor.md](612-security-control-assessor.md) |
| 622 Secure Software Assessor | Source-code review for probe validation against upstream | [622-secure-software-assessor.md](622-secure-software-assessor.md) |
| 651 Enterprise Architect | Tool-family architecture decisions (aimap/scanner/herald separation) | [651-enterprise-architect.md](651-enterprise-architect.md) |
| 652 Security Architect | Defense-in-depth boundaries; multilevel security model context | [652-security-architect.md](652-security-architect.md) |
| 671 System Testing and Evaluation Specialist | Probe validation against Python baselines; T&E discipline | [671-system-testing-and-evaluation-specialist.md](671-system-testing-and-evaluation-specialist.md) |
| 711 Cyber Instructional Curriculum Developer | Case study as teaching artifact; future curriculum from corpus | [711-cyber-instructional-curriculum-developer.md](711-cyber-instructional-curriculum-developer.md) |
| 722 Information Systems Security Manager | Canonical disclosure-recipient role for institutional findings | [722-information-systems-security-manager.md](722-information-systems-security-manager.md) |
| 731 Cyber Legal Advisor | Pre-disclosure legal review (ITAR, OFAC, GDPR jurisdiction) | [731-cyber-legal-advisor.md](731-cyber-legal-advisor.md) |
| 732 Privacy Officer / Privacy Compliance Manager | PII/PHI exposure findings (Phoenix /v1/users) | [732-privacy-officer-privacy-compliance-manager.md](732-privacy-officer-privacy-compliance-manager.md) |
| 752 Cyber Policy and Strategy Planner | Upstream-maintainer disclosure strategy | [752-cyber-policy-strategy-planner.md](752-cyber-policy-strategy-planner.md) |
| 805 IT Program Auditor | T&E/audit discipline analog for verification stage | [805-it-program-auditor.md](805-it-program-auditor.md) |
| 901 Executive Cyber Leadership | High-severity escalation terminus | [901-executive-cyber-leadership.md](901-executive-cyber-leadership.md) |

## Upstream-causes roles (the source-side of the auth-on-default thesis)

These are the roles whose *omissions or oversights* produce the exposures NuClide surveys discover:

| Role | Why upstream | Detail |
|---|---|---|
| 421 Database Administrator | DB-exposure findings come from operator-side admin gaps | [421-database-administrator.md](421-database-administrator.md) |
| 441 Network Operations Specialist | Operates the network plane NuClide enumerates externally | [441-network-operations-specialist.md](441-network-operations-specialist.md) |
| 451 System Administrator | Most common operator behind unauth AI/ML exposures | [451-system-administrator.md](451-system-administrator.md) |
| 611 Authorizing Official | Senior AO who signs ATOs; risk acceptance authority | [611-authorizing-official.md](611-authorizing-official.md) |
| 621 Software Developer | Builds inference servers / agent platforms; **auth-on-default originates here** | [621-software-developer.md](621-software-developer.md) |
| 632 Systems Developer | HW/OS/SW integration; embedded/multilevel-security weight | [632-systems-developer.md](632-systems-developer.md) |
| 641 Systems Requirements Planner | Requirements upstream; **where auth-on-default gets specified or omitted** | [641-systems-requirements-planner.md](641-systems-requirements-planner.md) |

## Other roles (indexed for completeness)

The following roles are catalogued but not actively invoked by current research-program activities:

- [211 Law Enforcement Counterintelligence Forensics Analyst](211-law-enforcement-counterintelligence-forensics-analyst.md) — LE-side; not invoked
- [212 Cyber Defense Forensics Analyst](212-cyber-defense-forensics-analyst.md) — IR handoff role for confirmed incidents
- [221 Cyber Crime Investigator](221-cyber-crime-investigator.md) — LE prosecution-side; not invoked
- [411 Technical Support Specialist](411-technical-support-specialist.md) — Entry-tier IT; foundational
- [431 Knowledge Manager](431-knowledge-manager.md) — Classification taxonomy ownership
- [712 Cyber Instructor](712-cyber-instructor.md) — Future curriculum delivery
- [723 COMSEC Manager](723-comsec-manager.md) — Communications security
- [751 Cyber Workforce Developer and Manager](751-cyber-workforce-developer-and-manager.md) — Workforce-side
- [801 Program Manager](801-program-manager.md) — Program governance
- [802 IT Project Manager](802-it-project-manager.md) — Project execution
- [803 Product Support Manager](803-product-support-manager.md) — Sustainment
- [804 IT Investment Portfolio Manager](804-it-investment-portfolio-manager.md) — Portfolio strategy

## Cross-role meta-observations

From the per-role extraction work (3 parallel agent batches, all 35 pathways indexed):

- **The 611/612/641/651/652 cluster is the upstream governance/architecture chain** whose gaps produce the AI/LLM exposures NuClide surfaces externally. The 612 Security Control Assessor is the closest NICE analog to NuClide work, performed from inside the system boundary.
- **The 521/531 pair is the defender-side response chain** that receives the disclosures. Per-org disclosure outreach typically routes through these roles or the 722 ISSM.
- **The 621/622/632 developer-assessor cluster is the demographic whose default-deployment choices determine the Insight #76 outcome.** Upstream-maintainer disclosure (Langfuse / InfiniFlow / Arize) targets 621-equivalent roles inside those orgs.
- **671 STES and 805 IT Program Auditor are the strongest methodological analogs to NuClide's verification-stage discipline.** Both define T&E rigor we approximate in restraint-bounded outer-1 verification.
- **732 + 731 dyad is the standard route for PII/PHI exposure disclosures.** The Phoenix `/v1/users` finding class routes here when the operator is a US enterprise; LGPD/GDPR jurisdictions route via 731 first.
- **901 Executive Cyber Leadership terminates high-severity escalations.** Some Taiwan MoE / national-edu-infrastructure findings would route through TWCERT/CC to a 901-equivalent role in country.

## Source

NICE Cybersecurity Workforce Framework, Interagency Federal Cyber Career Pathways Working Group, November 2020. PDFs are the canonical reference for each role's task ID schema and KSA ID schema.

Foundational documents (not extracted into role files):
- `Report-Interagency_Federal_Cyber_Career_Pathways_Initiative_Nov2020_DoD-CIO.pdf` — framework methodology
- `Interagency_WG_Article-Final.pdf` — intent and rollout

## Extraction provenance

- Active roles (422, 541, 631, 661): manually extracted 2026-06-06 by primary analyst
- All other roles: parallel agent extraction 2026-06-06 in three batches (10 + 10 + 15 PDFs), each from pages 1-15 of the source PDF
