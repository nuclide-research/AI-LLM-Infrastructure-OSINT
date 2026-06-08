#!/usr/bin/env python3
"""
glance — schema-only sensitivity analyzer for sealed corpora.

v0.1.1 — DCWF panel corrections integrated:
  - DCWF 672 T&E: strict letter/digit boundary replaces \\b (recovers underscore-
    joined tokens like safe_runpod_dcgm_exporter); UnicodeDecodeError handled;
    TLD-suffix allowlist closes the operator-namespace leak; labels promoted
    to first-class stream.
  - DCWF 733 Risk&Ethics: non-English PII/PHI/FINANCE/DEFENSE_GOV/CRITICAL_INFRA
    additions; operator-derived patterns moved out of compiled-in dictionary;
    minimum-frequency floor on TLD + suffix histograms in sealed mode; low-N
    stream suppression.
  - DCWF 753 AI/ML: AI_WORKLOAD split into 6 sub-categories
    (LLM_SERVING/LLM_TRAINING/VECTOR_DB/RAG_AGENT/GPU_INFRA/LLM_OBSERVABILITY)
    plus new AI_PII_SIGNAL category; ~53 new patterns; mlflow-tracking and
    langfuse-traces extractors added.

USAGE
  glance scan <dir> --source <profile> [-o report.json]
  glance verify         # self-test the classifier against fixtures

PROFILES
  vm-verify        VictoriaMetrics per-host evidence
  chroma-campaign  Chroma per-host evidence
  mlflow-tracking  MLflow REST API evidence
  langfuse-traces  Langfuse public API evidence
  generic          Configurable jsonpath (--name-paths)
"""
import argparse, json, re, math, sys
from pathlib import Path
from collections import Counter, defaultdict

# ───────────────────────────────────────────────────────────────────────────────
# Strict alphanumeric boundary — fires inside underscore-joined tokens
# (safe_runpod_dcgm_exporter, vllm_prompt_tokens_total).
# Replaces \b throughout — \b doesn't fire at _ which is a word character.
# ───────────────────────────────────────────────────────────────────────────────
_BD  = r'(?<![A-Za-z0-9])'
_BDE = r'(?![A-Za-z0-9])'

def B(pat):
    """Wrap a pattern fragment with strict letter/digit boundaries."""
    return _BD + pat + _BDE

# ───────────────────────────────────────────────────────────────────────────────
# Category dictionary — bag-of-fields classifier (v0.1.1, panel-corrected)
# ───────────────────────────────────────────────────────────────────────────────

