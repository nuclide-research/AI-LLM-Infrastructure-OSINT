#!/usr/bin/env python3
"""
verify_vm_unauth — verifier for VictoriaMetrics auth posture + data-exposure
class across vmsingle / vmagent / vmcluster / vmalert.

Restraint ethic (per NuClide doctrine):
  - Read-only probes ONLY. No POSTs.
  - No /api/v1/import (that's a write surface).
  - No /api/v1/admin/tsdb/delete_series.
  - We test what they LEAK, not what we can break.

Signals per host:
  /api/v1/status/buildinfo     — version + branch + revision (VM-specific)
  /api/v1/status/tsdb          — series count, label cardinality, churn rate
  /api/v1/labels               — full metric-label catalog
  /api/v1/label/__name__/values — full metric-NAME catalog (operator stack inference)
  /api/v1/targets              — vmagent scrape targets (only on vmagent)
  /metrics                     — self-monitoring (port-internal stats)
  /debug/pprof/                — upstream issue #3060 (profiling auth bypass)
  /api/v1/rules                — vmalert rule definitions (only on vmalert)
  /api/v1/alerts               — vmalert firing alerts (only on vmalert)

Classification:
  STATE = UNAUTH-READ        — list endpoints return 200 with data
        | AUTH-ON            — 401/403 on the gated endpoint
        | PARTIAL-AUTH       — some endpoints 200, others 401 (rare)
        | OFFLINE
        | UNCLASSIFIED

Sensitivity tags (when UNAUTH-READ):
  - vmsingle/vmcluster: series_count, label_cardinality, churn_rate, metric_name_catalog
  - vmagent: target_count, scrape_config_leak (target URLs reveal internal infra)
  - vmalert: rule_count, alert_severity_distribution
  - pprof_open: True/False (independent indicator regardless of -httpAuth)
"""
import asyncio, aiohttp, json, sys, re, time
from pathlib import Path
from collections import Counter, defaultdict

OUT = Path.home()/"syllabus"/"shodan"/"vm-verify"
OUT.mkdir(parents=True, exist_ok=True)
(OUT/"hosts").mkdir(exist_ok=True)

TIMEOUT = aiohttp.ClientTimeout(total=8, connect=4)
CONC = 50

PATHS = [
    ('/api/v1/status/buildinfo',      'buildinfo'),
    ('/api/v1/status/tsdb',           'tsdb_status'),
    ('/api/v1/labels',                'labels'),
    ('/api/v1/label/__name__/values', 'metric_names'),
    ('/api/v1/targets',               'targets'),
    ('/api/v1/rules',                 'rules'),
    ('/api/v1/alerts',                'alerts'),
    ('/metrics',                      'self_metrics'),
    ('/debug/pprof/',                 'pprof'),
]

VERSION_RX = re.compile(r'"version"\s*:\s*"([^"]+)"')
BRANCH_RX  = re.compile(r'"branch"\s*:\s*"([^"]+)"')


async def aget(s, target, path):
    scheme = 'https' if ':443' in target or ':8443' in target else 'http'
    url = f"{scheme}://{target}{path}"
    try:
        async with s.get(url, ssl=False, allow_redirects=False) as r:
            body = await r.text(errors='ignore')
            return {'status': r.status, 'body': body[:5000], 'len': len(body)}
    except asyncio.TimeoutError:
        return {'status': 0, 'body': '', 'err': 'timeout'}
    except Exception as e:
        return {'status': 0, 'body': '', 'err': type(e).__name__}


async def probe(s, target):
    out = {'target': target, 'evidence': {}, 'classified_at': int(time.time())}
    for path, key in PATHS:
        out['evidence'][key] = await aget(s, target, path)

    decision = classify(out)
    out['decision'] = decision
    return out


