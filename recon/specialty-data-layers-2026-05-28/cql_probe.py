import socket, struct, sys, json, os

def probe_cql(ip, port=9042, timeout=5):
    try:
        s = socket.create_connection((ip, port), timeout=timeout)
        # Send OPTIONS (opcode 0x05)
        s.sendall(b"\x04\x00\x00\x00\x05\x00\x00\x00\x00")
        hdr = s.recv(9)
        if len(hdr) < 9:
            return {"ip": ip, "status": "no_response"}
        version, flags, stream, opcode, length = struct.unpack(">BBhBI", hdr)
        body = s.recv(min(length, 4096)) if length > 0 else b""
        is_scylla = b"SCYLLA" in body or b"scylla" in body
        # Send STARTUP
        startup_body = b'\x00\x01\x00\x0bCQL_VERSION\x00\x053.0.0'
        startup_len = len(startup_body)
        s.sendall(struct.pack(">BBhBI", 0x04, 0x00, 0x01, 0x01, startup_len) + startup_body)
        resp_hdr = s.recv(9)
        if len(resp_hdr) < 9:
            return {"ip": ip, "status": "no_startup_response", "scylla": is_scylla}
        _, _, _, resp_opcode, _ = struct.unpack(">BBhBI", resp_hdr)
        auth_state = "OPEN" if resp_opcode == 0x02 else "AUTH_REQUIRED" if resp_opcode == 0x03 else f"OPCODE_{hex(resp_opcode)}"
        s.close()
        return {"ip": ip, "status": auth_state, "scylla": is_scylla, "cql_version": version & 0x7f}
    except Exception as e:
        return {"ip": ip, "status": "error", "error": str(e)[:60]}

home = os.path.expanduser('~')
ips = open(f'{home}/AI-LLM-Infrastructure-OSINT/recon/specialty-data-layers-2026-05-28/cassandra-ips.txt').read().split()
results = [probe_cql(ip) for ip in ips]
open_instances = [r for r in results if r.get('status') == 'OPEN']
auth_instances = [r for r in results if r.get('status') == 'AUTH_REQUIRED']
scylla_instances = [r for r in results if r.get('scylla')]
error_count = len([r for r in results if 'error' in r.get('status','')]) + len([r for r in results if r.get('status') == 'no_response'])

print(f"Total probed: {len(results)}")
print(f"OPEN (no auth): {len(open_instances)}")
print(f"AUTH_REQUIRED: {len(auth_instances)}")
print(f"ScyllaDB detected: {len(scylla_instances)}")
print(f"Errors/timeout: {error_count}")
print(f"Open instances: {[r['ip'] for r in open_instances]}")
print(f"ScyllaDB IPs: {[r['ip'] for r in scylla_instances]}")

out_path = f'{home}/AI-LLM-Infrastructure-OSINT/recon/specialty-data-layers-2026-05-28/cassandra-cql-probe.json'
open(out_path, 'w').write(json.dumps(results, indent=2))
print(f"Results written to {out_path}")
