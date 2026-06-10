#!/usr/bin/env python3
"""
Lane A — NICE 541 Pentester
Paired-probe re-validation for Cat-Tabby + Devstral re-survey 2026-06-09.

Mission: detect MITM/cache/load-balancer response rewriting introduced by
Mullvad VPN exit (us-phx-wg-206). For each candidate Ollama host:
  T0:  GET /api/tags  (no Authorization)
  +8s
  T1:  GET /api/tags  (no Authorization)
  diff: sha256(sorted(model_names)) at T0 vs T1.

Stable  = signatures match => trustworthy live cohort
Unstable = signatures diverge => VPN rewrite / cache / round-robin LB => EXCLUDE

Restraint: GET /api/tags ONLY. No /api/generate, /api/chat, /api/pull,
/api/delete. Names are the finding (Insight #1).

Atoms exercised:
  T0028 authorized pentest    K0342 pentest principles
  S0051 pentest tooling       S0001 vuln scan
  S0081 network analysis      T0188 audit findings & remediation
  K0177 kill chain (recon stage)

Output JSON (per-host record) is VisorLog-ingest compatible:
  {ip, port, t0, t1, status_t0, status_t1, sig_t0, sig_t1, stable,
   model_count_t0, model_count_t1, code_models_t0, code_models_t1,
   divergence_kind, models_t0, models_t1}
"""
from __future__ import annotations
import argparse
import asyncio
import hashlib
import json
import sys
import time
from pathlib import Path

import aiohttp

# Code-model substring matchers (qwen3-coder, devstral, codellama, starcoder,
# deepseek-coder, code-gemma, codestral, granite-code, wizardcoder, magicoder)
CODE_TOKENS = (
    "coder", "code-", "codestral", "devstral", "starcoder",
    "codellama", "codegemma", "wizardcoder", "magicoder", "granite-code",
)

def is_code_model(name: str) -> bool:
    n = name.lower()
    return any(tok in n for tok in CODE_TOKENS)

def sig(models: list[str]) -> str:
    # Stable sha256 over the sorted name list — order-insensitive.
    joined = "\n".join(sorted(models))
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()[:16]

def classify_divergence(rec_t0: dict, rec_t1: dict) -> str:
    s0, s1 = rec_t0["status"], rec_t1["status"]
    if s0 is None and s1 is None:
        return "both-unreachable"
    if s0 is None or s1 is None:
        return "reachability-flip"
    if s0 != s1:
        return f"status-flip-{s0}-to-{s1}"
    if s0 != 200:
        return f"both-{s0}"
    # both 200
    m0, m1 = set(rec_t0["models"]), set(rec_t1["models"])
    if m0 == m1:
        return "stable"
    if len(m0) != len(m1):
        return "different-model-count"
    return "different-model-set"

async def probe_once(session: aiohttp.ClientSession, ip: str, port: int) -> dict:
    url = f"http://{ip}:{port}/api/tags"
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as r:
            status = r.status
            if status == 200:
                try:
                    j = await r.json(content_type=None)
                    models = [m.get("name", "") for m in j.get("models", []) if m.get("name")]
                except Exception as e:
                    return {"status": status, "err": f"json-parse: {e}", "models": []}
                return {"status": status, "err": None, "models": models}
            return {"status": status, "err": None, "models": []}
    except asyncio.TimeoutError:
        return {"status": None, "err": "timeout", "models": []}
    except aiohttp.ClientConnectorError as e:
        return {"status": None, "err": f"connect: {str(e)[:80]}", "models": []}
    except Exception as e:
        return {"status": None, "err": f"{type(e).__name__}: {str(e)[:80]}", "models": []}

async def paired_probe(session: aiohttp.ClientSession, ip: str, port: int, gap: float) -> dict:
    t0 = time.time()
    r0 = await probe_once(session, ip, port)
    await asyncio.sleep(gap)
    t1 = time.time()
    r1 = await probe_once(session, ip, port)

    rec = {
        "ip": ip,
        "port": port,
        "t0": int(t0),
        "t1": int(t1),
        "status_t0": r0["status"],
        "status_t1": r1["status"],
        "err_t0": r0["err"],
        "err_t1": r1["err"],
        "models_t0": r0["models"],
        "models_t1": r1["models"],
        "model_count_t0": len(r0["models"]),
        "model_count_t1": len(r1["models"]),
        "sig_t0": sig(r0["models"]) if r0["models"] else None,
        "sig_t1": sig(r1["models"]) if r1["models"] else None,
        "code_models_t0": [m for m in r0["models"] if is_code_model(m)],
        "code_models_t1": [m for m in r1["models"] if is_code_model(m)],
    }
    rec["stable"] = (
        rec["status_t0"] == 200
        and rec["status_t1"] == 200
        and rec["sig_t0"] is not None
        and rec["sig_t0"] == rec["sig_t1"]
    )
    rec["divergence_kind"] = classify_divergence(
        {"status": rec["status_t0"], "models": rec["models_t0"]},
        {"status": rec["status_t1"], "models": rec["models_t1"]},
    )
    return rec