CATEGORIES = {
    'PII': [
        # English identifiers
        B(r'(?:email|e_?mail|phone|telephone|mobile|ssn|tax_?id|passport)'),
        B(r'(?:birth_?date|dob|address|street|zip_?code|postal_?code)'),
        B(r'(?:first_?name|last_?name|full_?name|nationality|nat_id)'),
        B(r'(?:driver_?lic|license_?num|government_?id|gov_?id)'),
        B(r'(?:user_?id|customer_?id|account_?id|profile_?id|applicant)'),
        r'resume|career_?tracker|cv_?upload|hr_?candidate',
        # Non-English national IDs (DCWF 733 additions)
        B(r'(?:documento_identidad|dni|nie|cpf|rg|aadhaar|pan_no)'),
        B(r'(?:mykad|nric|cedula|numero_carnet|personnummer|bsn|tckn)'),
        B(r'(?:shenfenzheng|nationalRegistrationNumber)'),
    ],
    'PHI': [
        B(r'(?:patient|diagnosis|medical|clinical|prescript|treatment)'),
        B(r'(?:hipaa|phi|ehr|emr|disease|symptom|hospital)'),
        B(r'(?:icd_?\d|cpt_?code|snomed|loinc)'),
        B(r'hypertension|diabetes|oncology|cardio|neurology|radiology'),
        # Non-English clinical vocabulary (DCWF 733 additions)
        B(r'(?:paciente|historia_clinica|dossier_medical|klinik|krankenakte)'),
        B(r'(?:bolnitsa|hasta|pasien|prontuario|kanja)'),
        B(r'(?:nhs_no|read_codes|mkb_10)'),
    ],
    'FINANCE': [
        B(r'(?:account_?num|payment|transaction|credit_?card|cvv|iban|swift)'),
        B(r'(?:bank|wallet|merchant|invoice|billing|charge)'),
        B(r'(?:btc|eth|crypto|forex|trading|ledger)'),
        # Non-Western payment rails (DCWF 733 additions)
        B(r'(?:upi|vpa|bhim|alipay|wechat_pay|unionpay)'),
        B(r'(?:mpesa|airtel_money|paytm|pix|sepa_xml)'),
        B(r'(?:clabe|interac|iso20022|ach_routing)'),
    ],
    'DEFENSE_GOV': [
        # English-coded TLDs
        r'\.mil\b|\.gov\b|\.go\.[a-z]{2}\b|\.mil\.[a-z]{2}\b',
        # Non-English government TLDs (DCWF 733 additions)
        r'\.gouv\.[a-z]{2}\b|\.gob\.[a-z]{2}\b|\.bund\.de\b',
        r'\.gc\.ca\b|\.govt\.nz\b|\.gov\.cn\b|\.gov\.il\b',
        r'\.gov\.in\b|\.go\.id\b|\.gov\.br\b',
        # English agency vocabulary — long enough that FP risk is acceptable
        B(r'(?:classified|defense_clearance|secret_clearance)'),
        B(r'(?:dod_(?:contract|cage|duns)|nsa_(?:tao|cyber)|cia_(?:operations|intelligence)|fbi_(?:cyber|intelligence))'),
        # Non-US agency vocabulary — compound forms only to avoid FP collision
        # (e.g., `pla` alone would match `play`, `placeholder`; `mod_uk` is safer)
        B(r'(?:mod_uk|bundeswehr|dgse_(?:bureau|service)|fsb_(?:russia|service))'),
        B(r'(?:gru_(?:russia|intel)|pla_(?:army|navy|airforce|rocket_force)|mss_(?:china|state_security))'),
        B(r'(?:idf_(?:israel|unit)|mossad_(?:operations|intel)|raw_(?:india|wing)|isi_(?:pakistan|intel))'),
        B(r'(?:itar|ear_export|cui_(?:basic|specified)|nipr|sipr|jwics)'),
        # NOTE: named-prime contractor patterns (lockheed/raytheon/etc) MOVED
        # to operator-derived rules per DCWF 733 — no targeting lists in
        # the compiled-in dictionary.
    ],
    'CRITICAL_INFRA': [
        # Industrial protocols (high precision)
        B(r'(?:scada|modbus|opc_?ua|dnp3|bacnet|iec_?61850|profinet)'),
        # NOTE: `plc` alone removed per FP audit — too short, collides with
        # `placeholder`, `place_*`, `plc_log` (programming). Use compound only.
        B(r'(?:plc_(?:address|register|coil)|plc_program)'),
        # Tightened protocol-adjacent vocabulary
        B(r'(?:rtu|hmi|dcs|safety_plc|process_control)'),
        # Utility equipment (compound only — `pipeline`/`valve`/`pump`/`grid`/`relay`
        # alone false-fire on RAG pipelines, ML pipelines, smart grids of any kind)
        B(r'(?:gas_pipeline|oil_pipeline|water_pipeline|pipeline_(?:pressure|flow|leak))'),
        B(r'(?:power_grid|smart_grid|electrical_grid|grid_(?:voltage|frequency|stability))'),
        B(r'(?:substation|transformer_(?:oil|temp|tap)|turbine_(?:rpm|temp|vibration)|reactor_(?:core|coolant|control))'),
        B(r'(?:water_treat|wastewater|sewage_plant|hvac_(?:zone|chiller)|cooling_tower)'),
        # Carrier optical / telecom — compound only
        B(r'(?:optical_(?:rx|tx)|sfp_temp|fiber_optic|bias_current_(?:tx|rx|sfp|optical)|sfp_bias)'),
        B(r'(?:gnss|gps_time|ptp_clock|grandmaster_clock)'),
        # Non-Western utility operator vocabulary
        B(r'(?:state_grid|sgcc|csg|gazprom|rosenergo|pgcil)'),
        B(r'(?:eskom|petrobras_scada|pemex_scada|aramco_scada|acueducto|saneamiento)'),
    ],
    'GENERIC_INFRA': [
        B(r'(?:cadvisor|node_?exporter|blackbox(?:_?exporter)?|process_?exporter)'),
        B(r'(?:nginx|apache|httpd|haproxy|envoy|traefik|caddy)'),
        B(r'(?:mysql|postgres|mariadb|mongodb|redis|memcache|elasticsearch)'),
        B(r'(?:kafka|rabbitmq|nats|pulsar|activemq)'),
        B(r'(?:kubelet|kube_?state|metrics_?server|prometheus|grafana)'),
        B(r'(?:cpu_?(?:user|system|idle|iowait)|memory_?(?:used|free|cached))'),
        B(r'(?:disk_?(?:io|read|write)|filesystem_?(?:size|free))'),
        B(r'(?:network_?(?:rx|tx)|tcp_?(?:established|wait)|http_?requests)'),
    ],
    # ── AI/ML sub-categories (DCWF 753 split) ─────────────────────────────
    'LLM_SERVING': [
        B(r'vllm[:_-]?(?:gpu_cache_usage_perc|num_requests_(?:running|waiting|swapped)|prompt_tokens_total|generation_tokens_total|time_to_first_token_seconds|time_per_output_token_seconds)'),
        B(r'vllm_(?:cache_config_info|model_executor|paged_attention)'),
        B(r'tgi_(?:batch_(?:current_size|next_size)|request_(?:duration|queue_duration|input_length|generated_tokens)|queue_size)'),
        B(r'sglang_(?:router|backend|cache_hit_rate|prefill_throughput|decode_throughput)'),
        B(r'lmdeploy_(?:turbomind|pytorch_engine|kv_cache)'),
        B(r'triton_(?:inference_(?:count|exec_count|queue_duration_us)|model_(?:repository|state)|gpu_(?:memory_used_bytes|utilization))'),
        B(r'ollama(?:_(?:api|models|generate|chat|embed|pull|ps))?'),
        B(r'(?:llama_cpp|ggml|gguf)_(?:model|context|tokens|threads)'),
        B(r'(?:text_generation_(?:webui|inference)|tabbyAPI|aphrodite_engine)'),
        B(r'(?:tokens_?per_?second|prompt_?tokens|completion_?tokens|inference_?(?:latency|queue|qps)|model_?load)'),
        B(r'(?:openai_api_(?:requests|tokens)|openai_chat_completion|openai_embedding_(?:request|tokens))'),
    ],
    'LLM_TRAINING': [
        B(r'pl_(?:trainer|callback|module|datamodule)_(?:step|epoch|loss)'),
        B(r'accelerate_(?:state|distributed|mixed_precision|gradient_accumulation)'),
        B(r'deepspeed_(?:zero[123]?|stage[123]|offload|moe|pipeline_parallel)'),
        B(r'megatron_(?:tensor_parallel|pipeline_parallel|sequence_parallel|tp_size|pp_size)'),
        B(r'(?:jax|flax)_(?:pjit|pmap|jit_cache|device_mesh)'),
        B(r'fsdp_(?:wrap|shard|reduce_scatter|all_gather)'),
        B(r'(?:train|val|test)_(?:loss|acc|perplexity|bleu|rouge|wer|cer)'),
        B(r'(?:learning_rate|lr_scheduler|warmup_steps|grad_(?:scale|norm|clip)|optimizer_(?:state|step))'),
        B(r'(?:pytorch|tensorflow|finetune|lora|adapter)'),
        B(r'mlflow_(?:run_(?:id|name|status)|experiment_(?:id|name)|registered_model|model_version|artifact_uri)'),
        B(r'wandb_(?:run_(?:id|name|path)|sweep_(?:id|name)|project|entity|artifact)'),
        B(r'clearml_(?:task_(?:id|name)|project|queue|worker|model_id)'),
        B(r'neptune_(?:run_(?:id|name)|project|workspace|metadata)'),
        B(r'comet(?:_ml)?_(?:experiment_(?:id|key)|workspace|project)'),
        B(r'polyaxon_(?:run_(?:id|uuid)|project|component|operation)'),
        B(r'determined_(?:experiment_(?:id|name)|trial_id|checkpoint_uuid)'),
    ],
    'VECTOR_DB': [
        B(r'(?:qdrant|milvus|weaviate|chroma|pinecone|pgvector|vespa|marqo|vald)'),
        B(r'pinecone_(?:index|namespace|vector_count|upsert|query_(?:duration|count))'),
        B(r'weaviate_(?:class|shard|tenant|vector_index|cluster_status)'),
        B(r'(?:opensearch|elasticsearch)_knn_(?:index|query|cache|ann)'),
        B(r'faiss_(?:index_(?:ivf|hnsw|pq|flat|ivfpq)|nprobe|nlist)'),
        B(r'(?:annoy|scann|nmslib)_(?:index|tree|search)'),
        B(r'(?:hnsw|ann_recall|embedding_(?:req|latency)|vector_(?:db|index))'),
    ],
    'RAG_AGENT': [
        B(r'(?:rag|retrieval|context_?window)'),
        B(r'(?:langchain|llama_?index|haystack|langgraph|autogen|crewai)'),
        B(r'llama_?index_(?:node_(?:id|parser)|document_id|query_engine|retriever)'),
        B(r'haystack_(?:pipeline|node|document_store|retriever|reader)'),
        B(r'langgraph_(?:state|node|edge|checkpoint|thread_id)'),
        B(r'autogen_(?:agent|groupchat|conversation|role)'),
        B(r'crewai_(?:crew|task|agent|tool|process)'),
        B(r'(?:autogpt|babyagi|agentgpt)_(?:task|step|goal|memory)_id'),
        B(r'open_?interpreter_(?:session|code|exec)'),
        B(r'(?:devin|replit_agent|cursor|aider)_(?:session|workspace|patch|edit)'),
        B(r'(?:agent|tool|skill)_(?:call_id|invocation_id|trace_id|exec_id)'),
    ],
    'GPU_INFRA': [
        B(r'(?:dcgm|nvidia_?(?:gpu|smi)|nvml|cuda|rocm|tensor_?rt)'),
        B(r'(?:gpu_?(?:util|temp|mem|power)|kv_?cache|hbm_?usage)'),
        B(r'(?:habana|hpu)_(?:gaudi|synapse|hl_smi|hpu_util)'),
        B(r'(?:amd|rocm)_(?:mi(?:25|50|60|100|210|250|300)|rocm_smi|gpu_dpm)'),
        B(r'(?:cerebras|wse[23]?)_(?:wafer|appliance|swarm)'),
        B(r'(?:graphcore|ipu)_(?:bow|pod16|poplar|gcl)'),
        B(r'neuron_(?:core|device|runtime|monitor)|(?:trainium|inferentia)[12]?'),
        B(r'(?:runpod|coreweave|lambdalabs|paperspace|modal|fluidstack|crusoe|together_?ai)'),
        B(r'(?:runpodip|safe_?runpod|secure_?pod)'),
        B(r'slurm_(?:job_(?:id|name|state)|partition|qos|gres_gpu)'),
        B(r'kubeflow_(?:pipeline|run|experiment|component|workflow)'),
        B(r'ray_(?:job_(?:id|name)|actor|task|placement_group|cluster)'),
        B(r'volcano_(?:queue|job|podgroup|priority)'),
        # Non-Western model families + frameworks (DCWF 733 additions)
        B(r'(?:qwen|baichuan|glm|deepseek|moonshot|kimi|yi_|wenxin|tongyi)'),
        B(r'(?:paddlepaddle|mindspore|bittensor)'),
    ],
    'LLM_OBSERVABILITY': [
        B(r'(?:langfuse|langsmith|helicone|phoenix|arize|openllmetry)'),
        B(r'helicone_(?:trace|request|user|property)_id'),
        B(r'(?:phoenix|arize)_(?:span|trace|embedding|drift|monitor)'),
        B(r'openllmetry_(?:trace|span|llm|gen_ai)'),
        B(r'langfuse_(?:trace|observation|generation|score|dataset)'),
    ],
    'AI_PII_SIGNAL': [
        B(r'(?:prompt|completion|generation|embedding)_tokens_by_(?:user|customer|tenant|account)'),
        B(r'(?:tokens|requests|cost)_per_(?:user|customer|tenant|account|api_key)'),
        B(r'(?:user|customer|tenant|account)_(?:llm|inference|embedding|completion)_(?:usage|count|tokens|latency)'),
        B(r'(?:user|customer|tenant|account|session)_id.{0,32}(?:prompt|completion|inference|embedding|model)'),
        B(r'(?:prompt|inference|embedding|generation)_(?:latency|duration|qps).{0,32}(?:tenant|user|customer|org|workspace)'),
        B(r'(?:model|adapter|finetune)_used_by_(?:user|customer|tenant|account|org)'),
        B(r'(?:rag|retrieval|context|search)_(?:per|by)_(?:user|customer|tenant|workspace)'),
        B(r'langfuse_(?:user|session|tenant)_(?:trace|generation|score)'),
        B(r'helicone_user_(?:trace_id|request_count|cost)'),
        B(r'(?:api_key|bearer_token|customer_token|user_token)_(?:prompt|inference|model|tokens)'),
    ],
}

