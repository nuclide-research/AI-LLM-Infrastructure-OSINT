#!/usr/bin/env python3
"""
Cat-Tabby + Devstral cross-section probe — code-model deep-enum over Ollama.

Restraint discipline:
  ALLOWED:  GET /api/tags                     (model list — names ARE the finding)
  REFUSED:  POST /api/generate                (compute exfil)
  REFUSED:  POST /api/chat                    (compute exfil)
  REFUSED:  POST /api/pull /api/delete /api/push /api/create  (destructive)

Code-model families flagged (per HuggingFace + Ollama Library coverage 2026-06):
  Mistral:    devstral, devstral-2, codestral, codestral-mamba
  Qwen:       qwen2.5-coder, qwen-coder, qwen3-coder, qwen-25-coder
  DeepSeek:   deepseek-coder, deepseek-coder-v2
  Meta:       codellama, code-llama
  IBM:        granite-code, granite-3-code
  BigCode:    starcoder, starcoder2, starchat
  Salesforce: codegen, codegen2, codegen25
  Replit:     replit-code
  WizardLM:   wizardcoder
  Phind:      phind-codellama
"""
import asyncio, json, sys, time
from pathlib import Path
try:
    import aiohttp
except ImportError:
    print("install aiohttp: pip install aiohttp", file=sys.stderr); sys.exit(1)

CODE_MODEL_TOKENS = [
    'devstral', 'codestral',
    'qwen2.5-coder', 'qwen-coder', 'qwen3-coder', 'qwen25-coder', 'qwen2-coder',
    'deepseek-coder',
    'codellama', 'code-llama', 'code_llama',
    'granite-code', 'granite-3-code',
    'starcoder', 'starcoder2', 'starchat',
    'codegen',
    'replit-code',
    'wizardcoder',
    'phind-codellama', 'phind-code',
    'opencoder', 'open-coder',
    'yi-coder',
    'aixcoder',
]

def is_code_model(model_name):
    n = model_name.lower()
    return any(tok in n for tok in CODE_MODEL_TOKENS)

async def probe_one(session, ip, port, sem):
    async with sem:
        url = f"http://{ip}:{port}/api/tags"
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as r:
                if r.status != 200:
                    return {"ip": ip, "port": port, "status": r.status, "err": None, "models": [], "code_models": []}
                body = await r.text()
                data = json.loads(body)
                models = data.get('models', [])
                model_names = [m.get('name') or m.get('model') for m in models if isinstance(m, dict)]
                model_names = [n for n in model_names if n]
                code = [n for n in model_names if is_code_model(n)]
                # Pull richer model metadata for code-loaded hosts
                detail = []
                if code:
                    for m in models:
                        if not isinstance(m, dict): continue
                        nm = m.get('name') or m.get('model')
                        if nm and is_code_model(nm):
                            detail.append({
                                'name': nm,
                                'size': m.get('size'),
                                'family': (m.get('details') or {}).get('family'),
                                'parameter_size': (m.get('details') or {}).get('parameter_size'),
                                'quantization_level': (m.get('details') or {}).get('quantization_level'),
                                'modified_at': m.get('modified_at'),
                            })
                return {
                    "ip": ip, "port": port, "status": 200, "err": None,
                    "model_count": len(model_names),
                    "models": model_names,
                    "code_models": code,
                    "code_model_detail": detail,
                }
        except (aiohttp.ClientError, asyncio.TimeoutError, OSError) as e:
            return {"ip": ip, "port": port, "status": None, "err": str(e)[:80], "models": [], "code_models": []}
        except (ValueError, KeyError) as e:
            return {"ip": ip, "port": port, "status": "parse_err", "err": str(e)[:80], "models": [], "code_models": []}

async def main():
    targets = []
    for line in Path(sys.argv[1]).read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#'): continue
        if ':' in line:
            ip, port = line.rsplit(':', 1)
            targets.append((ip, int(port)))
        else:
            targets.append((line, 11434))

    print(f"# probing {len(targets)} Ollama hosts", file=sys.stderr)
    sem = asyncio.Semaphore(120)
    conn = aiohttp.TCPConnector(limit=200, ssl=False)
    out_path = sys.argv[2] if len(sys.argv) > 2 else 'probe-results.jsonl'
    code_path = 'code-loaded-hosts.jsonl'
    f_all = open(out_path, 'w')
    f_code = open(code_path, 'w')

    n_done = n_live = n_code = 0
    code_summary = {}
    t0 = time.time()
    async with aiohttp.ClientSession(connector=conn) as session:
        tasks = [probe_one(session, ip, port, sem) for ip, port in targets]
        for fut in asyncio.as_completed(tasks):
            r = await fut
            f_all.write(json.dumps(r) + '\n')
            n_done += 1
            if r.get('status') == 200:
                n_live += 1
                if r.get('code_models'):
                    n_code += 1
                    f_code.write(json.dumps(r) + '\n')
                    for m in r['code_models']:
                        code_summary[m] = code_summary.get(m, 0) + 1
                    print(f"[+] {r['ip']:<16}:{r['port']:<5} code_models={r['code_models'][:5]}", file=sys.stderr)
            if n_done % 250 == 0:
                rate = n_done / max(1, time.time() - t0)
                print(f"# progress: {n_done}/{len(targets)} ({rate:.0f}/s) live={n_live} code={n_code}", file=sys.stderr)

    f_all.close(); f_code.close()
    print(f"\n# DONE — total={n_done} live={n_live} code-loaded={n_code}", file=sys.stderr)
    print(f"# top code models (out of {n_code} hosts):", file=sys.stderr)
    for m, n in sorted(code_summary.items(), key=lambda x:-x[1])[:30]:
        print(f"#   {n:>4}  {m}", file=sys.stderr)

if __name__ == "__main__":
    asyncio.run(main())
