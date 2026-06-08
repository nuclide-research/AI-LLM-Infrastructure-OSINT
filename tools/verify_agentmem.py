#!/usr/bin/env python3
"""
verify_agentmem — verifier for agent-memory layer platforms.

Tests the MemMorph paper's attack surface at population scale:
  - Mem0:    /v1/memories/, /v1/users
  - Letta:   /v1/agents, /v1/agents/{id}/messages, /v1/tools
  - Zep:     /api/v1/sessions, /api/v1/memory/{session}/messages
  - Cognee:  /docs (FastAPI), /pipelines

Restraint discipline: READ-ONLY probes. No POSTs even on the documented
write endpoints (the MemMorph attack vector is exactly POST /v1/memories;
we measure the OPEN-OF-WRITE-SURFACE by observing whether GET on the
related endpoints returns 200 unauth, never by attempting a write).
"""
import asyncio, aiohttp, json, sys, re, time
from pathlib import Path
from collections import Counter

OUT = Path.home()/"syllabus"/"shodan"/"agentmem-verify"
OUT.mkdir(parents=True, exist_ok=True)
(OUT/"hosts").mkdir(exist_ok=True)

TIMEOUT = aiohttp.ClientTimeout(total=8, connect=4)
CONC = 30

# Per-platform read-only probe set
PROBE_SET = {
    'mem0': [
        '/openapi.json',
        '/docs',
        '/v1/memories/',
        '/v1/users',
        '/v1/configs/reset',
        '/health',
    ],
    'letta': [
        '/openapi.json',
        '/docs',
        '/v1/agents',
        '/v1/tools',
        '/v1/blocks',
        '/v1/health',
        '/health',
    ],
    'zep': [
        '/openapi.json',
        '/api/v1/sessions',
        '/api/v1/memory',
        '/healthz',
    ],
    'cognee': [
        '/openapi.json',
        '/docs',
        '/health',
        '/api/v1/datasets',
        '/api/v1/pipelines',
    ],
}


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


async def probe(s, target, platform):
    paths = PROBE_SET.get(platform, [])
    out = {'target': target, 'platform_guess': platform, 'evidence': {}, 'classified_at': int(time.time())}
    for p in paths:
        key = p.lstrip('/').replace('/', '_') or 'root'
        out['evidence'][key] = await aget(s, target, p)
    out['decision'] = classify(out, platform)
    return out


def classify(h, platform):
    ev = h['evidence']
    d = {'state': 'UNCLASSIFIED', 'platform_confirmed': False,
         'write_surface_open': False, 'memories_visible_count': 0,
         'agents_visible_count': 0, 'sessions_visible_count': 0,
         'openapi_visible': False, 'docs_visible': False,
         'is_fastapi': False, 'reasons': []}

    # Universal: openapi exposed?
    openapi = ev.get('openapi.json'.replace('.', '_').replace('/', '_'), {}) or ev.get('openapi_json',{})
    if openapi.get('status') == 200:
        body = openapi.get('body','')
        if '"openapi"' in body or 'swagger' in body.lower():
            d['openapi_visible'] = True
            d['is_fastapi'] = 'fastapi' in body.lower() or 'pydantic' in body.lower()

    docs = ev.get('docs', {})
    if docs.get('status') == 200 and ('swagger' in docs.get('body','').lower() or 'redoc' in docs.get('body','').lower()):
        d['docs_visible'] = True

    if platform == 'mem0':
        mems = ev.get('v1_memories_', {}) or ev.get('v1_memories', {})
        users = ev.get('v1_users', {})
        if mems.get('status') == 200:
            d['platform_confirmed'] = True
            d['state'] = 'UNAUTH-READ'
            try:
                j = json.loads(mems['body'])
                if isinstance(j, dict) and 'memories' in j:
                    d['memories_visible_count'] = len(j['memories'])
                elif isinstance(j, list):
                    d['memories_visible_count'] = len(j)
            except: pass
            d['reasons'].append('mem0 /v1/memories returns 200 unauth')
        elif mems.get('status') in (401, 403, 422):
            d['state'] = 'AUTH-ON'
            d['platform_confirmed'] = True
        if users.get('status') == 200:
            d['write_surface_open'] = True
            d['reasons'].append('mem0 users endpoint exposes user list — write surface for poisoning attack reachable')

    elif platform == 'letta':
        agents = ev.get('v1_agents', {})
        if agents.get('status') == 200:
            d['platform_confirmed'] = True
            d['state'] = 'UNAUTH-READ'
            try:
                j = json.loads(agents['body'])
                if isinstance(j, list):
                    d['agents_visible_count'] = len(j)
                elif isinstance(j, dict) and 'agents' in j:
                    d['agents_visible_count'] = len(j['agents'])
            except: pass
            d['reasons'].append('letta /v1/agents returns 200 unauth')
        elif agents.get('status') in (401, 403):
            d['state'] = 'AUTH-ON'
            d['platform_confirmed'] = True

    elif platform == 'zep':
        sessions = ev.get('api_v1_sessions', {})
        if sessions.get('status') == 200:
            d['platform_confirmed'] = True
            d['state'] = 'UNAUTH-READ'
            try:
                j = json.loads(sessions['body'])
                if isinstance(j, list): d['sessions_visible_count'] = len(j)
                elif isinstance(j, dict) and 'sessions' in j: d['sessions_visible_count'] = len(j['sessions'])
            except: pass
            d['reasons'].append('zep /api/v1/sessions returns 200 unauth')
        elif sessions.get('status') in (401, 403):
            d['state'] = 'AUTH-ON'
            d['platform_confirmed'] = True

    elif platform == 'cognee':
        datasets = ev.get('api_v1_datasets', {})
        pipelines = ev.get('api_v1_pipelines', {})
        if datasets.get('status') == 200 or pipelines.get('status') == 200:
            d['platform_confirmed'] = True
            d['state'] = 'UNAUTH-READ'
            d['reasons'].append('cognee API returns 200 unauth')
        elif (datasets.get('status') in (401,403) or pipelines.get('status') in (401,403)):
            d['state'] = 'AUTH-ON'
            d['platform_confirmed'] = True

    if d['state'] == 'UNCLASSIFIED' and all(ev[k]['status'] == 0 for k in ev):
        d['state'] = 'OFFLINE'

    return d


