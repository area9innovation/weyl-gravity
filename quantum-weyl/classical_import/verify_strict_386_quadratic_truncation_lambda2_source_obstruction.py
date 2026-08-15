#!/usr/bin/env python3
"""Schema, determinism and semantic verification for the lambda2 obstruction."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_QUADRATIC_TRUNCATION_LAMBDA2_SOURCE_OBSTRUCTION_V1.json"
SCHEMA = HERE / "schema/strict-386-quadratic-truncation-lambda2-source-obstruction-v1.schema.json"
BUILDER = HERE / "build_strict_386_quadratic_truncation_lambda2_source_obstruction.py"
CHECKER = HERE / "check_strict_386_quadratic_truncation_lambda2_source_obstruction.py"


def module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def verify(value: dict | None = None) -> list[str]:
    value = value or json.loads(RESULT.read_text())
    schema = json.loads(SCHEMA.read_text())
    errors = ["schema: " + item.message for item in Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(value)]
    checker = module("lambda2_source_obstruction_checker", CHECKER)
    errors.extend("checker: " + item for item in checker.check(value))
    if value == json.loads(RESULT.read_text()):
        builder = module("lambda2_source_obstruction_builder", BUILDER)
        expected, report = builder.generated()
        if RESULT.read_bytes() != expected:
            errors.append("deterministic certificate drift")
        if (HERE / "REPORT_STRICT_386_QUADRATIC_TRUNCATION_LAMBDA2_SOURCE_OBSTRUCTION_V1.md").read_bytes() != report:
            errors.append("deterministic report drift")
    return errors


def main() -> int:
    errors = verify()
    print("STRICT_386_QUADRATIC_TRUNCATION_LAMBDA2_SOURCE_OBSTRUCTION_V1_SCHEMA: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
