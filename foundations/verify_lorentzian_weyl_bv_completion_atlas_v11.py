#!/usr/bin/env python3
"""Schema, determinism and independence verifier for completion atlas V11."""

from __future__ import annotations

import importlib.util
import json
from jsonschema import Draft202012Validator, FormatChecker
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "foundations"
RESULT = HERE / "results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V11.json"
REPORT = HERE / "reports/lorentzian-weyl-bv-completion-atlas-v11.md"
SCHEMA = HERE / "schema/foundational-lorentzian-weyl-bv-completion-atlas-v11.schema.json"


def module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


builder = module(HERE / "build_lorentzian_weyl_bv_completion_atlas_v11.py", "atlas_v11_builder")
checker = module(HERE / "check_lorentzian_weyl_bv_completion_atlas_v11.py", "atlas_v11_checker")


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
    for token in ("complete content-addressed unary snapshot", "2,193", "zero exact defects", "Unary snapshot", "Gate A", "Hadamard", "QME", "Boundaries"):
        if token not in report:
            errors.append("report token " + token)
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V11_SCHEMA: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
