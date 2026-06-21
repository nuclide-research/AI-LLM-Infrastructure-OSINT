# MITRE ATLAS Contribution Plan

Date: 2026-06-20
Author: Nicholas Kloster / NuClide Research
Source material: `analysis/2026-06-20-atlas-gap-inference-time-rag-poisoning.md`,
`assessments/keystone-keyst.one-disclosure-report-2026-06-20.md`

## How ATLAS contributions actually work (verified live 2026-06-20)

The form at `atlas.mitre.org/contribute/submit?type=<type>` is a structured YAML
generator. You fill the sections, click **Create File** to download a `.yaml`,
then email that file as an attachment to **atlas@mitre.org**. There is no in-page
submit. The contribution IS an email to atlas@mitre.org with the file attached.

Contribution types and their forms:
- Tactic     -> `?type=tactics`
- Technique  -> `?type=techniques`
- Mitigation -> `?type=mitigations`
- Case Study -> `?type=studies`
- General    -> `?type=other`
- Suggest edit -> `?action=edit`

Each contribution is credited (name or alias) when accepted.

## What we have, and what fits

Primary source check on AML.T0070 RAG Poisoning (live, v2026.05, modified 2026-05-27):
- Tactic: Persistence. Maturity: Demonstrated. Platforms: Agentic AI, Generative AI.
- Case studies: 2 (AML.CS0026 Zenity M365 Copilot, AML.CS0035 PromptArmor Slack AI).
  Both are blind indirect-injection. Neither has a query-time ranking oracle.
- Mitigations: 0. The technique currently has NO mitigations attached.
- Description names the OUTCOME ("content targeted such that it would always surface
  as a search result for a specific user query") but not the METHOD that guarantees it.

| Contribution | Fit | Names a target? | Send now? |
|---|---|---|---|
| Mitigation for AML.T0070 | Standout. T0070 has 0 mitigations and MITRE wants them. | No | YES |
| Sub-technique of AML.T0070 (closed-loop oracle-tuned rank optimization) | Strong. Names the method T0070 omits. | No | YES |
| Case study (Keystone) | Novel: first oracle-equipped RAG poisoning. | YES (operator IP + identity) | NO. Gates behind vendor disclosure + remediation, or full anonymization. |

## Decision

Two contributions are clean to send immediately because neither names the operator
or any live target. They are our own method and mitigation research:

1. `contribution-mitigation-rag-interfaces.md`  -> Mitigation form
2. `contribution-subtechnique-closed-loop-oracle-tuned.md` -> Technique form

The Keystone case study is held. ATLAS case studies are public. Submitting one with
the operator named, before the operator is notified and the exposure is closed, is
public disclosure of a live finding. Sequence: disclose to Keystone -> remediation
confirmed -> then submit the case study (or submit anonymized if the operator declines
attribution). Draft case study is NOT written yet by design; it follows disclosure.

## Send checklist (each step holds for Nick's explicit go)

- [ ] Fill Mitigation form with `contribution-mitigation-rag-interfaces.md`, Create File
- [ ] Fill Technique form with `contribution-subtechnique-closed-loop-oracle-tuned.md`, Create File
- [ ] Email both .yaml files to atlas@mitre.org using `cover-email-atlas-mitre.md`
- [ ] (post-disclosure) Author + submit Keystone case study

Contact block for the forms (Nick's public researcher identity):
- Contact Name: Nicholas Kloster (NuClide Research)
- Contact Email: nicholas@nuclide-research.com
