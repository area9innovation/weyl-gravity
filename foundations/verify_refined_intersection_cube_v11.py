#!/usr/bin/env python3
"""Fail-closed verifier for foundations cube v11."""
from __future__ import annotations

import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from foundations.check_refined_intersection_cube_v11 import check
from foundations.refine_intersection_cube_v11 import generated


RESULT = ROOT / "foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V11.json"
REPORT = ROOT / "foundations/reports/refined-intersection-cube-v11.md"
SCHEMA = ROOT / "foundations/schema/foundational-intersection-cube-v11.schema.json"


def verify(*, result: dict | None = None, report: str | None = None) -> tuple[list[str], list[str]]:
    value = json.loads(RESULT.read_text()) if result is None else result
    text = REPORT.read_text() if report is None else report
    errors = ["schema " + error.message for error in Draft202012Validator(json.loads(SCHEMA.read_text())).iter_errors(value)]
    checker_errors, _ = check(value)
    errors += ["checker " + error for error in checker_errors]
    result_bytes, report_bytes = generated()
    if (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode() != result_bytes:
        errors.append("deterministic result drift")
    if text.encode() != report_bytes:
        errors.append("deterministic report drift")
    flags = value.get("claim_flags", {})
    for key in ("v10_surface_preserved", "all_576_coordinates_assessed", "declared_wave_observable_imported", "uniform_observable_reconstruction_imported", "explicit_cutoff_imported"):
        if flags.get(key) is not True:
            errors.append("positive flag " + key)
    for key in ("full_state_reconstruction_established", "representation_invariance_established", "causal_support_established", "empirical_agreement_assessed", "complete_physical_theory_established", "new_lorentzian_claim"):
        if flags.get(key) is not False:
            errors.append("boundary flag " + key)
    for token in ("576-coordinate", "N(k)=k+ell(K)+1", "not the full field", "does not establish"):
        if token not in text:
            errors.append("report token " + token)
    return errors, ["Draft 2020-12 schema", "independent preservation audit", "deterministic artifacts", "exact two-cell scope", "claim boundaries"]


def main() -> int:
    errors, checks = verify()
    print("FOUNDATIONAL_INTERSECTION_CUBE_V11: " + ("PASS" if not errors else "FAIL"))
    for item in checks if not errors else errors:
        print("  - " + item)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
