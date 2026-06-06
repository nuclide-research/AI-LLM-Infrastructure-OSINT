# NICE 641 — Systems Requirements Planner

**Source PDF:** `~/Documents/dod-cyber-pathways/641-Systems-Requirements-Planner-Career-Pathway.pdf`

**Role definition (NICE):** "Consults with customers to gather and evaluate functional requirements and translates these requirements into technical solutions. Provides guidance to customers about applicability of information systems to meet business needs."

**OPM Occupational Series alignment (top 3):**
- 2210-Information Technology Management Series — 60%
- 501-Financial Administration and Program — 5%
- 855-Electronics Engineering — 5%

**Common Work Role Pairings (top 3):**
- 671-System Testing and Evaluation Specialist — 43%
- 801-Program Manager — 11%
- 802-IT Project Manager — 7%

## Core Tasks

| Task ID | Task Statement |
|---|---|
| T0033 | Conduct risk analysis, feasibility study, and/or trade-off analysis to develop, document, and refine functional requirements and specifications. |
| T0039 | Consult with customers to evaluate functional requirements. |
| T0052 | Define project scope and objectives based on customer requirements. |
| T0235 | Translate functional requirements into technical solutions. |
| T0300 | Develop and document User Experience (UX) requirements including information architecture and UI requirements. |

## Additional Tasks

| Task ID | Task Statement |
|---|---|
| T0045 | Coordinate with systems architects and developers to provide oversight in development of design solutions. |
| T0062 | Develop and document requirements, capabilities, and constraints for design procedures and processes. |
| T0127 | Integrate and align information security and/or cybersecurity policies to ensure that system analysis meets security requirements. |
| T0156 | Oversee and make recommendations regarding configuration management. |
| T0174 | Perform needs analysis to determine opportunities for new and improved business process solutions. |
| T0191 | Prepare use cases to justify the need for specific IT solutions. |
| T0273 | Develop and document supply chain risks for critical system elements, as appropriate. |
| T0313 | Design and document quality standards. |
| T0325 | Document a system's purpose and preliminary system security concept of operations. |
| T0334 | Ensure that all systems components can be integrated and aligned. |
| T0454 | Define baseline security requirements in accordance with applicable guidelines. |
| T0463 | Develop cost estimates for new or modified system(s). |
| T0497 | Manage the IT planning process to ensure that developed solutions meet customer requirements. |

## Core KSAs

| KSA ID | Description | Competency |
|---|---|---|
| K0101 | Knowledge of the organization's enterprise IT goals and objectives. | Enterprise Architecture |
| K0044 | Knowledge of cybersecurity and privacy principles and organizational requirements. | Information Assurance |
| K0045 | Knowledge of information security systems engineering principles (NIST SP 800-160). | Information Systems/Network Security |
| A0064 | Ability to interpret and translate customer requirements into operational capabilities. | Requirements Analysis |
| K0008 | Knowledge of applicable business processes and operations of customer organizations. | Requirements Analysis |
| K0012 | Knowledge of capabilities and requirements analysis. | Requirements Analysis |
| S0010 | Skill in conducting capabilities and requirements analysis. | Requirements Analysis |
| K0090 | Knowledge of system life cycle management principles, including software security and usability. | Systems Integration |

## Core Competencies

- C018 — Enterprise Architecture (Core)
- C022 — Information Assurance (Core)
- C043 — Requirements Analysis (Core)
- C049 — Systems Integration (Core)
- C026 — Infrastructure Design (Additional)
- C030 — Legal, Government, and Jurisprudence (Additional)
- C050 — Systems Testing and Evaluation (Additional)

## On Ramps

- 411-Technical Support Specialist
- 421-Database Administrator
- 441-Network Operations Specialist
- 451-Systems Administrator
- 621-Software Developer
- 632-Systems Developer

## Off Ramps

- 431-Knowledge Manager
- 621-Software Developer
- 632-Systems Developer
- 661-Research and Development Specialist
- 671-System Testing and Evaluation Specialist

## Research-program relevance

Upstream of the deploy. The 641 writes the requirements that determine whether the AI/LLM system NuClide later finds exposed was specified with auth-on, network segmentation, and a security CONOPS (T0325) — or specified for "make it work fast". Most NuClide auth-on-default failures trace back to a requirements document the 641 either never wrote or wrote without K0044 cybersecurity baselines. Not directly invoked in active assessments, but useful when reasoning about why a particular exposure exists: the gap is usually in C043 Requirements Analysis, not in the developer's code.
