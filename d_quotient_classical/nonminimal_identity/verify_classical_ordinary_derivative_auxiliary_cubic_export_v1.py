#!/usr/bin/env python3
"""Verify schema, exact types, semantics and determinism for the auxiliary cubic export."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RESULT = ROOT / "d_quotient_classical/certificates/CLASSICAL_ORDINARY_DERIVATIVE_AUXILIARY_CUBIC_EXPORT_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/classical-ordinary-derivative-auxiliary-cubic-export-v1.md"
SCHEMA = HERE / "schema/classical-ordinary-derivative-auxiliary-cubic-export-v1.schema.json"
BUILDER = HERE / "classical_ordinary_derivative_auxiliary_cubic_export_v1.py"
CHECKER = HERE / "check_classical_ordinary_derivative_auxiliary_cubic_export_v1.py"


def module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def floats(value: object, path: str = "$") -> list[str]:
    if isinstance(value, float):
        return [path]
    if isinstance(value, dict):
        return [item for key, child in value.items() for item in floats(child, f"{path}.{key}")]
    if isinstance(value, list):
        return [item for index, child in enumerate(value) for item in floats(child, f"{path}[{index}]")]
    return []


def verify(value: dict | None = None, report: str | None = None) -> list[str]:
    value = value or json.loads(RESULT.read_text())
    report = REPORT.read_text() if report is None else report
    errors = ["schema: " + item.message for item in Draft202012Validator(json.loads(SCHEMA.read_text())).iter_errors(value)]
    errors.extend("checker: " + item for item in module("aux_cubic_checker", CHECKER).check(value))
    errors.extend("floating-point value: " + item for item in floats(value))
    for token in (value.get("result_id", ""), "polarization is **-1**", "not a no-go for equivalence"):
        if token not in report:
            errors.append("report token missing: " + token)
    if value == json.loads(RESULT.read_text()):
        expected_result, expected_report = module("aux_cubic_builder", BUILDER).generated()
        if RESULT.read_bytes() != expected_result:
            errors.append("deterministic result drift")
        if REPORT.read_bytes() != expected_report:
            errors.append("deterministic report drift")
    return errors


def main() -> int:
    errors = verify()
    print("CLASSICAL_ORDINARY_DERIVATIVE_AUXILIARY_CUBIC_EXPORT_V1_SCHEMA: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
