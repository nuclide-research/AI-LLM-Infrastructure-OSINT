# Contributing

Thanks for considering a contribution. This repository is meant to grow continuously, new platforms ship every week and the catalogue should keep up.

## What belongs here

**Yes:**
- Shodan, Censys, FOFA, ZoomEye, Hunter.how, Quake, Netlas queries for AI/ML platforms
- Google dorks and GitHub dorks for leaked AI provider keys, model files, training configs
- Nuclei templates that detect specific AI/ML services or misconfigurations
- Anonymized case studies of real-world exposures (with the affected party's data fully redacted)
- Defensive guides, how to harden a specific platform, expected security posture per category

**No:**
- Queries that target specific identified victims
- Working exploits against unpatched vulnerabilities (use a coordinator like CERT/CC)
- Stolen data, dumped credentials, or anything obtained without authorization
- Hot takes, opinion pieces, marketing for commercial products

## Query Quality Bar

Every query you submit should:

1. **Be verifiable**, you've actually run it and seen real results in the wild.
2. **Be specific**, `port:8000` alone is not a query. `"vLLM" port:8000` is.
3. **Include context**, when the query reveals something interesting (no auth, version disclosure, downloadable backups, default creds), put it in the `Notes` column.
4. **Avoid duplicates**, check the existing tables first. Different fingerprints for the same platform are fine; identical queries are not.

## How to add a query

1. Fork the repo.
2. Find the right category file under `shodan/queries/` (or `censys/`, `fofa/`, etc. once those are populated).
3. Add a new row to the appropriate Markdown table:
   ```markdown
   | `"YourPlatform" port:1234 "/some/path"` | Notes about what this reveals |
   ```
4. If the platform is brand new and doesn't fit, propose a new subsection in your PR.
5. Submit the PR with a one-line description: what platform, what query, what it shows.

## How to add a new category

Open an issue first. Categories should map to a class of AI/ML infrastructure (not a single product), and there should be at least 3-4 distinct platforms or services you intend to populate it with.

## Case Studies

Case studies of real exposures are welcome under `case-studies/` once that directory exists. **Strict rules:**

- The affected organization must be either (a) yours, (b) one that has publicly acknowledged the exposure, or (c) anonymized to the point where the org cannot be identified.
- No screenshots containing real data, IPs, hostnames, or identifying logos.
- Focus on the chain, what was exposed, why it mattered, what fixed it.
- If you reported through coordinated disclosure, link the CVE / advisory.

## Style

- Markdown tables with `Shodan Query` and `Notes` columns (or `Censys Query`, `FOFA Query`, etc.).
- Backtick all queries: `` `"Flowise" port:3000` ``.
- Italicize in `Notes` only when calling out a specific behavior (`*No auth confirmed*`, `*Pre-auth default era*`).
- Keep prose short. The catalogue is the value; the prose is connective tissue.

## Code of Conduct

Be useful. Be precise. Don't be a jerk in PR comments. Disagreements about whether a query belongs are resolved by the maintainer; appeals are welcome but final.

## Disclosure

If you find an exposed system using these queries, do **not** open a PR with the IP or hostname. Follow [DISCLAIMER.md](DISCLAIMER.md) and pursue coordinated disclosure with the affected party.
