#!/usr/bin/env python3
"""Verify schema, semantics, exact types and determinism for Atlas V27."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V27.json"
REPORT = ROOT / "foundations/reports/lorentzian-weyl-bv-completion-atlas-v27.md"
SCHEMA = ROOT / "foundations/schema/foundational-lorentzian-weyl-bv-completion-atlas-v27.schema.json"
BUILDER = ROOT / "foundations/build_lorentzian_weyl_bv_completion_atlas_v27.py"
CHECKER = ROOT / "foundations/check_lorentzian_weyl_bv_completion_atlas_v27.py"


def module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def floats(value: object, path: str = "$") -> list[str]:
    if isinstance(value, float):
        return [path]
    if isinstance(value, dict):
        return [item for key, child in value.items() for item in floats(child, f"{path}.{key}")]
    if isinstance(value, list):
        return [item for index, child in enumerate(value) for item in floats(child, f"{path}[{index}]")]
    return []


def verify(value: dict | None = None, report: str | None = None) -> list[str]:
    value = value or json.loads(RESULT.read_text())
    report = REPORT.read_text() if report is None else report
    errors = ["schema: " + item.message for item in Draft202012Validator(json.loads(SCHEMA.read_text())).iter_errors(value)]
    errors.extend("checker: " + item for item in module("atlas_v27_checker", CHECKER).check(value))
    errors.extend("floating-point value in exact new block: " + item for item in floats(value.get("strict_quadratic_auxiliary_elimination", {})))
    for token in (value.get("result_id", ""), "Source / correction / transformed / candidate / residual: **-1 / 1 / 0 / 0 / 0**", "Gate V9 remains **FAIL_CLOSED**"):
        if token not in report:
            errors.append("report token missing: " + token)
    if value == json.loads(RESULT.read_text()):
        result, generated_report = module("atlas_v27_builder", BUILDER).generated()
        if RESULT.read_bytes() != result:
            errors.append("deterministic result drift")
        if REPORT.read_bytes() != generated_report:
            errors.append("deterministic report drift")
    return errors


def main() -> int:
    errors = verify()
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V27_SCHEMA: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
