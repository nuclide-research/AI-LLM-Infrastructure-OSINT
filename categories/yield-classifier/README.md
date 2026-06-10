# yield-classifier

Predict exposure-finding yield for any AI/ML category **before** committing
arsenal-chain wall-clock to it.

## Why this exists

Cat-Tabby + Devstral 2026-06-09 burned ~2 hours surveying a hardened (Tier-C)
cohort when the goal was exposure findings. The arsenal chain executed cleanly;
the category was simply wrong for the goal. This tool fingerprints the category
up front so that mismatch is caught before Stage 0.

## What it does

Reads `categories.yaml` (auditable source-of-truth) + `~/tome/platforms/*.json`
(ground-truth `auth_default`), applies tier-rule scoring, and outputs a
yield prediction with confidence, evidence citations, recommendation, and
high-yield alternatives.

No network probes. Pure stdlib. Reads files, writes JSON to stdout.

## Install

```
chmod +x yield-classifier.py
```

Python 3.10+. No external dependencies.

## Usage

### Classify one category

```
./yield-classifier.py cat-tabby
```

Outputs JSON with:

- `yield_prediction` (EXPOSED-DOMINANT / EXPOSURE-LIKELY / MIXED / NEGATIVE-RESULT-LIKELY / OUT-OF-SCOPE)
- `tier_distribution` (count of A / A* / B / C / n/a platforms)
- `exposure_score` and `thesis_score` on [0, 1]
- `confidence` on [0, 1]
- `evidence` (case-study filenames + tome JSON cross-checks)
- `recommendation` (proceed / pivot / skip)
- `high_yield_alternatives` (top-5 by exposure score)
- `ksat_alignment` (DCWF KSAT framing)

### Surface top-N candidates by goal

```
./yield-classifier.py --top-n 5 --goal exposure
./yield-classifier.py --top-n 5 --goal thesis
```

Use **exposure** when the operator wants new findings. Use **thesis** when the
operator wants publishable auth-on-default evidence (positive or negative).

### Audit coverage

```
./yield-classifier.py --audit
```

Reports any category in `categories.yaml` missing tier annotations, plus a
sample of `FUTURE-SURVEYS.md` rows still marked `not-yet` and not yet in
`categories.yaml`.

## Tier vocabulary

The load-bearing semantics of `categories.yaml`. Edit `categories.yaml` to add
coverage; do not invent new tiers without updating `TIER_WEIGHTS` in
`yield-classifier.py`.

| Tier  | Meaning                                 | Yield prediction         | Examples                                           |
|-------|------------------------------------------|--------------------------|----------------------------------------------------|
| **A**   | No auth concept (open by design)       | EXPOSED-DOMINANT         | Ollama, Phoenix, Prometheus, ROS master, ComfyUI   |
| **A***  | Auth optional, off by default          | EXPOSURE-LIKELY          | Weaviate, ClearML (older), LiteLLM, Helicone       |
| **B**   | Setup wizard or version-load-bearing   | MIXED                    | older Postgres, fixed-by-default configurations    |
| **C**   | Auth on by default                     | NEGATIVE-RESULT-LIKELY   | Langfuse, Tabby v0.11.0+, Sourcegraph Cody         |
| **n/a** | CLI-only / no server-side surface      | OUT-OF-SCOPE             | Devstral (model not server), Continue.dev (CLI)    |

## Status modifiers

The status field in `categories.yaml` discounts the raw tier score:

| Status         | Exposure multiplier | Thesis multiplier |
|----------------|---------------------|-------------------|
| `not-yet`      | 1.00                | 1.00              |
| `partial`      | 0.90                | 0.95              |
| `done`         | 0.10                | 0.20              |
| `done-negative`| 0.05                | 0.30              |

`done-negative` is a confirmed thesis data point — it remains useful for citation
but offers near-zero new evidence.

## How to update `categories.yaml`

When a new category gets surveyed or a new platform shows up in
`~/tome/platforms/`:

1. Add an entry (or new platform under an existing entry) to `categories.yaml`.
   Schema:

   ```yaml
   - slug: cat-newthing
     name: "Cat-XX — Human label"
     status: not-yet | partial | done | done-negative
     platforms:
       - {name: platform-slug, tier: A | A* | B | C | n/a}
     notes: "one-line headline finding or rationale"
     alt_ports: [optional, list, of, Shodan-dark, ports]
   ```

2. Cross-check the tier against `~/tome/platforms/<name>.json` →
   `auth_default`. Mapping:

   - `none` / `not-required` / `optional-off` → **A** or **A***
   - `optional-but-recommended` / `mixed` (version-load-bearing) → **B** or **C**
   - `required` / `auth-on-default` → **C**
   - `n/a-no-server` / `inherited-from-serving-stack` → **n/a**

3. Run `./yield-classifier.py --audit` — it should report your new category
   under `audited_categories` with no `warnings`.

4. Run `./yield-classifier.py <new-slug>` to confirm the prediction reads
   sensibly. Sanity rule of thumb: a brand-new Tier-A `not-yet` should land
   `EXPOSED-DOMINANT` with exposure_score ≥ 0.90.

## Limits

- The classifier scores tier distributions, not realities. A Tier-A category
  ranking at the top still needs the full arsenal chain to verify findings.
- A category marked `done-negative` will rank low for exposure but is a strong
  thesis data point — read the recommendation field, not just the score.
- Tier annotations are operator judgement, anchored to `tome/platforms/*.json`
  ground truth. When tome and FUTURE-SURVEYS.md disagree, tome wins.
- `notes` is human-curated. Keep it to one line, headline finding only.

## DCWF KSAT framing

The `ksat_alignment` field maps the prediction to the DCWF AI work-role
vocabulary:

- **NEGATIVE-RESULT-LIKELY / OUT-OF-SCOPE** → 672 T0247 / 733 T5919
  (falsifiable thesis test, publishable negative result)
- **EXPOSED-DOMINANT** → 672 T5904 / 733 T5868
  (population-scale exposure assessment, real-world impact)
- **EXPOSURE-LIKELY / MIXED** → 672 T5904 / 733 T5882
  (mixed-cohort verification + responsible-AI practice)

## Files

- `yield-classifier.py` — the CLI tool
- `categories.yaml` — auditable source-of-truth, edit freely
- `README.md` — this file
