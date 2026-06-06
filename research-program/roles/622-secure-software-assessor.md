# NICE 622 — Secure Software Assessor

**Source PDF:** `~/Documents/dod-cyber-pathways/622_Secure_Software_Assessor.pdf`

**Role definition (NICE):** "Analyzes the security of new or existing computer applications, software, or specialized utility programs and provides actionable results."

**OPM Occupational Series alignment (top 3):**
- 2210-Information Technology — 65%
- 1550-Computer Science — 15%
- 0854-Computer Engineering — 7%

**Common Work Role Pairings (top 3):**
- 621-Software Developer — 44%
- 641-Systems Requirements Planner — 17%
- 671-System Testing and Evaluation Specialist — 11%

## Core Tasks

| Task ID | Task Statement |
|---|---|
| T0456 | Develop secure software testing and validation procedures. |
| T0516 | Perform secure program testing, review, and/or assessment to identify potential flaws in codes and mitigate vulnerabilities. |
| T0217 | Address security implications in the software acceptance phase including completion criteria, risk acceptance and documentation, common criteria, and methods of independent testing. |
| T0181 | Perform risk analysis whenever an application or system undergoes a major change. |
| T0013 | Apply coding and testing standards, apply security testing tools including "fuzzing" static-analysis code scanning tools, and conduct code reviews. |
| T0554 | Determine and document software patches or the extent of releases that would leave software vulnerable. |
| T0118 | Identify security issues around steady state operation and management of software and incorporate security measures at end of life. |
| T0111 | Identify basic common coding flaws at a high level. |
| T0040 | Consult with engineering staff to evaluate interface between hardware and software. |

## Additional Tasks

| Task ID | Task Statement |
|---|---|
| T0022 | Capture security controls during requirements phase. |
| T0236 | Translate security requirements into application design elements including threat modeling. |
| T0457 | Develop system testing and validation procedures. |
| T0436 | Conduct trial runs of programs. |
| T0171 | Perform integrated QA testing for security functionality. |
| T0311 | Consult with customers about software system design and maintenance. |
| T0117 | Identify security implications across centralized and decentralized environments. |
| T0424 | Analyze and provide information to stakeholders that supports development of security an application. |
| T0428 | Analyze security needs and software requirements to determine feasibility of design. |
| T0038 | Develop threat model based on customer interviews and requirements. |
| T0266 | Perform penetration testing as required for new or updated applications. |
| T0324 | Direct software programming and development of documentation. |
| T0228 | Store, retrieve, and manipulate data for analysis. |
| T0337 | Supervise and assign work to programmers, designers. |
| T0014 | Apply secure code documentation. |
| T0100 | Evaluate factors to determine hardware configuration. |

## Core KSAs

| KSA ID | Description | Competency |
|---|---|---|
| K0260 | Knowledge of PII data security standards. | Data Privacy and Protection |
| K0044 | Knowledge of cybersecurity principles and organizational requirements. | Information Assurance |
| S0034 | Skill in discerning the protection needs of information systems and networks. | Information Systems/Network Security |
| K0060 | Knowledge of operating systems. | Operating Systems |
| K0263 | Knowledge of IT risk management policies. | Risk Management |
| K0039 | Knowledge of cybersecurity principles and methods that apply to software development. | Software Development |
| K0153 | Knowledge of software QA process. | Software Development |
| K0178 | Knowledge of secure software deployment methodologies, tools, and practices. | Software Development |
| S0174 | Skill in using code analysis tools. | Software Testing and Evaluation |
| K0073 | Knowledge of secure configuration management techniques. | System Administration |
| K0028 | Knowledge of organization's evaluation and validation requirements. | Systems Testing and Evaluation |
| S0135 | Skill in secure test plan design. | Systems Testing and Evaluation |
| S0022 | Skill in designing countermeasures to identified security risks. | Threat Analysis |
| K0070 | Knowledge of system/application security threats and vulnerabilities. | Vulnerabilities Assessment |
| S0001 | Skill in conducting vulnerability scans and recognizing vulnerabilities in security systems. | Vulnerabilities Assessment |

## Core Competencies

- C006 — Computer Languages (Core)
- C014 — Data Privacy and Protection (Core)
- C022 — Information Assurance (Core)
- C045 — Software Development (Core)
- C050 — Systems Testing and Evaluation (Core)
- C057 — Vulnerabilities Assessment (Core)
- C044 — Risk Management (Additional)
- C026 — Infrastructure Design (Additional)
- C024 — Information Systems/Network Security (Additional)

## On Ramps

- 621-Software Developer
- 661-Research & Development Specialist
- 671-System Testing and Evaluation Specialist

## Off Ramps

- 661-Research and Development Specialist
- 671-System Testing and Evaluation Specialist
- 541-Vulnerability Assessment Analyst
- 612-Security Control Assessor
- 722-Information Systems Security Manager

## Role Pairings (extended)

- 621-Software Developer — 44%
- 641-Systems Requirements Planner — 17%
- 671-System Testing and Evaluation Specialist — 11%

## Research-program relevance

The 622 is the internal counterpart to NuClide's external work on the software side — pen tests new and updated applications (T0266), runs threat modeling (T0038), reviews secure deployment methodologies. When a target organization has a strong 622 function, the AI/LLM exposures we find are typically configuration gaps the assessor didn't have scope to test, not code defects. When a target lacks the 622 function, expect default-credential and missing-auth findings at the application layer. Useful disclosure routing: 622 owns "actionable results" deliverables, so frame findings as remediation steps not just exposure inventories.