async def main():
    hosts = json.load(open('/home/cowboy/syllabus/shodan/agentmem-harvest/hosts.json'))
    print(f"[verify_agentmem] hosts={len(hosts)} conc={CONC}", file=sys.stderr)
    sem = asyncio.Semaphore(CONC)
    conn = aiohttp.TCPConnector(ssl=False, limit=CONC+10)

    async with aiohttp.ClientSession(connector=conn, timeout=TIMEOUT) as s:
        async def b(h):
            async with sem:
                target = f"{h['ip']}:{h['port']}"
                plat = h.get('platform_guess','mem0')
                try:
                    return await probe(s, target, plat)
                except Exception as e:
                    return {'target': target, 'platform_guess': plat, 'decision': {'state':'PROBE-ERR','reasons':[repr(e)]}}

        t0 = time.time()
        rows = []
        tasks = [asyncio.create_task(b(h)) for h in hosts]
        done = 0
        for c in asyncio.as_completed(tasks):
            r = await c
            rows.append(r)
            done += 1
            if done % 50 == 0 or done == len(tasks):
                print(f"  [{done}/{len(tasks)}] {time.time()-t0:.1f}s", file=sys.stderr)
            safe = r['target'].replace(':','_').replace('/','_')
            (OUT/'hosts'/f"{safe}.json").write_text(json.dumps(r, indent=2))

    # Rollup per-platform
    by_plat = {}
    for r in rows:
        p = r.get('platform_guess','unknown')
        by_plat.setdefault(p, []).append(r)

    print(f"\nPER-PLATFORM ROLLUP:", file=sys.stderr)
    rollup = {'sweep_t': int(time.time()), 'total': len(rows), 'platforms': {}}
    for plat, rs in by_plat.items():
        states = Counter(r['decision']['state'] for r in rs)
        unauth = sum(1 for r in rs if r['decision']['state'] == 'UNAUTH-READ')
        confirmed = sum(1 for r in rs if r['decision'].get('platform_confirmed'))
        write_open = sum(1 for r in rs if r['decision'].get('write_surface_open'))
        total_memories = sum(r['decision'].get('memories_visible_count',0) for r in rs)
        total_agents = sum(r['decision'].get('agents_visible_count',0) for r in rs)
        total_sessions = sum(r['decision'].get('sessions_visible_count',0) for r in rs)
        openapi_open = sum(1 for r in rs if r['decision'].get('openapi_visible'))

        print(f"\n  {plat}  (n={len(rs)})", file=sys.stderr)
        print(f"    states: {dict(states)}", file=sys.stderr)
        print(f"    platform-confirmed: {confirmed}/{len(rs)}", file=sys.stderr)
        print(f"    UNAUTH-READ: {unauth}/{len(rs)} ({unauth*100//len(rs)}%)", file=sys.stderr)
        print(f"    openapi.json visible: {openapi_open}", file=sys.stderr)
        print(f"    write surface reachable: {write_open}", file=sys.stderr)
        if total_memories: print(f"    Total memories visible: {total_memories}", file=sys.stderr)
        if total_agents:   print(f"    Total agents visible:   {total_agents}", file=sys.stderr)
        if total_sessions: print(f"    Total sessions visible: {total_sessions}", file=sys.stderr)
        rollup['platforms'][plat] = {
            'total': len(rs),
            'states': dict(states),
            'platform_confirmed': confirmed,
            'unauth_read': unauth,
            'openapi_visible': openapi_open,
            'write_surface_open': write_open,
            'total_memories_visible': total_memories,
            'total_agents_visible': total_agents,
            'total_sessions_visible': total_sessions,
        }
    rollup['rows'] = rows
    (OUT/'rollup.json').write_text(json.dumps(rollup, indent=2))
    print(f"\n-> {OUT}/rollup.json", file=sys.stderr)


if __name__ == '__main__':
    asyncio.run(main())