def classify(h):
    ev = h['evidence']
    d = {'state': 'UNCLASSIFIED', 'component_guess': None, 'sensitivity': [],
         'version': None, 'pprof_open': False, 'series_count': None,
         'label_count': None, 'metric_name_count': None, 'target_count': None,
         'rule_count': None, 'reasons': []}

    # offline check (everything 0)
    statuses = [ev[k]['status'] for k in ev]
    if statuses.count(0) >= len(statuses) - 1:
        d['state'] = 'OFFLINE'
        return d

    # auth check on gated endpoints
    gated = ['labels', 'metric_names', 'tsdb_status']
    gated_statuses = [ev[k]['status'] for k in gated]
    n_unauth = sum(1 for s in gated_statuses if s == 200)
    n_authon = sum(1 for s in gated_statuses if s in (401, 403))
    if n_authon == len(gated):
        d['state'] = 'AUTH-ON'
        d['reasons'].append(f'all gated endpoints return {gated_statuses}')
    elif n_unauth >= 1:
        d['state'] = 'UNAUTH-READ'
        d['reasons'].append(f'gated endpoints UNAUTH: labels={ev["labels"]["status"]}, metric_names={ev["metric_names"]["status"]}, tsdb={ev["tsdb_status"]["status"]}')

    # version
    bi = ev.get('buildinfo', {})
    if bi.get('status') == 200:
        m = VERSION_RX.search(bi.get('body',''))
        if m:
            d['version'] = m.group(1)
            d['reasons'].append(f'version={d["version"]}')

    # component guess (which VM family?)
    if ev.get('targets', {}).get('status') == 200:
        d['component_guess'] = 'vmagent'
        body = ev['targets'].get('body','')
        # rough count of target entries
        target_count = body.count('"scrapeUrl"') or body.count('"endpoint"')
        d['target_count'] = target_count
        if target_count > 0:
            d['sensitivity'].append(f'scrape_target_count:{target_count}')
    elif ev.get('rules', {}).get('status') == 200 or ev.get('alerts', {}).get('status') == 200:
        d['component_guess'] = 'vmalert'
        body = ev.get('rules',{}).get('body','') + ev.get('alerts',{}).get('body','')
        d['rule_count'] = body.count('"name"')
        if d['rule_count'] > 0:
            d['sensitivity'].append(f'rule_count:{d["rule_count"]}')
    elif ev.get('tsdb_status', {}).get('status') == 200:
        d['component_guess'] = 'vmsingle_or_vmselect'
        try:
            j = json.loads(ev['tsdb_status']['body'])
            stat = j.get('data', {}).get('headStats') or j.get('data',{})
            sc = stat.get('seriesCount') or stat.get('seriesCountByMetricName')
            if isinstance(sc, int):
                d['series_count'] = sc
            elif isinstance(sc, list):
                d['series_count'] = len(sc)
            lcp = stat.get('labelValueCountByLabelName') or []
            if isinstance(lcp, list) and lcp:
                d['label_count'] = len(lcp)
        except (json.JSONDecodeError, KeyError, TypeError):
            pass

    # metric_name catalog size
    mn = ev.get('metric_names', {})
    if mn.get('status') == 200:
        try:
            j = json.loads(mn['body'])
            if isinstance(j.get('data'), list):
                d['metric_name_count'] = len(j['data'])
                if d['metric_name_count'] > 0:
                    d['sensitivity'].append(f'metric_name_catalog:{d["metric_name_count"]}_names')
        except json.JSONDecodeError:
            pass

    # label catalog
    lab = ev.get('labels', {})
    if lab.get('status') == 200:
        try:
            j = json.loads(lab['body'])
            if isinstance(j.get('data'), list):
                d['label_count'] = len(j['data'])
        except json.JSONDecodeError:
            pass

    # pprof
    p = ev.get('pprof', {})
    if p.get('status') == 200 and ('goroutine' in p.get('body','').lower() or 'pprof' in p.get('body','').lower()):
        d['pprof_open'] = True
        d['sensitivity'].append('pprof_open')
        d['reasons'].append('upstream-issue-3060: /debug/pprof/ returns 200 regardless of -httpAuth')

    return d


async def main():
    targets = [l.strip() for l in open('/home/cowboy/syllabus/shodan/vm-harvest/classified-hosts.txt') if l.strip()]
    print(f"[verify_vm_unauth] targets={len(targets)} conc={CONC}", file=sys.stderr)

    sem = asyncio.Semaphore(CONC)
    conn = aiohttp.TCPConnector(ssl=False, limit=CONC+10)
    async with aiohttp.ClientSession(connector=conn, timeout=TIMEOUT) as s:
        async def b(t):
            async with sem:
                try:
                    out = await probe(s, t)
                except Exception as e:
                    out = {'target': t, 'decision': {'state':'PROBE-ERR','reasons':[repr(e)]}}
                safe = t.replace(':','_').replace('/','_')
                (OUT/'hosts'/f"{safe}.json").write_text(json.dumps(out, indent=2))
                return out

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

    # rollup
    state_count = Counter(r['decision']['state'] for r in rows)
    comp_count = Counter(r['decision'].get('component_guess') or 'unclassified' for r in rows)
    ver_count = Counter(r['decision'].get('version') or 'unknown' for r in rows)
    pprof_open = sum(1 for r in rows if r['decision'].get('pprof_open'))

    print("\nSTATE distribution:", file=sys.stderr)
    for s,n in state_count.most_common(): print(f"  {n:>4}  {s}", file=sys.stderr)
    print("\nCOMPONENT distribution:", file=sys.stderr)
    for c,n in comp_count.most_common(): print(f"  {n:>4}  {c}", file=sys.stderr)
    print(f"\nVersion distribution (top 10):", file=sys.stderr)
    for v,n in ver_count.most_common(10): print(f"  {n:>4}  {v}", file=sys.stderr)
    print(f"\npprof_open hosts: {pprof_open}/{len(rows)}", file=sys.stderr)

    # high-value finds: large metric_name_count, large target_count, large series_count
    unauth_read = [r for r in rows if r['decision']['state'] == 'UNAUTH-READ']
    unauth_read.sort(key=lambda r: -(r['decision'].get('metric_name_count') or r['decision'].get('target_count') or r['decision'].get('series_count') or 0))
    print(f"\nTop UNAUTH-READ by data-volume signal (first 10):", file=sys.stderr)
    for r in unauth_read[:10]:
        d = r['decision']
        m = d.get('metric_name_count')
        t = d.get('target_count')
        s = d.get('series_count')
        print(f"  {r['target']:30}  comp={d.get('component_guess','?'):>20}  metrics={m}  targets={t}  series={s}", file=sys.stderr)

    rollup = {
        'sweep_t': int(time.time()),
        'targets': len(targets),
        'state_count': dict(state_count),
        'component_count': dict(comp_count),
        'version_count': dict(ver_count.most_common(20)),
        'pprof_open_count': pprof_open,
        'rows': rows,
    }
    (OUT/'rollup.json').write_text(json.dumps(rollup, indent=2))
    print(f"\n-> {OUT}/rollup.json", file=sys.stderr)

if __name__ == '__main__':
    asyncio.run(main())
