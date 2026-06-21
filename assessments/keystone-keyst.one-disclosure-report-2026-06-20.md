# Keystone Hardware Wallet: Unauthenticated Control of the AI Customer-Service Knowledge Base

| Field | Value |
|-------|-------|
| **Target** | Keystone (keyst.one), hardware cryptocurrency wallet manufacturer |
| **IP** | 43.153.169.169 (Tencent Cloud) |
| **Date** | 2026-06-20 |
| **Severity** | Critical |
| **Researcher** | Nicholas Kloster, NuClide Research, nicholas@nuclide-research.com |
| **Classification** | CWE-306 Missing Authentication for Critical Function (primary), CWE-284 Improper Access Control (secondary), OWASP LLM Top 10 2025 LLM04 Data and Model Poisoning |
| **Status** | Confirmed |

---

## Executive Summary

Keystone's AI customer-service system runs on a public server with no password on any part of it. Anyone on the internet can read, change, or erase the entire knowledge base that powers Keystone's official support chatbot, and a second open service lets that same person watch their changes take effect before any real customer sees them. The customers at risk are the ones who bought a Keystone wallet precisely because they hold real crypto and take key custody seriously, and the topic at risk is the one where a wrong answer drains a wallet: seed phrase recovery. The chatbot answers as Keystone official support, so a customer has no way to tell a tampered answer from a real one. We confirmed full read, write, delete, and live answer generation with our own evidence, and we removed every test artifact we created. The first fix takes one firewall change today and no code change.

---

## Operator and Scope

**Keystone builds hardware wallets for people who take custody seriously, and this server answers their support questions.**

Keystone is a Shenzhen-based hardware wallet manufacturer. The flagship Keystone 3 Pro is air-gapped, moves data only by QR code, carries a triple secure element rated CC EAL5+, and ships open-source firmware. The company sells to a customer base that is security-conscious by definition. These users paid for a hardware wallet precisely because they treat private-key custody as the thing that must not fail.

The exposed host backs a customer-facing AI chatbot. The chatbot answers questions about seed phrases, wallet recovery, private-key handling, multisig setup, and blind signing. The knowledge base behind it carries 6,907 records across two collections, in English and Chinese.

We discovered the host through infrastructure reconnaissance for exposed AI and vector-database services. We attributed it to Keystone from the data itself: collection names `keystone_knowledge_base` and `keystone_article_style`, content that references the Keystone product line, source URLs pointing at `blog.keyst.one`, and the chatbot's own persona prompt, which opens every answer as "Keystone official customer service."

This work was conducted under NuClide Research's responsible-disclosure practice. We enumerated the exposed surface, confirmed each finding with the minimum action needed to prove it, and reversed every change we made. Prior coordinated disclosures from this researcher include CVE-2025-4364 and ICSA-25-140-11, both handled through CISA.

---

## Attack Surface

**Three services, three roles, zero authentication, one host.**

| Port | Software | Role | Auth |
|------|----------|------|------|
| 8000 | ChromaDB 1.0.0 | RAG vector database, holds the full knowledge base | None |
| 5050 | Flask on Werkzeug 3.1.8, Python 3.12.3 | Live RAG console: retrieve, then answer via DeepSeek as Keystone support | None |
| 8080 | nginx/1.28.1, React SPA built 2026-01-03 | ChromaDB admin UI, hardcoded to the instance on 8000 | None |

SSH on port 22 is the only other open port. A port sweep confirmed exactly four open ports. This is a dedicated AI chatbot backend.

The three services line up as a complete loop. Port 8000 stores the data. Port 5050 reads that data and turns it into an answer. Port 8080 is a graphical front door to the store. None of them ask who is calling.

---

## Findings

### Finding 1: Full read, write, and delete on the ChromaDB vector store (port 8000)

| Attribute | Value |
|-----------|-------|
| Service | ChromaDB 1.0.0, API v2 (multi-tenant) |
| Weakness | CWE-306 Missing Authentication for Critical Function |
| Auth state | None |
| Confirmed access | Read all records, write a record, delete a record, create a tenant, create a database |
| Severity | Critical |

The store holds two collections.

