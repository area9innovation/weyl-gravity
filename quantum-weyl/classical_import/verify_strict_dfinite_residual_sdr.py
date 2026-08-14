#!/usr/bin/env python3
"""Fail-closed schema, provenance and independence verifier for the D-finite SDR."""
from __future__ import annotations

import ast
import importlib.util
from json import loads
from pathlib import Path
import sys

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
DIRECTORY = ROOT / "quantum-weyl/classical_import"
RESULT = DIRECTORY / "certificates/STRICT_DFINITE_RESIDUAL_SDR_V1.json"
REPORT = DIRECTORY / "REPORT_STRICT_DFINITE_RESIDUAL_SDR_V1.md"
SCHEMA = DIRECTORY / "schema/strict-dfinite-residual-sdr-v1.schema.json"
CHECKER = DIRECTORY / "check_strict_dfinite_residual_sdr.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


builder = load_module(DIRECTORY / "build_strict_dfinite_residual_sdr.py", "strict_dfinite_sdr_builder")
checker = load_module(CHECKER, "strict_dfinite_sdr_checker")


def imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text())
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.update(item.name.split(".")[0] for item in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.module != "__future__":
            found.add(node.module.split(".")[0])
    return found


def verify(*, result: dict | None = None, report: str | None = None) -> tuple[list[str], list[str]]:
    value = loads(RESULT.read_text()) if result is None else result
    text = REPORT.read_text() if report is None else report
    errors = [
        "schema " + item.message
        for item in Draft202012Validator(loads(SCHEMA.read_text()), format_checker=FormatChecker()).iter_errors(value)
    ]
    checker_errors, _ = checker.check(value)
    errors.extend("checker " + item for item in checker_errors)
    result_bytes, report_bytes = builder.generated()
    if result_bytes != (RESULT.read_bytes() if result is None else (builder.dumps(value, indent=2, ensure_ascii=False) + "\n").encode()):
        errors.append("deterministic result drift")
    if report_bytes != text.encode():
        errors.append("deterministic report drift")
    if imports(CHECKER) != {"fractions", "hashlib", "json", "math", "pathlib", "typing"}:
        errors.append("independent checker import boundary")
    for token in (
        "portable exact object", "4490 full coordinates", "470 residual coordinates",
        "primitive-recursive arithmetic", "No form of", "Gate A remains",
        "does not establish",
    ):
        if token not in text:
            errors.append("report token " + token)
    return errors, [
        "Draft 2020-12 schema",
        "independent standard-library sparse rational receiver",
        "five-block semantic map reconstruction",
        "eight exact SDR identities and normalized side conditions",
        "six content-pinned inputs",
        "finite-foundational-strength and Gate-A scope firewalls",
        "deterministic certificate and report",
    ]


def main() -> int:
    errors, checks = verify()
    print("STRICT_DFINITE_RESIDUAL_SDR_V1: " + ("PASS" if not errors else "FAIL"))
    for item in errors if errors else checks:
        print("  - " + item)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
