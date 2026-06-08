#!/usr/bin/env python3
"""
verify_prom_unauth — Prometheus auth-posture + scrape-topology verifier.

Tests two falsifiable claims from the VM survey:
  Insight #88 (scrape topology = org chart): /api/v1/targets exposes
    internal infrastructure naming on unauth Prometheus at population scale.
  Insight #89 (framework-level pprof bypass): /debug/pprof/ is open
    regardless of --web.config.file basic_auth configuration.

Probes (all read-only, no POST):
  /api/v1/status/buildinfo     — version + branch + revision
  /api/v1/status/config        — full prometheus.yml (HIGHEST risk endpoint)
  /api/v1/status/runtimeinfo   — server runtime state
  /api/v1/status/flags         — command-line flags
  /api/v1/status/tsdb          — series/label cardinality
  /api/v1/labels               — label catalog
  /api/v1/label/__name__/values — full metric-name catalog
  /api/v1/targets              — scrape configuration (Insight #88 endpoint)
  /api/v1/rules                — alerting/recording rule definitions
  /api/v1/alerts               — currently firing alerts
  /metrics                     — self-monitoring
  /debug/pprof/                — Insight #89 endpoint
  /graph                       — web UI (auth posture indicator)
"""
import asyncio, aiohttp, json, sys, re, time
from pathlib import Path
from collections import Counter, defaultdict

OUT = Path.home()/"syllabus"/"shodan"/"prom-verify"
OUT.mkdir(parents=True, exist_ok=True)
(OUT/"hosts").mkdir(exist_ok=True)

TIMEOUT = aiohttp.ClientTimeout(total=8, connect=4)
CONC = 60

PATHS = [
    ('/api/v1/status/buildinfo',      'buildinfo'),
    ('/api/v1/status/config',         'config'),
    ('/api/v1/status/runtimeinfo',    'runtimeinfo'),
    ('/api/v1/status/flags',          'flags'),
    ('/api/v1/status/tsdb',           'tsdb_status'),
    ('/api/v1/labels',                'labels'),
    ('/api/v1/label/__name__/values', 'metric_names'),
    ('/api/v1/targets',               'targets'),
    ('/api/v1/rules',                 'rules'),
    ('/api/v1/alerts',                'alerts'),
    ('/metrics',                      'self_metrics'),
    ('/debug/pprof/',                 'pprof'),
    ('/graph',                        'graph_ui'),
]

VERSION_RX = re.compile(r'"version"\s*:\s*"([^"]+)"')
GOVERSION_RX = re.compile(r'"goVersion"\s*:\s*"([^"]+)"')


async def aget(s, target, path):
    scheme = 'https' if ':443' in target or ':8443' in target else 'http'
    url = f"{scheme}://{target}{path}"
    try:
        async with s.get(url, ssl=False, allow_redirects=False) as r:
            body = await r.text(errors='ignore')
            return {'status': r.status, 'body': body[:8000], 'len': len(body)}
    except asyncio.TimeoutError:
        return {'status': 0, 'body': '', 'err': 'timeout'}
    except Exception as e:
        return {'status': 0, 'body': '', 'err': type(e).__name__}


async def probe(s, target):
    out = {'target': target, 'evidence': {}, 'classified_at': int(time.time())}
    for path, key in PATHS:
        out['evidence'][key] = await aget(s, target, path)
    out['decision'] = classify(out)
    return out


