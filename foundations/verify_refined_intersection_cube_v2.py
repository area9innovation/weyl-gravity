#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from foundations.check_refined_intersection_cube_v2 import check
from foundations.refine_intersection_cube_v2 import generated

RESULT = ROOT / "foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V2.json"
SCHEMA = ROOT / "foundations/schema/foundational-intersection-cube-v2.schema.json"
REPORT = ROOT / "foundations/reports/refined-intersection-cube-v2.md"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(*, result=None, report=None) -> tuple[list[str], list[str]]:
    value = load(RESULT) if result is None else result
    text = REPORT.read_text() if report is None else report
    errors: list[str] = []
    checks: list[str] = []

    errors.extend(
        "schema " + error.message
        for error in Draft202012Validator(load(SCHEMA), format_checker=FormatChecker()).iter_errors(value)
    )
    checks.append("Draft 2020-12 schema")

    checker_errors, summary = check(value)
    errors.extend("checker " + error for error in checker_errors)
    expected_summary = {
        "digest": "34996392dc7b7d4548f7bbf76cf1b6f8b50402da16e1789a637661a96f8fddc3",
        "cells": 452,
        "audit_decisions_applied": 112,
        "coverage_classified": 364,
        "reviewed_no_transfer": 88,
        "reviewed_child_gap": 24,
        "migration_pending": 0,
        "role_counts": {"DIRECT_LITERATURE": 84, "DIRECT_LOCAL": 76, "SUPPORTING": 267, "UNREVIEWED": 159},
        "dual_direct_cells": 7,
    }
    if summary != expected_summary:
        errors.append("expected v2 cube summary")
    checks.append("independent coordinate, coverage, and migration audit")

    expected_result, expected_report = generated()
    if (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode() != expected_result:
        errors.append("deterministic result drift")
    if text.encode() != expected_report:
        errors.append("deterministic report drift")
    checks.append("deterministic v2 cube and report")

    for pin in value.get("provenance", {}).get("inputs", []):
        path = ROOT / pin.get("path", "")
        if not path.is_file() or sha(path) != pin.get("sha256"):
            errors.append("provenance " + str(pin.get("path")))
    checks.append("v1 cube and migration-audit pins")

    flags = value.get("claim_flags", {})
    for key in ("v0_preserved", "v1_preserved", "all_v1_migrations_reviewed", "coverage_and_migration_separated"):
        if flags.get(key) is not True:
            errors.append("positive flag " + key)
    for key in ("all_576_cells_assessed", "literature_complete", "weakest_base_proved", "new_lorentzian_claim"):
        if flags.get(key) is not False:
            errors.append("boundary flag " + key)
    checks.append("compatibility and claim-boundary flags")

    for token in (
        "all **452** emitted coordinates",
        "**0 pending**",
        "**88 reviewed no-transfer**",
        "Coverage is classified in **364**",
        "`NOT_MAPPED`",
        "does not answer whether other literature supports the cell",
        "current-corpus programme gap rather than an impossibility result",
    ):
        if token not in text:
            errors.append("report token " + token)
    checks.append("plain-language v2 interpretation")
    return errors, checks


def main() -> int:
    errors, checks = verify()
    print("FOUNDATIONAL_INTERSECTION_CUBE_V2: " + ("PASS" if not errors else "FAIL"))
    for item in checks if not errors else errors:
        print("  - " + item)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
