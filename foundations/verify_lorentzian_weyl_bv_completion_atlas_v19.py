#!/usr/bin/env python3
"""Verify schema, determinism and replay for Atlas V19."""

from __future__ import annotations

import importlib.util
import json
from jsonschema import Draft202012Validator, FormatChecker
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V19.json"
REPORT = ROOT / "foundations/reports/lorentzian-weyl-bv-completion-atlas-v19.md"
SCHEMA = ROOT / "foundations/schema/foundational-lorentzian-weyl-bv-completion-atlas-v19.schema.json"


def module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


builder = module(ROOT / "foundations/build_lorentzian_weyl_bv_completion_atlas_v19.py", "atlas_v19_builder")
checker = module(ROOT / "foundations/check_lorentzian_weyl_bv_completion_atlas_v19.py", "atlas_v19_checker")


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
        "77", "Every finite retarded", "Every finite advanced", "40", "38", "2",
        "Foundational boundary", "STRICT_386_AUTHORITATIVE_Q2_IDENTITY",
        "STRICT_POLARIZED_FORMAL_MOLLER_COEFFICIENTS", "authoritative q2",
    ):
        if token not in report:
            errors.append("report token " + token)
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V19_SCHEMA: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
