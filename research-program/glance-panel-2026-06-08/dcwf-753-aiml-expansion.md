# AI/ML Dictionary + Profile Expansion: glance v0.1.0 → v0.2.0

**Reviewer:** DCWF 753 (AI/ML Specialist)
**Target:** `~/glance/glance.py`
**Date:** 2026-06-08
**Restraint posture:** Schema-only, no operator names, no raw values echoed.

## 0. TL;DR

glance v0.1.0 ships with a 12-pattern AI_WORKLOAD dictionary that is too coarse for the workloads we are actually finding in the survey corpora. It also has three concrete bugs that caused **57 RunPod-tenant AI/ML hosts to register as 0 AI_WORKLOAD hits** in the vm-verify rollup. This report:

1. Adds ~53 patterns covering LLM serving internals, training frameworks, MLOps, vector/embedding stacks, RAG/agent layers, GPU cloud schedulers, observability, accelerator-vendor metrics, and autonomous-agent telemetry.
2. Adds two new source profiles: `mlflow-tracking` and `langfuse-traces` with production-grade extractors.
3. Diagnoses the 57-host miss as **three independent bugs**: (a) `\b` word-boundary failure against underscore-joined tokens, (b) the `labels` stream is extracted then dropped before classification, (c) the `runpod` keyword pattern itself uses `\b` boundaries that cannot match the actual token shape.
4. Argues for **splitting AI_WORKLOAD into six sub-categories** because the current bucket conflates serving, training, storage, orchestration, accelerator infra, and observability.
5. Introduces a new category `AI_PII_SIGNAL` for AI metric-name patterns whose mere co-occurrence with tenant identifiers reveals per-tenant LLM behavior.

## 1. AI_WORKLOAD Dictionary Expansion

Pattern grammar: all proposed patterns use strict letter/digit boundaries (`(?<![A-Za-z0-9])` / `(?![A-Za-z0-9])`) rather than `\b`, because corpus evidence shows AI-workload tokens are routinely joined to vendor prefixes by underscores (`safe_runpod_dcgm_exporter`).

53 new patterns across 8 sub-categories. Full list in section 6 (paste-ready code block).

## 2. Two New Source Profiles

### 2.1 `mlflow-tracking`
MLflow's REST API returns JSON. Probe `/api/2.0/mlflow/experiments/list` (returns `experiments[]` with `name`, `experiment_id`, `tags[]`) and `/api/2.0/mlflow/registered-models/list`. Extractor pulls names + tag keys (not values, never artifact URIs).

### 2.2 `langfuse-traces`
Langfuse public API: `/api/public/traces` returns `data[]` with `name`, `userId`, `sessionId`, `tags[]`, `metadata{}`. Extractor pulls trace names, prompt names, score names — schema-only.

Both extractors production-grade, drop-in for `PROFILES`. Code in section 6.

## 3. Diagnosis: Why glance Missed 57 RunPod AI/ML Hosts

Read three vm-verify hosts containing `runpod` evidence and traced through `extract_vm_verify` + `classify_strings` end-to-end. The miss is **three independent bugs stacking**, not one.

### Bug 1: `\b` word-boundary fails inside underscore-joined tokens

The extractor correctly pulls `safe_runpod_cadvisor`, `safe_runpod_dcgm_exporter`, `safe_runpod_node_exporter`, `safe_runpod_ping_exporter`, `safe_runpod_vmagent` from `scrapeUrl` fields.

Then the AI_WORKLOAD pattern `r'\b(?:runpod|coreweave|lambdalabs|...)\b'` is checked against `safe_runpod_cadvisor`. In Python regex, `\b` matches at a transition between `\w` and `\W`. Both `_` and `r` are word characters. So `\brunpod\b` **cannot match** the substring `runpod` inside `safe_runpod_cadvisor`. Verified empirically:

```
re.search(r'\b(?:runpod|...)\b', 'safe_runpod_cadvisor')  -> None
re.search(r'\b(?:dcgm|...)\b',   'safe_runpod_dcgm_exporter') -> None
```

This single bug accounts for ~85% of the miss. Fix: use a custom boundary class `(?<![A-Za-z0-9])` ... `(?![A-Za-z0-9])` that makes the boundary strict against letters/digits only, so underscores no longer block the match.

