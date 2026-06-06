# NICE 651 — Enterprise Architect

**Source PDF:** `~/Documents/dod-cyber-pathways/651-Enterprise-Architect-Career-Pathway.pdf`

**Role definition (NICE):** "Develops and maintains business, systems, and information processes to support enterprise mission needs; develops information technology (IT) rules and requirements that describe baseline and target architectures."

**OPM Occupational Series alignment (top 3):**
- 2210-Information Technology — 72%
- 855-Electronics Engineering — 7%
- 1550-Computer Science — 5%

**Common Work Role Pairings (top 3):**
- 651-Systems Requirements Planner — 15%
- 632-Systems Developer — 15%
- 661-Research & Development Specialist — 10%

## Core Tasks

| Task ID | Task Statement |
|---|---|
| T0084 | Employ secure configuration management processes. |
| T0090 | Ensure that acquired or developed system(s) and architecture(s) are consistent with organization's cybersecurity architecture guidelines. |
| T0108 | Identify and prioritize critical business functions in collaboration with organizational stakeholders. |
| T0427 | Analyze user needs and requirements to plan architecture. |
| T0448 | Develop enterprise architecture or system components required to meet user needs. |
| T0473 | Document and update as necessary all definition and architecture activities. |
| T0521 | Plan implementation strategy to ensure that enterprise components can be integrated and aligned. |

## Additional Tasks

| Task ID | Task Statement |
|---|---|
| T0196 | Provide advice on project costs, design concepts, or design changes. |
| T0205 | Provide input to the RMF process activities and related documentation. |
| T0307 | Analyze candidate architectures, allocate security services, and select security mechanisms. |
| T0314 | Develop a system security context, preliminary system security CONOPS, and define baseline system security requirements. |
| T0328 | Evaluate security architectures and designs to determine the adequacy of security design and architecture. |
| T0338 | Write detailed functional specifications that document the architecture development process. |
| T0440 | Capture and integrate essential system capabilities or business functions required for partial or full system restoration. |
| T0517 | Integrate results regarding the identification of gaps in security architecture. |
| T0542 | Translate proposed capabilities into technical requirements. |
| T0555 | Document how the implementation of a new system or new interface between systems impacts the current and target environment including security posture. |
| T0557 | Integrate key management functions as related to cyberspace. |
| T0051 | Define appropriate levels of system availability based on critical system functions and ensure system requirements identify appropriate DR/COOP. |

## Core KSAs

| KSA ID | Description | Competency |
|---|---|---|
| K0291 | Knowledge of the enterprise IT architectural concepts and patterns (baseline, validated design, target architectures). | Enterprise Architecture |
| K0293 | Knowledge of integrating the organization's goals and objectives into the architecture. | Enterprise Architecture |
| A0060 | Ability to build architectures and frameworks. | Enterprise Architecture |
| K0056 | Knowledge of network access, identity, and access management (PKI, OAuth, OpenID, SAML, SPML). | Identity Management |
| K0027 | Knowledge of organization's enterprise information security architecture. | Information Assurance |
| K0179 | Knowledge of network security architecture concepts including topology, protocols, defense-in-depth. | Information Systems/Network Security |
| K0333 | Knowledge of network design processes (security objectives, operational objectives, trade-offs). | Infrastructure Design |
| K0102 | Knowledge of the systems engineering process. | Systems Integration |

## Core Competencies

- C018 — Enterprise Architecture (Core)
- C022 — Information Assurance (Core)
- C024 — Information Systems/Network Security (Core)
- C026 — Infrastructure Design (Core)
- C048 — System Administration (Core)
- C049 — Systems Integration (Core)
- C025 — Information Technology Assessment (Additional)
- C057 — Vulnerabilities Assessment (Additional)

## On Ramps

- 621-Software Developer
- 632-Systems Developer
- 631-Information Systems Security Developer
- 652-Security Architect
- 661-Research and Development Specialist

## Off Ramps

- 652-Security Architect

## Research-program relevance

The 651 sets the baseline and target architecture — including identity/access management (K0056: PKI, OAuth, OIDC, SAML, SPML). NuClide assessments often find AI/LLM components deployed *outside* the documented enterprise architecture (shadow ML stacks, researcher-spun MLflow/Weaviate). The 651's gap is scope, not skill: their architecture diagram doesn't include the GPU box a data scientist stood up. Useful frame for executive disclosure summaries: "your enterprise architecture does not account for these N components currently exposed." Maps to TOGAF/DoDAF/FEAF (A0008) for federal targets.
