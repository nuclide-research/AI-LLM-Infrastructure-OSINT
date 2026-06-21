# ATLAS Technique (Sub-technique) Contribution

Form: atlas.mitre.org/contribute/submit?type=techniques
Maps field-by-field to the Technique submission form. Paste each block into the
matching field, then click Create File and attach the resulting .yaml to the email.

This is proposed as a SUB-TECHNIQUE of AML.T0070 RAG Poisoning. Note that intent in
the Additional Info field; the form does not have a dedicated parent-technique field,
so the relationship is stated in the summary and additional info.

---

## Contact Details

Contact Name(s): Nicholas Kloster (NuClide Research)
Contact Email(s): nicholas@nuclide-research.com

## Technique Details

Technique Name:
  Closed-Loop Oracle-Tuned RAG Poisoning  (sub-technique of AML.T0070 RAG Poisoning)

Technique Summary:
  AML.T0070 states that poisoned content may be "targeted such that it would always
  surface as a search result for a specific user query." That describes the outcome.
  This sub-technique describes the method an adversary uses to guarantee that outcome
  when they have query-time access to the deployed RAG system.

  The adversary treats the live retrieval interface as a black-box ranking oracle.
  They inject a candidate document, query the store for the target user phrasing, and
  read back the retrieval rank or similarity score. They then adjust the document,
  re-embed, re-upsert, and re-query, repeating until the injected record dominates the
  nearest-neighbor result for the target query. At that point retrieval is confirmed
  before any legitimate user is involved.

  This converts the probabilistic, blind injection assumed by prior work into
  deterministic, pre-confirmed injection. It also defeats detection designed for blind
  injection. Retrieval-distribution anomaly detection assumes the adversary cannot see
  retrieval, so a payload tuned until its score profile matches a native record reads
  as normal. Near-duplicate vector detection is evaded by tuning the payload to score
  high against user queries and low against existing documents, so the duplicate check
  passes. The enabling condition is an exposed or reachable retrieval interface
  (a search console, similarity-debug endpoint, or evaluation harness) that returns
  rank or score feedback to the caller.

## Associated Tactics

  Persistence  (consistent with parent AML.T0070)

## Associated Mitigations

  Restrict and Authenticate RAG Index Read and Write Interfaces  (submitted alongside
  this technique; removing the ranking oracle reverts the attack to blind placement)

## Technique References

  Reference Description: AML.T0070 RAG Poisoning (parent technique; names the targeted-
    retrieval outcome this sub-technique achieves deterministically)
  Reference Link: https://atlas.mitre.org/techniques/AML.T0070

  Reference Description: PoisonedRAG (models the adversary as blind post-injection;
    the oracle-tuned loop is the contrast this sub-technique formalizes)
  Reference Link: https://arxiv.org/abs/2402.07867

  Reference Description: OWASP Top 10 for LLM Applications, LLM04 Data and Model Poisoning
  Reference Link: https://genai.owasp.org/

## Additional Info

  Proposed as a sub-technique of AML.T0070 RAG Poisoning. The parent technique and its
  two current case studies (AML.CS0026, AML.CS0035) cover blind indirect injection,
  where content is placed in an indexed location and later retrieved. Neither involves
  a query-time ranking oracle. This sub-technique fills that gap: it names the
  iterative oracle-feedback loop that makes targeted retrieval deterministic rather
  than probabilistic. NuClide observed this method against an internet-exposed RAG
  stack and can provide a sanitized case study under responsible disclosure once the
  affected operator is notified and the exposure closed.
