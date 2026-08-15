#!/usr/bin/env python3
"""Verify schema, semantics and determinism for Gate-A v8."""

from __future__ import annotations
import importlib.util
import json
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]; HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V8_RECONCILIATION.json"; REPORT = HERE / "REPORT_GATE_V8.md"
SCHEMA = HERE / "schema/classical-import-gate-v8-reconciliation-v1.schema.json"; BUILDER = HERE / "build_classical_import_gate_v8_reconciliation.py"; CHECKER = HERE / "check_classical_import_gate_v8_reconciliation.py"

def module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None: raise RuntimeError(path)
    value = importlib.util.module_from_spec(spec); spec.loader.exec_module(value); return value

def verify(value: dict | None = None) -> list[str]:
    value = value or json.loads(RESULT.read_text()); errors = ["schema: " + x.message for x in Draft202012Validator(json.loads(SCHEMA.read_text())).iter_errors(value)]; errors.extend("checker: " + x for x in module("gate_v8_checker", CHECKER).check(value))
    if value == json.loads(RESULT.read_text()):
        result, report = module("gate_v8_builder", BUILDER).generated()
        if RESULT.read_bytes() != result: errors.append("deterministic result drift")
        if REPORT.read_bytes() != report: errors.append("deterministic report drift")
    return errors

def main() -> int:
    errors = verify(); print("CLASSICAL_IMPORT_GATE_V8_RECONCILIATION_SCHEMA: " + ("PASS" if not errors else "FAIL"))
    for error in errors: print("  - " + error)
    return bool(errors)

if __name__ == "__main__": raise SystemExit(main())
