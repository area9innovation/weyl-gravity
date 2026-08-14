#!/usr/bin/env python3
"""Schema and deterministic-artifact verifier for the BT foundations import."""
from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from foundations.build_bt_euclidean_lattice_import import generated
from foundations.check_bt_euclidean_lattice_import import check

RESULT = ROOT / "foundations/results/FOUNDATIONAL_BT_EUCLIDEAN_LATTICE_IMPORT_V1.json"
REPORT = ROOT / "foundations/reports/bt-euclidean-lattice-foundational-import.md"
SCHEMA = ROOT / "foundations/schema/foundational-bt-euclidean-lattice-import-v1.schema.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def verify(*, value: dict[str, Any] | None = None, report: str | None = None) -> tuple[list[str], list[str]]:
    result = load(RESULT) if value is None else value
    text = REPORT.read_text() if report is None else report
    errors = ["schema " + item.message for item in Draft202012Validator(load(SCHEMA), format_checker=FormatChecker()).iter_errors(result)]
    checks = ["Draft 2020-12 import schema"]
    checker_errors, _ = check(result)
    errors.extend("checker " + item for item in checker_errors)
    checks.append("independent exact arithmetic, provenance, numerical-gate, and boundary checks")
    result_bytes, report_bytes = generated()
    if (json.dumps(result, indent=2, ensure_ascii=False) + "\n").encode() != result_bytes or text.encode() != report_bytes:
        errors.append("deterministic artifact drift")
    checks.append("deterministic result and report")
    for token in ("five direct capabilities", "COARSE_REPRODUCTION_ONLY", "not identical", "stays a priority gap", "anything LORENTZIAN-CAUSAL"):
        if token not in text:
            errors.append("report token " + token)
    checks.append("human-readable exact/numeric/reconstruction boundaries")
    return errors, checks


def main() -> int:
    errors, checks = verify()
    print("FOUNDATIONAL_BT_EUCLIDEAN_LATTICE_IMPORT_V1: " + ("PASS" if not errors else "FAIL"))
    for item in checks if not errors else errors:
        print("  - " + item)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
