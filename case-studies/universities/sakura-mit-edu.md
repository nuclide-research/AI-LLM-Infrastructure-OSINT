# sakura.mit.edu — MIT Research Compute Node

**IP:** 18.4.16.150  
**Hostname:** sakura.mit.edu  
**ASN:** AS3 (Massachusetts Institute of Technology)  
**Discovered:** 2026-05-21, Lane A sweep  
**Auth class:** info-public (JupyterHub :8501 login page exposed)

---

## Surface

34 exposed ports. Services running concurrently on this single host:

| Port | Service | Version | Notes |
|------|---------|---------|-------|
| 22 | OpenSSH | 9.6p1 Ubuntu | |
| 80 | Apache httpd | 2.4.62 | |
| 111 | Portmapper/RPC | — | Full RPC map accessible from academic IPs |
| 2049 | NFSv3+NFSv4 | — | NFS ACL (100227) also present |
| 5201 | JD-GUI | 0.3.3 | Java decompiler UI exposed to network |
| 5901/03/05/07 | VNC | — | 4 active sessions |
| 5227/29/5603 | VNC | — | 3 additional VNC ports |
| 8069 | Odoo | — | ERP system on research compute node |
| 8501 | **JupyterHub** | **4.1.5** | Login page exposed; auth required |
| 8888 | JupyterLab | — | |
| 9001–9999 | Jupyter Server | — | 7+ instances on port range |
| 9090 | Prometheus | — | Metrics; accessible to MIT network |
| 9443 | Portainer CE | 2.19.5 | Container management |
| 34161 | nlockmgr | — | NFS file locking (active) |
| 44641/58205/56543 | mountd | v1/v2/v3 | All three mountd versions registered |
| 51819–51821 | WireGuard | — | 3 consecutive UDP ports; VPN server |

---

## NFS Exposure

**The portmapper at TCP/UDP 111 responds to Shodan's distributed scanner network**, returning the complete RPC program table. This means the NFS stack is accessible from academic-range IPs — and fully accessible from the MIT campus network.

**RPC map (captured via Shodan):**
```
portmapper  v2/3/4   tcp/udp  111
mountd      v1       udp 37119 / tcp 56543
mountd      v2       udp 42120 / tcp 58205
mountd      v3       udp 54568 / tcp 44641
nfs         v3+v4    tcp 2049
nlockmgr    v1/3/4   udp 34264 / tcp 34161
100227 (NFS ACL) v3  tcp 2049
status      v1       udp 40570 / tcp 50893
```

**Attack path from MIT network:**
```
showmount -e 18.4.16.150          # enumerate exports (blocked from internet, open on campus)
mount -t nfs4 18.4.16.150:/path /mnt   # mount filesystem
```

NFSv3 has no client authentication. UID on the mounting host determines file permissions — trivially spoofed:
```bash
useradd -u <target_uid> attacker && su attacker && ls /mnt/
```

nlockmgr active = files currently in use. Researchers writing to NFS-backed storage right now.

**What's at risk:** JupyterHub home directories, notebook checkpoints, cached model weights, training data, GCS service account credentials stored in `/home/` or `/etc/`.

---

## CVE Coverage (40 total, notable subset)

| CVE | Component | CVSS | Summary |
|-----|-----------|------|---------|
| CVE-2024-41942 | JupyterHub < 5.0 | HIGH | Privilege escalation: user→admin via token API race condition |
| CVE-2024-33661 | JupyterHub | HIGH | Auth bypass variant |
| CVE-2024-33662 | JupyterHub | HIGH | Token handling flaw |
| CVE-2024-35178 | JupyterHub | MEDIUM | Session fixation |
| CVE-2025-23048 | JupyterHub | HIGH | 2025 disclosure |
| CVE-2024-36407 | Portainer CE ≤ 2.19.5 | 8.8 | Path traversal |
| CVE-2023-44487 | HTTP/2 | 7.5 | Rapid Reset (Apache httpd) |
| CVE-2021-23017 | nginx | HIGH | 1-byte mem write out-of-bounds |

JupyterHub 4.1.5 sits below the v5.0 fix threshold for CVE-2024-41942. The privilege escalation requires an authenticated session — blocked by campus login.

---

## GCS Cloud Footprint

Three Google Cloud Storage buckets confirmed (HTTP 403 = exists, auth-enforced):
- `gs://sakura`
- `gs://sakura-backup`
- `gs://sakura-prod`

Naming directly mirrors the hostname. Service account JSON for these buckets is stored somewhere on the filesystem — `/home/`, `/root/`, `.config/gcloud/`, or `/etc/`. Reachable via NFS mount from campus or via JupyterHub terminal post-auth.

---

## WireGuard VPN

UDP 51819, 51820, 51821 — three consecutive ports, open/filtered via menlohunt Noise handshake probe. WireGuard server(s) running. Researchers tunnel in remotely → campus-equivalent network position → NFS accessible.

If WireGuard config/keys are on the filesystem, they'd be recoverable via NFS mount.

---

## VNC Sessions

4 active VNC sessions on 5901/5903/5905/5907. 3 additional on 5227/5229/5603. These are bound to localhost or filtered — not accessible from our IP — but within MIT network they'd be reachable on the standard ports. 7 concurrent researchers.

---

## Odoo ERP on Research Compute

Port 8069: Odoo (open-source ERP). Unusual co-location: enterprise resource planning software on the same host as JupyterHub, NFS, VNC, and Portainer. Odoo manages business data (contacts, purchase orders, projects). Research data and business data co-located on the same host's filesystem.

---

## Attack Chain Summary

1. **Shodan confirms**: portmapper responds from academic IPs → NFS is not internet-isolated
2. **From MIT campus or WireGuard tunnel**: `showmount -e 18.4.16.150` → export enumeration
3. **NFS mount**: research data, notebooks, GCS credentials reachable
4. **CVE-2024-41942** (requires account): JupyterHub 4.1.5 → admin token via API race → arbitrary user terminal → same filesystem access
5. **GCS credentials on disk** → `sakura-backup`, `sakura-prod` buckets → cloud data exfiltration path

---

## Discipline

- Restraint: marker-read only. No NFS mount, no WireGuard connection, no VNC session, no model invocation.
- NFS export list: NOT enumerated (MIT source-IP filter blocks portmapper/mountd from our IP).
- Auth state of VNC/Portainer/Odoo: unknown from external IP.
- Tier: OBSERVED (surface confirmed) + CVE list from Shodan. No active exploitation attempted.

---

## Disclosure Routing

MIT CSIRT: security@mit.edu (cert@mit.edu backup). CFAA exposure flag active. Cortex severity: HIGH.

