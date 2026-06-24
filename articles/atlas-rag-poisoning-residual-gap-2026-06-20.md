---
title: "The MITRE ATLAS Residual Gap: Closed-Loop Oracle-Tuned Retrieval-Rank Poisoning"
date: 2026-06-20
type: synthesis
summary: "ATLAS v5.6.0 covers the base RAG poisoning attack class via AML.T0070 and a full supporting cluster. The residual is narrow: no technique enumerates the closed-loop oracle-tuned variant that turns probabilistic injection into deterministic, pre-confirmed injection. We propose a sub-technique and anchor it to the Keystone ChromaDB worked example."
tags: [atlas, mitre, rag-poisoning, chromadb, keystone, inference-time, research, sub-technique]
featured: true
---

# The MITRE ATLAS Residual Gap: Closed-Loop Oracle-Tuned Retrieval-Rank Poisoning

**Date:** 2026-06-20
**Author:** NuClide Research
**Worked example:** Keystone (keyst.one), 43.153.169.169
**Classification:** CWE-306 (Missing Authentication for Critical Function) mapped to AML.T0070 RAG Poisoning, with a proposed sub-technique for the closed-loop oracle-tuned variant
**Status:** Verified 2026-06-20 against MITRE ATLAS v5.6.0 (release 2026.05, dated 2026-05-27; source github.com/mitre-atlas/atlas-data dist/ATLAS.yaml and atlas.mitre.org). The broad RAG/retrieval-context-poisoning gap is CLOSED by AML.T0070 RAG Poisoning, AML.T0071 False RAG Entry Injection, AML.T0066 Retrieval Content Crafting, AML.T0064 Gather RAG-Indexed Targets, AML.T0099, AML.T0080, and AML.T0051.001. The only residual gap is the closed-loop oracle-tuned retrieval-rank-optimization variant, which no single technique enumerates as its own method.

---

## Summary

We found an exposed RAG stack. Unauthenticated ChromaDB feeds a live customer-service pipeline running on DeepSeek. The base attack that follows from this exposure does have a home in MITRE ATLAS. As of ATLAS v5.6.0, verified 2026-06-20, AML.T0070 RAG Poisoning covers inference-time injection of malicious content into data indexed by a RAG system, and a full cluster around it covers the recon, content-authoring, and false-entry mechanics. Our earlier draft asserted that the attack class had no row on the matrix. That broad claim does not survive verification, and we retract it.

What does survive is narrow. AML.T0070 captures the outcome, that injected content can be targeted to always surface for a specific user query. It does not name the method by which the Keystone exposure makes that outcome deterministic: iteratively querying the live deployed RAG system as a black-box ranking oracle and tuning the injected document so it maximizes retrieval rank for a target query family. ATLAS also does not separately call out the unauthenticated-write, zero-credential path as the cheap delivery vector for that method. That residual is the finding. The base attack class is on the map; the closed-loop, oracle-tuned optimization that turns probabilistic injection into pre-confirmed injection is not enumerated as its own technique.

## What ATLAS is, and why it is the defender playbook

ATLAS (Adversarial Threat Landscape for Artificial-Intelligence Systems) is MITRE's extension of ATT&CK into the AI domain. It keeps the ATT&CK structure. Tactics, techniques, and procedures, scoped to attacks against machine learning systems.

Security teams use ATLAS the way they use ATT&CK. They build detection rules against technique IDs. They write threat hunt queries against coverage gaps. They design incident response playbooks per technique. They run coverage reviews that map their detections to the matrix and report a percentage.

The matrix is the map. If a technique is in ATLAS, defenders know to look for it. If a technique is not in ATLAS, they do not know the attack class exists. The map sets the field of view. That is why the precise question for this analysis is not whether RAG poisoning is on the map. It is. The question is whether the specific oracle-tuned method is enumerated as its own row, or whether it hides inside the more general AML.T0070 description.

## The taxonomy as it stands, and what it already covers

ATLAS organizes attacks along the ML system lifecycle. Reconnaissance, Resource Development, ML Attack Staging, Initial Access, ML Model Access, Exfiltration, Impact.

As of v5.6.0, verified 2026-06-20, the matrix carries a dedicated cluster for RAG and retrieval-context poisoning. The on-point technique is AML.T0070 RAG Poisoning. Its description: adversaries may inject malicious content into data indexed by a retrieval augmented generation (RAG) system to contaminate a future thread through RAG-based search results, and the content may be targeted such that it would always surface as a search result for a specific user query. That is squarely inference-time retrieval-context poisoning. The supporting techniques are:

