#!/usr/bin/env python3
"""Fail-closed schema, determinism and independent-check verifier for V5."""

from __future__ import annotations

import ast
import importlib.util
import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "foundations"
RESULT = HERE / "results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V5.json"
REPORT = HERE / "reports/lorentzian-weyl-bv-completion-atlas-v5.md"
SCHEMA = HERE / "schema/foundational-lorentzian-weyl-bv-completion-atlas-v5.schema.json"
CHECKER = HERE / "check_lorentzian_weyl_bv_completion_atlas_v5.py"


def module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


builder = module(HERE / "build_lorentzian_weyl_bv_completion_atlas_v5.py", "atlas_v5_builder")
checker = module(CHECKER, "atlas_v5_checker")


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
    errors = ["schema " + item.message for item in Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(value)]
    checked, _ = checker.check(value)
    errors.extend("checker " + item for item in checked)
    result_bytes, report_bytes = builder.generated()
    if RESULT.read_bytes() != result_bytes:
        errors.append("deterministic result drift")
    if report.encode() != report_bytes:
        errors.append("deterministic report drift")
    if imports(CHECKER) != {"hashlib", "json", "pathlib", "typing"}:
        errors.append("checker import boundary")
    for token in ("80/80", "700/700", "490,000", "619", "-I_5", "PRA", "Pairing boundary", "Updated route selection", "does not establish"):
        if token not in report:
            errors.append("report token " + token)
    return errors, [
        "Draft 2020-12 schema", "independent 77-cell audit", "V4 preservation",
        "80-table unary comparison", "700-column Bach comparison",
        "five-row pairing-sign firewall", "Gate-A/full-carrier firewall",
        "unchanged Berger chain", "five-route ranking", "41 content-pinned inputs",
        "deterministic result and report",
    ]


def main() -> int:
    errors, checks = verify()
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V5_SCHEMA: " + ("PASS" if not errors else "FAIL"))
    if errors:
        for error in errors:
            print("  - " + error)
    else:
        for check in checks:
            print("  - " + check)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
