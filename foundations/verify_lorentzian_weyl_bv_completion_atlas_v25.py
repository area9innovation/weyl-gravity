#!/usr/bin/env python3
"""Verify schema, semantics and determinism for completion Atlas V25."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V25.json"
REPORT = ROOT / "foundations/reports/lorentzian-weyl-bv-completion-atlas-v25.md"
SCHEMA = ROOT / "foundations/schema/foundational-lorentzian-weyl-bv-completion-atlas-v25.schema.json"
BUILDER = ROOT / "foundations/build_lorentzian_weyl_bv_completion_atlas_v25.py"
CHECKER = ROOT / "foundations/check_lorentzian_weyl_bv_completion_atlas_v25.py"


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
    errors = ["schema: " + item.message for item in Draft202012Validator(schema).iter_errors(value)]
    errors.extend("checker: " + item for item in module("atlas_v25_checker", CHECKER).check(value))
    if value == json.loads(RESULT.read_text()):
        expected_result, expected_report = module("atlas_v25_builder", BUILDER).generated()
        if RESULT.read_bytes() != expected_result:
            errors.append("deterministic result drift")
        if REPORT.read_bytes() != expected_report:
            errors.append("deterministic report drift")
    return errors


def main() -> int:
    errors = verify()
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V25_SCHEMA: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
