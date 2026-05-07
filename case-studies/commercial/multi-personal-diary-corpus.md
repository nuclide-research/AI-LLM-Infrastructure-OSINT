# Multi-Tenant Personal Document SaaS: Diary, Theater Scripts, Philosophy via Unauth ChromaDB

_NuClide Research · 2026-05-03_

---

## Summary

A ChromaDB instance on a DigitalOcean VPS exposes three CUID-named collections (`corpus_cln*`) representing the personal document corpora of three users on what appears to be a multi-tenant document-RAG SaaS. The contents range from a user's personal alcohol-cessation diary (GDPR Article 9 special-category health data), to creative theater scripts naming real authors with email addresses and Belgian phone numbers, to a public-domain philosophical text (Nietzsche's *Beyond Good and Evil*). All readable without authentication on port 8000.

The CUID format (`cln4mq3w4000rka2lyt792a32`) is the Prisma-generated "collision-resistant unique ID", a strong indicator of a Node/Prisma SaaS where each user's documents are stored in a private ChromaDB collection named by their generated user ID. This is a structural multi-tenant exposure: every user's collection is enumerable, and the collection-naming convention reveals the platform's underlying user-ID schema.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 188.166.71.44 |
| Hosting | DigitalOcean |
| Port | 8000 (HTTP, no auth) |
| ChromaDB version | 0.4.13 (v1 API) |
| Tenant / DB | (v1, no tenant model) |
| Discovery date | 2026-05-03 |
| User-ID convention | Prisma CUID (`cln*` prefix denotes 2023+ generation) |

---

## Collections

| Collection | Docs | Content class |
|---|---|---|
| `corpus_cln4mq3w4000rka2lyt792a32` | 1,487 | Personal diary (alcohol cessation log, French) |
| `corpus_cln2zh86b0001p82knhrr7hlk` | 643 | Nietzsche, *Beyond Good and Evil* (public domain, French translation) |
| `corpus_cln2yf6py0001mp2kk7t63amf` | 68 | Theater scripts with named authors + email + Belgian phone numbers |

---

## Findings

### F1: GDPR Article 9 Special-Category Data: Health-Related Personal Diary (HIGH)

`corpus_cln4mq3w4000rka2lyt792a32` contains chronological French-language entries reading as a personal diary. The opening sample:

```
18/04/22: arrêt de l'alcool.
18/06/22: bu Orval 3° (édition spéciale à l'Abbaye)
```

Translation: *"04/18/22: stopped drinking alcohol. 06/18/22: drank Orval 3° (special abbey edition)."*

The entry is recovery-related health context. Under GDPR Article 9(1), "data concerning health" is special-category data with a higher protection threshold than ordinary personal data. The user has stored 1,487 chronological entries, which at the rate of one per day implies a multi-year log. The full dataset likely contains a detailed personal narrative including health, mental state, relationships, and other sensitive disclosures.

**Risk:** This is the most sensitive class of finding in the survey, direct GDPR Article 9 special-category data exposed unauth, with the user's CUID providing pseudonymous attribution.

### F2: Real Names + Emails + Phone Numbers in Creative IP (HIGH)

`corpus_cln2yf6py0001mp2kk7t63amf` contains theater scripts with credentialing identifiable individuals:

```
LES FORMES VIDES - LE THÉÂTRE DE LA VACUITÉ
Sébastien Lacomblez
sebastien.lacomblez@gmail.com
0497/75.31.02
Emmanuel Pire
piremmanuel@gmail.com
0486/77.69.87
```

Belgian mobile prefixes (0497, 0486) and `.gmail.com` addresses confirm contact details for two named individuals, likely the script's authors or contributors. While the creative work itself is not GDPR special-category, the contact data is straightforward personal data subject to GDPR Article 6 / Article 14 (right to know data is processed) obligations.

**Risk:** Real authors' direct contact channels are exposed alongside their unpublished creative work. An attacker could spear-phish the authors using the script content as the social-engineering hook; an opportunistic harvester could spam-list these addresses.

