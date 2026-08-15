#!/usr/bin/env python3
"""Schema, determinism and report verifier for the 386 pairing serialization."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from build_strict_386_component_pairing_serialization import generated
from check_strict_386_component_pairing_serialization import check


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.json"
REPORT = HERE / "REPORT_STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.md"
SCHEMA = HERE / "schema/strict-386-component-pairing-serialization-v1.schema.json"


def main() -> int:
    value = json.loads(RESULT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    errors = ["schema " + item.message for item in Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(value)]
    errors.extend("checker " + item for item in check(value))
    result, report = generated()
    if RESULT.read_bytes() != result:
        errors.append("deterministic result drift")
    if REPORT.read_bytes() != report:
        errors.append("deterministic report drift")
    text = REPORT.read_text()
    for token in ("356=36+320", "410", "rank **386**", "30", "60", "320", "T^T Omega=Omega T^sharp_G", "54", "operator", "Does not establish"):
        if token not in text:
            errors.append("report token " + token)
    print("STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1_SCHEMA: " + ("PASS" if not errors else "FAIL"))
    if errors:
        for error in errors:
            print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
