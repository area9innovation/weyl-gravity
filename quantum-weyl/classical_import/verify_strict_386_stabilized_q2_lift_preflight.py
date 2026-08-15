#!/usr/bin/env python3
"""Verify schema, determinism and independent replay for the q2 preflight."""

from __future__ import annotations

import importlib.util
import json
from jsonschema import Draft202012Validator, FormatChecker
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_STABILIZED_Q2_LIFT_PREFLIGHT_V1.json"
REPORT = HERE / "REPORT_STRICT_386_STABILIZED_Q2_LIFT_PREFLIGHT_V1.md"
SCHEMA = HERE / "schema/strict-386-stabilized-q2-lift-preflight-v1.schema.json"


def module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


builder = module(HERE / "build_strict_386_stabilized_q2_lift_preflight.py", "q2_preflight_builder")
checker = module(HERE / "check_strict_386_stabilized_q2_lift_preflight.py", "q2_preflight_checker")


def main() -> int:
    value = json.loads(RESULT.read_text())
    schema = json.loads(SCHEMA.read_text())
    report = REPORT.read_text()
    Draft202012Validator.check_schema(schema)
    errors = [
        "schema " + item.message
        for item in Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(value)
    ]
    errors.extend("checker " + item for item in checker.check(value))
    result_bytes, report_bytes = builder.generated()
    if RESULT.read_bytes() != result_bytes:
        errors.append("deterministic result drift")
    if REPORT.read_bytes() != report_bytes:
        errors.append("deterministic report drift")
    for token in (
        "q2_graph(x,y)=S q2_split(S^-1 x,S^-1 y)", "140", "68", "110",
        "authoritative nonlinear", "Gate A", "cyclic L-infinity", "D/q2",
    ):
        if token not in report:
            errors.append("report token " + token)
    print("STRICT_386_STABILIZED_Q2_LIFT_PREFLIGHT_V1_SCHEMA: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
