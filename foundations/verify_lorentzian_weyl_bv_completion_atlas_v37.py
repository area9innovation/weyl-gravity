#!/usr/bin/env python3
"""Validate the Atlas V37 JSON schema."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "foundations/schema/foundational-lorentzian-weyl-bv-completion-atlas-v37.schema.json"
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V37.json"


def main() -> int:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V37_SCHEMA: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
