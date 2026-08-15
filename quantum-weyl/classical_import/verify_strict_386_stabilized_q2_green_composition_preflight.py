#!/usr/bin/env python3
"""Verify schema, determinism and replay for the q2/Green preflight."""

from __future__ import annotations

import importlib.util
import json
from jsonschema import Draft202012Validator, FormatChecker
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_STABILIZED_Q2_GREEN_COMPOSITION_PREFLIGHT_V1.json"
REPORT = HERE / "REPORT_STRICT_386_STABILIZED_Q2_GREEN_COMPOSITION_PREFLIGHT_V1.md"
SCHEMA = HERE / "schema/strict-386-stabilized-q2-green-composition-preflight-v1.schema.json"


def module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


builder = module(HERE / "build_strict_386_stabilized_q2_green_composition_preflight.py", "q2_green_builder")
checker = module(HERE / "check_strict_386_stabilized_q2_green_composition_preflight.py", "q2_green_checker")


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
        "B_plus", "B_minus", "B_causal", "causal support", "Foundational split",
        "completed infinite-dimensional spaces", "authoritative", "recursive", "Hadamard", "QME",
    ):
        if token not in report:
            errors.append("report token " + token)
    print("STRICT_386_STABILIZED_Q2_GREEN_COMPOSITION_PREFLIGHT_V1_SCHEMA: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