| Collection | ID | Records | Dimensions | Content |
|------------|----|---------|------------|---------|
| keystone_knowledge_base | 8ea8b4cb-ec2d-463f-a2bd-a335e1c98d27 | 6,155 | 1024 | Product docs, integration guides, security explainers, seed-phrase guidance |
| keystone_article_style | 001c74f8-135d-4455-9ce6-cc096755b649 | 752 | 1024 | Editorial and marketing content, English and Chinese |

The knowledge base is the high-value target, and its highest-risk slices are small and specific. We confirmed the category breakdown with a full sweep.

| Category | Records | Note |
|----------|---------|------|
| guide/wallet_integration | 851 | MetaMask, Sparrow, Rabby, Solflare integration guides |
| blog/security_explainer | 747 | User security education |
| blog/technical_deep_dive | 699 | Deep technical content |
| guide/seed_phrase | 46 | Highest risk: seed phrase, mnemonic, Shamir backup |
| guide/security | 54 | Highest risk: security-hardening guidance |

Those 100 records in `guide/seed_phrase` and `guide/security` are the ones the chatbot reads when a customer asks how to recover a wallet. They are the smallest categories in the corpus and the most dangerous to tamper with.

**The embedding-model documentation error.** The collection schema labels the embedding model as `paraphrase-multilingual-MiniLM-L12-v2` at 384 dimensions. That label is wrong. The live dimension is 1024, and our PoC confirmed the operator runs `intfloat/multilingual-e5-large`. Embeddings from that model match the corpus and writes succeed. A write also succeeds with a plain zero vector, so reproducing the operator's model is not even required to add a record. The mislabel is a documentation error, not a control.

We read all 6,907 records without credentials. We then proved write by inserting one record, clearly marked as a NuClide Research canary, into the store. We deleted that record and confirmed by a follow-up read that it was absent. We also proved infrastructure-level write by creating a tenant named `nuclide-poc-tenant` and a database named `poc-db`, then removing them. Every test object we created we removed.

A note on identifiers, so a triager can reproduce cleanly. Our standalone PoC targets `keystone_knowledge_base` (collection `8ea8b4cb-ec2d-463f-a2bd-a335e1c98d27`) with the marked record `nuclide-research-poc-001`, carrying a real `multilingual-e5-large` embedding. An earlier manual confirmation used `keystone_article_style` (collection `001c74f8-135d-4455-9ce6-cc096755b649`) with the canary `nuclide-canary-2026` and a zero vector. Both writes were unauthenticated, both were deleted, and both deletions were verified by a follow-up read returning an empty `ids` list. Use the PoC identifiers as the load-bearing reference.

**Evidence.** Write returned success on a marked record. Delete returned `{"deleted": 1}`. The verifying read returned an empty `ids` list, confirming the record was gone.

```bash
BASE="http://43.153.169.169:8000/api/v2/tenants/default_tenant/databases/default_database"
COLL="8ea8b4cb-ec2d-463f-a2bd-a335e1c98d27"   # keystone_knowledge_base

# READ: pull records, no credentials
curl -s -X POST "$BASE/collections/$COLL/get" \
  -H "Content-Type: application/json" \
  -d '{"limit": 10, "include": ["documents", "metadatas"]}'

# VERIFY DELETE: after removing the canary, this returns ids: []
curl -s -X POST "$BASE/collections/$COLL/get" \
  -H "Content-Type: application/json" \
  -d '{"ids": ["nuclide-research-poc-001"]}'
```

### Finding 2: Live RAG console and LLM execution as Keystone official support (port 5050)

| Attribute | Value |
|-----------|-------|
| Service | Flask RAG console, title "ChromaDB 客服测试台" (ChromaDB Customer Service Test Console) |
| Weakness | CWE-306 applied to a live inference pipeline |
| Auth state | None |
| Confirmed access | Live query, retrieval scoring, DeepSeek answer in the Keystone support persona |
| Severity | Critical |

This is not a static test page. It is the live production RAG pipeline exposed as a developer console. A POST to `/api/search` embeds the caller's query, retrieves the top matches from `keystone_knowledge_base` by cosine similarity, passes that context to DeepSeek, and returns an answer that speaks as Keystone's official customer service.