def classify(h):
    ev = h['evidence']
    d = {'state': 'UNCLASSIFIED', 'is_prometheus': False, 'is_vm_compat': False,
         'version': None, 'go_version': None, 'pprof_open': False,
         'config_leaked': False, 'rule_count': 0, 'target_count': 0,
         'metric_name_count': None, 'alerts_count': 0,
         'embedded_creds_in_config': False, 'remote_write_urls': 0,
         'sensitivity': [], 'reasons': []}

    # Prometheus fingerprint check (vs VM Prometheus-compat)
    bi = ev.get('buildinfo', {})
    if bi.get('status') == 200:
        body = bi.get('body', '')
        v = VERSION_RX.search(body)
        gv = GOVERSION_RX.search(body)
        if v:
            d['version'] = v.group(1)
        if gv:
            # goVersion is Prometheus-specific; VM doesn't return it
            d['go_version'] = gv.group(1)
            d['is_prometheus'] = True
            d['reasons'].append(f'prometheus confirmed (version={d["version"]}, go={d["go_version"]})')
        elif v and not gv:
            # VM compat or other Prometheus-API-compatible server
            d['is_vm_compat'] = True
            d['reasons'].append(f'VM/Prometheus-compat (version={d["version"]}, no goVersion field)')

    # Auth state check
    gated = ['targets', 'config', 'tsdb_status', 'metric_names']
    statuses = [ev[k].get('status') for k in gated]
    if statuses.count(0) >= len(statuses) - 1:
        d['state'] = 'OFFLINE'
        return d

    unauth_count = sum(1 for s in statuses if s == 200)
    authon_count = sum(1 for s in statuses if s in (401, 403))

    if authon_count == len(gated):
        d['state'] = 'AUTH-ON'
        d['reasons'].append(f'all gated endpoints return {statuses}')
    elif unauth_count >= 2:
        d['state'] = 'UNAUTH-READ'
        d['reasons'].append(f'gated endpoints UNAUTH (statuses: {statuses})')
    else:
        d['state'] = 'PARTIAL'

    # /api/v1/status/config is the HIGHEST-value endpoint — full prometheus.yml
    cfg = ev.get('config', {})
    if cfg.get('status') == 200 and cfg.get('len', 0) > 100:
        d['config_leaked'] = True
        body = cfg.get('body', '')
        # check for embedded credentials patterns
        if re.search(r'basic_auth.*password', body, re.I | re.S) or \
           re.search(r'bearer_token.*:', body, re.I) or \
           re.search(r'authorization.*credentials', body, re.I):
            d['embedded_creds_in_config'] = True
            d['sensitivity'].append('config_embedded_creds')
        # remote_write URLs
        rw_count = len(re.findall(r'remote_write|remoteWrite', body))
        d['remote_write_urls'] = rw_count
        if rw_count > 0:
            d['sensitivity'].append(f'remote_write_urls:{rw_count}')

    # Targets count
    tg = ev.get('targets', {})
    if tg.get('status') == 200:
        body = tg.get('body', '')
        d['target_count'] = body.count('"scrapeUrl"')
        if d['target_count'] > 0:
            d['sensitivity'].append(f'scrape_target_count:{d["target_count"]}')

    # Rules + alerts
    if ev.get('rules', {}).get('status') == 200:
        d['rule_count'] = ev['rules']['body'].count('"name"')
    if ev.get('alerts', {}).get('status') == 200:
        d['alerts_count'] = ev['alerts']['body'].count('"labels"')

    # Metric-name catalog
    mn = ev.get('metric_names', {})
    if mn.get('status') == 200:
        try:
            j = json.loads(mn['body'])
            if isinstance(j.get('data'), list):
                d['metric_name_count'] = len(j['data'])
                if d['metric_name_count'] > 0:
                    d['sensitivity'].append(f'metric_name_catalog:{d["metric_name_count"]}')
        except json.JSONDecodeError:
            pass

    # Pprof check (Insight #89)
    p = ev.get('pprof', {})
    if p.get('status') == 200 and ('pprof' in p.get('body','').lower() or 'goroutine' in p.get('body','').lower()):
        d['pprof_open'] = True
        d['sensitivity'].append('pprof_open')
        d['reasons'].append('pprof-open: /debug/pprof/ returns 200')

    return d


