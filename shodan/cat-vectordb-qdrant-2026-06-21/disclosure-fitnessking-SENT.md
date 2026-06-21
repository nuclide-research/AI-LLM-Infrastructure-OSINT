# Disclosure: Fitnessking fk_email_threads Qdrant Exposure
# Status: SENT 2026-06-21
# To: info@fitnessking.be
# From: nicholas@nuclide-research.com
# Gmail messageId: 19eea238fdb99f5a

---
Subject: Beveiligingsprobleem: Klantenservice database openbaar toegankelijk / Security Issue: Customer Service Database Publicly Exposed

Host: 54.224.57.246:80 (AWS us-east-1, Qdrant 1.17.1)
Collections: fk_email_threads (18,517), fk_email_threads_e5 (18,517), fk_email_threads_gemini (19,838)
Total: 56,872 email thread vectors, dim=1024/1536
R/W/D: confirmed -- op_id 4729 (write), 4730 (delete)

Data class: customer support emails -- full content, sender/recipient addresses,
AI labels (emotion, intent, resolution_status). EU customer PII. GDPR exposure.

Top external sender domains: gmail.com (953), hotmail.com (633), telenet.be (619),
hammer.de (742), bhfitness.com (625), skynet.be (123), tunturi.com (75).

Active since: 2026-04-25. 1,507 writes, 237 deletes, 49 dashboard visits via telemetry.
No snapshots exposed.