We ran it. A query for "seed phrase recovery" returned a top retrieval score of 0.844 and surfaced the record "Never Share Your 24-Word Recovery Phrase." DeepSeek answered in character, opening with "您好，我是 Keystone 硬件钱包的官方客服" ("Hello, I am the official customer service of Keystone hardware wallet").

The console's tabs expose more than search: a data browser, a document-detail view, and an article-writing tab that generates knowledge-base content with the LLM. Two of those generation endpoints, `/api/generate-article-stream` and `/api/fact-check`, call DeepSeek with the operator's server-side API key, and both are unauthenticated. An anonymous caller can drive unbounded inference against Keystone's DeepSeek account, which runs up cost and can exhaust the API quota. We did not exercise this. We name it because the surface is open.

**Proof this is live production, not a sandbox.** The endpoint `/api/writing-history` returns every article the system has generated, including full text, with no authentication. One of those articles covers a Korean government seed-phrase leak that cost $4.8M. The console is not a forgotten test rig. It is producing customer-facing content today, and its writing history is itself an information-exposure finding.

The DeepSeek API key lives in this app's server-side environment. We did not extract it. The routes `/config` and `/env` returned 404, and we did not pursue the key further. The significance of the live pipeline next to an open store is covered in "Why This Finding Is Different."

### Finding 3: ChromaDB admin UI with no authentication (port 8080)

| Attribute | Value |
|-----------|-------|
| Service | React SPA on nginx/1.28.1, built 2026-01-03 |
| Weakness | CWE-306 |
| Auth state | None |
| Confirmed access | Visual collection management and deletion |
| Severity | High |

The admin UI is hardcoded to the ChromaDB instance on port 8000. It gives the same read, write, and delete power as the raw API, with a graphical interface. The JS bundle carries the endpoint `http://43.153.169.169:8000` in plain text. A non-technical attacker who never touches the API can browse and delete collections by clicking.

---

## Attack Chain

**From an anonymous HTTP request to customer asset loss, link by link. We confirmed every primitive. We did not run the full chain against real users.**

```
[1] Anonymous attacker, no account, no credential
      |
      v  POST :8000/.../keystone_knowledge_base/get
[2] Read the existing seed-phrase and recovery guidance          [CONFIRMED]
      |
      v  POST :8000/.../keystone_knowledge_base/upsert
[3] Write a record that reads as native Keystone guidance         [CONFIRMED capability]
      |     (we wrote a marked canary, then deleted it)
      v  POST :5050/api/search {"query": "how do I recover my wallet"}
[4] Read back the retrieval rank to confirm the record surfaces;  [CONFIRMED single read-back;
      |     tuning to rank 1 is the next step                       tuning not run against the
      |                                                              live corpus]
      v  [a real user asks the Keystone chatbot]
[5] DeepSeek retrieves the record, answers as Keystone official    [PIPELINE CONFIRMED,
      |     support, score 0.844 on the recovery query              not run against users]
      v
[6] User follows the answer, discloses their seed phrase           [DEMONSTRATED CAPABILITY,
      |                                                              never carried out]
      v
[7] Crypto assets lost                                             [DEMONSTRATED CAPABILITY]
```

Links 2 and 3 are confirmed with evidence: we read the corpus, and we wrote and deleted a marked record. Link 4 is confirmed as a single retrieval read-back through the open console. We did not iterate it to tune a payload against the production corpus. Link 5 is confirmed at the pipeline level: we ran `/api/search` and DeepSeek answered as Keystone support with real corpus context. We did not place a malicious record in front of a real user. Links 6 and 7 are the end state that these confirmed primitives make possible. They are a capability we assembled from independently proven parts. They are not an attack we carried out, and no customer was harmed.

The link that makes the chain land is trust. The chatbot answers as official Keystone support, on the one topic, seed-phrase recovery, where a user has no independent reference to check the answer against. They asked the official channel. The official channel answered. They follow the steps.

The target selects itself. Keystone's customers are the people careful enough to buy a hardware wallet and to ask official support before they touch their seed phrase. A phishing page would not catch them. This does, because it arrives through the channel they trust, on the device they bought to stay safe. The attacker does not have to trick anyone. They wait for a careful customer to do the careful thing.