# Back-compat alias — fires AI_WORKLOAD when any sub-category fires.
AI_WORKLOAD_SUBCATS = ('LLM_SERVING', 'LLM_TRAINING', 'VECTOR_DB',
                       'RAG_AGENT', 'GPU_INFRA', 'LLM_OBSERVABILITY')

# Compiled patterns
COMPILED = {cat: [re.compile(p, re.I) for p in pats] for cat, pats in CATEGORIES.items()}

# IP detection
PRIV_IP_RX = re.compile(
    r'^(?:'
    r'10\.\d+\.\d+\.\d+'
    r'|172\.(?:1[6-9]|2[0-9]|3[01])\.\d+\.\d+'
    r'|192\.168\.\d+\.\d+'
    r'|127\.\d+\.\d+\.\d+'
    r'|169\.254\.\d+\.\d+'
    r'|fc[0-9a-f]{2}:'
    r'|fe80:'
    r')'
)
PUBLIC_IP_RX = re.compile(r'^\d+\.\d+\.\d+\.\d+$')

# DCWF 672 sealed-mode fix: TLD allowlist (real ccTLDs + common gTLDs).
# Everything not in this set buckets as `.<private>` to prevent
# operator-namespace leakage like .teye/.prod/.internal.
TLD_ALLOWLIST = {
    # Generic TLDs
    'com','net','org','io','ai','app','co','dev','xyz','tech','cloud','info',
    'biz','name','pro','site','online','store','space','tools','link',
    # ccTLDs (broad list)
    'us','uk','ca','de','fr','it','es','nl','be','ch','at','se','no','dk',
    'fi','pl','cz','sk','hu','ro','ru','ua','by','ee','lv','lt','tr','gr',
    'pt','ie','is','mt','cy','lu','li','mc','sm','va','ad','az','am','ge',
    'kz','uz','kg','tj','tm','mn','cn','jp','kr','tw','hk','sg','my','th',
    'id','vn','ph','in','pk','bd','lk','np','bt','mm','la','kh','bn','mv',
    'ae','sa','qa','bh','kw','om','jo','lb','il','ps','sy','iq','ir','eg',
    'ly','sd','ss','tn','dz','ma','mr','sn','ml','bf','ne','td','cm','cf',
    'cg','cd','ga','gq','ao','zm','zw','mw','mz','ng','gh','ci','tg','bj',
    'lr','sl','gn','gw','cv','gm','et','er','dj','so','ke','tz','ug','rw',
    'bi','ke','mg','mu','sc','km','re','yt','za','ls','sz','bw','na','st',
    'au','nz','fj','pg','sb','vu','nc','pf','to','tv','ws','ki','nr','mh',
    'fm','pw','ck','nu','tk','wf',
    'mx','gt','bz','sv','hn','ni','cr','pa','cu','ht','do','pr','jm','tt',
    'bb','gd','vc','lc','dm','ag','kn','bs','tc','vg','ai','cv',
    'br','ar','cl','uy','py','bo','pe','ec','co','ve','gy','sr','gf','fk',
    # Multi-label TLDs / sLDs treated as "real"
    'gov','mil','edu','int','arpa',
    # Country-coded second-level (we won't strip these in the suffix function)
}

