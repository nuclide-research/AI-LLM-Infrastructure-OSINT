#!/usr/bin/env python3
"""
vectordb_probe.py - focused, deadline-correct, restraint-bounded vector-DB / snapshot reader (Cat-13).

Why this and not aimap: aimap's enum phase has no per-read deadline, so it tarpits and
deadlocks on hosts that accept a connection and never reply (seen twice on this host set:
576 / 289 held ESTABLISHED sockets, futex deadlock, no JSON written). This tool enforces a
hard per-recv deadline AND a response byte cap, so a tarpit host costs READ_T seconds and a
bounded buffer, never a hang.

What it reads (GET only, read-only):
  qdrant   :6333  /collections                      (collection names)
                  /collections/{c}                   (vector count, config) - first N only
                  /collections/{c}/snapshots         (snapshot listing - the Cat-13 surface)
  weaviate :8080  /v1/meta /v1/schema                (version, class names)
                  /v1/backups/filesystem|s3|gcs      (backup listing - Cat-13)
                  /v1/nodes                          (object/shard counts)
  chroma   :8000  /api/v2/heartbeat /api/v1/heartbeat
                  /api/v1/collections                (v1 collection list)
                  /api/v2/tenants/default_tenant/databases/default_database/collections (v2)
  elastic  :9200  /  /_cat/indices  /_snapshot  /_snapshot/_all  (index + snapshot repos)
  clickhouse:8123 /?query=SHOW DATABASES             (db names - metadata only)

Restraint: NAMES and COUNTS only. Never GET /collections/{c}/points (vector payloads),
never scroll/search, never read an ES document, never SELECT rows (only SHOW DATABASES
metadata), never POST a snapshot/restore. Response hard-capped at CAP bytes. A 401/403 is
recorded auth_status=AUTH_ON ("surface open, access not exercised"), never as access.
"""
import sys, json, socket, ssl, re, concurrent.futures as cf

CONNECT_T = 4.0
READ_T = 5.0
CAP = 256 * 1024
CONC = 16
PER_COLLECTION_LIMIT = 8   # cap per-collection follow-up requests (snapshots/count)

def http_get(ip, port, path, host_hdr=None):
    use_tls = port in (443, 9243)
    try:
        raw = socket.create_connection((ip, port), timeout=CONNECT_T)
    except Exception as e:
        return None
    s = raw
    try:
        if use_tls:
            ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
            s = ctx.wrap_socket(raw, server_hostname=ip)
        req = ("GET %s HTTP/1.1\r\nHost: %s\r\nUser-Agent: nuclide-cat13-verify\r\n"
               "Accept: application/json\r\nConnection: close\r\n\r\n" % (path, host_hdr or ip)).encode()
        s.sendall(req)
        s.settimeout(READ_T)
        buf=b""
        while len(buf)<CAP:
            try: c=s.recv(8192)
            except Exception: break
            if not c: break
            buf+=c
        head,_,body=buf.partition(b"\r\n\r\n")
        m=re.match(rb"HTTP/\d\.\d (\d{3})", head)
        status=int(m.group(1)) if m else None
        return (status, body[:CAP].decode("latin1","replace"))
    except Exception:
        return None
    finally:
        try: s.close()
        except Exception: pass

def auth_label(status):
    if status in (401,403): return "AUTH_ON"      # surface open, access not exercised
    if status==200: return "UNAUTH_OPEN"
    return "OTHER"

def jtry(body):
    try: return json.loads(body)
    except Exception:
        # body may have trailing junk past cap; try to find first JSON object/array
        for op,cl in (("{","}"),("[","]")):
            i=body.find(op)
            if i>=0:
                try: return json.loads(body[i:body.rfind(cl)+1])
                except Exception: pass
    return None

def probe_qdrant(ip):
    o={"ip":ip,"platform":"qdrant","port":6333}
    r=http_get(ip,6333,"/collections")
    if not r: o["auth_status"]="DEAD"; return o
    st,body=r; o["auth_status"]=auth_label(st); o["status"]=st
    if st!=200: o["evidence"]=body[:120]; return o
    j=jtry(body) or {}
    cols=[c.get("name") for c in (((j.get("result") or {}).get("collections")) or [])]
    o["collections"]=cols; o["collection_count"]=len(cols)
    o["snapshots"]={}; o["vector_counts"]={}
    for c in cols[:PER_COLLECTION_LIMIT]:
        rs=http_get(ip,6333,f"/collections/{c}/snapshots")
        if rs and rs[0]==200:
            sj=jtry(rs[1]) or {}
            snaps=[s.get("name") for s in ((sj.get("result")) or [])]
            if snaps: o["snapshots"][c]=snaps
        rc=http_get(ip,6333,f"/collections/{c}")
        if rc and rc[0]==200:
            cj=jtry(rc[1]) or {}
            pts=((cj.get("result") or {}).get("points_count"))
            if pts is not None: o["vector_counts"][c]=pts
    return o