---

## Why This Finding Is Different

**An open RAG console turns blind injection into a tuned, verified attack. That is the part the literature does not model.**

Two weaknesses stack here, and the stack is worse than either part.

**The door: CWE-306.** Missing authentication on a function with security implications. Three such functions are reachable by anyone: read the knowledge base, write to or delete from it, and run the full retrieval-plus-LLM pipeline. This is the same weakness class behind a decade of exposed Elasticsearch, Redis, MongoDB, and etcd. It is well understood and easy to fix.

**What you do through the door: RAG data poisoning.** In a retrieval-augmented system, the LLM answers from whatever the retrieval step hands it. It cannot tell a real Keystone document from an injected one. Both are just text in the context window. Write to the vector store and you control what the model reads before it speaks. On a read-only store, CWE-306 is a confidentiality problem. On a store wired into user-facing AI output, write access becomes control over what the chatbot tells customers.

**The feedback oracle, on port 5050.** This is the novel part. Published RAG-poisoning research, PoisonedRAG (2024) and OWASP LLM04, models the attacker as blind after injection: write a record and hope it surfaces. The open console on 5050 removes the blindness. It turns a guess into a tuned, confirmed attack. The next section walks that difference step by step.

**The MITRE ATLAS angle.** OWASP LLM04 names this attack class but is not a TTP framework. ATLAS is, and as of ATLAS v5.6.0, verified against the live matrix on 2026-06-20, RAG poisoning is on the map. AML.T0070 RAG Poisoning covers inference-time injection of content into RAG-indexed data, targeted to surface for a specific query, and AML.T0066, AML.T0071, and AML.T0064 cover the content-authoring, false-entry, and recon mechanics. The Keystone write primitive maps cleanly to AML.T0070. AML.T0020 Poison Training Data does not fit, because it is training-time and this attack never touches model weights or any training pipeline. What no single technique names is the method the open 5050 console enables: the closed-loop, oracle-tuned tuning that queries the live system as a ranking oracle and confirms the injected record wins retrieval before any real user is in the loop. AML.T0070 names the outcome. It does not name that optimization loop. The residual is the method, not the class. We document it, with a proposed sub-technique under AML.T0070, in `analysis/2026-06-20-atlas-gap-inference-time-rag-poisoning.md`.

**Why there is no CVE.** A CVE attaches to a product version with a code-level defect. ChromaDB's default-no-auth posture is a deployment misconfiguration working as designed, not a flaw in its code. The RAG-poisoning attack class lives in research, and research does not produce CVEs. The closest analogues, the unauthenticated Kubernetes API server and the no-auth Jupyter default, followed the same path: documented as guidance first, CVE treatment later once vendors were pressured to change defaults. Right now this is a misconfiguration with a novel exploitation path.

---

## Blind vs Closed-Loop: Why the Oracle Changes the Threat Model

**Every prior RAG-poisoning case was blind. This one has a rangefinder.**

The research papers and the few real-world RAG-poisoning cases on record share one constraint. The attacker writes to the vector store, then sees nothing. No view of the rank their document earned, no view of which queries pull it, no confirmation the embedding landed where they aimed.

```
BLIND INJECTION  (all prior work)

Attacker               Vector Store            Users
   |                        |                    |
   |--- write poison ------>|                    |
   |      (no feedback)     |                    |
   |                     [later]                 |
   |                        |<---- user query ---|
   |                        |--- retrieve --?--> |
   |                        |   maybe surfaces,  |
   |                        |   maybe does not   |
```

This is why the literature calls it probabilistic. The attacker is guessing at embedding-space geometry with no map. They write something plausible, hope it lands near the target queries, and get no confirmation until a user somewhere does something they cannot see.

Port 5050 is a search interface against the same store, the same embedding model, the same retrieval pipeline. It is the oracle the attacker needs.

