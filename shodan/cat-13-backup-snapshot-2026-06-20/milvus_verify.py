#!/usr/bin/env python3
"""
milvus_verify.py - refute-or-confirm the "all 82 hosts = Milvus/2.3.4" uniformity (Cat-13 VERIFY).

82 hosts ALL bannering the identical version 2.3.4 on :9091 is implausible for organic
deployments (real populations show version spread). Hypotheses: (a) deception fleet spoofing
the Server header, (b) one operator's cloned cohort, (c) a managed-service template pinning 2.3.4.

Discriminator (all read-only, :9091 metrics/health port - NOT the gRPC data port):
  GET /healthz   -> real Milvus returns "OK" plies; a spoof may 200 with wrong/empty body
  GET /metrics   -> real Milvus emits prometheus 'milvus_*' metrics incl collection counts;
                    a header-only spoof cannot synthesize a coherent metrics body
We read the Server header, /healthz body, and whether /metrics contains genuine milvus_ metric
families + the collection-count gauge. We do NOT touch gRPC :19530 (data plane).
"""
import sys, json, socket, re, concurrent.futures as cf
CONNECT_T=4.0; READ_T=5.0; CAP=256*1024; CONC=16

def get(ip,port,path):
    try: s=socket.create_connection((ip,port),timeout=CONNECT_T)
    except Exception: return None
    try:
        s.sendall(f"GET {path} HTTP/1.1\r\nHost: {ip}\r\nUser-Agent: nuclide-cat13-verify\r\nConnection: close\r\n\r\n".encode())
        s.settimeout(READ_T); b=b""
        while len(b)<CAP:
            try: c=s.recv(8192)
            except Exception: break
            if not c: break
            b+=c
        head,_,body=b.partition(b"\r\n\r\n")
        m=re.match(rb"HTTP/\d\.\d (\d{3})",head); st=int(m.group(1)) if m else None
        sm=re.search(rb"[Ss]erver:\s*([^\r\n]+)",head); srv=sm.group(1).decode("latin1").strip() if sm else ""
        return st,srv,body[:CAP].decode("latin1","replace")
    except Exception: return None
    finally:
        try: s.close()
        except Exception: pass

def probe(ip):
    o={"ip":ip}
    h=get(ip,9091,"/healthz")
    if not h: o["verdict"]="DEAD"; return o
    o["health_status"],o["server"],hb=h
    o["healthz_body"]=hb[:80].replace("\n"," ")
    mm=get(ip,9091,"/metrics")
    real_metrics=False; collnum=None
    if mm and mm[0]==200:
        body=mm[2]
        fams=len(re.findall(r'^milvus_\w+', body, re.M))
        real_metrics=fams>=5
        o["milvus_metric_families"]=fams
        cm=re.search(r'milvus_\w*collection_num\S*\s+([\d.]+)', body)
        if cm: collnum=cm.group(1)
        o["collection_num_metric"]=collnum
    # verdict
    if real_metrics:
        o["verdict"]="REAL_MILVUS"
    elif o["health_status"]==200 and "milvus" in (o["server"] or "").lower():
        o["verdict"]="HEADER_ONLY_SUSPECT"   # claims milvus but no coherent metrics body
    elif o["health_status"]==200:
        o["verdict"]="200_NO_MILVUS_BODY"
    else:
        o["verdict"]="OTHER"
    return o

def main():
    hosts=[l.strip() for l in open(sys.argv[1]) if l.strip() and not l.startswith("#")]
    res=[]
    with cf.ThreadPoolExecutor(max_workers=CONC) as ex:
        futs={ex.submit(probe,h):h for h in hosts}
        for i,f in enumerate(cf.as_completed(futs),1):
            try: r=f.result()
            except Exception as e: r={"ip":futs[f],"error":str(e)}
            res.append(r)
            print(f"[{i}/{len(hosts)}] {r.get('ip'):<16} {r.get('verdict'):<20} server={r.get('server','')[:24]} mfam={r.get('milvus_metric_families')} coll={r.get('collection_num_metric')}", flush=True)
    out=sys.argv[2] if len(sys.argv)>2 else "milvus-verify.json"
    json.dump(res,open(out,"w"),indent=2)
    import collections as C
    v=C.Counter(r.get("verdict") for r in res)
    print(f"\n=== milvus verify: {dict(v)} ===\nwrote {out}")

if __name__=="__main__": main()
