#!/usr/bin/env python3
"""Schema, determinism and independent-check verifier for endpoint q1 bridge."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from build_strict_386_endpoint_q1_content_bridge import generated
from check_strict_386_endpoint_q1_content_bridge import check


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_ENDPOINT_Q1_CONTENT_BRIDGE_V1.json"
REPORT = HERE / "REPORT_STRICT_386_ENDPOINT_Q1_CONTENT_BRIDGE_V1.md"
SCHEMA = HERE / "schema/strict-386-endpoint-q1-content-bridge-v1.schema.json"


def main() -> int:
    value = json.loads(RESULT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    errors = [
        "schema " + item.message
        for item in Draft202012Validator(
            schema, format_checker=FormatChecker()
        ).iter_errors(value)
    ]
    result_bytes, report_bytes = generated()
    if RESULT.read_bytes() != result_bytes:
        errors.append("certificate is stale relative to fast producer")
    if REPORT.read_bytes() != report_bytes:
        errors.append("report is stale relative to fast producer")
    checked, _ = check(value)
    errors.extend("checker " + item for item in checked)
    for token in (
        "700/700", "80/80", "common Gate-coordinate q1 digest",
        "Pairing boundary", "-I_5", "PRA", "Does not establish",
    ):
        if token not in REPORT.read_text():
            errors.append("report token " + token)
    print("STRICT_386_ENDPOINT_Q1_CONTENT_BRIDGE_V1_SCHEMA: " + ("PASS" if not errors else "FAIL"))
    if errors:
        for error in errors:
            print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