```
CLOSED-LOOP  (this finding)

Attacker           :8000 ChromaDB       :5050 Console
   |                     |                    |
   |-- write poison ---->|                    |
   |-- query "seed phrase recovery" --------->|
   |                     |<--- retrieve ------|
   |<-- rank 4, score 0.71 ------------------ |
   |   revise: add "wallet recovery", "lost device", "24 words"
   |-- upsert revised -->|                    |
   |-- query again -------------------------> |
   |<-- rank 2, score 0.81 ------------------ |
   |   revise again      |                    |
   |-- upsert revised -->|                    |
   |-- query again -------------------------> |
   |<-- rank 1, score 0.87 ------------------ |
   |   stop. confirmed dominant.              |
```

Now the attacker is hill-climbing the cosine-similarity landscape with real gradient at every step. They know the score their document holds, the rank it holds against the legitimate records, the query phrasings that pull it, and the moment they have won. They stop at rank 1. The injection is verified dominant before a single user query ever touches it.

**It breaks the defenses built for blind injection.** The two detection approaches in the current literature both assume the attacker cannot see retrieval.

Anomaly detection on the retrieval distribution flags a document that surfaces too often, or scores too high for queries it should not match. That works on blind payloads, which embed unevenly and look statistically off. An attacker with the oracle tunes the document until its score profile across query phrasings matches a native record. Nothing reads as anomalous.

Near-duplicate vector detection alerts when an ingested document sits unusually close to an existing one, the signature of a record trying to shadow a legitimate one. An attacker with the oracle tunes away from that. The payload scores high against user queries and low against existing documents. The duplicate check passes clean.

Without the oracle, the attacker fires into a dark room, listens for impact, and adjusts. Probabilistic, and noisy enough that the firing itself can be the tell. With the oracle, they have a rangefinder and a display of every shot. They center the crosshairs, fire once, and leave. The 5050 console is the rangefinder. That is what makes this finding structurally different from everything before it.

---

## The Short Chain and the Asymmetry

**Thirty seconds and one HTTP request, against a permanent loss. The attacker is gone before the harm lands.**

Most attack chains are long. A web-app intrusion runs recon, initial access, persistence, privilege escalation, lateral movement, then reaches the data. A supply-chain attack compromises a build pipeline, ships a package, waits for adoption, activates, calls home. Each hop is a point of failure, a time cost, and a place a defender can interrupt. The longer the chain, the more chances to catch it.

This chain is four steps, and the attacker only acts in the first one.

```
[1] Anonymous HTTP POST to :8000     single request, no auth, ~200ms
[2] Wait                             attacker has zero presence on the host
[3] A user queries the chatbot       the user triggers it, not the attacker
[4] Financial loss                   irreversible, on-chain
```

What this chain does not need is everything that normally makes an attack detectable.

No persistence. The payload is a database record. It persists because that is what a database does. The attacker maintains nothing. It sits until a query retrieves it.

No command and control. C2 is among the most detectable parts of any operation: beacons, callbacks, JA3 fingerprints. After the POST there is nothing calling home, nothing listening, nothing to fingerprint.

No malware. Nothing is delivered to the victim's machine. No exploit, no dropper, no shellcode. The malicious content is a text string in a database. It passes through a legitimate LLM and comes out as a normal answer. There is no file to scan and no signature to write.

No victim contact with attacker infrastructure. In a phishing chain the victim eventually touches something the attacker owns. Here the victim only ever touches Keystone's own chatbot, on Keystone's own interface. The attacker's text rides inside Keystone's trust relationship with its customer, invisibly.

No attacker presence at the moment of harm. The attacker wrote one POST, possibly weeks earlier, and has had no presence since. They do not have to be online when the customer loses their funds.

When an incident like this is detected, if it is detected, the trail leads to one unauthenticated HTTP request from an IP that was probably a VPN exit or a cloud instance that no longer exists. ChromaDB's default configuration does not log individual writes, so the attack may leave no log entry at all. There is no persistence to analyze, no malware sample, no C2 domain, no lateral movement, no credential use, and no victim-side artifact. The first sign that anything happened is a customer reporting a loss after following chatbot advice, and they may never file it, because they may never connect the chatbot to the loss, and the on-chain transaction is irreversible and pseudonymous.