# ───────────────────────────────────────────────────────────────────────────────
# Extractors
# ───────────────────────────────────────────────────────────────────────────────

def extract_vm_verify(host_json):
    """Extract scrape targets + metric names + labels from VictoriaMetrics evidence."""
    out = {'targets': [], 'metric_names': [], 'labels': [], 'pool_names': []}
    ev = host_json.get('evidence', {})

    targets_body = ev.get('targets', {}).get('body', '')
    if targets_body:
        for m in re.finditer(r'"scrapeUrl"\s*:\s*"([^"]+)"', targets_body):
            url = m.group(1)
            host_m = re.match(r'https?://([^/:]+)', url)
            if host_m:
                out['targets'].append(host_m.group(1))
            # Also extract the path tail (after the host) for context, schema-only
        for m in re.finditer(r'"(?:scrapePool|job)"\s*:\s*"([^"]+)"', targets_body):
            out['pool_names'].append(m.group(1))
        # Label keys + values — DCWF 753 bug 2 fix: don't drop these
        for m in re.finditer(r'"labels"\s*:\s*\{([^}]+)\}', targets_body):
            for lm in re.finditer(r'"([^"]+)"\s*:\s*"([^"]+)"', m.group(1)):
                out['labels'].append(lm.group(1))
                out['labels'].append(lm.group(2))

    mn_body = ev.get('metric_names', {}).get('body', '')
    if mn_body:
        try:
            j = json.loads(mn_body)
            data = j.get('data', [])
            if isinstance(data, list):
                out['metric_names'].extend(data)
        except (json.JSONDecodeError, AttributeError, TypeError):
            pass

    return out


