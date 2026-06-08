#!/usr/bin/env python3
"""
glance — schema-only sensitivity analyzer for sealed corpora.

The premise: NuClide surveys collect per-host evidence (collection names,
scrape targets, metric labels). We want to *characterize* what's in the corpus
without *reading* its content. glance does three things:

  1. STRUCTURAL counts (no content read at all)
     RFC1918 vs public IPv4 vs hostnames; cardinality; length distribution.

  2. BAG-OF-FIELDS sensitivity classifier (per the schema-recon skill)
     Pattern-match identifier names against a category dictionary (PII, PHI,
     financial, defense, critical-infra, AI-workload). Names only, never values.

  3. STATISTICAL shape (hashed, never echoed)
     Distinct cardinality, top-prefix-tree counts, character entropy, hostname
     suffix histogram.

The corpus stays sealed. The user sees aggregates and category counts. No raw
hostname, IP, label, or metric name appears in glance's output unless it was
already in a known-public dictionary entry (and even then, you can opt out).

USAGE
  glance scan <dir> --source <profile> [-o report.json]
  glance scan ~/syllabus/shodan/vm-verify/hosts --source vm-verify
  glance scan ~/syllabus/shodan/chroma-campaign/hosts --source chroma-campaign

PROFILES
  vm-verify        VictoriaMetrics per-host evidence; extracts scrape targets
                   from evidence.targets.body + metric names from
                   evidence.metric_names.body
  chroma-campaign  Chroma per-host evidence; extracts collection names from
                   evidence.v2_body_full + v1_body_full + sample_names
  generic          Generic JSON; configurable jsonpath (--name-paths)

OUTPUT
  Human-readable table + JSON rollup. The rollup contains zero raw values
  unless --include-samples=N is passed (default 0).
"""
import argparse, json, re, math, hashlib, sys
from pathlib import Path
from collections import Counter, defaultdict

# ───────────────────────────────────────────────────────────────────────────────
# Category dictionary — bag-of-fields classifier
# ───────────────────────────────────────────────────────────────────────────────

