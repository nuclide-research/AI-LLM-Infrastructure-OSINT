#!/usr/bin/env python3
"""
Step 0c scanner — BentoML banner grab + liveness verification
Parallel TCP/TLS connect, read banner, identify BentoML vs FP
"""

import socket
import sys
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from time import time

CORPUS_FILE = 'data/corpus/bentoml-corpus-2026-06-27.txt'
TIMEOUT = 5
MAX_WORKERS = 20

def grab_banner(ip, port, timeout=TIMEOUT):
    """Connect, grab banner, detect BentoML"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((ip, int(port)))

        # Read up to 4KB
        banner = b''
        try:
            while len(banner) < 4096:
                chunk = s.recv(4096 - len(banner))
                if not chunk:
                    break
                banner += chunk
        except socket.timeout:
            pass
        s.close()

        banner_str = banner.decode('utf-8', errors='ignore')

        # Detect BentoML
        is_bentoml = False
        version = None
        server_header = None

        if 'BentoML' in banner_str:
            is_bentoml = True
            # Try to extract version
            import re
            vm = re.search(r'BentoML[^/\d]*(\d+\.\d+\.\d+)', banner_str)
            if vm:
                version = vm.group(1)

        if 'Server:' in banner_str:
            import re
            sm = re.search(r'Server:\s*([^\r\n]+)', banner_str)
            if sm:
                server_header = sm.group(1).strip()

        return {
            'ip': ip,
            'port': port,
            'live': True,
            'is_bentoml': is_bentoml,
            'version': version,
            'server': server_header,
            'banner_preview': banner_str[:200],
            'status': 'BENTOML' if is_bentoml else 'FP_CANDIDATE',
        }

    except socket.timeout:
        return {
            'ip': ip,
            'port': port,
            'live': False,
            'error': 'timeout',
            'status': 'TIMEOUT',
        }
    except ConnectionRefusedError:
        return {
            'ip': ip,
            'port': port,
            'live': False,
            'error': 'refused',
            'status': 'REFUSED',
        }
    except Exception as e:
        return {
            'ip': ip,
            'port': port,
            'live': False,
            'error': str(e)[:50],
            'status': 'ERROR',
        }

def main():
    # Load corpus
    with open(CORPUS_FILE) as f:
        hosts = [line.strip() for line in f if line.strip()]

    print(f"[*] Starting banner grab on {len(hosts)} hosts")
    print(f"[*] Timeout: {TIMEOUT}s, Workers: {MAX_WORKERS}")

    results = {'bentoml': [], 'fp': [], 'offline': [], 'error': []}
    start = time()

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = {}
        for host in hosts:
            ip, port = host.rsplit(':', 1)
            f = ex.submit(grab_banner, ip, port)
            futures[f] = host

        completed = 0
        for f in as_completed(futures):
            completed += 1
            host = futures[f]
            try:
                result = f.result()
            except Exception as e:
                result = {'ip': host.split(':')[0], 'port': host.split(':')[1], 'error': str(e), 'status': 'EXCEPTION'}

            if result.get('status') == 'BENTOML':
                results['bentoml'].append(result)
                print(f"[+] {host} — BENTOML {result.get('version', '?')}")
            elif result.get('live') and not result.get('is_bentoml'):
                results['fp'].append(result)
                print(f"[-] {host} — FP ({result.get('server', 'unknown server')})")
            elif result.get('status') in ['TIMEOUT', 'REFUSED']:
                results['offline'].append(result)
                if completed % 10 == 0:
                    print(f"[.] {completed}/{len(hosts)} — {result['status']}")
            else:
                results['error'].append(result)
                print(f"[!] {host} — ERROR: {result.get('error')}")

    elapsed = time() - start

    print(f"\n{'='*70}")
    print(f"RESULTS ({elapsed:.1f}s)")
    print(f"{'='*70}")
    print(f"BentoML (confirmed):    {len(results['bentoml'])} hosts")
    print(f"False positives:        {len(results['fp'])} hosts")
    print(f"Offline/timeout:        {len(results['offline'])} hosts")
    print(f"Errors:                 {len(results['error'])} hosts")
    print(f"\nLive rate: {(len(results['bentoml']) + len(results['fp'])) / len(hosts) * 100:.1f}%")
    print(f"FP rate (of live):      {len(results['fp']) / max(1, len(results['bentoml']) + len(results['fp'])) * 100:.1f}%")

    # Write clean corpus (BentoML only)
    with open('data/corpus/bentoml-verified-2026-06-27.txt', 'w') as f:
        for r in sorted(results['bentoml'], key=lambda x: (x['ip'], int(x['port']))):
            f.write(f"{r['ip']}:{r['port']}\n")

    # Write full results as JSON
    with open('data/scanner-results-bentoml-2026-06-27.json', 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n[*] Verified corpus: data/corpus/bentoml-verified-2026-06-27.txt ({len(results['bentoml'])} hosts)")
    print(f"[*] Full results: data/scanner-results-bentoml-2026-06-27.json")

if __name__ == '__main__':
    main()
