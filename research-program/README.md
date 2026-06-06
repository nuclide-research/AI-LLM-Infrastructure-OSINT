# NuClide Research Program

This directory is an **index over the entire research program**. It does not contain primary artifacts — case studies live in `../case-studies/`, tools live in their own repos, academic papers live in `~/Documents/cs*-aisecure/`, and NICE pathway PDFs live in `~/Documents/dod-cyber-pathways/`. This directory links them together so nothing falls through the cracks.

## How to navigate

| If you want to ... | Open ... |
|---|---|
| Understand the thesis we're testing | `PROGRAM.md` |
| See what surveys are done and what's next | `ROADMAP.md` |
| Find a specific survey by date or platform | `surveys/INDEX.md` |
| Understand which NICE role maps to which research activity | `roles/INDEX.md` |
| Find the academic citation for a threat class | `literature/INDEX.md` and `literature/threat-classes/` |
| See the state of a tool's design | `tools/INDEX.md` |
| Find the disclosure pipeline state for a target | `disclosures/INDEX.md` |
| Read a numbered methodology insight | `insights/INDEX.md` |

## The three layers

Every primary artifact (a survey, a tool, a finding) is indexed three ways:

1. **Research thread** — which insight or thesis does this evidence support? → `insights/`, `PROGRAM.md`
2. **NICE role + task** — which federal role definition does this work fit under, and which T-ID is the core task? → `roles/`
3. **Disclosure state** — if this is a finding worth disclosing, where is it in the pipeline? → `disclosures/`

A single Phoenix case study, for example, is listed in:
- `surveys/INDEX.md` (the date-indexed survey log)
- `insights/76-auth-permissive-cohort-default.md` (the thesis it supports)
- `roles/541-vulnerability-assessment-analyst.md` (the audit-report task it completes)
- `roles/422-data-analyst.md` (the dataset-analysis task)
- `disclosures/INDEX.md` (Northeastern, SENAI, et al. — pipeline state)
- `literature/threat-classes/llm02-sensitive-info-disclosure.md` (the OWASP category it maps to)

## Indexing discipline

- **Every index file stays under 200 lines.** Detail lives in linked files, not in indices.
- **One-line entries.** A survey entry is `- [2026-06-06 Phoenix](2026-06-06-phoenix.md) — 41/55 PROJECTS_UNAUTH, 34/55 USERS_UNAUTH. LLM02 class.`
- **No primary content in indices.** If you find yourself writing a paragraph in an INDEX file, it belongs in a sub-file.
- **Update at end of session.** SESSION.md tracks in-conversation state; indices track program state. Both updated when work concludes.

## Repo visibility

This directory is in `nuclide-research/AI-LLM-Infrastructure-OSINT`, a **public** repo. Therefore:

- **Operator names, contact details, and specific institutional identifiers** that already appear in case studies stay in case studies (they're already public there by Nick's choice).
- **Disclosure pipeline state** is tracked here at an abstraction level — target ID, severity, status — not contact methods or sensitive coordination details.
- **Personal contact details** for the researcher (Nicholas Kloster) are NOT placed here; the OSINT repo's contact policy is `nuclide-research.com` only.
- **Internal methodology notes** that aren't ready for public publication go to `~/.claude/nuclide-internal/`, not here.