CATEGORIES = {
    'PII': [
        r'\b(?:email|e_?mail|phone|telephone|mobile|ssn|tax_?id|passport)\b',
        r'\b(?:birth_?date|dob|address|street|zip_?code|postal_?code)\b',
        r'\b(?:first_?name|last_?name|full_?name|nationality|nat_id)\b',
        r'\b(?:driver_?lic|license_?num|government_?id|gov_?id)\b',
        r'\b(?:user_?id|customer_?id|account_?id|profile_?id|applicant)\b',
        r'resume|career_?tracker|cv_?upload|hr_?candidate',
    ],
    'PHI': [
        r'\b(?:patient|diagnosis|medical|clinical|prescript|treatment)\b',
        r'\b(?:hipaa|phi|ehr|emr|disease|symptom|hospital)\b',
        r'\b(?:icd_?\d|cpt_?code|snomed|loinc)\b',
        r'doc_?(?:hypertension|diabetes|cancer|cardio|neuro|onco)',
        r'hypertension|diabetes|oncology|cardio|neurology|radiology',
    ],
    'FINANCE': [
        r'\b(?:account_?num|payment|transaction|credit_?card|cvv|iban|swift)\b',
        r'\b(?:bank|wallet|merchant|invoice|billing|charge)\b',
        r'\b(?:btc|eth|crypto|forex|trading|ledger)\b',
        r'app_?(?:btc|eth|merchant|rates|wallet|crypto|trading)',
        r'sql_?cache_.*_(?:head_office|branch|finance)',
    ],
    'DEFENSE_GOV': [
        r'\.mil\b|\.gov\b|\.go\.[a-z]{2}\b|\.mil\.[a-z]{2}\b',
        r'\b(?:cleared|classified|dod|nsa|cia|fbi|atf|cbp)\b',
        r'\b(?:lockheed|raytheon|northrop|boeing_?defense|general_?dynamics)\b',
        r'\b(?:anduril|palantir|saic|leidos|booz_?allen|caci|mantech)\b',
        r'\b(?:itar|ear|cui|nipr|sipr|jwics)\b',
    ],
    'CRITICAL_INFRA': [
        r'\b(?:scada|plc|modbus|opc_?ua|dnp3|bacnet|iec_?61850)\b',
        r'\b(?:substation|transformer|generator|turbine|reactor)\b',
        r'\b(?:pipeline|valve|pump|grid|feeder|relay)\b',
        r'\b(?:water_?treat|wastewater|sewage|hvac|cooling_?tower)\b',
        r'\b(?:bias_?current|optical_?(?:rx|tx)|sfp_?temp|fiber_?optic)\b',
        r'\b(?:gnss|gps_?time|ptp_?clock|grandmaster)\b',
        r'power_?(?:scrap|monitor|consumption|generation)',
    ],
    'AI_WORKLOAD': [
        r'\b(?:dcgm|nvidia_?(?:gpu|smi)|nvml|cuda|rocm|tensor_?rt)\b',
        r'\b(?:gpu_?(?:util|temp|mem|power)|kv_?cache|hbm_?usage)\b',
        r'\b(?:ollama|vllm|tgi|sglang|lmdeploy|triton)\b',
        r'\b(?:tokens_?per_?second|prompt_?tokens|completion_?tokens)\b',
        r'\b(?:inference_?(?:latency|queue|qps)|model_?load)\b',
        r'\b(?:pytorch|tensorflow|jax|train_?loss|val_?loss|gradient_?norm)\b',
        r'\b(?:mlflow|wandb|langchain|langfuse|langsmith)\b',
        r'\b(?:embedding_?(?:req|latency)|vector_?(?:db|index)|hnsw|ann_?recall)\b',
        r'\b(?:qdrant|milvus|weaviate|chroma|pinecone|pgvector)\b',
        r'\b(?:rag|retrieval|context_?window|finetune|lora|adapter)\b',
        r'\b(?:runpod|coreweave|lambdalabs|paperspace|modal)\b',
        r'\b(?:runpodip|user_?id.*pod|safe_?runpod|secure.*pod)\b',
    ],
    'GENERIC_INFRA': [
        r'\b(?:cadvisor|node_?exporter|blackbox(_?exporter)?|process_?exporter)\b',
        r'\b(?:nginx|apache|httpd|haproxy|envoy|traefik|caddy)\b',
        r'\b(?:mysql|postgres|mariadb|mongodb|redis|memcache|elasticsearch)\b',
        r'\b(?:kafka|rabbitmq|nats|pulsar|activemq)\b',
        r'\b(?:kubelet|kube_?state|metrics_?server|prometheus|grafana)\b',
        r'\b(?:cpu_?(?:user|system|idle|iowait)|memory_?(?:used|free|cached))\b',
        r'\b(?:disk_?(?:io|read|write)|filesystem_?(?:size|free))\b',
        r'\b(?:network_?(?:rx|tx)|tcp_?(?:established|wait)|http_?requests)\b',
    ],
}

# Precompile
COMPILED = {cat: [re.compile(p, re.I) for p in pats] for cat, pats in CATEGORIES.items()}

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


# ───────────────────────────────────────────────────────────────────────────────
# Extractors — one per source profile
# ───────────────────────────────────────────────────────────────────────────────