def extract_chroma_campaign(host_json):
    out = {'collection_names': []}
    names = host_json.get('collection_names_sample') or []
    out['collection_names'].extend(names)
    for k in ('v1_body_full', 'v2_body_full', 'v1_body', 'v2_body'):
        body = host_json.get(k, '')
        if body:
            for m in re.finditer(r'"name"\s*:\s*"([^"]+)"', body):
                out['collection_names'].append(m.group(1))
    out['collection_names'] = list(set(out['collection_names']))
    return out


def extract_mlflow_tracking(host_json):
    """Extract experiment/model/tag identifiers from MLflow tracking API evidence."""
    out = {'experiment_names': [], 'registered_models': [], 'tag_keys': [], 'param_keys': []}
    ev = host_json.get('evidence', {})

    exp_body = ev.get('experiments_list', {}).get('body', '')
    if exp_body:
        try:
            j = json.loads(exp_body)
            for exp in j.get('experiments', []) or []:
                if isinstance(exp, dict):
                    n = exp.get('name')
                    if isinstance(n, str): out['experiment_names'].append(n)
                    for tag in exp.get('tags', []) or []:
                        if isinstance(tag, dict) and isinstance(tag.get('key'), str):
                            out['tag_keys'].append(tag['key'])
        except (json.JSONDecodeError, AttributeError, TypeError):
            pass

    rm_body = ev.get('registered_models_list', {}).get('body', '')
    if rm_body:
        try:
            j = json.loads(rm_body)
            for m in j.get('registered_models', []) or []:
                if isinstance(m, dict):
                    n = m.get('name')
                    if isinstance(n, str): out['registered_models'].append(n)
                    for tag in m.get('tags', []) or []:
                        if isinstance(tag, dict) and isinstance(tag.get('key'), str):
                            out['tag_keys'].append(tag['key'])
        except (json.JSONDecodeError, AttributeError, TypeError):
            pass

    runs_body = ev.get('runs_search', {}).get('body', '')
    if runs_body:
        try:
            j = json.loads(runs_body)
            for run in j.get('runs', []) or []:
                data = run.get('data', {}) if isinstance(run, dict) else {}
                for p in data.get('params', []) or []:
                    if isinstance(p, dict) and isinstance(p.get('key'), str):
                        out['param_keys'].append(p['key'])
        except (json.JSONDecodeError, AttributeError, TypeError):
            pass

    return out


def extract_langfuse_traces(host_json):
    """Extract trace/prompt/score identifiers from Langfuse public API evidence."""
    out = {'trace_names': [], 'prompt_names': [], 'score_names': [],
           'tag_values': [], 'metadata_keys': []}
    ev = host_json.get('evidence', {})

    tr_body = ev.get('public_traces', {}).get('body', '')
    if tr_body:
        try:
            j = json.loads(tr_body)
            for t in j.get('data', []) or []:
                if not isinstance(t, dict): continue
                n = t.get('name')
                if isinstance(n, str): out['trace_names'].append(n)
                for tag in t.get('tags', []) or []:
                    if isinstance(tag, str): out['tag_values'].append(tag)
                md = t.get('metadata')
                if isinstance(md, dict):
                    out['metadata_keys'].extend(k for k in md.keys() if isinstance(k, str))
        except (json.JSONDecodeError, AttributeError, TypeError):
            pass

    pr_body = ev.get('public_prompts', {}).get('body', '')
    if pr_body:
        try:
            j = json.loads(pr_body)
            for p in j.get('data', []) or []:
                if isinstance(p, dict) and isinstance(p.get('name'), str):
                    out['prompt_names'].append(p['name'])
        except (json.JSONDecodeError, AttributeError, TypeError):
            pass

    sc_body = ev.get('public_scores', {}).get('body', '')
    if sc_body:
        try:
            j = json.loads(sc_body)
            for s in j.get('data', []) or []:
                if isinstance(s, dict) and isinstance(s.get('name'), str):
                    out['score_names'].append(s['name'])
        except (json.JSONDecodeError, AttributeError, TypeError):
            pass

    return out


def extract_generic(host_json, name_paths=None):
    out = {'names': []}
    if not name_paths:
        return out
    for path in name_paths:
        parts = path.split('.')
        cur = host_json
        for p in parts:
            if isinstance(cur, dict) and p in cur:
                cur = cur[p]
            else:
                cur = None
                break
        if isinstance(cur, list):
            out['names'].extend(str(x) for x in cur)
        elif isinstance(cur, str):
            out['names'].append(cur)
    return out


PROFILES = {
    'vm-verify': extract_vm_verify,
    'chroma-campaign': extract_chroma_campaign,
    'mlflow-tracking': extract_mlflow_tracking,
    'langfuse-traces': extract_langfuse_traces,
    'generic': extract_generic,
}


# ───────────────────────────────────────────────────────────────────────────────
# Analyzers
# ───────────────────────────────────────────────────────────────────────────────

def classify_strings(strings):
    """Bag-of-fields classification. Returns category counts + matched-rule
    counts. Does NOT echo the strings in the return value."""
    cat_counts = Counter()
    hit_count = 0
    per_string_hits = []
    for s in strings:
        hits = []
        for cat, patterns in COMPILED.items():
            for p in patterns:
                if p.search(s):
                    hits.append(cat)
                    break
        if hits:
            hit_count += 1
            for c in hits:
                cat_counts[c] += 1
            # Back-compat: AI_WORKLOAD fires when any sub-category fires
            if any(c in AI_WORKLOAD_SUBCATS for c in hits):
                cat_counts['AI_WORKLOAD'] += 1
            per_string_hits.append((s, hits))
    return cat_counts, hit_count, per_string_hits