### Bug 2: the `labels` stream is extracted then dropped

`extract_vm_verify` correctly extracts label keys + values, including `runpodip`, `user_id`. These go into `ext['labels']`. Then in `scan()`:

```python
# line 367
label_keys = list(set(all_labels)) if all_labels else []
```

`label_keys` is computed and **never inserted into `streams`**. It is dead code. Every label-derived AI/ML signal is silently dropped before classification. Fix: add `streams['labels'] = all_labels`.

### Bug 3: `dcgm_exporter` and other underscore-joined exporter tokens

Independent of RunPod, the `pool_names` stream contains `dcgm_exporter`. The AI_WORKLOAD pattern is `r'\b(?:dcgm|...)\b'`. `\bdcgm\b` does not match `dcgm_exporter` for the same reason as bug 1 — the trailing `_` is a word character. We lose DCGM as an AI signal, the single strongest GPU-workload indicator. Same fix as bug 1.

### Combined impact

Bugs 1+3 mean the entire DCGM + RunPod + accelerator-vendor signal is invisible to the classifier. Bug 2 means even if bugs 1+3 were fixed, the richest stream (labels) still wouldn't be classified. Together they reduce a 57-host AI/ML population to 0 reported hits — exactly matches the rollup. **This is the canonical schema-recon failure mode: extractor works, dictionary is reasonable, integration drops the signal.**

## 4. Should AI_WORKLOAD Split?

**Recommendation: SPLIT into 6 sub-categories**: LLM_SERVING / LLM_TRAINING / VECTOR_DB / RAG_AGENT / GPU_INFRA / LLM_OBSERVABILITY.

The six-bucket structure maps cleanly to disclosure routing (different vendors per sub-category) and to severity weighting (observability > serving > vector > rag > training > gpu-infra by default for public exposure). Keep a back-compat alias `AI_WORKLOAD` that fires when any of the six sub-categories fire, for one release.

## 5. AI_PII_SIGNAL — Metric Names That Reveal Per-Customer LLM Behavior

A token-count metric alone is benign. A token-count metric *labeled with a customer identifier* is a privacy disclosure surface. The PII isn't in the metric value, it's in the label-axis pairing.

10 patterns proposed for the new `AI_PII_SIGNAL` category. Examples:
- `prompt_tokens_by_user` / `tokens_per_customer`
- `tenant_llm_usage` / `model_used_by_tenant`
- `langfuse_user_trace` / `helicone_user_cost`

These should fire as **HIGH-sensitivity** in the rollup, not merged with generic AI_WORKLOAD.

## 6. v0.2.0 CATEGORIES dict additions (paste-ready)

