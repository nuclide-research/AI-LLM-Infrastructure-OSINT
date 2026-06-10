#!/usr/bin/env python3
"""Wrapper to run Cisco MCP scanner with TLS verify off (self-signed customer certs)."""
import ssl
import sys

# Monkeypatch BEFORE the scanner imports httpx/anyio
_orig_create = ssl.create_default_context
def _perm(*a, **kw):
    ctx = _orig_create(*a, **kw)
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx
ssl.create_default_context = _perm
ssl._create_default_https_context = ssl._create_unverified_context

# httpx env override
import os
os.environ["SSL_CERT_FILE"] = ""
os.environ["CURL_CA_BUNDLE"] = ""

# Also patch httpx if available
try:
    import httpx
    _orig_init = httpx.AsyncClient.__init__
    def _patched(self, *args, **kwargs):
        kwargs.setdefault("verify", False)
        return _orig_init(self, *args, **kwargs)
    httpx.AsyncClient.__init__ = _patched
    _orig_init_s = httpx.Client.__init__
    def _patched_s(self, *args, **kwargs):
        kwargs.setdefault("verify", False)
        return _orig_init_s(self, *args, **kwargs)
    httpx.Client.__init__ = _patched_s
except ImportError:
    pass

sys.argv = [
    "mcp-scanner",
    "--analyzers", "yara",
    "--format", "detailed",
    "--output", "cisco-scanner-3.137.167.45.json",
    "remote", "--server-url", "https://3.137.167.45:9090/mcp",
]
from mcpscanner.cli import cli_entry_point
cli_entry_point()
