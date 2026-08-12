#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from foundations.build_normal_hyperbolic_factor_atlas import generated
from foundations.check_normal_hyperbolic_factor_atlas import check

RESULT = ROOT / "foundations/results/FOUNDATIONAL_NORMAL_HYPERBOLIC_FACTOR_ATLAS_V1.json"
LEDGER = ROOT / "foundations/literature-causal-green-atlas-v1.json"
REPORT = ROOT / "foundations/reports/normal-hyperbolic-factor-foundations.md"
RESULT_SCHEMA = ROOT / "foundations/schema/foundational-normal-hyperbolic-factor-atlas-v1.schema.json"
LEDGER_SCHEMA = ROOT / "foundations/schema/foundational-causal-green-literature-v1.schema.json"


def verify(*, result=None, ledger=None, report=None):
    value = json.loads(RESULT.read_text()) if result is None else result
    sources = json.loads(LEDGER.read_text()) if ledger is None else ledger
    text = REPORT.read_text() if report is None else report
    errors = ["result schema " + e.message for e in Draft202012Validator(json.loads(RESULT_SCHEMA.read_text())).iter_errors(value)]
    errors += ["ledger schema " + e.message for e in Draft202012Validator(json.loads(LEDGER_SCHEMA.read_text())).iter_errors(sources)]
    checker_errors, summary = check(value, sources)
    errors += ["checker " + e for e in checker_errors]
    expected_ledger, expected_result, expected_report = generated()
    if (json.dumps(sources, indent=2, ensure_ascii=False) + "\n").encode() != expected_ledger: errors.append("deterministic ledger drift")
    if (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode() != expected_result: errors.append("deterministic result drift")
    if text.encode() != expected_report: errors.append("deterministic report drift")
    for pin in value.get("provenance", {}).get("inputs", []):
        path = ROOT / pin.get("path", "")
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != pin.get("sha256"): errors.append("provenance " + str(pin.get("path")))
    flags = value.get("claim_flags", {})
    for key in ("reverse_math_strength_proved", "bishop_constructive_green_theorem_identified", "choice_free_green_theorem_proved", "full_biwave_reversal_proved", "new_weyl_bv_propagator"):
        if flags.get(key) is not False: errors.append("claim boundary " + key)
    if summary != {"digest": value["independent_checker"]["expected_digest"], "sources": 6, "dependency_stages": 9, "frameworks": 6, "cell_actions": 9, "evidence_overlays": 5}: errors.append("expected atlas summary")
    return errors, ["two schemas", "independent atlas audit", "deterministic artifacts", "input hashes", "claim boundary"]


def main():
    errors, checks = verify()
    print("FOUNDATIONAL_NORMAL_HYPERBOLIC_FACTOR_ATLAS_V1: " + ("PASS" if not errors else "FAIL"))
    for item in checks if not errors else errors: print("  - " + item)
    return bool(errors)


if __name__ == "__main__": raise SystemExit(main())
