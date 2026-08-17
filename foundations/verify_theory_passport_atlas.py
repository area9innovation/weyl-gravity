#!/usr/bin/env python3
"""Verify schema, deterministic production, independent audit, and exposition."""
from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from foundations.build_theory_passport_atlas import build, canonical_digest, report
from foundations.check_theory_passport_atlas import check

RESULT = ROOT / "foundations/results/FOUNDATIONAL_END_TO_END_THEORY_PASSPORT_ATLAS_V1.json"
REPORT = ROOT / "foundations/reports/end-to-end-theory-passport-atlas-v1.md"
SCHEMA = ROOT / "foundations/schema/foundational-end-to-end-theory-passport-atlas-v1.schema.json"


def verify(*, value: dict[str, Any] | None = None, text: str | None = None) -> tuple[list[str], list[str]]:
    result = json.loads(RESULT.read_text()) if value is None else value
    human = REPORT.read_text() if text is None else text
    errors = ["schema " + item.message for item in Draft202012Validator(json.loads(SCHEMA.read_text()), format_checker=FormatChecker()).iter_errors(result)]
    checks = ["Draft 2020-12 schema"]
    if result.get("canonical_digest") != canonical_digest(result):
        errors.append("canonical digest")
    checks.append("canonical digest")
    if build() != result:
        errors.append("deterministic result drift")
    if report(result) != human:
        errors.append("deterministic report drift")
    checks.append("deterministic result and report")
    checker_errors, checker_summary = check(result)
    errors.extend("checker " + item for item in checker_errors)
    checks.append(f"independent source/assertion audit ({checker_summary['source_assertions']} assertions)")
    for token in ("not a score", "assumptions", "state", "dynamics", "observable", "prediction", "empirical", "first blocker", "highest-value next step", "does not establish"):
        if token.lower() not in human.lower():
            errors.append("report token " + token)
    checks.append("plain-language journey, statuses, blockers, and boundaries")
    return errors, checks


def main() -> int:
    errors, checks = verify()
    print("FOUNDATIONAL_END_TO_END_THEORY_PASSPORT_ATLAS_V1: " + ("PASS" if not errors else "FAIL"))
    for item in errors if errors else checks:
        print("  - " + item)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
