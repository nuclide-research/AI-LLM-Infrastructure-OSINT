---
type: case-study
severity: CRITICAL
date: 2026-06-20
title: "Keystone Hardware Wallet: Unauthenticated Control of the AI Customer-Service Knowledge Base"
summary: "Keystone's AI support chatbot for 6,907-record knowledge base was fully open: read, write, delete, and live LLM execution as official Keystone support. The novel finding is a closed-loop oracle: an open RAG console on a second port let an attacker tune poisoned records by watching retrieval scores in real time, converting blind injection into a verified, ranked attack before any user query ever lands."
tags:
  - chromadb
  - rag-poisoning
  - vector-database
  - cwe-306
  - llm04
  - atlas-aml-t0070
  - cryptocurrency
  - hardware-wallet
abstract: "Keystone deployed their AI support chatbot backend with no authentication on any component. Three services -- ChromaDB vector store, Flask RAG console, ChromaDB admin UI -- were each publicly reachable. The novel risk: the open console enabled oracle-tuned RAG poisoning, converting the standard blind-injection problem into a confirmed, ranked attack. Disclosed 2026-06-20."
sidenotes:
  - kind: host
    label: Target
    kv:
      - k: Operator
        v: "Keystone (keyst.one)"
      - k: Sector
        v: "Cryptocurrency / Hardware Wallet"
      - k: Location
        v: "Shenzhen, CN (Tencent Cloud)"
      - k: Disclosed
        v: "2026-06-20"
      - k: Severity
        v: CRITICAL
  - kind: see-also
    label: Classification
    kv:
      - k: Primary
        v: "CWE-306 Missing Authentication for Critical Function"
      - k: Secondary
        v: "CWE-284 Improper Access Control"
      - k: OWASP
        v: "LLM04 Data and Model Poisoning"
      - k: ATLAS
        v: "AML.T0070 RAG Poisoning"
---

# Keystone Hardware Wallet: Unauthenticated Control of the AI Customer-Service Knowledge Base

_NuClide Research -- Nicholas Kloster -- 2026-06-20_

---

## Summary

Keystone's AI customer-service system ran on a public server with no authentication on any component. Anyone on the internet could read, change, or erase the entire knowledge base that powers Keystone's official support chatbot. A second open service let that same person watch their changes take effect in real time before any real customer saw them.

The customers at risk are the ones who bought a Keystone wallet to take custody seriously. The topic at risk is seed-phrase recovery -- the one where a wrong answer drains a wallet. The chatbot answers as Keystone official support. A customer has no way to tell a tampered answer from a real one.

We confirmed full read, write, delete, and live answer generation. We reversed every change we made.

---

## Attack Surface

Three services. Three roles. Zero authentication. One host.

| Port | Software | Role | Auth |
|------|----------|------|------|
| 8000 | ChromaDB 1.0.0 | RAG vector database -- 6,907-record knowledge base | None |
| 5050 | Flask / Werkzeug 3.1.8 | Live RAG console: retrieval + DeepSeek answering as Keystone support | None |
| 8080 | nginx / React SPA | ChromaDB admin UI, hardcoded to port 8000 | None |

Port 8000 stored the data. Port 5050 read that data and produced answers. Port 8080 was a graphical front door. None of them asked who was calling.

---

## Knowledge Base Contents

The store held two collections.

| Collection | Records | Content |
|------------|---------|---------|
| keystone_knowledge_base | 6,155 | Product docs, integration guides, security explainers, seed-phrase guidance |
| keystone_article_style | 752 | Editorial and marketing content, English and Chinese |

The highest-risk slice was small: 46 records in `guide/seed_phrase` and 54 records in `guide/security`. These are the records the chatbot reads when a customer asks how to recover a wallet.

---

## What We Confirmed

**Read:** Pulled all 6,907 records without credentials.

**Write:** Inserted a marked canary record (`nuclide-research-poc-001`) into the knowledge base. Wrote with a real `intfloat/multilingual-e5-large` embedding to confirm proper storage. Also confirmed that a plain zero vector writes successfully -- the operator's embedding model is not required to inject.

**Delete:** Removed the canary. Verified deletion by re-querying for the ID, which returned an empty `ids` list.