The economics are lopsided. The attacker spends about thirty seconds and one request and carries almost no operational risk: no time on target, no infrastructure to burn, no presence to detect. The customer's loss is permanent. Most of what makes an attack expensive is the cost of holding access, and this attack has no maintenance phase at all.

---

## Impact

**Anonymous control of an AI support channel that holds real money behind it.**

**Technical.** Full read, write, and delete on the vector store, plus tenant and database creation, plus unauthenticated execution of the live LLM pipeline. We confirmed each of these primitives and reversed every change. The same primitives also let an attacker partition the instance with shadow tenants or exhaust storage, and let an anonymous caller drive cost against the operator's DeepSeek key through the generation endpoints. We did not exercise those last two. ChromaDB's default configuration keeps no audit log, so a write or delete leaves no trace today.

**Business.** The knowledge base is Keystone's customer-support brain. Read access exfiltrates the full 6,155-record corpus, including the proprietary editorial framing in `keystone_article_style`. That collection holds Keystone's Chinese and English security-marketing copy, some still under development, and it is competitor-extractable in one read. Write access lets an attacker change what the official chatbot tells customers. Delete access lets an attacker quietly erase legitimate guidance, the quieter and easier variant: no payload to tune, just remove the real seed-phrase records and let the chatbot answer customers from a corpus with holes in it. With no audit log, the erased guidance is hard to even notice.

**Financial.** Keystone's customers hold real cryptocurrency. The chatbot answers seed-phrase and recovery questions as official support. Tampered guidance on key custody has direct financial consequences for the customer, and those losses are irreversible on-chain. There is no clawback on a transferred seed phrase.

**Trust.** A self-custody hardware wallet brand sells trust as the product. A support channel that can be made to hand out attacker-controlled recovery instructions damages exactly the asset the brand is built on, whether or not any individual loss is ever traced back to the channel.

**Multilingual reach.** The corpus serves English and Chinese users from one store. A single injection reaches both audiences through one retrieval pipeline, so the blast radius is the entire customer base, not one language segment.

---

## Proof of Concept

**One script, eight steps, every primitive confirmed and cleaned up.** Full source: `data/poc-keystone-rag-poison.py`.

The PoC uses the Python standard library plus `sentence-transformers` to produce matching 1024-dimension embeddings. It verifies unauthenticated read, exercises tenant and database creation and deletion, captures a baseline retrieval, writes a clearly marked research record, reads back its retrieval rank through the open console, runs the live DeepSeek answer, and deletes the record. The injected record states in its own text that it is a NuClide Research security-research notice and is removed in the final step.

| What | Result | Evidence |
|------|--------|----------|
| Read collections, no credentials | 2 collections, 6,907 records | ChromaDB v2 collections endpoint |
| Tenant and database creation | `nuclide-poc-tenant`, `poc-db` created, then deleted | PoC step 2 |
| Live retrieval | Score 0.844 for "seed phrase recovery" | PoC step 4 |
| Write a marked canary | Accepted, 1024-dim embedding | PoC step 5 |
| Read back retrieval rank via 5050 | Injected record surfaces in ranked results | PoC step 6 |
| Live LLM answer as Keystone support | DeepSeek replies in the official persona | PoC step 7 |
| Delete the canary, unauthenticated | Removed, verified absent | PoC step 8 |

Key request primitives:

```bash
BASE="http://43.153.169.169:8000/api/v2/tenants/default_tenant/databases/default_database"
COLL="8ea8b4cb-ec2d-463f-a2bd-a335e1c98d27"

# Read the live retrieval pipeline, no auth (used once to confirm a pipeline run)
curl -s -X POST "http://43.153.169.169:5050/api/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "seed phrase recovery", "n_results": 1, "ai": "off"}'

# Tenant creation, infrastructure-level write, no auth (removed after)
curl -s -X POST "http://43.153.169.169:8000/api/v2/tenants" \
  -H "Content-Type: application/json" \
  -d '{"name": "nuclide-poc-tenant"}'

# Delete a record, no auth (returns {"deleted": 1})
curl -s -X POST "$BASE/collections/$COLL/delete" \
  -H "Content-Type: application/json" \
  -d '{"ids": ["nuclide-research-poc-001"]}'
```