def structural_counts(strings, sealed=True, total_min_visible=None):
    """Count RFC1918 vs public IPv4 vs hostnames. TLD suffix histogram filtered
    against allowlist + frequency floor to prevent operator-namespace leakage."""
    private = 0
    public = 0
    hostnames = 0
    other = 0
    suffix_counts = Counter()
    private_suffix_count = 0
    for s in strings:
        if PRIV_IP_RX.match(s):
            private += 1
        elif PUBLIC_IP_RX.match(s):
            public += 1
        elif '.' in s:
            hostnames += 1
            parts = s.rsplit('.', 2)
            if len(parts) >= 2:
                suf = parts[-1].lower().strip()
                if suf in TLD_ALLOWLIST:
                    suffix_counts['.' + suf] += 1
                else:
                    private_suffix_count += 1
        else:
            other += 1

    # Sealed-mode frequency floor: hide low-N suffixes
    if sealed:
        total = len(strings) or 1
        floor = total_min_visible or max(5, math.ceil(0.01 * total))
        visible = [(s, n) for s, n in suffix_counts.items() if n >= floor]
        suppressed = sum(n for s, n in suffix_counts.items() if n < floor)
    else:
        visible = list(suffix_counts.items())
        suppressed = 0

    return {
        'rfc1918': private,
        'public_ipv4': public,
        'hostnames': hostnames,
        'other': other,
        'top_tld_suffixes': sorted(visible, key=lambda x: -x[1])[:10],
        'private_namespace_count': private_suffix_count,
        'suppressed_low_n_suffixes': suppressed,
    }


def char_entropy(s):
    if not s:
        return 0.0
    freq = Counter(s)
    total = len(s)
    return -sum((c/total) * math.log2(c/total) for c in freq.values())


