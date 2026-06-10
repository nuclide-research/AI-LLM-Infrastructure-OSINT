#!/usr/bin/env python3
"""
yield-classifier.py — predict exposure-finding yield for an AI/ML category
before committing arsenal-chain wall-clock to it.

Why this exists: Cat-Tabby + Devstral 2026-06-09 burned ~2 hours surveying a
hardened (Tier-C) cohort when the user wanted exposure findings. The arsenal
chain executed cleanly; the category was simply wrong for the goal. This tool
fingerprints the category up-front so that mismatch is caught before Stage 0.

Inputs (read-only, stdlib only):
  - categories.yaml (same directory) — auditable source-of-truth
  - tome/platforms/*.json (optional, for ground-truth auth_default cross-check)

CLI surface:
  yield-classifier.py <slug>
  yield-classifier.py --top-n 5 --goal exposure
  yield-classifier.py --top-n 5 --goal thesis
  yield-classifier.py --audit
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

# ----------------------------------------------------------------------
# Paths
# ----------------------------------------------------------------------

HERE = Path(__file__).resolve().parent
CONFIG_PATH = HERE / "categories.yaml"
TOME_PLATFORMS = Path.home() / "tome" / "platforms"
COMMERCIAL_DIR = (
    HERE.parent.parent / "case-studies" / "commercial"
)  # AI-LLM-Infrastructure-OSINT/case-studies/commercial

# ----------------------------------------------------------------------
# Tier rule table — load-bearing semantics
# ----------------------------------------------------------------------

# Per-platform tier -> (exposure_weight, thesis_weight) on [0, 1]
# Exposure weight = how likely a population scan finds an open compute primitive.
# Thesis weight   = how likely the survey produces publishable auth-on-default evidence
#                   (negative results on Tier-C are publishable; so is positive on Tier-A).
TIER_WEIGHTS = {
    "A":   {"exposure": 0.95, "thesis": 0.80, "label": "EXPOSED-DOMINANT"},
    "A*":  {"exposure": 0.70, "thesis": 0.85, "label": "EXPOSURE-LIKELY"},
    "B":   {"exposure": 0.40, "thesis": 0.60, "label": "MIXED"},
    "C":   {"exposure": 0.05, "thesis": 0.75, "label": "NEGATIVE-RESULT-LIKELY"},
    "n/a": {"exposure": 0.00, "thesis": 0.00, "label": "OUT-OF-SCOPE"},
}

# Status modifiers: completed surveys do not need re-running for exposure goals.
STATUS_EXPOSURE_MULTIPLIER = {
    "not-yet":      1.00,
    "partial":      0.90,  # untouched dark-tier still possible
    "done":         0.10,  # already documented, low marginal yield
    "done-negative": 0.05,  # confirmed hardened
}

# Status modifiers for thesis-test goal: a category already done-negative is
# valuable as a confirmed data point but offers no new evidence.
STATUS_THESIS_MULTIPLIER = {
    "not-yet":      1.00,
    "partial":      0.95,
    "done":         0.20,
    "done-negative": 0.30,  # confirmed thesis support, but already published
}

# ----------------------------------------------------------------------
# Tiny YAML reader (stdlib only) — supports the subset used by categories.yaml
# ----------------------------------------------------------------------

def _strip_inline_comment(line: str) -> str:
    """Strip ' # comment' tail unless inside quotes/brackets."""
    in_quote = False
    quote_char = ""
    bracket_depth = 0
    out = []
    for i, ch in enumerate(line):
        if ch in ('"', "'") and not in_quote:
            in_quote = True
            quote_char = ch
        elif ch == quote_char and in_quote:
            in_quote = False
        elif ch in "[{" and not in_quote:
            bracket_depth += 1
        elif ch in "]}" and not in_quote:
            bracket_depth -= 1
        elif ch == "#" and not in_quote and bracket_depth == 0:
            # comment start
            return "".join(out).rstrip()
        out.append(ch)
    return "".join(out).rstrip()


def _parse_inline_value(val: str):
    """Parse an inline YAML scalar / flow-style mapping or list."""
    val = val.strip()
    if not val:
        return ""
    # Flow-style list
    if val.startswith("[") and val.endswith("]"):
        inner = val[1:-1].strip()
        if not inner:
            return []
        return [_parse_inline_value(x) for x in _split_flow(inner)]
    # Flow-style mapping
    if val.startswith("{") and val.endswith("}"):
        inner = val[1:-1].strip()
        result = {}
        for part in _split_flow(inner):
            if ":" not in part:
                continue
            k, v = part.split(":", 1)
            result[k.strip()] = _parse_inline_value(v.strip())
        return result
    # Quoted string
    if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
        return val[1:-1]
    # Number
    try:
        if "." not in val:
            return int(val)
        return float(val)
    except ValueError:
        pass
    # Bare scalar
    return val


def _split_flow(s: str):
    """Split a flow-style sequence respecting nested {}/[]/quotes."""
    parts, current, depth = [], [], 0
    in_quote, quote_char = False, ""
    for ch in s:
        if ch in ('"', "'") and not in_quote:
            in_quote = True
            quote_char = ch
            current.append(ch)
        elif ch == quote_char and in_quote:
            in_quote = False
            current.append(ch)
        elif ch in "[{" and not in_quote:
            depth += 1
            current.append(ch)
        elif ch in "]}" and not in_quote:
            depth -= 1
            current.append(ch)
        elif ch == "," and depth == 0 and not in_quote:
            parts.append("".join(current).strip())
            current = []
        else:
            current.append(ch)
    if current:
        parts.append("".join(current).strip())
    return parts


def load_yaml(path: Path) -> dict:
    """Parse the narrow YAML subset used by categories.yaml.

    Supports: top-level key, nested mappings (2-space indent), sequences of
    mappings starting with '- ', flow-style {k: v} list items, scalar values,
    and # comments. Refuses to grow into a general YAML parser by design —
    if categories.yaml gains exotic constructs, rewrite this fn or vendor PyYAML.
    """
    raw = path.read_text()
    lines = [_strip_inline_comment(ln).rstrip() for ln in raw.splitlines()]
    # Remove blank lines for index math, but track depths.
    root: dict = {}
    stack = [(-1, root)]  # (indent, container)
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        indent = len(line) - len(line.lstrip(" "))
        body = line.lstrip(" ")
        # Pop stack until parent indent < current indent
        while stack and stack[-1][0] >= indent:
            stack.pop()
        parent_indent, parent = stack[-1]

        if body.startswith("- "):
            # Sequence item
            item_body = body[2:].strip()
            if not isinstance(parent, list):
                # parent should be a list; if it's a dict whose last key value is missing list,
                # this is malformed for our schema. Skip.
                i += 1
                continue
            if not item_body:
                # nested mapping under list item, e.g.
                # -
                #   slug: foo
                new_item = {}
                parent.append(new_item)
                stack.append((indent, new_item))
            elif item_body.startswith("{") and item_body.endswith("}"):
                parent.append(_parse_inline_value(item_body))
            elif ":" in item_body and not item_body.startswith('"'):
                # inline first-key of a mapping item: "- slug: cat-tabby"
                key, _, val = item_body.partition(":")
                key = key.strip()
                val_stripped = val.strip()
                new_item = {}
                parent.append(new_item)
                if val_stripped == "":
                    new_item[key] = None
                    stack.append((indent, new_item))
                    # The key needs its own pending-value slot for further nesting.
                    # Push a marker so children at indent+2 attach to new_item[key].
                    stack.append((indent + 2 - 1, new_item))  # any deeper indent attaches to new_item
                    # Track pending key for sub-mapping/sub-list
                    new_item["__pending_key__"] = key
                else:
                    new_item[key] = _parse_inline_value(val_stripped)
                    stack.append((indent, new_item))
            else:
                parent.append(_parse_inline_value(item_body))
            i += 1
            continue

        # Mapping entry: key: value
        if ":" in body:
            key, _, val = body.partition(":")
            key = key.strip()
            val_stripped = val.strip()
            if isinstance(parent, dict) and "__pending_key__" in parent:
                # The previous list item had a pending key; this entry is a sibling at same indent
                pass
            if val_stripped == "":
                # Look ahead: next non-blank line determines list vs map
                j = i + 1
                while j < len(lines) and not lines[j].strip():
                    j += 1
                if j < len(lines):
                    next_line = lines[j]
                    next_indent = len(next_line) - len(next_line.lstrip(" "))
                    next_body = next_line.lstrip(" ")
                    if next_indent > indent and next_body.startswith("- "):
                        new_container = []
                    else:
                        new_container = {}
                else:
                    new_container = {}
                if isinstance(parent, dict):
                    parent[key] = new_container
                stack.append((indent, new_container))
            else:
                if isinstance(parent, dict):
                    parent[key] = _parse_inline_value(val_stripped)
            i += 1
            continue

        # Unknown line shape — skip
        i += 1

    # Clean pending markers
    def _clean(obj):
        if isinstance(obj, dict):
            obj.pop("__pending_key__", None)
            for v in obj.values():
                _clean(v)
        elif isinstance(obj, list):
            for v in obj:
                _clean(v)

    _clean(root)
    return root


# ----------------------------------------------------------------------
# Classifier
# ----------------------------------------------------------------------

def classify_category(cat: dict) -> dict:
    """Apply tier-rule scoring to a category record."""
    platforms = cat.get("platforms") or []
    status = cat.get("status", "not-yet")

    dist = {"A": 0, "A*": 0, "B": 0, "C": 0, "n/a": 0}
    for p in platforms:
        t = p.get("tier", "n/a")
        if t not in dist:
            t = "n/a"
        dist[t] += 1

    # Score = weighted-mean exposure across in-scope platforms, scaled by status.
    in_scope = [p for p in platforms if p.get("tier", "n/a") != "n/a"]
    if not in_scope:
        exposure_raw = 0.0
        thesis_raw = 0.0
        dominant_tier = "n/a"
    else:
        exposure_raw = sum(TIER_WEIGHTS[p["tier"]]["exposure"] for p in in_scope) / len(in_scope)
        thesis_raw = sum(TIER_WEIGHTS[p["tier"]]["thesis"] for p in in_scope) / len(in_scope)
        # Dominant tier = highest-yield tier present (A > A* > B > C)
        for t in ("A", "A*", "B", "C"):
            if dist[t] > 0:
                dominant_tier = t
                break
        else:
            dominant_tier = "n/a"

    exposure_score = exposure_raw * STATUS_EXPOSURE_MULTIPLIER.get(status, 1.0)
    thesis_score = thesis_raw * STATUS_THESIS_MULTIPLIER.get(status, 1.0)

    label = TIER_WEIGHTS.get(dominant_tier, TIER_WEIGHTS["n/a"])["label"]

    # Confidence: high when we have a clear tier majority and ground-truth backing.
    n = len(platforms)
    confidence = 0.65
    if n >= 3:
        confidence += 0.10
    if status in ("done", "done-negative"):
        confidence += 0.15
    confidence = min(confidence, 0.95)

    return {
        "tier_distribution": dist,
        "dominant_tier": dominant_tier,
        "yield_prediction": label,
        "exposure_score": round(exposure_score, 3),
        "thesis_score": round(thesis_score, 3),
        "confidence": round(confidence, 2),
        "status": status,
    }


def gather_evidence(slug: str, cat: dict) -> list[str]:
    """Cite case-study files + tome JSONs that back the call."""
    ev = []

    # 1. Case study filename heuristic — match the slug segment.
    if COMMERCIAL_DIR.exists():
        slug_token = slug.replace("cat-", "").split("-")[0]
        for f in sorted(COMMERCIAL_DIR.glob(f"*{slug_token}*.md"))[:2]:
            try:
                rel = f.relative_to(HERE.parent.parent)
            except ValueError:
                rel = f
            ev.append(f"case-studies/{rel.relative_to('case-studies') if 'case-studies' in str(rel) else f.name}")

    # Fallback: cite the exact slug as the case-study basename if it exists.
    direct = COMMERCIAL_DIR / f"{slug}-survey-2026-06-09.md"
    if direct.exists():
        ev.append(f"case-studies/commercial/{direct.name} backs the prediction")

    # 2. Tome platform ground-truth for each named platform.
    for p in cat.get("platforms") or []:
        name = p.get("name")
        tome_file = TOME_PLATFORMS / f"{name}.json"
        if tome_file.exists():
            try:
                data = json.loads(tome_file.read_text())
                auth_default = data.get("auth_default", "unknown")
                ev.append(
                    f"tome/platforms/{name}.json declares auth_default='{auth_default}' "
                    f"(tier={p.get('tier')})"
                )
            except (json.JSONDecodeError, OSError):
                pass

    # 3. Notes from the config itself.
    if cat.get("notes"):
        ev.append(f"categories.yaml notes: {cat['notes']}")

    return ev[:6]  # cap


def make_recommendation(prediction: str, status: str, goal: str | None = None) -> str:
    if status == "done-negative":
        return (
            "Pivot if user asked for exposure findings. Proceed if user explicitly "
            "wants thesis confirmation evidence (negative result is publishable)."
        )
    if status == "done":
        return (
            "Already surveyed. Re-run only for drift detection or new operator-tier sub-population. "
            "Otherwise pivot to a not-yet category."
        )
    if prediction == "EXPOSED-DOMINANT":
        return "Proceed — exposure-findings highly likely. Run full arsenal chain (Stages -1 through 13)."
    if prediction == "EXPOSURE-LIKELY":
        return "Proceed with verification discipline — auth-optional cohort produces mixed yield."
    if prediction == "NEGATIVE-RESULT-LIKELY":
        return (
            "Pivot if user asked for exposure findings. Proceed if user explicitly "
            "wants thesis confirmation evidence."
        )
    if prediction == "OUT-OF-SCOPE":
        return "Skip — CLI-only or no server-side surface. Redirect to upstream gateway population."
    return "Proceed with verification discipline."


def ksat_for(prediction: str) -> str:
    """Map prediction to DCWF KSAT framing."""
    if prediction in ("NEGATIVE-RESULT-LIKELY", "OUT-OF-SCOPE"):
        return "672 T0247 / 733 T5919 — falsifiable thesis test, publishable negative result"
    if prediction == "EXPOSED-DOMINANT":
        return "672 T5904 / 733 T5868 — population-scale exposure assessment, real-world impact"
    return "672 T5904 / 733 T5882 — mixed-cohort verification + responsible-AI practice"


def high_yield_alternatives(categories: list[dict], current_slug: str | None,
                            goal: str = "exposure") -> list[str]:
    """Surface top alternatives by score for the requested goal."""
    score_key = "exposure_score" if goal == "exposure" else "thesis_score"
    enriched = []
    for c in categories:
        if c.get("slug") == current_slug:
            continue
        cls = classify_category(c)
        enriched.append((cls[score_key], c, cls))
    enriched.sort(key=lambda x: x[0], reverse=True)
    out = []
    for score, c, cls in enriched[:5]:
        port_hint = ""
        if c.get("alt_ports"):
            port_hint = f" [ports: {','.join(str(p) for p in c['alt_ports'])}]"
        out.append(
            f"{c['slug']} ({cls['dominant_tier']}, score={score:.2f}, status={cls['status']})"
            f"{port_hint}"
        )
    return out


# ----------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------

def cmd_classify(slug: str, config: dict) -> int:
    cats = config.get("categories") or []
    cat = next((c for c in cats if c.get("slug") == slug), None)
    if cat is None:
        slugs = [c.get("slug") for c in cats]
        print(json.dumps({
            "error": f"unknown category slug: {slug}",
            "known_slugs_sample": slugs[:10],
            "hint": "edit categories.yaml to add coverage",
        }, indent=2))
        return 2

    cls = classify_category(cat)
    out = {
        "category": cat.get("slug"),
        "name": cat.get("name"),
        "tier_distribution": cls["tier_distribution"],
        "yield_prediction": cls["yield_prediction"],
        "exposure_score": cls["exposure_score"],
        "thesis_score": cls["thesis_score"],
        "confidence": cls["confidence"],
        "status": cls["status"],
        "evidence": gather_evidence(slug, cat),
        "recommendation": make_recommendation(cls["yield_prediction"], cls["status"]),
        "high_yield_alternatives": high_yield_alternatives(cats, slug, "exposure"),
        "ksat_alignment": ksat_for(cls["yield_prediction"]),
    }
    print(json.dumps(out, indent=2))
    return 0


def cmd_top_n(n: int, goal: str, config: dict) -> int:
    cats = config.get("categories") or []
    score_key = "exposure_score" if goal == "exposure" else "thesis_score"
    enriched = []
    for c in cats:
        cls = classify_category(c)
        enriched.append((cls[score_key], c, cls))
    enriched.sort(key=lambda x: x[0], reverse=True)
    out = {
        "goal": goal,
        "top_n": n,
        "results": [
            {
                "rank": i + 1,
                "slug": c.get("slug"),
                "name": c.get("name"),
                "yield_prediction": cls["yield_prediction"],
                "dominant_tier": cls["dominant_tier"],
                "exposure_score": cls["exposure_score"],
                "thesis_score": cls["thesis_score"],
                "status": cls["status"],
                "alt_ports": c.get("alt_ports") or [],
                "notes": c.get("notes", ""),
            }
            for i, (score, c, cls) in enumerate(enriched[:n])
        ],
    }
    print(json.dumps(out, indent=2))
    return 0


def cmd_audit(config: dict) -> int:
    cats = config.get("categories") or []
    warnings = []
    for c in cats:
        slug = c.get("slug", "<no-slug>")
        platforms = c.get("platforms") or []
        if not platforms:
            warnings.append(f"{slug}: no platforms declared")
            continue
        for p in platforms:
            if "tier" not in p:
                warnings.append(f"{slug}: platform '{p.get('name')}' missing tier annotation")
            elif p["tier"] not in TIER_WEIGHTS:
                warnings.append(f"{slug}: platform '{p.get('name')}' has unknown tier '{p['tier']}'")
        if "status" not in c:
            warnings.append(f"{slug}: missing status field")
        # Cross-check: known FUTURE-SURVEYS categories not yet in this config.
    futures_path = COMMERCIAL_DIR / "FUTURE-SURVEYS.md"
    coverage_gap = []
    if futures_path.exists():
        text = futures_path.read_text()
        # Heuristic: 'not-yet' rows in any table.
        for ln in text.splitlines():
            if "not-yet" in ln and "|" in ln:
                m = re.match(r"\|\s*\*\*([^|*]+)\*\*", ln)
                if m:
                    coverage_gap.append(m.group(1).strip())
    out = {
        "audited_categories": len(cats),
        "warnings": warnings,
        "future_surveys_not_yet_in_config_sample": sorted(set(coverage_gap))[:20],
        "advice": (
            "Update categories.yaml to bring uncovered platforms under classification. "
            "Tier annotations come from tome/platforms/<name>.json auth_default."
        ),
    }
    print(json.dumps(out, indent=2))
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Predict exposure-finding yield for an AI/ML category before "
            "committing arsenal-chain wall-clock to it."
        )
    )
    parser.add_argument("slug", nargs="?", help="category slug (e.g. cat-tabby)")
    parser.add_argument("--top-n", type=int, help="surface top-N candidates")
    parser.add_argument("--goal", choices=["exposure", "thesis"], default="exposure",
                        help="ranking objective (default: exposure)")
    parser.add_argument("--audit", action="store_true",
                        help="report categories missing tier annotations")
    args = parser.parse_args(argv)

    if not CONFIG_PATH.exists():
        print(json.dumps({"error": f"missing config: {CONFIG_PATH}"}, indent=2))
        return 2

    config = load_yaml(CONFIG_PATH)

    if args.audit:
        return cmd_audit(config)
    if args.top_n is not None:
        return cmd_top_n(args.top_n, args.goal, config)
    if args.slug:
        return cmd_classify(args.slug, config)

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
