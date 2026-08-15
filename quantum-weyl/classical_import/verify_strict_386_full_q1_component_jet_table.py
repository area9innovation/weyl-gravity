#!/usr/bin/env python3
"""Verify schema, determinism, report, and independent full-q1 replay."""

from __future__ import annotations

import importlib.util
import json
from jsonschema import Draft202012Validator, FormatChecker
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_FULL_Q1_COMPONENT_JET_TABLE_V1.json"
REPORT = HERE / "REPORT_STRICT_386_FULL_Q1_COMPONENT_JET_TABLE_V1.md"
SCHEMA = HERE / "schema/strict-386-full-q1-component-jet-table-v1.schema.json"


def module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


builder = module(HERE / "build_strict_386_full_q1_component_jet_table.py", "strict_full_q1_builder")
checker = module(HERE / "check_strict_386_full_q1_component_jet_table.py", "strict_full_q1_checker")


def main() -> int:
    value = json.loads(RESULT.read_text())
    schema = json.loads(SCHEMA.read_text())
    report = REPORT.read_text()
    Draft202012Validator.check_schema(schema)
    errors = ["schema " + item.message for item in Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(value)]
    errors.extend("checker " + item for item in checker.check(value))
    result_bytes, report_bytes = builder.generated()
    if RESULT.read_bytes() != result_bytes:
        errors.append("deterministic result drift")
    if REPORT.read_bytes() != report_bytes:
        errors.append("deterministic report drift")
    for token in ("386 rows", "2193", "Suspended cyclicity defects", "unary snapshot", "Gate-A", "Hadamard", "QME"):
        if token not in report:
            errors.append("report token " + token)
    print("STRICT_386_FULL_Q1_COMPONENT_JET_TABLE_V1_SCHEMA: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