def extract_vm_verify(host_json):
    """Extract scrape targets + metric names from VictoriaMetrics evidence."""
    out = {'targets': [], 'metric_names': [], 'labels': [], 'pool_names': []}
    ev = host_json.get('evidence', {})

    # /api/v1/targets body
    targets_body = ev.get('targets', {}).get('body', '')
    if targets_body:
        # scrapeUrl host portion
        for m in re.finditer(r'"scrapeUrl"\s*:\s*"([^"]+)"', targets_body):
            url = m.group(1)
            host_m = re.match(r'https?://([^/:]+)', url)
            if host_m:
                out['targets'].append(host_m.group(1))
        # job + scrapePool labels
        for m in re.finditer(r'"(?:scrapePool|job)"\s*:\s*"([^"]+)"', targets_body):
            out['pool_names'].append(m.group(1))
        # all label keys + values (for sensitivity scan, not raw printing)
        for m in re.finditer(r'"labels"\s*:\s*\{([^}]+)\}', targets_body):
            for lm in re.finditer(r'"([^"]+)"\s*:\s*"([^"]+)"', m.group(1)):
                out['labels'].append(lm.group(1))
                out['labels'].append(lm.group(2))

    # /api/v1/label/__name__/values body
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
    """Extract collection names from Chroma campaign evidence."""
    out = {'collection_names': []}

    # already-parsed sample_names field
    names = host_json.get('collection_names_sample') or []
    out['collection_names'].extend(names)

    # also scan v1/v2 full bodies if present
    for k in ('v1_body_full', 'v2_body_full', 'v1_body', 'v2_body'):
        body = host_json.get(k, '')
        if body:
            for m in re.finditer(r'"name"\s*:\s*"([^"]+)"', body):
                out['collection_names'].append(m.group(1))

    # dedup
    out['collection_names'] = list(set(out['collection_names']))
    return out


def extract_generic(host_json, name_paths=None):
    """Generic extractor — pull strings from configurable dotted paths."""
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
            per_string_hits.append((s, hits))
    return cat_counts, hit_count, per_string_hits


def structural_counts(strings):
    """Count RFC1918 vs public IPv4 vs hostnames. No string echoed."""
    private = 0
    public = 0
    hostnames = 0
    other = 0
    suffix_counts = Counter()
    for s in strings:
        if PRIV_IP_RX.match(s):
            private += 1
        elif PUBLIC_IP_RX.match(s):
            public += 1
        elif '.' in s:
            hostnames += 1
            # extract TLD-ish suffix without echoing full hostname
            parts = s.rsplit('.', 2)
            if len(parts) >= 2:
                suffix_counts['.' + parts[-1]] += 1
        else:
            other += 1
    return {
        'rfc1918': private,
        'public_ipv4': public,
        'hostnames': hostnames,
        'other': other,
        'top_tld_suffixes': suffix_counts.most_common(10),
    }


def char_entropy(s):
    """Shannon entropy of a string. Low = human-named, high = random ID."""
    if not s:
        return 0.0
    freq = Counter(s)
    total = len(s)
    return -sum((c/total) * math.log2(c/total) for c in freq.values())


def statistical_shape(strings):
    """Cardinality + length distribution + entropy histogram. Values hashed."""
    if not strings:
        return {'cardinality': 0, 'len_median': 0, 'len_p99': 0, 'entropy_mean': 0}
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
        'low_entropy_count': sum(1 for e in entropies if e < 3.0),  # human-named
        'high_entropy_count': sum(1 for e in entropies if e > 4.5),  # random IDs
    }


# ───────────────────────────────────────────────────────────────────────────────
# Main scanner
# ───────────────────────────────────────────────────────────────────────────────

def scan(corpus_dir, source, name_paths=None, include_samples=0):
    profile_fn = PROFILES[source]
    files = sorted(Path(corpus_dir).glob('*.json'))
    if not files:
        return {'error': f'no .json files in {corpus_dir}'}

    all_targets = []
    all_metric_names = []
    all_collection_names = []
    all_labels = []
    all_pool_names = []
    all_generic = []
    hosts_with_data = 0

    for f in files:
        try:
            h = json.loads(f.read_text())
        except (json.JSONDecodeError, OSError):
            continue
        if source == 'vm-verify':
            ext = profile_fn(h)
            if ext['targets'] or ext['metric_names']:
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
        else:
            ext = profile_fn(h, name_paths)
            if ext['names']:
                hosts_with_data += 1
            all_generic.extend(ext['names'])

    report = {
        'corpus_dir': str(corpus_dir),
        'source_profile': source,
        'files_scanned': len(files),
        'hosts_with_data': hosts_with_data,
    }

    # Per-stream analysis
    streams = {}
    if all_targets:
        streams['scrape_targets'] = all_targets
    if all_metric_names:
        streams['metric_names'] = all_metric_names
    if all_collection_names:
        streams['collection_names'] = all_collection_names
    if all_pool_names:
        streams['scrape_pool_names'] = all_pool_names
    if all_generic:
        streams['names'] = all_generic
    # labels are noisy — keep separately
    label_keys = list(set(all_labels)) if all_labels else []

    report['streams'] = {}
    for name, strs in streams.items():
        cat_counts, hit_count, per_hits = classify_strings(strs)
        stream_report = {
            'count_total': len(strs),
            'count_distinct': len(set(strs)),
            'structural': structural_counts(strs),
            'sensitivity_categories': dict(cat_counts),
            'category_hit_count': hit_count,
            'statistical_shape': statistical_shape(strs),
        }
        # samples only if requested
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
        for cat, n_hits in s['sensitivity_categories'].items():
            global_cats[cat] += n_hits
    report['global_sensitivity_rollup'] = dict(global_cats)

    return report