async def worker(name: int, queue: asyncio.Queue, out_fp, session, gap: float, counters: dict):
    while True:
        item = await queue.get()
        if item is None:
            queue.task_done()
            return
        ip, port = item
        try:
            rec = await paired_probe(session, ip, port, gap)
            out_fp.write(json.dumps(rec) + "\n")
            out_fp.flush()
            counters["done"] += 1
            if rec["stable"]:
                counters["stable"] += 1
            elif rec["status_t0"] is None and rec["status_t1"] is None:
                counters["dead"] += 1
            else:
                counters["unstable"] += 1
            if counters["done"] % 50 == 0:
                print(
                    f"  [{counters['done']}/{counters['total']}] "
                    f"stable={counters['stable']} unstable={counters['unstable']} "
                    f"dead={counters['dead']}",
                    file=sys.stderr,
                )
        except Exception as e:
            print(f"  worker error on {ip}: {e}", file=sys.stderr)
        finally:
            queue.task_done()

def parse_target(line: str) -> tuple[str, int] | None:
    line = line.strip()
    if not line or line.startswith("#"):
        return None
    if ":" in line:
        ip, port = line.rsplit(":", 1)
        try:
            return ip.strip(), int(port)
        except ValueError:
            return None
    return line, 11434

def load_targets_txt(path: Path) -> list[tuple[str, int]]:
    out = []
    seen = set()
    for line in path.read_text().splitlines():
        t = parse_target(line)
        if t and t not in seen:
            seen.add(t)
            out.append(t)
    return out

def load_targets_jsonl(path: Path) -> list[tuple[str, int]]:
    out = []
    seen = set()
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        try:
            j = json.loads(line)
        except json.JSONDecodeError:
            continue
        ip = j.get("ip")
        port = j.get("port", 11434)
        if ip and (ip, port) not in seen:
            seen.add((ip, port))
            out.append((ip, port))
    return out

async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="targets file (.txt ip:port per line, or .jsonl with ip/port keys)")
    ap.add_argument("--output", required=True, help="output JSONL of paired records")
    ap.add_argument("--workers", type=int, default=80)
    ap.add_argument("--gap", type=float, default=8.0, help="seconds between T0 and T1 probes")
    ap.add_argument("--limit", type=int, default=0, help="0 = all")
    args = ap.parse_args()

    inp = Path(args.input)
    targets = load_targets_jsonl(inp) if inp.suffix == ".jsonl" else load_targets_txt(inp)
    if args.limit:
        targets = targets[: args.limit]
    print(f"Loaded {len(targets)} targets from {inp}", file=sys.stderr)

    queue: asyncio.Queue = asyncio.Queue()
    for t in targets:
        queue.put_nowait(t)
    for _ in range(args.workers):
        queue.put_nowait(None)

    counters = {"done": 0, "stable": 0, "unstable": 0, "dead": 0, "total": len(targets)}

    connector = aiohttp.TCPConnector(limit=args.workers * 2, ssl=False, force_close=True)
    headers = {"User-Agent": "nuclide-paired-probe/1.0 (+nuclide-research.com)"}
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    async with aiohttp.ClientSession(connector=connector, headers=headers) as session:
        with out_path.open("w") as out_fp:
            tasks = [
                asyncio.create_task(worker(i, queue, out_fp, session, args.gap, counters))
                for i in range(args.workers)
            ]
            await queue.join()
            for t in tasks:
                await t

    print(
        f"\nDONE  total={counters['total']}  stable={counters['stable']}  "
        f"unstable={counters['unstable']}  dead={counters['dead']}",
        file=sys.stderr,
    )

if __name__ == "__main__":
    asyncio.run(main())
