#!/usr/bin/env python3
"""Schema, determinism and independence verifier for atlas V6."""

from __future__ import annotations
import importlib.util
import json
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "foundations"
RESULT = HERE / "results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V6.json"
REPORT = HERE / "reports/lorentzian-weyl-bv-completion-atlas-v6.md"
SCHEMA = HERE / "schema/foundational-lorentzian-weyl-bv-completion-atlas-v6.schema.json"

def module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None: raise ImportError(path)
    value = importlib.util.module_from_spec(spec); spec.loader.exec_module(value); return value

builder = module(HERE / "build_lorentzian_weyl_bv_completion_atlas_v6.py", "atlas_v6_builder")
checker = module(HERE / "check_lorentzian_weyl_bv_completion_atlas_v6.py", "atlas_v6_checker")

def main() -> int:
    value = json.loads(RESULT.read_text()); schema = json.loads(SCHEMA.read_text()); report = REPORT.read_text()
    Draft202012Validator.check_schema(schema)
    errors = ["schema " + item.message for item in Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(value)]
    errors.extend("checker " + item for item in checker.check(value))
    result_bytes, report_bytes = builder.generated()
    if RESULT.read_bytes() != result_bytes: errors.append("deterministic result drift")
    if REPORT.read_bytes() != report_bytes: errors.append("deterministic report drift")
    for token in ("54", "T_30^sharp", "R_30", "376 positive", "10 negative", "not serialized", "STRICT_386_COMPONENT_PAIRING_SERIALIZATION", "Boundaries"):
        if token not in report: errors.append("report token " + token)
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V6_SCHEMA: " + ("PASS" if not errors else "FAIL"))
    if errors:
        for error in errors: print("  - " + error)
    return bool(errors)

if __name__ == "__main__": raise SystemExit(main())