**Infrastructure write:** Created a tenant (`nuclide-poc-tenant`) and database (`poc-db`), then removed both.

**Live pipeline:** Queried `/api/search` on port 5050 with "seed phrase recovery." Retrieved top score 0.844. DeepSeek answered as official Keystone support: "您好，我是 Keystone 硬件钱包的官方客服" (Hello, I am the official customer service of Keystone hardware wallet).

Every test artifact we created we removed.

---

## The Novel Finding: Closed-Loop Oracle-Tuned RAG Poisoning

Prior RAG-poisoning research (PoisonedRAG 2024, OWASP LLM04) models the attacker as blind after injection: write a record and hope it surfaces. The retrieval rank is invisible. The attacker guesses at embedding-space geometry with no feedback.

Port 5050 removed the blindness.

```
BLIND INJECTION  (all prior work)
  attacker writes -> hopes it ranks -> no feedback -> user eventually hits it

CLOSED-LOOP  (this finding)
  attacker writes -> queries :5050 -> sees rank and score ->
  revises -> queries again -> sees improved rank ->
  stops when rank 1, score confirmed dominant ->
  injection is verified before any user is in the loop
```

This converts a probabilistic guess into a hill-climbing optimization against the live retrieval pipeline. The attacker tunes the payload until it wins the target query, then stops. The confirmed score is 0.844 against "seed phrase recovery." The verified-dominant payload is the one a customer receives next time they ask.

Detection methods built for blind injection break here. Anomaly detection on retrieval distribution flags documents that surface too often or score too high for mismatched queries -- a signature of blind payloads that embed unevenly. An attacker with the oracle tunes the document until its score profile matches a native record. Statistical anomaly detection passes clean. Near-duplicate vector detection expects injected content to cluster near existing records. An oracle-tuned payload avoids that too: score high for target queries, low against existing documents. The check passes.

ATLAS AML.T0070 (RAG Poisoning) covers inference-time injection targeted to surface for a specific query. What no single technique in the current ATLAS matrix names is the closed-loop oracle-tuning step -- querying the live system as a ranking oracle and confirming the payload wins before any user is in the loop. The sub-technique gap is documented in our ATLAS contribution.

---

## Attack Chain

```
[1] Anonymous POST to :8000           single request, no auth, ~200ms, attacker leaves
[2] Wait                              attacker has zero presence on the host
[3] User queries the Keystone chatbot the user triggers it, not the attacker
[4] Financial loss                    irreversible, on-chain
```

No persistence. No C2. No malware. No victim contact with attacker infrastructure. No attacker presence at the moment of harm.

The attacker spent roughly thirty seconds. The customer's loss is permanent. The asymmetry is total.

ChromaDB's default configuration does not log individual writes. The attack may leave no log entry at all. First indication would be a customer reporting a loss after following chatbot advice -- and they may never connect the chatbot to the outcome.

---

## Impact

**Direct:** Anonymous read, write, and delete on the knowledge base backing an official support channel for a security-focused hardware wallet brand. Tampered recovery guidance can cause direct, irreversible financial loss for customers who act on it.

**Indirect:** Full read exfiltrates Keystone's 6,155-record corpus including proprietary Chinese and English editorial content still under development. Delete access removes legitimate guidance quietly, with no alert and no audit trail. Unauthenticated generation endpoints allow unlimited inference against Keystone's DeepSeek API key.

**Trust:** A self-custody hardware wallet brand sells trust as the product. An official support channel made to hand out attacker-controlled recovery instructions damages exactly that asset, whether or not any individual loss is ever traced back to the channel.

---

## Remediation

**Immediate (no code change required):** Firewall ports 8000, 5050, and 8080 to internal network only.

**Short-term:** Enable ChromaDB's built-in token authentication. Add audit logging. Rotate any credentials that may have been exposed through the open console.

**Medium-term:** Canary records in production vector stores to detect unauthorized writes. Periodic retrieval-distribution monitoring to detect ranking anomalies.

---

## Disclosure

Disclosed to eng@keyst.one and support@keyst.one on 2026-06-20 under NuClide Research responsible-disclosure practice. Prior coordinated disclosures from this researcher include CVE-2025-4364 and ICSA-25-140-11, both through CISA.
