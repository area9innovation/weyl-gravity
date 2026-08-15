#!/usr/bin/env python3
"""Schema, determinism and independence verifier for completion atlas V10."""

from __future__ import annotations

import importlib.util
import hashlib
import json
from jsonschema import Draft202012Validator, FormatChecker
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "foundations"
RESULT = HERE / "results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V10.json"
REPORT = HERE / "reports/lorentzian-weyl-bv-completion-atlas-v10.md"
SCHEMA = HERE / "schema/foundational-lorentzian-weyl-bv-completion-atlas-v10.schema.json"
SUCCESSOR = HERE / "results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V11.json"


def module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


builder = module(HERE / "build_lorentzian_weyl_bv_completion_atlas_v10.py", "atlas_v10_builder")
checker = module(HERE / "check_lorentzian_weyl_bv_completion_atlas_v10.py", "atlas_v10_checker")


def main() -> int:
    value, schema, report = json.loads(RESULT.read_text()), json.loads(SCHEMA.read_text()), REPORT.read_text()
    Draft202012Validator.check_schema(schema)
    errors = ["schema " + item.message for item in Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(value)]
    errors.extend("checker " + item for item in checker.check(value))
    successor = json.loads(SUCCESSOR.read_text()) if SUCCESSOR.is_file() else {}
    superseded = (
        successor.get("result_id") == "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V11"
        and successor.get("predecessor", {}).get("sha256") == hashlib.sha256(RESULT.read_bytes()).hexdigest()
        and successor.get("predecessor", {}).get("preserved") is True
    )
    if not superseded:
        result_bytes, report_bytes = builder.generated()
        if RESULT.read_bytes() != result_bytes:
            errors.append("deterministic result drift")
        if REPORT.read_bytes() != report_bytes:
            errors.append("deterministic report drift")
    for token in ("preferred local repair", "zero q-squared", "eight cyclicity defects", "1433.50", "82/82", "Full q1", "Hadamard", "QME", "Boundaries"):
        if token not in report:
            errors.append("report token " + token)
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V10_SCHEMA: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
