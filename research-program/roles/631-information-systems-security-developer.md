# NICE 631 — Information Systems Security Developer

**Source PDF:** `~/Documents/dod-cyber-pathways/631-Information-Systems-Security-Developer-Career-Pathway.pdf`

**Role definition (NICE):** "Designs, develops, tests, and evaluates information security throughout the systems development life cycle."

## Core Tasks performed in this research program

| Task ID | Task Statement | Where performed |
|---|---|---|
| T0021 | Build, test, and modify product prototypes using working models or theoretical models | herald v0.1.0 → v0.1.1 (numeric coercion fix during RAGFlow survey calibration) |
| T0053 | Design and develop cybersecurity or cybersecurity-enabled products | herald is a cybersecurity-enabled product (auth-posture-as-a-service) |
| T0055 | Design hardware, operating systems, and software applications to adequately address cybersecurity requirements | herald's declarative YAML probe schema is the cybersecurity requirement encoded |
| T0061 | Develop and direct system testing and validation procedures and documentation | Probe validation against Python baselines: Dify (747 findings match), Open WebUI, Langfuse |
| T0069 | Develop detailed security design documentation for component and interface specifications to support system design and development | herald README + per-platform YAML configs serve this function |
| T0124 | Incorporate cybersecurity vulnerability solutions into system designs (e.g., Cybersecurity Vulnerability Alerts) | Each new platform survey produces a new herald YAML — vulnerability solutions encoded as detection probes |
| T0181 | Perform risk analysis (e.g., threat, vulnerability, and probability of occurrence) whenever an application or system undergoes a major change | herald v0.1.1 numeric-coercion change: risk-analyzed (false negatives possible on int-vs-float) before deploy |
| T0518 | Perform security reviews and identify security gaps in architecture | Tool-family review: aimap (TCP/TLS) + scanner (banner) + herald (auth) — three layers, gaps identified |
| T0359 | Design, implement, test, and evaluate secure interfaces between information systems, physical systems, and/or embedded technologies | herald NDJSON output → visorlog ingest is the secure interface |

## Core KSAs invoked

| KSA ID | Where applied |
|---|---|
| K0044 Knowledge of cybersecurity and privacy principles and organizational requirements (relevant to CIA + auth + non-repudiation) | herald restraint clause: enumerate metadata, no PII extraction |
| K0049 Knowledge of information technology (IT) security principles and methods | Defense-in-depth context informing severity tiers in case studies |
| K0050 Knowledge of local area and wide area networking principles and concepts including bandwidth management | herald worker pool sizing (40-60 workers default, tunable) |
| K0090 Knowledge of system life cycle management principles, including software security and usability | herald has version tags (v0.1.0 → v0.1.1) with documented change rationale |
| K0073 Knowledge of secure configuration management techniques (e.g., STIGs) | YAML platform configs are version-controlled and reviewable |
| K0322 Knowledge of embedded systems | (not core to this program, but role-relevant for future ICS/OT pivots) |
| K0179 Knowledge of network security architecture concepts including topology, protocols, components, and principles (e.g., application of defense-in-depth) | Tool-family separation: aimap / scanner / herald is a defense-in-depth posture for analysis |
| S0001 Skill in conducting vulnerability scans | herald performs vulnerability-class-bounded scans (configurable per platform) |
| S0022 Skill in designing countermeasures to identified security risks | Per-platform remediation YAML in every case study |
| S0034 Skill in discerning the protection needs (i.e., security controls) of information systems and networks | Per-finding severity tier in breakdown files |
| S0036 Skill in evaluating the adequacy of security designs | herald validates its own probe semantics against upstream source code |

## Case studies / tools attributable to this role's tasks (2026-06-06)

- `tools/herald.md` — primary product
- All survey case studies — apply herald per T0124
- The numeric coercion fix (commit `20f079a` on herald) is the canonical T0021 + T0181 example of the day

## SDLC discipline applied to herald

| SDLC stage | Evidence |
|---|---|
| Requirements | The repeating per-survey-script pattern across 6+ platforms identified the need |
| Design | Channel-semaphore concurrency + declarative YAML pattern selected from O'Reilly literature review (Security with Go + Powerful CLI Applications) |
| Implementation | `~/herald/main.go` (~280 lines Go) |
| Testing | Python probe baseline validation; Dify 747 findings match before promotion to production use |
| Deployment | Public release at `github.com/nuclide-research/herald` under MIT |
| Maintenance | Numeric coercion fix between v0.1.0 and v0.1.1 — documented in commit message and CHANGELOG-equivalent in commit history |

## Off-ramps (where this role could lead)

Per NICE PDF: 651 Enterprise Architect, 652 Security Architect. The 631→652 off-ramp aligns with the research-program tooling becoming a coherent security-architecture artifact (the NuClide arsenal) rather than a collection of independent tools.
