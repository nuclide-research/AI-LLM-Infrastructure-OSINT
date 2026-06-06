# NICE 661 — Research and Development Specialist

**Source PDF:** `~/Documents/dod-cyber-pathways/661-Research-and-Development-Specialist.pdf`

**Role definition (NICE):** "Conducts software and systems engineering and software systems research to develop new capabilities, ensuring cybersecurity is fully integrated. Conducts comprehensive technology research to evaluate potential vulnerabilities in cyberspace systems."

## Core Tasks performed in this research program

| Task ID | Task Statement | Where performed |
|---|---|---|
| T0249 | Research current technology to understand capabilities of required system or network | Every Stage -1 OSINT Platoon dispatch; platform-intel research per new survey target |
| T0250 | Identify cyber capabilities strategies for custom hardware and software development based on mission requirements | herald capability strategy: declarative YAML + Go binary, no per-survey script writing |
| T0283 | Collaborate with stakeholders to identify and/or develop appropriate solutions technology | (research-program-internal: Nicholas Kloster as primary stakeholder; future: upstream maintainer collaboration when disclosing) |
| T0329 | Follow software and systems engineering life cycle standards and processes | SDLC discipline for herald per `roles/631-information-systems-security-developer.md` |
| T0547 | Research and evaluate available technologies and standards to meet customer requirements | O'Reilly literature review for Go HTTP scanning patterns (Security with Go + Powerful CLI Applications + Hacking APIs) |
| T0284 | Design and develop new tools/technologies as related to cybersecurity | herald, aimap-profile, scanner, BARE, recongraph, agent-logging-system, et al. |
| T0327 | Evaluate network infrastructure vulnerabilities to enhance capabilities being developed | Every survey informs herald's next platform config — capability iteration driven by vuln class discovered |
| T0410 | Identify functional- and security-related features to find opportunities for new capability development to exploit or mitigate vulnerabilities | LLM02 disclosure class identified in Phoenix → new `users_unauth` probe class → applicable to all future observability platforms |
| T0411 | Identify and/or develop reverse engineering tools to enhance capabilities and detect vulnerabilities | aimap fingerprint reverse engineering; herald source-code verification against upstream targets |

## Core KSAs invoked

| KSA ID | Where applied |
|---|---|
| K0059 Knowledge of new and emerging information technology (IT) and cybersecurity technologies | The entire research program is about new-and-emerging AI/LLM infrastructure |
| K0090 Knowledge of system life cycle management principles, including software security and usability | herald usability: declarative YAML lowers per-survey cognitive load |
| S0005 Skill in applying and incorporating information technologies into proposed solutions | herald's design draws from three O'Reilly books selected for the specific concurrency + REST + CLI patterns |
| S0140 Skill in applying the systems engineering process | herald followed scoped SDLC despite being a one-day build |
| K0314 Knowledge of industry technologies' potential cybersecurity vulnerabilities | OWASP LLM Top 10 (2025) tracking |
| K0288 Knowledge of industry standard security models | NIST CSF, ISO 27001 (referenced for compliance-mapping in case studies) |
| K0321 Knowledge of engineering concepts as applied to computer architecture and associated computer hardware/software | Tool-family architecture: aimap (L4) + scanner (L5 banner) + herald (L7 auth) — clean separation |
| A0018 Ability to prepare and present briefings | Case studies + breakdowns + this research-program directory are the briefing artifacts |
| A0019 Ability to produce technical documentation | herald README + 7 same-day case studies are the production output |

## Capability gap analysis methodology

The 661 role's most-applied skill in this program: **identifying when a recurring manual pattern is actually a capability gap.**

- Manual per-survey probe scripts → herald
- Manual ASN enrichment → integrate into herald output / future
- Manual case-study drafting → standardize the breakdown.txt schema (done)
- Manual disclosure tracking → `disclosures/INDEX.md` (in progress)
- Manual literature citation → `literature/` index (in progress)

Each capability gap, once identified, gets fed back through 631 (development), 671 (testing), and back to 541 (operational use).

## Case studies / tools attributable to this role's tasks (2026-06-06)

- `tools/herald.md` — capability gap analysis → product
- O'Reilly literature reviews (Security with Go, Powerful CLI Applications, Hacking APIs, AI-Native LLM Security, Hacking APIs) per T0249
- All case studies under `surveys/` — T0327 applied per platform

## Off-ramps (where this role could lead)

Per NICE PDF: 651 Enterprise Architect, 671 System Testing and Evaluation Specialist, 622 Secure Software Assessor, 631 Information Systems Security Developer (current adjacent role), 652 Security Architect. The 661→651 off-ramp would mean responsibility for the overall NuClide tool-family architecture as it scales beyond 19 tools.
