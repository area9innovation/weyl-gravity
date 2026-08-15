#!/usr/bin/env python3
"""Schema/provenance/report verifier for the strict five-row q2 AST."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_Q2_KINEMATIC_COTANGENT_AST_V1.json"
SCHEMA = HERE / "schema/strict-q2-kinematic-cotangent-ast-v1.schema.json"
REPORT = HERE / "REPORT_STRICT_Q2_KINEMATIC_COTANGENT_AST_V1.md"
sys.path.insert(0, str(HERE))
from check_strict_q2_kinematic_cotangent_ast import check  # noqa: E402


def verify(value: dict[str, object], report: str) -> list[str]:
    errors = [f"schema: {error.message}" for error in Draft202012Validator(json.loads(SCHEMA.read_text())).iter_errors(value)]
    errors.extend(check(value))
    required_report_tokens = (
        "FIVE_OF_SIX_MINIMAL_ROWS_SERIALIZED_POLARIZATION_OPEN",
        "odd ghost diagonal",
        "OPEN_HARD_BACH_AND_COTANGENT_ROW",
        "NOT_REPLAYED",
        "D^2 Bach[h,h]",
        "SUPPORT_LOCAL_Q2_EXPORT_CONTRACT",
    )
    for token in required_report_tokens:
        if token not in report:
            errors.append(f"human report missing boundary token: {token}")
    if value.get("classical_commit") != "3e15eafa5e0bb8cbc3eb1d2ad79a669c54ce9cca":
        errors.append("classical source commit drift")
    if value.get("dependency_tags") != ["LOCAL-ALGEBRAIC"]:
        errors.append("dependency tag promotion")
    if len(value.get("does_not_establish", [])) < 7:
        errors.append("does_not_establish ledger shortened")
    for item in value.get("provenance", {}).get("inputs", []):
        path = ROOT / item.get("path", "")
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != item.get("sha256"):
            errors.append(f"input hash drift: {item.get('path')}")
    return errors


def main() -> int:
    value = json.loads(RESULT.read_text())
    errors = verify(value, REPORT.read_text())
    print("STRICT_Q2_KINEMATIC_COTANGENT_AST_V1: " + ("PASS" if not errors else "FAIL"))
    if errors:
        for error in errors:
            print(f"  - {error}")
    else:
        print("  - Draft 2020-12 schema and five-row independent receiver replay")
        print("  - exact source hashes, report boundary and no-promotion flags")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