- **AML.T0070 RAG Poisoning.** The core inference-time technique. Injects malicious content into RAG-indexed data to contaminate a future thread through retrieval results; content may be targeted to always surface for a specific user query; may include prompt injections or false RAG entries.
- **AML.T0071 False RAG Entry Injection.** Introduces false document entries into a victim RAG database so the LLM treats retrieved content as a genuine RAG result. Embedding false docs inside regular entries bypasses data-monitoring tools and resists direct deletion, and allows metadata manipulation (title, author, date).
- **AML.T0066 Retrieval Content Crafting.** The content-authoring half. Crafting content designed to be retrieved by user queries to influence the user, abusing trust in the system, explicitly including getting crafted content into a vector database used in a RAG system.
- **AML.T0064 Gather RAG-Indexed Targets.** The reconnaissance technique. Identifying the external data sources a RAG system indexes, including by interacting with the system directly and observing references to external data.
- **AML.T0099 AI Agent Tool Data Poisoning.** The agent-tool analogue. Placing malicious content where it is retrieved by an AI agent tool, targeted to be retrieved by common queries, and may include prompt injections.
- **AML.T0080 AI Agent Context Poisoning**, with sub-techniques AML.T0080.000 Memory and AML.T0080.001 Thread. Manipulating the context an agent's LLM uses to persistently change behavior.
- **AML.T0051.001 LLM Prompt Injection: Indirect**, the sub-technique of AML.T0051 LLM Prompt Injection. Prompts injected via a separate data channel the LLM ingests, including text pulled from databases or websites, hidden from the user. This is the indirect-injection-via-retrieved-content variant adjacent to RAG poisoning.

For the retrieval-side abuses that bracket poisoning, ATLAS also carries AML.T0082 RAG Credential Harvesting and AML.T0085.000 Exfiltration via AI Service / RAG Databases. Those are read-side theft, not poisoning, and we name them only to keep the boundary clean.

### ID correction

Our earlier draft treated AML.T0020 Poison Training Data as the nearest technique to the Keystone case, and loose web references conflated RAG poisoning with AML.T0020. Both are wrong. AML.T0020 is confirmed in ATLAS.yaml v5.6.0, but its scope is training and fine-tuning data poisoning via supply chain or post-access modification, activated by a backdoor trigger (AML.T0043.004). It does not cover inference-time RAG or retrieval poisoning. The technique that covers inference-time RAG poisoning is AML.T0070. Indirect prompt injection is AML.T0051.001, a sub-technique of AML.T0051, not a standalone AML.T number. AI Agent Context Poisoning is AML.T0080 with sub-techniques .000 Memory and .001 Thread. We correct all of these below and do not cite AML.T0020 as the technique that would cover the RAG surface.

## Where AML.T0070 stops, and the residual begins

AML.T0070 captures the outcome of a targeted RAG poisoning attack: the injected content can be tuned so it always surfaces as a search result for a specific user query. AML.T0064 captures direct interaction with the system to identify targets. What neither names is the method that connects the two in the Keystone case: a closed feedback loop in which the adversary queries the live deployed RAG system as a black-box ranking oracle and tunes the injected document's embedding and wording to maximize its retrieval rank for a target query family before any real user ever queries the system.

AML.T0070 describes the destination. It does not describe the oracle-feedback optimization that makes arrival deterministic instead of probabilistic. That optimization loop is the residual gap.

The other half of the residual is the delivery path. The Keystone exposure makes the whole loop free. The vector store is unauthenticated (CWE-306), so injection requires no credentials, and a second console gives a query interface against the same store, so the rank oracle is handed to the attacker. ATLAS does not separately enumerate this unauthenticated-write, zero-credential path as the cheap carrier for retrieval-rank optimization. It is implied by the general technique, but it is not called out as its own delivery primitive.

## RAG is an inference-time surface, and the cluster already reflects that

ATLAS was originally built around two attack surfaces. The model itself, meaning adversarial examples, model inversion, membership inference, and backdoors baked into the weights. And the ML pipeline, meaning poisoning the dataset before training, and supply chain compromise. AML.T0020 lives in that second surface.

RAG does not work that way, and the current matrix has caught up to it. The AML.T0070 cluster is explicitly an inference-time, data-layer set of techniques. The diagrams below show where each lives.

Here is the traditional ML attack surface. AML.T0020 lives at the training-data step.

```
TRADITIONAL ML

  Training Data  ->  Training Run  ->  Model Weights  ->  Inference
       ^
       |
  AML.T0020 lives here (pre-deployment, modifies the artifact)
```

Here is the RAG attack surface. As of ATLAS v5.6.0, verified 2026-06-20, the vector-store and retrieval steps are covered.

