#!/usr/bin/env python3
"""Fail-closed verifier for foundations cube v13."""
from __future__ import annotations

import json
from pathlib import Path
import sys
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))
from foundations.check_refined_intersection_cube_v13 import check
from foundations.refine_intersection_cube_v13 import generated

RESULT = ROOT / "foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V13.json"
REPORT = ROOT / "foundations/reports/refined-intersection-cube-v13.md"
SCHEMA = ROOT / "foundations/schema/foundational-intersection-cube-v13.schema.json"


def verify(*, result: dict | None = None, report: str | None = None) -> tuple[list[str], list[str]]:
    value = json.loads(RESULT.read_text()) if result is None else result; text = REPORT.read_text() if report is None else report
    errors = ["schema " + error.message for error in Draft202012Validator(json.loads(SCHEMA.read_text())).iter_errors(value)]
    checker_errors, _ = check(value); errors += ["checker " + error for error in checker_errors]
    result_bytes, report_bytes = generated()
    if (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode() != result_bytes: errors.append("deterministic result drift")
    if text.encode() != report_bytes: errors.append("deterministic report drift")
    flags = value.get("claim_flags", {})
    for key in ("v12_surface_preserved", "all_576_coordinates_assessed", "named_h2_test_completion_imported", "distributional_state_map_imported", "energy_image_weak_evolution_imported"):
        if flags.get(key) is not True: errors.append("positive flag " + key)
    for key in ("full_lf_test_topology_established", "arbitrary_distributional_uniqueness_established", "causal_support_established", "green_operator_established", "empirical_agreement_assessed", "complete_physical_theory_established", "new_lorentzian_claim"):
        if flags.get(key) is not False: errors.append("boundary flag " + key)
    for token in ("576-coordinate", "State representation", "well-posedness", "fast name", "does not establish"):
        if token not in text: errors.append("report token " + token)
    return errors, ["Draft 2020-12 schema", "independent preservation audit", "deterministic artifacts", "exact four-cell evidence scope", "two scoped direct-local promotions", "LF, arbitrary-distribution, and causal boundaries"]


def main() -> int:
    errors, checks = verify(); print("FOUNDATIONAL_INTERSECTION_CUBE_V13: " + ("PASS" if not errors else "FAIL")); [print("  - " + item) for item in (checks if not errors else errors)]; return bool(errors)


if __name__ == "__main__": raise SystemExit(main())