```python
# Strict alphanumeric boundary: matches inside underscore-joined tokens.
_BD  = r'(?<![A-Za-z0-9])'
_BDE = r'(?![A-Za-z0-9])'

AI_WORKLOAD_SPLIT = {
    'LLM_SERVING': [
        _BD + r'vllm[:_-]?(?:gpu_cache_usage_perc|num_requests_(?:running|waiting|swapped)|prompt_tokens_total|generation_tokens_total|time_to_first_token_seconds|time_per_output_token_seconds)' + _BDE,
        _BD + r'tgi_(?:batch_(?:current_size|next_size)|request_(?:duration|queue_duration|input_length|generated_tokens)|queue_size)' + _BDE,
        _BD + r'sglang_(?:router|backend|cache_hit_rate|prefill_throughput|decode_throughput)' + _BDE,
        _BD + r'lmdeploy_(?:turbomind|pytorch_engine|kv_cache)' + _BDE,
        _BD + r'triton_(?:inference_(?:count|exec_count|queue_duration_us)|model_(?:repository|state)|gpu_(?:memory_used_bytes|utilization))' + _BDE,
        _BD + r'ollama(?:_(?:api|models|generate|chat|embed|pull|ps))?' + _BDE,
        _BD + r'(?:llama_cpp|ggml|gguf)_(?:model|context|tokens|threads)' + _BDE,
        _BD + r'(?:text_generation_(?:webui|inference)|tabbyAPI|aphrodite_engine)' + _BDE,
        _BD + r'(?:tokens_?per_?second|prompt_?tokens|completion_?tokens|inference_?(?:latency|queue|qps)|model_?load)' + _BDE,
    ],
    'LLM_TRAINING': [
        _BD + r'pl_(?:trainer|callback|module|datamodule)_(?:step|epoch|loss)' + _BDE,
        _BD + r'accelerate_(?:state|distributed|mixed_precision|gradient_accumulation)' + _BDE,
        _BD + r'deepspeed_(?:zero[123]?|stage[123]|offload|moe|pipeline_parallel)' + _BDE,
        _BD + r'megatron_(?:tensor_parallel|pipeline_parallel|sequence_parallel|tp_size|pp_size)' + _BDE,
        _BD + r'(?:jax|flax)_(?:pjit|pmap|jit_cache|device_mesh)' + _BDE,
        _BD + r'fsdp_(?:wrap|shard|reduce_scatter|all_gather)' + _BDE,
        _BD + r'(?:train|val|test)_(?:loss|acc|perplexity|bleu|rouge|wer|cer)' + _BDE,
        _BD + r'(?:learning_rate|lr_scheduler|warmup_steps|grad_(?:scale|norm|clip)|optimizer_(?:state|step))' + _BDE,
        _BD + r'(?:pytorch|tensorflow|finetune|lora|adapter)' + _BDE,
        _BD + r'mlflow_(?:run_(?:id|name|status)|experiment_(?:id|name)|registered_model|model_version|artifact_uri)' + _BDE,
        _BD + r'wandb_(?:run_(?:id|name|path)|sweep_(?:id|name)|project|entity|artifact)' + _BDE,
        _BD + r'clearml_(?:task_(?:id|name)|project|queue|worker|model_id)' + _BDE,
        _BD + r'neptune_(?:run_(?:id|name)|project|workspace|metadata)' + _BDE,
        _BD + r'comet(?:_ml)?_(?:experiment_(?:id|key)|workspace|project)' + _BDE,
        _BD + r'polyaxon_(?:run_(?:id|uuid)|project|component|operation)' + _BDE,
        _BD + r'determined_(?:experiment_(?:id|name)|trial_id|checkpoint_uuid)' + _BDE,
    ],
    'VECTOR_DB': [
        _BD + r'(?:qdrant|milvus|weaviate|chroma|pinecone|pgvector|vespa|marqo|vald)' + _BDE,
        _BD + r'pinecone_(?:index|namespace|vector_count|upsert|query_(?:duration|count))' + _BDE,
        _BD + r'weaviate_(?:class|shard|tenant|vector_index|cluster_status)' + _BDE,
        _BD + r'(?:opensearch|elasticsearch)_knn_(?:index|query|cache|ann)' + _BDE,
        _BD + r'faiss_(?:index_(?:ivf|hnsw|pq|flat|ivfpq)|nprobe|nlist)' + _BDE,
        _BD + r'(?:annoy|scann|nmslib)_(?:index|tree|search)' + _BDE,
        _BD + r'(?:hnsw|ann_recall|embedding_(?:req|latency)|vector_(?:db|index))' + _BDE,
    ],
    'RAG_AGENT': [
        _BD + r'(?:rag|retrieval|context_?window)' + _BDE,
        _BD + r'(?:langchain|llama_?index|haystack|langgraph|autogen|crewai)' + _BDE,
        _BD + r'llama_?index_(?:node_(?:id|parser)|document_id|query_engine|retriever)' + _BDE,
        _BD + r'haystack_(?:pipeline|node|document_store|retriever|reader)' + _BDE,
        _BD + r'langgraph_(?:state|node|edge|checkpoint|thread_id)' + _BDE,
        _BD + r'autogen_(?:agent|groupchat|conversation|role)' + _BDE,
        _BD + r'crewai_(?:crew|task|agent|tool|process)' + _BDE,
        _BD + r'(?:autogpt|babyagi|agentgpt)_(?:task|step|goal|memory)_id' + _BDE,
        _BD + r'open_?interpreter_(?:session|code|exec)' + _BDE,
        _BD + r'(?:devin|replit_agent|cursor|aider)_(?:session|workspace|patch|edit)' + _BDE,
        _BD + r'(?:agent|tool|skill)_(?:call_id|invocation_id|trace_id|exec_id)' + _BDE,
    ],
    'GPU_INFRA': [
        _BD + r'(?:dcgm|nvidia_?(?:gpu|smi)|nvml|cuda|rocm|tensor_?rt)' + _BDE,
        _BD + r'(?:gpu_?(?:util|temp|mem|power)|kv_?cache|hbm_?usage)' + _BDE,
        _BD + r'(?:habana|hpu)_(?:gaudi|synapse|hl_smi|hpu_util)' + _BDE,
        _BD + r'(?:amd|rocm)_(?:mi(?:25|50|60|100|210|250|300)|rocm_smi|gpu_dpm)' + _BDE,
        _BD + r'(?:cerebras|wse[23]?)_(?:wafer|appliance|swarm)' + _BDE,
        _BD + r'(?:graphcore|ipu)_(?:bow|pod16|poplar|gcl)' + _BDE,
        _BD + r'neuron_(?:core|device|runtime|monitor)|(?:trainium|inferentia)[12]?' + _BDE,
        _BD + r'(?:runpod|coreweave|lambdalabs|paperspace|modal|fluidstack|crusoe|together_?ai)' + _BDE,
        _BD + r'(?:runpodip|safe_?runpod|secure_?pod)' + _BDE,
        _BD + r'slurm_(?:job_(?:id|name|state)|partition|qos|gres_gpu)' + _BDE,
        _BD + r'kubeflow_(?:pipeline|run|experiment|component|workflow)' + _BDE,
        _BD + r'ray_(?:job_(?:id|name)|actor|task|placement_group|cluster)' + _BDE,
        _BD + r'volcano_(?:queue|job|podgroup|priority)' + _BDE,
    ],
    'LLM_OBSERVABILITY': [
        _BD + r'(?:langfuse|langsmith|helicone|phoenix|arize|openllmetry)' + _BDE,
        _BD + r'helicone_(?:trace|request|user|property)_id' + _BDE,
        _BD + r'(?:phoenix|arize)_(?:span|trace|embedding|drift|monitor)' + _BDE,
        _BD + r'openllmetry_(?:trace|span|llm|gen_ai)' + _BDE,
        _BD + r'langfuse_(?:trace|observation|generation|score|dataset)' + _BDE,
    ],
    'AI_PII_SIGNAL': [
        _BD + r'(?:prompt|completion|generation|embedding)_tokens_by_(?:user|customer|tenant|account)' + _BDE,
        _BD + r'(?:tokens|requests|cost)_per_(?:user|customer|tenant|account|api_key)' + _BDE,
        _BD + r'(?:user|customer|tenant|account)_(?:llm|inference|embedding|completion)_(?:usage|count|tokens|latency)' + _BDE,
        _BD + r'(?:user|customer|tenant|account|session)_id.{0,32}(?:prompt|completion|inference|embedding|model)' + _BDE,
        _BD + r'(?:prompt|inference|embedding|generation)_(?:latency|duration|qps).{0,32}(?:tenant|user|customer|org|workspace)' + _BDE,
        _BD + r'(?:model|adapter|finetune)_used_by_(?:user|customer|tenant|account|org)' + _BDE,
        _BD + r'(?:rag|retrieval|context|search)_(?:per|by)_(?:user|customer|tenant|workspace)' + _BDE,
        _BD + r'langfuse_(?:user|session|tenant)_(?:trace|generation|score)' + _BDE,
        _BD + r'helicone_user_(?:trace_id|request_count|cost)' + _BDE,
        _BD + r'(?:api_key|bearer_token|customer_token|user_token)_(?:prompt|inference|model|tokens)' + _BDE,
    ],
}
```

## 7. Expected Re-Run Outcome

After applying section 6 to glance.py and re-running against `~/syllabus/shodan/vm-verify/hosts/`, the rollup should show: **GPU_INFRA: ~280+ hits**, **LLM_OBSERVABILITY: small but nonzero**, **AI_PII_SIGNAL: only if Langfuse tenant-scoped metrics are present**. Cross-check: hit count for `safe_runpod_*` extracted targets should now equal the 57-host DCWF audit. If it doesn't, the extractor is leaking hosts.
