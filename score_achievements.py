"""
Score each SNS JU 2025 key achievement against stop6g.eu threat categories,
then inject the scored data into the HTML template so the result is a single
self-contained file you can open directly in a browser.

Usage:
    python3 score_achievements.py

Inputs:
    ../key_achievements_2025.csv      (produced by ../fetch_key_achievements.py)
    ../projects_summarized_en.csv     (project budgets + coordinators, hand-curated)
    ./template.html                   (UI shell with __DATA_JSON__ placeholder)

Outputs:
    ./key_achievements_2025_scored.json   (raw scored data, for inspection)
    ./threat_scanner.html                 (self-contained, double-click to open)

Tune SCORING_RULES below to change which categories trigger.
Each matched category adds 1 to the danger_score (range 0–8).

(SCORING_WEIGHTS support is kept commented out at the bottom of the file
in case you want weighted scoring later — set USE_WEIGHTS = True.)
"""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent

INPUT_CSV = ROOT / "key_achievements_2025.csv"
PROJECTS_CSV = ROOT / "projects_summarized_en.csv"
TEMPLATE = HERE / "template.html"
OUT_JSON = HERE / "key_achievements_2025_scored.json"
OUT_HTML = HERE / "threat_scanner.html"

# --------------------------------------------------------------------------
# SCORING RULES — edit these freely, then re-run the script.
#
# Each category can use:
#   "any":     list of plain substrings to match (case-insensitive)
#   "regex":   list of regex patterns (case-insensitive, re.IGNORECASE)
#   "exclude": list of regex patterns; if any matches, the WHOLE category
#              is skipped for that achievement (used to suppress false
#              positives — e.g. don't trigger "Zero Trust" on plain "trusted")
#
# A category counts as triggered if at least one "any" substring OR one
# "regex" pattern matches AND no "exclude" pattern matches.
# --------------------------------------------------------------------------
SCORING_RULES: dict[str, dict[str, list[str]]] = {
    "ISAC / Sensing": {
        "any": [
            "isac", "jcas",
            "integrated sensing", "joint sensing", "joint communication and sensing",
            "radar", "passive sensing", "sensing-aided",
            "localization", "localisation", "positioning",
            "environment sensing", "environment perception",
            "obstacle detection", "target detection",
        ],
    },
    "Digital Twin": {
        # Only match "twin" when it's clearly the network/digital kind.
        # This avoids false positives on stray "twin" mentions.
        "regex": [
            r"\bdigital\s+twin",
            r"\bnetwork\s+twin",
            r"\bnetwork\s+digital\s+twin",
            r"\bndt\b",
            r"\bdiffrt\b",            # differentiable ray-tracing — digital-twin tech
        ],
    },
    "AI Predictive": {
        "any": [
            "ai/ml", "ai-native", "machine learning", "deep learning",
            "neural network", "federated learning",
            "predict", "anomaly detection",
            "behaviour profil", "behavior profil",
            "llm", "large language model",
            "explainable ai", "xai",
            # narrow "inference" to AI contexts so we don't match Bayesian /
            # statistical inference in non-ML signal-processing papers
            "ai inference", "ml inference", "model inference",
        ],
        "exclude": [
            r"\bpredictable\b",   # "predictable transport" ≠ predictive AI
        ],
    },
    "Zero Trust": {
        # Require the *concept* of identity/trust controls — not the word "trust"
        # in "trusted environment" or "trustworthy."
        "any": [
            "zero trust", "zero-trust",
            "biometric", "identity management",
            "authentication", "authorisation", "authorization",
            "access control",
        ],
        "regex": [
            r"\bzero[\s-]?touch\s+(?:security|trust)",
        ],
    },
    "High-frequency": {
        "any": [
            "high-frequency", "high frequency",
            "thz", "terahertz", "sub-thz", "sub-terahertz",
            "mmwave", "mm-wave", "millimeter wave", "millimetre wave",
            "26 ghz", "60 ghz", "ghz band",
        ],
    },
    "Surveillance / PPDR": {
        "any": [
            "ppdr",
            "emergency services", "first responder", "first-responder",
            "surveillance", "law enforcement", "public safety",
            "crowd monitor", "crowd analytics",
            "smart city", "smart-city",
            "border control",
        ],
    },
    "Edge / Cloud": {
        "any": [
            "edge computing", "edge cloud",
            "cloud-native", "cloud native",
            "mec ", "multi-access edge",
            "computing continuum", "device-edge-cloud",
            "edge-cloud", "edge offload",
        ],
    },
    "NTN / Satellite": {
        "any": [
            "ntn", "non-terrestrial",
            "satellite",
            "haps", "high altitude platform",
            "leo ", "low earth orbit", "low-earth-orbit",
            "mega-constellation", "megaconstellation",
            "constellation",
        ],
    },
}


