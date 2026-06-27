#!/usr/bin/env python3
"""
Step 0c scanner (refined) — HTTP endpoint verification
Since TCP banners are empty, verify via BentoML-specific endpoints:
GET /docs.json, /healthz, /schema.json, /metrics
"""

import requests
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from time import time

CORPUS_FILE = 'data/corpus/bentoml-corpus-2026-06-27.txt'
TIMEOUT = 5
MAX_WORKERS = 20

def http_verify(ip, port, timeout=TIMEOUT):
    """HTTP-level verification for BentoML endpoints"""
    base = f'http://{ip}:{port}'
    result = {
        'ip': ip,
        'port': port,
        'base_url': base,
        'is_bentoml': False,
        'endpoints': {},
        'status': 'NOT_BENTOML',
    }

    try:
        # Test each BentoML endpoint
        endpoints = {
            '/docs.json': {'expect': 'x-bentoml', 'type': 'json'},
            '/healthz': {'expect': 'ok', 'type': 'plain'},
            '/schema.json': {'expect': 'bentoml', 'type': 'json'},
            '/': {'expect': 'BentoML', 'type': 'html'},
        }

        for path, config in endpoints.items():
            try:
                url = base + path
                r = requests.get(url, timeout=timeout, verify=False, allow_redirects=False)
                text = r.text

                is_match = False
                if config['type'] == 'json':
                    try:
                        j = json.loads(text)
                        is_match = config['expect'].lower() in json.dumps(j).lower()
                    except:
                        is_match = config['expect'].lower() in text.lower()
                else:
                    is_match = config['expect'].lower() in text.lower()

                result['endpoints'][path] = {
                    'status': r.status_code,
                    'match': is_match,
                    'content_preview': text[:100] if text else '',
                }

                if is_match:
                    result['is_bentoml'] = True
                    result['status'] = 'BENTOML'

            except requests.exceptions.Timeout:
                result['endpoints'][path] = {'status': 'timeout'}
            except requests.exceptions.ConnectionError:
                result['endpoints'][path] = {'status': 'refused'}
            except Exception as e:
                result['endpoints'][path] = {'status': 'error', 'error': str(e)[:30]}

    except Exception as e:
        result['error'] = str(e)

    return result

def main():
    with open(CORPUS_FILE) as f:
        hosts = [line.strip() for line in f if line.strip()]

    print(f"[*] Starting HTTP verification on {len(hosts)} hosts")
    print(f"[*] Timeout: {TIMEOUT}s, Workers: {MAX_WORKERS}")

    results = {'bentoml': [], 'not_bentoml': [], 'error': []}
    start = time()

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = {}
        for host in hosts:
            ip, port = host.rsplit(':', 1)
            f = ex.submit(http_verify, ip, port)
            futures[f] = host

        completed = 0
        for f in as_completed(futures):
            completed += 1
            host = futures[f]
            try:
                result = f.result()
            except Exception as e:
                result = {'ip': host.split(':')[0], 'port': host.split(':')[1], 'error': str(e), 'status': 'EXCEPTION'}
                results['error'].append(result)
                continue

            if result.get('is_bentoml'):
                results['bentoml'].append(result)
                print(f"[+] {host} — BENTOML (confirmed via HTTP)")
            else:
                results['not_bentoml'].append(result)
                if completed % 10 == 0:
                    print(f"[.] {completed}/{len(hosts)} processed")

    elapsed = time() - start

    print(f"\n{'='*70}")
    print(f"HTTP VERIFICATION RESULTS ({elapsed:.1f}s)")
    print(f"{'='*70}")
    print(f"BentoML (HTTP verified): {len(results['bentoml'])} hosts")
    print(f"Not BentoML:            {len(results['not_bentoml'])} hosts")
    print(f"Errors:                 {len(results['error'])} hosts")

    # Write results
    with open('data/corpus/bentoml-http-verified-2026-06-27.txt', 'w') as f:
        for r in sorted(results['bentoml'], key=lambda x: (x['ip'], int(x['port']))):
            f.write(f"{r['ip']}:{r['port']}\n")

    with open('data/scanner-http-results-bentoml-2026-06-27.json', 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n[*] HTTP verified corpus: data/corpus/bentoml-http-verified-2026-06-27.txt")
    print(f"[*] Full results: data/scanner-http-results-bentoml-2026-06-27.json")

if __name__ == '__main__':
    main()
