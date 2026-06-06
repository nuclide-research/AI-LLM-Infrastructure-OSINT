# NICE Roles — Research Program Mapping

Mapping each NICE Cybersecurity Workforce Framework role (DoD-8140) to the research-program activities it covers. PDFs in `~/Documents/dod-cyber-pathways/`. Detail files in this directory map specific Core Tasks (T-IDs) to specific surveys and tools.

## Composite primary role (active)

| Role | Function in this program | Detail |
|---|---|---|
| **422 Data Analyst** | Population analysis, ASN/geo enrichment, longitudinal metrics, dataset validation | [422-data-analyst.md](422-data-analyst.md) |
| **541 Vulnerability Assessment Analyst** | Audit-report generation (case studies + breakdowns), finding classification, verification stage | [541-vulnerability-assessment-analyst.md](541-vulnerability-assessment-analyst.md) |
| **631 Information Systems Security Developer** | Tool design and testing (herald, aimap, scanner), documented SDLC | [631-information-systems-security-developer.md](631-information-systems-security-developer.md) |
| **661 Research and Development Specialist** | Capability gap analysis, new-tool design, methodology evolution | [661-research-and-development-specialist.md](661-research-and-development-specialist.md) |

## Supporting roles (referenced)

| Role | When invoked |
|---|---|
| 511 Cyber Defense Analyst | Threat intel context for defensive use cases of finding classes |
| 521 Cyber Defense Infrastructure Support Specialist | Hardening-side write-ups (remediation sections of case studies) |
| 531 Cyber Defense Incident Responder | CERT coordination on consolidated disclosures |
| 612 Security Control Assessor | Compliance-frame audit when a finding hits a specific regulated framework |
| 622 Secure Software Assessor | Source-code review (validates probe semantics against upstream source) |
| 651 Enterprise Architect | Tool-family architecture decisions (aimap / scanner / herald separation) |
| 671 System Testing and Evaluation Specialist | Probe validation against Python baselines |
| 711 Cyber Instructional Curriculum Developer | Case study as teaching artifact |
| 731 Cyber Legal Advisor | Pre-disclosure legal review (ITAR, OFAC, GDPR jurisdiction) |
| 732 Privacy Compliance Officer | PII/PHI exposure findings (Phoenix /v1/users) |
| 752 Cyber Policy and Strategy Planner | Upstream-maintainer disclosure strategy |

## Other roles (indexed for completeness, not invoked)

PDFs exist for: 211 LE-CI Forensics, 212 Cyber Defense Forensics, 221 Cyber Crime Investigator, 411 Tech Support, 421 DBA, 431 Knowledge Manager, 441 NetOps, 451 SysAdmin, 461 Systems Security Analyst, 611 Authorizing Official, 621 Software Developer, 632 Systems Developer, 641 Systems Requirements Planner, 652 Security Architect, 712 Cyber Instructor, 722 ISSM, 723 ComSec Manager, 751 Workforce Developer, 801–805 Program/Project Managers, 901 Executive Cyber Leadership.

These roles are catalogued in case the research program expands into their scope (e.g. 211 if NuClide takes on forensic post-incident work; 901 if a leadership briefing artifact is needed).

## Source

NICE Cybersecurity Workforce Framework, Interagency Federal Cyber Career Pathways Working Group, November 2020. PDFs are the canonical reference for each role's task ID schema and KSA ID schema.

Foundational documents:
- `Report-Interagency_Federal_Cyber_Career_Pathways_Initiative_Nov2020_DoD-CIO.pdf` (framework methodology)
- `Interagency_WG_Article-Final.pdf` (intent and rollout)