# Weighted scoring: not every category is equally on-topic for stop6g.
# Core threats (passive surveillance / identity gating) get weight 2.0;
# force-multipliers 1.5; enabling infra 1.0; generic infra 0.5.
USE_WEIGHTS = True
SCORING_WEIGHTS: dict[str, float] = {
    "ISAC / Sensing": 2.0, "Digital Twin": 2.0, "Zero Trust": 2.0,
    "AI Predictive": 1.5, "Surveillance / PPDR": 1.5,
    "High-frequency": 1.0, "NTN / Satellite": 1.0, "Edge / Cloud": 0.5,
}


# Map score → integer level (0–5) used for UI color + label.
# Thresholds differ for weighted (0–11.5) vs flat (0–8) scoring.
def bucket(score: float) -> tuple[int, str]:
    if USE_WEIGHTS:
        if score >= 5.0:  return (5, "CRITICAL")
        if score >= 3.5:  return (4, "HIGH")
        if score >= 2.0:  return (3, "MED")
        if score >= 1.0:  return (2, "LOW")
        if score > 0:     return (1, "TRACE")
        return (0, "CLEAR")
    # Flat-scoring thresholds
    if score >= 5:    return (5, "CRITICAL")
    if score >= 4:    return (4, "HIGH")
    if score >= 3:    return (3, "MED")
    if score >= 2:    return (2, "LOW")
    if score > 0:     return (1, "TRACE")
    return (0, "CLEAR")


def score_text(text: str) -> tuple[float, int, str, list[str], dict[str, list[str]]]:
    """Return (danger_score, level_int, level_label, triggered_tags, matches)."""
    lower = text.lower()
    triggered: list[str] = []
    matches: dict[str, list[str]] = {}

    for tag, rules in SCORING_RULES.items():
        # check excludes first
        excludes = rules.get("exclude", [])
        if any(re.search(pat, lower, flags=re.IGNORECASE) for pat in excludes):
            continue

        hits: list[str] = []
        for word in rules.get("any", []):
            if word.lower() in lower:
                hits.append(word)
        for pat in rules.get("regex", []):
            m = re.findall(pat, lower, flags=re.IGNORECASE)
            if m:
                hits.append(f"/{pat}/")

        if hits:
            triggered.append(tag)
            seen = set()
            matches[tag] = [h for h in hits if not (h in seen or seen.add(h))]

    if USE_WEIGHTS:
        raw = sum(SCORING_WEIGHTS.get(t, 1.0) for t in triggered)
    else:
        raw = float(len(triggered))   # flat count, 0–8
    level, label = bucket(raw)
    return round(raw, 1), level, label, triggered, matches


def load_project_index() -> dict[str, dict]:
    """Map normalised acronym -> {grant_eur, coordinator, year} from CSV_en."""
    index: dict[str, dict] = {}
    if not PROJECTS_CSV.exists():
        print(f"WARN: {PROJECTS_CSV} not found — cards won't show grant/coordinator.",
              file=sys.stderr)
        return index
    with PROJECTS_CSV.open(encoding="utf-8-sig") as f:
        for r in csv.DictReader(f, delimiter=";"):
            acro = (r.get("Acronym") or "").strip()
            if not acro:
                continue
            try:
                grant = float(r.get("Total Grant (€)") or 0)
            except ValueError:
                grant = 0.0
            index[acro.lower()] = {
                "grant_eur": grant,
                "coordinator": (r.get("Coordinator") or "").strip(),
                "year": (r.get("Year") or "").strip(),
            }
    return index


