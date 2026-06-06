# NICE 431 — Knowledge Manager

**Source PDF:** `~/Documents/dod-cyber-pathways/431-Knowledge-Manager-Career-Pathway.pdf`

**Role definition (NICE):** "Responsible for the management and administration of processes and tools that enable the organization to identify, document, and access intellectual capital and information content."

**OPM Occupational Series alignment (top 3):**
- 2210-Information Technology — 45%
- 301-Misc. Administration and Program — 11%
- 343-Management and Program Analysis — 7%

**Common Work Role Pairings (top 3):**
- 411-Technical Support Specialist — 36%
- 422-Data Analyst — 9%
- 451-System Administrator — 7%

## Core Tasks

| Task ID | Task Statement |
|---|---|
| T0037 | Construct access paths to suites of information (e.g., link pages) to facilitate access by end-users. |
| T0060 | Develop an understanding of the needs and requirements of information end-users. |
| T0154 | Monitor and report the usage of knowledge management assets and resources. |
| T0185 | Plan and manage the delivery of knowledge management projects. |
| T0339 | Lead efforts to promote the organization's use of knowledge management and information sharing. |
| T0421 | Manage the indexing/cataloguing, storage, and access of explicit organizational knowledge. |
| T0452 | Design, build, implement, and maintain a knowledge management framework that provides end-users access to the organization's intellectual capital. |
| T0524 | Promote knowledge sharing between information owners/users through organization's operational processes/systems. |

## Additional Tasks

| Task ID | Task Statement |
|---|---|
| T0209 | Provide recommendations on data structures and databases that ensure correct and quality production of reports/management information. |

## Core KSAs

| KSA ID | Description | Competency |
|---|---|---|
| K0004 | Knowledge of cybersecurity and privacy principles. | Information Systems/Network Security |
| K0001 | Knowledge of computer networking concepts/protocols. | Infrastructure Design |
| K0003 | Knowledge of laws/regulations related to cybersecurity. | Legal, Government, and Jurisprudence |
| K0002 | Knowledge of risk management processes. | Risk Management |
| K0005 | Knowledge of cyber threats and vulnerabilities. | Vulnerabilities Assessment |
| K0006 | Knowledge of operational impacts of cybersecurity lapses. | Vulnerabilities Assessment |
| K0095 | Knowledge of technologies for organizing and managing information (databases, bookmarking engines). | Data Management |
| K0195 | Knowledge of data classification standards based on sensitivity/risk factors. | Data Management |
| K0260 | Knowledge of PII data security standards. | Data Privacy and Protection |
| K0261 | Knowledge of PCI data security standards. | Data Privacy and Protection |
| K0262 | Knowledge of PHI data security standards. | Data Privacy and Protection |
| K0194 | Knowledge of Cloud-based knowledge management technologies. | Knowledge Management |
| K0228 | Knowledge of taxonomy and semantic ontology theory. | Knowledge Management |
| K0283 | Knowledge of use cases for collaboration/content synchronization across platforms. | Knowledge Management |
| K0146 | Knowledge of the organization's core business/mission processes. | Organizational Awareness |
| K0094 | Knowledge of content creation technologies (wikis, social networking, CMS, blogs). | Technology Awareness |
| K0096 | Knowledge of collaborative technologies (groupware, SharePoint). | Technology Awareness |
| K0013 | Knowledge of cyber defense and vulnerability assessment tools. | Vulnerabilities Assessment |

## Core Competencies

- C013 — Data Management (Core)
- C023 — Information Management (Core)
- C029 — Knowledge Management (Core)
- C014 — Data Privacy and Protection (Additional)
- C057 — Vulnerabilities Assessment (Additional)

## On Ramps

- 411-Technical Support Specialist
- 422-Data Analyst
- 641-Systems Requirements Planner

## Off Ramps

- 421-Database Administrator
- 422-Data Analyst
- (cross-functional: 711, 712, 732, 751, 752, 802, 803)

## Research-program relevance

Indirect relevance. 431 owns the org's information-classification taxonomy (K0195, K0287) — exactly the schema-level discipline NuClide's bag-of-fields sensitivity classification operates on, but from the defender's side. When a NuClide finding surfaces a "company internal" or "customer PII" classification label inside an exposed MLflow/Weaviate metadata blob, that label originated under a 431's framework. Not a chain step, but useful framing when explaining to a target org how their own classification scheme leaked through the data plane.
