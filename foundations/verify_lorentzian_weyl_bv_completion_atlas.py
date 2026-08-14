#!/usr/bin/env python3
"""Fail-closed verifier for the Lorentzian Weyl BV completion atlas."""
from __future__ import annotations

import ast
import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from foundations.build_lorentzian_weyl_bv_completion_atlas import generated
from foundations.check_lorentzian_weyl_bv_completion_atlas import check


RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V1.json"
REPORT = ROOT / "foundations/reports/lorentzian-weyl-bv-completion-atlas-v1.md"
SCHEMA = ROOT / "foundations/schema/foundational-lorentzian-weyl-bv-completion-atlas-v1.schema.json"
CHECKER = ROOT / "foundations/check_lorentzian_weyl_bv_completion_atlas.py"


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
    for token in ("The four useful fronts", "First missing theorem by route", "old import gate", "Ranked research queue", "does not establish"):
        if token not in text:
            errors.append("report token " + token)
    checks = ["Draft 2020-12 schema", "independent branch/stage checker", "20 content-addressed evidence inputs", "77 lifecycle cells", "strict-versus-changed-theory firewall", "deterministic result and report"]
    return errors, checks


def main() -> int:
    errors, checks = verify()
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V1: " + ("PASS" if not errors else "FAIL"))
    for item in errors if errors else checks:
        print("  - " + item)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
