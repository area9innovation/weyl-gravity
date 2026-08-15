#!/usr/bin/env python3
"""Schema, determinism and independent-check verifier for causal sign transport."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from build_strict_386_causal_sign_transport import generated
from check_strict_386_causal_sign_transport import check


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_CAUSAL_SIGN_TRANSPORT_V1.json"
REPORT = HERE / "REPORT_STRICT_386_CAUSAL_SIGN_TRANSPORT_V1.md"
SCHEMA = HERE / "schema/strict-386-causal-sign-transport-v1.schema.json"


def main() -> int:
    value = json.loads(RESULT.read_text())
    schema = json.loads(SCHEMA.read_text())
    errors = [
        "schema " + item.message
        for item in Draft202012Validator(
            schema, format_checker=FormatChecker()
        ).iter_errors(value)
    ]
    expected_result, expected_report = generated()
    if RESULT.read_bytes() != expected_result:
        errors.append("certificate is stale relative to producer")
    if REPORT.read_bytes() != expected_report:
        errors.append("report is stale relative to producer")
    errors.extend(check(value))
    print("STRICT_386_CAUSAL_SIGN_TRANSPORT_V1_SCHEMA: " + ("PASS" if not errors else "FAIL"))
    if errors:
        for error in errors:
            print(f"  - {error}")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
