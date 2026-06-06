# NICE 422 — Data Analyst

**Source PDF:** `~/Documents/dod-cyber-pathways/422-Data-Analyst-Career-Pathway.pdf`

**Role definition (NICE):** "Examines data from multiple disparate sources with the goal of providing security and privacy insight. Designs and implements custom algorithms, workflow processes, and layouts for complex, enterprise-scale data sets used for modeling, data mining, and research purposes."

## Core Tasks performed in this research program

| Task ID | Task Statement | Where performed |
|---|---|---|
| T0007 | Analyze and define data requirements and specifications | herald YAML probe schema design |
| T0342 | Analyze data sources to provide actionable recommendations | Every survey's geographic/ASN/institutional enrichment section |
| T0347 | Assess the validity of source data and subsequent findings | Verification stage (load-bearing); filtering FPs like Huawei "GOV" keyword |
| T0349 | Collect metrics and trending data | Insight #76 longitudinal — 88.9% / 87.2% / 74.5% same-day baseline |
| T0068 | Develop data standards, policies, and procedures | herald NDJSON output schema; case-study finding-breakdown standard |
| T0385 | Provide actionable recommendations to critical stakeholders | Disclosure pipeline state per finding |
| T0366 | Develop strategic insights from large data sets | Insight #76 cohort hypothesis from cross-platform data |

## Core KSAs invoked

| KSA ID | Where applied |
|---|---|
| S0109 Skill in identifying hidden patterns or relationships | Three-platform same-day rate clustering (Langfuse/RAGFlow/Phoenix) |
| S0123 Skill in transformation analytics (aggregation, enrichment, processing) | Joining Shodan records + herald NDJSON + IP→ASN |
| S0125 Skill in using basic descriptive statistics | Rate calculations, version-cohort breakdowns |
| K0083 Knowledge of sources, characteristics, and uses of the organization's data assets | Shodan record schema, herald output schema, case-study structure |
| K0236 Knowledge of how to utilize Hadoop, Java, Python, SQL, Hive, and Pig to explore data | Python + NDJSON + CSV pipeline |
| A0041 Ability to use data visualization tools | Markdown tables; future: Tableau or D3 if program scales |

## Case studies attributable to this role's tasks (2026-06-06)

- `surveys/2026-06-06-langfuse.md` — T0349 (longitudinal rate), T0342 (geographic enrichment), T0385 (per-org recommendation)
- `surveys/2026-06-06-ragflow.md` — same
- `surveys/2026-06-06-phoenix.md` — same + T0347 (data layer disclosure schema verification)
- All earlier surveys per case-studies index

## Off-ramps (where this role could lead)

Per NICE PDF: 421 DBA, 431 Knowledge Manager, 621 Software Developer, 632 Systems Developer, 661 R&D Specialist, 461 Systems Security Analyst, 511 Cyber Defense Analyst. The 422→661 off-ramp is the active progression for this program — data-analysis work informing tool development.
