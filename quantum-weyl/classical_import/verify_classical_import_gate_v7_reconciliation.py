#!/usr/bin/env python3
"""Verify schema, determinism and independent replay for Gate-A v7."""

from __future__ import annotations

import importlib.util
import json
from jsonschema import Draft202012Validator, FormatChecker
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V7_RECONCILIATION.json"
REPORT = HERE / "REPORT_GATE_V7.md"
SCHEMA = HERE / "schema/classical-import-gate-v7-reconciliation-v1.schema.json"


def module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


builder = module(HERE / "build_classical_import_gate_v7_reconciliation.py", "gate_v7_builder")
checker = module(HERE / "check_classical_import_gate_v7_reconciliation.py", "gate_v7_checker")


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
    for token in ("386", "140", "68", "110 / 110", "cyclic L-infinity", "not accepted", "Gate A", "M3-M6"):
        if token not in report:
            errors.append("report token " + token)
    print("CLASSICAL_IMPORT_GATE_V7_RECONCILIATION_SCHEMA: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
