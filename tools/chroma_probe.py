#!/usr/bin/env python3
"""ChromaDB version sweep. GET /api/v1/version -> {"version": "X.Y.Z"}"""
import asyncio, csv, json, re, sys
import aiohttp

TIMEOUT = aiohttp.ClientTimeout(total=8, connect=4)
CONCURRENCY = 80

async def probe(session, target):
    base = target.rstrip('/')
    result = {'target': target, 'version': '', 'auth_state': '', 'method': ''}
    for path in ['/api/v1/version', '/api/v1', '/api/v1/heartbeat']:
        url = base + path
        try:
            async with session.get(url, ssl=False, allow_redirects=True) as r:
                if r.status == 200:
                    body = await r.text(errors='ignore')
                    try:
                        j = json.loads(body)
                        # /api/v1/version returns bare string: "0.5.20"
                        if isinstance(j, str) and j:
                            result.update({'version': j, 'auth_state': 'unauth', 'method': path})
                            return result
                        # fallback: dict with version key
                        if isinstance(j, dict):
                            ver = j.get('version', '')
                            if ver:
                                result.update({'version': ver, 'auth_state': 'unauth', 'method': path})
                                return result
                    except:
                        pass
                    result['auth_state'] = 'unauth'
                elif r.status in (401, 403):
                    result['auth_state'] = 'auth'
        except:
            pass
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
            if done % 100 == 0 or done == len(tasks):
                found = sum(1 for x in rows if x['version'])
                print(f'  [{done}/{len(tasks)}] versioned: {found}', file=sys.stderr)
    rows.sort(key=lambda x: (not x['version'], x['target']))
    with open(out_path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['target', 'version', 'auth_state', 'method'])
        w.writeheader()
        w.writerows(rows)
    versioned = sum(1 for r in rows if r['version'])
    print(f"Saved {out_path} ({len(rows)} rows, {versioned} versioned)")

if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('input')
    p.add_argument('-o', '--output', default='chroma-versions.csv')
    args = p.parse_args()
    with open(args.input) as f:
        targets = [l.strip() for l in f if l.strip()]
    asyncio.run(run(targets, args.output))
