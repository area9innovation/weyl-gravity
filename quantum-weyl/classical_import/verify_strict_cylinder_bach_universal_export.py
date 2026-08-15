#!/usr/bin/env python3
"""Schema, report, and fast-receiver verifier for the universal Bach export."""
from __future__ import annotations

import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_CYLINDER_BACH_UNIVERSAL_EXPORT_V1.json"
SCHEMA = HERE / "schema/strict-cylinder-bach-universal-export-v1.schema.json"
REPORT = HERE / "REPORT_STRICT_CYLINDER_BACH_UNIVERSAL_EXPORT_V1.md"
sys.path.insert(0, str(HERE))
from check_strict_cylinder_bach_universal_export import check  # noqa: E402


def verify(value: dict[str, object], report: str) -> list[str]:
    errors = [f"schema: {error.message}" for error in Draft202012Validator(json.loads(SCHEMA.read_text())).iter_errors(value)]
    errors.extend(check(value))
    for token in (
        "UNIVERSAL_CYLINDER_TABLE_AND_DIFF_IDENTITY_CERTIFIED_GLOBAL_AST_OPEN",
        "700",
        "19,401",
        "normalized Taylor",
        "Input-slot symmetry is checked",
        "zero background, unary and quadratic defects",
        "all four fifth-jet coordinate",
        "three independent exact fifth-jet point-evaluator Diff probes",
        "TENSOR_NATURAL_GLOBALIZATION",
        "HT1B_MODE_ADAPTERS",
        "STRICT_HSTAR_PORTABLE_INTEGRATION",
        "Tier 2",
        "fast independent checker",
    ):
        if token not in report:
            errors.append(f"human report missing boundary token: {token}")
    if value.get("repository_base_commit") != "1b4b9350":
        errors.append("repository base commit drift")
    if len(value.get("does_not_establish", [])) < 7:
        errors.append("does_not_establish ledger shortened")
    return errors


def main() -> int:
    value = json.loads(RESULT.read_text())
    errors = verify(value, REPORT.read_text())
    print("STRICT_CYLINDER_BACH_UNIVERSAL_EXPORT_V1: " + ("PASS" if not errors else "FAIL"))
    if errors:
        for error in errors:
            print(f"  - {error}")
    else:
        print("  - schema, compact table, full Weyl identity, point probes and report agree")
        print("  - Diff identity certified; globalization, HT1B adapters and portable h-star integration remain open")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
