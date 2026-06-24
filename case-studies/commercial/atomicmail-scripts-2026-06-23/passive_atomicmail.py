#!/usr/bin/env python3
"""Passive recon: atomicmail.ai / 57.129.99.15 -- read-only, no auth"""
import urllib.request, ssl, socket
from cryptography import x509
from cryptography.hazmat.backends import default_backend

TARGET_IP = "57.129.99.15"
SUBDOMAINS = [
    "grafana", "api", "auth", "rspamd", "health",
    "webhooks", "www", "mta-sts", "mx1",
]

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


def https_get(path, subdomain):
    url = f"https://{TARGET_IP}{path}"
    req = urllib.request.Request(url)
    req.add_header("Host", f"{subdomain}.atomicmail.ai")
    req.add_header("User-Agent", "Mozilla/5.0")
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=8) as r:
            return r.status, r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:
        return None, str(e)


print("=== Grafana health (version leak -- unauthenticated by design) ===")
code, body = https_get("/api/health", "grafana")
print(f"[grafana /api/health] {code}: {body.strip()}")

print("\n=== TLS cert SAN enumeration ===")
with socket.create_connection((TARGET_IP, 443), timeout=8) as sock:
    with ctx.wrap_socket(sock, server_hostname="grafana.atomicmail.ai") as ssock:
        der = ssock.getpeercert(binary_form=True)
cert = x509.load_der_x509_certificate(der, default_backend())
san = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
print(f"[TLS SANs] {san.value.get_values_for_type(x509.DNSName)}")
print(f"[TLS expiry] {cert.not_valid_after_utc}")
print(f"[TLS subject] {cert.subject.rfc4514_string()}")
print(f"[TLS issuer]  {cert.issuer.rfc4514_string()}")

print("\n=== Subdomain HTTP sweep ===")
for sub in SUBDOMAINS:
    code, _ = https_get("/", sub)
    print(f"[{sub}.atomicmail.ai /] {code}")

print("\n=== rspamd API auth gate ===")
for ep in ["/stat", "/auth", "/maps"]:
    code, body = https_get(ep, "rspamd")
    print(f"[rspamd {ep}] {code}: {body[:80].strip()}")

print("\n=== Grafana auth gate ===")
for ep in ["/api/org", "/api/frontend/settings"]:
    code, body = https_get(ep, "grafana")
    print(f"[grafana {ep}] {code}: {body[:80].strip()}")
