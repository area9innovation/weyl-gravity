#!/usr/bin/env python3
"""Schema and report-boundary verifier for portable local q1."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema

from check_strict_portable_local_q1_ast import check


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_PORTABLE_LOCAL_Q1_AST_V1.json"
SCHEMA = HERE / "schema/strict-portable-local-q1-ast-v1.schema.json"
REPORT = HERE / "REPORT_STRICT_PORTABLE_LOCAL_Q1_AST_V1.md"


def verify(value: dict[str, Any], report: str) -> list[str]:
    errors = check(value)
    schema = json.loads(SCHEMA.read_text())
    try:
        jsonschema.Draft202012Validator(schema).validate(value)
    except jsonschema.ValidationError as exc:
        errors.append(f"schema rejection: {exc.message}")
    required_phrases = (
        "Bach-flat",
        "q1^2=0",
        "The exact next calculation is `[q1,q2]=0`",
        "does not silently claim an off-shell background",
        "## Does not establish",
        "Lorentzian QME",
    )
    for phrase in required_phrases:
        if phrase not in report:
            errors.append(f"report missing boundary phrase: {phrase}")
    return errors


def main() -> int:
    value = json.loads(RESULT.read_text())
    errors = verify(value, REPORT.read_text())
    print("STRICT_PORTABLE_LOCAL_Q1_AST_V1_SCHEMA: " + ("PASS" if not errors else "FAIL"))
    if errors:
        for error in errors:
            print(f"  - {error}")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
