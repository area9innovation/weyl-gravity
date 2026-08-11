#!/usr/bin/env python3
from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from foundations.expand_intersection_cube import OBLIGATIONS, POLICY, TARGET, assess, priority

RESULT = ROOT / "foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_EXPANSION_V1.json"
CUBE = ROOT / "foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V0.json"
SCHEMA = ROOT / "foundations/schema/foundational-intersection-cube-expansion-v1.schema.json"
LITERATURE_SCHEMA = ROOT / "foundations/schema/foundational-literature-expansion-v2.schema.json"
LITERATURE = ROOT / "foundations/literature-expansion-v2.json"
REPORT = ROOT / "foundations/reports/cube-expansion-literature-analysis.md"
LEDGERS = (ROOT / "foundations/literature-ledger.json", ROOT / "foundations/literature-supplement-known-attempts-v1.json", LITERATURE)


def load(path: Path):
    return json.loads(path.read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(additions):
    payload = [(x["foundation"], x["carrier"], x["obligation"], x["status"], x["evidence"]) for x in additions]
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def verify(*, result=None, cube=None, report=None):
    r = load(RESULT) if result is None else result
    c = load(CUBE) if cube is None else cube
    text = REPORT.read_text() if report is None else report
    errors: list[str] = []
    errors.extend("schema " + e.message for e in Draft202012Validator(load(SCHEMA), format_checker=FormatChecker()).iter_errors(r))
    literature = load(LITERATURE)
    errors.extend("literature schema " + e.message for e in Draft202012Validator(load(LITERATURE_SCHEMA), format_checker=FormatChecker()).iter_errors(literature))
    if len({x["id"] for x in literature["entries"]}) != 20:
        errors.append("literature identifiers")
    for entry in literature["entries"]:
        artifact = entry["artifact"]
        if (artifact["status"] == "CONTENT_PINNED") != (artifact["sha256"] is not None):
            errors.append("literature pin/status " + entry["id"])
    for pin in r.get("provenance", {}).get("inputs", []):
        path = ROOT / pin.get("path", "")
        if not path.is_file() or sha(path) != pin.get("sha256"):
            errors.append("input pin " + str(pin.get("path")))
    additions = r.get("cell_additions", [])
    if canonical(additions) != r.get("canonical_digest"):
        errors.append("canonical digest")
    coords = [(x["foundation"], x["carrier"], x["obligation"]) for x in additions]
    if len(coords) != len(set(coords)):
        errors.append("duplicate additions")
    cube_by = {(x["foundation"], x["carrier"], x["obligation"]): x for x in c["cells"]}
    if len(cube_by) != TARGET or any(cube_by.get(coord) != cell for coord, cell in zip(coords, additions)):
        errors.append("expanded cube crosswalk")
    base = {coord for coord in cube_by if coord not in set(coords)}
    if len(base) != 59:
        errors.append("base coordinate count")
    candidates = [assess(f, carrier, obligation) for f, carrier in sorted(POLICY) for obligation in OBLIGATIONS if (f, carrier, obligation) not in base]
    expected = sorted(candidates, key=priority)[:TARGET - 59]
    if expected != additions:
        errors.append("deterministic selection")
    ids = set()
    for ledger_path in LEDGERS:
        ids.update(x["id"] for x in load(ledger_path)["entries"])
    ids.update(load(path).get("result_id") for path in (ROOT / "foundations/results").glob("*.json"))
    if any(not set(cell["evidence"]) <= ids for cell in additions):
        errors.append("unknown evidence")
    counts = Counter(x["status"] for x in additions)
    if r.get("method", {}).get("status_counts") != dict(sorted(counts.items())) or r.get("method", {}).get("resulting_assessed_cells") != TARGET:
        errors.append("method counts")
    flags = r.get("claim_flags", {})
    if flags.get("seventy_five_percent_assessed") is not True:
        errors.append("75 percent flag")
    for key in ("literature_complete", "all_cells_solved", "cross_framework_transfer_automatic", "new_lorentzian_claim"):
        if flags.get(key) is not False:
            errors.append("boundary flag " + key)
    for token in ("103 new coordinates", "162 of 216", "75.0%", "42 literature results", "42 pieces-only", "19 bounded local results", "Weak arithmetic", "not a literature-absence claim", "LORENTZIAN-CAUSAL"):
        if token not in text:
            errors.append("report token " + token)
    return errors


def main() -> int:
    errors = verify()
    print("FOUNDATIONAL_INTERSECTION_CUBE_EXPANSION_V1: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
