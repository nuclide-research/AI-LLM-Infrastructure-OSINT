#!/usr/bin/env python3
"""
bucketnames.py - restraint-bounded anonymous-S3 bucket/key NAME reader (Cat-13 verify stage).

WHY this exists (and why not aimap): the Cat-13 finding for an anonymously-listable object
store is the set of bucket/key NAMES that reveal AI/ML artifact intent (mlflow-artifacts,
model-registry, checkpoints, *.safetensors). aimap's MinIO enumerator is single-vendor and
has no read deadline (it tarpits). These hosts are mixed-vendor S3 (Ceph RGW / SeaweedFS /
MinIO / Garage / Zenko / Ozone). This tool:
  - reads ONLY GET / (the bucket-list the host already serves to everyone, anonymously)
  - HARD-CAPS the response read at CAP bytes so it physically cannot pull an object body
  - parses ONLY <Name> (S3 root list) and <Key> (bucket key list) elements - names, never bodies
  - applies the AI-scope discriminator on names and reports matched tokens
  - has a real connect+read deadline (the thing aimap lacks) and bounded concurrency
Restraint: names ARE the finding. No object GET, no write, no delete, no policy read.
A 403/AccessDenied is logged "surface open, access not exercised", never as access.
"""
import sys, json, socket, ssl, re, concurrent.futures as cf
from urllib.parse import urlparse

CAP = 512 * 1024            # 512KB hard read cap - plenty for names, far below an object body of interest
CONNECT_T = 4.0
READ_T = 6.0
PORTS = [80, 443, 9000, 7480, 8333, 9878, 3902, 8000]   # generic + Ceph/SeaweedFS/Ozone/Garage/Chroma
CONC = 14

# AI/ML artifact intent tokens (bucket/key names only)
AI_TOKENS = [
    "mlflow","model-registry","modelregistry","models","checkpoint","ckpt","safetensors",
    ".pt",".pth",".gguf",".onnx",".h5",".npz","mlmodel","conda.yaml","dataset","training",
    "train-data","train_data","embedding","embeddings","vector","weights",".dvc","lakefs",
    "kubeflow","sagemaker","huggingface","hf-cache","tensorboard","feast","artifact","registry",
    "llm","llama","mistral","bert","rag","finetune","fine-tune","lora","adapter","pytorch",
    "tensorflow","keras","feature-store","featurestore","wandb","pachyderm","dvc-cache",
]
NAME_RE = re.compile(rb"<Name>([^<]{1,256})</Name>")
KEY_RE  = re.compile(rb"<Key>([^<]{1,512})</Key>")
ROOT_MARK = b"<ListAllMyBucketsResult"
BKT_MARK  = b"<ListBucketResult"
DENY_MARK = re.compile(rb"AccessDenied|SignatureDoesNotMatch|InvalidAccessKeyId|<Code>")

def http_get_root(ip, port):
    """Raw GET / with hard byte cap. Returns (status, server, body_bytes) or None."""
    use_tls = port in (443,)
    try:
        raw = socket.create_connection((ip, port), timeout=CONNECT_T)
    except Exception:
        return None
    s = raw
    try:
        if use_tls:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            s = ctx.wrap_socket(raw, server_hostname=ip)
        req = ("GET / HTTP/1.1\r\nHost: %s\r\nUser-Agent: nuclide-cat13-verify\r\n"
               "Accept: */*\r\nConnection: close\r\n\r\n" % ip).encode()
        s.sendall(req)
        s.settimeout(READ_T)
        buf = b""
        while len(buf) < CAP:
            try:
                chunk = s.recv(8192)
            except Exception:
                break
            if not chunk:
                break
            buf += chunk
        # split headers/body
        head, _, body = buf.partition(b"\r\n\r\n")
        status = None
        m = re.match(rb"HTTP/\d\.\d (\d{3})", head)
        if m: status = int(m.group(1))
        sm = re.search(rb"[Ss]erver:\s*([^\r\n]+)", head)
        server = sm.group(1).decode("latin1").strip() if sm else ""
        return (status, server, head + b"\r\n\r\n" + body[:CAP])
    except Exception:
        return None
    finally:
        try: s.close()
        except Exception: pass

def scope(names):
    low = [n.lower() for n in names]
    hits = sorted({t for t in AI_TOKENS for n in low if t in n})
    return hits

def probe_host(ip):
    out = {"ip": ip, "anon_listings": [], "ai_scope": False, "ai_tokens": [], "all_buckets": []}
    for port in PORTS:
        r = http_get_root(ip, port)
        if not r:
            continue
        status, server, body = r
        is_root = ROOT_MARK in body
        is_bkt = BKT_MARK in body
        if not (is_root or is_bkt):
            # surface present (port open) but not an anon listing on /
            if status and DENY_MARK.search(body):
                out["anon_listings"].append({"port": port, "status": status, "server": server,
                                             "kind": "denied", "note": "surface open, access not exercised"})
            continue
        names = [n.decode("latin1") for n in NAME_RE.findall(body)] if is_root else []
        keys  = [k.decode("latin1") for k in KEY_RE.findall(body)] if is_bkt else []
        vals = names + keys
        hits = scope(vals)
        rec = {"port": port, "status": status, "server": server,
               "kind": "root_bucketlist" if is_root else "bucket_keylist",
               "count": len(vals), "names": vals[:120], "ai_tokens": hits}
        out["anon_listings"].append(rec)
        out["all_buckets"].extend(vals)
        if hits:
            out["ai_scope"] = True
            out["ai_tokens"] = sorted(set(out["ai_tokens"]) | set(hits))
    return out

def main():
    hosts = [l.strip() for l in open(sys.argv[1]) if l.strip() and not l.startswith("#")]
    results = []
    with cf.ThreadPoolExecutor(max_workers=CONC) as ex:
        futs = {ex.submit(probe_host, h): h for h in hosts}
        for i, f in enumerate(cf.as_completed(futs), 1):
            try:
                r = f.result()
            except Exception as e:
                r = {"ip": futs[f], "error": str(e)}
            results.append(r)
            if r.get("anon_listings"):
                tag = "  *AI*" if r.get("ai_scope") else ""
                kinds = ",".join(sorted({a.get("kind","") for a in r["anon_listings"]}))
                print(f"[{i}/{len(hosts)}] {r['ip']:<16} listings={len(r['anon_listings'])} ({kinds}) "
                      f"buckets={len(r.get('all_buckets',[]))} tokens={r.get('ai_tokens')}{tag}", flush=True)
    out_f = sys.argv[2] if len(sys.argv) > 2 else "bucketnames-results.json"
    json.dump(results, open(out_f, "w"), indent=2)
    live = [r for r in results if r.get("anon_listings")]
    ai = [r for r in results if r.get("ai_scope")]
    print(f"\n=== {len(hosts)} hosts | {len(live)} with anon listing on / | {len(ai)} AI-scope ===")
    print(f"wrote {out_f}")

if __name__ == "__main__":
    main()
