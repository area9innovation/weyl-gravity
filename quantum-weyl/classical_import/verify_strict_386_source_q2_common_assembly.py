#!/usr/bin/env python3
"""Schema validation plus independent replay for the source-q2 assembly."""

from __future__ import annotations

import json
from pathlib import Path
from jsonschema import Draft202012Validator

from check_strict_386_source_q2_common_assembly import check


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_SOURCE_Q2_COMMON_ASSEMBLY_V1.json"
SCHEMA = HERE / "schema/strict-386-source-q2-common-assembly-v1.schema.json"


def main() -> int:
    value, schema = json.loads(RESULT.read_text()), json.loads(SCHEMA.read_text())
    errors = [error.message for error in Draft202012Validator(schema).iter_errors(value)] + check(value)
    print("STRICT_386_SOURCE_Q2_COMMON_ASSEMBLY_V1_SCHEMA_AND_INDEPENDENT_REPLAY: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
