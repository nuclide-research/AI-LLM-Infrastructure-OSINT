# NICE 441 — Network Operations Specialist

**Source PDF:** `~/Documents/dod-cyber-pathways/441-Network-Operations-Specialist-Career-Pathway.pdf`

**Role definition (NICE):** "Plans, implements, and operates network services / systems, to include hardware and virtual environments."

**OPM Occupational Series alignment (top 3):**
- 2210-Information Technology — 70%
- 391-Telecommunications — 11%
- 856-Electronics Technical — 10%

**Common Work Role Pairings (top 3):**
- 411-Technical Support Specialist — 35%
- 451-System Administrator — 29%
- 521-Cyber Defense Infrastructure Support Specialist — 6%

## Core Tasks

| Task ID | Task Statement |
|---|---|
| T0035 | Configure and optimize network hubs, routers, and switches (e.g., higher-level protocols, tunneling). |
| T0065 | Develop and implement network backup and recovery procedures. |
| T0081 | Diagnose network connectivity problem. |
| T0125 | Install and maintain network infrastructure device operating system software (e.g., IOS, firmware). |
| T0126 | Install or replace network hubs, routers, and switches. |
| T0153 | Monitor network capacity and performance. |
| T0160 | Patch network vulnerabilities to ensure information is safeguarded against outside parties. |
| T0232 | Test and maintain network infrastructure including software and hardware devices. |

## Additional Tasks

| Task ID | Task Statement |
|---|---|
| T0121 | Implement new system design procedures, test procedures, and quality standards. |
| T0129 | Integrate new systems into existing network architecture. |
| T0200 | Provide feedback on network requirements, including network architecture and infrastructure. |

## Core KSAs

| KSA ID | Description | Competency |
|---|---|---|
| K0004 | Knowledge of cybersecurity principles. | Information Systems/Network Security |
| K0001 | Knowledge of computer networking concepts/protocols. | Infrastructure Design |
| K0003 | Knowledge of laws related to cybersecurity. | Legal, Government, and Jurisprudence |
| K0002 | Knowledge of risk management processes. | Risk Management |
| K0005 | Knowledge of cyber threats and vulnerabilities. | Vulnerabilities Assessment |
| K0006 | Knowledge of operational impacts of cybersecurity lapses. | Vulnerabilities Assessment |
| S0150 | Skill in implementing and testing network infrastructure contingency and recovery plans. | Business Continuity |
| S0079 | Skill in protecting a network against malware (NIPS, anti-malware, spam filters). | Computer Network Defense |
| K0104 | Knowledge of VPN security. | Encryption |
| K0038 | Knowledge of cybersecurity principles used to manage risks. | Information Assurance |
| K0049 | Knowledge of IT security principles (firewalls, DMZs, encryption). | Information Systems/Network Security |
| K0179 | Knowledge of network security architecture (defense-in-depth). | Information Systems/Network Security |
| S0170 | Skill in configuring computer protection components. | Information Systems/Network Security |
| S0040 | Skill in implementing/maintaining network security practices. | Information Systems/Network Security |
| S0077 | Skill in securing network communications. | Information Systems/Network Security |
| K0053 | Knowledge of system performance/availability measures. | Information Technology Assessment |
| K0011 | Knowledge of capabilities/applications of network equipment. | Infrastructure Design |
| K0113 | Knowledge of types of network communication (LAN, WAN, MAN, WLAN, WWAN). | Infrastructure Design |
| K0061 | Knowledge of how traffic flows (TCP/IP, OSI, ITIL). | Infrastructure Design |
| K0050 | Knowledge of LAN/WAN principles including bandwidth management. | Infrastructure Design |
| K0332 | Knowledge of network protocols (TCP/IP, DHCP, DNS, directory services). | Infrastructure Design |
| K0029 | Knowledge of organization's LAN/WAN connections. | Infrastructure Design |
| K0137 | Knowledge of existing networks (PBX, LANs, WANs, WIFI, SCADA). | Infrastructure Design |
| S0035 | Skill in establishing a routing schema. | Infrastructure Design |
| S0162 | Skill in applying subnet techniques (CIDR). | Infrastructure Design |
| A0055/A0052/K0180/S0004/S0084/S0041/S0056/K0111 | Network management cluster: ops common net tools, equipment ops, mgmt principles, traffic analysis, protection components, LAN/WAN troubleshooting, mgmt-protocol analysis, ping/traceroute/nslookup. | Network Management |
| A0058 | Ability to execute OS command line (ipconfig, netstat, nbtstat). | Operating Systems |
| A0063 | Ability to operate communication systems (email, VOIP, IM, web forums). | System Administration |
| K0076 | Knowledge of server administration theories. | Systems Integration |
| K0071 | Knowledge of remote access technology concepts. | Technology Awareness |
| K0108/K0010/K0093/K0136 | Telecommunications cluster: comm media, principles, telecom concepts, electronic communication system capabilities. | Telecommunications |
| K0135 | Knowledge of web filtering technologies. | Web Technology |

## Core Competencies

- C033 — Network Management (Core)
- C026 — Infrastructure Design (Core)
- C054 — Telecommunications (Core)
- C024 — Information Systems/Network Security (Core)
- C014 — Data Privacy and Protection (Additional)

## On Ramps

- 411-Technical Support Specialist
- 421-Database Administrator
- 451-System Administrator

## Off Ramps

- 421-Database Administrator, 461-Systems Security Analyst, 511-Cyber Defense Analyst, 541-Vulnerability Assessment Analyst, 632-Systems Developer, 641-Systems Requirements Planner, 671-System Testing and Evaluation, 521-Cyber Defense Infrastructure Support Specialist, 722-Information Systems Security Manager

## Research-program relevance

Indirect. 441 operates the network plane NuClide enumerates from the outside. Tasks T0160 (patch network vulnerabilities) and T0035 (configure routers/switches) frame what *should* close the surface NuClide finds. When a host shows port open / no app data (Shodan-dark, SYN-ACK-only), the responsible operator is typically a 441 who left the inner service reachable but the edge ACL permissive. Knowledge of CIDR (S0162), routing (S0035), and bandwidth management (K0050) is mirror-image of NuClide's recon enumeration discipline.