async def main():
    targets_file = Path('/home/cowboy/syllabus/shodan/prom-harvest/hosts.txt')
    if not targets_file.exists():
        print(f"missing {targets_file}", file=sys.stderr)
        return
    targets = [l.strip() for l in targets_file.open() if l.strip()]
    print(f"[verify_prom_unauth] targets={len(targets)} conc={CONC}", file=sys.stderr)

    sem = asyncio.Semaphore(CONC)
    conn = aiohttp.TCPConnector(ssl=False, limit=CONC+20)
    async with aiohttp.ClientSession(connector=conn, timeout=TIMEOUT) as s:
        async def b(t):
            async with sem:
                try:
                    return await probe(s, t)
                except Exception as e:
                    return {'target': t, 'decision': {'state':'PROBE-ERR','reasons':[repr(e)]}}

        t0 = time.time()
        rows = []
        tasks = [asyncio.create_task(b(t)) for t in targets]
        done = 0
        for c in asyncio.as_completed(tasks):
            r = await c
            rows.append(r)
            done += 1
            if done % 100 == 0 or done == len(tasks):
                print(f"  [{done}/{len(tasks)}] {time.time()-t0:.1f}s", file=sys.stderr)
            safe = r['target'].replace(':','_').replace('/','_')
            (OUT/'hosts'/f"{safe}.json").write_text(json.dumps(r, indent=2))

    # rollup
    states = Counter(r['decision']['state'] for r in rows)
    is_prom = sum(1 for r in rows if r['decision'].get('is_prometheus'))
    is_vmcompat = sum(1 for r in rows if r['decision'].get('is_vm_compat'))
    pprof_open = sum(1 for r in rows if r['decision'].get('pprof_open'))
    config_leaked = sum(1 for r in rows if r['decision'].get('config_leaked'))
    creds_in_config = sum(1 for r in rows if r['decision'].get('embedded_creds_in_config'))
    total_targets = sum(r['decision'].get('target_count', 0) for r in rows)
    total_rules = sum(r['decision'].get('rule_count', 0) for r in rows)
    total_metrics = sum(r['decision'].get('metric_name_count') or 0 for r in rows)

    print("\nSTATE DISTRIBUTION:", file=sys.stderr)
    for s, n in states.most_common(): print(f"  {n:>4}  {s}", file=sys.stderr)
    print(f"\nFingerprint:", file=sys.stderr)
    print(f"  Prometheus (has goVersion):  {is_prom}/{len(rows)}", file=sys.stderr)
    print(f"  VM-compat (no goVersion):    {is_vmcompat}/{len(rows)}", file=sys.stderr)
    print(f"\nKey indicators:", file=sys.stderr)
    print(f"  /debug/pprof/ open:                  {pprof_open}/{len(rows)} ({pprof_open*100//len(rows)}%)", file=sys.stderr)
    print(f"  /api/v1/status/config leaked:        {config_leaked}/{len(rows)} ({config_leaked*100//len(rows)}%)", file=sys.stderr)
    print(f"  Embedded creds in config:            {creds_in_config}/{len(rows)}", file=sys.stderr)
    print(f"\nLeakage volume:", file=sys.stderr)
    print(f"  Total scrape targets exposed:        {total_targets}", file=sys.stderr)
    print(f"  Total alerting/recording rules:      {total_rules}", file=sys.stderr)
    print(f"  Total metric names disclosed:        {total_metrics}", file=sys.stderr)

    rollup = {
        'sweep_t': int(time.time()),
        'targets': len(targets),
        'state_distribution': dict(states),
        'is_prometheus_count': is_prom,
        'is_vm_compat_count': is_vmcompat,
        'pprof_open_count': pprof_open,
        'pprof_open_share': pprof_open / max(len(rows), 1),
        'config_leaked_count': config_leaked,
        'embedded_creds_in_config_count': creds_in_config,
        'total_scrape_targets': total_targets,
        'total_rules': total_rules,
        'total_metric_names': total_metrics,
        'rows': rows,
    }
    (OUT/'rollup.json').write_text(json.dumps(rollup, indent=2))
    print(f"\n-> {OUT}/rollup.json", file=sys.stderr)

if __name__ == '__main__':
    asyncio.run(main())
