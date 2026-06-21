To: atlas@mitre.org
Subject: Contribution: first mitigation for AML.T0070 RAG Poisoning, plus a closed-loop sub-technique

Attachments:
  contribution-mitigation.yaml   (generated from the Mitigation form)
  contribution-technique.yaml    (generated from the Technique form)

---

Hello ATLAS team,

We are NuClide Research, an independent security research practice. Our prior
coordinated disclosures include CVE-2025-4364 and ICSA-25-140-11, both handled
through CISA. We work on the security of exposed AI and LLM infrastructure, and we
have two contributions for AML.T0070 RAG Poisoning.

First, a mitigation. AML.T0070 currently lists no mitigations. The attached
mitigation proposes the first: authenticate and network-restrict both the write path
and the query path of the RAG data store, log writes, and deny unauthenticated
callers any retrieval-rank feedback. It is drawn from field assessment of
internet-exposed RAG stacks where the vector database and a retrieval search console
were both reachable without authentication.

Second, a sub-technique. AML.T0070 says poisoned content may be targeted so that it
"would always surface as a search result for a specific user query." That names the
outcome. The attached technique names the method that guarantees it when the adversary
has query-time access: the live retrieval interface is used as a black-box ranking
oracle, and the injected document is tuned until it wins retrieval before any
legitimate user is involved. This converts the blind, probabilistic injection that the
two existing case studies (AML.CS0026, AML.CS0035) illustrate into deterministic,
pre-confirmed injection, and it defeats detection built for the blind case. We propose
it as a sub-technique of AML.T0070.

We also have a real-world case study of the oracle-tuned variant against a production
RAG support system. We are coordinating disclosure with the affected operator first.
Once they are notified and the exposure is closed, we would be glad to submit a
sanitized case study so the technique has a documented real-world example.

We are happy to revise framing, IDs, or scope to fit the ATLAS data model. Thank you
for maintaining ATLAS.

Nicholas Kloster
NuClide Research
nicholas@nuclide-research.com