### F3: Public-Domain Content Mixed With User Data (MEDIUM)

`corpus_cln2zh86b0001p82knhrr7hlk` contains the French text of Friedrich Nietzsche's *Par delà le bien et le mal* (*Beyond Good and Evil*), 1913 Mercure de France edition, sourced from Wikisource. This is public-domain content and not directly sensitive, but its presence signals the platform's typical use case: a personal-document RAG where users upload their own materials (creative work, journal entries) plus reference texts they want to query against.

**Implication:** Other users' collections, not sampled in this survey, are likely to follow the same pattern (mixed personal + reference content), with a similar mix of severity classes.

### F4: CUID Naming Reveals Platform's User-ID Schema (HIGH)

The `cln*` CUID prefix encodes a timestamp from late 2023 onward (CUID v2 / Prisma's standard implementation). Each collection's CUID is a direct reference to a user record in the platform's relational database. An attacker can:

1. Enumerate all user CUIDs by listing ChromaDB collections
2. Map each CUID to the corresponding user record if the platform's user-API exposes endpoints like `/api/users/<cuid>`
3. Pivot between document content and user identity at scale

This is a structural exposure: the multi-tenant SaaS chose to use the user's CUID as the collection name, defeating the abstraction layer that would otherwise hide internal user IDs from leaked database content.

### F5: v1 API Indicates Older Stack (LOW informational)

ChromaDB 0.4.13 uses the v1 API path. v1 has been deprecated for v2 since ChromaDB 0.5.x; this operator has not upgraded. The relevance is forensic: this operator's deployment is older than the surrounding 1.0.x population, suggesting either a legacy environment or a low-maintenance hobbyist deployment. Either way, the operator is unlikely to be running auth on a system this far behind upstream.

### F6: Root Cause: Default-Off Auth (CRITICAL)

ChromaDB 0.4.13 unauthenticated, port 8000 on the public internet, no firewall. v1 collections by name (not UUID), easy to enumerate.

---

## Remediation

### Immediate

```bash
# v1 API auth via env (older ChromaDB)
CHROMA_SERVER_AUTHN_PROVIDER=chromadb.auth.token_authn.TokenAuthenticationServerProvider
CHROMA_SERVER_AUTHN_CREDENTIALS=<strong-token>
CHROMA_AUTH_TOKEN_TRANSPORT_HEADER=X-Chroma-Token
```

Firewall port 8000 to the application backend only.

### Architectural: fixing the structural exposure

1. **Stop using user-CUID as collection name.** Use a single collection per data class with `user_id` in document metadata; query with `where={"user_id": <id>}`. Even if the DB is again exposed, listing collections no longer enumerates users.
2. **Encrypt content at write-time.** A per-user envelope key derived from a server-side master key and the user's authenticated context. ChromaDB stores ciphertext; the embedding is over the plaintext but stored as a vector, the actual plaintext document is recoverable only with the user's session.
3. **Upgrade ChromaDB.** 0.4.13 is well behind 1.0.x. The newer release ships v2 API with collection-by-UUID semantics that mitigates collection-name enumeration.

### Notification

The diary-content user (collection `cln4mq3w*`) is the primary breach subject. Under GDPR Article 33, the operator has a 72-hour notification obligation to their lead supervisory authority once they reasonably know about the breach. Article 34 may require notifying the affected user directly. The Belgian phone numbers in the theater script collection suggest a Belgian or France-based user base; if the operator is established in EU, the relevant DPA is determined by establishment.

---

## Disclosure

- **Discovered:** 2026-05-03
- **Status:** Pending, operator unknown, no domain attribution from IP alone
- **Outreach plan:** Reverse-DNS lookup, TLS-cert SAN check on adjacent ports, and Prisma-style platform identification before initiating contact. The CUID-named ChromaDB pattern is distinctive enough that operator identification via Prisma SaaS user feedback or Stack Overflow questions may be possible.