def probe_weaviate(ip):
    o={"ip":ip,"platform":"weaviate","port":8080}
    r=http_get(ip,8080,"/v1/meta")
    if not r:
        r=http_get(ip,8080,"/v1/schema")
        if not r: o["auth_status"]="DEAD"; return o
    st,body=r; o["status"]=st
    meta=jtry(body) or {}
    o["version"]=meta.get("version")
    rs=http_get(ip,8080,"/v1/schema")
    if rs:
        o["auth_status"]=auth_label(rs[0])
        if rs[0]==200:
            sj=jtry(rs[1]) or {}
            classes=[c.get("class") for c in (sj.get("classes") or [])]
            o["classes"]=classes; o["class_count"]=len(classes)
        else:
            o["evidence"]=rs[1][:120]
    else:
        o["auth_status"]=auth_label(st)
    # backup listings (Cat-13)
    o["backups"]={}
    for be in ("filesystem","s3","gcs","azure"):
        rb=http_get(ip,8080,f"/v1/backups/{be}")
        if rb and rb[0]==200:
            bj=jtry(rb[1])
            if isinstance(bj,list) and bj: o["backups"][be]=[b.get("id") for b in bj if isinstance(b,dict)]
    rn=http_get(ip,8080,"/v1/nodes")
    if rn and rn[0]==200:
        nj=jtry(rn[1]) or {}
        try: o["object_count"]=sum(n.get("stats",{}).get("objectCount",0) for n in nj.get("nodes",[]))
        except Exception: pass
    return o

def probe_chroma(ip):
    o={"ip":ip,"platform":"chroma","port":8000}
    hb=http_get(ip,8000,"/api/v2/heartbeat") or http_get(ip,8000,"/api/v1/heartbeat")
    if not hb: o["auth_status"]="DEAD"; return o
    o["status"]=hb[0]
    # v1
    r=http_get(ip,8000,"/api/v1/collections")
    used="v1"
    if not r or r[0] in (404,410):
        r=http_get(ip,8000,"/api/v2/tenants/default_tenant/databases/default_database/collections"); used="v2"
    if not r: o["auth_status"]=auth_label(hb[0]); return o
    o["auth_status"]=auth_label(r[0]); o["api"]=used; o["status"]=r[0]
    if r[0]==200:
        j=jtry(r[1])
        if isinstance(j,list):
            o["collections"]=[c.get("name") for c in j if isinstance(c,dict)]
            o["collection_count"]=len(o["collections"])
    else:
        o["evidence"]=r[1][:120]
    return o

def probe_elastic(ip):
    o={"ip":ip,"platform":"elasticsearch","port":9200}
    r=http_get(ip,9200,"/")
    if not r: o["auth_status"]="DEAD"; return o
    st,body=r; o["status"]=st; o["auth_status"]=auth_label(st)
    if st==200:
        rj=jtry(body) or {}
        o["cluster"]=rj.get("cluster_name"); o["version"]=((rj.get("version") or {}).get("number"))
        ri=http_get(ip,9200,"/_cat/indices?format=json&h=index,docs.count,store.size")
        if ri and ri[0]==200:
            ij=jtry(ri[1]) or []
            o["indices"]=[{"i":x.get("index"),"docs":x.get("docs.count")} for x in ij][:60]
            o["index_count"]=len(ij)
        rsnap=http_get(ip,9200,"/_snapshot")
        if rsnap and rsnap[0]==200:
            sj=jtry(rsnap[1]) or {}
            o["snapshot_repos"]=list(sj.keys())
    else:
        o["evidence"]=body[:120]
    return o

def probe_clickhouse(ip):
    o={"ip":ip,"platform":"clickhouse","port":8123}
    r=http_get(ip,8123,"/?query=SHOW%20DATABASES")
    if not r: o["auth_status"]="DEAD"; return o
    st,body=r; o["status"]=st; o["auth_status"]=auth_label(st)
    if st==200:
        dbs=[l for l in body.strip().splitlines() if l and "<" not in l][:50]
        o["databases"]=dbs
    else:
        o["evidence"]=body[:120]
    return o

PROBES={"qdrant":probe_qdrant,"weaviate":probe_weaviate,"chroma":probe_chroma,
        "elastic":probe_elastic,"clickhouse":probe_clickhouse}

def main():
    plat=sys.argv[1]; listf=sys.argv[2]; outf=sys.argv[3] if len(sys.argv)>3 else f"vdb-{plat}.json"
    fn=PROBES[plat]
    hosts=[l.strip() for l in open(listf) if l.strip() and not l.startswith("#")]
    res=[]
    with cf.ThreadPoolExecutor(max_workers=CONC) as ex:
        futs={ex.submit(fn,h):h for h in hosts}
        for i,f in enumerate(cf.as_completed(futs),1):
            try: r=f.result()
            except Exception as e: r={"ip":futs[f],"platform":plat,"error":str(e)}
            res.append(r)
            asx=r.get("auth_status")
            if asx=="UNAUTH_OPEN":
                cc=r.get("collection_count") or r.get("class_count") or r.get("index_count") or len(r.get("databases",[]) or [])
                snaps=sum(len(v) for v in (r.get("snapshots") or {}).values())
                bks=sum(len(v) for v in (r.get("backups") or {}).values())
                extra=f" snaps={snaps}" if snaps else ""
                extra+=f" backups={bks}" if bks else ""
                print(f"[{i}/{len(hosts)}] {r['ip']:<16} UNAUTH_OPEN items={cc}{extra}", flush=True)
    json.dump(res,open(outf,"w"),indent=2)
    op=[r for r in res if r.get("auth_status")=="UNAUTH_OPEN"]
    au=[r for r in res if r.get("auth_status")=="AUTH_ON"]
    dead=[r for r in res if r.get("auth_status") in ("DEAD",None)]
    print(f"\n=== {plat}: {len(hosts)} hosts | UNAUTH_OPEN={len(op)} | AUTH_ON={len(au)} | dead/other={len(dead)} ===")
    print(f"wrote {outf}")

if __name__=="__main__":
    main()
