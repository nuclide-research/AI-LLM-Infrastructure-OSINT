#!/usr/bin/env python3
"""ClickHouse auth + version probe.
Probes: GET /?query=SELECT+version() -- returns version if unauth, 401/403 if auth.
Also checks /play, system.environment, system.tables count.
"""
import asyncio, csv, json, re, sys
import aiohttp

TIMEOUT = aiohttp.ClientTimeout(total=8, connect=4)
CONCURRENCY = 80
VER_RE = re.compile(r'^(\d+\.\d+[\.\d]*)$', re.M)

async def probe(session, target):
    base = target.rstrip('/')
    result = {
        'target': target, 'version': '', 'auth_state': '',
        'play_open': '', 'env_accessible': '', 'table_count': '',
        'display_name': '', 'notes': ''
    }
    ver_url = base + '/?query=SELECT+version()'
    try:
        async with session.get(ver_url, ssl=False, allow_redirects=True) as r:
            # Grab display-name header
            dn = r.headers.get('X-ClickHouse-Server-Display-Name', '')
            if dn:
                result['display_name'] = dn
            if r.status == 200:
                body = (await r.text(errors='ignore')).strip()
                m = VER_RE.search(body)
                if m:
                    result['version'] = m.group(1)
                    result['auth_state'] = 'unauth'
                    # Confirmed unauth — check /play
                    try:
                        async with session.get(base + '/play', ssl=False) as pr:
                            result['play_open'] = 'yes' if pr.status == 200 else 'no'
                    except:
                        result['play_open'] = 'err'
                    # system.environment for secrets
                    env_url = base + '/?query=SELECT+name,value+FROM+system.environment+FORMAT+JSONEachRow+LIMIT+50'
                    try:
                        async with session.get(env_url, ssl=False) as er:
                            if er.status == 200:
                                env_body = await er.text(errors='ignore')
                                sensitive = any(k in env_body.upper() for k in
                                    ['API_KEY','SECRET','TOKEN','PASSWORD','CREDENTIAL','ACCESS_KEY'])
                                result['env_accessible'] = 'yes_sensitive' if sensitive else 'yes'
                            else:
                                result['env_accessible'] = 'no'
                    except:
                        result['env_accessible'] = 'err'
                    # Table count
                    tc_url = base + '/?query=SELECT+count()+FROM+system.tables'
                    try:
                        async with session.get(tc_url, ssl=False) as tr:
                            if tr.status == 200:
                                result['table_count'] = (await tr.text(errors='ignore')).strip()
                    except:
                        pass
                else:
                    result['auth_state'] = 'unauth'
                    result['notes'] = 'open but no version in response'
            elif r.status in (401, 403):
                result['auth_state'] = 'auth'
            elif r.status == 400:
                # Bad request can mean unauth but query rejected
                body = await r.text(errors='ignore')
                if 'Authentication' in body or 'password' in body.lower():
                    result['auth_state'] = 'auth'
                else:
                    result['auth_state'] = 'unauth'
                    result['notes'] = f'400: {body[:80]}'
    except Exception as e:
        result['notes'] = str(e)[:60]
    return result

async def run(targets, out_path):
    sem = asyncio.Semaphore(CONCURRENCY)
    connector = aiohttp.TCPConnector(ssl=False, limit=CONCURRENCY + 20)
    rows = []
    async with aiohttp.ClientSession(connector=connector, timeout=TIMEOUT) as session:
        async def bounded(t):
            async with sem:
                return await probe(session, t)
        tasks = [bounded(t) for t in targets]
        done = 0
        for coro in asyncio.as_completed(tasks):
            r = await coro
            rows.append(r)
            done += 1
            if done % 50 == 0 or done == len(tasks):
                unauth = sum(1 for x in rows if x['auth_state'] == 'unauth' and x['version'])
                env_hit = sum(1 for x in rows if x['env_accessible'] in ('yes', 'yes_sensitive'))
                print(f'  [{done}/{len(tasks)}] unauth+versioned: {unauth} | env accessible: {env_hit}', file=sys.stderr)

    # Sort: unauth+versioned first, then unauth, then auth
    def sort_key(r):
        if r['auth_state'] == 'unauth' and r['version']:
            return (0, r['target'])
        elif r['auth_state'] == 'unauth':
            return (1, r['target'])
        elif r['auth_state'] == 'auth':
            return (2, r['target'])
        return (3, r['target'])

    rows.sort(key=sort_key)
    fields = ['target', 'version', 'auth_state', 'play_open', 'env_accessible', 'table_count', 'display_name', 'notes']
    with open(out_path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    unauth_ver = [r for r in rows if r['auth_state'] == 'unauth' and r['version']]
    unauth_any = [r for r in rows if r['auth_state'] == 'unauth']
    env_sensitive = [r for r in rows if r['env_accessible'] == 'yes_sensitive']
    print(f"\nTotal: {len(rows)}")
    print(f"Unauth + versioned: {len(unauth_ver)}")
    print(f"Unauth (any): {len(unauth_any)}")
    print(f"Auth: {sum(1 for r in rows if r['auth_state'] == 'auth')}")
    print(f"Env accessible: {sum(1 for r in rows if r['env_accessible'] in ('yes','yes_sensitive'))}")
    print(f"Env with sensitive values: {len(env_sensitive)}")
    if env_sensitive:
        print("  SENSITIVE ENV HOSTS:")
        for r in env_sensitive:
            print(f"  {r['target']}  v{r['version']}")
    print(f"\nSaved: {out_path}")

if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('input')
    p.add_argument('-o', '--output', default='clickhouse-findings.csv')
    args = p.parse_args()
    with open(args.input) as f:
        targets = [l.strip() for l in f if l.strip()]
    asyncio.run(run(targets, args.output))