def statistical_shape(strings):
    if not strings:
        return {'cardinality_total': 0, 'cardinality_distinct': 0,
                'len_median': 0, 'len_p99': 0, 'entropy_mean': 0}
    unique = set(strings)
    lengths = sorted(len(s) for s in strings)
    entropies = [char_entropy(s) for s in strings]
    return {
        'cardinality_total': len(strings),
        'cardinality_distinct': len(unique),
        'len_min': lengths[0],
        'len_median': lengths[len(lengths)//2],
        'len_p99': lengths[int(len(lengths)*0.99)] if len(lengths) > 1 else lengths[0],
        'len_max': lengths[-1],
        'entropy_mean': round(sum(entropies)/len(entropies), 2),
        'entropy_p99': round(sorted(entropies)[int(len(entropies)*0.99)] if len(entropies)>1 else entropies[0], 2),
        'low_entropy_count': sum(1 for e in entropies if e < 3.0),
        'high_entropy_count': sum(1 for e in entropies if e > 4.5),
    }


# ───────────────────────────────────────────────────────────────────────────────
# Main scanner
# ───────────────────────────────────────────────────────────────────────────────

def scan(corpus_dir, source, name_paths=None, include_samples=0,
         low_n_streams=False, sealed=True):
    """Scan a corpus directory. Sealed=True by default per restraint discipline.
    Low_n_streams=True allows sensitivity reporting on small streams (default
    suppressed to prevent single-string attribution per DCWF 733)."""
    profile_fn = PROFILES[source]
    files = sorted(Path(corpus_dir).glob('*.json'))
    if not files:
        return {'error': f'no .json files in {corpus_dir}'}

    all_targets = []
    all_metric_names = []
    all_collection_names = []
    all_labels = []
    all_pool_names = []
    all_experiment_names = []
    all_registered_models = []
    all_tag_keys = []
    all_param_keys = []
    all_trace_names = []
    all_prompt_names = []
    all_score_names = []
    all_tag_values = []
    all_metadata_keys = []
    all_generic = []
    hosts_with_data = 0

    for f in files:
        # DCWF 672 robustness fix: catch UnicodeDecodeError
        try:
            b = f.read_bytes()
            h = json.loads(b.decode('utf-8', errors='replace'))
        except (json.JSONDecodeError, OSError, ValueError):
            continue

        if source == 'vm-verify':
            ext = profile_fn(h)
            if ext['targets'] or ext['metric_names'] or ext['labels'] or ext['pool_names']:
                hosts_with_data += 1
            all_targets.extend(ext['targets'])
            all_metric_names.extend(ext['metric_names'])
            all_labels.extend(ext['labels'])
            all_pool_names.extend(ext['pool_names'])
        elif source == 'chroma-campaign':
            ext = profile_fn(h)
            if ext['collection_names']:
                hosts_with_data += 1
            all_collection_names.extend(ext['collection_names'])
        elif source == 'mlflow-tracking':
            ext = profile_fn(h)
            if any(ext[k] for k in ext):
                hosts_with_data += 1
            all_experiment_names.extend(ext['experiment_names'])
            all_registered_models.extend(ext['registered_models'])
            all_tag_keys.extend(ext['tag_keys'])
            all_param_keys.extend(ext['param_keys'])
        elif source == 'langfuse-traces':
            ext = profile_fn(h)
            if any(ext[k] for k in ext):
                hosts_with_data += 1
            all_trace_names.extend(ext['trace_names'])
            all_prompt_names.extend(ext['prompt_names'])
            all_score_names.extend(ext['score_names'])
            all_tag_values.extend(ext['tag_values'])
            all_metadata_keys.extend(ext['metadata_keys'])
        else:
            ext = profile_fn(h, name_paths)
            if ext['names']:
                hosts_with_data += 1
            all_generic.extend(ext['names'])

    report = {
        'glance_version': '0.1.1',
        'corpus_dir': str(corpus_dir),
        'source_profile': source,
        'files_scanned': len(files),
        'hosts_with_data': hosts_with_data,
        'sealed_mode': sealed,
        'low_n_streams_allowed': low_n_streams,
    }

    # Per-stream analysis
    streams = {}
    if all_targets: streams['scrape_targets'] = all_targets
    if all_metric_names: streams['metric_names'] = all_metric_names
    if all_collection_names: streams['collection_names'] = all_collection_names
    if all_pool_names: streams['scrape_pool_names'] = all_pool_names
    # DCWF 753 bug 2 fix: promote labels to first-class stream
    if all_labels: streams['labels'] = all_labels
    if all_experiment_names: streams['experiment_names'] = all_experiment_names
    if all_registered_models: streams['registered_models'] = all_registered_models
    if all_tag_keys: streams['tag_keys'] = all_tag_keys
    if all_param_keys: streams['param_keys'] = all_param_keys
    if all_trace_names: streams['trace_names'] = all_trace_names
    if all_prompt_names: streams['prompt_names'] = all_prompt_names
    if all_score_names: streams['score_names'] = all_score_names
    if all_tag_values: streams['tag_values'] = all_tag_values
    if all_metadata_keys: streams['metadata_keys'] = all_metadata_keys
    if all_generic: streams['names'] = all_generic

    report['streams'] = {}
    for name, strs in streams.items():
        cat_counts, hit_count, per_hits = classify_strings(strs)
        # DCWF 733 low-N suppression: hide sensitivity output on tiny streams
        # unless explicitly opted in
        if sealed and not low_n_streams and len(strs) < 20:
            cat_counts_visible = {}
            note = f'sensitivity suppressed (stream size {len(strs)} < 20); pass --low-n-streams to override'
        else:
            cat_counts_visible = dict(cat_counts)
            note = None

        stream_report = {
            'count_total': len(strs),
            'count_distinct': len(set(strs)),
            'structural': structural_counts(strs, sealed=sealed),
            'sensitivity_categories': cat_counts_visible,
            'category_hit_count': hit_count if not (sealed and not low_n_streams and len(strs) < 20) else None,
            'statistical_shape': statistical_shape(strs),
        }
        if note: stream_report['note'] = note

        if include_samples > 0:
            samples = []
            seen = set()
            for s, hits in per_hits:
                if s in seen: continue
                seen.add(s)
                samples.append({'value': s, 'categories': hits})
                if len(samples) >= include_samples:
                    break
            stream_report['flagged_samples'] = samples
        report['streams'][name] = stream_report

    # global category roll-up
    global_cats = Counter()
    for n, s in report['streams'].items():
        for cat, n_hits in s.get('sensitivity_categories', {}).items():
            global_cats[cat] += n_hits
    report['global_sensitivity_rollup'] = dict(global_cats)

    return report


# ───────────────────────────────────────────────────────────────────────────────
# Self-test (verify subcommand)
# ───────────────────────────────────────────────────────────────────────────────

SELF_TEST_FIXTURES = [
    # (string, expected_categories)
    ('safe_runpod_dcgm_exporter', ['GPU_INFRA']),
    ('runpodip', ['GPU_INFRA']),
    ('vllm_prompt_tokens_total', ['LLM_SERVING']),
    ('tgi_batch_current_size', ['LLM_SERVING']),
    ('mlflow_run_id', ['LLM_TRAINING']),
    ('langfuse_trace_id', ['LLM_OBSERVABILITY']),
    ('helicone_user_cost', ['AI_PII_SIGNAL', 'LLM_OBSERVABILITY']),
    ('prompt_tokens_by_user', ['AI_PII_SIGNAL', 'LLM_SERVING']),
    ('faiss_index_hnsw', ['VECTOR_DB']),
    ('langchain_agent', ['RAG_AGENT']),
    ('paciente_id', ['PHI']),
    ('aadhaar', ['PII']),
    ('alipay', ['FINANCE']),
    ('state_grid_substation', ['CRITICAL_INFRA']),
    ('cadvisor', ['GENERIC_INFRA']),
    ('node_exporter', ['GENERIC_INFRA']),
    ('safe_runpod_cadvisor', ['GPU_INFRA', 'GENERIC_INFRA']),
    ('not_a_match_at_all_xyz', []),
]

def self_test():
    fail = 0
    for s, expected in SELF_TEST_FIXTURES:
        _, _, hits = classify_strings([s])
        actual_cats = set()
        for _, cats in hits:
            actual_cats.update(cats)
        # ignore AI_WORKLOAD alias
        actual_cats.discard('AI_WORKLOAD')
        expected_set = set(expected)
        if actual_cats != expected_set:
            print(f"FAIL: {s!r} got {sorted(actual_cats)}, expected {sorted(expected_set)}")
            fail += 1
        else:
            print(f"OK:   {s!r} -> {sorted(actual_cats)}")
    print(f"\n{len(SELF_TEST_FIXTURES) - fail}/{len(SELF_TEST_FIXTURES)} fixtures passed")
    return fail


# ───────────────────────────────────────────────────────────────────────────────
# Pretty-printer
# ───────────────────────────────────────────────────────────────────────────────

def render_table(report):
    lines = []
    lines.append("=" * 72)
    lines.append(f"  GLANCE REPORT  (v{report.get('glance_version','?')}, sealed={report.get('sealed_mode',True)})")
    lines.append("=" * 72)
    lines.append(f"  corpus:         {report['corpus_dir']}")
    lines.append(f"  profile:        {report['source_profile']}")
    lines.append(f"  files scanned:  {report['files_scanned']}")
    lines.append(f"  hosts w/ data:  {report['hosts_with_data']}")
    lines.append("")

    for stream_name, s in report.get('streams', {}).items():
        lines.append("-" * 72)
        lines.append(f"  STREAM: {stream_name}")
        lines.append("-" * 72)
        lines.append(f"    total values:      {s['count_total']}")
        lines.append(f"    distinct values:   {s['count_distinct']}")
        if s.get('note'):
            lines.append(f"    NOTE: {s['note']}")
        lines.append("")
        lines.append(f"    STRUCTURAL (no content read):")
        st = s['structural']
        lines.append(f"      RFC1918 internal IPs:  {st['rfc1918']}")
        lines.append(f"      Public IPv4:           {st['public_ipv4']}")
        lines.append(f"      DNS hostnames:         {st['hostnames']}")
        lines.append(f"      Other / non-IP-DNS:    {st['other']}")
        if st.get('private_namespace_count'):
            lines.append(f"      Private-namespace suffixes (hidden): {st['private_namespace_count']}")
        if st.get('suppressed_low_n_suffixes'):
            lines.append(f"      Low-N TLD suffixes (suppressed): {st['suppressed_low_n_suffixes']}")
        if st['top_tld_suffixes']:
            lines.append(f"      Top TLD suffixes (allowlist + frequency floor):")
            for suf, n in st['top_tld_suffixes'][:6]:
                lines.append(f"        {suf:<10}  {n}")
        lines.append("")
        cats = s.get('sensitivity_categories', {})
        lines.append(f"    SENSITIVITY (bag-of-fields, names only):")
        if cats:
            for cat, n in sorted(cats.items(), key=lambda x: -x[1]):
                lines.append(f"      {cat:<22}  {n} hits")
        else:
            lines.append(f"      (no matches in any category dictionary)")
        if s.get('category_hit_count') is not None:
            lines.append(f"    Values matching any category: {s['category_hit_count']}/{s['count_total']}")
        lines.append("")
        lines.append(f"    STATISTICAL SHAPE (hashed, no content shown):")
        ss = s['statistical_shape']
        lines.append(f"      length median / p99 / max:  {ss.get('len_median',0)} / {ss.get('len_p99',0)} / {ss.get('len_max',0)}")
        lines.append(f"      entropy mean / p99:         {ss.get('entropy_mean',0)} / {ss.get('entropy_p99',0)}")
        lines.append(f"      low-entropy (human-named):  {ss.get('low_entropy_count',0)}")
        lines.append(f"      high-entropy (random ID):   {ss.get('high_entropy_count',0)}")
        lines.append("")

    lines.append("=" * 72)
    lines.append(f"  GLOBAL SENSITIVITY ROLLUP (across all streams)")
    lines.append("=" * 72)
    for cat, n in sorted(report.get('global_sensitivity_rollup', {}).items(), key=lambda x: -x[1]):
        lines.append(f"  {cat:<22}  {n} hits")
    lines.append("")

    if any(s.get('flagged_samples') for s in report.get('streams', {}).values()):
        lines.append("=" * 72)
        lines.append("  FLAGGED SAMPLES (--include-samples was used)")
        lines.append("=" * 72)
        for stream_name, s in report['streams'].items():
            if s.get('flagged_samples'):
                lines.append(f"  Stream: {stream_name}")
                for sample in s['flagged_samples'][:10]:
                    lines.append(f"    [{','.join(sample['categories'])}] {sample['value']}")
        lines.append("")

    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(prog='glance', description='Schema-only sensitivity analyzer for sealed corpora.')
    sub = ap.add_subparsers(dest='cmd', required=True)

    scan_p = sub.add_parser('scan', help='scan a corpus directory')
    scan_p.add_argument('corpus_dir')
    scan_p.add_argument('--source', required=True, choices=list(PROFILES.keys()))
    scan_p.add_argument('-o', '--output')
    scan_p.add_argument('--include-samples', type=int, default=0)
    scan_p.add_argument('--name-paths')
    scan_p.add_argument('--json-only', action='store_true')
    scan_p.add_argument('--low-n-streams', action='store_true',
                        help='allow sensitivity reporting on streams with <20 values (DEFAULT: suppressed)')
    scan_p.add_argument('--no-sealed', action='store_true',
                        help='disable sealed-mode defaults (DEFAULT: sealed)')

    sub.add_parser('verify', help='run self-test against built-in fixtures')

    args = ap.parse_args()
    if args.cmd == 'scan':
        name_paths = args.name_paths.split(',') if args.name_paths else None
        report = scan(args.corpus_dir, args.source, name_paths=name_paths,
                      include_samples=args.include_samples,
                      low_n_streams=args.low_n_streams,
                      sealed=not args.no_sealed)
        if args.output:
            Path(args.output).write_text(json.dumps(report, indent=2))
            print(f"-> {args.output}", file=sys.stderr)
        if args.json_only:
            print(json.dumps(report, indent=2))
        else:
            print(render_table(report))
    elif args.cmd == 'verify':
        return self_test()

if __name__ == '__main__':
    sys.exit(main() or 0)