def main() -> int:
    if not INPUT_CSV.exists():
        print(f"ERROR: input not found: {INPUT_CSV}", file=sys.stderr)
        print("Run ../fetch_key_achievements.py first to produce the CSV.", file=sys.stderr)
        return 1
    if not TEMPLATE.exists():
        print(f"ERROR: template not found: {TEMPLATE}", file=sys.stderr)
        return 1

    project_index = load_project_index()

    rows = []
    unmatched: set[str] = set()
    with INPUT_CSV.open(encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        for r in reader:
            text = " ".join([
                r.get("title", ""),
                r.get("description", ""),
                r.get("sub_categories", ""),
            ])
            score, level, label, tags, matches = score_text(text)
            project = (r.get("project") or "").strip()
            proj_meta = project_index.get(project.lower(), {})
            if project and not proj_meta:
                unmatched.add(project)
            rows.append({
                "id": r.get("id", ""),
                "title": r.get("title", ""),
                "project": project,
                "call": r.get("call", ""),
                "category": r.get("category", ""),
                "sub_categories": r.get("sub_categories", ""),
                "top10": (r.get("top10") or "").strip().lower() == "yes",
                "description": r.get("description", ""),
                "url": r.get("url", ""),
                "danger_score": score,        # weighted float
                "danger_level": level,        # 0–5 bucket
                "danger_label": label,        # CLEAR/TRACE/LOW/MED/HIGH/CRITICAL
                "danger_tags": tags,
                "matches": matches,
                # Enrichment from projects_summarized_en.csv
                "grant_eur": proj_meta.get("grant_eur", 0),
                "coordinator": proj_meta.get("coordinator", ""),
                "project_year": proj_meta.get("year", ""),
            })
    if unmatched:
        print(f"WARN: {len(unmatched)} projects in achievements not in CSV_en: "
              f"{sorted(unmatched)}", file=sys.stderr)

    rows.sort(key=lambda r: (-r["danger_score"], r["project"], r["title"]))

    # 1. Write the raw scored JSON for inspection
    OUT_JSON.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")

    # 2. Build self-contained HTML by inlining the data into the template
    template_html = TEMPLATE.read_text(encoding="utf-8")
    # Escape "</script" inside the JSON to keep the inline <script> safe
    data_json = json.dumps(rows, ensure_ascii=False).replace("</", "<\\/")
    out_html = template_html.replace("__DATA_JSON__", data_json)
    OUT_HTML.write_text(out_html, encoding="utf-8")

    # 3. Print a summary
    total = len(rows)
    by_level: dict[tuple[int, str], int] = {}
    for r in rows:
        key = (r["danger_level"], r["danger_label"])
        by_level[key] = by_level.get(key, 0) + 1
    by_tag: dict[str, int] = {}
    for r in rows:
        for t in r["danger_tags"]:
            by_tag[t] = by_tag.get(t, 0) + 1

    print(f"Scored {total} achievements")
    print(f"  wrote {OUT_JSON.relative_to(ROOT)}")
    print(f"  wrote {OUT_HTML.relative_to(ROOT)}")
    print()
    print("Level distribution:")
    for (lvl, lbl), n in sorted(by_level.items(), key=lambda kv: -kv[0][0]):
        bar = "#" * n
        print(f"  L{lvl} {lbl:8s} {n:4d}  {bar}")
    print()
    print("Triggers per category (weight in parens):")
    for tag, n in sorted(by_tag.items(), key=lambda kv: -kv[1]):
        w = SCORING_WEIGHTS.get(tag, 1.0)
        print(f"  {n:4d}  {tag} ({w})")

    return 0


if __name__ == "__main__":
    sys.exit(main())
