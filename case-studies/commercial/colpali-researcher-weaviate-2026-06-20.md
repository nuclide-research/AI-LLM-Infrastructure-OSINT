---
type: case-study
severity: HIGH
date: 2026-06-20
title: "ColPali Retrieval Researcher: Unauthenticated Weaviate Holding a Multimodal Benchmark Corpus"
summary: "An AI retrieval researcher exposed a Weaviate 1.36.8 instance with no authentication on port 8080. The store held 11 classes and roughly 64,099 objects spanning the ColPali, ViDoRe, and NanoBEIR benchmark evaluations. Anonymous read of the full schema and corpus was confirmed; write and delete surfaces were present but not exercised."
tags:
  - weaviate
  - vector-database
  - unauth
  - cwe-306
  - research-benchmark-data
  - academic-research
sidenotes:
  - kind: host
    label: Target
    kv:
      - k: Operator
        v: "AI retrieval researcher (identity not confirmed)"
      - k: Sector
        v: "Academic / ML Research"
      - k: Location
        v: "Asia-Pacific cloud (likely)"
      - k: Severity
        v: HIGH
  - kind: see-also
    label: Classification
    kv:
      - k: Primary
        v: "CWE-306 Missing Authentication for Critical Function"
      - k: Secondary
        v: "CWE-284 Improper Access Control"
      - k: OWASP
        v: "LLM04 Data and Model Poisoning"
---

# ColPali Retrieval Researcher: Unauthenticated Weaviate Holding a Multimodal Benchmark Corpus

_NuClide Research -- Nicholas Kloster -- 2026-06-20_

---

## Summary

A Weaviate 1.36.8 instance at 103.219.171.197:8080 ran with no authentication layer. The store held 11 classes and roughly 64,099 objects. The class names map to an active multimodal document-retrieval evaluation: ColPali, the ViDoRe benchmark, and NanoBEIR dense-retrieval baselines.

Anyone on the internet could read the full schema and pull records from any class. We confirmed read only. Write and delete endpoints had no auth in front of them, but we did not exercise them.

The operator is a retrieval researcher, likely academic or ML engineering. There is no commercial PII in this store. The exposure is research IP and benchmark corpus data, plus an open write surface that allows benchmark poisoning.

---

## Attack Surface

| Port | Software | Role | Auth |
|------|----------|------|------|
| 8080 | Weaviate 1.36.8 | Vector database, node ID ae5952d0dff9, 11 classes / ~64,099 objects | None |

A single open port. No token, no API key, no allowlist. Schema walk, class object reads, and GraphQL execution all returned 200.

---

## What We Confirmed

**Read:** Confirmed.

- `GET /v1/meta` returned 200 with version 1.36.8 and node ID ae5952d0dff9.
- `GET /v1/schema` returned 200 with all 11 class schemas.
- `POST /v1/graphql` returned 200 with records for NanoBEIR, ColpaliEval, and ViDoRe classes.

**Write:** Not exercised. `POST /v1/objects` had no auth layer in front of it. We did not send an insert. The poisoning path is structural and unconfirmed.

**Delete:** Not exercised. `DELETE /v1/objects/{uuid}` had no auth layer in front of it. We did not send a delete.

Read only was exercised. No write or delete was performed against this host.

---

## Data Exposed

11 classes, roughly 64,099 total objects. No commercial PII. The contents are retrieval-benchmark corpus and evaluation configuration data.

| Class | Props | Content |
|-------|-------|---------|
| NanoBEIRColBERTMinimal | corpusid, dataset | NanoBEIR benchmark corpus, ColBERT model evaluation |
| LIMITcolbertv2 | corpusid, text | ColBERT v2 dense retrieval evaluation |
| ColpaliEvalEf100R20K5P8edc696c39a | corpusid, dataset | ColPali eval run (ef=100, recall@20K, variant A) |
| ColpaliEvalR20K5P164cb50c8e31 | corpusid, dataset | ColPali eval variant B |
| ColpaliEvalEf100R20K5P8fc4e466e15 | corpusid, dataset | ColPali eval variant C |
| ColpaliEvalEf100R20K3P893f3c5aa48 | corpusid, dataset | ColPali eval variant D (K=3) |
| ColpaliEvalEf100R20K5P80154d84d81 | corpusid, dataset | ColPali eval variant E |
| ColpaliEvalEf100R20K3P859712b8e30 | corpusid, dataset | ColPali eval variant F (K=3) |
| ViDoReColPaliGoMuveraMinimal | corpusid, dataset | ViDoRe benchmark, GoMuvera model baseline |
| ViDoReColPaliMinimal | corpusid, dataset | ViDoRe benchmark, ColPali baseline |
| ColpaliEvalEf100R20K5P166d49dbf84c | corpusid, dataset | ColPali eval variant G |

The class naming schema encodes hyperparameters: `ColpaliEval Ef{ef_search} R{recall_at} K{param_count} P{precision_k} {run_hash}`. Each class is an isolated evaluation run. Eight concurrent ColPali variants indicate an active parameter sweep over ef_search and precision@K, not a historical archive.

The likely indexed benchmark datasets are ViDoRe (DocVQA, InfoVQA, ArxivQA, TabFQuAD, TatDQA) and NanoBEIR. The schema and counts are the finding. No individual records are reproduced here.

---

## Impact

**Research IP exposure.** The full hyperparameter sweep is readable from the schema alone: ef_search values, recall@K targets, precision@K settings, and per-run hashes are encoded in the class names. A competitor or adversary can extract the operator's experimental design before publication.

**Benchmark corpus exfiltration.** Roughly 64,099 indexed objects span the ViDoRe and NanoBEIR corpora. If custom annotation or scoring data is embedded in the dataset field, that is extractable evaluation data.

**Benchmark poisoning.** No write authentication means an actor could inject false corpus records into any of the 11 evaluation classes. Poisoned records would corrupt recall and precision metrics for the affected run. If the operator computes benchmark scores against this corpus, injected records produce falsified results, and any published results based on a poisoned corpus would constitute fabricated research data. This path was not exercised.

**Node ID fingerprint.** Node ID ae5952d0dff9 matches the Docker 12-char short-ID format. If the Docker daemon is exposed on the host, this fingerprint enables container enumeration.

---

## Remediation

**Immediate (no code change required):** Firewall port 8080 to the internal network only.

**Short-term:** Enable Weaviate's API-key or OIDC authentication and set `AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=false`. Verify that `POST /v1/objects` and `DELETE /v1/objects` reject anonymous calls.

**Medium-term:** Add canary records to detect unauthorized writes. Monitor the schema and object counts for unexpected class or record changes. Confirm the host's Docker daemon (ports 2375 and 2376) is not exposed.

---

## Disclosure

Finding documented 2026-06-20 under NuClide Research responsible-disclosure practice. Prior coordinated disclosures from this researcher include CVE-2025-4364 and ICSA-25-140-11, both through CISA.