We did not paste the embedding and tuning logic here. The full, runnable script is in the referenced file.

---

## Pivot Avenues

**Six read-only avenues remain open. We did not pursue them. They are listed so Keystone can scope the full exposure.**

| # | Avenue | What it would confirm |
|---|--------|-----------------------|
| 1 | keyst.one chatbot surface mapping | Identify the user-facing chatbot or docs assistant that routes through `:5050/api/search`, and whether KB content surfaces in production responses |
| 2 | `/api/generate-article-stream` quota probe | Confirm the DeepSeek key is live and measure cost and quota exposure from an unauthenticated caller |
| 3 | `/api/writing-history` full pull | Complete article history: internal research topics, draft copy, product-roadmap signals |
| 4 | Tencent Cloud 43.153.169.0/24 adjacency | Probe adjacent IPs for additional Keystone backend services |
| 5 | `keystone_knowledge_base` full scroll | Pull all 6,155 records with pagination, checking metadata fields (source, filepath, parent_id) for embedded credentials or internal API references |
| 6 | Cross-tenant enumeration | GET `/api/v2/tenants` to confirm whether additional tenants beyond `default_tenant` exist |

---

## Beyond Keystone: An Ecosystem Default

**This is not a Keystone mistake alone. It is a default that ships with the tooling, instantiated on a public IP.**

ChromaDB's 1.0.0 line runs with no in-process authentication. The store trusts its network, and the getting-started path does not turn auth on. A developer who follows the quickstart and exposes the port gets exactly this posture, by design: open read, write, and delete, with no warning in the default run.

Every RAG stack needs a vector database, and ChromaDB is a common first choice. The same auth-off default sits under every deployment that did not add a token gate or a firewall rule on its own. Keystone is one instance. The pattern is the tooling's default meeting a public interface, and it is being instantiated on production systems that serve real users right now.

That is what gives this finding reach beyond one operator. The fix for Keystone is one firewall rule. The fix for the class is a change in what getting started looks like: authentication on by default, or a loud warning when a store binds to a public interface. Until that shifts, this same finding keeps landing on live infrastructure.

---

## Remediation

**Prioritized. The first action closes public exposure today with no code change.**

**Immediate, today.** Firewall ports 8000, 5050, and 8080 to internal access only. A Tencent Cloud security-group rule is the fastest path. Restrict the services to the application's own network or a management VPN. This removes the public attack surface on all three services at once and requires no code change. Do this first.

**Short term.** Add authentication at the infrastructure layer. Put ChromaDB behind a reverse proxy that validates a token on every request, or gate the services behind VPN access. ChromaDB ships with no authentication by default, so the control belongs at the proxy or network layer. The 5050 console and the 8080 admin UI need the same treatment; an open console next to a closed store still gives an attacker the feedback oracle.

**Ongoing.**
- Audit the knowledge base for injected or altered records before re-exposing the pipeline. Verify the corpus, and the `guide/seed_phrase` and `guide/security` records in particular, against a known-good source.
- Add rate limiting and anomaly detection on the add and delete paths once authentication is in place.
- Enable audit logging. ChromaDB's default configuration keeps no record of who wrote or deleted what, so today a change would leave no trace.
- Treat the documentation mismatch on the embedding model as a signal to review the deployment's configuration management.

---

## Responsible Disclosure Statement

**We are reporting this to help Keystone close it, not to pressure anyone.**

We enumerated the three exposed services and confirmed each finding with the minimum action that proved it: unauthenticated read of 6,907 records, a write proved with one clearly marked research canary, a delete confirmed by a follow-up read that showed the canary gone, tenant and database creation that we then removed, and the live RAG-plus-DeepSeek pipeline confirmed with a single query. Every object we created, we deleted. The seed-phrase-theft end state in this report is a capability built from those confirmed primitives. We did not run it against anyone, and no customer was harmed.

We offer to help. NuClide Research will assist with remediation and verify the fix at no cost, on Keystone's timeline. There is no deadline and no demand attached to this report.

This report should reach the Keystone security team. We recommend confirming the correct intake channel before sending, for example a published `security@` address or a `security.txt` file on keyst.one. We do not assert a specific contact address as known.

