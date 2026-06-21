# ATLAS Mitigation Contribution

Form: atlas.mitre.org/contribute/submit?type=mitigations
Maps field-by-field to the Mitigation submission form. Paste each block into the
matching field, then click Create File and attach the resulting .yaml to the email.

---

## Contact Details

Contact Name(s): Nicholas Kloster (NuClide Research)
Contact Email(s): nicholas@nuclide-research.com

## Mitigation Details

Mitigation Name:
  Restrict and Authenticate RAG Index Read and Write Interfaces

Mitigation Summary:
  Treat the retrieval-augmented-generation (RAG) data store and its query interface
  as critical functions that require authentication and network restriction.

  RAG poisoning depends on the adversary being able to write content into the data
  the system indexes. When the vector store or its ingestion path is reachable
  without authentication, any anonymous actor can insert a poisoned record with a
  single request. Require authentication on all write paths to the vector store,
  restrict those paths to internal networks, and keep an audit log of writes so
  inserted records are attributable and reviewable. Many production vector databases
  ship with no authentication and no write audit log in their default and
  getting-started configurations, so this control must be applied deliberately at the
  infrastructure layer rather than assumed.

  Separately, do not expose the retrieval or ranking interface (search consoles,
  similarity-debug endpoints, evaluation harnesses) to untrusted networks. An exposed
  query interface lets an adversary use the live system as a ranking oracle: they can
  read back which record the retriever selects for a given query and tune a poisoned
  document until it reliably wins retrieval before any legitimate user is involved.
  Removing that oracle does not by itself stop injection, but it forces the adversary
  back to blind, probabilistic placement, which restores the assumptions that
  retrieval-anomaly and near-duplicate detection rely on. Authenticate and rate-limit
  any retrieval interface that must remain reachable, and never surface raw retrieval
  rank or similarity scores to unauthenticated callers.

  In short: authenticate and network-restrict both the write path and the query path,
  log writes, and deny anonymous callers any retrieval-rank feedback.

## Associated Techniques

  AML.T0070  RAG Poisoning  (primary)
  AML.T0071  False RAG Entry Injection
  AML.T0066  Retrieval Content Crafting
  AML.T0064  Gather RAG-Indexed Targets

## References

  Reference Description: OWASP Top 10 for LLM Applications, LLM04 Data and Model Poisoning
  Reference Link: https://genai.owasp.org/

  Reference Description: PoisonedRAG, knowledge corruption attacks on RAG (models the
    adversary as blind post-injection; this mitigation also addresses the oracle-equipped case)
  Reference Link: https://arxiv.org/abs/2402.07867

  Reference Description: CWE-306 Missing Authentication for Critical Function
  Reference Link: https://cwe.mitre.org/data/definitions/306.html

## Additional Info

  AML.T0070 currently lists zero mitigations. This contribution proposes the first.
  It is drawn from field assessment of internet-exposed RAG stacks where the vector
  database, its admin UI, and a retrieval search console were all reachable without
  authentication on the same host. NuClide can provide a sanitized real-world case
  study demonstrating the oracle-tuned variant under responsible disclosure once the
  affected operator has been notified and the exposure closed.
