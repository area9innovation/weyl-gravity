#!/usr/bin/env python3
"""Fail-closed verifier for classical import Gate-A reconciliation v3."""
from __future__ import annotations

import ast
import importlib.util
import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
DIRECTORY = ROOT / "quantum-weyl/classical_import"
RESULT = DIRECTORY / "certificates/CLASSICAL_IMPORT_GATE_V3_RECONCILIATION.json"
REPORT = DIRECTORY / "REPORT_GATE_V3.md"
SCHEMA = DIRECTORY / "schema/classical-import-gate-v3-reconciliation-v1.schema.json"
CHECKER = DIRECTORY / "check_classical_import_gate_v3_reconciliation.py"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


builder = load(DIRECTORY / "build_classical_import_gate_v3_reconciliation.py", "classical_import_gate_v3_builder")
checker = load(CHECKER, "classical_import_gate_v3_checker")


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
    value = json.loads(RESULT.read_text()) if result is None else result
    text = REPORT.read_text() if report is None else report
    errors = [
        "schema " + item.message
        for item in Draft202012Validator(
            json.loads(SCHEMA.read_text()), format_checker=FormatChecker()
        ).iter_errors(value)
    ]
    checker_errors, _ = checker.check(value)
    errors.extend("checker " + item for item in checker_errors)
    result_bytes, report_bytes = builder.generated()
    candidate_bytes = (
        RESULT.read_bytes()
        if result is None
        else (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode()
    )
    if result_bytes != candidate_bytes:
        errors.append("deterministic result drift")
    if report_bytes != text.encode():
        errors.append("deterministic report drift")
    if imports(CHECKER) != {"hashlib", "json", "pathlib", "typing"}:
        errors.append("independent checker import boundary")
    for token in (
        "historical residual-map portability gap is closed in one exact scope",
        "4490 full", "470 residual", "Three map exports",
        "Four freeze identities", "M3 is narrowed, not deleted",
        "Gate A remains fail-closed", "does not establish",
    ):
        if token not in text:
            errors.append("report token " + token)
    return errors, [
        "Draft 2020-12 schema",
        "append-only V2 predecessor pin",
        "independent three-map/four-identity promotion audit",
        "15 content-pinned inputs",
        "zero accepted common hashes and Gate-A fail-closed firewall",
        "M3 finite-versus-support-local boundary",
        "deterministic certificate and report",
    ]


def main() -> int:
    errors, checks = verify()
    print("CLASSICAL_IMPORT_GATE_V3_RECONCILIATION: " + ("PASS" if not errors else "FAIL"))
    for item in errors if errors else checks:
        print("  - " + item)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
