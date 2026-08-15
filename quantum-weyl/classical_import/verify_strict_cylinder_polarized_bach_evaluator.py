#!/usr/bin/env python3
"""Schema, report, and boundary verifier for the exact Bach evaluator prototype."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_CYLINDER_POLARIZED_BACH_EVALUATOR_V1.json"
SCHEMA = HERE / "schema/strict-cylinder-polarized-bach-evaluator-v1.schema.json"
REPORT = HERE / "REPORT_STRICT_CYLINDER_POLARIZED_BACH_EVALUATOR_V1.md"
sys.path.insert(0, str(HERE))
from check_strict_cylinder_polarized_bach_evaluator import check  # noqa: E402


def verify(value: dict[str, object], report: str) -> list[str]:
    errors = [f"schema: {error.message}" for error in Draft202012Validator(json.loads(SCHEMA.read_text())).iter_errors(value)]
    errors.extend(check(value))
    for token in (
        "EVALUATOR_PROTOTYPE_EXECUTED_UNIVERSAL_AST_AND_DIFF_IDENTITY_OPEN",
        "rational metric four-jets",
        "not yet the universal component AST",
        "Q[a,b]/(a^2,b^2)",
        "no hidden",
        "differentiated Diff Noether",
        "HT1B",
        "P4_PORTABLE_AST_EXPORT",
    ):
        if token not in report:
            errors.append(f"human report missing boundary token: {token}")
    if value.get("repository_base_commit") != "99d4020850ef9cd394a5cfd9e1001228f430e2e2":
        errors.append("repository base commit drift")
    if len(value.get("does_not_establish", [])) < 7:
        errors.append("does_not_establish ledger shortened")
    implementation = value.get("implementation", {})
    path = ROOT / implementation.get("path", "")
    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != implementation.get("sha256"):
        errors.append("implementation provenance drift")
    return errors


def main() -> int:
    value = json.loads(RESULT.read_text())
    errors = verify(value, REPORT.read_text())
    print("STRICT_CYLINDER_POLARIZED_BACH_EVALUATOR_V1: " + ("PASS" if not errors else "FAIL"))
    if errors:
        for error in errors:
            print(f"  - {error}")
    else:
        print("  - Draft 2020-12 schema, executable replay and report boundary agree")
        print("  - portable AST, Diff identity and HT1B projection remain fail closed")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