Contact: Nicholas Kloster, NuClide Research, nicholas@nuclide-research.com.

---

## Appendix

### A. Endpoint and Access Matrix

| Operation | Port | Method and path | Result | Auth |
|-----------|------|-----------------|--------|------|
| List tenants | 8000 | GET /api/v2/tenants | Tenant list | None |
| List collections | 8000 | GET /api/v2/.../collections | 2 collections | None |
| Read records | 8000 | POST .../collections/{id}/get | Documents and metadata | None |
| Write record | 8000 | POST .../collections/{id}/upsert | Accepted | None |
| Delete record | 8000 | POST .../collections/{id}/delete | `{"deleted": 1}` | None |
| Create tenant | 8000 | POST /api/v2/tenants | Created, then removed | None |
| Create database | 8000 | POST /api/v2/tenants/{t}/databases | Created, then removed | None |
| Semantic query and AI answer | 5050 | POST /api/search | Live DeepSeek answer as Keystone support | None |
| Data browser | 5050 | GET /api/data, /api/collections | Collection contents | None |
| Article generation | 5050 | POST /api/generate-article-stream | DeepSeek call on operator key (not exercised) | None |
| Fact check | 5050 | POST /api/fact-check | DeepSeek call on operator key (not exercised) | None |
| Writing history | 5050 | GET /api/writing-history | All generated articles, full text | None |
| Admin UI | 8080 | GET / | Full browse and manage | None |
| Config and env probe | 5050 | GET /config, GET /env | 404 (key not extracted) | n/a |

### B. Infrastructure Attribution

| Attribute | Value |
|-----------|-------|
| IP | 43.153.169.169 |
| Cloud | Tencent Cloud |
| Open ports | 22 (SSH), 5050, 8000, 8080 (only open ports) |
| Console stack | Python 3.12.3, Werkzeug 3.1.8, Flask (port 5050) |
| Admin stack | nginx/1.28.1, React SPA built 2026-01-03 (port 8080) |
| Vector store | ChromaDB 1.0.0, API v2 (port 8000) |
| LLM | DeepSeek, via the 5050 pipeline (model strings operator-reported) |
| Embedding model | intfloat/multilingual-e5-large, 1024 dimensions (confirmed via PoC; schema mislabel is 384d MiniLM) |
| Operator | Keystone (keyst.one), confirmed via collection naming, embedded blog.keyst.one source URLs, product content, and the DeepSeek persona prompt |

### C. Evidence Index

| # | Evidence |
|---|----------|
| 1 | ChromaDB v2 collections endpoint: 2 collections, 6,907 records, counts confirmed |
| 2 | Full category sweep of `keystone_knowledge_base`: 6,155 records across 30 categories, including guide/seed_phrase (46) and guide/security (54) |
| 3 | Read of `keystone_article_style` (752): editorial and marketing content, English and Chinese |
| 4 | Live pipeline: "seed phrase recovery" query, retrieval score 0.844, top record "Never Share Your 24-Word Recovery Phrase" |
| 5 | DeepSeek answer in the Keystone official-support persona ("您好，我是 Keystone 硬件钱包的官方客服") |
| 6 | `/api/collections` on 5050 confirms the same 2 collections |
| 7 | `/api/writing-history` on 5050: full article history, including a piece on a Korean government seed-phrase leak ($4.8M), proving live production use |
| 8 | Write: marked record accepted with a 1024-dimension embedding (PoC step 5); zero-vector write also accepted in manual confirmation |
| 9 | Tenant and database creation: `nuclide-poc-tenant`, `poc-db` created and removed (PoC step 2) |
| 10 | Closed-loop read-back: retrieval rank read through 5050 after injection (PoC step 6) |
| 11 | Delete: record removed, unauthenticated, verified absent on follow-up read (PoC step 8) |
| 12 | Port sweep: exactly four open ports confirmed |

### D. Tool Reference

**chromascan**: unauthenticated ChromaDB enumeration with canary write and delete verification. https://github.com/nuclide-research/chromascan

Standalone proof-of-concept: `data/poc-keystone-rag-poison.py` (eight steps, Python standard library plus sentence-transformers).