```
RAG

  Vector Store  ->  Retrieval  ->  LLM Context Window  ->  Output
       ^               ^
       |               |
  AML.T0066 /     AML.T0070 RAG Poisoning covers this surface
  AML.T0071       AML.T0051.001 indirect prompt injection rides
  write the doc   the retrieved content into the context window

  RESIDUAL: no single technique names the closed-loop oracle-tuned
  rank-optimization method that uses the live system as a ranking
  oracle, nor the unauthenticated zero-credential write path.
```

The model weights are never touched. The training pipeline is never touched. The attack happens at inference time, in the data layer that feeds the context window. The base technique for that is on the map. The optimization method that turns it deterministic is the part still missing.

## What the residual means in practice

The residual is narrower than a missing attack class, but it still propagates through the defensive functions that consume the matrix, because detection content is usually keyed to technique IDs and a method with no ID gets no dedicated rule.

**Detection engineers.** A team that maps to AML.T0070 may write detections for anomalous writes to the vector store. Fewer teams will have content keyed to the closed-loop signature specifically: high-frequency query-then-write cycles from one source, which is the tell of oracle tuning. That behavior is implied by AML.T0070 but is not its own row, so it is easy to miss when building per-technique detections.

**Threat hunters.** Hunt programs that walk the matrix row by row will now find AML.T0070 and can build a hunt for RAG store poisoning. They are less likely to build a hunt for the oracle-feedback loop as a distinct hypothesis, because the matrix does not separate it. The general hunt may run; the specific one may not be scoped.

**Incident response teams.** A playbook can now be organized under AML.T0070 for RAG poisoning. What the playbook will not get from the matrix is the triage step that separates a blind one-shot injection from a pre-confirmed, rank-tuned injection. Those have different evidence trails. The blind case leaves one write. The oracle-tuned case leaves a burst of paired query-and-write traffic before the payload lands.

**Blue-team coverage reviews.** A team mapping detections to ATLAS can now report coverage of AML.T0070 honestly. The risk is the inverse of the old one. A team can show green on RAG Poisoning and still have no coverage of the oracle-tuned variant, because the variant is not a separate row to be marked uncovered. Coverage of the general technique can read as coverage of the strongest form of it. That is the false-assurance risk that remains, scoped now to the method rather than the whole class.

## Why the residual is the part worth proposing

Most taxonomy work at this point is refinement, not discovery. The base class is documented. The community understands RAG poisoning as a distinct class, and the v5.6.0 cluster reflects that. What the literature and the matrix both under-specify is the closed-loop, oracle-tuned form.

| | Training Data Poisoning | RAG Store Poisoning | Closed-Loop Oracle-Tuned RAG Poisoning |
|---|---|---|---|
| Access required | Pipeline access | DB write access | DB write access plus a query/rank oracle |
| Effect timing | Delayed (next retrain) | Immediate (next query) | Immediate, and pre-confirmed before any real query |
| Reversibility | Hard (retrain) | Easy (delete record) | Easy (delete record) |
| Detectable via model auditing | Yes | No | No |
| Mitigated by data provenance | Yes | No | No |
| Injection certainty | Deterministic at train time | Probabilistic at retrieval time | Deterministic at retrieval time |
| ATLAS coverage | AML.T0020 | AML.T0070 and cluster | Not enumerated as its own method (residual) |

The first two columns are well-covered. The third is the one ATLAS does not separately name. A defender who maps to AML.T0070 and stops there has scoped the probabilistic case. The oracle-tuned case is a stronger threat model with a different evidence trail, and it is the column without a row.

## The closed-loop variant in detail

Prior art exists. PoisonedRAG, published in 2023, gave researchers a theoretical model for injecting malicious documents into a retrieval corpus. That work assumed blind injection. The attacker writes a poisoned document and hopes it gets retrieved for the target query class. Probabilistic.

The Keystone exposure removes the blindness. A second console on port 5050 is a retrieval-rank oracle. With a query interface against the same vector store, the attacker stops guessing. They inject a document, query the store, read the rank, adjust the document, and repeat until the injected record dominates the nearest-neighbor search for the target query. Probabilistic injection becomes deterministic, pre-confirmed injection. The attacker knows the payload will be retrieved before any real user ever queries the system.

The oracle also defeats the detection built for blind injection. Two approaches dominate the literature, and both assume the attacker cannot see retrieval. Anomaly detection on the retrieval distribution flags a document that surfaces too often or scores too high for queries it should not match. A blind payload embeds unevenly and trips it. An oracle-tuned payload is shaped until its score profile across query phrasings matches a native record, so nothing reads as anomalous. Near-duplicate vector detection flags an ingested document that sits too close to an existing one. An oracle-tuned payload is shaped to score high against user queries and low against existing documents, so the duplicate check passes clean. Without the oracle the attacker fires into a dark room and adjusts by ear. With it they have a rangefinder and a display of every shot. They center the crosshairs, fire once, and leave. That is the methodological difference the residual sub-technique is meant to capture.

