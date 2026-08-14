#!/usr/bin/env python3
"""Fail-closed schema, generator and independence verifier for atlas V2."""
from __future__ import annotations

import ast
import importlib.util
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "foundations"
RESULT = DIRECTORY / "results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V2.json"
REPORT = DIRECTORY / "reports/lorentzian-weyl-bv-completion-atlas-v2.md"
SCHEMA = DIRECTORY / "schema/foundational-lorentzian-weyl-bv-completion-atlas-v2.schema.json"


def module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


builder = module(DIRECTORY / "build_lorentzian_weyl_bv_completion_atlas_v2.py", "completion_atlas_v2_builder")
checker = module(DIRECTORY / "check_lorentzian_weyl_bv_completion_atlas_v2.py", "completion_atlas_v2_checker")


def imports(path: Path) -> set[str]:
    found: set[str] = set()
    for node in ast.walk(ast.parse(path.read_text())):
        if isinstance(node, ast.Import):
            found.update(item.name.split(".")[0] for item in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.module != "__future__":
            found.add(node.module.split(".")[0])
    return found


def verify(value: dict | None = None, report: str | None = None) -> tuple[list[str], list[str]]:
    value = json.loads(RESULT.read_text()) if value is None else value
    report = REPORT.read_text() if report is None else report
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    errors = ["schema " + item.message for item in Draft202012Validator(schema).iter_errors(value)]
    checked, _ = checker.check(value)
    errors += ["checker " + item for item in checked]
    result_bytes, report_bytes = builder.generated()
    if (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode() != result_bytes:
        errors.append("deterministic result drift")
    if report.encode() != report_bytes:
        errors.append("deterministic report drift")
    if imports(DIRECTORY / "check_lorentzian_weyl_bv_completion_atlas_v2.py") != {"hashlib", "json", "pathlib", "typing"}:
        errors.append("checker import boundary")
    for token in ("What changed from V1", "decision chain", "RANK_ONLY_FEASIBLE", "Route selection", "does not establish"):
        if token not in report:
            errors.append("report token " + token)
    return errors, ["Draft 2020-12 schema", "independent 77-cell audit", "eleven-step decision-chain scope firewall", "V1 preservation", "deterministic result and report"]


def main() -> int:
    errors, checks = verify()
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V2: " + ("PASS" if not errors else "FAIL"))
    for item in errors if errors else checks:
        print("  - " + item)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
