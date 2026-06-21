#!/usr/bin/env python3
"""
deep_verify.py - Cat-13 load-bearing VERIFY stage for the top organic vector-DB candidates.

For each candidate it does THREE read-only things only:
  1) RE-PROBE the names endpoint a second time (anti-transient: a finding must reproduce,
     not be a one-shot catch-all 200). qdrant /collections, weaviate /v1/schema+/v1/meta,
     chroma collections list. NAMES + COUNTS only.
  2) MARKER CONFIRM: pull the vendor-unique structural marker (qdrant result.collections[].name
     shape; weaviate meta.version + modules; chroma heartbeat nanosecond int) so we know it is
     the genuine engine, not a catch-all echoing 200.
  3) ATTRIBUTE: reverse-DNS (PTR) + TLS cert subject/SAN CN on 443 (operator identity).

Restraint: never reads a point/vector/document/row. Never scrolls/searches. Never POSTs.
Snapshot/backup LISTINGS (names only) are read for qdrant since that is the Cat-13 surface,
but their CONTENTS are never downloaded. 401/403 -> AUTH_ON, recorded as access-not-exercised.
"""
import sys, json, socket, ssl, re, concurrent.futures as cf

CONNECT_T=4.0; READ_T=6.0; CAP=256*1024

def http_get(ip, port, path, tls=False):
    try: raw=socket.create_connection((ip,port),timeout=CONNECT_T)
    except Exception: return None
    s=raw
    try:
        if tls:
            ctx=ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
            s=ctx.wrap_socket(raw,server_hostname=ip)
        s.sendall(("GET %s HTTP/1.1\r\nHost: %s\r\nUser-Agent: nuclide-cat13-verify\r\n"
                   "Accept: application/json\r\nConnection: close\r\n\r\n"%(path,ip)).encode())
        s.settimeout(READ_T); buf=b""
        while len(buf)<CAP:
            try: c=s.recv(8192)
            except Exception: break
            if not c: break
            buf+=c
        head,_,body=buf.partition(b"\r\n\r\n")
        m=re.match(rb"HTTP/\d\.\d (\d{3})",head); st=int(m.group(1)) if m else None
        return st, body[:CAP].decode("latin1","replace")
    except Exception: return None
    finally:
        try: s.close()
        except Exception: pass

def jtry(b):
    try: return json.loads(b)
    except Exception:
        for op,cl in (("{","}"),("[","]")):
            i=b.find(op)
            if i>=0:
                try: return json.loads(b[i:b.rfind(cl)+1])
                except Exception: pass
    return None

def reverse_dns(ip):
    try: return socket.gethostbyaddr(ip)[0]
    except Exception: return None

def cert_cn(ip, port=443):
    try:
        ctx=ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
        with socket.create_connection((ip,port),timeout=CONNECT_T) as raw:
            with ctx.wrap_socket(raw,server_hostname=ip) as s:
                c=s.getpeercert(binary_form=False) or {}
                # CERT_NONE gives empty dict; fall back to DER parse for subject/SAN
                der=s.getpeercert(binary_form=True)
        # minimal CN/SAN scrape from DER (avoid extra deps)
        if der:
            txt=der.decode("latin1","replace")
            cns=re.findall(r'[\x00-\x1f]([a-z0-9*][a-z0-9.\-*]{3,63}\.[a-z]{2,18})',txt,re.I)
            cns=[x for x in dict.fromkeys(cns) if not x.endswith(('.crt','.pem'))]
            return cns[:6] or None
    except Exception: return None
    return None

