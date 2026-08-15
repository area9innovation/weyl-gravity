#!/usr/bin/env python3
"""Schema, report, and independent-receiver verifier for the h-star row."""
from __future__ import annotations

import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_CYLINDER_HSTAR_BASEPOINT_ROW_V1.json"
SCHEMA = HERE / "schema/strict-cylinder-hstar-basepoint-row-v1.schema.json"
REPORT = HERE / "REPORT_STRICT_CYLINDER_HSTAR_BASEPOINT_ROW_V1.md"
sys.path.insert(0, str(HERE))
from check_strict_cylinder_hstar_basepoint_row import check  # noqa: E402


def verify(value: dict[str, object], report: str) -> list[str]:
    schema = json.loads(SCHEMA.read_text())
    errors = [f"schema: {error.message}" for error in Draft202012Validator(schema).iter_errors(value)]
    errors.extend(check(value))
    for token in (
        "HSTAR_BASEPOINT_ROW_AND_DIFF_IDENTITY_ASSEMBLED_PORTABLE_GLOBALIZATION_AND_POLARIZATION_OPEN",
        "q2_diagonal(h_star)",
        "one half",
        "minus the metric Euler derivative",
        "basepoint assembly",
        "TENSOR_NATURAL_GLOBALIZATION",
        "DIFFERENTIATED_DIFF_NOETHER",
        "SUSPENDED_GRADED_POLARIZATION",
        "SIX_ROW_INTERACTION_IDENTITIES",
        "Missing-object ledger",
        "Hadamard state",
    ):
        if token not in report:
            errors.append(f"human report missing boundary token: {token}")
    if value.get("repository_base_commit") != "1b4b9350":
        errors.append("repository base commit drift")
    return errors


def main() -> int:
    value = json.loads(RESULT.read_text())
    errors = verify(value, REPORT.read_text())
    print("STRICT_CYLINDER_HSTAR_BASEPOINT_ROW_V1: " + ("PASS" if not errors else "FAIL"))
    if errors:
        for error in errors:
            print(f"  - {error}")
    else:
        print("  - schema, source signs, variational adjoint, Hessian factor and report agree")
        print("  - no portable q2, Gate A, causal, Hadamard or QME promotion")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
