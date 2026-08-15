#!/usr/bin/env python3
"""Verify schema, determinism and independent replay for the local SDR maps."""

from __future__ import annotations

import importlib.util
import json
from jsonschema import Draft202012Validator, FormatChecker
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_LOCAL_SDR_COMPONENT_MAPS_V1.json"
REPORT = HERE / "REPORT_STRICT_386_LOCAL_SDR_COMPONENT_MAPS_V1.md"
SCHEMA = HERE / "schema/strict-386-local-sdr-component-maps-v1.schema.json"


def module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


builder = module(HERE / "build_strict_386_local_sdr_component_maps.py", "strict_local_sdr_builder")
checker = module(HERE / "check_strict_386_local_sdr_component_maps.py", "strict_local_sdr_checker")


def main() -> int:
    value, schema, report = json.loads(RESULT.read_text()), json.loads(SCHEMA.read_text()), REPORT.read_text()
    Draft202012Validator.check_schema(schema)
    errors = ["schema " + item.message for item in Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(value)]
    errors.extend("checker " + item for item in checker.check(value))
    result_bytes, report_bytes = builder.generated()
    if RESULT.read_bytes() != result_bytes:
        errors.append("deterministic result drift")
    if REPORT.read_bytes() != report_bytes:
        errors.append("deterministic report drift")
    for token in ("190", "70 derivative", "q1 H_alg + H_alg q1 = P_alg", "zero defects", "T/A/B", "Represented advanced/retarded", "FAIL_CLOSED", "Hadamard", "QME"):
        if token not in report:
            errors.append("report token " + token)
    print("STRICT_386_LOCAL_SDR_COMPONENT_MAPS_V1_SCHEMA: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
