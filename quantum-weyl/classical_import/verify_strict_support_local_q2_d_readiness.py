#!/usr/bin/env python3
"""Fail-closed verifier for strict support-local q2/D readiness."""
from __future__ import annotations

import ast
import importlib.util
import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[2]
DIRECTORY = ROOT / "quantum-weyl/classical_import"
RESULT = DIRECTORY / "certificates/STRICT_SUPPORT_LOCAL_Q2_D_READINESS_V1.json"
REPORT = DIRECTORY / "REPORT_STRICT_SUPPORT_LOCAL_Q2_D_READINESS_V1.md"
SCHEMA = DIRECTORY / "schema/strict-support-local-q2-d-readiness-v1.schema.json"
CHECKER = DIRECTORY / "check_strict_support_local_q2_d_readiness.py"


def module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


builder = module(DIRECTORY / "build_strict_support_local_q2_d_readiness.py", "strict_q2_d_readiness_builder")
checker = module(CHECKER, "strict_q2_d_readiness_checker")


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
    if (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode() != result_bytes:
        errors.append("deterministic result drift")
    if report.encode() != report_bytes:
        errors.append("deterministic report drift")
    if imports(CHECKER) != {"hashlib", "json", "pathlib", "typing"}:
        errors.append("checker import boundary")
    for token in ("Six output rows", "metric-antifield row", "Seven receiver gates", "rank", "does not obstruct", "Next executable cut", "does not establish"):
        if token not in report:
            errors.append("report token " + token)
    return errors, ["Draft 2020-12 schema", "independent six-row source crosswalk", "seven-gate no-promotion firewall", "rank-64 E5 receiver witness", "all-energy q2 non-obstruction boundary", "six content-pinned inputs", "deterministic certificate and report"]


def main() -> int:
    errors, checks = verify()
    print("STRICT_SUPPORT_LOCAL_Q2_D_READINESS_V1: " + ("PASS" if not errors else "FAIL"))
    for item in errors if errors else checks:
        print("  - " + item)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