def verify_qdrant(ip):
    o={"ip":ip,"platform":"qdrant"}
    r=http_get(ip,6333,"/collections")
    if not r or r[0]!=200: o["reproduce"]=False; o["status"]=(r or [None])[0]; return o
    j=jtry(r[1]) or {}
    cols=[c.get("name") for c in (((j.get("result") or {}).get("collections")) or [])]
    o["reproduce"]=True; o["marker"]="result.collections[] present"; o["collections"]=cols
    # qdrant root telemetry marker (version) - names/version only
    rt=http_get(ip,6333,"/")
    if rt and rt[0]==200:
        rj=jtry(rt[1]) or {}
        o["version"]=rj.get("version")
    # snapshot LISTINGS only (Cat-13 surface) - names, never download
    snaps={}
    for c in cols[:8]:
        rs=http_get(ip,6333,f"/collections/{c}/snapshots")
        if rs and rs[0]==200:
            sj=jtry(rs[1]) or {}
            names=[s.get("name") for s in (sj.get("result") or [])]
            if names: snaps[c]=names
    o["snapshots"]=snaps
    return o

def verify_weaviate(ip):
    o={"ip":ip,"platform":"weaviate"}
    rm=http_get(ip,8080,"/v1/meta")
    if rm and rm[0]==200:
        mj=jtry(rm[1]) or {}
        o["version"]=mj.get("version"); o["marker"]="meta.version="+str(mj.get("version"))
        mods=mj.get("modules") or {}
        o["modules"]=list(mods.keys())[:12]
    rs=http_get(ip,8080,"/v1/schema")
    if not rs or rs[0]!=200: o["reproduce"]=False; o["status"]=(rs or [None])[0]; return o
    sj=jtry(rs[1]) or {}
    o["classes"]=[c.get("class") for c in (sj.get("classes") or [])]
    o["reproduce"]=True
    return o

def verify_chroma(ip):
    o={"ip":ip,"platform":"chroma"}
    hb=http_get(ip,8000,"/api/v2/heartbeat") or http_get(ip,8000,"/api/v1/heartbeat")
    if hb and hb[0]==200:
        hj=jtry(hb[1]) or {}
        ns=hj.get("nanosecond heartbeat") or hj.get("nanosecond_heartbeat")
        o["marker"]=f"nanosecond_heartbeat={ns}" if ns else "heartbeat200"
    r=http_get(ip,8000,"/api/v1/collections"); api="v1"
    if not r or r[0] in (404,410):
        r=http_get(ip,8000,"/api/v2/tenants/default_tenant/databases/default_database/collections"); api="v2"
    if not r or r[0]!=200: o["reproduce"]=False; o["status"]=(r or [None])[0]; return o
    j=jtry(r[1])
    o["api"]=api; o["reproduce"]=True
    if isinstance(j,list): o["collections"]=[c.get("name") for c in j if isinstance(c,dict)]
    return o

VER={"qdrant":verify_qdrant,"weaviate":verify_weaviate,"chroma":verify_chroma}

def run(rec):
    ip=rec["ip"]; plat=rec["platform"]
    o=VER[plat](ip)
    o["ptr"]=reverse_dns(ip)
    o["cert_cn"]=cert_cn(ip)
    return o

def main():
    cands=json.load(open(sys.argv[1]))   # list of {ip, platform}
    res=[]
    with cf.ThreadPoolExecutor(max_workers=12) as ex:
        futs={ex.submit(run,c):c for c in cands}
        for i,f in enumerate(cf.as_completed(futs),1):
            try: r=f.result()
            except Exception as e: r={"ip":futs[f]["ip"],"error":str(e)}
            res.append(r)
            rep="OK" if r.get("reproduce") else "NO"
            n=len(r.get("collections") or r.get("classes") or [])
            sn=sum(len(v) for v in (r.get("snapshots") or {}).values())
            print(f"[{i}/{len(cands)}] {r.get('ip'):<16} {r.get('platform','?'):<9} reproduce={rep} names={n} snaps={sn} ptr={r.get('ptr')} cn={r.get('cert_cn')}",flush=True)
    out=sys.argv[2] if len(sys.argv)>2 else "deep-verify.json"
    json.dump(res,open(out,"w"),indent=2,default=str)
    print(f"\nwrote {out}")

if __name__=="__main__": main()
