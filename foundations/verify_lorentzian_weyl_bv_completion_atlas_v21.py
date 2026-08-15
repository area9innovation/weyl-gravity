#!/usr/bin/env python3
"""Schema and semantic verifier for completion Atlas V21."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V21.json"
SCHEMA = ROOT / "foundations/schema/foundational-lorentzian-weyl-bv-completion-atlas-v21.schema.json"
CHECKER = ROOT / "foundations/check_lorentzian_weyl_bv_completion_atlas_v21.py"


def main() -> int:
    spec = importlib.util.spec_from_file_location("atlas_v21_checker", CHECKER)
    if spec is None or spec.loader is None:
        raise ImportError(CHECKER)
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    value = json.loads(RESULT.read_text())
    schema = json.loads(SCHEMA.read_text())
    errors = [f"schema: {error.message}" for error in Draft202012Validator(schema).iter_errors(value)]
    errors.extend(checker.check(value))
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V21_SCHEMA: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
