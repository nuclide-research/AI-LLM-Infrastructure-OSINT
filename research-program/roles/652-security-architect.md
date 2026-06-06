# NICE 652 — Security Architect

**Source PDF:** `~/Documents/dod-cyber-pathways/652-Security-Architect-Career-Pathway.pdf`

**Role definition (NICE):** "Ensures that the stakeholder security requirements necessary to protect the organization's mission and business processes are adequately addressed in all aspects of enterprise architecture including reference models, segment and solution architectures, and the resulting systems supporting those missions and business processes."

**OPM Occupational Series alignment (top 3):**
- 2210-Information Technology — 63%
- 0080-Security Administration — 11%
- 1550-Computer Science — 8%

**Common Work Role Pairings (top 3):**
- 461-Systems Security Analyst — 11%
- 631-Information Systems Security Developer — 11%
- 651-Enterprise Architect — 10%

## Core Tasks

| Task ID | Task Statement |
|---|---|
| T0071 | Develop/integrate cybersecurity designs for systems and networks with multilevel security requirements or requirements for the processing of multiple classification levels of data primarily applicable to government organizations (e.g., UNCLASSIFIED, SECRET, and TOP SECRET). |
| T0082 | Document and address organization's information security, cybersecurity architecture, and systems security engineering requirements throughout the acquisition life cycle. |
| T0084 | Employ secure configuration management processes. |
| T0090 | Ensure that acquired or developed system(s) and architecture(s) are consistent with organization's cybersecurity architecture guidelines. |
| T0108 | Identify and prioritize critical business functions in collaboration with organizational stakeholders. |
| T0177 | Perform security reviews, identify gaps in security architecture, and develop a security risk management plan. |
| T0268 | Define and document how the implementation of a new system or new interfaces between systems impacts the security posture of the current environment. |
| T0328 | Evaluate security architectures and designs to determine the adequacy of security design and architecture proposed or provided in response to requirements contained in acquisition documents. |
| T0484 | Determine the protection needs (i.e., security controls) for the information system(s) and network(s) and document appropriately. |

## Additional Tasks

| Task ID | Task Statement |
|---|---|
| T0314 | Develop a system security context, preliminary system security CONOPS, and define baseline system security requirements. |
| T0307 | Analyze candidate architectures, allocate security services, and select security mechanisms. |
| T0427 | Analyze user needs and requirements to plan architecture. |
| T0050 | Define and prioritize essential system capabilities or business functions required for restoration after a catastrophic failure event. |
| T0051 | Define appropriate levels of system availability based on critical system functions, ensuring DR/COOP requirements. |
| T0196 | Provide advice on project costs, design concepts, or design changes. |
| T0203 | Provide input on security requirements to be included in statements of work and other procurement documents. |
| T0205 | Provide input to the RMF process. |
| T0338 | Write detailed functional specifications that document architecture development. |
| T0448 | Develop enterprise architecture or system components. |
| T0473 | Document and update all definition and architecture activities. |
| T0542 | Translate proposed capabilities into technical requirements. |
| T0556 | Assess and design security management functions as related to cyberspace. |

## Core KSAs

| KSA ID | Description | Competency |
|---|---|---|
| K0026 | Knowledge of business continuity and DR COOP plans. | Business Continuity |
| A0148 | Ability to serve as primary liaison between the enterprise architect and the systems security engineer. | Client Relationship Management |
| K0202 | Knowledge of application firewall concepts and functions. | Computer Network Defense |
| K0030 | Knowledge of electrical engineering as applied to computer architecture. | Computers and Electronics |
| K0055 | Knowledge of microprocessors. | Computers and Electronics |
| K0043 | Knowledge of industry-standard and organizationally accepted analysis principles and methods. | Data Analysis |
| K0291 | Knowledge of enterprise IT architectural concepts and patterns. | Enterprise Architecture |
| A0061 | Ability to design architectures and frameworks. | Enterprise Architecture |
| S0027 | Skill in determining how a security system should work. | Information Technology Assessment |
| K0015 | Knowledge of computer algorithms. | Mathematical Reasoning |
| K0264 | Knowledge of program protection planning (IT SCRM, anti-tampering). | Risk Management |
| K0035 | Knowledge of installation, integration, and optimization of system components. | Systems Integration |
| K0036 | Knowledge of human-computer interaction principles. | Systems Integration |
| K0071 | Knowledge of remote access technology concepts. | Technology Awareness |
| K0010 | Knowledge of communication methods, principles, and concepts that support network infrastructure. | Telecommunications |

## Core Competencies

- C014 — Data Privacy and Protection (Core)
- C018 — Enterprise Architecture (Core)
- C020 — Identity Management (Core)
- C022 — Information Assurance (Core)
- C024 — Information Systems/Network Security (Core)
- C026 — Infrastructure Design (Core)
- C049 — Systems Integration (Core)
- C017 — Encryption (Additional)
- C025 — Information Technology Assessment (Additional)
- C031 — Mathematical Reasoning (Additional)
- C043 — Requirements Analysis (Additional)
- C048 — System Administration (Additional)
- C053 — Technology Awareness (Additional)

## On Ramps

- 631-Information Systems Security Developer
- 632-Systems Developer
- 651-Enterprise Architect
- 661-Information Systems Security Developer

## Off Ramps

- 651-Enterprise Architect

## Research-program relevance

The 652 owns multilevel-security design (T0071, including UNCLASS/SECRET/TS) and decides which security controls live where in the reference architecture. Most relevant in NuClide's defense-contractor and cleared-target work: when an MLflow or vector DB sits outside the segmented enclave it should be inside, the 652 is who'd own the boundary decision. Strong K0264 supply-chain weight aligns with the AI model/dataset provenance attack surface that's growing across the corpus. For commercial targets, 652 work mostly shows up as defense-in-depth gaps between application and network layers — the recurring pattern where auth exists at one layer but not the next.
