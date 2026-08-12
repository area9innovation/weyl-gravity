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

from foundations.audit_intersection_migrations import generated
from foundations.check_intersection_migration_audit import check

RESULT = ROOT / "foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_MIGRATION_AUDIT_V2.json"
SCHEMA = ROOT / "foundations/schema/foundational-intersection-cube-migration-audit-v2.schema.json"
REPORT = ROOT / "foundations/reports/intersection-cube-migration-audit-v2.md"


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
        "digest": "02ba119ad08cd74f692ffbba7160f452ea57a72bdd25da7f1803295e6b231014",
        "decisions": 112,
        "reviewed_no_transfer": 88,
        "reviewed_child_gap": 24,
        "evidence_batches": 18,
        "result_descendants": 12,
        "pieces_descendants": 76,
        "pending_after": 0,
    }
    if summary != expected_summary:
        errors.append("expected migration-audit summary")
    checks.append("independent 112-cell decision reconstruction")

    expected_result, expected_report = generated()
    if (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode() != expected_result:
        errors.append("deterministic result drift")
    if text.encode() != expected_report:
        errors.append("deterministic report drift")
    checks.append("deterministic ledger and report")

    for pin in value.get("provenance", {}).get("inputs", []):
        path = ROOT / pin.get("path", "")
        if not path.is_file() or sha(path) != pin.get("sha256"):
            errors.append("provenance " + str(pin.get("path")))
    checks.append("v0, v1, literature-ledger, and local-result pins")

    flags = value.get("claim_flags", {})
    for key in ("all_v1_pending_reviewed", "coverage_separated_from_migration"):
        if flags.get(key) is not True:
            errors.append("positive flag " + key)
    for key in ("parent_results_blindly_inherited", "reviewed_no_transfer_means_literature_absent", "child_gap_means_impossible", "new_lorentzian_claim"):
        if flags.get(key) is not False:
            errors.append("boundary flag " + key)
    checks.append("claim-boundary flags")

    for token in (
        "All **112** v1 migration-pending cells",
        "**88 reviewed no-transfer**",
        "**24 reviewed child gaps**",
        "Pending after audit: **0**",
        "Coverage and migration are now different fields",
        "not a literature-absence claim",
        "Descendants of v0 direct results | 12",
        "Descendants of v0 pieces-only cells | 76",
        "Evidence-free v0 parent gaps | 24",
    ):
        if token not in text:
            errors.append("report token " + token)
    checks.append("plain-language decision and boundary report")
    return errors, checks


def main() -> int:
    errors, checks = verify()
    print("FOUNDATIONAL_INTERSECTION_CUBE_MIGRATION_AUDIT_V2: " + ("PASS" if not errors else "FAIL"))
    for item in checks if not errors else errors:
        print("  - " + item)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
