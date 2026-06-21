Subject: Unauthenticated knowledge base behind your AI support chatbot (43.153.169.169, ports 8000/5050/8080) lets anyone rewrite seed-phrase guidance

To: Keystone Security Team

Hello,

We are NuClide Research, an independent security research practice. We coordinate vulnerability disclosures responsibly. Our prior work includes CVE-2025-4364 and ICSA-25-140-11, both handled through CISA. We are writing because we found an exposure on Keystone infrastructure that we believe needs attention today, and we want to help you close it.

The finding. Three internet-facing services on 43.153.169.169, a Tencent Cloud host, carry no authentication. Port 8000 runs ChromaDB 1.0.0, the vector database that stores your AI customer-service knowledge base: 6,907 records across two collections, with 6,155 in keystone_knowledge_base. Port 5050 runs the live RAG console that answers user questions, retrieving from that knowledge base and returning DeepSeek answers in the voice of official Keystone support. Port 8080 serves an admin UI wired straight to the same database. Anyone on the internet can read, write, and delete the knowledge base your chatbot uses to answer questions about seed phrases and wallet recovery, with a single HTTP request and no credentials.

Why this is urgent. Your customers chose a hardware wallet because they take private-key custody seriously, and they hold real assets. The chatbot answers as official Keystone support, so a user has no reason to doubt what it says. A single poisoned record about seed-phrase recovery, surfaced to a real user, costs that user their funds. The exposed console on port 5050 sharpens the risk: it lets an attacker query the pipeline and read back which record the retriever picks, so a poisoned entry can be tuned to win before any real user is ever affected.

Our restraint. We held to a read-and-confirm posture. To prove write access we inserted one clearly marked research record, nuclide-research-poc-001, then deleted it and confirmed it was gone. The seed-phrase-theft outcome described above is a capability we assembled from confirmed primitives, not an attack we ran against your users. Your production content and your users were left untouched.

The ask. Firewall ports 8000, 5050, and 8080 to internal access today. That alone closes the exposure and needs no code change. The full technical report, including the access matrix, evidence, and a proof-of-concept, is attached. As follow-on steps, we recommend enabling ChromaDB authentication at the infrastructure layer and auditing the store for any records added before today. We are glad to help you verify the fix at no cost.

Thank you for the work you do on self-custody. We are available to answer questions and to coordinate on timing.

Nicholas Kloster
NuClide Research
nicholas@nuclide-research.com