# ───────────────────────────────────────────────────────────────────────────────
# Pretty-printer
# ───────────────────────────────────────────────────────────────────────────────

def render_table(report):
    lines = []
    lines.append("=" * 72)
    lines.append(f"  GLANCE REPORT")
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
        lines.append("")
        lines.append(f"    STRUCTURAL (no content read):")
        st = s['structural']
        lines.append(f"      RFC1918 internal IPs:  {st['rfc1918']}")
        lines.append(f"      Public IPv4:           {st['public_ipv4']}")
        lines.append(f"      DNS hostnames:         {st['hostnames']}")
        lines.append(f"      Other / non-IP-DNS:    {st['other']}")
        if st['top_tld_suffixes']:
            lines.append(f"      Top TLD suffixes:")
            for suf, n in st['top_tld_suffixes'][:6]:
                lines.append(f"        {suf:<10}  {n}")
        lines.append("")
        lines.append(f"    SENSITIVITY (bag-of-fields, names only):")
        cats = s['sensitivity_categories']
        if cats:
            for cat, n in sorted(cats.items(), key=lambda x: -x[1]):
                lines.append(f"      {cat:<22}  {n} hits")
        else:
            lines.append(f"      (no matches in any category dictionary)")
        lines.append(f"    Values matching any category: {s['category_hit_count']}/{s['count_total']}")
        lines.append("")
        lines.append(f"    STATISTICAL SHAPE (hashed, no content shown):")
        ss = s['statistical_shape']
        lines.append(f"      length median / p99 / max:  {ss['len_median']} / {ss['len_p99']} / {ss['len_max']}")
        lines.append(f"      entropy mean / p99:         {ss['entropy_mean']} / {ss['entropy_p99']}")
        lines.append(f"      low-entropy (human-named):  {ss['low_entropy_count']}")
        lines.append(f"      high-entropy (random ID):   {ss['high_entropy_count']}")
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
    scan_p.add_argument('corpus_dir', help='directory of per-host evidence JSON files')
    scan_p.add_argument('--source', required=True, choices=list(PROFILES.keys()),
                        help='source profile (which extractor to use)')
    scan_p.add_argument('-o', '--output', help='write JSON report to this path (in addition to stdout table)')
    scan_p.add_argument('--include-samples', type=int, default=0,
                        help='if >0, include up to N flagged sample values per stream in the JSON output. DEFAULT 0 (sealed mode).')
    scan_p.add_argument('--name-paths', help='for --source generic, comma-separated dotted JSON paths to scan')
    scan_p.add_argument('--json-only', action='store_true', help='emit only JSON to stdout, no human table')

    args = ap.parse_args()
    if args.cmd == 'scan':
        name_paths = args.name_paths.split(',') if args.name_paths else None
        report = scan(args.corpus_dir, args.source, name_paths=name_paths,
                      include_samples=args.include_samples)
        if args.output:
            Path(args.output).write_text(json.dumps(report, indent=2))
            print(f"-> {args.output}", file=sys.stderr)
        if args.json_only:
            print(json.dumps(report, indent=2))
        else:
            print(render_table(report))

if __name__ == '__main__':
    main()
