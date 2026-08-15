#!/usr/bin/env python3
"""Verify schema, semantics, exact types and determinism for the quadratic channel."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_QUADRATIC_AUXILIARY_ELIMINATION_CHANNEL_V1.json"
REPORT = HERE / "REPORT_STRICT_386_QUADRATIC_AUXILIARY_ELIMINATION_CHANNEL_V1.md"
SCHEMA = HERE / "schema/strict-386-quadratic-auxiliary-elimination-channel-v1.schema.json"
BUILDER = HERE / "build_strict_386_quadratic_auxiliary_elimination_channel.py"
CHECKER = HERE / "check_strict_386_quadratic_auxiliary_elimination_channel.py"


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
    schema = json.loads(SCHEMA.read_text())
    errors = ["schema: " + item.message for item in Draft202012Validator(schema).iter_errors(value)]
    errors.extend("checker: " + item for item in module("quadratic_channel_checker", CHECKER).check(value))
    errors.extend("floating-point value: " + item for item in floats(value))
    for token in (
        value.get("result_id", ""),
        "inverse-shift mass cross term: **1**",
        "residual: **0**",
        "Full q2/q3 pullback",
    ):
        if token not in report:
            errors.append("report token missing: " + token)
    if value == json.loads(RESULT.read_text()):
        expected_result, expected_report = module("quadratic_channel_builder", BUILDER).generated()
        if RESULT.read_bytes() != expected_result:
            errors.append("deterministic result drift")
        if REPORT.read_bytes() != expected_report:
            errors.append("deterministic report drift")
    return errors


def main() -> int:
    errors = verify()
    print("STRICT_386_QUADRATIC_AUXILIARY_ELIMINATION_CHANNEL_V1_SCHEMA: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
