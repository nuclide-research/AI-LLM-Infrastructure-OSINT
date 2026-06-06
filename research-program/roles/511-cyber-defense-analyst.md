# NICE 511 — Cyber Defense Analyst

**Source PDF:** `~/Documents/dod-cyber-pathways/511-Cyber-Defense-Analyst-Career-Pathway.pdf`

**Role definition (NICE):** "Uses data collected from a variety of cyber defense tools (e.g., IDS alerts, firewalls, network traffic logs) to analyze events that occur within their environments for the purposes of mitigating threats."

**OPM Occupational Series alignment (top 3):**
- 2210-Information Technology — 86%
- 1550-Computer Science — 7%
- 0132-Intelligence — 2%

**Common Work Role Pairings (top 3):**
- 531-Cyber Defense Incident Responder — 34%
- 541-Vulnerability Assessment Analyst — 15%
- 521-Cyber Defense Infrastructure Support Specialist — 13%

## Core Tasks

| Task ID | Task Statement |
|---|---|
| T0258 | Provide timely detection, identification, alerting of attacks/intrusions/anomalous activity; distinguish incidents from benign activity. |
| T0259 | Use cyber defense tools for continual monitoring/analysis of system activity to identify malicious activity. |
| T0155 | Document and escalate incidents (event history, status, potential impact) that may cause ongoing/immediate impact. |
| T0260 | Analyze identified malicious activity to determine weaknesses exploited, exploitation methods, effects on system/info. |
| T0166 | Perform event correlation using info from sources within the enterprise to gain situational awareness and determine attack effectiveness. |
| T0294 | Conduct research, analysis, correlation across all source data sets (indications and warnings). |
| T0214 | Receive and analyze network alerts from various sources and determine possible causes. |
| T0164 | Perform cyber defense trend analysis and reporting. |
| T0023 | Characterize and analyze network traffic to identify anomalous activity and potential threats. |
| T0043 | Coordinate with enterprise-wide cyber defense staff to validate network alerts. |
| T0293 | Identify and analyze anomalies in network traffic using metadata. |
| T0198 | Provide daily summary reports of network events and activity relevant to cyber defense practices. |
| T0297 | Identify applications and operating systems of a network device based on network traffic. |

## Additional Tasks

| Task ID | Task Statement |
|---|---|
| T0332 | Notify managers/IR/CSSP team of suspected cyber incidents and articulate event's history, status, impact. |
| T0526 | Provide cybersecurity recommendations to leadership. |
| T0545 | Work with stakeholders to resolve computer security incidents and vulnerability compliance. |
| T0295 | Validate IDS alerts against network traffic using packet analysis tools. |
| T0299 | Identify network mapping and OS fingerprinting activities. |
| T0310 | Assist in constructing signatures for cyber defense network tools. |
| T0298 | Reconstruct a malicious attack or activity based off network traffic. |
| T0290 | Determine TTPs for intrusion sets. |
| T0088 | Ensure cybersecurity-enabled products reduce identified risk to acceptable level. |
| T0291 | Examine network topologies to understand data flows. |
| T0187 | Plan and recommend modifications based on exercise results or system environment. |

## Core KSAs

| KSA ID | Description | Competency |
|---|---|---|
| K0004 | Knowledge of cybersecurity and privacy principles. | Information Systems/Network Security |
| K0001 | Knowledge of networking concepts/protocols. | Infrastructure Design |
| K0003 | Knowledge of laws/regulations/policies/ethics for cybersecurity. | Legal, Government, and Jurisprudence |
| K0002 | Knowledge of risk management processes. | Risk Management |
| K0005 | Knowledge of cyber threats and vulnerabilities. | Vulnerabilities Assessment |
| K0006 | Knowledge of cybersecurity-lapse operational impacts. | Vulnerabilities Assessment |
| K0046 | Knowledge of intrusion detection methodologies for host/network-based intrusions. | Computer Network Defense |
| K0157 | Knowledge of cyber defense and info security policies/procedures/regulations. | Computer Network Defense |
| K0160 | Knowledge of common attack vectors on the network layer. | Computer Network Defense |
| K0324 | Knowledge of IDS/IPS tools and applications. | Computer Network Defense |
| S0063 | Skill in collecting data from a variety of cyber defense resources. | Data Management |
| K0049 | Knowledge of IT security principles (firewalls, DMZs, encryption). | Information Systems/Network Security |
| K0061 | Knowledge of traffic flow (TCP/IP, OSI, ITIL). | Infrastructure Design |
| K0332 | Knowledge of network protocols (TCP/IP, DHCP, DNS, directory services). | Infrastructure Design |
| K0058 | Knowledge of network traffic analysis methods. | Network Management |
| K0059 | Knowledge of new/emerging IT and cybersecurity technologies. | Technology Awareness |
| K0161 | Knowledge of different classes of attacks (passive, active, insider, close-in, distribution). | Threat Analysis |
| K0162 | Knowledge of cyber attackers (script kiddies, insider, non-nation/nation-state). | Threat Analysis |
| K0013 | Knowledge of cyber defense and vulnerability assessment tools. | Vulnerabilities Assessment |
| K0106 | Knowledge of what constitutes a network attack and its relationship to threats/vulnerabilities. | Vulnerabilities Assessment |
| K0339 | Knowledge of network analysis tools for identifying vulnerabilities. | Vulnerabilities Assessment |
| S0078 | Skill in recognizing/categorizing types of vulnerabilities and associated attacks. | Vulnerabilities Assessment |
| S0156 | Skill in performing packet-level analysis. | Vulnerabilities Assessment |

## Core Competencies

- C007 — Computer Network Defense (Core)
- C055 — Threat Analysis (Core)
- C057 — Vulnerabilities Assessment (Core)
- C021 — Incident Management (Core)
- C033 — Network Management (Core)
- C013 — Data Management (Core)
- C024 — Information Systems/Network Security (Core)

## On Ramps

- 422-Data Analyst
- 441-Network Operations Specialist
- 451-System Administrator
- 461-Systems Security Analyst

## Off Ramps

- 111-All-Source Analyst
- 141-Threat/Warning Analyst
- 212-Cyber Defense Forensics Analyst
- 521-Cyber Defense Infrastructure Support Specialist
- 531-Cyber Defense Incident Responder
- 541-Vulnerability Assessment Analyst
- 722-Information Systems Security Manager

## Research-program relevance

Directly relevant — and the mirror role to NuClide's external assessment posture. 511 sits inside the org watching the same network traffic NuClide generates from the outside. Tasks T0023 (characterize anomalous traffic), T0297 (identify apps/OS from network traffic), T0299 (identify network mapping and OS fingerprinting activities) are exactly what *should* detect aimap/jaxen probes. When NuClide tradecraft stays quiet (slow probes, congestion-controlled, fingerprint-only), it is calibrated against this role's detection capability set (K0046 IDS methodologies, K0058 traffic analysis, S0156 packet analysis). When VisorRoam ships, it becomes the internal-side equivalent of a 511 sensor for AI/ML infrastructure. Disclosure recipients at orgs with mature SOCs route NuClide findings through a 511 before they reach a 461.
