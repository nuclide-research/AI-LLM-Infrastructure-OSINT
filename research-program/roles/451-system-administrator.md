# NICE 451 — System Administrator

**Source PDF:** `~/Documents/dod-cyber-pathways/451-System-Administrator-Career-Pathway.pdf`

**Role definition (NICE):** "Responsible for setting up and maintaining a system or specific components of a system (e.g. installing, configuring, and updating hardware and software; establishing and managing user accounts; overseeing or conducting backup and recovery tasks; implementing operational and technical security controls; and adhering to organizational security policies and procedures)."

**OPM Occupational Series alignment (top 3):**
- 2210-Information Technology — 85%
- 1550-Computer Science — 2%
- 391-Telecommunications — 2%

**Common Work Role Pairings (top 3):**
- 411-Technical Support Specialist — 35%
- 421-Database Administrator — 12%
- 441-Network Operations Specialist — 11%

## Core Tasks

| Task ID | Task Statement |
|---|---|
| T0029 | Conduct functional and connectivity testing to ensure continuing operability. |
| T0063 | Develop and document systems administration standard operating procedures. |
| T0136 | Maintain baseline system security according to organizational policies. |
| T0144 | Manage accounts, network rights, and access to systems and equipment. |
| T0186 | Plan, execute, and verify data redundancy and system recovery procedures. |
| T0418 | Install, update, and troubleshoot systems/servers. |
| T0458 | Comply with organization systems administration standard operating procedures. |
| T0461 | Implement and enforce local network usage policies and procedures. |
| T0498 | Manage system/server resources including performance, capacity, availability, serviceability, recoverability. |
| T0501 | Monitor and maintain system/server configuration. |
| T0515 | Perform repairs on faulty system/server hardware. |
| T0531 | Troubleshoot hardware/software interface and interoperability problems. |

## Additional Tasks

| Task ID | Task Statement |
|---|---|
| T0054 | Design group policies and access control lists to ensure compatibility with organizational standards. |
| T0207 | Provide ongoing optimization and problem-solving support. |
| T0431 | Check system hardware availability, functionality, integrity, efficiency. |
| T0435 | Conduct periodic system maintenance (cleaning, disk checks, reboots, data dumps, testing). |
| T0507 | Oversee installation, implementation, configuration, support of system components. |
| T0514 | Diagnose faulty system/server hardware. |

## Core KSAs

| KSA ID | Description | Competency |
|---|---|---|
| K0004 | Knowledge of cybersecurity and privacy principles. | Information Systems/Network Security |
| K0001 | Knowledge of computer networking concepts/protocols. | Infrastructure Design |
| K0003 | Knowledge of laws related to cybersecurity. | Legal, Government, and Jurisprudence |
| K0002 | Knowledge of risk management processes. | Risk Management |
| K0005 | Knowledge of cyber threats and vulnerabilities. | Vulnerabilities Assessment |
| K0006 | Knowledge of operational impacts of cybersecurity lapses. | Vulnerabilities Assessment |
| K0158 | Knowledge of IT user security policies (account creation, password, access control). | Identity Management |
| K0053 | Knowledge of system performance/availability measures. | Information Technology Assessment |
| K0064 | Knowledge of performance tuning tools and techniques. | Information Technology Assessment |
| S0155 | Skill in monitoring and optimizing system/server performance. | Information Technology Assessment |
| S0158 | Skill in OS administration (account maintenance, backups, install/configure hardware/software). | Operating Systems |
| K0088 | Knowledge of systems administration concepts. | System Administration |
| K0130 | Knowledge of virtualization technologies and VM development/maintenance. | System Administration |
| K0167 | Knowledge of system/network/OS hardening techniques. | System Administration |
| S0144 | Skill in correcting physical/technical problems impacting system performance. | System Administration |
| S0157 | Skill in recovering failed systems/servers. | System Administration |
| K0346 | Knowledge of principles for integrating system components. | Systems Integration |

## Core Competencies

- C024 — Information Systems/Network Security (Core)
- C025 — Information Technology Assessment (Core)
- C026 — Infrastructure Design (Core)
- C033 — Network Management (Core)
- C034 — Operating Systems (Core)
- C048 — System Administration (Core)
- C014 — Data Privacy and Protection (Additional)

## On Ramps

- 411-Technical Support Specialist
- 421-Database Administrator

## Off Ramps

- 421-Database Administrator, 441-Network Operations Specialist, 461-System Security Analyst, 511-Cyber Defense Analyst, 521-Cyber Defense Infrastructure Support Specialist, 541-Vulnerability Assessment Analyst, 621-Software Developer, 641-Systems Requirements Planner, 671-System Testing and Evaluation

## Research-program relevance

Directly relevant. 451 SysAdmin is the most common operator behind an exposed unauth AI/ML service in NuClide's findings — they stood up the Ollama instance, the Jupyter server, the MLflow tracking host, the Kubernetes node — and missed the auth-on-default toggle. Tasks T0136 (baseline security) and T0144 (account/access management) frame the controls that should have prevented the exposure; their absence in deploy practice is the structural condition NuClide's research program documents. K0167 (system hardening) and S0158 (OS administration) define the defender capability set we're measuring the gap against. Disclosure copy on misconfigured infra typically lands in a 451's queue.
