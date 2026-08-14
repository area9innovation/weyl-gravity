#!/usr/bin/env python3
"""Fail-closed verifier for classical import Gate-A reconciliation v2."""
from __future__ import annotations

import ast
import importlib.util
import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


DIRECTORY = ROOT / "quantum-weyl/classical_import"
build_module = load(DIRECTORY / "build_classical_import_gate_v2_reconciliation.py", "classical_import_gate_v2_builder")
check_module = load(DIRECTORY / "check_classical_import_gate_v2_reconciliation.py", "classical_import_gate_v2_checker")
generated = build_module.generated
check = check_module.check
RESULT = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V2_RECONCILIATION.json"
REPORT = ROOT / "quantum-weyl/classical_import/REPORT_GATE_V2.md"
SCHEMA = ROOT / "quantum-weyl/classical_import/schema/classical-import-gate-v2-reconciliation-v1.schema.json"
CHECKER = ROOT / "quantum-weyl/classical_import/check_classical_import_gate_v2_reconciliation.py"


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
    errors = ["schema " + item.message for item in Draft202012Validator(json.loads(SCHEMA.read_text())).iter_errors(value)]
    checker_errors, _ = check(value)
    errors += ["checker " + item for item in checker_errors]
    result_bytes, report_bytes = generated()
    if (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode() != result_bytes:
        errors.append("deterministic result drift")
    if text.encode() != report_bytes:
        errors.append("deterministic report drift")
    if imports(CHECKER) != {"hashlib", "json", "pathlib", "typing"}:
        errors.append("checker import boundary")
    for token in ("Twenty required exports", "Ten freeze identities", "Minimal replacement bundle", "Gate verdict", "tempting substitutions fail", "does not establish"):
        if token not in text:
            errors.append("report token " + token)
    return errors, ["Draft 2020-12 schema", "independent twenty-export/ten-check audit", "13 content-pinned inputs", "same-theory versus different-theory firewall", "residual-SDR naming firewall", "deterministic certificate and report"]


def main() -> int:
    errors, checks = verify()
    print("CLASSICAL_IMPORT_GATE_V2_RECONCILIATION: " + ("PASS" if not errors else "FAIL"))
    for item in errors if errors else checks:
        print("  - " + item)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
