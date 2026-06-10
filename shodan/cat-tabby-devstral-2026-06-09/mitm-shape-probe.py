#!/usr/bin/env python3
"""
Sandbox-MITM consistency probe.

NuClide methodology section 3: "Distrust your observation position."
recongraph + VisorGraph both run this check; if response shapes from
unrelated public IPs collapse to one digest, traffic is being rewritten
mid-stream and L7 conclusions get downgraded to OPAQUE.

T&E lane (DCWF 672) — Cat-Tabby + Devstral 2026-06-09 re-validation.
"""
from __future__ import annotations
import socket
import ssl
import hashlib
import json
import sys
import time
from dataclasses import dataclass, asdict


@dataclass
class Probe:
    label: str          # human label
    host: str           # SNI / Host header
    ip: str | None      # if None, resolve DNS once
    port: int
    path: str
    tls: bool


@dataclass
class Shape:
    label: str
    target: str
    path: str
    status: str
    header_keys: list[str]
    body_len: int
    body_head_b64: str
    shape_digest: str
    error: str | None = None


# Five UNRELATED public endpoints. Each control is a well-known
# public service designed to be probed. No survey-set hosts.
CONTROLS = [
    Probe("google-dns",   "dns.google",          "8.8.8.8",   443, "/",         True),
    Probe("cloudflare",   "one.one.one.one",     "1.1.1.1",   443, "/",         True),
    Probe("aws-s3",       "s3.amazonaws.com",    None,        443, "/",         True),
    Probe("github-api",   "api.github.com",      None,        443, "/",         True),
    Probe("example-org",  "example.org",         None,        443, "/",         True),
]

# The contaminated endpoint — same path that was poisoned at Stage 0.
# We send it to control hosts so the SHAPE comparison is on the SAME probe.
API_TAGS_PATH = "/api/tags"


def fetch_raw(p: Probe, path: str, timeout: float = 6.0) -> tuple[int | None, dict[str, str], bytes, str | None]:
    """Return (status, headers, body, error)."""
    try:
        ip = p.ip or socket.gethostbyname(p.host)
        raw = socket.create_connection((ip, p.port), timeout=timeout)
        if p.tls:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            sock = ctx.wrap_socket(raw, server_hostname=p.host)
        else:
            sock = raw
        req = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {p.host}\r\n"
            f"User-Agent: nuclide-mitm-probe/1.0\r\n"
            f"Accept: */*\r\n"
            f"Connection: close\r\n\r\n"
        ).encode()
        sock.sendall(req)
        chunks = []
        sock.settimeout(timeout)
        while True:
            try:
                b = sock.recv(8192)
            except (socket.timeout, ssl.SSLError):
                break
            if not b:
                break
            chunks.append(b)
            if sum(len(c) for c in chunks) > 64 * 1024:
                break
        sock.close()
        data = b"".join(chunks)
        # Split head/body
        sep = data.find(b"\r\n\r\n")
        if sep < 0:
            return None, {}, data, "no-header-sep"
        head = data[:sep].decode("iso-8859-1", errors="replace")
        body = data[sep + 4 :]
        lines = head.split("\r\n")
        status_line = lines[0] if lines else ""
        try:
            status = int(status_line.split()[1])
        except Exception:
            status = None
        headers = {}
        for line in lines[1:]:
            if ":" in line:
                k, v = line.split(":", 1)
                headers[k.strip().lower()] = v.strip()
        return status, headers, body, None
    except Exception as e:
        return None, {}, b"", f"{type(e).__name__}: {e}"


def shape_of(p: Probe, path: str) -> Shape:
    status, headers, body, err = fetch_raw(p, path)
    header_keys = sorted(headers.keys())
    # Normalize body length to nearest 64 bytes to absorb minor jitter,
    # but keep first 32 bytes raw — that's where rewrites tend to show.
    body_len = len(body)
    body_head = body[:32]
    canon = "|".join([
        str(status),
        ",".join(header_keys),
        str(body_len // 64),
        body_head.hex(),
    ])
    digest = hashlib.sha256(canon.encode()).hexdigest()[:16]
    target = f"{p.host}({p.ip or 'dns'})"
    import base64
    return Shape(
        label=p.label,
        target=target,
        path=path,
        status=str(status),
        header_keys=header_keys[:8],
        body_len=body_len,
        body_head_b64=base64.b64encode(body_head).decode(),
        shape_digest=digest,
        error=err,
    )


def run_consistency(label_suffix: str) -> dict:
    out = {"label": label_suffix, "root": [], "api_tags": []}
    for p in CONTROLS:
        out["root"].append(asdict(shape_of(p, "/")))
        out["api_tags"].append(asdict(shape_of(p, API_TAGS_PATH)))
    return out


def suspect_host_stability(host: str = "3.137.167.45", port: int = 11434, n: int = 3, gap: float = 15.0) -> list[dict]:
    p = Probe("suspect", host, host, port, API_TAGS_PATH, False)
    out = []
    for i in range(n):
        s = shape_of(p, API_TAGS_PATH)
        s_d = asdict(s)
        s_d["probe_idx"] = i
        s_d["t"] = time.time()
        out.append(s_d)
        if i < n - 1:
            time.sleep(gap)
    return out


def collapse_count(shapes: list[dict]) -> int:
    return len({s["shape_digest"] for s in shapes if s.get("status") not in (None, "None")})


if __name__ == "__main__":
    print("[*] Running sandbox-MITM consistency probe via current routing (VPN-on)")
    cur = run_consistency("vpn-on-current-routing")
    print(f"    root: {collapse_count(cur['root'])} unique shape(s) across {len(cur['root'])} controls")
    print(f"    api_tags: {collapse_count(cur['api_tags'])} unique shape(s) across {len(cur['api_tags'])} controls")

    print("[*] Pair-probing suspect host 3.137.167.45:11434 /api/tags x3 (15s gaps)")
    stab = suspect_host_stability()
    print(f"    suspect stability: {collapse_count(stab)} unique shape(s) across {len(stab)} probes")

    result = {
        "ts": time.time(),
        "routing": "vpn-on (Mullvad us-mia-wg-102, 146.70.187.101)",
        "current": cur,
        "suspect_stability": stab,
    }
    with open("mitm-shape-probe-results.json", "w") as f:
        json.dump(result, f, indent=2)
    print("[+] Wrote mitm-shape-probe-results.json")