This oracle-enabled tuning loop is not enumerated in ATLAS as a distinct method as of v5.6.0, verified 2026-06-20, and it is not isolated as a distinct variant in the research literature. AML.T0070 captures the outcome it produces. AML.T0064 captures direct interaction with the system for target identification. Neither captures the iterative rank-optimization loop itself. That is the precise shape of the residual gap.

## Proposed sub-technique (our proposal)

We propose the following as a sub-technique under AML.T0070 RAG Poisoning. This is our proposal. It is not an accepted ATLAS entry.

**Sub-technique: Closed-Loop Oracle-Tuned Retrieval-Rank Poisoning**

**Parent:** AML.T0070 RAG Poisoning

**Tactic:** Impact / ML Attack Staging

**Description.** Adversaries with both a write path into a RAG vector store and a query interface against that same store can treat the live deployed system as a black-box ranking oracle. They inject a candidate document, query the store, observe the retrieval rank of the injected record for a target query family, adjust the document's wording or embedding, and repeat until the injected record reliably dominates the nearest-neighbor search for that query family. This converts the probabilistic injection of the parent technique into deterministic, pre-confirmed injection: the adversary verifies retrieval before any real user query runs. When the vector store is unauthenticated (CWE-306), the write path and, frequently, the query oracle require no credentials, which makes the entire optimization loop free to run.

**Relationship to existing techniques.** This sub-technique optimizes the delivery of AML.T0070 and reuses the content-authoring of AML.T0066 and the recon of AML.T0064. It is distinguished by the iterative oracle-feedback loop and by the use of the live deployed system as the ranking oracle, neither of which the parent or its siblings name as a method.

**Mitigations.**
- Authenticate vector store write endpoints and any query or test console that targets the same store, so the rank oracle is not handed to an unauthenticated party.
- Maintain document provenance and change logging on the retrieval corpus.
- Rate-limit and monitor for paired query-and-write cycles from a single source, which signal oracle tuning.
- Validate retrieved context against known-good snapshots.

**Detection.**
- Unexpected records in vector collections, surfaced as metadata anomalies.
- Unauthenticated write attempts to vector DB APIs.
- High-frequency query-plus-write cycles from a single source, which signal closed-loop tuning and are the signature that distinguishes this sub-technique from a blind one-shot AML.T0070 injection.

As of ATLAS v5.6.0, verified 2026-06-20, this oracle-tuned method is not enumerated as its own technique or sub-technique. That is the residual gap.

## The worked example: Keystone

Keystone (keyst.one) at 43.153.169.169 grounds every point above in a live system.

The stack exposes three unauthenticated ports. ChromaDB serves on its default HTTP port with no authentication. It backs a live RAG pipeline that feeds a DeepSeek customer-service flow. We confirmed the core write primitive end to end. We read the store. We wrote a single marked canary record, then deleted it. We confirmed delete and tenant creation. We confirmed that the live pipeline executes against the store we can write to. That write-into-a-RAG-store primitive maps to AML.T0070 RAG Poisoning and, given the unauthenticated path, to CWE-306.

A second exposed console on port 5050 acts as the retrieval-rank oracle. It is the query interface that turns the blind PoisonedRAG model into the closed-loop variant described above. The two exposures together are the full closed-loop primitive: a write path into the retrieval corpus and an oracle that confirms rank before any real query runs. That oracle-tuned loop is the part of the chain that the current matrix does not enumerate as its own method.

We exercised restraint. We did not poison production. We did not inject any record that a real user would retrieve. The only write was a single canary that we marked and then deleted. No user received attacker-controlled output. We did not harm users. The point was to confirm the primitive, not to operate it. NuClide's prior disclosure work, including CVE-2025-4364 and ICSA-25-140-11, follows the same restraint ethic: confirm severity with the minimum touch, then stop.

## Closing

The matrix has moved with the architecture. ATLAS v5.6.0, verified 2026-06-20, carries a dedicated RAG and retrieval-context poisoning cluster: AML.T0070, AML.T0071, AML.T0066, AML.T0064, AML.T0099, AML.T0080, and AML.T0051.001. The broad gap our earlier draft claimed does not hold, and we retract it. The base attack class is on the map.

What remains is narrow and worth proposing. AML.T0070 names the outcome of targeted RAG poisoning but not the closed-loop, oracle-tuned method that makes the outcome deterministic, and the matrix does not isolate the unauthenticated, zero-credential write path that makes that method free to run. The Keystone exposure puts both in one host. We propose a sub-technique under AML.T0070 to enumerate the oracle-tuned variant, and we anchor it to the live evidence. The residual gap, as verified on 2026-06-20, is the optimization method, not the attack class.
