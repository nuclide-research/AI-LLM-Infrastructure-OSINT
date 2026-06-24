# X post — 66-host HK Meilisearch botnet (2026-06-08)

## Option A — Single tweet (267 chars)

```
66-host SEO content-spam fleet running unauthenticated Meilisearch on Alibaba Cloud Hong Kong.

6,402 fake-article indexes, one per brand domain. Same shape across every node.

Operator identified entirely from index names. No records read.

Names are the finding.
```

## Option B — Thread (4 tweets)

### 1/4 — the headline

```
A 66-host SEO content-spam fleet runs unauthenticated Meilisearch on Alibaba Cloud Hong Kong.

6,402 fake-article search backends across 66 nodes. Same per-tenant naming shape per host.

We identified the operator entirely from index names. No records read.

Names are the finding.
```

### 2/4 — the mechanism

```
The cluster lives at 177.210.106.x. Each host runs the same 97 Meilisearch indexes, each named articles_<brand-domain>_com.

The /stats endpoint returns index names without authentication. That alone fingerprints the operator, the per-tenant shape, and the full domain inventory.

No exploit. No record reads. Just the platform's documented metadata.
```

### 3/4 — the context

```
This came from a same-day population sweep across three AI-infra platforms.

ComfyUI: 186 unauth on default port, 6.6 TB VRAM exposed (re-measurement of Censys ARC's April GHOST surface; 3 likely-GHOST hosts handed off).

Meilisearch: 282 unauth, 780 GB exposed.

Marqo: 4 of 4 LIVE unauth.
```

### 4/4 — the methodology contribution

```
Across the four AI platforms we have current data on, the unauth rate tracks deploy-time auth friction:

Langfuse (forced):                 ~0%
Meilisearch (env var, doc-foregrounded):  ~10%
Phoenix (env var, not foregrounded):  ~25%
ComfyUI (no auth concept):        ~78%

Full write-ups: github.com/nuclide-research/AI-LLM-Infrastructure-OSINT
```

## Notes on voice

- No em dashes (top-priority rule).
- Single-clause news-headline copy; no two-beat reveals.
- "We" and "NuClide" not "I."
- "Names are the finding" is the doctrine line. Keep it as the kicker.
- No emojis.
- Numbers carry the weight; resist the urge to gloss them.
