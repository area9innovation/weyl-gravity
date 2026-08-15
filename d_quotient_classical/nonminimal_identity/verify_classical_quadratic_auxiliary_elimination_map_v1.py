#!/usr/bin/env python3
"""Verify schema, semantics and determinism for the quadratic auxiliary map."""

from __future__ import annotations
import importlib.util
import json
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "d_quotient_classical/nonminimal_identity"
RESULT = ROOT / "d_quotient_classical/certificates/CLASSICAL_QUADRATIC_AUXILIARY_ELIMINATION_MAP_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/classical-quadratic-auxiliary-elimination-map-v1.md"
SCHEMA = HERE / "schema/classical-quadratic-auxiliary-elimination-map-v1.schema.json"

def module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None: raise RuntimeError(path)
    value = importlib.util.module_from_spec(spec); spec.loader.exec_module(value); return value

def verify(value: dict | None = None) -> list[str]:
    value = value or json.loads(RESULT.read_text())
    errors = ["schema: " + item.message for item in Draft202012Validator(json.loads(SCHEMA.read_text())).iter_errors(value)]
    errors.extend("checker: " + item for item in module("quadratic_map_check", HERE / "check_classical_quadratic_auxiliary_elimination_map_v1.py").check(value))
    if value == json.loads(RESULT.read_text()):
        expected_result, expected_report = module("quadratic_map_build", HERE / "classical_quadratic_auxiliary_elimination_map_v1.py").generated()
        if RESULT.read_bytes() != expected_result: errors.append("deterministic result drift")
        if REPORT.read_bytes() != expected_report: errors.append("deterministic report drift")
    return errors

def main() -> int:
    errors = verify(); print("CLASSICAL_QUADRATIC_AUXILIARY_ELIMINATION_MAP_V1_SCHEMA: " + ("PASS" if not errors else "FAIL"))
    for error in errors: print("  - " + error)
    return bool(errors)

if __name__ == "__main__": raise SystemExit(main())
